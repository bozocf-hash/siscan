"""Disparo estocástico didático em memória; não aplica resultado ao exercício.

Regra fictícia de duas etapas independentes: interceptação e acerto condicional.
Não representa o motor do Command ou desempenho de sistemas reais. Não modela
detecção, compatibilidade de alvos ou trajetórias. As rodadas são ensaios isolados.
"""

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from cpc_models import Armamento, MeioNaval, UnidadeMilitar


def _validar_numero(valor: float | None, nome: str, maximo: float | None = None) -> None:
    if (isinstance(valor, bool) or not isinstance(valor, (float, int))
            or not math.isfinite(valor) or valor < 0
            or (maximo is not None and valor > maximo)):
        raise ValueError(f"{nome}: informe número finito não negativo"
                         + (f" até {maximo}." if maximo is not None else "."))


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
        *, gerador: random.Random | None = None,
    ) -> None:
        if atacante is defensor or atacante.identificador == defensor.identificador:
            raise ValueError("Atacante e defensor devem ter identidades distintas.")
        self.atacante = atacante
        self.defensor = defensor
        self.gerador = gerador if gerador is not None else random.Random()

    def _validar_rodada(self, acoes: tuple[AcaoDisparo, ...]) -> dict[Armamento, int]:
        unidades = (self.atacante, self.defensor)
        estoques = {}
        for unidade in unidades:
            _validar_numero(unidade.pontos_de_vida, "pontos_de_vida")
            if unidade.pontos_de_vida == 0:
                raise ValueError("Unidade sem pontos de vida no início da rodada.")
            nomes = set()
            for arma in unidade.armamentos:
                if arma.identificador in nomes:
                    raise ValueError("Estoque deve ter identificador único dentro da unidade.")
                nomes.add(arma.identificador)
                if arma in estoques:
                    raise ValueError("Um estoque não pode ser duplicado ou compartilhado entre unidades.")
                if type(arma.quantidade) is not int or arma.quantidade < 0:
                    raise ValueError("O estoque deve ter quantidade inteira não negativa.")
                estoques[arma] = arma.quantidade
        ids, reservas = set(), {}
        for acao in acoes:
            if not isinstance(acao.identificador, str) or not acao.identificador.strip() or acao.identificador in ids:
                raise ValueError("Cada ação precisa de identificador único e não vazio.")
            ids.add(acao.identificador)
            if (acao.atacante not in unidades or acao.defensor not in unidades
                    or acao.atacante is acao.defensor):
                raise ValueError("A ação deve pertencer ao par deste ensaio.")
            if acao.arma not in acao.atacante.armamentos or acao.arma.tipo == "defesa_ponto":
                raise ValueError("Informe um armamento ofensivo pertencente ao atacante.")
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
        return tuple(resultados)

    def resolver_disparo(
        self, atacante: UnidadeMilitar, defensor: UnidadeMilitar, arma: Armamento,
        *, defesa: Armamento | None = None, consumo_defensivo: int | None = None,
    ) -> str:
        """Atalho de uma ação; defesa só ocorre com estoque e custo explícitos."""
        acao = AcaoDisparo("disparo", atacante, defensor, arma, defesa, consumo_defensivo)
        return self.resolver_rodada([acao])[0].narrativa


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    from cpc_models import VetorAereo
    from source_catalog import browse

    parser = argparse.ArgumentParser(description="Ensaio fictício CPC com identidades do catálogo compilado.")
    parser.add_argument("--catalogo", type=Path,
                        default=Path(__file__).parent / "data/db3k-compiled-06.sqlite3")
    parser.add_argument("--semente", type=int, default=7)
    parser.add_argument("--iniciativa", choices=("simultanea", "aereo", "naval"), default="simultanea",
                        help="Condição didática explícita; não é calculada dos atributos técnicos.")
    args = parser.parse_args()
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
                     quantidade=2, pk=0.5, dano=10.0)
    estoque_defensivo = Armamento(identificador="pacotes-defensivos-sinteticos-01",
                                 tipo="defesa_ponto", quantidade=4)
    caca = VetorAereo(
        identificador=f"{aeronaves[0]['name']} [ensaio-aereo-01]",
        pontos_de_vida=100.0, assinatura_radar=None, velocidade=0.0,
        raio_de_acao=0.0, teto_operacional=0.0, armamentos=[arma],
    )
    fragata = MeioNaval(
        identificador=f"{navios[0]['name']} [ensaio-naval-01]",
        pontos_de_vida=100.0, assinatura_radar=None, velocidade=0.0,
        capacidade_defesa_ponto=0.2, armamentos=[estoque_defensivo],
    )
    motor = GerenciadorDeCombate(caca, fragata, gerador=random.Random(args.semente))
    iniciativa = {"simultanea": None, "aereo": caca, "naval": fragata}[args.iniciativa]
    acao = AcaoDisparo("acao-sintetica-01", caca, fragata, arma,
                       defesa=estoque_defensivo, consumo_defensivo=2)
    print(f"Regime: {args.iniciativa}. Custo fictício declarado: 2 pacotes por tentativa defensiva.")
    for resultado in motor.resolver_rodada([acao], iniciativa=iniciativa):
        print(f"Fase {resultado.fase}: {resultado.narrativa}")
        for consumo in resultado.consumos:
            print(f"  {consumo.finalidade}: {consumo.estoque_id}; "
                  f"{consumo.antes} - {consumo.quantidade} = {consumo.depois}")
