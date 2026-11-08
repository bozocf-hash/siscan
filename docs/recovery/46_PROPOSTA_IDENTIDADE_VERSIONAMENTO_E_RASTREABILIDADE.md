# 46 — Proposta conceitual de identidade, versionamento e rastreabilidade

**Status:** proposta elaborada antes das APR-10–APR-12. Identidade interna SISCAN, preservação contextual de meios, alteração de cenários publicados durante a execução e transferência de aeronave foram decididas com limites em [49](49_REGISTRO_DECISOES_APR_01_A_APR_20.md). Esquema físico, granularidade e regras detalhadas de versionamento permanecem pendentes; nenhuma migração ou implementação foi autorizada.

## Princípios de identidade

1. Cada entidade controlada pelo SISCAN deve receber identificador estável, sem depender de nome, posição, caminho de arquivo ou chave externa mutável.
2. ID externo (por exemplo, DB3K) é atributo de proveniência/mapeamento, não ID canônico SISCAN, até comprovar semântica, unicidade e estabilidade entre versões.
3. Entidades-mestre de referência devem ser distinguidas das instâncias específicas de cenário/exercício.
4. Revisões publicadas/submetidas são preservadas; correções criam nova versão/evento em vez de sobrescrever história silenciosamente.
5. Identidade, configuração e vínculo temporal são conceitos distintos.

## Plataforma, configuração e unidade individual

| Conceito | Definição proposta | Identidade e relação |
|---|---|---|
| PlataformaModelo | Tipo/modelo de plataforma cadastral (ex.: classe/tipo, não unidade do exercício) | ID SISCAN estável; guarda fabricante/tipo/categoria quando fontes suportarem, atributos e proveniência. Possui uma ou mais ConfiguraçõesVersionadas. |
| ConfiguraçãoPlataforma | Arranjo específico de equipamentos, sensores, sistemas e parâmetros logísticos que aplica a um modelo | ID próprio e revisão; validade/configuração-fonte; não assume que a configuração é uma unidade real. |
| Equipamento/Sensor | Item mestre com identidade técnica e metadados próprios | ID próprio; pode ser associado a configuração e ter relações de componente, posição, quantidade e intervalo de validade, conforme regras futuras. |
| UnidadeIndividual | Meio individual identificado para cadastro/planejamento, quando houver evidência de identidade | ID SISCAN próprio, distinto de modelo; pode referenciar modelo/configuração e cadastros externos. A mesma unidade mestre pode ser mencionada em mais de um cenário sem compartilhar o estado didático. |
| InstânciaDeUnidadeNoCenário | Ocorrência da unidade, com estado, configuração aplicada, equipe, posição e condições específicas de uma versão de cenário/exercício | ID de instância próprio + referência opcional à UnidadeIndividual; guarda snapshot/referência versionada de dados que determinam o exercício. Não altera o cadastro mestre. |

Essa separação evita confundir “modelo” (categoria), “configuração” (arranjo técnico) e “unidade” (meio individual). Campos e relações precisam ser validados com domínio, fontes e casos reais/acadêmicos antes de qualquer schema.

## Aeronave e plataforma hospedeira/base

**Proposta:** uma aeronave individual referencia seu próprio registro de identidade/configuração e uma atribuição de hospedagem ou base com escopo temporal/contextual. Um navio-aeródromo ou base é entidade distinta; associação registra início/fim ou vínculo na versão do cenário. Para um exercício, a atribuição pode ser congelada em snapshot da versão. Não modelar a aeronave como mero componente do navio se sua identidade individual e ciclo de vida precisarem persistir. Cardinalidade (uma base simultânea, transferência, disponibilidade) é **PENDENTE**.

## Unidade ao longo de cenários

**Proposta:** manter separado (a) cadastro mestre de unidade individual, se aplicável, (b) instância contextual no cenário, e (c) estado temporal durante o exercício. Assim, a unidade pode ser reconhecida em diversos cenários, mas cada cenário fixa a configuração, origem, equipe, posição e condições usadas. Para unidade hipotética/sintética, criar identidade no escopo do catálogo didático e indicar `sintética/estimada`, sem inventar equivalência com uma unidade real. Relações e visibilidade permanecem sujeitas às permissões de exercício.

## Cenários e versões

**Proposta:** cenário possui identidade estável e versões ordenadas. Rascunhos são mutáveis dentro de regra aprovada; publicar/congelar cria uma versão identificada, que exercícios referenciam. Alteração posterior cria nova versão, sem reescrever a versão usada em exercício em andamento/concluído. Deve-se registrar versões dos dados de referência, parâmetros, geometrias, meios e premissas incluídas. Clonagem/branch é possível apenas se aprovado e deve preservar a origem.

Perguntas: cenário fica imutável após publicação? Mudança exige versão nova? Exercício pode migrar de versão? Uma correção crítica pode atualizar exercício ativo? São questões do responsável em 48/Q-10.

## Temporalidade de configuração

Configuração/equipamento/hospedagem podem variar no tempo. **Proposta:** registrar validade ou intervalo aplicável no catálogo de referência; a instância do cenário mantém uma fotografia/referência da revisão válida. Não é necessário supor um esquema bitemporal. Caso seja importante distinguir “quando era válido” de “quando foi registrado no sistema”, isso precisa ser requisito explícito.

## Dados de referência versus dados do exercício

| Referência/catálogo | Específico de exercício |
|---|---|
| PlataformaModelo, equipamento, sensor, fonte, unidade de medida, configuração versionada, regra de validade | Versão de cenário, instância de unidade, lado/equipe didática, condição inicial, posição, resposta, justificativa, adjudicação e avaliação |

Dados de referência não recebem alterações originadas de resposta do aluno. Exercício captura referências/revisões necessárias para reproduzir seu contexto. Cópia de cadastro para versão de exercício não significa duplicação de semântica ou autorização de edição.

## Identidade de outros objetos

Proposta de ID estável para força, cenário, versão de cenário, exercício, participante (referência a conta institucional, evitando duplicar PII), submissão, revisão de submissão, avaliação, adjudicação, posição/evento e evento de auditoria. IDs devem ser opacos e não conter classificação/segredo. A política de geração, exposição e retenção fica pendente de decisão arquitetural.

## Proveniência e confiança

Para dado de referência relevante, registrar fonte/origem, identificador externo, edição/versão da fonte, data de coleta/referência, unidade/CRS quando espacial ou físico, processo de transformação, grau/descritor de confiança e estado `confirmado`, `estimado` ou `hipótese`. Não atribuir valor de confiança numérico sem escala aprovada. Para valor inferido, identificar responsável e justificativa.

Para cada mudança de cenário, cadastro ou submissão, preservar ator, instante, objeto, revisão anterior/nova, ação, justificativa quando requerida e fonte/versão contextual. Resultado liberado deve apontar versão de cenário e submissão avaliada.

## Limites de equivalência externa

- DB3K: 167 tabelas/75 FKs estruturais não determinam domínio, unidade, cardinalidade semântica ou estabilidade de IDs; não usar como identidade canônica sem verificação (04,37).
- ATLANTICADOR: `elements`, `effects`, `confrontations`, `body` JSON e revisões pertencem ao modelo de aplicação daquele produto; não são entidades SISCAN equivalentes (20,27,37).
- CMO: cenário/lado/unidade/hospedagem/mission/trigger-action são referências do manual; relações descritas não comprovam ER ou chaves (12–15,37).

## Decisões solicitadas

Aprovar ou ajustar identidade mestre versus instância de cenário, IDs próprios SISCAN, versionamento imutável de versões publicadas, representação de hospedagem temporal, snapshot de referência por exercício e campos mínimos de proveniência. Até aprovação, tudo permanece proposta conceitual.
