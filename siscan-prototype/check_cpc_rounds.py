"""Invariantes das rodadas fictícias: simultaneidade e estoques defensivos."""

import random
import unittest
from unittest.mock import Mock

from cpc_combat import AcaoDisparo, GerenciadorDeCombate
from cpc_models import Armamento, MeioNaval
from cpc_scenario import CenarioTatico


class RodadaTests(unittest.TestCase):
    def setUp(self):
        self.arma_a = Armamento(identificador="ofensivo-a", tipo="missil_antinavio",
                               quantidade=3, pk=1.0, dano=100.0, alcance_maximo=20.0)
        self.arma_b = Armamento(identificador="ofensivo-b", tipo="missil_antinavio",
                               quantidade=3, pk=1.0, dano=100.0, alcance_maximo=20.0)
        self.defesa = Armamento(identificador="defensivo-b", tipo="defesa_ponto", quantidade=4)
        self.a = MeioNaval(identificador="a", pontos_de_vida=100.0, assinatura_radar=1.0,
                          velocidade=0.0, capacidade_defesa_ponto=None, armamentos=[self.arma_a],
                          alcance_radar=20.0, probabilidade_deteccao=1.0)
        self.b = MeioNaval(identificador="b", pontos_de_vida=100.0, assinatura_radar=1.0,
                          velocidade=0.0, capacidade_defesa_ponto=0.5,
                          armamentos=[self.arma_b, self.defesa],
                          alcance_radar=20.0, probabilidade_deteccao=1.0)
        self.rng = Mock(spec=random.Random)
        self.rng.random.return_value = 0.0
        self.cenario = CenarioTatico([self.a, self.b], {("a", "b"): 5.0}, {1.0: 1.0})
        self.motor = GerenciadorDeCombate(self.a, self.b, cenario=self.cenario, gerador=random.Random(0))
        assert self.motor.tentar_detecao(self.a, self.b)
        assert self.motor.tentar_detecao(self.b, self.a)
        self.motor.gerador = self.rng
        self.ab = AcaoDisparo("a-para-b", self.a, self.b, self.arma_a)
        self.ba = AcaoDisparo("b-para-a", self.b, self.a, self.arma_b)

    def defendido(self, identificador="a-para-b", custo=2):
        return AcaoDisparo(identificador, self.a, self.b, self.arma_a,
                           defesa=self.defesa, consumo_defensivo=custo)

    def test_simultaneos_respondem_mesmo_apos_dano_no_mesmo_lote(self):
        resultados = self.motor.resolver_rodada([self.ab, self.ba])
        self.assertEqual([r.situacao for r in resultados], ["impacto", "impacto"])
        self.assertEqual((self.a.pontos_de_vida, self.b.pontos_de_vida), (0.0, 0.0))
        self.assertEqual((self.arma_a.quantidade, self.arma_b.quantidade), (2, 2))

    def test_iniciativa_suspende_acao_ainda_nao_iniciada_sem_debito(self):
        resultados = self.motor.resolver_rodada([self.ab, self.ba], iniciativa=self.a)
        self.assertEqual(resultados[1].situacao, "nao_iniciada")
        self.assertEqual(self.a.pontos_de_vida, 100.0)
        self.assertEqual(self.arma_b.quantidade, 3)
        self.assertEqual(resultados[1].consumos, ())

    def test_iniciativa_do_outro_lado_nao_depende_da_ordem_da_lista(self):
        resultados = self.motor.resolver_rodada([self.ab, self.ba], iniciativa=self.b)
        por_id = {r.acao_id: r for r in resultados}
        self.assertEqual(por_id["a-para-b"].situacao, "nao_iniciada")
        self.assertEqual(self.b.pontos_de_vida, 100.0)
        self.assertEqual(self.arma_a.quantidade, 3)

    def test_dano_nao_total_permite_resposta_na_segunda_fase(self):
        self.arma_a.dano = 10.0
        resultados = self.motor.resolver_rodada([self.ab, self.ba], iniciativa=self.a)
        self.assertEqual([(r.fase, r.situacao) for r in resultados], [(1, "impacto"), (2, "impacto")])
        self.assertEqual((self.a.pontos_de_vida, self.b.pontos_de_vida), (0.0, 90.0))
        self.assertEqual((self.arma_a.quantidade, self.arma_b.quantidade), (2, 2))

    def test_interceptacao_na_primeira_fase_preserva_resposta(self):
        resultados = self.motor.resolver_rodada([self.defendido(), self.ba], iniciativa=self.a)
        self.assertEqual([r.situacao for r in resultados], ["interceptado", "impacto"])
        self.assertEqual(self.b.pontos_de_vida, 100.0)
        self.assertEqual((self.arma_a.quantidade, self.arma_b.quantidade, self.defesa.quantidade), (2, 2, 2))

    def test_defesa_bem_sucedida_debita_custo_explicito(self):
        resultado, = self.motor.resolver_rodada([self.defendido()])
        self.assertEqual(resultado.situacao, "interceptado")
        self.assertEqual(self.b.pontos_de_vida, 100.0)
        self.assertEqual((self.arma_a.quantidade, self.defesa.quantidade), (2, 2))
        consumo = resultado.consumos[1]
        self.assertEqual((consumo.estoque_id, consumo.antes, consumo.quantidade, consumo.depois),
                         ("defensivo-b", 4, 2, 2))

    def test_defesa_que_falha_tambem_consume(self):
        self.rng.random.side_effect = [0.9, 0.0]
        resultado, = self.motor.resolver_rodada([self.defendido()])
        self.assertEqual(resultado.situacao, "impacto")
        self.assertEqual(self.defesa.quantidade, 2)
        self.assertEqual(resultado.sorteio_defesa, 0.9)

    def test_defesa_sem_estoque_nao_sorteia_nem_consume(self):
        self.defesa.quantidade = 1
        resultado, = self.motor.resolver_rodada([self.defendido()])
        self.assertEqual(resultado.situacao, "impacto")
        self.assertEqual(self.defesa.quantidade, 1)
        self.assertIsNone(resultado.sorteio_defesa)
        self.assertEqual(len(resultado.consumos), 1)
        self.rng.random.assert_called_once()

    def test_sem_defesa_declarada_nao_existe_defesa_infinita(self):
        self.b.capacidade_defesa_ponto = 1.0
        resultado, = self.motor.resolver_rodada([self.ab])
        self.assertEqual(resultado.situacao, "impacto")
        self.assertEqual(self.defesa.quantidade, 4)

    def test_custo_ausente_ou_invalido_impede_todo_o_lote(self):
        for custo in (None, 0, -1, 0.5, True):
            with self.subTest(custo=custo):
                with self.assertRaises(ValueError):
                    self.motor.resolver_rodada([self.ba, self.defendido(custo=custo)])
                self.assertEqual((self.arma_a.quantidade, self.arma_b.quantidade, self.defesa.quantidade),
                                 (3, 3, 4))
                self.assertEqual((self.a.pontos_de_vida, self.b.pontos_de_vida), (100.0, 100.0))
                self.rng.random.assert_not_called()

    def test_disputa_defensiva_nao_favorece_primeiro_id(self):
        self.defesa.quantidade = 3
        with self.assertRaisesRegex(ValueError, "[Cc]onflito"):
            self.motor.resolver_rodada([self.defendido("x"), self.defendido("y")])
        self.assertEqual((self.arma_a.quantidade, self.defesa.quantidade), (3, 3))
        self.rng.random.assert_not_called()

    def test_reservas_ofensivas_nao_excedem_estoque(self):
        self.arma_a.quantidade = 1
        outra = AcaoDisparo("outra", self.a, self.b, self.arma_a)
        with self.assertRaisesRegex(ValueError, "[Cc]onflito"):
            self.motor.resolver_rodada([self.ab, outra])
        self.assertEqual(self.arma_a.quantidade, 1)
        self.rng.random.assert_not_called()

    def test_danos_simultaneos_compartilham_mesma_vida_inicial(self):
        outra = AcaoDisparo("outra", self.a, self.b, self.arma_a)
        resultados = self.motor.resolver_rodada([self.ab, outra])
        self.assertEqual([r.vida_antes for r in resultados], [100.0, 100.0])
        self.assertEqual([r.vida_apos_lote for r in resultados], [0.0, 0.0])
        self.assertEqual(self.b.pontos_de_vida, 0.0)

    def test_ids_duplicados_e_estoque_compartilhado_recusados(self):
        with self.assertRaises(ValueError):
            self.motor.resolver_rodada([self.ab, self.ab])
        self.a.armamentos.append(self.defesa)
        with self.assertRaises(ValueError):
            self.motor.resolver_rodada([self.ab])
        self.rng.random.assert_not_called()

    def test_ordem_de_entrada_nao_muda_resultados_com_mesma_semente(self):
        self.arma_a.pk = self.arma_b.pk = 0.5
        self.motor.gerador = random.Random(17)
        r1 = self.motor.resolver_rodada([self.ab, self.ba])
        self.setUp()
        self.arma_a.pk = self.arma_b.pk = 0.5
        self.motor.gerador = random.Random(17)
        r2 = self.motor.resolver_rodada([self.ba, self.ab])
        self.assertEqual(r1, r2)

    def test_falha_no_gerador_nao_aplica_lote_parcial(self):
        self.rng.random.side_effect = [0.0, RuntimeError("falha de ensaio")]
        with self.assertRaises(RuntimeError):
            self.motor.resolver_rodada([self.ab, self.ba])
        self.assertEqual((self.arma_a.quantidade, self.arma_b.quantidade), (3, 3))
        self.assertEqual((self.a.pontos_de_vida, self.b.pontos_de_vida), (100.0, 100.0))


if __name__ == "__main__":
    unittest.main()
