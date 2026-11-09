"""Read-only navigation over compiled source records and measured associations."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tools.compile_db3k import MASTERS

CATEGORIES = ('DataAircraft','DataShip','DataSubmarine','DataGroundUnit','DataFacility','DataSatellite')


def connection(path):
    db=sqlite3.connect(Path(path).resolve(strict=True).as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    return db


def browse(path, table, term='', page=1):
    if table not in CATEGORIES or len(term)>120 or not 1<=page<=1000000:
        raise ValueError('Categoria, pesquisa ou página inválida.')
    with closing(connection(path)) as db:
        where="WHERE table_name=? AND (?='' OR source_id_json=? OR (?=0 AND instr(lower(json_extract(payload_json,'$.Name')),lower(?))>0))"
        args=(table,term,term,int(term.isdecimal()),term)
        total=db.execute('SELECT count(*) FROM records '+where,args).fetchone()[0]
        pages=max(1,(total+49)//50)
        page=min(page,pages)
        items=[]
        for row in db.execute('SELECT source_id_json,payload_json FROM records '+where+' ORDER BY CAST(source_id_json AS INTEGER),source_rowid LIMIT 50 OFFSET ?',(*args,(page-1)*50)):
            item=json.loads(row['payload_json'])
            items.append({'id':json.loads(row['source_id_json']),'name':item.get('Name') or f"Registro {row['source_id_json']}",
                          'year':item.get('YearCommissioned'),'hypothetical':item.get('Hypothetical')})
        counts={r['name']:r['row_count'] for r in db.execute('SELECT name,row_count FROM tables') if r['name'] in CATEGORIES}
        return {'items':items,'total':total,'page':page,'pages':pages,'categories':counts,'table':table}


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
          ORDER BY a.table_name,a.source_rowid LIMIT 1001''',(table,row['source_rowid'])).fetchall()
        groups={}
        weapon_names={}
        for item in group_rows[:1000]:
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
        return {'table':table,'id':int(identifier),'display_name':display_name,'fields':fields,'domains':domains,'groups':groups,
                'direct_links':direct,'truncated':len(group_rows)>1000,'source':source,
                'validation_status':'source_evidence_not_approved_for_calculation'}
