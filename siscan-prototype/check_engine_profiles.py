"""Read-only profile predictions, exact demand and explicit exhaustion."""
from contextlib import closing
import sqlite3,copy,uuid
import app,engine_profiles as profiles
from engine_units import prepare_units
from engine_runtime import start_run,advance_run,Conflict

teacher={'uid':1,'role':'instructor','team':None};student={'uid':2,'role':'student','team':'AZUL'}
with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.executescript(app.SCHEMA)
 for uid,role,team in [(1,'instructor',None),(2,'student','AZUL')]:db.execute("INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,X'00',X'00')",(uid,str(uid),str(uid),role,team))
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 db.executemany('INSERT INTO assignments VALUES(1,?)',[(1,),(2,)])
 prepare_units(db,teacher);run=start_run(db,teacher)
 payload={'run_id':run['run_id'],'unit_id':run['states'][0]['unit_id'],'expected_revision':0,'segments':[{'regime_id':'SYN-ECO','minutes':10},{'regime_id':'SYN-REF','minutes':20},{'regime_id':'SYN-HIGH','minutes':5}]}
 before=list(db.iterdump());changes=db.total_changes
 preview=profiles.preview(db,teacher,payload)
 assert profiles.verify_preview(db,teacher,payload,preview['manifest_sha256'])==preview
 try:profiles.verify_preview(db,teacher,payload,'0'*64)
 except Conflict:pass
 else:raise AssertionError('Unreviewed preview accepted')
 assert preview['duration_minutes']==35 and preview['fuel_required_grams']==65000 and preview['fuel_remaining_grams']==535000 and preview['feasible']
 assert [s['fuel_required_grams'] for s in preview['segments']]==[5000,40000,20000]
 assert preview['curve'][0]['minute_offset']==0 and preview['curve'][-1]['minute_offset']==35
 assert profiles.preview(db,teacher,payload)==preview
 assert list(db.iterdump())==before and db.total_changes==changes
 import fuel_limits
 fuel_limits.set_limit(db,teacher,{'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'unit_id':payload['unit_id'],'expected_revision':0,'expected_limit_revision':0,'minimum_kg':'550'})
 try:profiles.verify_preview(db,teacher,payload,preview['manifest_sha256'])
 except Conflict:pass
 else:raise AssertionError('Changed operator minimum did not invalidate preview')
 exact={**payload,'segments':[{'regime_id':'SYN-HIGH','minutes':150}]};result=profiles.preview(db,teacher,exact)
 assert result['feasible'] and result['fuel_remaining_grams']==0 and result['exhaustion_at_offset_minutes']==150
 short={**payload,'segments':[{'regime_id':'SYN-HIGH','minutes':151}]};result=profiles.preview(db,teacher,short)
 assert not result['feasible'] and result['shortfall_grams']==4000 and result['fuel_remaining_grams']==0
 assert any(p['minute_offset']==150 and p['available_grams']==0 for p in result['curve'])
 assert all(p['available_grams']>=0 for p in result['curve'])
 invalid=[{**payload,'rate':1},{**payload,'segments':[]},{**payload,'segments':[{'regime_id':'UNKNOWN','minutes':1}]},{**payload,'segments':[{'regime_id':'SYN-ECO','minutes':True}]},{**payload,'segments':[{'regime_id':'SYN-ECO','minutes':1.5}]},{**payload,'segments':[{'regime_id':'SYN-ECO','minutes':0}]},{**payload,'segments':[{'regime_id':'SYN-ECO','minutes':1441}]},{**payload,'segments':[{'regime_id':'SYN-ECO','minutes':1000}]*2},{**payload,'segments':payload['segments']*9},{**payload,'unit_id':str(uuid.uuid4())}]
 for body in invalid:
  try:profiles.preview(db,teacher,body)
  except ValueError:pass
  else:raise AssertionError('Invalid plan accepted: '+str(body))
 try:profiles.preview(db,student,payload)
 except PermissionError:pass
 else:raise AssertionError('Student preview accepted')
 advance_run(db,teacher,{'command_id':str(uuid.uuid4()),'run_id':run['run_id'],'minutes':1,'expected_revision':0})
 try:profiles.preview(db,teacher,payload)
 except Conflict:pass
 else:raise AssertionError('Stale basis accepted')
 fraction=profiles.preview(db,teacher,{**payload,'expected_revision':1,'segments':[{'regime_id':'SYN-HIGH','minutes':150}]})
 assert fraction['exhaustion_at_offset_minutes']==149.5 and fraction['shortfall_grams']==2000
 assert fraction['official_calculation_ready'] is False and fraction['debit_applied'] is False
 handler=object.__new__(app.Handler);responses=[];handler.send_json=lambda status,body:responses.append((status,body))
 handler.engine_profile_action(db,student,payload);assert responses[-1][0]==403
 handler.engine_profile_action(db,teacher,{});assert responses[-1][0]==400
 handler.engine_profile_action(db,teacher,payload);assert responses[-1][0]==409
 handler.engine_profile_action(db,teacher);assert responses[-1][0]==200
print('PASS: exact piecewise demand, exhaustion/deficit, deterministic provenance, read-only state, invalid plans, role and stale-revision refusal')
