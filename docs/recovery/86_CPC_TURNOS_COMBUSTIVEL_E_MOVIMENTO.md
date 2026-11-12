# 86 — CPC: turnos de um minuto, combustível e movimento

**Data: 2026-11-12. Estado: incremento didático implementado e verificado.** Pedido expresso: loop de um minuto, combustível/consumo nas unidades, reserva de retorno, limite de munição e movimento no cenário. Complementa [84](84_CPC_RODADAS_INICIATIVA_E_CONSUMO_DEFENSIVO.md) e [85](85_CPC_DETECCAO_CONTATOS_E_ALCANCE.md). Não altera dados oficiais nem transforma os parâmetros fictícios em características dos meios reais.

## Contratos e unidades

| Elemento | Contrato |
|---|---|
| `UnidadeMilitar`, herdado pelos meios | `combustivel_atual`: kg; `taxa_consumo_combustivel`: kg/min; ausência é `None` |
| `VetorAereo` | `combustivel_minimo_retorno`: reserva explícita em kg; `estado_voo`: `em_voo`, `evadindo`, `pousado`, `perda_proposta` |
| `CenarioTatico` | Posições locais `(x, y)` em MN, além da matriz existente; devem ser completas e consistentes com ela |
| `SimulacaoTemporal`, em `cpc_time.py` | Um relógio para todo o cenário, rumos normais e de evasão declarados; `avancar_turno` avança 1 minuto |
| `ResultadoTurno` | Minuto, resumo logístico por unidade, motivos de suspensão de ações e resultados de combate |

Taxa em voo deve ser positiva; saldo/reserva devem ser finitos e não negativos. Dados ausentes impedem o turno, sem inventar combustível, taxa ou reserva. A reserva de retorno não é um percentual padrão e não substitui o alerta mínimo configurável do operador ou a margem M+5 pontos de 81. A relação entre reserva operacional e preferência de alerta precisa de contrato explícito na integração futura.

Foi conferido o código existente de `engine_profiles.py` e `fuel_limits.py`: permanece a separação entre previsão de recursos, estados/versionamento e limite do operador. Este incremento usa taxa constante fictícia em memória, não executa o débito por perfil daquele backend nem converte/promove registros DB3K. A unidade kg é consistente com a entrada de limites existente; a integração oficial em gramas permanece independente.

## Ordem de um turno

1. Copiar em conjunto o gerenciador/cenário, ações e iniciativa, preservando referências entre as cópias. Validar estoque, logística, geometria e comandos.
2. Para cada aeronave em voo ou evasão, consumir combustível no intervalo de um minuto. Aeronaves pousadas ou com perda proposta não consomem nem se movem. As demais unidades podem se mover, mas consumo naval não é modelado neste recorte.
3. Integrar deslocamentos com `distancia_MN = velocidade_nos * minutos / 60`. Rumos: 0° norte, 90° leste. Não se escolhe automaticamente perseguição, afastamento ou retorno a uma base.
4. Se a aeronave cruza a reserva dentro do intervalo, integrar o trecho restante com seu rumo de evasão declarado. Se esgota combustível antes do fim, limitar o tempo de movimento a `saldo/taxa`. Não movimentar a aeronave pelo minuto inteiro sem combustível.
5. Atualizar posições simultaneamente e recalcular toda a matriz por distância euclidiana. Expirar os contatos do instante anterior, inclusive para deslocamento zero.
6. No fim do minuto, verificar as ações declaradas: disponibilidade, voo sem evasão, estoque ofensivo, nova detecção e alcance. Realizar no máximo uma busca por par direcional naquele turno. Motivos normais de suspensão geram evento, sem debitar munição; a logística e o relógio continuam.
7. Resolver as ações elegíveis com as regras de simultaneidade/iniciativa e estoque defensivo existentes. Cada disparo ofensivo iniciado consome um item, inclusive quando erra ou é interceptado.
8. Somente após sucesso publicar o novo estado nos objetos do ensaio e avançar o relógio global. Erro de configuração/conflito de reservas recusa o minuto completo, preservando estado e gerador originais.

Não se espera um minuto de relógio de parede. As aeronaves que não participam do par de confronto também consomem no mesmo minuto global. O gerador deve ser `random.Random` padrão, para reprodução/publicação do estado; geradores especiais não foram integrados.

## Estado de voo e autoridade

Ao atingir `saldo <= reserva`, a aeronave fica `evadindo`: continua consumindo e se movendo no rumo de evasão, sem novos ataques. Não retorna automaticamente ao combate por alteração de combustível. Ao atingir saldo zero em voo, fica `perda_proposta`; não se modificam HP, causas de avaria ou perdas oficiais por essa transição.

O próprio gerenciador de combate também recusa uma chamada direta de ataque de aeronave pousada, evadindo ou com perda proposta. Alvos com perda proposta ficam indisponíveis para o ensaio. Isso não aplica as faixas navais de 80 a aeronaves. HP abstrato continua distinto do estado de voo; não há inferência automática de queda a partir de dano.

**O instrutor continua decidindo o resultado oficial.** Não foram criados autenticação, adjudicação, confirmação de perda, integração com bases/pouso ou gravação no banco SISCAN. Rumo de evasão e reserva informados não demonstram que uma base será alcançada: não há rota de retorno calculada neste modelo.

## Loop principal entregue

Em `cpc_combat.py`, após preparar as unidades, cenário e ação fictícios:

```python
simulacao = SimulacaoTemporal(
    motor,
    rumos={caca.identificador: 90.0},
    rumos_evasao={caca.identificador: 270.0},
)
for _ in range(args.turnos):
    turno = simulacao.avancar_turno([acao], iniciativa=iniciativa)
    print(f"Minuto {turno.minuto}: {cenario.distancia(caca, fragata):.3f} MN")
    for unidade in turno.logistica:
        print(unidade)
    for evento in turno.eventos:
        print(evento)
    for resultado in turno.combate:
        print(resultado.narrativa)
```

O script real apresenta resumos formatados e detalha movimentos de estoque. Executar na pasta `prototype`:

```powershell
python cpc_combat.py --turnos 3 --semente 7
python -m unittest discover -s . -p "check_cpc_*.py"
```

## Verificação

**63 testes passaram:** os 47 anteriores mais 16 de tempo/logística/geometria. Casos novos incluem consumo por minuto, suspensão na reserva, movimento parcial até esgotamento, aeronave pousada, evasão contínua, aproximação pelos dois movimentos, estoque esgotado sem interromper o relógio, parâmetros/posições ausentes, reversão do gerador junto com o minuto, terceiro meio consumindo no relógio global, contatos expirados e bloqueio direto em evasão.

Demonstração com nomes/IDs lidos no catálogo compilado, sem incorporar seus valores técnicos:

| Minuto | Combustível fictício | Distância fictícia | Estado do ensaio |
|---|---|---|---|
| 1 | 5 → 3 kg | 10 → 9 MN | Em voo; pode tentar detectar/disparar |
| 2 | 3 → 1 kg | 9 → 8 MN | Atinge a reserva declarada; evasão, sem novo ataque |
| 3 | 1 → 0 kg | 8 → 8,5 MN | Meio minuto no rumo de evasão; perda proposta |

Os valores não representam autonomia, velocidade ou consumo reais do F/A-18C/Niterói. A demonstração continua consultando somente identidade e preservando os bancos originais/derivados, o mapa e o exercício.

## Limites e continuidade

Plano local, taxas constantes e eventos de combate amostrados no fim do minuto: não se avaliam oportunidades transitórias de alcance no interior do intervalo, trajetórias de armamento, horizonte radar ou manobras físicas. Somente o combustível/movimento possui os subintervalos descritos. Não há consumo naval, abastecimento, pouso, rota/base de retorno, alerta percentual M+5, idempotência persistida ou aplicação oficial.

Antes da integração: definir snapshots/revisões, autorização do instrutor, proposta/adjudicação/aplicação de efeitos, relação reserva–alerta do operador e promoção dos dados técnicos. Repetir `avancar_turno` após sucesso avança outro minuto; não é reenvio idempotente. A publicação é síncrona em memória, sem garantias de persistência, concorrência entre threads ou recuperação após encerramento do processo.
