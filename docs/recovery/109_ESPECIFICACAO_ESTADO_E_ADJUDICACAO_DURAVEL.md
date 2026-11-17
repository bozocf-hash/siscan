# 109 — Especificação de estado e adjudicação durável

**Atualização de gate:** especificação aprovada pelo responsável por “siga”; plano de Fase 2 proposto em [110](110_PLANO_ESTADO_E_ADJUDICACAO_DURAVEL.md). O texto abaixo preserva o registro da fase documental anterior; sua aprovação não está mais pendente.

**2026-11-17. Fase 1 proposta para revisão.** Continuidade solicitada por “pode seguir” após a entrega 108. Segue a etapa 2 da ordem aprovada em [104](104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md), sem reabrir a seleção/conferência do par já entregue. Especificação completa em [SPEC-operational-state.md](../../SPEC-operational-state.md).

## Resultado proposto

Estado individual e histórico persistentes, com índice de origem separado de combustível/munição, referências de unidade/configuração, propostas versionadas, decisão do instrutor e efeitos antes/depois. Confirmação publica decisão, lote de efeitos e recibo numa transação; reenvio não aplica duas vezes. Rejeitar/revisar uma proposta não altera os meios. Ausência de avaliação não vira 100%.

Preservadas as faixas confirmadas de superfície: >60 combater, 40–60 inclusive navegar, <40 flutuar; não são regras de aeronave/submarino/terrestre. Perda é declaração separada, não consequência automática do índice. Regras de combustível e pendências de agregação/limiar de armamento permanecem conforme 81.

Propostas novas sujeitas à revisão: efeitos como atribuição absoluta de índice, correções rastreáveis de perda e implementação inicial do provedor sem novos controles gráficos. Essa etapa prepara a futura ligação julgamento → prévia → confirmação no mapa, sem anunciá-la como pronta.

## Base e limites da inspeção

Consultados 80, 81, 104, 108 e os contratos/código de `engine_units.py`, `engine_runtime.py`, `map_units.py` e preparação CPC. Identificados snapshots técnicos imutáveis, combustível de ensaio por execução e ausência de provedor oficial de estado operativo. Não houve nova auditoria DB3K, leitura integral das fontes históricas ou validação física de parâmetros. Referências anteriores mantêm seu escopo documental; não são novas decisões nesta etapa.

Dez critérios OS-01–10 cobrem limites do índice/domínio, autorização/visibilidade, ausência de efeitos em proposta/rejeição, transação integral, idempotência/concorrência, recuperação após reinício, migração/restauração e regressões. Comandos futuros registrados; verificadores novos ainda não existem e nenhum teste foi executado nesta etapa exclusivamente documental.

## Controle

Especificação e controles sincronizados para a pasta SISCAN e versionados no repositório. Nenhum código, banco, snapshot, original ou processo em uso foi modificado. Planos antigos do catálogo preservados; não foi criado plano técnico ou lista de implementação deste novo recorte.

A skill solicitada [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) determina: “Stop after writing the spec”. Portanto a próxima ação dependente é revisar/aprovar esta especificação; somente depois elaborar o plano técnico e sua migração em turno próprio. A autorização de continuidade foi usada para produzir a especificação concreta, sem tratar aprovação de 104/108 como aprovação antecipada deste novo contrato.
