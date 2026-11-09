from copy import deepcopy
from pathlib import Path
from contextlib import closing
import json,sqlite3,tempfile
from engine_input import validate_input, controlled_example, inspect_catalog
from tools.compile_db3k import compile_source
from tools.stage_db3k import digest
from resource_store import build_store
from technical_units import VERSION

payload=controlled_example();original=deepcopy(payload)
accepted=validate_input(payload)
assert accepted['accepted'] and accepted['accepted_for']=='synthetic_contract_test'
assert accepted['official_calculation_ready'] is False and accepted['errors']==[]
assert validate_input(payload)==accepted and payload==original
cases=[]
def bad(change,code,field):
 value=deepcopy(payload);change(value);cases.append((value,code,field))
bad(lambda p:p.pop('configuration_id'),'required','configuration_id')
bad(lambda p:p.update(schema_version='other'),'version_mismatch','schema_version')
bad(lambda p:p.update(data_kind='command'),'unsupported_source','data_kind')
bad(lambda p:p.update(approved=True),'unknown_field','approved')
bad(lambda p:p['measurements']['fuel_initial'].update(unit='L'),'unit_mismatch','measurements.fuel_initial.unit')
bad(lambda p:p['measurements']['duration'].update(unit='s'),'unit_mismatch','measurements.duration.unit')
bad(lambda p:p['measurements']['duration'].update(value=True),'number_invalid','measurements.duration.value')
bad(lambda p:p['measurements']['consumption_rate'].update(value=float('nan')),'number_invalid','measurements.consumption_rate.value')
bad(lambda p:p['measurements']['fuel_capacity'].update(value=2**1024),'number_invalid','measurements.fuel_capacity.value')
bad(lambda p:p['measurements']['consumption_rate'].update(value=-1),'domain_invalid','measurements.consumption_rate.value')
bad(lambda p:p['measurements']['duration'].update(value=0),'domain_invalid','measurements.duration.value')
bad(lambda p:p['measurements']['fuel_initial'].update(value=1001),'capacity_exceeded','measurements.fuel_initial.value')
bad(lambda p:p['measurements']['fuel_initial'].update(value=599),'dataset_mismatch','dataset_id')
for value,code,field in cases:
 result=validate_input(value)
 assert not result['accepted'] and any(e['code']==code and e['field']==field for e in result['errors']),(code,result)
for value in (None,[],{'measurements':None}):assert not validate_input(value)['accepted']

with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'tmp') as folder:
 folder=Path(folder);source=folder/'source.db3';compiled=folder/'compiled.sqlite3';resources=folder/'resources.sqlite3'
 with closing(sqlite3.connect(source)) as db,db:db.execute('CREATE TABLE DataShip(ID INTEGER PRIMARY KEY,Name TEXT)')
 compile_source(source,compiled);build_store(compiled,resources)
 hashes=[digest(p) for p in (source,compiled,resources)]
 result=inspect_catalog(source,compiled,resources)
 assert result['structurally_compatible'] and not result['official_calculation_ready']
 assert [digest(p) for p in (source,compiled,resources)]==hashes
 with closing(sqlite3.connect(resources)) as db,db:db.execute("UPDATE build SET compiled_sha256='wrong'")
 result=inspect_catalog(source,compiled,resources)
 assert not result['structurally_compatible'] and any(c['id']=='compilation_matches_resources' and not c['ok'] for c in result['checks'])
 with closing(sqlite3.connect(resources)) as db,db:db.execute('UPDATE build SET compiled_sha256=?, units_version=?',(hashes[1],'wrong'))
 assert not inspect_catalog(source,compiled,resources)['structurally_compatible']
 assert not inspect_catalog(folder/'missing',compiled,resources)['structurally_compatible']
 import app
 app.ENGINE_SOURCE_PATH=source;app.COMPILED_DB_PATH=compiled;app.RESOURCE_STORE_PATH=resources
 with closing(sqlite3.connect(':memory:')) as db:
  db.row_factory=sqlite3.Row;db.executescript(app.SCHEMA)
  db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
  db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
  db.execute('INSERT INTO assignments VALUES(1,1)')
  handler=object.__new__(app.Handler);responses=[]
  handler.send_json=lambda status,body:responses.append((status,body))
  handler.engine_readiness(db,{'uid':1,'role':'instructor'})
  assert responses[-1][0]==200 and responses[-1][1]['validation']['accepted']
  assert not responses[-1][1]['simulation_started']
  assert not responses[-1][1]['catalog']['structurally_compatible']
  for user in ({'uid':1,'role':'student'},{'uid':1,'role':'evaluator'},{'uid':2,'role':'instructor'}):
   handler.engine_readiness(db,user);assert responses[-1][0]==403
print('PASS: controlled contract, units/domains, trusted dataset/version, explicit refusals and read-only cross-build checks')
