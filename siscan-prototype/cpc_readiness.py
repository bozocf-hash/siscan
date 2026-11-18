"""Conferência somente leitura de entradas didáticas; não executa combate."""
from copy import deepcopy
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

def diagnosticar(base,hypotheses=None):
 preparation=base['preparation'];units=[];excluded=[];issues=[]
 for party in preparation['parties']:
  active=[]
  for member in party['members']:
   uid=member['unit_id'];current=base['states'][uid]['state']
   row=dict(unit_id=uid,team=party['team'],code=member['code'],name=member['name'],domain=member['domain'],state_revision=current['revision'])
   if current['lost'] is True:excluded.append(dict(row,reason='Perda oficial confirmada.'));continue
   units.append(row);active.append(row)
   if member['domain']!='aereo':issues.append(issue('unsupported_by_current_engine','domain','Configuração fora do recorte aéreo controlado.',uid,'unsupported_by_current_engine','Usar configuração demonstrada pelo provedor.'))
   for key,label,*_ in COMMON+AIR:issues.append(issue('missing_data',key,label+' não declarado.',uid))
   issues.append(issue('missing_data','armamentos','Declare os estoques, inclusive lista vazia explícita.',uid))
  if len(active)!=1:issues.append(issue('unsupported_by_current_engine' if active else 'no_available_member','selection','O ensaio exige um integrante utilizável por partido.',category='unsupported_by_current_engine' if active else 'operational_condition',action='Conferir composição e perdas oficiais.'))
 for key,label,*_ in SCENARIO:issues.append(issue('missing_data','scenario.'+key,label+' não declarado.'))
 issues.append(issue('missing_data','scenario.fatores_assinatura','Fatores didáticos de assinatura não declarados.'))
 if hypotheses is not None:raise ValueError('Perfil ainda não habilitado neste incremento.')
 issues.sort(key=lambda x:(x['unit_id'] or '',x['field'],x['code']))
 return dict(schema_version=SCHEMA,exercise_id=preparation['exercise_id'],scenario_version=preparation['scenario_version'],
  selection=deepcopy(base['selection']),view_sha256=preparation['view_sha256'],basis_sha256=base['basis_sha256'],
  scope='controlled_pair',units=units,excluded=excluded,issues=issues,warnings=[],hypotheses_sha256=None,
  status='unsupported' if any(i['category']=='unsupported_by_current_engine' for i in issues) else 'incomplete',
  ready_for_controlled_trial=False,official_calculation_ready=False,simulation_started=False,official_effects_applied=False)

def consultar_prontidao(db,user,registry,body):
 state.autorizar_instrutor(db,user,write=True)
 judgment.fields(body,{'selection','expected_view_sha256'},{'hypotheses'})
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
