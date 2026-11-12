"""Geometria estática e contatos privados de um ensaio inteiramente didático."""

from cpc_models import UnidadeMilitar, validar_numero


class CenarioTatico:
    """Matriz simétrica em milhas náuticas e rubrica fictícia de assinaturas.

    Informe um par por distância; a direção inversa é obtida automaticamente.
    A matriz deve cobrir todos os pares das unidades informadas. O cenário copia
    as entradas e não oferece movimento nesta etapa. Um novo cenário começa sem
    contatos. Fatores de assinatura são escolhas didáticas, não equações de radar.
    """

    def __init__(
        self, unidades: list[UnidadeMilitar],
        distancias: dict[tuple[str, str], float],
        fatores_assinatura: dict[float, float],
    ) -> None:
        self._unidades = {}
        for unidade in unidades:
            chave = unidade.identificador
            if not isinstance(chave, str) or not chave.strip() or chave in self._unidades:
                raise ValueError("Unidades do cenário precisam de identidades únicas e não vazias.")
            self._unidades[chave] = unidade
        self._distancias = {}
        for par, distancia in distancias.items():
            if (not isinstance(par, tuple) or len(par) != 2 or par[0] == par[1]
                    or any(chave not in self._unidades for chave in par)):
                raise ValueError("Distância exige um par de unidades distintas do cenário.")
            validar_numero(distancia, "distancia")
            chave = tuple(sorted(par))
            if chave in self._distancias and self._distancias[chave] != distancia:
                raise ValueError("Distâncias inversas conflitantes na matriz.")
            self._distancias[chave] = distancia
        total = len(self._unidades)
        if len(self._distancias) != total * (total - 1) // 2:
            raise ValueError("A matriz precisa cobrir todos os pares de unidades.")
        self._fatores_assinatura = dict(fatores_assinatura)
        for assinatura, fator in self._fatores_assinatura.items():
            validar_numero(assinatura, "assinatura_radar")
            validar_numero(fator, "fator_assinatura", 1.0)
        self._contatos: dict[tuple[str, str], tuple] = {}

    def validar_unidade(self, unidade: UnidadeMilitar) -> None:
        """Recusa outra instância que apenas reutilize o mesmo identificador."""
        if self._unidades.get(unidade.identificador) is not unidade:
            raise ValueError("A unidade não pertence a este cenário.")

    def distancia(self, unidade_a: UnidadeMilitar, unidade_b: UnidadeMilitar) -> float:
        """Consulta distância sem assumir zero para informação ausente."""
        self.validar_unidade(unidade_a)
        self.validar_unidade(unidade_b)
        if unidade_a is unidade_b:
            return 0.0
        return self._distancias[tuple(sorted((unidade_a.identificador, unidade_b.identificador)))]

    def fator_assinatura(self, assinatura: float | None) -> float:
        """Exige correspondência explícita na rubrica do cenário; não interpola."""
        validar_numero(assinatura, "assinatura_radar")
        if assinatura not in self._fatores_assinatura:
            raise ValueError("Assinatura radar sem fator didático declarado no cenário.")
        return self._fatores_assinatura[assinatura]

    def _contexto_contato(self, observador: UnidadeMilitar, alvo: UnidadeMilitar) -> tuple:
        return (observador.alcance_radar, observador.probabilidade_deteccao,
                alvo.assinatura_radar, self.distancia(observador, alvo))

    def _remover_contato(self, observador: UnidadeMilitar, alvo: UnidadeMilitar) -> None:
        self._contatos.pop((observador.identificador, alvo.identificador), None)

    def _registrar_contato(self, observador: UnidadeMilitar, alvo: UnidadeMilitar) -> None:
        self._contatos[observador.identificador, alvo.identificador] = self._contexto_contato(observador, alvo)

    def contatos_detectados(self, observador: UnidadeMilitar) -> frozenset[str]:
        """Visão direcional somente leitura; parâmetros alterados invalidam contato.

        Não há envelhecimento por tempo, compartilhamento entre aliados ou
        classificação/identificação do contato neste recorte estático.
        """
        self.validar_unidade(observador)
        contatos = set()
        for (origem, destino), contexto in tuple(self._contatos.items()):
            if origem == observador.identificador:
                alvo = self._unidades[destino]
                if contexto == self._contexto_contato(observador, alvo):
                    contatos.add(destino)
                else:
                    self._remover_contato(observador, alvo)
        return frozenset(contatos)
