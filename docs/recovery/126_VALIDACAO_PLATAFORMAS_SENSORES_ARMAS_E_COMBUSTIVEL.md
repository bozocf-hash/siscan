# 126 — Validação por plataforma: sensores, armas, combustível e consumo

**2026-11-18 · Primeira rodada integral de validação literal/estrutural concluída. Validação física/semântica ainda parcial.** O responsável determinou iniciar agora a validação dos sensores/armamentos de cada plataforma e acrescentou níveis de combustível/consumo. A dispensa das solicitações da skill permanece vigente; foram mantidos contrato, testes e evidências. Planos anteriores de `technical-catalog`, originais, compilação e bases em uso preservados.

## Recorte executável desta validação

1. Reconferir integralmente valores/inventário da compilação com o DB3K original usando a auditoria existente; verificar hashes antes/depois e acesso somente leitura.
2. Reconferir as relações de pertencimento, componentes e domínios relevantes, recalculando correspondência/chaves, sem confiar apenas no status gravado. Separar vínculo confirmado contra a fonte de FK declarada e hipótese estrutural/nominal.
3. Examinar todas as plataformas das seis categorias. Preservar sensores diretos, sensores de suportes/armas, alternativas de loadout, paióis e reservas separados. Componente compartilhado não é instalação única; referência de masquerade não é equipamento instalado.
4. Conferir campos, presença, tipo, faixas internas e sentinelas sem corrigi-los: alcance/probabilidades de origem, quantidade padrão/máxima/multiplicador, combustível/capacidade, propulsores e todas as linhas de regime/faixa/velocidade/consumo. Inversão de limites e valor não usual são ocorrências para avaliação, não prova automática de erro no Command.
5. Gerar sumário, lista por plataforma e fila rastreável de ocorrências, com tabela/rowid/ID e hashes. Usar arquivos derivados locais separados, fora do Git. Não criar aprovação operacional, conversão implícita ou valores novos.

Capacidade de tanque não é saldo atual. Componentes de combustível/propulsão das armas permanecem separados dos diretamente associados à plataforma. Não somar loadouts alternativos, não multiplicar Consumption por NumberOfEngines por presunção e não produzir consumo médio sem perfil temporal.

## Evidências e significado

Reutilizar 58–59 e 65–69 e `technical_units.py`: unidade SQL comprovada, unidade candidata e pendência são diferentes. A documentação primária [Emissions](https://commandlua.github.io/assets/Tables.html#Emissions) informa alcance de sensor da API em nm; ela não prova sozinha todas as colunas SQL. O template local `DB/Templates/Weapon.html` usa rótulos **Air PoH**, **Surface PoH / Reliability**, **Land PoH / Reliability**, **Sub PoH**, com tokens que diferem dos nomes SQL. Portanto, `*PoK` não será convertido em Pk do CPC só pelo nome ou pelo intervalo numérico.

Dados do catálogo são configurações de referência; saldo, avaria, modo ativo/passivo, estoque atual e condições do exercício pertencem à instância/estado. Homologação física exige evidência específica; validação estrutural/literal não equivale a essa homologação. Nenhum sensor gera uma probabilidade universal de detecção por alcance máximo.

## Entregáveis e verificação

- [x] Ferramenta repetível de auditoria e diagnóstico, sem alterar fornecedores atuais de dados.
- [x] Testes com fontes sintéticas: ciclo, instalação repetida, órfão, vínculo adulterado, alternativas, zero/NULL, combustível de arma separado, limites e preservação das fontes.
- [x] Execução integral da versão DB3K_498 disponível, com contagens reais por categoria e pendências por plataforma.
- [x] Documento de resultados, índice, comandos, sincronização e Git atualizados; dados proprietários fora do repositório, conferidos no encerramento.

Saídas previstas: auditoria literal existente, manifesto/estatísticas, componentes/ocorrências JSONL e plataformas JSONL/CSV. Contextos/evidências de unidade compartilhados para evitar copiar explicações extensas em cada linha. Nenhuma mudança de interface, DDL principal ou execução de combate é necessária para esta missão.

## Resultado da execução

Implementação em `siscan-prototype/tools/validate_platform_data.py`; testes em `check_platform_validation.py`. Sem dependências novas, alteração do compilador, do provedor, das unidades ou de `calculation_ready` do sistema. O diagnóstico conserva esse flag falso enquanto unidade, condições e aprovação não forem demonstradas. Isso não apaga as verificações literais/relacionais concluídas.

| Verificação | Resultado |
|---|---:|
| Tabelas originais conferidas | 167 |
| Registros comparados com o DB3K original | 766.989 |
| Valores comparados | 8.010.533 |
| Divergências literais | **0** |
| Tabelas selecionadas para diagnóstico de sensores/armas/logística | 71 |
| Registros dessas tabelas examinados | 688.800 |
| Regras de relacionamento recalculadas | 192 |
| Vínculos com destino único recalculados e conferidos | 1.725.128 |
| Valores sem correspondência em domínios | 8 |
| Vínculos `ComponentID` conferidos com destino único | 354.275 |
| Vínculos de pertencimento `ID` conferidos com destino único | 609.986 |
| Plataformas examinadas | **14.968** |

Os oito casos sem correspondência são três `DataAircraft.AutonomousControlLevel`, três `DataAircraft.Visibility` e dois `DataWeaponWRA.ShooterQty`. São códigos de domínio já documentados em 65; não são oito sensores/armas desaparecidos. **Não houve vínculo pendente de componente ou pertencimento nas relações selecionadas.** As 191 ocorrências do domínio orbital de 65 não fazem parte deste recorte de sensores/armas/logística; os valores originais dessas tabelas também foram conferidos pela auditoria literal completa.

Conferência relacional recalcula valor-chave, cardinalidade, rowid de destino e status para cada linha de cada regra selecionada; não confia no `matched` gravado. Regra estrutural/nominal continua identificada como tal, sem virar FK declarada ou prova de semântica física. Ciclos são percorridos com conjunto visitado; `MasqueradeAs` e domínios não são contados como equipamento instalado.

### Cobertura por categoria

As colunas abaixo contam plataformas com referências encontradas, **não quantidade física de sensores/tanques**. Ausência de linhas é ausência no recorte da fonte, sem declarar por inferência que o meio não tem determinada capacidade.

| Categoria | Examinadas | Sensores diretos | Sensores alcançáveis na cadeia | Armas alcançáveis | Combustível direto | Propulsão direta | Com desempenho direto |
|---|---:|---:|---:|---:|---:|---:|---:|
| Aeronaves | 6.047 | 5.299 | 5.416 | 5.306 | 6.026 | 6.047 | 6.047 |
| Navios | 4.035 | 3.925 | 3.935 | 3.638 | 3.978 | 4.035 | 4.024 |
| Submarinos | 699 | 686 | 686 | 617 | 355 | 699 | 699 |
| Terrestres | 416 | 183 | 312 | 349 | 389 | 397 | 397 |
| Instalações | 3.625 | 1.007 | 2.707 | 2.323 | 39 | 0 | 0 |
| Satélites | 146 | 145 | 145 | 1 | 0 | 0 | 0 |

Foram examinados integralmente os cadastros de **6.747 sensores, 3.995 armas, 10.021 registros de carga de arma, 3.593 suportes, 1.587 paióis, 31.258 loadouts, 1.238 ogivas, 1.940 combustíveis, 3.467 propulsores e 20.544 pontos de desempenho**. Campos e auxiliares selecionados acompanham os diagnósticos/estatísticas. Número de registros do catálogo não representa quantidade de equipamentos adjudicados ou disponíveis.

### Ocorrências para avaliação

Foram registradas **5.331 ocorrências** de coerência/semântica em registros e domínios. Uma linha pode ter mais de uma ocorrência e um componente pode servir a várias plataformas. Portanto, não são 5.331 registros diferentes nem 5.331 defeitos comprovados.

| Ocorrência | Quantidade | Tratamento |
|---|---:|---|
| `NumberOfEngines=0` | 2.200 propulsores | Preservar convenção do tipo; não multiplicar fluxo por zero nem inferir ausência de motores |
| `Consumption=0` | 662 pontos | Conservar regime/tipo/faixa; pode exigir interpretação de energia, estado estacionário ou outra convenção |
| `Speed=0` | 25 pontos | Não inventar deslocamento/velocidade mínima |
| Faixa de altitude invertida | 1 ponto | Revisar coluna/sentinela/contexto antes de selecionar o ponto |
| `RangeMax=0` | 869 sensores | Não transformar automaticamente em ausência de detecção/capacidade |
| Mínimo maior que máximo | 30 ocorrências: 28 sensores e 2 limites de uma arma | Revisar sentinelas e papel do sensor/arma; sem correção automática |
| Massa de arma zero | 1.370 armas | Sem massa unitária utilizável para payload por presunção |
| `Multiple` diferente de 1 | 165 registros de arma | Preservar multiplicador; não assumir contagem por item sem regra |
| Quantidade padrão maior que máxima | 1 registro de arma | Investigar, preservando ambos os valores |
| Códigos sem domínio | 8 | Conservar código literal e origem |

Casos prioritários rastreáveis: `DataWeaponRecord/9428`, arma referenciada 285, traz `DefaultLoad=400` e `MaxLoad=100`; `DataPropulsionPerformance` rowid **15639**, propulsor **2683**, faixa 1/regime 1, traz `AltitudeMin=19812`, `AltitudeMax=0`, velocidade/consumo zero; `DataWeapon/3566` tem dois pares de limites a investigar. Isso aponta trabalho de validação, sem afirmar defeito do software ou preencher correções.

Único cadastro de propulsão sem linhas de desempenho continua sendo `DataPropulsion/567 — Static`. Não recebeu consumo fictício. Todos os pontos disponíveis foram preservados individualmente; não foi produzida média por plataforma.

## Exemplos concretos já associados

**F/A-18C Hornet — DataAircraft/8:** três linhas de sensores diretos (IDs 1562, 1584 e 2898), dois suportes, **27 alternativas de loadout**, combustível 173 e propulsor 34 com **16 pontos de desempenho**. O combustível 173 traz `Type=2001 / Aviation Fuel`, `Capacity=4925` literal; unidade SQL continua separada de kg como referência de apresentação. O propulsor 34 registra dois motores. Isso não autoriza duplicar automaticamente cada taxa de consumo nem somar todas as alternativas de armamento.

**Niterói — DataShip/1349, F 40 Niteroi [Vosper Mk10, ASW]:** nove linhas de sensores, oito referências distintas de sensor, 12 linhas de suporte, seis paióis, propulsor 923 com quatro pontos de desempenho e dois registros de combustível: **1541, Type=3001 / Diesel Fuel, Capacity=480000**, e **1542, Type=2001 / Aviation Fuel, Capacity=26000**, ambos valores literais. Esses combustíveis permanecem separados, sem formar um tanque único ou atribuir o combustível de aviação ao sistema propulsor por suposição. As variantes 1351, 1799 e 1800 também foram examinadas com suas composições próprias.

Nenhuma dessas capacidades é o saldo atual de uma instância SISCAN. O relatório mantém `current_fuel`, `current_ammunition` e `average_consumption` nulos, com a razão explícita: estado atual não pertence ao catálogo estático e média requer perfil temporal/modelo válido. O mínimo configurável pelo operador e margem M+5 permanecem decisões anteriores, sem novos padrões.

## Evidências de significado e limites de uso

O template local de armas foi relido; SHA-256 `e5d76719059e01dcf881f4e83e63c71d3e329c8acf766f0ad7be604acf4afa66`. Rótulos de PoH/confiabilidade não equivalem por si só ao Pk didático de acerto 0–1. Na fonte, 969 armas têm `AirPoK>1`; não foi aplicado `/100` nem recalibrado dano por conveniência. A correspondência entre campo, contexto e regra de cálculo ainda precisa ser explicitamente demonstrada.

As referências de unidades existentes foram reaproveitadas por contexto, inclusive tipo de combustível e tipo de propulsor para as linhas de consumo. [Emissions](https://commandlua.github.io/assets/Tables.html#Emissions) documenta nm para `sensor_maxrange` da API; [Unit](https://commandlua.github.io/assets/Wrappers.html#Unit) expõe combustível como parte da instância. Esses contratos não documentam automaticamente a escala de todas as colunas SQL do DB3K_498. Valores e evidências candidatas estão acessíveis agora, sem falsificar aprovação física.

## Artefatos e reprodução

Pasta local de entrega: **`C:/Users/bozoc/Documents/siscan/prototype/data/platform-validation-20261118-v1/`**; equivalente no repositório: `siscan-prototype/data/platform-validation-20261118-v1/`. Dez arquivos, aproximadamente 203 MB, fora do Git:

- `summary.json`: versão, hashes, cobertura por categoria, contagens e hashes dos demais artefatos.
- `literal_audit.json`: comparação integral com original e inventário de colunas.
- `platforms.csv` / `platforms.jsonl`: uma entrada por plataforma, instalações, componentes diretos/transitivos, perfis e ocorrências.
- `components.jsonl`: campos literais dos componentes/pontos de desempenho, identidade fonte, evidência e diagnóstico.
- `installations.jsonl`: linhas próprias de associação e parâmetros; preserva repetições e alternativas.
- `issues.jsonl`: fila por tabela/rowid/ID/campo, valor, código e motivo de revisão.
- `relation_coverage.json`: regras, fundamento e resultados recalculados.
- `field_profiles.json`: presença, NULL, zero, sinais, tipos e extremos por campo.
- `field_evidence.json`: evidências compartilhadas por tabela/contexto, sem promoção.

SHA-256 da fonte: `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`; compilação: `de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9`. Ambos reconferidos antes/depois e `PRAGMA quick_check=ok` em leitura separada. Sumário: `2b7fc4b639a876daa606a17d51b621d7f436a840dd9e7cfc4d3a5800e2cd9135`.

Na pasta `prototype` da entrega ou `siscan-prototype` do repositório, sempre com pasta de saída nova:

```powershell
$pythonValidation = 'C:/Users/bozoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pythonValidation -u -m tools.validate_platform_data 'C:/Users/bozoc/Documents/siscan/DB3K_498.db3' 'data/db3k-compiled-06.sqlite3' 'data/platform-validation-NOVA'
& $pythonValidation -m unittest check_platform_validation
```

Pasta existente é recusada; fontes em modo somente leitura/query_only. Sumário de conclusão só é emitido depois de terminar e reconferir os hashes. Execução interrompida pode deixar artefatos parciais sem `summary.json`; não usar esses arquivos como entrega concluída. CSV neutraliza fórmulas originadas de nomes. Componentes compartilhados são contados como referências distintas, instalações repetidas são preservadas e não há limite de profundidade no percurso selecionado.

## Verificação e encerramento desta rodada

Os **seis testes novos** foram escritos antes da ferramenta e passaram após a implementação. Demonstraram instalação repetida, componente compartilhado/ciclo, masquerade fora do inventário, órfãos, adulteração de vínculo/valor, ausência de relatório completo em falha, alternativas de carga, combustível de arma separado, zero/NULL, limites, destinos exclusivos e CSV seguro. **Todos os 41 scripts Python `check_*.py` passaram**, incluindo fluxo documental, catálogo, recursos, combustível, CPC, adjudicação, persistência e API. Contagem por scripts; não é alegação de apenas 41 casos. Log externo: `%TEMP%/siscan-platform-validation-regression-20261118-v1.log`.

Não houve mudança de interface; não foi alegada nova inspeção visual no Command ou leitura integral do manual. Não foram alterados DB3K, compilação, base SISCAN ativa, perfis sintéticos, senhas ou processos. Sem conversões, DDL principal, promoção de atributos ou mudança de autoridade. Os planos antigos `tasks/plan.md` e `tasks/todo.md` permanecem intactos; este diagnóstico não executa silenciosamente a publicação/aprovação prevista neles.

**Trabalho seguinte de validação:** resolver ocorrências prioritárias com evidência por campo/tipo/configuração; comprovar unidades/escala e base de consumo; definir o mapeamento de características de sensores/armas para o modelo CPC, sem reduzir sensor a alcance ou dano físico a pontos arbitrários; vincular capacidade validada a saldo/estoque inicial explicitamente configurado na instância. A primeira rodada está concluída; não se declara homologação física integral do catálogo.
