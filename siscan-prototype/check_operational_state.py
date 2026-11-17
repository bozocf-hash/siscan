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


def decision(result,action='reject'):
    return dict(command_id=str(uuid.uuid4()),proposal_id=result['proposal_id'],expected_revision=result['revision'],
                expected_sha256=result['body_sha256'],action=action,reason='Decisão do instrutor')


class ConfirmationTests(unittest.TestCase):
    setUp=lambda self:ReadTests.setUp(self)

    def confirm(self,body=None):
        result=state.registrar_proposta(self.db,TEACHER,body or proposal(self.db))
        command=decision(result,'confirm')
        return state.decidir_proposta(self.db,TEACHER,command),command

    def test_confirma_lote_e_replay(self):
        result,command=self.confirm()
        self.assertEqual(result['action'],'confirm');self.assertEqual(len(result['effects']),2)
        before=list(self.db.iterdump());self.assertEqual(result,state.decidir_proposta(self.db,TEACHER,command))
        self.assertEqual(list(self.db.iterdump()),before)
        for u in self.units:
            current=state.consultar(self.db,TEACHER,u['unit_id']);self.assertEqual(current['state']['index_percent'],80)
            self.assertEqual(current['state']['revision'],1);self.assertIsNone(current['condition'])

    def test_perda_independente_e_correcao_referenciada(self):
        first,_=self.confirm(proposal(self.db,{'index_percent':0,'lost':True}))
        self.assertTrue(state.consultar(self.db,TEACHER,self.blue)['state']['lost'])
        second,_=self.confirm(proposal(self.db,{'index_percent':90}))
        self.assertTrue(state.consultar(self.db,TEACHER,self.blue)['state']['lost'])
        self.assertIsNone(state.consultar(self.db,TEACHER,self.blue)['condition'])
        body=proposal(self.db,{'lost':False})
        with self.assertRaises(state.Conflict):self.confirm(body)
        body=proposal(self.db,{'lost':False});body['correction_decision_id']=second['decision_id']
        self.confirm(body)
        self.assertFalse(state.consultar(self.db,TEACHER,self.blue)['state']['lost'])
        self.assertEqual(len(state.historico(self.db,TEACHER,self.blue)),3)

    def test_retirar_avaliacao_e_preservar_campo_omitido(self):
        self.confirm();self.confirm(proposal(self.db,{'index_percent':None}))
        current=state.consultar(self.db,TEACHER,self.blue)['state']
        self.assertIsNone(current['index_percent']);self.assertIsNone(current['lost'])

    def test_rollback_entre_integrantes(self):
        first=state.registrar_proposta(self.db,TEACHER,proposal(self.db));before=list(self.db.iterdump())
        self.db.execute("""CREATE TRIGGER fail_second_effect BEFORE INSERT ON operational_effects
          WHEN (SELECT count(*) FROM operational_effects)>0 BEGIN SELECT RAISE(ABORT,'falha'); END""")
        self.db.commit()
        with self.assertRaises(sqlite3.IntegrityError):state.decidir_proposta(self.db,TEACHER,decision(first,'confirm'))
        self.db.execute('DROP TRIGGER fail_second_effect');self.db.commit()
        self.assertEqual(list(self.db.iterdump()),before)

    def test_reconferencia_adjudicacao_e_cenario(self):
        first=state.registrar_proposta(self.db,TEACHER,proposal(self.db))
        self.db.execute("UPDATE party_allocations SET active=0 WHERE team='AZUL'");self.db.commit()
        with self.assertRaises(PermissionError):state.decidir_proposta(self.db,TEACHER,decision(first,'confirm'))
        self.db.execute('UPDATE party_allocations SET active=1');self.db.execute("UPDATE exercises SET scenario_version=2");self.db.commit()
        with self.assertRaises(state.Conflict):state.decidir_proposta(self.db,TEACHER,decision(first,'confirm'))
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_decisions').fetchone()[0],0)

    def test_nao_interfere_no_resto_do_banco(self):
        before=[s for s in self.db.iterdump() if s.startswith('INSERT INTO') and '"operational_' not in s]
        self.confirm()
        self.assertEqual(before,[s for s in self.db.iterdump() if s.startswith('INSERT INTO') and '"operational_' not in s])

    def test_historico_do_operador_nao_contem_motivo_privado(self):
        self.confirm()
        self.assertNotIn('reason',state.historico(self.db,BLUE,self.blue)[0])
        self.assertIn('reason',state.historico(self.db,TEACHER,self.blue)[0])
        with self.assertRaises(PermissionError):state.historico(self.db,BLUE,self.red)

    def test_faixas_confirmadas_com_provedor_controlado_de_superficie(self):
        evidence=dict(domain='superficie',basis='fixture_only',reference='teste')
        with patch.object(engine_units,'configuration_domain',return_value=evidence):
            self.confirm(proposal(self.db,{'index_percent':60}))
            self.assertEqual(state.consultar(self.db,TEACHER,self.blue)['condition'],'navegar')
        self.assertEqual(state.consultar(self.db,TEACHER,self.blue)['state']['domain'],'superficie')


class RevisionTests(unittest.TestCase):
    setUp=lambda self:ReadTests.setUp(self)

    def test_revisao_cria_versao_e_rejeicao_terminal_sem_efeito(self):
        first=state.registrar_proposta(self.db,TEACHER,proposal(self.db))
        edit=dict(proposal(self.db),proposal_id=first['proposal_id'],expected_revision=1,expected_sha256=first['body_sha256'])
        edit['effects'][0]['changes']={'index_percent':40}
        second=state.revisar_proposta(self.db,TEACHER,edit)
        self.assertEqual(second,state.revisar_proposta(self.db,TEACHER,edit));self.assertEqual(second['revision'],2)
        with self.assertRaises(state.Conflict):state.decidir_proposta(self.db,TEACHER,decision(first))
        command=decision(second);result=state.decidir_proposta(self.db,TEACHER,command)
        self.assertEqual(result['action'],'reject');self.assertEqual(result,state.decidir_proposta(self.db,TEACHER,command))
        self.assertEqual(self.db.execute('SELECT count(*) FROM operational_effects').fetchone()[0],0)
        with self.assertRaises(state.Conflict):state.revisar_proposta(self.db,TEACHER,dict(edit,command_id=str(uuid.uuid4())))
        with self.assertRaises(state.Conflict):state.decidir_proposta(self.db,TEACHER,decision(second))

    def test_operador_nao_revisa_ou_rejeita(self):
        first=state.registrar_proposta(self.db,TEACHER,proposal(self.db))
        for operation,payload in [(state.decidir_proposta,decision(first)),(state.revisar_proposta,dict(
                proposal(self.db),proposal_id=first['proposal_id'],expected_revision=1,expected_sha256=first['body_sha256']))]:
            with self.assertRaises(PermissionError):operation(self.db,BLUE,payload)

    def test_hash_e_payload_invalidos(self):
        first=state.registrar_proposta(self.db,TEACHER,proposal(self.db))
        for bad in (dict(decision(first),expected_sha256='x'),dict(decision(first),expected_revision=True)):
            with self.assertRaises((ValueError,state.Conflict)):state.decidir_proposta(self.db,TEACHER,bad)

    def test_rejeicao_falha_reverte_decisao(self):
        first=state.registrar_proposta(self.db,TEACHER,proposal(self.db));before=list(self.db.iterdump())
        with patch.object(state,'_receipt',side_effect=RuntimeError('falha')):
            with self.assertRaises(RuntimeError):state.decidir_proposta(self.db,TEACHER,decision(first))
        self.assertEqual(list(self.db.iterdump()),before)


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
        for value in (True,False,-1,101,10**400,math.nan,math.inf,-math.inf,'80',{},[]):
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
            evidence=engine_units.configuration_domain(db,unit)
            self.assertEqual(evidence['domain'],'aereo')
            self.assertTrue(evidence['reference'].startswith('engine_units.prepare_units/'))
            unit['snapshot']['model_id']='inventado'
            self.assertIsNone(engine_units.configuration_domain(db,unit))


if __name__=='__main__':unittest.main()
