# 17 — Arquitetura técnica do ATLANTICADOR

## Síntese

**CONFIRMADO no código:** pacote monolítico simples com servidor HTTP Python, frontend estático no mesmo processo/origem, chamadas JSON para rotas implementadas em `serve.py`, serviços funcionais Python e SQLite no diretório de dados. Um processo auxiliar sincroniza fontes KMZ; outro ciclo periódico trata expiração de entradas e efeitos agendados. O modo de mapa estruturado é opcional e tem restrição de loopback quando ativado.

Isso descreve estrutura e caminhos de código, não prova execução, disponibilidade ou segurança efetiva em produção. Não foi executado código, servidor ou teste.

## Componentes e dependências

| Componente | Responsabilidade e vínculos | Evidência |
|---|---|---|
| `serve.Handler` | `SimpleHTTPRequestHandler` especializado; serve `frontend/`, roteia GET/POST, autentica, verifica origem/CSRF, aplica regras de acesso e serializa JSON | `serve.py`, classe `Handler`, `do_GET`, `do_POST` |
| `Auth` | Credenciais PBKDF2-HMAC-SHA256, sessões, senha inicial, rate limits em memória, entradas temporárias; compõe `AccessBlocks` e `AccessAudit` | `auth.py` |
| `profiles.py` | Normalização, partido, função, fontes visíveis e perfil público | `profiles.py` |
| `Situation` | Modelo de aplicação e facade: herda `Confrontations`, `EffectWorkflow`, `StructuredMap`; estado oficial e transações | `situation.py` |
| `SourceStore` | Lê configuração, consulta fontes KMZ, valida KML, mantém cache/snapshot e ícones; sincronização periódica | `sources.py` |
| `StructuredMap` | Exportação/transporte estruturado e materialização de mapas; ativação optativa por argumento | `structured_map.py`, `serve.py --structured-map` |
| Frontend viewer | Mapa, camadas, estado oficial, efeitos e confrontos; consome rotas `/api/...` | `frontend/viewer.html`, `frontend/src/viewer.mjs` |
| Frontend editor | Edição local de cena/camadas, importação e exportação de formatos cartográficos | `frontend/editor.html`, `frontend/src/app.mjs` |
| Mosaicos externos | Tiles cartográficos podem sair do navegador para provedores definidos pela UI/documentação | Não equivale a API SISCAN; configuração/uso em operação não verificado |

## Inicialização e fluxo de comunicação

`start-atlanticador.cmd` declara iniciar `py -3.12 serve.py`. Em `serve.py::main`, defaults declarados são host `127.0.0.1`, porta 8787, diretório `data/`, sync a cada 60 segundos. A inicialização prepara diretório/configuração, instancia `Auth`, `SourceStore` e `Situation`, associa fontes à situação, pode iniciar sincronização, agenda verificação periódica e monta `ThreadingHTTPServer`. **Esse fluxo não foi executado nesta missão.**

O viewer/editor é servido pelo mesmo handler que recebe sua API JSON. Não foi localizado OpenAPI/Swagger nem contrato neutro e versionado para integração SISCAN. As rotas são despachadas por condições de caminho em `serve.py`, com formatos definidos junto ao handler e aos serviços. A existência dessas rotas não cria, por si, uma interface estável para cliente externo.

### Famílias de endpoints identificadas

- Sessão/acesso: `/api/session`, `/api/login`, `/api/logout`, `/api/password/change`, `/api/entry/*`.
- Fontes/cartografia: `/api/sources`, `/api/kmz/*`, `/api/icons/*`, `/api/icon-manifest/*`, `/api/map-state`, `/api/map-symbol/*` e `/api/map-baseline*`.
- Controle: `/api/control/status`, `elements`, `events`, `effects`, `confrontations`, `roles`, `triggers`, `profiles`, `access-blocks`, `map-exports`, `publication/*` e `freeze`; POST atende operações e transições.
- Há rotas antigas de evento que retornam HTTP 410 segundo o handler, sinalizando fluxo substituído.

Métodos verificados no handler: GET, HEAD (delegado a GET) e POST. Não foi identificada API de escrita SISCAN ou rotas para módulos conceituais ainda inexistentes.

## Autenticação, autorização e tratamento de erro

`Auth` mantém sessões e tentativas na memória do processo; cookies são HttpOnly e SameSite Strict, com Secure opcional por argumento. `serve.Handler::do_POST` confere `Origin`, tipo/tamanho do JSON, sessão e `X-CSRF-Token`; permissões adicionais são aplicadas em rotas de controle. `profiles.py`, `Situation.actor/require_final` e serviços de workflow fazem checagens por perfil/partido/função. `situation.py::SituationError` carrega status HTTP e detalhes; o handler traduz erros e algumas falhas de entrada em respostas JSON.

O código contém mecanismos de segurança, mas não foram executados nem submetidos a teste ou revisão de ameaça nesta missão. Não tratar presença de verificação como garantia de funcionamento ou certificação.

## Persistência, fontes e auditoria

Ver análise detalhada em [20 — Persistência e dados](20_PERSISTENCIA_E_MODELO_DE_DADOS.md). Em alto nível, `situation.sqlite3` mantém estado, snapshots, eventos, funções e registros; `access.sqlite3` contém bloqueios/ingressos; `access-log.sqlite3` recebe auditoria de acesso. Fonte KMZ e ícones possuem caches em arquivos no diretório de dados. O DB3K do CMO é arquivo externo e separado.

`serve.Handler::log_message` registra método/caminho/status sem query string; `AccessAudit` grava eventos limitados e `situation.audit` armazena trilha das decisões/efeitos com bloqueio de UPDATE/DELETE em tabela audit. Erros de processos periódicos são reportados sem interromper o ciclo. Não foi verificado comportamento em execução.

## Pontos de integração e questões arquiteturais

**INFERÊNCIA/PROPOSTO:** o mesmo processo/origem HTTP e as APIs JSON poderiam ser pontos a avaliar para comunicação futura, mas atualmente atendem o ATLANTICADOR e não têm contrato SISCAN. Uma integração exigiria decidir identidade/versionamento dos dados, eventos, autorização, compatibilidade da persistência, formato de entidades e independência do MPNL. Não presumir reuso direto de `Situation` ou das tabelas JSON como modelo do SISCAN.
