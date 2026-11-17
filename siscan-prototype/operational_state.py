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
        root,revision,_=_proposal(db,exercise,payload)
        body=_body(db,user,payload,exercise)
        result=_save_revision(db,user,exercise,root['proposal_id'],revision['revision']+1,body)
        return _receipt(db,user,exercise,payload,'revise',result)


def decidir_proposta(db,user,payload):
    _context(db,user,write=True)
    with atomic(db):
        exercise,replay=_command(db,user,payload,'decide',
            {'proposal_id','expected_revision','expected_sha256','action','reason'})
        if replay is not None:return replay
        if payload['action'] not in ('confirm','reject'):raise ValueError('Ação de decisão inválida.')
        _reason(payload['reason']);root,revision,body=_proposal(db,exercise,payload)
        if payload['action']=='confirm':
            if body['scenario_version']!=exercise['scenario_version']:raise Conflict('Cenário alterado; revise a proposta.')
            source=[dict(unit_id=e['refs']['unit_id'],expected_state_revision=e['expected_state_revision'],
                         **{k:e['refs'][k] for k in ('snapshot_id','snapshot_sha256','configuration_version_id')},
                         changes=e['changes']) for e in body['effects']]
            if _effects(db,user,source,exercise)!=body['effects']:raise Conflict('Fonte da proposta alterada.')
        decision_id=str(uuid.uuid4())
        effect_rows,effects=_prepare_effects(db,user,exercise,root,body,decision_id) if payload['action']=='confirm' else ([],[])
        db.execute('INSERT INTO operational_decisions VALUES(?,?,?,?,?,?,?,?,?)',
            (decision_id,root['proposal_id'],revision['revision'],revision['body_sha256'],payload['action'],
             payload['reason'],user['uid'],datetime.now(timezone.utc).isoformat(),payload['command_id']))
        db.executemany('INSERT INTO operational_effects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',effect_rows)
        result=dict(proposal_id=root['proposal_id'],revision=revision['revision'],body_sha256=revision['body_sha256'],
                    decision_id=decision_id,action=payload['action'],effects=effects)
        return _receipt(db,user,exercise,payload,'decide',result)


def _prepare_effects(db,user,exercise,root,body,decision_id):
    results=_calculate_effects(db,user,body['effects'],root['correction_decision_id']);rows=[]
    for effect,result in zip(body['effects'],results):
        refs=effect['refs'];before=result['before'];after=result['after']
        rows.append((decision_id,refs['unit_id'],exercise['id'],refs['team'],after['revision'],before['revision'],refs['snapshot_id'],
             engine_units.encoded(refs),_digest(refs),engine_units.encoded(before),_digest(before),
             engine_units.encoded(after),_digest(after)))
    return rows,results


def _calculate_effects(db,user,effects,correction):
    results=[]
    for effect in effects:
        refs=effect['refs'];unit=_unit(db,user,refs['unit_id']);history=_chain(db,unit)
        before=history[-1]['after'] if history else _initial(db,unit)
        changes=effect['changes']
        if before['lost'] is True and changes.get('lost') is False:
            if correction!=history[-1]['decision_id']:
                raise Conflict('Recuperação exige referência à decisão do estado atual.')
        evidence=refs['domain_evidence']
        after=dict(before,**changes);after.update(revision=before['revision']+1,domain=evidence['domain'] if evidence else None)
        results.append(dict(unit_id=unit['unit_id'],before=before,after=after))
    return results


def autorizar_instrutor(db,user,write=False):
    exercise=_context(db,user,write=write)
    if user['role']!='instructor':raise PermissionError('Operação exclusiva do instrutor.')
    return dict(exercise)


def prever_efeitos(db,user,effects,correction_decision_id=None):
    with _view(db):
        exercise=autorizar_instrutor(db,user,write=True);storage.validate(db)
        return _calculate_effects(db,user,_effects(db,user,effects,exercise),correction_decision_id)


def consultar_recibo(db,user,command_id):
    with _view(db):
        exercise=autorizar_instrutor(db,user);storage.validate(db);_uuid(command_id)
        row=db.execute('SELECT * FROM operational_commands WHERE command_id=?',(command_id,)).fetchone()
        if row is None:return None
        if row['exercise_id']!=exercise['id'] or row['actor_id']!=user['uid']:
            raise PermissionError('Recibo indisponível para este participante.')
        return dict(operation=row['operation'],payload=_checked_json(row['payload_json'],row['payload_sha256']),
                    result=_checked_json(row['result_json'],row['result_sha256']))


def consultar_proposta(db,user,proposal_id):
    with _view(db):
        exercise=autorizar_instrutor(db,user);storage.validate(db);_uuid(proposal_id)
        root=db.execute('SELECT * FROM operational_proposals WHERE proposal_id=? AND exercise_id=?',
                        (proposal_id,exercise['id'])).fetchone()
        if root is None:raise KeyError('Proposta não encontrada neste exercício.')
        revisions=[]
        for row in db.execute('SELECT * FROM operational_proposal_revisions WHERE proposal_id=? ORDER BY revision',(proposal_id,)):
            if row['revision']!=len(revisions)+1:raise sqlite3.DatabaseError('Proposal revision chain mismatch.')
            revisions.append(dict(revision=row['revision'],body_sha256=row['body_sha256'],
                                  body=_checked_json(row['body_json'],row['body_sha256']),created_at=row['created_at']))
        if not revisions:raise sqlite3.DatabaseError('Missing proposal revision.')
        decision=db.execute('SELECT * FROM operational_decisions WHERE proposal_id=?',(proposal_id,)).fetchone()
        receipt=None
        if decision:
            row=db.execute('SELECT * FROM operational_commands WHERE command_id=?',(decision['command_id'],)).fetchone()
            if row is None:raise sqlite3.DatabaseError('Missing decision receipt.')
            _checked_json(row['payload_json'],row['payload_sha256']);receipt=_checked_json(row['result_json'],row['result_sha256'])
            if receipt['decision_id']!=decision['decision_id']:raise sqlite3.DatabaseError('Decision receipt mismatch.')
        return dict(root, current=revisions[-1],revisions=revisions,decision=dict(decision) if decision else None,receipt=receipt)


def listar_propostas(db,user,*,limit=20,cursor=0,origin_schema=None):
    with _view(db):
        exercise=autorizar_instrutor(db,user);storage.validate(db)
        if type(limit) is not int or not 1<=limit<=50 or type(cursor) is not int or cursor<0:
            raise ValueError('Paginação inválida.')
        rows=db.execute('SELECT rowid,proposal_id FROM operational_proposals WHERE exercise_id=? AND rowid>? ORDER BY rowid LIMIT ?',
                        (exercise['id'],cursor,limit+1)).fetchall()
        items=[]
        for row in rows[:limit]:
            view=consultar_proposta(db,user,row['proposal_id'])
            if origin_schema and view['current']['body']['origin'].get('schema_version')!=origin_schema:continue
            items.append(dict(proposal_id=view['proposal_id'],revision=view['current']['revision'],
                body_sha256=view['current']['body_sha256'],reason=view['current']['body']['reason'],
                status=view['decision']['action'] if view['decision'] else 'pending',created_at=view['created_at']))
        return dict(items=items,next_cursor=rows[limit-1]['rowid'] if len(rows)>limit else None)


def _digest(value):return hashlib.sha256(engine_units.encoded(value).encode('utf-8')).hexdigest()


def _context(db,user,write=False):
    actor=db.execute('SELECT role,team,active FROM users WHERE id=?',(user['uid'],)).fetchone()
    if not actor or not actor['active'] or actor['role']!=user['role'] or actor['team']!=dict(user).get('team'):
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
    exercise=_context(db,user)
    row=db.execute('SELECT exercise_id,team FROM engine_units WHERE unit_id=?',(unit_id,)).fetchone()
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
        if not isinstance(value,dict) or _digest(value)!=sha or engine_units.encoded(value)!=text:raise ValueError()
        return value
    except (ValueError,TypeError,OverflowError) as exc:
        raise sqlite3.DatabaseError('Operational content integrity mismatch.') from exc


def _chain(db,unit):
    rows=db.execute("""SELECT e.*,d.action,d.actor_id,d.created_at,d.reason,d.proposal_id,d.revision AS proposal_revision,
      r.body_json,r.body_sha256,c.payload_json,c.payload_sha256,c.result_json,c.result_sha256,
      c.actor_id AS command_actor,c.exercise_id AS command_exercise,c.operation
      FROM operational_effects e JOIN operational_decisions d ON d.decision_id=e.decision_id
      JOIN operational_proposal_revisions r ON r.proposal_id=d.proposal_id AND r.revision=d.revision
      JOIN operational_commands c ON c.command_id=d.command_id
      WHERE e.unit_id=? ORDER BY e.revision""",(unit['unit_id'],)).fetchall()
    # Detectar efeito removido sem transformar histórico confirmado em ausência.
    expected=db.execute("""SELECT d.decision_id,r.body_json,r.body_sha256 FROM operational_decisions d
      JOIN operational_proposal_revisions r ON r.proposal_id=d.proposal_id AND r.revision=d.revision
      WHERE r.exercise_id=? AND d.action='confirm' AND instr(r.body_json,?)>0""",
      (db.execute('SELECT exercise_id FROM engine_units WHERE unit_id=?',(unit['unit_id'],)).fetchone()[0],
       '"unit_id":'+engine_units.encoded(unit['unit_id']))).fetchall()
    expected_ids=set()
    try:
        for row in expected:
            body=_checked_json(row['body_json'],row['body_sha256'])
            if any(e['refs']['unit_id']==unit['unit_id'] for e in body['effects']):expected_ids.add(row['decision_id'])
    except (KeyError,TypeError) as exc:
        raise sqlite3.DatabaseError('Invalid confirmed proposal content.') from exc
    if expected_ids!={row['decision_id'] for row in rows}:
        raise sqlite3.DatabaseError('Missing operational effect.')
    previous=None;history=[]
    try:
        for row in rows:
            before=_checked_json(row['before_json'],row['before_sha256'])
            after=_checked_json(row['after_json'],row['after_sha256'])
            refs=_checked_json(row['refs_json'],row['refs_sha256'])
            body=_checked_json(row['body_json'],row['body_sha256'])
            command=_checked_json(row['payload_json'],row['payload_sha256'])
            receipt=_checked_json(row['result_json'],row['result_sha256'])
            source=next(e for e in body['effects'] if e['refs']['unit_id']==unit['unit_id'])
            evidence=refs['domain_evidence'];domain=evidence['domain'] if evidence else None
            for value in (before,after):
                if set(value)!={'revision','index_percent','lost','domain'} or type(value['revision']) is not int:
                    raise ValueError('Invalid state shape')
                validar_alteracoes({'index_percent':value['index_percent']})
                if value['lost'] is not None and type(value['lost']) is not bool:raise ValueError('Invalid loss')
            initial=dict(revision=0,index_percent=None,lost=None,domain=domain)
            calculated=dict(before,**validar_alteracoes(source['changes']))
            calculated.update(revision=len(history)+1,domain=domain)
            snapshot=db.execute('SELECT * FROM engine_unit_snapshots WHERE snapshot_id=?',(refs['snapshot_id'],)).fetchone()
            if (row['action']!='confirm' or row['team']!=unit['team'] or row['revision']!=len(history)+1
                    or row['before_revision']!=len(history) or before!=(previous if previous is not None else initial)
                    or after!=calculated or refs!=source['refs'] or source['expected_state_revision']!=before['revision']
                    or refs['unit_id']!=unit['unit_id'] or refs['team']!=unit['team'] or refs['exercise_id']!=row['exercise_id']
                    or refs['snapshot_id']!=row['snapshot_id'] or snapshot is None
                    or any(snapshot[k]!=refs[k] for k in ('unit_id','exercise_id','team','snapshot_sha256','configuration_version_id'))
                    or row['command_actor']!=row['actor_id'] or row['command_exercise']!=row['exercise_id']
                    or row['operation']!='decide' or command['action']!='confirm' or command['reason']!=row['reason']
                    or command['proposal_id']!=row['proposal_id'] or command['expected_revision']!=row['proposal_revision']
                    or command['expected_sha256']!=row['body_sha256'] or receipt['decision_id']!=row['decision_id']
                    or len(receipt['effects'])!=len(body['effects'])
                    or dict(unit_id=unit['unit_id'],before=before,after=after) not in receipt['effects']):
                raise ValueError('Inconsistent operational effect')
            history.append(dict(decision_id=row['decision_id'],actor_id=row['actor_id'],created_at=row['created_at'],
                                reason=row['reason'],before=before,after=after))
            previous=after
    except (KeyError,TypeError,ValueError,StopIteration) as exc:
        raise sqlite3.DatabaseError('Operational effect chain mismatch.') from exc
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
        if value is not None and (type(value) not in (int,float) or not 0<=value<=100 or not math.isfinite(value)):
            raise ValueError('Índice deve ser número finito entre 0 e 100 ou null.')
    if 'lost' in changes and type(changes['lost']) is not bool:
        raise ValueError('Declaração de perda deve ser booleana.')
    return dict(changes)


def classificar(domain, index):
    validar_alteracoes({'index_percent':index})
    if domain!='superficie' or index is None:return None
    return 'combater' if index>60 else 'navegar' if index>=40 else 'flutuar'
