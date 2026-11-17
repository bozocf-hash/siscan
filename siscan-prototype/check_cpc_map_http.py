"""HTTP CPC real em base/cookie/porta isolados."""
import sqlite3
import unittest
import uuid
from check_map_groups_http import sandbox, database, request
from check_cpc_map import seed_pairs


class CpcHttpTests(unittest.TestCase):
    def setUp(self):
        self.manager = sandbox()
        self.env = self.manager.__enter__()
        self.addCleanup(self.manager.__exit__, None, None, None)
        with database(self.env.db_path) as db:
            self.selection = seed_pairs(db, self.env.server.unit_group_registry)

    def prepare(self, **kwargs):
        return request(self.env, '/api/cpc/preparations', body=self.selection, user=1, **kwargs)

    def test_sessao_papel_e_csrf(self):
        self.assertEqual(request(self.env,'/api/cpc/groups',user=None)[0],401)
        self.assertEqual(request(self.env,'/api/cpc/groups',user=2)[0],403)
        self.assertEqual(request(self.env,'/api/cpc/preparations',body=self.selection,user=3)[0],403)
        self.assertEqual(self.prepare(csrf=False)[0],403)
        with database(self.env.db_path) as db: db.execute('DELETE FROM assignments WHERE user_id=1')
        self.assertEqual(request(self.env,'/api/cpc/groups',user=1)[0],403)

    def test_preparacao_repetida_sem_escrita_ou_execucao(self):
        with database(self.env.db_path) as db: before=list(db.iterdump())
        status, listing=request(self.env,'/api/cpc/groups',user=1)
        self.assertEqual(status,200);self.assertEqual(len(listing['parties']),2)
        status, result=self.prepare()
        self.assertEqual(status,200)
        self.assertEqual(result,self.prepare()[1])
        self.assertIs(result['official_effects_applied'],False)
        self.assertIs(result['simulation_started'],False)
        self.assertNotIn('input_template',str(result))
        with database(self.env.db_path) as db: self.assertEqual(list(db.iterdump()),before)

    def test_formato_contexto_e_query_nao_injetaveis(self):
        self.assertEqual(request(self.env,'/api/cpc/groups?team=AZUL',user=1)[0],400)
        for value in ({},dict(self.selection,exercise_id=1),dict(self.selection,autorizar_instrutor=True)):
            self.assertEqual(request(self.env,'/api/cpc/preparations',user=1,body=value)[0],400)

    def test_fechamento_e_consulta(self):
        with database(self.env.db_path) as db: db.execute("UPDATE exercises SET state='closed'")
        self.assertFalse(request(self.env,'/api/cpc/groups',user=1)[1]['exercise_open'])
        self.assertEqual(self.prepare()[0],400)

    def test_arquivo_e_grupo_ausente(self):
        self.env.server.unit_group_registry.arquivar_grupamento(dict(exercise_id=1,team='AZUL'),
            dict(command_id=str(uuid.uuid4()),**self.selection['AZUL']))
        self.assertEqual(self.prepare()[0],409)
        other=dict(self.selection,AZUL=dict(group_id=str(uuid.uuid4()),expected_revision=1))
        self.assertEqual(request(self.env,'/api/cpc/preparations',user=1,body=other)[0],404)

    def test_integridade_indisponivel_nao_e_lista_vazia(self):
        with database(self.env.db_path) as db:
            db.execute('DROP TRIGGER engine_snapshot_no_update')
            db.execute("UPDATE engine_unit_snapshots SET snapshot_json='{}' WHERE team='AZUL'")
        self.assertEqual(self.prepare()[0],503)
        self.assertEqual(request(self.env,'/api/cpc/groups',user=1)[0],503)


if __name__=='__main__':
    import sys, json, time
    if '--serve' in sys.argv:
        with sandbox(with_map=True) as env:
            with database(env.db_path) as db:
                seed_pairs(db, env.server.unit_group_registry)
            print(json.dumps(dict(url=env.url,database=str(env.db_path))),flush=True)
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                pass
    else:
        unittest.main()
