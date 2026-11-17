# 114 — Plano: julgamento didático no mapa

**Atualização de gate:** plano aprovado pelo responsável por “sim”; lista de Fase 3 proposta em [115](115_TAREFAS_JULGAMENTO_DIDATICO_NO_MAPA.md). O texto abaixo preserva a proposta documental anterior; aprovação do plano não está mais pendente.

**2026-11-17. Especificação 113 aprovada por “sim”; Fase 2 proposta para revisão.** Plano completo em [tasks/force-confrontation/julgamento/plan.md](../../tasks/force-confrontation/julgamento/plan.md), seguindo o Recorte 3 de [SPEC-force-confrontation.md](../../SPEC-force-confrontation.md). A continuidade posterior confirmou como próximo marco uma versão parcial utilizável pelo instrutor, antes do automático.

Marco verificável: no mapa ATLANTICADOR existente, selecionar o par, julgar, conferir prévia, registrar/revisar, confirmar/rejeitar e consultar efeitos/histórico. A entrega só será concluída depois do percurso real em navegador isolado; testes de backend sozinhos não representam aplicativo integrado.

O plano reaproveita o publicador de 112, adiciona leituras públicas de proposta/recibo e coordenação pública de revisões do registro de grupos. Ordem proposta para novas escritas: reserva SQL → escopo do registro → revalidação/aplicação → commit antes de liberar o registro. Conexão independente, sem acesso privado, mutação de grupos no escopo ou alegação de transação distribuída.

Base própria inclui estado oficial, composição, snapshots e posições. Preview não grava; confirmação usa exatamente a revisão aceita. Replay autorizado consulta recibo antes de exigir grupos ainda disponíveis, sem reaplicar efeitos. Retomada/correção preservam histórico. Estado oficial é projetado no mapa/hover/lista, com privacidade por partido e sem indicadores inventados.

Prévia usa pasta de teste persistente, migração explícita, porta/cookie próprios e nenhum reseed ao reabrir a mesma base. Reinício não reconstrói grupos temporários. Principal 8787, originais e DB3K preservados; sua habilitação/migração exige procedimento próprio. Automático continua etapa 4 de 104.

Sequência/checkpoints A–D: provedores públicos → adaptador/base/decisões → HTTP/projeção → painel/mapa → navegador/recuperação → documentação/entrega. Após aprovação, detalhar lista própria em `tasks/force-confrontation/julgamento/todo.md`, sem sobrescrever outros planos.

Somente documentação nesta fase: nenhum código, banco, original ou processo modificado e nenhum teste executado. Documentos/links/diff e planos antigos verificados; arquivos sincronizados para SISCAN e versionados no GitHub. Não foi criada lista de implementação.

A skill solicitada [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) orienta: “Do not advance to the next phase until the current one is validated”. A revisão deste plano antecede as tarefas; a especificação já está aprovada e não precisa ser reaprovada.
