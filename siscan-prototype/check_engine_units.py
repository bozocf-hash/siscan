from contextlib import closing
from copy import deepcopy
from unittest.mock import patch
import json,sqlite3
import app
from engine_units import prepare_units,list_units

with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.executescript(app.SCHEMA)
 for uid,role,team in [(1,'instructor',None),(2,'student','AZUL'),(3,'student','AZUL'),(4,'student','VERMELHO'),(5,'evaluator',None),(6,'instructor',None)]:
  db.execute('INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,?,?)',(uid,str(uid),str(uid),role,team,b'x',b'x'))
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 for uid in range(1,6):db.execute('INSERT INTO assignments VALUES(1,?)',(uid,))
 teacher={'uid':1,'role':'instructor'};blue={'uid':2,'role':'student','team':'AZUL'};blue2={'uid':3,'role':'student','team':'AZUL'};red={'uid':4,'role':'student','team':'VERMELHO'}
 for user in (blue,red,{'uid':5,'role':'evaluator'},{'uid':6,'role':'instructor'}):
  try:prepare_units(db,user)
  except PermissionError:pass
  else:raise AssertionError('Unauthorized preparation accepted')
 created=prepare_units(db,teacher)
 assert created['created']==2
 all_units=list_units(db,teacher)['units'];assert len(all_units)==2
 assert len({u['unit_id'] for u in all_units})==2
 assert len({u['configuration_version_id'] for u in all_units})==1
 assert list_units(db,blue)['units']==[] and list_units(db,red)['units']==[]
 first=next(u for u in all_units if u['team']=='AZUL')
 db.execute('INSERT INTO party_allocations VALUES(1,?,?,?,?,?)',('AZUL',first['asset_id'],1,1,'2026-11-09'))
 assert list_units(db,blue)['units']==list_units(db,blue2)['units']
 assert list_units(db,blue)['units'][0]['unit_id']==first['unit_id']
 assert list_units(db,red)['units']==[]
 assert prepare_units(db,teacher)['created']==0
 assert db.execute('SELECT count(*) FROM assets').fetchone()[0]==2
 assert db.execute('SELECT count(*) FROM engine_unit_snapshots').fetchone()[0]==2
 assert db.execute("SELECT count(*) FROM events WHERE event_type='engine.units_prepared'").fetchone()[0]==1
 frozen=deepcopy(list_units(db,teacher)['units'])
 with patch('engine_units.controlled_example',return_value={'changed':'catalog'}):
  assert prepare_units(db,teacher)['created']==0
  assert list_units(db,teacher)['units']==frozen
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,2,'New','X','2026-11-09')")
 db.execute('UPDATE exercises SET scenario_version=2 WHERE id=1')
 result=list_units(db,teacher)
 assert result['current_scenario_version']==2 and all(u['snapshot']['scenario_version']==1 for u in result['units'])
 for statement in ["UPDATE engine_unit_snapshots SET snapshot_json='{}'","DELETE FROM engine_unit_snapshots","UPDATE engine_configurations SET input_json='{}'","DELETE FROM engine_configurations"]:
  try:db.execute(statement)
  except sqlite3.IntegrityError:pass
  else:raise AssertionError('Immutable data changed')
 db.execute('UPDATE party_allocations SET active=0 WHERE asset_id=?',(first['asset_id'],))
 assert list_units(db,blue)['units']==[]
 assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
 handler=object.__new__(app.Handler);responses=[]
 handler.send_json=lambda status,body:responses.append((status,body))
 handler.engine_unit_catalog(db,teacher,{})
 assert responses[-1][0]==200 and responses[-1][1]['created']==0
 handler.engine_unit_catalog(db,teacher,{'team':'AZUL'})
 assert responses[-1][0]==400
 handler.engine_unit_catalog(db,blue,{})
 assert responses[-1][0]==403
 handler.engine_unit_catalog(db,blue)
 assert responses[-1][0]==200 and responses[-1][1]['units']==[]
 handler.engine_unit_catalog(db,{'uid':6,'role':'instructor'})
 assert responses[-1][0]==403
 db.execute('DROP TRIGGER engine_snapshot_no_update')
 db.execute("UPDATE engine_unit_snapshots SET snapshot_json='{}'")
 handler.engine_unit_catalog(db,teacher)
 assert responses[-1][0]==503

with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.executescript(app.SCHEMA)
 db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 db.execute('INSERT INTO assignments VALUES(1,1)')
 with patch('engine_units.controlled_example',return_value={}):
  try:prepare_units(db,teacher)
  except ValueError:pass
  else:raise AssertionError('Invalid fixture created units')
 db.executescript("CREATE TRIGGER test_fail_red BEFORE INSERT ON engine_unit_snapshots WHEN NEW.team='VERMELHO' BEGIN SELECT RAISE(ABORT,'test atomic failure'); END;")
 try:prepare_units(db,teacher)
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Injected failure was ignored')
 for table in ('engine_units','engine_unit_snapshots','engine_configurations','assets','events'):
  assert db.execute('SELECT count(*) FROM '+table).fetchone()[0]==0,table
 assert db.execute('SELECT count(*) FROM users').fetchone()[0]==1
 db.execute("UPDATE exercises SET state='closed'")
 try:prepare_units(db,teacher)
 except ValueError:pass
 else:raise AssertionError('Closed exercise accepted preparation')
print('PASS: stable party unit identity, immutable configuration/snapshot, sharing, allocation access, idempotency and source independence')
