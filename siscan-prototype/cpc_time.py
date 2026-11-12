"""Turnos didáticos de 1 minuto: logística, movimento, detecção e combate.

Sem sleep ou relógio de parede; cada chamada avança exatamente 1 minuto simulado.
Taxas, reservas e rumos são dados explícitos do ensaio, não parâmetros reais.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import math
import random
from typing import TYPE_CHECKING

from cpc_models import VetorAereo, validar_estoques, validar_numero

if TYPE_CHECKING:
    from cpc_combat import AcaoDisparo, GerenciadorDeCombate, ResultadoDisparo
    from cpc_models import UnidadeMilitar


@dataclass(frozen=True)
class ResumoLogistico:
    unidade_id: str
    combustivel_antes: float | None
    combustivel_depois: float | None
    estado_voo: str | None
    posicao_antes: tuple[float, float]
    posicao_depois: tuple[float, float]


@dataclass(frozen=True)
class ResultadoTurno:
    minuto: int
    logistica: tuple[ResumoLogistico, ...]
    eventos: tuple[str, ...]
    combate: tuple[ResultadoDisparo, ...]


def _deslocamento(velocidade: float, rumo: float, minutos: float) -> tuple[float, float]:
    distancia = velocidade * minutos / 60.0
    angulo = math.radians(rumo)
    return distancia * math.sin(angulo), distancia * math.cos(angulo)


class SimulacaoTemporal:
    """Um relógio para todas as unidades do cenário, sem persistência oficial.

    Rumos em graus: 0 norte, 90 leste. O rumo de evasão é fornecido pelo operador;
    não se calcula rota de retorno, interceptação ou perseguição. Requer Random
    padrão, para copiar e publicar o estado aleatório junto com o turno.
    """

    def __init__(
        self, gerenciador: GerenciadorDeCombate, *, rumos: dict[str, float],
        rumos_evasao: dict[str, float],
    ) -> None:
        if gerenciador.cenario is None:
            raise ValueError("Turnos exigem cenário com posições.")
        if type(gerenciador.gerador) is not random.Random:
            raise ValueError("Use random.Random padrão para reprodução dos turnos.")
        self.gerenciador = gerenciador
        self.rumos = dict(rumos)
        self.rumos_evasao = dict(rumos_evasao)
        self.minuto_atual = 0

    def _logistica_e_movimento(self, motor):
        cenario = motor.cenario
        ids = {u.identificador for u in cenario.unidades}
        for rumos in (self.rumos, self.rumos_evasao):
            if not rumos.keys() <= ids:
                raise ValueError("Rumo declarado para unidade fora do cenário.")
            for rumo in rumos.values():
                validar_numero(rumo, "rumo_graus", 360.0)
        deslocamentos, antes = {}, {}
        for unidade in cenario.unidades:
            chave = unidade.identificador
            antes[chave] = (unidade.combustivel_atual, cenario.posicao(unidade))
            validar_numero(unidade.velocidade, "velocidade")
            rumo = self.rumos.get(chave, 0.0)
            normal, evasao = 1.0, 0.0
            if isinstance(unidade, VetorAereo):
                if unidade.estado_voo not in ("em_voo", "evadindo", "pousado", "perda_proposta"):
                    raise ValueError("Estado de voo não reconhecido.")
                normal = 0.0
                if unidade.estado_voo in ("em_voo", "evadindo"):
                    for nome in ("combustivel_atual", "taxa_consumo_combustivel", "combustivel_minimo_retorno"):
                        validar_numero(getattr(unidade, nome), nome)
                    taxa, saldo = unidade.taxa_consumo_combustivel, unidade.combustivel_atual
                    if taxa == 0:
                        raise ValueError("Taxa de consumo em voo deve ser positiva.")
                    duracao = min(1.0, saldo / taxa)
                    normal = 0.0 if unidade.estado_voo == "evadindo" else min(
                        duracao, max(0.0, (saldo - unidade.combustivel_minimo_retorno) / taxa))
                    evasao = duracao - normal
                    unidade.combustivel_atual = max(0.0, saldo - taxa)
                    if unidade.combustivel_atual == 0:
                        unidade.estado_voo = "perda_proposta"
                    elif unidade.estado_voo == "evadindo" or unidade.combustivel_atual <= unidade.combustivel_minimo_retorno:
                        unidade.estado_voo = "evadindo"
                    if unidade.velocidade > 0 and chave not in self.rumos_evasao:
                        raise ValueError("Declare rumo de evasão para cada aeronave móvel em voo.")
            if unidade.velocidade > 0 and normal > 0 and chave not in self.rumos:
                raise ValueError("Declare o rumo de cada unidade que se movimenta.")
            dx, dy = _deslocamento(unidade.velocidade, rumo, normal)
            ex, ey = _deslocamento(unidade.velocidade, self.rumos_evasao.get(chave, 0.0), evasao)
            deslocamentos[chave] = dx + ex, dy + ey
        cenario.aplicar_deslocamentos(deslocamentos)
        return tuple(ResumoLogistico(
            u.identificador, antes[u.identificador][0], u.combustivel_atual,
            u.estado_voo if isinstance(u, VetorAereo) else None,
            antes[u.identificador][1], cenario.posicao(u),
        ) for u in cenario.unidades)

    def avancar_turno(
        self, acoes: list[AcaoDisparo], *, iniciativa: UnidadeMilitar | None = None,
    ) -> ResultadoTurno:
        """Calcula em cópia; erro não publica tempo, combustível, posição ou RNG.

        Consumo/movimento ocorrem no intervalo; detecção e novas ações, no final.
        Falta de contato/alcance/estoque ou evasão suspende a ação, não o relógio.
        Erro de configuração ou conflito de reservas recusa o turno completo.
        """
        original = self.gerenciador
        if iniciativa is not None and iniciativa not in (original.atacante, original.defensor):
            raise ValueError("Iniciativa fora do par do ensaio.")
        motor, declaradas, primeira = deepcopy((original, acoes, iniciativa))
        validar_estoques(motor.cenario.unidades)
        logistica = self._logistica_e_movimento(motor)
        eventos, elegiveis, deteccoes, ids = [], [], {}, set()
        par = (motor.atacante, motor.defensor)
        for acao in sorted(declaradas, key=lambda a: a.identificador):
            if not isinstance(acao.identificador, str) or not acao.identificador.strip() or acao.identificador in ids:
                raise ValueError("Ações do turno precisam de IDs únicos.")
            ids.add(acao.identificador)
            if acao.atacante not in par or acao.defensor not in par or acao.atacante is acao.defensor:
                raise ValueError("Ação fora do par do ensaio.")
            if acao.arma not in acao.atacante.armamentos or acao.arma.tipo == "defesa_ponto":
                raise ValueError("Armamento ofensivo não pertence ao atacante.")
            motivo = None
            for unidade in (acao.atacante, acao.defensor):
                validar_numero(unidade.pontos_de_vida, "pontos_de_vida")
                if unidade.pontos_de_vida == 0 or (isinstance(unidade, VetorAereo) and unidade.estado_voo == "perda_proposta"):
                    motivo = "participante indisponível no ensaio"
            if isinstance(acao.atacante, VetorAereo) and acao.atacante.estado_voo != "em_voo":
                motivo = f"atacante em {acao.atacante.estado_voo}"
            if acao.arma.quantidade == 0:
                motivo = "estoque ofensivo esgotado"
            if motivo is None:
                validar_numero(acao.arma.alcance_maximo, "alcance_maximo")
                chave = (acao.atacante.identificador, acao.defensor.identificador)
                if chave not in deteccoes:
                    deteccoes[chave] = motor.tentar_detecao(acao.atacante, acao.defensor)
                if not deteccoes[chave]:
                    motivo = "alvo não detectado"
                elif motor.cenario.distancia(acao.atacante, acao.defensor) > acao.arma.alcance_maximo:
                    motivo = "alvo fora do alcance da arma"
            if motivo is None:
                elegiveis.append(acao)
            else:
                eventos.append(f"Ação {acao.identificador} não iniciada: {motivo}; sem consumo de armamento.")
        combate = motor.resolver_rodada(elegiveis, iniciativa=primeira) if elegiveis else ()
        estado_gerador = motor.gerador.getstate()
        copias = {u.identificador: u for u in motor.cenario.unidades}
        original.cenario._copiar_estado_de(motor.cenario)
        for unidade in original.cenario.unidades:
            copia = copias[unidade.identificador]
            unidade.combustivel_atual = copia.combustivel_atual
            unidade.pontos_de_vida = copia.pontos_de_vida
            if isinstance(unidade, VetorAereo):
                unidade.estado_voo = copia.estado_voo
            for estoque, novo in zip(unidade.armamentos, copia.armamentos):
                estoque.quantidade = novo.quantidade
        original.gerador.setstate(estado_gerador)
        self.minuto_atual += 1
        return ResultadoTurno(self.minuto_atual, logistica, tuple(eventos), combate)
