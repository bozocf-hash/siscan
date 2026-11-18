# 127 — Comprovação de unidades, escalas e condições de combustível

**2026-11-18 · Comprovação amostral e diagnóstico entregues; homologação física global pendente.** Continuidade autorizada após 126; novas solicitações de aprovação da skill dispensadas pelo responsável. Essa dispensa não homologa unidades por inferência. Originais e estado operacional preservados.

## Método e escopo

Separar: definição documental da grandeza/unidade; correspondência numérica entre fonte identificada e SQL; condição de configuração/regime/faixa/base da taxa; aprovação para uma finalidade; saldo atual da instância. Comparar valores originais sem substituí-los por números mais recentes encontrados na internet. Converter somente unidades explicitamente identificadas, com fator de referência e sem conversão massa↔volume por densidade presumida.

### Evidências de partida novas

- [Planilha de propulsão publicada pelo Command](https://www.warfaresims.com/WarSimsWP/wp-content/uploads/2014/07/F-22-Engine-Stats.jpg), vinculada ao [Mega-FAQ oficial](https://command.matrixgames.com/?page_id=2920): IDs de propulsor, número de motores e colunas de altitude em ft/m, velocidade em kt e consumo em kg/min. Imagem examinada visualmente; versão histórica, sem extrapolação automática para todo o DB3K_498.
- Registro SQL `DataPropulsion/734 — 2x F119-PW-100`: identidade e parâmetros de motor coincidem com a linha da imagem. `DataPropulsionPerformance`, rowid 3701, faixa 1/regime 3, coincide em velocidade 650, limites 0/3657,6 e consumo 267,47. Investigar a extensão exata dessa correspondência, sem promover todos os regimes/propulsores.
- Pontos de faixas superiores têm correspondências e diferenças que devem aparecer separadamente. Não corrigir limites SQL ou arredondar números para fabricar igualdade.
- [Rafale — fabricante](https://www.dassault-aviation.com/en/defense/rafale/specifications-and-performance-data/) documenta capacidade interna em massa e distingue combustível externo. Comparação com o Rafale M histórico no SQL exige registrar variante/configuração/época; proximidade numérica não homologa o campo inteiro.
- [F-15E — USAF](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/viewType/Print/viewClass/f-15e-strike-eagle/) qualifica a capacidade publicada como incluindo tanques conformais e externos. Não comparar esse total diretamente à linha de combustível interno do catálogo.
- [API Fuel](https://commandlua.github.io/assets/DataTypes.html#Fuel): tipos separados, capacidade máxima e quantidade atual distintos. A lista documental pode não cobrir extensões do banco; não corrigir um código SQL por ausência na página.

### Acesso visual e manual

Após solicitação de Windows desbloqueado, o lançador 1.05.1307 tornou-se acessível. “Jogar” informou `Invalid target location` para `C:\Program Files (x86)\Matrix Games\Command Modern Operations\Command.exe`. O arquivo existe, com 33.682.608 bytes; causa da falha não determinada. A tentativa direta também expirou. **Nenhuma ficha nova foi comparada no Database Viewer nesta execução.** Não se alterou a instalação.

Manual instalado de 353 páginas: busca textual por termos de combustível, leitura e inspeção visual da página PDF 80. Consumo depende de velocidade, altitude e regime. A afirmação antiga sobre combustível terrestre não substitui a decisão expressa do SISCAN: zero imobiliza meios terrestres/navais; aeronaves são perdidas. No manual oficial de 425 páginas, a página PDF 91 foi reinspecionada: C-130H com saldo 28537,8 kg e taxa 23,4 kg/min, em voo. Não mostra capacidade máxima, DBID/configuração ou correspondência com tanque SQL. Não houve leitura integral nova nem OCR novo. Planilha de propulsão inteira e ampliação para decimais foram examinadas; sem inspeção integral das figuras do manual. Skills PDF e Computer Use aplicadas, além de Ponytail, TDD, documentação, revisão e versionamento nas atividades correspondentes.

Complemento primário: [manual oficial — painel de informações](https://command.matrixgames.com/manual/05-8-context-menus-and-info-panel/).

## Resultado da comparação por campo

Propulsor 734, `Throttle=3`, quatro faixas: **nove campos coincidentes, incluindo um ponto completo**. Unidades documentais: altitude m; velocidade kn; consumo kg/min.

| rowid / faixa | Altitude SQL mín./máx. | Altitude documental mín./máx. (m) | Velocidade SQL / documento (kn) | Consumo SQL / documento (kg/min) | Coincidências |
|---|---|---|---|---|---|
| 3701 / 1 | 0 / 3657,6 | 0 / 3657,6 | 650 / 650 | 267,47 / 267,47 | 4 |
| 3704 / 2 | 3657,6 / 7315,2 | 3657,9 / 7315,2 | 750 / 750 | 250,53 / 250,54 | 2 |
| 3707 / 3 | 7315,2 / 10972,8 | 7315,5 / 10972,8 | 850 / 850 | 211,31 / 211,32 | 2 |
| 3710 / 4 | 10972,8 / 18288 | 10973,1 / 12192 | 1000 / 1000 | 201,84 / 201,85 | 1 |

A regra exige identidade do motor e hashes da fonte/imagem; atribui `verified_documentary_sample` somente aos campos coincidentes. Campos divergentes mantêm unidade documental e diferença histórica separadas. `unit=null` significa ausência de correspondência numérica nesta prova, não demonstração de outra unidade física. Não corrigir valores nem inventar tolerância. A versão histórica não comprova o catálogo inteiro.

**INFERÊNCIA delimitada:** a planilha representa o desempenho do modelo F-22A associado ao conjunto `2x F119`; para esta amostra, taxa do conjunto modelado, sem multiplicação adicional por dois. Não generalizar a outros propulsores. `NumberOfEngines` não é multiplicador universal: há conjuntos CODOG com zero nesse campo. Mesmo o ponto completo retorna `calculation_ready=false`, pendente de configuração/estado e finalidade autorizada.

## Capacidades e escalas: resultado ainda não homologado

| Plataforma / tanque | Capacidade SQL literal | Referência externa e conversão | Limite da comparação |
|---|---|---|---|
| F/A-18C Aircraft/8; Fuel/173 | 4925 | NTSP US Navy: 10860 lb internas A/C = 4926,0131382 kg | Só excerto indexado; acesso ao PDF retornou 403. Não é igualdade ou prova da versão SQL. |
| Rafale M Aircraft/35; Fuel/201 | 4750 | Fabricante: 4,7 t internas = 4700 kg | Família/variante/época não demonstradas como equivalentes. |
| F-15E Aircraft/6; Fuel/266 | 5960 | USAF: 35550 lb = 16125,20875350 kg | Total inclui CFT e três tanques externos; comparação direta com tanque interno é inválida. |
| Niterói Ship/1349, /1351, /1799, /1800; Fuel/1541 e /1542 | 480000 diesel; 26000 aviação | Sem comprovação independente nesta entrega | Reservas diferentes; não somar aviação à propulsão naval. |

Fonte parcial do F/A-18: [NTSP histórico da US Navy, espelho](https://www.globalsecurity.org/military/library/policy/navy/ntsp/f-18-a_2001.pdf). Conversões de massa explicitamente identificada usam [NIST Handbook 44, apêndice C](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958917): tonelada métrica = 1000 kg; libra avoirdupois = 0,45359237 kg. Converter a referência não comprova unidade SQL por proximidade numérica. Litros/galões exigem densidade, tipo e condições; “ton” ambígua não é aceita como tonelada métrica. **Nenhuma capacidade SQL foi homologada nesta entrega.**

## Cobertura e classificação dos recursos

Foram examinados os **1.940 registros DataFuel**, preservados sem unidade SQL confirmada e sem saldo atual inferido:

| Código / descrição de origem | Registros | Domínio |
|---|---:|---|
| 1001 NoFuel | 0 | Sem recurso |
| 2001 AviationFuel | 735 | Líquido; kg apenas candidato para capacidade SQL |
| 3001 DieselFuel | 478 | Líquido; unidade pendente |
| 3002 OilFuel | 112 | Líquido; unidade pendente |
| 3003 GasFuel | 79 | Combustão; fase e unidade não confirmadas pelo nome |
| 3006 Gasoline | 4 | Líquido; unidade pendente |
| 4001 Battery | 74 | Recurso elétrico; não presumir massa ou kWh |
| 4002 AirIndependent | 4 | Recurso AIP; grandeza/unidade pendentes |
| 4003 LithiumIon | 1 | Recurso elétrico; não presumir massa ou kWh |
| 5001 RocketFuel | 350 | Propulsão de arma, separada da plataforma |
| 5002 TorpedoFuel | 72 | Propulsão de arma, separada da plataforma |
| 5003 WeaponCoastTime | 31 | Duração; escala temporal pendente |

A referência Lua consultada lista dez códigos; ausência de 3006/4003 nessa versão documental não os torna inválidos. Classificação de domínio não confirma unidade física.

Os **20.544 pontos** distribuem-se por **20 tipos de propulsão**. Há **662 taxas zero, das quais 623 nucleares**: não são automaticamente 662 dados faltantes. Zeros precisam de regra por domínio antes de concluir erro, autonomia infinita ou consumo nulo aplicável. Há **2.339 fronteiras compartilhadas de faixas aéreas**; exigem política de intervalo/faixa explícita, não são 2.339 erros comprovados.

## Condições para cálculo

1. Identificar plataforma, versão, loadout, tanque e recurso compatível com propulsor. Separar combustível próprio, aviação embarcada, eletricidade e propulsão de armas.
2. Demonstrar unidade/escala de capacidade e taxa, base por motor/conjunto e tempo. Não multiplicar por número de motores indiscriminadamente.
3. Informar capacidade utilizável e saldo da instância na mesma grandeza, finitos, não negativos e saldo ≤ capacidade. Capacidade não inicializa silenciosamente tanque cheio.
4. Fixar regime, velocidade e altitude/faixa, incluindo fronteiras e modificadores da configuração. Não interpolar/extrapolar sem método aprovado.
5. Segmentar alterações de regime, limitar débito ao saldo e tratar zero por domínio antes de dividir para obter autonomia.
6. Preservar decisões: mínimo configurado por operador/instrutor; pré-alerta fixo de cinco pontos percentuais; sem mínimo padrão de 30%. Reserva de retorno, alerta e autonomia são conceitos distintos. Zero imobiliza naval/terrestre e implica perda aérea.

As matrizes explicitam condições pendentes; não implementam outra física no motor. Sensores/armas mantêm pendências de 126; ensaio 125 permanece sintético.

## Código, artefatos e reprodução

Adicionados `prototype/fuel_unit_proof.py`, `prototype/tools/inspect_fuel_proof.py` e sete testes em `prototype/check_fuel_unit_proof.py`. Sem alteração de `technical_units.py`, contrato CPC, flags de uso, saldos ou fontes.

Entrega local em `C:\Users\bozoc\Documents\siscan\prototype\data\fuel-unit-proof-20261118-v3\`: `fuel_capacity_matrix.csv` (1.940 linhas de dados), `performance_conditions.csv` (20.544), `official_propulsion_chart.jpg` e `proof_report.json` (amostras, casos, fronteiras, hashes do produtor/regras e dos três arquivos anteriores). SHA-256 do relatório: `f617e027c6354ef887dd5ce40530e58d8b1bdc156b9b72ca3c3ab20c959719fe`. Dados locais não são publicados no GitHub; v1/v2 são intermediários, não a entrega.

Na pasta `prototype`, com as evidências preservadas e pasta de saída **nova**:

```powershell
python -m unittest check_fuel_unit_proof
python -m tools.inspect_fuel_proof data/db3k-compiled-06.sqlite3 data/fuel-unit-proof-20261118-v3/official_propulsion_chart.jpg data/fuel-unit-proof-NOVA
```

Sete testes focados passaram: identidade/hash, divergência histórica, recusa fora da amostra, preservação, conversão de massa e separação de recursos. **42 scripts Python** de regressão passaram em 53,95 s; log `%TEMP%/siscan-fuel-proof-regression-20261118-v2.log`. Testes comprovam software, não toda a física. Sem mudança gráfica, não foi repetida a suíte de navegador.

| Evidência | SHA-256 |
|---|---|
| DB3K_498.db3 | `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d` |
| Compilação 06 | `de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9` |
| Planilha oficial JPG | `9d6de52800e5ac6d8ac4c9d2ffd22b737c49247d42d156c3fcfa9eed4cdd152a` |
| Manual instalado | `da3f75ec537b2a64e77c432324c02410dd2c12f6d999e4813b96ab7c04df51c1` |

A ferramenta fixa hashes da compilação/imagem e identidade da fonte, sem uso silencioso de outra versão. Nenhum banco original/operacional alterado; servidor principal e planos antigos preservados.

Sincronização conferida para `C:\Users\bozoc\Documents\siscan`: sete arquivos de código/documentação e quatro artefatos, com igualdade de hashes entre as cópias; fonte/compilação e hashes dos planos antigos reconferidos. Código/documentação seguem o branch `codex/initial-siscan`; dados e imagem permanecem locais.

## Encerramento e pendências

- [x] Comparar amostra por ID/faixa/regime/campo e hash.
- [x] Classificar recursos e registrar condições de todos os pontos de desempenho.
- [x] Separar capacidade/saldo, base da taxa, configuração, zeros e fronteiras.
- [x] Testar e produzir artefatos rastreáveis sem promoção operacional.
- [ ] Confirmar unidades/escalas das capacidades SQL por domínio/configuração, com visualizador ou evidência primária equivalente.
- [ ] Demonstrar ligação tanque–propulsor e condições dos demais perfis; fixar política de faixas/base antes da integração física ao motor.

Hipóteses sintéticas de teste podem comprovar o comportamento do software, não a unidade física de um registro real. Não liberar o catálogo inteiro ou o motor com base em uma amostra.
