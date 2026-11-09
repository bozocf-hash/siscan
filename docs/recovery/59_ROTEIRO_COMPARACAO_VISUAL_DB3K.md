# 59 — Evidências do visualizador e roteiro de comparação DB3K

## Escopo e resultado — 2026-11-09

**Atualização posterior com auxílio do responsável:** o visualizador foi acessado e a seção GENERAL DATA foi examinada. O resultado inicial abaixo descreve a tentativa anterior; os achados posteriores e suas limitações estão no final deste documento.

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

**Classificação:** cinco correspondências numéricas observadas, com rótulos m/kg na apresentação, ainda sem vínculo visual completo ao ID. O cabeçalho da ficha com nome e DBID ficou fora da região visível; a lista superior exibia variantes A/F-117X e o filtro SubType estava em Attack. A descrição inferior trata da família Seahawk. A orientação dada e a resposta do responsável não substituem a inspeção do cabeçalho. Portanto, ainda não se registra uma ficha plenamente identificada nem validação definitiva do mapeamento SQL/apresentação.

A captura pertence à observação da janela via computer-use nesta conversa; não foi exportada como arquivo no repositório. A leitura dos números foi visual, sem OCR nem texto de acessibilidade dos campos. Não houve alteração de código, bancos ou status dos candidatos. Os 580 valores permanecem pendentes no lote.

### Divergência entre descrição e dados gerais

Na mesma tela, a seção textual SPECIFICATIONS informa comprimento de 19.75 m e diâmetro do rotor de 16.35 m; GENERAL DATA informa Length 15,2 m e Wingspan 2,2 m. São valores e rótulos de seções diferentes. Diâmetro do rotor não deve ser equiparado automaticamente a Wingspan, e não foi determinada a causa da diferença de comprimento. A descrição textual inclui referência externa, que não foi consultada nesta etapa. A concordância com valores SQL não comprova exatidão física nem adequação do atributo ao SISCAN.

Próximo passo: observar o cabeçalho #3 / SH-60B Seahawk na mesma ficha e confirmar a continuidade com GENERAL DATA. Depois, ampliar a comparação para outras plataformas e para a versão 498 quando disponível no visualizador. Não substituir valores, unidades ou interpretação técnica com base nesta única observação.
