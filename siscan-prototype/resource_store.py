"""Derived SQL resources, preserving source rows and unapproved unit evidence."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from tools.compile_db3k import MASTERS, compact
from tools.stage_db3k import digest
from technical_units import describe_fields, VERSION

SCHEMA='''
CREATE TABLE build(id INTEGER PRIMARY KEY CHECK(id=1), source_sha256 TEXT NOT NULL,
 compiled_sha256 TEXT NOT NULL, units_version TEXT NOT NULL, builder_sha256 TEXT NOT NULL,
 created_at TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('building','complete')));
CREATE TABLE owners(source_table TEXT,source_rowid INTEGER,source_id_json TEXT NOT NULL,name TEXT,
 PRIMARY KEY(source_table,source_rowid));
CREATE INDEX owner_identity ON owners(source_table,source_id_json);
CREATE TABLE components(source_table TEXT CHECK(source_table IN ('DataFuel','DataPropulsion')),
 source_rowid INTEGER,source_id_json TEXT NOT NULL,name TEXT,fuel_type INTEGER,capacity NUMERIC,
 propulsion_type INTEGER,number_of_engines NUMERIC,payload_json TEXT NOT NULL,measurements_json TEXT NOT NULL,
 PRIMARY KEY(source_table,source_rowid));
CREATE VIEW fuel_records AS SELECT * FROM components WHERE source_table='DataFuel';
CREATE VIEW propulsion_records AS SELECT * FROM components WHERE source_table='DataPropulsion';
CREATE TABLE performance(source_rowid INTEGER PRIMARY KEY,source_id_json TEXT NOT NULL,
 component_table TEXT NOT NULL CHECK(component_table='DataPropulsion'),component_rowid INTEGER,
 link_status TEXT NOT NULL,throttle INTEGER,altitude_band INTEGER,speed NUMERIC,
 altitude_min NUMERIC,altitude_max NUMERIC,consumption NUMERIC,
 payload_json TEXT NOT NULL,measurements_json TEXT NOT NULL,
 FOREIGN KEY(component_table,component_rowid) REFERENCES components(source_table,source_rowid));
CREATE INDEX performance_component ON performance(component_table,component_rowid);
CREATE TABLE installations(source_table TEXT,source_rowid INTEGER,source_id_json TEXT NOT NULL,
 owner_table TEXT NOT NULL,owner_rowid INTEGER,owner_status TEXT NOT NULL,
 component_table TEXT NOT NULL,component_rowid INTEGER,component_status TEXT NOT NULL,
 payload_json TEXT NOT NULL,PRIMARY KEY(source_table,source_rowid),
 FOREIGN KEY(owner_table,owner_rowid) REFERENCES owners(source_table,source_rowid),
 FOREIGN KEY(component_table,component_rowid) REFERENCES components(source_table,source_rowid));
CREATE INDEX installation_owner ON installations(owner_table,owner_rowid);
CREATE INDEX installation_component ON installations(component_table,component_rowid);
'''


def readonly(path):
    db=sqlite3.connect(Path(path).resolve(strict=True).as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    return db


def build_store(compiled, output):
    compiled,output=Path(compiled).resolve(strict=True),Path(output).resolve()
    compiled_hash=digest(compiled)
    with closing(readonly(compiled)) as source:
        provenance=dict(source.execute('SELECT * FROM source').fetchone())
        rules=[dict(r) for r in source.execute('SELECT * FROM relations')]
        components_rules=[r for r in rules if r['to_table'] in ('DataFuel','DataPropulsion') and r['from_column']=='ComponentID']
        parents={}
        for rule in components_rules:
            matches=[r for r in rules if r['from_table']==rule['from_table'] and r['from_column']=='ID']
            if len(matches)!=1:raise sqlite3.DatabaseError('Installation owner rule is ambiguous or missing')
            parents[rule['from_table']]=matches[0]
        owner_tables=set(MASTERS[:6])|{'DataWeapon'}|{r['to_table'] for r in parents.values()}
        # Exclusive creation prevents replacement of either a source or a previous build.
        with output.open('xb'):pass
        with closing(sqlite3.connect(output)) as db:
            db.row_factory=sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            db.executescript(SCHEMA)
            with db:
                db.execute('INSERT INTO build VALUES(1,?,?,?,?,?,?)',(provenance['sha256'],compiled_hash,VERSION,digest(Path(__file__)),datetime.now(timezone.utc).isoformat(),'building'))
                for row in source.execute('SELECT * FROM records WHERE table_name IN ('+','.join('?' for _ in owner_tables)+')',tuple(sorted(owner_tables))):
                    fields=json.loads(row['payload_json'])
                    db.execute('INSERT INTO owners VALUES(?,?,?,?)',(row['table_name'],row['source_rowid'],row['source_id_json'],fields.get('Name')))
                propulsors={}
                for row in source.execute("SELECT * FROM records WHERE table_name IN ('DataFuel','DataPropulsion')"):
                    fields=json.loads(row['payload_json']);fuel=row['table_name']=='DataFuel'
                    if not fuel:propulsors[row['source_rowid']]=fields
                    measurements=describe_fields(row['table_name'],fields)
                    db.execute('INSERT INTO components VALUES(?,?,?,?,?,?,?,?,?,?)',(
                        row['table_name'],row['source_rowid'],row['source_id_json'],fields.get('Name'),
                        fields.get('Type') if fuel else None,fields.get('Capacity') if fuel else None,
                        fields.get('Type') if not fuel else None,fields.get('NumberOfEngines') if not fuel else None,
                        row['payload_json'],compact(measurements)))
                perf_rules=[r for r in rules if r['from_table']=='DataPropulsionPerformance' and r['from_column']=='ID' and r['to_table']=='DataPropulsion']
                perf_count=source.execute("SELECT count(*) FROM records WHERE table_name='DataPropulsionPerformance'").fetchone()[0]
                if perf_count and len(perf_rules)!=1:raise sqlite3.DatabaseError('Performance parent rule is ambiguous or missing')
                if perf_count:
                    for row in source.execute('''SELECT a.*,l.target_rowid,l.status FROM records a LEFT JOIN links l
                         ON l.relation_id=? AND l.from_rowid=a.source_rowid WHERE a.table_name='DataPropulsionPerformance' ''',(perf_rules[0]['id'],)):
                        if row['status'] is None:raise sqlite3.DatabaseError('Performance link missing from compilation')
                        fields=json.loads(row['payload_json']);kind=propulsors.get(row['target_rowid'],{}).get('Type')
                        db.execute('INSERT INTO performance VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(
                            row['source_rowid'],row['source_id_json'],'DataPropulsion',row['target_rowid'],row['status'],
                            *(fields.get(f) for f in ('Throttle','AltitudeBand','Speed','AltitudeMin','AltitudeMax','Consumption')),
                            row['payload_json'],compact(describe_fields('DataPropulsionPerformance',fields,propulsion_type=kind))))
                for rule in components_rules:
                    parent=parents[rule['from_table']]
                    for row in source.execute('''SELECT a.*,p.target_rowid AS owner_rowid,p.status AS owner_status,
                         c.target_rowid AS component_rowid,c.status AS component_status FROM records a
                         LEFT JOIN links p ON p.relation_id=? AND p.from_rowid=a.source_rowid
                         LEFT JOIN links c ON c.relation_id=? AND c.from_rowid=a.source_rowid WHERE a.table_name=?''',
                         (parent['id'],rule['id'],rule['from_table'])):
                        if row['owner_status'] is None or row['component_status'] is None:raise sqlite3.DatabaseError('Installation link missing from compilation')
                        db.execute('INSERT INTO installations VALUES(?,?,?,?,?,?,?,?,?,?)',(
                            row['table_name'],row['source_rowid'],row['source_id_json'],parent['to_table'],row['owner_rowid'],row['owner_status'],
                            rule['to_table'],row['component_rowid'],row['component_status'],row['payload_json']))
                if db.execute('PRAGMA foreign_key_check').fetchall():raise sqlite3.DatabaseError('Derived FK check failed')
                verified=0
                for target,table in [('components',None),('performance','DataPropulsionPerformance'),('installations',None)]:
                    for row in db.execute('SELECT * FROM '+target):
                        name=table or row['source_table']
                        rowid=row['source_rowid']
                        values=dict(row)
                        original=source.execute('SELECT payload_json,source_id_json FROM records WHERE table_name=? AND source_rowid=?',(name,rowid)).fetchone()
                        if original is None or values['payload_json']!=original['payload_json'] or values['source_id_json']!=original['source_id_json']:
                            raise sqlite3.DatabaseError('Derived payload differs from compilation')
                        verified+=1
                integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
                if integrity!='ok' or digest(compiled)!=compiled_hash:raise sqlite3.DatabaseError('Integrity or source hash changed during build')
                counts={t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('owners','components','performance','installations')}
                expected=sum(source.execute('SELECT count(*) FROM records WHERE table_name=?',(r['from_table'],)).fetchone()[0] for r in components_rules)
                component_count=source.execute("SELECT count(*) FROM records WHERE table_name IN ('DataFuel','DataPropulsion')").fetchone()[0]
                if counts['installations']!=expected or counts['performance']!=perf_count or counts['components']!=component_count:raise sqlite3.DatabaseError('Incomplete resource coverage')
                db.execute("UPDATE build SET status='complete' WHERE id=1")
                return {**counts,'performance_points':counts['performance'],'payloads_verified':verified,'integrity':integrity,
                        'source_sha256':provenance['sha256'],'compiled_sha256':compiled_hash,'units_version':VERSION}


def resources(path, table, identifier, expected_source):
    if table not in MASTERS or not identifier.isascii() or not identifier.isdecimal() or len(identifier)>12:
        raise ValueError('Identificação de fonte inválida.')
    with closing(readonly(path)) as db:
        build=db.execute('SELECT * FROM build WHERE id=1').fetchone()
        if build is None or build['status']!='complete' or build['source_sha256']!=expected_source or build['units_version']!=VERSION:
            raise sqlite3.DatabaseError('Resource source, contract or build state mismatch')
        owner=db.execute('SELECT * FROM owners WHERE source_table=? AND source_id_json=?',(table,str(int(identifier)))).fetchone()
        installations=[dict(r) for r in db.execute('SELECT * FROM installations WHERE owner_table=? AND owner_rowid=? ORDER BY source_table,source_rowid',(table,owner['source_rowid']))] if owner else []
        component_keys={(r['component_table'],r['component_rowid']) for r in installations if r['component_rowid'] is not None}
        # Component dossiers can also inspect their own persistent resource record.
        if table in ('DataFuel','DataPropulsion'):
            component_keys.update((table,r[0]) for r in db.execute('SELECT source_rowid FROM components WHERE source_table=? AND source_id_json=?',(table,str(int(identifier)))))
        components=[];performance=[]
        for name,rowid in sorted(component_keys):
            component=db.execute('SELECT * FROM components WHERE source_table=? AND source_rowid=?',(name,rowid)).fetchone()
            if component is None:raise sqlite3.DatabaseError('Missing persistent component')
            components.append(dict(component))
            performance.extend(dict(r) for r in db.execute('SELECT * FROM performance WHERE component_table=? AND component_rowid=? ORDER BY source_rowid',(name,rowid)))
        for row in installations+components+performance:
            row['fields']=json.loads(row.pop('payload_json'))
            if 'measurements_json' in row:row['measurements']=json.loads(row.pop('measurements_json'))
        return {'status':'available','build':dict(build),'owner':dict(owner) if owner else None,
                'installations':installations,'components':components,'performance':performance,'calculation_ready':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('compiled');parser.add_argument('output')
    args=parser.parse_args()
    print(json.dumps(build_store(args.compiled,args.output),ensure_ascii=False,indent=2))
