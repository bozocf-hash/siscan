# 85 — CPC: detecção, contatos e alcance

**Data: 2026-11-12. Estado: incremento didático implementado e verificado.** Atende ao pedido expresso de acrescentar radar, distâncias relativas, detecção anterior ao disparo e alcance máximo do armamento. Complementa [84](84_CPC_RODADAS_INICIATIVA_E_CONSUMO_DEFENSIVO.md), preservando simultaneidade, iniciativa explícita, estoque defensivo e resultado oficial do instrutor. Não constitui modelo físico do Command nem valida parâmetros dos meios reais.

## Contrato dos dados

| Elemento | Campo/contrato |
|---|---|
| `UnidadeMilitar`, herdado por `MeioNaval`/`VetorAereo` | `alcance_radar`: limite didático em milhas náuticas (MN); `probabilidade_deteccao`: probabilidade-base entre 0 e 1 |
| `Armamento` | `alcance_maximo`: distância máxima didática em MN |
| `CenarioTatico`, em `cpc_scenario.py` | Unidades identificadas, matriz simétrica de distâncias em MN e tabela explícita de fatores por assinatura |
| `GerenciadorDeCombate` | Recebe `cenario`; oferece `tentar_detecao(unidade_a, unidade_b)` e preserva APIs de disparo/rodada |

Os parâmetros novos têm `None` como ausência, não zero ou infinito. Isso preserva a construção de objetos antigos, mas não libera execução sem informações obrigatórias. Zero continua sendo valor numérico válido onde aplicável. Grandezas devem ser finitas, não negativas e probabilidades/fatores devem estar entre 0 e 1.

A matriz aceita uma orientação de cada par e fornece a inversa automaticamente. Deve cobrir todos os pares das unidades cadastradas; valores inversos conflitantes, distâncias inválidas ou pares desconhecidos são recusados. As entradas são copiadas. Não há movimento ou integração ao mapa; para outra geometria deve-se criar novo cenário, sem contatos herdados.

## Regra didática de detecção

1. Validar que observador e alvo são unidades distintas deste ensaio/cenário e têm pontos de vida positivos.
2. Remover o contato anterior deste par: a nova tentativa substitui a anterior neste modelo simplificado.
3. Se a distância excede `alcance_radar`, retornar falso sem sorteio.
4. Exigir assinatura conhecida e fator explicitamente associado a ela na rubrica do cenário.
5. Calcular `p_efetiva = probabilidade_deteccao * fator_assinatura` e sortear com o gerador do ensaio. Detectar apenas quando `sorteio < p_efetiva`.
6. Registrar o contato somente para o observador, sem revelar reciprocamente a busca ou compartilhar com aliados.

O limite de distância é inclusivo. A assinatura continua documentada em m² no modelo, mas o fator é uma escolha de exercício, não uma conversão física de RCS para alcance/probabilidade. Não há interpolação, curva implícita, equação de radar ou coeficientes extraídos do DB3K. Ausência de assinatura/fator gera diagnóstico; não se supõe alvo invisível ou inevitavelmente detectado.

`cenario.contatos_detectados(unidade)` fornece uma coleção somente leitura. Cada contato guarda o contexto de radar/probabilidade do observador, assinatura do alvo e distância. Alteração desses valores invalida o contato na consulta. Não existe persistência de trilha, envelhecimento por relógio, classificação ou identificação automática neste recorte estático.

## Porta de entrada do disparo

Tanto `resolver_disparo` quanto `resolver_rodada` conferem cenário, pertencimento das instâncias, contato válido do atacante e `distancia <= arma.alcance_maximo`. A validação ocorre antes de reservas efetivas, consumo ou sorteios de combate. Uma ação inválida bloqueia o lote completo, sem aplicação parcial.

Não há caminho alternativo que omita cenário ou crie contato automaticamente ao solicitar disparo. Iniciativa continua sendo configuração didática explícita, não consequência calculada dos atributos ou da primeira chamada ao método.

**Limite defensivo:** essa validação refere-se às ações de disparo contra unidades. A tentativa defensiva previamente declarada em uma ação permanece reação abstrata ao evento de ataque de 84. Não foi criado sensor/rastreador de munições em voo; não usar o contato com a plataforma atacante como substituto fictício para detecção do projétil.

## Evidências e reprodução

Foram executados **47 testes**, todos aprovados: 12 de disparo, 16 de rodadas e 19 de detecção/geometria. Os anteriores foram adaptados para criar cenário e realizar detecção bem-sucedida antes do combate, sem inserir manualmente contatos ou retirar suas verificações de consumo/efeitos.

Os novos testes cobrem limites inclusivos de radar/armamento, fator de assinatura, falta de contato, direção não recíproca, tentativa falha, assinatura desconhecida, contato invalidado, cenário novo, ausência de cenário, matriz completa/simétrica, parâmetros inválidos, zeros válidos e lote sem aplicação quando apenas uma ação tem contato.

Na pasta `prototype`:

```powershell
python check_cpc_combat.py
python check_cpc_rounds.py
python check_cpc_detection.py
python cpc_combat.py --semente 7
python cpc_combat.py --semente 0
```

A demonstração ainda obtém somente os nomes/IDs F/A-18C (`DataAircraft/8`) e Niterói (`DataShip/1349`) no catálogo compilado em modo somente leitura. Distâncias, assinaturas, radar, fatores, alcance da arma, probabilidades e dano são fictícios. Com semente 7 há detecção e o ensaio prossegue; com 0 não há detecção nem consumo. Não são resultados de desempenho dessas plataformas reais.

## Pendências preservadas

Integração com snapshots/revisões, autorização do instrutor, adjudicação/aplicação oficial, idempotência, múltiplos grupos, geometria dinâmica, contexto dos sensores e validação dos dados permanecem pendentes. Não houve atualização de bancos, atributos aprovados, mapa ou exercício. A integração futura deve respeitar 53, 80/81 e o ciclo próprio de `technical-catalog`.
