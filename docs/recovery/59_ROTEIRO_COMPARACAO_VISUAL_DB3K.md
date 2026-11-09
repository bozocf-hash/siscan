# 59 — Evidências do visualizador e roteiro de comparação DB3K

## Escopo e resultado — 2026-11-09

**Resultado atual com auxílio do responsável:** quatro fichas identificadas e examinadas em DB3K_498a: Aircraft/3 SH-60B Seahawk, Ship/3 D 10 Almirante Brown, Submarine/3 PLARB-667A Yankee I [Navaga] e GroundUnit/3 AAVP-7A1. Os 18 valores inicialmente preparados foram examinados: 17 correspondências numéricas e uma diferença de apresentação (MastHeight: SQL 3.26; ficha 3 m). Area aparece com rótulo m, sem unidade dimensional validada. Não houve aprovação de atributos. O resultado inicial abaixo descreve a tentativa anterior; os achados posteriores e suas limitações estão no final deste documento.

Foi observada a janela do jogo **Command v1.05 — Build 1307**, além do painel inicial com o mesmo build. Isso complementa a confirmação anterior, restrita ao lançador (58). Nenhuma ficha de plataforma foi aberta no jogo; nenhuma unidade SQL foi validada e nenhum dos 580 valores técnicos foi promovido.

A primeira tentativa de dispensar o painel inicial ficou sem resultado por expiração da revisão automática de permissão. Após recuperação da janela, foram tentados o fechamento pelo X, Escape e acesso à seleção de cenário existente. Não houve mudança observável do painel nas capturas de verificação. A captura da janela principal também apresentou conteúdo de outro aplicativo em uma consulta; recuperou-se então a janela secundária Command, que mostrou o painel inicial. Não se atribui causa a esses comportamentos nem se afirma que os comandos tenham sido processados pelo jogo. A interação foi encerrada sem carregar, editar ou salvar cenário por ação confirmada.

## Manual digital consultado

Fonte: `C:\Program Files (x86)\Matrix Games\Command Modern Operations\Manuals\CMO manual EBOOK.pdf`, 353 páginas, SHA-256 `da3f75ec537b2a64e77c432324c02410dd2c12f6d999e4813b96ab7c04df51c1`.

Uma busca textual por termos do visualizador localizou a seção relevante. Foram lidos os textos das páginas PDF 155–158 e inspecionada visualmente a página PDF 155, renderizada com Poppler. Nesta seção, a numeração impressa coincide com a numeração PDF. Não houve OCR, leitura integral deste novo manual ou inspeção visual das demais páginas nesta etapa. O PDF original foi preservado; a renderização é derivada temporária local.

| Origem | Conteúdo recuperado | Limite |
|---|---|---|
| Seção 6.3.4, p. 155 | O visualizador mostra o banco selecionado; escolha de tipo e plataforma, filtros de nome, país e condição real/hipotética | A descrição exemplifica Build 478; não confirma o banco ativo na instalação |
| Figura da p. 155 | Cabeçalho do visualizador identifica Build 473; ficha #3313 RF-111C Aardvark (Australia - 1980); dimensões com m e massas com kg | Figura histórica, banco diferente de 498; não comprova vínculo nem conversões das colunas SQL atuais |
| P. 156 | Filtros podem ser combinados e reiniciados; seção de armas lista plataformas portadoras | Procedimento documental; não executado no visualizador nesta etapa |
| P. 157 | Continuação da seção, com conceitos OODA e agilidade | Não adota esses modelos como requisitos nem como escalas SISCAN |
| Seção 6.3.5, p. 158 | Browse Scenario Platforms restringe a consulta às plataformas usadas no cenário e permite filtro por lado | Distinguir catálogo geral de meios presentes no exercício |

A divergência Build 478 no texto versus Build 473 na figura demonstra por que a versão deve ser registrada em cada comparação. Nenhuma dessas versões substitui a identificação do arquivo DB3K_498 efetivamente usado como fonte.

## Amostra preparada em modo somente leitura

Seleção: menor ID numérico entre os 20 candidatos de cada uma das quatro tabelas do lote local. Os quatro registros selecionados possuem ID 3, mas são identidades distintas: **tabela + ID + hash da fonte**. O nome não identifica uma unidade física SISCAN.

Fonte SQL: `C:\Users\bozoc\Documents\siscan\DB3K_498.db3`, SHA-256 `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`. A seleção consultou o arquivo local de candidatos e o banco original com conexão SQLite `mode=ro`.

| Tabela / ID | Nome literal | Valores SQL brutos a comparar | Observação na ficha |
|---|---|---|---|
| DataShip / 3 | D 10 Almirante Brown [Meko 360H2] | Length=125.9; Beam=15.0; Draft=4.3; Height=0.0 | Pendente |
| DataAircraft / 3 | SH-60B Seahawk | Length=15.2; Span=2.2; Height=5.2; WeightEmpty=6190; WeightMax=9927 | Pendente |
| DataSubmarine / 3 | PLARB-667A Yankee I [Navaga] | Length=128.0; Beam=11.7; Draft=7.9; Height=0.0; MaxDepth=-320 | Pendente |
| DataGroundUnit / 3 | AAVP-7A1 | Length=7.94; Width=3.27; MastHeight=3.26; Area=25.96 | Pendente |

São 18 valores preparados para comparação, não 18 valores confirmados. Os 580 valores técnicos do lote continuam pendentes. Zero permanece zero sem interpretação; o sinal negativo de MaxDepth é preservado, sem aplicar valor absoluto. Area permanece sem unidade confirmada; o rótulo m do template terrestre não autoriza m² nem uma correção do banco. Não confundir Width terrestre com Beam naval ou Span aeronáutico.

## Procedimento de retomada e critérios de registro

1. Obter janela estável do jogo e acessar Game / Database Viewer, conforme a organização do capítulo 6.3. Registrar versão do jogo e identificação do banco exibida no visualizador. Não presumir que o banco ativo seja 498 por ele existir no disco.
2. Selecionar tipo e nome, removendo filtros de país/condição que possam ocultar o registro. Confirmar tabela/tipo, ID e nome da ficha antes de comparar números.
3. Para cada campo, registrar valor SQL bruto, rótulo da ficha, valor apresentado, unidade apresentada, arredondamento ou omissão observável e localização da evidência. Anotar explicitamente campos não exibidos ou ilegíveis.
4. Distinguir correspondência numérica amostral de comprovação do mapeamento e da conversão. Para WeightEmpty/WeightMax, exigir evidência do vínculo com EmptyWeight/MaxWeight; nomes parecidos não bastam. Ausência de Height ou zero na ficha não prova o significado de zero no SQL.
5. Ampliar a amostra para outros valores, NULL e variantes somente após uma primeira comparação válida. Manter unidades/domínios pendentes onde a evidência não for suficiente.
6. Submeter eventual proposta de uso de atributos ao responsável, separada da aprovação já concedida às 80 referências de identificação. Não criar unidades físicas nem disponibilizar atributos automaticamente.

## Relação com o SISCAN

Referências conceituais: separar catálogo de plataformas e composição do exercício; filtrar consultas; preservar versão/origem; controlar visibilidade por partido. O manual não altera a regra aprovada: o instrutor disponibiliza meios para AZUL ou VERMELHO, e os alunos do partido acessam esses meios. A exposição do catálogo de referência não equivale à alocação de meios.

## Observação assistida do visualizador — 2026-11-09

O responsável abriu o visualizador e navegou na ficha solicitada. Foram observados sucessivamente os títulos CWDB_498 e, após orientação para troca de banco, DB3K_498a. CWDB e DB3K são fontes distintas; o número 498 isolado não as identifica. A captura com os valores abaixo mostra explicitamente **Database Viewer (DB3K_498a)** e Type Aircraft.

O arquivo instalado `DB\DB3K_498a.db3` tem SHA-256 `866f4cded2e03ad350bab5ed67fef16f74da06c849bcbaf886839b273906a7b4`, diferente do 498 original. Consultas SQLite somente leitura confirmaram que DataAircraft/3 se chama SH-60B Seahawk nos dois arquivos e que os cinco valores abaixo são iguais entre eles. Isso não demonstra igualdade das versões completas nem prova, isoladamente, qual arquivo o programa carregou; a evidência da versão ativa é o título da interface.

| Campo SQL comparado em DataAircraft/3 | Valor bruto no 498 | Valor bruto no 498a instalado | Rótulo e valor visíveis em GENERAL DATA |
|---|---|---|---|
| Length | 15.2 | 15.2 | Length: 15,2 m |
| Span | 2.2 | 2.2 | Wingspan: 2,2 m |
| Height | 5.2 | 5.2 | Height: 5,2 m |
| WeightEmpty | 6190 | 6190 | Empty Weight: 6190 kg |
| WeightMax | 9927 | 9927 | Max Weight: 9927 kg |

**Classificação na primeira leitura:** cinco correspondências numéricas observadas, com rótulos m/kg na apresentação, então sem vínculo visual completo ao ID. O cabeçalho ficou fora da região visível; a lista superior exibia variantes A/F-117X e o filtro SubType estava em Attack. Essa lacuna de identificação foi resolvida pela captura posterior descrita a seguir; a primeira leitura, isoladamente, não permitia identificar a ficha.

A captura pertence à observação da janela via computer-use nesta conversa; não foi exportada como arquivo no repositório. A leitura dos números foi visual, sem OCR nem texto de acessibilidade dos campos. Não houve alteração de código, bancos ou status dos candidatos. Os 580 valores permanecem pendentes no lote.

### Divergência entre descrição e dados gerais

Na mesma tela, a seção textual SPECIFICATIONS informa comprimento de 19.75 m e diâmetro do rotor de 16.35 m; GENERAL DATA informa Length 15,2 m e Wingspan 2,2 m. São valores e rótulos de seções diferentes. Diâmetro do rotor não deve ser equiparado automaticamente a Wingspan, e não foi determinada a causa da diferença de comprimento. A descrição textual inclui referência externa, que não foi consultada nesta etapa. A concordância com valores SQL não comprova exatidão física nem adequação do atributo ao SISCAN.

### Confirmação posterior do cabeçalho

Após ajuste do zoom pelo responsável, foi observado diretamente **#3 - SH-60B Seahawk (United States - 1991)**, na mesma tela que o título Database Viewer (DB3K_498a), Type Aircraft e GENERAL DATA. Nessa captura são legíveis Length 15,2 m, Wingspan 2,2 m e Height 5,2 m; a captura secundária também mostra Empty Weight 6190 kg. Max Weight 9927 kg foi lido na captura anterior; não se afirma que os cinco valores estejam todos visíveis nesta última imagem. O vínculo entre cabeçalho e dimensões agora é direto, com continuidade da ficha nas observações assistidas.

**Resultado consolidado:** uma ficha identificada no visualizador 498a, cinco correspondências numéricas com os registros SQL Aircraft/3 em 498 e 498a, três outras fichas da amostra ainda não examinadas. Isso constitui evidência amostral da apresentação, sem comprovar o mecanismo de conversão, todos os registros do banco ou a exatidão física dos valores. O filtro/lista superior permanece diferente da ficha exibida; não utilizá-lo como substituto do cabeçalho para identificar uma plataforma.

Naquele estágio, a próxima ficha era Ship/3; o exame realizado em seguida está registrado abaixo. Continua necessária a ampliação para outras plataformas e para a versão 498 quando disponível no visualizador. Os 580 valores técnicos permanecem pendentes de aprovação para uso no SISCAN.

## Observação assistida naval — 2026-11-09

Foi observado o título Database Viewer (DB3K_498a), Type Ship e o cabeçalho **#3 - D 10 Almirante Brown [Meko 360H2] (Argentina - 1984)** junto a GENERAL DATA. A leitura foi visual, sem OCR; a imagem permaneceu na conversa, sem exportação para o repositório. Os valores SQL foram consultados novamente em modo somente leitura nos arquivos 498 original e 498a instalado.

| Campo DataShip/3 | SQL 498 | SQL 498a | Apresentação observada | Resultado |
|---|---|---|---|---|
| Length | 125.9 | 125.9 | Length: 125,9 m | Correspondência numérica amostral |
| Beam | 15.0 | 15.0 | Beam: 15 m | Correspondência, sem casa decimal exibida |
| Draft | 4.3 | 4.3 | Draft: 4,3 m | Correspondência numérica amostral |
| Height | 0.0 | 0.0 | Height: 0 m | Zero exibido; significado técnico não determinado |
| DisplacementEmpty | 0 | 0 | Empty Displacement: - | Zero SQL coincide com omissão por traço nesta ficha; não generalizar a regra |
| DisplacementStandard | 2900 | 2900 | Standard Displacement: 2900 tons | Correspondência numérica; tons é rótulo literal, sem confirmar tipo de tonelada |
| DisplacementFull | 3360 | 3360 | Full Displacement com rótulo tons; algarismos sem leitura segura nesta escala | Pendente de leitura ampliada; não registrar igualdade ou divergência numérica |
| Crew | 200 | 200 | Crew: 200 | Correspondência numérica; não determina composição por função |

Os quatro campos dimensionais completam a comparação naval da amostra inicial: Aircraft 5 + Ship 4 = **9 de 18 valores com correspondência numérica observada**, em duas fichas identificadas no visualizador 498a. DisplacementEmpty, DisplacementStandard e Crew são observações adicionais, fora dos 18 valores inicialmente selecionados; DisplacementFull permanece sem leitura visual segura. O banco 498a não substitui o 498 como fonte e não houve execução do visualizador com a versão 498 confirmada no título.

O tratamento diferente de Height=0 e DisplacementEmpty=0 mostra que não existe base nesta amostra para uma regra universal de zero. O rótulo tons não autoriza converter automaticamente para tonelada métrica, tonelada longa ou outra unidade. Os 580 valores técnicos continuam pendentes de aprovação, inclusive os que receberam evidência visual amostral.

Próxima ficha preparada: Submarine / ID 3, PLARB-667A Yankee I [Navaga]. Comparar Length, Beam, Draft, Height e MaxDepth, preservando o sinal de MaxDepth=-320 e registrando o que a interface efetivamente apresenta.

## Observação assistida do submarino — 2026-11-09

O responsável abriu a ficha seguinte. Foram observados Database Viewer (DB3K_498a), Type Submarine e o cabeçalho **#3 - PLARB-667A Yankee I [Navaga] (Russia [1992-] - 1992)**, junto a GENERAL DATA. Os dados SQL abaixo foram consultados novamente nos arquivos 498 original e 498a instalado, por conexão SQLite somente leitura. A leitura da tela foi visual, sem OCR; as capturas permanecem na conversa, sem exportação para o repositório.

| Campo DataSubmarine/3 | SQL 498 | SQL 498a | Apresentação observada | Resultado |
|---|---|---|---|---|
| Length | 128.0 | 128.0 | Length: 128 m | Correspondência numérica, sem casa decimal exibida |
| Beam | 11.7 | 11.7 | Beam: 11,7 m | Correspondência numérica amostral |
| Draft | 7.9 | 7.9 | Draft: 7,9 m | Correspondência numérica amostral |
| Height | 0.0 | 0.0 | Height: 0 m | Zero exibido; significado técnico não determinado |
| MaxDepth | -320 | -320 | Max Depth: -320 m | Sinal negativo preservado na apresentação |
| DisplacementEmpty | 0 | 0 | Empty Displacement: - | Traço na apresentação, sem concluir significado do zero |
| DisplacementStandard | 7770 | 7770 | Standard Displacement: 7770 tons | Correspondência numérica; tipo de tonelada não confirmado |
| DisplacementFull | 10020 | 10020 | Full Displacement: 10020 tons | Correspondência numérica; tipo de tonelada não confirmado |
| Crew | 120 | 120 | Crew: 120 | Correspondência numérica; composição por função não determinada |

**Resultado consolidado:** três fichas identificadas, **14 de 18 valores inicialmente preparados** com correspondência numérica observada no visualizador 498a: Aircraft 5, Ship 4 e Submarine 5. As observações adicionais de deslocamento/tripulação não entram nesse denominador. Não foi determinada uma regra universal de sinal, unidade SQL, zero ou NULL. Em particular, não se aplica valor absoluto a MaxDepth nem se usa o número como profundidade de operação autorizada; observou-se apenas o campo e sua apresentação.

Os 580 valores técnicos continuam pendentes de aprovação para uso. Não houve alteração de código, bancos ou status dos candidatos. GroundUnit/3 AAVP-7A1 é a última ficha da amostra inicial; comparar Length, Width, MastHeight e Area, com atenção ao rótulo dimensional de Area. A leitura ampliada de Full Displacement do navio permanece pendente.

## Observação assistida terrestre e fechamento da amostra — 2026-11-09

O responsável informou que a busca direta por ID 3 não abriu o item e que encontrou AAVP-7A1 pelo nome; em seguida informou que o cabeçalho mostrava 3. A captura confirmou diretamente **#3 - AAVP-7A1 (United States - 0)**, Type Ground Unit e Database Viewer (DB3K_498a). Em outra captura, após rolagem pelo responsável, foram lidos os quatro campos de GENERAL DATA. Não se atribui causa ao comportamento da busca nem significado cronológico ao zero do cabeçalho.

Consultas SQL somente leitura aos arquivos 498 original e 498a instalado confirmaram os valores abaixo e localizaram dois registros homônimos AAVP-7A1, IDs 3 e 377, em ambos os bancos. A identificação usada é o cabeçalho #3, não apenas o nome ou a igualdade dos valores. Os hashes foram recalculados e permaneceram iguais aos registrados: 498 `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`; 498a `866f4cded2e03ad350bab5ed67fef16f74da06c849bcbaf886839b273906a7b4`.

| Campo DataGroundUnit/3 | SQL 498 | SQL 498a | Apresentação observada | Resultado |
|---|---|---|---|---|
| Length | 7.94 | 7.94 | Length: 7,94 m | Correspondência numérica amostral |
| Width | 3.27 | 3.27 | Width: 3,27 m | Correspondência numérica amostral |
| MastHeight | 3.26 | 3.26 | Mast Height: 3 m | Diferença de apresentação; causa não determinada |
| Area | 25.96 | 25.96 | Area: 25,96 m | Correspondência numérica; rótulo dimensional requer avaliação |

O template GroundUnit.html contém `<%MastHeight%> m` na linha 34 e `<%Area%> m` na linha 70, conferidos novamente. O template não demonstra por que 3.26 é apresentado como 3. Arredondamento, truncamento ou outra transformação são hipóteses não verificadas; não se modifica o valor original nem se generaliza uma regra de conversão.

Area é mostrado literalmente com m, assim como no template. Não foi confirmado se o domínio SQL é área em m², outra medida ou um campo com apresentação inadequada. A tela também contém um campo distinto Cargo Capacity / Area com rótulo sq m; ele não comprova a unidade de DataGroundUnit.Area e não foi incluído na comparação. Não substituir m por m² por inferência.

### Resultado consolidado da amostra inicial

| Tabela / ID | Valores preparados examinados | Correspondências numéricas | Diferenças numéricas |
|---|---:|---:|---:|
| DataAircraft / 3 | 5 | 5 | 0 |
| DataShip / 3 | 4 | 4 | 0 |
| DataSubmarine / 3 | 5 | 5 | 0 |
| DataGroundUnit / 3 | 4 | 3 | 1 |
| Total | 18 | 17 | 1 |

São quatro fichas identificadas no visualizador **498a**, não uma inspeção de todo o catálogo nem execução confirmada com o banco 498. Os cinco/quatro valores SQL preparados por tabela foram consultados nos dois arquivos, preservando a distinção entre eles. A leitura da tela foi visual, sem OCR; as capturas permanecem nesta conversa e não foram exportadas para o repositório. Nenhum código, banco, status de candidato ou aprovação foi alterado.

A comparação dos 18 valores está documentada; permanecem pendentes a causa da diferença MastHeight, a unidade/domínio de Area, os significados de zero e NULL, o tipo de tonelada, a divergência entre descrição e dados gerais da aeronave e a leitura ampliada do Full Displacement naval adicional à amostra. A evidência amostral não aprova uso de atributos: os 580 valores técnicos continuam pendentes de aprovação. A ampliação deve priorizar essas divergências e novos registros, sem copiar valores de apresentação para substituir o SQL.
