"""Estruturas didáticas do CPC, sem resolução de combate ou persistência.

As unidades declaradas são convenções deste módulo, não interpretações dos
campos brutos do DB3K. A integração futura exige conversão e validação explícitas.
Type hints documentam o contrato; estes construtores não validam entradas externas.
"""

from typing import Literal


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
    """

    def __init__(
        self,
        *,
        identificador: str,
        tipo: Literal["missil_antinavio", "missil_ar_ar", "defesa_ponto"],
        quantidade: int,
        pk: float | None = None,
        dano: float | None = None,
    ) -> None:
        self.identificador = identificador
        self.tipo = tipo
        self.quantidade = quantidade
        self.pk = pk
        self.dano = dano


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
    """

    def __init__(
        self,
        *,
        identificador: str,
        pontos_de_vida: float,
        assinatura_radar: float | None,
        velocidade: float,
        armamentos: list[Armamento] | None = None,
    ) -> None:
        self.identificador = identificador
        self.pontos_de_vida = pontos_de_vida
        self.assinatura_radar = assinatura_radar
        self.velocidade = velocidade
        self.armamentos: list[Armamento] = (
            list(armamentos) if armamentos is not None else []
        )


class MeioNaval(UnidadeMilitar):
    """Especializa uma unidade naval com uma capacidade didática declarada.

    Attributes:
        capacidade_defesa_ponto: Probabilidade didática de interceptação entre
            0 e 1 na regra sintética atual; None indica não avaliado. Substitui a
            escala abstrata inicialmente proposta. Não é eficácia real validada
            nem quantidade de munição; não modela consumo da defesa nesta etapa.

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
    ) -> None:
        super().__init__(
            identificador=identificador,
            pontos_de_vida=pontos_de_vida,
            assinatura_radar=assinatura_radar,
            velocidade=velocidade,
            armamentos=armamentos,
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
    ) -> None:
        super().__init__(
            identificador=identificador,
            pontos_de_vida=pontos_de_vida,
            assinatura_radar=assinatura_radar,
            velocidade=velocidade,
            armamentos=armamentos,
        )
        self.raio_de_acao = raio_de_acao
        self.teto_operacional = teto_operacional
