"""HTTP do julgamento e harness persistente exclusivamente de teste."""
import sqlite3
import unittest
import uuid
from check_map_groups_http import sandbox,database,request
from check_cpc_map import seed_pairs
import operational_state_storage as storage


class JudgmentHttpTests(unittest.TestCase):
    def setUp(self):
        self.manager=sandbox();self.env=self.manager.__enter__();self.addCleanup(self.manager.__exit__,None,None,None)
        with database(self.env.db_path) as db:
            db.execute('PRAGMA foreign_keys=ON');storage.migrate(db)
            self.selection=seed_pairs(db,self.env.server.unit_group_registry)

    def post(self,path,body):return request(self.env,path,user=1,body=body)

    def body(self):
        status,base=self.post('/api/cpc/judgments/context',dict(selection=self.selection));self.assertEqual(status,200)
        return dict(selection=self.selection,basis_sha256=base['basis_sha256'],reason='Julgamento HTTP',
            effects=[dict(unit_id=next(iter(base['states'])),changes={'index_percent':60})])

    def test_sessao_papel_csrf_e_formato(self):
        self.assertEqual(request(self.env,'/api/cpc/judgments',user=None)[0],401)
        self.assertEqual(request(self.env,'/api/cpc/judgments',user=2)[0],403)
        self.assertEqual(request(self.env,'/api/cpc/judgments/context',user=1,body={'selection':self.selection},csrf=False)[0],403)
        self.assertEqual(request(self.env,'/api/cpc/judgments?role=instructor',user=1)[0],400)

    def test_fluxo_completo_e_replay(self):
        body=self.body();self.assertEqual(self.post('/api/cpc/judgments/preview',body)[0],200)
        status,p=self.post('/api/cpc/judgments',dict(body,command_id=str(uuid.uuid4())));self.assertEqual(status,200)
        path='/api/cpc/judgments/'+p['proposal_id']
        self.assertTrue(request(self.env,path,user=1)[1]['available'])
        self.assertEqual(len(request(self.env,'/api/cpc/judgments',user=1)[1]['items']),1)
        command=dict(command_id=str(uuid.uuid4()),expected_revision=p['revision'],expected_sha256=p['body_sha256'],
                     action='confirm',reason='Confirmado')
        status,result=self.post(path+'/decisions',command);self.assertEqual(status,200)
        self.assertEqual(self.post(path+'/decisions',command)[1],result)
        self.assertEqual(request(self.env,path,user=1)[1]['decision']['action'],'confirm')

    def test_schema_ausente_e_caminho_invalido(self):
        with database(self.env.db_path) as db:db.execute('DROP TRIGGER operational_commands_no_update')
        self.assertEqual(request(self.env,'/api/cpc/judgments',user=1)[0],503)
        self.assertEqual(self.post('/api/cpc/judgments/context?inject=1',dict(selection=self.selection))[0],400)


if __name__=='__main__':unittest.main()
