# 121 — Prontidão para o ensaio automático controlado

**Estado atual: especificação, plano e tarefas aprovados; implementação concluída em [124](124_ENTREGA_PRONTIDAO_ENSAIO_CPC.md).** Este registro preserva a etapa original de especificação, aprovada por “sim”; a continuidade foi autorizada por “pode continuar”, após 120. As aprovações posteriores permitiram implementar o recorte, sem aprovar parâmetros reais.

Contrato canônico: [SPEC-force-confrontation.md — Recorte 4-A](../../SPEC-force-confrontation.md#recorte-4-a--prontidão-para-o-ensaio-automático-controlado). Não duplicar o contrato neste registro.

## Resultado visível entregue

No CPC, depois de preparar o par, o instrutor consulta **Conferir prontidão do ensaio**. Recebe entradas incompletas, recorte não suportado ou prontidão para ensaio controlado, com motivos por meio. O julgamento didático continua funcionando. Prontidão não executa combate e não aplica resultado.

## Evidências e motivo do recorte

- 104 aprova a ordem: preparação → estado/adjudicação → julgamento integrado → produtor automático de proposta.
- 116 entrega o julgamento; 117–120 corrigem apresentação e retirada de perdas.
- `cpc_combat.py`, `GerenciadorDeCombate._validar_rodada`: ações pertencem somente ao par atacante/defensor. Não há resolvedor de grupamentos demonstrado.
- `cpc_time.py`, `SimulacaoTemporal.avancar_turno`: recebe ações fornecidas pelo chamador. O loop temporal não escolhe alvos autonomamente.
- `cpc_scenario.py`: posições/distâncias locais em NM; latitude/longitude do mapa ainda não são entradas equivalentes.
- `engine_units.py`, `configuration_domain`: reconhece somente a referência aérea sintética controlada. Catálogo consultável não é cadastro de instâncias reais executáveis.
- `operational_state_storage.py`: origem armazenada limitada a `didactic`; ensaio automático precisa de proveniência própria antes de persistir sugestões.

Foco desta especificação: tornar essas lacunas verificáveis para o instrutor e preparar a entrada da execução seguinte, sem escolher coeficientes ou contornar contratos por inferência.

## Controles

Especificação inclui fronteiras de entrada/saída, permissões, doze critérios AUTO-READY, limites de dados/recorte e estratégia de teste. Na etapa de especificação não foram escritos plano, tarefas, código, DDL, parâmetros de combate ou novas telas. Não foram executados testes nem iniciado/reiniciado servidor: edição exclusivamente documental e inspeção de código. Originais, bancos e planos anteriores preservados.

Na etapa original, a revisão da especificação precedeu o plano conforme a skill Spec Driven Development. Essas revisões foram concluídas; durante a implementação o responsável dispensou solicitações adicionais da skill. Não existe gate pendente desta fatia.


Continuidade: plano de Fase 2 aprovado após [122](122_PLANO_PRONTIDAO_ENSAIO_AUTOMATICO.md), lista de Fase 3 aprovada após [123](123_TAREFAS_PRONTIDAO_ENSAIO_AUTOMATICO.md), READY-01–12 concluídas e verificadas em [124](124_ENTREGA_PRONTIDAO_ENSAIO_CPC.md). Os limites acima permanecem; o diagnóstico não é o motor automático.
