"""First engine boundary: controlled inputs and explicit artifact compatibility."""
import hashlib
import json
import math
from pathlib import Path
from contextlib import closing
import sqlite3
import resource_store
from resource_store import readonly
from technical_units import VERSION as UNITS_VERSION
from tools.stage_db3k import digest

SCHEMA_VERSION='siscan-engine-input-01'
DATASET_ID='synthetic-fuel-01'
DATASET_SHA256='ffd1a7740e037a6cdec662660150adada04d0e0f4a0941128f49a0b85aa4abe7'
FIELDS={'fuel_capacity':('kg',True),'fuel_initial':('kg',False),
        'consumption_rate':('kg/min',False),'duration':('min',True)}


def input_hash(value):
    text=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def trusted_manifest():
    code=Path(__file__).read_text(encoding='utf-8').replace('\r\n','\n')
    return {'schema_version':SCHEMA_VERSION,'rules_version':'synthetic-boundary-01',
            'dataset_id':DATASET_ID,'dataset_sha256':DATASET_SHA256,
            'contract_code_sha256':hashlib.sha256(code.encode('utf-8')).hexdigest(),
            'scope':'synthetic_contract_test'}


def controlled_example():
    path=Path(__file__).parent/'fixtures/engine/synthetic-fuel-01.json'
    return json.loads(path.read_text(encoding='utf-8'))


def validate_input(payload):
    errors=[];manifest=trusted_manifest()
    def error(field,code,message):errors.append({'field':field,'code':code,'message':message})
    if not isinstance(payload,dict):
        error('$','object_required','A entrada deve ser um objeto.')
    else:
        expected={'schema_version':SCHEMA_VERSION,'data_kind':'synthetic_controlled','dataset_id':DATASET_ID,
                  'entity_id':None,'configuration_id':None,'measurements':None}
        for field in payload:
            if field not in expected:error(str(field),'unknown_field','Campo fora do contrato; aprovação não pode ser declarada pelo próprio payload.')
        for field,wanted in expected.items():
            if field not in payload:error(field,'required','Campo obrigatório ausente.');continue
            value=payload[field]
            if field=='measurements':continue
            if not isinstance(value,str) or not value or len(value)>120:
                error(field,'text_invalid','Identificação textual inválida.');continue
            if wanted is not None and value!=wanted:
                code='unsupported_source' if field=='data_kind' else 'version_mismatch' if field=='schema_version' else 'dataset_mismatch'
                error(field,code,'Fonte, versão ou conjunto não permitido neste contrato sintético.')
            if field in ('entity_id','configuration_id') and not value.startswith('SYN-'):
                error(field,'identity_invalid','O caso controlado exige identidade sintética.')
        measurements=payload.get('measurements')
        if not isinstance(measurements,dict):error('measurements','object_required','Medições obrigatórias devem ser um objeto.')
        else:
            for field in measurements:
                if field not in FIELDS:error('measurements.'+str(field),'unknown_field','Medição fora do contrato.')
            valid={}
            for field,(unit,positive) in FIELDS.items():
                path='measurements.'+field;item=measurements.get(field)
                if field not in measurements:error(path,'required','Medição obrigatória ausente.');continue
                if not isinstance(item,dict):error(path,'object_required','Medição deve conter value e unit.');continue
                for key in item:
                    if key not in ('value','unit'):error(path+'.'+str(key),'unknown_field','Parâmetro fora do contrato.')
                for key in ('value','unit'):
                    if key not in item:error(path+'.'+key,'required','Parâmetro obrigatório ausente.')
                if item.get('unit')!=unit:error(path+'.unit','unit_mismatch','Unidade esperada: '+unit+'. Não há conversão implícita.')
                value=item.get('value')
                try:finite=isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
                except OverflowError:finite=False
                if not finite:
                    error(path+'.value','number_invalid','Valor deve ser numérico e finito.');continue
                if value<0 or (positive and value==0):
                    error(path+'.value','domain_invalid','Valor fora do domínio permitido.');continue
                valid[field]=value
            if 'fuel_initial' in valid and 'fuel_capacity' in valid and valid['fuel_initial']>valid['fuel_capacity']:
                error('measurements.fuel_initial.value','capacity_exceeded','Combustível inicial excede a capacidade.')
        try:
            if input_hash(payload)!=manifest['dataset_sha256']:
                error('dataset_id','dataset_mismatch','Conteúdo diferente do conjunto controlado fixado no backend.')
        except (TypeError,ValueError):error('$','json_invalid','Entrada não é JSON canônico finito.')
    return {'accepted':not errors,'accepted_for':'synthetic_contract_test',
            'official_calculation_ready':False,'manifest':manifest,'errors':errors}


def inspect_catalog(original, compiled, resources):
    checks=[];artifacts={}
    def check(identifier,ok,message):checks.append({'id':identifier,'ok':bool(ok),'message':message})
    paths={'source':Path(original),'compilation':Path(compiled),'resources':Path(resources)}
    if not all(path.is_file() for path in paths.values()):
        check('artifacts_available',False,'Uma ou mais bases de origem/compilação/recursos não estão disponíveis.')
    else:
        try:
            for name,path in paths.items():artifacts[name]={'file_name':path.name,'sha256':digest(path)}
            with closing(readonly(compiled)) as db:source=dict(db.execute('SELECT * FROM source').fetchone())
            with closing(readonly(resources)) as db:build=dict(db.execute('SELECT * FROM build WHERE id=1').fetchone())
            check('source_matches_compilation',source['sha256']==artifacts['source']['sha256'],'A compilação identifica o hash da fonte original disponível.')
            check('source_matches_resources',build['source_sha256']==artifacts['source']['sha256'],'A base de recursos identifica a mesma fonte original.')
            check('compilation_matches_resources',build['compiled_sha256']==artifacts['compilation']['sha256'],'O hash da compilação carregada coincide com o registrado na base de recursos.')
            check('resources_complete',build['status']=='complete','A construção da base de recursos está completa.')
            check('units_contract',build['units_version']==UNITS_VERSION,'A versão do contrato de unidades coincide com a base de recursos.')
            check('resource_builder',build['builder_sha256']==digest(Path(resource_store.__file__)),'O construtor/leitor corresponde ao hash registrado na base de recursos.')
            artifacts['resources']['units_version']=build['units_version']
            artifacts['resources']['builder_sha256']=build['builder_sha256']
        except (OSError,sqlite3.Error,KeyError,TypeError,ValueError):
            check('metadata_readable',False,'Não foi possível conferir os metadados das bases.')
    return {'structurally_compatible':bool(checks) and all(c['ok'] for c in checks),
            'official_calculation_ready':False,'checks':checks,'artifacts':artifacts,
            'qualification':'Compatibilidade de arquivos não aprova unidades, taxas, massas ou modelo físico. Os dados Command continuam pendentes.'}


def readiness(original, compiled, resources):
    try:
        example=controlled_example();validation=validate_input(example)
    except (OSError,ValueError):
        example=None;validation={'accepted':False,'accepted_for':'synthetic_contract_test','official_calculation_ready':False,
                                'manifest':trusted_manifest(),'errors':[{'field':'dataset_id','code':'fixture_unavailable','message':'Conjunto sintético indisponível ou ilegível.'}]}
    return {'synthetic_input':example,'validation':validation,'catalog':inspect_catalog(original,compiled,resources),
            'simulation_started':False,'qualification':'Contrato de entrada em preparação. Não houve avanço de tempo, cálculo de consumo, baixa de estoque ou aprovação de dados.'}
