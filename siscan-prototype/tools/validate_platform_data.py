"""Auditoria literal/relacional em lote, sem homologação física ou escrita nas fontes."""
import argparse
from collections import Counter,defaultdict
from contextlib import ExitStack,closing
import csv
import json
import math
from pathlib import Path

from source_catalog import CATEGORIES,connection
from technical_units import describe_fields,VERSION as UNITS_VERSION
from tools.audit_compilation import audit_source
from tools.compile_db3k import MASTERS,compact
from tools.stage_db3k import digest

VERSION='siscan-platform-data-validation-01'
COMPONENTS={'DataSensor','DataMount','DataMagazine','DataLoadout','DataWeaponRecord',
            'DataWeapon','DataWarhead','DataFuel','DataPropulsion'}
PLATFORM_SUFFIXES={'','Sensors','Directors','Mounts','Magazines','Loadouts','Weapons','Fuel','Propulsion','Signatures'}


def diagnose_fields(table,fields):
    """Sinaliza coerência interna; não transforma convenções em regras físicas."""
    issues=[]
    def add(code,field):issues.append(dict(code=code,field=field,value=fields.get(field),severity='review'))
    def numeric(field,integer=False):
        v=fields[field]
        if type(v) not in (int,float) or not math.isfinite(v):add('numeric_value_unresolved',field);return False
        if integer and int(v)!=v:add('fractional_count_requires_review',field)
        if v<0:add('negative_value_requires_semantics',field)
        return True
    def limits(low,high):
        valid={f:numeric(f) for f in (low,high) if f in fields}
        if valid.get(low) and valid.get(high) and fields[low]>fields[high]:add('inverted_limits_requires_semantics',low)
    if table=='DataSensor':
        limits('RangeMin','RangeMax')
        if fields.get('RangeMax')==0:add('zero_range_requires_semantics','RangeMax')
        for f in ('ScanInterval','MaxContactsAir','MaxContactsSurface','MaxContactsSubmarine','MaxContactsIlluminate'):
            if f in fields:numeric(f)
    elif table=='DataWeapon':
        for prefix in ('Air','Surface','Land','Subsurface'):
            limits(prefix+'RangeMin',prefix+'RangeMax')
            f=prefix+'PoK'
            if f in fields and numeric(f) and not 0<=fields[f]<=100:add('source_probability_scale_requires_review',f)
        if 'Weight'in fields and numeric('Weight') and fields['Weight']==0:add('zero_mass_requires_semantics','Weight')
    elif table=='DataWeaponRecord':
        for f in ('DefaultLoad','MaxLoad','Multiple'):
            if f in fields:numeric(f,True)
        if all(type(fields.get(f)) in (int,float) for f in ('DefaultLoad','MaxLoad')) and fields['DefaultLoad']>fields['MaxLoad']:
            add('default_exceeds_max','DefaultLoad')
        if fields.get('Multiple')!=1:add('multiple_requires_semantics','Multiple')
    elif table=='DataFuel':
        if 'Capacity'in fields and numeric('Capacity') and fields['Capacity']==0:add('zero_capacity_requires_semantics','Capacity')
    elif table=='DataPropulsion':
        if 'NumberOfEngines'in fields and numeric('NumberOfEngines',True) and fields['NumberOfEngines']==0:
            add('zero_engine_count_requires_semantics','NumberOfEngines')
    elif table=='DataPropulsionPerformance':
        for f in ('Speed','Consumption'):
            if f in fields and numeric(f) and fields[f]==0:add('zero_'+f.lower()+'_requires_semantics',f)
        # Signed altitude/depth is preserved, not rejected as a negative quantity.
        low,high=fields.get('AltitudeMin'),fields.get('AltitudeMax')
        if type(low)in (int,float) and type(high)in (int,float) and low>high:add('inverted_altitude_band','AltitudeMin')
    if 'Optional'in fields and fields['Optional'] not in (0,1):add('optional_flag_requires_semantics','Optional')
    return issues


def _selected(table):
    root=next((m for m in sorted(MASTERS,key=len,reverse=True) if table.startswith(m)),None)
    return root in COMPONENTS or root in CATEGORIES and table[len(root):] in PLATFORM_SUFFIXES


def _csv_cell(value):
    return "'"+value if isinstance(value,str) and (value.lstrip().startswith(('=','+','-','@')) or value.startswith(('\t','\r','\n'))) else value


def validate_platform_data(source,compiled,output,progress=None):
    """Cria pasta exclusiva; summary.json só existe após concluir e conferir tudo."""
    source,compiled=Path(source).resolve(strict=True),Path(compiled).resolve(strict=True)
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    tell=progress or (lambda message:None)
    tell('Conferindo todos os valores contra a fonte original…')
    literal=audit_source(source,compiled,output/'literal_audit.json')
    tell('Valores conferidos; examinando campos e relações…')
    nodes={};adj=defaultdict(list);installation_nodes=set();evidence={};profiles={}
    issue_counts=Counter();link_counts=Counter();rule_counts=[];category_counts=Counter();category_coverage=defaultdict(Counter)
    with closing(connection(compiled)) as db,ExitStack() as stack:
        tables={r['name']:r['row_count'] for r in db.execute('SELECT name,row_count FROM tables') if _selected(r['name'])}
        writers={name:stack.enter_context((output/name).open('x',encoding='utf-8')) for name in ('components.jsonl','issues.jsonl','installations.jsonl','platforms.jsonl')}
        def write(name,row):writers[name].write(compact(row)+'\n')
        prop_types={compact(json.loads(r['source_id_json'])):json.loads(r['payload_json']).get('Type') for r in db.execute("SELECT source_id_json,payload_json FROM records WHERE table_name='DataPropulsion'")}
        for table in sorted(tables):
            for row in db.execute('SELECT * FROM records WHERE table_name=? ORDER BY source_rowid',(table,)):
                fields=json.loads(row['payload_json']);key=(table,row['source_rowid']);identity=json.loads(row['source_id_json'])
                issues=diagnose_fields(table,fields)
                nodes[key]=dict(id=identity,name=fields.get('Name'),issue_codes=[i['code'] for i in issues])
                for issue in issues:
                    write('issues.jsonl',dict(table=table,rowid=key[1],id=identity,**issue));issue_counts[issue['code']]+=1
                kind=prop_types.get(compact(fields.get('ID'))) if table=='DataPropulsionPerformance' else None
                context=compact([table,fields.get('Type') if table=='DataFuel' else kind])
                if context not in evidence:evidence[context]=describe_fields(table,fields,propulsion_type=kind)
                for field,value in fields.items():
                    profile=profiles.setdefault(table+'.'+field,dict(count=0,null_count=0,zero_count=0,negative_count=0,minimum=None,maximum=None,types=Counter()))
                    profile['count']+=1;profile['types'][type(value).__name__]+=1
                    if value is None:profile['null_count']+=1
                    elif type(value)in (int,float) and math.isfinite(value):
                        profile['zero_count']+=int(value==0);profile['negative_count']+=int(value<0)
                        profile['minimum']=value if profile['minimum'] is None else min(value,profile['minimum'])
                        profile['maximum']=value if profile['maximum'] is None else max(value,profile['maximum'])
                if table in COMPONENTS or table=='DataPropulsionPerformance':
                    write('components.jsonl',dict(table=table,rowid=key[1],id=identity,fields=fields,evidence_key=context,issues=issues,calculation_ready=False))

        lookups={}
        for rule in db.execute('SELECT * FROM relations ORDER BY id'):
            if rule['from_table'] not in tables:continue
            lookup_key=(rule['to_table'],rule['to_column'])
            if lookup_key not in lookups:
                lookup=defaultdict(list)
                for row in db.execute('SELECT source_rowid,payload_json FROM records WHERE table_name=?',(rule['to_table'],)):
                    lookup[compact(json.loads(row['payload_json']).get(rule['to_column']))].append(row['source_rowid'])
                lookups[lookup_key]=lookup
            lookup=lookups[lookup_key];counts=Counter()
            rows=db.execute('''SELECT r.source_rowid,r.payload_json,l.target_key_json,l.target_rowid,l.status
              FROM records r LEFT JOIN links l ON l.relation_id=? AND l.from_rowid=r.source_rowid
              WHERE r.table_name=? ORDER BY r.source_rowid''',(rule['id'],rule['from_table']))
            for row in rows:
                fields=json.loads(row['payload_json']);value=fields.get(rule['from_column']);raw=compact(value)
                matches=lookup.get(raw,[]) if value is not None else []
                status='null' if value is None else 'matched' if len(matches)==1 else 'missing' if not matches else 'ambiguous'
                target=matches[0] if len(matches)==1 else None
                if (raw,target,status)!=(row['target_key_json'],row['target_rowid'],row['status']):
                    raise ValueError(f"Vínculo compilado divergente/ausente: regra {rule['id']}, linha {row['source_rowid']}.")
                counts[status]+=1;link_counts[status]+=1
                start=(rule['from_table'],row['source_rowid']);end=(rule['to_table'],target)
                if status!='matched':
                    code='link_'+status;issue_counts[code]+=1;nodes[start]['issue_codes'].append(code)
                    write('issues.jsonl',dict(table=start[0],rowid=start[1],id=nodes[start]['id'],code=code,field=rule['from_column'],value=value,target_table=rule['to_table'],relation_id=rule['id'],basis=rule['basis'],severity='review'))
                if rule['from_column']=='ID' and status=='matched' and end in nodes:adj[end].append(start)
                if rule['from_column']=='ComponentID' and rule['to_table'] in COMPONENTS:
                    installation_nodes.add(start)
                    if status=='matched':adj[start].append(end)
                    write('installations.jsonl',dict(table=start[0],rowid=start[1],id=nodes[start]['id'],parameters=fields,
                          component_table=rule['to_table'],component_rowid=target,component_id=value,
                          status=status,relation_id=rule['id'],basis=rule['basis']))
                # MasqueradeAs and enum relations are audited but never create installed equipment.
            stored=db.execute('SELECT COUNT(*) FROM links WHERE relation_id=?',(rule['id'],)).fetchone()[0]
            if stored!=sum(counts.values()):raise ValueError('Vínculos excedentes na regra '+str(rule['id']))
            rule_counts.append(dict(rule_id=rule['id'],from_table=rule['from_table'],field=rule['from_column'],to_table=rule['to_table'],basis=rule['basis'],counts=dict(counts)))

        csv_stream=stack.enter_context((output/'platforms.csv').open('x',encoding='utf-8-sig',newline=''))
        csv_writer=csv.DictWriter(csv_stream,fieldnames=['table','id','name','sensor_installation_rows','sensor_references','weapon_references','loadout_alternatives','fuel_references_direct','fuel_references_chain','propulsion_references_direct','performance_rows_direct','review_occurrences','calculation_ready'])
        csv_writer.writeheader();platform_count=0
        def component_ids(keys):
            result=defaultdict(set)
            for k in keys:
                if k[0]in COMPONENTS:result[k[0]].add(nodes[k]['id'])
            return {table:sorted(values,key=compact) for table,values in sorted(result.items())}
        for root,record in nodes.items():
            if root[0]not in CATEGORIES:continue
            children=set(adj[root]);placements=children&installation_nodes
            direct={target for child in placements for target in adj[child] if target[0]in COMPONENTS}
            visited=set();pending=[root]
            while pending:
                key=pending.pop()
                if key in visited:continue
                visited.add(key);pending.extend(adj[key])
            direct_counts=Counter(k[0] for k in placements)
            codes=Counter(code for k in visited for code in nodes[k]['issue_codes'])
            direct_performance={child for parent in direct if parent[0]=='DataPropulsion' for child in adj[parent] if child[0]=='DataPropulsionPerformance'}
            reachable=component_ids(visited);direct_ids=component_ids(direct);chain=component_ids((visited-{root})-direct)
            payload=dict(table=root[0],rowid=root[1],id=record['id'],name=record['name'],direct_installation_counts=dict(direct_counts),
                         direct_components=direct_ids,reachable_components=reachable,chain_components=chain,
                         direct_performance_rows=len(direct_performance),review_counts=dict(codes),
                         source_presence={t:'direct_rows_present' if any(k[0]==root[0]+suffix for k in placements) else 'no_direct_rows_in_source' for t,suffix in [('DataSensor','Sensors'),('DataFuel','Fuel'),('DataPropulsion','Propulsion')]},
                         current_fuel=None,current_ammunition=None,average_consumption=None,calculation_ready=False,
                         qualification='Referências de catálogo; alternativas e repetição não são estoque atual ou soma física.')
            write('platforms.jsonl',payload)
            csv_writer.writerow({k:_csv_cell(v) for k,v in dict(table=root[0],id=record['id'],name=record['name'],
              sensor_installation_rows=direct_counts.get(root[0]+'Sensors',0),sensor_references=len(reachable.get('DataSensor',[])),
              weapon_references=len(reachable.get('DataWeapon',[])),loadout_alternatives=len(direct_ids.get('DataLoadout',[])),
              fuel_references_direct=len(direct_ids.get('DataFuel',[])),fuel_references_chain=len(chain.get('DataFuel',[])),
              propulsion_references_direct=len(direct_ids.get('DataPropulsion',[])),performance_rows_direct=len(direct_performance),
              review_occurrences=sum(codes.values()),calculation_ready=False).items()})
            category_counts[root[0]]+=1;platform_count+=1
            coverage=category_coverage[root[0]]
            for t in ('DataSensor','DataWeapon','DataFuel','DataPropulsion'):
                if reachable.get(t):coverage['with_reachable_'+t]+=1
                if direct_ids.get(t):coverage['with_direct_'+t]+=1
            if direct_performance:coverage['with_direct_performance']+=1
            if codes:coverage['with_review_occurrences']+=1
            if platform_count%500==0:tell(f'Plataformas examinadas: {platform_count}')
        missing_profiles=[]
        for key,record in nodes.items():
            if key[0]=='DataPropulsion' and not any(child[0]=='DataPropulsionPerformance' for child in adj[key]):
                missing_profiles.append(dict(table=key[0],rowid=key[1],id=record['id'],name=record['name']))

    # Shared evidence is not a promotion; unknown SQL units remain null.
    for name,data in [('field_evidence.json',evidence),('field_profiles.json',profiles),('relation_coverage.json',rule_counts)]:
        with (output/name).open('x',encoding='utf-8') as stream:json.dump(data,stream,ensure_ascii=False,indent=2,allow_nan=False)
    if digest(source)!=literal['source_sha256'] or digest(compiled)!=literal['compiled_sha256']:
        raise RuntimeError('Uma fonte mudou durante a validação; nenhum sumário completo emitido.')
    summary=dict(schema_version=VERSION,status='literal_and_structural_checks_complete_semantics_pending',calculation_ready=False,
                 source_sha256=literal['source_sha256'],compiled_sha256=literal['compiled_sha256'],validator_sha256=digest(Path(__file__)),units_contract=UNITS_VERSION,
                 literal_tables=literal['tables'],literal_records=literal['records'],literal_values=literal['values'],
                 selected_tables=tables,selected_records=len(nodes),recomputed_relations=len(rule_counts),link_status_counts=dict(link_counts),
                 platform_count=platform_count,category_counts=dict(category_counts),category_coverage={k:dict(v) for k,v in category_coverage.items()},
                 record_review_counts=dict(issue_counts),propulsors_without_performance=missing_profiles,
                 current_state='not_part_of_static_catalog',artifacts={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    with (output/'summary.json').open('x',encoding='utf-8') as stream:json.dump(summary,stream,ensure_ascii=False,indent=2,allow_nan=False)
    tell(f'Concluído: {platform_count} plataformas; fontes preservadas.')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','compiled','output'):parser.add_argument(name,type=Path)
    args=parser.parse_args()
    result=validate_platform_data(args.source,args.compiled,args.output,progress=lambda s:print(s,flush=True))
    print(json.dumps({k:result[k] for k in ('status','platform_count','category_counts','link_status_counts','record_review_counts')},ensure_ascii=False))
