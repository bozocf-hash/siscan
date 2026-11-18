# 125 — Ensaio automático controlado do par CPC

**2026-11-18 · Contrato do próximo incremento; implementação em andamento.** Continuidade autorizada por “siga” após a entrega 124. O responsável dispensou solicitações adicionais da skill Spec Driven Development. Aplicar Ponytail, implementação incremental e testes, preservando os documentos/decisões anteriores.

## Escopo e política explícita

Reutilizar o par aéreo sintético e o perfil de hipóteses de [124](124_ENTREGA_PRONTIDAO_ENSAIO_CPC.md). No painel de prontidão, executar ensaio controlado e ler estados inicial/final, combustível, estoques, perdas propostas e eventos. Nenhum parâmetro técnico real será criado/aprovado, nenhuma posição geográfica será movida e nenhum efeito/proposta oficial será gravado.

Política `siscan-cpc-controlled-policy-01`: seleção expressa do instrutor para cada unidade: um estoque ar-ar ou nenhuma ação ofensiva. Uma tentativa por minuto, usando somente esse estoque, sem troca automática de arma. O motor existente exige detecção renovada, alcance e disponibilidade para consumir; não há disparo sem contato. Ordem explicitamente simultânea ou iniciativa de AZUL/VERMELHO, sem presumir first strike por velocidade. Consumo/logística/movimento antes das ações ao final do minuto, conforme biblioteca atual.

Duração vem do perfil: entre 1 e 120 minutos neste adaptador, para limitar custo/volume. Interromper ao primeiro minuto que produza perda de um participante, por dano ou combustível, registrando motivo e duração efetiva. Evadir suspende novos ataques, não elimina combustível consumido. Em voo, taxa de consumo precisa ser positiva; a prontidão de dados com taxa zero não garante execução. Não confundir reserva de retorno em kg com alerta mínimo do operador. Não modelar trajetória geográfica, perseguição, altitude de voo, propagação física ou defesa naval neste incremento.

## Contrato HTTP

`POST /api/cpc/controlled-trial`, somente instrutor participante com exercício aberto, sessão e CSRF. Campos obrigatórios: `selection`, `expected_view_sha256`, `expected_basis_sha256`, `expected_hypotheses_sha256`, `hypotheses`, `policy`. Política: `schema_version`, `initiative` (`simultaneous`, `AZUL` ou `VERMELHO`) e `weapons` (mapa exato de dois UUIDs para estoque ou null). Não aceitar estado oficial, coeficientes adicionais, IDs alheios ou chaves extras.

Reconferir prontidão e hashes antes de executar; criar objetos/RNG locais a partir da semente explícita; reconferir contexto depois, recusando resultado se a base mudou. Limitar requisição a 64.000 bytes. Resultado transitório `siscan-cpc-controlled-trial-01` contém referências da base/hipóteses/política, metadados do motor, estados, balanço e histórico. `official_effects_applied=false`; sem gravação de proposta, decisão, recurso, relatório em caminho escolhido pelo cliente ou UUID de aplicação.

Dados reprodutíveis com mesmas entradas, política, versão do motor e Python; ID do relatório é identidade da execução e pode diferir entre repetições. Não anunciar hash idêntico de envelopes com IDs distintos. Nada será encaminhado automaticamente à confirmação didática como se tivesse origem didática humana.

## Interface e invalidação

Controles de execução somente após prontidão positiva; nenhum estoque/ordem pré-selecionado. Resumo compacto por meio; detalhes de eventos recolhidos e download JSON local para análise. Editar hipóteses, reconferir entradas, trocar par/fontes ou sair invalida resultado do ensaio; resposta atrasada não o restaura. 401/403 limpa dados privados. Falha mantém mensagem explícita, nunca resultado parcial/publicação oficial. O instrutor retorna ao julgamento para deliberar, sem conversão automática de pontos abstratos em índice operativo.

## Tarefas e aceites

- [ ] AUTO-RUN-01: testes primeiro; adaptador do motor com validação de política, limite, hashes e reprodução; nenhuma mutação de domínio ou RNG global.
- [ ] AUTO-RUN-02: HTTP protegido; pronta/incompleta/inválida/conflito/revogação/fonte indisponível, sem migração ou reinício principal.
- [ ] AUTO-RUN-03: execução e resumo no painel atual; edição e respostas atrasadas invalidadas; download transitório.
- [ ] AUTO-RUN-04: navegador isolado, regressões, documentação, sincronização protegida e commits no repositório autorizado.

Testes: unittest `check_cpc_controlled_trial*.py`, node:test da prontidão e regressões CPC existentes, verificadores de mapa/silhuetas. Comparar SQL/entradas/RNG, estoque gasto, combustível, eventos/perdas, determinismo sem IDs de execução e mudança real de grupo durante cálculo. Harness próprio, pasta/cookie/porta novos; preservar 61273 e principal 8787. Registrar evidências reais no fechamento deste documento.
