"""Prontidão: SQLite descartável, hipóteses explícitas e nenhuma execução."""
from copy import deepcopy
import random
import sqlite3
import unittest
from unittest.mock import patch
from check_map_groups import seed,TEACHER,BLUE
from check_cpc_map import seed_pairs
from unit_groups import RegistroGrupamentos,GroupConflict
import operational_state_storage as storage
import cpc_judgment
import cpc_readiness as ready

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

if __name__=='__main__':unittest.main()
