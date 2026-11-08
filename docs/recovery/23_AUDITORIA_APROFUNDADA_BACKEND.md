# 23 — Auditoria aprofundada do backend ATLANTICADOR

**Escopo:** leitura estática do código contido em `atlanticador-main (1).zip` (versão 2.0.0). Esta auditoria documenta evidências do pacote, sem atestar execução, segurança operacional ou comportamento em produção. Não foram executados servidor, testes ou comandos de gerenciamento.

## Síntese

O backend é uma aplicação Python baseada na biblioteca padrão, servida por `ThreadingHTTPServer` e `SimpleHTTPRequestHandler`. `serve.py` concentra o protocolo HTTP e compõe `Auth`, `SourceStore` e `Situation`. A classe `Situation` agrega `Confrontations`, `EffectWorkflow` e `StructuredMap`. O modelo é orientado a fluxos de situação/mapa, publicações KMZ e registros de efeitos/confrontos; não há API OpenAPI nem contrato independente encontrado.

O arquivo de situação usa SQLite, mas muitos registros de domínio são JSON armazenado em colunas `body`; o mapa oficial também mantém KMZ como BLOB, snapshots e metadados. Autenticação usa sessões em memória e cookies; bloqueios e auditoria de acesso usam bancos SQLite separados. A fonte externa é consultada por `SourceStore`; há sincronização periódica prevista no inicializador, não observada em execução.

## Arquitetura e acoplamentos

| Camada | Evidência estática | Observação |
|---|---|---|
| HTTP e inicialização | `serve.py:26-284,286-408,411-452` | Rotas, autenticação, validação de cabeçalhos, resposta JSON/binária e inicialização no mesmo módulo. |
| Identidade e sessão | `auth.py:25-227`, `profiles.py`, `function_roles.py` | PBKDF2-SHA256, sessão em memória, funções/células e visibilidade por partido. |
| Orquestração da situação | `situation.py:28-56` | Herda três mixins de fluxo; transações SQLite e tabelas base. |
| Efeitos | `effect_workflow.py:48-368` | Validação, revisão, reserva de edição, aprovações, aplicação e agendamento. |
| Confrontos | `confrontations.py:38-486` | Registro de arbitragem humana e pareceres de células, com revisão e aprovações. |
| Propostas dos partidos | `party_proposals.py:58-213` | Propostas e intake da DIREx por blocos; alimenta o fluxo de efeitos. |
| Fontes cartográficas | `sources.py:21-300` | Configuração, download/sincronização, validação KMZ e cache. |
| Publicação cartográfica | `official_kmz.py:1-204`, `structured_map.py`, `export_deltas.py` | Baseline e snapshots derivados; modo estruturado opcional. |
| Acesso/auditoria | `access_blocks.py:9-70`, `access_audit.py:13-40` | Bloqueios persistentes e trilha append-only de eventos de acesso. |

Há acoplamento entre HTTP e classes de serviço por chamadas diretas, entre os mixins por chamadas cruzadas (por exemplo, confronto cria/aplica efeito), e entre dados cartográficos e fluxo de situação. O modelo de domínio não está isolado atrás de interfaces formais. Configuração de fontes e diretório de dados também se relacionam diretamente com o ciclo de inicialização.

## Segurança e limites de evidência

No código são identificados: cookie `HttpOnly`/`SameSite=Strict` (e `Secure` opcional); verificação de `Origin` em POST; cabeçalho CSRF para rotas autenticadas; limites de corpo; checagem de papéis/células; consultas SQLite parametrizadas nos trechos examinados; hash de senha PBKDF2; bloqueio por tentativas em memória; e filtragem de fontes conforme perfil. Esses itens são características observadas no código, não resultado de teste de segurança. Não foram avaliados controles de implantação, TLS, proxy, segredos, configuração de produção, abuso concorrente nem vulnerabilidades.

## Descobertas funcionais relevantes

- Fechamento da situação exige baselines/versionamentos das fontes e publica snapshots; congelamento de fontes é uma barreira de fluxo, não uma simulação (`situation.py:136-179`).
- Efeitos oficiais dependem de validação contra revisões atuais, revisão de célula e aprovações; podem ser agendados e entrar em conflito se a validação posterior falhar (`effect_workflow.py:164-215,276-368`).
- Confrontos agregam dados de tropas dos dois partidos e pareceres de células; decisões e alterações efetivas são humanas e registradas no fluxo (`confrontations.py:100-195,302-364,378-486`). O pacote declara que não há simulação ou aconselhamento tático automático (`confrontations.py:1`).
- Propostas de partido passam por aprovação interna e encaminhamento à DIREx; o código impede que a proposta altere diretamente o mapa durante a etapa de proposta (`party_proposals.py:1,78-147`).
- `Situation.propose`/`decision` e consulta de eventos permanecem no código, mas POST legado `/api/control/events*` responde 410; portanto, não se deve tratar essas funções internas como interface ativa de escrita (`serve.py:401`).
- Rotas e esquemas de entrada são implementados manualmente. A validação de corpo está distribuída entre `serve.py` e serviços; não se encontrou especificação formal versionada da API.

## Ver também

- [24 — Módulos e serviços](24_MAPEAMENTO_MODULOS_SERVICOS_BACKEND.md)
- [25 — Rotas e interfaces](25_INVENTARIO_ROTAS_E_INTERFACES_API.md)
- [26 — Fluxos de negócio](26_FLUXOS_DE_NEGOCIO_BACKEND.md)
- [27 — Persistência](27_PERSISTENCIA_E_ACESSO_DADOS_BACKEND.md)
- [28 — Reutilização no SISCAN](28_MATRIZ_REUTILIZACAO_BACKEND_SISCAN.md)

## Limitações

Somente código e documentação empacotados foram consultados. Nenhum banco de dados operacional do ATLANTICADOR foi aberto; não há confirmação de configuração/contas/fontes em produção. A leitura é estática e focada em módulos de backend e suas conexões; não substitui revisão linha a linha do pacote, execução controlada, testes ou auditoria de segurança. As relações com SISCAN são referências para avaliação, não decisões aprovadas nem autorização de reutilização.
