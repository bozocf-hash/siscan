# Tarefas — prontidão do ensaio CPC controlado

**2026-11-17. Estado: Fase 3 aprovada por “sim”; implementação em andamento.** Especificação aprovada por “sim”; plano aprovado por “prossiga” após a solicitação de revisão. Base: [plano aprovado](plan.md), [SPEC-force-confrontation — Recorte 4-A](../../../SPEC-force-confrontation.md), [121](../../../docs/recovery/121_ESPECIFICACAO_PRONTIDAO_ENSAIO_AUTOMATICO.md) e [122](../../../docs/recovery/122_PLANO_PRONTIDAO_ENSAIO_AUTOMATICO.md). O responsável também dispensou as solicitações de aprovação da skill Spec Driven Development para a continuidade deste recorte.

Após aprovação desta lista, executar sequencialmente com teste de comportamento falhando antes da mudança, verificação por incremento e commits coerentes. Checkpoints são verificações técnicas: comunicar evidências e continuar na execução autorizada, sem pedir aprovação a cada teste. Mudança material de contrato exige rever o ponto afetado. Preservar os planos anteriores, originais, DB3K, bases/processos em uso e decisões do instrutor.

## Comandos e evidências

Na raiz do repositório, Python em `C:/Users/bozoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. Nos comandos abaixo, `$pythonCpc` representa esse executável. Criar os verificadores antes de executá-los; contagem zero não é prova. Usar unittest, node:test, SQLite temporário e harness isolado existente. Não instalar dependências ou iniciar `app.py` na base principal.

Comandos focados previstos: `& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_readiness.py'`, `& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_readiness_http.py'` e `node --test siscan-prototype/check_cpc_readiness.mjs`. Esses três arquivos ainda não existem. Regressões existentes estão relacionadas em READY-10. Na raiz, `git diff --check`.

Cada tarefa atualiza seu estado neste checklist. Evidências distinguem testes JS/Python/HTTP de inspeção real do navegador. Não antecipar número de testes ou prontidão positiva. Até READY-05, um perfil ainda não validado integralmente nunca pode produzir resultado pronto; os primeiros incrementos são conferidos em harness isolado, sem ativação principal.

## READY-01 — Diagnóstico autorizado do par sem hipóteses

- [x] Serviço inicial de diagnóstico implementado; quatro testes focados passaram. A cobertura adicional de perdas/limites será ampliada nos incrementos seguintes.
- **Aceite:** serviço `consultar_prontidao` usa contexto público, escopo SQL de leitura e reconferência; devolve referência da base, perdas excluídas e pendências por campo/unidade. Nega operador/outro exercício antes de consultar grupos e informa cardinalidade/domínio não suportados sem reduzir composição. Não escreve nem cria RNG; todos os flags de execução/aplicação permanecem falsos.
- **Verificar:** teste focado Python para consulta sem perfil, grupo incompatível, perda, estado desconhecido, contexto/hash alterado e exceção; comparar banco/registro/RNG antes/depois e independência das cópias. AUTO-READY-01/02/03/05/06/09.
- **Dependência:** aprovação desta lista.
- **Arquivos:** `siscan-prototype/cpc_readiness.py`, `siscan-prototype/check_cpc_readiness.py`, este checklist — 3, médio.

## READY-02 — Consulta HTTP protegida e somente leitura

- [x] Rota de diagnóstico inicial implementada; três testes HTTP passaram (sessão/CSRF/papel, leitura sem efeitos e recusas).
- **Aceite:** `POST /api/cpc/trial-readiness` exige sessão/participação de instrutor, exercício aberto e CSRF, payload estrito e limite existente de corpo; query string recusada. Diagnóstico negativo válido retorna 200; erros seguem o contrato e não incluem detalhes adversários. Nenhuma migração ou recibo de aplicação é criado.
- **Verificar:** teste HTTP focado para 200 negativo, 400/401/403/404/409/503, revogação, corpo excedido, rota/query e dados de domínio preservados; reenvio de consulta não cria proposta/evento. Validação de perfil completo depende de READY-04/05. AUTO-READY-01/02/09/12.
- **Dependência:** READY-01.
- **Arquivos:** `siscan-prototype/app.py`, `siscan-prototype/check_cpc_readiness_http.py`, módulo de serviço se necessário, este checklist — até 4, médio.

## READY-03 — Primeiro diagnóstico visível no CPC

- [x] Painel inicial ligado; cinco testes JS novos passaram e o percurso negativo foi observado em navegador isolado na porta 61272.
- **Aceite:** depois da preparação, **Conferir prontidão do ensaio** abre uma única área de diagnóstico com resumo e detalhes por meio; sem perfil, mostra as pendências reais. Módulo/rota indisponível informa limitação e preserva preparação/julgamento. Operador não recebe botão/dados privados; não há botão de executar combate.
- **Verificar:** testes JS para consulta, erro, 401/403 e retorno ao julgamento; HTTP verifica autenticação/MIME/cache do novo asset. Fazer smoke no harness isolado e conferir pendências do caso sintético. AUTO-READY-01/03/05/06/11.
- **Dependência:** READY-02.
- **Arquivos:** `siscan-prototype/static/cpc-readiness.mjs`, `siscan-prototype/check_cpc_readiness.mjs`, `siscan-prototype/static/cpc-preparation.mjs`, `siscan-prototype/app.py`, este checklist — 5, médio.

### Checkpoint A — Caminho negativo utilizável

- [x] Percurso negativo observado no mesmo mapa: dois meios e pendências por partido, sem efeitos no exercício.
- [x] Autoridade, cardinalidade, perdas e falhas de fonte estão distintos e verificados nos testes Python/HTTP.
- [x] Resultados registrados; continuidade autorizada sem anúncio de confronto automático.

## READY-04 — Identificação e parâmetros do perfil didático

- [x] Validação de perfil implementada; casos parciais, tipos, identidades, unidades e origem verificados.
- **Aceite:** reconhecer formato/metadados e descritores com valor/unidade/origem; campo ausente gera pendência e valor/tipo inválido gera erro. IDs pertencem ao par e não se repetem; nota/rótulo do cliente não aprovam fonte. Validar condição inicial, domínio e parâmetros individuais sem defaults, preservando zero explícito e perdas oficiais.
- **Verificar:** testes Python/HTTP para perfil omitido, parcial e malformado; booleanos numéricos, negativos onde inválidos, NaN/Infinity, origem alegada, chaves extras e identidade estranha. Nenhuma hipótese limpa perda ou altera avaliação oficial. AUTO-READY-03/04/06/07/09.
- **Dependência:** READY-02; integração visual posterior a READY-03.
- **Arquivos:** módulo de serviço, seus verificadores Python de unidade/HTTP, este checklist — 4, médio.

## READY-05 — Conferência completa das entradas do par controlado

- [x] Conferência completa do par aéreo controlado implementada; nove testes Python e quatro HTTP passaram, incluindo prontidão positiva sem escritas.
- **Aceite:** validar estoques individuais, Pk/dano/alcance, contabilização defensiva quando aplicável, logística, condição aérea, escala abstrata e geometria local/fatores de assinatura. Coordenadas com sinal são válidas; não há conversão geográfica implícita, interpolação ou criação de recursos. Só perfil completo e coerente do recorte suportado pode retornar prontidão positiva, sempre sintética e sem execução.
- **Verificar:** testes positivos/negativos de todas as famílias de campos, incluindo quantidade/taxa/probabilidade zero, estoque duplicado/compartilhado, unidade/escala incompatível, fator ausente, geometria inconsistente e situação inicial impeditiva. Testar hash canônico e cópias. Um caso completo aéreo sintético precisa passar por HTTP sem efeitos no banco/RNG. AUTO-READY-04/05/07/08/09.
- **Dependência:** READY-04.
- **Arquivos:** módulo de serviço, seus verificadores Python de unidade/HTTP, este checklist — 4, médio.

## READY-06 — Formulário progressivo de hipóteses

- [x] Formulário progressivo observado no navegador com perfil parcial e completo; valores zero, falso e ausência cobertos por testes JS.
- **Aceite:** campos por Condição inicial, Sensores, Armamentos, Logística e Cenário, com unidade/origem e valores inicialmente não preenchidos. Não exigir JSON cru nem abrir todas as seções simultaneamente. O instrutor pode preencher o perfil, consultar e localizar o campo indicado por uma pendência; a tela identifica claramente hipótese e prontidão das entradas.
- **Verificar:** testes JS de coleta/presença dos valores sem tratar zero como vazio, perfil parcial/completo e mensagens vindas do servidor. Inspeção preliminar em tela estreita/desktop, teclado, foco e leitura dos rótulos. AUTO-READY-03/04/07/08/11.
- **Dependência:** READY-03 e READY-05.
- **Arquivos:** módulo JS de prontidão, seu verificador, `siscan-prototype/static/map-interface.css`, este checklist — 4, médio.

### Checkpoint B — Perfis e diagnóstico completo

- [x] Perfil parcial explica lacunas; perfil completo do caso controlado tem prontidão positiva; perfil inválido não é aceito.
- [x] Formulário mantém o mapa legível e o julgamento utilizável, sem defaults numéricos ou selos de validação fictícios.
- [x] Nenhuma dessas operações avança tempo ou altera estoques, perdas, posições ou propostas.

## READY-07 — Invalidação, saída e respostas atrasadas

- [x] Edição/resposta atrasada/403/descarte verificados por testes JS; cancelamento e descarte aceito observados na interface, incluindo reinicialização dos campos no mesmo par.
- **Aceite:** editar hipóteses, trocar seleção/fontes, sair ou perder autorização invalida diagnóstico. Resposta antiga não o restaura; timeout/erro nunca vira pronto. Troca entre prontidão e julgamento respeita edição não salva e retorno explícito, com aviso compreensível quando houver descarte e sem confirmação duplicada. Hipóteses continuam somente em memória.
- **Verificar:** testes JS com promises controladas para edição/troca/saída durante consulta, 401/403, falha/timeout, reentrada e retorno ao julgamento; conservar regressões de edição/decisão anteriores. AUTO-READY-10/11/12.
- **Dependência:** READY-06.
- **Arquivos:** módulo JS de prontidão, integração CPC, verificador JS de prontidão, `siscan-prototype/check_cpc_preparation.mjs`, este checklist — 5, médio.

## READY-08 — Robustez da captura e privacidade

- [x] Testes com arquivamento real durante diagnóstico, schema indisponível, limite de corpo e revogação passaram; SAVEPOINT liberado e SQL preservado. Total focado: 11 testes de serviço e 6 HTTP.
- **Aceite:** fonte/schema/integridade indisponível retorna indisponibilidade, não pendência vazia. Mudança de grupos observada na reconferência recusa o diagnóstico; IDs do pedido não contornam autorização. Sucesso, negativa e exceção mantêm domínio/registro/RNG intactos, sem depender de locks privados ou de alteração global do parser.
- **Verificar:** injetar mudança de revisão/arquivamento entre consultas públicas, corrupção e falha na leitura; testar liberação do SAVEPOINT, limites do perfil e mensagens sem vazamento. Usar sincronização controlada, sem sleeps como prova de concorrência. AUTO-READY-01/02/09/12.
- **Dependência:** READY-05 e READY-07.
- **Arquivos:** módulo de serviço, `siscan-prototype/app.py`, verificadores Python de prontidão/HTTP, este checklist — 5, médio.

### Checkpoint C — Diagnóstico seguro sob falha

- [x] Troca/falha não restaura dados antigos, não expõe o adversário ao operador e não deixa contexto parcialmente aceito.
- [x] Hash, fonte e ausência de efeitos estão demonstrados por comportamento, não só por inspeção de código.

## READY-09 — Percurso real do instrutor em ambiente isolado

- [ ] Executado e registrado.
- **Aceite:** harness com pasta/cookie/base próprios e porta livre; nenhuma reinicialização dos processos existentes ou uso da base principal. Percorrer diagnóstico sem hipóteses → perfil parcial → perfil completo → edição invalida → nova conferência → retorno ao julgamento. Operador não tem acesso à prontidão do par; perda confirmada continua fora do conjunto ativo.
- **Verificar:** navegador real em 320 px e desktop, rótulos/unidades, foco, mensagens, console e mapa único; salvar captura de evidência e remover viewport forçado. Comparar banco antes/depois das consultas; separar escritas legítimas de fixture/login de efeitos do diagnóstico. AUTO-READY-01–12.
- **Dependência:** READY-08.
- **Arquivos:** harness em `siscan-prototype/check_cpc_readiness_http.py` se necessário e este checklist — até 2. Capturas e bases de teste fora do Git.

## READY-10 — Regressões e revisão da entrega

- [ ] Executadas e conferidas.
- **Aceite:** verificadores novos têm casos reais e contagem não nula; regressões preservam julgamento, perdas no mapa, grupos, plotagem e silhuetas. Revisão de correção, simplicidade, fronteiras, privacidade e custo conclui sem riscos materiais pendentes do recorte. Não enfraquecer testes para obter sucesso.
- **Verificar:** descoberta Python `check_cpc_readiness*.py` e `check_cpc_*.py`; JS `check_cpc_readiness.mjs`, `check_cpc_judgment.mjs`, `check_cpc_preparation.mjs`, `check_map_presentation.mjs`, `check_map_groups.mjs`; verificadores `check_map_units.py`, `check_map_visuals.mjs`; `git diff --check`. Rodar checks pertinentes por incremento e consolidar antes da entrega, sem recontar a mesma execução.
- **Dependência:** READY-09.
- **Arquivos:** este checklist; se surgirem falhas, correção e teste afetados em incremento de até 5 arquivos, com evidência antes/depois. Não refatorar subsistemas alheios para acomodar esta entrega.

## READY-11 — Relatório de entrega e roteiro do instrutor

- [ ] Atualizados com evidências reais.
- **Aceite:** documento de entrega no próximo número livre distingue diagnóstico de execução, origem hipotética de dado aprovado e preservação de saldos/estado. Roteiro e README usam os nomes reais dos controles e explicam limitações do par/dados, hipótese transitória e como conferir a prévia correta.
- **Verificar:** links/nomes/estados coerentes com a interface observada; registrar comandos/contagens realmente executados, evidência e limites, sem anunciar confronto automático. AUTO-READY-11/12.
- **Dependência:** READY-10.
- **Arquivos:** documento de entrega novo, `docs/recovery/103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md`, `siscan-prototype/README.md`, este checklist — 4.

## READY-12 — Controles, sincronização e versão

- [ ] Concluídos e conferidos.
- **Aceite:** especificação/índice/registro do plano/tarefas refletem exatamente o entregue; aprovações históricas e planos incompletos anteriores preservados. Sincronizar para `C:/Users/bozoc/Documents/siscan` com conferência de divergência antes de sobrescrever; salvar commits por incremento e enviar ao repositório autorizado. Bancos, senhas, temporários e originais ficam fora do Git.
- **Verificar:** diff/hashes dos arquivos, links, status Git e remoto; comprovar que a pasta principal recebeu os arquivos esperados sem modificação de dados. Não afirmar que processo antigo foi atualizado apenas porque o arquivo foi sincronizado. AUTO-READY-12.
- **Dependência:** READY-11.
- **Arquivos:** SPEC-force-confrontation, índice 00, registro 122, registro 123 e este checklist — 5.

### Checkpoint final — Prontidão entregue e limites claros

- [ ] AUTO-READY-01–12 mapeados a evidências reais, com fatos observados separados de hipóteses/limitações.
- [ ] Instrutor consegue usar a conferência; o fluxo didático anterior continua funcionando.
- [ ] Relatório final indica o que foi implementado, testado e o que ainda falta para executar o confronto automático.

## Aprovação solicitada

Esta lista é a Fase 3. A aprovação permitirá implementar READY-01–12 e percorrer seus checkpoints sem novas confirmações rotineiras, dentro deste recorte. Não autoriza execução automática, DDL, mudança de regras/coeficientes, ampliação N×M ou migração/reinício principal. A skill Spec Driven Development determina validar a fase atual antes da implementação.
