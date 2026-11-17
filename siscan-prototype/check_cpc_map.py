"""Conferência CPC no mapa: dados sintéticos e SQLite em memória."""
from copy import deepcopy
import sqlite3
import unittest
from unittest.mock import patch
import uuid

from check_map_groups import seed, TEACHER, BLUE
import cpc_map
import map_groups
from unit_groups import GroupConflict, RegistroGrupamentos


def seed_pairs(db, registry):
    selection = {}
    for team in ('AZUL', 'VERMELHO'):
        units = map_groups.view(db, TEACHER, team)['units']
        result = map_groups.command(db, TEACHER, registry, dict(team=team,
            command_id=str(uuid.uuid4()), designation='Grupo ' + team, domain='aereo',
            member_unit_ids=[u['unit_id'] for u in units if u['eligible']]))
        selection[team] = dict(group_id=result['group']['group_id'], expected_revision=1)
    return selection


class MapPreparationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        seed(self.db)
        self.registry = RegistroGrupamentos()
        self.selection = seed_pairs(self.db, self.registry)

    def prepare(self, **kwargs):
        return cpc_map.prepare(self.db, kwargs.get('user', TEACHER), self.registry,
                               kwargs.get('selection', self.selection))

    def test_lista_por_partido_e_revisao(self):
        before = list(self.db.iterdump())
        result = cpc_map.listing(self.db, TEACHER, self.registry)
        self.assertEqual([p['team'] for p in result['parties']], ['AZUL', 'VERMELHO'])
        self.assertTrue(all(p['groups'][0]['preparable'] for p in result['parties']))
        self.assertEqual(result['scenario_version'], 1)
        self.assertEqual(list(self.db.iterdump()), before)

    def test_autorizacao_antes_de_consultar_partidos(self):
        with patch('map_groups.view', side_effect=AssertionError('Leitura indevida')):
            with self.assertRaises(PermissionError): self.prepare(user=BLUE)
            with self.assertRaises(PermissionError):
                self.prepare(user=dict(uid=99, role='instructor'))

    def test_prepara_par_sem_posicoes_ou_efeitos(self):
        before = list(self.db.iterdump())
        groups = {t:self.registry.consultar_grupamento(dict(exercise_id=1,team=t),s['group_id'])
                  for t,s in self.selection.items()}
        result = self.prepare()
        self.assertEqual(result['schema_version'], 'siscan-cpc-map-preparation-01')
        self.assertEqual(result['status'], 'requires_instructor_review')
        for flag in ('simulation_started','official_calculation_ready','official_effects_applied'):
            self.assertIs(result[flag], False)
        self.assertEqual([p['team'] for p in result['parties']], ['AZUL','VERMELHO'])
        for party in result['parties']:
            self.assertEqual(party['designation'], 'Grupo ' + party['team'])
            self.assertEqual(party['domain'], 'aereo')
            member = party['members'][0]
            self.assertIsNone(member['latitude'])
            self.assertIsNone(member['current_logistics'])
            self.assertIn('snapshot_sha256', member)
        self.assertNotIn('input_template', str(result))
        self.assertEqual(list(self.db.iterdump()), before)
        for team, expected in groups.items():
            self.assertEqual(self.registry.consultar_grupamento(dict(exercise_id=1,team=team),expected['group_id']), expected)

    def test_fechamento_recusa_preparar_mas_informa_na_lista(self):
        self.db.execute("UPDATE exercises SET state='closed'")
        self.assertFalse(cpc_map.listing(self.db, TEACHER, self.registry)['exercise_open'])
        with self.assertRaises(ValueError): self.prepare()

    def test_selecao_ou_revisao_invalida(self):
        with self.assertRaises(ValueError): self.prepare(selection={})
        invalid = deepcopy(self.selection);invalid['AZUL']['expected_revision'] = 2
        with self.assertRaises(GroupConflict): self.prepare(selection=invalid)
        invalid['AZUL'] = self.selection['VERMELHO']
        with self.assertRaises(KeyError): self.prepare(selection=invalid)

    def test_arquivado_ou_revogado_nao_prepara(self):
        self.registry.arquivar_grupamento(dict(exercise_id=1,team='AZUL'),
            dict(command_id=str(uuid.uuid4()),**self.selection['AZUL']))
        listing = cpc_map.listing(self.db, TEACHER, self.registry)
        self.assertFalse(listing['parties'][0]['groups'][0]['preparable'])
        with self.assertRaises(GroupConflict): self.prepare()

    def test_revogacao_antes_da_captura(self):
        self.db.execute("UPDATE party_allocations SET active=0 WHERE team='AZUL'")
        with self.assertRaises(PermissionError): self.prepare()

    def test_hashes_deterministas_e_posicao_separada_do_tecnico(self):
        import hashlib, json
        first = self.prepare()
        self.assertEqual(self.prepare(selection=dict(reversed(list(self.selection.items())))), first)
        body = deepcopy(first);sha = body.pop('view_sha256')
        self.assertEqual(sha, hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False,
                         separators=(',', ':'),allow_nan=False).encode('utf-8')).hexdigest())
        aid = first['parties'][0]['members'][0]['asset_id']
        self.db.execute('INSERT INTO map_unit_positions VALUES(?,?,?,1,1)', (aid,-22.7,-43.1))
        moved = self.prepare()
        self.assertEqual(first['dossier_sha256'], moved['dossier_sha256'])
        self.assertNotEqual(first['positions_sha256'], moved['positions_sha256'])
        self.assertNotEqual(first['view_sha256'], moved['view_sha256'])

    def test_copias_independentes(self):
        expected = self.prepare();result = self.prepare()
        result['parties'][0]['members'].clear()
        self.assertEqual(self.prepare(), expected)

    def test_nao_participante_nao_muda_hash(self):
        expected = self.prepare()
        self.db.execute("INSERT INTO assets(exercise_id,team,code,name,category,fiche) VALUES(1,'AZUL','EXTRA','Extra','Teste','Teste')")
        aid = self.db.execute('SELECT max(id) FROM assets').fetchone()[0]
        self.db.execute("INSERT INTO party_allocations VALUES(1,'AZUL',?,1,1,'2026-11-17')", (aid,))
        self.assertEqual(self.prepare(), expected)

    def conflict_during_capture(self, action):
        original = cpc_map._project
        count = 0
        def projecting(*args):
            nonlocal count
            result = original(*args)
            count += 1
            if count == 1: action(result)
            return result
        with patch.object(cpc_map, '_project', side_effect=projecting):
            with self.assertRaises(GroupConflict): self.prepare()

    def test_posicao_alterada_durante_captura_recusa_vista(self):
        self.conflict_during_capture(lambda result: self.db.execute(
            'INSERT INTO map_unit_positions VALUES(?,?,?,1,1)',
            (result['parties'][0]['members'][0]['asset_id'],-22,-43)))

    def test_revogacao_durante_captura_recusa_vista(self):
        self.conflict_during_capture(lambda _:self.db.execute("UPDATE party_allocations SET active=0 WHERE team='AZUL'"))

    def test_fechamento_durante_captura_recusa_vista(self):
        self.conflict_during_capture(lambda _:self.db.execute("UPDATE exercises SET state='closed'"))

    def test_arquivamento_durante_captura_recusa_vista(self):
        self.conflict_during_capture(lambda _:self.registry.arquivar_grupamento(
            dict(exercise_id=1,team='AZUL'),dict(command_id=str(uuid.uuid4()),**self.selection['AZUL'])))


if __name__ == '__main__':
    unittest.main()
