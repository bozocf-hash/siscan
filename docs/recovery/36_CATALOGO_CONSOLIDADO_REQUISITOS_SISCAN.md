# 36 — Catálogo consolidado de requisitos SISCAN

**Atualização de governança:** o registro do responsável em [49 — Decisões APR-01 a APR-20](49_REGISTRO_DECISOES_APR_01_A_APR_20.md) é a fonte para classificar requisitos aprovados conceitualmente, aprovados parcialmente e pendentes. Este catálogo não transforma recomendações em requisitos, não completa detalhes que o responsável deixou em aberto e não autoriza implementação. Onde houver diferença com propostas nos documentos 42–48, prevalece a decisão e ressalva específica registrada em 49.

## Convenções

Os códigos e prioridades abaixo preservam [05](05_REQUISITOS_FUNCIONAIS.md). **P0/P1/P2 são prioridades preliminares do documento 05**, não repriorização feita nesta missão. `Aprovado` significa concepção expressa, não software entregue; `Proposto` é critério sugerido; `Pendente` requer definição; `Não verificado` não tem comprovação funcional. Critérios de aceite marcados **PROPOSTA** precisam ser aprovados pelo responsável.

## Requisitos funcionais por módulo

| Código | Requisito consolidado | Origem | Prioridade registrada | Situação | Dependências | Critério de aceite proposto |
|---|---|---|---|---|---|---|
| GEO-01 | Representar dados espaciais aproveitando capacidades ATLANTICADOR verificadas. | 05 M01 | P0 | Aprovado como concepção; integração não verificada | Revisão técnica/licença, contrato de geometria | **PROPOSTA:** viewer exibe dados aceitos e registra origem/CRS sem tornar visualização fonte oficial. |
| GEO-02 | Validar posição/percurso de navios/submarinos contra máscara vetorial de terra, também em importação e atualização temporal. | 05, 07 | P1 | Aprovado como concepção; dados pendentes | Máscara, resolução, CRS, estados/tempo | **PROPOSTA:** posições e segmentos que cruzam máscara violam a regra; política de margem deve ser configurada/documentada. |
| GEO-03 | Permitir margem costeira configurável. | 05, 07 | P1 | Aprovado como concepção | GEO-02, fonte/resolução | **PROPOSTA:** margem efetivamente aplicada aparece nas configurações e no registro da validação. |
| SYM-01 | Integrar/gerir simbologia Calunga. | 05 | P1 | Pendente de licença e compatibilidade | SYM, autoridade simbólica, origem dos bundles | **PROPOSTA:** cada símbolo registra código/versão/origem; só após liberação documental. |
| AST-01 | Manter modelos, configurações e unidades individuais separadamente. | 05, 07 | P0 | Aprovado como concepção | Identidade, relações, versionamento | **PROPOSTA:** alterar instância não altera modelo/configuração mestre sem ação explícita. |
| AST-02 | Catalogar navios, submarinos, aeronaves, navios-aeródromo, navios-tanque e auxiliares. | 05 | P0 | Aprovado como concepção | Fonte, taxonomia e campos | **PROPOSTA:** cadastro distingue categorias indicadas e armazena fonte/data/referência. |
| AST-03 | Identificar aeronaves individualmente e associá-las a hospedeiro ou base. | 05, 07 | P1 | Aprovado como concepção | AST-01, vínculos temporais | **PROPOSTA:** instância exibe vínculo explicitamente e impede referência inexistente. |
| AST-04 | Rastrear identificador, nome, tipo, aplicabilidade, fonte, data de referência e confiabilidade. | 05, 07 | P1 | Aprovado como princípio; escala pendente | Proveniência e classificação | **PROPOSTA:** campos de proveniência são consultáveis em cada dado sujeito a estimativa. |
| AST-05 | Distinguir cadastro técnico, logístico e econômico no MPNL. | 05, 08 | P1 | Aprovado como concepção | Identidade cruzada do material e vigência | **PROPOSTA:** editar preço não muda identidade/especificação técnica. |
| SCN-01 | Criar e gerir cenários didáticos e versões. | 05, 06 | P0 | Aprovado como concepção; mecanismo pendente | AST, GEO, FOR, DID, versionamento | **PROPOSTA:** exercício registra versão exata do cenário usado; regra de imutabilidade ainda a decidir. |
| FOR-01 | Organizar forças em quatro níveis por ramo conforme decisão registrada. | 05, 07, 08 | P0 | Aprovado; nomenclatura FA provisória | DEC-011, hierarquia e vínculo de unidade | **PROPOSTA:** validar níveis por ramo e assegurar que Exército não acrescente nível subunidade. |
| DID-01 | Instrutor disponibiliza exercício, meios e recursos. | 05 | P0 | Aprovado como concepção | Identidade, SCN, AST, autorização | **PROPOSTA:** aluno autorizado consulta apenas exercício publicado para sua equipe. |
| DID-02 | Aluno compõe forças, registra decisões e justificativas. | 05 | P0 | Aprovado como concepção | FOR, SCN, versionamento e rascunho | **PROPOSTA:** submissão registra autoria, versão-base e justificativa antes de envio. |
| DID-03 | Instrutor avalia submissões e libera visibilidade. | 05 | P0 | Aprovado como concepção; rubrica pendente | DID-04, papéis, avaliação | **PROPOSTA:** avaliação e liberação são ações separadas e auditadas. |
| DID-04 | Aluno não visualiza submissão alheia antes de liberação pelo instrutor. | 05, 07 | P0 | Aprovado como regra; controles pendentes | Backend como autoridade, escopo de equipe | **PROPOSTA:** requisição direta por aluno não autorizado não retorna dados alheios, independente da UI. |
| SIM-01 | Apoiar simulação abstrata com adjudicação humana. | 05, 07 | P1 | Aprovado como concepção; procedimento pendente | DID, NAV, fonte/estado, HIS | **PROPOSTA:** registro distingue hipótese/modelo, decisão humana e resultado, com ator/fundamento. |
| ANA-01 | Consolidar resultados em relatório. | 05 | P0 | Aprovado como concepção; conteúdo pendente | DID, SIM, HIS, rubrica | **PROPOSTA:** relatório aponta exercício/versões/fontes e critérios de avaliação aplicados. |
| NAV-01 | Atualizar posição por posição inicial, velocidade de referência, deslocamento e intervalo temporal. | 05, 07 | P1 | Aprovado como concepção | GEO, relógio e unidades | **PROPOSTA:** atualização registra premissas e valida posição resultante por GEO-02. |
| NAV-02 | Permitir avançar, pausar, retroceder e manter relógio simulado/histórico de posições. | 05, 07 | P1 | Aprovado como intenção; semântica pendente | SIM, HIS, temporalidade | **PROPOSTA:** cada passo/reversão mantém histórico reproduzível sem apagar autoria; comportamento de ramificação precisa decisão. |
| LOG-01 | Calcular consumo por regime de velocidade (navios) e velocidade/altitude (aeronaves), curvas por plataforma/configuração. | 05, 07 | P1 | Aprovado como concepção; parâmetros pendentes | AST, unidade, fonte/confiabilidade | **PROPOSTA:** cada resultado referencia curva/versão e intervalo; valores sem fonte são marcados estimados. |
| LOG-02 | Registrar autonomia/consumo, reserva configurável e alertar limite. | 05, 07 | P1 | Aprovado como concepção; valor/default pendente | LOG-01, unidade temporal | **PROPOSTA:** alerta segue reserva configurada; 30% não é padrão aprovado. |
| LOG-03 | Separar combustível do navio-tanque do saldo transferível. | 05, 07 | P1 | Aprovado como regra | Estoque próprio, transferência e histórico | **PROPOSTA:** transferência reduz estoque transferível e registra origem/destino/quantidade; regra quantitativa pendente. |
| PRC-01 | Permitir indicadores didáticos configuráveis e estudos comparativos com hipóteses explícitas. | 05, 07 | P2 | Aprovado como intenção; critérios pendentes | Avaliação acadêmica, proveniência, HIS | **PROPOSTA:** resultado mostra fatores/hipóteses/versão e não se rotula previsão determinística. |
| HIS-01 | Registrar eventos, alterações e auditoria. | 05, 07 | P1 | Aprovado como intenção; política pendente | Identidade, objetos versionados, retenção | **PROPOSTA:** mudança registrável contém ator, instante, tipo, objeto e referência antes/depois ou motivo conforme sensibilidade. |
| MPNL-01 | Consolidar necessidades ascendentemente, rastreando origem, recursos compartilhados e sem duplicidade. | 05, 07, 08 | P1 | Aprovado — MPNL-001 | Hierarquia FOR/MPNL, item, período, inventário | **PROPOSTA:** total consolidado é decomponível até origens e apresenta compartilhamentos e regra de deduplicação. |
| MPNL-02 | Considerar inventário, manutenção, disponibilidade e ciclo de vida. | 05, 07, 08 | P1 | Aprovado como princípio | Bases técnica/logística, histórico temporal | **PROPOSTA:** necessidade indica quais fontes desses quatro fatores estavam disponíveis ou ausentes. |
| MPNL-03 | Calcular necessidade/reposição antes de preços/orçamento. | 05, 08 | P1 | Aprovado — sequência metodológica | Demanda, estoque, disponibilidade | **PROPOSTA:** relatório técnico/logístico pode ser consolidado sem preços; orçamento referencia quantidades já consolidadas. |
| MPNL-04 | Produtos incluem estoques, reposições, disponibilidade e consolidação temporal; economia vem depois. | 05, 08 | P1 | Planejado; método pendente | MPNL-01–03, períodos, dados | **PROPOSTA:** cada projeção identifica período, premissas e lacunas. |
| CMO-01 | Avaliar conceitos de catálogo DB3K sem copiar código nem assumir equivalência. | 05, 04, 13–14 | P2 | Proposto/avaliação documental | Semântica, unidades, licença, estabilidade | **PROPOSTA:** cada campo candidato só é aceito com fonte autoritativa, unidade e semântica confirmadas. |

## Requisitos não funcionais

Os documentos existentes não especificam níveis mensuráveis de desempenho, disponibilidade ou recuperação. A tabela separa princípios decididos de recomendações propostas.

| ID | Aspecto | Estado documentado | Origem/dependências | Critério de aceite (proposta, não aprovado) |
|---|---|---|---|---|
| RNF-SEG-01 | Segurança | **DECIDIDO:** não operacionalizar; autorização oficial no backend; segregação DID obrigatória. Implementação técnica pendente. | 07 DID-001; Missão 03 §7; 29–34 | **PROPOSTA:** testes autorizados comprovam negação de acesso no servidor e registro de ações sensíveis. |
| RNF-AUT-01 | Autenticação/autorização | **PENDENTE** perfis, permissões e recuperação; perfis instrutor/aluno/avaliador/admin constam em 02. | 02, 09 P-09, 34 | **PROPOSTA:** cada papel tem matriz de capacidade revisada e aplicada no backend. |
| RNF-AUD-01 | Rastreabilidade/auditoria | **DECIDIDO** em intenção; retenção/acesso/imutabilidade pendentes. | 05 HIS-01, 07, 09 | **PROPOSTA:** ações de domínio e transições de exercício possuem ator/data/objeto/origem consultáveis. |
| RNF-PERF-01 | Desempenho | **NÃO ESPECIFICADO** | 09/16–34 | **PROPOSTA:** metas por fluxo, tamanho de cenário e concorrência definidas antes de aceite. |
| RNF-DISP-01 | Disponibilidade | **NÃO ESPECIFICADO** | 09 | **PROPOSTA:** disponibilidade/indisponibilidade e continuidade definidas para o contexto acadêmico. |
| RNF-DAD-01 | Integridade dos dados | **DECIDIDO** preservar origem/confiabilidade e impedir duplicidade MPNL; mecanismos gerais pendentes. | 07,08,Missão 03 §10 | **PROPOSTA:** validação de esquema, revisão/versão e restrições de domínio documentadas por entidade. |
| RNF-VER-01 | Versionamento | **DECIDIDO** cenário/modelos precisam proveniência; política exata pendente. | 05 SCN-01, 13–14 CMO apenas referência | **PROPOSTA:** exercício referencia versão congelada de cenário, parâmetros e fonte. |
| RNF-UX-01 | Usabilidade | **PROPOSTO** preservar recursos cartográficos ATLANTICADOR e separar UI didática; requisitos de acessibilidade não definidos. | 19,29–34 | **PROPOSTA:** tarefas por perfil e requisitos de acessibilidade aprovados e avaliados. |
| RNF-MAN-01 | Manutenibilidade | **PROPOSTO** módulos/interfaces explícitos e adaptadores; stack ainda não aprovada. | 34, 38 | **PROPOSTA:** módulos possuem limites, contratos e testes independentes definidos em projeto autorizado. |
| RNF-INT-01 | Interoperabilidade | **PENDENTE** formatos/CRS/contratos; CMO, DB3K e ATLANTICADOR não equivalentes. | 04, 21, 25, 32 | **PROPOSTA:** formatos suportados e regras de perda/proveniência documentados e testados. |
| RNF-POR-01 | Portabilidade | **NÃO ESPECIFICADO** além de proposta de manter stack existente. | 16,34 | **PROPOSTA:** plataformas/navegadores e condições offline/rede aprovados. |
| RNF-REC-01 | Recuperação/backup | **PENDENTE** política de backup e restauração de dados SISCAN. | 09,10 | **PROPOSTA:** política RPO/RTO/backup/restauração definida com exercícios de recuperação autorizados. |

## Observações de consistência

Critérios de aceite são propostas nesta missão porque 05 registra requisitos sem critérios verificáveis. Não se criou prioridade nova. Requisitos que dependem de dados, licenças ou decisões permanecem pendentes mesmo quando o conceito foi decidido. MPNL-001 e os níveis de FOR em 08 não foram alterados; PRC/SIM continuam didáticos e humanos conforme 35.
