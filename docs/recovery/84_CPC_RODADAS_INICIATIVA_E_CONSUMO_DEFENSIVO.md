# 84 — CPC: rodadas, iniciativa e consumo defensivo

**Data: 2026-11-12. Estado: incremento didático isolado implementado e verificado.** O responsável autorizou as classes, o disparo sintético e, após discussão dos critérios, a continuidade de iniciativa/consumo defensivo. Este recorte complementa a proposta de [83](83_ALGORITMO_CONCEITUAL_CPC_REFERENCIA_COMMAND.md); não implementa o algoritmo completo ali proposto nem aprova parâmetros físicos.

## Decisões e regras do recorte

- Rodada simultânea como padrão: todas as ações válidas da fase são iniciadas antes dos efeitos. Uma ação não é apagada porque outra do mesmo lote deixa sua unidade sem pontos.
- Iniciativa explicitamente informada: ações do participante escolhido compõem a primeira fase; ações do outro ficam na segunda. Não se calcula iniciativa a partir de sensores, velocidade, assinatura ou identificadores.
- Na segunda fase, uma ação ainda não iniciada fica suspensa se atacante ou defensor estiver sem pontos. Não consome recurso ou sorteio. Dano parcial não impede automaticamente a resposta. Zero pontos é uma condição abstrata deste ensaio, não afundamento/perda oficial ou aplicação das faixas de estado operativo de 80.
- Cada tentativa defensiva exige selecionar um estoque pertencente ao defensor naval e declarar seu custo inteiro positivo. O custo não possui padrão; na demonstração são dois pacotes fictícios. Não corresponde a quantidade real de projéteis ou mísseis de qualquer meio.
- Tentativa realizada consome o custo completo, mesmo quando falha. Estoque inferior ao custo impede a tentativa, sem consumo parcial ou chance de defesa residual. Defesa não declarada também não ocorre; percentual isolado não cria recursos.
- Uma rodada reserva os recursos de todas as ações declaradas antes dos sorteios, inclusive quando tem iniciativa. Se reservas combinadas excederem um estoque, o motor recusa a rodada; não escolhe vencedor do conflito pelo primeiro ID. A reserva é cálculo em memória, não débito definitivo.
- As ações são ordenadas por ID para reprodução dos sorteios. Isso não altera o direito de agir dentro da fase ou resolve disputas de estoque. IDs devem ser únicos na rodada.

## Código e contratos

`siscan-prototype/cpc_models.py` mantém as classes solicitadas. `pk` e `dano` são opcionais para preservar construtores antigos, mas devem estar definidos para efetuar disparos. `capacidade_defesa_ponto` passou da escala abstrata inicial para probabilidade didática de interceptação, conforme pedido posterior; não é parâmetro validado de sistemas reais.

`siscan-prototype/cpc_combat.py` contém:

| Elemento | Responsabilidade |
|---|---|
| `AcaoDisparo` | Declaração da ação, participantes, estoque ofensivo e eventual estoque/custo defensivo |
| `ConsumoArmamento` | Unidade, estoque, finalidade, quantidade e saldo anterior/posterior |
| `ResultadoDisparo` | ID da ação, fase, situação, narrativa, sorteios, consumos, dano proposto e vida antes/depois do lote |
| `GerenciadorDeCombate.resolver_rodada` | Valida/reserva, processa fases em estado temporário e aplica o lote aos objetos do ensaio somente após sucesso |
| `resolver_disparo` | Atalho de uma ação; mantém retorno textual, mas defesa agora exige estoque e custo explícitos |

O registro é retornado em memória, sem log persistido, recibo ou confirmação oficial. Danos simultâneos são somados por defensor antes de limitar a vida final a zero. O dano proposto por evento não deve ser confundido com a redução efetiva do lote; a vida inicial/final se repete nos resultados que pertencem à mesma fase/defensor, não deve ser somada por evento.

O estoque ofensivo consome um item por disparo iniciado. Estoques defensivos são independentes. Não se pode compartilhar o mesmo objeto de estoque entre unidades ou duplicá-lo na lista; nomes de estoque devem ser únicos dentro de cada unidade.

Dados inválidos, falta de parâmetros ou conflitos de reservas recusam o lote antes de consumir ou sortear. Se o gerador falhar durante o processamento, os estoques/vidas originais não são alterados; a sequência do gerador pode ter avançado. Para repetir um ensaio abortado, recriar as instâncias e o gerador com a mesma semente.

## Demonstração e evidências

`python cpc_combat.py --semente 7` consulta em modo somente leitura o catálogo compilado `data/db3k-compiled-06.sqlite3`. Obtém apenas a identificação de `DataAircraft/8 — F/A-18C Hornet` e `DataShip/1349 — F 40 Niteroi [Vosper Mk10, ASW]`. Probabilidades, pontos e pacotes são fictícios; não foram extraídos desses registros ou das relações técnicas.

A demonstração tem somente uma ação da aeronave. O parâmetro opcional `--iniciativa` configura o regime, mas não cria uma resposta armada do navio. As diferenças entre duas ações recíprocas são verificadas nos testes com unidades inteiramente fictícias.

**28 testes passaram:** 12 de disparo em `check_cpc_combat.py` e 16 de rodadas em `check_cpc_rounds.py`. Cobrem interceptação/erro/acerto, limites de probabilidade, dados inválidos, consumo ofensivo/defensivo, ausência de defesa, falta/conflito de estoque, ações simultâneas, iniciativa dos dois participantes, resposta após dano parcial, suspensão sem débito, reprodução e falha sem aplicação parcial. A demonstração foi executada sobre o catálogo local.

## Limites e continuidade

Preservados: resultado oficial exclusivo do instrutor (80), indicadores/limiares de 81 e promoção de dados de 53. Esta biblioteca não autentica instrutor; essa autorização deverá existir na futura integração ao backend. Não há atualização do banco SISCAN, mapa ou exercício, e nenhum banco/original foi modificado.

Faltam: integração com snapshots/revisões, proposta/adjudicação/aplicação oficial, idempotência persistida, duração temporal de ações, grupos com mais de duas unidades, rubricas e custos por contexto aprovados, compatibilidade de configurações e vínculo dos recursos à condição efetiva. Não há modelo de detecção, alocação automática de defesas, eficácia real ou validação operacional.

Repetir uma chamada não é reenvio idempotente: representa nova execução sobre o estado dos objetos. Não usar este módulo diretamente sobre unidades oficiais. O ciclo de `technical-catalog` permanece independente; as pendências documentadas nas propostas anteriores continuam válidas fora deste recorte isolado.
