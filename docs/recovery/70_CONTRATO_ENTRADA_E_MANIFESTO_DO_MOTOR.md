# 70 — Primeiro contrato de entrada e manifesto do motor

**Continuidade:** [72](72_ESTADO_RELOGIO_E_CONSUMO_TRANSACIONAL.md) acrescenta execução sintética separada do diagnóstico deste documento. O diagnóstico continua sem avançar tempo por si; seu indicador agora informa se há execução visível iniciada. O contrato de entrada e seus hashes permanecem preservados.

**Continuidade:** as unidades individuais e snapshots do próximo passo foram entregues em [71](71_IDENTIDADE_CONFIGURACAO_E_SNAPSHOT_UNIDADES.md), sem iniciar consumo ou execução.

## Escopo — 2026-11-09

Implementar a primeira entrega da sequência 69: validar um conjunto sintético controlado de entradas e identificar suas versões/hashes. Não implementar avanço de tempo, consumo, estoque, movimentação ou promoção de dados Command nesta etapa.

Critérios: campos obrigatórios e esquema explícitos; valores finitos com domínio definido; unidades canônicas exatas; combustível inicial não superior à capacidade; identidade/configuração sintéticas; manifesto confiável fornecido pelo backend, nunca pelo cliente; recusa de alteração de dados/versões e de alegação de aprovação dentro do próprio payload. O aceite vale apenas para teste sintético do contrato.

Conferir também a compatibilidade estrutural entre fonte original, compilação, base de recursos e versão/construtor, separadamente da prontidão física. Base Command compatível não é automaticamente apta para cálculos. Arquivo faltante ou incompatível precisa de diagnóstico explícito, sem bloquear o teste sintético independente.

Expor diagnóstico somente leitura ao instrutor atribuído, conforme política existente. A tela deve mostrar os dados sintéticos, o aceite do contrato e as pendências dos dados Command, sem afirmar que o motor já está simulando.

## Contrato entregue

`engine_input.py` define `siscan-engine-input-01` e o conjunto de teste `synthetic-fuel-01`. A fixture própria fica em `fixtures/engine/synthetic-fuel-01.json`, versionada no repositório. Não contém dados Command e não cria um meio alocável.

| Entrada sintética | Valor | Unidade exata | Domínio |
|---|---:|---|---|
| Capacidade | 1000 | kg | Maior que zero |
| Combustível inicial | 600 | kg | Não negativo e não superior à capacidade |
| Taxa de consumo | 2 | kg/min | Não negativa |
| Duração de referência | 30 | min | Maior que zero |

Esses valores são arbitrados para testar o contrato, não taxas reais ou parâmetros padrão do SISCAN. Não há conversão implícita de unidades. Campos adicionais, números não finitos, booleanos como quantidade, medidas incompletas, identidades não sintéticas e alegações de aprovação dentro da entrada são recusados.

O manifesto é construído pelo backend e inclui versão de esquema/regras, identidade e hash do conjunto, escopo e hash do código do contrato. A identidade e o conteúdo esperado do conjunto são fixados no código; um cliente não pode mudar o dado e fornecer seu próprio hash para aprová-lo. O hash do JSON usa chaves ordenadas, representação compacta, UTF-8 e recusa de valores não finitos. O hash do código normaliza finais de linha para LF. Não se trata de assinatura digital.

O validador retorna erros estruturados com `field`, `code` e `message`. `accepted=true` significa somente `accepted_for=synthetic_contract_test`, mantendo `official_calculation_ready=false`. Nesta entrega, apenas o conteúdo do conjunto controlado é aceito; mesmo uma alteração numericamente plausível, como trocar 600 por 599, requer outro conjunto/manifesto confiável. Não há endpoint de ingestão/promoção de dados de cliente.

## Compatibilidade entre bases

O diagnóstico calcula os hashes efetivos do DB3K original, compilação 06 e recursos 09, em consultas somente leitura, e confere seis condições:

1. Compilação identifica o hash da origem disponível.
2. Base de recursos identifica a mesma origem.
3. Hash efetivo da compilação coincide com `build.compiled_sha256` dos recursos.
4. Construção da base de recursos está completa.
5. Contrato de unidades coincide com a versão da aplicação.
6. Código do construtor/leitor de recursos coincide com `build.builder_sha256`.

O resultado real desta entrega foi compatível nas seis condições. `structurally_compatible=true` continua separado de `official_calculation_ready=false`: não valida unidades físicas ou taxas/massas. Arquivo ausente, metadados ilegíveis ou incompatibilidade geram diagnóstico negativo explícito; o teste sintético pode continuar independente. A conferência ocorre sob solicitação do instrutor, não em cada leitura de ficha.

Essa entrega fecha a conferência cruzada de arquivos no diagnóstico. Ainda não existe ativação de execução que imponha um manifesto imutável/snapshot e valide todas as dependências de um motor real. ED-09 de 69 permanece parcialmente atendido, não concluído para simulação.

## Interface e acesso

`GET /api/engine-readiness`, sem parâmetros, retorna `synthetic_input`, `validation`, `catalog`, `simulation_started=false` e a qualificação de escopo. Consulta anônima recebe 401; aluno, avaliador e instrutor não atribuído recebem 403. Parâmetros fornecidos pelo cliente são recusados com 400, sem aceitar manifesto ou caminhos arbitrários. Não há nova permissão ou escrita de estado.

O instrutor pode abrir **Preparação do motor** no Catálogo técnico, ver as entradas/unidades, aceite, condições das bases e manifesto. A atualização é manual. O painel mantém o aviso de que não ocorreu simulação, consumo, baixa de estoque ou aprovação de dados Command; as fichas e os fluxos existentes foram preservados.

## Verificação e evidência

Os 14 verificadores Python passaram. `check_engine_input.py` cobre entrada correta, imutabilidade/repetibilidade, campos/versão/fonte indevidos, tentativa de autoaprovação, unidades incompatíveis, booleano, NaN, inteiro fora da representação finita, taxa negativa, duração zero, excesso de capacidade e conteúdo divergente do manifesto. Também cobre arquivo ausente, hash de compilação incompatível, versão de unidades divergente, fonte preservada e autorização do diagnóstico.

Edge conferiu painel, unidades, seis condições reais, hash do conjunto, atualização manual, tela de 390 px, ausência de simulação, 401/403 e recusa de parâmetros de cliente. Os testes de armamento/payload anteriores também passaram. Não foi feito teste de precisão física ou concorrência do motor, pois o motor ainda não foi executado.

Relatório local: `prototype/data/engine-input-readiness-11.json`, fora do GitHub. SHA-256: `9a8dbf39acd61a3a30c7194268a32d42dceec62cd3c03576799def6cdffd79a2`. Hash canônico do conjunto sintético: `ffd1a7740e037a6cdec662660150adada04d0e0f4a0941128f49a0b85aa4abe7`. Hash do código do contrato na emissão: `8b6dfe811f6da53f86f60bb757eeab36419aae90a5411607a4ed5bbb6f67a555`.

DB3K, compilação, recursos e dados operacionais foram preservados; nenhuma aprovação técnica, alocação ou cálculo operacional foi introduzido. A próxima entrega da sequência 69 é a identidade/configuração e snapshot de uma unidade por partido, antes do estado transacional e avanço de tempo.
