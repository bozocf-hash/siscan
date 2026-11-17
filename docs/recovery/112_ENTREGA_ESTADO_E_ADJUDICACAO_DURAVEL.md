# 112 — Entrega: estado e adjudicação durável

**2026-11-17. OST-01–10 concluídas.** Especificação aprovada por “siga”, plano e lista aprovados por “aprovado”. Contratos em [SPEC-operational-state.md](../../SPEC-operational-state.md), [plano](../../tasks/operational-state/plan.md) e [tarefas](../../tasks/operational-state/todo.md). Entrega do provedor interno da etapa 2 de 104, sem ligação gráfica de julgamento ou execução de combate.

## Comportamento entregue

- `operational_state.py`: consulta autorizada, registro/revisão de propostas, rejeição, confirmação integral, correção referenciada e histórico. Somente instrutor participante e ativo publica efeitos. Operador consulta estado confirmado do próprio partido, sem motivos privados ou composição adversária.
- Proposta/revisão/rejeição preservam o estado dos meios. Confirmar reconfere cenário, adjudicação, identidade/snapshot/configuração e revisões; decisão, efeitos e recibo entram na mesma transação. Falha entre integrantes reverte tudo.
- Índice de origem permanece separado de recursos e perda. Ausência não vira 0%/100%; faixas >60 combater, 40–60 navegar e <40 flutuar valem somente com evidência de superfície. Perda é explícita; aumentar índice não recupera meio perdido. Correção de perda exige referenciar a decisão do estado atual.
- `operational_state_storage.py`: migração explícita, aditiva/versionada, seis tabelas com FKs, índices e histórico imutável. Estado corrente é projeção do histórico confirmado; não há segunda tabela mutável de prontidão. Schema parcial/divergente ou integridade incompatível são recusados.
- Evidência de domínio compartilhada por `engine_units.configuration_domain`, preservando o contrato anterior da ponte de grupos. O provedor atual demonstra somente a configuração aérea sintética; os testes de superfície são fixtures declaradas, não homologação de navios reais.

O contrato dos payloads e os comandos de uso/verificação estão no README do protótipo. Fonte aceita nesta fatia é `didactic`; não há parâmetros reais de combate, sorteio ou produtor automático. `origin` é referência declarativa congelada, não prova de autoridade/disponibilidade. Snapshot/referências das unidades são conferidos no servidor. Sem estado confirmado, `consultar` retorna revisão 0 e ausência explícita, sem INSERT.

## Persistência, transações e integridade

Propostas/revisões, decisões, efeitos e recibos estão no SQLite, com autoria, instante do servidor, justificativas, antes/depois e hashes canônicos. O grupo em memória não é FK do histórico; sua perda não apaga decisões. Reenvio idêntico autorizado devolve recibo histórico; outro conteúdo/contexto/operação recusa, sem reaplicação.

Comandos reutilizam `engine_runtime.atomic`. Fora de transação externa, a operação confirma seu lote; dentro dela, o commit é responsabilidade do chamador. O retorno antes desse commit não é promessa de durabilidade. Rollback externo também desfaz decisão, efeitos e recibo. Consulta/histórico usam vista SQL consistente e não gravam estado.

Migração exige conexão independente com FKs habilitadas, usa `BEGIN IMMEDIATE` e declarações completas por `execute`; não depende de `executescript` ou desativação de FKs. Valida versão/schema/integridade e reexecução. Falha no DDL reverte o lote. `app.initialize` não foi alterado para migrar automaticamente.

Leitura confere a cadeia selecionada contra proposta, recibo e referências, detectando elo removido e inconsistência de antes/depois mesmo com hash de um registro recalculado. Não se promete proteção criptográfica contra administrador capaz de reescrever coerentemente todo o banco. Verificações de schema/FK e cadeia têm custo de leitura; não houve benchmark de escala ou auditoria integral de todo histórico em produção.

## Evidências executadas

**95 testes nomeados distintos passaram**, sem dupla soma:

| Verificador | Testes |
|---|---:|
| `check_operational_state.py` | 27 novos |
| `check_operational_state_storage.py` | 19 novos |
| `check_cpc_map.py` | 14 regressões |
| `check_cpc_group_preparation.py` | 21 regressões |
| `check_map_groups.py` | 6 regressões |
| `check_map_groups_http.py` | 8 regressões |

Também passou o verificador assertivo `check_map_units.py`. `git diff --check` sem erros. TDD observado para validação/leitura, migração, propostas/revisões, confirmação e integridade; erros encontrados nos ciclos foram corrigidos e os verificadores afetados repetidos. Nenhuma dependência instalada.

| Critérios | Evidência |
|---|---|
| OS-01/02/09 | Fronteiras 0/40/60/80/100 e vizinhas, ausência, booleano/NaN/infinito/inteiro enorme; domínio comprovado, perda/correção explícitas e leitura sem escrita |
| OS-03/04 | Papel/participação/revogação/partido; rejeição/revisão sem efeitos, revisão antiga recusada e motivos privados removidos da consulta de operador |
| OS-05/06 | Falha SQL entre integrantes, rollback integral, duas conexões concorrentes, mesma proposta/comando e propostas disputando revisão da unidade; replay e transação externa |
| OS-07/08 | Processo Python novo abre arquivo commitado e recupera estado/histórico/recibo sem registro de grupos; backup por `Connection.backup`, restauração em terceiro arquivo e checks SQLite; corrupção e DDL parcial recusados |
| OS-10 | Regressões acima; comparação das tabelas não operativas antes/depois, planos antigos por SHA-256 e entrega sem bancos/originais |

Todos os dados foram descartáveis: schema e seed existentes do harness, SQLite em memória/arquivos temporários e HTTP em porta/cookie próprios. Não houve inspeção gráfica nova: este recorte não altera UI. Não se declara validação de interface de julgamento, teste de migração em cópia da base real ou análise nova do DB3K.

## Implantação e próximo recorte

Código/documentação sincronizados com a pasta SISCAN por SHA-256 e commits publicados na branch existente. Banco principal, originais/DB3K, snapshots reais, mapas preparados e processos em uso preservados; não há DDL automático no servidor ativo. Os planos independentes do catálogo permanecem com seus hashes anteriores.

Para usar no principal será necessário procedimento de implantação próprio, com backup consistente verificado, janela sem escritores, migração explícita, verificação e política de restauração que não descarte escritas posteriores. Esta entrega não executou esse procedimento nem promete disponibilidade de novas operações na interface atual.

Próxima etapa conforme 104: especificar a ligação **julgamento didático → prévia → confirmação → consulta dos efeitos no mesmo mapa**, consumindo este provedor, sem duplicar a publicação. Reconferir composição e fontes no futuro adaptador CPC; origem congelada não reserva grupo ou disponibilidade. Regras de recursos, agregação de armamento, índices de força e produtor automático permanecem em seus contratos próprios. Resultado oficial continua sendo decisão do instrutor.
