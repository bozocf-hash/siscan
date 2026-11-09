"""Party-owned synthetic unit identities and immutable initial technical snapshots."""
import json
import sqlite3
import uuid
from datetime import datetime,timezone
from engine_input import controlled_example,validate_input,input_hash

SCHEMA='''
CREATE TABLE IF NOT EXISTS engine_configurations(
 version_id TEXT PRIMARY KEY,model_id TEXT NOT NULL,configuration_id TEXT NOT NULL,
 dataset_sha256 TEXT NOT NULL,input_json TEXT NOT NULL,manifest_json TEXT NOT NULL,
 created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS engine_units(
 unit_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL REFERENCES exercises(id),
 team TEXT NOT NULL CHECK(team IN ('AZUL','VERMELHO')),
 asset_id INTEGER NOT NULL UNIQUE REFERENCES assets(id),
 purpose TEXT NOT NULL CHECK(purpose='synthetic-engine-01'),
 UNIQUE(exercise_id,team,purpose),UNIQUE(unit_id,exercise_id,team));
CREATE TABLE IF NOT EXISTS engine_unit_snapshots(
 snapshot_id TEXT PRIMARY KEY,unit_id TEXT NOT NULL,
 exercise_id INTEGER NOT NULL,team TEXT NOT NULL,revision INTEGER NOT NULL CHECK(revision>0),
 configuration_version_id TEXT NOT NULL REFERENCES engine_configurations(version_id),
 scenario_version INTEGER NOT NULL,snapshot_json TEXT NOT NULL,snapshot_sha256 TEXT NOT NULL,
 created_by INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,
 UNIQUE(unit_id,revision),
 FOREIGN KEY(unit_id,exercise_id,team) REFERENCES engine_units(unit_id,exercise_id,team),
 FOREIGN KEY(exercise_id,scenario_version) REFERENCES scenario_versions(exercise_id,version));
CREATE TRIGGER IF NOT EXISTS engine_units_asset_scope BEFORE INSERT ON engine_units
 WHEN NOT EXISTS(SELECT 1 FROM assets WHERE id=NEW.asset_id AND exercise_id=NEW.exercise_id AND team=NEW.team)
 BEGIN SELECT RAISE(ABORT,'Engine unit asset scope mismatch'); END;
CREATE TRIGGER IF NOT EXISTS engine_units_identity_guard BEFORE UPDATE ON engine_units
 BEGIN SELECT RAISE(ABORT,'Engine unit identity is immutable in this version'); END;
CREATE TRIGGER IF NOT EXISTS engine_configuration_no_update BEFORE UPDATE ON engine_configurations
 BEGIN SELECT RAISE(ABORT,'Configuration version is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_configuration_no_delete BEFORE DELETE ON engine_configurations
 BEGIN SELECT RAISE(ABORT,'Configuration version is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_snapshot_no_update BEFORE UPDATE ON engine_unit_snapshots
 BEGIN SELECT RAISE(ABORT,'Technical snapshot is immutable'); END;
CREATE TRIGGER IF NOT EXISTS engine_snapshot_no_delete BEFORE DELETE ON engine_unit_snapshots
 BEGIN SELECT RAISE(ABORT,'Technical snapshot is immutable'); END;
'''


def context(db,user,write=False):
    exercise=db.execute('SELECT * FROM exercises ORDER BY id LIMIT 1').fetchone()
    assigned=exercise and db.execute('SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?',(exercise['id'],user['uid'])).fetchone()
    allowed=user['role']=='instructor' or (not write and user['role']=='student' and user['team'] in ('AZUL','VERMELHO'))
    if not assigned or not allowed:raise PermissionError('Consulta ou preparação não autorizada para este participante.')
    if write and exercise['state']!='open':raise ValueError('Exercício encerrado; preparação recusada.')
    return exercise


def encoded(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)


def prepare_units(db,user):
    exercise=context(db,user,write=True)
    db.execute('SAVEPOINT prepare_engine_units')
    try:
        existing={r['team']:r['unit_id'] for r in db.execute('SELECT team,unit_id FROM engine_units WHERE exercise_id=?',(exercise['id'],))}
        missing=[team for team in ('AZUL','VERMELHO') if team not in existing]
        if not missing:
            db.execute('RELEASE prepare_engine_units')
            return {'created':0,'unit_ids':list(existing.values())}
        payload=controlled_example();validation=validate_input(payload)
        if not validation['accepted']:raise ValueError('O conjunto sintético não passou no contrato de entrada; nenhuma unidade foi criada.')
        manifest=validation['manifest'];model='SYN-AIR-MODEL-001'
        version=str(uuid.uuid5(uuid.NAMESPACE_URL,input_hash({'model':model,'input':payload,'manifest':manifest})))
        now=datetime.now(timezone.utc).isoformat()
        db.execute('INSERT OR IGNORE INTO engine_configurations VALUES(?,?,?,?,?,?,?)',
                   (version,model,payload['configuration_id'],manifest['dataset_sha256'],encoded(payload),encoded(manifest),now))
        configuration=db.execute('SELECT * FROM engine_configurations WHERE version_id=?',(version,)).fetchone()
        if (configuration['input_json'],configuration['manifest_json'],configuration['model_id'],configuration['configuration_id'],configuration['dataset_sha256'])!=(encoded(payload),encoded(manifest),model,payload['configuration_id'],manifest['dataset_sha256']):
            raise sqlite3.DatabaseError('Configuration version differs from its controlled contents')
        created=[]
        for team in missing:
            cursor=db.execute('INSERT INTO assets(exercise_id,team,code,name,category,fiche,source_label) VALUES(?,?,?,?,?,?,?)',
                (exercise['id'],team,team[0]+'-ENG-001','Unidade aérea sintética '+team,'Aeronave sintética de teste',
                 'Unidade para teste do contrato do motor. Snapshot técnico inicial versionado; não representa plataforma real ou execução.',
                 'Conjunto sintético controlado synthetic-fuel-01'))
            unit_id=str(uuid.uuid4());asset_id=cursor.lastrowid
            db.execute('INSERT INTO engine_units VALUES(?,?,?,?,?)',(unit_id,exercise['id'],team,asset_id,'synthetic-engine-01'))
            snapshot={'schema_version':'siscan-unit-snapshot-01','unit_id':unit_id,'exercise_id':exercise['id'],
                      'team':team,'scenario_version':exercise['scenario_version'],'model_id':model,
                      'configuration_id':payload['configuration_id'],'configuration_version_id':version,
                      'input_template':payload,'input_manifest':manifest,
                      'source_kind':'synthetic_controlled','official_calculation_ready':False}
            db.execute('INSERT INTO engine_unit_snapshots VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                       (str(uuid.uuid4()),unit_id,exercise['id'],team,1,version,exercise['scenario_version'],encoded(snapshot),input_hash(snapshot),user['uid'],now))
            created.append(unit_id)
        db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',
                   (exercise['id'],user['uid'],'engine.units_prepared',encoded({'unit_ids':created,'dataset_sha256':manifest['dataset_sha256'],'scope':'synthetic_test_only'})))
        db.execute('RELEASE prepare_engine_units')
        return {'created':len(created),'unit_ids':list(existing.values())+created}
    except Exception:
        db.execute('ROLLBACK TO prepare_engine_units');db.execute('RELEASE prepare_engine_units')
        raise


def list_units(db,user):
    exercise=context(db,user)
    where='u.exercise_id=?';params=[exercise['id']]
    if user['role']=='student':
        where+=' AND u.team=? AND EXISTS(SELECT 1 FROM party_allocations p WHERE p.exercise_id=u.exercise_id AND p.team=u.team AND p.asset_id=u.asset_id AND p.active=1)'
        params.append(user['team'])
    rows=db.execute('''SELECT u.*,a.code,a.name,a.category,s.snapshot_id,s.revision,s.configuration_version_id,
          s.snapshot_json,s.snapshot_sha256,s.created_at FROM engine_units u
          JOIN assets a ON a.id=u.asset_id AND a.exercise_id=u.exercise_id AND a.team=u.team
          LEFT JOIN engine_unit_snapshots s ON s.unit_id=u.unit_id AND s.revision=(
            SELECT max(revision) FROM engine_unit_snapshots WHERE unit_id=u.unit_id)
          WHERE '''+where+' ORDER BY u.team,u.unit_id',params).fetchall()
    units=[]
    for row in rows:
        if row['snapshot_json'] is None:raise sqlite3.DatabaseError('Unit snapshot missing')
        try:snapshot=json.loads(row['snapshot_json'])
        except ValueError as exc:raise sqlite3.DatabaseError('Unit snapshot JSON is invalid') from exc
        if not isinstance(snapshot,dict) or input_hash(snapshot)!=row['snapshot_sha256'] or snapshot.get('unit_id')!=row['unit_id'] or snapshot.get('team')!=row['team'] or snapshot.get('exercise_id')!=exercise['id'] or snapshot.get('configuration_version_id')!=row['configuration_version_id']:
            raise sqlite3.DatabaseError('Unit snapshot integrity mismatch')
        allocated=db.execute('SELECT 1 FROM party_allocations WHERE exercise_id=? AND team=? AND asset_id=? AND active=1',(exercise['id'],row['team'],row['asset_id'])).fetchone()
        unit={k:row[k] for k in ('unit_id','asset_id','team','code','name','category','snapshot_id','revision','configuration_version_id','snapshot_sha256','created_at')}
        unit.update(snapshot=snapshot,allocated=bool(allocated));units.append(unit)
    return {'units':units,'current_scenario_version':exercise['scenario_version'],
            'simulation_started':False,'scope':'synthetic_initial_snapshots'}
