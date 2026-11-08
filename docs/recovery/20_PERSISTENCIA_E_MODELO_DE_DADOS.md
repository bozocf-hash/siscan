# 20 — Persistência e modelo de dados do ATLANTICADOR

## Escopo e distinções

Esta análise trata da persistência declarada no código do ZIP ATLANTICADOR 2.0.0. O arquivo operacional `data/` e seus bancos privados não estão no pacote nem foram consultados como ambiente de produção. Nenhuma instância SQLite foi aberta nesta missão; a estrutura abaixo foi identificada em DDL e funções do código. Não confundir:

1. `situation.sqlite3`: estado oficial do ATLANTICADOR.
2. `access.sqlite3` e `access-log.sqlite3`: bloqueios/ingressos e auditoria de acesso.
3. `DB3K_498.db3`: catálogo CMO externo em `Documents\siscan`, distinto dos bancos ATLANTICADOR; não foi localizada integração direta no código do ZIP.

## Localização e ciclo de vida

`serve.py::main` usa por padrão `ROOT/data` (substituível por `--data-dir`), chama `initialize_source_config`, instancia serviços e `Situation`. `Situation.__init__` define `situation.sqlite3`, ativa WAL e executa criação condicional de tabelas; `transaction` coordena conexões, `BEGIN IMMEDIATE` para escrita e `PRAGMA query_only=ON` para leitura declarada. `Auth` aponta para `access.sqlite3` e `access-log.sqlite3`; `profile_store` consulta contas no banco da situação, com fallback para `accounts.json` quando necessário. `SourceStore` mantém `sources.json`, `kmz-cache/` e `icon-cache/`.

Esses caminhos descrevem efeitos possíveis ao iniciar o serviço. O processo não foi iniciado; nenhuma configuração, pasta, banco ou cache foi criado/modificado nesta missão.

## Entidades SQLite identificadas no código

| Tabela/registro | Campos/chaves observáveis | Papel indicado pelo código |
|---|---|---|
| `meta` | `key` PK, `value` | Estado de fechamento/configuração |
| `roles` | `login` PK, `function`, `cell` | Funções/células associadas a contas |
| `elements` | `id` PK, `body` JSON | Elementos cartográficos/situação |
| `baselines` | `source` PK, `data` BLOB | Linha base/snapshot de cada fonte |
| `snapshots` | `version` PK, `source`, `data`, `created_at` | Versões imutáveis da fonte congelada |
| `current` | `source` PK, `version` | Ponteiro para versão atualmente utilizada |
| `events` | `id` PK, `body` JSON | Eventos/decisões publicados |
| `audit` | `seq` autoincrement, `event_id`, `body` JSON | Trilhas append-only; triggers impedem UPDATE/DELETE |
| `publications` | `id`, `version`, `created_at`, `status`, `details` | Acompanhamento de publicação |
| `triggers` | `id` PK, `name` | Categorias/acionadores de eventos |
| `effect_records` | `id` PK, `body` JSON | Efeitos e estados do workflow |
| `effect_editors` | `effect_id` PK, `login`, `token`, `name`, `expires` | Reserva temporária de edição |
| `confrontations` | `id` PK, `body` JSON | Registros de confronto |
| `user_accounts`/`profile_meta` | acessadas por `profile_store`, incluindo corpo JSON/assignments e marcador de migração | Diretório de contas migrado; estrutura gerida por scripts de perfil |

`access.sqlite3` contém, pelo menos, `account_blocks`, `block_history` e `entry_windows`; `access-log.sqlite3` contém `access_events` e índice temporal. DDL desses módulos está em `access_blocks.py` e `access_audit.py`. O inventário é das estruturas declaradas no código, não uma inspeção do banco de produção.

## Formato, relações e consistência

Há tabelas relacionais com chaves primárias, mas vários campos `body` guardam documentos JSON, e baselines/snapshots guardam BLOBs. Relações observáveis incluem `events`/`audit` por `event_id`, efeitos/confrontos por IDs em payload ou método e versões/sources através de `current`/`snapshots`; nem toda relação é FK declarada. `Situation.log` insere auditoria; chamadas de decisão atualizam transacionalmente situação/efeito conforme serviços. O código instala triggers de imutabilidade de `audit`.

É **INFERÊNCIA** chamar isso de modelo híbrido relacional/documental: a forma JSON é identificada, mas cardinalidades/semântica completa dependem de contratos e estado real. O documento não é ER formal e não substitui inspeção autorizada de uma instância operacional.

## DB3K do CMO

O DB3K está em arquivo separado e foi analisado em missões anteriores somente leitura: integridade estrutural `ok`, 167 tabelas, 75 vínculos FK e metadados. A inspeção estática não localizou conexão, caminho de arquivo ou uso funcional do `DB3K_498.db3`, `DB3K` ou `CWDB` nos componentes do aplicativo; busca literal pode coincidir incidentalmente com texto codificado. Não há evidência no ZIP de que o ATLANTICADOR use esse banco em runtime. Correspondência conceitual não significa acesso integrado; campos, unidades e domínios DB3K seguem pendentes.

## Pontos futuros para integração

**PENDENTE/PROPOSTO:** decidir se cadastro técnico SISCAN terá base própria, importação controlada ou outra fonte; definir chaves SISCAN, versionamento, proveniência/unidades, mapeamento de configuração/instância e autorização. Não copiar tabelas DB3K, nem acrescentar FK/colunas a estes bancos nesta missão.
