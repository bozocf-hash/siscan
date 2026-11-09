from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
from tools.compile_db3k import compile_source
from source_catalog import technical_bundle
from tools.audit_compilation import audit_source

scratch=Path(__file__).resolve().parent.parent/'tmp'
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as directory:
    source,target=Path(directory)/'source.db3',Path(directory)/'compiled.sqlite3'
    with closing(sqlite3.connect(source)) as db,db:
        db.executescript('''
        CREATE TABLE DataShip(ID INTEGER PRIMARY KEY,Name TEXT);
        CREATE TABLE DataShipSensors(ID INTEGER REFERENCES DataShip(ID),ComponentID INTEGER);
        CREATE TABLE DataSensor(ID INTEGER PRIMARY KEY,Name TEXT,RangeMax REAL,Comments TEXT,MasqueradeAs INTEGER);
        CREATE TABLE DataSensorSensorGroups(ID INTEGER REFERENCES DataSensor(ID),ComponentID INTEGER);
        CREATE TABLE DataSensorFrequencySearchAndTrack(ID INTEGER REFERENCES DataSensor(ID),Frequency INTEGER);
        CREATE TABLE EnumSensorFrequency(ID INTEGER PRIMARY KEY,Description TEXT);
        CREATE TABLE DataShipFuel(ID INTEGER REFERENCES DataShip(ID),ComponentID INTEGER);
        CREATE TABLE DataFuel(ID INTEGER PRIMARY KEY,Type INTEGER,Capacity INTEGER);
        CREATE TABLE EnumFuelType(ID INTEGER PRIMARY KEY,Description TEXT);
        CREATE TABLE DataShipPropulsion(ID INTEGER REFERENCES DataShip(ID),ComponentID INTEGER);
        CREATE TABLE DataPropulsion(ID INTEGER PRIMARY KEY,Name TEXT,SFCMilitary REAL);
        CREATE TABLE DataPropulsionPerformance(ID INTEGER REFERENCES DataPropulsion(ID),AltitudeBand INTEGER,Throttle INTEGER,Speed INTEGER,Consumption REAL);
        INSERT INTO DataShip VALUES(1,'Ship');
        INSERT INTO DataShipSensors VALUES(1,2);
        INSERT INTO DataShipSensors VALUES(1,2);
        INSERT INTO DataShipSensors VALUES(1,999);
        INSERT INTO DataSensor VALUES(2,'Sensor <raw>',35.5,NULL,2);
        INSERT INTO DataSensorSensorGroups VALUES(2,2);
        INSERT INTO DataSensorFrequencySearchAndTrack VALUES(2,4);
        INSERT INTO EnumSensorFrequency VALUES(4,'Frequency band');
        INSERT INTO DataShipFuel VALUES(1,3);
        INSERT INTO DataFuel VALUES(3,3002,0);
        INSERT INTO EnumFuelType VALUES(3002,'OilFuel');
        INSERT INTO DataShipPropulsion VALUES(1,5);
        INSERT INTO DataPropulsion VALUES(5,'Engine',0.123456);
        INSERT INTO DataPropulsionPerformance VALUES(5,0,1,10,2.123456);
        INSERT INTO DataPropulsionPerformance VALUES(5,1,2,20,3.987654);
        ''')
    compile_source(source,target)
    result=technical_bundle(target,'DataShip','1')
    assert result['complete'] is True
    nodes=result['nodes']
    assert len({(n['table'],n['rowid']) for n in nodes})==len(nodes)
    sensors=[n for n in nodes if n['table']=='DataSensor']
    assert len(sensors)==1 and sensors[0]['fields']['RangeMax']==35.5
    assert sensors[0]['fields']['Comments'] is None
    assert len([n for n in nodes if n['table']=='DataShipSensors'])==3
    assert len([n for n in nodes if n['table']=='DataPropulsionPerformance'])==2
    assert [n for n in nodes if n['table']=='DataFuel'][0]['fields']['Capacity']==0
    assert any(n['fields'].get('Description')=='OilFuel' for n in nodes)
    assert any(n['fields'].get('Description')=='Frequency band' for n in nodes)
    assert len([e for e in result['links'] if e['status']=='missing'])==1
    assert result['field_count']==sum(len(n['fields']) for n in nodes)
    assert result['measurement_contract_version']=='db3k-498-units-01'
    profile=result['consumption_profiles'][0]
    assert profile['direct'] and len(profile['points'])==2
    assert profile['average_consumption'] is None and not profile['calculation_ready']
    assert all(point['measurements']['Consumption']['unit'] is None for point in profile['points'])
    assert profile['points'][0]['values']['Consumption']==2.123456
    assert technical_bundle(target,'DataShip','999') is None
    report=audit_source(source,target,Path(directory)/'audit.json')
    assert report['tables']==12 and report['status']=='all_source_values_matched'
    with closing(sqlite3.connect(target)) as db,db:
        db.execute("UPDATE records SET payload_json='{}' WHERE table_name='DataFuel'")
    try:
        audit_source(source,target,Path(directory)/'invalid-audit.json')
    except ValueError:
        pass
    else:
        raise AssertionError('Lost source values were not detected')
    print('PASS: complete recursive sensor/fuel/performance bundle, cycles, shared components, repeated installations, missing links and raw precision')
