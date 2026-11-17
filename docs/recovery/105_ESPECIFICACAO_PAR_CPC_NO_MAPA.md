# 105 — Especificação da seleção do par CPC no mapa

**Atualização de gate:** especificação aprovada por “siga”; plano proposto em [106](106_PLANO_PAR_CPC_NO_MAPA.md). O conteúdo abaixo registra a preparação histórica da Fase 1, sem implementação desta extensão.

**Data: 2026-11-17. Estado: escopo/ordem de 104 aprovados por “si”; Fase 1 do primeiro recorte proposta para revisão.** Extensão em [SPEC-force-confrontation.md](../../SPEC-force-confrontation.md), Recorte 2, preservando entregas 98/102.

Primeira ligação: instrutor seleciona AZUL/VERMELHO e prepara o dossiê pela interface do mesmo mapa ATLANTICADOR. Backend autoriza, confere composições/snapshots/adjudicação e associa manifesto das posições de planejamento. Duas forças selecionadas aparecem sem duplicar marcadores ou permitir plotagem no modo de conferência.

Contratos propostos: GET `/api/cpc/groups` e POST `/api/cpc/preparations`, exclusivos do instrutor participante, com sessão/CSRF existentes. Hash técnico de 98 preservado; posição/revisão geográfica tem manifesto separado. Snapshot inicial não é estoque atual; planejamento não é trajetória de combate.

CP-01–CP-12 cobrem autorização/identidade, seleção/conflitos, fontes, vista simultânea, isolamento de plotagem, respostas atrasadas, desconhecidos e ausência de efeitos. Plano posterior fechará módulos e comandos focados. Sem DDL, dependência ou código novo nesta etapa.

Não existe execução, julgamento ou confirmação oficial nesta fatia. O escopo completo de 104 prevê esses passos depois dos contratos de estado/adjudicação durável. A seleção isolada não será anunciada como confronto concluído.

Inspeção documental/de código: `cpc_group_preparation.py`, `map_groups.py`, `map_units.py`, `engine_runtime.py`, mapa de capacidades e decisões 80/81/104. Nenhum teste ou inspeção visual executado nesta fase.

A skill [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) exige “Stop after writing the spec (CRITICAL)”. Próximo gate: revisão desta especificação antes do plano; escopo 104 e entregas anteriores permanecem aprovados.
