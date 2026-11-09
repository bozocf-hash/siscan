# 65 — Levantamento integral e dados técnicos compilados por ficha

## Solicitação e resultado — 2026-11-09

O responsável determinou levantar todos os dados agora e reunir, abaixo de cada ficha, os dados técnicos e componentes, especialmente sensores, combustível e regimes de consumo. A apresentação anterior preservava os registros, mas exigia navegar individualmente aos componentes e limitava parte das associações exibidas.

Foi entregue a seção **Dados técnicos compilados**, reunindo recursivamente os registros associados sem sair da ficha. Foram acrescentadas bibliotecas para consultar diretamente sensores, combustível, propulsão, suportes, paióis, configurações, armas, ogivas e demais cadastros técnicos. A coleta de valores desta versão da fonte não foi adiada para outra fase.

## Auditoria integral de preservação

A ferramenta `tools/audit_compilation.py` comparou **cada linha e cada valor** do DB3K original com a compilação: identidade da tabela/linha, ID original e JSON completo dos campos. Também conferiu a lista de colunas e exportou tipo declarado, nulabilidade, valor padrão e posição na chave primária, inclusive chaves compostas.

| Cobertura conferida | Resultado |
|---|---:|
| Tabelas | 167 |
| Registros | 766.989 |
| Valores de campo comparados | 8.010.533 |
| Divergências de valor/coluna/linha | 0 |

O status da auditoria é `all_source_values_matched`. A contagem inclui todos os valores das tabelas, técnicos e não técnicos; não significa que todos tenham unidade ou significado físico validados. Valores binários usam representação base64 explícita, como no compilador, e foram comparados nessa representação. Zeros, NULL, sinais, precisão numérica e textos foram preservados. O arquivo original manteve seu hash.

A compilação vigente é `prototype/data/db3k-compiled-06.sqlite3`. Ela substitui a versão 05 como fonte de consulta da interface, preservando o artefato anterior para rastreabilidade. O banco do exercício não foi substituído.

## Dados prioritários recuperados

| Família | Registros da fonte | Conteúdo reunido |
|---|---:|---|
| DataSensor | 6.747 | 78 campos por sensor: limites de alcance/altitude, varredura, radar, ESM/ECM, sonar, visual/IR, assinaturas mínimas e demais valores |
| DataFuel | 1.940 | Tipo de combustível, capacidade e registros de associação à plataforma/componente |
| DataPropulsion | 3.467 | Identificação, tipo, número de motores, empuxos, SFC e demais campos da fonte |
| DataPropulsionPerformance | 20.544 | ID do propulsor, faixa de altitude, regime, velocidade, altitude mínima/máxima e consumo |

Todos os 20.544 registros de desempenho pertencem a propulsores existentes: **zero órfãos**. Eles cobrem 3.466 cadastros de propulsão. O único dos 3.467 sem registros de regime é **DataPropulsion/567 — Static**; a interface informa a ausência na fonte, sem inventar consumo.

Distribuição literal dos regimes: código 1, 5.581 linhas; código 2, 6.919; código 3, 5.578; código 4, 2.466. Como referência complementar, os nomes Loiter, Cruise, Full e Flank seguem os códigos publicados na [documentação Command Lua](https://commandlua.github.io/assets/DataTypes.html). Essa documentação é da API: não comprova por si só a unidade de armazenamento SQL de Speed, Consumption ou Altitude, nem uma regra de conversão. Os valores SQL continuam intactos e a qualificação acompanha a ficha exportada.

## Relações adicionais investigadas

A compilação passou de 240 para **243 regras**, com **1.876.710 vínculos de destino único**. Permanecem 75 regras de FK declarada; as novas relações têm evidência estrutural/nominal explícita:

- DataSensor.MasqueradeAs → DataSensor.ID: todos os valores encontram registro; 37 apontam a referências alternativas específicas e 6.710 ao cadastro 1001, cujo nome literal é None. Isso não representa 6.710 instalações de outro sensor e não gera contagem física.
- DataLoadout.QuickTurnaround_TimeofDay → EnumLoadoutTimeOfDay.ID: permite recuperar os códigos de período também para quick turnaround.
- DataSatelliteOrbits.Plane → EnumSatelliteOrbitPlane.ID: expõe o domínio do plano orbital e seus casos sem correspondência.

O total de ocorrências sem destino passou de oito para **199** porque a nova regra de plano orbital identificou **191 valores Plane=0**, sem ID 0 no domínio de destino. Os oito casos anteriores permanecem: três Visibility textuais, três AutonomousControlLevel e dois ShooterQty. O aumento reflete ampliação da cobertura, não perda de dados. Nenhum zero foi convertido para o código 1001/None e nenhuma associação foi preenchida por suposição. Todas as FKs declaradas continuam com destino correspondente.

Domínios sem coluna de referência identificada, como certos perfis de arma, permanecem preservados no inventário integral. Não foram conectados por coincidência numérica. Convenções como arcos permanecem nos parâmetros originais, sem conversão de setores por inferência.

## Ficha técnica reunida

O endpoint `GET /api/source-technical?table=DataShip&id=3` percorre:

1. O registro selecionado e suas tabelas auxiliares próprias.
2. Componentes, equipamentos e domínios codificados.
3. Os registros próprios dos componentes: frequências/capacidades/códigos de sensores, desempenho de propulsão, armas de configurações e suportes, registros intermediários de arma, combustível e demais cadeias mapeadas.

A resposta normaliza nodes e links, preservando tabela, rowid, ID original, todos os campos, parâmetros de associação, destino, evidência e status. Componentes compartilhados são reunidos uma vez; instalações repetidas permanecem como linhas separadas. Ciclos são referências entre nós, sem recursão infinita. A travessia é feita em lotes e **não usa limite de profundidade ou truncamento de registros**. Também foi retirado o limite anterior de 1.000 associações da consulta de detalhe.

`complete=true` significa que a travessia alcançável pelas regras compiladas foi esgotada, não que todas as relações semânticas possíveis do software tenham sido provadas. Vínculos sem correspondência continuam na resposta, com valor original e destino ausente.

Na interface, a ficha mostra:

- **Sensores, frequências e capacidades:** campos principais, todos os 78 campos sob expansão, frequências de busca/acompanhamento e iluminação, capacidades, códigos e agrupamentos.
- **Combustível e armazenamento:** tipo descrito pelo domínio, capacidade literal e associações ao registro selecionado.
- **Propulsão, regimes e consumo:** dados do propulsor e todas as suas linhas de desempenho, com regime, velocidade e consumo priorizados na tabela.
- **Todos os registros compilados:** acesso agrupado por tabela a todos os nós e campos reunidos, inclusive auxiliares e domínios.
- **Baixar ficha compilada (JSON):** exportação local de todos os nós, vínculos e proveniência, sem limitar o conteúdo ao que está expandido na tela.

Sensores/combustíveis/propulsores diretamente associados ao registro selecionado são separados dos pertencentes à cadeia de equipamentos e armamentos. Assim, o consumo de um motor de torpedo não é apresentado como consumo da plataforma hospedeira. Não são somadas capacidades nem multiplicados consumos pelo número de motores sem regra validada.

Os campos extensos são renderizados quando expandidos, mas os dados já estão na resposta completa. Há estado de carregamento e tentativa novamente em caso de falha. As tabelas permitem rolagem horizontal no celular; regime, velocidade e consumo são as primeiras colunas. As bibliotecas técnicas incluem também registros não utilizados por um meio específico, como todos os 1.940 combustíveis e 3.467 cadastros de propulsão.

## Verificações

O novo `check_technical_bundle.py` foi escrito antes da implementação e falhou inicialmente pela ausência da função. Depois passou cobrindo cadeias de sensores/frequências/combustível/propulsão, ciclo de sensores, componente compartilhado, instalações repetidas, destino ausente, precisão, zero, NULL e detecção de valor perdido na auditoria. A autorização da nova rota foi incluída nos testes de API. Os **dez scripts check_*.py** passaram e a sintaxe JavaScript foi conferida.

Verificações de travessia em dados reais:

| Registro | Nós reunidos | Campos preservados | Linhas de desempenho na cadeia |
|---|---:|---:|---:|
| Aircraft/3 | 393 | 3.164 | 10 |
| Ship/3 | 1.428 | 11.550 | 10 |
| Submarine/3 | 395 | 3.074 | 17 |
| GroundUnit/3 | 339 | 2.235 | 10 |
| Aircraft/5257, maior número de loadouts da fonte | 3.912 | 28.455 | 37 |

São contagens de registros de fonte, incluindo auxiliares/domínios/componentes transitivos; não quantidades físicas instaladas. As travessias medidas ficaram entre aproximadamente 0,05 e 0,15 s nesta máquina, sem constituir garantia para todas as fichas ou instalações.

No Edge/Playwright, com perfil isolado, foram conferidos: linhas de consumo da plataforma e da cadeia completas, expansão dos 78 campos do sensor, tabela de frequências, exportação JSON com a mesma contagem de nós/vínculos da API, bibliotecas, ausência real de regimes no cadastro Static, grafo grande, largura de 390 px e negação de acesso ao aluno. A verificação passou na cópia isolada e no serviço efetivo em 8787; o teste anterior de seis categorias, fotos e navegação também passou. As imagens foram inspecionadas visualmente.

As tabelas de negócio foram comparadas integralmente antes/depois da entrega e permaneceram iguais: 11.197 referências, dois registros de aprovação, 77.349 valores brutos cadastrados, oito meios sintéticos, duas alocações por partido, zero submissões, zero notas de revisão e cinco eventos. Sessões de login dos testes não fazem parte dessa comparação. A integridade do banco ativo retornou ok.

## Artefatos locais e rastreabilidade

Arquivos entregues em `C:\Users\bozoc\Documents\siscan\prototype\data\`, fora do GitHub:

- db3k-compiled-06.sqlite3 e db3k-compiled-06.json;
- db3k-compilation-manifest-06.json;
- db3k-association-audit-06.csv e db3k-association-unresolved-06.json;
- db3k-full-value-audit-07.json: comparação integral e inventário de tipos/PKs;
- db3k-technical-discovery-07.json: cobertura de propulsão e distribuição de regimes.

| Item | SHA-256 |
|---|---|
| Fonte DB3K_498.db3 | 1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d |
| Compilação 06 | de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9 |
| Compilador usado | cf66097b81d66b45ef3e60165afb733113a72f2422822e5f729e3552b824baca |
| Auditoria integral 07 | 8264c556c826a3d3ce525744529b64b15121586e12ac6a3ed347c75b612f27f7 |

Reprodução da auditoria, sempre com novo destino:

```text
python -m tools.audit_compilation CAMINHO_DB3K COMPILACAO.sqlite3 NOVO_RELATORIO.json
```

A coleta literal desta fonte está completa e conferida. Permanecem como investigação de significado/unidade as convenções não demonstradas, os códigos sem correspondência e a adequação para cálculos. Isso não impede consultar os dados agora e não autoriza inventar valores ou tratar as relações não declaradas como FKs confirmadas.
