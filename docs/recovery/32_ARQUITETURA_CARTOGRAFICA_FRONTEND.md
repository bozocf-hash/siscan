# 32 — Arquitetura cartográfica do frontend

## Componentes e fluxo de renderização

O viewer e o editor usam Leaflet, carregado pelas páginas e disponível como global `L`. `viewer.mjs` e `app.mjs` inicializam mapas; o `renderer.mjs` cria uma camada SVG própria e projeta coordenadas usando `map.latLngToContainerPoint`/`containerPointToLatLng` (`renderer.mjs:19-53`). O renderer ordena camadas, simplifica geometrias por zoom, desenha pontos/linhas/polígonos e aplica símbolos/estados. Leaflet oferece base/interação; parte do desenho vetorial é controlada por módulos da aplicação.

Bibliotecas vendorizadas: Leaflet e rotate; polygon-clipping; fflate; html-to-image; jsPDF. São arquivos locais em `frontend/vendor/` (inventário em 30). Não foram testados compatibilidade, versão efetivamente carregada nem termos de uso de tiles.

## Dados geográficos e coordenadas

- GeoJSON/KML usam coordenadas `[longitude, latitude]` em graus, em contexto WGS84/EPSG:4326; `workflow.mjs` valida faixas e rejeita CRS diferente salvo reconhecimento de 4326/CRS84 (`workflow.mjs:25-30`).
- Elemento de cena: `id`, vértices com IDs próprios e coordenadas; linha usa vertices; área usa rings; cena guarda nós/camadas com hierarquia, estilos, origem e metadados (`scene.mjs:5-7,35-47,120-128`).
- Conversão UTM WGS84↔UTM, seleção de zona/hemisfério e projeção para zona compartilhada estão em `utm.mjs:1-7,80-120,143-177`. Limites declarados de latitude: -80° a 84°. Exatidão/edge cases não foram verificados.
- `geometry.mjs` atende snap, distância, segmento, limites e união de áreas; `map-grids.mjs` gera grade visual; nenhum recurso equivale a análise ou validação de combate.

## Camadas, seleção e edição

`layer-tree.mjs` opera grupos e ordem/visibilidade de camadas; `scene.mjs` contém funções para mover/organizar nós, mover feição e editar vértices; `modes.mjs` e `app.mjs` controlam modos/ferramentas. A árvore local descreve cenas de trabalho, não o banco de dados. `model.mjs` filtra feições para apresentação por observador e declara expressamente que isso não é controle de acesso (`model.mjs:1-13`).

O mapa seleciona feições e manipula vértices no editor; o viewer aplica estados oficiais e patches a uma cena destinada à visualização. Movimentação e alteração oficial seguem fluxos de backend de efeitos/Confronto, enquanto movimentação do editor permanece em rascunho local. Essas operações não devem ser confundidas.

## Importação, formatos e exportação

`exchange.mjs`, `kml.mjs`, `workflow.mjs` importam GeoJSON/KML; `map-unpack.mjs` delega a descompactação KMZ ao `map-worker.mjs` quando Web Worker está disponível (`map-unpack.mjs:1-10`). `draftFile` caracteriza arquivo ATLANTICADOR como draft, não aprovado/publicado (`workflow.mjs:26`). Exportação inclui KML de camadas/cópia, renderização raster, GeoTIFF georreferenciado e CSV de pontos (`map-export-core.mjs:30-60`; `map-export.mjs`; `point-export.mjs`). O módulo pode tentar baixar recursos do tile layer e seu comportamento depende do browser/rede. Nenhum formato foi aberto, importado ou exportado nesta missão.

## Calunga e símbolos

`calunga-generator.mjs` carrega `/vendor/calunga/catalog.json` e os bundles locais; resolve identidade, modificadores e SIDC, produzindo SVG para símbolo amigável/hostil (`calunga-generator.mjs:5-35`). `symbols.mjs`, `assets.mjs`, `hostile-symbol.mjs`, `viewer-icons.mjs` e `renderer.mjs` integram símbolos ao mapa. O catálogo tem 497 ícones centrais segundo README/JSON. Dados guardados na feição podem conter a especificação `calunga`, SIDC e SVG gerado; isso é evidência de representação, não confirmação de compatibilidade normativa.

README de Calunga descreve origem e adaptação, mas não concede licença. Há avisos de terceiros dentro dos bundles, e dependências vendorizadas possuem avisos distintos. Antes de usar ou redistribuir no SISCAN: determinar titularidade/licença de cada bundle e catálogo; preservar notices; conferir restrições de portal e marcas; avaliar a licença das dependências; confirmar direito de adaptação; obter parecer jurídico; e validar catálogo/simbologia com autoridade competente.

## Limites e avaliação

Confirmado: Leaflet, coordenadas geográficas, formato da cena, renderização SVG, caminho UTM e módulos de import/export estão presentes. Identificado: worker, cache, recursos e Calunga. Não verificado: funcionamento, desempenho, precisão, acessibilidade, offline, atribuição de tiles, licença completa e interoperabilidade real. Componentes reutilizáveis são avaliados em 33; arquitetura proposta em 34.
