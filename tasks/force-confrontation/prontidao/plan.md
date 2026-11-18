# Plano técnico — prontidão do ensaio CPC controlado

**Data: 2026-11-17. Estado: Fase 2 proposta para revisão.** Especificação do Recorte 4-A aprovada pelo responsável por “sim”, após 121. A aprovação abrange conferência de entradas, não execução automática ou parâmetros de combate.

Contrato: [SPEC-force-confrontation — Recorte 4-A](../../../SPEC-force-confrontation.md). Registro: [121](../../../docs/recovery/121_ESPECIFICACAO_PRONTIDAO_ENSAIO_AUTOMATICO.md). Este diretório segue a convenção já usada em `mapa/` e `julgamento/`, preservando os planos incompletos `tasks/plan.md` e `tasks/todo.md`. A lista detalhada será criada aqui em `todo.md` na Fase 3, depois da revisão deste plano; não existe nesta etapa.

## Marco verificável

No mesmo CPC, o instrutor prepara os grupos e aciona **Conferir prontidão do ensaio**. Sem hipóteses, obtém pendências reais. Um perfil didático completo para o par controlado pode produzir **Entradas prontas para ensaio controlado**, sem disparar, avançar tempo, consumir recursos ou registrar proposta. Grupo maior/domínio não demonstrado recebe motivo de não suporte, sem selecionar um integrante por conveniência. Julgamento didático continua utilizável.

A prontidão é das entradas declaradas: não é autorização de emprego, previsão real, prova de que haverá engajamento ou reserva de recursos. Todas as respostas mantêm `official_calculation_ready=false`, `simulation_started=false` e `official_effects_applied=false`.

## Dependências e sequência

```text
Contexto público CPC + estados oficiais + identidades/snapshots
                  ↓
Diagnóstico de lacunas e limites do par controlado
                  ↓
HTTP autorizado + diagnóstico visível no painel existente
                  ↓
Validação do perfil de hipóteses + formulário progressivo
                  ↓
Conferência positiva/negativa, invalidação e preservação de dados
                  ↓
Navegador isolado + documentação de entrega
```

Sem novo resolvedor, serviço, banco, dependência ou trabalho com agentes paralelos. As fatias compartilham contratos e serão sequenciais. A captura, validação e apresentação serão pequenas funções/módulos; não criar um framework de regras para esta conferência.

## Provedores e captura da fonte

1. O adaptador HTTP reutiliza sessão, participação e CSRF do servidor. A camada de serviço também exige instrutor participante/exercício aberto antes de consultar dados dos grupos. Formato e query string seguem a convenção CPC; nunca retornar o adversário ao operador.
2. Validar payload estrito e teto existente de 64.000 bytes; não ampliar o limite global de `Handler.read_json`. O módulo valida números finitos explicitamente, pois o parser JSON atual aceita representações não finitas que não devem chegar à serialização canônica.
3. Abrir escopo de leitura SQL com SAVEPOINT próprio, liberado ou revertido corretamente. Chamar a API pública `cpc_judgment.context` com seleção e `expected_view_sha256`. Não importar `_view`, `_refs`, locks privados ou fixtures na produção. Não abrir transação de escrita para uma consulta.
4. Usar estados individuais da base para excluir `lost is True`, preservando no resultado o motivo e a identidade da exclusão. `lost=None` permanece não avaliado: exige hipótese inicial explícita quando necessária; não vira disponível por omissão. Hipótese não restitui perda confirmada.
5. Quando necessário à exposição de origem, consultar `map_units.listing` por partido dentro do mesmo escopo SQL. Seu saldo atual continua separado da capacidade/snapshot e dos valores hipotéticos. A primeira versão não promove campos brutos do DB3K nem inventa um provedor de aprovação técnica.
6. Depois da conferência, chamar novamente o contexto público e comparar sua base com a capturada. Revisão/arquivamento de grupo observado recusa por conflito. A vista SQL é uma captura coerente; mudança após seu término pode torná-la histórica. Readiness não reserva dados ou disponibilidade para execução futura.

Se o schema/provedor existente estiver ausente ou íntegro não puder ser demonstrado, responder indisponibilidade, não uma lista vazia de pendências. Nenhuma migração ocorre em GET/POST. Este procedimento não promete atomicidade distribuída entre SQL e o registro temporário de grupos.

## Contrato interno proposto

Arquivo novo: `siscan-prototype/cpc_readiness.py`.

- `consultar_prontidao(db, user, registry, body) -> dict`: autorização, captura das fontes públicas, reconferência e envelope de resposta.
- Validação/diagnóstico em função separada, recebendo base capturada e hipóteses, devolvendo dados independentes das entradas. Sem leitura de arquivo, rede, simulação ou escrita. Não aceitar snapshots enviados pelo cliente como base.
- Reutilizar validadores públicos de números/estoques em `cpc_models` quando semanticamente adequados. Coordenadas locais aceitam sinal; não usar validador de quantidade não negativa para x/y. Não duplicar fórmulas de dano ou detecção.
- Instanciar somente estruturas de dados necessárias à validação, e apenas com entradas completas e explícitas. `CenarioTatico` pode conferir geometria/fatores; não construir `GerenciadorDeCombate` ou `SimulacaoTemporal`, criar RNG ou chamar detecção/disparo/turno para verificar prontidão.
- Serialização e SHA-256 usam a convenção canônica existente (`engine_units.encoded`/`cpc_judgment.digest`), sem horário, UUID ou ordem de inserção como fonte de variação.

O limite do consumidor atual é um integrante utilizável por partido. Para qualquer outro número, registrar `unsupported_by_current_engine`; não calcular confrontos N×M, somar poder ou escolher um representante. O domínio só é demonstrado pela evidência do provedor. A configuração real de demonstração reconhecida hoje é aérea sintética; testes de nomes/modelos não poderão promover meios navais ou reais por inferência.

## Formato do perfil — detalhamento técnico

Payload: `selection`, `expected_view_sha256` e `hypotheses` opcional. Chaves extras recusadas. `hypotheses`, quando presente, é objeto com somente `schema_version`, `label`, `revision`, `scenario` e `units`.

Formato reconhecido: `siscan-cpc-trial-hypotheses-01`. Metadados/campos ausentes geram pendências; versão fornecida incompatível, tipo errado ou valor inválido gera 400. `label`/notas são texto limitado e sem interpretação como HTML. Revisão, duração, semente e quantidades são inteiros, sem aceitar booleanos como números. Duração positiva; semente zero é válida. Não inserir valores iniciais de duração, semente, vida ou eficácia.

`units` é uma lista de registros únicos `{unit_id, parameters, armamentos}`. IDs devem pertencer à seleção capturada, sem repetição. Limitar coleções/textos ao conteúdo do pedido e aos limites do endpoint; não aceitar listas sem teto lógico, IDs de estoques duplicados ou estoques compartilhados entre unidades. Parâmetros de integrantes perdidos não podem reincluí-los no conjunto ativo.

Cada grandeza declarada usa descritor `{value, unit, source, note?}`. O primeiro caminho é `source='didactic_assumption'`; `source='unavailable'` mantém a pendência. Campo ausente ou valor desconhecido não recebe default. Origem aprovada só pode ser reconhecida se resolvida por provedor confiável e finalidade pertinente; rótulo ou nota do cliente não são prova. Primeiro marco não depende de aprovação técnica Command ainda inexistente.

| Grupo | Campos / representação |
|---|---|
| Cenário | Duração em minutos, semente, identificação da escala abstrata comum a vida/dano e referência local didática; fatores de assinatura por valor exato, sem interpolação |
| Unidade | `pontos_de_vida`, `assinatura_radar`, `velocidade`, `alcance_radar`, `probabilidade_deteccao`; disponibilidade inicial assumida quando o oficial não for avaliado |
| Estoque | Identificador, tipo aceito pelo motor, quantidade/unidade de contabilização, Pk, dano na escala declarada e alcance máximo; itens/alternativas não são agregados |
| Logística | `combustivel_atual` kg, `taxa_consumo_combustivel` kg/min; dados expressamente hipotéticos continuam distintos dos saldos oficiais |
| Aéreo | `raio_de_acao` NM, `teto_operacional` m, `combustivel_minimo_retorno` kg e `estado_voo` explícito, sem assumir o default do construtor |
| Defesa, se aplicável | Eficácia didática, estoque defensivo identificado e custo inteiro positivo por tentativa na mesma unidade de contabilização; sem munição criada ou custo presumido |
| Geometria | Posição local x/y em NM por unidade, rumos normal/evasão em graus conforme convenção existente e distâncias coerentes; não converter latitude/longitude neste módulo |

Probabilidades são adimensionais na faixa 0–1; não interpretar porcentagem como fração. Grandezas negativas são recusadas onde o motor exige não negatividade; coordenadas locais negativas são válidas. Rumos seguem o limite de 0–360 já usado no módulo temporal. Unidades incompatíveis são recusadas, sem conversão silenciosa. Fator de assinatura precisa ter correspondência exata; pares repetidos não podem sobrescrever evidência silenciosamente.

Quando posições locais forem fornecidas, distância euclidiana pode ser derivada de modo identificado; isso não é conversão geográfica. Se o perfil também declarar distância, conferir consistência pela convenção pública do cenário. Nada disso altera as coordenadas de planejamento.

Quantidade zero, taxa zero e probabilidades zero são valores declarados, não ausência. Podem originar avisos de falta de engajamento/sustentação, sem adulterar estoques. Situação inicial incompatível com o consumidor vira condição impeditiva identificada, distinta de campo ausente. Este plano não decide política de ações, salvas, iniciativa ou seleção de alvo.

## Resposta e erros

A resposta só contém o diagnóstico necessário: versão, contexto/cenário/seleção, hashes/revisões de origem, hash das hipóteses quando fornecidas, `scope='controlled_pair'`, unidades incluídas/excluídas e pendências/avisos. Não repetir todos os snapshots ou inventário do exercício no payload.

Cada item: código estável, categoria (`missing_data`, `unsupported_by_current_engine`, `operational_condition` ou aviso), `unit_id` opcional, caminho do campo, mensagem e providência. Ordenação determinística para comparação. Campos inicialmente previstos: `status`, `ready_for_controlled_trial`, `issues`, `warnings` e os três flags falsos do marco. `ready_for_controlled_trial` só será verdadeiro sem itens impeditivos. Se houver limite de motor, o resumo prioriza não suporte, mas mantém as demais pendências; lacunas de dados mantêm entradas incompletas. A interface traduz os rótulos para português.

HTTP 200 para diagnóstico negativo válido; 400 formato/valor inválido; 401 sessão; 403 autoridade; 404 referência autorizada ausente; 409 base/revisão conflitante; 503 fonte/schema/integridade indisponível. Erros seguem `{error: mensagem}` do servidor existente; códigos de pendências pertencem ao diagnóstico 200. Não reestruturar as outras APIs.

## HTTP e interface

Nova rota `POST /api/cpc/trial-readiness`, sem query string, protegida como os POST CPC existentes. Adaptador enxuto em `app.py`; módulo de serviço não grava UUID de comando, proposta ou evento de combate para essa consulta.

Módulo candidato: `static/cpc-readiness.mjs`, carregado de forma recuperável. Sua ausência/404 não derruba preparação ou julgamento em instância antiga. Incluir o asset na mesma lista autenticada de módulos do mapa, com MIME/cache existentes; endpoint e dados de prontidão exclusivos do instrutor; o asset segue a autenticação estática existente, sem tratar a visibilidade do botão como autorização.

Em `static/cpc-preparation.mjs`, manter o ponto de entrada **Conferir prontidão do ensaio** após preparação válida. Usar uma área ativa: consulta/hipóteses ou julgamento; nunca dois formulários abertos disputando o painel. A transição respeita edição não salva do julgamento. Retorno explícito ao julgamento, sem apagar propostas registradas. Edição transitória de hipóteses deve ter saída compreensível e aviso de descarte quando necessário, evitando confirmações duplicadas.

Formulário por seções expansíveis: Condição inicial, Sensores, Armamentos, Logística e Cenário. Campos em branco, unidade junto do rótulo e origem identificada; sem obrigar JSON cru, código de banco ou cinquenta campos simultaneamente visíveis. Pendência permite localizar o campo correspondente. Usar tokens e densidade de 117–119, sem redesenhar silhuetas. Não acrescentar botão de executar nesta entrega.

Controlador recebe preparação/revisão e perfil; edição, troca de grupo, atualização de fonte e saída invalidam o resultado e sua geração. Resposta antiga não restaura diagnóstico ou dados de outro contexto. 401/403 limpa dados privados e comunica revogação ao painel proprietário; erro não vira resultado pronto. Requisições usam timeout e foco/aria-live conforme os adaptadores existentes. Hipóteses ficam em memória, sem localStorage ou persistência automática.

## Fatias propostas e checkpoints

Esta é a ordem do plano, não a lista detalhada da Fase 3.

| Fatia | Entrega verificável | Arquivos candidatos / porte |
|---|---|---|
| 1 | Serviço retorna lacunas, não suporte e exclusão por perda, com autorização/reconferência e nenhuma escrita | `cpc_readiness.py`, `check_cpc_readiness.py` — 2 |
| 2 | Instrutor consulta diagnóstico negativo pela rota e painel; sessão/partido/CSRF e fallback testados | `app.py`, `check_cpc_readiness_http.py`, `static/cpc-preparation.mjs`, `static/cpc-readiness.mjs`, `check_cpc_readiness.mjs` — até 5 |
| Checkpoint A | Percurso sem hipóteses explica bloqueios no mesmo mapa, mantém julgamento e preserva dados | AUTO-READY-01/02/03/05/06/09/11 |
| 3 | Perfil completo/incompleto/inválido é validado; caso aéreo sintético controlado pode ter prontidão positiva | Módulo de serviço e verificadores Python de unidade/HTTP — até 3 |
| 4 | Instrutor preenche hipóteses por seção, consulta novamente e perde a validação antiga ao editar/sair | Módulo JS, integração CPC, CSS e verificador JS — até 4 |
| Checkpoint B | Casos positivo e negativo, invalidade e troca de contexto demonstrados sem execução ou aplicação | AUTO-READY-04/07/08/09/10/11 |
| 5 | Concorrência observada, erros, privacidade e regressões das fatias anteriores ficam verificados | Verificadores focados e módulos correspondentes, dividindo se exceder 5 arquivos |
| 6 | Percurso real no navegador, documentação de entrega, sincronização e Git | Documentação em lotes de até 5; nenhum original ou banco principal |
| Checkpoint final | Doze critérios demonstrados; relatório distingue execução de teste, observação visual e funcionalidades ainda ausentes | AUTO-READY-01–12 |

A Fase 3 detalhará aceites, dependências, verificações e arquivos de cada tarefa em `tasks/force-confrontation/prontidao/todo.md`. Não executar fatias só porque constam neste plano proposto.

## Verificação planejada

Usar unittest/SQLite temporário e `node:test`, seguindo os verificadores existentes. Testar sem perfil, perfil parcial, conjunto completo, zero explícito, coordenada negativa, perda confirmada, estado não avaliado, vários integrantes, domínio não demonstrado, quantidade fracionária, booleano numérico, NaN/Infinity, chaves extras, IDs duplicados/estranhos e unidade/escala incompatível. Perfil completo positivo é hipótese sintética identificada, sem falsificar uma aprovação Command.

Comparar dados de domínio antes/depois de respostas positivas, negativas e exceções; capturar RNG global e garantir que não é consultado/alterado. Conferir cópias e hash canônico; reordenar chaves mantém hash, mudar valor/unidade/origem muda hash. Alteração observada de grupo/versão invalida consulta sem resultado parcial. SQL e memória não devem sofrer mutação por validação.

Testes HTTP cobrem identidade, exercício, CSRF, mensagens sem dados adversários, limite de corpo, query string, endpoint exato e indisponibilidade. Testes JS cobrem leitura, edição, resposta atrasada, 401/403, erro e preservação do julgamento. Não reduzir as verificações de 120 para acomodar a tela nova.

Comandos futuros, na raiz, somente depois de existirem os novos verificadores (confirmar contagem não nula):

```powershell
$pythonCpc = 'C:/Users/bozoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_readiness*.py'
node --test siscan-prototype/check_cpc_readiness.mjs
& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_*.py'
node --test siscan-prototype/check_cpc_judgment.mjs siscan-prototype/check_cpc_preparation.mjs siscan-prototype/check_map_presentation.mjs siscan-prototype/check_map_groups.mjs
& $pythonCpc siscan-prototype/check_map_units.py
node siscan-prototype/check_map_visuals.mjs
git diff --check
```

Sem build ou pacote a instalar. Harness de navegador: reutilizar o contexto público `persistent_server` de `check_cpc_judgment_http.py`, pasta temporária nova e porta livre. Não reiniciar os processos 61270/61271 nem o principal em 8787 para verificar esta fatia. Inspecionar instrutor e operador separadamente, campos/erros/estado positivo em 320 e desktop, foco e console; salvar evidência e remover override de viewport.

Nesta Fase 2 não há arquivos de produção/verificadores novos, execução de testes ou servidor. Documentar resultados apenas na implementação, sem antecipar número de testes ou sucesso.

## Riscos e tratamento

| Risco | Tratamento |
|---|---|
| Readiness parecer botão de combate | Texto sobre entradas, flags de não execução e ausência de botão executar |
| Hipótese parecer saldo/atributo validado | Origem explícita e fonte oficial separada; não confiar em selo do cliente |
| Grupo reduzido ao primeiro integrante | Não suporte visível e nenhuma seleção automática de representante |
| Geometria local parecer trajetória do mapa | Referência didática e ausência de conversão lat/lon no módulo |
| Consulta positiva envelhecer | Hash/revisões, invalidação local e reconferência obrigatória futura |
| Falta de fonte virar valor zero | Separar indisponibilidade, ausência e zero explícito |
| Formulário voltar a ocupar todo o mapa | Seções progressivas, uma área ativa e verificação em viewport estreito |
| Novo módulo derrubar o julgamento | Carregamento recuperável, compatibilidade e regressões |
| Consulta alterar eventos/estoques/RNG | Provedores de leitura, nenhum loop/gerenciador e comparação de dados antes/depois |

## Gate de Fase 2

Revisar a divisão, captura de fontes, formato de hipóteses e experiência do instrutor. A skill Spec Driven Development exige validação de cada fase antes da seguinte. A aprovação deste plano habilita detalhar a lista da Fase 3; não aprova implementação, parâmetros reais, origem automática durável, migração ou ampliação do resolvedor para grupamentos.
