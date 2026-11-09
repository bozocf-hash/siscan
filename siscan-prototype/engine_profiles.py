"""Read-only piecewise synthetic consumption prediction; never writes runtime state."""
import hashlib,json,sqlite3,uuid
from pathlib import Path
import engine_runtime,engine_units
import fuel_limits
from engine_input import input_hash,validate_input,trusted_manifest

DATA_PATH=Path(__file__).resolve().parent/'fixtures/engine/synthetic-profiles-01.json'
DATA_SHA256='1cd0f7ba3ac0b20ae3e3900a2702563d71329ed08d5fc6ffc3da2a3712b0e3d4'


def verify_preview(db,user,payload,expected_manifest_sha256):
    """Recompute the reviewed basis before any future transactional debit."""
    if not isinstance(expected_manifest_sha256,str) or len(expected_manifest_sha256)!=64:raise ValueError('Manifesto de previsão inválido.')
    result=preview(db,user,payload)
    if result['manifest_sha256']!=expected_manifest_sha256:raise engine_runtime.Conflict('Plano, saldo, limite ou contrato mudou. Recalcule a previsão antes de aplicar.')
    return result


def contract():
    try:data=json.loads(DATA_PATH.read_text(encoding='utf-8'))
    except ValueError as exc:raise sqlite3.DatabaseError('Invalid synthetic profile dataset') from exc
    if input_hash(data)!=DATA_SHA256:raise sqlite3.DatabaseError('Synthetic profile dataset mismatch')
    code=hashlib.sha256(Path(__file__).read_text(encoding='utf-8').replace('\r\n','\n').encode()).hexdigest()
    return {'dataset':data,'manifest':{'schema_version':data['schema_version'],'dataset_version':data['dataset_version'],
            'dataset_sha256':DATA_SHA256,'algorithm_sha256':code},'official_calculation_ready':False}


def preview(db,user,payload):
    exercise=engine_units.context(db,user)
    if user['role']!='instructor':raise PermissionError('Previsão restrita ao instrutor atribuído.')
    if not isinstance(payload,dict) or set(payload)!={'run_id','unit_id','expected_revision','segments'}:raise ValueError('Informe execução, unidade, revisão e trechos, sem campos adicionais.')
    for field in ('run_id','unit_id'):
        try:valid=isinstance(payload[field],str) and str(uuid.UUID(payload[field]))==payload[field]
        except ValueError:valid=False
        if not valid:raise ValueError('Identificador inválido.')
    if type(payload['expected_revision']) is not int or payload['expected_revision']<0:raise ValueError('Revisão inválida.')
    segments=payload['segments'];trusted=contract();rates={r['id']:r for r in trusted['dataset']['regimes']}
    if not isinstance(segments,list) or not 1<=len(segments)<=24:raise ValueError('O plano exige de 1 a 24 trechos.')
    duration=0
    for segment in segments:
        if not isinstance(segment,dict) or set(segment)!={'regime_id','minutes'} or not isinstance(segment['regime_id'],str) or segment['regime_id'] not in rates or type(segment['minutes']) is not int or not 1<=segment['minutes']<=1440:raise ValueError('Trecho inválido; selecione regime de teste e minutos inteiros positivos.')
        duration+=segment['minutes']
    if duration>1440:raise ValueError('A duração total máxima do teste é 1440 min.')
    current=engine_runtime.read_runtime(db,user)
    if not current['initialized'] or current['run_id']!=payload['run_id'] or current['revision']!=payload['expected_revision'] or not current['advance_allowed']:raise engine_runtime.Conflict('Execução/revisão incompatível. Atualize o estado antes de prever.')
    state=db.execute('SELECT * FROM engine_resource_states WHERE run_id=? AND unit_id=?',(payload['run_id'],payload['unit_id'])).fetchone()
    if state is None:raise ValueError('Unidade não pertence à execução consultada.')
    pinned=db.execute('SELECT * FROM engine_unit_snapshots WHERE snapshot_id=?',(state['snapshot_id'],)).fetchone()
    try:snapshot=json.loads(pinned['snapshot_json']) if pinned else None
    except ValueError as exc:raise sqlite3.DatabaseError('Invalid pinned snapshot') from exc
    specifications={s['unit_id']:s for s in current['manifest']['units']};spec=specifications.get(payload['unit_id'])
    if snapshot is None or spec is None or input_hash(snapshot)!=pinned['snapshot_sha256'] or pinned['snapshot_sha256']!=spec['snapshot_sha256'] or any(state[k]!=spec[k] for k in ('snapshot_id','capacity_grams','initial_grams','rate_grams_per_minute')):raise sqlite3.DatabaseError('Preview snapshot integrity mismatch')
    if snapshot['source_kind']!='synthetic_controlled' or not validate_input(snapshot['input_template'])['accepted'] or snapshot['input_manifest']!=trusted_manifest():raise engine_runtime.Conflict('Unidade sem o contrato sintético exigido.')
    initial=state['remaining_grams'];elapsed=0;required=0;rows=[];curve=[{'minute_offset':0,'available_grams':initial}];exhaustion=0 if initial==0 else None
    for segment in segments:
        regime=rates[segment['regime_id']];rate=regime['grams_per_minute'];spent=segment['minutes']*rate;before=initial-required
        if exhaustion is None and spent>=before:
            exhaustion=elapsed+before/rate
            if spent>before:curve.append({'minute_offset':exhaustion,'available_grams':0})
        required+=spent;elapsed+=segment['minutes'];available=max(0,initial-required)
        rows.append({**segment,'label':regime['label'],'rate_grams_per_minute':rate,'fuel_required_grams':spent,'cumulative_required_grams':required,'end_offset_minutes':elapsed,'available_grams':available,'shortfall_grams':max(0,required-initial)})
        curve.append({'minute_offset':elapsed,'available_grams':available})
    limit=fuel_limits.status(db,payload['unit_id'],initial);minimum=limit['minimum_grams'];reached=0 if minimum is not None and initial<=minimum else None
    offset=0;used=0
    for row in rows:
        if minimum is not None and reached is None and initial-used-row['fuel_required_grams']<=minimum:reached=offset+(initial-used-minimum)/row['rate_grams_per_minute']
        offset+=row['minutes'];used+=row['fuel_required_grams']
    manifest={**trusted['manifest'],'fuel_limit_version':limit['version'],'minimum_grams':minimum,'run_id':current['run_id'],'run_manifest_sha256':current['manifest_sha256'],
              'scenario_version':current['scenario_version'],'revision':current['revision'],'unit_id':payload['unit_id'],
              'snapshot_sha256':pinned['snapshot_sha256'],'fuel_basis_grams':initial,'plan_sha256':input_hash(payload)}
    return {'scope':'synthetic_profile_preview','official_calculation_ready':False,'debit_applied':False,'duration_minutes':duration,
            'basis_elapsed_minutes':current['elapsed_minutes'],'fuel_basis_grams':initial,'fuel_required_grams':required,
            'fuel_remaining_grams':max(0,initial-required),'shortfall_grams':max(0,required-initial),'feasible':required<=initial,
            'minimum_alert':limit,'minimum_reached_at_offset_minutes':reached,
            'exhaustion_at_offset_minutes':exhaustion,'segments':rows,'curve':curve,'manifest':manifest,'manifest_sha256':input_hash(manifest)}
