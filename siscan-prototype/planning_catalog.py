"""Instâncias DB3K para planejamento, sem promover atributos para cálculo."""
import hashlib,json,uuid
import engine_units,engine_runtime,source_catalog

SCHEMA='''
CREATE TABLE IF NOT EXISTS planning_units(
 asset_id INTEGER PRIMARY KEY REFERENCES assets(id),unit_id TEXT NOT NULL UNIQUE,
 snapshot_json TEXT NOT NULL,snapshot_sha256 TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS planning_catalog_commands(
 command_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL REFERENCES exercises(id),
 actor_id INTEGER NOT NULL REFERENCES users(id),payload_json TEXT NOT NULL,result_json TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS planning_snapshot_no_update BEFORE UPDATE ON planning_units
 BEGIN SELECT RAISE(ABORT,'Planning snapshot is immutable'); END;
CREATE TRIGGER IF NOT EXISTS planning_snapshot_no_delete BEFORE DELETE ON planning_units
 BEGIN SELECT RAISE(ABORT,'Planning snapshot is immutable'); END;
'''
CATEGORIES={'DataAircraft':'Aéreo','DataShip':'Naval','DataSubmarine':'Submarino',
            'DataGroundUnit':'Terrestre','DataFacility':'Instalação','DataSatellite':'Satélite'}
DOMAINS={'DataAircraft':'aereo','DataShip':'naval'}

def digest(value):return hashlib.sha256(engine_units.encoded(value).encode('utf-8')).hexdigest()

def create(db,user,compiled,body):
    exercise=engine_units.context(db,user,write=True)
    if not isinstance(body,dict) or set(body)!={'command_id','table','id','team','quantity'}:
        raise ValueError('Informe comando, categoria, ID, partido e quantidade.')
    try:
        if not isinstance(body['command_id'],str) or str(uuid.UUID(body['command_id']))!=body['command_id']:raise ValueError()
    except (ValueError,AttributeError):raise ValueError('Comando UUID inválido.') from None
    if (not isinstance(body['table'],str) or body['table'] not in CATEGORIES or body['team'] not in ('AZUL','VERMELHO')
        or type(body['quantity']) is not int or not 1<=body['quantity']<=50
        or not isinstance(body['id'],str) or not body['id'].isascii()
        or not body['id'].isdecimal() or not 1<=len(body['id'])<=12):
        raise ValueError('Categoria, ID, partido ou quantidade inválidos; use de 1 a 50 exemplares.')
    payload=engine_units.encoded(body)
    with engine_runtime.atomic(db):
        previous=db.execute('SELECT * FROM planning_catalog_commands WHERE command_id=?',(body['command_id'],)).fetchone()
        if previous:
            if (previous['exercise_id'],previous['actor_id'],previous['payload_json'])!=(exercise['id'],user['uid'],payload):
                raise engine_runtime.Conflict('Comando já utilizado com outro conteúdo ou contexto.')
            return json.loads(previous['result_json'])
        record=source_catalog.detail(compiled,body['table'],body['id'])
        if record is None:raise ValueError('Plataforma não encontrada na compilação.')
        source=dict(source_sha256=record['source']['sha256'],table=body['table'],external_id=str(int(body['id'])),fields=record['fields'])
        configuration='planning:'+digest(source)
        assets=[]
        for _ in range(body['quantity']):
            uid=str(uuid.uuid4());code='PLAN-'+uid
            snapshot=dict(unit_id=uid,exercise_id=exercise['id'],team=body['team'],configuration_version_id=configuration,
                          source_kind='catalog_planning',source=source,official_calculation_ready=False)
            fiche='Referência DB3K para planejamento. Parâmetros de cálculo pendentes; saldo e armamento atuais não definidos.'
            asset=db.execute('INSERT INTO assets(exercise_id,team,code,name,category,fiche,source_label) VALUES(?,?,?,?,?,?,?)',
                (exercise['id'],body['team'],code,record['fields']['Name'],CATEGORIES[body['table']],fiche,'DB3K · planejamento; cálculo pendente')).lastrowid
            db.execute('INSERT INTO planning_units VALUES(?,?,?,?)',(asset,uid,engine_units.encoded(snapshot),digest(snapshot)))
            db.execute("INSERT INTO party_allocations(exercise_id,team,asset_id,allocated_by,active,updated_at) VALUES(?,?,?,?,1,datetime('now'))",
                       (exercise['id'],body['team'],asset,user['uid']))
            assets.append(asset)
        result=dict(asset_ids=assets,team=body['team'],planning_available=True,calculation_ready=False)
        db.execute('INSERT INTO planning_catalog_commands VALUES(?,?,?,?,?)',(body['command_id'],exercise['id'],user['uid'],payload,engine_units.encoded(result)))
        db.execute("INSERT INTO events(exercise_id,actor_id,event_type,detail_json,created_at) VALUES(?,?,?, ?,datetime('now'))",
                   (exercise['id'],user['uid'],'catalog.planning_allocated',engine_units.encoded(dict(**result,source={k:v for k,v in source.items() if k!='fields'}))))
        return result

def instances(db,user,team):
    exercise=engine_units.context(db,user)
    if team not in ('AZUL','VERMELHO') or (user['role']!='instructor' and team!=user['team']):raise PermissionError('Partido não autorizado.')
    result={}
    for row in db.execute('''SELECT p.* FROM planning_units p JOIN assets a ON a.id=p.asset_id
          JOIN party_allocations q ON q.asset_id=a.id AND q.exercise_id=a.exercise_id AND q.team=a.team AND q.active=1
          WHERE a.exercise_id=? AND a.team=?''',(exercise['id'],team)):
        snapshot=json.loads(row['snapshot_json']);domain=DOMAINS.get(snapshot['source']['table'])
        if (digest(snapshot)!=row['snapshot_sha256'] or snapshot.get('unit_id')!=row['unit_id']
            or snapshot.get('exercise_id')!=exercise['id'] or snapshot.get('team')!=team
            or snapshot.get('source_kind')!='catalog_planning' or snapshot.get('official_calculation_ready') is not False):
            raise ValueError('Snapshot de planejamento divergente.')
        if domain:
            result[row['asset_id']]=dict(asset_id=row['asset_id'],unit_id=row['unit_id'],team=team,allocated=True,
                snapshot=snapshot,snapshot_id='planning:'+row['unit_id'],snapshot_sha256=row['snapshot_sha256'],
                configuration_version_id=snapshot['configuration_version_id'],
                domain_evidence=dict(domain=domain,basis='catalog_mapping',reference='planning_catalog/'+snapshot['source']['table']))
    return result
