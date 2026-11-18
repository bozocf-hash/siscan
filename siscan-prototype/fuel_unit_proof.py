"""Correspondência documental delimitada: não homologa dados ou estado operacional."""
from decimal import Decimal,InvalidOperation
import math

SOURCE_SHA256='1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d'
IMAGE_SHA256='9d6de52800e5ac6d8ac4c9d2ffd22b737c49247d42d156c3fcfa9eed4cdd152a'
IMAGE_URL='https://www.warfaresims.com/WarSimsWP/wp-content/uploads/2014/07/F-22-Engine-Stats.jpg'
STANDARD_URL='https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958917'
VERSION='siscan-fuel-unit-proof-01'
# Transcrição visual da imagem oficial histórica; decimais não são corrigidos.
SAMPLE_ENGINE=dict(ID=734,Name='2x F119-PW-100',Type=2002,NumberOfEngines=2,
                   ThrustPerEngineMilitary=11350,SFCMilitary=0.76,
                   ThrustPerEngineAfterburner=16798,SFCAfterburner=1.9)
SAMPLES={1:dict(AltitudeMin=0,AltitudeMax=3657.6,Speed=650,Consumption=267.47),
         2:dict(AltitudeMin=3657.9,AltitudeMax=7315.2,Speed=750,Consumption=250.54),
         3:dict(AltitudeMin=7315.5,AltitudeMax=10972.8,Speed=850,Consumption=211.32),
         4:dict(AltitudeMin=10973.1,AltitudeMax=12192,Speed=1000,Consumption=201.85)}
UNITS={'AltitudeMin':'m','AltitudeMax':'m','Speed':'kn','Consumption':'kg/min'}


def _number(v):
    try:return type(v)in (int,float) and math.isfinite(v)
    except OverflowError:return False


def compare_point(engine,point,*,source_sha256,image_sha256):
    """Confirma somente campos que coincidem com a amostra e fontes identificadas."""
    applicable=(source_sha256==SOURCE_SHA256 and image_sha256==IMAGE_SHA256
                and all(engine.get(k)==v and type(engine.get(k))is not bool for k,v in SAMPLE_ENGINE.items())
                and point.get('ID')==734 and type(point.get('AltitudeBand'))is int
                and point.get('AltitudeBand')in SAMPLES and point.get('Throttle')==3)
    sample=SAMPLES.get(point.get('AltitudeBand'),{}) if type(point.get('AltitudeBand'))is int else {}
    measurements={}
    for field,unit in UNITS.items():
        raw,expected=point.get(field),sample.get(field)
        matched=applicable and _number(raw) and raw==expected
        measurements[field]=dict(raw_value=raw,document_value=expected,unit=unit if matched else None,
            documented_unit=unit,status='verified_documentary_sample' if matched else 'historical_value_difference' if applicable else 'outside_verified_sample',
            evidence=IMAGE_URL,evidence_sha256=IMAGE_SHA256,calculation_ready=False)
    return dict(sample_applicable=applicable,all_fields_match=applicable and all(m['unit'] for m in measurements.values()),
                measurements=measurements,rate_basis='modeled_propulsion_set' if applicable else None,
                additional_engine_multiplier=1 if applicable else None,calculation_ready=False,
                qualification='Correspondência amostral com documento histórico; uso exige estado, configuração e condições demonstrados. Sem herança para outros propulsores.')


def fuel_kind(code):
    """Classifica grandeza de recurso; não declara unidade SQL com base no nome."""
    if code in (2001,3001,3002,3006):kind='liquid_fuel'
    elif code==3003:kind='combustion_resource_phase_unconfirmed'
    elif code in (4001,4003):kind='electrical_resource'
    elif code==4002:kind='aip_resource'
    elif code==5003:kind='duration'
    elif code in (5001,5002):kind='weapon_propulsion_resource'
    elif code==1001:kind='none'
    else:kind='unknown'
    return dict(quantity_kind=kind,sql_unit=None,calculation_ready=False,
                candidate_unit='kg' if code==2001 else None)


def mass_to_kg(value,unit):
    """Conversão de uma massa explicitamente identificada, nunca inferência do SQL."""
    factors={'kg':Decimal(1),'t':Decimal(1000),'lb':Decimal('0.45359237')}
    if unit not in factors or type(value) not in (int,float,str,Decimal):raise ValueError('Informe massa em kg, t métrica ou lb avoirdupois; volume exige densidade e condições.')
    try:quantity=Decimal(str(value))
    except InvalidOperation:raise ValueError('Massa inválida.') from None
    if not quantity.is_finite() or quantity<0:raise ValueError('Massa deve ser finita e não negativa.')
    return quantity*factors[unit]
