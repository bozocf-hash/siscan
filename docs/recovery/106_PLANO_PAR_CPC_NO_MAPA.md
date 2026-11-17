# 106 — Plano da seleção do par CPC no mapa

**Atualização de gate:** plano aprovado por “sim”; tarefas propostas em [107](107_TAREFAS_PAR_CPC_NO_MAPA.md). O conteúdo abaixo registra a preparação histórica da Fase 2, sem implementação.

**Data: 2026-11-17. Estado: especificação de 105 aprovada por “siga”; plano de Fase 2 proposto para revisão.** [Plano técnico](../../tasks/force-confrontation/mapa/plan.md) do Recorte 2 de [force-confrontation](../../SPEC-force-confrontation.md), preservando os planos anteriores e entregas 98/102.

O plano liga provedor autorizado, dossiê 98, posições de planejamento, rotas e painel/camada de consulta no mapa existente. Define hash técnico, geográfico e de vista separadamente. O instrutor vê o par; operadores são recusados antes da leitura adversária. Não há execução, proposta de impactos, confirmação oficial ou persistência nesta fatia.

Ordem: provedor de lista/captura/projeção; HTTP; checkpoint A de preservação; seleção/assincronia; camada simultânea/retorno ao planejamento; checkpoint B no navegador; documentação/sincronização. Tarefas detalhadas serão propostas após aprovação do plano, no mesmo diretório, sem sobrescrever listas antigas.

Inspeção: `map_groups.py`, `cpc_group_preparation.py`, rotas/registro do servidor e `atlantic-bridge.mjs`. Testes futuros em banco/cookie/porta isolados, sem mover meios do usuário. Grupos e posições podem mudar após uma leitura; a vista identifica o que foi conferido e não reserva disponibilidade futura.

Nenhum teste, inspeção visual ou mudança de código/banco foi executado nesta fase documental. A skill [planning-and-task-breakdown](C:/Users/bozoc/.codex/skills/planning-and-task-breakdown/SKILL.md) exige “The human has reviewed and approved the plan”. Próximo gate: revisão do plano antes de detalhar Fase 3; especificação e escopo já aprovados.
