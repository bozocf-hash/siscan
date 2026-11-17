# 110 — Plano de estado e adjudicação durável

**Atualização de gate:** plano aprovado pelo responsável por “aprovado”; lista de Fase 3 proposta em [111](111_TAREFAS_ESTADO_E_ADJUDICACAO_DURAVEL.md). O conteúdo abaixo preserva o registro da proposta anterior; a aprovação do plano não está mais pendente.

**2026-11-17. Fase 1 aprovada por “siga”; Fase 2 proposta para revisão.** Plano completo em [tasks/operational-state/plan.md](../../tasks/operational-state/plan.md), baseado na [especificação aprovada](../../SPEC-operational-state.md). Preservadas as etapas de 104 e a entrega gráfica 108.

O provedor interno registrará proposta/revisões, decisão, efeitos e recibo de forma durável. Estado corrente será lido do histórico confirmado, sem tabela paralela mutável. Confirmação do instrutor será um único lote transacional com revisões e idempotência; rejeição/revisão não alterará os meios.

Inspeção do código confirmou `engine_units.context/list_units/encoded`, transações de `engine_runtime.atomic`, FKs em `app.connect`, validação aérea sintética privada em `map_groups` e uso de `executescript` na inicialização existente. O plano prevê extrair a evidência de domínio para função pública de identidade e executar migração aditiva própria, sem commits implícitos de `executescript` no lote. Isso não autoriza novos domínios técnicos ou validação real de meios.

Propostas técnicas: seis tabelas novas; referências de origem congeladas sem FK para grupos em memória; histórico imutável; classificação/perda separadas; operação de recuperação testada em cópia e processo novo. O provedor não dependerá do modelo de confronto e não importará o mapa. Migração do principal e conexão da interface permanecem fora desta etapa interna.

Sequência: validação/consulta → armazenamento/migração → proposta/revisão/rejeição → confirmação integral → concorrência/recuperação → documentação/entrega. Checkpoints A–D e matriz OS-01–10 constam do plano. Após aprovação, detalhar a lista em `tasks/operational-state/todo.md`; não sobrescrever os planos antigos.

Nenhum código, DDL, banco, original ou processo foi alterado. Não foram executados testes nem criada lista de implementação; verificadores novos são futuros. Documentos/links/diff verificados, sincronizados para SISCAN e versionados no GitHub.

A revisão do plano antecede a Fase 3 conforme a skill solicitada [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md): “Do not advance to the next phase until the current one is validated”. Aprovar a especificação não equivale a aprovar antecipadamente este plano de armazenamento/migração.
