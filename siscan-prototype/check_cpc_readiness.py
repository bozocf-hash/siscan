"""Prontidão: SQLite descartável, hipóteses explícitas e nenhuma execução."""
from copy import deepcopy
import random
import uuid
import sqlite3
import unittest
from unittest.mock import patch
from check_map_groups import seed,TEACHER,BLUE
from check_cpc_map import seed_pairs
from unit_groups import RegistroGrupamentos,GroupConflict
import operational_state_storage as storage
import cpc_judgment
import cpc_readiness as ready

def datum(value,unit):return dict(value=value,unit=unit,source='didactic_assumption')
def full_profile(base):
 units=[]
 for i,p in enumerate(base['preparation']['parties']):
  uid=p['members'][0]['unit_id'];params={key:datum(value,unit) for key,value,unit in [
   ('availability',True,'1'),('pontos_de_vida',100,'point'),('assinatura_radar',1,'m2'),('alcance_radar',50,'NM'),('probabilidade_deteccao',0.5,'1'),
   ('combustivel_atual',600,'kg'),('taxa_consumo_combustivel',2,'kg/min'),('velocidade',100,'kn'),('x',i*10,'NM'),('y',0,'NM'),('rumo',90,'deg'),('rumo_evasao',270,'deg'),
   ('raio_de_acao',200,'NM'),('teto_operacional',10000,'m'),('combustivel_minimo_retorno',100,'kg'),('estado_voo','em_voo','state')]}
  units.append(dict(unit_id=uid,parameters=params,armamentos=[dict(estoque_id=uid+'-missil',tipo='missil_ar_ar',quantidade=datum(2,'item'),pk=datum(0.4,'1'),dano=datum(10,'point'),alcance_maximo=datum(20,'NM'))]))
 return dict(schema_version=ready.PROFILE,label='Hipóteses exclusivamente sintéticas de teste',revision=1,scenario=dict(duration_minutes=datum(60,'min'),seed=datum(7,'1'),point_scale=datum('pontos-de-teste','scale'),reference=datum('plano-local-de-teste','local'),fatores_assinatura=[dict(assinatura_radar=datum(1,'m2'),fator=datum(0.5,'1'))]),units=units)

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');seed(self.db);storage.migrate(self.db)
        self.addCleanup(self.db.close);self.registry=RegistroGrupamentos()
        self.selection=seed_pairs(self.db,self.registry)
        self.base=cpc_judgment.context(self.db,TEACHER,self.registry,dict(selection=self.selection))
        self.body=dict(selection=self.selection,expected_view_sha256=self.base['preparation']['view_sha256'])
    def query(self,body=None,user=TEACHER):return ready.consultar_prontidao(self.db,user,self.registry,body or self.body)
    def test_sem_perfil_expoe_lacunas_sem_escrever_ou_sortear(self):
        before=list(self.db.iterdump());rng=random.getstate();groups=deepcopy(self.registry.listar_grupamentos(dict(exercise_id=1,team='AZUL')))
        with patch('random.Random',side_effect=AssertionError('RNG criado')):result=self.query()
        self.assertEqual(result['status'],'incomplete');self.assertFalse(result['ready_for_controlled_trial'])
        self.assertEqual(len(result['units']),2);self.assertTrue(result['issues'])
        for key in ('official_calculation_ready','simulation_started','official_effects_applied'):self.assertIs(result[key],False)
        self.assertEqual(before,list(self.db.iterdump()));self.assertEqual(random.getstate(),rng)
        self.assertEqual(groups,self.registry.listar_grupamentos(dict(exercise_id=1,team='AZUL')))
    def test_nega_operador_antes_de_ler_base(self):
        with patch.object(cpc_judgment,'context',side_effect=AssertionError('base lida')):
            with self.assertRaises(PermissionError):self.query(user=BLUE)
    def test_hash_antigo_e_extras_recusados(self):
        with self.assertRaises(ready.state.Conflict):self.query(dict(self.body,expected_view_sha256='0'*64))
        with self.assertRaises(ValueError):self.query(dict(self.body,extra=True))
    def test_reconferencia_observa_mudanca(self):
        original=cpc_judgment.context;calls=0
        def context(*args,**kwargs):
            nonlocal calls
            value=original(*args,**kwargs);calls+=1
            if calls==2:value['basis_sha256']='alterada'
            return value
        with patch.object(cpc_judgment,'context',side_effect=context):
            with self.assertRaises(ready.state.Conflict):self.query()
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_proposals').fetchone()[0],0)

    def test_perfil_completo_e_hash_reproduzivel_sem_efeitos(self):
        h=full_profile(self.base);before=list(self.db.iterdump());result=self.query(dict(self.body,hypotheses=h))
        self.assertTrue(result['ready_for_controlled_trial']);self.assertEqual(result['status'],'ready');self.assertEqual(result['issues'],[])
        self.assertEqual(before,list(self.db.iterdump()));self.assertIsNotNone(result['hypotheses_sha256'])
        h2=dict(reversed(list(h.items())));self.assertEqual(self.query(dict(self.body,hypotheses=h2))['hypotheses_sha256'],result['hypotheses_sha256'])
    def test_parcial_zero_e_coordenada_negativa(self):
        h=full_profile(self.base);params=h['units'][0]['parameters'];params['x']['value']=-10;params['taxa_consumo_combustivel']['value']=0;params['probabilidade_deteccao']['value']=0
        h['scenario']['seed']['value']=0;h['units'][0]['armamentos'][0]['quantidade']['value']=0
        result=self.query(dict(self.body,hypotheses=h));self.assertTrue(result['ready_for_controlled_trial']);self.assertTrue(result['warnings'])
        del params['pontos_de_vida'];result=self.query(dict(self.body,hypotheses=h));self.assertFalse(result['ready_for_controlled_trial']);self.assertTrue(any(i['field']=='pontos_de_vida' for i in result['issues']))
    def test_tipos_unidades_origens_estritos(self):
        for mutate in [lambda h:h.update(extra=1),lambda h:h.update(revision=True),lambda h:h.update(units=h['units']*2),
                       lambda h:h['units'][0].update(unit_id='estranho'),lambda h:h['units'][0]['parameters']['velocidade'].update(value=True),
                       lambda h:h['units'][0]['parameters']['combustivel_atual'].update(unit='litros'),lambda h:h['units'][0]['parameters']['pontos_de_vida'].update(source='aprovado'),
                       lambda h:h['units'][0]['armamentos'][0]['quantidade'].update(value=0.5),lambda h:h['units'][0]['parameters']['velocidade'].update(value=float('nan')),lambda h:h['units'][0]['parameters']['velocidade'].update(value=10**400)]:
            with self.subTest(mutate=mutate):
                h=full_profile(self.base);mutate(h)
                with self.assertRaises(ValueError):self.query(dict(self.body,hypotheses=h))
        with self.assertRaises(ValueError):self.query(dict(self.body,hypotheses=None))
    def test_fator_exato_e_estado_inicial_impeditivo(self):
        h=full_profile(self.base);h['scenario']['fatores_assinatura'][0]['assinatura_radar']['value']=2
        self.assertFalse(self.query(dict(self.body,hypotheses=h))['ready_for_controlled_trial'])
        h=full_profile(self.base);h['units'][0]['parameters']['availability']['value']=False
        self.assertTrue(any(i['category']=='operational_condition' for i in self.query(dict(self.body,hypotheses=h))['issues']))
    def test_perda_e_limite_nao_sao_contornados_por_hipotese(self):
        base=deepcopy(self.base);uid=base['preparation']['parties'][0]['members'][0]['unit_id'];base['states'][uid]['state']['lost']=True
        result=ready.diagnosticar(base,full_profile(self.base));self.assertFalse(result['ready_for_controlled_trial']);self.assertEqual(result['excluded'][0]['unit_id'],uid)
        base=deepcopy(self.base);base['preparation']['parties'][0]['members'].append(dict(base['preparation']['parties'][0]['members'][0],unit_id='outro'))
        base['states']['outro']=deepcopy(base['states'][uid]);result=ready.diagnosticar(base)
        self.assertEqual(result['status'],'unsupported')
        base=deepcopy(self.base);base['preparation']['parties'][0]['members'][0]['domain']='superficie'
        result=ready.diagnosticar(base);self.assertEqual(result['status'],'unsupported')
        self.assertTrue(any(i['field']=='domain' for i in result['issues']))

    def test_arquivamento_real_durante_diagnostico_recusa_resultado(self):
        original=ready.diagnosticar;before=list(self.db.iterdump())
        def changed(*args):
            result=original(*args);ref=self.selection['AZUL']
            self.registry.arquivar_grupamento(dict(exercise_id=1,team='AZUL'),dict(command_id=str(uuid.uuid4()),group_id=ref['group_id'],expected_revision=1))
            return result
        with patch.object(ready,'diagnosticar',side_effect=changed):
            with self.assertRaises(GroupConflict):self.query()
        self.assertEqual(before,list(self.db.iterdump()));self.assertFalse(self.db.in_transaction)
    def test_unavailable_estoques_e_geometria_invalidos(self):
        h=full_profile(self.base);h['units'][0]['parameters']['velocidade']={'value':None,'unit':'kn','source':'unavailable'}
        self.assertFalse(self.query(dict(self.body,hypotheses=h))['ready_for_controlled_trial'])
        for mutate in [lambda h:h['units'][0]['armamentos'].append(deepcopy(h['units'][0]['armamentos'][0])),
                       lambda h:h['scenario']['fatores_assinatura'].append(deepcopy(h['scenario']['fatores_assinatura'][0])),
                       lambda h:h['scenario'].update(distance_nm=datum(500,'NM')),
                       lambda h:h.update(units='invalido')]:
            h=full_profile(self.base);mutate(h)
            with self.assertRaises(ValueError):self.query(dict(self.body,hypotheses=h))
        h=full_profile(self.base);h['units'][0]['armamentos']=[]
        self.assertTrue(self.query(dict(self.body,hypotheses=h))['ready_for_controlled_trial'])

if __name__=='__main__':unittest.main()
