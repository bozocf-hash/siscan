# 62 — Incorporação de valores técnicos brutos ao banco SISCAN

## Autorização e escopo — 2026-11-09

O responsável respondeu **pode seguir** à proposta de incorporar os 77.349 valores brutos ao banco SISCAN com origem preservada, validação pendente e sem uso em cálculos. Essa autorização é distinta da aprovação de referências de identificação (61) e não constitui aprovação semântica de atributos.

O importador local `tools/import_technical_values.py` foi criado e executado no banco `C:\Users\bozoc\Documents\siscan\prototype\data\siscan-demo.sqlite3`. A fonte efetivamente conferida foi DB3K_498.db3, não a variante 498a observada na interface do CMO. A amostra visual de 59 permanece evidência complementar, sem generalização automática.

## Estrutura implementada

| Tabela | Conteúdo e controles |
|---|---|
| catalog_technical_imports | Hash da evidência como chave, hashes da fonte e da amostra, registro da decisão, quantidade de valores e horário UTC de incorporação |
| catalog_technical_values | Referência SISCAN, nome do campo SQL, valor bruto em JSON, tipo declarado no SQLite, unidade nula, estado pendente e vínculo ao arquivo de evidência |

A chave de cada valor é reference_id + field_name. A referência já contém versão por hash, tabela e ID externo. O vínculo ao manifesto da evidência permite recuperar sua origem. Os números são guardados sem conversão de unidade, sinal ou precisão; JSON null e zero permanecem diferentes. `sqlite_declared_type` representa o tipo declarado da coluna de origem, não uma unidade ou a classificação semântica da grandeza.

Restrições SQL exigem unit IS NULL e validation_status = `pending_unit_and_semantics`. Não se transforma uma linha de evidência em atributo aprovado por atualização de estado. Uma futura camada de atributos utilizáveis exigirá definição e validação próprias. Nenhum fluxo de cálculo ou alocação consulta essas novas tabelas.

O esquema é incluído também na inicialização da aplicação para bancos novos. O importador exige banco de destino existente com referências SISCAN, recusa arquivos de origem como destino e não cria referências ou meios.

## Conferência e transação

Antes da escrita, o importador executa novamente `inspect_domains` contra a fonte e a amostra, comparando a identificação, códigos e todos os campos técnicos com o arquivo de evidência. Campos com unidade atribuída, estado aprovado ou valores divergentes são recusados. As referências correspondentes devem existir para a mesma origem e nome literal. Os hashes das entradas são conferidos durante a preparação.

A criação das tabelas, o registro da importação e os valores são gravados em uma transação com chaves estrangeiras ativadas. Reexecução com as mesmas entradas não duplica valores. Conflitos com valores/evidências já armazenados causam erro e reversão, sem substituição automática.

Execução local, na pasta do protótipo:

```text
python -m tools.import_technical_values CAMINHO_DB3K CAMINHO_AMOSTRA EVIDENCIAS.json BANCO_SISCAN --decision-record "Registro da autorização de incorporação bruta pendente"
```

O texto de decisão é registro administrado pelo operador local; não é assinatura digital nem nova autorização via interface.

## Resultado no banco ativo

| Origem | Valores incorporados |
|---|---:|
| DataAircraft | 36.282 |
| DataShip | 32.280 |
| DataSubmarine | 6.291 |
| DataGroundUnit | 2.496 |
| Total | 77.349 |

São os 29 pares tabela/campo selecionados da inspeção de 60, não todos os atributos das 167 tabelas DB3K. Permanecem **77.349 valores pendentes**, **zero com unidade confirmada** e **zero promovidos para uso operacional/didático**.

As contagens preservadas são 9.602 zeros, 699 negativos e nenhum NULL neste lote específico. A ausência de NULL não significa completude semântica. Não houve alteração de Area, MastHeight, MaxDepth ou de deslocamentos para conciliar diferenças de apresentação.

## Verificação executada

O teste novo `check_technical_import.py` foi escrito antes do importador; inicialmente falhou pela ausência do módulo e depois passou. Cobre valor fracionário, NULL, zero, sinal, evidência adulterada, referência ausente, restrições de estado/unidade, idempotência, preservação de fontes/meios e reversão em conflito após inserção parcial.

Todos os sete scripts `check_*.py` passaram, incluindo os testes existentes de submissão, avaliação/liberação, isolamento entre partidos, notificações, catálogo e registro de referências. Não houve alteração de tela ou API de consulta, portanto não foi realizado teste visual de novos controles.

Na execução real, foram verificados:

- 77.349 linhas inseridas, todas pendentes e com unidade nula; as contagens por tabela e de zeros/negativos/NULL correspondem ao perfil anterior.
- `integrity_check=ok` e nenhuma violação em `foreign_key_check`.
- Comparação integral antes/depois de catalog_source_references, catalog_reference_approvals, assets, party_allocations, asset_allocations, submissions, catalog_review_notes e events: nenhuma mudança.
- Preservação de 11.197 referências, dois registros de aprovação, oito meios sintéticos, zero alocações, zero submissões, zero notas de revisão e dois eventos didáticos.
- Hashes das entradas correspondentes antes/depois e backup consistente anterior à escrita.

## Rastreabilidade e arquivos locais

| Entrada/backup | SHA-256 |
|---|---|
| Fonte DB3K_498.db3 | 1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d |
| db3k-review-expanded-02.sqlite3 | 11436f0a0f9d998595ab8bbb005940e3eb98f001546e95c501545b4a8177c5de |
| db3k-domains-expanded-02.json | 38ab969b9fd71129896186f176e91ca5fa740c860784c912c190df8a8c8168b5 |
| siscan-before-technical-import-02.sqlite3 | 39436b8af0c84e00d5601873cd427fa129e0fc0b6cb4201d841f37e91266662a |

O recibo `db3k-technical-import-receipt-02.json` e o backup anterior ficam em `C:\Users\bozoc\Documents\siscan\prototype\data\`, fora do GitHub. O backup contém dados locais do protótipo e não deve ser publicado. Os arquivos originais de evidência foram preservados.

## Limites e próximo incremento

Os valores já podem ser consultados nas tabelas do banco para revisão, ligados à origem. A interface continua usando o lote inicial e o arquivo de evidência anterior: ainda não oferece navegação dos 77.349 valores incorporados. Não foi reiniciado o servidor nesta etapa, pois o importador criou as tabelas diretamente e nenhum comportamento de tela foi alterado.

A próxima evolução é a consulta paginada de referências e valores pendentes pelo instrutor, preservando controle de acesso e notas antigas. Validar unidades/domínios e resolver as divergências continua sendo trabalho separado. Incorporação bruta não autoriza cálculos, recomendação automática ou alocação de registros DB3K como unidades físicas.
