"""Verifica trilha estruturada e exportação pós-ação sem bancos oficiais."""

import csv
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from cpc_combat import AcaoDisparo, GerenciadorDeCombate
from cpc_models import Armamento, MeioNaval, VetorAereo
from cpc_scenario import CenarioTatico
from cpc_time import SimulacaoTemporal


class RelatorioTests(unittest.TestCase):
    def setUp(self):
        self.preparar()

    def preparar(self, nome="aereo-ficticio"):
        self.arma = Armamento(identificador="arma", tipo="missil_antinavio", quantidade=3,
                               pk=1.0, dano=1.0, alcance_maximo=10.0)
        self.defesa = Armamento(identificador="pacotes", tipo="defesa_ponto", quantidade=4)
        self.a = VetorAereo(identificador=nome, pontos_de_vida=100.0, assinatura_radar=1.0,
                           velocidade=1.0, raio_de_acao=0.0, teto_operacional=0.0,
                           armamentos=[self.arma], alcance_radar=10.0, probabilidade_deteccao=1.0,
                           combustivel_atual=4.0, taxa_consumo_combustivel=1.0,
                           combustivel_minimo_retorno=0.0)
        self.b = MeioNaval(identificador="naval-ficticio", pontos_de_vida=2.0,
                           assinatura_radar=1.0, velocidade=0.0, capacidade_defesa_ponto=0.0,
                           armamentos=[self.defesa])
        cenario = CenarioTatico([self.a, self.b], {(nome, self.b.identificador): 1.0}, {1.0: 1.0},
                                posicoes={nome: (0.0, 0.0), self.b.identificador: (1.0, 0.0)})
        self.motor = GerenciadorDeCombate(self.a, self.b, cenario=cenario, gerador=random.Random(7))
        self.sim = SimulacaoTemporal(self.motor, rumos={nome: 270.0}, rumos_evasao={nome: 270.0})
        self.acao = AcaoDisparo("ab", self.a, self.b, self.arma, self.defesa, 2)

    def test_eventos_do_turno_sao_estruturados_e_correlacionados(self):
        self.sim.avancar_turno([self.acao])
        eventos = self.sim.eventos
        tipos = {e["tipo"] for e in eventos}
        self.assertTrue({"movimento", "consumo_combustivel", "deteccao", "disparo", "acerto",
                         "consumo_armamento", "dano_aplicado", "turno_concluido"} <= tipos)
        self.assertEqual([e["sequencia"] for e in eventos], list(range(1, len(eventos) + 1)))
        self.assertTrue(all(e["minuto"] == 1 and e["execucao_id"] for e in eventos))
        self.assertTrue(all(isinstance(e["dados"], dict) for e in eventos))

    def test_destruicao_e_perda_aerea_registradas_uma_vez(self):
        for _ in range(60):
            self.sim.avancar_turno([self.acao])
        tipos = [e["tipo"] for e in self.sim.eventos]
        self.assertEqual(tipos.count("destruicao_proposta"), 1)
        self.assertEqual(tipos.count("perda_aerea_proposta"), 1)
        self.assertEqual(tipos.count("turno_concluido"), 60)
        balanco = self.sim.historico.balanco()
        self.assertEqual(balanco["misseis_gastos"], 2)
        self.assertEqual(balanco["recursos_defensivos_gastos"], 4)
        self.assertEqual(balanco["quantidade_perdas_propostas"], 2)

    def test_exportacao_txt_tem_cabecalho_e_rodape(self):
        self.sim.avancar_turno([self.acao])
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self.sim.exportar_relatorio_pos_acao(Path(pasta) / "ensaio.txt")
            texto = caminho.read_text(encoding="utf-8")
            self.assertIn("Estado inicial das forças", texto)
            self.assertIn("Batalha Encerrada", texto)
            self.assertIn("Sobreviventes:", texto)
            self.assertIn("Mísseis gastos: 1", texto)
            self.assertIn("não adjudicados", texto)

    def test_csv_possui_secoes_e_numeros_em_colunas(self):
        self.sim.avancar_turno([self.acao])
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self.sim.exportar_relatorio_pos_acao(Path(pasta) / "ensaio.csv")
            with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo, delimiter=";"))
            self.assertEqual({r["secao"] for r in linhas}, {"cabecalho", "evento", "rodape"})
            consumo = next(r for r in linhas if r["tipo"] == "consumo_combustivel")
            self.assertEqual(float(consumo["consumido_kg"]), 1.0)
            balanco = json.loads(linhas[-1]["dados_json"])
            self.assertEqual(balanco["misseis_gastos"], 1)

    def test_exportar_nao_sobrescreve_arquivo_existente(self):
        self.sim.avancar_turno([])
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "original.txt"
            caminho.write_text("preservar", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self.sim.exportar_relatorio_pos_acao(caminho)
            self.assertEqual(caminho.read_text(encoding="utf-8"), "preservar")

    def test_exportacao_falha_nao_deixa_arquivo_parcial(self):
        self.sim.avancar_turno([])
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "incompleto.txt"
            with patch("cpc_reporting._json", side_effect=ValueError("falha de serialização")):
                with self.assertRaises(ValueError):
                    self.sim.exportar_relatorio_pos_acao(caminho)
            self.assertFalse(caminho.exists())

    def test_falha_do_turno_nao_publica_eventos_parciais(self):
        self.arma.pk = 2.0
        with self.assertRaises(ValueError):
            self.sim.avancar_turno([self.acao])
        self.assertEqual(self.sim.eventos, [])
        self.assertEqual(self.motor.eventos, [])

    def test_cabecalho_congela_estado_antes_do_primeiro_turno(self):
        self.a.combustivel_atual = 9.0
        self.sim.avancar_turno([])
        self.a.combustivel_atual = 999.0
        self.assertEqual(self.sim.historico.estado_inicial[0]["combustivel_kg"], 9.0)
        self.assertEqual(self.sim.historico.estado_final[0]["combustivel_kg"], 8.0)
        eventos = self.sim.eventos
        eventos.clear()
        self.assertTrue(self.sim.eventos)

    def test_csv_protege_celula_formula_e_preserva_id_no_json(self):
        self.preparar(nome="=2+2")
        self.sim.avancar_turno([])
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self.sim.exportar_relatorio_pos_acao(Path(pasta) / "ensaio.csv")
            with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo, delimiter=";"))
            inicio = next(r for r in linhas if r["tipo"] == "estado_inicial" and r["unidade_id"] == "'=2+2")
            self.assertEqual(json.loads(inicio["dados_json"])["unidade_id"], "=2+2")

    def test_imobilizacao_nao_vira_perda(self):
        self.b.combustivel_atual = 0.0
        self.sim.avancar_turno([])
        balanco = self.sim.historico.balanco()
        self.assertIn(self.b.identificador, balanco["sobreviventes"])
        self.assertIn(self.b.identificador, balanco["imobilizados_por_combustivel"])
        self.assertEqual(balanco["quantidade_perdas_propostas"], 0)

    def test_movimento_ida_e_volta_nao_e_confundido_com_parado(self):
        self.a.velocidade = 60.0
        self.a.combustivel_atual = 2.0
        self.a.taxa_consumo_combustivel = 2.0
        self.a.combustivel_minimo_retorno = 1.0
        self.sim.rumos[self.a.identificador] = 90.0
        self.sim.avancar_turno([])
        movimento = next(e["dados"] for e in self.sim.eventos if e["tipo"] == "movimento")
        self.assertAlmostEqual(movimento["distancia_percorrida_mn"], 1.0)
        self.assertAlmostEqual(movimento["deslocamento_resultante_mn"], 0.0)

    def test_sem_turnos_ou_extensao_invalida_nao_cria_relatorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "vazio.txt"
            with self.assertRaises(ValueError):
                self.sim.exportar_relatorio_pos_acao(caminho)
            self.assertFalse(caminho.exists())
            self.sim.avancar_turno([])
            with self.assertRaises(ValueError):
                self.sim.exportar_relatorio_pos_acao(Path(pasta) / "original.db3")


if __name__ == "__main__":
    unittest.main()
