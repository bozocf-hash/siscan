"""Estado operativo didático; avaliação de origem distinta dos recursos."""
import math
import hashlib
import json
import sqlite3
from contextlib import contextmanager
import engine_units
import operational_state_storage as storage


def _digest(value):return hashlib.sha256(engine_units.encoded(value).encode('utf-8')).hexdigest()


def _context(db,user,write=False):
    actor=db.execute('SELECT role,team,active FROM users WHERE id=?',(user['uid'],)).fetchone()
    if not actor or not actor['active'] or actor['role']!=user['role'] or actor['team']!=user.get('team'):
        raise PermissionError('Participante não autorizado.')
    return engine_units.context(db,user,write=write)


@contextmanager
def _view(db):
    db.execute('SAVEPOINT operational_view')
    try:
        yield
        db.execute('RELEASE operational_view')
    except Exception:
        db.execute('ROLLBACK TO operational_view');db.execute('RELEASE operational_view');raise


def _unit(db,user,unit_id):
    row=db.execute('SELECT exercise_id,team FROM engine_units WHERE unit_id=?',(unit_id,)).fetchone()
    exercise=_context(db,user)
    if not row or row['exercise_id']!=exercise['id'] or (user['role']!='instructor' and row['team']!=user['team']):
        raise PermissionError('Unidade não autorizada neste contexto.')
    unit=next((u for u in engine_units.list_units(db,user)['units'] if u['unit_id']==unit_id and u['allocated']),None)
    if unit is None:raise PermissionError('Unidade sem identidade/adjudicação disponível.')
    return unit


def _initial(db,unit):
    evidence=engine_units.configuration_domain(db,unit)
    return dict(revision=0,index_percent=None,lost=None,domain=evidence['domain'] if evidence else None)


def _checked_json(text,sha):
    try:
        value=json.loads(text)
        if _digest(value)!=sha or engine_units.encoded(value)!=text:raise ValueError()
        return value
    except (ValueError,TypeError,OverflowError) as exc:
        raise sqlite3.DatabaseError('Operational content integrity mismatch.') from exc


def _chain(db,unit):
    rows=db.execute('''SELECT e.*,d.action,d.actor_id,d.created_at,d.reason FROM operational_effects e
      JOIN operational_decisions d ON d.decision_id=e.decision_id
      WHERE e.unit_id=? ORDER BY e.revision''',(unit['unit_id'],)).fetchall()
    previous=None;history=[]
    for row in rows:
        before=_checked_json(row['before_json'],row['before_sha256'])
        after=_checked_json(row['after_json'],row['after_sha256'])
        refs=_checked_json(row['refs_json'],row['refs_sha256'])
        if (row['action']!='confirm' or row['team']!=unit['team'] or before['revision']!=len(history)
                or row['revision']!=len(history)+1 or after['revision']!=row['revision']
                or (previous is not None and before!=previous)
                or refs['unit_id']!=unit['unit_id'] or refs['snapshot_id']!=row['snapshot_id']):
            raise sqlite3.DatabaseError('Operational effect chain mismatch.')
        validar_alteracoes({'index_percent':after['index_percent']})
        history.append(dict(decision_id=row['decision_id'],actor_id=row['actor_id'],created_at=row['created_at'],
                            reason=row['reason'],before=before,after=after))
        previous=after
    return history


def consultar(db,user,unit_id):
    with _view(db):
        exercise=_context(db,user);unit=_unit(db,user,unit_id);storage.validate(db)
        history=_chain(db,unit);current=history[-1]['after'] if history else _initial(db,unit)
        origin={k:history[-1][k] for k in ('decision_id','actor_id','created_at')} if history else None
        return dict(exercise_id=exercise['id'],unit_id=unit_id,team=unit['team'],state=current,
                    condition=None if current['lost'] else classificar(current['domain'],current['index_percent']),
                    origin=origin,resource_restrictions='not_evaluated')


def historico(db,user,unit_id):
    with _view(db):
        _context(db,user);unit=_unit(db,user,unit_id);storage.validate(db)
        history=_chain(db,unit)
        if user['role']!='instructor':
            for item in history:item.pop('reason')
        return history


def validar_alteracoes(changes):
    if not isinstance(changes,dict) or not changes or set(changes)-{'index_percent','lost'}:
        raise ValueError('Informe índice e/ou declaração explícita de perda.')
    if 'index_percent' in changes:
        value=changes['index_percent']
        if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=100):
            raise ValueError('Índice deve ser número finito entre 0 e 100 ou null.')
    if 'lost' in changes and type(changes['lost']) is not bool:
        raise ValueError('Declaração de perda deve ser booleana.')
    return dict(changes)


def classificar(domain, index):
    validar_alteracoes({'index_percent':index})
    if domain!='superficie' or index is None:return None
    return 'combater' if index>60 else 'navegar' if index>=40 else 'flutuar'
