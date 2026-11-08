# 25 — Inventário estático de rotas e interfaces HTTP

Fonte principal: `atlanticador-main/serve.py:26-408`. A tabela registra rotas encontradas no despacho; não é contrato formal OpenAPI. Os esquemas completos de alguns corpos residem nos serviços e podem variar por ação.

## Regras transversais observadas

- API usa JSON; `reply` define cabeçalhos de cache e pode comprimir respostas grandes (`serve.py:74-103`). Há respostas binárias PNG/KMZ para rotas cartográficas.
- GET de API exige sessão, salvo endpoints de ingresso/login apropriados; estado de troca obrigatória de senha restringe chamadas (`serve.py:110-127`).
- POST exige `Origin` de mesma origem e `Content-Type: application/json`; tamanho máximo é 256 KiB em `/api/control/` e 4 KiB nas demais (`serve.py:289-303`). Escritas autenticadas exigem `X-CSRF` (`serve.py:334-338`).
- Permissões adicionais são aplicadas por perfil, fonte, partido, função e célula. Erros do serviço podem retornar 400/403/404/409/410/423/428/429/502/503 conforme o caso.
- Não foi encontrado documento de contrato de API ou esquema de payload independente. Onde indicado “corpo delegado”, a validação específica ocorre na camada de serviço.

## GET

| Rota | Acesso/consulta | Retorno observado |
|---|---|---|
| `/api/session` | Sessão autenticada | usuário, CSRF, status de troca de senha, permissões de Confronto. |
| `/api/map-state` | Sessão e filtros de fonte | estado cartográfico atual. |
| `/api/map-baseline-index/{source}` | Modo structured-map e fonte autorizada | índice de baseline; 404 fora do modo. |
| `/api/map-baseline-features/{source}?ids=…&version=…` | Structured-map/fonte autorizada | feições do baseline para IDs e versão informados. |
| `/api/map-baseline/{source}` | Structured-map/fonte autorizada | KMZ do snapshot/baseline, ETag; 409 quando baseline ausente. |
| `/api/control/status` | Usuário autorizado no controle | estado de fechamento, revisão, permissões, funções, gatilhos/publicações. |
| `/api/control/confrontations?limit=&offset=&archived=&status=&cell=` | Células participantes/DIREx | lista paginada e `next_offset`. |
| `/api/control/confrontations/{id}` | Permissão de visualização de Confronto | detalhe, pareceres, histórico, permissões e unidades desatualizadas. |
| `/api/control/map-exports` | Controle | estado de exportações de mapa. |
| `/api/control/elements` | Controle; pré/pós-fechamento altera visibilidade | catálogo ou prévia de elementos por fontes permitidas. |
| `/api/control/effects?limit=&offset=&archived=&status=&cell=` | Controle conforme visibilidade | lista paginada de efeitos/propostas. |
| `/api/control/effects/{id}` | Controle conforme visibilidade | detalhe, histórico e estado de edição. |
| `/api/control/events?element=…` | Controle conforme visibilidade | consulta de eventos/alterações efetivas; filtros de elemento. |
| `/api/control/access-blocks` | Função final DIREx | bloqueios e histórico de acesso. |
| `/api/control/profiles` | Função final DIREx | perfis/listagem administrativa. |
| `/api/control/roles` | Controle | papéis/funções disponíveis. |
| `/api/control/publication/{id}` | DIREx ou tutor conforme regra | snapshot KMZ publicado. |
| `/api/sources` | Sessão | fontes visíveis ao perfil. |
| `/api/icon-manifest/{source}` | Fonte autorizada | chaves e referências de ícones. |
| `/api/icons/{source}/{token}` | Fonte autorizada | PNG cacheável. |
| `/api/kmz/{source}` | Fonte autorizada | KMZ com ETag e suporte a 304; 503 enquanto aguarda carga inicial. |
| `/api/map-symbol/{token}` | Sessão e fonte autorizada | PNG; erros de fonte reportados pelo handler. |
| `/api/control/*` desconhecida | Sessão | 404. |

Parâmetro `view_party` é aceito somente em consultas selecionadas e limitado a perfis demo/partidos previstos no handler (`serve.py:163-211`). Consultas de registros limitam `limit` a 1–200.

## POST

| Rota | Corpo/controle observado | Efeito/documento de resposta |
|---|---|---|
| `/api/entry/start` | `party`; ingresso temporário sem sessão | cookie de entrada temporário. |
| `/api/entry/identify` | `login`, `sequence` e cookie de entrada | verificação de sequência do ingresso. |
| `/api/login` | `username`, `password` com limites; autenticação | usuário/CSRF/senha obrigatória e cookie de sessão; códigos 423/428/429 em bloqueio/expiração/limite. |
| `/api/password/change` | senha atual/nova, sessão e CSRF | troca de credencial e renovação de sessão. |
| `/api/control/freeze` | fontes e `expected_versions` | congela baseline/publica snapshots; papel e versões são validados. |
| `/api/control/access-blocks/release` | `login` | libera bloqueio; papel final requerido. |
| `/api/control/map-exports/materialize` | solicitação de materialização | gera/publica exportações pendentes. |
| `/api/control/triggers` | `name` | adiciona evento deflagrador. |
| `/api/control/roles` | corpo delegado ao serviço | altera função/célula sob regra administrativa. |
| `/api/control/effects` | corpo vazio/implícito | cria rascunho DIREx ou proposta de partido conforme ator. |
| `/api/control/effects/{id}/edit` | `action` acquire/renew/release, `edit_token` | reserva/libera edição temporária. |
| `/api/control/effects/{id}/revise` | corpo delegado, `expected_revision`, token quando aplicável | atualiza rascunho/devolvido. |
| `/api/control/effects/{id}/decision` | ação, revisão esperada e fundamento quando exigido | envia, aprova, devolve, nega, agenda, efetiva ou anula conforme regra. |
| `/api/control/confrontations` | sem esquema HTTP amplo; serviço inicia registro | cria rascunho de Confronto. |
| `/api/control/confrontations/{id}/revise` | revisão esperada, contexto/unidades/operações/observações | edita rascunho/devolvido. |
| `/api/control/confrontations/{id}/response` | célula, parecer, valores/formulário e revisão | grava parecer de célula ou bypass justificado. |
| `/api/control/confrontations/{id}/decision` | ação e revisão; fundamento em decisões pertinentes | conferir, aceitar, enviar, aprovar, negar/devolver, cancelar ou efetivar/anular admin. |
| `/api/control/confrontations/{id}/clone` | revisão esperada | clona registro, atualizando referência às tropas. |
| `/api/control/confrontations/{id}/refresh` | revisão esperada | atualiza referências às unidades atuais. |
| `/api/control/events*` | interface antiga | deliberadamente retorna 410; não é interface ativa de escrita. |
| `/api/logout` | sessão e CSRF | encerra sessão. |

## Rotas não API e formatos

Páginas públicas/autenticadas são servidas a partir de `frontend/`. `/importar` e `/editor.html` dependem de `can_import`; `/direx` restringe-se ao partido DIREx; `/mapa` serve o visualizador. O handler também atende `HEAD` via fluxo de GET. Não há inventário exaustivo dos assets estáticos neste documento.

**Limite:** nomes de campos acima foram anotados quando explícitos no despacho ou serviços examinados; isto não substitui especificação de contrato, nem confirma compatibilidade de clientes em execução.
