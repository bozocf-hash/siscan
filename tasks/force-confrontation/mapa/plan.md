# Plano técnico: force-confrontation — par CPC no mapa

**Data: 2026-11-17. Estado: especificação do Recorte 2 aprovada por “siga”; Fase 2 proposta para revisão.** Base: [SPEC-force-confrontation.md](../../../SPEC-force-confrontation.md), [104](../../../docs/recovery/104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md) e [105](../../../docs/recovery/105_ESPECIFICACAO_PAR_CPC_NO_MAPA.md). Este diretório preserva os planos anteriores do catálogo, do dossiê e da composição gráfica. Sem implementação nesta etapa.

## Resultado e dependências

Instrutor escolhe grupos AZUL/VERMELHO, prepara o dossiê no backend e confere ambas as forças no mesmo mapa ATLANTICADOR. Não há execução, impacto proposto, confirmação oficial, consumo, relógio ou persistência nesta fatia. A ordem completa de 104 continua válida; a preparação visual não será apresentada como confronto concluído.

```text
Sessão/participação + registro de grupos + provedor SQL autorizado
                              ↓
Lista CPC e captura de inventários/posições
                              ↓
preparar_dossie_grupamentos (contrato 98 preservado)
                              ↓
Projeção de conferência e manifesto geográfico
                              ↓
Painel CPC + camada de consulta no mapa existente
```

Código inspecionado: `map_groups.view/listing`, `cpc_group_preparation.preparar_dossie_grupamentos`, consultas públicas do registro, rotas/sessão/CSRF de `app.py` e adaptador `atlantic-bridge.mjs`. A ponte de grupos já fornece unit_id/asset_id, nomes, coordenadas/revisão e inventário elegível. Não inserir o CPC no provedor de identidade nem acessar armazenamento/locks privados.

## Backend proposto

Novo `siscan-prototype/cpc_map.py` oferece operações de lista e preparação ao servidor. Autorizar explicitamente instrutor participante antes de consultar qualquer partido, usando o contexto do exercício existente. GET pode informar exercício encerrado; POST deve recusá-lo. Exercício/versão de cenário vêm do servidor, nunca como autorização fornecida pelo cliente.

### Lista e seleção

`GET /api/cpc/groups` devolve exercício/versão, estado aberto/encerrado, aviso de armazenamento temporário e dois partidos em ordem AZUL/VERMELHO. Para cada grupo: ID, designação, revisão, domínio, ativo, elegibilidade para preparar e motivo de impedimento. Reaproveitar consultas públicas e projeção contextual existentes; não mandar inventário completo ou snapshots brutos.

Grupo inativo ou com referências/visibilidade pendentes fica visível para o instrutor com motivo e seleção desabilitada. Lista vazia não é erro de conexão. Não escolher automaticamente grupos, mesmo quando houver somente um por partido.

### Captura e preparação

`POST /api/cpc/preparations` recebe exatamente AZUL/VERMELHO com `group_id` e `expected_revision`. Sessão/CSRF existentes, sem `command_id`: não há publicação ou recibo nesta operação pura.

Fluxo:

1. Autorizar e validar formato. Abrir uma vista SQL de leitura consistente na conexão existente; manter transação local ao adaptador, sem importar helper privado de outro módulo ou adquirir lock de escrita sem necessidade.
2. Capturar as visões públicas de inventário/posições dos dois partidos no mesmo exercício. A captura do cenário pertence à mesma vista. O provedor atual reconhece somente configurações efetivamente demonstradas; não ampliar domínios ou criar instâncias.
3. Chamar `preparar_dossie_grupamentos` uma vez com os inventários capturados, a seleção e autorizador interno vinculado ao instrutor. Preservar seu schema/hash e todos os bloqueios existentes.
4. Resolver somente membros selecionados pelo vínculo unit_id/asset_id. Copiar nomes/códigos, partido, referências de composição/snapshot/configuração e posições/revisões. Campo geográfico ausente permanece nulo; não usar nome, ID DB3K ou centroide para completar o vínculo.
5. Fechar a vista SQL e conferir novamente fontes atuais relevantes: contexto/cenário, vínculos/referências dos participantes e manifesto de posições; consultar revisões/atividade dos grupos pelos métodos públicos. Divergência observada gera conflito sem resposta parcial, nunca atualização silenciosa ou repetição automática.
6. Construir a projeção canônica e seus hashes, devolver cópia independente com revisão do instrutor pendente e todos os flags de execução/aplicação falsos.

Cada consulta pública de grupos tem seu próprio lock. A verificação final detecta alterações observadas, mas não faz transação distribuída nem garante disponibilidade futura. Não manter um lock privado do registro durante SQL ou prometer que uma alteração posterior invalida magicamente a cópia já entregue. A próxima execução/decisão precisará de seus próprios contratos de revisão e disponibilidade.

### Saída e hashes

| Campo/conteúdo | Decisão do plano |
|---|---|
| `schema_version` | `siscan-cpc-map-preparation-01` |
| `exercise_id`, `scenario_version` | Contexto capturado e conferido no servidor |
| `dossier_sha256` | `preparation_sha256` do dossiê 98; sem alterar seu significado |
| Partidos/grupos | Ordem AZUL/VERMELHO, IDs, designações, revisões e domínio |
| Integrantes | Ordenados por unit_id; vínculo asset_id, nome/código, posição e referências técnicas necessárias à conferência |
| `positions_sha256` | Hash do manifesto geográfico dos integrantes selecionados, com contexto, partido, identidade, coordenadas/revisão |
| `view_sha256` | Hash da projeção completa, sem o próprio campo |
| Estado | `requires_instructor_review`; simulação, aptidão oficial e aplicação de efeitos sempre falsas |

Usar JSON canônico com ordenação, UTF-8 e recusa de NaN, seguindo a convenção do projeto. Não incluir relógio de parede ou UUID aleatório no cálculo. O backend pode manter o dossiê completo apenas como variável local durante a operação; não criar armazenamento temporário adicional para recuperá-lo por uma chave enviada pelo cliente.

Mudança somente de posição mantém o hash técnico e altera os hashes geográfico/visual. Mudança de nome pode alterar a vista, sem redefinir identidade ou hash técnico. Unidade externa ao par não entra nos manifestos. Não exibir o conteúdo de combustível do snapshot como saldo atual: esta projeção informa que é configuração inicial, deixando estado logístico atual não informado quando não houver contrato de fonte atual.

### HTTP e falhas

Rotas em `app.py`, usando o registro único já pertencente ao servidor. Reutilizar autenticação/CSRF; respostas 401/403/400/404/409/503 conforme a especificação. Não devolver IDs/dados de outro contexto na mensagem de erro. Integridade indisponível não vira lista vazia nem aptidão falsa convertida em sucesso de execução.

Novo módulo gráfico segue a política autenticada dos adaptadores. Carregamento deve ser opcional em processo antigo, preservando mapa/grupos existentes quando o módulo/rotas CPC não estiverem disponíveis. Não apresentar botão funcional de confirmação ou iniciar o motor CPC temporal nesta integração.

## Interface e camada de conferência

Novo `static/cpc-preparation.mjs` mantém seletores, revisão exibida, carga/erro/conflito e ficha do par. O adaptador do mapa oferece uma área CPC somente para instrutor e controla troca de modo/camadas. Operador não recebe a lista adversária nem o par para escondê-los por CSS.

Ao entrar: salvar a perspectiva/área de planejamento que será restaurada; cancelar reposicionamento/seleção de área pendentes, limpar realce de grupo e suspender a camada de meios de planejamento. Mostrar uma camada de consulta com os integrantes do par preparado, sem instanciar outro mapa ou editar feições originais. Reutilizar a construção visual/simbologia existente, passando partido explicitamente em vez de usar o seletor global de partido para colorir todos os meios.

Marcadores de conferência têm apenas consulta: clique abre ficha no painel, teclado acessa o integrante, sem popup de reposicionamento ou envio de plotagem. Não duplicar um asset por pertencer aos dados de planejamento e do par. Meios sem posição aparecem somente na lista. Enquadrar o par considera o espaço ocupado pelo painel e só muda câmera após solicitação.

Ao sair: invalidar requisições pendentes, remover a camada de consulta, reativar planejamento e recarregar meios autorizados atuais da perspectiva anterior. Não restaurar um inventário antigo em cache. Fechar/revogar sessão ou receber 403 limpa ambos os partidos da vista de conferência.

O controlador usa gerações de requisição: trocar seleção/iniciar nova carga/sair impede POST antigo de repintar o par. Alterar seleção invalida imediatamente a conferência anterior. Cenário/exercício diferentes entre lista e resposta exigem atualização explícita da seleção; não manter legenda de contexto antigo sobre resposta nova. Nova escolha nunca reutiliza uma preparação como autorização futura.

Rótulos: seleção do par, situação inicial, posições de planejamento, referências técnicas em expansão e aviso de que julgamento/decisão ainda não estão disponíveis. Preparar não tem aparência de batalha concluída. Um único painel, nomes como texto, foco visível, teclado e telas ampla/estreita. Preservar a largura normal da aplicação após testes de viewport.

## Ordem e checkpoints

| Etapa | Entrega verificável | Critérios |
|---|---|---|
| 1 | Provedor de lista/captura/projeção com autorização, identidade e hashes distintos | CP-01–06, CP-10–11 |
| 2 | Rotas reais com sessão/CSRF e falhas coerentes, sem efeitos SQL/memória | CP-01–06, CP-11–12 |
| Checkpoint A | Dados e HTTP passam; comparação antes/depois preserva posições, recursos, relógio e estado | CP-01–06, CP-10–12 |
| 3 | Painel de seleção/conferência, invalidação e respostas fora de ordem | CP-02, CP-09–12 |
| 4 | Camada simultânea no mapa, consulta e retorno seguro ao planejamento | CP-04, CP-07–08, CP-11–12 |
| Checkpoint B | Navegador real comprova par no mesmo mapa sem duplicidade ou plotagem; operadores sem acesso | CP-01–12 |
| 5 | Documentação, controles, sincronização e Git com status/limites comprovados | CP-01–12 |

Execução sequencial por contratos compartilhados; não requer agentes paralelos. Após aprovação deste plano, detalhar Fase 3 em `tasks/force-confrontation/mapa/todo.md`, dividindo tarefas para manter até cerca de cinco arquivos cada. Não modificar listas antigas ou reabrir gates cumpridos de 98/102/104/105.

## Verificação planejada

Novos verificadores candidatos: `check_cpc_map.py` (provedor), `check_cpc_map_http.py` (rotas) e `check_cpc_preparation.mjs` (seleção/assincronia). Fixtures/harness reutilizam a base isolada de grupos; cookie exclusivo, porta livre e caminhos temporários. Não reiniciar servidor em uso, copiar grupos do usuário ou usar a base principal para testes.

Casos: recusa antes da leitura dos dois partidos; fechamento; arquivo/revisão/snapshot/adjudicação incompatíveis; posição ausente e alteração observada; determinismo e separação dos hashes; cópias; participante externo não muda manifesto; resposta atrasada após saída/nova seleção; visualização simultânea e retorno ao planejamento; zero comandos de plotagem/execução e nenhum consumo nos caminhos válidos/falhos.

Na pasta `prototype`, comandos futuros:

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

Arquivos novos ainda não existem; nenhum teste executado nesta fase documental. Depois de alterações pertinentes, conferir `git diff --check`; não repetir baterias por documentação posterior. O teste de posições deve variar a posição em fixture isolada, não mover meios do usuário para gerar o caso.

Navegador real: selecionar ambos os grupos, preparar, contar marcadores e conferir partido, abrir integrantes e referências, mudar seleção com requisição pendente, sair/restaurar, teclado e viewport estreito. Conferir console/rede pelos recursos disponíveis e registrar limites. Não instalar ferramentas/dependências de navegador; usar os recursos disponíveis na implementação e remover overrides de largura ao terminar.

## Riscos e mitigação

| Risco | Tratamento |
|---|---|
| Hash técnico interpretado como posição ou prontidão | Três referências distintas e flags de execução/aplicação falsos |
| Vista muda durante captura | Leitura consistente e conferências atuais finais; conflito observado recusa, sem prometer reserva/atomicidade distribuída |
| Vazamento da força adversária | Instrutor participante autorizado antes de fonte; operador recusado no servidor |
| Plano inicial apresentado como estado atual | Rótulos de origem e ausência explícita de contrato logístico atual |
| Clique de conferência gera movimento | Camada sem handlers de plotagem, cancelamento de modos e comparação SQL no navegador de teste |
| Resposta atrasada restaura vista antiga | Geração de requisição e limpeza ao sair/trocar seleção/contexto |
| Processo antigo perde o mapa por módulo novo ausente | Carregamento opcional e indisponibilidade explícita, preservando ferramentas anteriores |

## Gate da Fase 2

Especificação aprovada por “siga”; este plano aguarda revisão antes da lista de tarefas. Sem código, DDL, banco, execução de testes ou validação visual nesta etapa. Julgamento/decisão/aplicação oficial continuam as próximas entregas da ordem aprovada em 104.
