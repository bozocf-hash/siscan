# 47 — Mapa de bases técnicas necessárias a GEO, AST e MPNL

**Status:** inventário conceitual anterior às APR-13–APR-20. Decisões sobre análise DB3K, dados GEO sintéticos iniciais, Calunga/SYM, MPNL, graus de confiança e relatórios ANA estão em [49](49_REGISTRO_DECISOES_APR_01_A_APR_20.md). Fontes cartográficas definitivas, validação semântica DB3K e bases quantitativas continuam pendentes; nomes de campos e sugestões não são decisão de aquisição.

## GEO — geografia e cartografia

| Base/conteúdo | Uso | Qualidade/proveniência necessária | Estado e lacunas |
|---|---|---|---|
| Costa/máscara terrestre vetorial | Validar posições e segmentos de deslocamento de navios de superfície e submarinos para impedir posição/deslocamento sobre terra (07 GEO-001/002). | Fonte, edição, data, escala/resolução, precisão horizontal, CRS/datum, cobertura, geometria válida, licença, transformações e incerteza. | Requisito de validação **DECIDIDO**; dataset, resolução, CRS, margem e atualização **PENDENTES**. |
| Camada base de referência (vetorial/raster/tiles) | Contexto visual de cenário e seleção de área. | Atribuição/licença, data, resolução, escala, disponibilidade/offline, CRS e limites de uso. | **IDENTIFICADO** no ATLANTICADOR que Leaflet/tiles externos existem; uso/termos para SISCAN **NÃO VERIFICADO**. Não usar tile visual como máscara de validação. |
| Geometrias de cenário/áreas | Zonas, pontos, limites e camadas do exercício. | CRS declarado, unidades, validade temporal, fonte/autor, precisão e versão. | Conceito GEO/SCN presente; taxonomia e formatos oficiais **PENDENTES**. |
| Dados para validação de percurso | Verificar linha/segmento entre estados temporais contra costa e margem. | Granularidade suficiente para resolução do movimento e regras de interseção aprovadas. | Regra de validar deslocamento **DECIDIDA**; algoritmos/tolerâncias não definidos. |
| Batimetria | Possível validação futura de profundidade submarina. | Fonte/licença, datum vertical, resolução, data e cobertura. | **DECIDIDO como possibilidade futura fora do requisito imediato**; não é dependência da primeira demonstração. |

### Fontes potenciais (categorias, não escolhas)

- Cartografia hidrográfica/topográfica oficial com metadados de costa e CRS.
- Geoportais públicos institucionais e bases geoespaciais com licença explícita.
- Datasets abertos globais como alternativa de estudo, condicionada à escala, generalização, data, licença e validação regional.
- Dados de exercício produzidos/validados pelo responsável como fixture didático, com indicação de que são sintéticos quando assim forem.

Nenhuma categoria acima é recomendação de fonte específica nem garante adequação. Registrar titular, termos, atribuição, obras derivadas, redistribuição e validade antes do uso. Definir margem costeira configurável sem confundi-la com incerteza de dado.

## AST — cadastro mestre de plataformas e equipamentos

| Base/conteúdo | Entidades/atributos conceituais | Qualidade/proveniência | Estado e lacunas |
|---|---|---|---|
| Catálogo de plataforma naval | Navios, submarinos, navios-aeródromo, navios-tanque e auxiliares; modelo/categoria, características suportadas pela fonte | Fonte primária, data, unidade, variante, estado de confiança, versão e aplicabilidade | Categorias identificadas em 05; campos, valores e fonte mestre pendentes. |
| Catálogo de aeronaves | Aeronaves embarcadas e baseadas em terra; modelo, versão, configuração e identificação individual quando conhecida | Identidade individual separada de modelo; país/fonte/data e variação | AST-03 decide vínculo a hospedeiro/base; atribuição temporal e cardinalidade pendentes. |
| Cadastro de equipamentos/sensores | Identidade, categoria, compatibilidade/configuração e parâmetros publicados | Documento técnico, edição, unidade, intervalo/condição e classificação de dado | Classes mencionadas em CMO/DB3K são referências; modelo SISCAN e semântica DB3K não confirmados. |
| Configuração | Associação de componentes e equipamentos a plataforma/configuração | Revisão, validade, condição de referência, fonte e incerteza | Separação de modelo/configuração/unidade **DECIDIDA**; identidade e cardinalidade pendentes. |
| Fonte de identificação | Documentação institucional autorizada, especificações públicas, documentação do fabricante, registros fornecidos e, como candidato secundário, DB3K | Deve permitir auditoria de origem e reconciliação de divergências; não preencher por inferência silenciosa. | DB3K contém DataShip/DataAircraft/DataSubmarine/DataSensor etc. e 75 FKs; unidade/semântica/ID estável não confirmados (04). |

### Regras de ingestão propostas

- Preservar valor original, unidade original, fonte e transformação aplicada.
- Normalizar unidade somente com regra documentada; manter relação ao dado de origem.
- Diferenciar ausência de informação, valor desconhecido, valor estimado e zero.
- Evitar misturar múltiplas variantes numa entidade sem chave de variante.
- Não atribuir sensor/equipamento a uma unidade real sem fonte; não derivar capacidades de nomes de tabelas.

## MPNL — dados necessários e sequência preservada

| Base/conteúdo | Uso logístico | Origem provável a avaliar | Lacunas |
|---|---|---|---|
| Inventário por unidade/escalão | Quantidade, condição, disponibilidade, item e período | Registros institucionais autorizados / cadastro produzido para exercício | Menor unidade, taxonomia, unidades, disponibilidade e corte temporal. |
| Cadastro técnico de material | Identidade, especificação, compatibilidade e unidade | AST e fonte técnica revisada | Identidade item/material e relação com componente/equipamento. |
| Histórico/parâmetro de manutenção | Manutenção preventiva/corretiva, condição, indisponibilidade e ciclo de vida | Registros/planos autorizados, documentação técnica | Política de falha, intervalo, qualidade e vigência. |
| Perfil de consumo/sustentação | Demanda por intervalo, regime e configuração | Dados técnicos validados ou parâmetros de exercício explicitamente hipotéticos | Fonte, unidade, cobertura, confiança e calibragem. |
| Estoque e compartilhamento | Existência, reserva, transferência, recursos compartilhados | Dados de inventário autorizados | Propriedade, local, alocação e deduplicação. |
| Necessidade/reposição/nível de suprimento | Consolidar demanda e lacuna por escalão/período | Derivada das bases anteriores sob método aprovado | Método, arredondamento, serviço, lead time e alçadas. |
| Preço individualizado/orçamento | Custo por material, moeda e vigência; agregação financeira | Fonte econômica autorizada e datada | Moeda, inflação/câmbio, validade e regras orçamentárias. |

### Sequência MPNL a preservar

1. Identificar as necessidades logísticas.
2. Identificar os níveis de suprimento.
3. Dimensionar as necessidades a partir dos inventários, equipamentos, manutenção e parâmetros de sustentação.
4. Consolidar as necessidades de baixo para cima, conforme a hierarquia organizacional de cada Força.
5. Identificar estoques, disponibilidade e necessidades de reposição.
6. Somente depois incorporar preços individualizados e elaborar o orçamento.

Esta redação detalha a regra MPNL-001 — Consolidação Logística Ascendente — sem alterar o encadeamento de 08. Ela preserva a estrutura de quatro níveis por Força, com Força Aérea provisória e Exército sem nível de subunidade. A ordem detalhada, taxonomias e parâmetros de demanda devem ser aprovados/validados; quantidades não podem ser deduzidas de valor de combate.

## Qualidade comum e gestão de fontes

Para cada dataset/campo: responsável, titularidade, fonte/versão, data de referência, data de ingestão, escala/unidade/CRS, cobertura, completude, acurácia/confiabilidade, transformação, licença e restrição de distribuição. Valores conflitantes ficam em disputa ou ligados à hipótese; não sobrescrever sem trilha. O sistema precisa preservar rótulo confirmado/estimado/hipótese e fonte em relatórios. Definição de escala de confiança é pendente.

## Gates antes de módulos

- **GEO:** fonte vetorial com direitos/CRS/resolução aprovados e casos de costa/terra definidos antes de aceitar validação.
- **AST:** glossário de entidade, chave SISCAN e unidades/proveniência antes de cadastro mestre; DB3K só após documentação semântica.
- **MPNL:** hierarquia MPNL preservada; menor unidade, itens, períodos, demanda/manutenção/compartilhamentos definidos; preços somente depois da necessidade.

Nenhuma das bases indicadas foi carregada ou alterada nesta missão.
