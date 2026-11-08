# 19 — Frontend do ATLANTICADOR

## Organização e entradas

Frontend sob `frontend/`, com páginas HTML e módulos ES puros, sem framework/bundler declarado no `package.json`.

| Página | Entrada e função identificada |
|---|---|
| `index.html`, `login.html` | Entrada e login |
| `azul.html`, `vermelho.html` | Fluxos de partido/ingresso, com `login.mjs` e `party-entry.mjs` |
| `tutores.html` | Ingresso de tutores, com `login.mjs` e `tutor-entry.mjs` |
| `viewer.html` | Visualizador cartográfico principal, `src/viewer.mjs` |
| `editor.html` | Editor local de cenas, `src/app.mjs` |
| `direx.html` | Página da DIREx; markup sem script module declarado diretamente |

`frontend/src/` tem 73 arquivos. Também há assets de login/estado/tutorial e bibliotecas locais em `frontend/vendor/`. UI é servida pelo mesmo processo HTTP Python; páginas de visualização fazem chamadas JSON `/api/...` para estado, fontes, login, efeitos e confrontos.

## Módulos funcionais

| Área | Arquivos/módulos representativos | Capacidades identificadas |
|---|---|---|
| Cena/camadas | `model.mjs`, `scene.mjs`, `layer-tree.mjs`, `workflow.mjs` | Modelo de cena local, árvore de grupos/camadas, edição, validação e diffs |
| Cartografia/render | `viewer.mjs`, `renderer.mjs`, `render-geometry.mjs`, `render-order.mjs`, `cartography.mjs`, `utm.mjs`, `map-grids.mjs`, `geometry.mjs` | Mapa Leaflet, renderização SVG, geometria, grade e conversão UTM |
| Importação/troca | `map-import.mjs`, `exchange.mjs`, `kml.mjs`, `map-unpack.mjs`, `map-worker.mjs` | Leitura local KML/KMZ/GeoJSON e rascunhos ATLANTICADOR; validação e limites de arquivo |
| Exportação | `map-export.mjs`, `map-export-core.mjs`, `point-export.mjs` | Exportação cartográfica/porção de mapa, formatos de imagem/georreferenciados e CSV de pontos |
| Fontes/situação | `source-view.mjs`, `situation-ui.mjs`, `official-scene.mjs`, `official-additions.mjs`, `baseline-patch.mjs` | Consumo de fontes/snapshots oficiais e renderização de efeitos aplicados |
| Login/perfis | `login.mjs`, `party-entry.mjs`, `tutor-entry.mjs`, `access-card.css` | Login e fluxo de ingresso por categoria/partido |
| Simbologia | `symbols.mjs`, `assets.mjs`, `calunga-generator.mjs`, `hostile-symbol.mjs`, `viewer-icons.mjs` | SVG/ícones, catálogo Calunga, variantes de símbolo e apresentação |
| Efeitos/histórico | `effects-panel.mjs`, `effect-history.mjs`, `effect-live-edit.mjs`, `effect-map-tools.mjs`, `unit-conditions.mjs` | UI de registros/efeitos, edição e visualização de histórico/estado |
| Confrontos | `confrontations.mjs`, `confrontation-models.mjs`, `confrontation-game.mjs` | UI de fluxo, modelos de apoio e comparação abstrata |
| UX auxiliar | `feedback.mjs`, `tutorial.mjs`, `about.mjs`, `button-feedback.mjs` | Mensagens, tutorial e informações |

## Edição e comunicação

`app.mjs` importa editor, modelo, cena, geometria, renderizador, camadas, modos e workflow. O editor trabalha em cenas locais; `scene.mjs` declara que cenas de trabalho não mutam cenas publicadas. `map-import.mjs` chama `/api/control/status` para verificar permissão, mas informa que a importação cartográfica é rascunho local sem publicação automática. Isso não equivale a editor de cenário SISCAN.

`viewer.mjs` concentra montagem de mapa e instala painéis funcionais (`installMapImport`, `installConfrontations`, `installSituationUI` e outros). Chamadas `fetch` dirigem-se a endpoints same-origin; não foi encontrada camada cliente compartilhada com um SDK de integração externa. Mudanças de estado oficial dependem de rotas/controladores do backend, não apenas do estado local da cena.

## Cartografia, formatos e dependências

HTML do viewer/editor carrega Leaflet e bibliotecas locais em `vendor/`: Leaflet, rotate, polygon-clipping, fflate, html-to-image e jsPDF. `exchange.mjs` identifica importação local KML/KMZ e GeoJSON, com suporte a arquivo de rascunho; há funções de saída KML/KMZ e CSV. `map-export.mjs` inclui renderização/exportação de mapa e `map-export-core.mjs` inclui codificação GeoTIFF. A disponibilidade de cada combinação de formato/ambiente foi inferida de código, sem executar navegador.

Tiles de mapa podem ser obtidos externamente; exportação de imagem tenta carregar recursos do mapa-base. Fonte/licença de camadas e comportamento offline dependem de configurações/documentos específicos, não verificados operacionalmente nesta missão.

## Simbologia e componentes com nomes SISCAN

`calunga-generator.mjs` carrega catálogo Calunga local e monta identidade/nomeação e SIDC a partir de parâmetros. `symbols.mjs`/`assets.mjs` lidam com símbolos SVG. Esse recurso é candidato conceitual ao módulo SYM, mas nomenclatura, escalões e perfil de dados devem ser compatibilizados com decisões SISCAN; existência não significa reutilização ou equivalência.

`confrontation-models.mjs` exporta modelos DAMEPLAN, CombaTer, SBE adaptado e convenção ATLANTICADOR; `confrontations.mjs` apresenta esses cálculos no fluxo de confrontos. Trata-se de código de apoio do ATLANTICADOR, em contexto distinto. Não equivale ao PRC didático decidido para SISCAN nem comprova motor de combate naval. `confrontation-game.mjs` é um componente separado de comparação abstrata conforme documentação 03.

## Segurança e limite

`model.mjs::availableFeatures` controla filtragem de apresentação no cliente e declara que essas funções não são controle de acesso; a autorização efetiva está no backend. Não considerar ocultação de elementos em frontend como isolamento suficiente. Código foi lido estaticamente, sem validação visual do aplicativo, execução ou testes; presença de componente não comprova funcionamento.
