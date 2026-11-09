"""Operator-owned thresholds, shared party state, exact crossing and audit."""
from contextlib import closing
import sqlite3,uuid
import app,engine_runtime as runtime,fuel_limits
from engine_units import prepare_units,list_units

teacher={'uid':1,'role':'instructor','team':None};blue={'uid':2,'role':'student','team':'AZUL'};peer={'uid':3,'role':'student','team':'AZUL'};red={'uid':4,'role':'student','team':'VERMELHO'}
with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.executescript(app.SCHEMA)
 for user in [teacher,blue,peer,red]:db.execute("INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,X'00',X'00')",(user['uid'],str(user['uid']),str(user['uid']),user['role'],user['team']))
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 db.executemany('INSERT INTO assignments VALUES(1,?)',[(u['uid'],) for u in [teacher,blue,peer,red]])
 prepare_units(db,teacher);run=runtime.start_run(db,teacher);unit=next(u for u in list_units(db,teacher)['units'] if u['team']=='AZUL')
 payload={'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'unit_id':unit['unit_id'],'expected_revision':0,'expected_limit_revision':0,'minimum_kg':'550'}
 try:fuel_limits.set_limit(db,blue,payload)
 except PermissionError:pass
 else:raise AssertionError('Unallocated operator changed threshold')
 db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-09')",(unit['asset_id'],))
 result=fuel_limits.set_limit(db,blue,payload);assert result['limit']['minimum_grams']==550000 and result['limit']['status']=='above_minimum'
 assert fuel_limits.set_limit(db,peer,payload)['replayed']
 assert runtime.read_runtime(db,blue)==runtime.read_runtime(db,peer)
 assert runtime.read_runtime(db,red)['states']==[]
 try:fuel_limits.set_limit(db,red,{**payload,'command_id':str(uuid.uuid4())})
 except PermissionError:pass
 else:raise AssertionError('Opponent changed limit')
 for value in ['-1','1000.001','NaN','Infinity','0.0001',True,550]:
  try:fuel_limits.set_limit(db,blue,{**payload,'command_id':str(uuid.uuid4()),'expected_limit_revision':1,'minimum_kg':value})
  except ValueError:pass
  else:raise AssertionError('Invalid threshold accepted')
 try:fuel_limits.set_limit(db,peer,{**payload,'command_id':str(uuid.uuid4())})
 except runtime.Conflict:pass
 else:raise AssertionError('Concurrent overwrite accepted')
 first=runtime.advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'minutes':25,'expected_revision':0})
 selected=next(s for s in first['states'] if s['team']=='AZUL');assert selected['minimum_alert']['status']=='at_minimum'
 assert db.execute("SELECT count(*) FROM events WHERE event_type='engine.fuel_minimum_reached'").fetchone()[0]==1
 import engine_profiles
 forecast=engine_profiles.preview(db,teacher,{'run_id':run['run_id'],'unit_id':unit['unit_id'],'expected_revision':1,'segments':[{'regime_id':'SYN-REF','minutes':1}]})
 assert forecast['minimum_reached_at_offset_minutes']==0
 second=runtime.advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'minutes':1,'expected_revision':1})
 assert next(s for s in second['states'] if s['team']=='AZUL')['minimum_alert']['status']=='below_minimum'
 assert db.execute("SELECT count(*) FROM events WHERE event_type='engine.fuel_minimum_reached'").fetchone()[0]==1
 changed=fuel_limits.set_limit(db,blue,{**payload,'command_id':str(uuid.uuid4()),'expected_revision':2,'expected_limit_revision':1,'minimum_kg':'560'})
 assert changed['limit']['active']
 cleared=fuel_limits.set_limit(db,blue,{**payload,'command_id':str(uuid.uuid4()),'expected_revision':2,'expected_limit_revision':2,'minimum_kg':None})
 assert cleared['limit']['status']=='not_configured'
 disabled=engine_profiles.preview(db,teacher,{'run_id':run['run_id'],'unit_id':unit['unit_id'],'expected_revision':2,'segments':[{'regime_id':'SYN-REF','minutes':1}]})
 assert disabled['minimum_reached_at_offset_minutes'] is None
 db.execute("CREATE TRIGGER fail_limit BEFORE INSERT ON events WHEN NEW.event_type='engine.fuel_limit_changed' BEGIN SELECT RAISE(ABORT,'fail'); END")
 try:fuel_limits.set_limit(db,blue,{**payload,'command_id':str(uuid.uuid4()),'expected_revision':2,'expected_limit_revision':3,'minimum_kg':'0'})
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Partial limit write accepted')
 assert fuel_limits.status(db,unit['unit_id'],548000)['version']==3
 db.execute('DROP TRIGGER fail_limit')
 zero=fuel_limits.set_limit(db,teacher,{**payload,'command_id':str(uuid.uuid4()),'expected_revision':2,'expected_limit_revision':3,'minimum_kg':'0'})
 assert zero['limit']['minimum_grams']==0 and not zero['limit']['active']
 before=runtime.read_runtime(db,teacher)
 events_before=db.execute('SELECT count(*) FROM events').fetchone()[0]
 db.execute("CREATE TRIGGER fail_crossing BEFORE INSERT ON events WHEN NEW.event_type='engine.fuel_minimum_reached' BEGIN SELECT RAISE(ABORT,'fail'); END")
 try:runtime.advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'minutes':274,'expected_revision':2})
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Alert failure allowed partial consumption')
 assert runtime.read_runtime(db,teacher)==before
 assert db.execute('SELECT count(*) FROM events').fetchone()[0]==events_before
 db.execute('DROP TRIGGER fail_crossing')
 end_command={'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'minutes':274,'expected_revision':2}
 end=runtime.advance_run(db,teacher,end_command)
 assert next(s for s in end['states'] if s['team']=='AZUL')['minimum_alert']['fuel_exhausted']
 count=db.execute('SELECT count(*) FROM events').fetchone()[0]
 assert runtime.advance_run(db,teacher,end_command)['replayed']
 assert db.execute('SELECT count(*) FROM events').fetchone()[0]==count
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
print('PASS: per-unit operator/instructor policy, party sharing/privacy, threshold versions, equality/crossing, no repeated alerts and explicit disable')
