"""Verifica detecção e elegibilidade fictícias, sem dados operacionais."""

import random
import unittest
from unittest.mock import Mock

from cpc_combat import GerenciadorDeCombate
from cpc_models import Armamento, MeioNaval
from cpc_scenario import CenarioTatico


class DeteccaoTests(unittest.TestCase):
    def setUp(self):
        self.arma = Armamento(identificador="arma", tipo="missil_antinavio",
                               quantidade=2, pk=1.0, dano=10.0, alcance_maximo=10.0)
        args = dict(pontos_de_vida=100.0, assinatura_radar=2.0, velocidade=0.0,
                    capacidade_defesa_ponto=None, alcance_radar=10.0, probabilidade_deteccao=0.8)
        self.a = MeioNaval(identificador="a", armamentos=[self.arma], **args)
        self.b = MeioNaval(identificador="b", **args)
        self.cenario = CenarioTatico([self.a, self.b], {("a", "b"): 10.0}, {2.0: 0.5})
        self.rng = Mock(spec=random.Random)
        self.motor = GerenciadorDeCombate(self.a, self.b, cenario=self.cenario, gerador=self.rng)

    def test_limite_radar_inclusivo_e_probabilidade_com_fator(self):
        self.rng.random.return_value = 0.39
        self.assertTrue(self.motor.tentar_detecao(self.a, self.b))
        self.assertEqual(self.cenario.contatos_detectados(self.a), frozenset({"b"}))

    def test_acima_da_probabilidade_efetiva_falha(self):
        self.rng.random.return_value = 0.4
        self.assertFalse(self.motor.tentar_detecao(self.a, self.b))
        self.assertFalse(self.cenario.contatos_detectados(self.a))

    def test_fora_do_radar_nao_sorteia(self):
        self.a.alcance_radar = 9.0
        self.assertFalse(self.motor.tentar_detecao(self.a, self.b))
        self.rng.random.assert_not_called()

    def test_contatos_nao_sao_reciprocos(self):
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        self.assertFalse(self.cenario.contatos_detectados(self.b))

    def test_disparo_sem_contato_nao_consume_nem_sorteia(self):
        with self.assertRaisesRegex(ValueError, "[Cc]ontato"):
            self.motor.resolver_disparo(self.a, self.b, self.arma)
        self.assertEqual(self.arma.quantidade, 2)
        self.assertEqual(self.b.pontos_de_vida, 100.0)
        self.rng.random.assert_not_called()

    def test_limite_da_arma_inclusivo(self):
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        self.motor.resolver_disparo(self.a, self.b, self.arma)
        self.assertEqual(self.arma.quantidade, 1)
        self.assertEqual(self.b.pontos_de_vida, 90.0)

    def test_arma_fora_de_alcance_nao_consume(self):
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        self.rng.reset_mock()
        self.arma.alcance_maximo = 9.0
        with self.assertRaisesRegex(ValueError, "[Aa]lcance"):
            self.motor.resolver_disparo(self.a, self.b, self.arma)
        self.assertEqual(self.arma.quantidade, 2)
        self.rng.random.assert_not_called()

    def test_assinatura_desconhecida_ou_sem_rubrica_nao_vira_zero(self):
        for assinatura in (None, 3.0):
            self.b.assinatura_radar = assinatura
            with self.assertRaises(ValueError):
                self.motor.tentar_detecao(self.a, self.b)
        self.rng.random.assert_not_called()

    def test_nova_tentativa_falha_remove_contato(self):
        self.rng.random.side_effect = [0.1, 0.9]
        self.assertTrue(self.motor.tentar_detecao(self.a, self.b))
        self.assertFalse(self.motor.tentar_detecao(self.a, self.b))
        self.assertFalse(self.cenario.contatos_detectados(self.a))

    def test_mudar_radar_ou_assinatura_invalida_contato(self):
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        self.b.assinatura_radar = 3.0
        self.assertFalse(self.cenario.contatos_detectados(self.a))
        self.b.assinatura_radar = 2.0
        self.motor.tentar_detecao(self.a, self.b)
        self.a.probabilidade_deteccao = 0.7
        self.assertFalse(self.cenario.contatos_detectados(self.a))

    def test_novo_cenario_nao_herda_contatos(self):
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        outro = CenarioTatico([self.a, self.b], {("a", "b"): 10.0}, {2.0: 0.5})
        motor = GerenciadorDeCombate(self.a, self.b, cenario=outro)
        with self.assertRaises(ValueError):
            motor.resolver_disparo(self.a, self.b, self.arma)

    def test_sem_cenario_nao_existe_bypass(self):
        motor = GerenciadorDeCombate(self.a, self.b)
        with self.assertRaises(ValueError):
            motor.resolver_disparo(self.a, self.b, self.arma)
        self.assertEqual(self.arma.quantidade, 2)

    def test_matriz_simetrica_e_completa(self):
        self.assertEqual(self.cenario.distancia(self.b, self.a), 10.0)
        for matriz in ({}, {("a", "b"): -1.0}, {("a", "b"): float("nan")},
                       {("a", "b"): 10.0, ("b", "a"): 9.0}):
            with self.subTest(matriz=matriz):
                with self.assertRaises(ValueError):
                    CenarioTatico([self.a, self.b], matriz, {2.0: 0.5})

    def test_probabilidades_invalidas_e_alcance_desconhecido(self):
        for atributo, valor in (("probabilidade_deteccao", 1.1), ("probabilidade_deteccao", None),
                                ("alcance_radar", None), ("alcance_radar", float("inf"))):
            with self.subTest(atributo=atributo, valor=valor):
                anterior = getattr(self.a, atributo)
                setattr(self.a, atributo, valor)
                with self.assertRaises(ValueError):
                    self.motor.tentar_detecao(self.a, self.b)
                setattr(self.a, atributo, anterior)

    def test_zero_nao_e_confundido_com_dado_ausente(self):
        self.cenario = CenarioTatico([self.a, self.b], {("a", "b"): 0.0}, {2.0: 1.0})
        self.motor.cenario = self.cenario
        self.a.alcance_radar = self.arma.alcance_maximo = 0.0
        self.a.probabilidade_deteccao = 1.0
        self.rng.random.return_value = 0.999
        self.assertTrue(self.motor.tentar_detecao(self.a, self.b))
        self.motor.resolver_disparo(self.a, self.b, self.arma)
        self.assertEqual(self.arma.quantidade, 1)

    def test_probabilidade_zero_nao_detecta_mesmo_com_sorteio_zero(self):
        self.a.probabilidade_deteccao = 0.0
        self.rng.random.return_value = 0.0
        self.assertFalse(self.motor.tentar_detecao(self.a, self.b))

    def test_alcance_da_arma_desconhecido_bloqueia_disparo(self):
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        self.rng.reset_mock()
        for valor in (None, -1.0, float("nan")):
            self.arma.alcance_maximo = valor
            with self.assertRaises(ValueError):
                self.motor.resolver_disparo(self.a, self.b, self.arma)
            self.assertEqual(self.arma.quantidade, 2)
            self.rng.random.assert_not_called()

    def test_matriz_para_tres_unidades_e_copia_das_entradas(self):
        c = MeioNaval(identificador="c", pontos_de_vida=100.0, assinatura_radar=2.0,
                       velocidade=0.0, capacidade_defesa_ponto=None)
        matriz = {("a", "b"): 10.0, ("b", "c"): 12.0, ("a", "c"): 15.0}
        fatores = {2.0: 0.5}
        cenario = CenarioTatico([self.a, self.b, c], matriz, fatores)
        matriz["a", "b"] = 999.0
        fatores[2.0] = 0.0
        self.assertEqual(cenario.distancia(self.a, self.b), 10.0)
        self.assertEqual(cenario.distancia(c, self.a), 15.0)
        self.assertEqual(cenario.fator_assinatura(2.0), 0.5)

    def test_contato_ausente_de_uma_acao_bloqueia_rodada_inteira(self):
        from cpc_combat import AcaoDisparo
        outra = Armamento(identificador="outra", tipo="missil_antinavio", quantidade=1,
                          pk=1.0, dano=10.0, alcance_maximo=10.0)
        self.b.armamentos.append(outra)
        self.rng.random.return_value = 0.0
        self.motor.tentar_detecao(self.a, self.b)
        self.rng.reset_mock()
        with self.assertRaises(ValueError):
            self.motor.resolver_rodada([AcaoDisparo("ab", self.a, self.b, self.arma),
                                        AcaoDisparo("ba", self.b, self.a, outra)])
        self.assertEqual((self.arma.quantidade, outra.quantidade), (2, 1))
        self.rng.random.assert_not_called()


if __name__ == "__main__":
    unittest.main()
