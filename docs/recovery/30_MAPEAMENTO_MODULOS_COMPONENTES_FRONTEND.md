# 30 — Mapeamento de módulos e componentes do frontend

Inventário estático relativo a `atlanticador-main/frontend/`. Contagens confirmadas no ZIP: **328 arquivos** (8 HTML, 73 arquivos em `src/`, 230 em `assets/`, 17 em `vendor/`).

## Árvore relevante

```text
frontend/
├── index.html, login.html, azul.html, vermelho.html, tutores.html, direx.html
├── viewer.html, editor.html
├── assets/                         # 230 imagens/ícones/recursos
├── src/                            # 73 módulos ES, CSS e auxiliares
│   ├── app.mjs, viewer.mjs
│   ├── model.mjs, scene.mjs, workflow.mjs, layer-tree.mjs, modes.mjs
│   ├── geometry.mjs, utm.mjs, cartography.mjs, map-grids.mjs
│   ├── renderer.mjs, render-geometry.mjs, render-order.mjs, symbols.mjs
│   ├── exchange.mjs, kml.mjs, map-import.mjs, map-unpack.mjs, map-worker.mjs
│   ├── map-export.mjs, map-export-core.mjs, map-crop.mjs, point-export.mjs
│   ├── source-view.mjs, official-scene.mjs, official-additions.mjs
│   ├── situation-ui.mjs, effects-panel.mjs, effect-*.mjs
│   ├── confrontations.mjs, confrontation-*.mjs, record-pages.mjs
│   ├── login.mjs, party-entry.mjs, tutor-entry.mjs
│   └── feedback/tutorial/about/button-feedback e CSS de tela
└── vendor/
    ├── leaflet/ (JS, CSS, licença)
    ├── leaflet-rotate/ (JS, licença)
    ├── polygon-clipping/ (JS, licença)
    ├── fflate/, html-to-image/, jspdf/ (JS e avisos de licença)
    └── calunga/ (README, catalog.json, engine.js, dependencies.js)
```

## Páginas

| Página | Finalidade/arquivos | Estado e dependências | Integração/limite |
|---|---|---|---|
| `index.html` | Entrada/encaminhamento | HTML e estilos | Comportamento visual completo não executado. |
| `login.html` | Login e sessão; `src/login.mjs` | formulário, mensagens, cookie gerido pelo navegador | `/api/session`, `/api/login`, `/api/logout`, `/api/password/change`. |
| `azul.html`, `vermelho.html` | Ingresso de partido; `party-entry.mjs` | estado do fluxo no formulário | `/api/entry/start`, `/api/entry/identify`, sessão. |
| `tutores.html` | Entrada de tutor; `tutor-entry.mjs` | consulta de sessão | Esquema de identidade e funcionamento dependem do backend. |
| `direx.html` | Página DIREx | markup; não declara diretamente módulo em `<script>` conforme auditoria anterior | A rota de servidor controla o acesso; confirmar ligação completa entre página e UI. |
| `viewer.html` | Visualizador; `src/viewer.mjs` | mapa, fontes, camadas e painéis; Leaflet | estado, sessão, fontes, KMZ/baseline e ícones. |
| `editor.html` | Editor de cena local; `src/app.mjs` | cena/histórico local; Leaflet, símbolos, camadas | importa arquivos para rascunho local; sem publicação automática. |

## Módulos por domínio

| Grupo e módulos | Responsabilidades e conexões | Acoplamento / avaliação inicial |
|---|---|---|
| Entrada: `app.mjs`, `viewer.mjs` | Inicializam mapa, estado de tela, painéis, eventos e dependências. | Alto: dependência de DOM, Leaflet global e muitos serviços UI. |
| Modelo: `model.mjs`, `scene.mjs`, `workflow.mjs` | Entidades de apresentação/cena, árvore, edição, validação, GeoJSON, rascunho e diff. | Médio: boa separação conceitual, mas tipos e vocabulário do simulador. |
| Camadas: `layer-tree.mjs`, `modes.mjs`, `box-dock.mjs` | Hierarquia, visibilidade, edição e interação de painéis. | Médio; UI/DOM e semântica ATLANTICADOR a avaliar. |
| Geoespacial: `geometry.mjs`, `cartography.mjs`, `utm.mjs`, `map-grids.mjs` | Geometria, conversões, grade e visualização de coordenadas. | Reutilização condicionada a testes de precisão e requisitos SISCAN. |
| Renderização: `renderer.mjs`, `render-geometry.mjs`, `render-order.mjs`, `symbols.mjs`, `hostile-symbol.mjs`, `viewer-icons.mjs`, `spiderfy.mjs` | Converte coordenadas para pixels e desenha SVG/camadas/ícones. | Dependência Leaflet, DOM/SVG e convenções de símbolo. |
| Importação: `exchange.mjs`, `kml.mjs`, `map-unpack.mjs`, `map-worker.mjs`, `map-import.mjs` | Leitura KML/KMZ/GeoJSON, validação, descompactação em Web Worker e rascunhos. | Worker e formatos/límites exigem validação independente. |
| Exportação: `map-export.mjs`, `map-export-core.mjs`, `map-crop.mjs`, `point-export.mjs`, `map-cache.mjs` | Captura de mapa, recorte, KML/KMZ, CSV, GeoTIFF e cache. | Dependências externas de tiles e bibliotecas; exportação deve ser validada. |
| Situação: `source-view.mjs`, `official-scene.mjs`, `official-additions.mjs`, `baseline-patch.mjs`, `scene-asset-cache.mjs` | Incorpora estado oficial, baseline e diferenças no visualizador. | Alto acoplamento ao contrato de dados ATLANTICADOR. |
| Efeitos: `situation-ui.mjs`, `effects-panel.mjs`, `effect-history.mjs`, `effect-live-edit.mjs`, `effect-map-tools.mjs`, `effect-preview-scene.mjs`, `effect-symbol-preview.mjs`, `unit-conditions.mjs` | Operações UI, edição, histórico, prévia e aplicação visual de estados. | Alto: UI contém chamadas API e regras do workflow backend. |
| Confronto: `confrontations.mjs`, `confrontation-models.mjs`, `confrontation-game.mjs`, `game-calendar.mjs`, `control-response.mjs`, `record-pages.mjs` | Formulários, pareceres, snapshots e modelos auxiliares de confronto. | Específico do fluxo; não equivale ao SIM/PRC SISCAN. |
| Símbolo: `calunga-generator.mjs`, `assets.mjs`, `hostile-symbol.mjs` | Carrega catálogo/motor Calunga, cria SIDC/SVG e apresenta símbolos. | Alto risco de licença/conformidade; ver 32 e 33. |
| Acesso/UX: `login.mjs`, `party-entry.mjs`, `tutor-entry.mjs`, `feedback.mjs`, `tutorial.mjs`, `about.mjs`, `button-feedback.mjs` | Sessão, ingresso, feedback e orientação. | Login depende do contrato de backend; UX pode inspirar após revisão. |
| CSS: 11 folhas próprias em `src/` | Estilos globais, viewer/editor, login, painéis e feedback. | Acoplamento a IDs/classes atuais; medir antes de reutilizar. |

## Comunicação e estado

Entradas chamam auxiliares por imports ES Modules; os módulos de tela chamam `fetch` diretamente. `renderer.mjs` resolve ícones via `/api/icons/`; `viewer.mjs` lê `/api/session`, `/api/sources`, `/api/map-state`, manifest, KMZ e endpoints de baseline; `situation-ui.mjs` e painéis falam com `/api/control/*`. A lista de correspondências com métodos e divergências está em [31](31_MAPEAMENTO_FLUXOS_INTERFACE_FRONTEND.md).

Editor salva cenas no `localStorage`; viewer salva preferências e enquadramento; Confronto usa `sessionStorage` para snapshots auxiliares. Não foi encontrado IndexedDB. Persistência oficial e permissões pertencem ao backend.

## Limites do inventário

Os 230 assets foram contados, não individualmente descritos por finalidade. Os 73 arquivos de `src/` foram inventariados por nome; leitura aprofundada se concentrou em entradas, cartografia, import/export, acesso, efeitos e Confronto. Presença de módulo não garante que esteja ligado em página ou funcional no navegador.
