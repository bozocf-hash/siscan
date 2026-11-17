# 111 — Tarefas de estado e adjudicação durável

**2026-11-17. Plano aprovado por “aprovado”; Fase 3 proposta para revisão.** A especificação já havia sido aprovada por “siga”. A lista concreta está em [tasks/operational-state/todo.md](../../tasks/operational-state/todo.md), com base no [plano](../../tasks/operational-state/plan.md) e na [especificação](../../SPEC-operational-state.md). Aprovações anteriores não estão pendentes.

OST-01–10 detalham validação/domínio, migração isolada, consulta autorizada, proposta, revisão/rejeição, confirmação integral, concorrência/idempotência, reinício/backup/restauração, documentação e sincronização. Cada tarefa informa aceite, verificação, dependências e até cerca de cinco arquivos por incremento; a manutenção documental foi dividida em subpassos.

Checkpoints A–D verificam migração, propostas sem efeitos, aplicação única e recuperação durável. OS-01–10 estão relacionados às tarefas. Depois de aprovada a lista, executar sequencialmente e comunicar resultados sem pedir novas confirmações rotineiras de checkpoint; alterações materiais exigem revisar o ponto afetado.

Não haverá escrita no banco principal, alteração de originais/DB3K, reinício de processo em uso ou novos botões de julgamento nesta fatia. O provedor interno precede a ligação ao mapa da etapa 3 de 104. Nenhuma tabela, código ou teste novo foi implementado/executado nesta fase documental; os comandos de teste são futuros.

Lista/controles sincronizados para a pasta SISCAN, links/diff e hashes dos planos antigos verificados e documentos versionados no GitHub. Planos anteriores do catálogo e confronto preservados.

A skill solicitada [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) determina: “Do not advance to the next phase until the current one is validated”. A aprovação recebida valida o plano; a próxima revisão é desta lista concreta antes de iniciar a Fase 4.
