"""Turnos sintéticos: relógio global, combustível e geometria, sem banco ativo."""

import random
import unittest

from cpc_combat import AcaoDisparo, GerenciadorDeCombate
from cpc_models import Armamento, MeioNaval, VetorAereo
from cpc_scenario import CenarioTatico
from cpc_time import SimulacaoTemporal


class TempoTests(unittest.TestCase):
    def setUp(self):
        self.arma = Armamento(identificador="arma", tipo="missil_antinavio",
                               quantidade=3, pk=1.0, dano=1.0, alcance_maximo=20.0)
        self.a = VetorAereo(
            identificador="a", pontos_de_vida=100.0, assinatura_radar=1.0,
            velocidade=60.0, raio_de_acao=0.0, teto_operacional=0.0,
            alcance_radar=20.0, probabilidade_deteccao=1.0, armamentos=[self.arma],
            combustivel_atual=5.0, taxa_consumo_combustivel=2.0,
            combustivel_minimo_retorno=1.0,
        )
        self.b = MeioNaval(identificador="b", pontos_de_vida=100.0,
                           assinatura_radar=1.0, velocidade=0.0, capacidade_defesa_ponto=None,
                           alcance_radar=20.0, probabilidade_deteccao=1.0)
        self.cenario = CenarioTatico([self.a, self.b], {("a", "b"): 10.0}, {1.0: 1.0},
                                     posicoes={"a": (0.0, 0.0), "b": (10.0, 0.0)})
        self.motor = GerenciadorDeCombate(self.a, self.b, cenario=self.cenario, gerador=random.Random(7))
        self.sim = SimulacaoTemporal(self.motor, rumos={"a": 90.0}, rumos_evasao={"a": 270.0})
        self.acao = AcaoDisparo("ab", self.a, self.b, self.arma)

    def test_minuto_consume_move_detecta_e_dispara(self):
        turno = self.sim.avancar_turno([self.acao])
        self.assertEqual((turno.minuto, self.sim.minuto_atual), (1, 1))
        self.assertEqual(self.a.combustivel_atual, 3.0)
        self.assertAlmostEqual(self.cenario.distancia(self.a, self.b), 9.0)
        self.assertEqual(self.arma.quantidade, 2)
        self.assertEqual(self.b.pontos_de_vida, 99.0)

    def test_reserva_nao_padrao_suspende_ataques(self):
        self.a.combustivel_minimo_retorno = 3.0
        turno = self.sim.avancar_turno([self.acao])
        self.assertEqual(self.a.estado_voo, "evadindo")
        self.assertEqual(self.arma.quantidade, 3)
        self.assertFalse(turno.combate)

    def test_exaustao_limita_tempo_de_movimento(self):
        self.a.combustivel_atual = 1.0
        self.a.combustivel_minimo_retorno = 0.0
        turno = self.sim.avancar_turno([self.acao])
        self.assertEqual(self.a.estado_voo, "perda_proposta")
        self.assertEqual(self.a.combustivel_atual, 0.0)
        self.assertAlmostEqual(self.cenario.distancia(self.a, self.b), 9.5)
        self.assertEqual(self.a.pontos_de_vida, 100.0)
        self.assertFalse(turno.combate)

    def test_aeronave_pousada_nao_move_ou_consume(self):
        self.a.estado_voo = "pousado"
        self.sim.avancar_turno([self.acao])
        self.assertEqual(self.a.combustivel_atual, 5.0)
        self.assertEqual(self.cenario.distancia(self.a, self.b), 10.0)
        self.assertEqual(self.arma.quantidade, 3)

    def test_evasao_continua_consumindo_sem_novos_disparos(self):
        for _ in range(3):
            self.sim.avancar_turno([self.acao])
        self.assertEqual((self.a.combustivel_atual, self.a.estado_voo), (0.0, "perda_proposta"))
        self.assertEqual(self.arma.quantidade, 2)
        self.assertAlmostEqual(self.cenario.distancia(self.a, self.b), 8.5)
        self.assertEqual(self.sim.minuto_atual, 3)

    def test_dois_movimentos_atualizam_distancia_por_posicoes(self):
        self.b.velocidade = 60.0
        self.sim.rumos["b"] = 270.0
        self.sim.avancar_turno([])
        self.assertAlmostEqual(self.cenario.distancia(self.a, self.b), 8.0)

    def test_sem_municao_o_relogio_e_combustivel_continuam(self):
        self.arma.quantidade = 0
        turno = self.sim.avancar_turno([self.acao])
        self.assertEqual(self.sim.minuto_atual, 1)
        self.assertEqual(self.a.combustivel_atual, 3.0)
        self.assertFalse(turno.combate)

    def test_reserva_ou_geometria_ausente_nao_avanca_parcialmente(self):
        self.a.combustivel_minimo_retorno = None
        with self.assertRaises(ValueError):
            self.sim.avancar_turno([self.acao])
        self.assertEqual((self.a.combustivel_atual, self.sim.minuto_atual), (5.0, 0))
        self.assertEqual(self.cenario.distancia(self.a, self.b), 10.0)

    def test_falha_de_combate_reverte_minuto_inclusive_gerador(self):
        self.arma.pk = 2.0
        antes = self.motor.gerador.getstate()
        with self.assertRaises(ValueError):
            self.sim.avancar_turno([self.acao])
        self.assertEqual(self.motor.gerador.getstate(), antes)
        self.assertEqual((self.a.combustivel_atual, self.arma.quantidade, self.sim.minuto_atual), (5.0, 3, 0))
        self.assertEqual(self.cenario.distancia(self.a, self.b), 10.0)

    def test_perda_proposta_nao_consume_em_turno_posterior(self):
        self.a.combustivel_atual = 0.0
        for _ in range(2):
            self.sim.avancar_turno([])
        self.assertEqual(self.a.estado_voo, "perda_proposta")
        self.assertEqual(self.cenario.distancia(self.a, self.b), 10.0)

    def test_cruzar_reserva_no_meio_do_minuto_muda_rumo_no_instante(self):
        self.a.combustivel_atual = 4.0
        self.a.combustivel_minimo_retorno = 3.0
        self.sim.avancar_turno([self.acao])
        self.assertEqual((self.a.combustivel_atual, self.a.estado_voo), (2.0, "evadindo"))
        self.assertAlmostEqual(self.cenario.distancia(self.a, self.b), 10.0)
        self.assertEqual(self.arma.quantidade, 3)

    def test_relogio_global_consumo_de_aeronave_fora_do_confronto(self):
        c = VetorAereo(identificador="c", pontos_de_vida=100.0, assinatura_radar=None,
                       velocidade=0.0, raio_de_acao=0.0, teto_operacional=0.0,
                       combustivel_atual=5.0, taxa_consumo_combustivel=1.0,
                       combustivel_minimo_retorno=0.0)
        self.cenario = CenarioTatico(
            [self.a, self.b, c], {("a", "b"): 10.0, ("a", "c"): 20.0, ("b", "c"): 10.0},
            {1.0: 1.0}, posicoes={"a": (0.0, 0.0), "b": (10.0, 0.0), "c": (20.0, 0.0)})
        self.motor.cenario = self.cenario
        self.sim.avancar_turno([])
        self.assertEqual((self.a.combustivel_atual, c.combustivel_atual), (3.0, 4.0))
        self.assertEqual(self.sim.minuto_atual, 1)

    def test_movimento_expira_contatos_mesmo_sem_ataques(self):
        self.assertTrue(self.motor.tentar_detecao(self.a, self.b))
        self.sim.avancar_turno([])
        self.assertFalse(self.cenario.contatos_detectados(self.a))

    def test_falta_de_rumo_ou_posicao_nao_inventa_movimento(self):
        self.sim.rumos_evasao.clear()
        with self.assertRaises(ValueError):
            self.sim.avancar_turno([])
        self.assertEqual((self.a.combustivel_atual, self.sim.minuto_atual), (5.0, 0))
        self.sim.rumos_evasao["a"] = 270.0
        self.motor.cenario = CenarioTatico([self.a, self.b], {("a", "b"): 10.0}, {1.0: 1.0})
        with self.assertRaises(ValueError):
            self.sim.avancar_turno([])
        self.assertEqual((self.a.combustivel_atual, self.sim.minuto_atual), (5.0, 0))

    def test_estado_de_evasao_tambem_bloqueia_chamada_direta(self):
        self.a.estado_voo = "evadindo"
        self.assertTrue(self.motor.tentar_detecao(self.a, self.b))
        with self.assertRaises(ValueError):
            self.motor.resolver_disparo(self.a, self.b, self.arma)
        self.assertEqual(self.arma.quantidade, 3)

    def test_posicoes_incompativeis_com_matriz_sao_recusadas(self):
        with self.assertRaises(ValueError):
            CenarioTatico([self.a, self.b], {("a", "b"): 10.0}, {1.0: 1.0},
                           posicoes={"a": (0.0, 0.0), "b": (11.0, 0.0)})


if __name__ == "__main__":
    unittest.main()
