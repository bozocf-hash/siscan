# Tarefas: operational-state — estado e adjudicação durável

**2026-11-17. Especificação aprovada por “siga”; plano aprovado por “aprovado”; Fase 3 aprovada por “aprovado”; Fase 4 em execução.** Referências: [especificação](../../SPEC-operational-state.md), [plano](plan.md), [111](../../docs/recovery/111_TAREFAS_ESTADO_E_ADJUDICACAO_DURAVEL.md). A aprovação do plano autoriza esta decomposição, sem iniciar código ou migração neste turno.

Depois de aprovada esta lista, executar sequencialmente com testes de comportamento antes da implementação correspondente e commits por incremento verificado. Checkpoints são verificações técnicas do contrato aprovado: comunicar e continuar sem novas confirmações rotineiras. Mudança material exige revisão do ponto afetado. Não alterar `tasks/plan.md`/`tasks/todo.md`, fontes originais, DB3K, banco principal ou processos em uso.

## Verificação prevista

Na pasta `prototype` de entrega (`siscan-prototype` no repositório):

```powershell
$pythonState = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonState check_operational_state.py
& $pythonState check_operational_state_storage.py
& $pythonState check_cpc_map.py
& $pythonState check_cpc_group_preparation.py
& $pythonState check_map_groups.py
& $pythonState check_map_groups_http.py
& $pythonState check_map_units.py
```

Na raiz: `git diff --check`. Os dois verificadores novos ainda não existem; nenhum teste executado nesta etapa documental. Executar comandos pertinentes a cada incremento e registrar contagens reais, sem somar novamente a mesma bateria. HTTP exige loopback autorizado e base/cookie/porta isolados. Não repetir testes por edição apenas documental nem declarar descoberta vazia como aprovação.

## OST-01 — Validar efeitos e compartilhar evidência de domínio

- [x] Validação/classificação e evidência pública implementadas; 4 testes novos, 6 de grupos e 14 de CPC passaram.
- **Aceite:** índice finito 0–100 ou ausência; booleanos/NaN/infinito/fora de domínio recusados. Superfície comprovada usa >60 combater, 40–60 navegar e <40 flutuar; não generalizar a outros domínios ou inferir perda. Evidência aérea sintética passa a função pública em `engine_units`, com a ponte de grupos delegando e sem ampliar elegibilidade.
- **Verificar:** teste de comportamento antes da mudança, cobrindo 0/40/60/80/100 e valores imediatamente acima/abaixo das fronteiras, ausência/índice `null`, omissão de alteração e perda independente. Fixture de domínio de superfície é explicitamente de teste, sem cadastrar navio real validado. Regressões `check_map_groups.py` e `check_cpc_map.py`. OS-01/02/09/10.
- **Dependência:** aprovação desta lista. Sem consulta fictícia a schema ainda inexistente; consulta não avaliada será ligada em OST-03.
- **Arquivos:** `siscan-prototype/engine_units.py`, `map_groups.py`, novo `operational_state.py`, novo `check_operational_state.py` e este checklist. Médio, até cinco arquivos.

## OST-02 — Migrar armazenamento em base isolada

- [ ] Implementar migração aditiva versionada, íntegra e reversível por rollback em caso de falha.
- **Aceite:** seis tabelas/relações/índices/triggers do plano, sem alterar tabelas anteriores; conexão independente, FK ativa, `BEGIN IMMEDIATE` e declarações completas por `execute`. Reexecução confere versão/schema sem escrita; schema parcial ou versão divergente/futura recusa sem completar silenciosamente.
- **Verificar:** `check_operational_state_storage.py` em SQLite temporário com dados anteriores. Provocar falha intermediária no DDL e comparar schema/dados/versão antes/depois; testar transação externa/FK desligada, constraints, imutabilidade, reexecução e divergência. Sem `executescript` no lote, sem `PRAGMA user_version` reaproveitado ou alteração de `app.initialize`. OS-08/10.
- **Dependência:** OST-01; pode exercitar somente armazenamento nesta fatia, sem comandos parciais publicados.
- **Arquivos:** novo `siscan-prototype/operational_state_storage.py`, novo `check_operational_state_storage.py`, este checklist. Pequeno, três arquivos.

### Checkpoint A — Migração isolada

- [ ] DDL/falha/reexecução/integridade verificados em base descartável; tabelas e dados anteriores preservados.
- [ ] Nenhuma migração automática, escrita no principal, alteração de originais ou ampliação de domínio.

## OST-03 — Consultar estado autorizado sem criar avaliação

- [ ] Implementar `consultar` e a projeção autorizada do histórico confirmado.
- **Aceite:** autorização precede leitura sensível; unidade deve pertencer ao exercício/partido permitido e ter identidade verificável. Sem efeito confirmado retorna revisão 0/estado não avaliado, sem INSERT. Com histórico, derivar estado da cadeia íntegra e não de recurso/snapshot; operador recebe somente estado/histórico oficial permitido, sem proposta privada ou adversário.
- **Verificar:** `check_operational_state.py` com instrutor, operador Azul/Vermelho, não participante, exercício distinto, identidade ausente/referências divergentes e revogação. Instrumentar acesso à fonte para comprovar fronteira; comparar SQL antes/depois das leituras. Schema não instalado deve ser erro explícito, não estado vazio válido. OS-01/03/09.
- **Dependências:** OST-01/02 e Checkpoint A.
- **Arquivos:** `siscan-prototype/operational_state.py`, `operational_state_storage.py` quando necessário, `check_operational_state.py`, este checklist. Médio, até quatro arquivos.

## OST-04 — Registrar proposta didática durável

- [ ] Implementar `registrar_proposta` com conteúdo congelado e recibo idempotente.
- **Aceite:** instrutor participante, exercício aberto, payload estrito e fonte didática; justificativa, cenário, referências reais/snapshots, revisão de estado esperada e efeitos sem unidades duplicadas. Gravar proposta/revisão/hash/recibo na mesma transação, sem efeito oficial. Origem congelada não depende de grupo em memória nem prova disponibilidade futura.
- **Verificar:** `check_operational_state.py`: proposta válida, referências inválidas, injeção de autor/papel/horário, esquema desconhecido, fonte automática, exercício fechado, comando repetido/divergente e falha de gravação. Conferir persistência da proposta em conexão nova e SQL das tabelas de meios/recursos/posições/relógio/snapshots inalterado. OS-03/04/06/07/09.
- **Dependência:** OST-03.
- **Arquivos:** `siscan-prototype/operational_state.py`, `check_operational_state.py`, este checklist. Pequeno, três arquivos.

## OST-05 — Revisar e rejeitar sem aplicar efeitos

- [ ] Implementar `revisar_proposta` e decisão de rejeição.
- **Aceite:** ajuste cria revisão imutável completa; revisão/hash esperados e autorização reconferidos. Rejeição é decisão terminal com motivo/recibo, sem efeitos; proposta decidida não pode ser revisada/reaberta. Versão antiga não pode ser confirmada depois do ajuste.
- **Verificar:** `check_operational_state.py` com encadeamento de revisões, payload inválido, revisão desatualizada, repetição/divergência de comando, rejeição repetida e tentativas após decisão/revogação. Comparar estado/recursos/mapa/snapshots antes/depois; falha de transação não deixa nova revisão/decisão/recibo parcial. OS-03/04/06/09.
- **Dependência:** OST-04.
- **Arquivos:** `siscan-prototype/operational_state.py`, `check_operational_state.py`, este checklist. Pequeno, três arquivos.

### Checkpoint B — Propostas sem efeitos

- [ ] Consulta, proposta, revisão e rejeição verificadas, com fronteira de autorização e conteúdo durável.
- [ ] Meios/recursos/relógio/posições/snapshots preservados; não apresentar proposta como resultado oficial.

## OST-06 — Confirmar lote oficial e corrigir por nova decisão

- [ ] Implementar confirmação transacional de todos os efeitos e sua consulta.
- **Aceite:** autorização/contexto/cenário, última revisão/hash da proposta, identidade/adjudicação/snapshots e revisão própria de cada unidade reconferidos dentro da transação. Decisão confirmada, efeitos antes/depois e recibo são publicados juntos, sem estado confirmado sem efeito correspondente ou aplicação parcial. Correção posterior cria nova proposta/decisão referenciada; recuperar perda exige referência explícita e não decorre de aumentar índice.
- **Verificar:** `check_operational_state.py` com lote válido, unidade/revisão incompatível, alteração de fonte, cenário/exercício fechado, revisão antiga, índice retirado, declaração explícita de perda e correção. Provocar falha entre integrantes e conferir rollback integral de estado/decisão/recibo. Operador nunca confirma. Nada altera recursos/mapa/tempo/configuração técnica. OS-02/03/04/05/09.
- **Dependências:** OST-05 e Checkpoint B.
- **Arquivos:** `siscan-prototype/operational_state.py`, `operational_state_storage.py` se necessário, `check_operational_state.py`, este checklist. Médio, até quatro arquivos.

## OST-07 — Comprovar aplicação única e disputas de revisão

- [ ] Verificar reenvio, concorrência e fronteira de commit do chamador.
- **Aceite:** replay autorizado idêntico retorna recibo sem exigir revisões pré-aplicação nem gerar novo efeito; outro conteúdo/autor/contexto/operação recusa. Uma decisão terminal por proposta e uma revisão nova por unidade/lote vencedor; lote perdedor não deixa registros parciais. Dentro de transação externa, durabilidade só após commit do chamador e rollback externo remove o lote inteiro.
- **Verificar:** `check_operational_state_storage.py` com conexões independentes e sincronização explícita, sem sleeps: duas confirmações da mesma proposta e duas propostas disputando a mesma unidade. Testar revogação antes do replay, mudança posterior de estado e comando já usado. Confirmar contagens/antes-depois de histórico e recibos, incluindo rollback externo. Corrigir apenas o código afetado e repetir testes pertinentes. OS-03/05/06/09.
- **Dependência:** OST-06.
- **Arquivos:** `siscan-prototype/check_operational_state_storage.py`, `operational_state.py` e/ou `operational_state_storage.py` se necessário, este checklist. Médio, até quatro arquivos.

### Checkpoint C — Publicação oficial integral

- [ ] Confirmação, correção, replay e concorrência demonstram publicação integral e única.
- [ ] Histórico anterior intacto; recursos/posição/tempo/configuração preservados; consulta distingue origem, perda e restrições não avaliadas.

## OST-08 — Recuperar, detectar corrupção e restaurar em cópia

- [ ] Verificar ciclo durável completo com processo novo e backup consistente.
- **Aceite:** proposta/revisões/decisão/efeitos/recibos e estado derivado sobrevivem ao reinício e à ausência do registro de grupos; inconsistência de schema/referências/hash/cadeia de efeitos recusa leitura, sem reset/default. Backup/restauração conservam relações/revisões/recibos e não sobrescrevem arquivo ativo.
- **Verificar:** `check_operational_state_storage.py` com processo Python independente aberto no arquivo temporário já commitado, sem herdar conexão/registro. Usar `Connection.backup`, restaurar em terceiro arquivo e conferir `integrity_check`/`foreign_key_check` e consultas autorizadas. Corromper somente cópias de teste, incluindo JSON/hash, elo antes/depois e versão de schema. Executar regressões previstas quando a extração/provedores afetarem consumidores. OS-07/08/10.
- **Dependências:** OST-07 e Checkpoint C.
- **Arquivos:** `siscan-prototype/check_operational_state_storage.py`, `operational_state_storage.py` e/ou `operational_state.py` se necessário, este checklist. Médio, até quatro arquivos.

### Checkpoint D — Durabilidade e recuperação

- [ ] OS-01–10 rastreados a testes reais; reinício não simulado apenas pela mesma conexão em memória.
- [ ] Migração, corrupção, restauração e regressões verificadas; contagens sem dupla soma e limitações reais documentadas.
- [ ] Nenhum processo/banco principal reiniciado ou migrado; não anunciar julgamento gráfico ou eficácia real de combate como entregue.

## OST-09 — Documentar e consolidar a entrega

- [ ] Revisar código/contratos e atualizar documentação em dois incrementos pequenos.
- **Aceite:** primeiro README, relatório numerado livre, especificação e este checklist refletem API/contratos/exemplos, resultados reais, fronteira de commit, migração somente isolada e ausência de integração gráfica. Depois índice/riscos/continuidade/mapa de capacidades e este checklist refletem entrega, sem declarar aplicação no principal ou reabrir gates anteriores.
- **Verificar:** diff/revisão do código, comandos pertinentes já executados, links locais e hashes dos planos antigos. Não repetir bateria por mudança apenas documental. Tratar números de testes e evidências conforme execução, sem antecipar sucesso.
- **Dependências:** OST-08 e Checkpoint D.
- **Arquivos:** subpasso A `siscan-prototype/README.md`, relatório em `docs/recovery/`, `SPEC-operational-state.md`, este checklist e `plan.md` se necessário; subpasso B controles `00`/`09`/`10`, `CAPABILITY_MAP.md` e este checklist. Até cinco arquivos por incremento.

## OST-10 — Sincronizar arquivos e versionar

- [ ] Entregar somente código/documentação autorizados na pasta SISCAN e GitHub.
- **Aceite:** comparar origem/destino e SHA-256, preservar alterações externas e não incluir bancos, backups, credenciais ou originais. Commits por incremento na branch existente, push e situação final verificados. Nenhuma migração automática do principal ou reinício que apague grupos em memória.
- **Verificar:** diff/hashes/commits e confirmação do envio. Provedor interno disponível no código/testes não significa botão no processo ativo. Reportar migração do principal e ligação ao mapa como etapas futuras explícitas.
- **Dependência:** OST-09.
- **Arquivos:** este checklist e relatório de entrega, cópias dos arquivos produzidos; sem nova mudança funcional.

## Gate

Especificação, plano e lista aprovados; executar OST-01–10 com checkpoints técnicos A–D, sem novas confirmações rotineiras. Este aceite não se estende a DDL no banco principal, APIs/UI de julgamento ou produtor automático. As restrições são as mesmas da especificação/plano aprovados.
