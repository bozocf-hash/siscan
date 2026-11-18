# 121 — Prontidão para o ensaio automático controlado

**Estado: especificação aprovada pelo responsável por “sim”, em resposta à revisão solicitada.** Continuidade autorizada por “pode continuar”, após a correção 120. A aprovação permite elaborar o plano, sem aprovar parâmetros reais ou iniciar implementação.

Contrato canônico: [SPEC-force-confrontation.md — Recorte 4-A](../../SPEC-force-confrontation.md#recorte-4-a--prontidão-para-o-ensaio-automático-controlado). Não duplicar o contrato neste registro.

## Resultado visível proposto

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

Conforme a skill [Spec Driven Development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md), a revisão da especificação precede a elaboração do plano. A revisão solicitada é concreta: aceitar esta primeira fatia de prontidão ou ajustar seu escopo.


Continuidade: plano de Fase 2 aprovado após [122](122_PLANO_PRONTIDAO_ENSAIO_AUTOMATICO.md), com lista de Fase 3 proposta em [123](123_TAREFAS_PRONTIDAO_ENSAIO_AUTOMATICO.md). Os limites e evidências acima permanecem; a aprovação não transforma o diagnóstico em motor automático.
