"""Preparação didática de dois partidos com registro real e dados sintéticos."""

from copy import deepcopy
import hashlib
import json
import unittest
import uuid
from unittest.mock import Mock, patch

from unit_groups import GroupConflict, RegistroGrupamentos
from cpc_group_preparation import preparar_dossie_grupamentos


def digest(value):
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


class PreparacaoTests(unittest.TestCase):
    def setUp(self):
        self.registro = RegistroGrupamentos()
        self.inventarios, self.selecao = {}, {}
        self.autorizar = Mock(return_value=True)
        for team in ('AZUL', 'VERMELHO'):
            inventario = {}
            for n in range(3):
                uid = f'{team}-{n}'
                snapshot = dict(unit_id=uid, exercise_id=1, team=team,
                                configuration_version_id='config-' + uid,
                                source_kind='synthetic_controlled', official_calculation_ready=False,
                                combustivel_kg=10, municao={'estoque-ficticio': 3}, desconhecido=None)
                inventario[uid] = dict(unit_id=uid, exercise_id=1, team=team, domain='naval',
                    domain_evidence=dict(domain='naval', basis='synthetic_controlled', reference='fixture-gp'),
                    allocated=True, snapshot_id='snapshot-' + uid, snapshot_sha256=digest(snapshot),
                    configuration_version_id=snapshot['configuration_version_id'], snapshot=snapshot)
            self.inventarios[team] = inventario
            grupo = self.registro.criar_grupamento(self.contexto(team), inventario, self.pedido(team))
            self.selecao[team] = dict(group_id=grupo['group_id'], expected_revision=1)

    def contexto(self, team):
        return dict(exercise_id=1, team=team)

    def pedido(self, team, domain='naval'):
        return dict(command_id=str(uuid.uuid4()), designation='Grupo didático', domain=domain,
                    member_unit_ids=[f'{team}-0', f'{team}-1'])

    def preparar(self, **kwargs):
        args = dict(exercise_id=1, autorizar_instrutor=self.autorizar, registro=self.registro,
                    inventarios=self.inventarios, selecao=self.selecao)
        args.update(kwargs)
        return preparar_dossie_grupamentos(**args)

    def grupos(self):
        return {team: self.registro.consultar_grupamento(self.contexto(team), sel['group_id'])
                for team, sel in self.selecao.items()}

    def test_dois_partidos_com_snapshots_somente_dos_membros(self):
        antes, grupos = deepcopy(self.inventarios), self.grupos()
        result = self.preparar()
        self.autorizar.assert_called_once_with(1)
        self.assertEqual(result['exercise_id'], 1)
        self.assertEqual([p['team'] for p in result['parties']], ['AZUL', 'VERMELHO'])
        for party in result['parties']:
            team = party['team']
            self.assertEqual(set(party['snapshots']), {f'{team}-0', f'{team}-1'})
            self.assertEqual(party['composition']['group_id'], self.selecao[team]['group_id'])
            self.assertEqual(party['snapshots'][f'{team}-0'], antes[team][f'{team}-0']['snapshot'])
        self.assertEqual(self.inventarios, antes)
        self.assertEqual(self.grupos(), grupos)
        self.assertEqual(result['status'], 'requires_instructor_review')
        self.assertIs(result['simulation_started'], False)
        self.assertIs(result['official_calculation_ready'], False)

    def test_negativa_nao_consulta_registro_nem_copia_inventario(self):
        class NaoCopiar(dict):
            def __deepcopy__(self, memo):
                raise AssertionError('Inventário acessado antes de autorização')
        for answer in (False, None, 1, 'instructor'):
            with self.subTest(answer=answer):
                registro = Mock()
                with self.assertRaises(PermissionError):
                    self.preparar(autorizar_instrutor=lambda _: answer, registro=registro,
                                  inventarios=NaoCopiar())
                self.assertEqual(registro.mock_calls, [])

    def test_excecao_autorizador_aborta_sem_consulta(self):
        registro = Mock()
        with self.assertRaisesRegex(RuntimeError, 'provedor indisponível'):
            self.preparar(autorizar_instrutor=Mock(side_effect=RuntimeError('provedor indisponível')),
                          registro=registro)
        self.assertEqual(registro.mock_calls, [])

    def test_exercicio_invalido_e_autorizador_nao_chamavel(self):
        for value in (True, 0, -1, '1', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.preparar(exercise_id=value)
        self.autorizar.assert_not_called()
        with self.assertRaises(ValueError):
            self.preparar(autorizar_instrutor=True)

    def test_selecao_estrita(self):
        for change in ({}, {'AZUL': self.selecao['AZUL']},
                       dict(self.selecao, role='instructor'),
                       dict(self.selecao, AZUL=dict(self.selecao['AZUL'], extra=1)),
                       dict(self.selecao, AZUL=dict(group_id='invalido', expected_revision=1)),
                       dict(self.selecao, AZUL=dict(self.selecao['AZUL'], expected_revision=True))):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.preparar(selecao=change)

    def test_inventarios_estritos(self):
        for value in (None, {}, {'AZUL': {}, 'VERMELHO': []}, dict(self.inventarios, OUTRO={})):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.preparar(inventarios=value)

    def test_grupo_de_outro_contexto_e_revisao_antiga(self):
        self.selecao['AZUL']['group_id'] = self.selecao['VERMELHO']['group_id']
        with self.assertRaises(KeyError):
            self.preparar()
        self.setUp()
        self.selecao['AZUL']['expected_revision'] = 2
        with self.assertRaises(GroupConflict):
            self.preparar()

    def test_indisponibilidade_e_snapshot_divergente(self):
        record = self.inventarios['VERMELHO']['VERMELHO-0']
        record['allocated'] = False
        with self.assertRaises(PermissionError):
            self.preparar()
        record['allocated'] = True
        record['snapshot']['combustivel_kg'] = 9
        with self.assertRaises(ValueError):
            self.preparar()

    def test_dominios_aereos_e_mistos_sem_alterar_mpnl(self):
        for domains in (('naval', 'aereo'), ('aereo', 'aereo')):
            with self.subTest(domains=domains):
                self.setUp()
                for team, domain in zip(('AZUL', 'VERMELHO'), domains):
                    for record in self.inventarios[team].values():
                        record['domain'] = domain
                        record['domain_evidence']['domain'] = domain
                    pedido = self.pedido(team, domain)
                    pedido.update(self.selecao[team])
                    grupo = self.registro.revisar_grupamento(self.contexto(team), self.inventarios[team], pedido)
                    self.selecao[team]['expected_revision'] = grupo['composition_revision']
                self.assertEqual(len(self.preparar()['parties']), 2)
                for grupo in self.grupos().values():
                    self.assertIsNone(grupo['mpnl_binding'])

    def test_falha_no_segundo_partido_preserva_todo_estado(self):
        del self.inventarios['VERMELHO']['VERMELHO-0']
        antes, grupos = deepcopy(self.inventarios), self.grupos()
        with self.assertRaises(PermissionError):
            self.preparar()
        self.assertEqual(self.inventarios, antes)
        self.assertEqual(self.grupos(), grupos)

    def test_grupo_arquivado_recusa_preparacao(self):
        self.registro.arquivar_grupamento(self.contexto('AZUL'),
            dict(command_id=str(uuid.uuid4()), **self.selecao['AZUL']))
        grupos = self.grupos()
        with self.assertRaises(GroupConflict):
            self.preparar()
        self.assertEqual(self.grupos(), grupos)

    def test_revisao_alterada_durante_preparacao_e_recusada(self):
        self.conflito_observado(arquivar=False)

    def test_arquivamento_durante_preparacao_e_recusado(self):
        self.conflito_observado(arquivar=True)

    def conflito_observado(self, *, arquivar):
        original = self.registro.preparar_composicao
        antes = deepcopy(self.inventarios)
        alterado = []

        def preparar_e_mudar(contexto, inventario, **selection):
            result = original(contexto, inventario, **selection)
            if contexto['team'] == 'VERMELHO':
                if arquivar:
                    pedido = dict(command_id=str(uuid.uuid4()), **self.selecao['AZUL'])
                    grupo = self.registro.arquivar_grupamento(self.contexto('AZUL'), pedido)
                else:
                    pedido = self.pedido('AZUL')
                    pedido.update(self.selecao['AZUL'])
                    grupo = self.registro.revisar_grupamento(self.contexto('AZUL'),
                                                           self.inventarios['AZUL'], pedido)
                alterado.append(grupo)
            return result

        with patch.object(self.registro, 'preparar_composicao', side_effect=preparar_e_mudar):
            with self.assertRaises(GroupConflict):
                self.preparar()
        self.assertEqual(self.inventarios, antes)
        self.assertEqual(self.grupos()['AZUL'], alterado[0])
        self.assertEqual(self.grupos()['VERMELHO']['composition_revision'], 1)


if __name__ == '__main__':
    unittest.main()
