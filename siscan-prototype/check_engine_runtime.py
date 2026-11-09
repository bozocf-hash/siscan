from contextlib import closing
import sqlite3,uuid,json
import app
from engine_units import prepare_units,list_units
from engine_runtime import start_run,advance_run,read_runtime,Conflict

with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.executescript(app.SCHEMA)
 for uid,role,team in [(1,'instructor',None),(2,'student','AZUL'),(3,'student','AZUL'),(4,'student','VERMELHO'),(5,'evaluator',None)]:
  db.execute('INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,?,?)',(uid,str(uid),str(uid),role,team,b'x',b'x'))
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 for uid in range(1,6):db.execute('INSERT INTO assignments VALUES(1,?)',(uid,))
 teacher={'uid':1,'role':'instructor'};blue={'uid':2,'role':'student','team':'AZUL'};peer={'uid':3,'role':'student','team':'AZUL'};red={'uid':4,'role':'student','team':'VERMELHO'}
 prepare_units(db,teacher);frozen=list_units(db,teacher)['units']
 for user in (blue,red,{'uid':5,'role':'evaluator'}):
  try:start_run(db,user)
  except PermissionError:pass
  else:raise AssertionError('Unauthorized start')
 run=start_run(db,teacher);assert run['initialized'] and run['elapsed_minutes']==0
 assert start_run(db,teacher)['run_id']==run['run_id']
 assert read_runtime(db,blue)['initialized'] is False
 command={'command_id':str(uuid.uuid4()),'minutes':30,'expected_revision':0}
 result=advance_run(db,teacher,command)
 assert result['revision']==1 and result['elapsed_minutes']==30
 assert all(s['fuel_remaining_kg']==540 and s['fuel_consumed_kg']==60 for s in result['states'])
 assert advance_run(db,teacher,command)['replayed'] is True
 assert read_runtime(db,teacher)['revision']==1
 assert list_units(db,teacher)['units']==frozen
 for bad in ({**command,'minutes':31},{'command_id':str(uuid.uuid4()),'minutes':1,'expected_revision':0}):
  try:advance_run(db,teacher,bad)
  except Conflict:pass
  else:raise AssertionError('Conflicting command accepted')
 for minutes in (0,-1,True,1.5,1441):
  try:advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'minutes':minutes,'expected_revision':1})
  except ValueError:pass
  else:raise AssertionError('Invalid duration accepted')
 before=read_runtime(db,teacher)
 try:advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'minutes':271,'expected_revision':1})
 except ValueError:pass
 else:raise AssertionError('Negative fuel accepted')
 assert read_runtime(db,teacher)==before
 asset=next(u['asset_id'] for u in frozen if u['team']=='AZUL')
 db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-09')",(asset,))
 assert read_runtime(db,blue)==read_runtime(db,peer)
 own=read_runtime(db,blue);assert len(own['states'])==1 and own['states'][0]['team']=='AZUL'
 assert len(own['ledger'])==1 and own['manifest'] is None
 assert 'VERMELHO' not in json.dumps(own)
 db.execute("CREATE TRIGGER test_fail_runtime BEFORE INSERT ON engine_fuel_ledger WHEN NEW.after_grams=538000 BEGIN SELECT RAISE(ABORT,'test rollback'); END")
 before=read_runtime(db,teacher)
 try:advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'minutes':1,'expected_revision':1})
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Injected ledger failure ignored')
 assert read_runtime(db,teacher)==before
 db.execute('DROP TRIGGER test_fail_runtime')
 final=advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'minutes':270,'expected_revision':1})
 assert final['elapsed_minutes']==300 and all(s['fuel_remaining_kg']==0 for s in final['states'])
 assert db.execute('SELECT count(*) FROM engine_runtime_steps').fetchone()[0]==2
 assert db.execute('SELECT count(*) FROM engine_fuel_ledger').fetchone()[0]==4
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,2,'Y','X','2026-11-09')")
 db.execute('UPDATE exercises SET scenario_version=2')
 try:advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'minutes':1,'expected_revision':2})
 except Conflict:pass
 else:raise AssertionError('Changed scenario silently accepted')
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
 handler=object.__new__(app.Handler);responses=[]
 handler.send_json=lambda status,body:responses.append((status,body))
 handler.engine_runtime_action(db,teacher,'read');assert responses[-1][0]==200
 handler.engine_runtime_action(db,blue,'advance',command);assert responses[-1][0]==403
 handler.engine_runtime_action(db,teacher,'advance',{'bad':True});assert responses[-1][0]==400
 handler.engine_runtime_action(db,teacher,'advance',{'command_id':str(uuid.uuid4()),'minutes':1,'expected_revision':2});assert responses[-1][0]==409

from pathlib import Path
import tempfile
from concurrent.futures import ThreadPoolExecutor
with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'tmp') as folder:
 path=Path(folder)/'concurrent.sqlite3'
 with closing(sqlite3.connect(path)) as db:
  db.row_factory=sqlite3.Row;db.executescript(app.SCHEMA)
  db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'t','T','instructor',X'00',X'00')")
  db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
  db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
  db.execute('INSERT INTO assignments VALUES(1,1)')
  prepare_units(db,teacher);start_run(db,teacher);db.commit()
 def submit(payload):
  with closing(sqlite3.connect(path,timeout=10)) as connection:
   connection.row_factory=sqlite3.Row;connection.execute('PRAGMA foreign_keys=ON')
   try:return advance_run(connection,teacher,payload)
   except Conflict:return 'conflict'
 with ThreadPoolExecutor(max_workers=2) as pool:
  results=list(pool.map(submit,[{'command_id':str(uuid.uuid4()),'minutes':30,'expected_revision':0} for _ in range(2)]))
 assert sum(r=='conflict' for r in results)==1
 same={'command_id':str(uuid.uuid4()),'minutes':30,'expected_revision':1}
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(submit,[same,same]))
 assert sorted(r['replayed'] for r in results)==[False,True]
 with closing(sqlite3.connect(path)) as db:
  db.row_factory=sqlite3.Row;current=read_runtime(db,teacher)
  assert current['revision']==2 and current['elapsed_minutes']==60
  assert all(s['fuel_remaining_kg']==480 for s in current['states'])
  assert db.execute('SELECT count(*) FROM engine_runtime_steps').fetchone()[0]==2
print('PASS: atomic fuel/clock ledger, idempotent commands, revision conflicts, exact exhaustion, rollback, frozen snapshots and party isolation')
