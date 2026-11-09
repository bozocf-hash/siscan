from contextlib import closing
import sqlite3,uuid
import app,map_units
teacher={'uid':1,'role':'instructor','team':None};blue={'uid':2,'role':'student','team':'AZUL'};red={'uid':3,'role':'student','team':'VERMELHO'}
with closing(sqlite3.connect(':memory:')) as db:
 db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.executescript(app.SCHEMA)
 for u in [teacher,blue,red]:db.execute("INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,X'00',X'00')",(u['uid'],str(u['uid']),str(u['uid']),u['role'],u['team']))
 db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')");db.executemany('INSERT INTO assignments VALUES(1,?)',[(1,),(2,),(3,)])
 for i in [1,2]:
  db.execute("INSERT INTO assets(id,exercise_id,team,code,name,category,fiche) VALUES(?,1,'AZUL',?,'Test','Test','Test')",(i,str(i)))
  db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-09')",(i,))
 body={'command_id':str(uuid.uuid4()),'team':'AZUL','latitude':-22.65,'longitude':-43.05,'units':[{'id':1,'expected_revision':0},{'id':2,'expected_revision':0}]}
 assert map_units.plot(db,blue,body)['plotted']==2
 assert map_units.plot(db,blue,body)['replayed']
 assert db.execute('SELECT count(*) FROM map_unit_positions').fetchone()[0]==2
 assert db.execute("SELECT count(*) FROM events WHERE event_type='map.units_plotted'").fetchone()[0]==1
 try:map_units.listing(db,red,'AZUL')
 except PermissionError:pass
 else:raise AssertionError('Enemy data exposed')
 assert map_units.listing(db,red,'VERMELHO')['units']==[]
 try:map_units.plot(db,blue,{**body,'command_id':str(uuid.uuid4())})
 except app.engine_runtime.Conflict:pass
 else:raise AssertionError('Stale revision accepted')
 before=[tuple(r) for r in db.execute('SELECT * FROM map_unit_positions')]
 db.execute("CREATE TRIGGER fail_plot BEFORE INSERT ON events WHEN NEW.event_type='map.units_plotted' BEGIN SELECT RAISE(ABORT,'test'); END")
 try:map_units.plot(db,blue,{**body,'command_id':str(uuid.uuid4()),'latitude':-20,'units':[{'id':1,'expected_revision':1}]})
 except sqlite3.IntegrityError:pass
 else:raise AssertionError('Failed audit did not abort')
 assert [tuple(r) for r in db.execute('SELECT * FROM map_unit_positions')]==before
 listed=map_units.listing(db,blue,'AZUL')['units'][0]
 assert listed['name']=='Test' and listed['combat_capability'] is None and listed['operational_availability'] is None and listed['fuel'] is None
 db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'X','X','2026-11-09')")
 app.engine_units.prepare_units(db,teacher);app.engine_runtime.start_run(db,teacher)
 synthetic=db.execute("SELECT * FROM engine_units WHERE team='AZUL'").fetchone()
 db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-09')",(synthetic['asset_id'],))
 item=next(u for u in map_units.listing(db,blue,'AZUL')['units'] if u['id']==synthetic['asset_id'])
 assert item['fuel']=={'remaining_kg':600,'capacity_kg':1000,'source':'synthetic_controlled'}
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
print('PASS: adjudicated party scope, batch plot, UUID identity, idempotency, stale revisions and full rollback')
