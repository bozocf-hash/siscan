# 95 — Plano de preparação dos grupamentos CPC

**Data: 2026-11-16. Estado: especificação aprovada por “siga”; plano de Fase 2 proposto.** O responsável aprovou a proposta de 94. O [plano](../../tasks/force-confrontation/plan.md) detalha o consumidor da [especificação](../../SPEC-force-confrontation.md), preservando a entrega 93 e os planos antigos do catálogo.

O plano propõe uma função pura para preparar o dossiê dos partidos AZUL/VERMELHO: autorização por provedor confiável, visões isoladas do inventário, operações públicas do registro, snapshots integrais e conferência final de revisões observadas. Não cria autenticação, persistência, exportador, mapa ou combate de grupamentos.

Sequência: fluxo autorizado válido; recusas e alteração de revisão; checkpoint A de preservação; cópias/hash; regressões/documentação; checkpoint B completo. Critérios GP-01–GP-12 serão detalhados na lista de Fase 3 após aprovação do plano. Não há checklist de implementação aberto nesta etapa.

Não existe transação atômica entre dois registros/inventários externos. O provedor deve entregar vista consistente, e uma preparação não reserva disponibilidade futura. Esse limite é explícito; a saída exige revisão do instrutor e informa simulação não iniciada.

Evidências utilizadas: contrato público de `unit_groups.py`, especificação aprovada, entregas 89/93/94, estrutura documental por módulo e planos existentes. Os comandos de teste no plano são futuros: nenhum teste de software foi executado e nenhum código ou banco foi modificado.

Próximo gate: responsável revisar o plano antes de detalhar tarefas. A skill [planning-and-task-breakdown](C:/Users/bozoc/.codex/skills/planning-and-task-breakdown/SKILL.md) exige “The human has reviewed and approved the plan”. Não reapresentar como pendentes as aprovações da especificação ou da entrega 93.
