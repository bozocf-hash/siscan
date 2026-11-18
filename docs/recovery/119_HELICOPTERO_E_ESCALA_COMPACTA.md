# 119 — Helicóptero e escala compacta

Correção solicitada pelo responsável após 118: helicóptero ilegível e silhuetas grandes.

- Helicóptero redesenhado em perfil lateral, com cabine, cauda, rotor principal horizontal e esquis; substitui o desenho superior de pás sobrepostas.
- Todos os símbolos do mapa: 36 × 28 → **26 × 20 px**. Contorno visual do marcador: 28 px, centralizado na área de interação original de **40 × 38 px**, preservando o ponto geográfico e o clique.
- Catálogo: 112 × 64 → **64 × 38 px**, cartões mais baixos e menos espaçamento. Identificação curta do mapa reduzida de 10 para 9 px; nome completo continua na ficha/título acessível.
- Cores dos partidos, classificações, comandos e dados dos meios preservados. Desenhos continuam ilustrativos por família.

Verificador `node check_map_visuals.mjs` passou; `git diff --check` sem problemas. Inspeção em navegador real confirmou as dez opções em 64 × 38, símbolo do mapa em 26 × 20 e área de clique em 40 × 38. Helicóptero e conjunto examinados em 1280 × 720; console sem erros/avisos. Não foi reexecutada a bateria do backend para esta alteração exclusiva de SVG/CSS. Nenhuma seleção ou plotagem foi aplicada durante a inspeção.

Prévia em nova aba de `http://localhost:61270/atlanticador/editor.html`, preservando as abas anteriores. Evidência fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-silhuetas-compactas-20261117.png`. Banco e originais não modificados; principal não reiniciado.


## Complemento — silhueta militar

A pedido do responsável, o perfil com esquis foi substituído por helicóptero militar utilitário: cabine angular, carenagem de motorização, cauda elevada e trem com rodas. Rótulo do catálogo: **Helicóptero militar**; chave interna `helicopter` e classificação mantidas. Mantidos 26 × 20 px no mapa e 64 × 38 px no catálogo. Perfil ilustrativo, sem identificar modelo exato nem atribuir capacidades à unidade.

Verificador SVG passou; nova inspeção real do catálogo confirmou o desenho e rótulo, sem erros/avisos no console. Evidência: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-helicoptero-militar-20261117.png`.
