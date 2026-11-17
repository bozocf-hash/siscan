# 113 — Especificação: julgamento didático no mapa

**Atualização de gate:** especificação aprovada pelo responsável por “sim”; plano de Fase 2 proposto em [114](114_PLANO_JULGAMENTO_DIDATICO_NO_MAPA.md). O conteúdo abaixo preserva o registro da proposta documental; a especificação não está mais aguardando aprovação.

**2026-11-17. Fase 1 proposta para revisão.** Continuidade solicitada por “pode seguir” após 112. Especificação completa no **Recorte 3** de [SPEC-force-confrontation.md](../../SPEC-force-confrontation.md), mantendo a convenção do módulo existente e a etapa 3 da ordem aprovada em 104. Entregas 108/112 permanecem concluídas.

Resultado proposto: no mesmo mapa/painel ATLANTICADOR, instrutor confere estado oficial, informa alterações didáticas, visualiza antes/depois, registra/revisa proposta e confirma ou rejeita. A confirmação usa exclusivamente o provedor durável de 112. Prévia/proposta não alteram os meios. O mapa recebe somente a projeção oficial após commit, com índice/perda/origem e regras de domínio comprovado.

A base de julgamento inclui composições, posições, referências técnicas e revisões de estado; mudança exige nova conferência. Reenvio de comando aplicado retorna recibo sem reaplicar. Retomada/histórico sobrevivem ao reload/reinício; grupos temporários perdidos impedem nova confirmação sem revalidar a composição, mas não apagam a decisão. Correção é nova proposta referenciada, sem desfazer histórico.

Inspecionados os contratos do Recorte 2, `cpc_map.py`, painel `cpc-preparation.mjs` e operações de `operational_state.py`. Lacunas de integração identificadas: preparação atual não contém estado oficial; provedor interno não oferece leitura pública de proposta/recibo para retomada gráfica; falta coordenação pública entre revisão dos grupos em memória e publicação SQL. O plano deverá tratar esses pontos sem acesso privado ou publicador duplicado.

Doze aceites JMAP-01–12 cobrem autorização/CSRF, base/revisões, ausência de efeitos em prévia/rejeição, confirmação única, concorrência, durabilidade, correção/perda, mapa/hover, privacidade, indisponibilidade e inspeção real em navegador isolado. Rotas e comandos futuros estão na especificação; verificadores novos ainda não existem.

Habilitação/verificação primeiro em banco/porta/cookie isolados com migração explícita do harness. Banco principal não será migrado/reiniciado automaticamente; ativação exige procedimento de entrega próprio. Não há cálculo de confronto, consumo, trajetória ou expansão de eficácia Command nesta proposta.

Somente documentação: nenhum código, banco, original, processo ou teste foi alterado/executado nesta etapa. Controles/documentos sincronizados com a pasta SISCAN e versionados no GitHub; planos anteriores preservados. Não foi produzido plano técnico ou lista de tarefas deste novo recorte.

A skill solicitada [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) determina “Stop after writing the spec”. Após revisão/aprovação desta especificação concreta, elaborar o plano técnico em turno próprio. A autorização de continuidade permitiu esta definição, sem antecipar aprovação do novo contrato gráfico/HTTP.
