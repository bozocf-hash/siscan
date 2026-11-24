"""Caminho HTTP real de adjudicação e composição com sessão/CSRF."""
import unittest,uuid
from unittest.mock import patch
from check_map_groups_http import sandbox,request

class PlanningHTTPTests(unittest.TestCase):
    def test_http_isolamento_csrf_reenvio_e_grupo(self):
        source=dict(source=dict(sha256='a'*64),fields=dict(ID=1351,Name='Fonte naval de teste'))
        body=dict(command_id=str(uuid.uuid4()),table='DataShip',id='1351',team='AZUL',quantity=2)
        with sandbox() as env,patch('planning_catalog.source_catalog.detail',return_value=source):
            def call(path,body=None,user=1,csrf=True):
                return request(env,path,user=user,body=body,csrf=csrf)
            status,created=call('/api/planning-catalog/allocate',body)
            self.assertEqual(status,200)
            self.assertEqual(call('/api/planning-catalog/allocate',body)[1],created)
            self.assertEqual(call('/api/planning-catalog/allocate',body,user=2)[0],403)
            self.assertEqual(call('/api/planning-catalog/allocate',body,csrf=False)[0],403)
            self.assertEqual(call('/api/planning-catalog/allocate',dict(body,quantity=3))[0],409)
            status,view=call('/api/map-unit-groups?team=AZUL',user=2)
            self.assertEqual(status,200)
            units=[u for u in view['units'] if u['asset_id'] in created['asset_ids']]
            self.assertEqual(len(units),2);self.assertTrue(all(u['eligible'] for u in units))

if __name__=='__main__':unittest.main()
