"""Disparo estocástico didático em memória; não aplica resultado ao exercício.

Regra fictícia de duas etapas independentes: interceptação e acerto condicional.
Não representa o motor do Command ou desempenho de sistemas reais. Não modela
detecção, compatibilidade de alvos, trajetórias ou consumo de munição defensiva.
"""

import math
import random

from cpc_models import Armamento, MeioNaval, UnidadeMilitar


def _validar_numero(valor: float | None, nome: str, maximo: float | None = None) -> None:
    if (isinstance(valor, bool) or not isinstance(valor, (float, int))
            or not math.isfinite(valor) or valor < 0
            or (maximo is not None and valor > maximo)):
        raise ValueError(f"{nome}: informe número finito não negativo"
                         + (f" até {maximo}." if maximo is not None else "."))


class GerenciadorDeCombate:
    """Resolve disparos somente sobre instâncias isoladas de um ensaio.

    O gerador opcional permite repetir um ensaio com uma semente conhecida.
    Não há confirmação de instrutor, persistência ou atualização de estado oficial.
    """

    def __init__(
        self, atacante: UnidadeMilitar, defensor: UnidadeMilitar,
        *, gerador: random.Random | None = None,
    ) -> None:
        if atacante is defensor:
            raise ValueError("Atacante e defensor devem ser unidades distintas.")
        self.atacante = atacante
        self.defensor = defensor
        self.gerador = gerador if gerador is not None else random.Random()

    def resolver_disparo(
        self, atacante: UnidadeMilitar, defensor: UnidadeMilitar, arma: Armamento,
    ) -> str:
        """Consome um item e retorna a narrativa; dados inválidos não alteram estado.

        Usa sorteios distintos: r_defesa < capacidade intercepta; caso contrário,
        r_acerto < pk causa dano limitado à vida restante. Igualdade não é sucesso.
        Chegar a zero pontos não declara afundamento, morte ou perda oficial.
        """
        if atacante is not self.atacante or defensor is not self.defensor:
            raise ValueError("As unidades não correspondem ao par deste ensaio.")
        if not any(item is arma for item in atacante.armamentos):
            raise ValueError("O armamento não pertence ao atacante.")
        if type(arma.quantidade) is not int or arma.quantidade <= 0:
            raise ValueError("O estoque deve conter uma quantidade inteira positiva.")
        _validar_numero(arma.pk, "pk", 1.0)
        _validar_numero(arma.dano, "dano")
        for unidade in (atacante, defensor):
            _validar_numero(unidade.pontos_de_vida, "pontos_de_vida")
            if unidade.pontos_de_vida == 0:
                raise ValueError("Uma unidade sem pontos de vida não participa do disparo.")
        if isinstance(defensor, MeioNaval):
            _validar_numero(defensor.capacidade_defesa_ponto, "capacidade_defesa_ponto", 1.0)

        arma.quantidade -= 1
        relato = (f"{arma.identificador} disparado por {atacante.identificador} "
                  f"contra {defensor.identificador}. Estoque restante: {arma.quantidade}. ")
        if isinstance(defensor, MeioNaval):
            if self.gerador.random() < defensor.capacidade_defesa_ponto:
                return relato + f"Ataque interceptado pela defesa de ponto de {defensor.identificador}. Sem dano."
            relato += f"Defesa de ponto de {defensor.identificador} falhou. "
        if self.gerador.random() >= arma.pk:
            return relato + "O disparo errou. Sem dano."
        dano_aplicado = min(arma.dano, defensor.pontos_de_vida)
        defensor.pontos_de_vida -= dano_aplicado
        return (relato + f"Impacto confirmado no ensaio, causando {dano_aplicado:g} pontos de dano. "
                f"Vida restante de {defensor.identificador}: {defensor.pontos_de_vida:g}.")


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    from cpc_models import VetorAereo
    from source_catalog import browse

    parser = argparse.ArgumentParser(description="Ensaio fictício CPC com identidades do catálogo compilado.")
    parser.add_argument("--catalogo", type=Path,
                        default=Path(__file__).parent / "data/db3k-compiled-06.sqlite3")
    parser.add_argument("--semente", type=int, default=7)
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
    caca = VetorAereo(
        identificador=f"{aeronaves[0]['name']} [ensaio-aereo-01]",
        pontos_de_vida=100.0, assinatura_radar=None, velocidade=0.0,
        raio_de_acao=0.0, teto_operacional=0.0, armamentos=[arma],
    )
    fragata = MeioNaval(
        identificador=f"{navios[0]['name']} [ensaio-naval-01]",
        pontos_de_vida=100.0, assinatura_radar=None, velocidade=0.0,
        capacidade_defesa_ponto=0.2,
    )
    motor = GerenciadorDeCombate(caca, fragata, gerador=random.Random(args.semente))
    print(motor.resolver_disparo(caca, fragata, arma))
