# Protótipo didático SISCAN

**Unidades de teste do motor:** o painel prepara uma unidade sintética por partido e mantém identidade UUID/configuração/snapshot inicial. `POST /api/engine-units/prepare` exige instrutor atribuído, CSRF e corpo vazio; repetir não duplica. `GET /api/engine-units` retorna ambas ao instrutor e apenas unidades próprias com alocação ativa ao aluno. As tabelas `engine_configurations`, `engine_units` e `engine_unit_snapshots` são aditivas; versões/snapshots têm proteção contra alteração e hash conferido na leitura. A preparação não aloca automaticamente nem inicia simulação. Execute `python check_engine_units.py`; detalhes, backup e recibo em 71.

**Preparação do motor:** botão no catálogo do instrutor, com diagnóstico somente leitura em `GET /api/engine-readiness`. `engine_input.py` valida a fixture controlada `fixtures/engine/synthetic-fuel-01.json`, unidades/domínios e manifesto fixado no backend; confere também hashes/versões reais da origem, compilação e recursos. O aceite é apenas para teste sintético, sem simulação ou promoção de atributos. Execute `python check_engine_input.py`; contrato, autenticação e limites no documento 70. Na instalação local, a fonte é `DB3K_498.db3` na pasta superior a `prototype`; ausência de arquivo aparece como pendência e não impede validar a fixture sintética.

**Armamento e payload** associa massa DataWeapon.Weight, DefaultLoad/MaxLoad e configuração/instalação no endpoint técnico (`armament_payload`). A ficha compara cada loadout separadamente ao WeightPayload aéreo, como referência documental, sem calcular carga operacional disponível. Opcionais, reservas e suportes são separados; massa desconhecida, Multiple diferente de 1 e quantidades conflitantes bloqueiam totalização. Execute `python check_armament_payload.py`. A auditoria integral usa `python -m tools.audit_armament_payload COMPILACAO NOVO_RELATORIO.json`; veja 68 para cobertura, hipóteses e pendências.

Combustível e propulsão possuem base SQL própria em `data/db3k-resources-09.sqlite3`, derivada da compilação: 1.940 combustíveis, 3.467 propulsores, 20.544 pontos e 28.757 instalações. Construa em novo destino com `python -m resource_store data/db3k-compiled-06.sqlite3 NOVO_DESTINO.sqlite3`; não sobrescreve arquivos. O endpoint técnico adiciona `resource_store` com registros diretos, unidades pendentes e proveniência; a exportação inclui esses dados. Consulta somente leitura, mesmo controle de acesso e sem alocação/cálculo automático. Confira com `python check_resource_store.py`; esquema, auditoria e limites em 67.

As fichas exibem unidades com evidência (`amostra`/`referência`) e pendências explícitas. `technical_units.py` fornece o contrato `db3k-498-units-01`; `source-platform` inclui `measurements` e `source-technical` inclui metadados por nó e `consumption_profiles` por propulsor. Cada ponto mantém valores brutos/origem; `unit=null` e `calculation_ready=false` impedem confundir referência de apresentação com unidade SQL aprovada. Não há média sem perfil temporal nem conversão automática. Execute `python check_technical_units.py`; detalhes e fontes no documento 66.

O instrutor abre em **Catálogo técnico**, com seis categorias, lista de meios e ficha com foto local, dados gerais e componentes navegáveis. **Exercício e revisão** mantém o fluxo didático e os painéis anteriores. A consulta usa `data/db3k-compiled-06.sqlite3`, gerada para esta versão com `python -m tools.compile_db3k CAMINHO_DB3K NOVO_DESTINO.sqlite3`; o destino deve ser novo. O compilador preserva as 167 tabelas em registros brutos e mede FKs, cadeias estruturais e domínios nominais. Não aprova relações semânticas/unidades. Fotos são lidas da instalação local CMO; não fazem parte do repositório. Confira com `python check_compilation.py`; evidências, API e limites nos documentos 64–65.

**Dados técnicos compilados**, abaixo de cada ficha, reúne recursivamente sensores completos, combustível, propulsão e tabelas de regime/consumo, sem navegação obrigatória para outra ficha. `GET /api/source-technical?table=DataShip&id=3` retorna todos os nós/campos/vínculos alcançáveis nas regras compiladas, preservando ciclos e instalações repetidas sem truncamento. A tela separa componentes diretos/transitivos e exporta JSON completo. As bibliotecas técnicas permitem consultar cadastros independentes. Execute `python check_technical_bundle.py`. Para comparar todos os valores e exportar metadados de colunas/PKs, use `python -m tools.audit_compilation CAMINHO_DB3K COMPILACAO.sqlite3 NOVO_RELATORIO.json`. A auditoria desta fonte conferiu 8.010.533 valores sem divergência; veja 65.

Para incorporar evidências técnicas brutas já conferidas e ligadas a referências cadastradas, execute `python -m tools.import_technical_values CAMINHO_DB3K CAMINHO_AMOSTRA EVIDENCIAS.json BANCO_SISCAN --decision-record "Registro da autorização de incorporação bruta pendente"`. Faça backup consistente antes da execução. O importador confere novamente a fonte, exige todas as referências e grava valores em `catalog_technical_values` com unidade nula e estado fixo `pending_unit_and_semantics`; `catalog_technical_imports` preserva hashes e decisão. Não cria meios, não aprova grandezas e não alimenta cálculos. Reexecução não duplica valores; divergências são recusadas sem sobrescrita. Confira com `python check_technical_import.py`; veja o documento 62.

O instrutor atribuído pode consultar o banco pelo painel **Catálogo cadastrado — referências e valores técnicos**: busca por trecho de nome ou ID numérico exato, filtro de plataforma e páginas de 50 referências. Os detalhes mostram valores brutos, tipo SQLite e hashes, com validação pendente explícita. O endpoint `GET /api/catalog-references?page=1&q=&table=` retorna referências e valores somente para o instrutor atribuído. Não oferece promoção, alocação ou escrita de atributos. A revisão antiga dos 80 candidatos e suas notas foi preservada. Verifique com `python check_reference_catalog.py`; contrato e validação visual no documento 63.

Para preparar uma amostra DB3K para revisão, execute `python tools/stage_db3k.py CAMINHO_DA_FONTE CAMINHO_DE_UM_NOVO_BANCO --limit-per-table 20`. A ferramenta não alimenta o exercício: nomes/IDs e códigos originais ficam em um banco separado, com origem e status pendente de revisão. O arquivo de origem é aberto somente para leitura. Confira a ferramenta com `python check_db3k_staging.py`.

Para consultar a amostra na interface, guarde o banco gerado em `data/db3k-review-01.sqlite3`. Um instrutor atribuído ao exercício pode abrir “Catálogo Command / DB3K para revisão” e pesquisar nome/ID ou filtrar a tabela de origem. A consulta retorna no máximo 500 candidatos pendentes, identifica a fonte pelo hash e não oferece promoção ou alocação. Execute `python check_candidate_catalog.py` para conferir autorização e preservação da fonte. O banco de candidatos permanece fora do GitHub.

Para investigar descrições literais dos códigos, na pasta do protótipo execute `python -m tools.inspect_db3k_domains CAMINHO_DB3K CAMINHO_AMOSTRA NOVO_RELATORIO.json`. O relatório distingue correspondência literal, ausência de código/domínio e vínculo sem FK; não aprova semântica nem altera a amostra. Confira com `python check_db3k_domains.py`. Guarde resultados em `data/` para mantê-los fora do GitHub.

A ferramenta também compara ID, nome e todos os códigos do candidato diretamente com o registro original antes de emitir evidências. Divergências interrompem a emissão. A promoção para catálogo utilizável exige aprovação explícita do responsável pelo projeto (documento 53); observações de instrutores não substituem essa aprovação.

Para preparar uma proposta de identificação de referência ao responsável, execute `python -m tools.prepare_approval_packet CAMINHO_AMOSTRA RELATORIO_CONFERIDO NOVO_PACOTE.json`. A ferramenta verifica os hashes e a cobertura da conferência literal, gerando JSON e Markdown com todas as decisões pendentes. Ela não aprova registros, não cria unidades e não permite alocação. Confira com `python check_approval_packet.py`. Os pacotes com dados de origem devem ficar em `data/`, fora do GitHub.

Após decisão explícita do responsável, um operador local pode registrar as referências com `python -m tools.register_source_references PACOTE.json APROVACAO.json BANCO_SISCAN`. O manifesto de aprovação deve identificar lote, hash do pacote, responsável, registro da decisão, escopo `literal_source_identification_only` e lista de candidatos aprovados. A ferramenta cria IDs próprios e estáveis para referências daquela versão da fonte, grava a decisão e recusa escopos mais amplos ou bancos de origem como destino. Reexecução não duplica referências. O manifesto é um registro administrado pelo operador local, não uma assinatura digital ou autorização de usuário pela interface. Teste com `python check_reference_registration.py`.

A tela consulta as descrições do arquivo local `data/db3k-domains-01.json`. Os hashes da fonte e da amostra devem corresponder aos do relatório; se houver divergência ou formato inválido, a consulta mantém os códigos originais e informa que as descrições não foram carregadas. Cada candidato oferece “Descrições e evidências dos códigos”, sem aprovação ou promoção automática.

A inspeção inclui os campos técnicos selecionados que existirem na tabela original, com valor literal, tipo SQLite e unidade nula. Na tela, “Valores técnicos originais — unidades pendentes” permite examiná-los. Zero e NULL não são interpretados como indisponibilidade ou capacidade real. O endpoint só aceita essa evidência com estado `pending_unit_and_semantics`; o módulo não converte valores, não atribui unidades e não os usa em cálculos ou meios alocáveis.

Em “Observações da revisão”, o instrutor atribuído pode acrescentar anotações de até 4000 caracteres. O histórico preserva autor, horário UTC, candidato, hash da fonte e exercício; anotações são adicionadas, não substituídas. Elas ficam no banco do protótipo e não alteram o DB3K, a amostra ou a situação pendente dos candidatos. A troca da amostra exige reabrir a consulta antes de registrar anotações para sua fonte.

Primeiro incremento local do fluxo aprovado: cenário fictício, consulta aos meios sintéticos da equipe, composição de grupamento, documento/justificativa, revisão humana e liberação pelo instrutor. Esta pasta é independente; não integra nem altera ATLANTICADOR ou DB3K.

## Limites

- Dados são sintéticos e demonstrativos; não usar informações operacionais, pessoais ou do DB3K.
- Aplicação de demonstração local, vinculada somente a `127.0.0.1`. Não publicar em rede nem usar com alunos antes de especificação e revisão de segurança.
- Sem mapa operacional, cálculo tático, motor de simulação, recomendação, MPNL, relatório PDF autenticado ou integração externa.
- A configuração sem limite de tentativas é apenas a configuração desta instância demonstrativa; o instrutor pode configurá-la por exercício. Prazos podem ficar sem data.
- A rubrica é narrativa, sem notas ou critérios automáticos.

## Execução local

Requer Python 3.11 ou posterior. No PowerShell:

```powershell
$env:SISCAN_INSTRUCTOR_PASSWORD = 'defina-uma-senha-local-forte'
$env:SISCAN_EVALUATOR_PASSWORD = 'defina-outra-senha-local-forte'
$env:SISCAN_STUDENT_PASSWORD = 'defina-uma-senha-local-forte'
python app.py
```

Contas sintéticas: `instrutor`, `avaliador`, `azul-01` a `azul-08`, `vermelho-01` a `vermelho-08`. As senhas de aluno usam a variável comum de demonstração; por isso, não reutilize este mecanismo em ambiente real. O banco local é criado em `data/siscan-demo.sqlite3`.

## Fluxo implementado

1. Instrutor aloca meios sintéticos ao partido Azul ou Vermelho no painel “Alocar meios ao partido”. Aluno autenticado vê os meios recebidos e o fluxograma confirmado; prepara composição e salva rascunho. Todos os alunos atribuídos ao partido acessam o mesmo conjunto disponibilizado.
2. Ao submeter sem justificativa, o sistema apresenta a advertência aprovada e registra a ausência se o aluno confirmar.
3. Avaliador pode comentar, validar ou devolver. Versões anteriores são preservadas.
4. Instrutor acompanha todas as equipes, solicita revisão ou libera o resultado após validação.
5. Instrutor pode alterar título/objetivo do cenário durante o exercício após o aviso obrigatório; cada mudança cria versão e registra autoria, horário e justificativa quando informada.
6. Eventos de autoria, revisão, submissão, liberação e mudança de cenário ficam registrados no backend.
7. Novas submissões notificam instrutores/avaliadores atribuídos; devoluções e liberações notificam o aluno. Cada destinatário registra a leitura das próprias notificações. A leitura não significa concordância nem altera prazos. Notificações são internas, atualizadas ao recarregar o painel, e começam com as ações realizadas após este incremento.

O fluxograma confirmado é exibido como referência de leitura. Este incremento implementa apenas a trilha de composição e revisão documental; não automatiza as decisões “Sim/Não” do diagrama.

O relatório individual oferece impressão e salvamento como PDF pelo navegador, com layout de papel. Essa cópia não possui QR Code nem validação de autenticidade; a emissão autenticável permanece pendente.

As alocações começam vazias. O instrutor deve configurá-las, inclusive em instâncias demonstrativas já existentes. Retirar um meio bloqueia sua seleção em novos salvamentos; documentos anteriores continuam preservados. A auditoria registra os meios adicionados/retirados e notifica os alunos do partido. Este catálogo ainda não usa dados DB3K.

## Verificação da impressão

`python check_workflow.py --print-fixture` cria um relatório HTML isolado em `tmp/print/report.html`, com justificativa longa e dados sintéticos. O arquivo temporário não é versionado. A conferência realizada no Edge gerou quatro páginas A4; as páginas foram renderizadas e inspecionadas, o conteúdo final e o histórico foram recuperados por extração de texto e os controles de impressão ficaram ocultos. Isso verifica a amostra usada; documentos com outros conteúdos continuam sujeitos a revisão de paginação.

A regra vigente é alocação por partido, conforme correção expressa do responsável. Registros antigos por aluno permanecem apenas como histórico e não concedem acesso; as alocações por partido devem ser configuradas pelo instrutor.

## Ensaio sintético de combustível

No painel “Unidades sintéticas”, o instrutor pode inicializar uma execução e avançar um intervalo manual. A taxa controlada é 2 kg/min e cada unidade começa com 600 kg. A tabela separa saldo inicial, saldo atual e consumido, com histórico por comando. Repetições não debitam novamente. Alunos leem apenas unidades alocadas ao próprio partido. Este teste não usa taxas Command. Veja [contrato, evidências e limites](../docs/recovery/72_ESTADO_RELOGIO_E_CONSUMO_TRANSACIONAL.md). Execute `python check_engine_runtime.py` para verificar transações, conflitos, conservação e concorrência com duas conexões.

## Continuidade e histórico dos ensaios

No painel de execução, o instrutor pode abrir “Continuar em nova versão”, informar motivo e criar uma sucessora. Tempo e combustível são herdados; a execução anterior fica disponível em “Consultar execuções preservadas”. Não há reabastecimento ou reset. Novos comandos identificam a execução e a revisão esperada. `python check_engine_continuity.py` verifica migração, conservação, conflitos e rollback. Veja [contrato e evidências](../docs/recovery/73_CONTINUIDADE_VERSIONADA_DOS_ENSAIOS.md).

## Prévia de perfil temporal

Em “Unidades de teste do motor → Prever perfil de consumo”, o instrutor monta trechos com regimes sintéticos e consulta demanda, saldo projetado, curva e déficit. O cálculo não altera estoque/relógio e não usa taxas Command. Editar o plano remove a previsão anterior; revisão desatualizada exige atualização do estado. Execute `python check_engine_profiles.py`. [Contrato e evidências](../docs/recovery/74_PREVISAO_PERFIL_TEMPORAL_CONSUMO.md).

## Alerta mínimo de combustível

Em “Unidades de teste do motor”, operador do próprio partido e instrutor podem definir o mínimo por meio, em kg. Alerta em saldo menor ou igual ao limite; zero é válido e desativação é explícita. Não há mínimo padrão imposto nem bloqueio automático da reserva. Os avisos são conferidos a cada 10 s com painel/aba visíveis. A prévia mostra a linha e o instante de cruzamento. Execute `python check_fuel_limits.py`. [Regras e evidências](../docs/recovery/75_ALERTAS_NIVEL_MINIMO_COMBUSTIVEL.md).

## Mapa ATLANTICADOR integrado

Após login, abra “Mapa ATLANTICADOR · inserir meios adjudicados”. Clique no mapa ou digite coordenadas, selecione meios e confirme plotagem. Seleção por retângulo usa “Selecionar área”. `python check_map_units.py` verifica isolamento e transações. Prepare o editor local com `python tools/prepare_atlantic_map.py <ZIP-original> data/atlanticador`. O ZIP e o frontend extraído não são publicados. [Escopo e limitações](../docs/recovery/77_PRIMEIRA_INTEGRACAO_MAPA_ATLANTICADOR.md).

## Representação e reposicionamento no mapa

Use as abas “Camadas” e “Meios adjudicados” na lateral. Botão direito no símbolo → “Reposicionar” → clique no destino; Esc cancela. Há alternativa por coordenadas. Selecione silhuetas ou o motor Calunga e consulte o catálogo visual. Hover abre a ficha com dados cadastrados; desconhecidos são explicitados. `node check_map_visuals.mjs` verifica as silhuetas. [Escopo e evidências](../docs/recovery/78_MAPA_PAINEL_REPOSICIONAMENTO_E_REPRESENTACOES.md).
