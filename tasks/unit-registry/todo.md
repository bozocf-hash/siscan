# Tarefas: unit-registry — grupamentos diretos

**Estado: Fase 3 aprovada em 2026-11-16, por “sim”; Fase 4 em execução.** [Especificação](../../SPEC-unit-registry.md), [plano](plan.md) e esta lista foram aprovados em interações distintas. Preservar as tarefas abertas de `technical-catalog` em `tasks/plan.md` e `tasks/todo.md`.

## Regras da execução futura

Executar na ordem abaixo, com testes de aceite/recusa antes de considerar cada tarefa concluída. Primeiro recorte em memória e com fixtures controladas. Nenhum endpoint, DDL, dependência ou integração física é autorizado por esta lista. Cada tarefa inclui o próprio registro de andamento em `todo.md`; os arquivos prováveis ficam dentro do limite de cinco por tarefa.

Comando focado, partindo da raiz do repositório no PowerShell:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_unit_groups.py
```

O verificador ainda não existe. Seu comando só será executado depois da criação de testes na implementação; não substituir por descoberta de zero testes. Não há servidor/build/navegador para iniciar nesta fatia.

## UGR-01 — Criar e consultar composição verificada

- [x] Implementar e verificar.
- **Resultado:** registro privado `RegistroGrupamentos`, contexto, visão de unidades, JSON canônico/hashes, criação e consulta atual/histórica.
- **Aceite:**
  - Criar grupo naval heterogêneo e grupo aéreo com designação “esquadrilha”, preservando IDs/snapshots e sem inferir escalão MPNL.
  - Recusar contexto, disponibilidade, domínio, snapshot ou entrada inválidos; duplicidade/disputa não publica versão, vínculo ou recibo parcial.
  - Reenvio idêntico retorna a versão original; chave com outra intenção conflita; consulta/retorno não permite revelar outro contexto ou editar estado privado.
- **Verificação:** comando focado acima e `git diff --check`; conferir entradas antes/depois e UG-01–05, UG-08–10, UG-12–14. Fixtures mantêm dados sintéticos e aprovação técnica separados.
- **Dependências:** aprovação desta lista.
- **Arquivos prováveis:** `siscan-prototype/unit_groups.py`, `siscan-prototype/check_unit_groups.py`, este checklist.
- **Escopo:** pequeno, até três arquivos.

## UGR-02 — Revisar composição preservando versões

- [x] Implementar e verificar.
- **Resultado:** substituição completa dos membros/metadados com `expected_revision`, referências históricas e troca dos vínculos ativos.
- **Aceite:**
  - Publicar nova revisão somente sobre a revisão esperada, preservando conteúdo/hash anteriores; remoções/adições alteram vínculos junto com a publicação.
  - Reenvio não duplica; falha não libera/reserva integrantes parcialmente; reordenação da mesma intenção preserva sua representação canônica.
  - Duas revisões concorrentes sobre a mesma revisão produzem uma publicação e um conflito sob lock do mesmo processo.
- **Verificação:** comando focado e `git diff --check`; UG-05–10, UG-12–14. Teste concorrente com sincronização controlada, sem depender de atraso/sleep para decidir resultado.
- **Dependências:** UGR-01.
- **Arquivos prováveis:** `siscan-prototype/unit_groups.py`, `siscan-prototype/check_unit_groups.py`, este checklist.
- **Escopo:** pequeno, até três arquivos.

### Checkpoint A — Criação e revisão

- [x] Fluxos de criação/consulta/revisão e recusas passam no verificador focado.
- [x] Não há estado parcial ou informação de outro contexto nos caminhos de erro.
- [x] IDs, recursos/snapshots de entrada e histórico permanecem preservados; resultado comunicado antes da etapa seguinte. Checkpoint A verificado com 14 testes focados.

## UGR-03 — Arquivar e liberar vínculos diretos

- [ ] Implementar e verificar.
- **Resultado:** revisão inativa, sem apagar o grupo, suas versões ou as unidades.
- **Aceite:**
  - Arquivar com revisão esperada cria versão inativa e libera integrantes para outro grupo ativo, mantendo referências históricas consultáveis.
  - Reenvio idêntico não duplica; revisão desatualizada, intenção conflitante ou contexto incorreto não altera vínculos/recibos.
  - Grupo inativo não recebe revisão ou reabertura neste recorte; preparação deverá recusá-lo ao ser implementada em UGR-04.
- **Verificação:** comando focado e `git diff --check`; UG-06–08, UG-10, UG-12–15. Demonstrar reutilização legítima do integrante sem duplicar inventário.
- **Dependências:** UGR-02 e Checkpoint A verificado.
- **Arquivos prováveis:** `siscan-prototype/unit_groups.py`, `siscan-prototype/check_unit_groups.py`, este checklist.
- **Escopo:** pequeno, até três arquivos.

## UGR-04 — Preparar composição com disponibilidade atual

- [ ] Implementar e verificar.
- **Resultado:** snapshot de referências da composição e manifesto da visão usada, sem iniciar CPC ou publicar efeitos.
- **Aceite:**
  - Conferir grupo/revisão ativos e inventário atual; indisponibilidade, mudança de configuração/snapshot ou dados obrigatórios ausentes produzem recusa explícita.
  - Não substituir referências silenciosamente; hash/recibo de criação antigo não autoriza disponibilidade atual; grupo arquivado é recusado.
  - Retorno não modifica versão, alocação, combustível, munição, relógio ou aprovação técnica; edição do retorno não altera o registro.
- **Verificação:** comando focado e `git diff --check`; UG-03–04 e UG-11–15. Comparar entradas/registro antes e depois tanto no aceite quanto na recusa.
- **Dependências:** UGR-03.
- **Arquivos prováveis:** `siscan-prototype/unit_groups.py`, `siscan-prototype/check_unit_groups.py`, este checklist.
- **Escopo:** pequeno, até três arquivos.

### Checkpoint B — Ciclo completo

- [ ] Criar → consultar → revisar → preparar → arquivar funciona no mesmo contexto com histórico intacto.
- [ ] Reenvios, disputa de integrante, revisão desatualizada e perda de disponibilidade mantêm os invariantes.
- [ ] Todos os critérios UG-01–UG-15 estão ligados a verificações reais; não há alegação de autenticação, persistência ou validação física implementadas.

## UGR-05 — Conferir preservação e documentar a entrega

- [ ] Executar e registrar a verificação final.
- **Resultado:** evidência do recorte implementado, exemplos controlados e comandos reproduzíveis.
- **Aceite:**
  - Verificador focado e regressões afetadas passam; não há modificação de bancos, originais ou recursos do exercício.
  - Documentar comportamento, falhas esperadas, limites em memória e status real de cada critério, sem apresentar o módulo como CPC oficial integrado.
  - Registrar quantidade efetiva de testes e resultado das verificações; não fixar contagem presumida nem silenciar falhas.
- **Verificação final, uma vez após as mudanças pertinentes:**

  ```powershell
  & $pythonCpc .\siscan-prototype\check_unit_groups.py
  & $pythonCpc .\siscan-prototype\check_engine_units.py
  & $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
  git diff --check
  ```

  O verificador existente de unidades usa SQLite `:memory:`. Os testes novos de grupo não deverão abrir banco real. Repetir/ampliar verificações somente quando nova alteração, falha ou preocupação concreta justificar.
- **Dependências:** UGR-04 e Checkpoint B verificado.
- **Arquivos prováveis:** `siscan-prototype/README.md`, futuro relatório de entrega em `docs/recovery/`, este checklist.
- **Escopo:** pequeno, até três arquivos. O número/nome do relatório será escolhido sem sobrescrever documentação existente.

## UGR-06 — Consolidar os controles do projeto

- [ ] Atualizar e conferir a documentação final.
- **Resultado:** índices/pendências/continuidade refletem a entrega comprovada e distinguem o que ainda não foi integrado.
- **Aceite:**
  - Referenciar a entrega e seus limites em 00, 09, 10 e no mapa de capacidades; manter IDs e o ciclo independente do catálogo.
  - Conferir links, diff e ausência de alterações nos planos antigos; não reapresentar gates já aprovados como pendentes.
  - Sincronizar os arquivos autorizados e registrar no Git apenas o recorte, sem fontes proprietárias, credenciais ou resultados locais em `data/`.
- **Verificação:** links locais, hashes/diff de preservação e `git diff --check`; não repetir testes de software por edição meramente documental após UGR-05 aprovado nos testes.
- **Dependências:** UGR-05.
- **Arquivos prováveis:** `docs/recovery/00_LEIA-ME_RECUPERACAO.md`, `docs/recovery/09_PENDENCIAS_E_RISCOS.md`, `docs/recovery/10_PLANO_DE_CONTINUIDADE.md`, `CAPABILITY_MAP.md`, este checklist.
- **Escopo:** médio, até cinco arquivos.

## Gate antes do código

Gate da Fase 3 satisfeito pela aprovação acima; Fase 4 em andamento. Checkpoints são verificações do contrato aprovado, não aprovação de novo escopo; qualquer alteração material exige revisar a decisão afetada antes de implementá-la.

As tarefas marcadas acima foram implementadas e verificadas. As demais permanecem pendentes; não há alteração de banco ou estado do exercício.
