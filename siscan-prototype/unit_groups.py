"""Composição versionada de grupamentos em memória, sem efeitos no exercício.

Contexto e inventário são entradas de um provedor interno já verificado, não
autenticação. Não consulta bancos, não promove dados ou agrega poder de combate.
"""

from copy import deepcopy
import hashlib
import json
import re
from threading import RLock
import uuid


class GroupConflict(ValueError):
    """Conflito de intenção, revisão ou vínculo operativo direto."""


def _encode(value) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError('Conteúdo deve ser JSON finito e canônico.') from exc


def _digest(value) -> str:
    return hashlib.sha256(_encode(value).encode('utf-8')).hexdigest()


def _text(value, name, *, trim=False, maximum=None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name}: texto não vazio obrigatório.')
    result = value.strip() if trim else value
    if maximum is not None and len(result) > maximum:
        raise ValueError(f'{name}: tamanho máximo {maximum}.')
    return result


def _uuid(value, name) -> str:
    try:
        if not isinstance(value, str) or str(uuid.UUID(value)) != value:
            raise ValueError()
    except (ValueError, AttributeError) as exc:
        raise ValueError(f'{name}: UUID canônico obrigatório.') from exc
    return value


def _context(contexto) -> tuple[int, str]:
    if (not isinstance(contexto, dict) or set(contexto) != {'exercise_id', 'team'}
            or type(contexto['exercise_id']) is not int or contexto['exercise_id'] <= 0
            or contexto['team'] not in ('AZUL', 'VERMELHO')):
        raise ValueError('Informe contexto interno com exercício positivo e partido válido.')
    return contexto['exercise_id'], contexto['team']


def _revision(value) -> int:
    if type(value) is not int or value < 1:
        raise ValueError('Revisão deve ser inteiro positivo.')
    return value


def _normalizar_composicao(pedido, *, revisao=False) -> dict:
    required = {'command_id', 'designation', 'domain', 'member_unit_ids'}
    if revisao:
        required |= {'group_id', 'expected_revision'}
    optional = {'organization_label', 'mpnl_binding'}
    if not isinstance(pedido, dict) or not required <= set(pedido) or set(pedido) - required - optional:
        raise ValueError('Pedido de composição incompleto ou com campos inesperados.')
    result = dict(command_id=_uuid(pedido['command_id'], 'command_id'),
                  designation=_text(pedido['designation'], 'designation', trim=True, maximum=120),
                  domain=pedido['domain'])
    if result['domain'] not in ('naval', 'aereo'):
        raise ValueError('Domínio não normalizado; use naval ou aereo.')
    membros = pedido['member_unit_ids']
    if not isinstance(membros, list) or not membros:
        raise ValueError('Informe lista não vazia de integrantes.')
    for member in membros:
        _text(member, 'unit_id')
    if len(set(membros)) != len(membros):
        raise ValueError('Integrante repetido no pedido.')
    result['member_unit_ids'] = sorted(membros)
    label = pedido.get('organization_label')
    result['organization_label'] = None if label is None else _text(label, 'organization_label', trim=True, maximum=120)
    binding = pedido.get('mpnl_binding')
    if binding is not None:
        if (not isinstance(binding, dict) or set(binding) != {'force', 'level'}
                or binding['force'] not in ('MARINHA', 'FORCA_AEREA', 'EXERCITO')
                or type(binding['level']) is not int or not 1 <= binding['level'] <= 4):
            raise ValueError('Vínculo MPNL exige ramo e um dos quatro níveis existentes.')
    result['mpnl_binding'] = deepcopy(binding)
    if revisao:
        result.update(group_id=_uuid(pedido['group_id'], 'group_id'),
                      expected_revision=_revision(pedido['expected_revision']))
    return result


def _members(context, inventario, ids, domain):
    if not isinstance(inventario, dict):
        raise ValueError('Visão de inventário deve ser um mapa por unit_id.')
    refs, projection = [], []
    for unit_id in ids:
        record = inventario.get(unit_id)
        if not isinstance(record, dict):
            raise PermissionError('Integrante não disponível na visão fornecida.')
        if (record.get('unit_id') != unit_id or type(record.get('exercise_id')) is not int
                or record.get('exercise_id') != context[0] or record.get('team') != context[1]
                or record.get('allocated') is not True):
            raise PermissionError('Integrante fora do contexto ou não disponível ao partido.')
        if record.get('domain') != domain:
            raise ValueError('Domínio incompatível ou sem normalização demonstrada.')
        evidence = record.get('domain_evidence')
        if (not isinstance(evidence, dict) or set(evidence) != {'domain', 'basis', 'reference'}
                or evidence['domain'] != domain
                or evidence['basis'] not in ('synthetic_controlled', 'catalog_mapping')):
            raise ValueError('Falta evidência de normalização do domínio pelo provedor.')
        _text(evidence['reference'], 'domain_evidence.reference')
        snapshot = record.get('snapshot')
        sha = record.get('snapshot_sha256')
        if (not isinstance(snapshot, dict) or not isinstance(sha, str)
                or re.fullmatch('[0-9a-f]{64}', sha) is None or _digest(snapshot) != sha):
            raise ValueError('Snapshot ausente ou hash divergente.')
        configuration = _text(record.get('configuration_version_id'), 'configuration_version_id')
        if (snapshot.get('unit_id') != unit_id or type(snapshot.get('exercise_id')) is not int
                or snapshot.get('exercise_id') != context[0] or snapshot.get('team') != context[1]
                or snapshot.get('configuration_version_id') != configuration):
            raise ValueError('Identidade/contexto/configuração do snapshot divergentes.')
        ready = snapshot.get('official_calculation_ready')
        if ready is not None and type(ready) is not bool:
            raise ValueError('Estado de aprovação do provedor inválido.')
        kind = snapshot.get('source_kind')
        if kind is not None:
            _text(kind, 'source_kind')
        ref = dict(unit_id=unit_id, snapshot_id=_text(record.get('snapshot_id'), 'snapshot_id'),
                   snapshot_sha256=sha, configuration_version_id=configuration,
                   source_kind=kind, official_calculation_ready=ready)
        refs.append(ref)
        projection.append(dict(**ref, exercise_id=context[0], team=context[1], domain=domain,
                               allocated=True, domain_evidence=deepcopy(evidence)))
    return refs, _digest(projection)


class RegistroGrupamentos:
    """Registro síncrono e thread-safe no mesmo processo; sem persistência."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._state = {'groups': {}, 'receipts': {}, 'owners': {}}

    def _replay(self, context, operation, pedido):
        receipt = self._state['receipts'].get(context + (pedido['command_id'],))
        if receipt is None:
            return None
        saved = json.loads(receipt)
        if saved['intent'] != _digest({'operation': operation, 'request': pedido}):
            raise GroupConflict('Comando já usado para outra intenção.')
        return saved['result']

    def _get(self, context, group_id, revision=None):
        versions = self._state['groups'].get(context + (group_id,))
        if not versions:
            raise KeyError('Grupamento não encontrado neste contexto.')
        if revision is None:
            return json.loads(versions[-1])
        if type(revision) is not int or revision < 1:
            raise ValueError('Revisão deve ser inteiro positivo.')
        if revision > len(versions):
            raise KeyError('Revisão não encontrada neste contexto.')
        return json.loads(versions[revision - 1])

    def _check_owners(self, context, members, own_group=None):
        for member in members:
            owner = self._state['owners'].get(context + (member['unit_id'],))
            if owner is not None and owner != own_group:
                raise GroupConflict('Integrante já possui vínculo operativo direto ativo.')

    def _version(self, context, group_id, revision, pedido, members, inventory_sha, *, active=True):
        result = dict(schema_version='siscan-unit-group-01', group_id=group_id,
                      exercise_id=context[0], team=context[1], composition_revision=revision,
                      designation=pedido['designation'], domain=pedido['domain'], active=active,
                      organization_label=pedido['organization_label'], mpnl_binding=deepcopy(pedido['mpnl_binding']),
                      members=deepcopy(members), inventory_snapshot_sha256=inventory_sha)
        result['composition_sha256'] = _digest(result)
        return result

    def _publish(self, state, context, operation, pedido, version):
        key = context + (version['group_id'],)
        state['groups'][key] = state['groups'].get(key, ()) + (_encode(version),)
        state['receipts'][context + (pedido['command_id'],)] = _encode({
            'intent': _digest({'operation': operation, 'request': pedido}), 'result': version})
        self._state = state
        return deepcopy(version)

    def criar_grupamento(self, contexto: dict, inventario: dict, pedido: dict) -> dict:
        """Cria revisão 1 com referências verificadas, sem alterar as unidades."""
        context, request = _context(contexto), _normalizar_composicao(pedido)
        with self._lock:
            replay = self._replay(context, 'create', request)
            if replay is not None:
                return replay
            members, inventory_sha = _members(context, inventario, request['member_unit_ids'], request['domain'])
            self._check_owners(context, members)
            group_id = str(uuid.uuid4())
            version = self._version(context, group_id, 1, request, members, inventory_sha)
            state = deepcopy(self._state)
            for member in members:
                state['owners'][context + (member['unit_id'],)] = group_id
            return self._publish(state, context, 'create', request, version)

    def consultar_grupamento(self, contexto: dict, group_id: str, revision: int | None = None) -> dict:
        """Consulta revisão explícita ou atual somente dentro do contexto."""
        context, group_id = _context(contexto), _uuid(group_id, 'group_id')
        with self._lock:
            return self._get(context, group_id, revision)

    def _current(self, context, group_id, expected_revision):
        current = self._get(context, group_id)
        if current['composition_revision'] != expected_revision:
            raise GroupConflict('Composição alterada; consulte a revisão atual.')
        if not current['active']:
            raise GroupConflict('Grupo arquivado não permite essa operação.')
        return current

    def _release(self, state, context, version):
        for member in version['members']:
            state['owners'].pop(context + (member['unit_id'],), None)

    def revisar_grupamento(self, contexto: dict, inventario: dict, pedido: dict) -> dict:
        """Publica nova revisão e troca vínculos no mesmo estado protegido."""
        context, request = _context(contexto), _normalizar_composicao(pedido, revisao=True)
        with self._lock:
            replay = self._replay(context, 'revise', request)
            if replay is not None:
                return replay
            current = self._current(context, request['group_id'], request['expected_revision'])
            members, inventory_sha = _members(context, inventario, request['member_unit_ids'], request['domain'])
            self._check_owners(context, members, current['group_id'])
            version = self._version(context, current['group_id'], current['composition_revision'] + 1,
                                    request, members, inventory_sha)
            state = deepcopy(self._state)
            self._release(state, context, current)
            for member in members:
                state['owners'][context + (member['unit_id'],)] = version['group_id']
            return self._publish(state, context, 'revise', request, version)
