# 100 — Plano dos grupamentos no mapa definido

**Data: 2026-11-16. Estado: especificação de 99 aprovada por “siga”; plano proposto para revisão.** [Plano técnico](../../tasks/unit-registry/mapa/plan.md) do Recorte 2 de [unit-registry](../../SPEC-unit-registry.md), sem reabrir a composição/dossiê já entregues em 93/98. Organização por módulo/recorte preserva planos antigos.

O plano liga identidades/autorização ao registro compartilhado do servidor e à aba de grupos no mapa ATLANTICADOR existente. Reutiliza sessão/CSRF, métodos públicos do registro e índice de marcadores; realce de grupo é separado da seleção de plotagem, para não mover unidades por consulta. Resposta atrasada e revogação precisam ser tratadas no servidor/cliente.

Ordem: provedor de identidade/elegibilidade; consulta contextual/rotas/registro por servidor; checkpoint A; painel/formulário/assincronia; realce e navegador real isolado; checkpoint B; documentação/sincronização. Tarefas detalhadas serão propostas somente após aprovação deste plano.

Inspeção confirmou ainda: schema atual das instâncias é sintético e possui unicidade por exercício/partido/finalidade; o servidor usa ThreadingHTTPServer; SISCAN_PORT não isola os caminhos da base; o adaptador do mapa já possui painel/seleção/markerIndex. As limitações devem aparecer na tela: instâncias sem snapshot/domínio ficam pendentes, e grupos se perdem no reinício.

Testes planejados: provedor/HTTP em base e porta isoladas, módulo JS para estados/assincronia, regressões do registro/mapa e navegador real antes de declarar entrega visual. Nenhum novo verificador existe ou foi executado nesta etapa; não houve inspeção visual da proposta, código, banco ou estado oficial alterado.

A skill [planning-and-task-breakdown](C:/Users/bozoc/.codex/skills/planning-and-task-breakdown/SKILL.md) exige “The human has reviewed and approved the plan”. Próximo gate é a revisão deste plano; especificação de 99 já aprovada. Não substituir o mapa, instalar outro motor ou ampliar esta etapa para confronto temporal/persistência.
