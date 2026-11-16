"""Disparo estocástico didático em memória; não aplica resultado ao exercício.

Regra fictícia de duas etapas independentes: interceptação e acerto condicional.
Não representa o motor do Command ou desempenho de sistemas reais. A detecção
usa uma rubrica fictícia explícita; não modela propagação de radar, compatibilidade
de alvos ou trajetórias. As rodadas são ensaios isolados.
"""

import random
from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Literal

from cpc_models import Armamento, MeioNaval, UnidadeMilitar, VetorAereo, validar_estoques
from cpc_models import validar_numero as _validar_numero
from cpc_scenario import CenarioTatico


@dataclass(frozen=True)
class AcaoDisparo:
    """Declara uma ação fictícia e, opcionalmente, sua tentativa defensiva.

    O custo defensivo é uma quantidade inteira de itens/pacotes do estoque
    selecionado pelo chamador; não existe custo padrão ou seleção automática.
    """

    identificador: str
    atacante: UnidadeMilitar
    defensor: UnidadeMilitar
    arma: Armamento
    defesa: Armamento | None = None
    consumo_defensivo: int | None = None


@dataclass(frozen=True)
class ConsumoArmamento:
    """Movimento de estoque no ensaio, na unidade de contabilização declarada."""

    unidade_id: str
    estoque_id: str
    finalidade: Literal["ofensiva", "defensiva"]
    quantidade: int
    antes: int
    depois: int


@dataclass(frozen=True)
class ResultadoDisparo:
    """Resultado proposto, sorteios e consumos; não é adjudicação oficial.

    Danos propostos de ações simultâneas são somados antes de limitar a vida
    final a zero; não se atribui a uma ação a perda efetiva de todo o lote.
    """

    acao_id: str
    fase: int
    situacao: Literal["interceptado", "erro", "impacto", "nao_iniciada"]
    narrativa: str
    consumos: tuple[ConsumoArmamento, ...]
    dano_proposto: float
    sorteio_defesa: float | None
    sorteio_acerto: float | None
    vida_antes: float
    vida_apos_lote: float


class GerenciadorDeCombate:
    """Ensaios de duas unidades: simultâneos ou com iniciativa explícita.

    A iniciativa deve vir da configuração didática do instrutor. Esta biblioteca
    não autentica usuários, não persiste resultados e não altera o exercício.
    """

    def __init__(
        self, atacante: UnidadeMilitar, defensor: UnidadeMilitar,
        *, cenario: CenarioTatico | None = None, gerador: random.Random | None = None,
    ) -> None:
        if atacante is defensor or atacante.identificador == defensor.identificador:
            raise ValueError("Atacante e defensor devem ter identidades distintas.")
        self.atacante = atacante
        self.defensor = defensor
        self.cenario = cenario
        self.gerador = gerador if gerador is not None else random.Random()
        self._eventos = []
        self.minuto_eventos = 0

    @property
    def eventos(self) -> list[dict]:
        return deepcopy(self._eventos)

    def _registrar_evento(self, tipo, *, unidade_id=None, alvo_id=None, acao_id=None, **dados):
        self._eventos.append({"minuto": self.minuto_eventos, "tipo": tipo, "nivel": "info",
                              "unidade_id": unidade_id, "alvo_id": alvo_id, "acao_id": acao_id,
                              "dados": deepcopy(dados)})

    def tentar_detecao(self, unidade_a: UnidadeMilitar, unidade_b: UnidadeMilitar) -> bool:
        """Atualiza contato direcional: distância válida e sorteio < p_base × fator.

        Fator é declarado na rubrica do cenário para a assinatura do alvo. Não
        há estimativa física de eficácia. Uma tentativa falha remove o contato
        anterior deste par; dado desconhecido provoca erro, não sucesso ou zero.
        """
        if self.cenario is None:
            raise ValueError("Declare um cenário antes de tentar detecção.")
        par = (self.atacante, self.defensor)
        if unidade_a not in par or unidade_b not in par or unidade_a is unidade_b:
            raise ValueError("Detecção deve envolver as duas unidades distintas deste ensaio.")
        self.cenario.validar_unidade(unidade_a)
        self.cenario.validar_unidade(unidade_b)
        self.cenario._remover_contato(unidade_a, unidade_b)
        for unidade in (unidade_a, unidade_b):
            _validar_numero(unidade.pontos_de_vida, "pontos_de_vida")
            if unidade.pontos_de_vida == 0:
                raise ValueError("Unidade sem pontos não participa da busca neste ensaio.")
            if isinstance(unidade, VetorAereo) and (unidade.estado_voo == "perda_proposta"
                    or (unidade.estado_voo in ("em_voo", "evadindo") and unidade.combustivel_atual == 0)):
                raise ValueError("Aeronave com perda proposta não participa da busca.")
        _validar_numero(unidade_a.alcance_radar, "alcance_radar")
        _validar_numero(unidade_a.probabilidade_deteccao, "probabilidade_deteccao", 1.0)
        distancia = self.cenario.distancia(unidade_a, unidade_b)
        if distancia > unidade_a.alcance_radar:
            self._registrar_evento("deteccao", unidade_id=unidade_a.identificador, alvo_id=unidade_b.identificador,
                                   detectado=False, motivo="fora_do_radar", distancia_mn=distancia,
                                   alcance_radar_mn=unidade_a.alcance_radar, sorteio=None)
            return False
        fator = self.cenario.fator_assinatura(unidade_b.assinatura_radar)
        probabilidade = unidade_a.probabilidade_deteccao * fator
        sorteio = self.gerador.random()
        detectado = sorteio < probabilidade
        if detectado:
            self.cenario._registrar_contato(unidade_a, unidade_b)
        self._registrar_evento("deteccao", unidade_id=unidade_a.identificador, alvo_id=unidade_b.identificador,
                               detectado=detectado, motivo="sorteio", distancia_mn=distancia,
                               alcance_radar_mn=unidade_a.alcance_radar, assinatura_alvo_m2=unidade_b.assinatura_radar,
                               probabilidade_base=unidade_a.probabilidade_deteccao, fator_assinatura=fator,
                               probabilidade_efetiva=probabilidade, sorteio=sorteio)
        return detectado

    def _registrar_resultados(self, acoes, resultados):
        por_id = {a.identificador: a for a in acoes}
        for fase in sorted({r.fase for r in resultados}):
            danos = {}
            for r in (r for r in resultados if r.fase == fase):
                acao = por_id[r.acao_id]
                contexto = dict(unidade_id=acao.atacante.identificador,
                                alvo_id=acao.defensor.identificador, acao_id=r.acao_id, fase=fase)
                if r.situacao == "nao_iniciada":
                    self._registrar_evento("acao_nao_iniciada", **contexto, motivo=r.narrativa)
                    continue
                self._registrar_evento("disparo", **contexto, estoque_id=acao.arma.identificador,
                                       tipo_armamento=acao.arma.tipo)
                for consumo in r.consumos:
                    estoque = acao.arma if consumo.finalidade == "ofensiva" else acao.defesa
                    self._registrar_evento("consumo_armamento", unidade_id=consumo.unidade_id,
                                           acao_id=r.acao_id, fase=fase, estoque_id=consumo.estoque_id,
                                           tipo_armamento=estoque.tipo, finalidade=consumo.finalidade,
                                           quantidade=consumo.quantidade, antes=consumo.antes, depois=consumo.depois)
                if r.sorteio_defesa is not None:
                    self._registrar_evento("tentativa_defesa", **contexto, sorteio=r.sorteio_defesa,
                                           interceptado=r.situacao == "interceptado")
                tipo = {"impacto": "acerto", "erro": "erro_disparo", "interceptado": "interceptacao"}[r.situacao]
                self._registrar_evento(tipo, **contexto, dano_proposto=r.dano_proposto,
                                       sorteio_acerto=r.sorteio_acerto)
                if r.vida_antes != r.vida_apos_lote:
                    danos[acao.defensor.identificador] = (r.vida_antes, r.vida_apos_lote)
            for alvo_id, (antes, depois) in sorted(danos.items()):
                self._registrar_evento("dano_aplicado", unidade_id=alvo_id, fase=fase,
                                       vida_antes=antes, vida_depois=depois, dano_efetivo=antes - depois)
                if antes > 0 and depois == 0:
                    self._registrar_evento("destruicao_proposta", unidade_id=alvo_id, fase=fase,
                                           motivo="pontos_de_vida_zerados_no_modelo", oficial=False)

    def _validar_rodada(self, acoes: tuple[AcaoDisparo, ...]) -> dict[Armamento, int]:
        unidades = (self.atacante, self.defensor)
        for unidade in unidades:
            _validar_numero(unidade.pontos_de_vida, "pontos_de_vida")
            if unidade.pontos_de_vida == 0:
                raise ValueError("Unidade sem pontos de vida no início da rodada.")
        estoques = validar_estoques(unidades)
        ids, reservas = set(), {}
        for acao in acoes:
            if not isinstance(acao.identificador, str) or not acao.identificador.strip() or acao.identificador in ids:
                raise ValueError("Cada ação precisa de identificador único e não vazio.")
            ids.add(acao.identificador)
            if (acao.atacante not in unidades or acao.defensor not in unidades
                    or acao.atacante is acao.defensor):
                raise ValueError("A ação deve pertencer ao par deste ensaio.")
            if isinstance(acao.atacante, VetorAereo) and (acao.atacante.estado_voo != "em_voo"
                    or acao.atacante.combustivel_atual == 0):
                raise ValueError("Aeronave que não está em voo disponível não inicia novos ataques.")
            if isinstance(acao.defensor, VetorAereo) and (acao.defensor.estado_voo == "perda_proposta"
                    or (acao.defensor.estado_voo in ("em_voo", "evadindo") and acao.defensor.combustivel_atual == 0)):
                raise ValueError("Alvo com perda proposta indisponível no ensaio.")
            if acao.arma not in acao.atacante.armamentos or acao.arma.tipo == "defesa_ponto":
                raise ValueError("Informe um armamento ofensivo pertencente ao atacante.")
            if self.cenario is None:
                raise ValueError("Declare um cenário para conferir contato e alcance.")
            self.cenario.validar_unidade(acao.defensor)
            if acao.defensor.identificador not in self.cenario.contatos_detectados(acao.atacante):
                raise ValueError("Contato detectado válido é obrigatório antes de declarar disparo.")
            _validar_numero(acao.arma.alcance_maximo, "alcance_maximo")
            if self.cenario.distancia(acao.atacante, acao.defensor) > acao.arma.alcance_maximo:
                raise ValueError("Alvo fora do alcance máximo do armamento.")
            _validar_numero(acao.arma.pk, "pk", 1.0)
            _validar_numero(acao.arma.dano, "dano")
            if estoques[acao.arma] == 0:
                raise ValueError("Não há estoque ofensivo disponível.")
            reservas[acao.arma] = reservas.get(acao.arma, 0) + 1
            if acao.defesa is None:
                if acao.consumo_defensivo is not None:
                    raise ValueError("Custo defensivo exige um estoque defensivo explícito.")
                continue
            if (not isinstance(acao.defensor, MeioNaval)
                    or acao.defesa not in acao.defensor.armamentos
                    or acao.defesa.tipo != "defesa_ponto"):
                raise ValueError("Defesa deve ser um estoque de defesa de ponto do defensor naval.")
            if type(acao.consumo_defensivo) is not int or acao.consumo_defensivo <= 0:
                raise ValueError("Declare uma quantidade inteira positiva por tentativa defensiva.")
            if estoques[acao.defesa] >= acao.consumo_defensivo:
                _validar_numero(acao.defensor.capacidade_defesa_ponto, "capacidade_defesa_ponto", 1.0)
                reservas[acao.defesa] = reservas.get(acao.defesa, 0) + acao.consumo_defensivo
        if any(qtd > estoques[arma] for arma, qtd in reservas.items()):
            raise ValueError("Conflito de reservas: redistribua as ações antes de resolver a rodada.")
        return estoques

    def resolver_rodada(
        self, acoes: list[AcaoDisparo], *, iniciativa: UnidadeMilitar | None = None,
    ) -> tuple[ResultadoDisparo, ...]:
        """Valida/reserva o lote todo antes de sortear; aplica só ao fim do ensaio.

        Sem iniciativa, todas as ações começam juntas. Com iniciativa, a segunda
        fase só começa após os efeitos da primeira; ações ainda não iniciadas são
        suspensas se um dos participantes estiver sem pontos. Ações da mesma fase
        permanecem simultâneas. IDs ordenam a reprodução, não o direito de agir.
        """
        if iniciativa is not None and iniciativa not in (self.atacante, self.defensor):
            raise ValueError("Iniciativa deve identificar uma unidade deste ensaio.")
        ordenadas = tuple(sorted(acoes, key=lambda acao: acao.identificador))
        if not ordenadas:
            raise ValueError("Declare ao menos uma ação.")
        estoques = self._validar_rodada(ordenadas)
        vidas = {u: u.pontos_de_vida for u in (self.atacante, self.defensor)}
        fases = (ordenadas,) if iniciativa is None else (
            tuple(a for a in ordenadas if a.atacante is iniciativa),
            tuple(a for a in ordenadas if a.atacante is not iniciativa),
        )
        resultados = []
        for fase_id, fase in enumerate(fases, start=1):
            danos = {u: 0.0 for u in vidas}
            lote = []
            for acao in fase:
                if vidas[acao.atacante] == 0 or vidas[acao.defensor] == 0:
                    lote.append(ResultadoDisparo(
                        acao.identificador, fase_id, "nao_iniciada",
                        f"Ação {acao.identificador} não iniciada: participante sem pontos após a primeira fase.",
                        (), 0.0, None, None, vidas[acao.defensor], vidas[acao.defensor],
                    ))
                    continue
                consumos = []

                def consumir(unidade, arma, quantidade, finalidade):
                    antes = estoques[arma]
                    estoques[arma] -= quantidade
                    consumos.append(ConsumoArmamento(
                        unidade.identificador, arma.identificador, finalidade,
                        quantidade, antes, estoques[arma],
                    ))

                consumir(acao.atacante, acao.arma, 1, "ofensiva")
                relato = (f"{acao.arma.identificador} disparado por {acao.atacante.identificador} "
                          f"contra {acao.defensor.identificador}. ")
                rd, ra, dano, situacao = None, None, 0.0, "erro"
                if acao.defesa is not None and estoques[acao.defesa] >= acao.consumo_defensivo:
                    consumir(acao.defensor, acao.defesa, acao.consumo_defensivo, "defensiva")
                    rd = self.gerador.random()
                    relato += (f"Defesa {acao.defesa.identificador}: consumo {acao.consumo_defensivo}, "
                               f"saldo {estoques[acao.defesa]}. ")
                    if rd < acao.defensor.capacidade_defesa_ponto:
                        situacao = "interceptado"
                        relato += "Ataque interceptado. Sem dano. "
                    else:
                        relato += "Defesa de ponto falhou. "
                else:
                    relato += "Sem tentativa defensiva: não declarada ou estoque insuficiente. "
                if situacao != "interceptado":
                    ra = self.gerador.random()
                    if ra < acao.arma.pk:
                        situacao, dano = "impacto", acao.arma.dano
                        danos[acao.defensor] += dano
                        relato += f"Impacto confirmado no ensaio: {dano:g} pontos de dano proposto. "
                    else:
                        relato += "O disparo errou. Sem dano. "
                lote.append(ResultadoDisparo(
                    acao.identificador, fase_id, situacao, relato, tuple(consumos), dano,
                    rd, ra, vidas[acao.defensor], vidas[acao.defensor],
                ))
            finais = {u: max(0.0, vidas[u] - danos[u]) for u in vidas}
            for acao, resultado in zip(fase, lote):
                depois = finais[acao.defensor]
                resultados.append(replace(
                    resultado, vida_apos_lote=depois,
                    narrativa=resultado.narrativa
                    + f"Dano efetivo do lote: {vidas[acao.defensor] - depois:g}; vida restante: {depois:g}.",
                ))
            vidas = finais
        for arma, quantidade in estoques.items():
            arma.quantidade = quantidade
        for unidade, vida in vidas.items():
            unidade.pontos_de_vida = vida
        self._registrar_resultados(ordenadas, resultados)
        return tuple(resultados)

    def resolver_disparo(
        self, atacante: UnidadeMilitar, defensor: UnidadeMilitar, arma: Armamento,
        *, defesa: Armamento | None = None, consumo_defensivo: int | None = None,
    ) -> str:
        """Exige contato e alcance; defesa só ocorre com estoque/custo explícitos."""
        acao = AcaoDisparo("disparo", atacante, defensor, arma, defesa, consumo_defensivo)
        return self.resolver_rodada([acao])[0].narrativa


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    from cpc_time import SimulacaoTemporal
    from source_catalog import browse

    parser = argparse.ArgumentParser(description="Ensaio fictício CPC com identidades do catálogo compilado.")
    parser.add_argument("--catalogo", type=Path,
                        default=Path(__file__).parent / "data/db3k-compiled-06.sqlite3")
    parser.add_argument("--semente", type=int, default=7)
    parser.add_argument("--turnos", type=int, default=3, help="Minutos simulados, de 1 a 1440.")
    parser.add_argument("--relatorio", type=Path, nargs="+", metavar="ARQUIVO",
                        help="Destinos novos .txt/.csv para o histórico e balanço pós-ação.")
    parser.add_argument("--iniciativa", choices=("simultanea", "aereo", "naval"), default="simultanea",
                        help="Condição didática explícita; não é calculada dos atributos técnicos.")
    args = parser.parse_args()
    if not 1 <= args.turnos <= 1440:
        parser.error("Informe de 1 a 1440 turnos de um minuto.")
    destinos = [p.expanduser().resolve() for p in (args.relatorio or [])]
    if len(set(destinos)) != len(destinos):
        parser.error("Os caminhos de relatório devem ser distintos.")
    for destino in destinos:
        if destino.suffix.lower() not in (".txt", ".csv") or destino.exists():
            parser.error(f"Informe um arquivo .txt/.csv novo, sem sobrescrever: {destino}")
    try:
        aeronaves = browse(args.catalogo, "DataAircraft", "8")["items"]
        navios = browse(args.catalogo, "DataShip", "1349")["items"]
        if not aeronaves or not navios:
            raise ValueError("Os registros DataAircraft/8 e DataShip/1349 não estão neste catálogo.")
        if "F/A-18" not in aeronaves[0]["name"] or "Niteroi" not in navios[0]["name"]:
            raise ValueError("As identidades encontradas diferem do recorte DB3K_498 esperado.")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print("ENSAIO SINTÉTICO — somente identificação vem do catálogo; todos os parâmetros são fictícios.")
    print(f"Catálogo somente leitura: {args.catalogo.resolve()}")
    print(f"DataAircraft/8: {aeronaves[0]['name']}")
    print(f"DataShip/1349: {navios[0]['name']}")
    arma = Armamento(identificador="municao-sintetica-01", tipo="missil_antinavio",
                     quantidade=2, pk=0.5, dano=10.0, alcance_maximo=15.0)
    estoque_defensivo = Armamento(identificador="pacotes-defensivos-sinteticos-01",
                                 tipo="defesa_ponto", quantidade=4)
    caca = VetorAereo(
        identificador=f"{aeronaves[0]['name']} [ensaio-aereo-01]",
        pontos_de_vida=100.0, assinatura_radar=1.0, velocidade=60.0,
        raio_de_acao=0.0, teto_operacional=0.0, armamentos=[arma],
        alcance_radar=20.0, probabilidade_deteccao=0.8,
        combustivel_atual=5.0, taxa_consumo_combustivel=2.0, combustivel_minimo_retorno=1.0,
    )
    fragata = MeioNaval(
        identificador=f"{navios[0]['name']} [ensaio-naval-01]",
        pontos_de_vida=100.0, assinatura_radar=2.0, velocidade=0.0,
        capacidade_defesa_ponto=0.2, armamentos=[estoque_defensivo],
        alcance_radar=20.0, probabilidade_deteccao=0.8,
    )
    cenario = CenarioTatico([caca, fragata],
                            {(caca.identificador, fragata.identificador): 10.0},
                            {1.0: 0.5, 2.0: 1.0},
                            posicoes={caca.identificador: (0.0, 0.0), fragata.identificador: (10.0, 0.0)})
    motor = GerenciadorDeCombate(caca, fragata, cenario=cenario, gerador=random.Random(args.semente))
    iniciativa = {"simultanea": None, "aereo": caca, "naval": fragata}[args.iniciativa]
    acao = AcaoDisparo("acao-sintetica-01", caca, fragata, arma,
                       defesa=estoque_defensivo, consumo_defensivo=2)
    print(f"Regime: {args.iniciativa}. Custo fictício declarado: 2 pacotes por tentativa defensiva.")
    print("Distância fictícia: 10 MN; radar fictício: 20 MN; alcance da arma fictícia: 15 MN.")
    print("Logística fictícia: 5 kg iniciais, 2 kg/min e reserva de retorno de 1 kg; não são dados do F/A-18.")
    simulacao = SimulacaoTemporal(motor, rumos={caca.identificador: 90.0},
                                  rumos_evasao={caca.identificador: 270.0},
                                  origem="terminal_cpc", semente=args.semente)
    for _ in range(args.turnos):
        turno = simulacao.avancar_turno([acao], iniciativa=iniciativa)
        print(f"\nMinuto {turno.minuto}: distância {cenario.distancia(caca, fragata):.3f} MN")
        for unidade in turno.logistica:
            if unidade.estado_voo is not None:
                print(f"  {unidade.unidade_id}: combustível {unidade.combustivel_antes:g} -> "
                      f"{unidade.combustivel_depois:g} kg; {unidade.estado_voo}")
            elif unidade.imobilizado_por_combustivel:
                print(f"  {unidade.unidade_id}: imobilizado por combustível zerado; sem perda automática.")
        for evento in turno.eventos:
            print(evento)
        for resultado in turno.combate:
            print(f"Fase {resultado.fase}: {resultado.narrativa}")
            for consumo in resultado.consumos:
                print(f"  {consumo.finalidade}: {consumo.estoque_id}; "
                      f"{consumo.antes} - {consumo.quantidade} = {consumo.depois}")
    for destino in destinos:
        try:
            caminho = simulacao.exportar_relatorio_pos_acao(destino)
        except (OSError, ValueError) as exc:
            parser.exit(2, f"Falha ao exportar relatório: {exc}\n")
        print(f"Relatório pós-ação salvo: {caminho}")
