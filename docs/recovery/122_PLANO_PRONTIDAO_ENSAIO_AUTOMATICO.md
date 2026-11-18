# 122 — Plano de prontidão do ensaio automático

**Estado: plano técnico aprovado por “prossiga”; especificação aprovada por “sim”.** Fase 2 do Recorte 4-A de `force-confrontation`.

Documento canônico: [tasks/force-confrontation/prontidao/plan.md](../../tasks/force-confrontation/prontidao/plan.md). Especificação em [121](121_ESPECIFICACAO_PRONTIDAO_ENSAIO_AUTOMATICO.md) e SPEC-force-confrontation.

O plano organiza serviço de diagnóstico, consulta HTTP autorizada, preenchimento progressivo de hipóteses, invariantes e percurso real no navegador. Primeiro caminho visível: par preparado → conferência sem hipóteses → pendências por meio. Em seguida, validação de um perfil completo para o par aéreo sintético controlado. Não há execução, publicação de resultado, alteração de schema ou promoção de dados Command.

Decisões técnicas do plano aprovado: API pública de contexto existente, escopo SQL de leitura, reconferência das fontes, hashes canônicos e nenhuma criação de RNG; hipóteses com unidade/origem explícitas; diagnóstico distinto de erro; painel único, sem edição obrigatória de JSON e sem ocupar o mapa com todos os campos simultaneamente. Incluídos os doze AUTO-READY, checkpoints, arquivos candidatos e comandos de verificação.

A convenção dos recortes `mapa/` e `julgamento/` foi mantida. Os planos do catálogo na raiz de tasks continuam preservados, inclusive suas pendências. A lista detalhada `prontidao/todo.md` pertence à Fase 3, proposta posteriormente em 123; não havia sido criada na etapa de planejamento.

Nesta etapa: inspeção somente leitura do código e edição documental. Nenhum teste, servidor, código de produção, banco ou original alterado. A aprovação do plano permitiu detalhar as tarefas em [123](123_TAREFAS_PRONTIDAO_ENSAIO_AUTOMATICO.md); não significa aprovação da implementação.
