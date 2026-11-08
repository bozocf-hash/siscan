# 27 — Persistência e acesso a dados do backend

Leitura estática de caminhos e instruções encontrados no pacote. Não foram abertos nem inspecionados bancos operacionais ATLANTICADOR; arquivos descritos são nomes/caminhos configurados pelo código.

## Armazenamentos identificados

| Arquivo/armazenamento | Conteúdo/campos identificados | Acesso observado | Limite |
|---|---|---|---|
| `data/situation.sqlite3` | estado principal, papéis, fontes congeladas, snapshots, eventos, auditoria de domínio, publicações, efeitos, editores, confrontos, gatilhos e exportações | conexão SQLite; WAL; transação `BEGIN` ou `BEGIN IMMEDIATE`; `foreign_keys=ON`; `query_only=ON` em leitura (`situation.py:29-71`) | Esquema misto e registros JSON; não é banco operacional verificado. |
| `data/access.sqlite3` | bloqueios, histórico de bloqueio, janelas de ingresso (`access_blocks.py:13-19`) | SQLite e transações próprias | Banco auxiliar de identidade/acesso. |
| `data/access-log.sqlite3` | eventos de acesso: id, UTC, evento, login/nome/partido, status HTTP, recurso, IP de backend (`access_audit.py:7-23`) | SQLite, índice temporal e triggers sem update/delete; fallback para journal | Trilha técnica, não trilha completa das ações de domínio. |
| `data/accounts.json` | fallback de contas se perfil SQLite indisponível/não migrado | leitura/gravação condicional (`auth.py`, `profile_store.py`) | Conteúdo real não consultado. |
| `data/sources.json` e `data/kmz-cache/` | configuração e cache de fontes KMZ | arquivos em diretório de dados | Configuração de produção não confirmada. |
| `data/situation-backups/` | cópias de baselines KMZ ao congelar | arquivos KMZ gerados por código | Não foi criado nenhum backup nesta auditoria. |

## Situação principal: esquema e codificação

`Situation.__init__` contém DDL para `meta`, `roles`, `elements`, `baselines`, `snapshots`, `current`, `events`, `audit`, `publications`, `triggers`; mixins adicionam `effect_records`, `effect_editors`, `confrontations` e estruturas de exportação (`situation.py:29-56`, `effect_workflow.py:48-50`, `confrontations.py:38-40`). Em geral o domínio serializa objeto em texto JSON (`body`) associado a identificador. Baselines/snapshots preservam bytes KMZ como BLOB; `current` mantém versão por fonte. A existência destas tabelas no código não significa que foram criadas em uma instalação.

Relações identificáveis incluem efeito→elemento por `element_id`, efeito derivado→proposta por `proposal_id`, confronto→efeito por `effect_id`, editor→efeito por `effect_id`, snapshots/publicações→revisão/versão de fonte. Parte dessas relações está embutida no JSON e validada pelo serviço, não expressa necessariamente como FK relacional. Não generalizar as 75 FKs do DB3K para estes bancos independentes.

## Transações, consistência e histórico

`Situation.transaction` controla commit/rollback e configura leitura/escrita; operações de mutação passam por transação imediata. Registros de efeito/confronto gravam JSON e ação correspondente em `audit`. A auditoria de acesso é separada e possui política append-only definida por triggers. Não foi feita análise dinâmica de concorrência, recuperação de falha, desempenho, retenção ou consistência entre SQLite e arquivos no disco.

Edição de efeito tem tabela de reserva com usuário, token, nome e expiração; o token é recebido no corpo e a reserva expira após 60s (sem conclusão sobre segurança operacional). Revisões esperadas protegem atualização contra alterações concorrentes. Efeitos agendados são relidos e validados no momento de aplicar; conflito fica registrado.

## Acesso e limites de leitura

Consultas filtram visibilidade por partido/função/célula e limitam paginação. Perfil do usuário pode ser lido de `situation.sqlite3` em modo somente leitura depois de indicador de migração, ou de JSON. Fontes são filtradas por `allowed_sources`. Não houve abertura dos DBs do ATLANTICADOR, inventário de dados reais, confirmação de unidades/domínios, conteúdo de cadastros ou validação de anonimização.

## Separação em relação ao DB3K

DB3K é uma fonte separada do produto de banco de dados do COMMAND. Sua integridade estrutural, inventário e relacionamentos declarados não comprovam entendimento semântico. Os armazenamentos ATLANTICADOR acima têm finalidades próprias e não são o DB3K; não foi identificada leitura direta do DB3K pelo backend analisado. Campos embutidos em JSON precisam de interpretação explícita antes de qualquer comparação com o modelo SISCAN.
