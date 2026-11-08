# 08 — Metodologia do Planejamento de Necessidades Logísticas (MPNL)

## Propósito e independência

**DECIDIDO (Missão 01):** MPNL planeja necessidades logísticas, estoque, sobressalentes, manutenção, disponibilidade e orçamento. É módulo integrado ao SISCAN, potencialmente utilizável sem simulação cartográfica. Este documento consolida a concepção, sem definir algoritmo, coeficientes ou implementação.

## Organização das Forças — estrutura de quatro níveis

**DECIDIDO:** preservar a estrutura de planejamento de quatro níveis abaixo. Ela é a hierarquia adotada para o SISCAN e não deve ser apresentada como reprodução integral da cadeia oficial de comando de cada Força.

| Nível | Marinha | Força Aérea | Exército |
|---:|---|---|---|
| 1 | Unidade-Tarefa | Elemento Aéreo | Unidade (Batalhão, Regimento ou Grupo) |
| 2 | Grupo-Tarefa | Unidade Aérea | Grande Unidade (Brigada) |
| 3 | Força-Tarefa | Força Aérea | Divisão de Exército |
| 4 | Força Naval Componente | Força Aérea Componente | Força Terrestre Componente |

**Marinha — DECIDIDO:** a sequência é Unidade-Tarefa → Grupo-Tarefa → Força-Tarefa → Força Naval Componente.

**Força Aérea — DECIDIDO com nomenclatura provisória:** preservar Elemento Aéreo → Unidade Aérea → Força Aérea → Força Aérea Componente. A nomenclatura e o aprofundamento da estrutura permanecem provisórios para revisão posterior; não substituir silenciosamente os níveis registrados.

**Exército — DECIDIDO:** preservar Unidade (Batalhão, Regimento ou Grupo) → Grande Unidade (Brigada) → Divisão de Exército → Força Terrestre Componente. **Não haverá nível de subunidade nesta estrutura.**

## Níveis do planejamento logístico

Os níveis de planejamento descrevem como uma necessidade é calculada e consolidada; não criam escalões adicionais nem alteram a hierarquia acima.

1. **Unidade (nível de origem):** registrar inventário, condição/disponibilidade, manutenção, consumo ou necessidade projetada e período no menor escalão organizacional incluído. Cada necessidade mantém sua unidade de origem e suas premissas.
2. **Força (nível de consolidação intermediária):** reunir necessidades das unidades subordinadas de acordo com a organização aplicável. Identificar apoio e recursos compartilhados, eliminar dupla contagem da mesma disponibilidade e preservar o vínculo às unidades que geraram a demanda.
3. **Organizacional/operacional (nível de consolidação superior):** agregar as necessidades das forças até o escalão operacional considerado, com totais rastreáveis, lacunas, incerteza e premissas. A consolidação não confunde demanda logística com importância organizacional ou valor de combate.

O responsável ainda deverá definir qual menor unidade será incluída em cada exercício/planejamento e as regras de demanda por material. A existência de quatro níveis organizacionais não define, por si só, os parâmetros quantitativos de consumo ou manutenção.

## Conceitos

- **Dotação inicial:** recursos disponibilizados no início do exercício ou período de planejamento.
- **Estoque de sustentação:** recursos destinados à manutenção e continuidade.
- **Necessidade de reposição:** diferença entre recursos disponíveis e necessidades logísticas projetadas.

## Sequência metodológica obrigatória

1. Determinar necessidades logísticas a partir de inventário, manutenção, disponibilidade, ciclo de vida, menor escalão incluído, horizonte e premissas documentadas.
2. Consolidar quantidades da unidade para a força e, então, para o nível organizacional/operacional, preservando rastreabilidade, recursos compartilhados, lacunas e incerteza.
3. **Somente depois** incorporar preços e elaborar orçamento por período.

**DECIDIDO:** não inverter a sequência. Preço não altera a identidade técnica de material ou equipamento.

## REGRA MPNL-001 — Consolidação Logística Ascendente

**DECIDIDO:** iniciar no menor escalão organizacional considerado no planejamento e progredir até o escalão operacional. Para cada linha consolidada:

- preservar a origem de cada necessidade e a trilha até a unidade que a gerou;
- registrar item/material, quantidade, condição, período e premissas/fonte quando conhecidos;
- identificar recursos compartilhados entre unidades ou escalões;
- evitar duplicidade ao consolidar disponibilidade, inventário e demanda compartilhados;
- considerar inventário de equipamentos, dados históricos de manutenção, disponibilidade e ciclo de vida;
- distinguir explicitamente necessidade logística, importância organizacional e valor de combate;
- não usar valor de combate como substituto de demanda de sobressalentes ou critério isolado de dimensionamento logístico.

### Aplicação por nível

| Nível | Operação documental/analítica prevista | Preservação necessária |
|---|---|---|
| Unidade | Identificar a necessidade e disponibilidade no menor nível incluído | Unidade de origem, item, condição, período, fonte e premissas |
| Força | Consolidar unidades subordinadas e reconhecer suporte compartilhado | Decomposição por unidade, regra de não duplicidade e recursos compartilhados |
| Organizacional/operacional | Consolidar forças até o nível de planejamento definido | Totais rastreáveis, lacunas, incerteza e vínculo aos níveis inferiores |

## Bases relacionadas, mas independentes

| Base | Responsabilidade conceitual | Exemplos de dados |
|---|---|---|
| Técnica | Identidade e características do material/equipamento | identificador, especificação, configuração, fonte |
| Logística | Inventário, manutenção, necessidade e disponibilidade | unidade, quantidade/condição, histórico, período, reposição |
| Econômica | Preço e premissas financeiras | valor, moeda, fonte, validade, cenário orçamentário |

Vínculos entre as três bases devem ser rastreáveis. Regras de identidade, vigência, unidade de medida e conversão ainda precisam de definição. Preços não alteram a identidade técnica do item.

## Produtos previstos

Cadastro mestre de materiais/equipamentos; inventário por unidade; histórico de manutenção; parâmetros preventivos/corretivos; necessidades agregadas de sobressalentes; estoques iniciais e projetados; necessidade de reposição; disponibilidade projetada; consolidação por escalão; posterior orçamento por período; cenários de restrição orçamentária e atrasos de fornecimento. Podem ser usados períodos longos, inclusive seis meses conforme cenário; seis meses não é duração fixa.

## Limites e pendências

**DECIDIDO:** não dimensionar armamentos/munições para otimizar operações contra uma força adversária.

**PENDENTE:** menor unidade efetivamente incluída em cada caso; taxonomia/material crítico; método de demanda/consumo/falha; dados escassos; lead time; níveis de serviço; compartilhamento entre unidades; arredondamentos; custos/inflação/câmbio; unidade de medida e conversões; validação acadêmica. Nenhum desses parâmetros foi preenchido por suposição. A estrutura de quatro níveis e a regra ascendente não constituem fórmula quantitativa pronta.
