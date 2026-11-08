# 18 — Backend do ATLANTICADOR

## Fonte e método

Leitura estática do ZIP `C:\Users\bozoc\Documents\siscan\atlanticador-main (1).zip`, versão declarada 2.0.0. Arquivos não extraídos/alterados; nenhum código foi executado. Funções citadas são identificadas no texto das fontes, sem validar comportamento em runtime.

## Entrada e montagem

`start-atlanticador.cmd` chama `py -3.12 serve.py`. `serve.py::main` define defaults de host loopback `127.0.0.1`, porta 8787, `ROOT/data` e intervalo de fontes de 60 s; inicializa configuração de fonte, `Auth`, `SourceStore` e `Situation`, associa o store à situação e constrói `ThreadingHTTPServer`. Flags observadas: `--secure-cookie`, `--no-sync`, `--allow-party-preview`, `--structured-map`. As duas últimas têm guardas declaradas para loopback. Este fluxo é descrição estática, não foi executado.

## Mapa do backend

| Arquivo | Responsabilidade identificada | Funções/classes indicativas |
|---|---|---|
| `serve.py` | HTTP estático + JSON API, roteamento, gates e composição | `Handler.do_GET`, `do_POST`, `reply`, `record_page`, `main` |
| `situation.py` | Estado oficial, papéis, eventos, snapshots, auditoria e transações | `Situation`, `transaction`, `actor`, `status`, `freeze`, `snapshot`, `propose`, `decision` |
| `auth.py` | Autenticação, hash de senha, sessões, ingresso e bloqueio de tentativa | `Auth`, `password_hash`, `verify_password`, `login`, `session`, `logout` |
| `profiles.py`, `function_roles.py`, `profile_store.py` | Funções/papéis, partido, fontes visíveis e diretório de contas | `party_of`, `allowed_sources`, `initial_assignment`, `stored_accounts` |
| `access_blocks.py`, `access_audit.py` | Bloqueio/ingresso de contas e log de acessos | `AccessBlocks`, `AccessAudit` |
| `sources.py` | KMZ externo: configuração, busca, validação, cache, snapshots e ícones | `SourceStore`, `validate_kmz`, `initialize_source_config` |
| `official_kmz.py` | Parse/transformação/montagem de dados KML/KMZ oficiais | `read_data`, `unpack`, `apply_states`, `build_snapshots` |
| `structured_map.py` | Índice, estado e exportação cartográfica estruturada | `StructuredMap`, `map_state`, `baseline_index`, `materialize_exports` |
| `effect_workflow.py`, `effect_kmz.py`, `effect_annul.py` | Efeitos: edição, validação, decisão, aplicação, prazo e exportação cartográfica | `EffectWorkflow`, `effect_validate`, `effect_decide`, `effect_apply`, `effects_due` |
| `confrontations.py` | Registro, revisão, respostas, decisão e associação de confrontos/efeitos | `Confrontations`, `confrontation_update`, `confrontation_decide` |
| `party_proposals.py` | Propostas de partidos, visibilidade, intake e adjudicação/aplicação | `PartyProposals` |
| `unit_conditions.py`, `record_queries.py` | Estado/condições e consultas/paginação de registros | `conditions_of`, `init_record_indexes`, `list_records` |
| `calunga.py` | Catálogo e normalização de simbologia | `catalog`, `identify`, `normalize_calunga` |
| `map_templates.py`, `export_deltas.py` | Templates e captura/restauração de deltas de mapa | `templates`, `capture`, `restore` |
| `manage.py` | CLI administrativa e operação de base; algumas rotinas têm caminho explícito de escrita | `main`; não executado |

Os componentes são módulos Python planos no diretório raiz do pacote. `Situation` agrega `Confrontations`, `EffectWorkflow` e `StructuredMap` por herança; os serviços compartilham transações/estado SQLite mediante composição e chamadas de método. Essa integração interna não constitui API pública para SISCAN.

## Rotas e interface

`serve.Handler` implementa GET/HEAD/POST. A camada de serviço inclui sessão/login/alteração de senha; fontes e KMZ; estado/mapa; perfis/roles; eventos; elementos; efeitos; confrontos; triggers; publicação; exportação e congelamento de snapshots. POST de controle inclui, entre outros, criar/revisar/decidir efeitos e confrontos, editar, clonar/atualizar, gerir roles e finalizar estado. Handler traduz `SituationError` para status HTTP e respostas JSON; evento legado retorna 410. O catálogo resumido de rotas consta em 17.

Frontend e backend comunicam-se por `fetch('/api/...')` na mesma origem; requests mutáveis carregam JSON e token CSRF. Não foi localizado esquema OpenAPI, SDK ou endpoint versionado destinado a integração externa SISCAN. Requisitos de interface, autenticação de serviço e contratos de dados estão pendentes.

## Autenticação e permissões

`Auth` usa `profile_store.stored_accounts` para ler contas no SQLite oficial, com fallback JSON quando a migração de contas não está concluída. `password_hash`/`verify_password` usam PBKDF2-HMAC-SHA256 e comparação em tempo constante. Tokens de sessão são mantidos em estrutura ordenada no processo; falhas de login têm throttling em memória. Cookies de sessão têm flags observadas no código; Secure depende de configuração. `profiles.py` determina grupo/partido e fontes; `Situation.actor` deriva função/célula e `require_final` protege ações finais. `do_POST` verifica origem e CSRF após login. Os controles não foram testados nem auditados contra implantação real.

## Persistência e arquivos

`Situation.__init__` declara que prepara `data/situation.sqlite3`, ativa WAL e cria tabelas de estado quando iniciado. `transaction(write=False)` ativa `PRAGMA query_only`; a transação padrão grava. `Auth`, bloqueios, auditoria de acesso, perfis e efeitos têm outros stores descritos em 20. `SourceStore` cria cache de KMZ/ícones e usa `config/sources.example.json` como modelo para `data/sources.json`. Essa inicialização pode gravar arquivos/DB; não foi executada.

O exemplo declara três IDs de fonte (`azul`, `vermelho`, `direx`) com IDs de Drive. São configuração de exemplo, não confirmação de configuração de produção nem credencial. O polling usa `urllib`; `validate_kmz` impõe limites declarados de tamanho e conteúdo. Fontes de dados e funcionamento externo não foram acessados.

## Erros e auditoria

Erros de domínio usam `SituationError(message,status,details)`. Entradas inválidas/parâmetros são tratados com respostas 400; falta de sessão 401; falha de função/origem/CSRF 403; rotas/serviços específicos retornam status 404/409/410/503 conforme branch. Registro HTTP omite query/headers e `AccessAudit` declara não guardar credenciais, cookies ou corpo. `situation.audit` é imutável contra atualização/exclusão por triggers criados no código. Essas propriedades são identificadas estaticamente; não são garantia de validação runtime.

## Reuso potencial e limites

**INFERÊNCIA:** funções de autenticação/roles, persistência de eventos, importadores geográficos e exportadores podem servir de referência para contratos futuros. Reutilização direta exigiria licença/escopo, fronteiras de segurança, identidade de objeto, migração, retenção e API aprovadas. Não há endpoint existente específico para módulos SISCAN e nenhum banco foi alterado nesta auditoria.
