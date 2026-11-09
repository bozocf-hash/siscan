"""Versioned continuation, legacy migration and transactional preservation."""
from contextlib import closing
import sqlite3,uuid,json
import app,engine_runtime as runtime,engine_continuity as continuity
from engine_units import prepare_units,list_units

teacher={'uid':1,'role':'instructor','team':None}
blue={'uid':2,'role':'student','team':'AZUL'}
def command(**values):return {'command_id':str(uuid.uuid4()),**values}
def setup(db):
 db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.executescript(app.SCHEMA)
 for uid,role,team in [(1,'instructor',None),(2,'student','AZUL')]:
  db.execute("INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,X'00',X'00')",(uid,str(uid),str(uid),role,team))
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 db.executemany('INSERT INTO assignments VALUES(1,?)',[(1,),(2,)])
 prepare_units(db,teacher);runtime.start_run(db,teacher)
 return runtime.advance_run(db,teacher,command(minutes=30,expected_revision=0))

with closing(sqlite3.connect(':memory:')) as db:
 first=setup(db);old=runtime.read_runtime(db,teacher);snapshots=[tuple(r) for r in db.execute('SELECT * FROM engine_unit_snapshots')]
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,2,'Y','X','2026-11-09')")
 db.execute('UPDATE exercises SET scenario_version=2')
 payload=command(previous_run_id=first['run_id'],expected_revision=1,reason='Cenário revisado para ensaio')
 result=continuity.continue_run(db,teacher,payload);new=runtime.read_runtime(db,teacher)
 assert new['run_id']!=old['run_id'] and new['elapsed_minutes']==30 and new['revision']==0 and new['scenario_version']==2
 assert all(s['fuel_initial_kg']==600 and s['fuel_remaining_kg']==540 and s['fuel_consumed_kg']==60 for s in new['states'])
 assert len(continuity.history(db,teacher)['runs'])==2
 assert continuity.continue_run(db,teacher,payload)['run_id']==result['run_id']
 try:continuity.continue_run(db,teacher,{**payload,'reason':'Outro conteúdo'})
 except runtime.Conflict:pass
 else:raise AssertionError('Continuation key reused for another intention')
 archived=runtime.read_runtime(db,teacher,old['run_id']);historical=[{**s,'minimum_alert':None} for s in old['states']];assert archived['states']==historical and not archived['advance_allowed']
 legacy_step=db.execute('SELECT payload_json FROM engine_runtime_steps WHERE run_id=?',(old['run_id'],)).fetchone()[0]
 assert runtime.advance_run(db,teacher,{**json.loads(legacy_step),'run_id':old['run_id']})['replayed']
 for row in snapshots:assert db.execute('SELECT 1 FROM engine_unit_snapshots WHERE snapshot_id=? AND snapshot_json=?',(row[0],row[7])).fetchone()
 assert len(list_units(db,teacher)['units'])==2 and all(u['revision']==2 for u in list_units(db,teacher)['units'])
 for who,body in [(blue,payload),(teacher,{**payload,'reason':''})]:
  try:continuity.continue_run(db,who,body)
  except (PermissionError,ValueError):pass
  else:raise AssertionError('Unauthorized/invalid continuation accepted')
 try:continuity.continue_run(db,teacher,{**payload,'command_id':str(uuid.uuid4())})
 except runtime.Conflict:pass
 else:raise AssertionError('Second successor accepted')
 for body in [command(minutes=1,expected_revision=0),command(run_id=old['run_id'],minutes=1,expected_revision=1)]:
  try:runtime.advance_run(db,teacher,body)
  except runtime.Conflict:pass
  else:raise AssertionError('Unscoped or archived advance accepted')
 runtime.advance_run(db,teacher,command(run_id=new['run_id'],minutes=15,expected_revision=0))
 current=runtime.read_runtime(db,teacher);assert current['elapsed_minutes']==45 and all(s['fuel_remaining_kg']==510 for s in current['states'])
 assert runtime.read_runtime(db,teacher,old['run_id'])['states']==historical
 asset=next(u['asset_id'] for u in list_units(db,teacher)['units'] if u['team']=='AZUL')
 db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-09')",(asset,))
 visible=runtime.read_runtime(db,blue);assert len(visible['states'])==1 and visible['run_id']==new['run_id'] and 'VERMELHO' not in json.dumps(visible)
 try:continuity.history(db,blue)
 except PermissionError:pass
 else:raise AssertionError('Student accessed history listing')
 try:runtime.read_runtime(db,blue,old['run_id'])
 except PermissionError:pass
 else:raise AssertionError('Student accessed historical run')
 before=[tuple(r) for r in db.execute('SELECT * FROM engine_runs')]
 db.execute("CREATE TRIGGER fail_continuation BEFORE INSERT ON engine_run_continuations BEGIN SELECT RAISE(ABORT,'injected'); END")
 try:continuity.continue_run(db,teacher,command(previous_run_id=new['run_id'],expected_revision=1,reason='rollback'))
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Failure injection ignored')
 assert [tuple(r) for r in db.execute('SELECT * FROM engine_runs')]==before
 assert db.execute('SELECT count(*) FROM engine_unit_snapshots').fetchone()[0]==4
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
 db.execute("UPDATE exercises SET state='closed'")
 handler=object.__new__(app.Handler);responses=[];handler.send_json=lambda status,body:responses.append((status,body))
 handler.engine_runtime_action(db,teacher,'history');assert responses[-1][0]==200
 handler.engine_runtime_action(db,teacher,'read',old['run_id']);assert responses[-1][0]==200
 handler.engine_runtime_action(db,teacher,'continue',command(previous_run_id=new['run_id'],expected_revision=1,reason='closed'));assert responses[-1][0]==400
print('PASS: inherited balances/time, scoped commands, historical isolation, immutable snapshots, continuation idempotency and rollback')

with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row
 legacy=app.SCHEMA.replace('run_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL REFERENCES exercises(id),','run_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL UNIQUE REFERENCES exercises(id),')
 db.executescript(legacy)
 first=setup(db);db.commit()
 before={name:[tuple(r) for r in db.execute('SELECT * FROM '+name)] for name in ['engine_runs','engine_resource_states','engine_runtime_steps','engine_fuel_ledger','engine_unit_snapshots']}
 assert continuity.migrate(db)
 assert not continuity.migrate(db)
 for name,rows in before.items():assert [tuple(r) for r in db.execute('SELECT * FROM '+name)]==rows,name
 assert db.execute('PRAGMA foreign_keys').fetchone()[0]==1
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
 db.executescript(app.SCHEMA)
 continuity.continue_run(db,teacher,command(previous_run_id=first['run_id'],expected_revision=1,reason='Migração'))
 assert db.execute('SELECT count(*) FROM engine_runs').fetchone()[0]==2
 try:db.execute("UPDATE engine_runs SET manifest_sha256='bad'")
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Manifest guard lost during migration')
print('PASS: legacy UNIQUE migration preserves runs, states, snapshots, steps, ledger, foreign keys and manifest trigger')

with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.executescript(legacy);setup(db);db.commit()
 db.execute('PRAGMA foreign_keys=OFF');db.execute('UPDATE engine_runs SET created_by=999');db.commit();db.execute('PRAGMA foreign_keys=ON')
 before=[tuple(r) for r in db.execute('SELECT * FROM engine_runs')]
 try:continuity.migrate(db)
 except sqlite3.DatabaseError:pass
 else:raise AssertionError('Migration accepted invalid foreign key')
 assert db.execute('PRAGMA foreign_keys').fetchone()[0]==1
 assert [tuple(r) for r in db.execute('SELECT * FROM engine_runs')]==before
 assert 'UNIQUE' in db.execute("SELECT sql FROM sqlite_master WHERE name='engine_runs'").fetchone()[0]
 assert not db.execute("SELECT 1 FROM sqlite_master WHERE name='engine_runs_migration'").fetchone()
print('PASS: failed migration rolls back table replacement and restores FK enforcement')

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tempfile
with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'tmp') as folder:
 path=Path(folder)/'continuity.sqlite3'
 with closing(sqlite3.connect(path)) as db:first=setup(db);db.commit()
 def submit(payload):
  with closing(sqlite3.connect(path,timeout=10)) as db:
   db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
   try:return continuity.continue_run(db,teacher,payload) if 'previous_run_id' in payload else runtime.advance_run(db,teacher,payload)
   except runtime.Conflict:return 'conflict'
 payload=command(previous_run_id=first['run_id'],expected_revision=1,reason='Concorrência')
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(submit,[payload,{**payload,'command_id':str(uuid.uuid4())}]))
 assert sum(r=='conflict' for r in results)==1
 current=next(r for r in results if r!='conflict')
 payload=command(previous_run_id=current['run_id'],expected_revision=0,reason='Repetição concorrente')
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(submit,[payload,payload]))
 assert sorted(r['replayed'] for r in results)==[False,True]
 newest=results[0]['run_id']
 with ThreadPoolExecutor(max_workers=2) as pool:
  raced=list(pool.map(submit,[command(previous_run_id=newest,expected_revision=0,reason='Race with advance'),command(run_id=newest,minutes=30,expected_revision=0)]))
 assert sum(r=='conflict' for r in raced)==1
 with closing(sqlite3.connect(path)) as db:
  count=db.execute('SELECT count(*) FROM engine_runs').fetchone()[0];assert count in (3,4)
  assert db.execute('SELECT count(*) FROM engine_unit_snapshots').fetchone()[0]==count*2
  assert not db.execute('PRAGMA foreign_key_check').fetchall()
print('PASS: concurrent successors serialize, identical continuation replays and balances remain conserved')
