# 118 — Redesenho das silhuetas navais e aéreas

Solicitação: corrigir a qualidade visual das silhuetas após a entrega 117.

## Critério visual e escopo

Perfis laterais navais, vista superior de aeronave e helicóptero; reconhecimento pela forma externa em tamanho compacto. Casco, superestrutura, mastros e armamento aparente distinguem os perfis; linhas secundárias ajudam a leitura ampliada no catálogo. Paleta dos partidos e tokens do ATLANTICADOR preservados. SVG nativo, sem imagens remotas, fontes ou dependências adicionais.

Redesenhadas as nove famílias conhecidas: fragata, corveta, contratorpedeiro, torpedeiro, navio de apoio, porta-aviões, submarino, aeronave e helicóptero. O marcador desconhecido continua neutro quanto à categoria. São ilustrações por família, não desenhos certificados de classe/modelo real. Classificação por nome/categoria e preferências existentes não foram alteradas.

No mapa, mantém-se 36 × 28 px, sem ampliar a área ocupada pelos meios. Catálogo apresenta o desenho maior, nome e botão acessível. Nenhuma seleção foi aplicada ao meio durante a inspeção; nenhuma posição, composição, estado, combustível ou munição foi alterada.

## Validação

`node check_map_visuals.mjs`: passou, incluindo famílias, classificação conservadora, desenhos distintos, cores AZUL/VERMELHO, fallback seguro para chaves desconhecidas/injetadas e duas camadas de desenho por família. `node --test check_map_presentation.mjs`: dois testes passaram. Sintaxe do bridge e revisão do diff verificadas. Não se declara reexecução da bateria completa do backend para esta alteração de arte vetorial.

Inspeção real do catálogo e marcador na prévia 61270, em nova aba, preservando a aba que o responsável estava utilizando. Dez opções renderizadas, dois paths por SVG, sem erros/avisos no console. Em viewport 320 × 740, página sem transbordamento horizontal, painel de 296 px e cartões sem overflow; mapa continuou com símbolo de 36 × 28 px. Conjunto completo examinado também em 1280 × 900; override removido ao terminar.

Evidência local fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-silhuetas-20261117.png`.

## Continuidade

A aprovação estética final cabe ao responsável. Associação a perfis exatos de cada classe real depende de arte e identificação específicas; esta entrega não transforma a ilustração genérica em evidência técnica do catálogo. Calunga, fluxo de julgamento e contratos do motor permanecem como em 117. Banco principal e originais preservados.
