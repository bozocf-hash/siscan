"""API de prontidão com sessão/CSRF e banco descartável."""
import unittest
import sqlite3
from check_map_groups_http import sandbox,database,request
from check_cpc_map import seed_pairs
from check_map_groups import TEACHER
import operational_state_storage as storage
import cpc_judgment
from check_cpc_readiness import full_profile

class ReadinessHttpTests(unittest.TestCase):
 def setUp(self):
  self.manager=sandbox();self.env=self.manager.__enter__();self.addCleanup(self.manager.__exit__,None,None,None)
  with database(self.env.db_path) as db:
   db.execute('PRAGMA foreign_keys=ON');storage.migrate(db);selection=seed_pairs(db,self.env.server.unit_group_registry)
   db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
   base=cpc_judgment.context(db,TEACHER,self.env.server.unit_group_registry,dict(selection=selection))
   self.body=dict(selection=selection,expected_view_sha256=base['preparation']['view_sha256'])
 def post(self,**kwargs):return request(self.env,'/api/cpc/trial-readiness',body=self.body,user=kwargs.pop('user',1),**kwargs)
 def test_sessao_csrf_e_papel(self):
  self.assertEqual(self.post(user=None)[0],401)
  self.assertEqual(self.post(user=2)[0],403)
  self.assertEqual(self.post(user=3)[0],403)
  self.assertEqual(self.post(csrf=False)[0],403)
 def test_diagnostico_negativo_sem_escritas(self):
  with database(self.env.db_path) as db:before=list(db.iterdump())
  status,result=self.post();self.assertEqual(status,200);self.assertFalse(result['ready_for_controlled_trial'])
  self.assertEqual(len(result['units']),2)
  self.assertNotIn('snapshot',result)
  self.assertEqual(self.post()[1],result)
  with database(self.env.db_path) as db:self.assertEqual(list(db.iterdump()),before)
 def test_conflito_formato_e_schema_ausente(self):
  self.assertEqual(request(self.env,'/api/cpc/trial-readiness?extra=1',user=1,body=self.body)[0],400)
  self.assertEqual(request(self.env,'/api/cpc/trial-readiness',user=1,body=dict(self.body,extra=1))[0],400)
  self.assertEqual(request(self.env,'/api/cpc/trial-readiness',user=1,body=dict(self.body,expected_view_sha256='0'*64))[0],409)
  with database(self.env.db_path) as db:db.execute('DROP TRIGGER operational_commands_no_update')
  self.assertEqual(self.post()[0],503)

 def test_perfil_completo_por_http_preserva_dados(self):
  with database(self.env.db_path) as db:
   db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
   base=cpc_judgment.context(db,TEACHER,self.env.server.unit_group_registry,dict(selection=self.body['selection']));before=list(db.iterdump())
  body=dict(self.body,hypotheses=full_profile(base));status,result=request(self.env,'/api/cpc/trial-readiness',user=1,body=body)
  self.assertEqual(status,200);self.assertTrue(result['ready_for_controlled_trial']);self.assertFalse(result['official_effects_applied'])
  with database(self.env.db_path) as db:self.assertEqual(list(db.iterdump()),before)

if __name__=='__main__':unittest.main()
