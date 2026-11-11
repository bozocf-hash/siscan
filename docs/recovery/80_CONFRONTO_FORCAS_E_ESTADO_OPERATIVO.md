# 80 — Confronto de forças e estado operativo

**Decisões complementares do responsável — 2026-11-11.** Requisito acrescentado durante a revisão das tarefas de `technical-catalog`. Este documento registra escopo funcional; não é especificação técnica aprovada nem implementação. Número 79 está reservado, na lista de tarefas, ao relatório futuro do catálogo técnico.

## Finalidade e autoridade

SISCAN também deve permitir contrapor a composição de forças dos partidos Azul e Vermelho e apoiar sua avaliação por critérios explícitos. O operador poderá definir/configurar a funcionalidade de confronto, com parâmetros e limites a detalhar. Isso não lhe concede autoridade para publicar resultados oficiais ou modificar o estado operativo decorrente de confronto por conta própria.

O **resultado oficial sempre será definido pelo instrutor**, nos dois caminhos:

1. Confronto apoiado pelo sistema: critérios/modelo produzem uma apuração ou proposta, que o instrutor pode adotar, ajustar ou rejeitar.
2. Arbitragem didática direta: o instrutor escolhe os resultados/efeitos que deseja aplicar aos meios/forças, sem depender de cálculo automático prévio.

Ambos devem produzir efeitos rastreáveis no estado operativo, com autoria, momento/execução, unidades envolvidas, antes/depois e referência ao confronto ou à intervenção didática. Preservar justificativa quando informada. Resultado calculado, resultado confirmado e efeito aplicado são registros distintos; não aplicar proposta automaticamente.

Relaciona-se a 35 DEC-001/018/019, 49 e aos domínios SIM/PRC/HIS. Mantém arbitragem humana e finalidade didática. Não adotar fórmulas CMO/ATLANTICADOR como se já fossem critérios SISCAN aprovados.

## Índice e condições dos meios de superfície

O responsável definiu três condições e confirmou explicitamente os limites por pergunta/resposta na conversa:

| Índice de estado operativo | Condição | Cor |
|---|---|---|
| Acima de 60% até 100% | Combater | Cor normal, a definir no leiaute |
| De 40% a 60%, incluindo exatamente 40% e 60% | Navegar | Laranja |
| Abaixo de 40%, no domínio de 0% a 100% | Flutuar | Vermelho |

Exemplo solicitado: 80% aparece em barra, com valor e condição “Combater”. Usar texto/valor junto da cor, garantindo compreensão sem depender apenas da percepção de cores.

Tratar como índice de **estado operativo** no exercício; não é porcentagem de combustível, probabilidade de vitória, massa de armamento ou atributo físico bruto do DB3K. Sem avaliação registrada, apresentar “estado operativo não avaliado”; não presumir 100% ou usar zero no lugar de ausência. Definição do método de obtenção do índice continua pendente, respeitando a confirmação final do instrutor.

Não criar automaticamente uma quarta condição “afundado/destruído” a partir desse índice: o responsável pediu três. A relação de efeitos extraordinários com essas condições deve ser especificada separadamente. Não generalizar “navegar/flutuar” para aeronaves, meios terrestres ou estado agregado da força.

## Uso e visualização

Ao passar o mouse sobre meio ou força autorizados, a ficha deve indicar efeitos/impactos confirmados, estado conhecido, fonte/autoridade e sua referência temporal. Para meio de superfície avaliado, mostrar índice percentual, barra, cor e condição derivada das faixas acima. Não apresentar apuração ainda não confirmada como estado atual.

O estado operativo deve orientar os módulos que autorizam o emprego do meio. Os efeitos concretos sobre movimento, combate, sensores, armamento ou logística serão definidos em suas especificações; não inventar redução proporcional de velocidade, consumo ou alcance a partir do percentual.

Para forças, composição e estados dos membros devem ser rastreáveis à versão utilizada. O responsável ainda não definiu fórmula para índice agregado: **não calcular média simples nem aplicar automaticamente as faixas individuais à força inteira**. Registrar essa pendência ao especificar a ficha de força.

Manter APR-06: comparação autorizada não abre consulta livre aos dados do adversário. O serviço pode precisar de informações disponíveis ao instrutor sem divulgá-las aos operadores. Papéis, visibilidade de propostas e permissões de parametrização devem ser especificados.

## Separação de capacidades e dependências

- `operational-state`: contrato de estado/efeito confirmado, índice, classificação por faixa e histórico; valida autoridade do instrutor para efeitos de confronto/arbitragem.
- `force-confrontation`: composição contraposta, critérios configuráveis, apuração/proposta e confirmação pelo instrutor; consome o contrato de estado/efeitos.
- A mudança confirmada é aplicada pelo provedor de estado, em transação rastreável e idempotente. O estado não depende da implementação interna do modelo de confronto: intervenção didática direta também usa o mesmo contrato de efeitos.
- `technical-catalog` fornece atributos técnicos elegíveis como subsídio, quando cabíveis; não aprova critérios didáticos nem determina resultados oficiais. O índice não será incorporado ao catálogo como valor técnico original.

Essa separação evita ciclo de módulos: confronto consulta/solicita efeitos ao provedor de estado; o provedor não precisa conhecer ou executar o modelo de confronto para aplicar uma intervenção autorizada.

## Pendências de especificação

1. Critérios/modelos, dados necessários, pesos e limites configuráveis pelo operador, distinguindo critérios aprovados de hipóteses.
2. Procedimento de confirmação/ajuste do instrutor, visibilidade das propostas e tratamento de comandos concorrentes/repetidos.
3. Índice agregado e representação da força; efeitos e estados específicos de outras naturezas de meio.
4. Efeitos concretos das condições sobre ações autorizadas do motor, mantendo exceções didáticas explícitas e histórico.
5. Testes das fronteiras: 100, 80, imediatamente acima de 60, 60, imediatamente abaixo de 60, 40, imediatamente abaixo de 40, zero, ausência e entradas fora do domínio. Testar também recusa de resultado oficial por operador e ausência de aplicação automática de proposta.

## Limite desta entrega

Somente documentação e atualização do mapa de capacidades. Nenhum confronto, índice, cor, estado, schema ou resultado foi implementado/aplicado nesta etapa. A aprovação das faixas não homologa um algoritmo de confronto nem substitui as decisões anteriores do projeto.
