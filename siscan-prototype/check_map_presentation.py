"""Assets do mapa seguem a autenticação e os MIME types corretos."""
import unittest
from http.client import HTTPConnection
import app
from check_map_groups_http import sandbox

class InterfaceAssetsTests(unittest.TestCase):
    def test_assets_protegidos_com_mime_sem_cache(self):
        with sandbox() as env:
            for path,mime in [('/map-interface.css','text/css'),('/map-presentation.mjs','text/javascript')]:
                for user in (None,1,2,3):
                    with self.subTest(path=path,user=user):
                        conn=HTTPConnection('127.0.0.1',env.port,timeout=5)
                        try:
                            headers={'Cookie':f'{app.COOKIE_NAME}=map-test-{user}'} if user else {}
                            conn.request('GET',path,headers=headers)
                            response=conn.getresponse();body=response.read()
                            self.assertEqual(response.status,200 if user else 401)
                            if user:
                                self.assertTrue(response.getheader('Content-Type').startswith(mime))
                                self.assertEqual(response.getheader('Cache-Control'),'no-store')
                                self.assertTrue(body)
                        finally:conn.close()

if __name__=='__main__':unittest.main()
