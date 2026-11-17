# Tarefas: unit-registry — grupamentos no mapa

**Data: 2026-11-16. Estado: especificação e plano aprovados por respostas distintas “siga”; Fase 3 aprovada por “siga”; Fase 4 em execução.** Referências: [especificação](../../../SPEC-unit-registry.md), [plano](plan.md), [101](../../../docs/recovery/101_TAREFAS_GRUPAMENTOS_NO_MAPA.md). Preservar os planos abertos do catálogo e os recortes concluídos 93/98.

Após aprovação desta lista, executar sequencialmente, com testes antes da implementação pertinente e commits por incremento verificado. Checkpoints A/B/C são verificações do contrato já aprovado; comunicar resultados e continuar dentro do escopo. Mudança material de contrato exige revisar a decisão afetada. Não instalar dependências, modificar originais, migrar bancos ou iniciar confronto temporal.

## Comandos

Partindo de `siscan-prototype`:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_map_groups.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_unit_groups.py
& $pythonCpc check_map_units.py
node check_map_groups.mjs
node check_map_visuals.mjs
```

Os novos verificadores ainda não existem. Não houve execução de testes de software nesta preparação documental. Verificar o runtime Node disponível antes de executar os comandos JS. Não usar descoberta vazia ou leitura do código como teste de interface. `git diff --check` é executado na raiz do repositório antes de registrar incrementos.

## GMAP-01 — Resolver identidade e elegibilidade autorizadas

- [x] Implementar e verificar o provedor do partido. Seis testes passaram, sem alteração dos dados SQL.
- **Aceite:** sessão/participação e partido autorizados antes da leitura; `unit_id`/`asset_id` pertencem ao mesmo contexto e adjudicação ativa; snapshot/configuração íntegros. Domínio da configuração sintética tem evidência explícita; nome/categoria/flag isolada não demonstram elegibilidade. Meio sem instância ou domínio válido permanece plotável, mas aparece pendente, sem criar dados ou revelar o adversário.
- **Verificar:** `check_map_groups.py` com SQLite isolado e fonte real do adaptador, incluindo vínculo inválido, fonte sintética falsamente alegada, adjudicação revogada e dados desconhecidos. Comparar dados SQL antes/depois. GM-02–04, GM-11–12.
- **Dependência:** aprovação desta lista.
- **Arquivos prováveis:** `siscan-prototype/map_groups.py`, `siscan-prototype/check_map_groups.py`, este checklist. Pequeno, três arquivos.

## GMAP-02 — Listar grupos pelo contrato público

- [x] Implementar e verificar consulta contextual do registro. Trinta e um testes do registro passaram, incluindo dois novos de lista/cópia/contexto.
- **Aceite:** `listar_grupamentos(contexto)` devolve versões atuais, inclusive arquivadas, em ordem determinística e como cópias; não atravessa exercício/partido. Consulta e edição do retorno não mudam registro/histórico; preservar criação, revisão, arquivo, recibos e exclusividade existentes.
- **Verificar:** `check_unit_groups.py` com casos novos de lista/contexto/cópia/arquivo; sem acesso privado pelo consumidor. GM-04, GM-07, GM-09 e preservação dos critérios UG da entrega 93.
- **Dependência:** GMAP-01 para a sequência de integração; o registro continua independente de SQLite/HTTP.
- **Arquivos prováveis:** `siscan-prototype/unit_groups.py`, `siscan-prototype/check_unit_groups.py`, este checklist. Pequeno, três arquivos.

## GMAP-03 — Integrar rotas e registro compartilhado ao servidor

- [x] Implementar e verificar criar/consultar/arquivar por HTTP. Sete testes de HTTP real passaram em loopback com banco temporário.
- **Aceite:** três rotas de 99, corpos/consulta/URL estritos, sessão/CSRF, exercício aberto na escrita e respostas 400/403/404/409 coerentes. Uma instância por servidor atende threads; reenvio/conflito preservam publicação única, e todas as respostas passam por projeção autorizada atual, inclusive recibos após revogação. Arquivo preserva unidades/posições e libera vínculos; reinício tem lista vazia e aviso de armazenamento em memória.
- **Verificar:** `check_map_groups_http.py`, base temporária com caminhos `DATA_DIR`/`DB_PATH` isolados e porta livre; sessões de instrutor/operadores; escrita sem CSRF, outro partido/exercício, conflito/reenvio, comandos concorrentes e vínculo revogado. Comparar dados SQL e confirmar que nenhuma rota cria meios ou consome recursos. GM-04–05, GM-07, GM-09, GM-11–12.
- **Dependências:** GMAP-01/02.
- **Arquivos prováveis:** `siscan-prototype/app.py`, `siscan-prototype/map_groups.py`, `siscan-prototype/check_map_groups_http.py`, este checklist. Médio, quatro arquivos.

### Checkpoint A — Backend da interface

- [x] Provedor/registro/HTTP passam com recusas e preservação de dados.
- [x] Respostas não vazam integrantes revogados ou partido não autorizado; recibo não substitui autorização atual.
- [x] A API diferencia vazio, pendência e erro; memória temporária é declarada. Resultados comunicados antes do gráfico.

## GMAP-04 — Acrescentar aba e fluxo de composição

- [ ] Implementar e verificar painel, formulário e arquivamento.
- **Aceite:** aba “Grupamentos” no painel existente, uma área ativa, seletor de partido coerente e aviso temporário persistente. Criar/consultar/confirmar arquivo usa API/sessão/CSRF; nomes como texto, foco e alternativa por lista/teclado. Carregamento/vazio/erro/pendência/arquivado distintos; comando só é reutilizado para a mesma intenção após falha de rede.
- **Verificar:** `check_map_groups.mjs` para estados, criação, conflito e reenvio com respostas controladas; verificar que nenhum payload inclui snapshots, aprovação ou `asset_id` alegado pelo cliente. Não anunciar validação visual antes de GMAP-06. GM-01, GM-03–05, GM-07, GM-09–10.
- **Dependência:** GMAP-03 e Checkpoint A verificado.
- **Arquivos prováveis:** `siscan-prototype/static/map-groups.mjs`, `static/atlantic-bridge.mjs`, `siscan-prototype/app.py` (servir módulo sob política autenticada), `check_map_groups.mjs`, este checklist. Médio, até cinco arquivos.

## GMAP-05 — Realçar membros sem alterar plotagem

- [ ] Implementar e verificar seleção e enquadramento seguros.
- **Aceite:** consulta do grupo realça somente marcadores já existentes; enquadramento exige ação/posição válidas; ausência de posição/vínculo não inventa marcador. Seleção de grupo é separada da seleção de plotagem; alternar para grupos cancela reposicionamento/área pendentes sem gravar coordenadas. Troca de partido limpa seleção e descarta GET/POST atrasados; redraw só reaplica realce de membros ainda autorizados.
- **Verificar:** `check_map_groups.mjs` com callbacks de marcador/câmera, respostas fora de ordem e troca de contexto durante escrita; `check_map_visuals.mjs` e `check_map_units.py` como regressões. Conferir que seleção/consulta não envia POST de plotagem. GM-01, GM-06, GM-08, GM-10–12.
- **Dependência:** GMAP-04.
- **Arquivos prováveis:** `siscan-prototype/static/map-groups.mjs`, `static/atlantic-bridge.mjs`, `check_map_groups.mjs`, este checklist. Médio, quatro arquivos.

### Checkpoint B — Fluxo gráfico verificável

- [ ] Testes JS/backend passam; seleção, escrita e respostas atrasadas mantêm contexto/identidade.
- [ ] Ferramentas e mapa originais preservados; sem marcadores duplicados ou comando de plotagem por consulta.
- [ ] Interface informa claramente elegibilidade limitada e perda no reinício; ainda não declarar inspeção visual concluída.

## GMAP-06 — Verificar no navegador real isolado

- [ ] Executar fluxo de ponta a ponta e registrar evidências.
- **Aceite:** criar → consultar/selecionar → enquadrar → arquivar funciona no mapa ATLANTICADOR definido em cópia de teste, sem painel sobreposto. Conferir foco/teclado, viewport estreita, camadas, reposicionamento e hover anteriores; consulta do operador não expõe outro partido. Nenhuma ação de teste é aplicada à base/posições do usuário.
- **Verificar:** servidor de teste em porta própria e `DATA_DIR`/`DB_PATH` temporários; mapa preparado em cópia, sem modificar ZIP/original. Usar ferramenta de navegador disponível sem instalar serviço. Conferir erros de console/rede pelos recursos disponíveis, registrar exatamente o que foi observado e qualquer limite. Se faltar mapa/ferramenta, não alegar visual completo; resolver a preparação autorizada ou registrar impedimento real.
- **Dependência:** GMAP-05 e Checkpoint B verificado.
- **Arquivos prováveis:** harness de `check_map_groups_http.py`, artefatos de evidência locais fora do Git e este checklist. Pequeno; correções funcionais retornam à tarefa afetada com teste de regressão.

### Checkpoint C — Aceite observado

- [ ] GM-01–GM-12 ligados a testes/evidências efetivos, sem confundir verificação JS com inspeção visual.
- [ ] Preservação da base/posições/recursos do usuário conferida; resultado comunicado.
- [ ] Nenhum confronto temporal, replay ou estado oficial aplicado; limitações não ocultadas.

## GMAP-07 — Documentar entrega e contratos

- [ ] Revisar o código e consolidar evidências finais.
- **Aceite:** especificação/plano/lista distinguem implementado/pendente e gates satisfeitos; README/relatório descrevem como acessar, aviso temporário e categorias elegíveis. Contagens são as efetivamente executadas, sem dupla soma ou testes ignorados; exemplos não representam composição real otimizada.
- **Verificar:** comandos pertinentes acima e diff; ampliar regressões somente quando houver motivo concreto. Conferir links e registro da inspeção visual. Não repetir software por edição documental posterior.
- **Dependências:** GMAP-06 e Checkpoint C verificado.
- **Arquivos prováveis:** `siscan-prototype/README.md`, relatório numerado livre em `docs/recovery/`, `SPEC-unit-registry.md`, `plan.md`, este checklist. Médio, até cinco arquivos.

## GMAP-08 — Atualizar controles

- [ ] Consolidar índice, riscos, continuidade e mapa de capacidades.
- **Aceite:** controles refletem a entrega comprovada e limites de memória/elegibilidade, distinguindo composição gráfica de confronto CPC. Não reabrir aprovações das entregas 93/98 nem modificar planos antigos do catálogo.
- **Verificar:** links locais, hashes de preservação dos planos antigos e `git diff --check`.
- **Dependência:** GMAP-07.
- **Arquivos prováveis:** `docs/recovery/00_LEIA-ME_RECUPERACAO.md`, `09_PENDENCIAS_E_RISCOS.md`, `10_PLANO_DE_CONTINUIDADE.md`, `CAPABILITY_MAP.md`, este checklist. Médio, até cinco arquivos.

## GMAP-09 — Sincronizar e versionar

- [ ] Entregar arquivos autorizados na pasta SISCAN e no GitHub.
- **Aceite:** origem/destino conferidos por SHA-256; somente código/docs do recorte versionados, sem originais proprietários, credenciais, bases ou resultados locais de teste. Estado Git e envio verificados; não reiniciar/substituir servidor em uso sem preservar seu estado temporário e informar o impacto.
- **Verificar:** hashes, diff preparado, commits por incremento e resultado do envio. Publicar código não significa atualizar processo já em execução; registrar separadamente a disponibilidade da interface no servidor ativo e não alegar que a nova aba está visível sem observá-la.
- **Dependência:** GMAP-08.
- **Arquivos prováveis:** este checklist e relatório de entrega, mais cópia dos arquivos já produzidos; sem nova alteração funcional.

## Gate

Lista de Fase 3 aprovada pelo responsável por “siga”; implementação em execução. Após aprovação, implementar GMAP-01–09 sem novas confirmações rotineiras de cada tarefa/checkpoint. A autorização desta lista não muda o requisito de usar o mapa definido nem aprova migração de instâncias reais, persistência, instalação de dependências ou execução de combate.
