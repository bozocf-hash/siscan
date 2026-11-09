# 61 — Aprovação e registro das referências DB3K ampliadas

## Decisão do responsável — 2026-11-09

O responsável respondeu **sim** à pergunta explícita sobre cadastrar as **11.117 novas referências somente com nome, tabela, ID externo e origem**, preservando o escopo da proposta 60. A decisão aprova identificação de referência, sem atributos técnicos, unidades individuais, meios alocáveis ou cálculos. Não altera a regra de disponibilização por partido.

Lote aprovado: `DB3K-48fed2847397f951`. A proposta contém 11.197 candidatos, mas o manifesto seleciona somente os 11.117 novos, identificados pela diferença de chaves de origem em relação às 80 referências existentes.

| Registro | SHA-256 |
|---|---|
| Fonte DB3K_498.db3 | 1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d |
| Proposta JSON aprovada no escopo de identificação | a741375a972e13e3ceda2983ecf45b57477c20a12d193eb05e5041d0b3d4a64e |
| Manifesto de aprovação | 83b89b7235ed61a853e2acef7241fb3530d99d759e357c2544f75cdda481bc52 |
| Backup anterior ao registro | 45c428a6af804ed58e731429e5affe57b500923e3d42719b9e60518cf2ee0378 |

O manifesto é um registro administrado pelo operador local a partir da decisão expressa nesta conversa, não uma assinatura digital ou nova função de autorização na interface.

## Execução e resultado

Destino: `C:\Users\bozoc\Documents\siscan\prototype\data\siscan-demo.sqlite3`. Antes da escrita, foi criado backup consistente com a API SQLite backup, a partir de conexão somente leitura. O original DB3K não foi destino de escrita.

A ferramenta existente `tools.register_source_references.register_references` registrou **11.117 referências novas**. A reexecução com o mesmo manifesto registrou **zero**, confirmando idempotência neste lote. Os 80 registros anteriores foram comparados integralmente antes/depois e preservaram IDs, nomes, proveniência e vínculo à aprovação original.

| Tabela de origem | Total de referências cadastradas |
|---|---:|
| DataAircraft | 6.047 |
| DataShip | 4.035 |
| DataSubmarine | 699 |
| DataGroundUnit | 416 |
| Total | 11.197 |

O banco contém dois registros de aprovação: o lote inicial e a ampliação. Cada referência possui ID SISCAN próprio, separado do ID externo. A identidade de origem permanece hash + tabela + ID externo; nomes homônimos não foram fundidos.

## Verificações e preservação

- O teste existente `check_reference_registration.py` passou antes da execução, cobrindo escopo explícito, IDs estáveis, idempotência, ausência de criação de meios e preservação dos arquivos de entrada.
- Os hashes da proposta e da fonte corresponderam ao esperado antes/depois.
- O banco final retornou `integrity_check=ok` e nenhuma violação em `foreign_key_check`.
- Foram comparadas todas as linhas de assets, party_allocations, asset_allocations, submissions, catalog_review_notes e events antes/depois: nenhuma mudança.
- Permaneceram oito meios sintéticos, zero alocações, zero submissões, zero notas de revisão e dois eventos. O registro da decisão está nas tabelas de aprovação/referências; a ferramenta não acrescentou evento didático.
- Não houve alteração de código, servidor, amostra DB3K ou evidência técnica.

## Arquivos locais

Em `C:\Users\bozoc\Documents\siscan\prototype\data\`:

- `db3k-approval-expanded-02.approved.json`: aprovação explícita vinculada ao hash da proposta e aos 11.117 novos candidatos.
- `db3k-registration-expanded-02.json`: recibo da execução e verificações.
- `siscan-before-expanded-registration-02.sqlite3`: backup anterior à escrita; contém os dados locais do protótipo e permanece fora do GitHub.

A minuta `.pending.json`, a proposta e o resumo gerados na preparação foram preservados como registros daquele estágio; seus estados pendentes não substituem esta decisão posterior. O manifesto aprovado e o recibo são arquivos adicionais.

## Limites e continuidade

A aprovação cobre **referências de identificação**, não aprovação semântica dos 77.349 valores técnicos. Esses valores permanecem em artefatos separados, com unidade nula e estado pendente; as divergências de 59 e a triagem de 60 continuam válidas.

A interface de revisão permanece consultando o lote inicial de 80 candidatos. A ampliação de referências está no banco, mas a navegação do lote completo ainda exige evolução da consulta, incluindo paginação e preservação das notas ligadas ao lote antigo. Não foi feita troca silenciosa de arquivos. Não foi verificada uma tela de consulta das 11.197 referências nesta etapa, pois nenhuma interface foi alterada.
