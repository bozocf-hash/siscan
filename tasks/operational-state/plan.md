# Plano técnico: operational-state — estado e adjudicação durável

**2026-11-17. Especificação de Fase 1 aprovada por “siga”; Fase 2 proposta para revisão.** Contrato: [SPEC-operational-state.md](../../SPEC-operational-state.md). Escopo/ordem de [104](../../docs/recovery/104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md) e entrega 108 preservados. Plano novo na localização já indicada pela especificação; não sobrescrever `tasks/plan.md`, `tasks/todo.md` ou os planos anteriores de confronto. Sem código, DDL ou testes executados nesta fase.

## Resultado e dependências

Provedor Python interno que recebe contexto autenticado e registra propostas didáticas, revisões, decisões, efeitos oficiais e recibos no SQLite SISCAN. O índice oficial só muda numa confirmação autorizada e transacional. Persistência não depende do registro em memória de grupamentos. Novas rotas, botões e ligação ao mapa ficam para a etapa 3 de 104.

```text
Contexto/sessão + identidades/snapshots + adjudicação existentes
                  ↓
Validação contextual e evidência de domínio
                  ↓
Migração aditiva e armazenamento durável
                  ↓
Proposta imutável → nova revisão / rejeição / confirmação
                                              ↓
                          lote de efeitos + decisão + recibo
                                              ↓
                          consulta autorizada e recuperação
```

Executar sequencialmente: migração e comandos compartilham schema/estado. Não há necessidade de subagentes ou trabalho concorrente de implementação. Testes de concorrência são parte da verificação do serviço, não execução paralela da entrega.

## Evidência técnica e reaproveitamento

- `engine_units.context`, `list_units` e `encoded`: contexto/participação, referências e JSON canônico. `context` usa o primeiro exercício do protótipo; esta fatia não introduz seleção multi-exercício. Confrontar toda identidade recebida com o exercício efetivamente autorizado.
- `map_groups._controlled_domain`: prova somente a configuração aérea sintética. Extrair essa validação para pequena função pública de `engine_units`, mantendo a ponte de grupos como delegadora e preservando seu comportamento. Estado não dependerá de mapa nem de função privada. Nenhum novo domínio real será autorizado pela extração.
- `engine_runtime.atomic`: padrão de transação `BEGIN IMMEDIATE`/savepoint e rollback. Reaproveitar nos comandos; recibo só é durável depois do commit do chamador. API documentará essa fronteira quando chamada dentro de transação externa.
- `app.connect`: FK habilitada, `sqlite3.Row` e timeout. `app.initialize` usa `executescript` para schemas existentes. Não acoplar a nova migração a essa chamada nem presumir que `executescript` preserva a transação externa.
- `engine_resource_states` é saldo de ensaio; `map_unit_positions` é planejamento. Consultar identidade não autoriza reescrever essas tabelas.

## Contratos internos propostos

| Operação | Entrada essencial | Resultado |
|---|---|---|
| `consultar(db, user, unit_id)` | Sessão confiável e identidade | Estado confirmado ou ausência explícita, revisão própria e origem permitida ao perfil |
| `registrar_proposta(db, user, payload)` | Comando UUID, fonte didática, justificativa, referências congeladas e efeitos explícitos | Proposta/revisão/hash e recibo; sem mudar estado |
| `revisar_proposta(db, user, payload)` | Comando, ID/revisão/hash esperados e novo conteúdo completo | Nova revisão imutável; anterior preservada |
| `decidir_proposta(db, user, payload)` | Comando, revisão/hash esperados, confirmar/rejeitar e justificativa | Decisão, aplicação integral quando confirmada e recibo |
| `historico(db, user, unit_id)` | Identidade autorizada | Trilha oficial do meio; detalhes privados de proposta só para instrutor |

Payloads estritos, sem campos arbitrários de autor/papel/horário. Efeitos identificam unidade, revisão de estado esperada, snapshot/hash/configuração esperados, alteração explícita de índice e/ou perda. Indicar ausência com revisão 0 na pré-condição, sem gravar estado fictício. Índice aceita número finito 0–100 sem arredondamento oculto; rejeitar booleanos. Serializar canonicamente e conservar valor recebido normalizado para comparação, sem inventar precisão adicional ou converter percentual em pontos de vida.

Perda tem três situações de conhecimento: não avaliada, explicitamente não perdida e perdida; omitir campo preserva, índice `null` retira avaliação conforme especificação. Recuperação de perda já confirmada exige referência explícita à decisão corrigida. A leitura apresenta índice de origem separado da declaração de perda e não exibe “combater” como condição efetiva de um meio declarado perdido. Não criar nova faixa percentual ou regra de recuperação automática.

O usuário e contexto são fornecidos por chamador confiável, não pelo payload. Validar participação/perfil antes de qualquer fonte sensível; reconferir autorização em cada comando e antes de reenvio. Ler as unidades do próprio partido no caminho de operador, sem consultar/devolver inventário adversário completo. Exercício fechado permite leitura, não comando novo.

## Modelo de armazenamento proposto

Seis tabelas novas, nomes físicos sujeitos ao detalhamento das tarefas sem mudar o contrato:

| Tabela | Conteúdo e restrições essenciais |
|---|---|
| `operational_schema_migrations` | Versão aplicada e hash do contrato DDL; versão desconhecida/divergência recusa inicialização |
| `operational_proposals` | ID durável, exercício, fonte didática, autor/instante; referência opcional a proposta/decisão corrigida |
| `operational_proposal_revisions` | Chave proposta/revisão, cenário, conteúdo canônico/hash, justificativa, referências e efeitos solicitados congelados; append-only |
| `operational_decisions` | Uma decisão terminal por proposta, revisão/hash decidido, confirmar/rejeitar, autor/momento/motivo e comando; append-only |
| `operational_effects` | Decisão, unidade/exercício/partido, revisão anterior/nova, snapshot/hash/configuração, antes/depois e proveniência; único por decisão/unidade e unidade/revisão |
| `operational_commands` | Comando único, exercício/autor/operação, payload canônico/hash, recibo e instante; append-only |

Estado corrente é o último efeito confirmado por unidade, com índice de consulta apropriado, sem segunda tabela mutável de estado. Antes/depois completos permitem verificar a cadeia desde a ausência inicial. Sem efeitos, consulta retorna revisão 0/estado não avaliado sem INSERT. Não afirmar que um hash protege contra um administrador que reescreva todo o banco; validações detectam inconsistências dentro do modelo de confiança local.

FKs para exercício, usuário e identidade comprovada; conferir coerência conjunta de unidade/exercício/partido e snapshot/configuração por constraints e validação transacional. JSON não substitui validação semântica. Triggers recusam UPDATE/DELETE dos registros históricos; constraints e transação evitam decisões/efeitos duplicados. Domínio e evidência de origem são congelados; só prova validada permite classificar superfície. A fixture pode testar domínio de superfície por seam controlado de provedor, sem cadastrar falsamente um navio real como validado.

Não usar FK para grupos temporários. Referência de origem guarda conteúdo congelado necessário à interpretação: identidade/revisão/hash de composição quando fornecida, integrantes e snapshots/referências. O provedor confere integridade/formato e referências reais das unidades; essa cópia não prova que um grupo continua disponível. O futuro adaptador CPC reconferirá composições/posições antes da confirmação; nenhum botão atual será conectado neste plano.

## Migração e recuperação

Implementação prevista em `siscan-prototype/operational_state_storage.py`, com versão única inicial e função explícita `migrate(db)`. Exigir conexão independente sem transação aberta e FKs habilitadas. Validar pré-requisitos do SISCAN e ausência/compatibilidade da versão. Em `BEGIN IMMEDIATE`, executar cada declaração completa individualmente por `execute` (incluindo triggers completos), validar schema/FKs e registrar versão antes de commit. Não dividir SQL ingenuamente por ponto e vírgula; não usar `executescript` dentro da transação.

Reexecução da mesma versão confere estrutura esperada e retorna sem alteração. Schema parcial sem marcador, marcador divergente ou versão futura desconhecida deve falhar, sem tentar completar/normalizar silenciosamente. Falha durante DDL reverte todas as tabelas/triggers/versão deste lote. Não desligar FKs, reconstruir tabelas anteriores, criar estado de prontidão ou reaproveitar `PRAGMA user_version` sem investigar sua titularidade.

Primeiro verificar em banco descartável com schema/dados do harness existente e, na etapa de entrega autorizada, em cópia produzida pela API `sqlite3.Connection.backup`, evitando cópia crua de arquivo em uso. Verificar backup, `integrity_check`/`foreign_key_check`, inventário e dados preservados antes/depois. Testar restauração em outro arquivo e conexão/processo novos, sem sobrescrever base ativa. Validar histórico/revisões/hash/recibos e estado reconstruído; corrupção recusa consulta sensível, não reseta o exercício.

Este recorte não modifica `app.initialize` nem migra automaticamente o banco principal. A entrega do provedor pode ser verificada e sincronizada sem DDL no banco em uso. Aplicação na base principal exigirá procedimento de entrega explícito: backup verificado, janela sem escritores, migração, verificação e política de restauração; não restaurar automaticamente um backup que descarte escritas posteriores. A integração gráfica futura decidirá quando habilitar o provedor já migrado.

## Transação de confirmação

1. Autorizar contexto atual antes da consulta sensível e entrar em transação de escrita; repetir checagens relevantes dentro dela.
2. Conferir recibo pelo comando e comparar exercício/autor/operação/conteúdo. Replay idêntico, ainda autorizado, retorna recibo; não reaplica nem exige que o estado já aplicado continue na revisão antiga. Comando divergente recusa.
3. Verificar proposta ainda não decidida e revisão/hash atuais; exercício/cenário, snapshots, adjudicação, unidades sem duplicação e revisões de estado de todos os integrantes.
4. Preparar antes/depois de todos os efeitos, validar correções explícitas e limites. Gravar decisão, efeitos, revisão e recibo no mesmo lote; rejeição grava somente decisão/recibo.
5. Verificar integridade e concluir a transação. Exceção/constraint/concorrência implica rollback integral. Nada altera combustível, munição, tempo, mapa ou snapshot técnico.

Revisão de proposta e rejeição também usam transação, pré-condições e comando idempotente. Decisão terminal não permite nova revisão. Corrigir depois cria nova proposta referenciada, preservando registros anteriores. Dois comandos diferentes para a mesma proposta só permitem uma decisão terminal; dois lotes para a mesma unidade devem conferir a revisão própria, mesmo em propostas distintas.

## Sequência de implementação a detalhar na Fase 3

1. Validação/classificação e consulta não avaliada autorizada, com extração mínima de evidência de domínio e regressão da ponte existente.
2. Migração aditiva e consulta durável verificada em base isolada. **Checkpoint A:** rollback DDL, reexecução e dados anteriores preservados.
3. Registrar proposta com referências congeladas e recibo, sem alterar estado; em seguida revisar/rejeitar sem efeitos. **Checkpoint B:** versões imutáveis e autorização/recibos corretos.
4. Confirmar lote e consultar estado oficial, incluindo correção de perda. Depois testar disputas/reenvios e falhas entre integrantes. **Checkpoint C:** aplicação integral e única, estados/recursos não relacionados preservados.
5. Recuperação em processo novo, corrupção e restauração; regressões dos provedores. **Checkpoint D:** durabilidade e rastreabilidade OS-01–10 demonstradas.
6. Documentar contratos/limites, sincronizar apenas código/docs autorizados e versionar; manter processo/banco principal intactos e relatar separadamente sua indisponibilidade nesta fase interna.

Fatiar cada item em tarefas de até cerca de cinco arquivos, com testes de comportamento antes da implementação correspondente. Os checkpoints verificam o contrato aprovado; comunicar resultados e continuar sem novas confirmações rotineiras durante a execução aprovada. Mudança material de contrato requer revisão do ponto afetado. Não escrever a lista de Fase 3 nem implementar antes de aprovação deste plano.

## Verificadores previstos

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

Na raiz: `git diff --check`. Os verificadores novos não existem e nenhum teste foi executado nesta fase. A futura bateria HTTP usa base/cookie/porta isolados e permissão de loopback quando necessária; não usa o processo principal. Não repetir verificadores por edição apenas documental.

Cobertura planejada: OS-01/02/09 por validação/classificação e estado ausente; OS-03 por papel, exercício e revogação; OS-04 por SQL antes/depois de proposta/revisão/rejeição; OS-05/06 por falhas provocadas, disputa com conexões independentes sem sleeps e recibos; OS-07/08 por processo novo, migração/backup/restauração/corrupção; OS-10 por regressões e hashes dos arquivos preservados. Sem ensaio de combate ou auditoria de parâmetros reais nesta bateria.

## Riscos e tratamento

| Risco | Tratamento |
|---|---|
| Estado inicial tratado como pronto ou destruído | Ausência explícita, revisão 0 sem INSERT e perda independente do índice |
| Dependência de domínio privado/cartográfico | Extrair validação existente para identidade; manter evidência sintética e testes de regressão |
| Migração parecer atômica apesar de commit implícito | Declarações completas por `execute`, conexão própria, falha DDL provocada e comparação de schema/dados |
| Grupos temporários desaparecerem após reinício | Origem congelada durável; consulta de resultado independente do registro em memória |
| Reenvio ou disputa duplicar efeito | Comando/decisão únicos, revisão por unidade e transação com testes de conexões independentes |
| Histórico expor o adversário ao operador | DTO de leitura limitado ao partido e estado confirmado; proposta/recibo privado restritos ao instrutor |
| Recuperação apagar escritas novas | Restaurar apenas em cópia no teste; procedimento principal exige janela e verificação explícitas |

## Gate da Fase 2

Fase 1 aprovada por “siga”. Submeter este plano concreto à revisão antes de detalhar tarefas de Fase 3. Não restam perguntas de localização: `tasks/operational-state/` já consta da especificação aprovada. Nenhum schema/código/banco/processo foi alterado; a migração descrita não foi executada ou testada ainda.
