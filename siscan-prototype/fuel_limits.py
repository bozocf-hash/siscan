"""Versioned operator alert preferences, independent of technical platform configuration."""
from datetime import datetime,timezone
import json,re,sqlite3,uuid
import engine_units

SCHEMA='''
CREATE TABLE IF NOT EXISTS engine_fuel_limits(
 limit_id TEXT PRIMARY KEY,unit_id TEXT NOT NULL REFERENCES engine_units(unit_id),
 run_id TEXT NOT NULL REFERENCES engine_runs(run_id),version INTEGER NOT NULL CHECK(version>0),
 minimum_grams INTEGER CHECK(minimum_grams IS NULL OR minimum_grams>=0),
 actor_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,
 command_id TEXT NOT NULL UNIQUE,payload_json TEXT NOT NULL,UNIQUE(unit_id,version));
CREATE TRIGGER IF NOT EXISTS fuel_limits_no_update BEFORE UPDATE ON engine_fuel_limits
 BEGIN SELECT RAISE(ABORT,'Fuel limit versions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS fuel_limits_no_delete BEFORE DELETE ON engine_fuel_limits
 BEGIN SELECT RAISE(ABORT,'Fuel limit versions are immutable'); END;
'''


def status(db,unit_id,remaining):
    row=db.execute('SELECT * FROM engine_fuel_limits WHERE unit_id=? ORDER BY version DESC LIMIT 1',(unit_id,)).fetchone()
    minimum=row['minimum_grams'] if row else None
    label='not_configured' if minimum is None else 'below_minimum' if remaining<minimum else 'at_minimum' if remaining==minimum else 'above_minimum'
    return {'version':row['version'] if row else 0,'minimum_grams':minimum,'status':label,'active':minimum is not None and remaining<=minimum,'fuel_exhausted':remaining==0,'actor_id':row['actor_id'] if row else None,'changed_at':row['created_at'] if row else None}


def set_limit(db,user,payload):
    import engine_runtime as runtime
    engine_units.context(db,user)
    required={'command_id','run_id','unit_id','expected_revision','expected_limit_revision','minimum_kg'}
    if not isinstance(payload,dict) or set(payload)!=required:raise ValueError('Informe comando, execução, unidade, revisões e mínimo em kg (ou null para desativar).')
    for key in ('command_id','run_id','unit_id'):
        try:valid=isinstance(payload[key],str) and str(uuid.UUID(payload[key]))==payload[key]
        except ValueError:valid=False
        if not valid:raise ValueError('Identificador inválido.')
    if any(type(payload[k]) is not int or payload[k]<0 for k in ('expected_revision','expected_limit_revision')):raise ValueError('Revisão inválida.')
    value=payload['minimum_kg']
    if value is not None and (not isinstance(value,str) or not re.fullmatch(r'\d{1,7}(?:\.\d{1,3})?',value)):raise ValueError('Informe kg positivos ou zero, com até três casas decimais.')
    minimum=None if value is None else runtime.grams(value)
    with runtime.atomic(db):
        exercise=engine_units.context(db,user)
        if exercise['state']!='open':raise ValueError('Exercício encerrado; alteração de alerta recusada.')
        visible={u['unit_id'] for u in engine_units.list_units(db,user)['units']}
        if payload['unit_id'] not in visible:raise PermissionError('Meio não disponibilizado ao seu partido ou exercício.')
        prior=db.execute('SELECT * FROM engine_fuel_limits WHERE command_id=?',(payload['command_id'],)).fetchone()
        if prior:
            if prior['payload_json']!=engine_units.encoded(payload):raise runtime.Conflict('Chave já usada para outro limite.')
            return {'replayed':True,'saved_version':prior['version']}
        run=runtime.current_run(db,exercise['id'])
        if run is None or run['run_id']!=payload['run_id'] or run['revision']!=payload['expected_revision']:raise runtime.Conflict('Execução/revisão desatualizada. Atualize o estado.')
        state=db.execute('SELECT * FROM engine_resource_states WHERE run_id=? AND unit_id=?',(run['run_id'],payload['unit_id'])).fetchone()
        if state is None:raise ValueError('Unidade sem estado nesta execução.')
        if minimum is not None and minimum>state['capacity_grams']:raise ValueError('O mínimo não pode ultrapassar a capacidade cadastrada.')
        previous=status(db,payload['unit_id'],state['remaining_grams'])
        if previous['version']!=payload['expected_limit_revision']:raise runtime.Conflict('Outro operador alterou o limite. Atualize o estado.')
        version=previous['version']+1
        db.execute('INSERT INTO engine_fuel_limits VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),payload['unit_id'],run['run_id'],version,minimum,user['uid'],datetime.now(timezone.utc).isoformat(),payload['command_id'],engine_units.encoded(payload)))
        current=status(db,payload['unit_id'],state['remaining_grams'])
        db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',(exercise['id'],user['uid'],'engine.fuel_limit_changed',engine_units.encoded({'unit_id':payload['unit_id'],'run_id':run['run_id'],'limit':current,'previous_version':previous['version']})))
        return {'replayed':False,'saved_version':version,'limit':current}


def crossings(db,exercise_id,run_id,user,movements,command_id):
    found=[]
    for row,spent,remaining,sha in movements:
        limit=status(db,row['unit_id'],remaining);minimum=limit['minimum_grams']
        kinds=[]
        if minimum is not None and row['remaining_grams']>minimum>=remaining:kinds.append('engine.fuel_minimum_reached')
        if row['remaining_grams']>0 and remaining==0:kinds.append('engine.fuel_exhausted')
        for kind in kinds:
            detail={'run_id':run_id,'command_id':command_id,'unit_id':row['unit_id'],'before_grams':row['remaining_grams'],'after_grams':remaining,'limit':limit}
            db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',(exercise_id,user['uid'],kind,engine_units.encoded(detail)));found.append({'event_type':kind,**detail})
    return found
