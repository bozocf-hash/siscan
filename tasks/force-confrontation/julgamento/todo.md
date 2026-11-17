# Tarefas: julgamento didático e efeitos no mapa

**2026-11-17. Especificação e plano aprovados por “sim”; Fase 3 aprovada por “sim”; Fase 4 em execução.** Base: [especificação — Recorte 3](../../../SPEC-force-confrontation.md), [plano aprovado](plan.md) e [115](../../../docs/recovery/115_TAREFAS_JULGAMENTO_DIDATICO_NO_MAPA.md). Entregas 108/112 e planos anteriores preservados. Após aprovação desta lista, implementar sequencialmente, com testes de comportamento antes da mudança correspondente e commits por incremento verificado.

O aceite final é o percurso real do instrutor no mapa, não apenas backend. Checkpoints são verificações técnicas: comunicar resultados e continuar sem confirmações rotineiras durante a execução aprovada. Mudança material exige rever o ponto afetado. Não migrar o principal, reiniciar processos em uso, editar originais/DB3K ou criar produtor automático.

## Comandos previstos

Na pasta `prototype` de entrega (`siscan-prototype` no repositório):

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_cpc_judgment.py
& $pythonCpc check_cpc_judgment_http.py
& $pythonCpc check_operational_state.py
& $pythonCpc check_operational_state_storage.py
& $pythonCpc check_unit_groups.py
& $pythonCpc check_cpc_map.py
& $pythonCpc check_cpc_group_preparation.py
& $pythonCpc check_map_groups.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_map_units.py
node check_cpc_judgment.mjs
node check_cpc_preparation.mjs
node check_map_groups.mjs
```

Na raiz: `git diff --check`. Verificadores de julgamento ainda não existem; nenhum teste executado nesta fase documental. Rodar os comandos pertinentes por incremento, sem repetir bateria por documentação ou somar novamente a mesma execução. HTTP/navegador usam banco, cookie, porta e meios descartáveis. Teste vazio e leitura de código não substituem verificação funcional/visual.

## JUD-01 — Consultar proposta/recibo e conferir efeitos por API pública

- [x] Leituras públicas/prévia implementadas; 28 testes do provedor e 19 de armazenamento passaram.
- **Aceite:** instrutor participante consulta proposta/revisões/decisão/recibo mesmo sem grupos; índice limitado/cursor estrito e filtro de origem CPC, sem snapshots completos. Retorno verifica integridade/contexto e não grava. Transformação pública de antes/depois mantém as regras de índice/perda/correção de 112 e não publica efeitos.
- **Verificar:** testes em `check_operational_state.py` e `check_operational_state_storage.py` para papel, revogação, contexto, paginação, registro pendente/decidido, corrupção e SQL preservado; comparar prévia com efeito confirmado. Operador não recebe proposta/motivo privado. JMAP-01/03/06/07/09/12.
- **Dependência:** aprovação desta lista.
- **Arquivos:** `siscan-prototype/operational_state.py`, seus dois verificadores e este checklist. Médio, até quatro arquivos.

## JUD-02 — Proteger revisões de grupos por escopo público

- [x] Escopo público implementado; 32 testes do registro passaram, incluindo disputa e saída por exceção.
- **Aceite:** conferir contexto, grupos ativos/revisões de ambos os partidos e manter o escopo até a saída. Leituras reentrantes permitidas; adaptador não chama mutação do registro dentro do escopo. Thread concorrente só publica mudança após sua liberação; exceção libera o escopo sem alterar grupos.
- **Verificar:** `check_unit_groups.py` com eventos/barreiras e limite de espera, sem sleeps: revisão/arquivo antes do escopo, mutação concorrente bloqueada, saída normal/exceção e cópias independentes. Preservar operações/recibos existentes. JMAP-02/05/12.
- **Dependência:** JUD-01 para integração posterior; o registro continua independente do provedor SQL.
- **Arquivos:** `siscan-prototype/unit_groups.py`, `check_unit_groups.py`, este checklist. Pequeno, três arquivos.

### Verificação de fundação

- [x] Leituras/prévia e escopo verificados, sem publicação adicional ou ciclo.
- [x] Interfaces públicas verificadas antes do adaptador.

## JUD-03 — Capturar base de julgamento e prévia sem escrita

- [x] Base/prévia implementadas; quatro testes passaram, sem escrita e com invalidação de referências.
- **Aceite:** autorização antes de ler adversário; preparar par por 108, acrescentar estados oficiais/revisões e hash de base separado. Efeitos só em membros explícitos do par, com omissão preservada e motivo; origem/ref/snapshot/domínio obtidos pelo servidor. Mudança da base recusa prévia antiga, sem reconstruir força ou substituir desconhecido por zero.
- **Verificar:** novo `check_cpc_judgment.py` com grupo/snapshot/adjudicação/posição/estado/cenário alterados, duplicação/unidade externa/campos injetados, ausência e schema indisponível. Comparar SQL e registro antes/depois de contexto/prévia; nenhum recibo fictício. JMAP-01/02/03/07/10.
- **Dependências:** JUD-01/02.
- **Arquivos:** novo `siscan-prototype/cpc_judgment.py`, novo `check_cpc_judgment.py`, este checklist. Pequeno, três arquivos.

## JUD-04 — Registrar e retomar propostas CPC duráveis

- [x] Registro/revisão/retomada/replay implementados; cinco testes do adaptador passaram.
- **Aceite:** base esperada e referências reconferidas; origem `siscan-cpc-didactic-origin-01` e hash da intenção HTTP construídos no servidor. Registro/revisão usa somente publicador 112, sem efeitos oficiais; revisão substitui conteúdo completo e exige referência vigente. Retomada distingue origem congelada de disponibilidade atual, inclusive após perder grupos.
- **Verificar:** `check_cpc_judgment.py`: base desatualizada, proposta de outra origem/exercício, paginação, proposta decidida/pendente e leitura após registro novo em memória vazio. Replay exato de registro/revisão devolve recibo; mesma chave com outra intenção recusa, sem depender de grupo atual para comando já aplicado. JMAP-01/02/03/05/06.
- **Dependência:** JUD-03.
- **Arquivos:** `siscan-prototype/cpc_judgment.py`, `check_cpc_judgment.py`, este checklist. Pequeno, três arquivos.

## JUD-05 — Confirmar/rejeitar com revisão protegida e aplicação única

- [ ] Implementar decisão CPC e a coordenação transacional de novas escritas.
- **Aceite:** conexão independente, reserva SQL → escopo público do registro → conferência/aplicação → commit ainda protegido. Confirmação usa exatamente revisão/hash/base aceitos; rejeição não exige grupo disponível, conforme 112. Replay autorizado consulta recibo antes de revalidar grupo antigo; correção é nova proposta referenciada, sem apagar decisão.
- **Verificar:** `check_cpc_judgment.py` com conexões/threads controladas e timeout: grupo alterado antes/durante confirmação, duas decisões, estado concorrente, falha entre integrantes/commit e transação externa recusada. Comprovar ordem de locks, ausência de deadlock e lote integral, sem escrita em recursos/posição/tempo/snapshot. JMAP-02/03/04/05/06/07.
- **Dependências:** JUD-04 e fundação verificada.
- **Arquivos:** `siscan-prototype/cpc_judgment.py`, `check_cpc_judgment.py`, este checklist. Pequeno, três arquivos; correção de contrato público retorna à tarefa correspondente.

### Checkpoint A — Backend do julgamento

- [ ] Base/prévia, registro/revisão e confirmação/rejeição/retomada verificadas pelo publicador único.
- [ ] Alteração concorrente de grupo/estado serializada ou recusada, com rollback/replay e commit durável comprovados.
- [ ] Sem aplicação por prévia/rejeição ou alteração de recursos/mapa/relógio; autorização e origem separadas.

## JUD-06 — Expor rotas autenticadas e CSRF

- [ ] Integrar contexto/prévia, registro, revisão, decisão, índice e consulta individual ao servidor existente.
- **Aceite:** contratos estritos de corpo/query/caminho e contexto de sessão; POST com CSRF, erros 401/403/400/404/409/503 coerentes e sem falso vazio/sucesso. Nenhuma migração por requisição ou chamada HTTP interna para resolver fonte.
- **Verificar:** novo `check_cpc_judgment_http.py`, reutilizando harness isolado: login/papel/participação/CSRF, formato/contexto injetado, fluxo completo, revisão antiga, resposta/recibo repetidos, schema/fonte indisponível e visibilidade. Regressões HTTP de grupos quando rotas compartilhadas forem afetadas. JMAP-01/03/04/05/06/09/10/12.
- **Dependência:** JUD-05 e Checkpoint A.
- **Arquivos:** `siscan-prototype/app.py`, novo `check_cpc_judgment_http.py`, `cpc_judgment.py` se necessário e este checklist. Médio, até quatro arquivos.

## JUD-07 — Disponibilizar prévia persistente isolada

- [ ] Implementar modo `--serve --data-dir` do harness sem reseed de base já existente.
- **Aceite:** primeira execução cria apenas dados/mapa/migração de teste em pasta própria identificada; reabertura verifica a titularidade da pasta/base e preserva histórico. Porta/cookie/contas próprios; não aceitar pasta/base principal ou existente sem identificação do harness. Reinício não recria grupos para fingir continuidade.
- **Verificar:** `check_cpc_judgment_http.py` em diretórios temporários: primeiro uso/reabertura, pasta não pertencente ao harness recusada sem escrita, histórico preservado e grupos ausentes após reinício. Preparar comandos reproduzíveis de prévia; não encerrar processos alheios. JMAP-06/10/12.
- **Dependência:** JUD-06.
- **Arquivos:** `siscan-prototype/check_cpc_judgment_http.py`, este checklist; helper de teste separado somente se necessário, mantendo até três arquivos.

## JUD-08 — Projetar estado oficial nas consultas do mapa

- [ ] Acrescentar projeção oficial mínima à consulta autorizada de meios existente.
- **Aceite:** identidade demonstrada recebe estado confirmado/revisão/origem, sem motivo privado ou adversário; diferenciar não avaliado, armazenamento não habilitado e integridade indisponível. Meio sem instância continua plotável sob regra anterior. Sem novo publicador, ciclo de imports, migração ou saldo de ensaio promovido a estado oficial.
- **Verificar:** `check_cpc_judgment.py` e/ou `check_map_units.py` com confirmação, ausência, schema ausente/corrompido, operador por partido e meio sem instância; comparar SQL sem escrita e regressões `check_map_groups.py`/HTTP se pertinentes. JMAP-07/08/09/10/12.
- **Dependências:** JUD-01/06; harness JUD-07 disponível para observação seguinte.
- **Arquivos:** `siscan-prototype/map_units.py`, `check_map_units.py`, `check_cpc_judgment.py` se necessário e este checklist. Médio, até quatro arquivos.

### Checkpoint B — HTTP e projeção

- [ ] Fluxo HTTP completo verificado em base/porta/cookie isolados, com contratos de acesso/erro e sem DDL por requisição.
- [ ] Projeção oficial e privacidade confirmadas; armazenamento ausente preserva planejamento e não fabrica avaliação.
- [ ] Harness abre novamente a própria base sem reseed ou reconstrução de grupos; principal preservado.

## JUD-09 — Editar e registrar julgamento pelo painel

- [ ] Implementar controlador/formulário de contexto, edição, prévia e registro/revisão.
- **Aceite:** módulo próprio instalado no CPC existente, uma área lateral; alterações explícitas de índice/perda e motivo com prévia antes/depois. Preservar/retirar avaliação são ações distintas; vazio não vira zero. Ajuste posterior marca revisão não salva; não confirmar ou salvar implicitamente.
- **Verificar:** novo `check_cpc_judgment.mjs` com validação local, payloads enviados, respostas atrasadas/fora de contexto, troca de seleção e saída com edição não salva. Preview não envia comando de aplicação. Módulo autenticado/opcional mantém mapa anterior em instância antiga. JMAP-03/04/07/10/11.
- **Dependências:** JUD-06/08 e Checkpoint B.
- **Arquivos:** novo `siscan-prototype/static/cpc-judgment.mjs`, novo `check_cpc_judgment.mjs`, `static/cpc-preparation.mjs`, `app.py` para servir módulo e este checklist. Médio, até cinco arquivos.

## JUD-10 — Confirmar, rejeitar, retomar e corrigir pelo painel

- [ ] Implementar revisão final explícita, decisões e recuperação da intenção/recibo na interface.
- **Aceite:** Confirmar efeitos → Confirmar aplicação envia revisão aceita; cancelar não aplica. Retry mantém UUID e intenção; após commit/refresh falho, conservar recibo e indicar vista pendente sem novo comando. Retomada/histórico e nova proposta de correção não recriam grupo, reaplicam decisão ou apagam passado.
- **Verificar:** `check_cpc_judgment.mjs` com duplo clique, falha/resposta perdida, retry, rejeição, revisão editada, refresh falho, grupo ausente, retorno de consulta antiga e correção referenciada. Nenhum efeito disparado por reload, seleção ou abertura de histórico. JMAP-04/05/06/07/11.
- **Dependência:** JUD-09.
- **Arquivos:** `siscan-prototype/static/cpc-judgment.mjs`, `check_cpc_judgment.mjs`, `static/cpc-preparation.mjs` se necessário e este checklist. Médio, até quatro arquivos.

## JUD-11 — Mostrar efeitos oficiais no mesmo mapa

- [ ] Integrar atualização de marcador/hover/lista e retorno ao planejamento.
- **Aceite:** somente projeção oficial altera informações visuais do meio, com texto/valor/origem temporal; prévia não repinta como aplicada. Faixas só em superfície comprovada e perda não exibida como aptidão de combate. Preservar mapa, silhuetas, camada única, bloqueio de plotagem e dados desconhecidos explícitos.
- **Verificar:** controlador/ponte e regressões `check_cpc_preparation.mjs`, `check_map_groups.mjs`, `check_map_units.py` pertinentes; no harness preparar percurso gráfico para JUD-12. Refresh oficial, troca de partido/saída e respostas atrasadas não restauram dados revogados ou geram movimento. JMAP-07/08/09/10/11/12.
- **Dependências:** JUD-08/10.
- **Arquivos:** `siscan-prototype/static/atlantic-bridge.mjs`, `static/cpc-preparation.mjs`, `static/cpc-judgment.mjs` se necessário, `check_cpc_judgment.mjs` e este checklist. Médio, até cinco arquivos.

### Checkpoint C — Painel e mapa integrados

- [ ] Controle de intenção/revisão, confirmação em duas ações, retry e falha de refresh verificados, sem aplicação implícita.
- [ ] Projeção oficial consistente em lista/hover/planejamento, sem novo mapa, movimentação ou dados inventados.

## JUD-12 — Observar o marco parcial no navegador e após reinício

- [ ] Verificar o percurso real completo em prévia isolada persistente e registrar evidências.
- **Aceite:** selecionar par → abrir julgamento → prévia → registrar/revisar → confirmar/rejeitar → estado/histórico no mapa. Conferir correção, reload, teclado/foco/tela estreita e restauração de largura; operador só vê próprio estado oficial. Processo novo recupera histórico/recibo; proposta sem grupo disponível não confirma.
- **Verificar:** navegador real com dados descartáveis e base persistente do harness, comparação SQL antes/depois e logs disponíveis. Encerrar/reiniciar apenas processo de teste identificado, nunca principal/prévia alheia. Registrar screenshots/limites e testes realmente observados, sem substituir browser por inspeção de código ou anunciar automático. JMAP-01–12 conforme matriz do plano.
- **Dependências:** JUD-11 e Checkpoint C.
- **Arquivos:** evidências locais fora do Git, harness de teste e este checklist; correção funcional retorna à tarefa afetada e verificação pertinente.

### Checkpoint D — Aplicativo parcial demonstrado

- [ ] Percurso real, rejeição sem efeito, confirmação única, consulta e recuperação observados; JMAP-01–12 rastreados a evidência real.
- [ ] Contagens sem dupla soma, regressões pertinentes aprovadas e dados/posições/recursos do usuário preservados.
- [ ] Versão parcial identificada como prévia isolada; nenhum confronto automático, implantação/migração/reinício principal alegado.

## JUD-13 — Documentar a entrega e o roteiro do instrutor

- [ ] Revisar código/contratos e consolidar documentos em incrementos pequenos.
- **Aceite:** subpasso A atualiza README, relatório numerado livre, roteiro 103 e checklist com passos reais, contas/URL de teste e limites. Subpasso B atualiza especificação/plano/checklist com gates concluídos. Subpasso C atualiza controles 00/09/10, mapa de capacidades e checklist sem contradições com a disponibilidade observada.
- **Verificar:** revisão do código/diff, links locais, contagens/evidências e hashes dos planos antigos. Não repetir testes por edição apenas documental. Relatar separadamente código instalado, prévia executando e principal sem migração.
- **Dependências:** JUD-12 e Checkpoint D.
- **Arquivos:** até cinco por subpasso; sem nova alteração funcional. Relatório em `docs/recovery/`; manter os planos independentes intactos.

## JUD-14 — Sincronizar e publicar os incrementos

- [ ] Entregar somente código/documentação autorizados na pasta SISCAN e no GitHub.
- **Aceite:** comparar destino com base conhecida antes de copiar, verificar SHA-256, preservar alterações externas e não incluir banco, backup, credenciais ou arquivos originais. Commits por incremento verificado na branch existente; push/situação final comprovados. Manter prévia identificada se entregue e não reiniciar principal/grupos temporários.
- **Verificar:** hashes/diff/commits/resultado do envio e URL da prévia quando em execução. Não declarar o fluxo disponível no servidor principal sem procedimento específico e observação real.
- **Dependência:** JUD-13.
- **Arquivos:** este checklist/relatório e cópias dos arquivos produzidos; sem nova mudança funcional.

## Gate

Especificação e plano aprovados por “sim”; revisar esta lista concreta antes da Fase 4. Depois de aprovada, executar JUD-01–14 sequencialmente, com os checkpoints técnicos previstos e sem novas confirmações rotineiras. Não antecipar migração principal, confronto automático ou ampliação de escopo.
