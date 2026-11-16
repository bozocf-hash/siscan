# 92 — Tarefas propostas para grupamentos

**Data: 2026-11-16. Estado: Fase 3 para revisão.** O responsável aprovou o plano de `unit-registry` por “aprovado”. A lista detalhada está em `tasks/unit-registry/todo.md`, no diretório próprio escolhido para este módulo. Nenhuma implementação foi iniciada.

## Sequência proposta

| Tarefa | Resultado |
|---|---|
| UGR-01 | Criar/consultar composição com contexto, identidade, snapshots, hash, reenvio e exclusividade verificados |
| UGR-02 | Revisar com versão esperada, histórico e troca indivisível de vínculos |
| UGR-03 | Arquivar por versão inativa, liberar vínculos atuais e preservar referências anteriores |
| UGR-04 | Preparar composição com inventário atualizado sem iniciar simulação ou promover dados |
| UGR-05 | Conferir regressões afetadas, preservação e documentar a entrega real |
| UGR-06 | Consolidar índices, pendências e continuidade, sincronizar e registrar somente o recorte autorizado |

Checkpoint A após UGR-02; checkpoint B após UGR-04. Cada tarefa tem até cinco arquivos prováveis, dependências, critérios de aceite e comandos de verificação. A lista vincula os critérios UG-01–UG-15 a verificações de comportamento, inclusive recusas, concorrência no mesmo processo, falha sem publicação parcial e proteção do histórico.

## Autorizações e limites

Especificação e plano foram aprovados em interações distintas. Falta o aceite desta lista antes da Fase 4. Depois desse aceite, checkpoints são verificações técnicas do contrato, sem reabrir decisões já aprovadas; nova mudança de escopo continua exigindo revisão própria.

Não alterar `tasks/plan.md`/`tasks/todo.md` de `technical-catalog`. Não adicionar banco, API, dependência, interface gráfica, modelo físico ou enfrentamento de múltiplos grupos. Os arquivos de código e o verificador novo ainda não existem; nenhum comando futuro foi apresentado como teste já executado.

Nesta etapa, somente documentos foram alterados e seus links/diff foram conferidos. Os hashes dos planos antigos foram verificados para confirmar preservação. Não houve execução de testes de software por ausência de alteração de código.
