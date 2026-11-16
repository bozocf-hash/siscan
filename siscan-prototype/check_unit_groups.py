"""Contrato de grupamentos em memória; fixtures próprias, sem banco ou servidor."""

from copy import deepcopy
import hashlib
import json
from queue import SimpleQueue
from threading import Barrier, Thread
import unittest
import uuid

from unit_groups import GroupConflict, RegistroGrupamentos


def digest(value):
    texto = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def unidade(unit_id, *, domain='naval', team='AZUL', exercise_id=1, classe='classe-ficticia'):
    snapshot = dict(unit_id=unit_id, exercise_id=exercise_id, team=team,
                    configuration_version_id='config-' + unit_id, model_id=classe,
                    source_kind='synthetic_controlled', official_calculation_ready=False,
                    combustivel_kg=10, municao=3)
    return dict(unit_id=unit_id, exercise_id=exercise_id, team=team, domain=domain,
                domain_evidence=dict(domain=domain, basis='synthetic_controlled', reference='fixture-ug-01'),
                allocated=True, snapshot_id='snapshot-' + unit_id, snapshot_sha256=digest(snapshot),
                configuration_version_id=snapshot['configuration_version_id'], snapshot=snapshot)


class GrupamentosTests(unittest.TestCase):
    def setUp(self):
        self.registro = RegistroGrupamentos()
        self.contexto = dict(exercise_id=1, team='AZUL')
        self.inventario = {'n1': unidade('n1', classe='classe-a'), 'n2': unidade('n2', classe='classe-b'),
                           'n3': unidade('n3', classe='classe-c'), 'a1': unidade('a1', domain='aereo')}

    def pedido(self, membros=None, **campos):
        return dict(command_id=str(uuid.uuid4()), designation='Grupo de teste', domain='naval',
                    member_unit_ids=['n1', 'n2'] if membros is None else membros, **campos)

    def criar(self, pedido=None):
        return self.registro.criar_grupamento(self.contexto, self.inventario,
                                              self.pedido() if pedido is None else pedido)

    def revisao(self, grupo, membros):
        pedido = self.pedido(membros)
        pedido.update(group_id=grupo['group_id'], expected_revision=grupo['composition_revision'])
        return pedido

    def test_criacao_heterogenea_preserva_referencias_e_entradas(self):
        antes = deepcopy(self.inventario)
        grupo = self.criar()
        self.assertEqual(grupo['composition_revision'], 1)
        self.assertEqual([m['unit_id'] for m in grupo['members']], ['n1', 'n2'])
        self.assertEqual(grupo['members'][1]['snapshot_sha256'], self.inventario['n2']['snapshot_sha256'])
        self.assertEqual(self.inventario, antes)
        self.assertEqual(str(uuid.UUID(grupo['group_id'])), grupo['group_id'])
        self.assertNotIn('combustivel_kg', grupo)

    def test_esquadrilha_nao_infere_mpnl(self):
        pedido = self.pedido(['a1'])
        pedido.update(domain='aereo', organization_label='Esquadrilha')
        grupo = self.criar(pedido)
        self.assertEqual(grupo['organization_label'], 'Esquadrilha')
        self.assertIsNone(grupo['mpnl_binding'])

    def test_reenvio_e_ordem_dos_membros_nao_duplicam(self):
        pedido = self.pedido()
        grupo = self.criar(pedido)
        pedido['member_unit_ids'].reverse()
        self.assertEqual(self.criar(pedido), grupo)
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, grupo['group_id']), grupo)
        pedido['designation'] = 'Outra intenção'
        with self.assertRaises(GroupConflict):
            self.criar(pedido)

    def test_consulta_e_retorno_nao_permitem_editar_registro(self):
        grupo = self.criar()
        gid = grupo['group_id']
        esperado = deepcopy(grupo)
        grupo['members'].clear()
        consultado = self.registro.consultar_grupamento(self.contexto, gid, revision=1)
        self.assertEqual(consultado, esperado)
        consultado['designation'] = 'editado fora'
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, gid), esperado)

    def test_contextos_nao_revelam_grupo(self):
        grupo = self.criar()
        for contexto in (dict(exercise_id=1, team='VERMELHO'), dict(exercise_id=2, team='AZUL')):
            with self.subTest(contexto=contexto):
                with self.assertRaises(KeyError):
                    self.registro.consultar_grupamento(contexto, grupo['group_id'])

    def test_falha_nao_reserva_integrante_valido(self):
        with self.assertRaises(ValueError):
            self.criar(self.pedido(['n1', 'n1']))
        with self.assertRaises(PermissionError):
            self.criar(self.pedido(['n1', 'ausente']))
        self.assertEqual(len(self.criar()['members']), 2)
        with self.assertRaises(GroupConflict):
            self.criar(self.pedido(['n1']))

    def test_pertencimento_disponibilidade_e_dominio(self):
        for campo, valor in (('team', 'VERMELHO'), ('exercise_id', 2), ('allocated', False), ('allocated', 1)):
            with self.subTest(campo=campo):
                inventario = deepcopy(self.inventario)
                inventario['n1'][campo] = valor
                with self.assertRaises(PermissionError):
                    self.registro.criar_grupamento(self.contexto, inventario, self.pedido(['n1']))
        with self.assertRaises(ValueError):
            self.criar(self.pedido(['a1']))

    def test_integridade_do_snapshot_e_normalizacao(self):
        for campo in ('snapshot_sha256', 'snapshot_id', 'configuration_version_id', 'domain_evidence'):
            with self.subTest(campo=campo):
                inventario = deepcopy(self.inventario)
                inventario['n1'].pop(campo)
                with self.assertRaises(ValueError):
                    self.registro.criar_grupamento(self.contexto, inventario, self.pedido(['n1']))
        inventario = deepcopy(self.inventario)
        inventario['n1']['snapshot']['combustivel_kg'] = 999
        with self.assertRaises(ValueError):
            self.registro.criar_grupamento(self.contexto, inventario, self.pedido(['n1']))

    def test_campos_inesperados_e_contexto_invalidos(self):
        for campos in ({'approved': True}, {'role': 'instructor'}, {'snapshot_sha256': 'a' * 64}):
            with self.assertRaises(ValueError):
                self.criar(self.pedido(**campos))
        for contexto in (dict(exercise_id=True, team='AZUL'), dict(exercise_id=1, team='outro')):
            with self.assertRaises(ValueError):
                self.registro.criar_grupamento(contexto, self.inventario, self.pedido())

    def test_mpnl_expresso_valida_ramo_e_nivel_sem_inferir_forca(self):
        grupo = self.criar(self.pedido(mpnl_binding={'force': 'MARINHA', 'level': 2}))
        self.assertEqual(grupo['mpnl_binding'], {'force': 'MARINHA', 'level': 2})
        for binding in ({'force': 'MARINHA', 'level': 5}, {'force': 'OUTRA', 'level': 2}):
            with self.assertRaises(ValueError):
                self.criar(self.pedido(['n3'], mpnl_binding=binding))

    def test_revisao_preserva_historico_e_libera_integrante_removido(self):
        original = self.criar()
        pedido = self.revisao(original, ['n1', 'n3'])
        novo = self.registro.revisar_grupamento(self.contexto, self.inventario, pedido)
        self.assertEqual(novo['composition_revision'], 2)
        self.assertNotEqual(novo['composition_sha256'], original['composition_sha256'])
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, original['group_id'], 1), original)
        self.assertEqual(self.criar(self.pedido(['n2']))['members'][0]['unit_id'], 'n2')
        with self.assertRaises(GroupConflict):
            self.criar(self.pedido(['n3']))
        self.assertEqual(self.registro.revisar_grupamento(self.contexto, self.inventario, pedido), novo)

    def test_revisao_desatualizada_e_falha_nao_publicam_ou_reservam(self):
        original = self.criar()
        with self.assertRaises(PermissionError):
            self.registro.revisar_grupamento(self.contexto, self.inventario,
                                             self.revisao(original, ['n3', 'ausente']))
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, original['group_id']), original)
        self.criar(self.pedido(['n3']))
        self.registro.revisar_grupamento(self.contexto, self.inventario, self.revisao(original, ['n1']))
        with self.assertRaises(GroupConflict):
            self.registro.revisar_grupamento(self.contexto, self.inventario, self.revisao(original, ['n2']))

    def test_reenvio_retorna_resultado_historico_sem_reexecutar_inventario(self):
        pedido = self.pedido()
        grupo = self.criar(pedido)
        self.inventario['n1']['allocated'] = False
        self.assertEqual(self.criar(pedido), grupo)

    def test_duas_revisoes_concorrentes_publicam_uma_so(self):
        original = self.criar()
        pedidos = [self.revisao(original, ['n1']), self.revisao(original, ['n2'])]
        barrier, saida = Barrier(3), SimpleQueue()

        def executar(pedido):
            try:
                barrier.wait(timeout=5)
                novo = self.registro.revisar_grupamento(self.contexto, self.inventario, pedido)
                saida.put(('ok', novo['composition_revision']))
            except BaseException as exc:
                saida.put((type(exc).__name__, None))

        threads = [Thread(target=executar, args=(pedido,), daemon=True) for pedido in pedidos]
        for thread in threads:
            thread.start()
        barrier.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
        respostas = [saida.get_nowait(), saida.get_nowait()]
        self.assertCountEqual(respostas, [('ok', 2), ('GroupConflict', None)])
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, original['group_id'])['composition_revision'], 2)


if __name__ == '__main__':
    unittest.main()
