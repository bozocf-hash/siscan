# Plano técnico: force-confrontation — preparação de grupamentos

**Data: 2026-11-16. Estado: Fase 1 aprovada por “siga”; Fase 2 aprovada por “seguimos”; tarefas propostas para revisão.** Referência: [especificação](../../SPEC-force-confrontation.md). Manter intactos os planos/listas de `technical-catalog` e a entrega concluída de `unit-registry`. Este local segue a organização por módulo adotada anteriormente; não sobrescreve `tasks/plan.md` ou `tasks/todo.md`.

## Resultado e fronteira

Um módulo Python sem estado persistente produz o dossiê inicial de dois grupamentos do mesmo exercício, um AZUL e um VERMELHO. Usa somente operações públicas do registro e a visão de inventário fornecida por camada confiável. Não importa motor temporal, resolução de combate, servidor, banco ou exportador. Nenhuma transformação de parâmetro técnico em eficácia militar.

Fontes inspecionadas: especificação aprovada, `unit_groups.py` (consulta/preparação e validação de snapshots), estrutura do verificador de grupos e entregas 89/93/94. A inspeção confirmou que `preparar_composicao` já confere domínio, disponibilidade, identidade, configuração e hash. O consumidor não deve reimplementar essas regras ou acessar `_state`/`_lock`.

## Dependências e interface proposta

```text
Provedor: autorização do instrutor + inventário consistente
                         ↓
RegistroGrupamentos: preparar composições por partido
                         ↓
Resolver e copiar snapshots selecionados
                         ↓
Conferir revisões observadas e formar dossiê canônico
                         ↓
Revisão do instrutor — sem execução ou publicação de efeitos
```

Única função pública proposta em `siscan-prototype/cpc_group_preparation.py`:

```python
def preparar_dossie_grupamentos(
    *, exercise_id: int, autorizar_instrutor, registro,
    inventarios: dict, selecao: dict,
) -> dict:
    ...
```

Na implementação, tipar `autorizar_instrutor` como `Callable[[int], bool]` e `registro` como `RegistroGrupamentos`. A função de autorização é fornecida pela camada confiável, vinculada à identidade do usuário por essa camada; não recebe papel/identidade alegados em `selecao`. O teste usa um provedor sintético, sem alegar autenticação real implementada.

`selecao` contém exatamente `AZUL` e `VERMELHO`, cada um com `group_id` e `expected_revision`. `inventarios` contém as duas visões por partido, no formato aceito pelo registro. `exercise_id` é inteiro estrito positivo; revisões são inteiros estritos positivos, IDs são UUIDs canônicos. Não há `command_id`: a operação é uma leitura/preparação pura sem recibo ou publicação.

## Fluxo proposto

1. Validar identidade do exercício e verificar se o autorizador é chamável. Invocá-lo para o exercício antes de consultar grupos/copiar inventários. Somente retorno `True` estrito autoriza; negativa ou retorno inválido gera `PermissionError`. Exceção do provedor aborta, sem liberar consulta e sem transformá-la em autorização.
2. Conferir o formato estrito da seleção e das duas visões. Copiar os inventários para isolar o trabalho de edições posteriores. Essa cópia pressupõe que o provedor entregou vista consistente; não cria uma transação sobre inventário externo sendo alterado simultaneamente.
3. Em ordem AZUL, VERMELHO, chamar `registro.preparar_composicao` com exercício/partido e a revisão selecionada. Usar os snapshots da mesma cópia de inventário validada pelo registro. Não atualizar referências silenciosamente, buscar por nome ou completar dados de outra configuração.
4. Montar cada partido como `{team, composition, snapshots}`: `composition` é o manifesto devolvido pelo registro, `snapshots` é mapa por `unit_id` com os conteúdos integrais dos integrantes selecionados. Não incluir unidades não participantes ou dados privados do provedor/autorizador. Preservar unidades, valores desconhecidos e classificação/estado de aprovação nos snapshots.
5. Consultar a versão atual de cada grupo por `consultar_grupamento`. Conferir ativo, revisão e hash contra o manifesto capturado; divergência observada gera `GroupConflict`. Não alterar o registro nem usar seus locks privados para prolongar a preparação.
6. Construir o envelope definido na especificação, serializar com JSON canônico (`sort_keys=True`, `ensure_ascii=False`, separadores compactos, `allow_nan=False`), calcular SHA-256 UTF-8 excluindo o próprio hash e retornar cópia independente. Conteúdo não serializável produz `ValueError`, sem dossiê parcial.

Não acrescentar horário de parede, UUID aleatório, estoque agregado ou cálculo de poder. O manifesto existente já guarda referências/configurações e seu hash; o novo hash abrange ambos os partidos e o conteúdo dos snapshots, não substitui os anteriores.

### Consistência e validade

As consultas finais detectam revisões/arquivamentos observados durante a preparação. Não demonstram instantâneo atômico dos dois grupos: cada chamada pública possui seu próprio lock. Uma mudança após a conferência pode tornar a preparação histórica imediatamente. Isso é aceitável para o dossiê de revisão, que não reserva recursos nem inicia simulação. Não afirmar que o dossiê está permanentemente disponível ou autorizado para execução futura.

Não haverá repetição automática em caso de conflito. O chamador deverá obter uma vista atual e preparar novamente com as revisões escolhidas. O risco de coordenação mais forte pertence à futura integração de execução/persistência, não será escondido por um lock local novo.

### Erros

Preservar `ValueError`, `KeyError`, `GroupConflict` e `PermissionError` conforme a especificação. Mensagens de ausência/contexto não devem revelar grupos de outro partido/exercício. Não capturar genericamente exceções para devolver lista vazia, status válido ou resultado parcial. Não registrar snapshots nem dados do provedor em logs de erro.

## Ordem de construção e checkpoints

| Etapa | Entrega verificável | Cobertura |
|---|---|---|
| 1 | Preparação válida com registro real em memória e bloqueio de autorização antes de leitura | GP-01–05, GP-11–12 |
| 2 | Recusas por segundo partido inválido e alteração observada de revisão/arquivamento, sem resultado parcial | GP-04–07, GP-11 |
| Checkpoint A | Fluxo com dois partidos e recusas preserva registro, inventário e recursos | GP-01–07, GP-11–12 |
| 3 | Independência das cópias, snapshots integrais, ordem canônica e hash reproduzível | GP-08–10 |
| 4 | Regressões afetadas e documentação de entrega/limites, sincronização e Git | GP-01–12 |
| Checkpoint B | Todos os critérios demonstrados com testes reais; nenhuma execução de combate ou efeito oficial | GP-01–12 |

Implementar sequencialmente por compartilhar o mesmo contrato; não requer agentes paralelos. O módulo e seu verificador são os únicos candidatos novos de código. Fixture controlada preferencialmente no verificador, sem importar testes na produção ou consultar banco real.

A lista detalhada de Fase 3 será registrada em `tasks/force-confrontation/todo.md` após aprovação deste plano, com aceites, comandos e arquivos de cada tarefa. Não antecipar sua implementação. Na tarefa documental final, dividir a manutenção de controles se ultrapassar aproximadamente cinco arquivos por tarefa.

## Verificação planejada

Usar `unittest` com casos positivos e negativos. Exercitar autorização por provedor que conta acessos: contexto negado não pode invocar o registro. Mutação de revisão entre chamadas será provocada de forma controlada, sem sleeps ou depender da ordem de threads. Testes devem preservar o comportamento público do registro, não inspecionar seu armazenamento privado.

Comparar inventários e consultas antes/depois nos fluxos válidos e nas falhas. Editar retorno/entradas para demonstrar independência. Conferir hash sobre conteúdo canônico; permutar ordem de mapas não muda o hash, mudar snapshot exige revisão explícita e gera preparação diferente. Testar snapshots com dados desconhecidos/extra e classificações diversas, preservados sem interpretação.

Comandos futuros, na raiz do repositório:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_cpc_group_preparation.py
& $pythonCpc .\siscan-prototype\check_unit_groups.py
& $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
git diff --check
```

O novo verificador ainda não existe. Estes comandos não foram executados nesta etapa documental; nenhuma contagem de testes é presumida. A descoberta `check_cpc_*.py` também incluirá o novo verificador após sua criação; a execução focada serve para diagnóstico. Não há build/navegador/servidor a iniciar.

## Riscos e mitigação

| Risco | Tratamento |
|---|---|
| Autorização alegada pelo pedido | Autorizador confiável separado, com negativa antes de leitura; nenhum endpoint nesta fatia |
| Inventário externo muda durante captura | Provedor entrega vista consistente; cópia local isola o trabalho subsequente |
| Revisão muda entre as duas preparações | Conferência pública final, conflito explícito e ausência de resultado parcial |
| Confundir cópia com disponibilidade reservada | Status exige revisão; sem relógio/execução, validade futura não garantida |
| Dossiê vaza inventário completo | Incluir somente snapshots dos integrantes selecionados |
| Hash interpretado como validação física | Preservar classificações, status global falso e limites documentados |
| Duplicar motor ou regras de registro | Reutilizar operações públicas, sem refatorar CPC temporal ou criar resolução de grupos |

Sem DDL, dependências, gravação de dados oficiais, integração gráfica ou interpretação física de sensores. Os bancos originais, estados do exercício e decisões MPNL permanecem intocados.

## Gate da Fase 2

Especificação e plano aprovados pelo responsável. Lista de [Fase 3](todo.md) proposta conforme [96](../../docs/recovery/96_TAREFAS_PREPARACAO_CPC_GRUPAMENTOS.md), aguardando aprovação. A concepção gráfica de [97](../../docs/recovery/97_CONCEPCAO_GRAFICA_DISPOSICAO_E_CONFRONTO.md) preserva expressamente o mapa já definido e não amplia o escopo desta implementação. Não iniciar código antes do gate da lista.
