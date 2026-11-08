# 39 — Matriz de interfaces conceituais e dependências

As interfaces abaixo são **PROPOSTAS de organização**, não API, schema ou contrato de software. Cada módulo mantém sua responsabilidade e autoridade conforme 35/38.

## Interfaces conceituais

| Origem → destino | Informação compartilhada | Finalidade | Dependências | Situação e questões abertas |
|---|---|---|---|---|
| AST → SCN | modelos/configurações, fonte, data, confiança | Selecionar meios para versão de cenário | Identidade/versão, categorias | Conceito compatível com AST-01/SCN-01; campos e chaves pendentes. |
| AST → FOR | unidade individual, hospedeiro/base e capacidades cadastrais | Compor força sem duplicar ficha técnica | Hierarquia por ramo, validade | Unidade/hospedeiro decididos em conceito; cardinalidade pendente. |
| FOR → SCN | composição e níveis organizacionais | Inserir composição em cenário | DEC-011, versão de força | Quatro níveis decididos; movimento/edição e versões pendentes. |
| GEO → SCN | geometria, CRS, fonte, máscara e resultado de validação | Definir área e validar posicionamento inicial | Fonte/licença, resolução, margem | Necessidade decidida; fonte e contrato pendentes. |
| SCN → DID | versão, período, premissas, forças/recursos disponíveis | Instanciar exercício reproduzível | SCN-01, FOR, AST, GEO | Uso conceitual decidido; freeze/ramificação pendentes. |
| DID → participante | descrição, briefing, dados liberados e tarefas | Apresentar exercício por perfil/equipe | Autorização backend, instrutor/aluno | Privacidade pré-liberação decidida; formatos/escopo pendentes. |
| participante → DID | composição submetida, decisões e justificativa | Registrar trabalho de aluno | Revisão, autoria, cenário-base | Intenção decidida; estados, prazo e retentativa pendentes. |
| DID → instrutor/avaliador | submissão, versão, rubrica e evidência | Avaliar e liberar | Papéis, privacidade, HIS | Avaliação prevista; relação avaliador/instrutor e rubrica pendentes. |
| GEO ↔ DID | leitura de geometria e representação de entidades autorizadas; retorno de seleção/viewport | Usar mapa no trabalho didático | Adaptador de apresentação, filtros no backend | **INFERÊNCIA/PROPOSTA**; definir limites de edição e payload. |
| DID → SIM | estado submetido, premissas, contexto temporal | Abrir etapa de adjudicação/atividade | DID status, SIM-01 | Adjudicação humana decidida; procedimento e quem decide pendentes. |
| SIM → HIS | hipótese, decisão humana, fundamento, instante e efeito didático | Rastrear adjudicação | Identidade, versão, histórico | Intenção de auditoria decidida; taxonomia/retificação pendentes. |
| NAV → GEO | posição/tempo em cada instante | Atualizar apresentação e validar posição | relógio, CRS, regra costeira GEO | NAV e GEO conceitualmente relacionados; semântica temporal pendente. |
| NAV → LOG | duração, velocidade/altitude e histórico de estado | Estimar consumo/autonomia | curvas por plataforma/configuração | Requisito conceitual decidido; parâmetros/unidades pendentes. |
| AST + FOR + NAV → LOG | configuração, quantidade, hierarquia e uso temporal | Disponibilidade, consumo e combustível | identificação e proveniência | **INFERÊNCIA** a partir dos requisitos; regra de cálculo pendente. |
| LOG → MPNL | inventário, consumo, condição, manutenção, disponibilidade, período | Calcular necessidade logística na unidade | unidade de medida, taxonomia de material | Sequência bottom-up decidida; contrato de dados pendente. |
| MPNL → escalão superior | necessidade com origem, demanda, recurso compartilhado e quantidade | Consolidar sem dupla contagem | quatro níveis 08, regra de compartilhamento | MPNL-001 decidido; fórmula/regra quantitativa pendente. |
| MPNL → base econômica | itens e quantidades já consolidados | Posteriormente atribuir preço/orçamento | base técnica/logística, vigência/moeda | Ordem “necessidade antes de preço” decidida; interface/etapa econômica pendente. |
| SIM/DID/NAV/LOG/MPNL → ANA | resultados, avaliação, versões, fontes e limitações | Relatórios didáticos/logísticos | rubrica, acesso e métricas | Relatório previsto; indicadores/formatos pendentes. |
| todos os domínios → HIS | ator, timestamp, objeto, mudança, versão, fonte e justificativa | Auditoria e reconstrução | identidade, política de retenção | Necessidade decidida; eventos e política pendentes. |
| backend → frontend | DTOs autorizados, capabilities, revisão/versionamento, erros | Separar UI de schema e impor autoridade do servidor | Contratos versionados e IAM | Princípio da Missão 03; contratos ainda não definidos. |
| atlanticador adapter → GEO | fontes/cartografia e seleção/viewport | Preservar visualização existente, se aprovado | compatibilidade, licença, versão, segurança | PROPOSTO, sem integração disponível. |
| DB3K → AST (via processo controlado futuro) | candidatos de cadastro e seus metadados | Estudo/mapeamento de proveniência | semântica/unidades/licença/ID estável | Não é interface aprovada; não há vínculo direto no código atual. |

## Matriz de dependências entre módulos

`A → B` indica que B consome conceito/dado de A, não necessariamente que deve ser serviço separado.

| Módulo | Depende de | Fundamentação/risco de iniciar antes |
|---|---|---|
| HIS | Identidade e catálogo de eventos | Pode especificar campos comuns cedo; implementação depende dos objetos/políticas de retenção. |
| GEO | CRS, fonte vetorial, licenças, máscara e regra costeira | Sem eles não se aceita validação de posição; viewer sem máscara não satisfaz GEO-02. |
| SYM | Catálogo, categorias/unidades e licença | Integração Calunga bloqueada até direitos e conformidade. |
| AST | Taxonomia, identidade, proveniência e unidade | SCN/FOR/LOG não podem fixar chaves/campos antes do cadastro conceitual. |
| FOR | AST e hierarquia MPNL/ramo | Deve respeitar 08; se iniciado com hierarquia errada causa retrabalho e violação de decisão. |
| SCN | AST, FOR, GEO, versionamento e premissas | Exercício DID depende de cenário reproduzível. |
| DID | SCN, FOR, identidade, autorização e HIS | Requer privacidade server-side; início sem política de acesso é risco alto. |
| NAV | GEO, relógio, unidade de velocidade e estado temporal | Atualização espacial não deve preceder regra de tempo/retrocesso. |
| SIM | DID, estado/versão, NAV quando temporal, HIS | Não iniciar adjudicação sem processo humano, eventos e resultado definido. |
| PRC | DID/SIM, rubrica, fontes e hipóteses | Fórmula não aprovada; só especificar depois de decisão acadêmica. |
| LOG | AST, NAV, perfil de consumo, unidades e confiabilidade | Consumo não pode ser confiável sem parâmetros/unidades documentados. |
| MPNL | LOG, inventário/manutenção, FOR e itens | Deve preservar MPNL-001; não usar valor de combate como proxy de demanda. |
| ANA | DID/SIM/PRC/NAV/LOG/MPNL, rubrica e permissões | Relatórios antes de definir dados produzem métricas inconsistentes. |

## Sequência de desenvolvimento candidata

Sequência e critérios de passagem mais completos estão em [41](41_ROADMAP_PRELIMINAR_DESENVOLVIMENTO_SISCAN.md). O roadmap sugere decisões e modelagem antes de codificação, requisitos de acesso antes de submissão, base técnica antes de LOG e LOG antes de consolidar MPNL. Não define cronograma, esforço nem aprovação.
