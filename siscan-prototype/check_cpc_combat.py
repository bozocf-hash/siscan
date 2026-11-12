"""Verifica somente a regra sintética de disparo, sem bancos ou exercício ativo."""

import random
import unittest
from unittest.mock import Mock

from cpc_combat import GerenciadorDeCombate
from cpc_models import Armamento, MeioNaval, VetorAereo
from cpc_scenario import CenarioTatico


class CombateTests(unittest.TestCase):
    def setUp(self):
        self.arma = Armamento(
            identificador="arma-ficticia", tipo="missil_antinavio",
            quantidade=2, pk=0.7, dano=30.0, alcance_maximo=20.0,
        )
        self.atacante = VetorAereo(
            identificador="aereo-ficticio", pontos_de_vida=100.0,
            assinatura_radar=1.0, velocidade=0.0, raio_de_acao=0.0,
            teto_operacional=0.0, armamentos=[self.arma],
            alcance_radar=20.0, probabilidade_deteccao=1.0,
        )
        self.defesa = Armamento(
            identificador="defesa-ficticia", tipo="defesa_ponto", quantidade=10,
        )
        self.defensor = MeioNaval(
            identificador="naval-ficticio", pontos_de_vida=80.0,
            assinatura_radar=1.0, velocidade=0.0, capacidade_defesa_ponto=0.4,
            armamentos=[self.defesa],
            alcance_radar=20.0, probabilidade_deteccao=1.0,
        )
        self.rng = Mock(spec=random.Random)
        self.cenario = CenarioTatico([self.atacante, self.defensor],
                                    {("aereo-ficticio", "naval-ficticio"): 5.0}, {1.0: 1.0})
        self.motor = GerenciadorDeCombate(self.atacante, self.defensor,
                                         cenario=self.cenario, gerador=random.Random(0))
        assert self.motor.tentar_detecao(self.atacante, self.defensor)
        assert self.motor.tentar_detecao(self.defensor, self.atacante)
        self.motor.gerador = self.rng

    def disparar(self):
        parametros = dict(defesa=self.defesa, consumo_defensivo=2) if isinstance(self.defensor, MeioNaval) else {}
        return self.motor.resolver_disparo(self.atacante, self.defensor, self.arma, **parametros)

    def test_interceptacao_consume_arma_sem_causar_dano(self):
        self.rng.random.side_effect = [0.2]
        self.assertIn("interceptado", self.disparar())
        self.assertEqual(self.defensor.pontos_de_vida, 80.0)
        self.assertEqual(self.arma.quantidade, 1)
        self.assertEqual(self.defesa.quantidade, 8)
        self.assertEqual(self.rng.random.call_count, 1)

    def test_impacto_e_narrativa(self):
        self.rng.random.side_effect = [0.8, 0.2]
        relato = self.disparar()
        for texto in ("arma-ficticia", "aereo-ficticio", "naval-ficticio", "falhou", "30"):
            self.assertIn(texto, relato)
        self.assertEqual(self.defensor.pontos_de_vida, 50.0)
        self.assertEqual(self.arma.quantidade, 1)

    def test_erro_tambem_consume_arma(self):
        self.rng.random.side_effect = [0.8, 0.9]
        self.assertIn("errou", self.disparar())
        self.assertEqual(self.defensor.pontos_de_vida, 80.0)
        self.assertEqual(self.arma.quantidade, 1)

    def test_dano_limitado_a_vida_restante(self):
        self.defensor.pontos_de_vida = 10.0
        self.rng.random.side_effect = [0.8, 0.2]
        self.assertIn("10", self.disparar())
        self.assertEqual(self.defensor.pontos_de_vida, 0.0)

    def test_extremos_de_probabilidade(self):
        self.defensor.capacidade_defesa_ponto = 0.0
        self.arma.pk = 0.0
        self.rng.random.side_effect = [0.0, 0.0]
        self.assertIn("errou", self.disparar())
        self.defensor.capacidade_defesa_ponto = 1.0
        self.rng.random.side_effect = [0.999999]
        self.assertIn("interceptado", self.disparar())

    def test_valores_invalidos_nao_mutam_estado(self):
        for atributo, valor in [("pk", -0.1), ("pk", 1.1), ("pk", float("nan")),
                                ("pk", None), ("dano", -1), ("dano", float("inf")),
                                ("quantidade", 0), ("quantidade", 1.5)]:
            with self.subTest(atributo=atributo, valor=valor):
                anterior = getattr(self.arma, atributo)
                setattr(self.arma, atributo, valor)
                with self.assertRaises(ValueError):
                    self.disparar()
                self.assertEqual(self.defensor.pontos_de_vida, 80.0)
                self.rng.random.assert_not_called()
                setattr(self.arma, atributo, anterior)

    def test_defesa_desconhecida_nao_vira_zero(self):
        self.defensor.capacidade_defesa_ponto = None
        with self.assertRaises(ValueError):
            self.disparar()
        self.assertEqual(self.arma.quantidade, 2)

    def test_defesa_invalida_recusada_antes_do_consumo(self):
        for valor in (-0.1, 1.1, float("nan")):
            with self.subTest(valor=valor):
                self.defensor.capacidade_defesa_ponto = valor
                with self.assertRaises(ValueError):
                    self.disparar()
                self.assertEqual(self.arma.quantidade, 2)
                self.rng.random.assert_not_called()

    def test_estoque_esgotado_impede_novo_disparo(self):
        self.arma.quantidade = 1
        self.rng.random.side_effect = [0.2]
        self.disparar()
        with self.assertRaises(ValueError):
            self.disparar()
        self.assertEqual(self.arma.quantidade, 0)
        self.assertEqual(self.rng.random.call_count, 1)

    def test_arma_nao_embarcada_e_par_diferente_recusados(self):
        self.atacante.armamentos.clear()
        with self.assertRaises(ValueError):
            self.disparar()
        with self.assertRaises(ValueError):
            self.motor.resolver_disparo(self.defensor, self.atacante, self.arma)
        self.assertEqual(self.arma.quantidade, 2)

    def test_defensor_aereo_nao_recebe_defesa_naval(self):
        self.defensor = VetorAereo(
            identificador="outro-aereo", pontos_de_vida=100.0,
            assinatura_radar=1.0, velocidade=0.0, raio_de_acao=0.0, teto_operacional=0.0,
            alcance_radar=20.0, probabilidade_deteccao=1.0,
        )
        cenario = CenarioTatico([self.atacante, self.defensor],
                               {("aereo-ficticio", "outro-aereo"): 5.0}, {1.0: 1.0})
        self.motor = GerenciadorDeCombate(self.atacante, self.defensor,
                                         cenario=cenario, gerador=random.Random(0))
        assert self.motor.tentar_detecao(self.atacante, self.defensor)
        self.motor.gerador = self.rng
        self.rng.random.side_effect = [0.1]
        self.assertIn("Impacto", self.disparar())
        self.assertEqual(self.rng.random.call_count, 1)

    def test_semente_reproduz_relato(self):
        r1 = GerenciadorDeCombate(self.atacante, self.defensor,
                                  cenario=self.cenario, gerador=random.Random(7))
        relato = r1.resolver_disparo(self.atacante, self.defensor, self.arma)
        self.setUp()
        r2 = GerenciadorDeCombate(self.atacante, self.defensor,
                                  cenario=self.cenario, gerador=random.Random(7))
        self.assertEqual(relato, r2.resolver_disparo(self.atacante, self.defensor, self.arma))


if __name__ == "__main__":
    unittest.main()
