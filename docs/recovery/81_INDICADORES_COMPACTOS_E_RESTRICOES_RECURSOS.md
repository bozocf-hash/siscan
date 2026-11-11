# 81 — Três indicadores compactos e restrições por recursos

**Decisões complementares — 2026-11-11.** Requisito documental recebido após 80; não implementa barras, consumo, limiares novos ou mudanças de estado na aplicação.

## Ficha resumida

O responsável solicitou três barras compactas na ficha do meio, evitando caixa extensa que cubra o mapa:

1. Estado operativo: índice/condição confirmados pelo instrutor, conforme 80.
2. Armamento geral: um único indicador resumido, sem uma barra por arma no hover.
3. Combustível: indicador com mínimo escolhido pelo operador e pré-alerta fixo.

Mostrar rótulo curto, percentual conhecido e cor; condição efetiva e motivo de restrição em texto sucinto. Detalhes e histórico ficam na ficha expandida, sem expandir automaticamente o hover. Dimensões/leiaute serão validados depois, conforme prioridade atual do backend. Não depender somente de cor para comunicar a condição.

Indicador desconhecido aparece como não informado/não avaliado, sem preenchimento automático em zero ou 100%. As barras são variáveis diferentes; não transformar uma em outra.

## Combustível — regra confirmada explicitamente

O mínimo **M** é definido pelo operador, sem padrão de 30% ou 40%. O responsável rejeitou um segundo limite configurável: a antecipação é fixa de **5 pontos percentuais**, não 5% relativos ao mínimo.

| Percentual de combustível F | Indicação |
|---|---|
| F > M + 5 | Verde |
| M < F <= M + 5 | Laranja, pré-alerta na ficha |
| F <= M | Vermelho, mínimo atingido/ultrapassado |

Exemplos confirmados: M=30% → pré-alerta em 35%; M=40% → pré-alerta em 45%. Exatamente no mínimo já é vermelho, coerente com o alerta `saldo <= mínimo` de 75. Na ausência de mínimo configurado, indicar essa ausência; não inventar M=30% ou M=0%.

Percentuais são comparáveis somente com denominador e unidade conhecidos. Proposta para especificação: usar capacidade de combustível validada da configuração/snapshot como 100%, mantendo saldo e mínimo absolutos rastreáveis. O protótipo existente de 75 guarda mínimo em kg/gramas: esta decisão **não migra silenciosamente valores para percentuais**. A integração deve declarar a base, a versão e a conversão; sem capacidade comprovada, não fabricar percentual. Não converter litros, kg ou energia entre si sem evidência.

O pré-alerta deve ser derivado do mínimo, sem novo ajuste independente. Se M+5 ultrapassar 100%, o intervalo fisicamente possível pode já começar em pré-alerta; não criar valores de combustível acima da capacidade ou alterar o mínimo automaticamente. Testar bordas 0/100 e ausência de configuração na futura especificação.

Permanece 75: mínimo é alerta, não um bloqueio automático adicional de consumo. O responsável não determinou, nesta decisão, mudança automática da condição operativo-naval por combustível baixo. Esgotamento, impossibilidade de executar intervalo e seus efeitos continuam em contratos próprios.

## Armamento geral

O hover mostra nível geral, mas o backend deve conservar estoques por tipo/configuração, para calcular/justificar o resumo. Simplificar a exibição não autoriza misturar contagens de munições heterogêneas, apagar a rastreabilidade ou representar estoque inexistente como armamento disponível.

O responsável exemplificou cores/faixas semelhantes às do estado operativo. **Regra funcional expressa:** quando o armamento cair abaixo do limiar de combate, um meio que poderia “Combater” fica restrito a “Navegar”. Foi citado **30% como exemplo**; fixação/configurabilidade desse limiar e método de agregação ainda precisam ser definidos na especificação. Não instituir 30% universal a partir de um exemplo.

Definir a referência de 100% (configuração/carga de referência aprovada) e a regra de agregação, inclusive armas incompatíveis com o confronto, munição indisponível e falta de uma arma essencial. Não adotar soma simples de projéteis ou média de percentuais sem decisão. Reabastecimento não pode redefinir silenciosamente o denominador para fazer qualquer estoque parecer 100%.

Faixas de cor detalhadas da barra de armamento ainda precisam de confirmação: “mesmos critérios” é indicação de alinhamento, não aprovação de regra de combustível aplicada à munição. Não usar o limiar de mínimo do operador para combustível como limiar de armamento.

## Condição de origem e restrição efetiva

Preservar o índice/estado operativo resultante da avaliação ou confronto confirmado pelo instrutor. Separar esse registro da restrição automática de emprego por falta de recursos, agora expressamente solicitada.

Exemplos conceituais, usando o limiar de armamento de 30% citado:

| Condição de origem | Armamento geral | Condição/restrição efetiva |
|---|---|---|
| Combater | 20% | Navegar; combate bloqueado por armamento insuficiente |
| Navegar | 20% | Navegar; não elevar a capacidade |
| Flutuar | 20% | Flutuar; a regra de munição não pode recuperar a navegação |
| Não avaliada | 20% | Não avaliada, com restrição de combate conhecida; não presumir navegabilidade |

O índice de origem não é reescrito para 60% só para obter a etiqueta “Navegar”. Mostrar o motivo da restrição, sem afirmar que uma proposta automática de confronto virou resultado oficial. A autoridade do instrutor de 80 permanece preservada; aqui existe uma restrição logística derivada autorizada pelo responsável.

A recomposição após rearmamento, eventuais exceções didáticas e a interação com outras avarias exigem regra explícita. Não restaurar automaticamente “Combater” apagando efeitos confirmados pelo instrutor. Registrar transição, causa, valores de origem/efetivos, versão dos critérios e tempo da execução; idempotência impede efeitos/alertas duplicados.

## Alocação de responsabilidades

- `resource-engine`: quantidades de combustível/armamento, base dos percentuais, mínimo, pré-alerta e fatos de insuficiência, preservando detalhes internos.
- `operational-state`: condição determinada pelo instrutor e restrição efetiva derivada desses fatos, sem sobrescrever a origem.
- `force-confrontation`: considera a condição efetiva e a composição/configuração autorizada; apuração continua sujeita ao resultado oficial do instrutor.
- Interface: resume os três contratos em uma ficha compacta, sem calcular percentuais ou estados oficiais por conta própria.

O grafo propõe dependência de `operational-state` em `resource-engine`; o provedor de recursos não depende do modelo de confronto/estado para calcular seus fatos. Essa mudança de dependência fica identificada como complemento para revisão, sem reabrir o recorte aprovado de `technical-catalog`.

## Critérios a testar quando especificado

M=30 e M=40, F exatamente em M+5, entre os limites, exatamente em M e abaixo; limites 0/100 e ausência de M/capacidade. Armamento imediatamente abaixo/no/acima do limiar aprovado, estoque desconhecido, preservação de estados mais restritivos e fonte de avaliação desconhecida. Verificar que consulta/hover não muda estado nem fornece informação adversária, e que restrição derivada não se confunde com nova decisão de confronto.

**Pendências:** denominadores, agregação do armamento, limiar de combate e cores de munição, recomposição/exceções, apresentação compacta e agregação por força. Regra de combustível M+5 e três indicadores foram expressamente confirmadas; não estão implementadas nesta entrega documental.
