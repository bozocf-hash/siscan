# Spec: technical-catalog — dados técnicos utilizáveis e rastreáveis

**Estado:** Fase 1 aprovada pelo responsável em 2026-11-11, por resposta expressa “sim” após apresentação desta especificação e do recorte. **Mapa:** [CAPABILITY_MAP.md](CAPABILITY_MAP.md), Fase 0 aprovada. A aprovação permite elaborar o plano técnico; não aprova dados físicos nem inicia implementação.

## Objetivo

Permitir que o backend diferencie evidência técnica recuperada de atributo apto a um cálculo específico. Usuários: responsável que aprova a promoção, equipe que reúne evidências e módulos consumidores que precisam de dados versionados. Sucesso: um consumidor recebe um perfil elegível, com origem/unidades/condições demonstradas, ou uma recusa explícita e rastreável; nunca um número presumido.

### Premissas propostas

1. Primeiro recorte: combustível de aviação e taxas de consumo de aeronaves por regime/faixa/configuração. Não abrange combustível naval, baterias, sensores ou poder de combate nesta fatia.
2. Partir da compilação e da base de recursos já existentes, sem repetir a extração integral. Preservar fonte, valores literais e relações pendentes.
3. Separar unidade SQL, unidade de apresentação e unidade normalizada. Evidência de kg/kg/min no painel não basta para aprovar escala SQL ou taxa por motor/conjunto.
4. Casos sintéticos continuam independentes e identificados; não geram aprovação de dados reais.
5. Implementação deverá reaproveitar a estrutura atual e acrescentar apenas o necessário. Nenhuma migração, dependência ou serviço novo está determinada por esta especificação.

## Escopo e limites

Inclui inventário do recorte já recuperado, registro de evidências por atributo/contexto, validação de unidade/domínio/base de contabilização, transformações demonstradas, aprovação explícita por escopo e consulta de elegibilidade. Inclui preservar decisão, autoria, fonte/versão e motivo de recusa.

Não inclui criar unidades do exercício, adjudicar meios, atualizar estoques/relógio, calcular movimento, aplicar perfis de consumo, reabastecer, criar bases ou reformular frontend. Não atribui disponibilidade operacional ou capacidade de combate a partir de números técnicos. Essas responsabilidades pertencem às outras capacidades do mapa.

A fatia estará concluída funcionalmente quando conseguir representar e verificar o contrato com casos controlados e rejeitar os casos reais ainda insuficientemente comprovados. A homologação de um perfil real exige evidência e aprovação próprias; não é substituída pelo teste do software.

## Rastreabilidade documental

| Referência | Requisito preservado |
|---|---|
| 35–39, 49 APR-06/07/10/13 | Autoridade do backend; domínios separados; referência/modelo/configuração/unidade distintos; dados incertos não são entrada oficial |
| [53](docs/recovery/53_APROVACAO_PROMOCAO_CATALOGO.md) | Promoção de candidato validado exige aprovação explícita do responsável; observação de instrutor não basta |
| [65](docs/recovery/65_LEVANTAMENTO_INTEGRAL_E_DADOS_TECNICOS_COMPILADOS.md) | Preservar valores e relações recuperados, inclusive faltas de destino |
| [66](docs/recovery/66_UNIDADES_E_BASE_DOS_PERFIS_DE_CONSUMO.md) | Não confundir rótulo de tela com escala SQL; não presumir taxa por motor/conjunto ou média dos regimes |
| [67](docs/recovery/67_BASE_PERSISTIDA_COMBUSTIVEL_E_PROPULSAO.md) | Reutilizar persistência de combustível/propulsão e proveniência, mantendo leitura das fontes |
| [69](docs/recovery/69_PARECER_ENGENHARIA_DADOS_E_PRONTIDAO_MOTOR.md) | Elegibilidade por capacidade/recorte, sem exigir catálogo inteiro validado |
| 70–75 | Contrato sintético, manifesto, snapshots, transações e mínimo do operador não promovem valores Command |
| 78 | Dados desconhecidos não equivalem a zero ou indisponibilidade; representação gráfica não altera configuração física |

Os documentos são fontes normativas conforme suas decisões/status, não substituídos por este texto. Contradição relevante encontrada exige atualização da especificação e resolução explícita antes da implementação afetada. A contagem de 79 documentos não implica releitura integral de todos nesta fase.

## Linha de base e stack

Backend existente em Python, biblioteca padrão e SQLite; runtime local inspecionado: Python 3.12.14. Frontend atual em JavaScript nativo, sem alteração nesta fatia. Manter versões existentes; nenhuma nova dependência proposta.

Já existem `technical_units.py`, `resource_store.py`, `source_catalog.py`, compilação integral, registro de referências e importação literal. `engine_input.py` restringe a entrada ao caso sintético fixado. Unidades e semânticas pendentes devem conservar sua condição; não trocar `calculation_ready` isoladamente. O registro de referência com escopo `literal_source_identification_only` não aprova atributos para consumo operacional.

## Contrato do provedor

Estas são responsabilidades e informações observáveis; nomes de tabelas, rotas e funções serão definidos no plano técnico, sem duplicar fornecedores existentes.

### Evidência e atributo

Cada atributo consultável deve permitir identificar: entidade/tabela/campo/chave na fonte, valor literal e tipo, hash/versão da fonte, relações/contexto usados, unidade candidata e unidade comprovada separadas, evidências localizadas, estado da validação e limitações. Valor normalizado, unidade e transformação só existem quando demonstrados; preservar o valor bruto em qualquer caso.

Para massa de combustível e taxa, registrar explicitamente a base de contabilização (tanque, instalação, motor ou conjunto, conforme demonstrado), tipo de combustível, regime, faixa de altitude e configuração aplicável. Ausência de base ou condições obrigatórias impede aquele cálculo. Não multiplicar uma taxa pelo número de motores sem comprovar o significado da linha.

### Aprovação e versão

Separar validação técnica de autorização de uso. A aprovação deve identificar responsável, referência da decisão, atributo/perfil e contexto exatos, hash da evidência/conjunto aprovado e finalidade autorizada. Reexecução do mesmo registro não duplica versões. Mudança de valor, fonte, regra ou contexto não herda aprovação silenciosamente; gera nova versão pendente e preserva a anterior.

A aprovação não pode ser autoatribuída por um cliente ou por uma flag no pedido. O mecanismo de autenticação/registro dessa autoridade é uma questão aberta; o manifesto local já existente não deve ser apresentado como assinatura digital.

### Consulta para consumidores

Solicitação deve identificar configuração/perfil, versão e finalidade de uso. Resposta elegível reúne os atributos obrigatórios, unidades, condições, origem, aprovação e versão/hash do contrato. Resposta não elegível devolve motivos específicos, mantendo os valores de referência acessíveis apenas como evidência. Não converter falta de informação em valor zero nem suprimir campos para fazer um caso parecer completo.

Para o recorte inicial, elegibilidade exige simultaneamente: integridade/origem coerentes, unidade/escala comprovadas, domínio e base da taxa conhecidos, vínculo de configuração demonstrado, combustível compatível, condições do perfil definidas e aprovação explícita no escopo solicitado. Não interpolar, extrapolar, preencher regimes ou produzir média nesta capacidade; ela fornece dados, não o modelo de consumo.

Histórico aprovado continua consultável por versão. Consumidor não recebe a versão mais recente silenciosamente quando solicitou outra. Alocação, alteração de combustível ou posição não são efeitos permitidos da consulta/promoção.

## Estrutura do projeto

- `docs/recovery/`: decisões, fontes e evidências históricas; manter links e classificações.
- `CAPABILITY_MAP.md` e `SPEC-technical-catalog.md`: índice aprovado de capacidades e esta proposta.
- `siscan-prototype/`: backend e verificadores atuais `check_*.py`.
- `siscan-prototype/tools/`: investigação/importação/registro já existentes; reaproveitar suas verificações de proveniência.
- `siscan-prototype/fixtures/engine/`: casos sintéticos versionados; futuros casos adicionais devem ser identificados como sintéticos.
- `siscan-prototype/data/` e `tmp/`: bancos, originais derivados, recibos e resultados locais fora do GitHub. Não incluir dados proprietários ou credenciais nas fixtures públicas.

## Comandos verificáveis

Executar no PowerShell, partindo da raiz do repositório. Os comandos abaixo documentam verificações existentes; não foram executados nesta etapa documental.

```powershell
$python = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Set-Location .\siscan-prototype
& $python --version
& $python check_technical_units.py
& $python check_resource_store.py
& $python check_technical_import.py
& $python check_reference_registration.py
& $python check_engine_input.py
```

Regressão completa existente, no mesmo diretório:

```powershell
Get-ChildItem -File -Filter 'check_*.py' | Sort-Object Name | ForEach-Object {
    & $python $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Falhou: $($_.Name)" }
}
```

Verificação sintática sem emitir arquivos compilados:

```powershell
& $python -c "import ast,pathlib; [ast.parse(p.read_text(encoding='utf-8'),filename=str(p)) for p in pathlib.Path('.').rglob('*.py') if 'data' not in p.parts]"
```

Desenvolvimento local: `& $python app.py`, conforme o README e com banco isolado configurado para verificação. Esse comando abre/inicializa a instância; não o executar sobre arquivos de origem nem confundir o DB3K com banco do exercício. Não há build ou linter dedicado identificado para este módulo; não inventar comandos nem instalar ferramentas nesta fase.

## Estilo de código

Preservar a organização atual, nomes Python em `snake_case`, consultas parametrizadas e verificações explícitas. Exemplo real de `technical_units.py`, ilustrando a separação entre evidência e elegibilidade:

```python
def evidence(symbol=None, status='unconfirmed', source=None, note=UNKNOWN):
    return {'unit': None, 'candidate_unit': symbol, 'display_unit': symbol,
            'status': status, 'evidence': source, 'qualification': note,
            'calculation_ready': False, 'contract_version': VERSION}
```

Uma evidência candidata não altera automaticamente `unit` nem libera cálculo. Preferir biblioteca padrão e funções pequenas às abstrações genéricas. Validação de autorização/proveniência permanece no backend. Não usar supressões ou alterar testes para ocultar lacunas.

## Estratégia de testes e aceite

Usar os verificadores atuais e fixtures controladas isoladas, sem gravar nas fontes. A futura implementação deverá cobrir cada condição abaixo com resultado esperado, incluindo recusa. Não há porcentagem de cobertura presumida; exigir cobertura demonstrável das regras e regressão existente passando.

| ID | Condição verificável |
|---|---|
| TC-01 | Fonte e derivados mantêm valores brutos; leitura/validação não alteram seus hashes |
| TC-02 | Unidade candidata, semântica desconhecida, taxa por motor/conjunto indefinida ou condição obrigatória ausente recusam elegibilidade com motivo |
| TC-03 | NULL, zero, valor negativo e código desconhecido são preservados como encontrados; interpretação/conversão inválida é recusada, não corrigida por suposição |
| TC-04 | Caso sintético completo retorna contrato elegível somente para teste; não aprova registro real |
| TC-05 | Caso real tecnicamente completo, sem aprovação explícita, permanece não elegível para uso operacional |
| TC-06 | Aprovação de identificação literal ou observação de instrutor não equivale a aprovação de unidade/taxa/perfil |
| TC-07 | Aprovação restrita a um contexto não libera outra configuração, combustível, faixa ou finalidade |
| TC-08 | Registro repetido da mesma decisão não duplica dados; nova evidência/valor/hash não reutiliza aprovação antiga silenciosamente |
| TC-09 | Versão anterior preserva seu conteúdo e sua decisão após uma nova versão; consulta explícita por versão não retorna substituição automática |
| TC-10 | Pedido de cliente tentando se autoaprovar é recusado; falha durante gravação de decisão/versão não deixa estado parcial |
| TC-11 | Operação do catálogo não cria/adjudica unidades, não altera snapshots em uso e não debita estoque ou relógio |
| TC-12 | Alteração de evidência, unidade ou aprovação é rastreável a autor/decisão/contexto; limites de consulta/autorização existentes continuam válidos |

Testes unitários verificam domínios, evidência e elegibilidade; testes SQLite isolados verificam atomicidade/idempotência/versões; testes de integração verificam os consumidores e recusa de dados pendentes. Navegador só é necessário se uma interface for alterada com escopo aprovado. Validação física é conferência independente com evidências, não resultado de teste de software ou de carga.

## Limites de atuação

- **Sempre:** consultar os documentos aplicáveis, preservar valores e versões, registrar proveniência, conferir autorização, testar caminhos de recusa e executar regressão antes de entregar código.
- **Revisar primeiro:** especificação afetada por nova regra, novo recorte físico, mudança de schema, dependência ou contrato público. Autorizações anteriores permanecem válidas em seu escopo; a revisão não reabre decisões APR aprovadas. Promoção de valor real exige decisão própria do responsável, conforme 53.
- **Nunca:** modificar originais DB3K/CMO/ATLANTICADOR, publicar bases/credenciais, atribuir unidade ou aprovação sem evidência, reduzir testes para obter sucesso ou reescrever snapshots/decisões antigos. Cópia derivada controlada não autoriza editar o original.

## Questões abertas para revisão

1. **Resolvido:** combustível/consumo aéreo confirmado como primeiro recorte pela aprovação da especificação.
2. Selecionar amostra real e evidências suficientes para comprovar escala SQL, base por motor/conjunto e condições de configuração. Nenhuma amostra foi escolhida ou aprovada por esta especificação.
3. Definir como o responsável autenticará/registrará aprovações na aplicação, preservando o registro explícito exigido em 53; não presumir que instrutor possua essa autoridade.
4. Definir critérios de comparação e tolerâncias por quantidade com base em evidência, sem adotar margem numérica universal. Divergências permanecem pendentes até resolução.

## Gate de conclusão desta fase

O responsável revisa objetivo, recorte, contrato, limites, critérios de aceite e questões abertas. Somente após aprovação da especificação em uma nova interação será produzido o plano técnico. Não foram criados plano de execução, tarefas ou código nesta fase.
