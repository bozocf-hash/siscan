"""Manual constant-rate synthetic run, with atomic integer fuel accounting."""
from contextlib import contextmanager
from datetime import datetime,timezone
from decimal import Decimal
import hashlib,json,sqlite3,uuid
from pathlib import Path
import engine_units
from engine_input import input_hash,validate_input,trusted_manifest

RULES_VERSION='constant-rate-synthetic-01'
SCHEMA='''
CREATE TABLE IF NOT EXISTS engine_runs(
 run_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL UNIQUE REFERENCES exercises(id),
 scenario_version INTEGER NOT NULL,manifest_json TEXT NOT NULL,manifest_sha256 TEXT NOT NULL,
 elapsed_minutes INTEGER NOT NULL CHECK(elapsed_minutes>=0),revision INTEGER NOT NULL CHECK(revision>=0),
 created_by INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,
 FOREIGN KEY(exercise_id,scenario_version) REFERENCES scenario_versions(exercise_id,version));
CREATE TABLE IF NOT EXISTS engine_resource_states(
 run_id TEXT NOT NULL REFERENCES engine_runs(run_id),unit_id TEXT NOT NULL REFERENCES engine_units(unit_id),
 snapshot_id TEXT NOT NULL REFERENCES engine_unit_snapshots(snapshot_id),
 capacity_grams INTEGER NOT NULL CHECK(capacity_grams>0),initial_grams INTEGER NOT NULL CHECK(initial_grams>=0),
 rate_grams_per_minute INTEGER NOT NULL CHECK(rate_grams_per_minute>=0),
 remaining_grams INTEGER NOT NULL CHECK(remaining_grams>=0),consumed_grams INTEGER NOT NULL CHECK(consumed_grams>=0),
 PRIMARY KEY(run_id,unit_id),CHECK(initial_grams=remaining_grams+consumed_grams),CHECK(initial_grams<=capacity_grams));
CREATE TABLE IF NOT EXISTS engine_runtime_steps(
 run_id TEXT NOT NULL REFERENCES engine_runs(run_id),command_id TEXT NOT NULL,payload_json TEXT NOT NULL,
 revision INTEGER NOT NULL,before_minutes INTEGER NOT NULL,after_minutes INTEGER NOT NULL,
 duration_minutes INTEGER NOT NULL CHECK(duration_minutes>0),actor_id INTEGER NOT NULL REFERENCES users(id),
 result_json TEXT NOT NULL,created_at TEXT NOT NULL,
 PRIMARY KEY(run_id,command_id),UNIQUE(run_id,revision),CHECK(after_minutes=before_minutes+duration_minutes));
CREATE TABLE IF NOT EXISTS engine_fuel_ledger(
 run_id TEXT NOT NULL,command_id TEXT NOT NULL,unit_id TEXT NOT NULL,
 before_grams INTEGER NOT NULL CHECK(before_grams>=0),consumed_grams INTEGER NOT NULL CHECK(consumed_grams>=0),
 after_grams INTEGER NOT NULL CHECK(after_grams>=0),snapshot_sha256 TEXT NOT NULL,
 PRIMARY KEY(run_id,command_id,unit_id),
 FOREIGN KEY(run_id,command_id) REFERENCES engine_runtime_steps(run_id,command_id),
 FOREIGN KEY(run_id,unit_id) REFERENCES engine_resource_states(run_id,unit_id),
 CHECK(before_grams=after_grams+consumed_grams));
CREATE TRIGGER IF NOT EXISTS engine_run_manifest_guard BEFORE UPDATE OF run_id,exercise_id,scenario_version,manifest_json,manifest_sha256 ON engine_runs
 BEGIN SELECT RAISE(ABORT,'Run manifest is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_state_reference_guard BEFORE UPDATE OF run_id,unit_id,snapshot_id,capacity_grams,initial_grams,rate_grams_per_minute ON engine_resource_states
 BEGIN SELECT RAISE(ABORT,'State initial references are immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_steps_no_update BEFORE UPDATE ON engine_runtime_steps
 BEGIN SELECT RAISE(ABORT,'Step history is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_steps_no_delete BEFORE DELETE ON engine_runtime_steps
 BEGIN SELECT RAISE(ABORT,'Step history is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_ledger_no_update BEFORE UPDATE ON engine_fuel_ledger
 BEGIN SELECT RAISE(ABORT,'Fuel ledger is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_ledger_no_delete BEFORE DELETE ON engine_fuel_ledger
 BEGIN SELECT RAISE(ABORT,'Fuel ledger is immutable'); END;
'''


class Conflict(ValueError):pass


@contextmanager
def atomic(db):
    nested=db.in_transaction
    db.execute('SAVEPOINT engine_runtime' if nested else 'BEGIN IMMEDIATE')
    try:
        yield
        db.execute('RELEASE engine_runtime') if nested else db.commit()
    except Exception:
        if nested:db.execute('ROLLBACK TO engine_runtime');db.execute('RELEASE engine_runtime')
        else:db.rollback()
        raise


def code_hash():
    return hashlib.sha256(Path(__file__).read_text(encoding='utf-8').replace('\r\n','\n').encode('utf-8')).hexdigest()


def grams(value):
    exact=Decimal(str(value))*1000
    if not exact.is_finite() or exact!=exact.to_integral_value() or exact<0:raise ValueError('Massa não representável em gramas inteiras neste teste.')
    return int(exact)


def manifest_of(run):
    try:manifest=json.loads(run['manifest_json'])
    except ValueError as exc:raise sqlite3.DatabaseError('Invalid run manifest') from exc
    if not isinstance(manifest,dict) or input_hash(manifest)!=run['manifest_sha256']:raise sqlite3.DatabaseError('Run manifest integrity mismatch')
    return manifest


def start_run(db,user):
    engine_units.context(db,user,write=True)
    with atomic(db):
        exercise=engine_units.context(db,user,write=True)
        if db.execute('SELECT 1 FROM engine_runs WHERE exercise_id=?',(exercise['id'],)).fetchone():return read_runtime(db,user)
        units=engine_units.list_units(db,user)['units']
        if len(units)!=2 or {u['team'] for u in units}!={'AZUL','VERMELHO'}:raise ValueError('Prepare primeiro uma unidade sintética por partido.')
        specifications=[]
        for unit in units:
            snapshot=unit['snapshot'];template=snapshot['input_template']
            if snapshot['source_kind']!='synthetic_controlled' or not validate_input(template)['accepted'] or snapshot['input_manifest']!=trusted_manifest():raise ValueError('Snapshot sem contrato sintético compatível.')
            if snapshot['scenario_version']!=exercise['scenario_version']:raise Conflict('Snapshot de versão anterior do cenário; não foi recomposto automaticamente.')
            fields=template['measurements']
            specifications.append({'unit_id':unit['unit_id'],'snapshot_id':unit['snapshot_id'],'snapshot_sha256':unit['snapshot_sha256'],
                                   'capacity_grams':grams(fields['fuel_capacity']['value']),'initial_grams':grams(fields['fuel_initial']['value']),
                                   'rate_grams_per_minute':grams(fields['consumption_rate']['value'])})
        manifest={'schema_version':'siscan-engine-run-01','scope':'synthetic_constant_rate_test','rules_version':RULES_VERSION,
                  'engine_code_sha256':code_hash(),'input_manifest':trusted_manifest(),'scenario_version':exercise['scenario_version'],
                  'mass_storage_unit':'g','clock_unit':'min','units':sorted(specifications,key=lambda s:s['unit_id'])}
        run_id=str(uuid.uuid4());now=datetime.now(timezone.utc).isoformat()
        db.execute('INSERT INTO engine_runs VALUES(?,?,?,?,?,0,0,?,?)',(run_id,exercise['id'],exercise['scenario_version'],engine_units.encoded(manifest),input_hash(manifest),user['uid'],now))
        for item in specifications:
            db.execute('INSERT INTO engine_resource_states VALUES(?,?,?,?,?,?,?,0)',(run_id,item['unit_id'],item['snapshot_id'],item['capacity_grams'],item['initial_grams'],item['rate_grams_per_minute'],item['initial_grams']))
        db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',(exercise['id'],user['uid'],'engine.run_initialized',engine_units.encoded({'run_id':run_id,'manifest_sha256':input_hash(manifest),'scope':'synthetic_test_only'})))
        return read_runtime(db,user)


def read_runtime(db,user):
    exercise=engine_units.context(db,user)
    visible=engine_units.list_units(db,user)['units']
    if not visible:return {'initialized':False,'states':[],'ledger':[],'scope':'synthetic_constant_rate_test'}
    run=db.execute('SELECT * FROM engine_runs WHERE exercise_id=?',(exercise['id'],)).fetchone()
    if run is None:return {'initialized':False,'states':[],'ledger':[],'scope':'synthetic_constant_rate_test'}
    manifest=manifest_of(run);ids=[u['unit_id'] for u in visible];placeholders=','.join('?' for _ in ids)
    metadata={u['unit_id']:u for u in visible};states=[]
    for row in db.execute('SELECT * FROM engine_resource_states WHERE run_id=? AND unit_id IN ('+placeholders+') ORDER BY unit_id',(run['run_id'],*ids)):
        unit=metadata[row['unit_id']]
        states.append({'unit_id':row['unit_id'],'team':unit['team'],'code':unit['code'],'snapshot_id':row['snapshot_id'],
                       'fuel_initial_kg':row['initial_grams']/1000,'fuel_remaining_kg':row['remaining_grams']/1000,
                       'fuel_consumed_kg':row['consumed_grams']/1000,'rate_kg_per_minute':row['rate_grams_per_minute']/1000})
    expected=set(ids)&{s['unit_id'] for s in manifest['units']}
    if {s['unit_id'] for s in states}!=expected:raise sqlite3.DatabaseError('Visible state coverage mismatch')
    ledger=[dict(r) for r in db.execute('''SELECT l.unit_id,l.command_id,l.before_grams,l.consumed_grams,l.after_grams,s.revision,s.after_minutes,s.duration_minutes,s.created_at
       FROM engine_fuel_ledger l JOIN engine_runtime_steps s ON s.run_id=l.run_id AND s.command_id=l.command_id
       WHERE l.run_id=? AND l.unit_id IN ('''+placeholders+') ORDER BY s.revision DESC,l.unit_id LIMIT 40',(run['run_id'],*ids))]
    return {'initialized':True,'run_id':run['run_id'],'elapsed_minutes':run['elapsed_minutes'],'revision':run['revision'],
            'scenario_version':run['scenario_version'],'current_scenario_version':exercise['scenario_version'],
            'advance_allowed':exercise['state']=='open' and run['scenario_version']==exercise['scenario_version'] and manifest['rules_version']==RULES_VERSION and manifest['engine_code_sha256']==code_hash(),
            'manifest_sha256':run['manifest_sha256'],'manifest':manifest if user['role']=='instructor' else None,
            'states':states,'ledger':ledger,'scope':'synthetic_constant_rate_test','official_calculation_ready':False}


def advance_run(db,user,payload):
    engine_units.context(db,user,write=True)
    if not isinstance(payload,dict) or set(payload)!= {'command_id','minutes','expected_revision'}:raise ValueError('Comando deve conter apenas command_id, minutes e expected_revision.')
    command=payload['command_id'];minutes=payload['minutes'];expected=payload['expected_revision']
    try:valid_id=isinstance(command,str) and str(uuid.UUID(command))==command
    except ValueError:valid_id=False
    if not valid_id or type(minutes) is not int or not 1<=minutes<=1440 or type(expected) is not int or expected<0:raise ValueError('Identificador, intervalo ou revisão inválidos.')
    with atomic(db):
        exercise=engine_units.context(db,user,write=True)
        run=db.execute('SELECT * FROM engine_runs WHERE exercise_id=?',(exercise['id'],)).fetchone()
        if run is None:raise ValueError('Inicialize primeiro a execução sintética.')
        prior=db.execute('SELECT * FROM engine_runtime_steps WHERE run_id=? AND command_id=?',(run['run_id'],command)).fetchone()
        if prior:
            if prior['payload_json']!=engine_units.encoded(payload):raise Conflict('Chave já usada para um comando diferente.')
            return {**json.loads(prior['result_json']),'replayed':True}
        manifest=manifest_of(run)
        if run['revision']!=expected:raise Conflict('Revisão desatualizada. Atualize o estado antes de criar outro comando.')
        if run['scenario_version']!=exercise['scenario_version'] or manifest['rules_version']!=RULES_VERSION or manifest['engine_code_sha256']!=code_hash():raise Conflict('Versão do cenário ou do motor mudou; avanço recusado sem alterar o histórico.')
        rows=db.execute('SELECT * FROM engine_resource_states WHERE run_id=? ORDER BY unit_id',(run['run_id'],)).fetchall()
        specifications={s['unit_id']:s for s in manifest['units']}
        if set(specifications)!={r['unit_id'] for r in rows}:raise sqlite3.DatabaseError('Run state coverage mismatch')
        movements=[]
        for row in rows:
            spec=specifications[row['unit_id']]
            snapshot=db.execute('SELECT snapshot_json,snapshot_sha256 FROM engine_unit_snapshots WHERE snapshot_id=?',(row['snapshot_id'],)).fetchone()
            if snapshot is None or input_hash(json.loads(snapshot['snapshot_json']))!=spec['snapshot_sha256'] or snapshot['snapshot_sha256']!=spec['snapshot_sha256']:raise sqlite3.DatabaseError('Pinned snapshot mismatch')
            if any(row[k]!=spec[k] for k in ('snapshot_id','capacity_grams','initial_grams','rate_grams_per_minute')):raise sqlite3.DatabaseError('Initial state parameters mismatch')
            spent=minutes*row['rate_grams_per_minute']
            if spent>row['remaining_grams']:raise ValueError('Combustível insuficiente para o intervalo completo. Nenhum saldo ou relógio foi alterado.')
            movements.append((row,spent,row['remaining_grams']-spent,spec['snapshot_sha256']))
        changed=db.execute('UPDATE engine_runs SET elapsed_minutes=elapsed_minutes+?,revision=revision+1 WHERE run_id=? AND revision=?',(minutes,run['run_id'],expected))
        if changed.rowcount!=1:raise Conflict('Revisão concorrente; avanço recusado.')
        for row,spent,remaining,sha in movements:
            db.execute('UPDATE engine_resource_states SET remaining_grams=?,consumed_grams=consumed_grams+? WHERE run_id=? AND unit_id=?',(remaining,spent,run['run_id'],row['unit_id']))
        current=read_runtime(db,user)
        result={k:current[k] for k in ('run_id','elapsed_minutes','revision','states','manifest_sha256')}
        result.update(command_id=command,replayed=False,movements=[{'unit_id':row['unit_id'],'before_grams':row['remaining_grams'],'consumed_grams':spent,'after_grams':remaining,'snapshot_sha256':sha} for row,spent,remaining,sha in movements])
        now=datetime.now(timezone.utc).isoformat()
        db.execute('INSERT INTO engine_runtime_steps VALUES(?,?,?,?,?,?,?,?,?,?)',(run['run_id'],command,engine_units.encoded(payload),expected+1,run['elapsed_minutes'],run['elapsed_minutes']+minutes,minutes,user['uid'],engine_units.encoded(result),now))
        for row,spent,remaining,sha in movements:
            db.execute('INSERT INTO engine_fuel_ledger VALUES(?,?,?,?,?,?,?)',(run['run_id'],command,row['unit_id'],row['remaining_grams'],spent,remaining,sha))
        db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',(exercise['id'],user['uid'],'engine.step_applied',engine_units.encoded({'run_id':run['run_id'],'command_id':command,'revision':expected+1,'minutes':minutes,'scope':'synthetic_test_only'})))
        return result
