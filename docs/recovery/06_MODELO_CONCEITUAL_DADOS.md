# 06 — Modelo conceitual de dados

Este é um mapa de conceitos, não um esquema aprovado. **PROPOSTO** indica organização analítica para continuidade; atributos e relações precisam de validação pelo responsável. A distinção entre fonte ATLANTICADOR, estruturas DB3K e conceitos SISCAN é obrigatória.

## Estruturas identificadas nas fontes

| Fonte | Elementos | Evidência/limite |
|---|---|---|
| ATLANTICADOR | Nenhuma entidade confirmada nesta sessão | Código ausente; tecnologias e módulos preliminares em 03 são não verificados |
| DB3K, metadados secundários | `DataShip`, `DataAircraft`, `DataSubmarine`, `DataFacility`, `DataGroundUnit`; tabelas de sensores, armas, comunicações, propulsão, combustível e enumerações | IDENTIFICADO nos relatórios locais como nomes/colunas; significado e relacionamentos semânticos não confirmados |
| SISCAN | Entidades abaixo | DECIDIDO/PLANEJADO conceitualmente no contexto; não implica implementação |

## Entidades conceituais SISCAN

| Entidade | Atributos conceituais | Relações conceituais |
|---|---|---|
| PlataformaModelo | identidade, nome, categoria/tipo, fonte, data de referência, confiabilidade | possui configurações |
| ConfiguraçãoPlataforma | componentes, sensores, equipamentos, perfil de consumo | pertence a modelo; pode instanciar unidade |
| UnidadeCenário | identidade individual, estado, configuração, posição/condição | integra força; participa cenário |
| Cenário / VersãoCenário | objetivo didático, período, recursos, estado/versionamento | contém forças, unidades, exercício e eventos |
| Força / Escalão | ramo, nível e denominação | composição hierárquica de forças/unidades |
| Exercício / Submissão / Decisão | autoria, escolhas, justificativa, versão, estado de liberação e avaliação | submetida por aluno em exercício; avaliada por instrutor |
| PosiçãoHistórica / Evento | instante simulado, posição, evento e autoria | vinculada a unidade e cenário |
| PerfilConsumo / RegistroConsumo | curva, condições, quantidade, fonte e confiabilidade | associado a configuração/unidade; acumula no tempo |
| MáscaraTerrestre | geometria, fonte, resolução e data | usada por validação de posição/percurso |
| IndicadorPRC / Hipótese | critério configurado, escala, fonte, incerteza | associado a estudo/cenário; sem fórmula definida |
| Material / Equipamento | identidade técnica, especificação e fonte | referenciado em inventário e manutenção |
| RegistroLogístico | unidade, material, quantidade, condição, período | consolida bottom-up sem duplicar compartilhados |
| EventoManutenção | item/unidade, tipo, data, histórico e disponibilidade | atualiza necessidade e projeção |
| Estoque / Necessidade / Reposição | quantidade, local/escalão e período | deriva de inventário, manutenção e premissas |
| BaseEconômica / Preço | valor, moeda, fonte, vigência e condição | ligado ao material após apuração da necessidade |
| Usuário / Perfil / Permissão | identidade, papel, escopo e estado | autoria, avaliação e controle de acesso |

## Relações e dependências propostas

**INFERÊNCIA/PROPOSTA:** Cenário possui versões; versão agrega forças e unidades; força contém subforças/unidades e preserva ramo/nível; unidade referencia configuração e pode ter histórico temporal; exercício vincula submissões a cenário/versionamento; submissão tem decisões, justificativas e avaliações. O MPNL agrega necessidades ascendendo escalões, rastreando origem e compartilhamento. A base técnica identifica o material; base logística acompanha inventário/manutenção/necessidade; base econômica atribui preço apenas após quantificação. Não reutilizar IDs DB3K como chaves SISCAN sem estratégia de estabilidade validada.

Cardinalidades, unicidade, temporalidade, versionamento, retenção e modelo de autorização estão **PENDENTES**. O diagrama físico depende de auditoria das estruturas reais e de decisão arquitetural.
