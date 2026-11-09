# 74 — Previsão de consumo por perfil temporal

**Complemento em 75:** [75](75_ALERTAS_NIVEL_MINIMO_COMBUSTIVEL.md) acrescenta à prévia o mínimo definido pelo operador, sua versão no manifesto, linha tracejada e instante de cruzamento. A previsão permanece sem débito; os resultados e hashes registrados abaixo referem-se à entrega 74 anterior a esse complemento.

## Contrato do incremento — 2026-11-09

Prévia exclusiva do instrutor atribuído, baseada em uma unidade da execução corrente e sua revisão. Sequência de até 24 trechos, cada um com regime sintético e duração inteira positiva, total máximo de 1440 min. IDs, unidades e taxas vêm de fixture fixada pelo backend; cliente não envia taxas. Unidades de massa em gramas no cálculo e kg na apresentação; tempo em minutos.

Regimes hipotéticos, sem correspondência operacional: econômico de teste (0,5 kg/min), referência de teste (2 kg/min) e intensivo de teste (4 kg/min). Não são inferências Command nem alteram a taxa constante da execução existente. Servem para verificar ordenação temporal, demanda, esgotamento e unidades do contrato. Não são curvas físicas aprovadas.

GET `/api/engine-profile-contract`: conjunto sintético e manifesto. POST `/api/engine-profile-preview`: `run_id`, `unit_id`, `expected_revision`, `segments` com `regime_id` e `minutes`. Exigir sessão, origem e CSRF. Recusar revisões antigas, execuções históricas/incompatíveis, unidades fora do exercício e valores/campos inválidos. Não aceitar valores de combustível fornecidos pelo cliente.

Retornar demanda por trecho, acumulado, combustível disponível projetado, déficit explícito, curva e manifesto da prévia (contrato/algoritmo/plano/execução/revisão/snapshot). A curva representa combustível disponível: alcança zero no instante calculado do esgotamento e permanece em zero, enquanto a demanda não atendida aparece separadamente. O instante fracionário serve apenas à apresentação; os débitos por trecho são inteiros exatos.

Nenhuma alteração de saldo, relógio, ledger, snapshots ou cenário. Não há botão de execução do perfil. Resultados são uma previsão vinculada à revisão consultada, não reserva ou garantia de saldo futuro. Qualquer alteração do plano deve invalidar a prévia exibida. Esta fatia prepara o contrato; conectar perfis a débitos exige incremento próprio com idempotência e versionamento das taxas.

## Entrega

`engine_profiles.py` valida o contrato e calcula a demanda exata em gramas. `fixtures/engine/synthetic-profiles-01.json` tem SHA-256 canônico fixado: `1cd0f7ba3ac0b20ae3e3900a2702563d71329ed08d5fc6ffc3da2a3712b0e3d4`. Divergência do conjunto é recusada. A validação também confere o snapshot da unidade, seu vínculo ao manifesto da execução e o contrato sintético original. Não há alteração do schema nem migração neste incremento.

`app.py` executa a prévia em transação de leitura, mantendo uma visão consistente do saldo/revisão. Respostas: 400 para plano inválido, 403 para acesso indevido, 409 para execução/revisão incompatível e 503 para falha de conferência da fonte/estado. Campos extras, taxas enviadas pelo cliente, combustível fornecido pelo cliente, regimes desconhecidos, duração booleana/fracionária, intervalos inválidos e excesso de trechos/duração são recusados. A revisão da execução é uma base consultada; não fica bloqueada para ações posteriores à resposta.

`static/engine-profiles.js` apresenta seleção de unidade, adição/remoção de trechos, taxas/unidades, curva SVG e tabela equivalente. Abre em “Unidades de teste do motor → Prever perfil de consumo”. O manifesto fica disponível em seção recolhível. Ao editar unidade ou plano, o resultado anterior é removido; resposta atrasada não restaura uma previsão de plano já editado. Novo avanço da execução exige atualizar o estado e recalcular. Plano e previsão não são persistidos pelo módulo.

A curva mostra combustível disponível, não demanda atendida após o esgotamento. O déficit é separado da quantidade disponível; nenhum número negativo é gravado como saldo. Tempo do perfil é futuro e relativo ao saldo-base; não é o relógio atual do ensaio. “Viável” significa somente demanda de combustível coberta nesta hipótese, sem validar alcance, velocidade, aeronavegabilidade, missão, payload ou prontidão operacional.

## Verificação — 2026-11-09

- Passaram os 18 scripts Python. `check_engine_profiles.py` cobre demanda ordenada por trecho, cálculo determinístico, conservação do banco por comparação de dump/contador de alterações, esgotamento exato e fracionário, déficit, domínio/campos inválidos, acesso por papel e conflito por revisão antiga. Também verifica respostas 200/400/403/409 do handler.
- Exemplo isolado com saldo inicial de 600 kg: 10 min a 0,5 kg/min + 20 min a 2 kg/min + 5 min a 4 kg/min = 35 min e demanda de 65 kg, com saldo projetado de 535 kg. Taxa constante anterior não é substituída por estes regimes.
- Edge/Playwright em cópia isolada e aplicação local: com saldo-base de 510 kg, plano de 35 min prevê 65 kg e saldo de 445 kg. Editar o primeiro trecho para 11 min prevê 65,5 kg e remove a curva anterior antes do recálculo. Plano de 130 min a 4 kg/min demanda 520 kg: disponível final zero, déficit 10 kg, esgotamento aos 127,5 min.
- Foram conferidos tabela, curva, controles nativos com rótulos, invalidação do resultado, recusa de revisão incompatível, CSRF, papéis e consulta com parâmetros indevidos. Tela de 390 px sem transbordamento da página; tabela ampla tem rolagem própria. Nenhuma exceção JavaScript. Diagnóstico de entrada do motor continuou passando.
- Backup consistente anterior: `prototype/data/siscan-before-engine-profiles-15.sqlite3`. Comparação bidirecional EXCEPT de todas as linhas das 23 tabelas anteriores conferidas, excluindo sessões transitórias: nenhum registro adicionado, removido ou alterado. Schema também idêntico. Cenário, alocações, snapshots, ledger, eventos e saldos preservados. Execução atual permanece em 45 min, revisão 1, 510 kg por unidade.
- `integrity_check=ok`, zero violações FK. DB3K original, compilação 06 e recursos 09 mantêm os hashes anteriores. Nenhuma fonte Command foi modificada ou aprovada.
- Recibo local `prototype/data/engine-profile-preview-receipt-15.json`, SHA-256 `5b5b0999f026d09d12aba6550ca77bc351a720585f8b0ab734b312780bc10896`. Manifesto do exemplo viável: `7db237efc1ac03bfe05f52706aed197d7fe89f2fd9f00b606d9c0363faa8cc54`. Código/testes/fixture sintética são versionados; bancos, recibos e backups ficam fora do GitHub.

## Pendências

Esta entrega não aplica o perfil ao estoque. A próxima fatia deverá fixar contrato de taxas/regimes na execução e registrar o débito do perfil completo em uma transação idempotente, com recusa integral se houver insuficiência. Não reutilizar silenciosamente o comando de consumo constante para taxas diferentes.

Antes de qualquer uso Command: comprovar unidade/escala, fluxo por motor/conjunto, regimes e configurações, efeitos de carga e compatibilidade do combustível; aprovação e calibração próprias permanecem obrigatórias. Este incremento não resolve essas lacunas de 66/69 nem produz curvas físicas de plataformas reais.
