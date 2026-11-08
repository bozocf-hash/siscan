# 05 — Requisitos funcionais

Prioridade preliminar: **P0** essencial à visão inicial; **P1** importante; **P2** futuro/condicional. Situação: **Planejado** indica decisão conceitual, **Pendente** exige especificação. Nenhum item implica implementação existente. Origem `M01` = contexto consolidado da Missão 01; `DB` = artefatos secundários DB3K.

| ID | Módulo | Requisito | Origem | Prior. | Situação |
|---|---|---|---|---|---|
| GEO-01 | GEO | Representar dados espaciais aproveitando capacidades ATLANTICADOR verificadas | M01 | P0 | Planejado; integração não verificada |
| GEO-02 | GEO | Validar posição e percurso de navios/submarinos contra máscara vetorial terrestre, inclusive importação e atualização temporal | M01 | P1 | Planejado; dados/resolução pendentes |
| GEO-03 | GEO | Permitir margem costeira configurável | M01 | P1 | Planejado |
| SYM-01 | SYM | Integrar/gerir simbologia Calunga | M01 | P1 | Planejado; implementação não verificada |
| AST-01 | AST | Manter modelos, configurações e unidades individuais separadamente | M01 | P0 | Planejado |
| AST-02 | AST | Catalogar navios, submarinos, aeronaves, porta-aviões/navios-aeródromo, navios-tanque e auxiliares | M01 | P0 | Planejado |
| AST-03 | AST | Identificar aeronaves individualmente e associá-las a hospedeiro ou base | M01 | P1 | Planejado |
| AST-04 | AST | Rastrear identificador, nomenclatura, categoria/tipo, aplicabilidade, fonte, data de referência e confiabilidade | M01 | P1 | Planejado |
| AST-05 | AST | Distinguir cadastro técnico, logístico e econômico no MPNL | M01 | P1 | Planejado |
| SCN-01 | SCN | Criar e gerir cenários didáticos e versões | M01 | P0 | Planejado; versionamento por definir |
| FOR-01 | FOR | Organizar forças em quatro níveis conforme ramo definido | M01 | P0 | Planejado |
| DID-01 | DID | Instrutor disponibiliza exercício, meios e recursos | M01 | P0 | Planejado |
| DID-02 | DID | Aluno compõe forças, registra decisões e justificativas | M01 | P0 | Planejado |
| DID-03 | DID | Instrutor avalia submissões e libera visibilidade | M01 | P0 | Planejado |
| DID-04 | DID | Impedir aluno de visualizar submissão alheia antes da liberação do instrutor | M01 | P0 | Regra decidida; controles pendentes |
| SIM-01 | SIM | Apoiar simulação abstrata com adjudicação humana | M01 | P1 | Planejado; procedimento pendente |
| ANA-01 | ANA | Consolidar resultados em relatório | M01 | P0 | Planejado; conteúdo/formatos pendentes |
| NAV-01 | NAV | Atualizar posição usando posição inicial, velocidade, deslocamento e intervalo temporal | M01 | P1 | Planejado |
| NAV-02 | NAV | Permitir avanço, pausa e retrocesso; manter relógio simulado e histórico de posições | M01 | P1 | Planejado; semântica de retrocesso pendente |
| LOG-01 | LOG | Calcular consumo por regime de velocidade (navios) e velocidade/altitude (aeronaves), com curvas por plataforma/configuração | M01 | P1 | Planejado; parâmetros/fontes pendentes |
| LOG-02 | LOG | Registrar autonomia, consumo, reserva configurável e alertar ao limite | M01 | P1 | Planejado; 30% é apenas exemplo |
| LOG-03 | LOG | Separar combustível próprio do navio-tanque do saldo transferível | M01 | P1 | Planejado |
| PRC-01 | PRC | Permitir indicadores didáticos configuráveis, estudos comparativos e hipóteses explicitadas | M01 | P2 | Planejado; critérios/validação pendentes |
| HIS-01 | HIS | Registrar eventos, alterações e auditoria | M01 | P1 | Planejado; retenção e acesso pendentes |
| MPNL-01 | MPNL | Consolidar necessidades do menor escalão ao operacional com rastreabilidade e controle de duplicidade/compartilhamento | M01 | P1 | Regra MPNL-001 decidida |
| MPNL-02 | MPNL | Considerar inventário, manutenção, disponibilidade e ciclo de vida | M01 | P1 | Planejado |
| MPNL-03 | MPNL | Calcular necessidades e reposição antes de incorporar preços/orçamento | M01 | P1 | Sequência decidida |
| MPNL-04 | MPNL | Produzir estoques, reposições, disponibilidade e consolidação temporal; depois projeções econômicas | M01 | P1 | Planejado; método pendente |
| CMO-01 | AST | Avaliar conceitos de catálogo DB3K sem copiar código ou assumir equivalência | M01/DB | P2 | Mapeamento parcial secundário |

Requisitos de autenticação, autorização granular, privacidade além da regra de submissões, cópia de segurança, concorrência, acessibilidade, desempenho e implantação não foram especificados; ver documento 09.
