# 04 — Mapeamento do CMO / DB3K

## Fontes examinadas e limites

Na pasta `C:\Users\bozoc\Documents\siscan\` foram encontrados `DB3K_498.db3` e `command manual.pdf` (353 páginas). O SQLite foi aberto com URI `mode=ro` e `PRAGMA query_only=ON`; `PRAGMA integrity_check` retornou `ok`. O manual é digitalizado como imagens, sem camada de texto útil nas páginas verificadas. Nesta Missão 01-B, OCR local processou todas as 353 páginas em lotes. A análise textual foi sintetizada por capítulo; figuras foram examinadas por amostragem e dez páginas de menor confiança foram conferidas visualmente. Não se detectaram páginas inteiramente ilegíveis; letras pequenas em screenshots/tabelas podem conter perdas. Ver documentos 12–15 para método, cobertura, páginas e mapeamento.

## Estrutura direta do DB3K

Consultas a `sqlite_master` e `PRAGMA foreign_key_list` confirmam:

| Elemento | Resultado |
|---|---:|
| Tabelas | 167 |
| Views | 0 |
| Triggers | 0 |
| Índices explícitos | 199 |
| Índices automáticos SQLite | 79 |
| Índices totais no catálogo | 278 |
| Vínculos FK declarados | 75 |
| Integridade | `ok` |

## Categorias e exemplos

Metadados identificam tabelas `DataShip`, `DataAircraft`, `DataSubmarine`, `DataWeapon`, `DataSensor`, `DataFacility`, `DataGroundUnit`, `DataMount`, `DataComm`, `DataPropulsion`, `DataFuel`, `DataMagazine`, `DataLoadout`, assinaturas, relações componente-plataforma e tabelas `Enum*`. O dicionário de dados registra nomes, tipos e chaves; o tipo SQLite não determina unidade nem domínio. Relacionamentos inferidos por nomes não comprovam cardinalidade ou semântica.

### Revisão read-only do esquema e das relações

Uma nova leitura direta em modo URI `mode=ro`, com `PRAGMA query_only=ON`, confirmou `integrity_check = ok`, 167 tabelas e 75 entradas de FK declaradas. As FKs inspecionadas ligam tabelas satélites/associativas ao registro-base por `ID` (por exemplo, `DataShipMounts.ID → DataShip.ID`, `DataAircraftSensors.ID → DataAircraft.ID`, `DataMountWeapons.ID → DataMount.ID` e `DataLoadoutWeapons.ID → DataLoadout.ID`). Isso documenta vínculo estrutural declarado; não prova cardinalidade conceitual completa nem significado dos dados.

O inventário `03_relacionamentos.csv` contém, além dessas 75 FKs, 3.246 correspondências **inferidas por nome** contra possíveis PKs. Esse número representa pares de colunas candidatos gerados por regra nominal, não 3.246 relações confirmadas. Campos como `ComponentID`, `ComponentNumber` e `CodeID` devem ser verificados quanto a destino, domínio e cardinalidade antes de qualquer modelagem. Um mesmo nome pode ocorrer em tabelas semânticas distintas.

O dicionário contém parâmetros sugestivos, entre outros, `DataShip.Length`, `DataSubmarine.MaxDepth`, campos de faixa em `DataSensor`, parâmetros de `DataWeapon` e `DataPropulsionPerformance.Speed`/altitude. Na varredura de nomes de coluna não foi identificada coluna explícita que documente unidade física desses valores; nomes/tipos, por si, não permitem concluir se a unidade é metro, nó, quilômetro, kg, ano ou outra. Também não foi confirmada estabilidade de IDs entre versões do catálogo. Logo, esquema e campos foram mapeados, mas unidades, escalas e semântica permanecem pendentes de documentação de domínio confiável.

## Manual CMO — leitura por OCR

O manual possui 353 páginas digitalizadas. OCR local processou todas as páginas; capítulos 1–13 e elementos iniciais foram sintetizados em 12, e páginas/subtítulos estão indexados em 15. Sumário visual nas pp. 7–8. Dez páginas abaixo de confiança OCR 0,90 foram conferidas visualmente; nenhuma era ilegível. Figuras foram amostradas, não examinadas exaustivamente. OCR de letras pequenas pode conter perdas. O manual cobre interface, ScenEdit, menus, missões/RP, bancos/templates, combate, apêndices, glossário e histórico.

## Interpretação para o SISCAN

O manual é guia funcional, não modelo ER. Cenário/catálogo versionado, lados, unidades hospedadas/agrupadas, componentes, missões, áreas, eventos, briefings, score, logs e relatórios podem motivar perguntas conceituais. Tabelas comparativas e classificações estão nos documentos 13–14. Não copiar estruturas proprietárias, código ou dados, não importar regras automaticamente e não substituir decisões SISCAN.

**DECIDIDO:** uso descritivo/conceitual; não modificar banco original, nem presumir reprodução integral. A leitura semântica completa de 167 tabelas, unidades, estabilidade de IDs e relações sem FK permanece pendente. Esta missão não executou ATLANTICADOR/DB3K, testes ou implementação.
