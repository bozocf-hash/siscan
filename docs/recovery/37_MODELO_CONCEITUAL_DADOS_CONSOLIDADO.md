# 37 — Modelo conceitual de dados consolidado

## Propósito e classificação

Este é um modelo conceitual de referência, não um esquema físico, migração ou autorização de alteração de banco. Classificações: **SISCAN decidido** = conceito aprovado em documentos 01/05/07/08; **proposto** = entidade analítica organizada em 06 ou nesta consolidação; **pendente** = identidade/relação/cardinalidade depende de decisão; **ATLANTICADOR identificado** = código/persistência encontrada estaticamente em 16–28; **DB3K identificado** = metadado de tabela, sem equivalência de domínio garantida.

## Domínios conceituais SISCAN

| Domínio/entidade | Maturidade e fonte | Relações conceituais | Dúvidas / limites |
|---|---|---|---|
| PlataformaModelo | SISCAN decidido conceitualmente: modelos/meios separados (05 AST-01/02; 06) | Modelo possui configurações; cadastra atributos técnicos com fonte/data/confiabilidade. | Identidade, categoria, versão, campos e catálogo mestre pendentes. |
| ConfiguraçãoPlataforma | SISCAN decidido conceitualmente (05 AST-01; 06) | Pertence a um modelo; reúne equipamentos/sensores e perfil de consumo; pode ser base de uma unidade. | Validade temporal e cardinalidade de componente pendentes. |
| Equipamento / Sensor / Material | Identificado nos requisitos e MPNL; entidade conceitual proposta em 06 | Componente instalado ou item de inventário; pode ter identidade técnica/logística/econômica vinculada. | Taxonomia, unidade, relação peça-material e fonte DB3K pendentes. |
| UnidadeCenário | SISCAN decidido conceitualmente (05 AST/FOR; 07 AST-001/002; 06) | Unidade individual referencia configuração e pertence a força/versão de cenário; tem estados/posições históricos. | Regras de unidade hospedada/base e relação com força/cenário carecem de chaves e temporalidade. |
| Força / Escalão | Hierarquia FOR decidida (07–08; 35) | Níveis hierárquicos por ramo; unidades subordinadas preservam origem. | Relação entre níveis deve obedecer exatamente 08; Exército sem subunidade; FA nomenclatura provisória. |
| Cenário / VersãoCenário | SISCAN decidido como criação e versões (05 SCN-01); estrutura proposta em 06 | Versão agrega contexto, forças/unidades, parâmetros, dados geográficos e premissas. Exercício usa uma versão. | Política de congelamento, ramificação, alteração após início e cardinalidades pendentes. |
| Exercício | SISCAN planejado (02, 05 DID-01/04) | Usa cenário/versão, participantes, prazos, submissões e avaliações. | Relação cenário-exercício e status completo pendentes. |
| Participante / Usuário / Perfil / Permissão | Perfis conceituais listados em 02; modelo de permissão pendente | Usuário participa de exercício por perfil/equipe; autoria em submissão, avaliação e eventos. | Fonte de identidade, escopo de perfil, relação avaliador/instrutor e observador pendentes. |
| Submissão / Composição / Justificativa | SISCAN decidido na primeira demonstração (01,05 DID-02/04) | Aluno envia composição/decisões e justificativa contra uma versão do cenário; privacidade até liberação. | Estados, múltiplas tentativas, prazo, versionamento e compartilhamento pendentes. |
| Avaliação / Rubrica | Relatório/avaliação previstos (02,05 DID-03/ANA-01) | Instrutor/avaliador avalia submissão e pode liberar visibilidade; gera resultado/feedback. | Critérios, escala, autoria, múltiplos avaliadores pendentes. |
| Evento / Decisão / Adjudicação | SISCAN decidido como SIM didático/humano e HIS (01,05,07) | Adjudicação vinculada a exercício, instante simulado, hipótese, decisão humana, fundamento e impacto registrado. | Taxonomia, efeitos, sequência temporal e reversão pendentes; CMO trigger-action é só referência. |
| PosiçãoHistórica / EstadoUnidade | NAV decidido (05 NAV-01/02; 07 NAV-001/002) | Unidade tem série temporal de posições/estado associada a cenário/exercício e eventos. | Política de granularidade, retrocesso, branching e retenção pendente. |
| MáscaraTerrestre / Geometria / Camada | GEO decidido (07 GEO-001/002); dados pendentes | Camada geográfica alimenta validação espacial de posição/percurso e visualização. | CRS, fonte/licença, resolução, margem e temporalidade pendentes. |
| PerfilConsumo / RegistroConsumo | LOG decidido conceitualmente (05 LOG-01/02; 07 LOG-001/002) | Curva associada a modelo/configuração e condições; registros de consumo/posição temporal alimentam autonomia. | Unidades, fonte e método quantitativo pendentes. |
| Estoque / Material / NecessidadeLogística / Reposição | MPNL decidido como domínio e sequência (05,07,08) | Inventário e manutenção geram necessidade no menor nível; consolida bottom-up até escalão operacional. Recursos compartilhados preservam origens sem dupla contagem. | Menor unidade, itens, condições, regra de demanda, períodos, lead time e arredondamento pendentes. |
| EventoManutenção / Disponibilidade / CicloVida | Princípios MPNL decididos (07–08) | Afetam disponibilidade e necessidade de material/reposição; conservam histórico. | Estados, métodos, fonte e vínculo material/unidade pendentes. |
| BaseEconômica / Preço / Orçamento | MPNL decidido como etapa posterior; detalhes propostos em 06/08 | Preço/validade/moeda vincula item após quantidade e necessidade determinadas. | Câmbio, vigência, projeção e regra orçamentária pendentes. |
| IndicadorPRC / Hipótese | PRC didático decidido, entidade conceitual proposta (05 PRC-01; 07 PRC-001/003; 06) | Configuração de estudo associa critérios, fontes, incerteza e resultado comparativo. | Fórmula, peso e validação não definidos; não criar fórmula determinística nem usar como logística. |
| Histórico / Auditoria | HIS decidido como intenção (05 HIS-01) | Registra autoria, data, objeto/versão, ação e motivo, associado aos domínios. | Retenção, acesso, imutabilidade e detalhe antes/depois pendentes. |

## Evidência externa: entidades encontradas nas fontes, não SISCAN

| Fonte | Elementos identificados | Classificação e limite |
|---|---|---|
| ATLANTICADOR 2.0.0 | `elements`, `roles`, `baselines`, `snapshots`, `current`, `events`, `audit`, `publications`, `triggers`, `effect_records`, `effect_editors`, `confrontations`, exportações; objetos frequentemente guardados como JSON `body` e KMZ BLOB | **IDENTIFICADO** no código (20, 27). A fotografia do ZIP não comprova DB instalado nem equivalência com entidade SISCAN. |
| ATLANTICADOR frontend | cenas, nós/camadas, feições, vértices, drafts GeoJSON/KML/KMZ; estado local | **IDENTIFICADO** em 29–32; modelo de apresentação/editor, não modelo canônico de domínio SISCAN. |
| DB3K | `DataShip`, `DataAircraft`, `DataSubmarine`, `DataWeapon`, `DataSensor`, `DataFacility`, `DataGroundUnit`, `DataMount`, `DataComm`, `DataPropulsion`, `DataFuel`, `DataMagazine`, `DataLoadout`, tabelas satélites/associativas e `Enum*` | **IDENTIFICADO** por metadados em 04. 167 tabelas, 75 FKs; relações semânticas, unidades, domínios e estabilidade de IDs não confirmados. |
| CMO manual | cenário, lado, unidade hospedeira, grupo, plataforma, componente, missão, área/RP, evento/trigger/action, briefing, score e log como conceitos narrados | **IDENTIFICADO** documentalmente em 12–15; manual não é esquema ER nem define cardinalidades de SISCAN. |

Não se presume equivalência de `DataShip` com PlataformaModelo, de um `element` ATLANTICADOR com UnidadeCenário, ou de lados CMO/partidos ATLANTICADOR com forças/equipes SISCAN. Nenhuma migração nem vínculo físico é proposto.

## Relações conceituais e cardinalidades

**Confirmadas como regra organizacional, não cardinalidade de banco:** os quatro níveis por ramo em 08; uma composição de força usa a hierarquia definida, com Exército sem subunidade. **Decididas em fluxo didático:** aluno cria submissão de exercício; instrutor avalia/libera; o aluno não vê submissões alheias antes da liberação. **Propostas/inferências:** cenário contém versões; versão associa forças/unidades; unidade referencia configuração; exercício utiliza versão; submissão gera avaliação; unidade acumula posição/estado; inventário/manutenção alimentam necessidade; necessidade agrega por escalão com origem preservada; preço vincula-se ao material após a etapa logística. Cardinalidades, opcionalidade, chaves, temporalidade e exclusividade permanecem **PENDENTES**.

## Regras para evolução do modelo

1. Identificadores SISCAN próprios e estáveis precisam ser definidos; não reutilizar IDs DB3K sem comprovação de estabilidade e semântica.
2. Registrar origem, data de referência, confiabilidade e estado confirmado/estimado/hipótese quando aplicável.
3. Separar dados geográficos, didáticos, planejamento logístico e trilha de histórico, conectando-os por interfaces explícitas.
4. Preservar as três bases MPNL (técnica, logística, econômica) relacionadas, mas independentes.
5. Não converter este documento em DDL, ER físico, API ou migração sem decisão e missão autorizada.
