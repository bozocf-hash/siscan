"""HTTP do julgamento e harness persistente exclusivamente de teste."""
import sqlite3
import unittest
import uuid
from contextlib import contextmanager,closing
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread,Event
from types import SimpleNamespace
from unittest.mock import patch
import json
import shutil
import app
from check_map_groups_http import sandbox,database,request
from check_cpc_map import seed_pairs
import operational_state_storage as storage
from check_map_groups import seed


@contextmanager
def persistent_server(folder,port=0):
    folder=Path(folder).resolve();marker=folder/'harness.json';database_path=folder/'test.sqlite3'
    kind='siscan-cpc-judgment-test-01'
    first=not marker.exists()
    if folder==app.DATA_DIR.resolve() or database_path==app.DB_PATH.resolve():raise ValueError('Base principal recusada.')
    if first and folder.exists() and any(folder.iterdir()):raise ValueError('Pasta não pertence ao harness.')
    if first:
        folder.mkdir(parents=True,exist_ok=True)
        with closing(sqlite3.connect(database_path)) as db:
            db.execute('PRAGMA foreign_keys=ON');seed(db);storage.migrate(db)
            for uid in (1,2,3):
                salt,hashed=app.password_record('somente-teste-local')
                db.execute('UPDATE users SET salt=?,password_hash=? WHERE id=?',(salt,hashed,uid))
            for aid,team in db.execute('SELECT asset_id,team FROM engine_units').fetchall():
                db.execute('INSERT INTO map_unit_positions VALUES(?,?,?,1,1)',(aid,-22.7,-43.1 if team=='AZUL' else -42.9))
            db.commit()
        shutil.copytree(app.DATA_DIR/'atlanticador',folder/'atlanticador')
        metadata=dict(kind=kind,cookie='siscan_judgment_test_'+uuid.uuid4().hex)
        marker.write_text(json.dumps(metadata),encoding='utf-8')
    else:
        metadata=json.loads(marker.read_text(encoding='utf-8'))
        if metadata.get('kind')!=kind or not database_path.is_file():raise ValueError('Harness incompatível.')
        with closing(sqlite3.connect(database_path)) as db:
            db.execute('PRAGMA foreign_keys=ON');storage.migrate(db)
            if db.execute('SELECT code FROM exercises ORDER BY id LIMIT 1').fetchone()!=('TEST',):raise ValueError('Exercício não é de teste.')
    class Quiet(app.Handler):
        def log_message(self,*args):pass
    original_connect=app.connect
    @contextmanager
    def isolated_connect():
        with closing(original_connect()) as db:
            with db:yield db
    with patch.object(app,'DATA_DIR',folder),patch.object(app,'DB_PATH',database_path),\
            patch.object(app,'COOKIE_NAME',metadata['cookie']),patch.object(app,'connect',isolated_connect):
        server=app.SiscanServer(('127.0.0.1',port),Quiet)
        if first:
            with closing(sqlite3.connect(database_path)) as db:
                db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');seed_pairs(db,server.unit_group_registry)
        worker=Thread(target=server.serve_forever,daemon=True);worker.start()
        try:yield SimpleNamespace(server=server,url='http://localhost:'+str(server.server_address[1]),db_path=database_path)
        finally:server.shutdown();server.server_close();worker.join(5)


class HarnessTests(unittest.TestCase):
    def test_reabrir_preserva_base_sem_reconstruir_grupos(self):
        with TemporaryDirectory() as folder:
            with persistent_server(folder) as env:
                with closing(sqlite3.connect(env.db_path)) as db:before=list(db.iterdump())
                self.assertTrue(env.server.unit_group_registry.listar_grupamentos(dict(exercise_id=1,team='AZUL')))
            with persistent_server(folder) as env:
                with closing(sqlite3.connect(env.db_path)) as db:self.assertEqual(list(db.iterdump()),before)
                self.assertFalse(env.server.unit_group_registry.listar_grupamentos(dict(exercise_id=1,team='AZUL')))

    def test_pasta_alheia_recusada_sem_escrita(self):
        with TemporaryDirectory() as folder:
            file=Path(folder)/'arquivo.txt';file.write_text('Preservar',encoding='utf-8')
            with self.assertRaises(ValueError):
                with persistent_server(folder):pass
            self.assertEqual([p.name for p in Path(folder).iterdir()],['arquivo.txt'])


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


if __name__=='__main__':
    import sys,argparse
    if '--serve' in sys.argv:
        parser=argparse.ArgumentParser();parser.add_argument('--serve',action='store_true')
        parser.add_argument('--data-dir',required=True);parser.add_argument('--port',type=int,default=0)
        options=parser.parse_args()
        with persistent_server(options.data_dir,options.port) as env:
            print(json.dumps(dict(url=env.url,database=str(env.db_path))),flush=True)
            try:Event().wait()
            except KeyboardInterrupt:pass
    else:unittest.main()
