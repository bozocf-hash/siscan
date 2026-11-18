# 125 — Ensaio automático controlado do par CPC

**2026-11-18 · Recorte 4-B implementado e verificado.** Continuidade autorizada por “siga” após a entrega 124. O responsável dispensou solicitações adicionais da skill Spec Driven Development. Aplicados Ponytail, implementação incremental e testes, preservando os documentos/decisões anteriores.

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

- [x] AUTO-RUN-01: testes primeiro; adaptador do motor com validação de política, limite, hashes e reprodução; nenhuma mutação de domínio ou RNG global. Oito testes de serviço passaram.
- [x] AUTO-RUN-02: HTTP protegido; validação, conflito/revogação/fonte indisponível, sem migração ou reinício principal. Três testes HTTP passaram, incluindo comparação integral do banco antes/depois.
- [x] AUTO-RUN-03: execução e resumo no painel atual; edição e respostas atrasadas invalidadas; download transitório. Três testes JS novos passaram; execução/exportação e invalidação também observadas no navegador.
- [x] AUTO-RUN-04: navegador isolado, regressões, documentação, sincronização protegida e commits no repositório autorizado, conforme evidências e conferência de encerramento.

Testes: unittest `check_cpc_controlled_trial*.py`, node:test da prontidão e regressões CPC existentes, verificadores de mapa/silhuetas. Comparar SQL/entradas/RNG, estoque gasto, combustível, eventos/perdas, determinismo sem IDs de execução e mudança real de grupo durante cálculo. Harness próprio, pasta/cookie/porta novos; preservar 61273 e principal 8787. Registrar evidências reais no fechamento deste documento.

## Entrega e evidências

Arquivos de produção: `cpc_controlled_trial.py` (adaptador), rota em `app.py`, controlador/formulário de execução em `static/cpc-readiness.mjs`. Sem alteração das bibliotecas de combate/tempo, sem schema novo e sem dependências. Verificadores novos: `check_cpc_controlled_trial.py` e `check_cpc_controlled_trial_http.py`; ampliado `check_cpc_readiness.mjs`.

**Passaram 165 testes Python CPC + 49 JavaScript: 214 testes nomeados distintos**, além dos dois verificadores por assertions de plotagem e silhuetas. O novo recorte acrescenta 8 testes de serviço, 3 HTTP e 3 JS. Reexecuções não aumentam a contagem. Comandos, na raiz do repositório:

```powershell
$pythonCpc = 'C:/Users/bozoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_*.py'
node --test siscan-prototype/check_cpc_readiness.mjs siscan-prototype/check_cpc_preparation.mjs siscan-prototype/check_cpc_judgment.mjs siscan-prototype/check_map_presentation.mjs siscan-prototype/check_map_groups.mjs
& $pythonCpc siscan-prototype/check_map_units.py
node siscan-prototype/check_map_visuals.mjs
git diff --check
```

Casos demonstrados por comportamento: 60 minutos; detecção zero sem consumo de munição; esgotamento de estoques; perdas simultâneas e iniciativa explicitamente AZUL; evasão/perda por combustível; nenhuma ação ofensiva expressa; recusa de arma alheia ou antinavio contra o par aéreo; duração excessiva; taxa zero em voo; perfil incompleto; hashes antigos; operador recusado antes do motor; arquivamento real do grupo durante cálculo descarta o relatório e libera o SAVEPOINT. Comparações de SQL/entradas/RNG global preservadas; mesma entrada/semente reproduz estados, balanço e eventos desconsiderando o UUID de cada execução.

HTTP demonstrou 401/403/CSRF, revogação, 400 por formato/query/limite, 409 por base antiga, 503 por schema indisponível e 200 com resultado completo, sem mudanças na base. JS demonstrou envio das referências conferidas, invalidação por hipótese/política, descarte de resposta atrasada, erro por base divergente e limpeza por 403, preservando regressões de julgamento/mapa.

### Navegador real

Prévia final: **`http://localhost:61274/`**, pasta `%TEMP%/siscan-controlled-20261118-v1`, processo próprio iniciado com o código atualizado. Login instrutor **1**, senha sintética **somente-teste-local**, mapa `/atlanticador/editor.html`. Usado o harness de teste existente, com cookie/base próprios. Principal 8787 e prévias anteriores preservados; não foi feita ativação/migração principal.

Percurso: preparar par → declarar hipóteses → conferir prontidão → escolher ordem simultânea e um estoque por meio → executar → expandir estado → baixar relatório JSON → alterar política (resultado removido) → recarregar e repetir com rótulos finais → alterar semente (resultado removido e execução oculta) → reconferir/reexecutar. Política/estoques inicialmente vazios e botão bloqueado até seleção expressa. Nenhum parâmetro numérico foi preenchido por padrão pelo produto.

Caso observado, exclusivamente sintético: duração 60 min, semente 7, vida 100 pontos, radar 50 NM/probabilidade 1, assinatura 1 m²/fator 1, combustível 600 kg/taxa 2 kg/min, velocidade didática zero, posições locais separadas por 10 NM, reserva 100 kg, raio 200 NM/teto 10.000 m. Cada meio declarou 2 itens ar-ar, Pk 0,4, dano 10 pontos e alcance 20 NM. Esses números foram digitados como hipóteses de teste, não extraídos/aprovados do Command; o caso estacionário não valida cinemática real de aeronave.

Resultado observado: **60/60 minutos, quatro mísseis gastos, vida 100→90 pontos e combustível 600→480 kg em cada meio, zero perdas propostas e 494 eventos**. Download JSON efetivamente realizado; arquivo lido/validado no disco, incluindo todos os eventos e flags de não aplicação. A tela limita a lista a 100 eventos para manter o painel leve; o download conserva todos. UUIDs dos estoques permanecem no relatório, com rótulos curtos na tela.

Console sem erros/avisos capturados. Interface inspecionada em 1280×720 e 320×720; na tela estreita, documento de 320 px e painel de 260 px sem transbordamento horizontal. Override removido, tamanho natural reconferido. Não foi auditoria WCAG completa nem ensaio com leitor de tela. Captura fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-ensaio-controlado-20261118.png`.

Após as execuções, consulta SQLite somente leitura: integridade **ok**; propostas, decisões, efeitos/comandos operativos, execuções/saldos oficiais de ensaio e comandos de plotagem **zero**. Duas posições preservadas na revisão 1. Sessões de login são escritas legítimas do harness. Resultados locais do motor não foram confundidos com essas tabelas oficiais.

## Limites e continuidade

Entrega executa automaticamente apenas o par aéreo sintético, sob política expressa. Ainda faltam execução N×M, outros domínios, regras de defesa aplicáveis, adaptação geográfica, parâmetros físicos validados e origem durável para traduzir o resultado em proposta oficial rastreável. O resultado não desloca marcadores, não retira meios do mapa e não converte vida abstrata em percentual operativo. O instrutor continua deliberando no julgamento existente, com confirmação própria; não há encaminhamento automático de uma sugestão para o schema de origem didática humana.

Dados DB3K, originais, código extraído do ATLANTICADOR e bases/processos anteriores preservados. Código/documentação entregues em commits sequenciais na branch `codex/initial-siscan`, repositório autorizado `bozocf-hash/siscan`, com sincronização protegida para `C:/Users/bozoc/Documents/siscan` (`siscan-prototype` → `prototype`). Capturas, relatório baixado e bases temporárias ficam fora do Git. Atualizar arquivos não atualiza as rotas importadas de um processo antigo.

Conferência de sincronização: 12 arquivos comparados previamente com a base Git `8e9b2a5` antes da primeira escrita e idênticos byte a byte no destino. Links relativos dos documentos verificados; hashes dos planos anteriores `tasks/plan.md` e `tasks/todo.md` preservados. Revisão técnica de correção, fronteiras, privacidade, simplicidade e custo concluída dentro dos limites deste recorte; nenhuma alteração das regras oficiais de adjudicação.
