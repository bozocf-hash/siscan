# 93 — Entrega do registro de grupamentos em memória

**Data: 2026-11-16. Estado: recorte implementado e verificado.** O responsável aprovou escopo, especificação, plano e tarefas em interações distintas; a aprovação da lista de Fase 3 foi “sim”. Executadas UGR-01–UGR-06. Esta entrega é o contrato de composição, não a integração oficial de confrontos entre grupamentos.

Referências: `SPEC-unit-registry.md`, `tasks/unit-registry/plan.md`, `tasks/unit-registry/todo.md`, 08/49/53/71 e documentos preparatórios 89–92. Os registros preparatórios descrevem seu estado nas etapas anteriores; o status atual de implementação e gates é este documento e o checklist concluído, sem reabrir aprovações já dadas.

## Código entregue

`siscan-prototype/unit_groups.py` usa apenas biblioteca padrão. `RegistroGrupamentos` oferece:

| Operação | Comportamento |
|---|---|
| `criar_grupamento(contexto, inventario, pedido)` | Valida integrantes e cria revisão 1; mantém referências individuais |
| `consultar_grupamento(contexto, group_id, revision=None)` | Retorna versão explícita ou atual como cópia, limitada ao contexto |
| `revisar_grupamento(contexto, inventario, pedido)` | Exige revisão esperada; preserva histórico e troca vínculos no mesmo estado publicado |
| `arquivar_grupamento(contexto, pedido)` | Cria revisão inativa e libera vínculos diretos; não apaga unidades/versões |
| `preparar_composicao(contexto, inventario, group_id, expected_revision)` | Confere disponibilidade/referências atuais; retorna manifesto sem iniciar simulação |

Armazenamento privado contém versões JSON canônicas, recibos e vínculos ativos. `threading.RLock` serializa conferência/publicação no mesmo processo. Alterações são construídas em cópia antes da publicação. Não há coordenação entre processos ou persistência após reinício.

## Entradas e fronteira do provedor

Contexto: `exercise_id` inteiro positivo e `team` igual a `AZUL` ou `VERMELHO`. É uma entrada interna já verificada; não é autenticação. Não existe endpoint que aceite esse objeto de um cliente nesta entrega.

A visão de inventário é um mapa por `unit_id`. Cada integrante selecionado deve fornecer:

- Identidade/contexto: `unit_id`, `exercise_id`, `team`.
- `allocated=True` estrito: disponibilidade de alocação ao partido, não prontidão física para combate.
- `domain` normalizado e `domain_evidence={domain, basis, reference}`. Bases aceitas: `synthetic_controlled` ou `catalog_mapping`; referência não vazia. O módulo confere formato/coerência dessa declaração de um provedor confiável, não pesquisa ou aprova por conta própria a fonte citada.
- `snapshot_id`, `snapshot_sha256`, `configuration_version_id` e o conteúdo `snapshot`.

O SHA-256 do conteúdo é recalculado, e identidade/contexto/configuração são comparados. O snapshot mantém sua classificação `source_kind` e seu estado `official_calculation_ready`, inclusive ausência/pendência. Esses campos não são promovidos pelo cadastro de grupo.

`inventory_snapshot_sha256` registra a projeção efetivamente utilizada dos integrantes escolhidos. Alteração de unidade não participante não muda esse manifesto; alteração de disponibilidade/referências de participante é conferida na preparação. O lock do registro não sincroniza edições externas no inventário: o provedor deve entregar uma visão consistente.

## Invariantes demonstrados

Cada unidade possui no máximo um vínculo direto ativo no mesmo exercício/partido. Versões anteriores mantêm os integrantes históricos sem reservá-los novamente. Campos extras no pedido, membro repetido, unidade desconhecida/não alocada, domínio incompatível ou snapshot divergente recusam a operação.

Comando idêntico retorna o resultado daquela operação, inclusive após uma revisão/arquivamento posterior. Isso não reativa a versão antiga: consulta atual e preparação conferem o estado/revisão atuais. Comando reutilizado para intenção ou operação diferente gera `GroupConflict`.

Arquivar libera integrantes e preserva história. Grupo inativo não pode ser revisado, reaberto ou preparado neste recorte. Preparar não atualiza snapshots/configurações silenciosamente; exige revisão explícita quando as referências mudam.

Domínio operativo é distinto de Força organizacional. Um vínculo MPNL explícito aceita somente ramos/níveis de 08, sem inferir o ramo pelo meio ser aéreo/naval. “Esquadrilha” permanece designação e não altera os níveis provisórios aéreos. Não foi criado nível de subunidade terrestre.

## Testes e critérios

**29 testes de grupamentos passaram**, cobrindo UG-01–UG-15. Também passaram os **81 testes CPC existentes** e o verificador `check_engine_units.py`, que usa SQLite `:memory:` para identidade/snapshot/alocação. Não foi executada uma bateria indiscriminada dos demais subsistemas, que não foram alterados.

| Critérios | Evidências no verificador |
|---|---|
| UG-01–02 | Composição de referências heterogêneas; designação aérea sem inferência MPNL |
| UG-03–04 | Contexto/disponibilidade/domínio; normalização e hash; identidade falsa com hash recalculado recusada |
| UG-05 | Membro repetido/disputa recusados; duas criações concorrentes publicam somente uma para o mesmo integrante |
| UG-06–07 | Revisão preserva histórico; revisão desatualizada e duas revisões concorrentes não perdem atualização |
| UG-08–09 | Reenvio, ordem canônica dos membros e chave vinculada à intenção/operação |
| UG-10 | Cópias de retorno e falha sem reservar parcialmente um integrante válido |
| UG-11 | Preparação revalida disponibilidade e alteração de snapshot/configuração |
| UG-12 | Consultas e recibos não atravessam contextos |
| UG-13–14 | Entradas/recursos preservados; preparação não inicia simulação ou promove referência descritiva |
| UG-15 | Arquivamento libera vínculos, preserva histórico e impede preparação de grupo inativo |

Na raiz do repositório:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_unit_groups.py
& $pythonCpc .\siscan-prototype\check_engine_units.py
& $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
```

Na pasta de entrega `C:\Users\bozoc\Documents\siscan\prototype`, retirar o prefixo `siscan-prototype` dos comandos. O alias `python` do Windows não foi necessário.

## Demonstração verificável

Artefato local `prototype/data/unit_groups_demo_20261116.json`, fora do Git, usa três unidades de classes inteiramente sintéticas. Mostra revisão 1 com `demo-1`/`demo-2`, revisão 2 com `demo-1`/`demo-3`, preparação dessa composição e revisão 3 arquivada. Consultas às revisões anteriores mantiveram seu conteúdo; `simulation_started=False` e nenhum recurso foi consumido.

Os checkpoints de código foram registrados em `7c685e6` (criação/revisão) e `0d357ee` (arquivamento/preparação). A documentação de entrega segue em registro posterior, sem alterar o significado dos dados.

## Limites e continuidade

Não há tela, API, autenticação, persistência, adaptação automática de todas as categorias reais ou integração com grupos no motor/mapa/relatório CPC. Preparar composição não declara aptidão física para confronto; `official_calculation_ready=False` e `simulation_started=False` são mantidos no resultado dessa operação.

Próxima integração precisa de contrato próprio para resolver membros em estados individuais, congelar versões, conferir permissões e aplicar somente decisões oficiais do instrutor. Cadastro de grupo não recomenda composição otimizada nem estima eficácia operacional real.

Os bancos, originais, recursos/relógio do exercício e os arquivos antigos `tasks/plan.md`/`tasks/todo.md` foram preservados. Não foram introduzidos dependências ou migrações. Os gates anteriores estão concluídos para esta fatia; não implicam aprovação dos recortes pendentes de `technical-catalog`.
