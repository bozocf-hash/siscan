# Spec: unit-registry — composição versionada de grupamentos

**Incremento autorizado e entregue em 2026-11-24 — [129](docs/recovery/129_CATALOGO_PARA_PLANEJAMENTO_E_GRUPAMENTOS.md):** exemplares de planejamento derivados da compilação podem integrar grupos navais/aéreos sem prontidão física. Provedor `planning_catalog` conserva hash/tabela/ID e snapshot imutável com prontidão falsa; adjudicação ao partido permanece necessária. Grupos continuam em memória; instâncias/posições são persistidas. Essa extensão amplia as referências descritivas aceitas na composição e não promove atributos reais para cálculo ou substitui a arbitragem.

**Estado: especificação aprovada e recorte implementado em 2026-11-16.** Escopo, especificação, plano e tarefas foram aprovados em interações distintas; a lista de Fase 3 recebeu “sim”. [Plano](tasks/unit-registry/plan.md) e [tarefas](tasks/unit-registry/todo.md) preservam o trabalho aberto de `technical-catalog`. Entrega e evidências em [93](docs/recovery/93_ENTREGA_GRUPAMENTOS_EM_MEMORIA.md), sem API/banco ou integração física.

**Recorte 2 implementado e verificado em 2026-11-16:** especificação, plano e tarefas aprovados; entrega em [102](docs/recovery/102_ENTREGA_GRUPAMENTOS_NO_MAPA.md). Composição/consulta gráfica no mapa ATLANTICADOR já definido, sem confronto integrado. Roteiro do instrutor em [103](docs/recovery/103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md). Entrega 93 preservada.

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

Gates de escopo, especificação, plano e tarefas satisfeitos por aprovações distintas. Implementação deste recorte verificada em 93, sem ampliar as autorizações para integração/API, persistência ou modelos físicos.

## Recorte 2 — Compor e consultar no mapa existente

### Objetivo e premissas propostas

Permitir que operador do próprio partido e instrutor criem, consultem e arquivem grupos diretos no **mesmo mapa ATLANTICADOR já integrado ao SISCAN**. A seleção na lista realça os integrantes que já possuem posição; não move, duplica ou cria meios. A criação/arquivamento fecha um fluxo utilizável sem depender de grupos fictícios pré-carregados ou tornar impossível liberar vínculos pela interface.

Manter o mapa, suas camadas e ferramentas de plotagem/reposicionamento. Usar o painel lateral existente, com uma aba “Grupamentos”; uma única área ativa, sem janela sobreposta. Revisão da composição pela tela, persistência, CPC temporal, replay e confirmação oficial ficam fora desta extensão. Para recompor neste recorte, arquivar e criar outro grupo, preservando os históricos no processo.

Referências: entrega de identidade/snapshots em 71, mapa 76–78, composição 93, concepção 97 e dossiê 98. A extensão pertence a `unit-registry`, consumindo permissões/inventário/posições existentes; não cria um segundo mapa ou módulo de confronto. Dossiê de 98 continua independente: nenhum botão desta tela inicia combate.

### Lacunas confirmadas na inspeção

`map_units.listing` usa `assets.id` e posições de planejamento. `engine_units.list_units` possui o vínculo explícito `unit_id` → `asset_id`, snapshot/configuração/hash e alocação. O servidor ainda não integra `RegistroGrupamentos`; não há lista HTTP de grupos. O campo `group_name` das submissões didáticas não é um grupo versionado: não convertê-lo automaticamente.

O cadastro atual de instâncias do motor é sintético; `prepare_units` identifica a configuração aérea controlada. Não há evidência de instâncias/snapshots elegíveis para todo meio real já plotável. Primeira integração aceita apenas instâncias efetivamente existentes e validadas: referência do catálogo ou categoria textual não substitui snapshot/domínio.

### Contrato funcional e identidade

O backend fornece uma visão de grupos e meios elegíveis para o exercício/partido autorizado, ligando cada integrante por `unit_id` e `asset_id`. A ligação deve corresponder ao mesmo exercício/partido e à adjudicação ativa, com unicidade; não relacionar por nome, código parecido ou ID DB3K.

Para entrada do registro, o adaptador acrescenta domínio/evidência demonstrados pelo provedor, sem editar snapshot ou seu hash. A regra inicial pode reconhecer explicitamente a configuração sintética criada por `engine_units.prepare_units`, com referência à origem controlada, não por procurar a palavra “aéreo” no nome. Outra categoria/configuração sem mapeamento demonstrado aparece pendente e não pode criar grupo até integração própria; isso não impede sua plotagem atual.

Na criação, cliente envia apenas partido solicitado, comando, designação, domínio e IDs de unidades selecionadas. Exercício e identidade/permissões vêm da sessão no servidor. O servidor consulta inventário atual e executa o contrato de 93, preservando reenvio idêntico, conflitos e exclusividade. Nenhum snapshot, aprovação ou vínculo `asset_id` alegado no pedido substitui o provedor.

Na consulta, cada membro informa identidade/nome/código do cadastro, referência de composição, posição/revisão quando disponível e eventual impedimento. Recurso ou estado operativo ausente continua “Não informado”; esta fatia não implementa as três barras nem calcula agregações. Grupo existente que perder adjudicação/snapshot deve ser exibido como pendente de conferência, sem usar seu recibo histórico como disponibilidade atual e sem revelar dados revogados de membros ao operador.

Arquivar exige ID do grupo, comando e revisão esperada, libera vínculos conforme 93 e preserva histórico em memória. Não apaga unidades, posições ou recursos. Operações de escrita exigem exercício aberto e proteção CSRF existente; leitura pode consultar grupos arquivados somente no contexto autorizado.

### Interfaces HTTP propostas

| Operação | Contrato pretendido |
|---|---|
| `GET /api/map-unit-groups?team=AZUL` | Grupos do partido autorizado, projeção dos integrantes visíveis, unidades elegíveis e motivos de pendência; não devolver inventário adversário |
| `POST /api/map-unit-groups` | Criar com `{team, command_id, designation, domain, member_unit_ids}`; corpo estrito, inventário resolvido no backend |
| `POST /api/map-unit-groups/{group_id}/archive` | Arquivar com `{team, command_id, expected_revision}`; corpo/URL conferidos e proteção de revisão |

Sessão ausente usa o comportamento de autenticação existente; acesso negado 403; formato inválido 400; grupo ausente no contexto 404; conflito de revisão/intenção/vínculo 409. Não converter erro de rede/servidor em lista vazia. Um único registro por processo do servidor atende suas threads, preservando o lock existente; não usar um registro por requisição ou por aba.

Esta extensão mantém armazenamento em memória. A tela deve exibir aviso persistente de que composições/histórico se perdem ao reiniciar o servidor; não anunciar salvamento durável. Reinício deve devolver uma lista vazia real e clara, sem reconstruir grupos pelo nome, pela lista de submissões ou pelo último dossiê exportado.

### Interações no mapa

Selecionar um grupo realça todos os integrantes plotados por meio do índice existente de marcadores, sem desenhar marcadores duplicados. Lista indica “Sem posição” quando a ligação existe e a posição falta, e “Vínculo indisponível” quando não pode ser resolvida/autorizada. Não criar coordenada em (0, 0), centroide físico ou fallback que oculte falha de identidade.

Oferecer “Enquadrar integrantes” explicitamente, habilitado quando existir posição válida; evitar mover zoom automaticamente a cada atualização. Selecionar membro abre sua consulta no painel sem alterar sua posição. Criar grupo é ação separada de inserir/reposicionar meios: modo de seleção para grupo não deve disparar comando de plotagem.

Ao trocar partido/perspectiva autorizada, limpar a seleção e o conteúdo do grupo anterior antes de carregar o novo; resposta atrasada não deve restaurar seleção/conteúdo de outro contexto. Desadjudicação ou conflito pede atualização explícita, sem inclusão silenciosa ou remoção de meio do grupo.

Alternativa por lista/teclado, foco visível, rótulos textuais, estados de carregamento/vazio/erro e confirmação de arquivamento. Nomes/designações são texto, nunca HTML executável. Não depender apenas das cores azul/vermelho ou do realce para comunicar seleção/partido. Reutilizar tecnologia atual; sem dependência gráfica nova ou alteração do ZIP original.

### Arquivos e verificações futuras

Backend: adaptador de grupos/identidades e rotas no servidor; nova consulta pública contextual no registro, caso necessária, sem acessar `_state`/`_lock` de fora. Frontend: adaptador `static/atlantic-bridge.mjs` e eventual módulo específico importado por ele, preservando o mapa preparado. Implementados `map_groups.py`, `check_map_groups.py`, `check_map_groups_http.py`, `static/map-groups.mjs` e `check_map_groups.mjs`, conforme 102.

Padrão Python/JavaScript existente, type hints nas novas fronteiras Python, módulos JS nativos e manipulação por `textContent`. Testes Python com SQLite de teste isolado e registro real; testes de seleção com módulos nativos JS; teste de integração HTTP com sessão/CSRF; verificação de navegador real antes de declarar interface entregue. Não usar a instância/dados do usuário para mover, criar ou arquivar grupos de teste.

Comandos atuais de regressão, partindo de `siscan-prototype`:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_unit_groups.py
& $pythonCpc check_map_units.py
node check_map_visuals.mjs
```

Verificadores desta extensão e regressões afetadas foram executados conforme 102: 53 testes nomeados e dois verificadores assertivos passaram. A interface foi inspecionada no navegador real, em base temporária. Sem build adicional ou reextração do ATLANTICADOR. Não declarar validação visual por leitura do código.

### Critérios de aceite da extensão

| ID | Resultado verificável |
|---|---|
| GM-01 | Aba de grupamentos funciona no mapa existente, preservando camadas, plotagem, reposicionamento e hover |
| GM-02 | Vínculo unit_id/asset_id/contexto/adjudicação é explícito; nome parecido não une unidades |
| GM-03 | Meio sem snapshot/domínio demonstrado continua plotável, mas fica inelegível para criar grupo com motivo legível |
| GM-04 | Operador consulta/escreve somente no próprio partido; instrutor autorizado escolhe partido; resposta HTTP não contém dados adversários indevidos |
| GM-05 | Criar grupo mantém reenvio/conflitos e não cria meio, posição, combustível ou munição |
| GM-06 | Seleção realça somente marcadores existentes; sem posição/vínculo não gera marcador ou coordenada fictícios |
| GM-07 | Arquivar exige revisão esperada, libera vínculos e preserva histórico sem remover meios/posições |
| GM-08 | Troca de contexto e resposta atrasada não restauram conteúdo/seleção anterior; vínculo revogado não expõe dados ao operador |
| GM-09 | Estados de vazio/erro/carregamento são distintos; perda do registro após reinício é explicitada sem alegar durabilidade |
| GM-10 | Fluxo por teclado, nomes seguros, foco e painel único conferidos no navegador; sem sobreposição ou perda de ferramentas |
| GM-11 | Consumos, motor, dossiê 98 e resultados oficiais não são modificados por consultar/compor no mapa |
| GM-12 | Testes isolados verificam sessão/CSRF, concorrência/reenvio e preservação; nenhuma ação de teste altera meios do usuário |

### Limites e gate desta extensão

Não inclui persistência/DDL, migração de todos os meios reais para instâncias, revisão gráfica da composição, execução/replay, eficácia militar, indicadores coletivos ou publicação de resultados. A falta dessas integrações deve aparecer com clareza; não apresentar a tela como motor de confronto pronto.

Gates de especificação, plano e tarefas do Recorte 2 satisfeitos por aprovações distintas. GMAP-01–09 concluídas conforme [102](docs/recovery/102_ENTREGA_GRUPAMENTOS_NO_MAPA.md). Não reabrir os gates desta fatia nem das entregas 93/98. Executar confronto, selecionar par e publicar efeitos na tela ainda depende de recorte próprio; o roteiro 103 distingue etapas atuais e futuras.
