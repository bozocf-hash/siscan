# 72 — Estado, relógio e consumo transacional sintéticos

## Escopo — 2026-11-09

Implementar um ensaio manual de consumo constante nas duas unidades sintéticas de 71. Separar snapshot inicial imutável, estado atual e movimentos de combustível. O relógio é de teste, por exercício; não implementa marchas automáticas, movimento, combate ou modelos Command.

Critérios: inicialização idempotente sem reset; quantidades persistidas em gramas inteiras; avanço inteiro de 1 a 1440 minutos; taxa e unidades somente do conjunto sintético validado. Avançar todas as unidades capturadas no ensaio na mesma transação. Se faltar combustível em qualquer uma, recusar todo o intervalo sem avançar o relógio ou criar débito parcial.

Usar chave de comando vinculada ao conteúdo e revisão esperada; repetir o mesmo comando deve retornar seu resultado anterior sem novo débito. Chave reutilizada para outro conteúdo e revisão desatualizada devem gerar conflito. Registrar antes/depois, autor, versão/regra e snapshot. Preservar alocações e impedir leitura de dados do adversário pelo aluno.

Nenhum dado Command é promovido. Uma mudança de versão do cenário ou do algoritmo impede novo avanço deste ensaio até tratamento explícito, sem impedir a edição do cenário nem apagar o histórico. Os limites numéricos e a taxa constante são do teste, não novas regras operacionais do projeto.

## Entrega e contrato

Entregue em `siscan-prototype/engine_runtime.py`, integrado a `app.py` e ao painel “Execução sintética” dentro de “Unidades sintéticas”. Backend autoritativo; nenhuma atualização automática pelo navegador.

| Interface | Comportamento |
|---|---|
| GET `/api/engine-runtime` | Estado atual e até 40 movimentos recentes; rejeita parâmetros de consulta. Histórico completo permanece no banco. |
| POST `/api/engine-runtime/start`, `{}` | Instrutor atribuído, exercício aberto; captura os dois snapshots existentes e inicia uma única execução. Repetir não reinicia saldos. |
| POST `/api/engine-runtime/advance` | Exige `command_id` UUID, `minutes` inteiro de 1 a 1440 e `expected_revision` inteiro. Sem campos adicionais. |

POST exige sessão, origem válida e CSRF. Escrita exclusiva do instrutor atribuído. Alunos acessam somente unidades com alocação ativa ao próprio partido; colegas compartilham o mesmo saldo. Avaliador não recebe acesso a este ensaio. O manifesto completo é restrito ao instrutor. Sem unidade visível, a consulta não expõe execução adversária.

As duas unidades capturadas consomem no ensaio, inclusive enquanto não alocadas. A alocação controla visibilidade neste teste, não atividade tática. Nenhuma alocação foi criada ou alterada pela entrega.

## Persistência, consistência e rastreabilidade

| Tabela | Responsabilidade |
|---|---|
| `engine_runs` | Identidade da execução, cenário, manifesto imutável, relógio e revisão. Uma execução por exercício. |
| `engine_resource_states` | Referências iniciais imutáveis e saldos mutáveis em gramas inteiras. Conservação: inicial = saldo + consumido. |
| `engine_runtime_steps` | Comando, conteúdo, revisão, autor, horário e resultado original. Histórico protegido contra atualização/exclusão. |
| `engine_fuel_ledger` | Antes, débito, depois e hash do snapshot por unidade/comando. Histórico protegido contra atualização/exclusão. |

Manifesto fixa contrato de entrada, hash do algoritmo, regra `constant-rate-synthetic-01`, cenário e snapshots/valores iniciais. `BEGIN IMMEDIATE` serializa escritores independentes; revisão esperada também é conferida na atualização. Dentro de transação já aberta, usa savepoint. Saldo, relógio, histórico e evento de auditoria são gravados juntos. Falta de combustível em qualquer unidade recusa o intervalo inteiro; não há débito parcial ou ajuste automático para zero.

A repetição de chave e conteúdo retorna o resultado original com `replayed=true`, mesmo após revisões posteriores, sem novo débito. Reutilização da chave para outro conteúdo e nova chave com revisão antiga retornam 409. A interface consulta novamente o estado atual após o sucesso. Em falha, conserva o comando pendente para repetição; “Atualizar estado” permite consultar antes de emitir outra intenção.

## Verificação e evidências — 2026-11-09

- Passaram os 16 scripts `check_*.py`, incluindo `check_engine_runtime.py`: consumo, esgotamento exato, insuficiência, revisão antiga, repetição, permissões, isolamento de partidos e rollback com falha injetada na escrita do ledger.
- Concorrência real com duas conexões SQLite: chaves diferentes na mesma revisão resultam em um avanço e um conflito; mesma chave resulta em um avanço e uma repetição. Isso não constitui teste de carga com 16 usuários.
- Edge/Playwright: inicialização e avanço pelos botões, resultados persistidos, comandos repetidos, erros 400/403/409, snapshots e alocações preservados, ausência de erro JavaScript e largura móvel de 390 px sem transbordamento da página. Também passaram as verificações de diagnóstico de entrada, fichas técnicas completas e massa/payload.
- Entrega local em `C:\Users\bozoc\Documents\siscan\prototype`: execução `f9cdeeef-1afb-4716-bc44-6fc703654d18`, revisão 1, tempo 30 min. Cada unidade: inicial 600 kg, débito 60 kg e saldo 540 kg. Snapshots permanecem com os 600 kg iniciais. Um comando e dois movimentos de combustível.
- Backup consistente anterior: `data/siscan-before-engine-runtime-13.sqlite3`. Comparação por diferença de linhas: todos os registros das 18 tabelas anteriores conferidas foram preservados; somente `events` recebeu duas linhas adicionais. Sessões foram excluídas da comparação por serem transitórias. Assets, alocações, unidades, configurações e snapshots anteriores não mudaram.
- `integrity_check=ok`; nenhuma violação de FK. SHA-256 das fontes DB3K original, compilada 06 e recursos 09 permanece igual ao registrado nas entregas anteriores.
- Recibo local `data/engine-runtime-receipt-13.json`, SHA-256 `60f785757a5b4c7e9f0799524777a1c7cca9344ebc5502d79eb122dfd7728c47`. Manifesto da execução: `1cbb41e22d88deac441b5a4e7a6b647cd1aa32409b85ba29b604307e1fc24de5`. Recibo e bancos não são publicados no GitHub.

## Limites e continuidade

Avançam ED-04/ED-07/ED-09/ED-12 no recorte sintético de 69; não significam encerramento desses requisitos para dados reais. Permanecem: taxas/unidades físicas Command validadas e aprovadas, curvas por regime/configuração, múltiplos perfis, reabastecimento, outros estoques, localização/movimento, recuperação operacional e carga multiusuário. A constante 2 kg/min não é média extraída do DB3K.

Não há reset, transferência ou nova ramificação da execução nesta versão. Mudança do cenário/algoritmo bloqueia novos avanços; a leitura histórica continua disponível. A edição do cenário permanece autorizada conforme APR-11. O próximo incremento deverá tratar explicitamente continuidade/versionamento das execuções antes de combinar este ensaio com modelos operacionais. Preservadas arbitragem humana e separação entre necessidade logística e valor de combate.
