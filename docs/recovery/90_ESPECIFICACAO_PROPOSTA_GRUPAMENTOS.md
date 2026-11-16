# 90 — Especificação aprovada de grupamentos

**Data: 2026-11-16. Estado: especificação de Fase 1 aprovada por “sim”.** O responsável havia aprovado o escopo de 89 por “pode seguir”. A especificação completa está em `SPEC-unit-registry.md`, na raiz do repositório e na pasta de entrega SISCAN. Plano de Fase 2 posteriormente proposto em `tasks/unit-registry/plan.md`, local escolhido pelo responsável na opção 1; resumo em [91](91_PLANO_PROPOSTO_GRUPAMENTOS.md). Nenhum código ou lista detalhada de implementação foi iniciado.

## Primeira entrega proposta

Módulo de domínio em memória para criar, revisar, consultar, arquivar e preparar composição de grupamentos diretos navais/aéreos. Classes diferentes preservam suas referências individuais. Não haverá nesta fatia tela, HTTP, persistência ou simulação de enfrentamento de múltiplos grupos.

Preservar IDs SISCAN e snapshots existentes; disponibilidade conferida por visão de inventário do partido; versões imutáveis, hashes e reenvio idempotente enquanto o processo estiver ativo. Nenhuma contagem coletiva cria combustível/armamentos ou promove dados reais.

Regra aprovada: exclusividade de uma unidade em um vínculo operativo direto ativo no mesmo exercício/partido. Arquivar cria versão inativa, libera essa exclusividade e mantém o histórico. Hospedagem em base/porta-aviões e hierarquia orgânica são relações diferentes e não são alteradas.

“Esquadrilha” permanece designação operacional, sem renomear os quatro níveis aéreos provisórios de 08 ou inferir sua correspondência. O primeiro recorte permite cadastro sem esse vínculo MPNL; hierarquia completa e subgrupos são evoluções posteriores.

## Aceite e limites

A especificação define contratos de dados/operações, fronteiras dos provedores, erros, comandos completos, estilo e 15 critérios UG-01–UG-15. Cobrem composição heterogênea, pertencimento, disponibilidade, snapshots, não duplicidade, revisão, reenvio, imutabilidade, consulta contextual e arquivamento.

Autenticação real continua no backend: fornecer um campo de perfil no pedido não concede autorização. O módulo em memória não substitui autorização, persistência, recuperação após reinício ou aprovação de atributos de 53.

## Próximo gate

Revisão do plano técnico de Fase 2, sem reabrir o contrato já aprovado. A futura lista de Fase 3 ficará no diretório do módulo, sem sobrescrever as tarefas abertas de `technical-catalog`. Plano antigo e novo permanecem independentes.

Verificação desta etapa: revisão documental e conferência dos links. Não houve execução de testes de software por ausência de alteração de código; a especificação não afirma que `check_unit_groups.py` já existe.
