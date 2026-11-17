"""Rotas reais com sessão/CSRF, banco temporário e porta livre."""
from contextlib import closing, contextmanager
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
from threading import Thread
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

import app
from check_map_groups import seed


@contextmanager
def database(path):
    with closing(sqlite3.connect(path)) as db:
        with db:
            yield db


@contextmanager
def sandbox(with_map=False):
    with TemporaryDirectory(prefix='siscan-map-groups-') as temp:
        data = Path(temp)
        db_path = data / 'test.sqlite3'
        with database(db_path) as db:
            seed(db)
            for uid in (1, 2, 3):
                token = 'map-test-' + str(uid)
                db.execute('INSERT INTO sessions VALUES(?,?,?,?)',
                           (hashlib.sha256(token.encode()).hexdigest(), uid, 'csrf-test', int(time.time()) + 3600))
                salt, hashed = app.password_record('somente-teste-local')
                db.execute('UPDATE users SET salt=?,password_hash=? WHERE id=?', (salt, hashed, uid))
            if with_map:
                for row in db.execute('SELECT asset_id,team FROM engine_units').fetchall():
                    db.execute('INSERT INTO map_unit_positions VALUES(?,?,?,1,1)',
                               (row[0], -22.7, -43.1 if row[1] == 'AZUL' else -42.9))
        if with_map:
            shutil.copytree(app.DATA_DIR / 'atlanticador', data / 'atlanticador')
        class QuietHandler(app.Handler):
            def log_message(self, *args):
                pass
        original_connect = app.connect
        @contextmanager
        def isolated_connect():
            with closing(original_connect()) as db:
                with db:
                    yield db
        with patch.object(app, 'DATA_DIR', data), patch.object(app, 'DB_PATH', db_path), \
                patch.object(app, 'connect', isolated_connect), \
                patch.object(app, 'COOKIE_NAME', 'siscan_map_groups_test_' + data.name):
            server = app.SiscanServer(('127.0.0.1', 0), QuietHandler)
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                yield SimpleNamespace(server=server, db_path=db_path, data=data,
                                      port=server.server_address[1], url=f'http://127.0.0.1:{server.server_address[1]}')
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=3)


def request(env, path, *, user=2, body=None, csrf=True):
    headers = {}
    if user:
        headers['Cookie'] = f'{app.COOKIE_NAME}=map-test-{user}'
    if csrf:
        headers['X-CSRF-Token'] = 'csrf-test'
    if body is not None:
        headers['Content-Type'] = 'application/json'
    conn = HTTPConnection('127.0.0.1', env.port, timeout=5)
    try:
        conn.request('POST' if body is not None else 'GET', path,
                     json.dumps(body) if body is not None else None, headers)
        response = conn.getresponse()
        return response.status, json.loads(response.read())
    finally:
        conn.close()


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.manager = sandbox()
        self.env = self.manager.__enter__()
        self.addCleanup(self.manager.__exit__, None, None, None)

    def listing(self, **kwargs):
        return request(self.env, '/api/map-unit-groups?team=AZUL', **kwargs)

    def create_body(self):
        status, view = self.listing()
        self.assertEqual(status, 200)
        return dict(team='AZUL', command_id=str(uuid.uuid4()), designation='Grupo <teste>',
                    domain='aereo', member_unit_ids=[u['unit_id'] for u in view['units'] if u['eligible']])

    def create(self, body=None, **kwargs):
        return request(self.env, '/api/map-unit-groups', body=body or self.create_body(), **kwargs)

    def test_autenticacao_partido_e_csrf(self):
        self.assertTrue(app.COOKIE_NAME.startswith('siscan_map_groups_test_'))
        self.assertEqual(self.listing(user=None)[0], 401)
        self.assertEqual(self.listing(user=3)[0], 403)
        self.assertEqual(self.listing(user=1)[0], 200)
        self.assertEqual(self.create(csrf=False)[0], 403)
        self.assertEqual(self.create(user=3)[0], 403)
        self.assertEqual(request(self.env, '/api/map-unit-groups?team=AZUL&extra=1')[0], 400)

    def test_criar_reenviar_conflitar_arquivar_sem_escrita_sql(self):
        body = self.create_body()
        with database(self.env.db_path) as db:
            before = list(db.iterdump())
        status, result = self.create(body)
        self.assertEqual(status, 200)
        self.assertEqual(result['storage'], 'memory')
        group = result['group']
        self.assertEqual(len(group['members']), 1)
        self.assertNotIn('snapshot', json.dumps(group))
        self.assertEqual(self.create(body)[1]['group']['group_id'], group['group_id'])
        self.assertEqual(self.create(dict(body, designation='Outra intenção'))[0], 409)
        archive = dict(team='AZUL', command_id=str(uuid.uuid4()), expected_revision=1)
        path = '/api/map-unit-groups/' + group['group_id'] + '/archive'
        self.assertEqual(request(self.env, path, body=dict(archive, expected_revision=2))[0], 409)
        self.assertEqual(request(self.env, path, body=archive)[1]['group']['active'], False)
        self.assertEqual(request(self.env, path, body=archive)[0], 200)
        self.assertEqual(len(self.listing()[1]['groups']), 1)
        self.assertEqual(self.create(dict(body, command_id=str(uuid.uuid4())))[0], 200)
        with database(self.env.db_path) as db:
            self.assertEqual(list(db.iterdump()), before)

    def test_revogacao_mascara_membros_inclusive_no_recibo(self):
        body = self.create_body()
        group = self.create(body)[1]['group']
        uid = body['member_unit_ids'][0]
        with database(self.env.db_path) as db:
            db.execute("UPDATE party_allocations SET active=0 WHERE team='AZUL'")
        result = self.listing()[1]
        self.assertEqual(result['units'], [])
        self.assertNotIn(uid, json.dumps(result))
        self.assertEqual(result['groups'][0]['unavailable_count'], 1)
        replay = self.create(body)[1]
        self.assertNotIn(uid, json.dumps(replay))
        self.assertEqual(replay['group']['group_id'], group['group_id'])

    def test_exercicio_encerrado_so_leitura(self):
        body = self.create_body()
        with database(self.env.db_path) as db:
            db.execute("UPDATE exercises SET state='closed'")
        self.assertEqual(self.create(body)[0], 400)
        self.assertFalse(self.listing()[1]['exercise_open'])

    def test_campos_extras_ou_unidade_nao_elegivel(self):
        body = self.create_body()
        self.assertEqual(self.create(dict(body, snapshot={}))[0], 400)
        self.assertEqual(self.create(dict(body, member_unit_ids=['desconhecido']))[0], 403)
        self.assertEqual(request(self.env, '/api/map-unit-groups/invalido/archive',
                                body=dict(team='AZUL', command_id=str(uuid.uuid4()), expected_revision=1))[0], 400)

    def test_publicacao_unica_concorrente(self):
        from concurrent.futures import ThreadPoolExecutor
        body = self.create_body()
        other = dict(body, command_id=str(uuid.uuid4()))
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda b: self.create(b)[0], (body, other)))
        self.assertEqual(sorted(statuses), [200, 409])
        self.assertEqual(len(self.listing()[1]['groups']), 1)

    def test_registro_e_por_servidor(self):
        from unit_groups import RegistroGrupamentos
        self.create()
        self.env.server.unit_group_registry = RegistroGrupamentos()
        self.assertEqual(self.listing()[1]['groups'], [])


if __name__ == '__main__':
    import sys
    if '--serve' in sys.argv:
        with sandbox(with_map=True) as env:
            print(json.dumps(dict(url=env.url, database=str(env.db_path))), flush=True)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
    else:
        unittest.main()
