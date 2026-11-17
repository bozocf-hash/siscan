# 102 — Entrega dos grupamentos no mapa definido

**Elaboração: 2026-11-16; fechamento: 2026-11-17. Estado: Recorte 2 de unit-registry implementado e verificado.** Especificação, plano e tarefas tiveram aprovações distintas; GMAP-01–09 aprovadas por “siga”. Interface usa o mesmo mapa ATLANTICADOR preparado anteriormente, sem modificar ZIP/original. O [roteiro do instrutor](103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md) explica o que já funciona e o confronto ainda pendente de integração.

## Uso e escopo real

Abrir o mapa com sessão do exercício. No painel lateral, a aba visual “Grupos” tem nome acessível “Grupamentos”. O instrutor escolhe AZUL/VERMELHO; operador permanece no próprio partido. Informar designação/domínio/integrantes elegíveis e criar; selecionar grupo realça marcadores existentes. Enquadrar altera somente câmera. Integrantes sem posição não geram coordenada/marcador fictício.

Arquivar exige revisão esperada e confirmação no próprio painel, com opção de cancelar. Libera vínculos, preserva histórico do processo e não apaga meios/posições. Não há revisão gráfica de composição; recompor exige arquivar/criar. Campos MPNL não foram renomeados ou inferidos.

**Registro temporário:** grupos/histórico se perdem ao reiniciar. A interface mostra aviso persistente. Não há migração/DDL ou persistência de composições. O provedor só reconhece o contrato aéreo sintético efetivamente criado por `engine_units.prepare_units`; outros meios sem instância/snapshot/domínio demonstrado aparecem pendentes e continuam plotáveis nas ferramentas existentes. Não representa integração de todas as plataformas reais ou validade física de combate.

Não existe botão de combate: a tela compõe/consulta/arquiva. Dossiê de dois partidos em 98 é biblioteca de backend; seleção de par, execução de grupamentos, replay, julgamento didático e publicação oficial de efeitos ainda precisam de integração própria. O resultado sempre depende do instrutor, conforme 80/81.

## Código e fronteiras

- `map_groups.py`: vista SQL consistente por partido, vínculo explícito unit_id/asset_id, elegibilidade por configuração controlada e projeção atual de membros; nenhuma escrita de meio/posição/recurso.
- `unit_groups.py`: nova consulta pública `listar_grupamentos`, contextual, ordenada e retornando cópias; demais operações preservadas.
- `app.py`: `SiscanServer` mantém registro único por processo compartilhado pelas threads. GET `/api/map-unit-groups?team=...`, POST `/api/map-unit-groups` e POST `/api/map-unit-groups/{id}/archive`, com sessão/participação/CSRF e exercício aberto na escrita.
- `static/map-groups.mjs`: painel/controlador de consulta, criação/arquivo, estados e descarte de respostas atrasadas; texto seguro, foco/teclado e confirmação sem caixa nativa.
- `static/atlantic-bridge.mjs`: aba no painel original, seletor comum de partido, realce separado da seleção de plotagem e câmera que considera o painel; sem outro mapa ou marcador duplicado.

Respostas de comandos, inclusive recibos históricos, são projetadas com a visibilidade atual. Integrante revogado não tem nome, posição, ID/snapshot técnico expostos ao operador; a composição indica quantidade indisponível e pendência. Hash/recibo não autoriza disponibilidade futura. Consulta a inventário e escrita em memória não são transação distribuída ou reserva de recursos SQL.

## Verificação executada

Passaram **54 testes nomeados**: 6 do provedor, 31 do registro (29 anteriores + 2 novos), 8 HTTP e 9 JavaScript. Também passaram os verificadores assertivos existentes de mapa e silhuetas, a análise sintática do adaptador e `git diff --check`. Não somar scripts assertivos como contagens presumidas de casos. Não foi repetida a bateria CPC temporal, que não foi alterada.

HTTP real em banco temporário/porta livre, com caminhos isolados e cookie exclusivo por instância: sessão/CSRF, outro partido, validação, fechado, reenvio/intenção, comandos concorrentes, arquivamento/revisão, projeção após revogação e reinício do registro. Operações de grupos preservaram os dados SQL comparados antes/depois.

Inspeção por navegador real no mapa preparado em cópia: criação, seleção, realce de um único marcador, enquadramento, arquivo com cancelar/confirmar, consulta de meio, alternância de abas/partido e operador vermelho com seletor bloqueado. Sem conteúdo de grupo azul na consulta vermelha. Telas de 1280 e 390 px conferidas, sem rolagem horizontal ou áreas laterais sobrepostas. Aviso permanece visível ao rolar, rótulos de abas curtos e foco de teclado preservado. Console observado sem erros pertinentes ao fluxo; não é auditoria de todos os recursos externos de mapa.

Problemas encontrados e corrigidos: foco perdido ao redesenhar seleção; rótulos longos em tela estreita; bloqueio da caixa nativa de confirmação, substituída por confirmação no painel; propagação do clique de reposicionamento. A primeira base visual registrou uma plotagem durante a checagem dessa interação. Após corrigir a propagação, outra base visual nova demonstrou cancelamento com ambas as posições iniciais intactas e **zero comandos de plotagem**. Não foi restaurado ou sobrescrito o estado da prévia usada pelo responsável.

| Critérios | Evidência principal |
|---|---|
| GM-01, GM-06, GM-10 | Navegador real, abas/ferramentas preservadas, marcador único/realce, telas ampla/estreita e teclado |
| GM-02–03 | Provedor com vínculo explícito, snapshot/hash e origem controlada; homônimo sem instância continua pendente |
| GM-04, GM-08 | HTTP/JS: autorização, revogação/recibo, resposta fora de ordem; operador restringido e troca de partido no navegador |
| GM-05, GM-07 | HTTP real: reenvio, intenção conflitante, disputa concorrente e arquivo com revisão esperada/liberação |
| GM-09 | Aviso em tela, vazio/erro distintos; registro por servidor e sem reconstrução automática |
| GM-11–12 | Comparação SQL no HTTP e nova base visual após correção; zero execução/consumo ou aplicação oficial |

Comandos na pasta `prototype` de entrega:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_map_groups.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_unit_groups.py
& $pythonCpc check_map_units.py
node check_map_groups.mjs
node check_map_visuals.mjs
```

Conexões de loopback dos testes HTTP exigiram execução fora do bloqueio de rede do sandbox; o teste continuou usando somente a base temporária. Harness `check_map_groups_http.py --serve` abre prévia isolada com cópia do mapa e dados sintéticos; não usa `app.main` sobre a base principal. A senha embutida no harness pertence exclusivamente às contas descartáveis de teste, não a contas reais.

## Entrega e disponibilidade

Checkpoints de código: `8d92cda` (provedor/lista), `3e2151a` (HTTP) e `183eddb` (painel/realce). Código/docs sincronizados com `C:\Users\bozoc\Documents\siscan`, conferidos por SHA-256 e enviados na branch `codex/initial-siscan`. Artefatos locais, bases e cópias do mapa não entram no Git.

Prévia desta sessão: `http://localhost:53197/atlanticador/editor.html`, em processo e dados temporários separados. Foi mantida para consulta. O servidor principal em 8787 **não foi reiniciado**: copiar arquivos/publicar commits não atualiza seu código Python já carregado. Recarregar uma página atualiza módulos estáticos, mas não cria as novas rotas num processo antigo. Não alegar interface disponível no principal sem atualização/verificação próprias. A importação do painel de grupos é opcional: se um processo antigo ainda não serve o módulo, a aba fica desabilitada com indicação de atualização, preservando as ferramentas anteriores. Esse fallback foi conferido no navegador com módulo indisponível simulado; não aprova o restante das rotas de um processo antigo.

Evidência de imagem: `C:\Users\bozoc\.codex\visualizations\2026\11\07\01a1b83c-fb2b-7343-90c8-6eecfff70486\siscan-grupamentos-20261116.jpg`, de ambiente sintético. Overrides de largura usados na inspeção foram removidos; após relato do responsável, a prévia foi conferida com 1242 px de largura. A largura real do painel da aplicação hospedeira pode ser diferente do viewport de teste.

Planos antigos do catálogo, bancos/originais e base do exercício principal preservados. Documentos 99–101 são registros históricos das fases; gates deste recorte estão satisfeitos. Continuidade: seguir o roteiro 103 para especificar a seleção do par e a conferência inicial, antes de ligar execução/adjudicação ao mapa. Não confundir composição entregue com confronto completo.
