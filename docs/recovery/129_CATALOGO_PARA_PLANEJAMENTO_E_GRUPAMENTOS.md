# 129 — Catálogo para planejamento e grupamentos

**2026-11-24 · Incremento implementado e verificado**, autorizado por “concordo” à sequência catálogo utilizável → validação paralela → integração física gradual. Novas solicitações de aprovação de skills dispensadas anteriormente pelo responsável. Aplicadas Spec Driven Development, Ponytail, implementação incremental, TDD, UI, revisão, segurança e versionamento: contrato escrito antes do código, reaproveitando SPEC-unit-registry, SPEC-technical-catalog e o mapa existente. Computer Use verificou a interface; Chrome DevTools MCP não estava disponível nesta sessão.

## Contrato deste incremento

Instrutor atribuído ao exercício aberto seleciona uma plataforma do catálogo, partido AZUL/VERMELHO e quantidade de exemplares. O backend obtém identidade/nome/categoria da compilação confiável, cria identidades individuais SISCAN e disponibiliza ao partido em uma transação. Comando UUID repetido não duplica exemplares; conteúdo/contexto diferente com o mesmo comando é conflito. Sem promoção técnica, combustível presumido ou alteração do DB3K.

O operador do partido consulta e plota os meios adjudicados no mapa existente. Meios de superfície e aéreos podem compor os grupamentos dos respectivos domínios já suportados; demais categorias ficam disponíveis para planejamento/plotagem, sem inventar novos domínios de grupamento. Domínio vem da categoria de fonte, nunca do nome do meio. Snapshot de planejamento tem origem/versionamento e prontidão de cálculo falsa; não se disfarça de instância sintética. Confronto continua sujeito à conferência de entradas e decisão do instrutor.

## Critérios de aceite e sequência

1. Testar isolamento entre partidos, instrutor sem atribuição, exercício fechado, categoria/quantidade inválidas, origem inexistente, transação e reenvio idempotente.
2. Adicionar armazenamento de instâncias de planejamento separado do esquema sintético; conservar evidência literal e snapshot sem números físicos inventados.
3. Conectar à adjudicação/plotagem e visão de grupamentos existentes, preservando recusas de cálculo.
4. Expor ação na ficha do catálogo, protegida pela sessão/CSRF existentes, com status de planejamento e pendência de cálculo explícitos.
5. Verificar fluxo isolado, regressões e interface real; registrar limites, sincronizar e versionar. Não migrar/reiniciar o principal sem necessidade desta verificação.

Planos antigos de technical-catalog não são reescritos. O trabalho de validação física de 126–128 segue paralelo. Igualdade de 32 registros não se torna declaração de igualdade global dos bancos.

## Entrega e uso

Na ficha de qualquer plataforma do catálogo, o instrutor atribuído encontra **Planejamento do exercício → Partido → Exemplares (1–50) → Disponibilizar ao partido**. O nome/categoria e a referência por hash/tabela/ID vêm do backend. Exemplares diferentes têm identidades próprias, mesmo quando pertencem à mesma classe. O código PLAN identifica o exemplar; não substitui o ID DB3K da origem. Nenhum atributo físico vem do formulário.

Depois, abrir **Exercício e revisão → Mapa ATLANTICADOR → Meios**, selecionar os exemplares, escolher posição no mapa ou coordenadas e confirmar. Na aba **Grupos**, informar designação/domínio, selecionar integrantes e criar. O operador do partido também consegue consultar, plotar e compor com os meios adjudicados ao seu partido. A publicação de exemplares é restrita ao instrutor atribuído.

Categorias de planejamento: aeronaves, navios, submarinos, terrestres, instalações e satélites — as 14.968 plataformas da compilação estão pesquisáveis, sem aprovação física implícita. Grupos deste incremento continuam restritos aos domínios existentes `DataAircraft → aereo` e `DataShip → naval`; submarino não foi reclassificado silenciosamente como navio de superfície. Outras categorias podem ser adjudicadas/plotadas, mas seus domínios próprios de grupamento ainda não foram implementados. Seleção não confirma existência/disponibilidade no inventário real de uma força.

## Persistência, rastreabilidade e limites

- Tabelas aditivas `planning_units` e `planning_catalog_commands`, separadas das instâncias sintéticas. Snapshot imutável contém referência/versionamento da fonte e `official_calculation_ready=false`. Trata-se de referência de planejamento, não configuração/loadout operacional aprovado. Não fornece saldo, munição ou desempenho fictício.
- Adjudicação em `assets`/`party_allocations`, identidade, snapshot, recibo do comando e evento `catalog.planning_allocated` são gravados juntos. Falha reverte tudo. Reenvio do mesmo comando/contexto/conteúdo retorna os IDs anteriores; alteração com a mesma chave é conflito.
- Sessão/CSRF da API existente; exercício aberto e instrutor atribuído no backend. Partido do operador é conferido nas consultas; hashes e papel enviados por cliente não concedem autoridade.
- Instâncias e posições são persistidas. **Grupamentos continuam em memória**, conforme aviso existente: composição/histórico se perdem ao reiniciar o servidor. A persistência dos grupamentos é a próxima lacuna do fluxo, não foi apresentada como resolvida.
- Estado operativo, consumo, confronto físico automático e aprovação técnica não foram ampliados. O motor sintético continua separado. A relação catálogo → unidade de planejamento não remove a conferência de parâmetros exigida pelo CPC.

## Verificações efetivas

Sete testes novos passaram: seis de domínio e um de HTTP com várias asserções. Cobrem criação, IDs distintos, reenvio/conflito, isolamento de partido, autorização/CSRF, exercício fechado, categoria/tipo/quantidade inválidos, origem ausente, rollback após erro no meio da criação, grupos com snapshots de planejamento, persistência/reabertura, imutabilidade e exclusão do motor sintético.

Regressão final: **44 scripts Python passaram**, em 42,9 s; log `%TEMP%/siscan-planning-regression-20261124-v3.log`. Vinte testes JavaScript de grupos/prontidão passaram (`node --test check_map_groups.mjs check_cpc_readiness.mjs`); sintaxe de `static/source-catalog.js` conferida. Uma execução inicial encontrou interrupção Windows de conexão no teste preexistente de rejeição de pedido grande; a execução completa seguinte e a final passaram sem reduzir testes ou limites. A revisão também acrescentou recusa explícita de categoria JSON em formato de lista.

Percurso real isolado no navegador: instrutor 1 → ficha SH-60B/3 da compilação → dois exemplares AZUL → mapa existente → esquadrilha com os dois integrantes → plotagem dos dois → consulta da composição mostrando ambos plotados. Janela estreita de aproximadamente 445 px examinada; não se alega inspeção visual em todos os tamanhos. Nenhuma leitura de console foi realizada nesta verificação.

Prévia: **http://localhost:61275/**, instrutor **1**, senha exclusivamente sintética **somente-teste-local**. Banco do harness `%TEMP%/siscan-planning-20261124-v1/test.sqlite3`; principal 8787 não migrado/reiniciado. Atualizar arquivos sem iniciar processo novo não atualiza processos antigos. Para iniciar outra prévia com o código atual e pasta própria nova, dentro de `prototype`:

```powershell
python check_cpc_judgment_http.py --serve --data-dir "$env:TEMP/siscan-planejamento-NOVO" --port 61276
python -m unittest check_planning_catalog check_planning_catalog_http
```

Arquivos: `planning_catalog.py`, `check_planning_catalog.py`, `check_planning_catalog_http.py`, integração em `app.py`/`map_groups.py` e formulário em `static/source-catalog.js`. Evidência visual local em `prototype/data/planning-catalog-20261124-v1/flow.png`; não publicada no GitHub. Fontes DB3K/compilação preservadas; planos antigos intactos. Não se iniciou integração física automática de combustível/sensores/armamentos por causa da disponibilidade para planejamento.
