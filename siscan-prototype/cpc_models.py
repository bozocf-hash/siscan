"""Estruturas didáticas do CPC, sem resolução de combate ou persistência.

As unidades declaradas são convenções deste módulo, não interpretações dos
campos brutos do DB3K. A integração futura exige conversão e validação explícitas.
Type hints documentam o contrato; estes construtores não validam entradas externas.
"""

import math
from typing import Literal


def validar_numero(valor: float | None, nome: str, maximo: float | None = None) -> None:
    """Valida grandezas do ensaio nas fronteiras de cenário e execução."""
    if (isinstance(valor, bool) or not isinstance(valor, (float, int))
            or not math.isfinite(valor) or valor < 0
            or (maximo is not None and valor > maximo)):
        raise ValueError(f"{nome}: informe número finito não negativo"
                         + (f" até {maximo}." if maximo is not None else "."))


class Armamento:
    """Representa um estoque de armamento de uma unidade no ensaio.

    Attributes:
        identificador: Identidade do estoque/configuração no ensaio; não presume
            equivalência com um identificador de arma do DB3K.
        tipo: Categoria didática: míssil antinavio, míssil ar-ar ou defesa de ponto.
        quantidade: Número de itens disponíveis na unidade de contabilização
            definida para este estoque. Não é uma porcentagem agregada.
        pk: Probabilidade didática de acerto entre 0 e 1, condicionada a passar
            pela defesa. Não é probabilidade validada de destruição. None indica
            parâmetro não definido; não pode ser usado para resolver um disparo.
        dano: Pontos abstratos de dano não negativos por impacto; None indica
            parâmetro não definido. Não é dado físico importado do DB3K.
        alcance_maximo: Limite didático em milhas náuticas; None impede disparo.
    """

    def __init__(
        self,
        *,
        identificador: str,
        tipo: Literal["missil_antinavio", "missil_ar_ar", "defesa_ponto"],
        quantidade: int,
        pk: float | None = None,
        dano: float | None = None,
        alcance_maximo: float | None = None,
    ) -> None:
        self.identificador = identificador
        self.tipo = tipo
        self.quantidade = quantidade
        self.pk = pk
        self.dano = dano
        self.alcance_maximo = alcance_maximo


class UnidadeMilitar:
    """Armazena os atributos comuns de uma unidade individual do ensaio.

    Attributes:
        identificador: Identidade estável da instância; na integração deverá
            preservar a identidade da unidade existente, não apenas seu modelo.
        pontos_de_vida: Pontos abstratos na escala declarada pelo cenário. Não são
            automaticamente DamagePoints do DB3K ou o índice operativo de 0–100%.
        assinatura_radar: Seção reta radar de referência em m², no contexto
            declarado pelo cenário; None indica dado desconhecido. Este escalar
            não representa sozinho um modelo de detecção.
        velocidade: Velocidade atual em nós; não representa velocidade máxima.
        armamentos: Lista própria de estoques embarcados. A lista recebida é
            copiada superficialmente; os objetos Armamento continuam os mesmos
            e devem pertencer à unidade, sem compartilhamento entre unidades.
        alcance_radar: Limite didático de busca em milhas náuticas. None indica
            parâmetro não definido; não é automaticamente o alcance de um sensor DB3K.
        probabilidade_deteccao: Probabilidade-base didática entre 0 e 1, antes do
            fator explícito de assinatura do cenário; None indica não definido.
    """

    def __init__(
        self,
        *,
        identificador: str,
        pontos_de_vida: float,
        assinatura_radar: float | None,
        velocidade: float,
        armamentos: list[Armamento] | None = None,
        alcance_radar: float | None = None,
        probabilidade_deteccao: float | None = None,
    ) -> None:
        self.identificador = identificador
        self.pontos_de_vida = pontos_de_vida
        self.assinatura_radar = assinatura_radar
        self.velocidade = velocidade
        self.alcance_radar = alcance_radar
        self.probabilidade_deteccao = probabilidade_deteccao
        self.armamentos: list[Armamento] = (
            list(armamentos) if armamentos is not None else []
        )


class MeioNaval(UnidadeMilitar):
    """Especializa uma unidade naval com uma capacidade didática declarada.

    Attributes:
        capacidade_defesa_ponto: Probabilidade didática de interceptação entre
            0 e 1 na regra sintética atual; None indica não avaliado. Substitui a
            escala abstrata inicialmente proposta. Não é eficácia real validada
            nem quantidade de munição. Uma tentativa exige estoque defensivo e
            custo explícitos na ação; a probabilidade sozinha não ativa a defesa.

    Os demais atributos seguem o contrato de UnidadeMilitar.
    """

    def __init__(
        self,
        *,
        identificador: str,
        pontos_de_vida: float,
        assinatura_radar: float | None,
        velocidade: float,
        capacidade_defesa_ponto: float | None,
        armamentos: list[Armamento] | None = None,
        alcance_radar: float | None = None,
        probabilidade_deteccao: float | None = None,
    ) -> None:
        super().__init__(
            identificador=identificador,
            pontos_de_vida=pontos_de_vida,
            assinatura_radar=assinatura_radar,
            velocidade=velocidade,
            armamentos=armamentos,
            alcance_radar=alcance_radar,
            probabilidade_deteccao=probabilidade_deteccao,
        )
        self.capacidade_defesa_ponto = capacidade_defesa_ponto


class VetorAereo(UnidadeMilitar):
    """Especializa uma unidade aérea com referências de alcance e altitude.

    Attributes:
        raio_de_acao: Raio de ação de referência em milhas náuticas para o perfil
            e configuração declarados; não é alcance total nem autonomia atual.
        teto_operacional: Altitude máxima operacional de referência em metros
            acima do nível médio do mar; não é a altitude atual.

    Os demais atributos seguem o contrato de UnidadeMilitar.
    """

    def __init__(
        self,
        *,
        identificador: str,
        pontos_de_vida: float,
        assinatura_radar: float | None,
        velocidade: float,
        raio_de_acao: float,
        teto_operacional: float,
        armamentos: list[Armamento] | None = None,
        alcance_radar: float | None = None,
        probabilidade_deteccao: float | None = None,
    ) -> None:
        super().__init__(
            identificador=identificador,
            pontos_de_vida=pontos_de_vida,
            assinatura_radar=assinatura_radar,
            velocidade=velocidade,
            armamentos=armamentos,
            alcance_radar=alcance_radar,
            probabilidade_deteccao=probabilidade_deteccao,
        )
        self.raio_de_acao = raio_de_acao
        self.teto_operacional = teto_operacional
