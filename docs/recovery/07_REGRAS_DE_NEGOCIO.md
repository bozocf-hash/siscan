# 07 — Regras de negócio

| ID | Regra | Classificação e origem |
|---|---|---|
| FOR-001 | Planejamento usa quatro níveis: Marinha Unidade-Tarefa → Grupo-Tarefa → Força-Tarefa → Força Naval Componente | **DECIDIDO**, Missão 01; não equivale automaticamente à cadeia oficial |
| FOR-002 | Força Aérea: Elemento Aéreo → Unidade Aérea → Força Aérea → Força Aérea Componente; estrutura provisória | **DECIDIDO**, terminologia sujeita a aprofundamento |
| FOR-003 | Exército: Unidade (Batalhão/Regimento/Grupo) → Grande Unidade (Brigada) → Divisão de Exército → Força Terrestre Componente; sem nível de subunidade | **DECIDIDO** |
| AST-001 | Separar modelo, configuração e unidade individual no cenário | **DECIDIDO** |
| AST-002 | Aeronave individual tem vínculo com plataforma hospedeira ou base | **DECIDIDO** |
| NAV-001 | Movimento inicial é temporal, com posição, velocidade de referência, deslocamento e intervalos | **DECIDIDO**; rotas detalhadas não são requisito inicial |
| NAV-002 | Linha temporal deve permitir avanço, pausa e retrocesso; relógio simulado independe do real e posições são históricas | **DECIDIDO**; semântica de reexecução/ramificações pendente |
| LOG-001 | Consumo de navio varia por regime de velocidade; aeronave por velocidade e altitude; curva individual por plataforma/configuração | **DECIDIDO**; dados e unidades pendentes |
| LOG-002 | Registrar fonte, premissas e confiabilidade dos parâmetros; reserva configurável com alertas e histórico | **DECIDIDO**; 30% é exemplo, não regra universal |
| LOG-003 | Navio-tanque mantém combustível de propulsão separado do estoque transferível | **DECIDIDO** |
| GEO-001 | Navios de superfície e submarinos não podem ser posicionados/movidos sobre terra; validar entrada, deslocamento, atualização temporal e importação | **DECIDIDO** |
| GEO-002 | Validação usa máscara vetorial costa/terra independente do mapa-base; considerar resolução e margem configurável | **DECIDIDO**; fonte de dados pendente |
| GEO-003 | Batimetria/profundidade submarina é possibilidade futura | **DECIDIDO como fora do requisito imediato** |
| PRC-001 | PRC é indicador didático configurável, exige critérios acadêmicos, escalas, fontes, incerteza, hipóteses, sinergias possíveis e validação | **DECIDIDO** |
| PRC-002 | Não definir fórmulas/coeficientes nesta missão; PRC não prevê deterministicamente resultado de combate | **DECIDIDO** |
| PRC-003 | First Strike é hipótese configurável sujeita a incerteza e avaliação didática | **DECIDIDO** |
| MPNL-001 | Consolidar necessidades do menor escalão até o operacional, com rastreabilidade, sem duplicidades e recursos compartilhados explícitos | **DECIDIDO — Regra MPNL-001** |
| MPNL-002 | Considerar inventário, histórico de manutenção, disponibilidade e ciclo de vida; distinguir necessidade, importância organizacional e valor de combate | **DECIDIDO** |
| MPNL-003 | Determinar necessidades logísticas antes de incorporar preços/orçamento | **DECIDIDO**, ordem obrigatória |
| MPNL-004 | Não dimensionar sobressalentes simplesmente pelo valor de combate da plataforma | **DECIDIDO** |
| MPNL-005 | Não desenvolver otimização de armamentos/munições contra força adversária no MPNL | **DECIDIDO** |
| DID-001 | Alunos não veem submissões alheias antes de liberação pelo instrutor | **DECIDIDO**; controles técnicos pendentes |

Regras adicionais de validação, autorização, desempate, avaliação, dados incompletos e correção de submissão permanecem **PENDENTES**.
