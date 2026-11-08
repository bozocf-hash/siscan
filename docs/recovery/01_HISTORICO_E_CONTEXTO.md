# 01 — Histórico e contexto

## Propósito e proveniência

**DECIDIDO — contexto Missão 01:** SISCAN (Sistema de Simulação e Análise de Combate Naval) é iniciativa em pré-desenvolvimento para simulação didática, análise e apoio ao ensino, integrada ao ATLANTICADOR. Command: Modern Operations (CMO) é referência conceitual. A prioridade é preservar decisões e separar concepção de implementação.

O histórico de conversas anterior não está presente no workspace. Assim, os objetivos e decisões abaixo foram transcritos/organizados do contexto consolidado fornecido, e não validados contra atas ou conversas originais. Artefatos DB3K presentes indicam trabalho anterior de inventário; isso não comprova autoria, data, versão do banco em uso ou inspeção reproduzível nesta sessão.

## Evolução conceitual consolidada

- **DECIDIDO:** aproveitar componentes existentes do ATLANTICADOR, evitando reescrita desnecessária; não presumir implementação por ter sido planejada.
- **DECIDIDO:** organização modular GEO, SYM, AST, SCN, FOR, DID, SIM, ANA, NAV, LOG, PRC, HIS e MPNL.
- **DECIDIDO:** simulação para ensino e adjudicação humana, sem recomendação operacional de emprego de armamentos.
- **DECIDIDO:** deslocamento temporal inicial sem exigir rotas detalhadas; combustível dinâmico e validação costeira independente do mapa-base.
- **DECIDIDO:** PRC didático configurável sem fórmula ou coeficiente definitivo; First Strike é hipótese de cenário.
- **DECIDIDO:** MPNL bottom-up, necessidades primeiro e preços depois, em bases técnica, logística e econômica relacionadas, porém independentes.
- **DECIDIDO:** hierarquia de quatro níveis para cada força; Exército sem nível de subunidade; nomenclatura da Força Aérea provisória.
- **DECIDIDO:** aluno não visualiza submissões de outros alunos até liberação do instrutor.
- **PLANEJADO:** primeira demonstração permite instrutor criar cenário e recursos, aluno organizar forças e justificar decisões, instrutor avaliar e sistema consolidar relatório.

## Premissas e cautelas

**DECIDIDO:** distinguir existente, parcial, planejado, não especificado e a verificar. **NÃO VERIFICADO:** estado real do produto e correspondência entre artefatos atuais e concepções anteriores. Os seis artefatos no workspace estão sem rastreamento Git (`git status --short` os marcou como untracked); foram preservados sem edição. Não há histórico de alterações para atribuir autoria ou momento.

Ver [09 — Pendências e riscos](09_PENDENCIAS_E_RISCOS.md) para lacunas que impedem declarar a recuperação integral.
