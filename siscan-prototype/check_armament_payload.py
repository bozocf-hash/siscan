from copy import deepcopy
from armament_payload import assess_payload

def node(key,table,fields):return {'key':key,'table':table,'rowid':int(key[1:]),'id':fields.get('ID'),'fields':fields}
nodes=[node('r1','DataAircraft',{'ID':1,'WeightPayload':100,'WeightEmpty':500,'WeightMax':1000}),
       node('a1','DataAircraftLoadouts',{'ID':1,'ComponentID':10}),node('c1','DataLoadout',{'ID':10,'Name':'First'}),
       node('a2','DataAircraftLoadouts',{'ID':1,'ComponentID':20}),node('c2','DataLoadout',{'ID':20,'Name':'Alternative'}),
       node('e1','DataLoadoutWeapons',{'ID':10,'ComponentID':30,'ComponentNumber':99,'Optional':0,'Internal':1}),
       node('e2','DataLoadoutWeapons',{'ID':10,'ComponentID':30,'ComponentNumber':100,'Optional':1,'Internal':0}),
       node('e3','DataLoadoutWeapons',{'ID':20,'ComponentID':30,'ComponentNumber':1,'Optional':0,'Internal':0}),
       node('w1','DataWeaponRecord',{'ID':30,'ComponentID':40,'DefaultLoad':2,'MaxLoad':4,'Multiple':1}),
       node('m1','DataWeapon',{'ID':40,'Name':'Weapon','Weight':12.5})]
links=[]
def edge(source,field,target):links.append({'source':source,'field':field,'target':target})
for a,c in [('a1','c1'),('a2','c2')]:edge(a,'ID','r1');edge(a,'ComponentID',c)
for e,c in [('e1','c1'),('e2','c1'),('e3','c2')]:edge(e,'ID',c);edge(e,'ComponentID','w1')
edge('w1','ComponentID','m1')
before=deepcopy(nodes)
r=assess_payload(nodes,links,'r1')
assert nodes==before
assert len(r['groups'])==2 and r['declared_payload']==100
assert r['operational_available_payload'] is None and not r['calculation_ready']
g=r['groups'][0]
assert len(g['items'])==2 and g['nominal_default_mass']==25 and g['reference_balance']==75
assert g['items'][0]['unit_weight']==12.5 and g['items'][0]['nominal_mass']==25
assert r['groups'][1]['nominal_default_mass']==25
nested=nodes+[node('b1','DataWeaponWeapons',{'ID':40}),node('m2','DataWeapon',{'ID':99,'Weight':999})]
nested_links=links+[{'source':'b1','field':'ID','target':'m1'},{'source':'b1','field':'ComponentID','target':'m2'}]
assert assess_payload(nested,nested_links,'r1')['groups'][0]['nominal_default_mass']==25
for changes,issue in [({'Weight':0},'weight_unresolved'),({'Weight':None},'weight_unresolved')]:
 altered=deepcopy(nodes);altered[-1]['fields'].update(changes)
 result=assess_payload(altered,links,'r1')['groups'][0]
 assert result['nominal_default_mass'] is None and result['reference_balance'] is None
 assert issue in result['items'][0]['issues']
for changes,issue in [({'Multiple':0},'multiple_unresolved'),({'Multiple':2},'multiple_unresolved'),({'DefaultLoad':5},'default_exceeds_max'),({'DefaultLoad':-1},'quantity_invalid')]:
 altered=deepcopy(nodes);altered[-2]['fields'].update(changes)
 result=assess_payload(altered,links,'r1')['groups'][0]
 assert result['nominal_default_mass'] is None and issue in result['items'][0]['issues']
altered=deepcopy(nodes);altered[0]['fields']['WeightPayload']=20
assert assess_payload(altered,links,'r1')['groups'][0]['comparison']=='reference_exceeds'
altered=deepcopy(nodes);altered[0]['fields']['WeightPayload']=0
assert assess_payload(altered,links,'r1')['groups'][0]['reference_balance'] is None
broken=[l for l in links if not (l['source']=='w1' and l['field']=='ComponentID')]
assert 'weapon_unresolved' in assess_payload(nodes,broken,'r1')['groups'][0]['items'][0]['issues']
altered=deepcopy(nodes);altered[0]['table']='DataShip'
assert assess_payload(altered,links,'r1')['declared_payload'] is None
altered=deepcopy(nodes);altered[5]['fields']['Optional']=None
assert assess_payload(altered,links,'r1')['groups'][0]['nominal_default_mass'] is None
naval=[node('s1','DataShip',{'ID':1}),node('a3','DataShipMounts',{'ID':1}),node('a4','DataShipMounts',{'ID':1}),
       node('c3','DataMount',{'ID':50,'Name':'Mount'}),node('e4','DataMountWeapons',{'ID':50}),
       node('e5','DataMountMagazineWeapons',{'ID':50}),nodes[-2],nodes[-1]]
naval_links=[{'source':s,'field':f,'target':t} for s,f,t in [('a3','ID','s1'),('a4','ID','s1'),('a3','ComponentID','c3'),('a4','ComponentID','c3'),('e4','ID','c3'),('e5','ID','c3'),('e4','ComponentID','w1'),('e5','ComponentID','w1'),('w1','ComponentID','m1')]]
ng=assess_payload(naval,naval_links,'s1')['groups']
assert len(ng)==4 and all(g['nominal_default_mass']==25 and g['reference_balance'] is None for g in ng)

from pathlib import Path
from contextlib import closing
import sqlite3,tempfile
from tools.compile_db3k import compile_source
from tools.audit_armament_payload import audit_payload
with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'tmp') as folder:
 folder=Path(folder);original=folder/'source.db3';compiled=folder/'compiled.sqlite3';output=folder/'audit.json'
 with closing(sqlite3.connect(original)) as db,db:
  db.executescript('''
  CREATE TABLE DataAircraft(ID INTEGER PRIMARY KEY,WeightPayload REAL);
  CREATE TABLE DataAircraftLoadouts(ID INTEGER,ComponentID INTEGER);
  CREATE TABLE DataLoadout(ID INTEGER PRIMARY KEY,Name TEXT);
  CREATE TABLE DataLoadoutWeapons(ID INTEGER,ComponentID INTEGER,Optional INTEGER,Internal INTEGER);
  CREATE TABLE DataWeaponRecord(ID INTEGER PRIMARY KEY,ComponentID INTEGER,DefaultLoad INTEGER,MaxLoad INTEGER,Multiple INTEGER);
  CREATE TABLE DataWeapon(ID INTEGER PRIMARY KEY,Name TEXT,Weight REAL);
  INSERT INTO DataAircraft VALUES(1,100);
  INSERT INTO DataAircraftLoadouts VALUES(1,10),(1,20);
  INSERT INTO DataLoadout VALUES(10,'First'),(20,'Alternative');
  INSERT INTO DataLoadoutWeapons VALUES(10,30,0,1),(10,30,1,0),(20,30,0,0);
  INSERT INTO DataWeaponRecord VALUES(30,40,2,4,1);
  INSERT INTO DataWeapon VALUES(40,'Weapon',12.5);
  ''')
 compile_source(original,compiled)
 report=audit_payload(compiled,output)
 assert report['loadouts']==2 and report['loadout_weapon_rows_examined']==3
 assert report['aircraft_associations']=={'reference_within':2}
 try:audit_payload(compiled,output)
 except FileExistsError:pass
 else:raise AssertionError('Audit replaced an existing output')
print('PASS: per-loadout weapon mass and payload reference, alternatives/options, quantities, incomplete masses, anomalies and operational guard')
