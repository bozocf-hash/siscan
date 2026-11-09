from pathlib import Path
from contextlib import closing
import json
import sqlite3
import tempfile
from tools.compile_db3k import compile_source
from tools.stage_db3k import digest
from resource_store import build_store, resources

with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'tmp') as folder:
    folder=Path(folder)
    original,compiled,store=(folder/name for name in ('original.db3','compiled.sqlite3','resources.sqlite3'))
    with closing(sqlite3.connect(original)) as db,db:
        db.executescript('''
        CREATE TABLE DataShip(ID INTEGER PRIMARY KEY,Name TEXT);
        CREATE TABLE DataShipFuel(ID INTEGER,ComponentID INTEGER,ComponentNumber INTEGER);
        CREATE TABLE DataShipPropulsion(ID INTEGER,ComponentID INTEGER,ComponentNumber INTEGER);
        CREATE TABLE DataFuel(ID INTEGER PRIMARY KEY,Type INTEGER,Capacity REAL);
        CREATE TABLE DataPropulsion(ID INTEGER PRIMARY KEY,Name TEXT,Type INTEGER,NumberOfEngines REAL);
        CREATE TABLE DataPropulsionPerformance(ID INTEGER,Throttle INTEGER,AltitudeBand INTEGER,Speed REAL,AltitudeMin REAL,AltitudeMax REAL,Consumption REAL);
        INSERT INTO DataShip VALUES(3,'Ship'),(4,'No resources');
        INSERT INTO DataFuel VALUES(8,2001,0),(9,4001,NULL),(10,3001,123.456);
        INSERT INTO DataPropulsion VALUES(50,'Engine',2005,2),(51,'Unused',9001,0);
        INSERT INTO DataShipFuel VALUES(3,8,1),(3,8,2),(3,999,3),(999,9,4),(3,NULL,5);
        INSERT INTO DataShipPropulsion VALUES(3,50,1),(3,50,2);
        INSERT INTO DataPropulsionPerformance VALUES(50,2,1,140,-20,0,7.751234),(999,1,0,0,NULL,0,NULL);
        ''')
    compile_source(original,compiled)
    before=digest(compiled)
    report=build_store(compiled,store)
    assert digest(compiled)==before
    assert report['components']==5 and report['performance_points']==2 and report['installations']==7
    assert report['integrity']=='ok' and report['payloads_verified']==14
    with closing(sqlite3.connect(store)) as db:
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert db.execute('SELECT count(*) FROM components').fetchone()[0]==5
        assert db.execute('SELECT capacity FROM fuel_records WHERE source_id_json=?',('9',)).fetchone()[0] is None
        assert db.execute('SELECT consumption FROM performance WHERE source_rowid=2').fetchone()[0] is None
    result=resources(store,'DataShip','3',digest(original))
    assert result['status']=='available'
    assert len(result['installations'])==6
    assert len(result['components'])==2
    assert len(result['performance'])==1 and result['performance'][0]['consumption']==7.751234
    assert result['performance'][0]['altitude_min']==-20
    assert not result['calculation_ready']
    assert result['performance'][0]['measurements']['Consumption']['unit'] is None
    assert result['performance'][0]['speed']==140
    assert result['performance'][0]['throttle']==2 and result['performance'][0]['altitude_band']==1
    assert result['performance'][0]['altitude_max']==0
    import app
    app.COMPILED_DB_PATH=compiled
    app.RESOURCE_STORE_PATH=store
    with closing(sqlite3.connect(':memory:')) as db:
        db.row_factory=sqlite3.Row
        db.executescript(app.SCHEMA)
        db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
        db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
        db.execute('INSERT INTO assignments VALUES(1,1)')
        handler=object.__new__(app.Handler);responses=[]
        handler.send_json=lambda status,body:responses.append((status,body))
        handler.compiled_catalog(db,{'uid':1,'role':'instructor'},'/api/source-technical','table=DataShip&id=3')
        assert responses[-1][0]==200 and responses[-1][1]['resource_store']['status']=='available'
        for user in ({'uid':1,'role':'student'},{'uid':1,'role':'evaluator'},{'uid':2,'role':'instructor'}):
            handler.compiled_catalog(db,user,'/api/source-technical','table=DataShip&id=3')
            assert responses[-1][0]==403
    assert resources(store,'DataShip','4',digest(original))['installations']==[]
    assert resources(store,'DataShip','99',digest(original))['owner'] is None
    for table,identifier,source_hash in [('Unknown','3',digest(original)),('DataShip','../3',digest(original)),('DataShip','3','wrong')]:
        try:resources(store,table,identifier,source_hash)
        except (ValueError,sqlite3.DatabaseError):pass
        else:raise AssertionError('Invalid source request accepted')
    try:build_store(compiled,store)
    except FileExistsError:pass
    else:raise AssertionError('Existing store overwritten')
    with closing(sqlite3.connect(store)) as db,db:
        db.execute("UPDATE build SET status='building'")
    try:resources(store,'DataShip','3',digest(original))
    except sqlite3.DatabaseError:pass
    else:raise AssertionError('Incomplete store accepted')
print('PASS: normalized resource persistence, shared/repeated/missing links, exact payloads, units, source protection and guarded reads')
