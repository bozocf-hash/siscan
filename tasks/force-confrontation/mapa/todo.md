# Tarefas: force-confrontation — par CPC no mapa

**Data: 2026-11-17. Estado: escopo, especificação e plano aprovados; Fase 3 aprovada por “sim”; Fase 4 em execução.** O plano de 106 recebeu “sim”. Referências: [especificação](../../../SPEC-force-confrontation.md), [plano](plan.md), [107](../../../docs/recovery/107_TAREFAS_PAR_CPC_NO_MAPA.md). Preservar os planos anteriores e as entregas 98/102.

Após aprovação desta lista, executar sequencialmente com testes de comportamento antes da implementação correspondente e commits por incremento verificado. Checkpoints são verificações técnicas do contrato aprovado; comunicar resultados e continuar sem confirmações rotineiras. Mudança material exige rever a decisão afetada. Não instalar dependências, modificar originais, migrar bancos ou executar confronto.

## Comandos futuros

Na pasta `prototype` de entrega (`siscan-prototype` no repositório):

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_cpc_map.py
& $pythonCpc check_cpc_map_http.py
& $pythonCpc check_cpc_group_preparation.py
& $pythonCpc check_map_groups.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_map_units.py
node check_cpc_preparation.mjs
node check_map_groups.mjs
node check_map_visuals.mjs
```

Verificadores novos ainda não existem e nenhum teste foi executado nesta fase documental. Confirmar o runtime Node disponível antes de executá-los. Usar `git diff --check` na raiz antes de cada registro; não aceitar descoberta vazia ou leitura do código como evidência visual.

## CPMAP-01 — Listar e preparar o par autorizado

- [x] Implementar e verificar o fluxo válido e a fronteira de autorização. Sete testes focados passaram; sem escrita SQL ou alteração do registro.
- **Aceite:** instrutor participante é autorizado antes da leitura dos dois partidos; lista distingue grupos/revisões/impedimentos sem seleção automática. Preparação exige AZUL/VERMELHO explícitos e exercício aberto, usa o dossiê 98 e vincula membros/posições pelo provedor atual, preservando ausências e sem publicar efeitos.
- **Verificar:** `check_cpc_map.py` com banco de teste e registro real, provedor instrumentado que detecta leitura antes da autorização, casos de operador/não participante, fechado, seleção inválida, grupo arquivado/revisão/snapshot/adjudicação incompatíveis e vínculo ausente. Comparar entradas/registro/SQL antes/depois. CP-01–04, CP-10–11.
- **Dependência:** aprovação desta lista.
- **Arquivos prováveis:** `siscan-prototype/cpc_map.py`, `siscan-prototype/check_cpc_map.py`, este checklist. Pequeno, três arquivos.

## CPMAP-02 — Conferir a captura e separar os manifestos

- [x] Implementar e verificar revalidação observada, cópias e hashes. Quatorze testes focados passaram, incluindo mudanças provocadas durante a captura e manifesto geográfico separado.
- **Aceite:** dossiê técnico mantém o contrato/hash de 98; manifesto geográfico e hash de vista são distintos, canônicos e restritos ao par. Mudança observada de grupo/contexto/snapshot/adjudicação/posição recusa o lote sem resposta parcial; retorno e entradas independentes. Não alegar reserva futura ou transação distribuída.
- **Verificar:** `check_cpc_map.py` com alterações controladas entre chamadas, sem sleeps nem acesso privado ao registro. Mesmas entradas/ordens produzem os mesmos hashes; posição nova altera geográfico/vista e preserva o técnico; unidade não participante não muda manifestos. Campo desconhecido/posição ausente não vira zero/100%/coordenada. CP-03–06, CP-10–11.
- **Dependência:** CPMAP-01.
- **Arquivos prováveis:** os dois módulos acima e este checklist. Pequeno, três arquivos.

## CPMAP-03 — Integrar as rotas de preparação

- [ ] Implementar e verificar HTTP real com sessão/CSRF.
- **Aceite:** GET `/api/cpc/groups` e POST `/api/cpc/preparations` aplicam contratos estritos, contexto da sessão, códigos de falha e registro único do servidor. Não aceitam autorizador/snapshot/posição do cliente nem criam recibo fictício. Respostas não contêm inventários completos ou dados de outro contexto.
- **Verificar:** `check_cpc_map_http.py` com base, cookie exclusivo e porta isolados, reutilizando o harness existente sem tocar a base principal. Testar sessão/CSRF, papéis, fechado, formato/conflito/ausência/integridade e preservação SQL/registro. Regressão de `check_cpc_group_preparation.py`, `check_map_groups.py` e `check_map_groups_http.py` quando afetadas. CP-01–06, CP-11–12.
- **Dependências:** CPMAP-01/02.
- **Arquivos prováveis:** `siscan-prototype/app.py`, `siscan-prototype/cpc_map.py`, `siscan-prototype/check_cpc_map_http.py`, este checklist. Médio, quatro arquivos.

### Checkpoint A — Preparação pelo backend

- [ ] Provedor/HTTP passam, com autorização antes da leitura adversária e ausência de resposta parcial.
- [ ] Hash técnico, manifesto geográfico e vista têm significado separado; mudanças observadas recusadas.
- [ ] Posições, grupos, recursos, execuções/relógio e estado oficial preservados; resultado comunicado antes do gráfico.

## CPMAP-04 — Selecionar e conferir pelo painel

- [ ] Implementar e verificar seletores, preparação e invalidação da vista.
- **Aceite:** área CPC no painel existente somente para instrutor, com seletores AZUL/VERMELHO e impedimentos legíveis. Preparar exibe conferência/situação inicial, sem controles funcionais de julgamento/confirmação. Carga/vazio/erro/conflito distintos; trocar seleção/contexto/sair invalida a preparação e descarta respostas antigas.
- **Verificar:** `check_cpc_preparation.mjs` com respostas controladas de GET/POST fora de ordem, saída durante requisição, cenário/exercício divergente e erro/403. Conteúdo renderizado como texto; nenhuma requisição de plotagem, execução ou efeitos. Testar referências e desconhecidos sem apresentar snapshot inicial como saldo atual. CP-02, CP-09–12.
- **Dependência:** CPMAP-03 e Checkpoint A verificado.
- **Arquivos prováveis:** `siscan-prototype/static/cpc-preparation.mjs`, `static/atlantic-bridge.mjs`, `siscan-prototype/app.py` (servir módulo autenticado), `check_cpc_preparation.mjs`, este checklist. Médio, até cinco arquivos.

## CPMAP-05 — Mostrar o par no mesmo mapa

- [ ] Implementar e verificar camada de consulta e retorno ao planejamento.
- **Aceite:** os integrantes dos dois partidos aparecem no mapa definido, com simbologia existente e sem duplicidade de asset. Cancelar movimentação/área pendentes ao entrar e suspender camada de planejamento; consulta de marcador/lista não move ou edita. Sair remove a consulta e recarrega a perspectiva autorizada anterior, sem restaurar dados revogados.
- **Verificar:** `check_cpc_preparation.mjs` para callbacks de camada/câmera, seleção e saída; regressões de `check_map_groups.mjs`, `check_map_visuals.mjs` e `check_map_units.py` quando pertinentes. Sem posição só na lista; enquadramento explícito considera painel. Módulo/rota indisponível no processo antigo preserva as ferramentas existentes, sem falso sucesso de preparação. CP-04, CP-07–09, CP-11–12.
- **Dependência:** CPMAP-04.
- **Arquivos prováveis:** `siscan-prototype/static/atlantic-bridge.mjs`, `static/cpc-preparation.mjs`, `check_cpc_preparation.mjs`, este checklist. Médio, quatro arquivos.

## CPMAP-06 — Observar o fluxo no navegador isolado

- [ ] Verificar a interface real e registrar evidências.
- **Aceite:** selecionar ambos → preparar → conferir integrantes → enquadrar → sair funciona no mesmo mapa, sem painéis sobrepostos, marcadores duplicados ou gravação de posição. Conferir foco/teclado e tela estreita, sem deixar largura de teste aplicada; operador não tem acesso ao par adversário.
- **Verificar:** cópia do mapa, base/cookie/porta de teste; não usar grupos/meios do usuário. Instrumentar/comparar SQL e registro antes/depois, incluindo zero comandos de plotagem e execução. Conferir sessão/revogação/retorno ao planejamento e erros de console/rede pelos recursos disponíveis, registrando limites reais. Não instalar serviço de navegador ou declarar inspeção integral por teste JS.
- **Dependência:** CPMAP-05.
- **Arquivos prováveis:** harness de `check_cpc_map_http.py`, evidências locais fora do Git e este checklist. Pequeno; correção funcional retorna à tarefa afetada com verificação pertinente.

### Checkpoint B — Par conferido no mapa

- [ ] CP-01–CP-12 rastreados a testes/evidências reais; contagens sem dupla soma.
- [ ] Vista simultânea, consulta, saída, teclado/tela estreita e recusa ao operador observadas; dados do usuário preservados.
- [ ] Nenhum combate, consumo, relógio ou efeito oficial executado; preparação não é anunciada como fluxo de confronto completo.

## CPMAP-07 — Documentar o recorte entregue

- [ ] Revisar código, contratos e evidências finais.
- **Aceite:** README/relatório explicam uso, origem dos dados e limites de temporalidade/memória; especificação/plano/lista refletem implementação comprovada, com gates satisfeitos. Atualizar o roteiro do instrutor para distinguir nova conferência do julgamento/confirmação ainda pendentes, sem inventar botões.
- **Verificar:** comandos pertinentes acima, análise de diff e links. Registrar testes/inspeções realmente realizados e limitações; não repetir baterias após edição meramente documental. Dividir esta manutenção em subpassos documentais se ultrapassar cerca de cinco arquivos por alteração.
- **Dependências:** CPMAP-06 e Checkpoint B verificado.
- **Arquivos prováveis:** primeiro subpasso `siscan-prototype/README.md`, relatório numerado livre em `docs/recovery/`, `103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md`, este checklist; segundo subpasso `SPEC-force-confrontation.md`, `plan.md`, este checklist. Cada subpasso até quatro arquivos, sem mudança funcional.

## CPMAP-08 — Consolidar controles

- [ ] Atualizar índice, riscos, continuidade e mapa de capacidades.
- **Aceite:** controles distinguem seleção/conferência entregue de adjudicação/estado durável futuros. Preservar planos anteriores e não reabrir os gates das entregas anteriores ou de 104–106.
- **Verificar:** links locais, hashes dos planos antigos e `git diff --check`.
- **Dependência:** CPMAP-07.
- **Arquivos prováveis:** `docs/recovery/00_LEIA-ME_RECUPERACAO.md`, `09_PENDENCIAS_E_RISCOS.md`, `10_PLANO_DE_CONTINUIDADE.md`, `CAPABILITY_MAP.md`, este checklist. Médio, até cinco arquivos.

## CPMAP-09 — Sincronizar e versionar

- [ ] Entregar arquivos autorizados na pasta SISCAN e no GitHub.
- **Aceite:** código/docs sincronizados por SHA-256, sem sobrescrever alterações externas ou incluir fontes proprietárias, credenciais/bases/artefatos de teste. Situação Git e envio verificados. Não reiniciar processo em uso ou descartar grupos temporários para testar/entregar.
- **Verificar:** hashes/diff/commits e resultado do envio. Publicação e disponibilidade no servidor ativo reportadas separadamente; não alegar aba CPC disponível no principal sem observar atualização própria. Prévia isolada deve ser identificada como tal.
- **Dependência:** CPMAP-08.
- **Arquivos prováveis:** este checklist e relatório de entrega, mais cópia dos arquivos produzidos; sem nova alteração funcional.

## Gate

Fase 3 aprovada por “sim”; implementação em execução. Após aprovada, executar CPMAP-01–09 sem novas confirmações rotineiras de tarefas/checkpoints. Persistência/DDL, julgamento/decisão/efeitos e modo automático continuam fora deste recorte; não alterar a ordem de 104 ou o requisito de usar o mapa definido.
