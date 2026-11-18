"""Compara evidência documental de unidades com a fonte 498, sem promoção ou conversão do SQL."""
import argparse
from collections import Counter,defaultdict
from contextlib import closing
import csv
import json
from pathlib import Path
import shutil

from source_catalog import connection
from tools.stage_db3k import digest
from fuel_unit_proof import VERSION,SOURCE_SHA256,IMAGE_SHA256,IMAGE_URL,compare_point,fuel_kind,mass_to_kg

COMPILED_SHA256='de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9'
API_CODES={1001,2001,3001,3002,3003,4001,4002,5001,5002,5003}


def inspect_fuel_proof(compiled,image,output):
    compiled,image=Path(compiled).resolve(strict=True),Path(image).resolve(strict=True)
    if digest(compiled)!=COMPILED_SHA256 or digest(image)!=IMAGE_SHA256:raise ValueError('Compilação ou imagem difere da evidência fixada; não emitir comprovação.')
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    with closing(connection(compiled)) as db:
        source=dict(db.execute('SELECT * FROM source').fetchone())
        if source['sha256']!=SOURCE_SHA256:raise ValueError('Fonte diferente de DB3K_498.')
        def records(table):
            for r in db.execute('SELECT source_rowid,payload_json FROM records WHERE table_name=? ORDER BY source_rowid',(table,)):
                yield r['source_rowid'],json.loads(r['payload_json'])
        fuel_names={v['ID']:v['Description'] for _,v in records('EnumFuelType')}
        propulsion_names={v['ID']:v['Description'] for _,v in records('EnumPropulsionType')}
        engines={v['ID']:v for _,v in records('DataPropulsion')};fuel_counts=Counter();point_counts=Counter();proofs=[];zero_counts=Counter();bands=defaultdict(set)
        with (output/'fuel_capacity_matrix.csv').open('x',encoding='utf-8-sig',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(['fuel_id','fuel_type','description','capacity_literal','quantity_kind','candidate_unit','confirmed_sql_unit','current_quantity','status'])
            for rid,fuel in records('DataFuel'):
                code=fuel['Type'];kind=fuel_kind(code);fuel_counts[code]+=1
                writer.writerow([fuel['ID'],code,fuel_names.get(code,''),fuel['Capacity'],kind['quantity_kind'],kind['candidate_unit'] or '','','','sql_unit_and_current_quantity_pending'])
        with (output/'performance_conditions.csv').open('x',encoding='utf-8-sig',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(['rowid','propulsion_id','propulsion_type','altitude_band','throttle','altitude_min_raw','altitude_max_raw','speed_raw','consumption_raw','verified_units','conditions'])
            for rid,point in records('DataPropulsionPerformance'):
                engine=engines.get(point['ID'],{});code=engine.get('Type');point_counts[code]+=1
                proof=compare_point(engine,point,source_sha256=source['sha256'],image_sha256=IMAGE_SHA256)
                if proof['sample_applicable']:proofs.append(dict(source_table='DataPropulsionPerformance',rowid=rid,values=point,**proof))
                verified={k:m['unit'] for k,m in proof['measurements'].items() if m['unit']}
                conditions=['current_state_not_provided','configuration_not_fixed','fuel_to_propulsor_mapping_not_demonstrated']
                if not proof['all_fields_match']:conditions.append('whole_point_measurement_proof_incomplete')
                if point['Consumption']==0:conditions.append('zero_rate_requires_domain_policy');zero_counts[code]+=1
                if point['AltitudeMin']>point['AltitudeMax']:conditions.append('inverted_band_requires_semantics')
                if code in (2001,2002,2003,2004,2005):bands[point['ID']].add((point['AltitudeBand'],point['AltitudeMin'],point['AltitudeMax']))
                writer.writerow([rid,point['ID'],code,point['AltitudeBand'],point['Throttle'],point['AltitudeMin'],point['AltitudeMax'],point['Speed'],point['Consumption'],json.dumps(verified,sort_keys=True),';'.join(conditions)])
        boundaries=[]
        for engine_id,ranges in bands.items():
            ordered=sorted(ranges,key=lambda v:(v[1],v[2],v[0]))
            for a,b in zip(ordered,ordered[1:]):
                if a[0]!=b[0] and a[2]==b[1]:boundaries.append(dict(propulsion_id=engine_id,first_band=a[0],second_band=b[0],raw_boundary=a[2]))
        types=[dict(code=k,description=fuel_names[k],record_count=fuel_counts[k],code_in_api_reference=k in API_CODES,**fuel_kind(k)) for k in sorted(fuel_names)]
        result=dict(schema_version=VERSION,source_sha256=SOURCE_SHA256,compiled_sha256=COMPILED_SHA256,image_sha256=IMAGE_SHA256,image_url=IMAGE_URL,
            producer_sha256=digest(Path(__file__)),proof_rules_sha256=digest(Path(__file__).parent.parent/'fuel_unit_proof.py'),
            fuel_records=sum(fuel_counts.values()),performance_rows=sum(point_counts.values()),fuel_types=types,
            propulsion_types=[dict(code=k,description=propulsion_names.get(k),point_count=n,zero_consumption_rows=zero_counts[k]) for k,n in sorted(point_counts.items())],
            documentary_samples=proofs,complete_point_matches=sum(p['all_fields_match'] for p in proofs),
            verified_field_matches=sum(bool(m['unit']) for p in proofs for m in p['measurements'].values()),
            touching_aerial_band_boundaries=boundaries,
            mass_conversion_examples={'4.7_t_in_kg':str(mass_to_kg('4.7','t')),'10860_lb_in_kg':str(mass_to_kg('10860','lb'))},
            calculation_ready=False,qualification='Prova documental delimitada; não libera configuração, estoque atual, taxa de outro propulsor ou extrapolação.')
        # Reports keep comparisons even when a manufacturer figure has a different configuration.
        cases=[]
        for table,identifier,reference,url,scope in [
            ('DataAircraft',8,{'value':'10860','unit':'lb'},'https://www.globalsecurity.org/military/library/policy/navy/ntsp/f-18-a_2001.pdf','US Navy NTSP histórico: combustível interno F/A-18A/C; não comprova a versão SQL inteira'),
            ('DataAircraft',35,{'value':'4.7','unit':'t'},'https://www.dassault-aviation.com/en/defense/rafale/specifications-and-performance-data/','Fabricante apresenta família Rafale; variante/época não idênticas ao M de 2009'),
            ('DataAircraft',6,{'value':'35550','unit':'lb'},'https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/','Total USAF inclui CFT e três tanques externos; não comparar diretamente com combustível interno SQL')]:
            parent_rule=db.execute('SELECT id FROM relations WHERE from_table=? AND from_column=?',(table+'Fuel','ID')).fetchone()[0]
            component_rule=db.execute('SELECT id FROM relations WHERE from_table=? AND from_column=?',(table+'Fuel','ComponentID')).fetchone()[0]
            platform=db.execute('SELECT source_rowid,payload_json FROM records WHERE table_name=? AND source_id_json=?',(table,str(identifier))).fetchone()
            tanks=[]
            for row in db.execute('''SELECT t.source_rowid,t.payload_json FROM links p JOIN links c ON c.from_rowid=p.from_rowid AND c.relation_id=?
                JOIN records t ON t.table_name='DataFuel' AND t.source_rowid=c.target_rowid WHERE p.relation_id=? AND p.target_rowid=?''',(component_rule,parent_rule,platform['source_rowid'])):
                tanks.append(dict(rowid=row['source_rowid'],values=json.loads(row['payload_json'])))
            cases.append(dict(table=table,id=identifier,name=json.loads(platform['payload_json'])['Name'],direct_tanks=tanks,reference=reference,reference_mass_kg=str(mass_to_kg(reference['value'],reference['unit'])),evidence=url,scope=scope,
                              evidence_access='indexed_excerpt_pdf_fetch_403' if identifier==8 else 'primary_page_read',
                              sql_capacity_unit_confirmed=False,automatic_equality_or_tolerance_applied=False))
        result['capacity_reference_cases']=cases
    if digest(compiled)!=COMPILED_SHA256 or digest(image)!=IMAGE_SHA256:raise RuntimeError('Evidência mudou durante a leitura.')
    shutil.copy2(image,output/'official_propulsion_chart.jpg')
    result['artifacts']={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file()}
    with (output/'proof_report.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('compiled','image','output'):parser.add_argument(name,type=Path)
    args=parser.parse_args();r=inspect_fuel_proof(args.compiled,args.image,args.output)
    print(json.dumps({k:r[k] for k in ('fuel_records','performance_rows','complete_point_matches','verified_field_matches','calculation_ready')},ensure_ascii=False))
