"""Adaptador didático do par no mapa; publicador único em operational_state."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import sqlite3
import uuid
import cpc_map
import engine_units
import operational_state as state
import operational_state_storage as storage
from unit_groups import GroupConflict

ORIGIN='siscan-cpc-didactic-origin-01'


def digest(value):return hashlib.sha256(engine_units.encoded(value).encode('utf-8')).hexdigest()


def fields(body,required,optional=()):
    if not isinstance(body,dict) or not set(required)<=set(body) or set(body)-set(required)-set(optional):
        raise ValueError('Campos de julgamento inválidos.')


def _refs(exercise,selection):
    if not isinstance(selection,dict) or set(selection)!={'AZUL','VERMELHO'}:raise ValueError('Selecione AZUL e VERMELHO.')
    refs=[]
    for team,ref in selection.items():
        fields(ref,{'group_id','expected_revision'})
        refs.append(dict(context=dict(exercise_id=exercise['id'],team=team),**ref))
    return refs


@contextmanager
def _view(db):
    db.execute('SAVEPOINT cpc_judgment_view')
    try:yield;db.execute('RELEASE cpc_judgment_view')
    except Exception:
        db.execute('ROLLBACK TO cpc_judgment_view');db.execute('RELEASE cpc_judgment_view');raise


def context(db,user,registry,body):
    exercise=state.autorizar_instrutor(db,user,write=True);storage.validate(db)
    fields(body,{'selection'},{'expected_view_sha256'})
    with _view(db),registry.conferir_revisoes(_refs(exercise,body['selection'])):
        preparation=cpc_map.prepare(db,user,registry,body['selection'])
        if 'expected_view_sha256' in body and preparation['view_sha256']!=body['expected_view_sha256']:
            raise state.Conflict('Preparação mudou; confira o par novamente.')
        states={m['unit_id']:state.consultar(db,user,m['unit_id']) for p in preparation['parties'] for m in p['members']}
        result=dict(schema_version='siscan-cpc-judgment-basis-01',selection=deepcopy(body['selection']),
                    preparation=preparation,states=states)
        result['basis_sha256']=digest(result);return result


def _native(base,effects):
    if not isinstance(effects,list) or not 1<=len(effects)<=100:raise ValueError('Escolha os meios afetados.')
    members={m['unit_id']:m for p in base['preparation']['parties'] for m in p['members']}
    result=[];seen=set()
    for effect in effects:
        fields(effect,{'unit_id','changes'});uid=effect['unit_id']
        if not isinstance(uid,str) or uid not in members or uid in seen:raise ValueError('Meio fora do par ou duplicado.')
        seen.add(uid);member=members[uid]
        result.append(dict(unit_id=uid,changes=effect['changes'],expected_state_revision=base['states'][uid]['state']['revision'],
                           **{k:member[k] for k in ('snapshot_id','snapshot_sha256','configuration_version_id')}))
    return result


def preview(db,user,registry,body):
    state.autorizar_instrutor(db,user,write=True)
    fields(body,{'selection','basis_sha256','effects','reason'},{'correction_decision_id'})
    if not isinstance(body['reason'],str) or not body['reason'].strip() or len(body['reason'])>4000:
        raise ValueError('Justificativa obrigatória, até 4000 caracteres.')
    with _view(db):
        base=context(db,user,registry,dict(selection=body['selection']))
        if base['basis_sha256']!=body['basis_sha256']:raise state.Conflict('Base alterada; abra uma nova conferência.')
        effects=state.prever_efeitos(db,user,_native(base,body['effects']),body.get('correction_decision_id'))
        return dict(basis=base,effects=effects,reason=body['reason'])


def _proposal(db,user,proposal_id):
    view=state.consultar_proposta(db,user,proposal_id)
    if view['current']['body']['origin'].get('schema_version')!=ORIGIN:
        raise KeyError('Proposta não pertence ao julgamento CPC.')
    return view


def get(db,user,registry,proposal_id):
    state.autorizar_instrutor(db,user)
    with _view(db):
        view=_proposal(db,user,proposal_id);origin=view['current']['body']['origin']
        view.update(available=False,availability_reason='Decisão já registrada.' if view['decision'] else 'Base indisponível; confira a composição.')
        if view['decision'] is None:
            try:
                fresh=context(db,user,registry,dict(selection=origin['basis']['selection']))
                view['available']=fresh['basis_sha256']==origin['basis']['basis_sha256']
                if view['available']:view['availability_reason']=None
            except (GroupConflict,state.Conflict,KeyError,ValueError,PermissionError):pass
        return view


def listing(db,user,*,limit=20,cursor=0):
    return state.listar_propostas(db,user,limit=limit,cursor=cursor,origin_schema=ORIGIN)


def _write(db,user,registry,body,operation):
    exercise=state.autorizar_instrutor(db,user,write=True)
    if db.in_transaction:raise ValueError('Julgamento exige conexão sem transação externa.')
    required={'command_id','selection','basis_sha256','effects','reason'}
    optional={'correction_decision_id'} if operation=='register' else set()
    if operation=='revise':required|={'proposal_id','expected_revision','expected_sha256'}
    if operation=='decide':required={'command_id','proposal_id','expected_revision','expected_sha256','action','reason'}
    fields(body,required,optional)
    try:
        if not isinstance(body['command_id'],str) or str(uuid.UUID(body['command_id']))!=body['command_id']:raise ValueError()
        if len(engine_units.encoded(body).encode('utf-8'))>64000:raise ValueError()
    except (ValueError,TypeError,AttributeError) as exc:raise ValueError('Comando inválido ou excede 64 KB.') from exc
    db.execute('BEGIN IMMEDIATE')
    try:
        state.autorizar_instrutor(db,user,write=True)
        replay=state.consultar_recibo(db,user,body['command_id'])
        if replay is not None:
            matches=replay['operation']==operation
            if operation=='decide':
                _proposal(db,user,body['proposal_id'])
                matches=matches and replay['payload']==body
            else:
                origin=replay['payload'].get('origin',{})
                matches=matches and origin.get('schema_version')==ORIGIN and origin.get('request_sha256')==digest(body)
            if not matches:raise state.Conflict('Comando reutilizado com outra intenção.')
            db.commit();return replay['result']
        view=_proposal(db,user,body['proposal_id']) if operation in ('revise','decide') else None
        if operation=='decide' and body['action']=='reject':
            result=state.decidir_proposta(db,user,body);db.commit();return result
        selection=body['selection'] if operation!='decide' else view['current']['body']['origin']['basis']['selection']
        with registry.conferir_revisoes(_refs(exercise,selection)):
            if operation=='decide':
                saved=view['current']['body']['origin']['basis']
                current=context(db,user,registry,dict(selection=selection))
                if current['basis_sha256']!=saved['basis_sha256']:raise state.Conflict('Base da proposta alterada; revise o julgamento.')
                result=state.decidir_proposta(db,user,body)
            else:
                content={k:body[k] for k in ('selection','basis_sha256','effects','reason')}
                correction=body.get('correction_decision_id') if view is None else view['correction_decision_id']
                if correction is not None:content['correction_decision_id']=correction
                candidate=preview(db,user,registry,content)
                payload=dict(command_id=body['command_id'],source='didactic',reason=body['reason'],
                    origin=dict(schema_version=ORIGIN,basis=candidate['basis'],request_sha256=digest(body)),
                    effects=_native(candidate['basis'],body['effects']))
                if operation=='register':
                    if correction is not None:payload['correction_decision_id']=correction
                    result=state.registrar_proposta(db,user,payload)
                else:
                    payload.update(**{k:body[k] for k in ('proposal_id','expected_revision','expected_sha256')})
                    result=state.revisar_proposta(db,user,payload)
            db.commit();return result
    except Exception:
        db.rollback();raise


def register(db,user,registry,body):return _write(db,user,registry,body,'register')


def revise(db,user,registry,body):return _write(db,user,registry,body,'revise')


def decide(db,user,registry,body):return _write(db,user,registry,body,'decide')
