# 116 — Entrega: julgamento didático integrado ao mapa

**2026-11-17. Recorte 3 e JUD-01–14 concluídos.** Especificação 113, plano 114 e lista 115 aprovados por “sim”. Contratos em [SPEC-force-confrontation.md](../../SPEC-force-confrontation.md), [plano](../../tasks/force-confrontation/julgamento/plan.md) e [tarefas](../../tasks/force-confrontation/julgamento/todo.md). O marco parcial foi percorrido em navegador real, com dados sintéticos de teste. Não é implementação do confronto automático.

## Como testar

Prévia desta entrega: `http://localhost:61269/atlanticador/editor.html`. Login na raiz: 1 instrutor, 2 AZUL ou 3 VERMELHO; senha `somente-teste-local`. Pasta isolada `C:/Users/bozoc/AppData/Local/Temp/siscan-judgment-20261117-v1`. Esses dados/contas não são do principal. Para recriar/retomar o harness, usar os comandos do README do protótipo. Reiniciar a mesma pasta preserva estado/histórico, mas não recompõe grupos automaticamente.

Instrutor: **CPC → selecionar AZUL/VERMELHO → Preparar confronto → Abrir julgamento didático → escolher alterações e motivo → Conferir prévia → Registrar proposta → Confirmar efeitos → Confirmar aplicação**. Rejeitar não aplica efeitos. Editar após registro exige nova prévia e **Salvar revisão**; retomada/correção têm comandos próprios. Roteiro completo em [103](103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md).

## O que mudou

- `cpc_judgment.py`: base oficial canônica separada dos hashes de 98/108, prévia sem escrita, propostas/revisões, decisões, consulta/índice e replay. Origem congelada `siscan-cpc-didactic-origin-01`, construída no servidor. Publicador único continua `operational_state` de 112.
- Provedor de estado: leituras públicas autorizadas de proposta/índice/recibo e transformação de prévia compartilhada com aplicação. Autoridade, fonte e snapshot não vêm do cliente.
- Registro de grupos: escopo público de revisões. Escrita nova reserva SQL, protege grupos, reconfere/aplica e confirma commit antes de liberar o registro. Conexão externa já em transação é recusada. Não se afirma transação distribuída ou persistência dos grupos.
- `app.py`: rotas autenticadas/CSRF de contexto/prévia, registro, revisão, decisão, índice e consulta; módulo estático autenticado. Não migra por requisição.
- Painel no mapa existente: edição explícita de índice/perda, prévia, revisão final, rejeição, retomada e correção. Resposta perdida mantém comando/intenção para retry; falha de refresh após commit preserva recibo e indica vista pendente. Aceitar descarte de edição limpa o formulário/intenção local, impedindo confundir edição com proposta salva.
- Consulta do mapa: projeção mínima oficial por identidade/partido, índice conhecido, perda e origem/revisão temporal; tooltip/lista não apresentam proposta como estado oficial. Domínio não demonstrado não ganha condição naval. Planejamento, silhuetas e posições preservados.

Prévia e registro/revisão/rejeição não alteram o estado dos meios. Campo vazio não vira zero; omissão preserva e retirada explícita usa `null`. Perda é separada de índice e correção não apaga decisão. Mínimos/consumo de combustível e armamento continuam nos contratos existentes; não foram criadas barras logísticas presumidas ou índice de força.

## Evidência automatizada

**179 testes nomeados distintos passaram: 29 novos e 150 regressões**, contados uma vez por teste, não por repetição de execução:

| Verificador | Testes |
|---|---:|
| `check_operational_state.py` | 28 |
| `check_operational_state_storage.py` | 19 |
| `check_unit_groups.py` | 32 |
| `check_cpc_judgment.py` | 10 |
| `check_cpc_judgment_http.py` | 5 |
| `check_cpc_map.py` | 14 |
| `check_cpc_group_preparation.py` | 21 |
| `check_map_groups.py` | 6 |
| `check_map_groups_http.py` | 8 |
| `check_cpc_map_http.py` | 6 |
| `check_cpc_judgment.mjs` | 11 |
| `check_cpc_preparation.mjs` | 10 |
| `check_map_groups.mjs` | 9 |

Também passou o verificador assertivo `check_map_units.py`; sintaxe JS e `git diff --check` verificados. Ciclos red/green usados nos comportamentos novos e na correção do descarte. Nenhuma dependência instalada. Não houve benchmark de escala, auditoria física dos parâmetros Command ou execução de algoritmo automático.

## Evidência no navegador e recuperação

Instrutor selecionou/preparou o par, registrou avaliação AZUL 60%, cancelou a etapa final sem aplicar e depois confirmou explicitamente. Criou correção referenciada de 80%, revisou para 75% antes de confirmar; o AZUL terminou em 75%, revisão oficial 2. Proposta VERMELHO 20% foi rejeitada, mantendo estado não avaliado. Registradas também propostas pendentes para testar retomada; uma retomada pelo par atual foi posteriormente rejeitada.

Reload preservou propostas. Foi encerrado somente o processo do harness identificado pelo script/pasta e iniciado processo novo na mesma porta/base. Histórico/recibos permaneceram; grupos em memória desapareceram. Confirmação da proposta antiga ficou desabilitada, mantendo consulta/rejeição. Novos grupos foram criados manualmente pela interface, com novos IDs; a avaliação AZUL 75% continuou disponível. Retomada de proposta com grupos atuais restaurou explicitamente os dois marcadores do par conferido.

Operador 2, em sessão separada por host, viu somente o meio AZUL, seu tooltip com índice 75% e revisão 2, e nenhuma aba CPC. No instrutor, teclado Enter confirmou a ação final; cancelar saída preservou rascunho, e aceitar descarte limpou os campos antes da consulta de histórico. O diálogo nativo de descarte foi operado pela janela do aplicativo porque a automação DOM não o resolveu; não é evidência de falha de autorização ou aplicação.

Telas 1280×900 e 390×844 verificadas, com um mapa, uma área lateral e sem transbordamento horizontal no viewport estreito. Override removido; largura normal voltou a 446 pixels na janela usada. Sem auditoria completa de acessibilidade ou todos os tamanhos. Console sem erros na observação final; não se declara inspeção integral de tráfego/rede. Evidência local fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-julgamento-integrado-20261117.jpg`.

SQL final da base de teste: cinco propostas, quatro decisões e dois efeitos; um registro pendente antigo preservado. Duas posições originais em revisão 1; `map_plot_commands`, `engine_runs` e `engine_resource_states` vazios. `integrity_check=ok` e `foreign_key_check` sem resultados. Não confundir escritas legítimas de sessão/login da prévia com efeitos de combate.

Rastreabilidade: JMAP-01/09 por HTTP/papel/CSRF e observação do operador; 02/03/07 por base/preview/revisões/SQL; 04/05 por revisão final, rollback/replay, testes de disputa/refresh e ação real do instrutor; 06 por reload/processo novo/retomada; 08/11 por painel/mapa/tooltip/foco/viewport/descarte; 10 por schema ausente/fallback/harness; 12 por regressões e preservação dos planos/fontes. Respostas perdidas e refresh falho são testes controlados JS, não falhas de rede provocadas no navegador do usuário.

## Limites e continuidade

Código/documentação sincronizados por SHA-256 para a pasta SISCAN e publicados na branch existente. Principal 8787 e seu banco/processo não foram migrados/reiniciados. Originais/DB3K, mapas preparados e planos independentes preservados. Habilitar o principal continua procedimento próprio de backup consistente/janela/migração/verificação; instalar arquivos não atualiza um Python já em execução.

O fluxo parcial é didático, atualmente com elegibilidade de configuração aérea sintética. Não libera automaticamente todas as plataformas reais do catálogo nem calcula confronto entre grupamentos. A etapa 4 de 104 permanece: definir regras/entradas elegíveis e integrar produtor automático de proposta, sempre sujeito à decisão do instrutor. Persistência das próprias composições e expansão de domínios são recortes independentes, não resultados desta entrega.
