# 71 — Identidade, configuração e snapshot das unidades de teste

**Continuidade entregue:** [72](72_ESTADO_RELOGIO_E_CONSUMO_TRANSACIONAL.md) acrescenta estado mutável e consumo sintético sem reescrever os snapshots aqui descritos. As referências abaixo a ausência de consumo e ao próximo passo descrevem o estado da entrega 71.

## Escopo — 2026-11-09

Implementar o segundo passo da sequência 69/70: uma unidade sintética individual por partido, configuração versionada e snapshot técnico imutável. Preservar os oito meios demonstrativos e suas alocações; criar dois meios de teste identificados separadamente, sem alocação automática.

Critérios: IDs internos distintos por unidade, versão de configuração compartilhável sem compartilhar estoque, snapshot com exercício/partido/versão do cenário e manifesto do conjunto sintético; imutabilidade de versão e snapshot; criação idempotente e atômica; histórico de autoria. Mudança posterior no catálogo ou cenário não deve reescrever dados congelados.

Instrutor atribuído pode preparar/consultar; aluno atribuído consulta apenas unidades do próprio partido com alocação ativa. Dois alunos do mesmo partido recebem o mesmo ID/snapshot. Não aceitar IDs, atributos, partido ou aprovação enviados pelo cliente. Sem promoção Command, avanço de tempo, consumo ou transferência de titularidade nesta entrega.

## Entrega e esquema

Foram adicionadas três tabelas ao banco demonstrativo por criação aditiva/idempotente no schema do protótipo:

| Tabela | Responsabilidade |
|---|---|
| engine_configurations | Versão identificada de modelo/configuração sintéticos, JSON do conjunto de entrada, manifesto, hash e data; conteúdo imutável |
| engine_units | UUID da unidade individual, exercício, partido e vínculo ao meio alocável; unicidade por exercício/partido/finalidade |
| engine_unit_snapshots | UUID/revisão do snapshot, unidade, exercício/partido, versão do cenário/configuração, conteúdo/hash, autoria e data; conteúdo imutável |

Há FKs para meio, unidade, configuração, autor e versão de cenário. Um trigger exige que o meio esteja no mesmo exercício/partido da unidade. Triggers recusam atualização da identidade nesta versão e atualização/exclusão de configurações e snapshots. Alterações futuras precisam preservar identidade/histórico e acrescentar versões, não sobrescrever o passado. Não foi implementada transferência de partido ou um editor de configuração nesta entrega.

As duas unidades usam o mesmo modelo sintético `SYN-AIR-MODEL-001` e configuração `SYN-CONFIG-001`, com uma versão de configuração comum. Cada unidade tem UUID, meio alocável e snapshot distintos. O `entity_id` da fixture é identidade do template de teste, não a identidade individual das duas unidades. A igualdade dos dados de referência não constitui estoque compartilhado entre partidos.

O snapshot contém dados iniciais da fixture 70: capacidade 1000 kg, combustível inicial 600 kg, taxa de referência 2 kg/min e duração de referência 30 min, além do manifesto e contexto da unidade. São dados sintéticos arbitrados para testes, não parâmetros padrão de meios reais. `official_calculation_ready=false` continua preservado. Não há estado mutável de combustível, ledger ou execução de consumo nesta etapa.

Na leitura, o backend confere o hash e a correspondência do snapshot à unidade, partido, exercício e versão de configuração. Dados ausentes/adulterados provocam erro explícito. Não se relê a fixture/catálogo atual para reconstituir silenciosamente um snapshot. Atualizar a versão do cenário mantém o snapshot anterior e sua versão de origem; a interface informa a divergência em vez de rotulá-lo como novo.

## Criação, transação e acesso

`POST /api/engine-units/prepare` aceita somente objeto vazio, sessão válida, CSRF e instrutor atribuído ao exercício aberto. Usa `SAVEPOINT`, cria apenas os partidos ausentes e registra `engine.units_prepared` com autor/hash/IDs. Falha em qualquer unidade reverte configuração, meios, unidades, snapshots e evento dessa preparação, sem apagar dados anteriores. Repetição retorna created=0 e os mesmos IDs; não recria snapshot, não altera timestamp e não gera novo evento de criação.

`GET /api/engine-units` consulta o exercício atribuído, sem aceitar seleção de partido/IDs pelo cliente. Instrutor vê as duas unidades; aluno vê apenas as do próprio partido com `party_allocations.active=1`. Avaliador e instrutor não atribuído recebem 403; anônimo recebe 401. A preparação por aluno também é recusada. A associação de unidade a um partido é distinta de sua disponibilização para os alunos.

O painel **Unidades de teste do motor** fica no Catálogo técnico para o instrutor e na área do aluno, com leitura própria. Mostra código/UUID, partido, estado da disponibilização e atributos iniciais congelados. Os detalhes exibem modelo/configuração/revisão/cenário e hashes. O instrutor continua disponibilizando os meios em **Exercício e revisão → alocação por partido**; a preparação não altera alocações nem a composição/submissão do aluno.

## Resultado na aplicação em uso

| Resultado | Quantidade |
|---|---:|
| Meios demonstrativos anteriores preservados | 8 |
| Novos meios sintéticos A-ENG-001 e V-ENG-001 | 2 |
| Total de meios após a entrega | 10 |
| Unidades individuais novas | 2 |
| Versões de configuração | 1 |
| Snapshots iniciais | 2 |
| Novos eventos de preparação | 1 |
| Alterações nas alocações anteriores | 0 |

As unidades foram preparadas pelo endpoint autenticado do instrutor na aplicação em uso. Ambas permanecem **aguardando disponibilização**, sem alocação automática. Os dois registros anteriores de alocação por partido e os demais registros preexistentes foram preservados.

Antes da atualização foi criado backup consistente via SQLite `Connection.backup`: `prototype/data/siscan-before-engine-units-12.sqlite3`. O banco após a entrega apresentou integrity_check=ok e zero erros em foreign_key_check. Uma comparação EXCEPT entre backup e banco atual verificou que nenhuma linha anterior foi perdida/alterada, excluindo sessões de login dos testes; somente assets/events receberam as inserções previstas. Fonte DB3K, compilação 06, recursos 09 e suas referências/valores pendentes mantiveram os hashes/dados anteriores.

Recibo local: `prototype/data/engine-unit-snapshots-receipt-12.json`, SHA-256 `3823cb98c0fc298bacc824e5478a3c0f9ae9b5d3a407eacb8cf7ba984a7289d7`. Guarda IDs, snapshots, hashes e contagens antes/depois. Backup e recibo ficam fora do GitHub; código, testes e schema são versionados.

## Verificação e limites

Os 15 verificadores Python passaram. `check_engine_units.py` cobre unicidade e estabilidade da identidade, configuração compartilhada, snapshots distintos, imutabilidade, independência de mudanças do catálogo/cenário, criação idempotente, não duplicação de evento, acesso dependente de alocação, compartilhamento entre alunos, recusa de atributos enviados pelo cliente, autorização e snapshot adulterado. A injeção de falha na criação do snapshot vermelho confirmou reversão completa; fixture inválida e exercício encerrado não criaram unidades.

Edge isolado verificou preparação, repetição, CSRF, acesso de dois alunos azuis ao mesmo UUID/hash após alocação, isolamento do vermelho, bloqueio de avaliador/escrita de aluno e tela de 390 px. A alteração de alocação desse teste ocorreu apenas na cópia isolada e foi desfeita. Na aplicação em uso, verificou-se preparação idempotente, snapshots e interface, sem alterar alocações. Diagnóstico de entrada 70 e fichas completas anteriores continuaram passando.

Isso entrega a base de identidade/snapshot para o recorte sintético de ED-04, não todo o modelo de catálogo real. Não há promoção DB3K, decisão de carregamento, avanço do relógio, consumo, baixa de estoque, reabastecimento ou transferência de titularidade. A próxima entrega é estado mutável e tempo/eventos com contabilização transacional, preservando estes snapshots como referência inicial.
