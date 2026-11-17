"""Julgamento CPC com registro real e banco descartável."""
from copy import deepcopy
import sqlite3
import unittest
from unittest.mock import patch
import uuid
import engine_units
import operational_state as state
import operational_state_storage as storage
from check_map_groups import seed,TEACHER,BLUE
from check_cpc_map import seed_pairs
from unit_groups import RegistroGrupamentos,GroupConflict
import cpc_judgment as judgment


class JudgmentTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');seed(self.db);self.db.execute('PRAGMA foreign_keys=ON')
        storage.migrate(self.db);self.addCleanup(self.db.close)
        self.registry=RegistroGrupamentos();self.selection=seed_pairs(self.db,self.registry)

    def base(self):return judgment.context(self.db,TEACHER,self.registry,dict(selection=self.selection))

    def body(self):
        base=self.base();uid=next(iter(base['states']))
        return dict(selection=self.selection,basis_sha256=base['basis_sha256'],reason='Aula de julgamento',
                    effects=[dict(unit_id=uid,changes={'index_percent':60})])

    def register(self):
        body=dict(self.body(),command_id=str(uuid.uuid4()))
        return judgment.register(self.db,TEACHER,self.registry,body),body

    def test_registrar_retomar_revisar_e_replay_sem_grupos(self):
        first,body=self.register()
        view=judgment.get(self.db,TEACHER,self.registry,first['proposal_id'])
        self.assertTrue(view['available']);self.assertEqual(len(judgment.listing(self.db,TEACHER)['items']),1)
        edit=dict(self.body(),command_id=str(uuid.uuid4()),proposal_id=first['proposal_id'],
                  expected_revision=first['revision'],expected_sha256=first['body_sha256'])
        edit['effects'][0]['changes']['index_percent']=40
        second=judgment.revise(self.db,TEACHER,self.registry,edit)
        self.assertEqual(second['revision'],2)
        self.assertEqual(judgment.register(self.db,TEACHER,RegistroGrupamentos(),body),first)
        self.assertFalse(judgment.get(self.db,TEACHER,RegistroGrupamentos(),first['proposal_id'])['available'])
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_effects').fetchone()[0],0)

    def test_contexto_previa_sem_escrita_e_hash_estavel(self):
        before=list(self.db.iterdump());body=self.body()
        preview=judgment.preview(self.db,TEACHER,self.registry,body)
        self.assertEqual(preview['effects'][0]['after']['index_percent'],60)
        self.assertIsNone(preview['effects'][0]['before']['index_percent'])
        self.assertEqual(self.base()['basis_sha256'],body['basis_sha256'])
        self.assertEqual(list(self.db.iterdump()),before)

    def test_operador_recusado_antes_das_fontes(self):
        with patch('cpc_map.prepare',side_effect=AssertionError('Fonte indevida')):
            with self.assertRaises(PermissionError):judgment.context(self.db,BLUE,self.registry,dict(selection=self.selection))

    def test_base_posicao_e_estado_alterados_recusam(self):
        body=self.body();aid=self.db.execute('SELECT asset_id FROM engine_units LIMIT 1').fetchone()[0]
        self.db.execute('INSERT INTO map_unit_positions VALUES(?,?,?,1,1)',(aid,-22,-43));self.db.commit()
        with self.assertRaises(state.Conflict):judgment.preview(self.db,TEACHER,self.registry,body)

    def test_meio_externo_e_payload_inesperado(self):
        body=self.body();body['effects'][0]['unit_id']='externo'
        with self.assertRaises(ValueError):judgment.preview(self.db,TEACHER,self.registry,body)
        with self.assertRaises(ValueError):judgment.context(self.db,TEACHER,self.registry,dict(selection=self.selection,role='instructor'))


if __name__=='__main__':unittest.main()
