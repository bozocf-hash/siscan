# 31 — Fluxos de interface e comunicação frontend-backend

Fonte: inspeção estática de módulos do ZIP ATLANTICADOR 2.0.0. As linhas citadas são relativas a `atlanticador-main/`; o catálogo de servidor de referência é [25](25_INVENTARIO_ROTAS_E_INTERFACES_API.md). A leitura não confirmou fluxos em execução.

## Fluxos de tela e navegação

### Login e ingresso

- `login.mjs` tenta restaurar sessão por `GET /api/session`, envia credenciais para `POST /api/login`, guarda o token CSRF em estado de página e envia `X-CSRF-Token` nos POST de logout/troca de senha (`frontend/src/login.mjs:6,10,29,46,51`). O cookie é gerenciado pelo servidor/navegador.
- `party-entry.mjs`/`tutor-entry.mjs` ligam telas de ingresso a `/api/entry/start`, `/api/entry/identify` e `/api/session`. O frontend coordena sequência; validação autoritativa fica no backend.
- O cabeçalho `X-CSRF-Token` do cliente coincide com a checagem do mesmo cabeçalho no handler (`serve.py:337`); o envio é evidência de contrato estático, embora não tenha sido exercitado.

### Visualizador

1. `viewer.mjs` consulta sessão, carrega `/api/sources` e `/api/map-state`, calcula fontes/visibilidade e escolhe modo KMZ ou structured-map (`viewer.mjs:46,64-96,317-330,395-396`).
2. Para fontes, pede `/api/kmz/{source}` ou `/api/map-baseline/{source}` e, no modo estruturado, índice/feições. Manifest e ícones vêm de `/api/icon-manifest/{source}` e `/api/icons/{source}/{token}`.
3. Renderizador converte e desenha os dados em SVG sobre Leaflet; atualizações de sessão 401 encerram a tela.
4. Tiles base são obtidos de OpenTopoMap ou OpenStreetMap por URL externa (`viewer.mjs:543`). Disponibilidade, licença/termos e modo offline não foram verificados.

### Editor/importação/exportação

`app.mjs` abre cena inicial ou restaura rascunho `localStorage`; edições são mantidas por histórico local e salvamento local (`app.mjs:39-44`). `map-import.mjs` consulta `/api/control/status` para exibir/condicionar acesso, porém o resultado de importação permanece draft local; módulos `exchange.mjs`/`kml.mjs` tratam os arquivos. `map-unpack.mjs` cria worker de módulo para descompactação e timeout (`map-unpack.mjs:1-10`). Exportação é do lado cliente via `map-export.mjs`, `map-export-core.mjs` e `point-export.mjs`; isso não é publicação oficial do backend.

### Efeitos e Confronto

`effects-panel.mjs` e `confrontations.mjs` têm helper local de `fetch` para `/api/control/`, passando JSON e CSRF em POST (`effects-panel.mjs:56`, `confrontations.mjs:38`). Construem telas de listagem, edição, histórico, respostas e decisão e consomem as rotas GET/POST do backend. `situation-ui.mjs` traz status, fontes, controles, exportação e link de publicação (`situation-ui.mjs:22,50,180`). Como helpers e payloads estão distribuídos por módulos, o inventário abaixo não define um contrato estável.

**Divergência confirmada — eventos legados:** `situation-ui.mjs` ainda constrói formulário de proposta/revisão e envia POST para `/api/control/events` ou `/api/control/events/{id}/revise` (`situation-ui.mjs:60-90`). O handler do backend retorna 410 para `/api/control/events*` (`serve.py:401`). Portanto, estes controles existem no código da interface, mas a escrita correspondente está desativada nesta versão. Não foi executado para avaliar a apresentação do erro ou possível fluxo alternativo.

## Matriz de comunicação observada

| Consumidor/módulo | Endpoint(s) encontrados | Tipo de operação no cliente | Cruzamento com backend 25 |
|---|---|---|---|
| `login.mjs` | `/api/session`, `/api/login`, `/api/logout`, `/api/password/change` | GET de sessão; POST JSON de login, troca/logout | Compatível em nomes gerais com rotas do catálogo. Campos/erros precisam contrato completo. |
| `party-entry.mjs`, `tutor-entry.mjs` | `/api/entry/start`, `/api/entry/identify`, `/api/session` | GET/POST conforme fluxo | Catálogo backend registra ingresso; verificar campos e caminho tutor no contrato. |
| `viewer.mjs` | `/api/session`, `/api/sources`, `/api/map-state`, `/api/kmz/{source}`, `/api/map-baseline/{source}`, `/api/map-baseline-index/{source}`, `/api/map-baseline-features/{source}`, `/api/icon-manifest/{source}`, `/api/icons/{source}/{token}`, `/api/logout` | GET cartográfico/estado; POST logout | Correspondência com GETs do catálogo 25; formato/versão de feições requer detalhe. |
| `renderer.mjs` | `/api/icons/{source}/{token}` | GET binário de ícone | Endpoint registrado em 25. |
| `map-import.mjs` | `/api/control/status` | GET permissão/estado antes do rascunho | Endpoint registrado; importação em si não envia arquivo ao backend. |
| `situation-ui.mjs` | `/api/control/{path}`, `/api/sources`, `/api/control/publication/{id}`; constrói chamadas `events` | GET/POST JSON; baixa KMZ publicado | Status/fontes/publicação constam em 25; POST `events/revise` conflita com 410 do backend. |
| `effects-panel.mjs` | `/api/control/{path}`, `/api/control/effects/{id}/edit` | GET/POST; reserva de edição e ações | Mapeia para list/detail/edit/revise/decision; schema distribuído no helper/handler. |
| `confrontations.mjs` | `/api/control/{path}` | GET/POST de registros, respostas e decisões | Mapeia a list/detail/revise/response/decision/clone/refresh. |

## Divergências e questões

1. O nome `X-CSRF-Token` usado pelos helpers coincide com `serve.py:337`.
2. Rotas montadas como string (`/api/control/` + `path`) não deixam um endpoint literal no módulo. Para garantir lista integral de verbos, campos e caminhos, seria necessário seguir cada chamada de `request()` nos painéis.
3. Importação do editor é local; não se deve confundir consulta de permissão com upload/importação persistente.
4. Visualizador usa dois caminhos (KMZ e structured-map) e fontes/icon paths; dados e codificações exatos requerem documentação de contrato.
5. Não foi observada API cliente central, tipagem/schema compartilhados ou OpenAPI. Validação, parsing de erro e mensagens variam por tela.
6. O frontend ainda apresenta criação/revisão de eventos (`situation-ui.mjs:60-90`), mas o backend retorna 410 para a escrita correspondente (`serve.py:401`). É uma divergência estática a avaliar em manutenção futura, não corrigida nesta missão.

## Autenticação, erros e permissões

O navegador envia cookies same-origin por padrão em `fetch` sem `credentials:'omit'`; POST autenticado inclui token CSRF conforme helpers. A UI pode ocultar/condicionar operações com base em status e perfil, mas servidor aplica autorização. Alguns módulos tratam 401 redirecionando ou encerrando sessão e erros com feedback local. Nenhuma validação de sessão, CSRF, autorização, erro ou resposta foi exercitada em runtime.
