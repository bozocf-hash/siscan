# 56 — Inventário técnico literal da amostra DB3K

Foram recuperados 580 valores de campos técnicos presentes nos 80 candidatos, diretamente das tabelas DataShip, DataAircraft, DataSubmarine e DataGroundUnit, em modo somente leitura. A seleção cobre campos de dimensões, massa/deslocamento, profundidade, área e tripulação quando presentes, sem incluir parâmetros de emprego de armamentos. Campos ausentes não são criados por inferência.

Cada evidência mantém nome literal do campo, valor original, tipo declarado no SQLite, unidade nula e estado `pending_unit_and_semantics`. Valores zero e NULL são preservados sem interpretação. Nome/tipo do campo não prova a unidade, escala, aplicabilidade ou significado do valor.

O relatório técnico substitui apenas o arquivo de consulta derivado `prototype/data/db3k-domains-01.json`; sua versão anterior é preservada em `db3k-domains-before-technical-01.json`. O original DB3K, o banco de candidatos e os pacotes de aprovação permanecem preservados. As 80 referências aprovadas no documento 55 continuam restritas à identificação; nenhum valor técnico é promovido a elas ou à tabela de meios alocáveis.

A interface do instrutor exibe as evidências em seção própria. O backend confere fonte/amostra por hash e só aceita metadados técnicos com unidade nula e situação pendente. Os testes cobrem recuperação de frações e zero, preservação da fonte e rejeição de unidade atribuída indevidamente. A validação semântica e das unidades continua necessária antes de qualquer cálculo ou uso em configuração/unidade individual.

A pesquisa documental de unidades está registrada em [57 — Matriz de evidências](57_MATRIZ_EVIDENCIAS_UNIDADES_DB3K.md). As correspondências propostas não alteram o estado pendente nem substituem comprovação aplicável ao esquema DB3K_498.
