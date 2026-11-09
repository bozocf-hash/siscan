from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
from tools.stage_db3k import digest
from tools.compile_db3k import compile_source
import source_catalog
import app

scratch = Path(__file__).resolve().parent.parent/'tmp'
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source, target = Path(folder)/'source.db3', Path(folder)/'compiled.sqlite3'
    with closing(sqlite3.connect(source)) as db, db:
        db.executescript('''
        CREATE TABLE DataShip(ID INTEGER PRIMARY KEY,Name TEXT,Category INTEGER);
        CREATE TABLE EnumShipCategory(ID INTEGER PRIMARY KEY,Description TEXT);
        CREATE TABLE DataMount(ID INTEGER PRIMARY KEY,Name TEXT);
        CREATE TABLE DataShipMounts(ID INTEGER REFERENCES DataShip(ID),ComponentID INTEGER);
        CREATE TABLE DataMountWeapons(ID INTEGER REFERENCES DataMount(ID),ComponentID INTEGER);
        CREATE TABLE DataWeaponRecord(ID INTEGER PRIMARY KEY,ComponentID INTEGER,DefaultLoad INTEGER);
        CREATE TABLE DataWeapon(ID INTEGER PRIMARY KEY,Name TEXT);
        CREATE TABLE DataShipSignatures(ID INTEGER,Type INTEGER);
        CREATE TABLE EnumSignatureType(ID INTEGER PRIMARY KEY,Description TEXT);
        CREATE TABLE EnumShipType(ID INTEGER PRIMARY KEY,Description TEXT);
        INSERT INTO DataShip VALUES(1,'Ship <raw>',2);
        INSERT INTO EnumShipCategory VALUES(2,'Literal category');
        INSERT INTO DataMount VALUES(7,'Mount');
        INSERT INTO DataShipMounts VALUES(1,7);
        INSERT INTO DataShipMounts VALUES(1,999);
        INSERT INTO DataShipMounts VALUES(1,NULL);
        INSERT INTO DataMountWeapons VALUES(7,99);
        INSERT INTO DataWeaponRecord VALUES(99,3,8);
        INSERT INTO DataWeapon VALUES(3,'Weapon');
        INSERT INTO DataShipSignatures VALUES(1,1);
        INSERT INTO EnumSignatureType VALUES(1,'Signature type');
        INSERT INTO EnumShipType VALUES(1,'Different domain with same code');
        ''')
    original = digest(source)
    result = compile_source(source, target)
    assert result['tables'] == 10 and result['declared_rules'] == 2
    with closing(sqlite3.connect(target)) as db:
        rules = db.execute('SELECT from_table,from_column,to_table,basis FROM relations').fetchall()
        assert ('DataMountWeapons','ComponentID','DataWeaponRecord','structural_pattern') in rules
        assert ('DataWeaponRecord','ComponentID','DataWeapon','structural_pattern') in rules
        assert not any(a=='DataShipSignatures' and c=='EnumShipType' for a,b,c,_ in rules)
        assert not any(a=='DataShipMounts' and b=='ComponentID' and c=='DataWeapon' for a,b,c,_ in rules)
        stats = dict(db.execute("SELECT l.status,count(*) FROM links l JOIN relations r ON r.id=l.relation_id WHERE r.from_table='DataShipMounts' AND r.from_column='ComponentID' GROUP BY l.status"))
        assert stats == {'matched':1,'missing':1,'null':1}
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert digest(source) == original
    listing = source_catalog.browse(target,'DataShip')
    assert listing['total']==1 and listing['items'][0]['name']=='Ship <raw>'
    card = source_catalog.detail(target,'DataShip','1')
    assert card['domains']['Category']['description']=='Literal category'
    assert len(card['groups']['DataShipMounts'])==3
    assert card['groups']['DataShipMounts'][0]['target_name']=='Mount'
    mount = source_catalog.detail(target,'DataMount','7')
    assert mount['groups']['DataMountWeapons'][0]['target_id']==99
    assert mount['groups']['DataMountWeapons'][0]['target_name']=='Weapon'
    weapon_record = source_catalog.detail(target,'DataWeaponRecord','99')
    assert weapon_record['direct_links'][0]['id']==3
    assert source_catalog.detail(target,'DataShip','999') is None
    app.COMPILED_DB_PATH=target
    app.CMO_IMAGE_DIR=Path(folder)/'no-images'
    with closing(sqlite3.connect(':memory:')) as db:
        db.row_factory=sqlite3.Row
        db.executescript(app.SCHEMA)
        db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
        db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
        db.execute('INSERT INTO assignments VALUES(1,1)')
        handler=object.__new__(app.Handler)
        responses=[]
        handler.send_json=lambda status,body:responses.append((status,body))
        for user in ({'uid':1,'role':'student'},{'uid':1,'role':'evaluator'},{'uid':2,'role':'instructor'}):
            handler.compiled_catalog(db,user,'/api/source-platform','table=DataShip&id=1')
            assert responses[-1][0]==403
            handler.compiled_catalog(db,user,'/api/source-technical','table=DataShip&id=1')
            assert responses[-1][0]==403
        teacher={'uid':1,'role':'instructor'}
        handler.compiled_catalog(db,teacher,'/api/source-platform','table=DataShip&id=1')
        assert responses[-1][0]==200 and responses[-1][1]['photo_url'] is None
        handler.compiled_catalog(db,teacher,'/api/source-technical','table=DataShip&id=1')
        assert responses[-1][0]==200 and responses[-1][1]['complete'] is True
        handler.compiled_catalog(db,teacher,'/api/source-platform','table=DataShip&id=999')
        assert responses[-1][0]==404
        for query in ('table=DataShip&id=../1','table=Unknown&id=1','id=1&id=2'):
            handler.compiled_catalog(db,teacher,'/api/source-platform',query)
            assert responses[-1][0]==400
        handler.compiled_catalog(db,teacher,'/api/source-photo','table=DataShip&id=1')
        assert responses[-1][0]==404
    for table,identifier in [('DataShip','../3'),('Unknown','1')]:
        try:
            source_catalog.detail(target,table,identifier)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid source query accepted')
    try:
        compile_source(source,target)
    except ValueError:
        pass
    else:
        raise AssertionError('Existing compilation overwritten')
    print('PASS: all tables, declared links, component chains, unresolved/NULL preservation and immutable source')
