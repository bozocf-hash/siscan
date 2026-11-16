# 89 — Grupamentos e dados descritivos: proposta de escopo do CPC

**Data: 2026-11-16. Estado: complemento de escopo proposto para revisão, com inventário descritivo efetuado.** Atende ao pedido de iniciativa analítica, composição de grupamentos com referências do catálogo e apoio explicável ao instrutor. Não é especificação aprovada, plano de implementação ou modelo calibrado de combate real. Não recomenda composição otimizada para derrotar forças reais.

## Objetivo e premissas explícitas

Propor uma evolução do protótipo de pares de unidades para apoio didático a grupamentos: composição rastreável; dados de catálogo consultáveis; recursos individuais preservados; hipóteses/regras de exercício identificadas; resultados propostos e decisão oficial do instrutor separados.

Premissas: usar os dados já compilados sem refazer a extração integral; preservar identidade/configuração e aprovações por finalidade de 53; composição limitada aos meios disponíveis ao partido; manter os níveis MPNL de 08; não usar a demonstração de esgotamento de 86 como autonomia real; não converter alcance, classe ou campos brutos de sensores em probabilidades reais de vitória/dano.

As capacidades existentes serão preservadas. Esta ampliação envolve catálogo, identidade/composição, inventário e CPC, com critérios verificáveis distintos; por isso apresenta primeiro o complemento do mapa de capacidades, conforme a skill spec-driven-development já solicitada pelo responsável. Não foram elaboradas especificações de módulos ou iniciada implementação nesta etapa.

## Evidência local: sensores e vínculos diretos

Consulta ao `DB3K_498.db3` original por SQLite URI `mode=ro` e `PRAGMA query_only=ON`. SHA-256 observado: `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`.

`DataSensor`: **6.747 registros, 78 campos**. Existem campos de identidade/classificação, limites descritivos, condições, periodicidade, resolução e famílias de equipamentos. Exemplos de nomes encontrados: `Type`, `Role`, `RangeMin`, `RangeMax`, `ScanInterval`, `Availability`, `MaxContactsAir`, `MaxContactsSurface`. Não foram extraídos valores de desempenho de sistemas específicos ou derivados coeficientes de eficácia.

| Associação direta examinada | Linhas | IDs de modelos distintos | Referências ao modelo sem correspondência | Referências ao sensor sem correspondência |
|---|---:|---:|---:|---:|
| `DataAircraftSensors` | 16.781 | 5.299 | 0 | 0 |
| `DataShipSensors` | 28.047 | 3.925 | 0 | 0 |
| `DataSubmarineSensors` | 5.179 | 686 | 0 | 0 |
| `DataGroundUnitSensors` | 392 | 183 | 0 | 0 |
| Total das linhas diretas | **50.399** | — | **0** | **0** |

FK declarada encontrada nessas tabelas: `ID` para o modelo correspondente. A correspondência `ComponentID` → `DataSensor.ID` foi medida por consulta; não se apresenta como FK declarada ao sensor. Ausência de referência sem correspondência demonstra cobertura de chaves nesse recorte, não semântica, unidade de medida, configuração válida ou desempenho.

Esse levantamento não inclui todos os caminhos indiretos por outros componentes, controles, montagens ou categorias de plataforma. Não é nova auditoria integral das 167 tabelas. Deve-se reaproveitar a compilação/grafo existentes para ampliar a navegação descritiva.

Completude literal: `RangeMax` apresenta 869 zeros e nenhum nulo; `ScanInterval`, 1.163 zeros e nenhum nulo. Esses zeros não foram interpretados como ausência de sensor, capacidade ou disponibilidade. Os campos consultados permanecem sem promoção para cálculo nesta verificação.

Inventário detalhado local: `siscan-prototype/data/cpc_sensor_inventory_20261116.json` no repositório de trabalho; na entrega SISCAN, `prototype/data/cpc_sensor_inventory_20261116.json`. O JSON contém metadados e contagens, não valores de desempenho por plataforma. Não integra o GitHub.

## Complemento proposto do mapa de capacidades

| ID estável existente | Próximo recorte proposto | Dependências preservadas |
|---|---|---|
| `technical-catalog` | Navegação descritiva de sensores, evidência, unidade/domínio/contexto e elegibilidade por finalidade | Sem depender da composição dos partidos |
| `unit-registry` | Identidade/configuração das unidades; definição/versionamento de grupamentos e vínculos de integrantes | `technical-catalog` |
| `party-inventory` | Conferência de disponibilidade, pertencimento e não duplicidade ao compor uma força | `unit-registry` |
| `force-confrontation` | Consumir composição validada e snapshots; executar regras didáticas explícitas; explicar resultados e registrar adjudicação | Provedores atuais de identidade, inventário e estado |
| `verification-recovery` | Verificar integridade de composição, contabilidade, permissões, repetibilidade e exportação | Frente transversal; não cria novo domínio |

Não criar dependência de `unit-registry` para `party-inventory`: a definição de grupo guarda as identidades; a disponibilidade/autorização é conferida pelo provedor de inventário antes de executar o exercício. Não introduzir ciclo. Não substituir o ciclo já aprovado de `technical-catalog` ou presumir aprovação de tarefas pendentes.

## Estrutura candidata do grupamento

Identificador SISCAN, partido/exercício, designação, domínio, vínculo organizacional MPNL quando definido, grupo superior opcional, lista de IDs de unidades e versão da composição. Cada unidade mantém configuração/snapshot próprios; o grupo não copia combustível, estoques ou avarias para uma reserva fictícia compartilhada.

A organização MPNL continua a de 08: Marinha Unidade-Tarefa → Grupo-Tarefa → Força-Tarefa → Força Naval Componente; Força Aérea Elemento Aéreo → Unidade Aérea → Força Aérea → Força Aérea Componente, com nomes provisórios; Exército sem subunidade. “Esquadrilha” é designação operacional pedida pelo responsável; sua correspondência aos níveis provisórios precisa ser explicitada, sem criar ou renomear escalão silenciosamente.

Critérios de composição propostos: apenas integrantes permitidos ao partido; IDs estáveis; quantidade disponível respeitada; ausência de ciclos; versão congelada por ensaio; cada unidade contabilizada uma vez, inclusive quando exibida em grupos superiores. Mudança de composição gera nova versão, não altera retroativamente o histórico.

## Parametrização didática e fatores a explicitar

| Camada | Conteúdo proposto |
|---|---|
| Evidência técnica | Fonte, versão, configuração, campo literal, unidade/domínio, limite de interpretação e aprovação por finalidade |
| Condição inicial | Posição, recursos por item, estado operativo de origem, restrições conhecidas e informações disponíveis a cada participante |
| Contexto do exercício | Objetivo de aprendizagem, horizonte, escala temporal e condições declaradas; não uma hipótese implícita de eficácia real |
| Regras do modelo | Versão da rubrica didática, entradas obrigatórias, hipóteses, parâmetros fictícios identificados e motivos de inaplicabilidade |
| Análise | Estado antes/depois por integrante, gastos, imobilizações, perdas propostas, lacunas e sensibilidade às hipóteses didáticas |
| Arbitragem | Instrutor aceita, altera ou rejeita a proposta, ou determina efeitos diretamente; fundamento e autoria preservados |

Uma composição heterogênea não recebe um índice universal por soma de classes, sensores ou HP. O resumo do grupo deve preservar dimensões e unidades compatíveis, permitir abrir cada integrante e identificar desconhecidos. Necessidade logística, importância organizacional e valor de combate continuam separados conforme MPNL-001.

Autonomia deve ser coerente com combustível/perfil/configuração; elevar a duração do loop não aprova um perfil real. Da mesma forma, “pacotes defensivos” de demonstração não identificam equipamentos reais, e um campo de alcance não constitui modelo completo de defesa ou de munição em voo.

## Casos de ensino propostos, sem otimização de forças reais

1. **Referência homogênea:** verificar identidade, contagem, recursos e registro dos efeitos com unidades de uma mesma referência de catálogo e parâmetros didáticos controlados.
2. **Composição heterogênea:** verificar que classes/configurações diferentes preservam dados próprios e que as diferenças apresentadas têm evidência ou hipótese identificada.
3. **Sustentação e restrições:** comparar estados/recursos ao longo do tempo sob condições controladas, com faltas de dados explícitas e regras de esgotamento de 87 preservadas.

Esses casos definem objetivos de verificação e aprendizagem, não quantidades, arranjos, sistemas ou procedimentos para vencer adversários. A composição é escolhida para a pergunta de ensino, não calculada como recomendação operacional.

## Próximo gate e limites

Revisar esse recorte e as responsabilidades antes de escrever as especificações por módulo. Pontos para revisão: vínculo da designação “esquadrilha” com MPNL; prioridade entre composição e consulta descritiva; forma de adjudicação didática; referência/agregação de indicadores coletivos. Não escolher pesos/coeficientes para forçar resultado e apresentá-lo como previsão física.

Nesta etapa houve consulta somente leitura e elaboração documental. Nenhum código, banco, original ou resultado do exercício foi alterado. Não foram executados novos testes de software, pois não houve alteração de código; as contagens/correspondências do inventário foram verificadas por consultas locais.
