"""Dossiê didático de composições, sem executar combate ou publicar efeitos.

O provedor deve autorizar o instrutor e fornecer uma vista consistente do
inventário. Preparar não reserva disponibilidade futura ou autentica usuários.
"""

from collections.abc import Callable
from copy import deepcopy
import uuid

from unit_groups import RegistroGrupamentos


def preparar_dossie_grupamentos(
    *, exercise_id: int, autorizar_instrutor: Callable[[int], bool],
    registro: RegistroGrupamentos, inventarios: dict, selecao: dict,
) -> dict:
    """Confere dois partidos no registro e preserva seus snapshots individuais."""
    if type(exercise_id) is not int or exercise_id <= 0:
        raise ValueError('Exercício inválido.')
    if not callable(autorizar_instrutor):
        raise ValueError('Autorizador interno obrigatório.')
    if autorizar_instrutor(exercise_id) is not True:
        raise PermissionError('Preparação não autorizada para este exercício.')

    teams = ('AZUL', 'VERMELHO')
    if not isinstance(selecao, dict) or set(selecao) != set(teams):
        raise ValueError('Selecione exatamente AZUL e VERMELHO.')
    selection = deepcopy(selecao)
    for request in selection.values():
        if not isinstance(request, dict) or set(request) != {'group_id', 'expected_revision'}:
            raise ValueError('Informe grupo e revisão esperada.')
        gid, revision = request['group_id'], request['expected_revision']
        try:
            if not isinstance(gid, str) or str(uuid.UUID(gid)) != gid:
                raise ValueError()
        except (ValueError, AttributeError) as exc:
            raise ValueError('UUID canônico obrigatório.') from exc
        if type(revision) is not int or revision <= 0:
            raise ValueError('Revisão positiva obrigatória.')
    if (not isinstance(inventarios, dict) or set(inventarios) != set(teams)
            or any(not isinstance(inventarios[team], dict) for team in teams)):
        raise ValueError('Informe uma visão de inventário por partido.')
    inventory = deepcopy(inventarios)
    parties = []
    for team in teams:
        context = dict(exercise_id=exercise_id, team=team)
        composition = registro.preparar_composicao(context, inventory[team], **selection[team])
        snapshots = {member['unit_id']: deepcopy(inventory[team][member['unit_id']]['snapshot'])
                     for member in composition['members']}
        parties.append(dict(team=team, composition=composition, snapshots=snapshots))

    return dict(schema_version='siscan-cpc-group-preparation-01', exercise_id=exercise_id,
                parties=parties, status='requires_instructor_review',
                simulation_started=False, official_calculation_ready=False)
