"""Audit all stored loadout masses and aircraft associations without approving them."""
import argparse
from collections import Counter,defaultdict
from contextlib import closing
import json
from pathlib import Path
from armament_payload import assess_payload,number,VERSION
from resource_store import readonly
from tools.stage_db3k import digest


def audit_payload(compiled, output):
    compiled,output=Path(compiled).resolve(strict=True),Path(output).resolve()
    before=digest(compiled)
    with closing(readonly(compiled)) as db:
        tables=('DataLoadout','DataLoadoutWeapons','DataWeaponRecord','DataWeapon','DataAircraft','DataAircraftLoadouts')
        nodes={}
        for row in db.execute('SELECT * FROM records WHERE table_name IN ('+','.join('?' for _ in tables)+')',tables):
            key=f"{row['table_name']}@{row['source_rowid']}"
            nodes[key]={'key':key,'table':row['table_name'],'rowid':row['source_rowid'],'id':json.loads(row['source_id_json']),'fields':json.loads(row['payload_json'])}
        outgoing=defaultdict(list);owned=defaultdict(list)
        for row in db.execute('''SELECT r.from_table,r.from_column,r.to_table,l.from_rowid,l.target_rowid,l.status
              FROM relations r JOIN links l ON l.relation_id=r.id
              WHERE r.from_table IN ('DataLoadoutWeapons','DataWeaponRecord','DataAircraftLoadouts')
              AND r.from_column IN ('ID','ComponentID')'''):
            source=f"{row['from_table']}@{row['from_rowid']}"
            target=f"{row['to_table']}@{row['target_rowid']}" if row['status']=='matched' else None
            link={'source':source,'target':target,'target_table':row['to_table'],'field':row['from_column']}
            outgoing[source].append(link)
            if link['field']=='ID' and target:owned[target].append(source)
        loadouts={};issues=Counter();entries=0
        for key,root in nodes.items():
            if root['table']!='DataLoadout':continue
            subset={key};pending=list(owned[key])
            while pending:
                current=pending.pop()
                if current in subset:continue
                subset.add(current)
                pending.extend(l['target'] for l in outgoing[current] if l['field']=='ComponentID' and l['target'])
            links=[l for source in subset for l in outgoing[source]]
            group=assess_payload([nodes[k] for k in sorted(subset)],links,key)['groups'][0]
            for item in group['items']:issues.update(item['issues'])
            entries+=len(group['items'])
            loadouts[key]={'id':root['id'],'name':root['fields'].get('Name'),'items':len(group['items']),
                           'complete':group['complete_nominal_mass'],'nominal_default_mass':group['nominal_default_mass'],
                           'known_default_subtotal':group['known_default_subtotal']}
        comparisons=Counter()
        for key,node in nodes.items():
            if node['table']!='DataAircraftLoadouts':continue
            targets={l['field']:nodes.get(l['target']) for l in outgoing[key]}
            aircraft,loadout=targets.get('ID'),targets.get('ComponentID')
            if not aircraft or not loadout:comparisons['missing_relation']+=1;continue
            limit=aircraft['fields'].get('WeightPayload');summary=loadouts[loadout['key']]
            if not summary['items']:comparisons['no_armament_rows']+=1
            elif not number(limit) or limit<=0:comparisons['payload_unresolved']+=1
            elif summary['nominal_default_mass'] is None:comparisons['mass_incomplete']+=1
            else:comparisons['reference_exceeds' if summary['nominal_default_mass']>limit else 'reference_within']+=1
        records=[n for n in nodes.values() if n['table']=='DataWeaponRecord']
        anomalies=[{'weapon_record_id':n['id'],'fields':n['fields']} for n in records
                   if (number(n['fields'].get('DefaultLoad')) and number(n['fields'].get('MaxLoad')) and n['fields']['DefaultLoad']>n['fields']['MaxLoad']) or n['fields'].get('Multiple')==0]
        report={'version':VERSION,'source':dict(db.execute('SELECT * FROM source').fetchone()),'compiled_sha256':before,
                'loadouts':len(loadouts),'loadout_weapon_rows_examined':entries,'line_issues':dict(issues),
                'aircraft_associations':dict(comparisons),'weapon_record_anomalies':anomalies,
                'calculation_ready':False,'configurations':loadouts}
        expected=sum(n['table']=='DataLoadoutWeapons' for n in nodes.values())
        if entries!=expected or digest(compiled)!=before:raise ValueError('Incomplete coverage or source changed')
        with output.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False)
        return {k:v for k,v in report.items() if k!='configurations'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('compiled');parser.add_argument('output')
    args=parser.parse_args()
    print(json.dumps(audit_payload(args.compiled,args.output),ensure_ascii=False,indent=2))
