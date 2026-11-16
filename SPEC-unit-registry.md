# Spec: unit-registry — composição versionada de grupamentos

**Estado: Fase 1 aprovada pelo responsável em 2026-11-16, por “sim”.** Complemento de escopo de [89](docs/recovery/89_ESCOPO_GRUPAMENTOS_E_DADOS_DESCRITIVOS_CPC.md) e do [mapa de capacidades](CAPABILITY_MAP.md) previamente aprovado por “pode seguir”. Plano de Fase 2 aprovado posteriormente por “aprovado” em [tasks/unit-registry/plan.md](tasks/unit-registry/plan.md), local escolhido pelo responsável. Lista de Fase 3 proposta em [tasks/unit-registry/todo.md](tasks/unit-registry/todo.md), antes da implementação; preservar o trabalho aberto de `technical-catalog`.

## Objetivo

Permitir compor, consultar e revisar grupamentos diretos navais ou aéreos com unidades identificadas e disponíveis ao partido no contexto do exercício. Cada versão conserva membros e referências aos snapshots individuais, sem criar recursos, alterar meios ou sugerir composição otimizada de forças reais.

Usuários finais previstos: operador do próprio partido e instrutor no exercício. O primeiro recorte é um módulo de domínio em memória, verificável com fixtures controladas; não cria tela, rota HTTP, persistência ou autorização de usuário. Um consumidor futuro deverá fornecer contexto autenticado e disponibilidade conferida pelo backend.

Base: 08 (hierarquia/MPNL-001), 37 (modelo/configuração/unidade), 49 (identidade, partido e histórico), 51 (adjudicação por partido), 53 (autoridade para promoção), 71 (unidades/snapshots existentes), 80/81 (arbitragem e estado), 84–88 (ensaio CPC) e 89 (escopo aprovado).

## Premissas e recorte

1. Reutilizar IDs SISCAN de unidades, configurações e snapshots; ID DB3K identifica fonte, não unidade disponível ao partido.
2. Propor primeiro grupamentos diretos: lista de integrantes, sem grupos subordinados. Hierarquia completa e grupamentos conjuntos são recortes posteriores, sem mudança dos quatro níveis de 08.
3. Grupo naval admite classes/configurações navais diferentes; grupo aéreo admite referências aéreas diferentes. Neste recorte o domínio identifica o tipo do grupo, não avalia compatibilidade operacional ou eficácia.
4. “Esquadrilha” é designação operacional. O vínculo com os níveis aéreos provisórios do MPNL é opcional e não será inferido do nome. Não criar um quinto nível ou renomear os existentes.
5. Grupo referencia estado individual; não recebe HP, combustível ou armamento fictícios agregados. Hospedagem em base/porta-aviões pertence a `support-network`, não substitui o vínculo de composição.
6. Primeiro aceite com dados sintéticos explícitos. Referências reais permanecem descritivas e sujeitas aos escopos de aprovação vigentes; esse módulo não promove seus atributos.

## Contrato de identidade e versão

| Campo | Regra proposta |
|---|---|
| `schema_version` | `siscan-unit-group-01` |
| `group_id` | UUID próprio do grupo; não reaproveitar ID de plataforma |
| `exercise_id`, `team` | Contexto fornecido pelo backend; `AZUL` ou `VERMELHO`; nunca deduzido de um nome ou aceito como autorização do cliente |
| `designation` | Texto de 1–120 caracteres após remover espaços externos; não define doutrina ou capacidades |
| `domain` | `naval` ou `aereo` no primeiro recorte |
| `organization_label` | Designação operacional opcional, preservada sem conversão implícita de escalão |
| `mpnl_binding` | Opcional; quando informado, ramo/nível precisam corresponder a 08; vínculo aéreo não inferido de “esquadrilha” |
| `composition_revision` | Inteiro positivo, começa em 1; nova composição cria versão, sem editar a anterior |
| `active` | Verdadeiro na criação; arquivamento cria revisão inativa, preservando as referências históricas |
| `members` | Lista não vazia de referências individuais; cada `unit_id` aparece uma vez |
| `members[].unit_id` | Identidade opaca existente no contexto; respeitar representação original, sem substituir por nome/classe |
| `members[].snapshot_id`, `snapshot_sha256`, `configuration_version_id` | Referências obtidas do registro confiável da unidade; conservar os nomes já existentes em 71 |
| `inventory_snapshot_sha256` | Hash da visão de disponibilidade usada na conferência; evidência de entrada, não assinatura ou autorização |
| `composition_sha256` | Hash do conteúdo canônico da versão, com contexto e membros; não confundir com hash de arquivo DB3K |

O registro da versão deve ser imutável por contrato: conteúdo e listas retornados não podem permitir edição do armazenamento interno. A consulta histórica por revisão/hash deve retornar o conteúdo daquela revisão; nunca substituir silenciosamente pela mais recente.

## Fronteira dos provedores e operações propostas

O módulo recebe uma visão de unidades confiável, com identidade, contexto, domínio, configuração, snapshot e disponibilidade ao partido. A normalização da categoria existente para `naval`/`aereo` deve ser feita pelo adaptador de catálogo com evidência; categoria desconhecida gera diagnóstico, não classificação pelo nome.

`unit-registry` não passa a depender de `party-inventory`. O consumidor obtém desse provedor a disponibilidade e a fornece à composição. Ao preparar um ensaio, deve obter novamente uma visão atual, conferir a revisão da composição e congelar as entradas. Hash de inventário antigo não comprova disponibilidade atual.

Interfaces Python candidatas, a detalhar no plano após aprovação:

- `criar_grupamento(contexto, inventario, pedido)`: validar e criar grupo/revisão 1; retornar identidade, revisão e hash.
- `revisar_grupamento(contexto, inventario, pedido)`: exigir `expected_revision`; criar nova versão preservando a anterior.
- `consultar_grupamento(contexto, group_id, revision=None)`: consulta limitada ao contexto informado; revisão explícita preservada.
- `arquivar_grupamento(contexto, pedido)`: exigir `expected_revision`; criar revisão inativa e liberar a exclusividade direta dos integrantes, sem remover os meios ou suas referências históricas.
- `preparar_composicao(contexto, inventario, group_id, expected_revision)`: conferir disponibilidade atual e devolver snapshot de referências ou motivos de recusa. Não iniciar simulação.

Na criação, o pedido contém `command_id`, `designation`, `domain`, campos organizacionais opcionais e `member_unit_ids`. O domínio gera `group_id` e obtém as referências de snapshot do provedor; não aceita hashes/configurações autoafirmados pelo cliente. Revisão inclui `group_id`, `expected_revision` e substituição completa da composição/metadados. Arquivamento inclui apenas comando, grupo e revisão esperada. Rejeitar campos adicionais inesperados.

Contexto é uma entrada interna já verificada, não uma autenticação implementada por este módulo. Um campo `role='instructor'` ou `approved=true` em JSON não concede autoridade. A futura API deverá aplicar sessão, atribuição ao exercício, partido e CSRF antes de chamar o domínio. Neste recorte não existe endpoint para clientes externos.

## Invariantes de composição

- Todos os integrantes pertencem ao exercício/partido da composição e têm disponibilidade válida no inventário fornecido.
- Cada integrante possui snapshot/configuração existentes e hash coerente. Dado ausente ou divergente recusa a operação inteira.
- Repetir um membro no pedido é erro; não deduplicar silenciosamente.
- Proposta para esta primeira entrega: uma unidade integra diretamente apenas um grupamento ativo no mesmo exercício/partido. Versões históricas podem referenciá-la; ficam fora dessa exclusividade temporal. A regra não altera vínculos orgânicos/hospedagem.
- Mudança de designação, vínculo organizacional ou membros gera revisão nova. Não permitir grupo ativo vazio; arquivar o grupo para liberar todos os integrantes de uma vez, preservando histórico. Grupo arquivado não pode preparar ensaio; reabertura fica fora deste recorte.
- A ordem recebida dos membros não muda o hash da mesma composição: ordenar referências por `unit_id` para a representação canônica. Isso não cria ordem de atuação.
- Não criar/alocar unidades, transferir partido, mover meios, consumir recursos, editar snapshots ou adjudicar efeitos ao compor/revisar.

## Comandos e conflitos

Pedidos de criação/revisão/arquivamento incluem `command_id` UUID estável para reenvio da mesma intenção. A chave é vinculada ao contexto, operação e conteúdo canônico. Mesmo comando/contexto/conteúdo retorna o resultado anterior; conteúdo diferente com a mesma chave produz conflito. Conferir o contexto antes de consultar recibos, sem revelar grupos de outro partido.

O registro de comando e a nova versão são publicados juntos em memória após toda a validação. Uma falha não deve deixar grupo, revisão, exclusividade ou recibo parcial. Reiniciar o processo perde o registro em memória: não apresentar essa garantia como idempotência persistida ou recuperação oficial.

Erros locais propostos: `ValueError` para formato/domínio/dados obrigatórios; `PermissionError` para incompatibilidade de contexto/pertencimento; `GroupConflict(ValueError)` para revisão, comando ou disputa de integrante; grupo ausente no contexto resulta em erro de inexistência sem divulgar presença em outro contexto. Não importar exceções de `execution-core` para a camada de identidade, evitando dependência circular.

## Estrutura, tecnologia e estilo

Python 3.11+, biblioteca padrão. Preservar os módulos existentes. Arquivos candidatos: `siscan-prototype/unit_groups.py` e `siscan-prototype/check_unit_groups.py`; fixture sintética separada apenas se tornar os exemplos mais claros. Sem dependência nova ou DDL determinado por esta especificação.

Usar funções pequenas, type hints e estruturas retornadas sem referências mutáveis ao armazenamento. JSON usa `snake_case`, como os contratos atuais. Exemplo real da representação canônica em `engine_units.py`, a reutilizar como convenção, sem criar dependência circular de implementação:

```python
def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False)
```

Separar intenção do pedido, referências verificadas e resultado/versionamento. Não criar um framework de unidades ou reescrever as classes CPC existentes para cadastrar grupos.

## Comandos verificáveis

Partindo da raiz do repositório no PowerShell:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc --version
& $pythonCpc .\siscan-prototype\check_engine_units.py
& $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
git diff --check
```

Aceite futuro após implementação — o arquivo abaixo **ainda não existe**, não foi executado e não deve ser substituído por uma descoberta vazia de testes:

```powershell
& $pythonCpc .\siscan-prototype\check_unit_groups.py
```

Não há build, servidor, banco ou navegador a iniciar para esta fatia de domínio. Antes de eventual integração, aplicar os verificadores dos provedores afetados e uma especificação própria dos contratos HTTP/persistência.

## Estratégia de testes e critérios de aceite

Fixtures controladas isoladas, sem ler/escrever dados oficiais. Testes relevantes devem cobrir tanto aceite quanto recusa; não considerar validação de software como aprovação física.

| ID | Condição verificável |
|---|---|
| UG-01 | Criar grupo naval com referências de classes/configurações diferentes preserva todos os IDs e snapshots |
| UG-02 | Criar grupo aéreo com a designação “esquadrilha” não cria/renomeia nível MPNL |
| UG-03 | Unidade desconhecida, não disponível, do outro partido/exercício ou com domínio incompatível é recusada |
| UG-04 | Snapshot ausente, hash/configuração divergente ou categoria sem normalização demonstrada recusa o lote |
| UG-05 | Membro repetido no pedido ou disputa com outro grupo ativo não cria dupla contabilização |
| UG-06 | Revisão válida cria versão nova; histórico anterior e seus hashes permanecem intactos |
| UG-07 | Revisão esperada desatualizada é recusada; não substitui composição concorrente |
| UG-08 | Reenvio idêntico não duplica grupo/revisão; mesma chave com conteúdo diferente gera conflito |
| UG-09 | Reordenar membros sem mudar conteúdo preserva hash canônico; não altera prioridade de atuação |
| UG-10 | Edição de objeto retornado não altera versões armazenadas; falha não deixa publicação/recibo parcial |
| UG-11 | Preparar composição revalida inventário atual e não consome recurso, não cria meio e não inicia relógio |
| UG-12 | Consulta não atravessa contexto; comando/revisão de outro partido não é exposto |
| UG-13 | Combustível, munição, estado, configuração individual e bancos/originais não são modificados por operações de grupo |
| UG-14 | Dados sintéticos e referências descritivas não recebem aprovação real por pertencerem a um grupamento |
| UG-15 | Arquivamento cria versão inativa, libera exclusividade e preserva histórico; reenvio não duplica e grupo inativo não prepara ensaio |

## Limites de atuação

- **Sempre:** preservar 08/49/53, identidade e versões; validar contexto/provedores; dar motivos de recusa; testar regras e regressões afetadas antes de entregar código.
- **Revisar antes:** persistência/DDL, autenticação/API, hierarquia/subgrupos, grupos conjuntos, reabertura, indicadores coletivos ou novos escopos de dados reais.
- **Nunca:** editar originais, promover atributo por suposição, criar inventário pelo nome, calcular composição militar otimizada, alterar resultado oficial do instrutor ou reduzir verificações para aceitar lacunas.

Fora desta primeira entrega: sensor físico, previsão operacional de eficácia, confronto simultâneo de múltiplos grupos, cálculo de poder agregado, integração gráfica, exportação de grupos no relatório CPC e adjudicação oficial. Esses consumidores usarão o contrato de composição congelada após especificação própria.

## Questões para revisão

1. **Confirmado pela aprovação:** primeira entrega de grupamentos diretos em memória, navais/aéreos e sem persistência/API.
2. **Confirmado pela aprovação:** exclusividade de vínculo direto ativo por exercício/partido, sem alteração de hierarquia orgânica ou hospedagem, com liberação por revisão/arquivamento.
3. **Limite confirmado:** vínculo MPNL de “esquadrilha” permanece não inferido; cadastrar a designação não decide essa correspondência futura.

## Gate de conclusão

Gates de Fase 1 e do plano de Fase 2 satisfeitos por aprovações distintas. Lista detalhada de Fase 3 proposta para revisão; implementação não iniciada. Aprovações anteriores não aprovam automaticamente tarefas ou código.
