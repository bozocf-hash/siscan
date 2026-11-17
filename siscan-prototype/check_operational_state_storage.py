"""Migração, concorrência e recuperação em bancos descartáveis."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from check_map_groups import seed
import operational_state_storage as store


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
