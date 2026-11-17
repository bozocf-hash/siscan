"""Estado operativo didático; avaliação de origem distinta dos recursos."""
import math
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
import engine_units
import operational_state_storage as storage
from engine_runtime import atomic, Conflict


def _fields(value,required,optional=()):
    if not isinstance(value,dict) or not set(required)<=set(value) or set(value)-set(required)-set(optional):
        raise ValueError('Campos de comando inválidos.')


def _uuid(value):
    try:
        if not isinstance(value,str) or str(uuid.UUID(value))!=value:raise ValueError()
    except (ValueError,AttributeError) as exc:raise ValueError('Identificador UUID inválido.') from exc


def _reason(value):
    if not isinstance(value,str) or not value.strip() or len(value)>4000:
        raise ValueError('Justificativa obrigatória, até 4000 caracteres.')


def _command(db,user,payload,operation,required,optional=()):
    exercise=_context(db,user,write=True);storage.validate(db)
    _fields(payload,{'command_id',*required},optional);_uuid(payload['command_id'])
    try:
        if len(engine_units.encoded(payload).encode('utf-8'))>64000:raise ValueError('Comando excede 64 KB.')
    except (TypeError,OverflowError) as exc:raise ValueError('Conteúdo JSON inválido.') from exc
    row=db.execute('SELECT * FROM operational_commands WHERE command_id=?',(payload['command_id'],)).fetchone()
    if row:
        _checked_json(row['payload_json'],row['payload_sha256'])
        if (row['exercise_id']!=exercise['id'] or row['actor_id']!=user['uid'] or row['operation']!=operation
                or row['payload_json']!=engine_units.encoded(payload)):
            raise Conflict('Comando já usado com outro conteúdo/contexto.')
        return exercise,_checked_json(row['result_json'],row['result_sha256'])
    return exercise,None


def _receipt(db,user,exercise,payload,operation,result):
    db.execute('INSERT INTO operational_commands VALUES(?,?,?,?,?,?,?,?,?)',
        (payload['command_id'],exercise['id'],user['uid'],operation,engine_units.encoded(payload),_digest(payload),
         engine_units.encoded(result),_digest(result),datetime.now(timezone.utc).isoformat()))
    return result


def _effects(db,user,effects,exercise):
    if not isinstance(effects,list) or not 1<=len(effects)<=100:raise ValueError('Informe de 1 a 100 efeitos.')
    seen=set();captured=[]
    for item in effects:
        _fields(item,{'unit_id','expected_state_revision','snapshot_id','snapshot_sha256','configuration_version_id','changes'})
        if not isinstance(item['unit_id'],str) or item['unit_id'] in seen:raise ValueError('Unidade inválida ou duplicada.')
        seen.add(item['unit_id'])
        expected=item['expected_state_revision']
        if type(expected) is not int or expected<0:raise ValueError('Revisão de estado inválida.')
        changes=validar_alteracoes(item['changes']);unit=_unit(db,user,item['unit_id'])
        for key in ('snapshot_id','snapshot_sha256','configuration_version_id'):
            if item[key]!=unit[key]:raise Conflict('Referência técnica incompatível; atualize a proposta.')
        history=_chain(db,unit);current=history[-1]['after'] if history else _initial(db,unit)
        if current['revision']!=expected:raise Conflict('Estado operativo alterado; atualize a proposta.')
        evidence=engine_units.configuration_domain(db,unit)
        refs={k:unit[k] for k in ('unit_id','team','snapshot_id','snapshot_sha256','configuration_version_id')}
        refs.update(exercise_id=exercise['id'],domain_evidence=evidence)
        captured.append(dict(refs=refs,expected_state_revision=expected,changes=changes))
    return sorted(captured,key=lambda e:e['refs']['unit_id'])


def _body(db,user,payload,exercise):
    if payload['source']!='didactic':raise ValueError('Fonte aceita nesta fatia: didactic.')
    _reason(payload['reason'])
    if not isinstance(payload['origin'],dict) or not payload['origin']:raise ValueError('Referência de origem obrigatória.')
    return dict(scenario_version=exercise['scenario_version'],reason=payload['reason'],origin=payload['origin'],
                effects=_effects(db,user,payload['effects'],exercise))


def _save_revision(db,user,exercise,proposal_id,revision,body):
    sha=_digest(body)
    db.execute('INSERT INTO operational_proposal_revisions VALUES(?,?,?,?,?,?,?,?)',
        (proposal_id,exercise['id'],revision,exercise['scenario_version'],engine_units.encoded(body),sha,
         user['uid'],datetime.now(timezone.utc).isoformat()))
    return dict(proposal_id=proposal_id,revision=revision,body_sha256=sha,body=body)


def registrar_proposta(db,user,payload):
    """Grava somente proposta/recibo. Em transação externa, commit é do chamador."""
    _context(db,user,write=True)
    with atomic(db):
        exercise,replay=_command(db,user,payload,'register',{'source','reason','origin','effects'},{'correction_decision_id'})
        if replay is not None:return replay
        body=_body(db,user,payload,exercise);correction=payload.get('correction_decision_id')
        if correction is not None:
            _uuid(correction)
            prior=db.execute('''SELECT d.action,p.exercise_id FROM operational_decisions d JOIN operational_proposals p
              ON p.proposal_id=d.proposal_id WHERE d.decision_id=?''',(correction,)).fetchone()
            if not prior or prior['exercise_id']!=exercise['id'] or prior['action']!='confirm':
                raise Conflict('Decisão corrigida não encontrada neste exercício.')
        proposal_id=str(uuid.uuid4())
        db.execute('INSERT INTO operational_proposals VALUES(?,?,?,?,?,?)',
            (proposal_id,exercise['id'],'didactic',user['uid'],datetime.now(timezone.utc).isoformat(),correction))
        result=_save_revision(db,user,exercise,proposal_id,1,body)
        return _receipt(db,user,exercise,payload,'register',result)


def _proposal(db,exercise,payload):
    _uuid(payload['proposal_id'])
    if type(payload['expected_revision']) is not int or payload['expected_revision']<1:
        raise ValueError('Revisão de proposta inválida.')
    root=db.execute('SELECT * FROM operational_proposals WHERE proposal_id=? AND exercise_id=?',
                    (payload['proposal_id'],exercise['id'])).fetchone()
    if root is None:raise PermissionError('Proposta não disponível neste contexto.')
    if db.execute('SELECT 1 FROM operational_decisions WHERE proposal_id=?',(root['proposal_id'],)).fetchone():
        raise Conflict('Proposta já decidida.')
    revision=db.execute('SELECT * FROM operational_proposal_revisions WHERE proposal_id=? ORDER BY revision DESC LIMIT 1',
                        (root['proposal_id'],)).fetchone()
    if revision is None:raise sqlite3.DatabaseError('Missing proposal revision.')
    body=_checked_json(revision['body_json'],revision['body_sha256'])
    if revision['revision']!=payload['expected_revision'] or revision['body_sha256']!=payload['expected_sha256']:
        raise Conflict('Revisão/hash da proposta alterados.')
    return root,revision,body


def revisar_proposta(db,user,payload):
    _context(db,user,write=True)
    with atomic(db):
        exercise,replay=_command(db,user,payload,'revise',
            {'proposal_id','expected_revision','expected_sha256','source','reason','origin','effects'})
        if replay is not None:return replay
        root,revision,old_body=_proposal(db,exercise,payload)
        body=_body(db,user,payload,exercise)
        result=_save_revision(db,user,exercise,root['proposal_id'],revision['revision']+1,body)
        return _receipt(db,user,exercise,payload,'revise',result)


def decidir_proposta(db,user,payload):
    _context(db,user,write=True)
    with atomic(db):
        exercise,replay=_command(db,user,payload,'decide',
            {'proposal_id','expected_revision','expected_sha256','action','reason'})
        if replay is not None:return replay
        if payload['action']!='reject':raise ValueError('Ação de decisão inválida.')
        _reason(payload['reason']);root,revision,body=_proposal(db,exercise,payload)
        decision_id=str(uuid.uuid4())
        db.execute('INSERT INTO operational_decisions VALUES(?,?,?,?,?,?,?,?,?)',
            (decision_id,root['proposal_id'],revision['revision'],revision['body_sha256'],payload['action'],
             payload['reason'],user['uid'],datetime.now(timezone.utc).isoformat(),payload['command_id']))
        result=dict(proposal_id=root['proposal_id'],revision=revision['revision'],body_sha256=revision['body_sha256'],
                    decision_id=decision_id,action=payload['action'],effects=[])
        return _receipt(db,user,exercise,payload,'decide',result)


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
