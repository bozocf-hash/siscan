"""Ponte autorizada entre unidades individuais e o mapa, sem criar instâncias."""
from contextlib import contextmanager
import uuid

import engine_units
import map_units

WARNING = 'Grupamentos temporários: composições e histórico se perdem ao reiniciar o servidor.'


@contextmanager
def _read_view(db):
    db.execute('SAVEPOINT map_groups_view')
    try:
        yield
        db.execute('RELEASE map_groups_view')
    except Exception:
        db.execute('ROLLBACK TO map_groups_view')
        db.execute('RELEASE map_groups_view')
        raise


def _controlled_domain(db, unit):
    return engine_units.configuration_domain(db, unit)


def view(db, user: dict, team: str) -> dict:
    """Vista SQL consistente do partido; não reserva disponibilidade futura."""
    with _read_view(db):
        exercise = map_units.context(db, user, team)
        assets = map_units.listing(db, user, team)['units']
        instances = {u['asset_id']: u for u in engine_units.list_units(db, user)['units']
                     if u['team'] == team and u['allocated']}
        inventory, units = {}, []
        for asset in assets:
            instance = instances.get(asset['id'])
            evidence = _controlled_domain(db, instance) if instance else None
            item = dict(asset_id=asset['id'], unit_id=instance['unit_id'] if instance else None,
                        code=asset['code'], name=asset['name'], latitude=asset['latitude'],
                        longitude=asset['longitude'], position_revision=asset['position_revision'],
                        eligible=evidence is not None, domain=evidence['domain'] if evidence else None,
                        reason=None if evidence else ('Snapshot/instância não disponível.' if not instance
                                                     else 'Domínio/configuração sem mapeamento demonstrado.'))
            units.append(item)
            if evidence:
                uid = instance['unit_id']
                inventory[uid] = dict(unit_id=uid, exercise_id=exercise['id'], team=team,
                    domain=evidence['domain'], domain_evidence=evidence, allocated=True,
                    snapshot_id=instance['snapshot_id'], snapshot_sha256=instance['snapshot_sha256'],
                    configuration_version_id=instance['configuration_version_id'], snapshot=instance['snapshot'])
        return dict(context=dict(exercise_id=exercise['id'], team=team),
                    exercise_open=exercise['state'] == 'open', inventory=inventory, units=units)


def _project(group, current):
    visible = {u['unit_id']: u for u in current['units'] if u['unit_id'] is not None}
    members, unavailable, needs_review = [], 0, False
    for ref in group['members']:
        unit = visible.get(ref['unit_id'])
        if unit is None:
            unavailable += 1
            needs_review = True
            continue
        record = current['inventory'].get(ref['unit_id'])
        matches = record and all(record[field] == ref[field]
                                 for field in ('snapshot_id', 'snapshot_sha256', 'configuration_version_id'))
        member = dict(unit)
        if not matches:
            member.update(eligible=False, reason='Referências atuais exigem conferência da composição.')
            needs_review = True
        members.append(member)
    return dict(group_id=group['group_id'], designation=group['designation'], domain=group['domain'],
                composition_revision=group['composition_revision'], active=group['active'],
                members=members, unavailable_count=unavailable, needs_review=needs_review)


def listing(db, user, team, registro):
    current = view(db, user, team)
    groups = registro.listar_grupamentos(current['context'])
    owners = {m['unit_id'] for g in groups if g['active'] for m in g['members']}
    for unit in current['units']:
        unit['in_active_group'] = unit['unit_id'] in owners
    return dict(team=team, storage='memory', warning=WARNING, exercise_open=current['exercise_open'],
                units=current['units'], groups=[_project(g, current) for g in groups])


def command(db, user, registro, body, *, group_id=None):
    """Comando em memória; todo retorno recebe projeção autorizada atual."""
    fields = ({'team', 'command_id', 'designation', 'domain', 'member_unit_ids'} if group_id is None
              else {'team', 'command_id', 'expected_revision'})
    if not isinstance(body, dict) or set(body) != fields:
        raise ValueError('Campos do comando de grupamento inválidos.')
    current = view(db, user, body['team'])
    if not current['exercise_open']:
        raise ValueError('Exercício encerrado; composição recusada.')
    request = {k: v for k, v in body.items() if k != 'team'}
    if group_id is None:
        group = registro.criar_grupamento(current['context'], current['inventory'], request)
    else:
        request['group_id'] = group_id
        group = registro.arquivar_grupamento(current['context'], request)
    fresh = view(db, user, body['team'])
    return dict(storage='memory', warning=WARNING, group=_project(group, fresh))
