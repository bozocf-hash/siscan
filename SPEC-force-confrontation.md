# Spec: force-confrontation — preparação didática de grupamentos

**Atualização de 2026-11-17 — Recorte 3 aprovado por “sim”:** [113](docs/recovery/113_ESPECIFICACAO_JULGAMENTO_DIDATICO_NO_MAPA.md) especifica julgamento/prévia/confirmação/consulta no mapa, consumindo o estado durável entregue em 112. Recortes 1/2 permanecem concluídos. [Plano de Fase 2](tasks/force-confrontation/julgamento/plan.md) aprovado por “sim”; [tarefas de Fase 3](tasks/force-confrontation/julgamento/todo.md) propostas conforme [115](docs/recovery/115_TAREFAS_JULGAMENTO_DIDATICO_NO_MAPA.md), antes do código; sem migração principal autorizada nesta etapa.

**Data: 2026-11-16. Estado: especificação, plano e tarefas aprovados; recorte implementado e verificado em [98](docs/recovery/98_ENTREGA_PREPARACAO_CPC_GRUPAMENTOS.md).** A lista de Fase 3 foi aprovada por “siga”. O registro entregue em 93 permanece preservado. Esta entrega acrescenta o consumidor de composições em memória, sem execução ou interface de confronto. Mantido o mapa ATLANTICADOR já definido.

**Extensão de 2026-11-17:** escopo/ordem de [104](docs/recovery/104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md) aprovados por “si”. Recorte 2 abaixo especifica seleção do par e conferência no mapa; Fase 1 aprovada por “siga”; [plano de Fase 2](tasks/force-confrontation/mapa/plan.md) aprovado por “sim”; [tarefas de Fase 3](tasks/force-confrontation/mapa/todo.md) aprovadas por “sim” e concluídas conforme [108](docs/recovery/108_ENTREGA_PAR_CPC_NO_MAPA.md). Entrega 98 preservada; sem publicação de efeitos oficiais nesta extensão.

## Objetivo e premissas

Preparar um dossiê inicial de dois grupamentos, um AZUL e um VERMELHO, no mesmo exercício, para conferência didática pelo instrutor. Cada integrante mantém identidade, versão de configuração, snapshot e recursos próprios. O sucesso desta fatia é uma preparação rastreável e reproduzível, sem executar combate ou decidir o resultado.

Premissas propostas: continuar primeiro no backend; usar registro e inventário internos confiáveis; aceitar grupos diretos navais/aéreos, inclusive um de cada domínio; preservar os quatro níveis MPNL de 08, APR de 49 e autoridade de promoção de 53. O nome “esquadrilha” não determina escalão. Acesso aos dois partidos será exclusivo do contexto de instrutor autorizado pelo provedor; um operador não ganha acesso à composição inimiga.

Referências: [mapa de capacidades](CAPABILITY_MAP.md), [contrato de composição](SPEC-unit-registry.md), documentos 80–83 para requisitos/conceitos CPC e 84–88 para o ensaio sintético existente. A implementação atual resolve ações de unidades individuais; não há execução de grupamentos integrada. Nenhum parâmetro real de eficácia será derivado do catálogo nesta fatia.

## Fronteira e comportamento

Entrada interna: contexto de instrutor previamente autorizado para o exercício; registro de grupamentos; visão consistente de inventário por partido; seleção explícita de `group_id` e `expected_revision` para AZUL e VERMELHO. O adaptador não aceita um papel informado pelo cliente como prova de autorização. Esta entrega não cria autenticação ou endpoint: o provedor é a fronteira de confiança.

Preparação deve:

1. Conferir a autorização fornecida pelo provedor antes de consultar os dois partidos.
2. Reutilizar as operações públicas do registro para exigir grupos ativos, versões esperadas e disponibilidade atual. Não acessar ou modificar seus atributos privados.
3. Resolver cada referência no inventário fornecido, conferindo identidade, exercício, partido, configuração, conteúdo e SHA-256 do snapshot. Não completar campo ausente com dado de outro modelo/configuração.
4. Copiar integralmente os snapshots selecionados para o dossiê, mantendo os dados originais e suas classificações. Recurso desconhecido permanece desconhecido; nenhum valor é substituído por zero.
5. Conferir novamente as revisões selecionadas antes de devolver o resultado. Se uma revisão/arquivamento observado durante a preparação invalidar a seleção, recusar o dossiê inteiro. O provedor deve fornecer uma visão consistente e isolada do inventário; o módulo não pode garantir atomicidade entre fontes externas mutáveis.
6. Devolver apenas um dossiê completo. Falha em qualquer partido/integrante não retorna preparação parcial nem altera grupo, recibo, inventário ou recurso.

Uma preparação é um registro da vista conferida, não uma reserva de disponibilidade nem autorização para execução futura. Outro consumidor deverá revalidar antes de agir. Não acrescentar política de alvos, iniciativa, detecção, interceptação, emprego de armas ou otimização de força.

## Contrato de saída

JSON serializável, independente das entradas, com:

| Campo | Significado |
|---|---|
| `schema_version` | `siscan-cpc-group-preparation-01` |
| `exercise_id` | Exercício conferido pelo provedor |
| `parties` | Dois registros, AZUL e VERMELHO, em ordem canônica |
| Composição por partido | ID, revisão, hash da composição e manifesto do inventário devolvidos pelo registro |
| Integrantes por partido | Referências originais e conteúdo completo do snapshot de cada unidade, ordenados por ID |
| `preparation_sha256` | SHA-256 do conteúdo canônico, sem incluir o próprio hash |
| `status` | `requires_instructor_review` |
| `simulation_started` | Sempre `false` |
| `official_calculation_ready` | Sempre `false` para a preparação |

O indicador global falso não sobrescreve a classificação/validação original dos snapshots. Hashes identificam conteúdo, não comprovam autenticidade ou validade física. Campos desconhecidos no pedido são recusados; conteúdo adicional dos snapshots é preservado como dado, sem executá-lo ou interpretá-lo como instrução.

Mesmas entradas produzem o mesmo conteúdo/hash: não incluir data de parede, UUID aleatório ou ordem de inserção no cálculo. Novas versões/snapshots selecionados produzem dossiê diferente. Não somar combustível, munições de tipos diferentes, pontos de vida ou desempenho para calcular um poder agregado.

Falhas de entrada usam `ValueError`; ausência de grupo no contexto usa `KeyError` sem revelar outro contexto; revisão/conteúdo incompatível usa `GroupConflict`; contexto de instrutor não autorizado usa `PermissionError`. Não converter falhas em preparação válida com listas vazias.

## Estrutura e estilo

Python 3.11+, biblioteca padrão, mantendo a estrutura existente. Implementação proposta em `siscan-prototype/cpc_group_preparation.py`, verificador em `siscan-prototype/check_cpc_group_preparation.py`. Não duplicar o registro, renomear IDs ou importar fixtures de testes no módulo de produção. A função pública implementada é `preparar_dossie_grupamentos`, com assinatura detalhada no plano e em 98.

Seguir funções com type hints e docstrings como no código atual:

```python
def conferir_contexto(exercise_id: int) -> None:
    """Recusa identidade inválida antes de consultar composições."""
    if type(exercise_id) is not int or exercise_id <= 0:
        raise ValueError("Exercício inválido.")
```

Este trecho ilustra estilo; não é implementação nem exige um novo helper.

## Comandos e estratégia de verificação

Partindo da raiz do repositório, após a futura implementação:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_cpc_group_preparation.py
& $pythonCpc .\siscan-prototype\check_unit_groups.py
& $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
git diff --check
```

O verificador foi implementado: 21 testes focados passaram, além das regressões descritas em 98. Na entrega canônica, os fontes ficam em `C:\Users\bozoc\Documents\siscan\prototype`. Não há build, servidor ou navegador a iniciar para este módulo em memória.

Usar `unittest`, fixtures inteiramente sintéticas e testes positivos/negativos. Exercitar a fronteira com o registro real em memória, sem banco real. Verificar preservação por comparação antes/depois, sem testes que só reproduzam funções auxiliares. Não repetir baterias por edições exclusivamente documentais.

## Critérios de aceite

| ID | Resultado verificável |
|---|---|
| GP-01 | Preparar grupo AZUL e VERMELHO do mesmo exercício, preservando cada ID e referência |
| GP-02 | Aceitar naval/naval, aéreo/aéreo e naval/aéreo sem inferir MPNL ou compatibilidade de combate |
| GP-03 | Recusar contexto sem autorização do provedor antes de consultar os partidos |
| GP-04 | Recusar grupo de outro contexto, arquivado ou com revisão esperada desatualizada |
| GP-05 | Recusar integrante indisponível, ausente ou com snapshot/configuração/hash divergente |
| GP-06 | Alteração de revisão observada durante a preparação recusa o resultado inteiro |
| GP-07 | Falha no segundo partido não altera nem publica preparação parcial do primeiro |
| GP-08 | Alterar o retorno não altera entradas ou registro; alterar entradas depois não altera o dossiê retornado |
| GP-09 | Ordem de mapas/membros não altera hash; mudança efetiva de versão/snapshot altera o conteúdo identificado |
| GP-10 | Recursos, origens e estados desconhecidos dos snapshots são preservados; sem agregação ou promoção de dados |
| GP-11 | Nenhuma preparação move unidade, gasta combustível/munição, avança relógio ou invoca resolução de combate |
| GP-12 | Saída informa revisão do instrutor pendente e simulação não iniciada; autoridade oficial continua externa |

## Limites e questões para revisão

- Sempre preservar contratos de provedores, histórico, classificações de dados e decisões 08/49/53. Testar recusas e regressões afetadas antes de entregar código.
- Exigir revisão própria para persistência/DDL, HTTP/autenticação, integração gráfica, publicação de efeitos, execução temporal de grupamentos ou mudança dos contratos aprovados.
- Nunca modificar DB3K/originais, sugerir composição otimizada, derivar eficácia operacional real ou substituir a decisão do instrutor.

A proposta não inclui execução do confronto, exportador novo, gravador durável, cálculo agregado ou nova tela. A preparação rastreável das duas composições foi aprovada e entregue; a aprovação desta fatia não amplia automaticamente o escopo para execução ou publicação de efeitos.

## Conclusão

Gates de especificação, plano e tarefas satisfeitos por aprovações distintas. Implementação verificada em [98](docs/recovery/98_ENTREGA_PREPARACAO_CPC_GRUPAMENTOS.md); não reabrir os gates desta fatia. Novas integrações gráficas/execução/persistência seguem escopo próprio. A concepção de 97 mantém o mapa existente.

## Recorte 2 — Selecionar o par e conferir no mapa

### Objetivo e premissas

O instrutor atribuído ao exercício seleciona um grupamento AZUL e um VERMELHO, confere integrantes/posições/referências e obtém a preparação de 98 pela interface do mesmo mapa ATLANTICADOR. Esta é a primeira etapa da ordem aprovada em 104; julgamento, confirmação e aplicação oficial dependem das próximas especificações de estado/adjudicação durável.

Usar grupos efetivamente cadastrados na instância e o provedor autorizado de 102. Não pré-carregar forças fictícias, reconstruir grupos por nome ou importar a demonstração de 98. Elegibilidade continua limitada às instâncias/snapshots/domínios demonstrados; grupos em memória não são duráveis.

Operadores continuam compondo/consultando o próprio partido. A visão simultânea desta preparação é exclusiva do instrutor autorizado; não cria regra de contato/detecção ou acesso livre ao inimigo. Preservar identidade, quatro níveis MPNL, autoridade de dados e resultado oficial do instrutor, conforme 08/49/53/80/81.

### Fluxo de uso

1. Instrutor abre uma área CPC no painel existente, com seletores identificados por partido; uma única área lateral ativa e o mesmo mapa/camadas definidos.
2. Backend lista grupos/revisões e impedimentos. Grupo arquivado, integrante revogado, snapshot alterado ou domínio não demonstrado não prepara sem correção explícita; não editar composição para fazê-la caber no pedido.
3. Escolher ambos os grupos e acionar **Preparar confronto**. A tela explica que essa ação confere os dados, sem executar combate ou aplicar resultados.
4. Servidor usa `preparar_dossie_grupamentos` e associa vista autorizada das posições de planejamento. Devolve projeção de conferência, sem inventários completos/snapshots brutos desnecessários ao navegador.
5. O mesmo mapa mostra as duas forças selecionadas. Lista/ficha informa integrantes, nome/código, revisão, posição e pendências; enquadramento é ação explícita, sem deslocar meios.
6. Alteração de seleção, atualização das fontes ou troca de exercício invalida a preparação visual anterior. Sair restaura o modo/perspectiva autorizado anterior, sem gravar efeitos.

Não incluir controles funcionais de julgamento, execução ou confirmação nesta fatia. Indicar os próximos passos como ainda não disponíveis, sem confirmação simulada ou mensagem de confronto concluído.

### Entrada e HTTP

| Interface proposta | Contrato |
|---|---|
| `GET /api/cpc/groups` | Grupos AZUL/VERMELHO contextualizados, revisões e elegibilidade; sem preparar/executar |
| `POST /api/cpc/preparations` | Corpo estrito `{AZUL: {group_id, expected_revision}, VERMELHO: {group_id, expected_revision}}`; retorna conferência do par |

As duas interfaces são exclusivas do instrutor participante. Exercício/versão de cenário, papel e identidade vêm da sessão/participação no servidor. Cliente não envia exercício como autoridade, autorizador, snapshot, aprovação, regra de combate ou posição para substituir o provedor. POST exige CSRF. Preparação é leitura/conferência sem publicação: não introduzir recibo ou `command_id` fictício.

Autorizar antes de ler ambos os partidos. Usar 401 para sessão ausente, 403 para acesso negado, 400 para formato inválido, 404 para grupo ausente no contexto, 409 para referências/revisões incompatíveis e 503 para fonte/integridade indisponível. Erro não vira lista vazia ou preparação parcial válida. Exercício encerrado permite informar a situação, mas recusa nova preparação.

Usar operações públicas dos provedores; não acessar `_state`/`_lock` do registro ou chamar o próprio HTTP para resolver dados internos. Enviar esse POST não confirma efeito algum.

### Dossiê, posições e atualização

Preservar o contrato/hash de `siscan-cpc-group-preparation-01`: ele não contém posição geográfica. A nova projeção tem `schema_version=siscan-cpc-map-preparation-01`, exercício/versão de cenário conferidos, referência/hash do dossiê, grupos/revisões e integrantes selecionados. Manifesto geográfico registra `unit_id`, `asset_id`, partido, latitude/longitude quando existentes e `position_revision`.

Ausência de posição permanece `null`/“Sem posição”; não usar (0,0), centroide ou base presumida. Hash próprio da vista gráfica cobre o conteúdo canônico utilizado, excluindo o próprio hash. Nova posição altera o manifesto/vista, sem alterar o dossiê técnico se snapshots/composições permanecerem iguais. Unidade não participante não entra no manifesto; não usar horário/UUID aleatório para forçar diferenças.

Posições são de planejamento, não trajetórias/distâncias táticas. Não converter automaticamente latitude/longitude no plano local sintético do CPC. Snapshot inicial também não é saldo logístico atual: eventual recurso exibido exige fonte/unidade/referência temporal; ausência de fonte atual aparece não informada, sem copiar o saldo inicial como atual.

Revisões de grupo/posição observadas como alteradas durante a captura recusam o lote. A vista conferida e seus limites devem ser identificados: memória e SQL não constituem transação distribuída ou reserva de disponibilidade. Futura execução/decisão exige revalidar seus provedores. Conferência estrutural não é aptidão física para combate.

Saída: `status=requires_instructor_review`, `simulation_started=false`, `official_calculation_ready=false`, `official_effects_applied=false`. Sem consumo, relógio, movimento, avarias ou decisão oficial.

### Visualização e interação

Mostrar as duas forças com identificação textual de partido e símbolos/contornos distinguíveis sem depender só de cor. Reutilizar mapa e simbologia existentes. Na vista do par, ocultar/substituir apenas a camada de meios de planejamento para evitar duplicidade do mesmo asset; não modificar camadas originais ou desenhar outro mapa.

Conferência não permite plotar/reposicionar, selecionar área para gravar posição ou editar integrantes pelo marcador. Cancelar movimentação/área pendentes ao entrar; restaurar arraste/perspectiva coerentes ao sair e recarregar a vista autorizada atual, sem ressuscitar dados revogados. Meios sem posição ficam na lista sem marcador.

Clique no integrante abre conferência no painel, com referências técnicas detalhadas em expansão. Não inventar foto, estado operativo, munição, barra de poder ou probabilidade de vitória. Seleção não é ordem de ataque.

Distinguir carga/vazio/erro/conflito. Respostas atrasadas não restauram par de contexto anterior nem sobrescrevem seleção posterior. Sem painéis sobrepostos; foco/teclado, rótulos e alternativa pela lista. Testes de tela estreita não devem deixar viewport forçado no navegador do usuário.

### Estrutura, estilo e verificação

Python padrão e JS nativo; reaproveitar `cpc_group_preparation.py`, `map_groups.py`, `app.py` e adaptador do mapa. Plano fechará módulos/verificadores novos. Sem dependência, DDL ou alteração de originais. Não inserir comparação de poderes no provedor de identidade.

Seguir contratos/type hints/docstrings e renderização por texto, por exemplo:

```python
def conferir_revisao(actual: int, expected: int) -> None:
    """Recusa uma referência observada como desatualizada."""
    if actual != expected:
        raise GroupConflict("Atualize a composição antes de preparar o par.")
```

É exemplo de estilo, não implementação ou obrigação de criar helper. JS mantém seleção distinta dos comandos de plotagem.

Verificadores futuros: `unittest` de provedor/HTTP em banco/cookie/porta isolados; JS de seleção/respostas fora de ordem; navegador real com cópia do mapa para vista simultânea, teclado, tela estreita e retorno ao planejamento. Comparar posições, recursos, execuções e estado oficial antes/depois, inclusive nas recusas.

Regressões existentes, somente após implementar mudanças pertinentes, partindo de `prototype`:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_cpc_group_preparation.py
& $pythonCpc check_map_groups.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_map_units.py
node check_map_groups.mjs
node check_map_visuals.mjs
```

Comandos focados novos serão definidos no plano; verificadores da extensão ainda não existem e nenhum teste foi executado nesta fase documental. Não usar descoberta vazia ou leitura de código como prova visual. Testes não reiniciam a instância em uso ou descartam seus grupos; publicação e atualização do servidor ativo são fatos separados.

### Critérios de aceite

| ID | Resultado verificável |
|---|---|
| CP-01 | Instrutor participante consulta ambos os partidos; operador/não participante é recusado antes da leitura |
| CP-02 | Seleção exige grupo AZUL e VERMELHO, IDs/revisões explícitos no contexto atual |
| CP-03 | Preparação reutiliza 98 e recusa arquivo, snapshot/revisão/identidade/adjudicação incompatíveis sem resultado parcial |
| CP-04 | Nome/posição vêm de vínculo autorizado; ausência não inventa coordenada, meio ou fonte |
| CP-05 | Hash técnico e manifesto geográfico separados; posição nova altera somente o conteúdo correspondente |
| CP-06 | Mudança observada gera conflito; atualizações futuras exigem nova preparação, sem reserva pelo hash |
| CP-07 | Duas forças no mesmo mapa, sem marcadores duplicados; integrantes sem posição na lista |
| CP-08 | Conferência cancela movimentos pendentes, não grava plotagem e restaura a vista autorizada atual ao sair |
| CP-09 | Seleção/contexto novos e respostas atrasadas não restauram par antigo ou dados indevidos |
| CP-10 | Situação inicial distingue snapshot, planejamento e estado atual; desconhecidos não viram zero/100% |
| CP-11 | Interface não alega combate executado/resultado oficial; recursos, relógio e avarias permanecem intactos |
| CP-12 | Navegador/teclado/tela estreita em dados isolados, com sessão/CSRF/rotas e regressões afetadas passando |

### Limites e gate

- Sempre preservar identidade/revisão/evidência/autorização e ausência de efeitos pela preparação; informar disponibilidade temporária e testar recusas.
- Exigir contrato próprio antes de persistência/DDL, impactos propostos, decisão/aplicação oficial, posições temporais/consumo, exposição a operadores ou modelo automático.
- Nunca modificar DB3K/originais, promover dado por estar no grupo, calcular composição otimizada ou publicar cálculo militar automaticamente como resultado oficial.

Escopo/ordem de 104 aprovados por “si”. Fase 1 deste Recorte 2 aprovada por “siga”; [plano de Fase 2](tasks/force-confrontation/mapa/plan.md) aprovado por “sim”; [lista de Fase 3](tasks/force-confrontation/mapa/todo.md) aprovada por “sim” e concluída em [108](docs/recovery/108_ENTREGA_PAR_CPC_NO_MAPA.md). Seleção/conferência do par implementada e verificada; julgamento, decisão e efeitos continuam explicitamente pendentes até suas entregas próprias.

## Recorte 3 — Julgamento didático, confirmação e estado no mapa

**2026-11-17. Fase 1 e plano de Fase 2 aprovados por “sim”; tarefas de Fase 3 propostas em 115.** Continuidade solicitada por “pode seguir” após [112](docs/recovery/112_ENTREGA_ESTADO_E_ADJUDICACAO_DURAVEL.md). Corresponde à etapa 3 já delimitada em 104; mantém os IDs `force-confrontation`, `operational-state` e `execution-core`, sem um segundo publicador de efeitos.

### Objetivo, premissas e fronteira

O instrutor participante deve percorrer no mesmo mapa ATLANTICADOR: selecionar o par → conferir estado inicial → informar julgamento didático → visualizar antes/depois → registrar/revisar proposta → confirmar ou rejeitar → consultar estado confirmado e histórico. A prévia nunca é estado oficial; confirmar exige ação explícita posterior ao registro da proposta.

Premissas propostas: reutilizar sessão/CSRF, painel/camada de consulta de 108, armazenamento e comandos de 112, Python padrão e JS nativo. Configurações elegíveis continuam limitadas às identidades/domínios demonstrados. A entrega gráfica será verificada primeiro em banco/porta/cookie isolados com migração explícita do harness; isso não habilita automaticamente o principal em 8787.

Não incluir cálculo automático de confronto, detecção, consumo, deslocamento, relógio, trajetória, emprego de armas, novas regras de prontidão ou expansão de parâmetros Command. Não criar índice da força, estimativa de vitória ou perdas presumidas. O instrutor informa efeitos didáticos; a interface não os calcula por poder de combate.

### Fluxo e controles

1. Após preparar o par, **Abrir julgamento didático** obtém do servidor estados oficiais, revisões próprias e referências das unidades selecionadas. Estado não avaliado permanece explícito; falha/schema indisponível não vira 100%, zero ou lista vazia.
2. No painel existente, o instrutor escolhe os meios afetados, informa alterações e justificativa. Não é necessário alterar todos os integrantes; meio omitido é preservado. Índice aceita 0–100, campo omitido preserva e ação explícita **Retirar avaliação** produz `null`; campo vazio não vira zero. Perda oferece preservar/declaração explícita, sem inferir destruição pelo índice.
3. **Conferir prévia** mostra por meio identificação, revisão de origem, estado confirmado anterior e proposta de estado posterior. A prévia é identificada como didática e não consome recursos ou publica efeito. Ela não substitui uma proposta durável.
4. **Registrar proposta** salva conteúdo/referências e devolve ID, revisão e hash. Ajustar cria nova revisão pela operação **Salvar revisão**; não altera registros anteriores. Confirmação permanece vinculada exatamente à revisão exibida, sem salvar ajustes silenciosamente ao confirmar.
5. **Confirmar efeitos** abre uma revisão final no próprio painel, com antes/depois e justificativa. Somente **Confirmar aplicação** envia o comando de confirmação. Cancelar essa etapa não muda os meios. **Rejeitar proposta**, com motivo, grava decisão terminal sem efeitos.
6. Após resposta confirmada e commit, atualizar consulta oficial pelo servidor, exibir recibo e permitir consultar histórico. Se o refresh falhar, conservar recibo e avisar que a vista precisa ser atualizada; não anunciar falha de aplicação nem reenviar com comando novo automaticamente.
7. **Retomar julgamento** lista propostas deste exercício por referência/status/revisão para o instrutor. Recarregar a página não apaga proposta/decisão. Retomar não confirma, não recria grupos e não associa silenciosamente uma proposta a outra composição.
8. Correção de resultado confirmado começa em **Nova proposta de correção**, referenciando explicitamente a decisão corrigida. Continua sujeita a prévia, registro e confirmação; recuperação de perda obedece à referência exigida pelo provedor de 112. Nenhum botão desfaz ou apaga o histórico.

Sair/trocar seleção invalida a prévia local e respostas pendentes; proposta registrada continua durável. Antes de descartar edição local não salva, informar essa perda de edição e permitir continuar nela. Rejeitar não precisa de grupo ainda disponível, mas exige instrutor autorizado, exercício aberto e revisão vigente da proposta conforme 112. Uma proposta pendente com grupos perdidos/alterados continua consultável, porém não pode ser confirmada pela integração CPC sem nova conferência válida.

### Referências e concorrência

O servidor constrói uma base de julgamento com exercício/cenário, seleção AZUL/VERMELHO, revisões/hashes de composição e dossiê, manifesto de posições e revisão/estado oficial de cada integrante. `basis_sha256` cobre essa captura canônica e é separado dos hashes de 98/108. Nenhum horário aleatório é usado para simular mudança de conteúdo.

O cliente envia seleção, referência/hash da base e alterações didáticas, nunca snapshots, domínio, autoridade, saldo atual ou estado anterior como prova. Servidor recupera e reconfere as fontes e congela a origem da proposta em formato identificável `siscan-cpc-didactic-origin-01`. O publicador de 112 permanece a única autoridade de aplicação; não duplicar regras de perda/revisão/idempotência no adaptador.

Registrar/revisar/confirmar reconfere contexto, grupos ativos/revisões/integrantes, identidades, adjudicação, snapshots, posições e estados. Alteração observada invalida a base e exige nova conferência explícita; não substituir a prévia aceita por um antes/depois recalculado silenciosamente. Corrigir somente dados de um meio não permite ignorar que a composição escolhida mudou.

O plano deverá fechar a serialização entre mudanças no registro de grupos e confirmação no servidor único: API pública de coordenação/revisões, ordem de locks e transação SQL, sem acessar `_state`/`_lock` privados. Testar alteração concorrente de composição durante a confirmação. Não declarar atomicidade distribuída entre memória/SQL, nem publicar efeitos após detectar invalidação do par. Estado e recibo seguem a transação única de 112.

Comando de escrita usa UUID mantido para reenvio da mesma intenção. Replay autorizado de comando já aplicado retorna recibo durável mesmo após alteração posterior de estado ou perda dos grupos temporários; não exige restaurar a base anterior para reaplicar. Novo comando não pode usar o recibo como dispensa de disponibilidade/revisões. Plano deverá expor leitura pública/autorizada de proposta e recibo pelo provedor, sem depender de helpers privados ou SQL duplicado no frontend.

### Interfaces propostas

Nomes abaixo definem o contrato funcional a detalhar no plano, preservando rotas de 108:

| Interface | Comportamento |
|---|---|
| `POST /api/cpc/judgments/context` | Seleção e referência da preparação; retorna base atual e estados autorizados, sem escrita/recibo |
| `POST /api/cpc/judgments/preview` | Base esperada, alterações e motivo; valida e devolve prévia antes/depois, sem gravar proposta/efeito |
| `POST /api/cpc/judgments` | Comando/base/alterações/motivo; registra proposta didática com origem construída no servidor |
| `POST /api/cpc/judgments/{id}/revisions` | Comando, revisão/hash esperados e novo conteúdo completo conferido; cria revisão |
| `POST /api/cpc/judgments/{id}/decisions` | Comando, revisão/hash, confirmar/rejeitar e motivo; confirmação reconfere base e aplica pelo provedor |
| `GET /api/cpc/judgments` | Índice autorizado de propostas CPC do exercício, com paginação limitada, sem inventário/snapshots completos |
| `GET /api/cpc/judgments/{id}` | Proposta/revisões/decisão/recibo autorizados para retomada/histórico, com distinção entre origem congelada e contexto atual |
| Consulta de meio já existente | Acrescentar projeção oficial mínima somente quando há identidade demonstrada e armazenamento habilitado; sem expor proposta ou adversário |

Todas as operações de julgamento são exclusivas do instrutor participante. POST exige sessão/CSRF e formato estrito, inclusive operações de prévia/contexto. Usar 401 sem sessão, 403 sem autoridade, 400 formato, 404 referência inexistente autorizada, 409 desatualização e 503 armazenamento/fonte/integridade indisponível. Não confundir resposta indisponível com estado não avaliado. Leituras de propostas em exercício encerrado são permitidas; novas alterações, não.

Operador consulta apenas estado oficial do próprio partido pela projeção existente, sem rotas de julgamento, justificativa privada ou composição adversária. Revalidar autorização antes do replay e da consulta de origem congelada. Não mandar dados adversários para ocultação por CSS.

### Representação gráfica

Uma única área lateral ativa; sem janela/painel sobreposto ou mapa alternativo. Reutilizar marcadores, identificação textual, seleção, enquadramento e bloqueio de plotagem de 108. Resultado não altera coordenadas de planejamento ou camadas originais.

Hover/consulta resumida do meio mostra índice oficial conhecido, condição quando definida, perda confirmada e origem temporal; valor/texto junto da cor. Para superfície demonstrada, preservar >60 combater, 40–60 navegar e <40 flutuar. Meio perdido não é exibido como apto a combater por ter índice alto. Aeronaves/submarinos/terrestres não recebem navegar/flutuar. Dados desconhecidos são declarados; sem média/estado agregado de força.

Prévia fica identificada no painel como proposta; não repinta os marcadores oficiais como se já aplicada. Após confirmação, buscar projeção oficial e atualizar marcador/ficha/lista permitidos, incluindo retorno ao planejamento. Não acrescentar barras fictícias de combustível/armamento: indicadores de recursos seguem seus contratos, sem converter saldo inicial em atual ou criar limiar de 30%.

Requisições antigas não restauram proposta/estado de outro contexto; controlar geração de resposta e revisão de comando. Mensagens de carga/erro/conflito/aplicação são distintas. Foco/teclado, rótulos e alternativa pela lista; tela estreita sem deixar viewport forçado no navegador do usuário. Não mudar as silhuetas neste recorte.

### Armazenamento e habilitação

Consumir schema aditivo de 112; não criar novas tabelas por conveniência do adaptador nem executar migração em GET/POST de usuário. Proposta/origem/decisão continuam duráveis; o registro de grupos permanece temporário. Se houver necessidade real de mudança de schema, revisar esse ponto antes de implementar.

Prévia isolada deve migrar explicitamente sua base descartável e permitir confirmar/rejeitar/retomar em navegador real. A instância principal exige procedimento próprio de backup consistente verificado, janela sem escritores, migração explícita e verificação antes de habilitar rotas. Esta especificação não autoriza reiniciar o principal nem perder grupos em memória. Instância sem schema/módulo deve informar indisponibilidade e preservar o fluxo de planejamento/conferência anterior.

### Estrutura, estilo e comandos previstos

Adaptador novo em `siscan-prototype/cpc_judgment.py`, contratos públicos de leitura no provedor `operational_state.py`, rotas em `app.py` e módulo gráfico no diretório `static`, reutilizando `cpc-preparation.mjs`/`atlantic-bridge.mjs`. Plano/lista em `tasks/force-confrontation/julgamento/`, preservando os demais diretórios. Sem dependências novas. Payloads validados no servidor, renderização por `textContent`, comandos/UUID separados por intenção e funções pequenas conforme o backend existente.

Exemplo de fronteira, sem implementação nova:

```python
# O adaptador confere a composição; o provedor existente publica o lote.
result = operational_state.decidir_proposta(db, user, decision_payload)
```

Na pasta `prototype` de entrega (`siscan-prototype` no repositório), comandos futuros de verificação:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc check_cpc_judgment.py
& $pythonCpc check_cpc_judgment_http.py
& $pythonCpc check_operational_state.py
& $pythonCpc check_operational_state_storage.py
& $pythonCpc check_cpc_map.py
& $pythonCpc check_map_groups_http.py
& $pythonCpc check_map_units.py
node check_cpc_judgment.mjs
node check_cpc_preparation.mjs
```

Na raiz, `git diff --check`. Verificadores de julgamento ainda não existem; nenhum teste/inspeção gráfica novo foi executado nesta fase documental. Plano definirá harness e comandos de prévia isolada, sem usar dados do instrutor. Browser testing será de ações reais, não substituído por leitura de código ou teste JS.

### Critérios de aceite

| ID | Evidência exigida |
|---|---|
| JMAP-01 | Instrutor autorizado antes de fonte adversária; operador, sessão/CSRF inválidos, contexto revogado e exercício fechado recusados conforme operação |
| JMAP-02 | Base inclui revisão de estado/grupo/posição/snapshot; mudança de qualquer fonte impede registrar/confirmar a prévia antiga sem efeitos parciais |
| JMAP-03 | Prévia e proposta/revisão/rejeição não alteram estado oficial, posição, recursos, relógio ou snapshot |
| JMAP-04 | Confirmação explícita aplica apenas a revisão aceita, por publicador único; cancelamento e resposta atrasada não aplicam/restauram conteúdo antigo |
| JMAP-05 | Retry do mesmo comando não duplica efeitos; resposta perdida permite recuperar recibo; disputa de grupo/estado é serializada/recusada sem deadlock |
| JMAP-06 | Propostas/decisões retomadas após reload/processo novo; perda dos grupos não apaga histórico nem autoriza nova confirmação pela cópia congelada |
| JMAP-07 | Alterações de índice/perda e correção obedecem a 112, preservam ausência e não produzem classes/indicadores fictícios |
| JMAP-08 | No mesmo mapa/painel: selecionar → julgar → prévia → registrar → confirmar/rejeitar → consultar estado/histórico; hover/lista concordam com projeção oficial |
| JMAP-09 | Operador recebe somente estado confirmado do próprio partido; sem vazamento de proposta, motivos privados ou adversário |
| JMAP-10 | Schema/módulo indisponível não degrada planejamento anterior nem produz falso sucesso; isolamento e ausência de migração/reinício principal comprovados |
| JMAP-11 | Teclado/foco/tela estreita, saída/retorno ao planejamento e falha no refresh pós-commit verificados em navegador real isolado |
| JMAP-12 | Regressões de 108/112 passam, originais/planos anteriores preservados e documentos refletem exatamente o que estiver disponível |

### Limites e gate

Sempre preservar autoridade do instrutor, proveniência, visibilidade por partido e confirmação posterior à prévia. Rever mudanças de schema, ativação no principal, efeitos logísticos ou automação. Nunca publicar apuração automaticamente, recalcular silenciosamente a intenção aceita, modificar originais/DB3K ou alegar que julgamento didático valida parâmetros reais de combate.

Fase 1 aprovada por “sim”. Captura de base própria, confirmação em duas ações e retomada/correção pelo painel existente fazem parte do contrato aprovado. Plano de Fase 2 aprovado por “sim”; lista concreta de Fase 3 proposta em 115 e no diretório próprio, incluindo coordenação de concorrência e leitura pública dos registros. Revisar essa lista antes do código; nenhuma migração foi executada nesta fase documental.
