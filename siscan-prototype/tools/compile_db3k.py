"""Compile a read-only source snapshot and measured association graph, without promotion."""
import argparse
import base64
from collections import Counter, defaultdict
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tools.stage_db3k import digest

MASTERS = ('DataAircraft','DataShip','DataSubmarine','DataGroundUnit','DataFacility','DataSatellite',
           'DataSensor','DataMount','DataMagazine','DataLoadout','DataWeaponRecord','DataWeapon',
           'DataWarhead','DataPropulsion','DataFuel','DataComm','DataAircraftFacility','DataDockingFacility','DataContainer')
COMPONENTS = {'AircraftFacilities':'DataAircraftFacility','DockingFacilities':'DataDockingFacility',
              'Comms':'DataComm','Fuel':'DataFuel','Loadouts':'DataLoadout','Magazines':'DataMagazine',
              'Mounts':'DataMount','Propulsion':'DataPropulsion','Sensors':'DataSensor',
              'Directors':'DataSensor','Warheads':'DataWarhead','Weapons':'DataWeaponRecord',
              'MagazineWeapons':'DataWeaponRecord','SensorGroups':'DataSensor'}


def quoted(name):
    return '"'+name.replace('"','""')+'"'


def encoded(value):
    if isinstance(value, bytes):
        return {'encoding':'base64','value':base64.b64encode(value).decode('ascii')}
    return value


def compact(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',',':'))


def compile_source(source, output):
    source, output = Path(source).resolve(strict=True), Path(output).resolve()
    if output.exists() or source == output:
        raise ValueError('Informe um novo destino, distinto da fonte.')
    source_hash = digest(source)
    with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as original:
        original.execute('PRAGMA query_only=ON')
        tables = [r[0] for r in original.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        columns = {t:[r[1] for r in original.execute('PRAGMA table_info('+quoted(t)+')')] for t in tables}
        rules = {}

        def add(table, field, target, target_field='ID', basis='structural_pattern'):
            if target not in columns or field not in columns[table] or target_field not in columns[target]:
                return
            if basis != 'declared_fk' and any(k[:2] == (table,field) and v=='declared_fk' for k,v in rules.items()):
                return
            rules.setdefault((table,field,target,target_field),basis)

        for table in tables:
            fks = original.execute('PRAGMA foreign_key_list('+quoted(table)+')').fetchall()
            for fk in fks:
                if sum(r[0]==fk[0] for r in fks) != 1:
                    raise ValueError('FK composta requer tratamento explícito: '+table)
                add(table,fk[3],fk[2],fk[4],basis='declared_fk')
        for table in tables:
            root = next((m for m in sorted(MASTERS,key=len,reverse=True) if table.startswith(m)),None)
            if not root:
                continue
            suffix = table[len(root):]
            if suffix:
                add(table,'ID',root)
                if suffix in COMPONENTS:
                    target = 'DataWeapon' if table=='DataWeaponWeapons' else COMPONENTS[suffix]
                    add(table,'ComponentID',target)
            if table=='DataWeaponRecord':
                add(table,'ComponentID','DataWeapon')
            if table=='DataSensor':
                add(table,'MasqueradeAs','DataSensor')
            if table==root:
                for field in ('Category','Type','Generation','CSGen'):
                    add(table,field,'Enum'+root[4:]+field,basis='named_domain')
            for field,enum in {'OperatorCountry':'EnumOperatorCountry','OperatorService':'EnumOperatorService',
                               'Ergonomics':'EnumErgonomics','ExplosivesType':'EnumWarheadExplosivesType',
                               'ProjectileCaliber':'EnumWarheadCaliber','Frequency':'EnumSensorFrequency',
                               'Cargo_Type':'EnumCargoType','Self_Cargo_Type':'EnumCargoType',
                               'Carry_Cargo_Type':'EnumCargoType','DefaultMissionProfile':'EnumLoadoutMissionProfile'}.items():
                add(table,field,enum,basis='named_domain')
            if suffix=='Codes':
                add(table,'CodeID','Enum'+root[4:]+'Code',basis='named_domain')
            if suffix=='Capabilities':
                add(table,'CodeID','Enum'+root[4:]+'Capability',basis='named_domain')
            if suffix=='Signatures':
                add(table,'Type','EnumSignatureType',basis='named_domain')
            for field in columns[table]:
                if field.startswith('Armor') or field.endswith('Armor'):
                    add(table,field,'EnumArmorType',basis='named_domain')
            specifics = {
                'DataAircraft':{'CockpitGen':'EnumAircraftCockpitGen','Visibility':'EnumAircraftCockpitVisibility',
                                'AutonomousControlLevel':'EnumAircraftAutonomousControlLevel','PhysicalSizeCode':'EnumAircraftPhysicalSize','RunwayLengthCode':'EnumRunwayLength'},
                'DataShip':{'PhysicalSizeCode':'EnumShipPhysicalSize'},
                'DataSubmarine':{'PhysicalSizeCode':'EnumSubmarinePhysicalSize'},
                'DataAircraftFacility':{'PhysicalSize':'EnumAircraftPhysicalSize','RunwayLength':'EnumRunwayLength'},
                'DataDockingFacility':{'PhysicalSize':'EnumDockingFacilityPhysicalSize'},
                'DataLoadout':{'LoadoutRole':'EnumLoadoutRole','TimeofDay':'EnumLoadoutTimeOfDay','QuickTurnaround_TimeofDay':'EnumLoadoutTimeOfDay','Weather':'EnumLoadoutWeather','WinchesterShotgun':'EnumLoadoutWinchesterShotgun','MissionProfile':'EnumLoadoutMissionProfile'},
                'DataSatelliteOrbits':{'Plane':'EnumSatelliteOrbitPlane'},
                'DataSensor':{'Role':'EnumSensorRole'},
                'DataWeaponTargets':{'CodeID':'EnumWeaponTarget'},
                'DataWeaponWRA':{'CodeID':'EnumWeaponWRA','WeaponQty':'EnumWeaponWRAWeaponQty','ShooterQty':'EnumWeaponWRAShooterQty','SelfDefenceRange':'EnumWeaponWRASelfDefenceRange'}
            }
            for field,enum in specifics.get(table,{}).items():
                add(table,field,enum,basis='named_domain')
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('xb'):
            pass
        try:
            with closing(sqlite3.connect(output)) as db, db:
                db.executescript('''
                CREATE TABLE source(file_name TEXT,sha256 TEXT,compiled_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE tables(name TEXT PRIMARY KEY,columns_json TEXT,row_count INTEGER);
                CREATE TABLE records(table_name TEXT,source_rowid INTEGER,source_id_json TEXT,payload_json TEXT,
                  PRIMARY KEY(table_name,source_rowid));
                CREATE INDEX record_id ON records(table_name,source_id_json);
                CREATE TABLE relations(id INTEGER PRIMARY KEY,from_table TEXT,from_column TEXT,to_table TEXT,to_column TEXT,basis TEXT);
                CREATE TABLE links(relation_id INTEGER,from_rowid INTEGER,target_key_json TEXT,target_rowid INTEGER,status TEXT,
                  PRIMARY KEY(relation_id,from_rowid));
                CREATE INDEX incoming_link ON links(relation_id,target_rowid);
                ''')
                db.execute('INSERT INTO source(file_name,sha256) VALUES(?,?)',(source.name,source_hash))
                table_counts = {}
                for table in tables:
                    cursor = original.execute('SELECT rowid,* FROM '+quoted(table))
                    count = 0
                    while batch := cursor.fetchmany(2000):
                        values=[]
                        for row in batch:
                            payload=dict(zip(columns[table],map(encoded,row[1:])))
                            values.append((table,row[0],compact(payload.get('ID')),compact(payload)))
                        db.executemany('INSERT INTO records VALUES(?,?,?,?)',values)
                        count += len(batch)
                    table_counts[table]=count
                    db.execute('INSERT INTO tables VALUES(?,?,?)',(table,compact(columns[table]),count))
                by_table=defaultdict(list)
                lookups={}
                for number,(key,basis) in enumerate(sorted(rules.items()),1):
                    db.execute('INSERT INTO relations VALUES(?,?,?,?,?,?)',(number,*key,basis))
                    table,field,target,target_field=key
                    lookup_key=(target,target_field)
                    if lookup_key not in lookups:
                        lookup=defaultdict(list)
                        for rid,payload in db.execute('SELECT source_rowid,payload_json FROM records WHERE table_name=?',(target,)):
                            lookup[compact(json.loads(payload).get(target_field))].append(rid)
                        lookups[lookup_key]=lookup
                    by_table[table].append((number,field,lookup_key))
                stats=Counter()
                for table,table_rules in by_table.items():
                    batch=[]
                    for rid,raw in db.execute('SELECT source_rowid,payload_json FROM records WHERE table_name=?',(table,)):
                        payload=json.loads(raw)
                        for number,field,key in table_rules:
                            value=payload.get(field)
                            matches=lookups[key].get(compact(value),[]) if value is not None else []
                            status='null' if value is None else 'matched' if len(matches)==1 else 'missing' if not matches else 'ambiguous'
                            batch.append((number,rid,compact(value),matches[0] if len(matches)==1 else None,status))
                            stats[status]+=1
                        if len(batch)>=2000:
                            db.executemany('INSERT INTO links VALUES(?,?,?,?,?)',batch)
                            batch=[]
                    db.executemany('INSERT INTO links VALUES(?,?,?,?,?)',batch)
                if digest(source)!=source_hash:
                    raise RuntimeError('A fonte mudou durante a compilação.')
                result={'source_sha256':source_hash,'tables':len(tables),'records':sum(table_counts.values()),
                        'table_counts':table_counts,'relations':len(rules),
                        'declared_rules':sum(v=='declared_fk' for v in rules.values()),'links':dict(stats),
                        'status':'source_compilation_not_operational_approval'}
            with output.with_suffix('.json').open('x',encoding='utf-8') as stream:
                json.dump(result,stream,ensure_ascii=False,indent=2)
        except Exception:
            output.unlink(missing_ok=True)
            raise
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    result=compile_source(args.source,args.output)
    print(json.dumps({k:v for k,v in result.items() if k!='table_counts'},ensure_ascii=False))
