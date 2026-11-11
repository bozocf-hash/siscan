# Tarefas — technical-catalog

**Estado: proposta de Fase 3 para revisão — 2026-11-11.** Mapa, especificação e [plano](plan.md) aprovados. Este arquivo é o alvo único das tarefas. Nenhuma implementação iniciada.

## Gates gerais

- [x] Fase 0: mapa aprovado em 2026-11-11.
- [x] Fase 1: especificação/recorte aéreo aprovados em 2026-11-11.
- [x] Fase 2: plano aprovado por resposta “sim” em 2026-11-11.
- [x] Fase 3: decomposição preparada para revisão.
- [ ] Fase 3: responsável aprovar esta lista antes do código.

## Convenção de execução futura

Comandos PowerShell partindo da raiz:

```powershell
$python = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Set-Location .\siscan-prototype
```

Comandos/arquivos novos abaixo são **propostos**, não verificações já executadas. Cada tarefa de código exige teste focado e regressão antes da entrega:

```powershell
Get-ChildItem -File -Filter 'check_*.py' | Sort-Object Name | ForEach-Object {
    & $python $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Falhou: $($_.Name)" }
}
```

Arquivos de código abaixo são relativos a `siscan-prototype/`; caminhos `docs/` e `tasks/` são relativos à raiz. Até cinco arquivos por tarefa; se exceder, dividir primeiro. Fixtures públicas são fictícias; evidências reais, bancos e recibos permanecem ignorados pelo Git.

## TCAT-01 — Diagnóstico puro de elegibilidade

- [ ] Implementar e verificar.

**Entrega:** referência de perfil → validação pura → contrato de diagnóstico, sem escrita.

**Aceite:**
- Recusar unidade, escala, base da taxa ou condição obrigatória ausentes, com motivos específicos; preservar NULL/zero/negativo sem corrigir por suposição (TC-02/03).
- Caso sintético completo é elegível somente para teste; caso real sem aprovação não é operacionalmente elegível (TC-04/05/06).
- Não alterar adjudicação, snapshot, relógio ou estoque nem interpolar/extrapolar regimes (TC-11).

**Verificar:** proposto `& $python check_technical_catalog.py`, entradas antes/depois e regressão.

**Depende de:** aprovação da Fase 3. **Arquivos (3):** novos `technical_catalog.py`, `check_technical_catalog.py`, `fixtures/engine/technical-catalog-cases-01.json`.

## TCAT-02 — Conferir um perfil candidato na fonte

- [ ] Implementar e verificar.

**Entrega:** leitura pelos utilitários existentes → diagnóstico rastreável do recorte, sem reextração integral.

**Aceite:**
- Identificar tabela/campo/chave, hashes e vínculos realmente encontrados por configuração/instalação (TC-01/12).
- Conservar valores e ambiguidades; taxa por motor/conjunto não comprovada permanece pendente (TC-02/03).
- Não aprovar dados nem sobrescrever fonte ou relatório existente (TC-05/11).

**Verificar:** proposto `& $python check_technical_profile_inspection.py`; `& $python check_resource_store.py`; hashes em fontes fictícias isoladas; regressão.

**Depende de:** TCAT-01. **Arquivos (3):** novos `tools/inspect_technical_profile.py`, `check_technical_profile_inspection.py`; `technical_catalog.py`.

## Checkpoint A — Diagnóstico

- [ ] TCAT-01/02 passam com recusas e preservação de fontes.
- [ ] Revisão pelo responsável do recorte, do resultado e das lacunas, sem homologar uma amostra por simples inspeção.

## TCAT-03 — Desenhar persistência aditiva

- [ ] Preparar e revisar.

**Entrega:** desenho documentado antes do DDL.

**Aceite:**
- Descrever tabelas/índices/FKs/unicidade para perfis, evidências e decisões sem remover CHECKs das tabelas brutas (TC-01/08/09).
- Definir imutabilidade, hash/contexto/autoria, escopo de decisão, transação e falhas (TC-07/10/12).
- Descrever backup, aplicação isolada, comparação e restauração; não executar migração nesta tarefa.

**Verificar:** revisão contra schema/especificação; `git diff --check`. Sem testes de software para o documento.

**Depende de:** TCAT-02 e Checkpoint A. **Arquivo (1):** novo `docs/adr/001-technical-catalog-versions.md`.

**Gate específico:** aprovar o desenho SQL/migração concreto antes da TCAT-04. Aprovar a lista não aprova DDL ainda não escrito.

## TCAT-04 — Publicar versão pendente

- [ ] Implementar e verificar.

**Entrega:** versão técnica imutável → consulta por ID/hash, sem liberação operacional.

**Aceite:**
- Repetição não duplica; mudança relevante cria versão pendente e preserva a anterior (TC-08/09).
- FK, imutabilidade e rollback impedem publicação parcial; fontes/exercício intactos (TC-01/10/11).
- Consulta não substitui versão nem libera uso por simples publicação (TC-05/09).

**Verificar:** proposto `& $python check_technical_catalog_store.py`; migração em cópia conforme ADR aprovado; integridade/FKs, EXCEPT e falha injetada; regressão.

**Depende de:** TCAT-03 e aprovação do ADR. **Arquivos (4):** novos `technical_catalog_store.py`, `check_technical_catalog_store.py`; `technical_catalog.py`; ADR (evidências).

## TCAT-05 — Verificar autoridade autenticada

- [ ] Implementar e verificar.

**Entrega:** regra de autorização por conta explicitamente designada no contexto confiável do servidor.

**Aceite:**
- Instrutor, nome em arquivo e autor enviado pelo cliente não concedem autoridade (TC-06/10).
- Identidade vem da sessão e designação da configuração confiável; ausência, inatividade ou falta de designação recusam autorização.
- Contas fictícias nos testes; nenhuma conta real/demonstrativa recebe designação automática.

**Verificar:** proposto `& $python check_catalog_authority.py`; casos positivos/negativos isolados, sem credenciais reais; regressão.

**Depende de:** TCAT-04. **Arquivos (2):** novos `catalog_authority.py`, `check_catalog_authority.py`.

## Checkpoint B — Preservação e autoridade

- [ ] TCAT-04/05 passam; restauração de cópia de teste demonstrada, além da criação de backup.
- [ ] Antes de ativar aprovação real, responsável identifica a conta e sua designação é registrada. Sem isso, nenhuma conta real é habilitada.
- [ ] Amostra, escala/base e tolerâncias físicas continuam pendentes até evidência/decisão próprias. Isso não impede testes fictícios nem constitui homologação.

## TCAT-06 — Registrar decisão contextual imutável

- [ ] Implementar e verificar.

**Entrega:** autoridade conferida → decisão vinculada à versão/hash/finalidade.

**Aceite:**
- Autor deriva do contexto autenticado, sem ampliar aprovação de identificação literal (TC-06/07/12).
- Repetição idempotente; mudança de fonte/valor/contexto não herda aprovação; histórico preservado (TC-08/09).
- Falhas não deixam decisão parcial; testes fictícios não promovem fontes reais (TC-04/10).

**Verificar:** ampliar `& $python check_technical_catalog_store.py` e `& $python check_catalog_authority.py`; falhas injetadas e concorrência em SQLite isolado; regressão.

**Depende de:** TCAT-04/05; habilitação real condicionada ao Checkpoint B. **Arquivos (3):** `technical_catalog_store.py`, `check_technical_catalog_store.py`, `check_catalog_authority.py`.

## TCAT-07 — Consultar por versão e finalidade

- [ ] Implementar e verificar.

**Entrega:** consumidor interno recebe contrato exato ou motivos de recusa.

**Aceite:**
- Exigir condições técnicas e aprovação compatível; contexto/configuração/combustível/finalidade divergentes recusados (TC-02/05/07).
- Hash alterado não reaproveita aprovação; versão ausente não retorna automaticamente a mais recente (TC-08/09).
- Manter proveniência/unidades/condições; sintético somente para teste; consulta sem efeitos no exercício (TC-04/11/12).

**Verificar:** ampliar `& $python check_technical_catalog.py` e `& $python check_technical_catalog_store.py` com consumidor fictício; regressão.

**Depende de:** TCAT-06. **Arquivos (4):** `technical_catalog.py`, `technical_catalog_store.py`, `check_technical_catalog.py`, `check_technical_catalog_store.py`.

## TCAT-08 — Conectar ao backend autenticado

- [ ] Implementar e verificar.

**Entrega:** serviços de consulta/decisão no backend, sem reformulação visual ou troca da entrada do motor.

**Aceite:**
- Registrar/revisar contrato HTTP antes de alterar rotas; sessões, origem/CSRF e autoridade explícita nas escritas, sem autoaprovação pelo pedido (TC-10/12).
- Recusar separadamente acesso indevido, corpo inválido e conflito; consulta mantém os limites atuais de acesso ao catálogo.
- Inicialização preserva dados; não criar/adjudicar meios nem alterar snapshots/estoques do motor em uso (TC-01/11).

**Verificar:** proposto `& $python check_technical_catalog_api.py`; instância HTTP isolada, contas fictícias, CSRF/payload forjado/escopo incorreto; regressão.

**Depende de:** TCAT-05/06/07 e revisão do contrato HTTP nesta tarefa. **Arquivos (4):** `app.py`, novo `check_technical_catalog_api.py`, `catalog_authority.py`, ADR (contrato da integração).

## TCAT-09 — Consolidar entrega e preservação

- [ ] Executar e verificar.

**Entrega:** percurso referência → evidência → versão → decisão → consulta documentado.

**Aceite:**
- Evidenciar TC-01–12, identificando cenários reais pendentes sem falso resultado positivo.
- Documentar backup/restauração, comparação dos registros, integridade/FKs e concorrência; originais intactos.
- Atualizar documentação e tarefas; ausência de autoridade/evidência/aprovação continua bloqueando publicação real.

**Verificar:** suíte completa, verificadores novos, comparação de artefatos locais e `git diff --check`. Procedimentos na instância em uso e promoção real exigem seus gates específicos.

**Depende de:** TCAT-01–08 e gates aplicáveis. **Arquivos (4):** novo `docs/recovery/79_CONTRATO_CATALOGO_TECNICO_VALIDADO.md`, `docs/recovery/00_LEIA-ME_RECUPERACAO.md`, `siscan-prototype/README.md`, `tasks/todo.md`. Artefatos locais ignorados não são publicados.

## Checkpoint C — Encerramento

- [ ] Responsável revisou resultados, limites e pendências reais.
- [ ] Nenhuma lacuna física foi apresentada como aprovação automática.
- [ ] Próxima capacidade segue seu ciclo de especificação; não começa por aprovação presumida desta lista.

## Sequência

TCAT-01 → 02 → Checkpoint A → 03 → aprovação do ADR → 04 → 05 → Checkpoint B → 06 → 07 → 08 → 09 → Checkpoint C.

O Checkpoint B restringe ativação real; testes fictícios de 06–08 podem continuar sem conta real designada, mantendo a instância real sem aprovador habilitado. Evidências e casos negativos podem ser investigados independentemente; contratos, schema e aprovação mudam sequencialmente. Nenhuma delegação ou implementação foi iniciada por este documento.

## Complemento recebido após preparar esta lista

O requisito de confronto/estado operativo está registrado em `docs/recovery/80_CONFRONTO_FORCAS_E_ESTADO_OPERATIVO.md` e no mapa. Pertence a `force-confrontation`/`operational-state`; não transforma a promoção de dados técnicos em decisão de confronto e não acrescenta execução automática a TCAT-01–09. A lista de tarefas de technical-catalog continua proposta, aguardando revisão; o esclarecimento do novo requisito não é sua aprovação.
