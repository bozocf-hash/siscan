"""Read-only navigation over compiled source records and measured associations."""
from contextlib import closing
from collections import Counter, defaultdict
import json
from pathlib import Path
import sqlite3
from tools.compile_db3k import MASTERS
from technical_units import describe_fields, annotate_bundle, VERSION as UNITS_VERSION

CATEGORIES = ('DataAircraft','DataShip','DataSubmarine','DataGroundUnit','DataFacility','DataSatellite')


def connection(path):
    db=sqlite3.connect(Path(path).resolve(strict=True).as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    return db


def browse(path, table, term='', page=1):
    if table not in MASTERS or len(term)>120 or not 1<=page<=1000000:
        raise ValueError('Categoria, pesquisa ou página inválida.')
    with closing(connection(path)) as db:
        where="WHERE table_name=? AND (?='' OR source_id_json=? OR (?=0 AND instr(lower(json_extract(payload_json,'$.Name')),lower(?))>0))"
        args=(table,term,term,int(term.isdecimal()),term)
        total=db.execute('SELECT count(*) FROM records '+where,args).fetchone()[0]
        pages=max(1,(total+49)//50)
        page=min(page,pages)
        items=[]
        fuel_types={}
        if table=='DataFuel':
            for row in db.execute("SELECT source_id_json,payload_json FROM records WHERE table_name='EnumFuelType'"):
                fuel_types[json.loads(row['source_id_json'])]=json.loads(row['payload_json']).get('Description')
        for row in db.execute('SELECT source_id_json,payload_json FROM records '+where+' ORDER BY CAST(source_id_json AS INTEGER),source_rowid LIMIT 50 OFFSET ?',(*args,(page-1)*50)):
            item=json.loads(row['payload_json'])
            items.append({'id':json.loads(row['source_id_json']),'name':item.get('Name') or fuel_types.get(item.get('Type')) or f"Registro {row['source_id_json']}",
                          'year':item.get('YearCommissioned'),'hypothetical':item.get('Hypothetical')})
        counts={r['name']:r['row_count'] for r in db.execute('SELECT name,row_count FROM tables') if r['name'] in CATEGORIES}
        component_counts={r['name']:r['row_count'] for r in db.execute('SELECT name,row_count FROM tables') if r['name'] in MASTERS and r['name'] not in CATEGORIES}
        return {'items':items,'total':total,'page':page,'pages':pages,'categories':counts,'component_categories':component_counts,'table':table}


def technical_bundle(path, table, identifier):
    """Traverse owned records and component/domain links; retain cycles as references."""
    if table not in MASTERS or not identifier.isascii() or not identifier.isdecimal() or len(identifier)>12:
        raise ValueError('Identificação de fonte inválida.')
    with closing(connection(path)) as db:
        root=db.execute('SELECT source_rowid FROM records WHERE table_name=? AND source_id_json=?',
                        (table,str(int(identifier)))).fetchone()
        if root is None:
            return None
        source=dict(db.execute('SELECT * FROM source').fetchone())
        rules=[dict(r) for r in db.execute('SELECT * FROM relations ORDER BY id')]
        forward,owned=defaultdict(list),defaultdict(list)
        for rule in rules:
            forward[rule['from_table']].append(rule)
            if rule['from_column']=='ID':
                owned[rule['to_table']].append(rule)
        pending=defaultdict(set)
        pending[table].add(root[0])
        nodes,links={},{}

        def key(name,rid):
            return f'{name}@{rid}'

        def enqueue(name,rid):
            if key(name,rid) not in nodes:
                pending[name].add(rid)

        def include(rule,link):
            target=key(rule['to_table'],link['target_rowid']) if link['status']=='matched' else None
            links[(rule['id'],link['from_rowid'])]={
                'relation_id':rule['id'],'source':key(rule['from_table'],link['from_rowid']),
                'target':target,'field':rule['from_column'],'target_table':rule['to_table'],
                'target_field':rule['to_column'],'raw_key':json.loads(link['target_key_json']),
                'basis':rule['basis'],'status':link['status']}
            enqueue(rule['from_table'],link['from_rowid'])
            if target is not None:
                enqueue(rule['to_table'],link['target_rowid'])

        while pending:
            name=next(iter(pending))
            ids=sorted(pending[name])[:400]
            pending[name].difference_update(ids)
            if not pending[name]:
                del pending[name]
            ids=[rid for rid in ids if key(name,rid) not in nodes]
            if not ids:
                continue
            placeholders=','.join('?' for _ in ids)
            records=db.execute(f'SELECT source_rowid,source_id_json,payload_json FROM records WHERE table_name=? AND source_rowid IN ({placeholders})',(name,*ids)).fetchall()
            if len(records)!=len(ids):
                raise sqlite3.DatabaseError('A compiled target record is missing')
            for row in records:
                node_key=key(name,row['source_rowid'])
                nodes[node_key]={'key':node_key,'table':name,'rowid':row['source_rowid'],
                                 'id':json.loads(row['source_id_json']),'fields':json.loads(row['payload_json'])}
            for rule in forward[name]:
                for link in db.execute(f'SELECT * FROM links WHERE relation_id=? AND from_rowid IN ({placeholders})',(rule['id'],*ids)):
                    include(rule,link)
            for rule in owned[name]:
                for link in db.execute(f'SELECT * FROM links WHERE relation_id=? AND target_rowid IN ({placeholders})',(rule['id'],*ids)):
                    include(rule,link)
        ordered=sorted(nodes.values(),key=lambda n:(n['table'],n['rowid']))
        consumption_profiles=annotate_bundle(ordered,list(links.values()),key(table,root[0]))
        return {'root':key(table,root[0]),'source':source,'complete':True,'nodes':ordered,
                'measurement_contract_version':UNITS_VERSION,'consumption_profiles':consumption_profiles,
                'links':list(links.values()),'node_count':len(nodes),'field_count':sum(len(n['fields']) for n in ordered),
                'table_counts':dict(Counter(n['table'] for n in ordered)),
                'unresolved_link_count':sum(l['status']!='matched' for l in links.values()),
                'reference_annotations':{'throttle_codes':{'0':'FullStop','1':'Loiter','2':'Cruise','3':'Full','4':'Flank','5':'None'},
                                         'source_url':'https://commandlua.github.io/assets/DataTypes.html',
                                         'qualification':'API code reference; does not validate SQL units or consumption conversion'},
                'scope':'complete_reachable_source_graph_not_operational_approval'}


def detail(path, table, identifier):
    if table not in MASTERS or not identifier.isascii() or not identifier.isdecimal() or len(identifier)>12:
        raise ValueError('Identificação de fonte inválida.')
    with closing(connection(path)) as db:
        row=db.execute('SELECT source_rowid,payload_json FROM records WHERE table_name=? AND source_id_json=?',
                       (table,str(int(identifier)))).fetchone()
        if row is None:
            return None
        source=dict(db.execute('SELECT * FROM source').fetchone())
        fields=json.loads(row['payload_json'])
        domains={}
        for link in db.execute('''SELECT r.from_column,r.basis,l.status,t.payload_json
          FROM relations r JOIN links l ON l.relation_id=r.id
          LEFT JOIN records t ON t.table_name=r.to_table AND t.source_rowid=l.target_rowid
          WHERE r.from_table=? AND l.from_rowid=? AND r.basis='named_domain' ''',(table,row['source_rowid'])):
            target=json.loads(link['payload_json']) if link['payload_json'] else {}
            domains[link['from_column']]={'description':target.get('Description'),'status':link['status'],'basis':link['basis']}
        group_rows=db.execute('''SELECT a.table_name,a.source_rowid,a.payload_json,p.basis AS parent_basis,
          c.to_table,c.basis AS component_basis,e.status AS component_status,t.source_id_json,t.payload_json AS target_payload
          FROM relations p JOIN links l ON l.relation_id=p.id
          JOIN records a ON a.table_name=p.from_table AND a.source_rowid=l.from_rowid
          LEFT JOIN relations c ON c.from_table=a.table_name AND c.from_column IN ('ComponentID','CodeID','Type')
          LEFT JOIN links e ON e.relation_id=c.id AND e.from_rowid=a.source_rowid
          LEFT JOIN records t ON t.table_name=c.to_table AND t.source_rowid=e.target_rowid
          WHERE p.to_table=? AND p.from_column='ID' AND l.target_rowid=?
          ORDER BY a.table_name,a.source_rowid''',(table,row['source_rowid'])).fetchall()
        groups={}
        weapon_names={}
        for item in group_rows:
            target=json.loads(item['target_payload']) if item['target_payload'] else {}
            target_name=target.get('Name') or target.get('Description')
            if item['to_table']=='DataWeaponRecord' and target.get('ComponentID') is not None:
                weapon_id=json.dumps(target['ComponentID'])
                if weapon_id not in weapon_names:
                    weapon=db.execute("SELECT payload_json FROM records WHERE table_name='DataWeapon' AND source_id_json=?",(weapon_id,)).fetchone()
                    weapon_names[weapon_id]=json.loads(weapon[0]).get('Name') if weapon else None
                target_name=weapon_names[weapon_id] or target_name
            groups.setdefault(item['table_name'],[]).append({
                'parameters':json.loads(item['payload_json']),'parent_basis':item['parent_basis'],
                'target_table':item['to_table'],'target_id':json.loads(item['source_id_json']) if item['source_id_json'] else None,
                'target_name':target_name,
                'component_basis':item['component_basis'],'status':item['component_status']})
        direct=[]
        for item in db.execute('''SELECT r.from_column,r.to_table,r.basis,l.status,t.source_id_json,t.payload_json
           FROM relations r JOIN links l ON l.relation_id=r.id
           LEFT JOIN records t ON t.table_name=r.to_table AND t.source_rowid=l.target_rowid
           WHERE r.from_table=? AND l.from_rowid=? AND r.from_column='ComponentID' ''',(table,row['source_rowid'])):
            target=json.loads(item['payload_json']) if item['payload_json'] else {}
            direct.append({'field':item['from_column'],'table':item['to_table'],'basis':item['basis'],'status':item['status'],
                           'id':json.loads(item['source_id_json']) if item['source_id_json'] else None,'name':target.get('Name')})
        display_name=fields.get('Name') or next((x['name'] for x in direct if x['name']),f'{table} #{identifier}')
        for name,items in groups.items():
            for item in items:
                item['measurements']=describe_fields(name,item['parameters'],propulsion_type=fields.get('Type') if table=='DataPropulsion' else None)
        return {'table':table,'id':int(identifier),'display_name':display_name,'fields':fields,'domains':domains,'groups':groups,
                'measurements':describe_fields(table,fields,domains),'measurement_contract_version':UNITS_VERSION,
                'direct_links':direct,'truncated':False,'source':source,
                'validation_status':'source_evidence_not_approved_for_calculation'}
