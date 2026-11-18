"""Conferência somente leitura de entradas didáticas; não executa combate."""
from copy import deepcopy
import math
import engine_units
import cpc_judgment as judgment
import operational_state as state

SCHEMA='siscan-cpc-trial-readiness-01'
PROFILE='siscan-cpc-trial-hypotheses-01'
# key, label, unit, type, minimum, maximum, section
SCENARIO=[
 ('duration_minutes','Duração','min','integer',1,None,'Cenário'),
 ('seed','Semente reproduzível','1','integer',0,4294967295,'Cenário'),
 ('point_scale','Escala abstrata comum de vida e dano','scale','text',None,None,'Cenário'),
 ('reference','Referência da geometria local','local','text',None,None,'Cenário')]
COMMON=[
 ('availability','Disponibilidade assumida para o ensaio','1','boolean',None,None,'Condição inicial'),
 ('pontos_de_vida','Pontos de vida abstratos','point','number',0,None,'Condição inicial'),
 ('assinatura_radar','Assinatura radar didática','m2','number',0,None,'Sensores'),
 ('alcance_radar','Alcance radar didático','NM','number',0,None,'Sensores'),
 ('probabilidade_deteccao','Probabilidade didática de detecção','1','number',0,1,'Sensores'),
 ('combustivel_atual','Combustível inicial hipotético','kg','number',0,None,'Logística'),
 ('taxa_consumo_combustivel','Taxa de consumo hipotética','kg/min','number',0,None,'Logística'),
 ('velocidade','Velocidade','kn','number',0,None,'Logística'),
 ('x','Posição local X','NM','number',None,None,'Cenário'),
 ('y','Posição local Y','NM','number',None,None,'Cenário'),
 ('rumo','Rumo normal','deg','number',0,360,'Cenário'),
 ('rumo_evasao','Rumo de evasão','deg','number',0,360,'Cenário')]
AIR=[
 ('raio_de_acao','Raio de ação','NM','number',0,None,'Logística'),
 ('teto_operacional','Teto operacional','m','number',0,None,'Logística'),
 ('combustivel_minimo_retorno','Reserva de retorno hipotética','kg','number',0,None,'Logística'),
 ('estado_voo','Situação de voo','state','flight',None,None,'Condição inicial')]
WEAPONS=[
 ('quantidade','Quantidade','item','integer',0,None,'Armamentos'),
 ('pk','Pk didático','1','number',0,1,'Armamentos'),
 ('dano','Dano na escala abstrata do cenário','point','number',0,None,'Armamentos'),
 ('alcance_maximo','Alcance máximo','NM','number',0,None,'Armamentos')]

def issue(code,field,message,unit_id=None,category='missing_data',action='Declare o dado e sua origem didática.'):
 return dict(code=code,category=category,unit_id=unit_id,field=field,message=message,action=action)

def _object(value,allowed,name):
 if not isinstance(value,dict) or set(value)-set(allowed):raise ValueError(name+': campos inválidos.')
 return value

def _text(value,name,maximum=200):
 if not isinstance(value,str) or len(value)>maximum:raise ValueError(name+': texto inválido.')
 return value.strip()

def _descriptor(raw,spec,issues,path,uid=None):
 key,label,unit,kind,minimum,maximum,*_=spec
 if raw is None:issues.append(issue('missing_data',path,label+' não declarado.',uid));return None
 _object(raw,{'value','unit','source','note'},path)
 if 'note'in raw:_text(raw['note'],path+'.note',400)
 source=raw.get('source');value=raw.get('value')
 if source is not None and source not in ('didactic_assumption','unavailable'):raise ValueError(path+': origem não demonstrada; use hipótese didática explícita.')
 if value is None or source=='unavailable' or source is None or 'unit'not in raw:
  if source=='unavailable' and value is not None:raise ValueError(path+': origem indisponível não pode declarar valor.')
  issues.append(issue('missing_data',path,label+' sem valor/unidade/origem completos.',uid));return None
 if raw['unit']!=unit:raise ValueError(path+': unidade esperada '+unit+'.')
 if kind in ('text','flight'):
  value=_text(value,path)
  if not value:issues.append(issue('missing_data',path,label+' não declarado.',uid));return None
  if kind=='flight' and value not in ('em_voo','evadindo','pousado','perda_proposta'):raise ValueError(path+': situação de voo inválida.')
 elif kind=='boolean':
  if type(value)is not bool:raise ValueError(path+': informe verdadeiro ou falso explicitamente.')
 else:
  try:finite=type(value)in (int,float) and math.isfinite(value)
  except OverflowError:finite=False
  if not finite or kind=='integer' and (type(value)is not int or value>9007199254740991):raise ValueError(path+': número inválido.')
  if minimum is not None and value<minimum or maximum is not None and value>maximum:raise ValueError(path+': valor fora da faixa.')
 return value

def _form(specs):
 return [dict(key=k,label=l,unit=u,kind=t,minimum=mi,maximum=ma,section=g) for k,l,u,t,mi,ma,g in specs]

def diagnosticar(base,hypotheses=None):
 preparation=base['preparation'];units=[];excluded=[];issues=[];warnings=[];requirements={}
 h={} if hypotheses is None else _object(hypotheses,{'schema_version','label','revision','scenario','units'},'hypotheses')
 if h.get('schema_version') is None:issues.append(issue('missing_data','schema_version','Identificação do formato das hipóteses ausente.'))
 elif h['schema_version']!=PROFILE:raise ValueError('Formato das hipóteses não suportado.')
 if 'label'not in h or not _text(h['label'],'label',120):issues.append(issue('missing_data','label','Nome das hipóteses não declarado.'))
 if 'revision'not in h:issues.append(issue('missing_data','revision','Revisão das hipóteses não declarada.'))
 elif type(h['revision'])is not int or not 1<=h['revision']<=9007199254740991:raise ValueError('Revisão inválida.')
 scenario=_object(h.get('scenario',{}),{x[0] for x in SCENARIO}|{'fatores_assinatura','distance_nm'},'scenario')
 scenario_values={spec[0]:_descriptor(scenario.get(spec[0]),spec,issues,'scenario.'+spec[0]) for spec in SCENARIO}
 entries=h.get('units',[])
 if not isinstance(entries,list) or len(entries)>100:raise ValueError('Lista de hipóteses por unidade inválida.')
 allowed={m['unit_id'] for party in preparation['parties'] for m in party['members']};profiles={}
 for entry in entries:
  _object(entry,{'unit_id','parameters','armamentos'},'unit');uid=entry.get('unit_id')
  if not isinstance(uid,str) or uid not in allowed or uid in profiles:raise ValueError('Unidade de hipótese estranha ou repetida.')
  profiles[uid]=entry
 factors={};factor_specs=[('assinatura_radar','Assinatura radar','m2','number',0,None,'Sensores'),('fator','Fator didático de assinatura','1','number',0,1,'Sensores')]
 raw_factors=scenario.get('fatores_assinatura')
 if raw_factors is None:issues.append(issue('missing_data','scenario.fatores_assinatura','Fatores didáticos de assinatura não declarados.'))
 else:
  if not isinstance(raw_factors,list) or len(raw_factors)>100:raise ValueError('Lista de fatores inválida.')
  for i,entry in enumerate(raw_factors):
   _object(entry,{'assinatura_radar','fator'},'factor')
   values=[_descriptor(entry.get(spec[0]),spec,issues,f'scenario.fatores_assinatura[{i}].'+spec[0]) for spec in factor_specs]
   if values[0] is not None:
    if values[0]in factors:raise ValueError('Assinatura repetida na rubrica.')
    factors[values[0]]=values[1]
 points={};all_stocks=set()
 for party in preparation['parties']:
  active=[]
  for member in party['members']:
   uid=member['unit_id'];current=base['states'][uid]['state']
   row=dict(unit_id=uid,team=party['team'],code=member['code'],name=member['name'],domain=member['domain'],state_revision=current['revision'])
   if current['lost'] is True:excluded.append(dict(row,reason='Perda oficial confirmada.'));continue
   units.append(row);active.append(row)
   if member['domain']!='aereo':issues.append(issue('unsupported_by_current_engine','domain','Configuração fora do recorte aéreo controlado.',uid,'unsupported_by_current_engine','Usar configuração demonstrada pelo provedor.'))
   specs=COMMON+(AIR if member['domain']=='aereo' else [])
   requirements[uid]=_form(specs)
   entry=profiles.get(uid,{})
   params=_object(entry.get('parameters',{}),{x[0] for x in specs},'parameters')
   values={spec[0]:_descriptor(params.get(spec[0]),spec,issues,spec[0],uid) for spec in specs}
   if values['availability'] is False or values['pontos_de_vida']==0 or values.get('estado_voo')=='perda_proposta' or values.get('estado_voo')in ('em_voo','evadindo') and values['combustivel_atual']==0:
    issues.append(issue('initial_unavailable','availability','Condição inicial impeditiva declarada.',uid,'operational_condition','Rever a hipótese inicial sem alterar a perda oficial.'))
   signature=values['assinatura_radar']
   if signature is not None and (signature not in factors or factors[signature]is None):issues.append(issue('missing_signature_factor','assinatura_radar','Falta fator explícito para esta assinatura.',uid))
   if values['x']is not None and values['y']is not None:points[uid]=(values['x'],values['y'])
   weapons=entry.get('armamentos')
   if weapons is None:issues.append(issue('missing_data','armamentos','Declare os estoques, inclusive lista vazia explícita.',uid))
   else:
    if not isinstance(weapons,list) or len(weapons)>100:raise ValueError('Lista de estoques inválida.')
    total=0
    for i,weapon in enumerate(weapons):
     _object(weapon,{'estoque_id','tipo'}|{x[0] for x in WEAPONS},'armamento');stock=weapon.get('estoque_id')
     if stock is None:issues.append(issue('missing_data',f'armamentos[{i}].estoque_id','Identidade do estoque não declarada.',uid))
     else:
      stock=_text(stock,'estoque_id',120)
      if not stock or stock in all_stocks:raise ValueError('Estoque vazio, compartilhado ou repetido.')
      all_stocks.add(stock)
     if 'tipo'not in weapon:issues.append(issue('missing_data',f'armamentos[{i}].tipo','Tipo do estoque não declarado.',uid))
     elif weapon['tipo']not in ('missil_ar_ar','missil_antinavio','defesa_ponto'):raise ValueError('Tipo de armamento não suportado.')
     ws={spec[0]:_descriptor(weapon.get(spec[0]),spec,issues,f'armamentos[{i}].'+spec[0],uid) for spec in WEAPONS}
     if ws['quantidade']is not None:total+=ws['quantidade']
    if total==0:warnings.append(issue('no_ammunition','armamentos','Sem munição declarada para engajar.',uid,'warning','A prontidão das entradas não garante engajamento.'))
  if len(active)!=1:issues.append(issue('unsupported_by_current_engine' if active else 'no_available_member','selection','O ensaio exige um integrante utilizável por partido.',category='unsupported_by_current_engine' if active else 'operational_condition',action='Conferir composição e perdas oficiais.'))
 geometry=None
 if len(units)==2 and len(points)==2:
  distance=math.dist(*points.values())
  if not math.isfinite(distance):raise ValueError('Geometria fora da faixa numérica.')
  geometry=dict(reference=scenario_values['reference'],distance_nm=distance,source='derived_from_explicit_local_positions')
  if 'distance_nm'in scenario:
   given=_descriptor(scenario['distance_nm'],('distance_nm','Distância local','NM','number',0,None,'Cenário'),issues,'scenario.distance_nm')
   if given is not None and not math.isclose(given,distance,rel_tol=1e-9,abs_tol=1e-9):raise ValueError('Distância declarada incompatível com posições locais.')
 warnings.append(issue('local_geometry','scenario.reference','Geometria local hipotética; não é trajetória geográfica do mapa.',category='warning',action='Usar o contexto didático declarado.'))
 issues.sort(key=lambda x:(x['unit_id'] or '',x['field'],x['code']))
 return dict(schema_version=SCHEMA,exercise_id=preparation['exercise_id'],scenario_version=preparation['scenario_version'],
  selection=deepcopy(base['selection']),view_sha256=preparation['view_sha256'],basis_sha256=base['basis_sha256'],
  scope='controlled_pair',units=units,excluded=excluded,issues=issues,warnings=warnings,geometry=geometry,
  hypotheses_sha256=judgment.digest(hypotheses) if hypotheses is not None else None,
  requirements=dict(profile_schema=PROFILE,scenario=_form(SCENARIO),units=requirements,weapons=_form(WEAPONS)),
  status='unsupported' if any(i['category']=='unsupported_by_current_engine' for i in issues) else 'incomplete' if issues else 'ready',
  ready_for_controlled_trial=not issues,official_calculation_ready=False,simulation_started=False,official_effects_applied=False)

def consultar_prontidao(db,user,registry,body):
 state.autorizar_instrutor(db,user,write=True)
 judgment.fields(body,{'selection','expected_view_sha256'},{'hypotheses'})
 if 'hypotheses'in body and not isinstance(body['hypotheses'],dict):raise ValueError('Hipóteses devem ser objeto.')
 if len(engine_units.encoded(body).encode('utf-8'))>64000:raise ValueError('Pedido excede 64 KB.')
 db.execute('SAVEPOINT cpc_readiness_view')
 try:
  args=dict(selection=body['selection'],expected_view_sha256=body['expected_view_sha256'])
  base=judgment.context(db,user,registry,args)
  result=diagnosticar(base,body.get('hypotheses'))
  fresh=judgment.context(db,user,registry,args)
  if fresh['basis_sha256']!=base['basis_sha256']:raise state.Conflict('Base alterada; confira o par novamente.')
  db.execute('RELEASE cpc_readiness_view');return result
 except Exception:
  db.execute('ROLLBACK TO cpc_readiness_view');db.execute('RELEASE cpc_readiness_view');raise
