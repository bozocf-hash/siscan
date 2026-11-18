# Spec: force-confrontation — preparação didática de grupamentos

**Atualização de 2026-11-17 — Recorte 3 entregue:** especificação, plano e tarefas aprovados por “sim”; JUD-01–14 concluídas e verificadas em [116](docs/recovery/116_ENTREGA_JULGAMENTO_DIDATICO_NO_MAPA.md). Percurso real de julgamento/prévia/confirmacão/rejeição/estado/histórico no mesmo mapa. Banco/processo principal preservados; automático permanece etapa posterior.

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

**2026-11-17. Especificação, plano e tarefas aprovados por “sim”; implementação verificada em 116.** Continuidade solicitada por “pode seguir” após [112](docs/recovery/112_ENTREGA_ESTADO_E_ADJUDICACAO_DURAVEL.md). Corresponde à etapa 3 já delimitada em 104; mantém os IDs `force-confrontation`, `operational-state` e `execution-core`, sem um segundo publicador de efeitos.

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

Na raiz, `git diff --check`. Verificadores implementados e executados: 179 testes nomeados distintos e o verificador assertivo de plotagem passaram, com percurso real no navegador e recuperação em 116. Harness persistente em base/porta/cookie próprios, sem usar dados do instrutor. Testes JS/HTTP e observação de navegador foram registrados separadamente.

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

Gates de especificação, plano e tarefas satisfeitos por aprovações distintas. JUD-01–14 e checkpoints concluídos conforme 116; não reabrir gates desta fatia. Migração executada somente em bases de teste/harness; principal preservado. Produtor automático e implantação principal continuam recortes/procedimentos próprios.


## Recorte 4-A — Prontidão para o ensaio automático controlado

**Estado: especificação aprovada pelo responsável por “sim” após 121; plano de Fase 2 aprovado por “prossiga”; lista de Fase 3 proposta em 123; código não iniciado.** Continuidade da etapa 4 aprovada em 104, preservando os recortes já entregues. Capacidade `force-confrontation`, sem criar novo domínio ou mapa de módulos. Documento de leitura: [121](docs/recovery/121_ESPECIFICACAO_PRONTIDAO_ENSAIO_AUTOMATICO.md).

### Objetivo e premissas

Antes de ligar execução automática ao mapa, o instrutor deve conferir a prontidão das entradas do par escolhido e entender, por meio, o que falta. Esta entrega retorna diagnóstico; não resolve combate, registra proposta ou aplica efeitos. A autoridade final permanece no instrutor. Especificação e dados descritivos do Command não constituem validação de probabilidades, dano ou autonomia real.

Evidências diretas no código: `GerenciadorDeCombate._validar_rodada` aceita ações somente do par atacante/defensor; `SimulacaoTemporal.avancar_turno` recebe ações declaradas, sem uma política autônoma de escolha de alvos; `CenarioTatico` usa geometria cartesiana em milhas náuticas; `engine_units.configuration_domain` reconhece apenas a configuração aérea sintética controlada. O armazenamento de adjudicação atual aceita somente `source='didactic'`. Portanto, nesta fase não há suporte demonstrado a confronto automático de grupamentos, transformação geográfica do mapa, parâmetros reais ou origem persistida de ensaio automático.

Premissas propostas: reutilizar contexto/dossiê/identidades e o motor existentes; diagnóstico exclusivo do instrutor; hipóteses explicitamente identificadas; nenhum valor físico padrão criado para completar lacunas; nenhuma alteração de schema ou dependência. Começar pelo caso de duas unidades individuais, uma de cada partido, contidas nos grupos selecionados. Os grupos continuam com seus integrantes; cardinalidade maior aparece como limite do motor atual, sem selecionar um integrante silenciosamente.

### Experiência do instrutor

Depois de preparar o par no painel CPC, **Conferir prontidão do ensaio** apresenta um resumo: **Entradas incompletas**, **Recorte não suportado** ou **Pronto para ensaio controlado**. Os detalhes ficam expansíveis por meio, com campo, motivo, origem e providência necessária. Manter painel compacto e o mesmo mapa, sem abrir janelas sobrepostas.

O estado pronto significa somente que as entradas cumprem o contrato do ensaio sintético de pares. Não significa que o combate foi simulado, que haverá engajamento ou que os dados estão aprovados para previsão real. Não acrescentar botão habilitado que finja iniciar uma simulação nesta entrega. Julgamento didático e confirmação continuam disponíveis pelos caminhos existentes.

### Entrada e fontes

Propor `POST /api/cpc/trial-readiness`, sessão de instrutor atribuído ao exercício, CSRF e payload estrito. Entrada: `selection` com IDs/revisões dos grupos, `expected_view_sha256` da preparação e `hypotheses` opcional. Ausência de hipóteses é consulta válida e produz pendências, nunca preenchimento automático.

O servidor recupera a base atual pelo provedor de julgamento/contexto e reconfere seleção, cenário, adjudicação, snapshots, posições e estado oficial. O cliente não envia estados oficiais, snapshots ou provas de autorização como fonte confiável. Hash esperado divergente recusa a consulta por conflito, sem substituir silenciosamente o par.

Quando informado, `hypotheses` é um objeto de versão de formato explícita, identificação/versão declarada e parâmetros por `unit_id` pertencente ao par, além dos parâmetros do cenário. O hash canônico é calculado no servidor. A versão declarada identifica a hipótese, sem dar aprovação técnica. Cada grandeza deve declarar unidade e origem: dado aprovado para a finalidade, hipótese didática expressa ou indisponível. Proibir chaves extras, referências a outros meios, NaN/Infinity, booleanos usados como números e identificação duplicada. Perfil incompleto retorna pendências; valores inválidos retornam erro de validação. Limites de tamanho/quantidade serão compatíveis com os limites existentes, sem entrada ilimitada.

Snapshot técnico inicial não é saldo atual. Posição geográfica não é distância cartesiana do ensaio. A ausência de um adaptador geográfico explícito impede afirmar que os movimentos do ensaio refletem as posições do mapa. Nesta conferência, geometria local didática pode ser fornecida explicitamente, com origem/unidade e aviso de que não é trajetória geográfica. Não converter graus em NM por um fator constante implícito.

### Matriz de conferência

| Grupo de entrada | Conferência exigida | Lacuna / limite |
|---|---|---|
| Contexto e identidade | Mesmo exercício/cenário; grupos/revisões; instância/configuração/snapshot individual | Identidade incompatível recusa consulta; referência indisponível informa motivo |
| Perdas oficiais | `lost === true` exclui a unidade do conjunto ativo, conforme 120 | Não restaurar por hipótese; partido sem integrante utilizável bloqueia o ensaio |
| Quantidade e domínio | Um integrante utilizável por partido; configuração/domínio demonstrados | Mais integrantes ou domínio ainda não reconhecido: `unsupported_by_current_engine` |
| Condição inicial | Pontos de vida abstratos e escala do ensaio explicitamente declarados | Não transformar índice desconhecido em 100% nem copiar DamagePoints como equivalente |
| Estado inicial não avaliado | Hipótese didática de disponibilidade identificada separadamente, quando necessária | Não altera `lost=null` ou avaliação oficial; não pode contrariar perda confirmada |
| Detecção | Alcance NM, probabilidade didática 0–1, assinatura m² e fatores declarados | Alcance de sensor no catálogo não gera probabilidade por inferência |
| Estoques e armamentos | Estoques individuais, quantidade inteira, tipo aceito, alcance NM, Pk e dano abstrato declarados | Não somar paióis e configuração alternativa como estoque atual; zero explícito é válido |
| Defesa | Estoque defensivo e custo inteiro por tentativa, eficácia didática quando aplicável | Probabilidade isolada não cria munição defensiva ou tentativa ilimitada |
| Logística | Combustível kg, taxa kg/min, velocidade nós; reserva e situação de voo para aéreo | Saldo ausente não é tanque cheio; capacidade não substitui saldo; alerta M+5 separado da reserva de retorno |
| Geometria e tempo | Posições locais/pares de distâncias coerentes em NM, rumos, duração e semente explícitos | Conversão do mapa e política autônoma de ações ainda precisam de contratos próprios |

Essa matriz não introduz regras de alvos, prioridade, salvas, first strike, eficácia de defesa, perda percentual ou agregação de poder. São contratos a fechar para a execução seguinte. Valores zero válidos não viram ausência por teste de truthiness; zero munição pode gerar aviso de impossibilidade de engajar, sem adulterar o inventário. A capacidade de executar uma validação não equivale a capacidade de combater.

### Saída e semântica

Envelope JSON proposto: `schema_version='siscan-cpc-trial-readiness-01'`, exercício/cenário, seleção, referências da base/preparação, hash das hipóteses quando fornecidas, escopo `controlled_pair`, unidades incluídas/excluídas, lista de pendências e avisos, `ready_for_controlled_trial` e `official_calculation_ready=false`.

Cada pendência tem código estável, escopo global ou `unit_id`, campo, motivo e providência. Ausência de dado, entrada inválida, fonte indisponível, recorte não suportado e condição operacional conhecida são estados diferentes. Não anunciar lista vazia como leitura bem-sucedida após erro. Um resultado negativo válido é HTTP 200 com os motivos; erro de formato 400, falta de sessão 401, autoridade 403, referência autorizada inexistente 404, conflito 409 e fonte/integridade indisponível 503, conforme convenções atuais.

O diagnóstico não altera banco de domínio, relógio, RNG do motor, posições, munição, combustível, propostas, decisões ou eventos de combate. Não existe UUID de aplicação para essa consulta. Resultados em memória não constituem relatório persistido. Futura execução deverá congelar origem, parâmetros e rubrica, produzir relatório e preservar revisão humana; não mascarar resultado automático como origem didática já suportada pelo schema atual.

Operadores não recebem esta resposta com o adversário. No cliente, sair, trocar grupo, editar hipóteses ou atualizar fontes invalida o diagnóstico anterior e descarta respostas atrasadas. Uma consulta positiva não reserva recursos nem autoriza execução futura sem nova conferência.

### Estrutura, estilo e verificação

Locais candidatos, a confirmar somente no plano: `siscan-prototype/cpc_readiness.py` para a validação/diagnóstico; adaptador HTTP em `app.py`; painel existente em `static/cpc-preparation.mjs`; verificadores `check_cpc_readiness.py` e de HTTP/JS seguindo os padrões locais. Nenhum arquivo novo foi criado nesses caminhos nesta especificação.

Reutilizar funções públicas de contexto e provedores, sem importar fixtures em produção, acessar locks/estado privados ou duplicar o publicador. Manter estilo Python por funções pequenas, parâmetros explícitos, `dict`/JSON canônico, tipagem nas fronteiras e exceções de validação conhecidas. Exemplo já existente no provedor: `result['basis_sha256']=digest(result)`; o cliente não inventa o hash da fonte.

Comandos existentes de regressão, na raiz (não executados por esta edição documental):

```powershell
$pythonCpc = 'C:/Users/bozoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_*.py'
node --test siscan-prototype/check_cpc_judgment.mjs siscan-prototype/check_cpc_preparation.mjs siscan-prototype/check_map_presentation.mjs siscan-prototype/check_map_groups.mjs
git diff --check
```

Os verificadores novos terão comandos específicos no plano quando existirem. Não usar descoberta vazia como evidência. Sem build frontend ou dependência nova. Verificação em navegador usará harness isolado de `check_cpc_judgment_http.py`, diretório temporário novo e porta livre; não iniciar `app.py` na base principal como teste.

### Critérios de aceite

| ID | Comportamento verificável |
|---|---|
| AUTO-READY-01 | Instrutor consulta par autorizado; operador/outro exercício é recusado antes de expor integrantes |
| AUTO-READY-02 | Fonte e base são reconferidas; referência/hash divergente recusa diagnóstico sem substituir seleção |
| AUTO-READY-03 | Dado ausente gera pendência por campo/unidade; não são criados Pk, dano, saldo ou índice padrão |
| AUTO-READY-04 | Perfil didático completo válido é identificado como hipótese; readiness nunca aprova dados físicos/Command |
| AUTO-READY-05 | Grupo acima do limite de par/domínio não reconhecido aparece como não suportado, sem redução silenciosa |
| AUTO-READY-06 | Perda confirmada fica fora do conjunto ativo; hipótese não restaura perda; partido vazio bloqueia |
| AUTO-READY-07 | Zero explícito e unidade de contabilização são preservados; NaN, booleano numérico e unidade incompatível são recusados |
| AUTO-READY-08 | Geometria local não é anunciada como conversão das posições geográficas; pendências de execução ficam visíveis |
| AUTO-READY-09 | Consulta válida, negativa e falha não alteram estado, recursos, posições, propostas ou RNG |
| AUTO-READY-10 | Nova seleção/edição/saída invalida consulta; resposta atrasada não restaura resultado antigo |
| AUTO-READY-11 | Painel compacto, acessível por teclado e lista, preserva julgamento didático e o mapa definidos |
| AUTO-READY-12 | Testes de unidade, HTTP/CSRF, preservação de dados e navegador isolado demonstram os critérios e limites |

### Limites e revisão solicitada

Este recorte entrega conferência de entradas para o primeiro ensaio controlado; não entrega disparos automáticos, combate multimeios, reprodução de trajetórias ou aplicação de consumos no exercício. Depois dele ainda devem ser especificados: política de ações/alvos/iniciativa, ampliação do resolvedor para grupos, adaptador geográfico, tradução de resultado em sugestão de efeitos e origem durável do ensaio automático. Não alterar o schema `didactic` de 112 por conveniência.

Revisão desta especificação concluída por “sim”: prontidão aprovada como primeira fatia da ligação automática, com demonstração inicial limitada ao par controlado e hipóteses visíveis, antes de integrar execução por grupos. A skill Spec Driven Development determina: “Do not advance to the next phase until the current one is validated.” A aprovação deste documento permitirá elaborar o plano; não aprova parâmetros reais, migração ou implementação de etapas posteriores.


Plano técnico do Recorte 4-A: [tasks/force-confrontation/prontidao/plan.md](tasks/force-confrontation/prontidao/plan.md), aprovado por “prossiga” após 122. Lista detalhada em [tasks/force-confrontation/prontidao/todo.md](tasks/force-confrontation/prontidao/todo.md), proposta em 123; implementação não iniciada.
