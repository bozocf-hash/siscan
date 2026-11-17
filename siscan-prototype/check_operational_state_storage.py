"""Migração, concorrência e recuperação em bancos descartáveis."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import uuid
import json
import hashlib
import subprocess
import sys

from check_map_groups import seed,TEACHER
import operational_state_storage as store
import operational_state as state
from check_operational_state import proposal,decision


class RecoveryTests(unittest.TestCase):
    setUp=lambda self:TransactionTests.setUp(self)
    connect=lambda self:TransactionTests.connect(self)

    def confirmed(self):
        with self.connect() as db:
            p=state.registrar_proposta(db,TEACHER,proposal(db));command=decision(p,'confirm')
            result=state.decidir_proposta(db,TEACHER,command)
            uid=result['effects'][0]['unit_id']
            return uid,state.consultar(db,TEACHER,uid),command,result

    def test_processo_novo_recupera_estado_historico_e_recibo(self):
        uid,current,command,result=self.confirmed()
        code='''import sqlite3,json,sys
import operational_state as s
db=sqlite3.connect(sys.argv[1]);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
user=dict(uid=1,role='instructor',team=None)
command=json.loads(db.execute("SELECT payload_json FROM operational_commands WHERE operation='decide'").fetchone()[0])
print(json.dumps(dict(current=s.consultar(db,user,sys.argv[2]),history=s.historico(db,user,sys.argv[2]),receipt=s.decidir_proposta(db,user,command))))
db.close()
'''
        child=subprocess.run([sys.executable,'-c',code,str(self.path),uid],cwd=Path(__file__).parent,
                             capture_output=True,text=True,timeout=30,check=True)
        recovered=json.loads(child.stdout)
        self.assertEqual(recovered['current'],current);self.assertEqual(recovered['receipt'],result)
        self.assertEqual(len(recovered['history']),1)

    def test_backup_restauracao_em_terceiro_arquivo(self):
        uid,current,command,result=self.confirmed()
        backup=Path(self.temp.name)/'backup.sqlite3';restored=Path(self.temp.name)/'restored.sqlite3'
        with self.connect() as source,closing(sqlite3.connect(backup)) as target:source.backup(target)
        with closing(sqlite3.connect(backup)) as source,closing(sqlite3.connect(restored)) as target:source.backup(target)
        with closing(sqlite3.connect(restored)) as db:
            db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertFalse(db.execute('PRAGMA foreign_key_check').fetchall())
            self.assertEqual(state.consultar(db,TEACHER,uid),current)
            self.assertEqual(state.decidir_proposta(db,TEACHER,command),result)

    def corrupt(self,db,table,column,value,sha_column=None):
        trigger='operational_'+table+'_no_update'
        db.execute('DROP TRIGGER '+trigger)
        values=[value]
        sql='UPDATE operational_'+table+' SET '+column+'=?'
        if sha_column:
            sql+=','+sha_column+'=?';values.append(hashlib.sha256(value.encode('utf-8')).hexdigest())
        sql+=' WHERE rowid=(SELECT min(rowid) FROM operational_'+table+')'
        db.execute(sql,values)
        db.execute(next(s for s in store.STATEMENTS if s.startswith('CREATE TRIGGER '+trigger+' ')));db.commit()

    def test_corrupcao_semantica_com_hash_recalculado_recusa(self):
        uid,current,command,result=self.confirmed()
        cases=[('effects','before_json','before_sha256','index_percent',45),
               ('effects','after_json','after_sha256','index_percent',20),
               ('effects','after_json','after_sha256','lost','sim'),
               ('effects','refs_json','refs_sha256','configuration_version_id','inexistente')]
        for table,column,sha,key,value in cases:
            with self.subTest(column=column,key=key),self.connect() as source,closing(sqlite3.connect(':memory:')) as db:
                source.backup(db);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
                obj=json.loads(db.execute('SELECT '+column+' FROM operational_'+table+' ORDER BY rowid LIMIT 1').fetchone()[0]);obj[key]=value
                self.corrupt(db,table,column,json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')),sha)
                with self.assertRaises(sqlite3.DatabaseError):state.consultar(db,TEACHER,uid)

    def test_corrupcao_proposta_e_recibo_e_detectada_na_leitura(self):
        uid,current,command,result=self.confirmed()
        for table,column in [('proposal_revisions','body_json'),('commands','result_json')]:
            with self.subTest(table=table),self.connect() as source,closing(sqlite3.connect(':memory:')) as db:
                source.backup(db);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
                # Escolher o recibo da decisão, não o de registro da proposta.
                if table=='commands':
                    db.execute('DROP TRIGGER operational_commands_no_update')
                    db.execute("UPDATE operational_commands SET result_json='{}' WHERE operation='decide'")
                    db.execute(next(s for s in store.STATEMENTS if s.startswith('CREATE TRIGGER operational_commands_no_update ')));db.commit()
                else:self.corrupt(db,table,column,'{}')
                with self.assertRaises(sqlite3.DatabaseError):state.consultar(db,TEACHER,uid)

    def test_elo_removido_nao_vira_estado_nao_avaliado(self):
        uid,current,command,result=self.confirmed()
        with self.connect() as db:
            db.execute('DROP TRIGGER operational_effects_no_delete')
            db.execute('DELETE FROM operational_effects WHERE unit_id=?',(uid,))
            db.execute(next(s for s in store.STATEMENTS if s.startswith('CREATE TRIGGER operational_effects_no_delete ')));db.commit()
            with self.assertRaises(sqlite3.DatabaseError):state.consultar(db,TEACHER,uid)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='siscan-operational-');self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'state.sqlite3'
        with self.connect() as db:seed(db);store.migrate(db)

    def connect(self):
        db=sqlite3.connect(self.path,timeout=10);db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON');return closing(db)

    def register(self):
        with self.connect() as db:return state.registrar_proposta(db,TEACHER,proposal(db))

    def race(self,commands):
        barrier=Barrier(2)
        def worker(command):
            with self.connect() as db:
                barrier.wait(timeout=15)
                try:return state.decidir_proposta(db,TEACHER,command)
                except state.Conflict:return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:return list(pool.map(worker,commands))

    def counts(self):
        with self.connect() as db:
            return tuple(db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in
                         ('operational_decisions','operational_effects'))

    def test_mesmo_comando_concorrente_retorna_mesmo_recibo(self):
        command=decision(self.register(),'confirm');results=self.race([command,command])
        self.assertEqual(results[0],results[1]);self.assertEqual(self.counts(),(1,2))

    def test_duas_decisoes_mesma_proposta_um_vencedor(self):
        p=self.register();results=self.race([decision(p,'confirm'),decision(p,'confirm')])
        self.assertEqual(results.count('conflict'),1);self.assertEqual(self.counts(),(1,2))

    def test_duas_propostas_disputam_revisao_da_unidade(self):
        a=self.register();b=self.register();results=self.race([decision(a,'confirm'),decision(b,'confirm')])
        self.assertEqual(results.count('conflict'),1);self.assertEqual(self.counts(),(1,2))

    def test_transacao_externa_rollback_remove_lote(self):
        p=self.register()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');state.decidir_proposta(db,TEACHER,decision(p,'confirm'))
            self.assertEqual(db.execute('SELECT count(*) FROM operational_effects').fetchone()[0],2)
            with self.connect() as other:self.assertEqual(other.execute('SELECT count(*) FROM operational_effects').fetchone()[0],0)
            db.rollback()
        self.assertEqual(self.counts(),(0,0))

    def test_commit_externo_torna_lote_duravel(self):
        p=self.register()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');state.decidir_proposta(db,TEACHER,decision(p,'confirm'));db.commit()
        self.assertEqual(self.counts(),(1,2))

    def test_replay_apos_outro_estado_nao_aplica_novamente(self):
        command=decision(self.register(),'confirm')
        with self.connect() as db:first=state.decidir_proposta(db,TEACHER,command)
        with self.connect() as db:
            second=state.registrar_proposta(db,TEACHER,proposal(db,{'index_percent':40}))
            state.decidir_proposta(db,TEACHER,decision(second,'confirm'))
            self.assertEqual(state.decidir_proposta(db,TEACHER,command),first)
        self.assertEqual(self.counts(),(2,4))

    def test_comando_entre_operacoes_ou_contexto_nao_reutiliza(self):
        with self.connect() as db:
            body=proposal(db);p=state.registrar_proposta(db,TEACHER,body)
            command=decision(p,'confirm');command['command_id']=body['command_id']
            with self.assertRaises(state.Conflict):state.decidir_proposta(db,TEACHER,command)
        self.assertEqual(self.counts(),(0,0))


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');seed(self.db)
        self.db.execute('PRAGMA foreign_keys=ON');self.addCleanup(self.db.close)

    def test_migrar_repetir_preserva_tabelas_anteriores(self):
        before=list(self.db.iterdump());self.assertTrue(store.migrate(self.db))
        after=list(self.db.iterdump());self.assertFalse(store.migrate(self.db))
        self.assertEqual(list(self.db.iterdump()),after)
        for line in before:
            if line not in ('BEGIN TRANSACTION;','COMMIT;'):self.assertIn(line,after)
        self.assertEqual(len(self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'operational_%'").fetchall()),6)

    def test_falha_ddl_reverte_lote(self):
        before=list(self.db.iterdump())
        with patch.object(store,'STATEMENTS',store.STATEMENTS[:2]+('SQL INVALIDO',)+store.STATEMENTS[2:]):
            with self.assertRaises(sqlite3.DatabaseError):store.migrate(self.db)
        self.assertEqual(list(self.db.iterdump()),before)

    def test_conexao_independente_e_fk_obrigatorios(self):
        self.db.execute('PRAGMA foreign_keys=OFF')
        with self.assertRaises(sqlite3.DatabaseError):store.migrate(self.db)
        self.db.execute('PRAGMA foreign_keys=ON');self.db.execute('BEGIN')
        with self.assertRaises(sqlite3.DatabaseError):store.migrate(self.db)
        self.db.rollback()

    def test_schema_parcial_nao_e_completado(self):
        self.db.execute('CREATE TABLE operational_proposals(dummy TEXT)');self.db.commit()
        before=list(self.db.iterdump())
        with self.assertRaises(sqlite3.DatabaseError):store.migrate(self.db)
        self.assertEqual(list(self.db.iterdump()),before)

    def test_schema_sem_trigger_recusa(self):
        store.migrate(self.db)
        self.db.execute('DROP TRIGGER operational_commands_no_update');self.db.commit()
        with self.assertRaises(sqlite3.DatabaseError):store.validate(self.db)

    def test_versao_futura_ou_hash_divergente_recusa(self):
        store.migrate(self.db)
        self.db.execute('DROP TRIGGER operational_schema_migrations_no_update')
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('UPDATE operational_schema_migrations SET version=2')
        self.db.execute("UPDATE operational_schema_migrations SET schema_sha256='invalido'")
        self.db.execute(next(s for s in store.STATEMENTS if s.startswith('CREATE TRIGGER operational_schema_migrations_no_update ')))
        self.db.commit()
        with self.assertRaises(sqlite3.DatabaseError):store.migrate(self.db)
        self.db.rollback()

    def test_marcador_imutavel(self):
        store.migrate(self.db)
        for sql in ('UPDATE operational_schema_migrations SET version=2','DELETE FROM operational_schema_migrations'):
            with self.assertRaises(sqlite3.IntegrityError):self.db.execute(sql)
        self.db.rollback()


if __name__=='__main__':unittest.main()
