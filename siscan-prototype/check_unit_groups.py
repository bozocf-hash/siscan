"""Contrato de grupamentos em memória; fixtures próprias, sem banco ou servidor."""

from copy import deepcopy
import hashlib
import json
from queue import SimpleQueue
from threading import Barrier, Thread, Event
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
    def test_escopo_publico_serializa_e_libera_apos_excecao(self):
        grupo=self.criar();started=Event();done=Event()
        refs=[dict(context=self.contexto,group_id=grupo['group_id'],expected_revision=1)]
        def archive():
            started.set();self.registro.arquivar_grupamento(self.contexto,self.arquivo(grupo));done.set()
        thread=Thread(target=archive,daemon=True)
        with self.assertRaises(RuntimeError):
            with self.registro.conferir_revisoes(refs) as captured:
                captured[0]['members'].clear();thread.start();self.assertTrue(started.wait(2))
                self.assertFalse(done.is_set())
                self.assertEqual(self.registro.consultar_grupamento(self.contexto,grupo['group_id'])['composition_revision'],1)
                raise RuntimeError('saída provocada')
        thread.join(3);self.assertTrue(done.is_set())
        with self.assertRaises(GroupConflict):
            with self.registro.conferir_revisoes(refs):pass
    def test_lista_contextual_copias_e_arquivados(self):
        grupo = self.criar()
        self.assertEqual(self.registro.listar_grupamentos(self.contexto), [grupo])
        self.assertEqual(self.registro.listar_grupamentos(dict(exercise_id=1, team='VERMELHO')), [])
        self.assertEqual(self.registro.listar_grupamentos(dict(exercise_id=2, team='AZUL')), [])
        self.registro.listar_grupamentos(self.contexto)[0]['members'].clear()
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, grupo['group_id']), grupo)
        archived = self.registro.arquivar_grupamento(self.contexto, self.arquivo(grupo))
        self.assertEqual(self.registro.listar_grupamentos(self.contexto), [archived])

    def test_lista_ordenada_por_identidade(self):
        first = self.criar(self.pedido(['n1']))
        second = self.criar(self.pedido(['n2']))
        self.assertEqual([g['group_id'] for g in self.registro.listar_grupamentos(self.contexto)],
                         sorted([first['group_id'], second['group_id']]))

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

    def arquivo(self, grupo, **campos):
        return dict(command_id=str(uuid.uuid4()), group_id=grupo['group_id'],
                    expected_revision=grupo['composition_revision'], **campos)

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

    def concorrer(self, chamadas):
        barrier, saida = Barrier(3), SimpleQueue()

        def executar(chamada):
            try:
                barrier.wait(timeout=5)
                novo = chamada()
                saida.put(('ok', novo['composition_revision']))
            except BaseException as exc:
                saida.put((type(exc).__name__, None))

        threads = [Thread(target=executar, args=(chamada,), daemon=True) for chamada in chamadas]
        for thread in threads:
            thread.start()
        barrier.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
        return [saida.get_nowait(), saida.get_nowait()]

    def test_duas_revisoes_concorrentes_publicam_uma_so(self):
        original = self.criar()
        pedidos = [self.revisao(original, ['n1']), self.revisao(original, ['n2'])]
        respostas = self.concorrer([
            lambda p=p: self.registro.revisar_grupamento(self.contexto, self.inventario, p) for p in pedidos])
        self.assertCountEqual(respostas, [('ok', 2), ('GroupConflict', None)])
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, original['group_id'])['composition_revision'], 2)

    def test_criacao_concorrente_nao_compartilha_integrante(self):
        chamadas = [lambda: self.criar(self.pedido(['n1'])) for _ in range(2)]
        self.assertCountEqual(self.concorrer(chamadas), [('ok', 1), ('GroupConflict', None)])
        self.criar(self.pedido(['n2']))

    def test_arquivar_libera_unidades_e_preserva_historico(self):
        original = self.criar()
        pedido = self.arquivo(original)
        arquivado = self.registro.arquivar_grupamento(self.contexto, pedido)
        self.assertFalse(arquivado['active'])
        self.assertEqual(arquivado['composition_revision'], 2)
        self.assertEqual(arquivado['members'], original['members'])
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, original['group_id'], 1), original)
        self.assertEqual(self.registro.arquivar_grupamento(self.contexto, pedido), arquivado)
        self.criar()
        with self.assertRaises(GroupConflict):
            self.registro.revisar_grupamento(self.contexto, self.inventario,
                                             self.revisao(arquivado, ['n1']))

    def test_arquivo_invalido_nao_libera_vinculos(self):
        original = self.criar()
        for campo in ({'active': False}, {'role': 'instructor'}):
            with self.assertRaises(ValueError):
                self.registro.arquivar_grupamento(self.contexto, self.arquivo(original, **campo))
        pedido = self.arquivo(original)
        pedido['expected_revision'] = 2
        with self.assertRaises(GroupConflict):
            self.registro.arquivar_grupamento(self.contexto, pedido)
        with self.assertRaises(GroupConflict):
            self.criar()
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, original['group_id']), original)

    def test_chave_de_comando_nao_pode_mudar_de_operacao(self):
        pedido = self.pedido()
        grupo = self.criar(pedido)
        arquivar = self.arquivo(grupo)
        arquivar['command_id'] = pedido['command_id']
        with self.assertRaises(GroupConflict):
            self.registro.arquivar_grupamento(self.contexto, arquivar)

    def preparar(self, grupo, inventario=None):
        return self.registro.preparar_composicao(
            self.contexto, self.inventario if inventario is None else inventario,
            grupo['group_id'], grupo['composition_revision'])

    def test_preparar_retorna_referencias_sem_alterar_recursos(self):
        grupo = self.criar()
        antes = deepcopy(self.inventario)
        preparado = self.preparar(grupo)
        self.assertEqual(preparado['members'], grupo['members'])
        self.assertEqual(preparado['composition_sha256'], grupo['composition_sha256'])
        self.assertEqual(self.inventario, antes)
        self.assertFalse(preparado['simulation_started'])
        self.assertFalse(preparado['official_calculation_ready'])
        preparado['members'].clear()
        self.assertEqual(self.preparar(grupo)['members'], grupo['members'])
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, grupo['group_id']), grupo)

    def test_preparacao_revalida_disponibilidade_apos_reenvio(self):
        pedido = self.pedido()
        grupo = self.criar(pedido)
        self.inventario['n1']['allocated'] = False
        self.assertEqual(self.criar(pedido), grupo)
        with self.assertRaises(PermissionError):
            self.preparar(grupo)

    def test_preparacao_exige_revisao_se_snapshot_ou_configuracao_mudar(self):
        grupo = self.criar()
        for campo in ('snapshot', 'configuration_version_id', 'snapshot_id'):
            with self.subTest(campo=campo):
                inventario = deepcopy(self.inventario)
                row = inventario['n1']
                if campo == 'snapshot':
                    row['snapshot']['combustivel_kg'] = 9
                elif campo == 'configuration_version_id':
                    row[campo] = row['snapshot'][campo] = 'config-nova'
                else:
                    row[campo] = 'snapshot-novo'
                row['snapshot_sha256'] = digest(row['snapshot'])
                with self.assertRaises(GroupConflict):
                    self.preparar(grupo, inventario)
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, grupo['group_id']), grupo)

    def test_preparacao_recusa_grupo_inativo_ou_revisao_antiga(self):
        original = self.criar()
        atual = self.registro.revisar_grupamento(self.contexto, self.inventario,
                                                 self.revisao(original, ['n1']))
        with self.assertRaises(GroupConflict):
            self.preparar(original)
        arquivado = self.registro.arquivar_grupamento(self.contexto, self.arquivo(atual))
        with self.assertRaises(GroupConflict):
            self.preparar(arquivado)

    def test_preparacao_nao_promove_referencia_descritiva(self):
        row = self.inventario['n1']
        row['snapshot']['source_kind'] = 'descriptive_reference'
        row['snapshot']['official_calculation_ready'] = False
        row['snapshot_sha256'] = digest(row['snapshot'])
        grupo = self.criar(self.pedido(['n1']))
        preparado = self.preparar(grupo)
        self.assertEqual(preparado['members'][0]['source_kind'], 'descriptive_reference')
        self.assertFalse(preparado['members'][0]['official_calculation_ready'])
        self.assertFalse(preparado['official_calculation_ready'])

    def test_inventario_nao_utilizado_nao_altera_manifesto_dos_membros(self):
        grupo = self.criar()
        preparado = self.preparar(grupo)
        self.inventario['n3']['allocated'] = False
        self.assertEqual(self.preparar(grupo), preparado)

    def test_reenvio_antigo_nao_reativa_grupo_arquivado(self):
        pedido = self.pedido()
        grupo = self.criar(pedido)
        arquivado = self.registro.arquivar_grupamento(self.contexto, self.arquivo(grupo))
        self.assertEqual(self.criar(pedido), grupo)
        self.assertEqual(self.registro.consultar_grupamento(self.contexto, grupo['group_id']), arquivado)
        with self.assertRaises(GroupConflict):
            self.preparar(grupo)

    def test_identidade_falsa_no_snapshot_e_recusada_mesmo_com_hash_recalculado(self):
        for campo, valor in (('unit_id', 'outra'), ('exercise_id', 2), ('team', 'VERMELHO'),
                              ('configuration_version_id', 'outra-config')):
            with self.subTest(campo=campo):
                inventario = deepcopy(self.inventario)
                inventario['n1']['snapshot'][campo] = valor
                inventario['n1']['snapshot_sha256'] = digest(inventario['n1']['snapshot'])
                with self.assertRaises(ValueError):
                    self.registro.criar_grupamento(self.contexto, inventario, self.pedido(['n1']))

    def test_recibos_de_comando_nao_atravessam_contextos(self):
        pedido = self.pedido(['n1'])
        azul = self.criar(pedido)
        vermelho = dict(exercise_id=1, team='VERMELHO')
        inventario = {'n1': unidade('n1', team='VERMELHO')}
        outro = self.registro.criar_grupamento(vermelho, inventario, pedido)
        self.assertEqual(outro['team'], 'VERMELHO')
        self.assertNotEqual(outro['group_id'], azul['group_id'])
        self.assertEqual(self.criar(pedido), azul)

    def test_dominio_aereo_nao_determina_forca_organizacional(self):
        pedido = self.pedido(['a1'], organization_label='Esquadrilha',
                             mpnl_binding={'force': 'MARINHA', 'level': 1})
        pedido['domain'] = 'aereo'
        grupo = self.criar(pedido)
        self.assertEqual(grupo['mpnl_binding'], {'force': 'MARINHA', 'level': 1})

    def test_limites_de_pedido_e_revisao(self):
        for campo, valor in (('command_id', 'invalido'), ('designation', ' '),
                              ('designation', 'x' * 121), ('member_unit_ids', []),
                              ('member_unit_ids', ['']), ('member_unit_ids', ['n1', None])):
            with self.subTest(campo=campo, valor=valor):
                pedido = self.pedido()
                pedido[campo] = valor
                with self.assertRaises(ValueError):
                    self.criar(pedido)
        grupo = self.criar()
        for rev in (0, -1, True, '1'):
            with self.assertRaises(ValueError):
                self.registro.consultar_grupamento(self.contexto, grupo['group_id'], rev)


if __name__ == '__main__':
    unittest.main()
