"""Authoritative party-scoped plotting of adjudicated asset identities."""
import json,math,uuid
import engine_units,engine_runtime
SCHEMA='''
CREATE TABLE IF NOT EXISTS map_unit_positions(asset_id INTEGER PRIMARY KEY REFERENCES assets(id),latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),revision INTEGER NOT NULL,actor_id INTEGER NOT NULL REFERENCES users(id));
CREATE TABLE IF NOT EXISTS map_plot_commands(command_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL REFERENCES exercises(id),team TEXT NOT NULL,payload_json TEXT NOT NULL,result_json TEXT NOT NULL);
'''
def context(db,user,team):
 exercise=engine_units.context(db,user)
 if team not in ('AZUL','VERMELHO') or (user['role']!='instructor' and team!=user['team']):raise PermissionError('Partido não autorizado.')
 return exercise
def listing(db,user,team):
 exercise=context(db,user,team)
 rows=[dict(r) for r in db.execute('''SELECT a.id,a.code,a.name,a.category,a.source_label,a.fiche,p.latitude,p.longitude,coalesce(p.revision,0) AS position_revision FROM assets a
 JOIN party_allocations q ON q.asset_id=a.id AND q.exercise_id=a.exercise_id AND q.team=a.team AND q.active=1
 LEFT JOIN map_unit_positions p ON p.asset_id=a.id WHERE a.exercise_id=? AND a.team=? ORDER BY a.code''',(exercise['id'],team))]
 for unit in rows:
  unit['combat_capability']=None;unit['operational_availability']=None;unit['fuel']=None
  fuel=db.execute('''SELECT s.* FROM engine_units u JOIN engine_resource_states s ON s.unit_id=u.unit_id
    JOIN engine_runs r ON r.run_id=s.run_id WHERE u.asset_id=? AND r.exercise_id=? ORDER BY r.rowid DESC LIMIT 1''',(unit['id'],exercise['id'])).fetchone()
  if fuel:unit['fuel']={'remaining_kg':fuel['remaining_grams']/1000,'capacity_kg':fuel['capacity_grams']/1000,'source':'synthetic_controlled'}
 return {'units':rows,'team':team,'scope':'planning_positions','geographic_validation':'terrain_and_support_compatibility_pending'}
def plot(db,user,body):
 if not isinstance(body,dict) or set(body)!={'command_id','team','latitude','longitude','units'}:raise ValueError('Informe comando, partido, coordenadas e unidades.')
 try:valid=isinstance(body['command_id'],str) and str(uuid.UUID(body['command_id']))==body['command_id']
 except ValueError:valid=False
 if not valid:raise ValueError('Comando inválido.')
 for key,limit in [('latitude',90),('longitude',180)]:
  value=body[key]
  if type(value) not in (int,float) or not math.isfinite(value) or not -limit<=value<=limit:raise ValueError('Coordenada inválida.')
 units=body['units']
 if not isinstance(units,list) or not 1<=len(units)<=100:raise ValueError('Selecione de 1 a 100 meios.')
 if any(not isinstance(u,dict) or set(u)!={'id','expected_revision'} or type(u['id']) is not int or type(u['expected_revision']) is not int or u['expected_revision']<0 for u in units):raise ValueError('Identidade ou revisão inválida.')
 if len({u['id'] for u in units})!=len(units):raise ValueError('Meios duplicados na solicitação.')
 with engine_runtime.atomic(db):
  exercise=context(db,user,body['team'])
  if exercise['state']!='open':raise ValueError('Exercício encerrado.')
  available={u['id']:u for u in listing(db,user,body['team'])['units']}
  if any(u['id'] not in available for u in units):raise PermissionError('Meio não adjudicado ao partido.')
  prior=db.execute('SELECT * FROM map_plot_commands WHERE command_id=?',(body['command_id'],)).fetchone()
  if prior:
   if prior['payload_json']!=engine_units.encoded(body) or prior['exercise_id']!=exercise['id']:raise engine_runtime.Conflict('Comando já usado com outro conteúdo.')
   return {**json.loads(prior['result_json']),'replayed':True}
  if any(available[u['id']]['position_revision']!=u['expected_revision'] for u in units):raise engine_runtime.Conflict('Posições alteradas por outro operador. Atualize a lista.')
  for unit in units:
   db.execute('INSERT INTO map_unit_positions VALUES(?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET latitude=excluded.latitude,longitude=excluded.longitude,revision=excluded.revision,actor_id=excluded.actor_id',(unit['id'],body['latitude'],body['longitude'],unit['expected_revision']+1,user['uid']))
  result={'ok':True,'plotted':len(units),'replayed':False}
  db.execute('INSERT INTO map_plot_commands VALUES(?,?,?,?,?)',(body['command_id'],exercise['id'],body['team'],engine_units.encoded(body),engine_units.encoded(result)))
  db.execute('INSERT INTO events(exercise_id,actor_id,event_type,detail_json) VALUES(?,?,?,?)',(exercise['id'],user['uid'],'map.units_plotted',engine_units.encoded({'request':body,'previous_positions':[available[u['id']] for u in units],'scope':'planning_only'})))
  return result
