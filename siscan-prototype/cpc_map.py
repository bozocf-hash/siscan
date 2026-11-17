"""Seleção/conferência de duas composições no mapa, sem execução ou efeitos."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib

import engine_units
import map_groups
from cpc_group_preparation import preparar_dossie_grupamentos
from unit_groups import GroupConflict

TEAMS = ('AZUL', 'VERMELHO')


def _context(db, user):
    if user['role'] != 'instructor':
        raise PermissionError('A conferência dos dois partidos é exclusiva do instrutor.')
    exercise = engine_units.context(db, user)
    return dict(exercise_id=exercise['id'], scenario_version=exercise['scenario_version'],
                exercise_open=exercise['state'] == 'open')


@contextmanager
def _read_sql_view(db):
    db.execute('SAVEPOINT cpc_map_view')
    try:
        yield
        db.execute('RELEASE cpc_map_view')
    except Exception:
        db.execute('ROLLBACK TO cpc_map_view')
        db.execute('RELEASE cpc_map_view')
        raise


def _capture(db, user):
    with _read_sql_view(db):
        context = _context(db, user)
        views = {team: map_groups.view(db, user, team) for team in TEAMS}
        if any(v['context']['exercise_id'] != context['exercise_id'] for v in views.values()):
            raise GroupConflict('Contexto alterado durante a conferência.')
        return context, views


def listing(db, user, registro):
    """Lista de grupos elegíveis; não seleciona automaticamente um par."""
    with _read_sql_view(db):
        context = _context(db, user)
        parties = []
        for team in TEAMS:
            current = map_groups.listing(db, user, team, registro)
            groups = []
            for group in current['groups']:
                ready = group['active'] and not group['needs_review'] and bool(group['members'])
                groups.append(dict(group_id=group['group_id'], designation=group['designation'],
                    domain=group['domain'], composition_revision=group['composition_revision'],
                    preparable=ready, reason=None if ready else 'Grupo arquivado ou referências indisponíveis; atualize a composição.'))
            parties.append(dict(team=team, groups=groups))
        return dict(**context, parties=parties, storage='memory', warning=map_groups.WARNING)


def _digest(value):
    return hashlib.sha256(engine_units.encoded(value).encode('utf-8')).hexdigest()


def _metadata(registro, context, dossier):
    groups = {}
    for party in dossier['parties']:
        ref = party['composition']
        current = registro.consultar_grupamento(dict(exercise_id=context['exercise_id'], team=party['team']), ref['group_id'])
        if (not current['active'] or current['composition_revision'] != ref['composition_revision']
                or current['composition_sha256'] != ref['composition_sha256']):
            raise GroupConflict('Composição alterada durante a conferência.')
        groups[party['team']] = current
    return groups


def _project(context, views, dossier, metadata):
    parties, positions = [], []
    for party in dossier['parties']:
        team = party['team']
        composition = party['composition']
        source = {u['unit_id']: u for u in views[team]['units'] if u['unit_id'] is not None}
        members = []
        for ref in composition['members']:
            unit = source.get(ref['unit_id'])
            record = views[team]['inventory'].get(ref['unit_id'])
            if unit is None or record is None or any(record[key] != ref[key]
                    for key in ('snapshot_id', 'snapshot_sha256', 'configuration_version_id')):
                raise GroupConflict('Referências do integrante alteradas durante a conferência.')
            member = {key: unit[key] for key in ('unit_id','asset_id','code','name','domain',
                                                'latitude','longitude','position_revision')}
            member.update(deepcopy(ref), current_logistics=None, snapshot_scope='initial_configuration')
            members.append(member)
            positions.append(dict(exercise_id=context['exercise_id'], scenario_version=context['scenario_version'],
                team=team, **{key: unit[key] for key in ('unit_id','asset_id','latitude','longitude','position_revision')}))
        group = metadata[team]
        parties.append(dict(team=team, group_id=group['group_id'],
            designation=group['designation'], domain=group['domain'],
            composition_revision=group['composition_revision'], composition_sha256=group['composition_sha256'],
            members=members))
    result = dict(schema_version='siscan-cpc-map-preparation-01', **context,
                  dossier_sha256=dossier['preparation_sha256'], parties=parties,
                  positions_sha256=_digest(positions), status='requires_instructor_review',
                  simulation_started=False, official_calculation_ready=False, official_effects_applied=False,
                  position_scope='planning_positions', storage='memory', warning=map_groups.WARNING)
    result['view_sha256'] = _digest(result)
    return result


def prepare(db, user, registro, selection):
    """Prepara uma vista; não publica grupo, posição, recurso ou resultado."""
    _context(db, user)
    context, views = _capture(db, user)
    if not context['exercise_open']:
        raise ValueError('Exercício encerrado; preparação recusada.')
    dossier = preparar_dossie_grupamentos(exercise_id=context['exercise_id'],
        autorizar_instrutor=lambda exercise_id: exercise_id == context['exercise_id'],
        registro=registro, inventarios={team: views[team]['inventory'] for team in TEAMS}, selecao=selection)
    result = _project(context, views, dossier, _metadata(registro, context, dossier))
    # Fontes têm transações/locks próprios; esta conferência não reserva estado.
    fresh_context, fresh_views = _capture(db, user)
    fresh = _project(fresh_context, fresh_views, dossier, _metadata(registro, fresh_context, dossier))
    if result != fresh:
        raise GroupConflict('Dados ou posições alterados; prepare novamente o par.')
    return result
