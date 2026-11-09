# 66 — Unidades e base dos perfis de consumo

## Solicitação e resultado — 2026-11-09

O responsável solicitou unidades nos campos técnicos e a preparação dos dados para futuras curvas de consumo no backend. O levantamento integral de 65 permanece válido. Esta entrega adiciona metadados aos resultados de leitura, sem alterar valores, DB3K, compilação ou dados operacionais.

Contrato `db3k-498-units-01`, implementado em `technical_units.py`: a ficha retorna `measurements` para atributos e parâmetros das associações; o conjunto compilado retorna metadados por nó e `consumption_profiles` por propulsor. A interface aplica os rótulos nos dados gerais, resumos e tabelas, oferece evidências consultáveis e exporta tudo em JSON.

## Evidências e limites

O [manual oficial CMO](https://ftp.matrixgames.com/pub/CommandModernOperations/CMO%20manual%20EBOOK.pdf) consultado tem 425 páginas. A página PDF 91 foi extraída, renderizada e inspecionada visualmente: o painel aéreo apresenta combustível em kg, consumo em kg/min e distância em nm. Não houve nova leitura integral. SHA-256: `afa168367b46f2a82e979c99a014412c4511cf4f137eb5e41c8022ffe9f08736`. O PDF e a imagem de apoio permanecem em `tmp/`, fora do GitHub, sem substituir os arquivos originais.

O manual instalado de 353 páginas é outra fonte, consultada pontualmente por extração nas páginas PDF 80 e 294 nesta etapa. A página 294 usa litros numa regra histórica de bingo. Não foi demonstrado que essa regra descreva `DataFuel.Capacity`; ela não estabelece a unidade SQL. Campo, versão e contexto precisam acompanhar a evidência.

| Campos/contexto | Rótulo exibido | Evidência e limite |
|---|---|---|
| Dimensões de Aircraft, Ship, Submarine e Length/Width terrestre | m · amostra | Comparação assistida em 59, com valores iguais no SQL 498/498a; não aprovação geral |
| Aircraft.WeightEmpty/WeightMax | kg · amostra | Aircraft/3 em 59; limitação amostral |
| MastHeight terrestre, dimensões de Satellite e massas aéreas adicionais | m ou kg · referência | Templates em 58; transformação SQL não demonstrada; MastHeight divergiu na amostra |
| Deslocamentos navais/submarinos | tons · amostra | Rótulo literal de 59; tipo de tonelada não confirmado, sem conversão para t/kg |
| DataFuel.Capacity, Type=2001 (Aviation Fuel) | kg · referência | Manual PDF 91; correspondência SQL proposta, sem validação de todos os usos do tipo |
| DataFuel.Capacity, demais tipos | unidade a confirmar | Não transferir kg/litros a combustível naval, bateria, AIP ou tempo |
| DataPropulsionPerformance.Speed | kn · referência | [Manual: aprendizado por exemplo](https://command.matrixgames.com/manual/04-learning-by-example/); correspondência SQL pendente |
| DataPropulsionPerformance.AltitudeMin/Max e limites de altitude dos sensores | m · referência | [API: Altitude](https://commandlua.github.io/assets/DataTypes.html#Altitude); não comprova unidade/referência vertical de cada coluna SQL |
| Consumption, propulsor Type=2001–2005 | kg/min · referência | Painel aéreo do manual PDF 91; escala SQL, base por motor/conjunto e modificadores pendentes |
| Consumption, demais tipos de propulsão | unidade a confirmar | Não atribuir kg/min a motores navais, baterias ou armas por generalização |
| DataSensor.RangeMax | NM · referência | [API: Emissions](https://commandlua.github.io/assets/Tables.html#Emissions) documenta sensor_maxrange em nm; correspondência à coluna ainda pendente |
| SFCMilitary/SFCAfterburner | unidade a confirmar | Consumo específico, distinto de Consumption; unidade depende do tipo de motor |
| GroundUnit.Area | unidade a confirmar | Contradição dimensional em 58–59; não corrigir para m² por inferência |

NM/nm representam milhas náuticas; kn representa milhas náuticas por hora; m representa metro; kg, quilograma; kg/min, quilograma por minuto. Litros exigem densidade e condições pertinentes para conversão de massa. Nenhuma conversão foi introduzida.

Campos numéricos sem evidência recebem indicação explícita de pendência. IDs, códigos reconhecidos, anos e indicadores conhecidos não recebem unidades físicas; Crew e NumberOfEngines são contagens, sem reinterpretar zeros ou frações. NULL é preservado, e campos textuais nulos não recebem unidades.

## Contrato para o backend

Cada metadado distingue `unit` (unidade SQL confirmada), `candidate_unit`/`display_unit` (evidência de apresentação/referência), `status`, `evidence`, `qualification`, `calculation_ready` e versão. Nesta entrega, `unit` permanece nula e `calculation_ready=false`: não houve comprovação suficiente para aprovação do armazenamento e da semântica operacional. A tela diferencia amostra, referência e pendência.

Cada perfil identifica propulsor e origem, associação direta ou transitiva e pontos com linha fonte, regime, velocidade, faixa, limites e consumo originais, acompanhados dos metadados. Não agrega motores de armas/equipamentos ao consumo da plataforma. Não associa automaticamente um tanque a um propulsor sem comprovação. Faixas alternativas, sinais, zeros e repetições são preservados.

`average_consumption=null` é intencional: a missão não definiu durações. Depois de validar unidades/escala, a média por perfil temporal será `Σ(taxa_i × duração_i) / Σ(duração_i)` para taxas de mesma grandeza e durações na mesma unidade temporal; o consumo total será a soma dos segmentos. A média aritmética das linhas SQL mistura condições alternativas e não representa uma missão.

Antes de alimentar o motor: validar unidades e escala, fluxo por motor ou conjunto, combustível compatível, condições/faixas e efeito de carga/configuração. Interpolação exige um modelo explícito e versionado, sem extrapolar cobertura ou reproduzir automaticamente o algoritmo Command. Reservas seguem decisões SISCAN.

Não foram implementados curva, interpolação, média operacional ou baixa de estoque: a solicitação prepara a base para essas funcionalidades posteriores. Não houve promoção de atributos técnicos ou mudança da alocação por partido.

## Verificação

Os onze verificadores `check_*.py` passaram, incluindo `check_technical_units.py`, cobrindo escopo da evidência, separação de combustíveis/baterias/tempo, SFC versus fluxo, NULL/zero, texto nulo, contagem de motores, alcance e perfis diretos/transitivos. Compilação e autorização anteriores continuam verificadas.

Edge isolado conferiu rótulos, consumo por regime, fontes, exportação, categorias, permissões e tela de 390 px. Aircraft/3 tem propulsor 50 com seis pontos diretos, mantendo Consumption=7.75. Ship/3 mantém Capacity=15000 no combustível 196 sem receber kg por generalização. As sete colunas de desempenho são visíveis no desktop; a tela estreita tem rolagem interna.

O relatório derivado `data/db3k-units-evidence-08.json` registra contrato, hashes e quatro fichas amostrais com metadados/perfis. Original e compilação são abertos somente para leitura e mantêm os hashes de 65. Não foi introduzido SQL de escrita nos endpoints.
