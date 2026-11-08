# 41 — Roadmap preliminar de desenvolvimento SISCAN

**Situação: PROPOSTA.** Sequência por dependências funcionais e técnicas, não cronograma, estimativa de esforço, compromisso ou autorização para começar implementação. As APR-01–APR-20 foram concluídas em 49, mas isso não autoriza iniciar o roadmap. Qualquer fase de desenvolvimento exige autorização expressa posterior; antes de eventual programação do primeiro protótipo, cumprir o gate do fluxograma definido em 49.

## Etapas candidatas e critérios de passagem

| Etapa | Foco e módulos | Pré-requisitos | Saída documental/técnica esperada | Critério de passagem proposto | Risco se iniciada antes |
|---|---|---|---|---|---|
| 0 — Validar escopo e decisões | Primeira demonstração; papéis; rubrica; limites SIM/PRC; roadmap | Decisões do responsável sobre Q-01–Q-09 e Q-16/17 | Caso de uso aprovado, glossário, limites, critérios | Escopo, papéis, privacidade e aceites aprovados por escrito | Retrabalho e expansão para simulação operacional não desejada. |
| 1 — Fundamentos de identidade e contrato | Backend authority, identidade/capacidades, interfaces, HIS transversal | Q-05/Q-07/Q-08/Q-09; requisitos de privacidade DID-04 | Matriz de capacidades, contrato de erro/versionamento, política de histórico | Leituras/escritas e visibilidade definidas por perfil, sem depender da UI | Exposição de submissões, dados e endpoints incompatíveis. |
| 2 — Proveniência, catálogo e modelo-base | AST, FOR, fontes, identificadores e versionamento | Q-10/Q-11/Q-12; hierarquia 08 preservada; revisão de DB3K | Modelo conceitual aprovado, fonte de dados/campos confirmada, unidades | Casos de modelo/configuração/unidade/força validados e identificadores próprios | Chaves instáveis, campos sem unidade e composição incompatível com ramo. |
| 3 — GEO e adaptador cartográfico | GEO, visualizador, geometria, CRS, máscara e fonte | Q-06/Q-13/Q-14/Q-15/Q-22/Q-23 | Decisão de biblioteca/licença, contrato cartográfico, política de máscara | CRS/fontes/margem licenciados e casos de validação espacial definidos; viewer pode operar por interface aprovada | Mapa visual confundido com fonte de verdade; licença/dados inadequados. |
| 4 — Cenário e composição de força | SCN, FOR e integração AST/GEO | Etapa 2; interfaces da etapa 3; cenário/versionamento Q-10 | Cenário versionado, hierarquia validada, dados iniciais rastreáveis | Uma versão reproduzível preserva organização Marinha/FA/Exército e proveniência | Submissão passa a depender de cenários mutáveis/sem rastreio. |
| 5 — Fluxo didático inicial | DID: exercício, entrega/submissão, justificativa, avaliação e liberação | Etapa 1 e cenário/composição aprovados | Fluxo instrutor-aluno com isolamento server-side e histórico | Casos de acesso confirmam isolamento antes da liberação e autoria/versão da entrega | Violação DEC-004 e exposição de trabalho entre alunos. |
| 6 — NAV e SIM adjudicado | Relógio, estado/posição, hipóteses e decisão humana | GEO, DID, HIS; Q-04/Q-16/Q-18 | Semântica temporal, registro de hipóteses e adjudicações | Avanço/pausa/retrocesso e decisão humana rastreáveis conforme política aprovada | Ambiguidade na reversão, histórico sobrescrito ou cálculo apresentado como resultado automático. |
| 7 — LOG | Consumo, autonomia, transferência e disponibilidade | AST, NAV, fontes/unidades Q-19 | Parâmetros versionados, hipóteses e relatório por unidade/período | Resultados rastreáveis a curva/configuração/unidades aprovadas | Quantificação sem dados confiáveis ou duplicação de combustível. |
| 8 — MPNL bottom-up | Inventário, manutenção, estoque, necessidade, reposição; depois preço | LOG/AST/FOR; Q-20/Q-21 | Consolidação desde unidade até operacional e base econômica posterior | MPNL-001 preservada, decomposição da origem e controle de compartilhados verificados em caso de referência | Dupla contagem ou inversão necessidade→preço. |
| 9 — ANA/PRC e relatórios | Resultados, avaliação, indicadores, relatórios | DID/SIM/NAV/LOG/MPNL; rubricas e limites Q-02/Q-17/Q-24 | Relatórios com versão, fontes, hipótese, público e limitações | Indicadores interpretáveis, didáticos, auditáveis e autorizados | Métrica sem significado/rubrica ou alegação preditiva não aprovada. |
| 10 — Qualificação da solução | Segurança, desempenho, interoperabilidade, recuperação, acessibilidade | Decisões RNF 36, ambiente Q-25 e licenças | Planos e evidências de validação aprovados | Metas mensuráveis e procedimentos de backup/restore e acesso comprovados | Implantação sem disponibilidade, restauração ou salvaguardas definidas. |

## Caminhos paralelos possíveis (dependentes de autorização)

- **Documentação de dados e licenças:** pode avançar em paralelo à definição pedagógica, sem importar ou modificar DBs.
- **Protótipo cartográfico isolado:** poderia ser avaliado antes do fluxo DID somente após escolha de dados/CRS/licença; deve usar dataset de teste e não dados oficiais.
- **MPNL conceitual:** regras, material, unidade de medida e caso de referência podem ser definidos sem viewer/cartografia, preservando a independência concebida em 08.
- **IAM/HIS:** suas políticas podem ser documentadas em paralelo, mas a implementação precisa dos objetos e responsabilidades decididos.

## Dependências críticas

1. **Privacidade e autorização precedem submissões** (DID-04; Q-08/09).
2. **Proveniência e identidade precedem AST/FOR/SCN** (Q-10/11/12).
3. **Fonte, CRS, licença e máscara precedem validação geográfica** (GEO-02/03; Q-13/15).
4. **NAV depende de uma política temporal explícita e GEO/HIS** (Q-18).
5. **LOG depende de unidades e perfis confiáveis; MPNL depende de LOG, hierarquia, inventário/manutenção** (08; Q-19/20).
6. **MPNL determina necessidade antes de preços e orçamento** (MPNL-001/003; Q-21).
7. **PRC/ANA dependem de rubrica, fonte e limites didáticos aprovados** (Q-02/17/24).
8. **Qualquer reuso ATLANTICADOR depende de contrato, compatibilidade e licença** (21,28,33; Q-06/15/23/26).

## Condições de mudança de fase

Uma etapa só passa quando o responsável aprovar seus pré-requisitos e artefatos, questões de bloqueio forem resolvidas ou explicitamente aceitas e critérios de passagem forem substituídos por critérios aprovados. Não há estimativas de esforço nem datas, pois não existe evidência suficiente. Este roadmap não inicia a Missão 04.
