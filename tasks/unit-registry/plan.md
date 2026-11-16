# Plano técnico: unit-registry — grupamentos diretos

**Estado: plano aprovado e recorte implementado em 2026-11-16.** O plano foi aprovado por “aprovado”, após a especificação; as [tarefas](todo.md) foram aprovadas posteriormente por “sim”. Local deste plano escolhido explicitamente pelo responsável na opção 1. Entrega em [93](../../docs/recovery/93_ENTREGA_GRUPAMENTOS_EM_MEMORIA.md). Preservar `tasks/plan.md` e `tasks/todo.md`, referentes ao trabalho aberto de `technical-catalog`.

## Resultado pretendido

Entregar um registro de grupamentos diretos navais/aéreos em memória: criar, consultar, revisar, arquivar e preparar composição a partir de unidades existentes no contexto de exercício/partido. Preservar identidade, referências de configuração/snapshot e recursos individuais. Não implementar API, banco, hierarquia completa, modelo físico ou enfrentamento de múltiplos grupos.

## Inspeção e reaproveitamento

| Base existente | Uso proposto |
|---|---|
| `engine_units.py`: `unit_id`, `snapshot_id`, `snapshot_sha256`, `configuration_version_id`, contexto e alocação | Preservar nomes/referências; a primeira fixture simula a visão do provedor, sem escrever nas tabelas existentes |
| JSON canônico de `engine_units.encoded` | Reaproveitar convenção de ordenação/UTF-8/recusa de NaN; não importar a camada SQLite para o domínio novo |
| 08, 49, 53 e 71 | Preservar MPNL, partido, autoridade de dados e snapshots |
| `check_*.py` e fixtures controladas | Verificador focado com biblioteca padrão; resultados esperados para aceite e recusa |
| CPC 84–88 | Regressão de preservação; não refatorar as classes/algoritmos para cadastrar grupos |

Arquivos candidatos: `siscan-prototype/unit_groups.py` e `siscan-prototype/check_unit_groups.py`. Fixture externa somente se necessária para clareza; preferir fixtures pequenas no verificador. Documentação de entrega será atualizada ao implementar. Nenhuma dependência, rota, DDL ou serviço adicional.

## Grafo de dependências

```text
Contexto verificado + visão do provedor de unidades/inventário
                         ↓
         Validação de identidade/snapshot/domínio
                         ↓
         Registro de grupo e consulta por revisão
                         ↓
           Revisão e arquivamento com conflitos
                         ↓
       Preparação congelada com inventário atualizado
```

O provedor é uma entrada do consumidor; não criar import de `party-inventory` dentro de `unit-registry`. Também não importar `engine_runtime` para obter exceções: usar `GroupConflict(ValueError)` local, evitando ciclo com o núcleo de execução.

## Decisões de implementação aprovadas no plano

### 1. Um registro em memória, sem estado global

Uma instância `RegistroGrupamentos` mantém versões, recibos de comando e vínculo direto ativo de integrantes. Métodos terão os nomes de operações da especificação. A chave de contexto será `(exercise_id, team)`; consultar outro contexto não revela a existência do grupo.

Usar armazenamento privado e conteúdo canônico serializado para versões; retornar cópias. Versões não carregam referências mutáveis aos objetos ou dicionários fornecidos pelo chamador. Não copiar combustível/armamentos para um estoque do grupo.

Um `threading.RLock` por registro protege conferência/publicação no mesmo processo. É necessário para revisão esperada e disputa de integrante, inclusive quando dois chamadores tentarem publicar sobre a mesma revisão. Não prometer coordenação entre processos ou recuperação após reinício.

### 2. Fronteira de entrada explícita

Contexto identifica exercício/partido e vem de uma camada já verificada. A visão de inventário fornece registros por `unit_id`, incluindo contexto, domínio normalizado, disponibilidade, configuração, snapshot e seu hash. O primeiro aceite usa fixtures controladas; não se apresenta essa entrada local como autenticação.

Recomputar o hash do snapshot fornecido e conferir sua identidade/configuração/contexto. Não aceitar hashes ou configurações enviados no pedido como substitutos do provedor. Categoria sem normalização demonstrada não será inferida pelo nome do meio.

O pedido de criação contém somente comando, designação, domínio, campos organizacionais opcionais e IDs de integrantes. Revisão exige grupo/revisão esperada e composição completa; arquivamento exige apenas comando/grupo/revisão esperada. Campos extras são recusados. `organization_label` não define escalão; `mpnl_binding`, se informado, deve obedecer 08.

### 3. Hashes e reenvio

Ordenar membros por `unit_id` sem modificar suas identidades. O hash de composição considera o conteúdo da versão, incluindo contexto, ID/revisão, metadados e referências ordenadas, excluindo o próprio campo de hash. Não exigir que grupos diferentes tenham o mesmo hash: suas identidades são diferentes.

`inventory_snapshot_sha256` identifica a projeção do inventário utilizada para conferir os membros, com contexto e referências relevantes. Não é autorização nem comprova disponibilidade futura. Preparação de ensaio sempre verifica uma visão atual do provedor.

Fluxo sob o lock: conferir contexto e formato → normalizar intenção → consultar recibo do comando → se repetido com intenção idêntica, devolver o resultado histórico → se novo, validar estado/revisão/inventário/exclusividade → construir integralmente versão, recibo e vínculos novos → publicar o conjunto.

Recibos usam contexto, operação e `command_id`. Mesmo comando com intenção diferente conflita. Reenvio retorna o resultado daquela operação; não reexecuta sobre uma disponibilidade que mudou. Isso não libera um ensaio: `preparar_composicao` revalida disponibilidade/revisão separadamente.

### 4. Publicação sem estado parcial

Construir as alterações em cópia do estado privado e publicar por uma troca de referência após validação completa. Revisão pode liberar integrantes removidos e reservar adicionados somente junto com a nova versão. Falha não deixa recibo, revisão ou exclusividade parcial.

Arquivar cria versão inativa e libera vínculos diretos, conservando os integrantes históricos. Grupo inativo não prepara ensaio nem recebe nova revisão neste recorte; reabertura permanece fora do escopo. Não apagar o grupo ou as unidades.

### 5. Preparação sem simulação

Retornar contexto, grupo/revisão/hash, referências dos integrantes e manifesto da disponibilidade conferida. Não devolver uma força física agregada nem iniciar relógio, movimento, consumo ou confronto. Mudança do snapshot/configuração usado pela composição gera recusa e exige revisão explícita; não atualizar membros silenciosamente.

A preparação não promove dados técnicos. Flags/estados de evidência e aprovação das unidades permanecem como fornecidos; referência descritiva não vira dado apto a cálculo por estar no grupo.

## Sequência de entregas e checkpoints

| Etapa | Entrega verificável | Critérios da especificação |
|---|---|---|
| 1 | Criar/consultar grupo com membros verificados, isolamento contextual, hash, reenvio e exclusividade inicial | UG-01–05, 08–10, 12–14 |
| 2 | Revisar composição com versão esperada; manter histórico e trocar vínculos de forma indivisível | UG-05–10, 12–14 |
| Checkpoint A | Conferir criação/revisão, recusa de contexto indevido e duas alterações concorrentes sobre a mesma revisão; preservar dados de entrada | UG-03–10, 12–14 |
| 3 | Arquivar grupo, liberar exclusividade e impedir preparação/revisão de grupo inativo | UG-06–08, 10, 12–15 |
| 4 | Preparar composição com disponibilidade atual, recusando snapshot/configuração ou revisão incompatíveis | UG-03–04, 11–14 |
| Checkpoint B | Fluxo completo criar → revisar → preparar → arquivar; reenvios não duplicam; nenhum efeito em recursos, relógio ou bancos | UG-01–15 |
| 5 | Revisão final e documentação do recorte, seus comandos e suas limitações; conferir regressão afetada | UG-01–15 e preservação do protótipo |

As etapas são a ordem de construção. Após aprovação deste plano, a lista de Fase 3 foi proposta em `tasks/unit-registry/todo.md`, sem alterar o checklist aberto de `technical-catalog`. A divisão da verificação final em conferência funcional e controles documentais mantém cada tarefa dentro do limite de arquivos.

## Verificação planejada

Antes de entregar cada etapa: teste focado cobre o fluxo e suas recusas, incluindo ausência de publicação parcial. Conferir entradas antes/depois; consulta histórica mantém o conteúdo; retorno editado pelo consumidor não altera versões; reordenação de membros na mesma intenção não duplica recibo; mudança de contexto não revela outro grupo.

Teste concorrente restrito ao mesmo processo: duas revisões com o mesmo `expected_revision` devem resultar em uma publicação e um conflito, sem revisão perdida. Não transformar esse teste em promessa de concorrência distribuída.

Na raiz do repositório, comandos futuros de aceite:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_unit_groups.py
& $pythonCpc .\siscan-prototype\check_engine_units.py
& $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
git diff --check
```

`check_unit_groups.py` ainda não existe e não foi executado nesta fase. Não usar descoberta de testes vazia como aceite. Não há build ou navegador para esta entrega de domínio, e nenhum banco real deve ser inicializado para os testes do registro em memória.

## Riscos e limites

| Risco | Tratamento |
|---|---|
| Confundir contexto local com autenticação real | Não expor HTTP; documentar fronteira do backend e testar consistência de contexto |
| Inventário muda após criação | Preparação revalida; não usar hash anterior como autorização atual |
| Snapshot/configuração muda | Recusar preparação e exigir revisão explícita |
| Replay duplica revisão ou retorna outro comando | Intenção canônica, recibo contextual e publicação sob lock |
| Recurso aparece em dois grupos | Exclusividade direta ativa verificada no mesmo estado publicado; histórico não conta como vínculo atual |
| Arquivamento apaga evidência | Versão inativa preserva membros/hashes e libera somente vínculos ativos |
| Escopo ultrapassa o protótipo | Sem DDL, integração gráfica, interpretação física de sensores ou efeitos oficiais |

Não alterar originais ou promover dados; não selecionar composições otimizadas para derrotar forças reais. Sem persistência, reiniciar a instância perde grupos/recibos deste recorte. Preservar o ciclo pendente de `technical-catalog`, os dados do exercício e os módulos CPC existentes.

## Gate de conclusão da Fase 2

Gates da Fase 2 e da lista de Fase 3 satisfeitos por aprovações próprias. Recorte implementado e verificado em 93; mudanças futuras de escopo seguem revisão específica.
