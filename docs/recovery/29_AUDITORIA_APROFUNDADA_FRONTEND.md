# 29 — Auditoria aprofundada do frontend ATLANTICADOR

**Status:** auditoria documental estática do ZIP ATLANTICADOR 2.0.0. Caminhos e linhas abaixo são relativos a `atlanticador-main/`. Foram examinados o inventário completo de `frontend/` (328 arquivos), páginas, módulos centrais e auxiliares selecionados. Isso não comprova funcionamento no navegador.

## Síntese executiva

O frontend é servido junto com o backend Python e usa HTML/CSS e ES Modules nativos, sem framework/bundler declarado. Divide-se entre o visualizador (`viewer.html`/`src/viewer.mjs`), que consome fontes e situação oficial, e um editor cartográfico de rascunhos (`editor.html`/`src/app.mjs`), com estado local em `localStorage`. Módulos menores cobrem importação/exportação, geometria, camadas, renderização SVG sobre Leaflet, login, efeitos e Confronto.

A comunicação usa `fetch` same-origin e as rotas já inventariadas em [25 — API backend](25_INVENTARIO_ROTAS_E_INTERFACES_API.md). Há dependências diretas do DOM, de globais `L` (Leaflet) e `window.atlCalungaEngine`, além de módulos que importam uns aos outros. A separação visual/cartográfica existe em parte, mas regras de workflow, estado, renderização e chamadas HTTP ainda se cruzam.

Foi confirmada uma divergência frontend/backend: `situation-ui.mjs` ainda oferece proposta/revisão por `/api/control/events*`, enquanto `serve.py` retorna 410 para essas escritas (`situation-ui.mjs:60-90`; `serve.py:401`). A presença do formulário não comprova que o fluxo funcione.

## Estrutura verificada

`frontend/` contém 8 páginas HTML, `src/` com 73 arquivos, `assets/` com 230 itens e `vendor/` com 17 arquivos. Os diretórios relevantes e arquivos estão detalhados em [30](30_MAPEAMENTO_MODULOS_COMPONENTES_FRONTEND.md). O pacote inclui Leaflet 1.9.4, leaflet-rotate, polygon-clipping, fflate, html-to-image, jsPDF e motor/catalogação Calunga local; presença não é prova de validade/licença de uso pelo SISCAN.

## Arquitetura e acoplamentos

- `viewer.mjs` inicializa Leaflet, monta fontes/camadas e instala a UI funcional; importa cache, patches de baseline, cenas oficiais, painéis, importação, exportação, Confronto e situação (`frontend/src/viewer.mjs:2-20,64-96`).
- `app.mjs` reúne edição de cena, histórico, ferramentas, renderização, camadas e persistência local (`frontend/src/app.mjs:2-12,22,39-44`).
- `scene.mjs`/`model.mjs` fornecem estruturas de cena e apresentação; `workflow.mjs` valida rascunhos e diferenças; `geometry.mjs` e `utm.mjs` implementam operações espaciais.
- `renderer.mjs` converte coordenadas do domínio para pixels Leaflet e desenha SVG; `render-order.mjs`, `render-geometry.mjs`, `symbols.mjs` e `hostile-symbol.mjs` apoiam a apresentação.
- Módulos UI como `effects-panel.mjs` e `confrontations.mjs` contêm montagem DOM, validações locais e `fetch` a rotas do backend. Isso é acoplamento de apresentação com API e fluxo de negócio.

Importações são ES Modules relativos, porém os pontos de entrada ainda dependem de DOM/globais e de ordem de carregamento declarada pelas páginas. Não foi encontrado estado global centralizado ou SDK de API único; alguns módulos mantêm estado interno e caches em memória.

## Cartografia e simbologia

Leaflet é inicializado em viewer e editor. Os elementos de cena usam longitude/latitude WGS84 e tipos pontuais/linha/área; no editor, vértices carregam IDs e polígonos usam anéis (`scene.mjs:5-7,120-128`). Renderer projeta coordenadas via API de mapa Leaflet e cria SVG (`renderer.mjs:19-53`). Há conversão WGS84↔UTM em `utm.mjs`, seleção automática de zona e limites de latitude documentados no código (1-7, 80-96, 143-177). Existem grades e geometria auxiliares, mas não se atesta precisão ou adequação para uso operacional sem validação própria.

Calunga é composta por `catalog.json`, `engine.js` e `dependencies.js`, consumidos por `calunga-generator.mjs`. README da biblioteca diz que os arquivos locais são cópias do Portal de Simbologia Militar do Exército obtidas em 26 OUT 2026, identifica bundles derivados e preservação de avisos de terceiros (`frontend/vendor/calunga/README.md:1-9`). O catálogo declara 497 ícones centrais. Não foi localizada licença única/expressa para o pacote Calunga; bundles incluem avisos de terceiros. É necessária verificação de origem, licença, direitos, avisos, redistribuição e conformidade simbólica antes de eventual uso no SISCAN.

## Estado e persistência

Editor salva a cena de trabalho em `localStorage` por observador (`app.mjs:39-44`), trata cena como rascunho sem publicação (`scene.mjs:1`, `workflow.mjs:1,26`). Viewer guarda preferências/visão e cache local associado ao login/partido (`viewer.mjs:68-96,439`); Confronto mantém snapshots auxiliares em `sessionStorage` e memória (`confrontations.mjs:58-59`). Não foram identificados usos de IndexedDB no conjunto pesquisado. Sessão/autorização real vem do backend por cookie; não há evidência de que o frontend seja autoridade de acesso. O modelo também declara que filtros de apresentação não são controle de acesso (`model.mjs:1-2`).

## Conclusões para o SISCAN

O visualizador e a separação entre adaptadores cartográficos, cena, renderização e utilitários geográficos são referências úteis. `scene.mjs`, `geometry.mjs`, `utm.mjs`, renderização e import/export são candidatos a avaliação com adaptação, sempre após revisão técnica e de licenças. O editor, a Calunga específica, os fluxos de partido/DIREx, efeitos e Confronto carregam convenções ATLANTICADOR e não devem ser transplantados por simples disponibilidade. A proposta conceitual está em [34](34_PROPOSTA_ARQUITETURA_FRONTEND_SISCAN.md); a classificação detalhada em [33](33_MATRIZ_REUTILIZACAO_FRONTEND_SISCAN.md).

## Método, limites e pendências

Examinados o ZIP sem extração, lista completa dos 328 arquivos em `frontend/`, HTML, páginas e módulos de entrada/integração/cartografia, arquivos Calunga e documentação indicada. Não foram executados scripts da aplicação, servidor, testes, browser, instalação ou chamadas de rede. Também não se comprovou licença, comportamento visual, desempenho, compatibilidade entre todos os formatos, precisão de transformação cartográfica, nem acessibilidade. Os módulos auxiliares remanescentes constam no inventário, mas nem cada arquivo foi lido integralmente linha a linha. Não houve alteração de código, banco, configuração ou arquivos originais. A próxima missão permanece sujeita à autorização do responsável.
