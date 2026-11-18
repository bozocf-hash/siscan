"""Sessão/CSRF e ausência de efeitos na execução sintética HTTP."""
import unittest
from types import SimpleNamespace
import check_cpc_readiness_http as fixture
import check_cpc_controlled_trial as domain
from check_map_groups_http import database,request


class ControlledTrialHttpTests(unittest.TestCase):
    setUp=fixture.ReadinessHttpTests.setUp

    def payload(self):
        # Build the profile against this HTTP fixture's own UUIDs/context.
        import sqlite3,cpc_judgment
        from check_map_groups import TEACHER
        with database(self.env.db_path) as db:
            db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
            base=cpc_judgment.context(db,TEACHER,self.env.server.unit_group_registry,dict(selection=self.body['selection']))
        return domain.ControlledTrialTests.request_body(SimpleNamespace(base=base,body=self.body))

    def post(self,body,user=1,**kwargs):
        return request(self.env,'/api/cpc/controlled-trial',user=user,body=body,**kwargs)

    def test_auth_csrf_role_e_revogacao(self):
        body=self.payload()
        for user,status in [(None,401),(2,403),(3,403)]:self.assertEqual(self.post(body,user=user)[0],status)
        self.assertEqual(self.post(body,csrf=False)[0],403)
        with database(self.env.db_path) as db:db.execute('DELETE FROM assignments WHERE user_id=1')
        self.assertEqual(self.post(body)[0],403)

    def test_execucao_completa_preserva_banco_e_repete_resultados(self):
        body=self.payload()
        with database(self.env.db_path) as db:before=list(db.iterdump())
        status,result=self.post(body);self.assertEqual(status,200)
        self.assertEqual(result['minutes_completed'],60);self.assertFalse(result['official_effects_applied'])
        self.assertEqual(self.post(body)[1]['final'],result['final'])
        with database(self.env.db_path) as db:self.assertEqual(before,list(db.iterdump()))

    def test_formato_limites_conflito_e_indisponibilidade(self):
        body=self.payload()
        self.assertEqual(request(self.env,'/api/cpc/controlled-trial?x=1',user=1,body=body)[0],400)
        self.assertEqual(self.post(dict(body,extra=1))[0],400)
        self.assertEqual(self.post(dict(body,expected_basis_sha256='0'*64))[0],409)
        self.assertEqual(self.post(dict(body,hypotheses={'label':'x'*64001}))[0],400)
        with database(self.env.db_path) as db:db.execute('DROP TRIGGER operational_commands_no_update')
        self.assertEqual(self.post(body)[0],503)


if __name__=='__main__':unittest.main()
