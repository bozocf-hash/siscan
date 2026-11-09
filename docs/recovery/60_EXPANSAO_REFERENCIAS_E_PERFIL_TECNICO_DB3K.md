# 60 — Ampliação das referências e perfil técnico DB3K

## Solicitação e limites — 2026-11-09

O responsável selecionou as prioridades 2 e 3: ampliar referências DB3K e investigar campos técnicos; confirmou depois a prioridade 2. Foram usadas as ferramentas existentes, sem alteração de código. O DB3K original foi aberto somente para leitura. A ampliação foi preparada em banco separado, sem substituir o lote de 80 candidatos exibido na aplicação e sem registrar novas referências no banco SISCAN.

A autorização anterior (55) cobre 80 referências de identificação. Os 11.117 registros adicionais aguardam decisão explícita do responsável, conforme a autoridade registrada em 53. Esta proposta não inclui atributos técnicos, unidades individuais, meios alocáveis ou cálculos.

## Cobertura da preparação

Fonte: `C:\Users\bozoc\Documents\siscan\DB3K_498.db3`; SHA-256 `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`, preservado antes/depois da leitura.

| Tabela | Registros preparados | Referências já cadastradas para essa fonte | Novas propostas |
|---|---:|---:|---:|
| DataAircraft | 6.047 | 20 | 6.027 |
| DataShip | 4.035 | 20 | 4.015 |
| DataSubmarine | 699 | 20 | 679 |
| DataGroundUnit | 416 | 20 | 396 |
| Total | 11.197 | 80 | 11.117 |

Todos os registros dessas quatro tabelas foram preparados e conferidos literalmente: ID, nome e códigos copiados foram comparados ao original. Isso não significa recuperação ou validação de todas as 167 tabelas DB3K. Os IDs temporários dos candidatos do novo lote não substituem IDs de referência já registrados; a comparação com as 80 referências usa hash da fonte + tabela + ID externo. Nomes homônimos não são fundidos.

A inspeção encontrou 44.372 correspondências literais de códigos nas tabelas Enum consultadas. Correspondência nominal sem FK não passa a relacionamento semântico confirmado. Os nomes e os registros permanecem evidências de origem, não identificação automática de modelo/configuração/unidade física.

## Perfil dos campos técnicos

Foram inventariados **77.349 valores**, em **29 pares tabela/campo**, cobrindo os mesmos campos técnicos selecionados pela ferramenta anterior. Não são todos os campos técnicos do DB3K.

| Tabela | Campos selecionados presentes | Valores brutos |
|---|---:|---:|
| DataAircraft | 6 | 36.282 |
| DataShip | 8 | 32.280 |
| DataSubmarine | 9 | 6.291 |
| DataGroundUnit | 6 | 2.496 |
| Total | 29 pares | 77.349 |

O perfil registra contagem, NULL, zero, negativos, mínimo/máximo brutos e tipos de armazenamento SQLite por campo. Nos 29 pares examinados foram encontrados **9.602 zeros**, **699 valores negativos** e **nenhum NULL**. Ausência de NULL nesse recorte não comprova preenchimento semântico nem se estende às outras colunas/tabelas. Nenhum zero foi convertido em NULL; nenhum sinal foi alterado.

| Evidência bruta | Questão para investigação |
|---|---|
| DataShip.Height: 3.620 zeros em 4.035 registros | Zero pode ter papel de ausência, padrão ou valor; significado não comprovado |
| DataShip.DisplacementEmpty: 3.349 zeros | O traço observado na ficha Ship/3 não comprova regra universal |
| DataSubmarine.MaxDepth: 699 negativos em 699 registros; extremos -6000 e -6 | Preservar sinal; unidade, domínio e aplicação exigem validação |
| DataSubmarine.Height: 465 zeros; DisplacementEmpty: 680 zeros | Não interpretar como capacidade nula |
| DataShip.Length e Beam: máximo bruto 20000; DisplacementStandard: máximo 3000000 | Examinar identidade/contexto dos registros extremos antes de classificar como erro ou grandeza física |
| DataSubmarine.Beam, Draft e Height: máximo bruto 1000 | Avaliar contexto, registros especiais e eventual apresentação; não impor limite físico por inferência |
| GroundUnit/3.MastHeight: SQL 3.26 versus interface 3 m | Causa da transformação continua pendente (59) |
| GroundUnit/3.Area: SQL 25.96 e interface 25,96 m | Unidade dimensional continua pendente; não substituir por m² |

Os 77.349 valores ficam com unidade nula e estado `pending_unit_and_semantics`, inclusive os 580 valores do lote inicial. A inspeção visual anterior permanece amostral: quatro fichas em 498a, 18 valores, 17 correspondências numéricas e uma diferença. Não extrapolar essa evidência para todos os registros do arquivo 498.

## Artefatos locais e rastreabilidade

Diretório de entrega local: `C:\Users\bozoc\Documents\siscan\prototype\data\`. Os dados completos permanecem fora do GitHub conforme a política já utilizada; este documento contém o resumo e os hashes.

| Arquivo | Função |
|---|---|
| db3k-review-expanded-02.sqlite3 | 11.197 candidatos pendentes em banco separado |
| db3k-domains-expanded-02.json | Conferência literal, códigos e valores técnicos com unidade pendente |
| db3k-technical-profile-expanded-02.json | Estatísticas brutas dos 29 pares tabela/campo |
| db3k-proposal-expanded-02.json | Proposta integral pendente de identificação de referências |
| db3k-proposal-expanded-02.md | Relação legível de candidatos, IDs, nomes e decisões pendentes |
| db3k-expansion-summary-02.json | Cobertura, diferença em relação às 80 referências e hashes |
| db3k-approval-expanded-02.pending.json | Minuta pendente, selecionando somente os 11.117 novos candidatos; não constitui aprovação |

Lote: **DB3K-48fed2847397f951**.

| Artefato | SHA-256 |
|---|---|
| Banco ampliado | 11436f0a0f9d998595ab8bbb005940e3eb98f001546e95c501545b4a8177c5de |
| Evidências | 38ab969b9fd71129896186f176e91ca5fa740c860784c912c190df8a8c8168b5 |
| Proposta JSON | a741375a972e13e3ceda2983ecf45b57477c20a12d193eb05e5041d0b3d4a64e |

## Método e verificação

Na pasta do protótipo, foram executadas as ferramentas existentes nesta sequência, sempre com destinos novos:

```text
python tools/stage_db3k.py CAMINHO_DB3K data/db3k-review-expanded-02.sqlite3 --limit-per-table 10000
python -m tools.inspect_db3k_domains CAMINHO_DB3K data/db3k-review-expanded-02.sqlite3 data/db3k-domains-expanded-02.json
python -m tools.prepare_approval_packet data/db3k-review-expanded-02.sqlite3 data/db3k-domains-expanded-02.json data/db3k-proposal-expanded-02.json
```

O limite 10000 por tabela é superior à contagem máxima encontrada (6047), portanto não truncou essas quatro tabelas. O perfil adicional foi obtido com SELECT por campo: COUNT, contagem de IS NULL, =0 e <0, MIN/MAX e agrupamento por typeof; as conexões aos bancos existentes usaram `mode=ro`. A contagem de novos candidatos foi obtida pela diferença de chaves de origem contra catalog_source_references, também em modo somente leitura.

Verificações executadas: `integrity_check=ok` do novo banco; 11.197 candidatos `needs_review`; cobertura literal de todos; hashes de fonte/amostra/evidência/proposta correspondentes; todos os candidatos com decisão pendente e nenhum campo aprovado; todos os valores técnicos com unidade nula e estado pendente; perfil com 29 pares e 77.349 valores. Asserções confirmaram 80 referências existentes e 11.117 novas propostas.

O banco ativo do protótipo apresentou `quick_check=ok`, nenhuma violação em `foreign_key_check`, 80 referências, oito meios sintéticos, zero alocações e zero submissões. Não houve escrita nele nesta etapa. Nenhum servidor foi reiniciado e nenhuma interface foi modificada. Não foram executados testes de aplicação, pois nenhuma implementação foi alterada; a verificação incidiu sobre os artefatos gerados.

## Decisão solicitada e continuidade

Proposta concreta ao responsável: cadastrar **somente os 11.117 novos registros como identificação de referência** (nome literal, tabela, ID externo e hash), preservando os 80 existentes. A minuta está vinculada ao hash da proposta acima; todas as decisões continuam pendentes. A aprovação não incluirá atributos técnicos nem alocação aos partidos.

Após decisão favorável, registrar a aprovação com escopo restrito e executar a ferramenta existente no banco SISCAN, verificando preservação dos IDs anteriores e contagem final de 11.197 referências. A troca do lote consultável na interface exige tratar o limite atual de 500 resultados e preservar as observações ligadas aos candidatos antigos; não substituir arquivos do lote atual de forma silenciosa.

A investigação técnica deve priorizar Area, MastHeight, deslocamentos, sinais/zeros e extremos, usando registros identificados e fontes específicas. As estatísticas desta etapa são triagem de dados; não constituem validação operacional ou regra de cálculo.
