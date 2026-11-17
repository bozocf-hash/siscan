"""Provedor de grupos no mapa: banco em memória e fontes controladas."""
from contextlib import closing
from copy import deepcopy
import sqlite3
import unittest

import app
import engine_units
import map_groups


TEACHER = dict(uid=1, role='instructor', team=None)
BLUE = dict(uid=2, role='student', team='AZUL')
RED = dict(uid=3, role='student', team='VERMELHO')


def seed(db):
    db.row_factory = sqlite3.Row
    db.executescript(app.SCHEMA)
    for user in (TEACHER, BLUE, RED):
        db.execute("INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,X'00',X'00')",
                   (user['uid'], str(user['uid']), str(user['uid']), user['role'], user['team']))
    db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'TEST','Teste','Teste')")
    db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'Teste','Teste','2026-11-16')")
    db.executemany('INSERT INTO assignments VALUES(1,?)', [(1,), (2,), (3,)])
    engine_units.prepare_units(db, TEACHER)
    for row in db.execute('SELECT asset_id,team FROM engine_units').fetchall():
        db.execute("INSERT INTO party_allocations VALUES(1,?,?,1,1,'2026-11-16')", (row['team'], row['asset_id']))
    db.commit()


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        seed(self.db)
        self.addCleanup(self.db.close)

    def test_identidade_e_dominio_controlado_sem_escrita(self):
        before = list(self.db.iterdump())
        result = map_groups.view(self.db, BLUE, 'AZUL')
        self.assertEqual(result['context'], dict(exercise_id=1, team='AZUL'))
        self.assertEqual(len(result['inventory']), 1)
        record = next(iter(result['inventory'].values()))
        source = engine_units.list_units(self.db, BLUE)['units'][0]
        self.assertEqual(record['snapshot'], source['snapshot'])
        self.assertEqual(record['snapshot_sha256'], source['snapshot_sha256'])
        self.assertEqual(record['domain'], 'aereo')
        unit = result['units'][0]
        self.assertEqual(unit['unit_id'], source['unit_id'])
        self.assertEqual(unit['asset_id'], source['asset_id'])
        self.assertTrue(unit['eligible'])
        self.assertIsNone(unit['latitude'])
        self.assertEqual(list(self.db.iterdump()), before)

    def test_outro_partido_e_nao_participante_recusados(self):
        with self.assertRaises(PermissionError):
            map_groups.view(self.db, BLUE, 'VERMELHO')
        with self.assertRaises(PermissionError):
            map_groups.view(self.db, dict(uid=99, role='instructor'), 'AZUL')
        self.assertEqual(len(map_groups.view(self.db, TEACHER, 'VERMELHO')['inventory']), 1)

    def test_meio_sem_instancia_continua_plotavel_mas_pendente(self):
        self.db.execute("INSERT INTO assets(exercise_id,team,code,name,category,fiche) VALUES(1,'AZUL','PEND','Unidade aérea sintética AZUL','Aeronave','Teste')")
        aid = self.db.execute('SELECT max(id) FROM assets').fetchone()[0]
        self.db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-16')", (aid,))
        result = map_groups.view(self.db, BLUE, 'AZUL')
        pending = next(u for u in result['units'] if u['asset_id'] == aid)
        self.assertFalse(pending['eligible'])
        self.assertIsNone(pending['unit_id'])
        self.assertIn('snapshot', pending['reason'].lower())
        self.assertEqual(len(result['inventory']), 1)

    def test_adjudicacao_revogada_nao_e_exposta(self):
        self.db.execute("UPDATE party_allocations SET active=0 WHERE team='AZUL'")
        result = map_groups.view(self.db, BLUE, 'AZUL')
        self.assertEqual(result['units'], [])
        self.assertEqual(result['inventory'], {})

    def test_nome_e_flag_nao_substituem_configuracao(self):
        self.db.execute('DROP TRIGGER engine_snapshot_no_update')
        row = self.db.execute("SELECT * FROM engine_unit_snapshots WHERE team='AZUL'").fetchone()
        import json
        snapshot = json.loads(row['snapshot_json'])
        snapshot['model_id'] = 'OUTRO-MODELO'
        self.db.execute('UPDATE engine_unit_snapshots SET snapshot_json=?,snapshot_sha256=? WHERE snapshot_id=?',
                        (engine_units.encoded(snapshot), engine_units.input_hash(snapshot), row['snapshot_id']))
        result = map_groups.view(self.db, BLUE, 'AZUL')
        self.assertEqual(result['inventory'], {})
        self.assertFalse(result['units'][0]['eligible'])

    def test_snapshot_corrompido_nao_vira_lista_vazia(self):
        self.db.execute('DROP TRIGGER engine_snapshot_no_update')
        self.db.execute("UPDATE engine_unit_snapshots SET snapshot_json='{}' WHERE team='AZUL'")
        with self.assertRaises(sqlite3.DatabaseError):
            map_groups.view(self.db, BLUE, 'AZUL')


if __name__ == '__main__':
    unittest.main()
