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
