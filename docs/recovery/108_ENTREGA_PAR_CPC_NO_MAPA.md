# 108 — Entrega: par CPC no mapa

**2026-11-17. Recorte 2 concluído.** Escopo 104, especificação 105, plano 106 e tarefas 107 aprovados; a última lista recebeu “sim”. Implementação preserva 98/102 e o mapa ATLANTICADOR definido. Não executa confronto, consumo, relógio, julgamento ou efeitos oficiais.

## Uso e contratos

Instrutor participante abre **CPC**, seleciona um grupo AZUL e um VERMELHO e aciona **Preparar confronto**. Consulta integrantes/referências no painel ou marcador e usa **Enquadrar o par**. **Voltar ao planejamento** remove a consulta e recarrega a perspectiva autorizada. Passo a passo completo em [103](103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md).

- `GET /api/cpc/groups`: lista contextual, sem seleção automática; operador recusado antes da consulta adversária.
- `POST /api/cpc/preparations`: sessão/CSRF, contrato estrito e revisões explícitas; reutiliza o dossiê de 98. Mudanças observadas nas referências, grupos, adjudicação, exercício ou posições recusam o lote.
- `cpc_map.py`: projeção `siscan-cpc-map-preparation-01`, IDs unidade/asset e referências iniciais. Hash técnico de 98 preservado; hashes geográfico e da vista separados. Recurso atual ausente permanece `null`.
- `cpc-preparation.mjs`: seleção, erros e descarte de respostas atrasadas; camada de consulta integrada pelo adaptador existente. Ferramentas de edição ficam suspensas; a consulta não grava posições.
- Registro em memória e sem reserva futura. As fontes têm transações/locks próprios; revalidação observada não é atomicidade distribuída. Integrar novo consumidor exige revalidar novamente.

## Evidências

**73 testes nomeados passaram**, sem dupla soma: `check_cpc_map.py` 14; `check_cpc_map_http.py` 6; `check_cpc_preparation.mjs` 9; regressões `check_cpc_group_preparation.py` 21, `check_map_groups.py` 6, `check_map_groups_http.py` 8 e `check_map_groups.mjs` 9. Também passaram os verificadores assertivos `check_map_units.py` e `check_map_visuals.mjs`. `git diff --check` sem erros. Nenhuma dependência instalada.

No navegador isolado: seleção explícita dos dois grupos, preparação, dois marcadores no único mapa, consulta de integrante, enquadramento, limpeza ao trocar seleção e retorno ao planejamento. Teclado/foco da preparação conferidos e foco após resposta corrigido. Viewport 390×844 sem transbordamento horizontal; largura normal restaurada. Não se afirma auditoria completa de acessibilidade/rede ou ensaio de todos os tamanhos. Recusa a operador/sem participação/CSRF inválido comprovada por HTTP; revogações e mudanças durante captura por testes controlados, sem forçar mutações no exercício do usuário.

Após uso gráfico, a base descartável mantinha duas posições iniciais (-22,7/-43,1 e -22,7/-42,9), ambas revisão 1; `map_plot_commands`, `engine_runs` e `engine_resource_states` vazios. O fluxo não arquivou/revisou composições. Foto de evidência local: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-par-cpc-20261117.jpg` (fora do Git).

Rastreabilidade: CP-01/02/03/05/06/10/11 pelos testes de provedor/HTTP; CP-04 por manifesto/ausência de posição e observação gráfica; CP-07/08 por camada única, consulta/saída e SQL preservado; CP-09 por controlador, foco e viewport; CP-12 por regressões, carga opcional e comunicação explícita de indisponibilidade no código. Compatibilidade com processo antigo inspecionada no carregamento opcional, sem reiniciar o servidor principal para teste.

## Limites e continuidade

O provedor atual reconhece configuração aérea sintética controlada. Meios reais sem snapshot/domínio demonstrado continuam pendentes; a conferência não libera parâmetros técnicos Command nem inventa logística atual. Não há percentual de poder agregado ou resultado de combate produzido por esta preparação.

Próximo recorte conforme 104: estado/adjudicação durável, julgamento didático e confirmação/aplicação rastreável de efeitos pelo instrutor, com contrato próprio antes de implementação. Não reabrir gates desta entrega nem os planos independentes de catálogo.

Prévia isolada desta verificação: `http://localhost:60887/atlanticador/editor.html`, contas descartáveis do harness (1 instrutor; senha `somente-teste-local`). Porta depende do processo; para recriar executar `check_cpc_map_http.py --serve`, entrar na raiz da URL informada e abrir o editor. Não é a base principal. A instância principal em 8787 não foi reiniciada; copiar arquivos e publicar no Git não atualiza suas rotas em memória e um reinício descarta grupos temporários.

Entrega de arquivos: código/documentação sincronizados para a pasta SISCAN com comparação SHA-256; fontes originais, bancos, mapas preparados e planos antigos do catálogo preservados. Versionamento na branch `codex/initial-siscan`; conferir o histórico Git para os commits desta entrega.
