# Mapa de capacidades — conclusão do backend SISCAN

**Estado: Fase 0 original aprovada pelo responsável em 2026-11-11**, por resposta expressa “aprovado”. Complemento de confronto/estado operativo registrado posteriormente em [80](docs/recovery/80_CONFRONTO_FORCAS_E_ESTADO_OPERATIVO.md), por nova instrução expressa, com faixas confirmadas. A decomposição/dependências desse complemento ficam propostas para revisão; preservadas as aprovações das capacidades anteriores e de `technical-catalog`. Não aprova automaticamente especificações individuais, valores Command ou implementação.

## Premissas e base documental

- Preservar o backend existente e os cinco domínios conceituais aprovados: cartográfico, didático, técnico, logístico e histórico. Os IDs abaixo identificam capacidades de trabalho; não renomeiam AST/FOR/SCN/GEO/LOG/NAV/HIS/MPNL nem exigem novos serviços ou bancos.
- Refinamento visual fica para depois. Consumidores gráficos já existentes continuam atendidos por contratos do backend.
- Manter autoridade do backend, acesso por partido, identidades estáveis, histórico e arbitragem humana. O operador cria/distribui unidades respeitando os meios adjudicados ao partido; não recebe inventário ilimitado.
- Usar Ponytail: reaproveitar código e bibliotecas existentes, especificar a menor fatia completa, evitar abstrações/dependências sem necessidade. A organização documental não determina uma reescrita.
- Ensaios sintéticos não aprovam valores Command. Validação é por recorte/capacidade: não exigir validar todo o catálogo antes de continuar casos controlados.

Inventário-base confirmado na Fase 0: **79 arquivos Markdown em `docs/recovery/` (00–78)**, anterior aos complementos 80/81. O índice é [00](docs/recovery/00_LEIA-ME_RECUPERACAO.md), com inventário de fontes em [11](docs/recovery/11_INVENTARIO_FONTES.md). Esta contagem não representa releitura integral dos 79 arquivos nesta etapa.

Fundamentação: decisões/requisitos/modelo/arquitetura/interfaces em 35–39; decisões APR em 49; adjudicação por partido em 51; autoridade de promoção em 53; parecer de dados em 69; entregas/limitações posteriores em 70–78. Os avisos de proibição de implementação nas antigas missões documentais são históricos, conforme 00 e autorizações posteriores. Propostas antigas não prevalecem sobre decisões expressas posteriores.

Cada futura especificação deverá citar requisito/decisão/documento e distinguir **decidido, implementado, parcial e pendente**. Conflito real entre fontes será registrado para resolução antes da implementação afetada. Não transformar descrição do CMO em requisito SISCAN nem preencher lacunas por inferência não identificada.

## Capacidades propostas

Dependências indicam contratos de provedores. Implementação já disponível será preservada e verificada, não refeita automaticamente.

| ID estável | Responsabilidade restante | Depende de | Referências de partida em docs/recovery |
|---|---|---|---|
| `technical-catalog` | Validar unidades, semântica, domínios, origem e aprovação dos atributos por recorte técnico | — | 04, 53, 65–69 |
| `unit-registry` | Ligar modelo/configuração/componentes a unidades individuais e snapshots, além do recorte sintético | `technical-catalog` | 37, 46, 49 APR-10, 71 |
| `party-inventory` | Controlar adjudicação, quantidades e criação de instâncias pelo operador sem duplicações | `unit-registry` | 49, 51, 76 |
| `execution-core` | Consolidar estado, relógio, comandos idempotentes, revisões e histórico de execução | `unit-registry` | 49, 70–73 |
| `support-network` | Cadastrar apoios, posições, capacidades, compatibilidade e vínculos planejados/efetivos | `party-inventory` | 49 APR-12/14, 76–78 |
| `operational-state` | Definir disponibilidade/avarias, condição de origem e restrições efetivas por recursos; preservar efeitos confirmados pelo instrutor | `execution-core`, `resource-engine` | 35 DEC-019, 49, 69, 78, 80–81 |
| `resource-engine` | Aplicar consumo por perfil, estoques e reabastecimento; fornecer indicadores de munição/combustível e pré-alerta M+5 pontos | `execution-core`, `party-inventory`, `technical-catalog` | 67–69, 72, 74–75, 81 |
| `movement-engine` | Integrar trajetórias, marchas, tempo e consumo, respeitando vínculos e confirmações | `support-network`, `resource-engine`, `operational-state` | 49 APR-04/12/14/16, 76–78 |
| `force-confrontation` | CPC — Comparação de Poderes Combatentes: contrapor composições, apoiar apuração e arbitragem direta; resultado oficial sempre do instrutor | `unit-registry`, `party-inventory`, `operational-state` | 35 DEC-018/019, 49, 80–82 |
| `mpnl-needs` | Consolidar necessidades logísticas por escalão, origem e recursos compartilhados | `support-network`, `resource-engine`, `operational-state` | 08, 49 APR-17/18, 69 |
| `verification-recovery` | Verificar integração, concorrência, restauração e calibração dos recortes entregues | Capacidades anteriores | 09, 10, 69–78 |

`verification-recovery` é uma frente transversal de verificação, não um novo domínio funcional ou serviço. Testes e preservação já são obrigatórios em cada capacidade; não ficam adiados para essa frente final. Avaliação didática, autenticação/permissões e relatórios existentes permanecem como base compartilhada; mudanças neles exigem escopo próprio.

## Ordem proposta para revisão

1. `technical-catalog` → `unit-registry` → `party-inventory`.
2. Com esses contratos disponíveis, `execution-core` e `support-network`.
3. `resource-engine` → `operational-state`: complemento de dependência proposto em 81 para condição efetiva por recursos. Preservar a avaliação de origem do instrutor.
4. `force-confrontation`, `movement-engine` e `mpnl-needs`, respeitando suas dependências. Inclusão de `force-confrontation` é complemento proposto; sua ordem não obriga esperar o motor de movimento para testar adjudicação didática controlada.
5. Consolidação de `verification-recovery`, com verificações já executadas em cada entrega.

A ordem é lógica de dependências, não calendário nem proibição de desenvolver ensaios sintéticos independentes. A Fase 0 foi concluída antes de escrever especificações de módulo. A primeira especificação, `SPEC-technical-catalog.md`, foi aprovada posteriormente, com recorte inicial de combustível/consumo aéreo.

## Gates do catálogo e evolução posterior

Gates de Fase 0, especificação [SPEC-technical-catalog.md](SPEC-technical-catalog.md) e plano [tasks/plan.md](tasks/plan.md) satisfeitos por aprovações distintas do responsável. Tarefas propostas para revisão de Fase 3 em [tasks/todo.md](tasks/todo.md); implementação ainda não iniciada. As demais especificações serão produzidas por módulo em ordem de dependências.

O mapa original foi produzido como proposta documental. Entregas posteriores e suas verificações são registradas abaixo; o status do catálogo não é uma afirmação de ausência de código nos ensaios autorizados depois.

Pesquisa conceitual do CPC em [82](docs/recovery/82_PESQUISA_E_PROPOSTA_CONCEITUAL_CPC.md) e proposta de algoritmo em [83](docs/recovery/83_ALGORITMO_CONCEITUAL_CPC_REFERENCIA_COMMAND.md). O nome funcional CPC foi solicitado pelo responsável; o ID `force-confrontation` é preservado. Os estudos não são especificação/algoritmo aprovado nem alteram a autoridade do instrutor. Relação CPC/PRC/SIM deve ser esclarecida na especificação própria.

Autorização posterior específica para o ensaio isolado de classes, disparo, rodadas e consumo defensivo registrada em [84](docs/recovery/84_CPC_RODADAS_INICIATIVA_E_CONSUMO_DEFENSIVO.md), com código entregue e 28 testes. Isso não implementa a integração oficial de `force-confrontation` nem satisfaz os gates pendentes de `technical-catalog`.

Complemento solicitado de detecção, contatos e alcance implementado no ensaio estático em [85](docs/recovery/85_CPC_DETECCAO_CONTATOS_E_ALCANCE.md), com 47 testes. A geometria/rubrica é sintética, sem aprovação de eficácia real ou integração ao exercício oficial.

Loop de um minuto solicitado e entregue em [86](docs/recovery/86_CPC_TURNOS_COMBUSTIVEL_E_MOVIMENTO.md): consumo aéreo, reserva explícita, evasão/perda proposta e movimento planar, com 63 testes. É ensaio em memória; não substitui `execution-core`/`resource-engine` oficiais, não integra bases ou altera decisões de promoção de dados.

Ratificação posterior em [87](docs/recovery/87_REGRA_ESGOTAMENTO_COMBUSTIVEL_POR_DOMINIO.md): consumo não aéreo constante e regra de combustível zerado por domínio, com 69 testes. Superfície/terrestre imobilizam; aéreo em voo tem perda no ensaio para adjudicação. Não altera os IDs das capacidades ou aplica efeitos oficiais.

Logging e exportação pós-ação entregues em [88](docs/recovery/88_CPC_LOGGING_E_RELATORIO_POS_ACAO.md), com 81 testes e 60 turnos/314 eventos demonstrativos. Artefatos locais são resultados propostos, sem adjudicação ou alteração das dependências entre capacidades.

## Complemento de escopo — grupamentos e dados descritivos

**Recorte implementado em 2026-11-16 — [93](docs/recovery/93_ENTREGA_GRUPAMENTOS_EM_MEMORIA.md).** Escopo de [89](docs/recovery/89_ESCOPO_GRUPAMENTOS_E_DADOS_DESCRITIVOS_CPC.md), [especificação](SPEC-unit-registry.md), [plano](tasks/unit-registry/plan.md) e [tarefas](tasks/unit-registry/todo.md) receberam aprovações distintas. UGR-01–UGR-06 concluídas: registro de grupos diretos navais/aéreos por exercício/partido, versões imutáveis, recibos, exclusividade de vínculo, arquivamento e preparação com disponibilidade atual. Passaram 29 testes do registro, 81 CPC e `check_engine_units.py`. Sem API, persistência ou confronto integrado entre grupos.

Manter IDs/dependências: `technical-catalog` fornece evidência/consulta; `unit-registry` conserva identidades e composições; `party-inventory` fornece disponibilidade; `force-confrontation` poderá consumir os snapshots em uma integração própria, preservando o resultado oficial do instrutor. Não há inferência de escalão MPNL, aprovação de valores reais ou composição otimizada. Inspeção descritiva de sensores em 89 não valida semântica/eficácia. Documentos 89–92 são históricos; gates desta fatia concluídos conforme 93. O ciclo independente e os planos abertos de `technical-catalog` permanecem preservados.

## Preparação entregue em force-confrontation

[Especificação](SPEC-force-confrontation.md), [plano](tasks/force-confrontation/plan.md) e [tarefas](tasks/force-confrontation/todo.md) aprovados. Dossiê inicial AZUL/VERMELHO implementado e verificado em [98](docs/recovery/98_ENTREGA_PREPARACAO_CPC_GRUPAMENTOS.md): autorização interna, manifesto de composição, snapshots integrais e hash, sem execução, persistência ou efeito oficial. Passaram 131 testes distintos (102 CPC incluindo 21 novos, mais 29 do registro). Dependências/IDs e trabalho independente de `technical-catalog` preservados. Documentos 94–96 registram a preparação histórica; gates desta fatia concluídos.

Concepção gráfica em [97](docs/recovery/97_CONCEPCAO_GRAFICA_DISPOSICAO_E_CONFRONTO.md): requisito expresso de reutilizar o mapa ATLANTICADOR já definido. Disposição/composição consomem identidade, inventário e posições existentes; visualização CPC consome eventos/propostas; estado oficial permanece no provedor autorizado. Sem novo mapa, módulo paralelo ou alteração de dependências. A composição gráfica foi implementada posteriormente em 102; execução/reprodução/adjudicação do confronto permanecem pendentes.

## Extensão entregue de unit-registry no mapa

Recorte 2 de [SPEC-unit-registry.md](SPEC-unit-registry.md), [plano](tasks/unit-registry/mapa/plan.md) e [tarefas](tasks/unit-registry/mapa/todo.md) aprovados e executados. [Entrega 102](docs/recovery/102_ENTREGA_GRUPAMENTOS_NO_MAPA.md): grupos temporários no mapa ATLANTICADOR existente, identidade explícita, rotas autorizadas, painel/realce/enquadramento/arquivo. Passaram 54 testes nomeados, verificadores assertivos de mapa/silhuetas e navegador real isolado. Catálogo não vira inventário elegível sem instância/snapshot/domínio; sem DDL, persistência ou segundo mapa. IDs/dependências e entregas 93/98 preservados.

[Roteiro do instrutor 103](docs/recovery/103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md): composição gráfica implementada; seleção de par, conferência na tela, execução temporal/replay e confirmação/aplicação oficial de efeitos ainda não integrados. O dossiê 98 é backend disponível para uma próxima fatia. Prévia isolada não significa atualização automática do processo principal em 8787. Não reabrir gates concluídos de 99–101.

## Proposta de ligação mapa, ensaio e decisão

[104](docs/recovery/104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md) propõe fechar primeiro julgamento didático completo e depois ligar ensaio automático com entradas/regras verificadas. IDs preservados: `force-confrontation` prepara/propõe e consome o contrato de `operational-state`; `operational-state` publica efeitos autorizados por unidade; `execution-core` fornece contexto/revisões e suporte transacional/histórico; `unit-registry`/`party-inventory` fornecem composições/disponibilidade. O provedor de estado não executa/importa o modelo de confronto; sem ciclo ou segundo mapa.

Ordem de implementação proposta: seleção/conferência do par → contrato/armazenamento durável de adjudicação/estado → julgamento didático com confirmação e aplicação → automático como produtor de proposta. Mudança oficial de estado não será implementada em registro temporário nem acoplada ao ledger de combustível por atalho. Este complemento de escopo/ordem foi aprovado por “si”; não reabre gates das entregas 93/98/102.

Primeira especificação da ligação em [105](docs/recovery/105_ESPECIFICACAO_PAR_CPC_NO_MAPA.md), Recorte 2 de [force-confrontation](SPEC-force-confrontation.md): seleção do par e conferência do dossiê no mapa, com vista simultânea exclusiva do instrutor e manifesto geográfico separado. Fase 1 aprovada por “siga”; [plano de Fase 2](tasks/force-confrontation/mapa/plan.md) aprovado por “sim”. [Lista de Fase 3](tasks/force-confrontation/mapa/todo.md) proposta conforme [107](docs/recovery/107_TAREFAS_PAR_CPC_NO_MAPA.md), aguardando revisão. Sem implementação, DDL ou efeitos. Estado/adjudicação durável e julgamento/confirmação permanecem as próximas etapas da ordem aprovada, sem dependência circular ou novo mapa.


## Atualização — 2026-11-17: conferência CPC no mapa entregue

[108](docs/recovery/108_ENTREGA_PAR_CPC_NO_MAPA.md) conclui o Recorte 2 de `force-confrontation`: seleção explícita de grupos AZUL/VERMELHO pelo instrutor e consulta simultânea no mapa ATLANTICADOR. Revalidação de identidade/revisões/snapshots/adjudicação/posições, manifesto geográfico separado e ausência de efeitos verificados. Passaram 73 testes nomeados, dois verificadores assertivos e inspeção gráfica isolada. Gates de 104–107 satisfeitos; [roteiro 103](docs/recovery/103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md) atualizado.

Preparação não executa nem confirma confronto. Estado/adjudicação durável, julgamento didático e confirmação/aplicação oficial seguem próximos contratos de 104; execução/replay por grupamentos continua futura. Registro temporário e elegibilidade aérea sintética do provedor preservados; nenhuma aprovação de eficácia Command ou alteração dos planos independentes de catálogo.


## Atualização — 2026-11-17: especificação de estado/adjudicação

[109](docs/recovery/109_ESPECIFICACAO_ESTADO_E_ADJUDICACAO_DURAVEL.md) propõe a Fase 1 de `operational-state`, seguindo a etapa 2 já aprovada em 104. [SPEC-operational-state.md](SPEC-operational-state.md) define estado por unidade, proposta/decisão/efeitos duráveis, acesso por partido, confirmação transacional e recuperação. Não importa o algoritmo CPC; futuros consumidores usam o mesmo provedor de publicação. Especificação aprovada por “siga”; plano proposto em 110 antes de tarefas/código/migração; conferência no mapa de 108 permanece entregue. Não aprova valores Command, regras de armamento ou implementação antecipada.


## Atualização — 2026-11-17: plano de estado/adjudicação

[110](docs/recovery/110_PLANO_ESTADO_E_ADJUDICACAO_DURAVEL.md) registra a aprovação da especificação `operational-state` e propõe seu [plano técnico](tasks/operational-state/plan.md). Inclui persistência aditiva, identidade/domínio comprovados, propostas/decisões/efeitos/recibos, transações, autorização e recuperação. Fase 2 aprovada por “aprovado”; lista de Fase 3 proposta em 111 antes da implementação. Nenhum código ou banco alterado; integração de julgamento ao mapa e produtor automático continuam futuros.


## Atualização — 2026-11-17: tarefas de estado/adjudicação

[111](docs/recovery/111_TAREFAS_ESTADO_E_ADJUDICACAO_DURAVEL.md) registra o plano aprovado e propõe [OST-01–10](tasks/operational-state/todo.md), com dependências/aceites/verificações e checkpoints A–D. Especificação e plano não aguardam nova aprovação. Revisão da lista precede código; migração somente isolada, sem implementação gráfica ou produtor automático nesta fatia.
