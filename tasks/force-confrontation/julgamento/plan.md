# Plano técnico: julgamento didático e efeitos no mapa

**2026-11-17. Recorte 3 da especificação aprovado por “sim”; Fase 2 proposta para revisão.** O pedido posterior “seguios entao” mantém a continuidade. Base: [SPEC-force-confrontation.md](../../../SPEC-force-confrontation.md), Recorte 3, [113](../../../docs/recovery/113_ESPECIFICACAO_JULGAMENTO_DIDATICO_NO_MAPA.md), ordem de 104 e publicador de [112](../../../docs/recovery/112_ENTREGA_ESTADO_E_ADJUDICACAO_DURAVEL.md). Preservar todos os planos anteriores. Nenhum código, teste ou migração executado nesta fase.

## Marco de entrega

Versão parcial verificável pelo instrutor no mesmo mapa: selecionar AZUL/VERMELHO → abrir julgamento → conferir prévia → registrar/revisar → confirmar/rejeitar → consultar estado e histórico. Reload e processo novo preservam propostas/decisões; perder grupos em memória não apaga o resultado. Sem confronto automático, consumo ou simulação de trajetórias; automático permanece etapa 4 de 104.

O marco não será declarado concluído apenas por testes de backend. Exige percurso real no navegador isolado, incluindo rejeição sem efeitos, confirmação única e projeção oficial no hover/lista. O principal em 8787 não será reiniciado/migrado automaticamente.

## Dependências e fronteiras

```text
Leituras públicas de operational_state + coordenação pública de grupos
                              ↓
Base CPC com estado oficial e prévia sem escrita
                              ↓
Adaptador de proposta/revisão/decisão e retomada durável
                              ↓
Rotas autenticadas/CSRF + harness migrado isoladamente
                              ↓
Painel de julgamento + projeção oficial no mapa existente
                              ↓
Percurso real / recuperação / documentação / entrega
```

Reutilizar `operational_state` como publicador único. Adaptador `cpc_judgment.py` não importa helpers privados nem reimplementa cálculo de estado/perda. Novas leituras públicas ficam no provedor proprietário dos dados. O registro de grupos continua em memória, no mesmo processo, sem novas tabelas. Sem dependências externas ou subagentes.

## Leituras públicas e replay

Acrescentar a `operational_state.py` operações públicas de consulta de proposta, índice paginado e recibo para instrutor participante. Validar exercício, autoria/referências/integridade e projeção apropriada antes do retorno; não usar `_proposal`, que recusa propostas decididas, como atalho para consulta histórica. Propostas/revisões/decisão/recibo precisam ser consultáveis mesmo sem grupo em memória. Índice tem limite/cursor estritos e não devolve snapshots completos; origem identifica quais registros pertencem ao CPC gráfico.

Recibo público permite ao adaptador reconhecer comando já concluído antes de exigir grupo/base ainda disponíveis. Sempre validar autorização atual, operação, formato e intenção exata. A origem congelada de registro/revisão guarda hash canônico do pedido HTTP normalizado, além da base; replay confere esse hash contra o pedido recebido e usa recibo persistido. Decisão usa diretamente os campos estáveis do comando do publicador: ID da proposta, revisão/hash, ação e motivo. Comando novo segue toda a revalidação; comando reutilizado com outro conteúdo recusa.

Não expor recibo/proposta privada ao operador. Campo `origin` enviado pelo cliente nunca será aceito como autorização/origem comprovada; o adaptador constrói `siscan-cpc-didactic-origin-01` no servidor. Read/replay não migram schema nem recriam registros ou grupos perdidos.

## Coordenação de grupos e SQL

Adicionar API pública de escopo protegido ao `RegistroGrupamentos`, por exemplo `conferir_revisoes(referencias)`, que valida contexto, grupos ativos e revisões e mantém o lock do registro até sair do escopo. Código de identidade/registro não conhece SQLite. Leitura de grupo reentrante permanece permitida; o adaptador não invoca comandos de mutação de grupo dentro do escopo. Não acessar `_lock`/`_state` do lado consumidor.

Para novas escritas CPC, exigir conexão sem transação externa e ordenar **reserva de escrita SQL primeiro → escopo público do registro → conferência/aplicação → commit SQL ainda dentro do escopo → liberar registro**. Usar `BEGIN IMMEDIATE` no adaptador e rollback integral por exceção; o publicador opera como savepoint interno, sem decidir o commit externo. Rejeitar chamada com transação externa aberta, em vez de retornar confirmação não durável. Contexto/autorização são conferidos antes de fontes sensíveis e repetidos dentro do lote.

O wrapper de conexão do handler não inicia escrita antes dessa chamada. Inspecionar/testar todos os caminhos de mutação de grupos: atualmente a ponte lê SQL antes/depois e os métodos do registro mantêm lock apenas durante mutação em memória. Nenhum caminho poderá manter o lock do registro e esperar por reserva SQL de outro escritor. Adicionar prova de disputa com sincronização explícita e tempo limite, sem sleeps ou teste dependente de sorte.

Se grupo mudou antes da seção protegida, recusar a base. Se mudança concorre enquanto a confirmação já mantém o escopo, ela só pode ocorrer depois do commit. Falha no commit desfaz SQL e não muda grupos. Não alegar atomicidade distribuída, persistência de grupos ou garantia entre processos independentes; este contrato é do registro único da instância. Replay de recibo aplicado não adquire escopo de grupo desnecessariamente.

## Base, prévia e proposta

`cpc_judgment.context` reutiliza `cpc_map.prepare`, acrescenta estados oficiais/revisões obtidos por API pública e calcula `basis_sha256` canônico. Preservar os contratos/hashes de 98/108. Base inclui exercício/cenário, par/revisões/composições, referências técnicas, posições de planejamento e estado dos integrantes; sem horário aleatório ou substituição de desconhecido por zero. Retorno inclui avisos de domínio/elegibilidade e recursos não avaliados.

`preview` aceita seleção, hashes esperados, motivo e alterações de integrantes do par. Recusa unidade externa/duplicada/campos inesperados. Retorna antes/depois e pendências sem INSERT ou recibo. A transformação de índice/perda deve reutilizar uma função pública pequena do provedor, extraída da preparação dos efeitos existente, para que a prévia e a confirmação não divirjam. Não chamar confirmação real dentro de transação para depois desfazer como técnica de prévia.

Registrar/revisar recalcula fontes sob coordenação, compara a base esperada e chama o publicador com snapshot/configuração/revisões obtidos pelo servidor. Congela origem suficiente ao histórico; unidade omitida não recebe efeito. Revisão substitui conteúdo completo da proposta e invalida aceite anterior. Confirmação reconfere origem/base e aplica exatamente a revisão aceita; rejeição conserva as regras de 112 sem exigir grupo disponível. Correção referencia decisão do estado atual e passa pelo mesmo fluxo de nova proposta, sem desfazer histórico.

Depois de mudança externa da base, avisar e exigir nova conferência explícita; não rebasear silenciosamente intenção já aceita. Estado desconhecido, remoção da avaliação por `null`, preservação por omissão e perda explícita seguem 112. Não calcular percentual de força ou suprir sensores/armamentos de combate.

## HTTP e projeção oficial

Implementar as rotas propostas em 113: contexto/prévia, registro, revisão, decisão, índice e consulta individual de julgamento. `app.py` autoriza sessão/CSRF e delega, com validação estrita de caminho/query/corpo, limite de payload e códigos 401/403/400/404/409/503. Não criar autorizador informado pelo cliente nem chamar HTTP do próprio serviço para buscar fontes internas.

Consulta de meios existente ganha projeção mínima de estado confirmado para unidades com identidade demonstrada, consumindo API pública do provedor. Distinguir `not_evaluated`, `storage_not_enabled` e fonte/integridade indisponível; armazenamento ausente não é prontidão. Não importar mapa no provedor de estado nem criar ciclo. Unidade sem instância continua plotável conforme regra anterior, com ausência explícita de estado oficial. Operador só recebe o próprio partido e não recebe proposta/motivo privado.

Adicionar módulo estático autenticado de julgamento com carga opcional, como no adaptador anterior. Processo antigo/schema não habilitado mostra indisponibilidade e preserva planejamento/preparação de 108. Não executar migração durante GET/POST; código sincronizado não equivale a rotas novas carregadas pelo processo já em uso.

## Interface no painel existente

Controlador JS próprio, proposto `static/cpc-judgment.mjs`, instalado pelo módulo CPC existente. Estados explícitos: contexto em carga, edição local, prévia conferida, proposta registrada, revisão não salva, revisão final de aplicação, decisão confirmada/rejeitada e conflito/erro. Manter UUID por intenção para retry; mudar intenção gera outro comando. Não salvar ajustes implicitamente ao confirmar.

Uma única área lateral. Formulário por integrante com identificação de cadastro, estado/revisão oficial, alteração de índice e perda; ação separada para retirar avaliação e opção de preservar. Campo vazio não vira zero. Prévia compara antes/depois e destaca que é proposta; motivo obrigatório. Botões do contrato: Abrir julgamento, Conferir prévia, Registrar proposta/Salvar revisão, Confirmar efeitos/Confirmar aplicação, Rejeitar, Retomar julgamento e Nova proposta de correção, habilitados conforme estado real.

Avisar antes de abandonar edição local não salva. Sair/trocar seleção invalida respostas pendentes e a prévia, sem apagar proposta persistida. Retomada mostra origem congelada e disponibilidade atual distintas; falta de grupos não elimina histórico e bloqueia nova confirmação. Correção cria nova intenção referenciada, preservando decisão anterior.

Após confirmação, manter recibo durável e atualizar estado oficial no par e, ao sair, no planejamento. Falha no refresh mostra aplicação confirmada/vista pendente, sem alegar rollback ou gerar outro comando. Hover/lista usam mesma projeção oficial, com texto/valor/cor e origem temporal, sem pintar a proposta como já aplicada. Preservar os bloqueios de edição de 108 e não modificar as silhuetas ou criar outro mapa.

## Prévia isolada e recuperação

Harness proposto `check_cpc_judgment_http.py --serve --data-dir CAMINHO_DE_TESTE`, com pasta descartável explicitamente escolhida fora do Git e porta/cookie próprios. Primeiro uso prepara dados sintéticos e migra seu SQLite pela função explícita de 112; uso posterior abre a mesma base sem reseed/apagar histórico. Copiar somente o mapa já preparado para a pasta de teste. Não reconstruir grupos automaticamente após reinício para fingir que ainda são os mesmos.

O teste de navegador percorre confirmação/rejeição/correção e reload. Para recuperação de processo, encerrar somente o servidor de teste identificado, reiniciar com a mesma pasta e conferir histórico/recibo sem grupos em memória; proposta pendente fica indisponível para confirmação até recomposição/conferência válida. Não parar servidor principal, preview antigo ou processo sem comprovação de identidade. Restaurar viewport normal após teste estreito.

Testes sem navegador usam SQLite temporário, HTTP em loopback e controlador JS com respostas controladas. Entrega não inicia migração principal ou instala dependências. Implantação no principal continua procedimento próprio com backup verificado, janela sem escritores e verificação; não descartar grupos atuais para habilitar o novo fluxo.

## Sequência e checkpoints

1. Leituras públicas/recibo/prévia do provedor e escopo público de revisões do registro, com seus testes de regressão.
2. Base e prévia CPC sem escrita; depois registro/revisão/decisão/retomada com coordenação. **Checkpoint A:** revalidação, ausência de efeitos antes de confirmar, commit/replay e disputa de grupos comprovados.
3. Rotas, projeção oficial e harness isolado, com autorização/CSRF e schema indisponível. **Checkpoint B:** fluxo HTTP completo, privacidade e preservação de recursos/posições/tempo.
4. Controlador/painel e marcadores/hover/retorno ao planejamento. **Checkpoint C:** respostas atrasadas, retry, descarte de edição, confirmação em duas ações e refresh pós-commit verificados.
5. Percurso de navegador, foco/tela estreita, processo novo, histórico e correção. **Checkpoint D:** marco parcial observado, sem anunciar confronto automático ou principal atualizado.
6. Documentação, roteiro 103, controles/spec/plano/lista, comparação SHA-256 e commits/push. Dividir manutenção documental em incrementos de até cerca de cinco arquivos.

Plano será detalhado em `tasks/force-confrontation/julgamento/todo.md` após aprovação desta Fase 2. Cada tarefa terá até cerca de cinco arquivos, testes de comportamento antes da implementação correspondente, dependências e verificação. Execução será sequencial; checkpoints são verificações técnicas do contrato aprovado e não exigem novas confirmações rotineiras. Alteração material do contrato exige revisar o ponto afetado.

## Comandos e evidências previstos

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

Na raiz: `git diff --check`. Verificadores de julgamento/harness são futuros e nenhum teste/inspeção gráfica foi executado nesta fase documental. Confirmar nomes de comandos existentes na lista de tarefas antes de execução; teste vazio não é prova. Não repetir baterias por edição apenas documental.

JMAP-01/09 por autorização/CSRF/privacidade HTTP; 02/03/07 por base/preview/SQL antes/depois e provedor de 112; 04/05 por revisão/recibo/perda de resposta/disputa de locks e estado; 06 por reload e processo novo; 08/11 por ações reais no mapa/painel e viewport; 10 por indisponibilidade e fallback; 12 por regressões, hashes e documentação coerente. Preservar distinção entre teste JS, HTTP e observação real no navegador.

## Riscos e tratamento

| Risco | Tratamento |
|---|---|
| Deadlock entre SQLite e registro em memória | Ordem SQL → registro, commit dentro do escopo, conexão independente e disputa controlada com limite de espera |
| Prévia aceita mudar antes da confirmação | Base/hash com estados e referências; comparação obrigatória e revisão explícita |
| Resposta perdida parecer falha de aplicação | Recibo persistente e retry da mesma intenção antes de consultar grupos atuais |
| Snapshot/preview aparecer como estado oficial | Projeção separada, recursos desconhecidos explícitos e marcadores só com estado confirmado |
| Grupo sumir no reinício | Histórico de origem congelada; não reconstruir grupo ou autorizar confirmação pela cópia |
| Interface liberar adversário ao operador | Rotas de julgamento só do instrutor e DTO oficial restrito por partido |
| Prévia de teste parecer atualização do principal | URL/pasta/contas de teste identificadas e processo principal preservado |

## Gate da Fase 2

Especificação de 113 aprovada por “sim”; submeter este plano concreto à revisão antes de detalhar tarefas de Fase 3. Não há dúvida de localização: diretório já consta da especificação aprovada. Nenhum código/DDL/banco/processo alterado, teste executado ou nova funcionalidade anunciada como pronta nesta etapa.
