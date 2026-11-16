# Tarefas: force-confrontation — preparação dos grupamentos

**Data: 2026-11-16. Estado: especificação e plano aprovados por “siga” e “seguimos”; Fase 3 aprovada por “siga”; Fase 4 em execução.** Referências: [especificação](../../SPEC-force-confrontation.md), [plano](plan.md) e [96](../../docs/recovery/96_TAREFAS_PREPARACAO_CPC_GRUPAMENTOS.md). As ideias gráficas de [97](../../docs/recovery/97_CONCEPCAO_GRAFICA_DISPOSICAO_E_CONFRONTO.md) são frente futura, não ampliação destas tarefas.

Executar sequencialmente após aprovação desta lista, com testes de comportamento antes da implementação correspondente. Preservar `tasks/plan.md`, `tasks/todo.md` e a entrega `unit-registry` concluída. Checkpoints verificam o contrato aprovado; alteração material exige revisar a decisão afetada.

Comando focado futuro na raiz:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_cpc_group_preparation.py
```

O verificador ainda não existe. Não houve execução de testes nesta fase documental. Não iniciar servidor, build, banco ou navegador para esta fatia em memória.

## GPREP-01 — Preparar dois partidos com autorização

- [x] Implementar e verificar o fluxo válido e suas recusas de entrada. Nove testes focados passaram.
- **Aceite:** autorização pelo provedor ocorre antes de ler grupos/inventários; somente `True` estrito autoriza. Exercício/seleção inválidos, grupo de outro contexto, arquivado, revisão desatualizada ou integrante incompatível são recusados. Fluxo válido usa as operações públicas do registro e reúne somente membros selecionados de AZUL/VERMELHO, incluindo combinações naval/aéreo.
- **Verificar:** comando focado; provedor/registro instrumentados demonstram zero leitura de grupos quando não autorizado. Fixtures sintéticas usam o registro real em memória; GP-01–05, GP-11–12. Exceção do autorizador não libera consulta.
- **Dependência:** aprovação desta lista.
- **Arquivos:** `siscan-prototype/cpc_group_preparation.py`, `siscan-prototype/check_cpc_group_preparation.py`, este checklist. Pequeno, três arquivos.

## GPREP-02 — Recusar alteração observada sem preparação parcial

- [x] Implementar e verificar falha integral e conferência final de revisão. Treze testes focados passaram, incluindo revisão/arquivamento provocados durante a preparação.
- **Aceite:** falha no segundo partido não retorna dossiê parcial; revisão/arquivamento observado entre preparação e conferência final gera `GroupConflict`; nenhuma falha cria grupo, recibo, reserva, consumo ou relógio. Não usar estado/lock privado do registro nem repetir automaticamente em caso de conflito.
- **Verificar:** comando focado; mudança controlada durante chamadas públicas, sem sleeps, e comparação de inventários/consultas antes/depois. Separar alteração provocada pelo teste de qualquer efeito do preparador. GP-04–07, GP-11. Não alegar instantâneo atômico dos dois grupos.
- **Dependência:** GPREP-01.
- **Arquivos:** os dois módulos acima e este checklist. Pequeno, três arquivos.

### Checkpoint A — Contexto e preservação

- [x] Fluxo válido e recusas passam; sem acesso não autorizado ou preparação parcial.
- [x] Revisões observadas são conferidas; limite da vista consistente e ausência de reserva futura explícitos.
- [x] Inventário, grupos, recursos e fontes preservados nos caminhos que não incluem mutação provocada pelo teste.

## GPREP-03 — Congelar conteúdo e identificar o dossiê

- [x] Implementar e verificar cópias independentes e hash canônico. Vinte e um testes focados passaram, incluindo determinismo, referências atualizadas e preservação de valores desconhecidos.
- **Aceite:** snapshots integrais e referências preservados, inclusive valores desconhecidos, origem e classificação; entradas/retorno não compartilham estruturas mutáveis. Ordem de mapas não altera hash; nova versão/snapshot válida altera o conteúdo identificado. Envelope segue a especificação, exige revisão do instrutor, informa simulação não iniciada e aptidão global falsa, sem alterar classificação individual.
- **Verificar:** comando focado; editar retorno e entradas após preparação, permutar mapas, revisar composição sobre snapshot novo e conferir SHA-256 sem o próprio hash. Recusar JSON não finito/não serializável. GP-08–12; nenhuma chamada ao motor de combate ou soma de recursos heterogêneos.
- **Dependência:** GPREP-02 e Checkpoint A verificado.
- **Arquivos:** os dois módulos e este checklist. Pequeno, três arquivos.

## GPREP-04 — Conferir regressões e documentar o resultado

- [ ] Executar verificação final e registrar evidências reais.
- **Aceite:** GP-01–12 demonstrados, regressões afetadas passam, documentação distingue implementado/pendente e identifica limites de consistência, autorização interna e ausência de execução. Não presumir contagem ou aceitação por descoberta vazia.
- **Verificar:** uma vez após alterações pertinentes:

  ```powershell
  & $pythonCpc .\siscan-prototype\check_cpc_group_preparation.py
  & $pythonCpc .\siscan-prototype\check_unit_groups.py
  & $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
  git diff --check
  ```

  Descoberta CPC também incluirá o novo verificador; registrar totais sem somar duas vezes. Não repetir testes de software depois por edição meramente documental.
- **Dependência:** GPREP-03.
- **Arquivos:** `siscan-prototype/README.md`, relatório de entrega em `docs/recovery/` com número livre, este checklist, `SPEC-force-confrontation.md`, `plan.md`. Médio, até cinco arquivos.

### Checkpoint B — Preparação concluída

- [ ] GP-01–12 cobertos por verificações executadas e resultado comunicado.
- [ ] Nenhum banco, estado oficial, gráfico ou algoritmo de combate alterado; mapa definido continua preservado.
- [ ] Não apresentar preparação de forças como confronto de grupamentos já integrado.

## GPREP-05 — Atualizar controles

- [ ] Consolidar índices, riscos e continuidade com o resultado comprovado.
- **Aceite:** 00/09/10 e mapa de capacidades refletem o estado real, distinguem a futura interface de 97 e não reabrem gates já aprovados. Planos antigos permanecem idênticos.
- **Verificar:** links, hashes de preservação e `git diff --check`; sem nova bateria por documentação.
- **Dependência:** GPREP-04 e Checkpoint B verificado.
- **Arquivos:** `docs/recovery/00_LEIA-ME_RECUPERACAO.md`, `09_PENDENCIAS_E_RISCOS.md`, `10_PLANO_DE_CONTINUIDADE.md`, `CAPABILITY_MAP.md`, este checklist. Médio, até cinco arquivos.

## GPREP-06 — Sincronizar e versionar a entrega

- [ ] Sincronizar arquivos autorizados e registrar no GitHub.
- **Aceite:** códigos/docs entregues em `C:\Users\bozoc\Documents\siscan` com hashes iguais; somente o recorte é versionado, sem credenciais, fontes proprietárias ou artefatos locais de dados. Documento de entrega informa commit/limites verificáveis.
- **Verificar:** SHA-256 origem/destino, diff preparado, situação Git e resultado do envio. Se a checagem no destino for necessária, executar somente o verificador focado; não repetir toda a bateria sem motivo.
- **Dependência:** GPREP-05.
- **Arquivos:** este checklist e relatório de entrega, além da cópia dos arquivos já aprovados; sem alteração funcional. Pequeno.

## Gate

Lista de Fase 3 aprovada por “siga”; implementação em execução, sem reabrir gates anteriores. A solicitação de pensar na interface foi registrada em 97; não cria dependência que bloqueie esta fatia de backend e não autoriza mudanças silenciosas de mapa ou visibilidade.
