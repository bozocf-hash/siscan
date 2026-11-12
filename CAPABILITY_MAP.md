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

## Próximo gate

Gates de Fase 0, especificação [SPEC-technical-catalog.md](SPEC-technical-catalog.md) e plano [tasks/plan.md](tasks/plan.md) satisfeitos por aprovações distintas do responsável. Tarefas propostas para revisão de Fase 3 em [tasks/todo.md](tasks/todo.md); implementação ainda não iniciada. As demais especificações serão produzidas por módulo em ordem de dependências.

Nesta etapa não houve alteração de código, schema, dados, dependências ou servidor. Não foram executados testes de software por ser uma proposta documental.

Pesquisa conceitual do CPC em [82](docs/recovery/82_PESQUISA_E_PROPOSTA_CONCEITUAL_CPC.md) e proposta de algoritmo em [83](docs/recovery/83_ALGORITMO_CONCEITUAL_CPC_REFERENCIA_COMMAND.md). O nome funcional CPC foi solicitado pelo responsável; o ID `force-confrontation` é preservado. Os estudos não são especificação/algoritmo aprovado nem alteram a autoridade do instrutor. Relação CPC/PRC/SIM deve ser esclarecida na especificação própria.

Autorização posterior específica para o ensaio isolado de classes, disparo, rodadas e consumo defensivo registrada em [84](docs/recovery/84_CPC_RODADAS_INICIATIVA_E_CONSUMO_DEFENSIVO.md), com código entregue e 28 testes. Isso não implementa a integração oficial de `force-confrontation` nem satisfaz os gates pendentes de `technical-catalog`.

Complemento solicitado de detecção, contatos e alcance implementado no ensaio estático em [85](docs/recovery/85_CPC_DETECCAO_CONTATOS_E_ALCANCE.md), com 47 testes. A geometria/rubrica é sintética, sem aprovação de eficácia real ou integração ao exercício oficial.

Loop de um minuto solicitado e entregue em [86](docs/recovery/86_CPC_TURNOS_COMBUSTIVEL_E_MOVIMENTO.md): consumo aéreo, reserva explícita, evasão/perda proposta e movimento planar, com 63 testes. É ensaio em memória; não substitui `execution-core`/`resource-engine` oficiais, não integra bases ou altera decisões de promoção de dados.
