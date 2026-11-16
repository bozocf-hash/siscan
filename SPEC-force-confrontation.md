# Spec: force-confrontation — preparação didática de grupamentos

**Data: 2026-11-16. Estado: Fase 1 aprovada por “siga”; plano de Fase 2 proposto em 95.** O registro de grupamentos entregue em [93](docs/recovery/93_ENTREGA_GRUPAMENTOS_EM_MEMORIA.md) permanece concluído. Esta especificação acrescenta um consumidor de suas composições; não reabre os gates de `unit-registry` ou de `technical-catalog`.

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

Python 3.11+, biblioteca padrão, mantendo a estrutura existente. Implementação proposta em `siscan-prototype/cpc_group_preparation.py`, verificador em `siscan-prototype/check_cpc_group_preparation.py`. Não duplicar o registro, renomear IDs ou importar fixtures de testes no módulo de produção. Nome da função pública e assinatura concreta serão fechados no plano após aprovação do contrato funcional.

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

O novo verificador ainda não existe: estes são comandos futuros, não resultados obtidos. Na entrega canônica, os fontes ficam em `C:\Users\bozoc\Documents\siscan\prototype`. Não há build, servidor ou navegador a iniciar para este módulo em memória.

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

A proposta não inclui execução do confronto, exportador novo, gravador durável, cálculo agregado ou nova tela. A pergunta desta revisão é se a preparação rastreável das duas composições, com snapshots integrais e sem efeitos, é a próxima fatia desejada. A aprovação anterior de `unit-registry` não é aprovação automática desta especificação.

## Gate

Fase 1 aprovada pelo responsável por “siga”. [Plano de Fase 2](tasks/force-confrontation/plan.md) proposto para revisão, conforme [95](docs/recovery/95_PLANO_PREPARACAO_CPC_GRUPAMENTOS.md). Não iniciar tarefas ou código antes dos gates correspondentes.
