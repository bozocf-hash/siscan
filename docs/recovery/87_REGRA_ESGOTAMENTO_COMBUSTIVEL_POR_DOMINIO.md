# 87 — Regra de esgotamento de combustível por domínio

**Data: 2026-11-16. Estado: decisão ratificada pelo responsável e implementada no ensaio CPC.** Complementa [86](86_CPC_TURNOS_COMBUSTIVEL_E_MOVIMENTO.md). “Zerado” refere-se ao saldo `combustivel_atual`, não à taxa de consumo.

## Decisão expressa

| Domínio/situação | Consequência do combustível zerado |
|---|---|
| Aéreo, em voo ou evasão | Queda/perda no resultado automático do ensaio; `perda_proposta`, indisponível para continuar voo ou combate |
| Superfície | Incapacidade de deslocamento próprio; permanece no cenário, sem destruição/perda automática |
| Terrestre | Incapacidade de deslocamento próprio; permanece no cenário, sem destruição/perda automática |
| Aeronave pousada | Não se propõe queda por tanque vazio no solo |

O resultado oficial continua sob autoridade do instrutor, conforme 80. A designação `perda_proposta` não significa que uma aeronave sem combustível continua voando: é terminal no ensaio automático e preserva a etapa de adjudicação oficial. Não foi implementada física de queda ou intervenção didática no backend.

## Implementação

- `MeioTerrestre` herda os atributos da classe base, sem inventar equipamentos ou configuração física.
- Para meios navais/terrestres, o loop aplica a taxa constante de combustível explicitamente configurada. Se o saldo acaba durante o minuto, o deslocamento é limitado a `saldo/taxa`; após o esgotamento não há movimento nos turnos seguintes.
- Saldo zero imobiliza mesmo se a taxa ainda não foi informada: já se conhece a restrição. Saldo desconhecido não vira zero; movimento não aéreo com logística ausente é recusado. Meio estacionário sem saldo/taxa permanece não avaliado.
- Taxa zero explicitamente configurada não equivale a tanque vazio: o saldo é verificado separadamente. Não há taxa presumida de plataforma real.
- `ResumoLogistico.imobilizado_por_combustivel` é verdadeiro/falso para meios navais/terrestres com saldo conhecido e `None` quando não avaliado ou não aplicável. Não é índice geral de disponibilidade ou capacidade de combate.
- A velocidade informada permanece como referência do plano; o deslocamento efetivo é limitado pela disponibilidade de combustível. Não se apaga esse valor ao imobilizar o meio.
- Aeronave já iniciando o turno com saldo zero em voo recebe `perda_proposta`, sem depender de taxa, reserva ou rumo de evasão. Sem movimento adicional e sem inferir avaria/HP.
- Chamadas diretas de detecção/disparo também não permitem usar uma aeronave em voo com combustível conhecido zerado enquanto o próximo turno não foi processado.

Não se transforma falta de combustível naval/terrestre em afundamento, destruição, redução automática de HP ou cancelamento geral de sensores/armamentos. Essas consequências dependem de regras próprias; nesta decisão a restrição não aérea é de locomoção.

## Verificação e preservação

**69 testes passaram**, incluindo os 63 anteriores adaptados ao contrato de combustível do movimento não aéreo e seis casos novos. Verificados: imobilização de superfície/terrestre, esgotamento durante o minuto, permanência sem perda no turno seguinte, recusa de saldo desconhecido, aeronave pousada com saldo zero, perda aérea sem taxa/reserva/rumo e bloqueio direto de disparo antes do próximo turno. Alguns casos abrangem ambos os domínios no mesmo método de teste.

Arquivos de código: `cpc_models.py`, `cpc_time.py`, `cpc_combat.py` e `check_cpc_time.py`. A demonstração continua com parâmetros fictícios, sem importar consumo real dos registros F/A-18C/Niterói.

Não foram modificados bancos, arquivos originais, mapa ou exercício oficial. Consumo por perfis reais, abastecimento, reboque/transporte, bases/pouso, snapshots e adjudicação oficial continuam pendentes. Esta entrega resolve a antiga pendência de consumo não aéreo apenas para o recorte constante e controlado em memória.
