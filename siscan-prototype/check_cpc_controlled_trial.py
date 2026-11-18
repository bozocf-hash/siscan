"""Ensaio sintético local, sem mudanças no exercício."""
from copy import deepcopy
import random
import unittest
import uuid
from unittest.mock import patch
import check_cpc_readiness as fixture
import cpc_judgment
import cpc_controlled_trial as trial
from unit_groups import GroupConflict


class ControlledTrialTests(unittest.TestCase):
    setUp=fixture.ReadinessTests.setUp

    def request_body(self):
        # The existing fixture names its initial readiness request "body".
        h=fixture.full_profile(self.base)
        for u in h['units']:
            u['parameters']['velocidade']['value']=0
            u['parameters']['probabilidade_deteccao']['value']=1
            u['armamentos'][0]['pk']['value']=0
        h['scenario']['fatores_assinatura'][0]['fator']['value']=1
        return dict(self.body,expected_basis_sha256=self.base['basis_sha256'],
                    expected_hypotheses_sha256=cpc_judgment.digest(h),hypotheses=h,
                    policy=dict(schema_version='siscan-cpc-controlled-policy-01',initiative='simultaneous',
                                weapons={u['unit_id']:u['armamentos'][0]['estoque_id'] for u in h['units']}))

    def run_trial(self,body=None):
        return trial.executar_ensaio(self.db,fixture.TEACHER,self.registry,body or self.request_body())

    def changed(self,body):
        body['expected_hypotheses_sha256']=cpc_judgment.digest(body['hypotheses']);return body

    def test_sessenta_minutos_recursos_reproducao_e_nenhum_efeito(self):
        body=self.request_body();original=deepcopy(body);sql=list(self.db.iterdump());rng=random.getstate()
        a=self.run_trial(body);b=self.run_trial(body)
        self.assertEqual(a['balance']['minutos_simulados'],60);self.assertEqual(a['balance']['misseis_gastos'],4)
        self.assertEqual([u['combustivel_kg'] for u in a['final']], [480,480])
        self.assertEqual(a['initial'],b['initial']);self.assertEqual(a['final'],b['final']);self.assertEqual(a['balance'],b['balance'])
        clean=lambda r:[{k:v for k,v in e.items() if k!='execucao_id'} for e in r['events']]
        self.assertEqual(clean(a),clean(b));self.assertFalse(a['official_effects_applied'])
        self.assertEqual(sql,list(self.db.iterdump()));self.assertEqual(rng,random.getstate());self.assertEqual(body,original)

    def test_sem_deteccao_sem_consumo_de_armamento(self):
        body=self.request_body()
        for u in body['hypotheses']['units']:u['parameters']['probabilidade_deteccao']['value']=0
        r=self.run_trial(self.changed(body));self.assertEqual(r['balance']['misseis_gastos'],0)
        self.assertTrue(any(e['tipo']=='deteccao' and not e['dados']['detectado'] for e in r['events']))

    def test_simultaneo_e_iniciativa_explicita(self):
        body=self.request_body()
        for u in body['hypotheses']['units']:
            u['armamentos'][0]['pk']['value']=1;u['armamentos'][0]['dano']['value']=100
        r=self.run_trial(self.changed(body));self.assertEqual(r['balance']['quantidade_perdas_propostas'],2)
        self.assertEqual(r['minutes_completed'],1);self.assertEqual(r['stop_reason'],'participant_loss')
        body['policy']['initiative']='AZUL';r=self.run_trial(body)
        self.assertEqual(r['balance']['quantidade_perdas_propostas'],1);self.assertEqual(r['balance']['misseis_gastos'],1)

    def test_combustivel_evasao_e_perda_proposta(self):
        body=self.request_body();u=body['hypotheses']['units'][0]
        u['parameters']['combustivel_atual']['value']=3;u['parameters']['combustivel_minimo_retorno']['value']=2
        r=self.run_trial(self.changed(body));self.assertEqual(r['minutes_completed'],2)
        self.assertIn(u['unit_id'],r['balance']['perdas_aereas_propostas'])
        self.assertEqual(r['final'][0]['combustivel_kg'],0)

    def test_politica_limites_e_hipoteses_invalidas(self):
        for mutate in [lambda b:b['policy'].update(initiative='auto'),lambda b:b['policy']['weapons'].update(estranho=None),
                       lambda b:b['policy']['weapons'].update({next(iter(b['policy']['weapons'])):'alheio'}),
                       lambda b:b['hypotheses']['scenario']['duration_minutes'].update(value=121),
                       lambda b:b['hypotheses']['units'][0]['parameters']['taxa_consumo_combustivel'].update(value=0),
                       lambda b:b['hypotheses']['units'][0]['armamentos'][0].update(tipo='missil_antinavio')]:
            with self.subTest(mutate=mutate):
                body=self.request_body();mutate(body)
                with self.assertRaises(ValueError):self.run_trial(self.changed(body))
        body=self.request_body();del body['hypotheses']['units'][0]['parameters']['velocidade']
        with self.assertRaises(ValueError):self.run_trial(self.changed(body))

    def test_observacao_sem_arma_e_hash_antigo(self):
        body=self.request_body();body['policy']['weapons']=dict.fromkeys(body['policy']['weapons'])
        self.assertEqual(self.run_trial(body)['balance']['misseis_gastos'],0)
        for key in ['expected_basis_sha256','expected_hypotheses_sha256','expected_view_sha256']:
            with self.subTest(key=key):
                b=deepcopy(body);b[key]='0'*64
                with self.assertRaises(fixture.ready.state.Conflict):self.run_trial(b)

    def test_operador_recusado_antes_do_motor(self):
        with patch.object(trial,'simular_par',side_effect=AssertionError('motor invocado')):
            with self.assertRaises(PermissionError):trial.executar_ensaio(self.db,fixture.BLUE,self.registry,self.request_body())

    def test_mudanca_real_de_grupo_recusa_relatorio(self):
        original=trial.simular_par;before=list(self.db.iterdump())
        def changed(*args):
            result=original(*args);ref=self.selection['AZUL']
            self.registry.arquivar_grupamento(dict(exercise_id=1,team='AZUL'),dict(command_id=str(uuid.uuid4()),group_id=ref['group_id'],expected_revision=1))
            return result
        with patch.object(trial,'simular_par',side_effect=changed):
            with self.assertRaises(GroupConflict):self.run_trial()
        self.assertEqual(before,list(self.db.iterdump()));self.assertFalse(self.db.in_transaction)


if __name__=='__main__':unittest.main()
