# Plano técnico: unit-registry — grupamentos no mapa

**Data: 2026-11-16. Estado: especificação do Recorte 2 aprovada por “siga”; Fase 2 e lista de Fase 3 aprovadas; implementação verificada em 102.** Base: [SPEC-unit-registry.md](../../../SPEC-unit-registry.md), extensão de 99. Este local preserva os planos antigos do catálogo e os recortes concluídos de composição/dossiê 93/98. Recorte entregue conforme [102](../../../docs/recovery/102_ENTREGA_GRUPAMENTOS_NO_MAPA.md).

## Resultado

No mapa ATLANTICADOR existente, uma aba do painel lateral permite criar, consultar e arquivar grupos das unidades elegíveis do partido autorizado. Selecionar um grupo realça os marcadores existentes. Falta de posição/snapshot/domínio aparece explicitamente, sem inventar dados ou criar unidades. O registro continua temporário em memória, com aviso persistente.

## Evidências e reaproveitamento

| Base inspecionada | Decisão |
|---|---|
| `engine_units.list_units` | Usar identidade/snapshot/configuração conferidos; filtrar exercício/partido/alocação antes da projeção |
| `map_units.context`/`listing` | Reaproveitar autorização ao partido e nomes/códigos/posições dos meios adjudicados |
| `RegistroGrupamentos` | Reutilizar criação/arquivamento, revisão esperada, recibos, exclusividade e lock; acrescentar apenas consulta pública de lista contextual |
| `app.py` | Integrar às sessões, CSRF e `ThreadingHTTPServer` existentes; nenhum servidor paralelo ou framework |
| `static/atlantic-bridge.mjs` | Reutilizar painel, abas e `markerIndex`; não alterar ZIP original ou substituir o mapa preparado |
| `engine_units.prepare_units`/schema | Só existe configuração aérea sintética nesta entrada atual; UNIQUE por exercício/partido/finalidade limita o caso disponível. Não anunciar integração de todas as classes reais |

O campo `group_name` das submissões não é fonte de composições. Registros da demonstração 98 também não serão importados automaticamente: seus IDs fictícios não provam vínculo aos meios do mapa.

## Dependências

```text
Sessão/participação + inventário adjudicado + instâncias/snapshots
                                  ↓
Adaptador autorizado de identidade/elegibilidade
                                  ↓
Registro contextual + rotas HTTP de grupos
                                  ↓
Módulo gráfico no painel e realce dos marcadores existentes
                                  ↓
Verificação HTTP/JS/navegador em dados isolados
```

Sem inversão entre inventário e identidade: o adaptador consome as duas fontes, não faz o registro importar servidor/SQLite. A seleção não importa o motor CPC. Sem novos módulos funcionais no mapa de capacidades, DDL ou dependências.

## Contratos e decisões propostos

### 1. Adaptador de identidade/elegibilidade

Novo `siscan-prototype/map_groups.py` concentra contexto, visão do provedor e projeção segura. Autorizar sessão/participação/partido antes de ler dados; operadores apenas no próprio partido, instrutor no partido solicitado. Escrita exige exercício aberto.

Relacionar `unit_id`/`asset_id` explicitamente no mesmo exercício/partido, com adjudicação ativa. Usar as verificações públicas de snapshots existentes; não procurar por nome/categoria textual ou aceitar vínculo enviado pelo cliente. Captura de leituras deve ser consistente na conexão SQLite, sem afirmar transação atômica entre SQL e registro em memória.

Normalização inicial: regra explícita para a configuração sintética criada por `engine_units.prepare_units`, conferindo finalidade/modelo/configuração e conteúdo controlado, com evidência da origem. Não basta `source_kind=synthetic_controlled` ou nome com “aéreo”. Uma configuração não reconhecida fica pendente. Não editar o snapshot para inserir domínio, rehashá-lo ou promover aprovação.

Resposta separa unidades elegíveis e meios pendentes, com motivo legível. Elegível significa apto ao cadastro de composição deste recorte, não apto a cálculo oficial. Não selecionar automaticamente meios pendentes nem criar instâncias/snapshots para completar o grupo.

### 2. Registro único e consultas públicas

Uma instância de `RegistroGrupamentos` pertence ao objeto servidor e é compartilhada pelos handlers de suas threads. Instâncias de servidores de teste são independentes. Não criar registro por requisição, usar estado global do navegador ou inicializar dados demonstrativos no exercício real.

Adicionar `listar_grupamentos(contexto)` ao registro: versões atuais, inclusive arquivadas, em ordem determinística, como cópias limitadas ao contexto e sob seu lock. O adaptador usa somente essa função e os métodos públicos existentes; não lê `_state`/`_lock` de fora. Preservar os testes do primeiro recorte.

GET e respostas de POST passam pela projeção autorizada atual. Se vínculo foi revogado, não devolver nome, posição, snapshot ou referência técnica do integrante ao operador; apresentar membro indisponível e contagem, sem permitir que o histórico/recibo contorne visibilidade atual. Não enviar inventário inimigo ou snapshots integrais desnecessários ao navegador.

Grupo cuja disponibilidade mudou continua histórico, marcado para conferência. Membros autorizados, mas sem posição, aparecem como “Sem posição”. Falha de integridade não é convertida em elegibilidade ou lista vazia válida. Arquivar libera os vínculos sem exigir disponibilidade de todos os integrantes históricos, respeitando o contexto autorizado.

### 3. Rotas e comandos

Implementar os três contratos de 99:

- `GET /api/map-unit-groups?team=...`: valida consulta estrita e devolve grupos/projeções/elegibilidade do partido, com `storage=memory` e aviso de perda após reinício.
- `POST /api/map-unit-groups`: corpo estrito da especificação; CSRF e autorização atuais; cria pela visão do provedor e devolve resultado contextual projetado.
- `POST /api/map-unit-groups/{group_id}/archive`: ID canônico da URL, corpo estrito, revisão esperada, CSRF; usa arquivamento do registro.

Não introduzir resposta incompatível para as rotas existentes. Manter 403/400/404/409 conforme a especificação, sem revelar existência de outro contexto. Reenvio com mesma intenção preserva a operação histórica, mas a resposta projetada respeita visibilidade atual. O recibo não autoriza disponibilidade futura.

Criação não escreve na base SQLite: nenhum novo meio, posição, evento de recurso ou saldo. Leituras de adjudicação e escrita em memória não reservam recursos no banco. Desadjudicação posterior exige atualização da vista; futuras garantias de execução/persistência não serão alegadas nesta tela.

### 4. Interface e seleção

Módulo específico `static/map-groups.mjs` para lista, formulário, confirmação de arquivamento e estados de carga/erro. `atlantic-bridge.mjs` mantém o controle do mapa, das abas e do índice de marcadores. Servir o módulo pela mesma política autenticada dos adaptadores existentes, sem copiar biblioteca ou código do mapa.

Criar aba “Grupamentos” no mesmo painel. O seletor de partido deve permanecer acessível ao instrutor ao alternar abas, com uma fonte de verdade comum; operador continua fixo no próprio partido. Abrir grupo fecha a outra área lateral, sem nova janela ou painel sobreposto.

Manter duas seleções distintas: meios escolhidos para plotagem/reposicionamento e integrantes realçados para consulta de grupo. Não reutilizar o conjunto `selected` da plotagem para um realce somente de leitura. Troca para a aba de grupos cancela reposicionamento/seleção de área em curso e restaura arraste do mapa; não confirma coordenadas pendentes. Cliques em integrantes no modo de consulta não enviam comando de plotagem.

Passar ao módulo de grupos funções pequenas de realçar/enquadrar IDs de assets existentes, sem expor o mapa inteiro ou duplicar marcadores. “Enquadrar integrantes” só altera a câmera após ação explícita e quando há posição. Realce deve ser reaplicado aos marcadores ainda autorizados quando a listagem do mapa for redesenhada, sem restaurar seleções revogadas.

Carregamento usa token sequencial de contexto e descarte de resposta antiga; `AbortController` quando cabível. Trocar partido limpa imediatamente grupo, seleção, detalhes e erros anteriores. Resposta de criação/arquivamento que chega após a troca não reabre a seleção antiga; a operação concluída pertence ao contexto original. Manter comando pendente para reenvio da mesma intenção em falha de rede, sem reutilizá-lo após editar o pedido.

Renderizar nomes/designações como texto. Mostrar carregamento, vazio verdadeiro, falha de conexão, pendência e arquivado distintamente. Aviso temporário sempre visível; reinício resulta em lista vazia real, nunca reconstrução silenciosa. Foco/teclado e confirmação de arquivamento; grupo não recebe barra de poder ou capacidade fictícia.

## Sequência e checkpoints

| Etapa | Entrega verificável | Critérios |
|---|---|---|
| 1 | Adaptador de identidade/elegibilidade com autorização e pendências explícitas | GM-02–04, GM-11 |
| 2 | Consulta pública contextual, rotas de criar/consultar/arquivar e registro por servidor | GM-04–05, GM-07, GM-09, GM-12 |
| Checkpoint A | Testes de provedor/HTTP, sessão/CSRF, conflito/reenvio e visibilidade passam | GM-02–05, GM-07, GM-11–12 |
| 3 | Aba/formulário/lista com estados e isolamento de respostas atrasadas | GM-01, GM-03–05, GM-08–10 |
| 4 | Realce/enquadramento seguros, modos de interação e verificação no mapa real isolado | GM-01, GM-06, GM-08, GM-10–12 |
| Checkpoint B | Fluxo completo no mapa definido sem alterar meios/recursos do usuário | GM-01–12 |
| 5 | Documentar limites/evidências, atualizar controles, sincronizar e versionar | GM-01–12 e preservação |

Construção sequencial por compartilhar contratos/arquivos; não requer agentes paralelos. A lista detalhada de Fase 3 em `tasks/unit-registry/mapa/todo.md` foi aprovada e executada. Dividir integração de servidor, gráfico e controles em tarefas de até cerca de cinco arquivos. Os checkpoints são verificações técnicas; não reabrem gates de escopo já aprovados.

## Verificação planejada

Novos verificadores candidatos: `check_map_groups.py` (provedor/registro), `check_map_groups_http.py` (sessões/rotas) e `check_map_groups.mjs` (seleção/assincronia). O HTTP usa diretório temporário, banco de teste e servidor em porta livre. Configurar caminhos do módulo `app` no harness isolado antes de inicializá-lo; `SISCAN_PORT` sozinho não isola `DB_PATH`/`DATA_DIR`. Não iniciar `app.main` sobre a base do usuário para testar.

Verificar publicação única em comandos concorrentes, arquivo com revisão desatualizada, adjudicação revogada, replay sem vazamento, troca de partido enquanto GET/POST estão pendentes, distinção de seleção de consulta/plotagem e preservação bidirecional dos dados SQL. Primeiro aceite HTTP pode usar a unidade sintética atual de cada partido; não adicionar meios reais ou remover o limite de instâncias para aumentar a demonstração.

Comandos futuros na pasta `siscan-prototype`:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_map_groups.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_unit_groups.py
& $pythonCpc check_map_units.py
node check_map_groups.mjs
node check_map_visuals.mjs
```

Novos arquivos implementados e verificações executadas: 53 testes nomeados, dois verificadores assertivos e inspeção de navegador, conforme 102. Após os testes pertinentes, `git diff --check`. Regressões adicionais somente quando alteração/falha justificar; não repetir software por edição apenas documental.

Antes de declarar a interface entregue, conferir navegador real com mapa preparado em cópia de teste, sessões/CSRF isolados e porta própria: criar/selecionar/enquadrar/arquivar, recusa de outro partido, zero painel sobreposto, foco/teclado, viewport estreita, ferramentas anteriores preservadas e ausência de console/network errors pertinentes. Não mover os meios do usuário. A seleção de controles/ferramenta de teste será feita entre os recursos disponíveis na implementação; não há ferramenta Chrome DevTools configurada nesta sessão, nem instalação autorizada por este plano.

## Riscos e limites

| Risco | Tratamento |
|---|---|
| Catálogo confundido com instâncias prontas | Snapshot/domínio/vínculo exigidos; ausência vira pendência explícita, não cadastro automático |
| Resposta antiga vaza outro partido | Projeção no servidor e descarte imediato por token de contexto no cliente |
| Recibo histórico contorna revogação | Resultado projetado novamente com autorização/visibilidade atuais |
| Seleção de consulta desloca unidades | Separar realce de seleção de plotagem; cancelar modos ao mudar aba |
| Registro por handler perde grupos | Uma instância por servidor, thread-safe, com reset explícito no reinício |
| Uso operacional interpreta memória como durabilidade | Aviso persistente; persistência exige recorte posterior |
| Teste atinge banco em uso | Harness isola DATA_DIR/DB_PATH e porta antes de iniciar servidor |
| Promessa de combate pronto | Interface apenas compõe/consulta/arquiva; sem relógio, tiros, replay ou resultado oficial |

## Conclusão

Especificação, plano e tarefas aprovados em interações distintas; GMAP-01–09 verificadas em [102](../../../docs/recovery/102_ENTREGA_GRUPAMENTOS_NO_MAPA.md). Código sincronizado/versionado; servidor principal não reiniciado. Guia de uso e limites do confronto em [103](../../../docs/recovery/103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md).
