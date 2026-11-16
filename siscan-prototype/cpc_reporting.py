"""Histórico pós-ação do ensaio CPC: eventos estruturados, TXT e CSV.

Resultados são propostas do modelo didático, sem adjudicação oficial. CSV usa
uma única linha de colunas e distingue cabeçalho/evento/rodapé pela coluna secao.
"""

from copy import deepcopy
from contextlib import contextmanager
import csv
import hashlib
import json
from pathlib import Path
import sys
import uuid

from cpc_models import MeioNaval, MeioTerrestre, VetorAereo


def _json(valor, **opcoes):
    return json.dumps(valor, ensure_ascii=False, allow_nan=False, sort_keys=True, **opcoes)


def capturar_estado(cenario) -> list[dict]:
    """Copia somente campos conhecidos do modelo; não registra atributos extras."""
    estados = []
    for u in cenario.unidades:
        x, y = cenario.posicao(u)
        dominio = ("aereo" if isinstance(u, VetorAereo) else "naval" if isinstance(u, MeioNaval)
                   else "terrestre" if isinstance(u, MeioTerrestre) else "nao_definido")
        estados.append({
            "unidade_id": u.identificador, "classe": type(u).__name__, "dominio": dominio,
            "pontos_de_vida": u.pontos_de_vida, "combustivel_kg": u.combustivel_atual,
            "taxa_kg_min": u.taxa_consumo_combustivel, "velocidade_nos": u.velocidade,
            "x_mn": x, "y_mn": y, "assinatura_radar_m2": u.assinatura_radar,
            "alcance_radar_mn": u.alcance_radar, "probabilidade_deteccao": u.probabilidade_deteccao,
            "estado_voo": u.estado_voo if isinstance(u, VetorAereo) else None,
            "reserva_retorno_kg": u.combustivel_minimo_retorno if isinstance(u, VetorAereo) else None,
            "capacidade_defesa_ponto": u.capacidade_defesa_ponto if isinstance(u, MeioNaval) else None,
            "armamentos": [{"estoque_id": a.identificador, "tipo": a.tipo, "quantidade": a.quantidade,
                            "pk": a.pk, "dano": a.dano, "alcance_maximo_mn": a.alcance_maximo}
                           for a in u.armamentos],
        })
    return estados


def _celula_csv(valor):
    if isinstance(valor, (dict, list, tuple)):
        return _json(valor)
    if isinstance(valor, str) and (valor.lstrip().startswith(("=", "+", "-", "@"))
                                   or valor.startswith(("\t", "\r", "\n"))):
        return "'" + valor
    return valor


@contextmanager
def _arquivo_novo(destino, encoding):
    arquivo = destino.open("x", encoding=encoding, newline="")
    try:
        yield arquivo
        arquivo.close()
    except BaseException:
        try:
            arquivo.close()
        finally:
            destino.unlink(missing_ok=True)
        raise


class HistoricoCombate:
    """Journal do loop, com snapshots congelados e sem sobrescrever relatórios."""

    def __init__(self, *, origem="biblioteca_cpc", semente=None):
        pasta = Path(__file__).parent
        arquivos = ("cpc_models.py", "cpc_scenario.py", "cpc_combat.py", "cpc_time.py", "cpc_reporting.py")
        self.metadados = {
            "schema": "cpc-pos-acao-1", "execucao_id": str(uuid.uuid4()), "origem": origem,
            "escopo": "ensaio_sintetico_nao_adjudicado", "python": sys.version.split()[0],
            "semente_declarada": semente, "passo_minutos": 1,
            "algoritmos_sha256": {nome: hashlib.sha256(
                (pasta / nome).read_text(encoding="utf-8").encode("utf-8")).hexdigest() for nome in arquivos},
        }
        self._inicial = None
        self._final = None
        self._eventos = []
        self.minuto_final = 0

    @property
    def eventos(self) -> list[dict]:
        return deepcopy(self._eventos)

    @property
    def estado_inicial(self) -> list[dict]:
        return deepcopy(self._inicial)

    @property
    def estado_final(self) -> list[dict]:
        return deepcopy(self._final)

    def preparar_turno(self, inicial, final, eventos, minuto):
        """Valida/copia antes de o chamador publicar o turno calculado."""
        novos = []
        for indice, evento in enumerate(eventos, start=len(self._eventos) + 1):
            if evento["minuto"] != minuto:
                raise ValueError("Evento fora do minuto calculado.")
            novos.append({**evento, "sequencia": indice, "execucao_id": self.metadados["execucao_id"],
                          "origem": self.metadados["origem"]})
        return json.loads(_json([inicial, final, novos, minuto]))

    def publicar_turno(self, preparado):
        inicial, final, novos, minuto = preparado
        if self._inicial is None:
            self._inicial = inicial
        self._final = final
        self._eventos.extend(novos)
        self.minuto_final = minuto

    def balanco(self) -> dict:
        if self._final is None:
            raise ValueError("Execute pelo menos um turno antes de gerar o relatório.")
        dano = {u["unidade_id"] for u in self._final if u["pontos_de_vida"] == 0}
        combustivel = {u["unidade_id"] for u in self._final if u["estado_voo"] == "perda_proposta"}
        perdas = dano | combustivel
        sobreviventes = {u["unidade_id"] for u in self._final} - perdas
        imoveis = {u["unidade_id"] for u in self._final if u["dominio"] in ("naval", "terrestre")
                   and u["combustivel_kg"] == 0 and u["unidade_id"] in sobreviventes}
        consumos = [e["dados"] for e in self._eventos if e["tipo"] == "consumo_armamento"]
        return {
            "minutos_simulados": self.minuto_final, "sobreviventes": sorted(sobreviventes),
            "destruidos_propostos_por_dano": sorted(dano), "perdas_aereas_propostas": sorted(combustivel),
            "perdas_propostas": sorted(perdas), "quantidade_perdas_propostas": len(perdas),
            "imobilizados_por_combustivel": sorted(imoveis),
            "indisponiveis_iniciais": sorted(u["unidade_id"] for u in self._inicial
                if u["pontos_de_vida"] == 0 or u["estado_voo"] == "perda_proposta"),
            "misseis_gastos": sum(c["quantidade"] for c in consumos
                                  if c["tipo_armamento"] in ("missil_antinavio", "missil_ar_ar")),
            "municoes_ofensivas_gastas": sum(c["quantidade"] for c in consumos if c["finalidade"] == "ofensiva"),
            "recursos_defensivos_gastos": sum(c["quantidade"] for c in consumos if c["finalidade"] == "defensiva"),
        }

    def _linhas_csv(self, balanco):
        linhas = []

        def adicionar(secao, tipo, dados, **campos):
            linhas.append({"secao": secao, "tipo": tipo, "dados": dados,
                           "execucao_id": self.metadados["execucao_id"], **campos})

        adicionar("cabecalho", "metadados", self.metadados, minuto=0)
        for unidade in self._inicial:
            adicionar("cabecalho", "estado_inicial", unidade, unidade_id=unidade["unidade_id"], minuto=0)
        for evento in self._eventos:
            linhas.append({"secao": "evento", **evento})
        for unidade in self._final:
            adicionar("rodape", "estado_final", unidade, unidade_id=unidade["unidade_id"], minuto=self.minuto_final)
        adicionar("rodape", "balanco", balanco, minuto=self.minuto_final)
        return linhas

    def exportar_relatorio_pos_acao(self, caminho="relatorio_pos_acao.txt") -> Path:
        """Salva TXT ou CSV UTF-8; arquivos existentes nunca são sobrescritos."""
        balanco = self.balanco()
        destino = Path(caminho).expanduser().resolve()
        formato = destino.suffix.lower()
        if formato not in (".txt", ".csv"):
            raise ValueError("Escolha um destino .txt ou .csv.")
        destino.parent.mkdir(parents=True, exist_ok=True)
        with _arquivo_novo(destino, "utf-8-sig" if formato == ".csv" else "utf-8") as arquivo:
            if formato == ".csv":
                linhas = self._linhas_csv(balanco)
                comuns = ["secao", "execucao_id", "sequencia", "minuto", "tipo", "nivel", "origem",
                          "unidade_id", "alvo_id", "acao_id"]
                adicionais = sorted({k for linha in linhas for k in linha["dados"]} - set(comuns))
                escritor = csv.DictWriter(arquivo, fieldnames=comuns + adicionais + ["dados_json"], delimiter=";")
                escritor.writeheader()
                for linha in linhas:
                    registro = {k: linha.get(k) for k in comuns}
                    registro.update({k: linha["dados"].get(k) for k in adicionais})
                    registro["dados_json"] = _json(linha["dados"])
                    escritor.writerow({k: _celula_csv(v) for k, v in registro.items()})
            else:
                arquivo.write("RELATÓRIO PÓS-AÇÃO — ENSAIO CPC NÃO ADJUDICADO\n\nEstado inicial das forças\n")
                arquivo.write(_json({"metadados": self.metadados, "forcas": self._inicial}, indent=2))
                arquivo.write("\n\nHistórico de eventos\n")
                for evento in self._eventos:
                    arquivo.write(_json(evento) + "\n")
                arquivo.write("\nEstado final das forças\n" + _json(self._final, indent=2))
                arquivo.write("\n\nBatalha Encerrada — resultados propostos, não adjudicados.\n")
                for titulo, chave in (("Sobreviventes", "sobreviventes"), ("Destruídos por dano (proposta)", "destruidos_propostos_por_dano"),
                                      ("Perdas aéreas por combustível (proposta)", "perdas_aereas_propostas"),
                                      ("Imobilizados por combustível", "imobilizados_por_combustivel")):
                    arquivo.write(f"{titulo}: {_json(balanco[chave])}\n")
                arquivo.write(f"Mísseis gastos: {balanco['misseis_gastos']}\n")
                arquivo.write(f"Recursos defensivos gastos: {balanco['recursos_defensivos_gastos']}\n")
                arquivo.write(f"Perdas propostas totais (sem duplicação): {balanco['quantidade_perdas_propostas']}\n")
                arquivo.write("Balanço estruturado: " + _json(balanco) + "\n")
        return destino
