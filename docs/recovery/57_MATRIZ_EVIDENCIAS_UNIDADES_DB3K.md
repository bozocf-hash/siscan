# 57 — Evidências documentais de unidades e significado dos registros DB3K

## Resultado e alcance

Consulta documental em 08/11/2026. Foram encontradas unidades explícitas nos formulários públicos de entrada de dados da equipe do banco Command. Esses formulários são evidência primária do processo de solicitação, mas não são um dicionário das colunas SQLite da versão 498. As correspondências abaixo são propostas, não validações SQL ou aprovações de atributos.

Uma inspeção posterior encontrou a instalação local do CMO e templates de apresentação junto de um DB3K_498 com o mesmo hash da fonte analisada. As evidências adicionais e a discrepância do rótulo Area estão em [58](58_FONTES_LOCAIS_CMO_E_TEMPLATES.md). Elas não alteram automaticamente o estado pendente dos campos.

O [repositório público da equipe do banco](https://github.com/PygmalionOfCyprus/cmo-db-requests) descreve seu papel como rastreador de solicitações e problemas do CMO. A existência de um formulário não comprova que uma solicitação tenha sido aceita nem que seus valores tenham entrado no banco fornecido.

## Matriz de correspondências propostas

| Tabela/campos SQL da amostra | Evidência no formulário público | Unidade candidata | Situação |
|---|---|---|---|
| DataShip.Length, Beam, Draft | Campos dimensionais explicitamente rotulados com unidade | m | Correspondência nominal proposta; confirmar armazenamento e semântica na versão 498 |
| DataShip.DisplacementStandard, DisplacementFull, DisplacementEmpty | Três condições de deslocamento distinguidas | t | Confirmar equivalência das condições e convenção de tonelada usada |
| DataAircraft.Length, Height | Campos dimensionais explicitamente rotulados | m | Correspondência nominal proposta |
| DataAircraft.Span | Campo de envergadura | m | Além da unidade, confirmar se Span representa a mesma medida, inclusive variantes/configurações |
| DataAircraft.WeightEmpty | Campo de massa vazia | kg | Confirmar definição de massa vazia e equivalência com a coluna |
| DataAircraft.WeightMax | Campo de massa máxima de decolagem | kg | Confirmar que WeightMax equivale a MTOW e não a outro limite |
| DataSubmarine.Length, Beam, Draft | Campos dimensionais explicitamente rotulados | m | Correspondência nominal proposta |
| DataSubmarine.DisplacementStandard, DisplacementEmpty | Condições de deslocamento distinguidas | t | Confirmar condições e convenção usada |
| DataSubmarine.MaxDepth | Campo de profundidade máxima explicitamente rotulado | m | Confirmar definição do limite, aplicabilidade e tratamento de zero |
| DataSubmarine.DisplacementFull | Formulário distingue deslocamento submerso | Não atribuída | Não equiparar Full a submerso apenas pela posição ou semelhança do nome |
| DataShip.Height; DataSubmarine.Height; Crew das três tabelas | Sem vínculo SQL direto suficiente nas páginas consultadas | Não atribuída | Requer fonte adicional e definição de domínio |
| DataGroundUnit.Area, Crew, Length, Mass, MastHeight, Width | Nenhum formulário terrestre correspondente foi localizado neste recorte | Não atribuída | Requer fonte específica; não transferir automaticamente convenções navais/aéreas |

Fontes da matriz: [formulário naval](https://github.com/PygmalionOfCyprus/cmo-db-requests/blob/main/.github/ISSUE_TEMPLATE/14_NEW-SHIP.yml), [formulário de aeronaves](https://github.com/PygmalionOfCyprus/cmo-db-requests/blob/main/.github/ISSUE_TEMPLATE/11_NEW-AIRCRAFT.yml) e [formulário de submarinos](https://github.com/PygmalionOfCyprus/cmo-db-requests/blob/main/.github/ISSUE_TEMPLATE/15_NEW-SUBMARINE.yml). As URLs apontam para a branch pública main; mudanças posteriores devem ser reavaliadas.

Na amostra, 17 pares tabela/campo têm correspondências propostas com unidades documentadas nos formulários, abrangendo 340 valores literais. Os outros 12 pares abrangem 240 valores sem correspondência suficiente neste recorte. **Nenhum dos 580 valores foi promovido a validado por essa contagem.** Zero/NULL e campos não aplicáveis permanecem sem interpretação.

## Modelo, configuração e unidade individual

Os formulários naval e submarino orientam pedidos de classes usando o exemplar que lhes dá nome e admitem pedidos separados para variantes. Portanto, um nome semelhante a um navio individual no catálogo não demonstra, por si, que cada linha SQL representa exclusivamente uma unidade física. Essa evidência reforça a separação SISCAN entre referência de origem e identidade individual; o mapeamento definitivo continua pendente.

## API não equivale ao esquema de armazenamento

A [documentação de tipos da API Lua](https://commandlua.github.io/assets/DataTypes.html#Altitude) documenta altitude em metros na leitura da API. Os [wrappers](https://commandlua.github.io/assets/Wrappers.html) distinguem identificador de banco e GUID da unidade e documentam unidades próprias para determinados objetos de carga. Esses contratos não provam a unidade de uma coluna SQL homônima. Não transportar convenções da API para o arquivo DB3K sem demonstrar a correspondência.

## Evidência adicional necessária

Para validar um par tabela/campo, obter dicionário/especificação do esquema aplicável à versão 498 ou outra evidência direta que conecte a coluna à grandeza e unidade. Comparações com o visualizador do CMO precisam usar o mesmo DBID e versão, registrar a medida exibida e verificar possíveis conversões de apresentação. Comparar números plausíveis isolados não basta.

Registrar também definição da grandeza, condições de medição, domínio permitido, significado de zero/NULL, fonte e escopo de aprovação pelo responsável. Até essa resolução, os campos continuam com unidade nula e estado pendente; nenhuma conversão ou cálculo foi introduzido no protótipo.
