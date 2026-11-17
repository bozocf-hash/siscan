"""Estado/adjudicação didática: testes em SQLite descartável."""
import math
from copy import deepcopy
import sqlite3
import unittest
import uuid
from unittest.mock import patch

import engine_units
import operational_state as state
from check_map_groups import seed, TEACHER, BLUE, RED
import operational_state_storage as store


def proposal(db,changes=None):
    effects=[]
    for u in engine_units.list_units(db,TEACHER)['units']:
        effects.append(dict(unit_id=u['unit_id'],expected_state_revision=state.consultar(db,TEACHER,u['unit_id'])['state']['revision'],
            **{k:u[k] for k in ('snapshot_id','snapshot_sha256','configuration_version_id')},
            changes=changes or {'index_percent':80}))
    return dict(command_id=str(uuid.uuid4()),source='didactic',reason='Intervenção do instrutor',
                origin={'reference':'Aula controlada'},effects=effects)


class ProposalTests(unittest.TestCase):
    setUp=lambda self:ReadTests.setUp(self)

    def test_registro_e_replay_sem_estado_oficial(self):
        body=proposal(self.db);before=[state.consultar(self.db,TEACHER,u['unit_id']) for u in self.units]
        result=state.registrar_proposta(self.db,TEACHER,body)
        self.assertEqual(result,state.registrar_proposta(self.db,TEACHER,body))
        self.assertEqual(result['revision'],1)
        self.assertEqual([state.consultar(self.db,TEACHER,u['unit_id']) for u in self.units],before)
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_effects').fetchone()[0],0)
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_commands').fetchone()[0],1)

    def test_payload_e_fonte_estritos(self):
        body=proposal(self.db)
        for bad in ({},dict(body,actor_id=1),dict(body,source='automatic'),dict(body,reason=' '),dict(body,command_id='x')):
            with self.subTest(bad=bad),self.assertRaises(ValueError):state.registrar_proposta(self.db,TEACHER,bad)
        for key in ('snapshot_id','configuration_version_id','snapshot_sha256'):
            bad=deepcopy(body);bad['effects'][0][key]='divergente'
            with self.assertRaises(state.Conflict):state.registrar_proposta(self.db,TEACHER,bad)

    def test_papel_fechamento_revogacao_e_replay_divergente(self):
        body=proposal(self.db)
        with self.assertRaises(PermissionError):state.registrar_proposta(self.db,BLUE,body)
        result=state.registrar_proposta(self.db,TEACHER,body)
        with self.assertRaises(state.Conflict):state.registrar_proposta(self.db,TEACHER,dict(body,reason='outro'))
        self.db.execute('DELETE FROM assignments WHERE user_id=1')
        with self.assertRaises(PermissionError):state.registrar_proposta(self.db,TEACHER,body)
        self.db.rollback();self.db.execute("UPDATE exercises SET state='closed'")
        with self.assertRaises(ValueError):state.registrar_proposta(self.db,TEACHER,dict(body,command_id=str(uuid.uuid4())))

    def test_lote_duplicado_e_revisao_de_estado(self):
        body=proposal(self.db);body['effects'].append(deepcopy(body['effects'][0]))
        with self.assertRaises(ValueError):state.registrar_proposta(self.db,TEACHER,body)
        body=proposal(self.db);body['effects'][0]['expected_state_revision']=1
        with self.assertRaises(state.Conflict):state.registrar_proposta(self.db,TEACHER,body)

    def test_falha_recibo_reverte_proposta(self):
        body=proposal(self.db);before=list(self.db.iterdump())
        with patch.object(state,'_receipt',side_effect=RuntimeError('falha provocada')):
            with self.assertRaises(RuntimeError):state.registrar_proposta(self.db,TEACHER,body)
        self.assertEqual(list(self.db.iterdump()),before)

    def test_proposta_congela_origem_e_snapshots(self):
        body=proposal(self.db);result=state.registrar_proposta(self.db,TEACHER,body)
        body['origin']['reference']='mutado'
        stored=self.db.execute('SELECT body_json FROM operational_proposal_revisions').fetchone()[0]
        self.assertIn('Aula controlada',stored);self.assertNotIn('mutado',stored)
        self.assertIn('domain_evidence',stored);self.assertIn('snapshot_sha256',stored)


class ReadTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');seed(self.db)
        self.db.execute('PRAGMA foreign_keys=ON');store.migrate(self.db)
        self.addCleanup(self.db.close)
        self.units=engine_units.list_units(self.db,TEACHER)['units']
        self.blue=next(u for u in self.units if u['team']=='AZUL')['unit_id']
        self.red=next(u for u in self.units if u['team']=='VERMELHO')['unit_id']

    def test_ausente_nao_grava_nem_presume_prontidao(self):
        before=list(self.db.iterdump());result=state.consultar(self.db,BLUE,self.blue)
        self.assertEqual(result['state']['revision'],0)
        self.assertIsNone(result['state']['index_percent']);self.assertIsNone(result['state']['lost'])
        self.assertIsNone(result['condition']);self.assertEqual(state.historico(self.db,BLUE,self.blue),[])
        self.assertEqual(list(self.db.iterdump()),before)

    def test_autoriza_antes_de_ler_identidades(self):
        with patch.object(engine_units,'list_units',side_effect=AssertionError('Fonte consultada')):
            for user,unit in [(BLUE,self.red),(dict(uid=99,role='instructor'),self.blue),
                    (dict(uid=2,role='instructor',team=None),self.blue)]:
                with self.assertRaises(PermissionError):state.consultar(self.db,user,unit)

    def test_revogacao_e_fechamento(self):
        self.db.execute("UPDATE exercises SET state='closed'")
        self.assertEqual(state.consultar(self.db,TEACHER,self.blue)['state']['revision'],0)
        self.db.execute('DELETE FROM assignments WHERE user_id=1')
        with self.assertRaises(PermissionError):state.consultar(self.db,TEACHER,self.blue)

    def test_identidade_ou_adjudicacao_ausente(self):
        with self.assertRaises(PermissionError):state.consultar(self.db,BLUE,'inexistente')
        self.db.execute("UPDATE party_allocations SET active=0 WHERE team='AZUL'")
        with self.assertRaises(PermissionError):state.consultar(self.db,BLUE,self.blue)

    def test_schema_ausente_nao_e_estado_vazio(self):
        with sqlite3.connect(':memory:') as db:
            seed(db);db.execute('PRAGMA foreign_keys=ON')
            uid=engine_units.list_units(db,TEACHER)['units'][0]['unit_id']
            with self.assertRaises(sqlite3.DatabaseError):state.consultar(db,TEACHER,uid)


class ValidationTests(unittest.TestCase):
    def test_faixas_somente_superficie(self):
        for index, expected in [(0,'flutuar'),(39.999,'flutuar'),(40,'navegar'),
                (59.999,'navegar'),(60,'navegar'),(60.001,'combater'),(80,'combater'),(100,'combater')]:
            with self.subTest(index=index):
                self.assertEqual(state.classificar('superficie', index), expected)
                for domain in ('aereo','submarino','terrestre',None):
                    self.assertIsNone(state.classificar(domain,index))
        self.assertIsNone(state.classificar('superficie',None))

    def test_indice_invalido(self):
        for value in (True,False,-1,101,math.nan,math.inf,-math.inf,'80',{},[]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                state.validar_alteracoes({'index_percent':value})

    def test_alteracao_explicita_e_ausencia(self):
        self.assertEqual(state.validar_alteracoes({'index_percent':None}),{'index_percent':None})
        self.assertEqual(state.validar_alteracoes({'lost':False}),{'lost':False})
        for value in ({},{'lost':1},{'lost':None},{'index_percent':80,'role':'instructor'}):
            with self.subTest(value=value),self.assertRaises(ValueError):state.validar_alteracoes(value)

    def test_evidencia_publica_preserva_contrato(self):
        with sqlite3.connect(':memory:') as db:
            db.row_factory=sqlite3.Row;seed(db)
            unit=engine_units.list_units(db,TEACHER)['units'][0]
            self.assertEqual(engine_units.configuration_domain(db,unit)['domain'],'aereo')
            unit['snapshot']['model_id']='inventado'
            self.assertIsNone(engine_units.configuration_domain(db,unit))


if __name__=='__main__':unittest.main()
