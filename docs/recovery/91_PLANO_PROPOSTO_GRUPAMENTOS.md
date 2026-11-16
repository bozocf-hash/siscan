# 91 — Plano técnico aprovado para grupamentos

**Data: 2026-11-16. Estado: Fase 2 aprovada por “aprovado”.** O responsável aprovou `SPEC-unit-registry.md` por “sim” em interação anterior e escolheu a opção 1 para salvar o plano em `tasks/unit-registry/plan.md`, preservando `tasks/plan.md` e `tasks/todo.md`, que contêm trabalho aberto de `technical-catalog`. Lista de Fase 3 posteriormente proposta conforme [92](92_TAREFAS_PROPOSTAS_GRUPAMENTOS.md).

## Entregas e verificações propostas

1. Criação/consulta de grupos com dados do provedor conferidos, hash, contexto, reenvio e exclusividade.
2. Revisão versionada, histórico preservado e troca indivisível de vínculos.
3. Arquivamento com versão inativa, liberação dos vínculos atuais e preservação dos anteriores.
4. Preparação de composição com revisão e inventário atual, sem iniciar simulação ou consumir recurso.
5. Revisão final, regressões afetadas e documentação do recorte.

Checkpoint A após criação/revisão; checkpoint B após arquivamento/preparação. O plano relaciona essas etapas aos 15 critérios UG e inclui comandos concretos de verificação, riscos e critérios de preservação.

## Decisões técnicas aprovadas

Uma instância de registro mantém estado privado em memória. Conteúdo canônico e cópias de saída preservam versões. Um lock por registro protege a conferência/publicação no mesmo processo; não há promessa de persistência ou coordenação distribuída. Versão, recibo e vínculo são construídos juntos antes da publicação. Reenvio idêntico retorna o resultado histórico; preparação revalida disponibilidade atual separadamente.

Não serão importados módulos SQLite/execução para criar dependência circular na identidade. O contexto/normalização vem de um provedor interno confiável e fixtures controladas; não se trata de autenticação implementada nesse domínio.

## Próximo gate

A lista de Fase 3 foi proposta em `tasks/unit-registry/todo.md` e aguarda aprovação antes do código. Não alterar as tarefas abertas do catálogo. Nenhum código, banco, dependência, rota ou plano antigo foi modificado nesta etapa; foram conferidos documentação, links e preservação dos arquivos existentes.
