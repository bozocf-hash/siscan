"""Explicit, balance-preserving successors for controlled synthetic runs."""
import json,sqlite3,uuid
from datetime import datetime,timezone
import engine_runtime as runtime
import engine_units
from engine_input import input_hash,trusted_manifest,validate_input

SCHEMA='''
CREATE INDEX IF NOT EXISTS idx_engine_runs_exercise ON engine_runs(exercise_id);
CREATE TABLE IF NOT EXISTS engine_run_continuations(
 command_id TEXT PRIMARY KEY,previous_run_id TEXT NOT NULL UNIQUE REFERENCES engine_runs(run_id),
 next_run_id TEXT NOT NULL UNIQUE REFERENCES engine_runs(run_id),payload_json TEXT NOT NULL,
 reason TEXT NOT NULL,actor_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS engine_continuation_no_update BEFORE UPDATE ON engine_run_continuations
 BEGIN SELECT RAISE(ABORT,'Run continuation is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_continuation_no_delete BEFORE DELETE ON engine_run_continuations
 BEGIN SELECT RAISE(ABORT,'Run continuation is immutable'); END;
'''


def migrate(db):
    """Rebuild only the old UNIQUE(exercise_id) table, preserving child FK names."""
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='engine_runs'").fetchone():return False
    legacy=False
    for index in db.execute('PRAGMA index_list(engine_runs)').fetchall():
        name=index[1].replace('"','""')
        if index[2] and [r[2] for r in db.execute('PRAGMA index_info("'+name+'")')]==['exercise_id']:legacy=True
    if not legacy:return False
    if db.in_transaction:raise sqlite3.DatabaseError('Migration requires an independent transaction')
    db.execute('PRAGMA foreign_keys=OFF')
    try:
        db.execute('BEGIN IMMEDIATE')
        definition=runtime.SCHEMA.split(';',1)[0].replace('IF NOT EXISTS engine_runs','engine_runs_migration')
        db.execute(definition)
        db.execute('INSERT INTO engine_runs_migration SELECT * FROM engine_runs ORDER BY rowid')
        db.execute('DROP TABLE engine_runs')
        db.execute('ALTER TABLE engine_runs_migration RENAME TO engine_runs')
        guard=runtime.SCHEMA.split('CREATE TRIGGER IF NOT EXISTS engine_run_manifest_guard',1)[1].split('END;',1)[0]
        db.execute('CREATE TRIGGER engine_run_manifest_guard'+guard+'END')
        if db.execute('PRAGMA foreign_key_check').fetchall():raise sqlite3.DatabaseError('Migration foreign-key failure')
        db.commit()
        return True
    except Exception:
        db.rollback();raise
    finally:db.execute('PRAGMA foreign_keys=ON')


def history(db,user):
    exercise=engine_units.context(db,user)
    if user['role']!='instructor':raise PermissionError('Histórico restrito ao instrutor atribuído.')
    rows=[dict(r) for r in db.execute('''SELECT r.run_id,r.scenario_version,r.elapsed_minutes,r.revision,r.created_at,
      r.manifest_sha256,c.previous_run_id,c.reason FROM engine_runs r
      LEFT JOIN engine_run_continuations c ON c.next_run_id=r.run_id
      WHERE r.exercise_id=? ORDER BY r.rowid DESC''',(exercise['id'],))]
    return {'runs':rows,'current_run_id':rows[0]['run_id'] if rows else None}


def continue_run(db,user,payload):
    engine_units.context(db,user,write=True)
    if not isinstance(payload,dict) or set(payload)!={'command_id','previous_run_id','expected_revision','reason'}:raise ValueError('Informe comando, execução anterior, revisão e motivo.')
    for field in ('command_id','previous_run_id'):
        try:valid=isinstance(payload[field],str) and str(uuid.UUID(payload[field]))==payload[field]
        except ValueError:valid=False
        if not valid:raise ValueError('Identificador inválido.')
    if type(payload['expected_revision']) is not int or payload['expected_revision']<0 or not isinstance(payload['reason'],str) or not payload['reason'].strip() or len(payload['reason'])>1000:raise ValueError('Revisão ou motivo inválido (1 a 1000 caracteres).')
    with runtime.atomic(db):
        exercise=engine_units.context(db,user,write=True)
        prior=db.execute('SELECT c.*,r.exercise_id FROM engine_run_continuations c JOIN engine_runs r ON r.run_id=c.next_run_id WHERE command_id=?',(payload['command_id'],)).fetchone()
        if prior:
            if prior['exercise_id']!=exercise['id'] or prior['payload_json']!=engine_units.encoded(payload):raise runtime.Conflict('Chave já usada para outra continuação.')
            return {'run_id':prior['next_run_id'],'replayed':True}
        previous=runtime.current_run(db,exercise['id'])
        if previous is None or previous['run_id']!=payload['previous_run_id'] or previous['revision']!=payload['expected_revision']:raise runtime.Conflict('Execução ou revisão desatualizada. Atualize o estado.')
        old_manifest=runtime.manifest_of(previous)
        if old_manifest['rules_version']!=runtime.RULES_VERSION:raise runtime.Conflict('Regra anterior incompatível; continuação automática recusada.')
        units=engine_units.list_units(db,user)['units'];specifications={s['unit_id']:s for s in old_manifest['units']}
        states={r['unit_id']:r for r in db.execute('SELECT * FROM engine_resource_states WHERE run_id=?',(previous['run_id'],))}
        if len(units)!=2 or {u['unit_id'] for u in units}!=set(states) or set(states)!=set(specifications):raise sqlite3.DatabaseError('Continuation unit coverage mismatch')
        now=datetime.now(timezone.utc).isoformat();captured=[];next_id=str(uuid.uuid4())
        for unit in units:
            state=states[unit['unit_id']];spec=specifications[unit['unit_id']]
            if unit['snapshot_id']!=state['snapshot_id']:raise runtime.Conflict('Snapshot atual diverge da execução; continuação recusada.')
            pinned=db.execute('SELECT * FROM engine_unit_snapshots WHERE snapshot_id=?',(state['snapshot_id'],)).fetchone()
            if pinned is None:raise sqlite3.DatabaseError('Pinned snapshot missing')
            snapshot=json.loads(pinned['snapshot_json']);template=snapshot['input_template']
            if input_hash(snapshot)!=pinned['snapshot_sha256'] or pinned['snapshot_sha256']!=spec['snapshot_sha256'] or any(state[k]!=spec[k] for k in ('snapshot_id','capacity_grams','initial_grams','rate_grams_per_minute')):raise sqlite3.DatabaseError('Continuation snapshot mismatch')
            if snapshot['source_kind']!='synthetic_controlled' or not validate_input(template)['accepted'] or snapshot['input_manifest']!=trusted_manifest():raise runtime.Conflict('Contrato de origem incompatível; continuação recusada.')
            fields=template['measurements']
            if any(state[key]!=runtime.grams(fields[field]['value']) for key,field in [('capacity_grams','fuel_capacity'),('initial_grams','fuel_initial'),('rate_grams_per_minute','consumption_rate')]):raise sqlite3.DatabaseError('Controlled parameters differ')
            revised={**snapshot,'scenario_version':exercise['scenario_version'],'previous_snapshot_id':pinned['snapshot_id'],'continuation_of_run_id':previous['run_id']}
            snapshot_id=str(uuid.uuid4());sha=input_hash(revised)
            db.execute('INSERT INTO engine_unit_snapshots VALUES(?,?,?,?,?,?,?,?,?,?,?)',(snapshot_id,unit['unit_id'],exercise['id'],unit['team'],unit['revision']+1,unit['configuration_version_id'],exercise['scenario_version'],engine_units.encoded(revised),sha,user['uid'],now))
            captured.append({'unit_id':unit['unit_id'],'snapshot_id':snapshot_id,'snapshot_sha256':sha,**{k:state[k] for k in ('capacity_grams','initial_grams','rate_grams_per_minute','remaining_grams','consumed_grams')}})
        manifest={'schema_version':'siscan-engine-run-02','scope':'synthetic_constant_rate_test','rules_version':runtime.RULES_VERSION,
                  'engine_code_sha256':runtime.code_hash(),'input_manifest':trusted_manifest(),'scenario_version':exercise['scenario_version'],
                  'mass_storage_unit':'g','clock_unit':'min','previous_run_id':previous['run_id'],'previous_revision':previous['revision'],
                  'inherited_elapsed_minutes':previous['elapsed_minutes'],'units':sorted(captured,key=lambda s:s['unit_id'])}
        db.execute('INSERT INTO engine_runs VALUES(?,?,?,?,?,?,0,?,?)',(next_id,exercise['id'],exercise['scenario_version'],engine_units.encoded(manifest),input_hash(manifest),previous['elapsed_minutes'],user['uid'],now))
        for item in captured:
            db.execute('INSERT INTO engine_resource_states VALUES(?,?,?,?,?,?,?,?)',(next_id,item['unit_id'],item['snapshot_id'],item['capacity_grams'],item['initial_grams'],item['rate_grams_per_minute'],item['remaining_grams'],item['consumed_grams']))
        db.execute('INSERT INTO engine_run_continuations VALUES(?,?,?,?,?,?,?)',(payload['command_id'],previous['run_id'],next_id,engine_units.encoded(payload),payload['reason'].strip(),user['uid'],now))
        db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',(exercise['id'],user['uid'],'engine.run_continued',engine_units.encoded({'previous_run_id':previous['run_id'],'run_id':next_id,'reason':payload['reason'].strip(),'scope':'synthetic_test_only'})))
        return {'run_id':next_id,'replayed':False}
