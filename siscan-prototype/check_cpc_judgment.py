"""Julgamento CPC com registro real e banco descartável."""
from copy import deepcopy
import sqlite3
import unittest
from unittest.mock import patch
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread,Event
from contextlib import closing
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

    def command(self,p,action='confirm'):
        return dict(command_id=str(uuid.uuid4()),proposal_id=p['proposal_id'],expected_revision=p['revision'],
                    expected_sha256=p['body_sha256'],action=action,reason='Decisão em aula')

    def test_confirmar_replay_apos_perda_dos_grupos(self):
        p,_=self.register();command=self.command(p);result=judgment.decide(self.db,TEACHER,self.registry,command)
        self.assertEqual(result['action'],'confirm')
        self.assertEqual(judgment.decide(self.db,TEACHER,RegistroGrupamentos(),command),result)
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_effects').fetchone()[0],1)
        view=judgment.get(self.db,TEACHER,RegistroGrupamentos(),p['proposal_id'])
        self.assertEqual(view['decision']['action'],'confirm')

    def test_grupo_arquivado_recusa_confirmacao_mas_permite_rejeitar(self):
        p,_=self.register();ref=self.selection['AZUL']
        self.registry.arquivar_grupamento(dict(exercise_id=1,team='AZUL'),dict(command_id=str(uuid.uuid4()),**ref))
        with self.assertRaises(GroupConflict):judgment.decide(self.db,TEACHER,self.registry,self.command(p))
        self.assertEqual(judgment.decide(self.db,TEACHER,self.registry,self.command(p,'reject'))['action'],'reject')
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_effects').fetchone()[0],0)

    def test_falha_recibo_reverte_e_transacao_externa_recusada(self):
        p,_=self.register();before=list(self.db.iterdump())
        with patch.object(state,'_receipt',side_effect=RuntimeError('falha')):
            with self.assertRaises(RuntimeError):judgment.decide(self.db,TEACHER,self.registry,self.command(p))
        self.assertEqual(list(self.db.iterdump()),before)
        self.db.execute('BEGIN')
        with self.assertRaises(ValueError):judgment.decide(self.db,TEACHER,self.registry,self.command(p))
        self.db.rollback()

    def test_commit_ocorre_antes_de_liberar_mutacao_do_grupo(self):
        p,_=self.register();started=Event();done=Event();observed=[]
        with TemporaryDirectory() as folder,closing(sqlite3.connect(str(Path(folder)/'test.sqlite3'),timeout=5)) as db:
            self.db.backup(db);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
            path=Path(folder)/'test.sqlite3';original=state.decidir_proposta
            def archive():
                started.set()
                self.registry.arquivar_grupamento(dict(exercise_id=1,team='AZUL'),
                    dict(command_id=str(uuid.uuid4()),**self.selection['AZUL']))
                with closing(sqlite3.connect(path)) as other:
                    observed.append(other.execute('SELECT count(*) FROM operational_effects').fetchone()[0])
                done.set()
            thread=Thread(target=archive,daemon=True)
            def during(*args):
                thread.start();self.assertTrue(started.wait(2));self.assertFalse(done.is_set())
                return original(*args)
            with patch.object(state,'decidir_proposta',side_effect=during):
                judgment.decide(db,TEACHER,self.registry,self.command(p))
            thread.join(5);self.assertTrue(done.is_set());self.assertEqual(observed,[1])

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
