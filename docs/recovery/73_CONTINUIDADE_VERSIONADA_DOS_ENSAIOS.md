# 73 — Continuidade versionada dos ensaios sintéticos

## Contrato do incremento — 2026-11-09

Dar continuidade explícita ao ensaio de 72 após mudança de cenário ou atualização do algoritmo, preservando saldo e tempo e congelando a execução anterior. Somente instrutor atribuído, exercício aberto, sessão/origem/CSRF válidos. Continua restrito ao conjunto sintético e à mesma regra de consumo constante; não promove dados Command.

POST `/api/engine-runtime/continue`: `command_id` UUID, `previous_run_id` UUID, `expected_revision` inteiro e `reason` não vazia (até 1000 caracteres). O backend fixa a versão corrente do cenário e o algoritmo, cria snapshots de nova revisão para as mesmas unidades, conserva configurações e copia tempo/saldos/consumo acumulado. Revisão de comandos do novo ensaio começa em zero. Manifesto aponta para a execução e revisão anteriores e captura os saldos herdados. Não altera alocações. Repetição idêntica retorna a mesma nova execução; outra intenção baseada numa execução já sucedida retorna conflito.

GET `/api/engine-runtime/history` e GET `/api/engine-runtime?run_id=UUID`: consulta histórica exclusiva do instrutor atribuído ao exercício. Aluno continua consultando somente o estado corrente de unidades alocadas ao próprio partido. Avanço de execução histórica é recusado; comandos novos identificam a execução, além da revisão. Repetição de comando previamente aplicado retorna seu resultado original sem alteração.

Migração: remover apenas a unicidade de `engine_runs.exercise_id`, mantendo todas as linhas/IDs/FKs e a proteção do manifesto; adicionar relação imutável entre predecessora e sucessora. Backup consistente antes da entrega, comparação de registros e verificação de FKs. Falha na continuação deve reverter snapshots, execução, saldos, vínculo e evento juntos. Não remover ou reescrever snapshots antigos.

Critérios de aceite: herdar 540 kg e 30 min sem voltar a 600 kg; preservar resultados anteriores; recusar revisão, exercício, permissão ou comando incompatíveis; demonstrar rollback, repetição e duas continuações concorrentes; validar interface e conservação dos registros existentes. Não mudar o cenário real apenas para demonstrar a função.

## Implementação entregue

`engine_continuity.py` concentra migração e criação da sucessora. `engine_runtime.py` identifica a execução corrente e aceita consulta histórica sem permitir novos débitos nela. `app.py` mantém as mesmas proteções de autenticação/origem/CSRF; erros 400 para dados inválidos, 403 para acesso indevido, 409 para conflito e 503 para falha de persistência. Histórico continua legível com exercício encerrado; continuação e avanço exigem exercício aberto.

A relação `engine_run_continuations` armazena comando, predecessora única, sucessora única, conteúdo original, motivo, autor e horário. É protegida contra alteração/exclusão. `BEGIN IMMEDIATE` e revisão esperada serializam continuação e avanço; novas execuções formam uma sequência, sem ramificações alternativas concorrentes nesta versão.

`engine_runs` permite várias linhas por exercício; os IDs e conteúdos das linhas anteriores são preservados. A migração reconstrói somente essa tabela em transação independente, verifica FKs antes do commit e restaura a aplicação de FKs mesmo quando falha. Não altera valores técnicos. Inicializações seguintes detectam que a migração já foi aplicada e não a repetem. Depois de criada uma sucessora, comandos novos devem identificar `run_id`; clientes anteriores sem essa identificação são recusados para evitar aplicar uma intenção antiga à nova revisão zero.

Configuração, identidade da unidade, capacidade inicial, combustível inicial de referência e taxa continuam iguais. Os novos snapshots apontam para os anteriores e fixam a versão corrente do cenário. O manifesto registra revisão/execução predecessoras, tempo herdado e saldos/consumo por unidade. Inicial = saldo + consumido continua valendo para o acumulado completo. O ledger da sucessora registra apenas seus novos movimentos; o consumo herdado não é debitado novamente. A interface explicita essa distinção.

Chaves idênticas de continuação retornam o mesmo ID; conteúdo alterado gera conflito. Repetir um comando de avanço aplicado anteriormente continua sem novo débito, informando a execução original. Para comandos legados, acrescentar apenas seu `run_id` original permite localizar o resultado sem mudar os parâmetros da intenção. Cenário ou hash do algoritmo incompatível bloqueia avanço até continuação explícita; mudança da regra ou do contrato sintético é recusada, sem conversão automática.

O instrutor abre “Continuar em nova versão”, informa motivo e cria a continuação. As fichas de snapshots são atualizadas. “Consultar execuções preservadas” permite selecionar a atual ou uma histórica; histórico não apresenta botões de avanço/continuação. Nomes de ações e rótulos acessíveis seguem os controles nativos do protótipo.

## Verificação e entrega local — 2026-11-09

- Passaram 17 scripts Python. O novo `check_engine_continuity.py` cobre preservação de saldos/tempo/snapshots, recusa de comandos com revisão/execução desatualizada, consulta histórica sem alteração, repetição e chave incompatível, acesso do aluno somente ao próprio partido, proibição de histórico para aluno, leitura após encerramento e recusa de escrita nesse estado.
- Falha injetada na relação de continuidade reverte execução, estados e novos snapshots. Migração legada conserva todas as linhas e a proteção do manifesto. FK inválida injetada provoca rollback da reconstrução e restaura a aplicação de FKs.
- Duas conexões SQLite concorrentes: continuações distintas produzem uma sucessora e um conflito; chave idêntica produz uma sucessora e uma resposta de repetição. Continuação concorrente com avanço também produz um sucesso e um conflito, conservando a ordem dos eventos. Não é teste de carga com todos os alunos.
- Edge/Playwright, cópia isolada: edição do cenário e nova versão, snapshots atualizados, herança de 30 min/540 kg, avanço de 15 min até 45 min/510 kg, leitura da execução anterior inalterada e proibição de novo avanço nela. Bloqueios de papéis e CSRF, seleção de histórico e largura de 390 px conferidos; nenhuma exceção JavaScript. Diagnóstico de entrada e fichas técnicas completas também passaram.
- Na aplicação local, criou-se uma continuação por atualização do motor, com motivo registrado. O cenário v1 e as alocações não foram alterados. A execução anterior `f9cdeeef-1afb-4716-bc44-6fc703654d18` preserva 30 min/540 kg por unidade. Atual `aaee0406-52ed-403f-bda4-b17bdcd72684`: 45 min, revisão 1, 510 kg restantes e 90 kg de consumo acumulado por unidade. Houve somente um novo avanço de 15 min nesta entrega.
- Backup consistente: `prototype/data/siscan-before-engine-continuity-14.sqlite3`, antes da migração. Comparação EXCEPT das 22 tabelas anteriores, excluindo sessões transitórias: todas as linhas antigas preservadas. Inserções: uma execução, dois estados, dois snapshots, um comando de avanço, dois movimentos e dois eventos. A nova tabela contém uma relação de continuidade. Sem alteração de assets, configurações, cenário ou alocações.
- `integrity_check=ok`, zero violações FK. DB3K original, compilação 06 e recursos 09 mantêm os hashes documentados em 72. Nenhuma fonte Command, código ATLANTICADOR ou decisão APR foi alterada.
- Recibo local `prototype/data/engine-continuity-receipt-14.json`, SHA-256 `c5202d58ee4f9c05607d81a4de36da04e2769dc1590ee27857bc7b647dff0692`. Manifesto atual `0c25462d8077678cc1b06847a25d534ce5a1b7f18f74846ef9c879f7a709bcf9`. Bancos, backups e recibos permanecem fora do GitHub.

## Limites e próxima fatia

Continuidade é sequencial e conserva saldos; não oferece reset, reabastecimento, retorno da execução histórica à condição de atual, bifurcação alternativa ou transferência de meios. A repetição mantém o mesmo conjunto sintético; a autorização de continuação não aprova unidades físicas, taxas ou modelos Command. A política de recuperação operacional completa ainda exige testes de restauração/carga e seu procedimento próprio. O backup desta entrega é evidência de preservação, não homologação de recuperação em produção.

Permanecem curvas por regime/configuração e unidade/semântica aprovadas antes do uso de dados reais no motor, além de calibração física e decisões específicas de movimento/estoques. O próximo trabalho pode detalhar o contrato de perfil temporal e consumo por regime com dados controlados, preservando estes requisitos de rastreabilidade. Não calcular médias simples ou multiplicar taxas pelo número de motores sem comprovação.
