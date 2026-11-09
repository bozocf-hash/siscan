# 67 — Base persistida de combustível e propulsão

## Escopo autorizado — 2026-11-09

Continuação da implementação do banco solicitada pelo responsável após a entrega 66. Persistir cadastros de combustível/propulsão, instalações e pontos de desempenho em base derivada separada, com origem, integridade referencial, unidades/evidências e consulta pelo backend. Não alterar DB3K, compilação bruta, alocações, decisões ou aprovar taxas para o motor.

## Critérios de aceitação

- Preservar todos os cadastros e pontos das famílias selecionadas, inclusive registros sem uso, valores nulos, zero, sinais e frações.
- Preservar cada linha de instalação, inclusive repetições e referências sem destino; componente compartilhado é cadastrado uma vez.
- Identificar dono e componente por tabela/linha fonte, mantendo o ID externo e o parâmetro original. Não inferir que ComponentNumber é multiplicador de consumo.
- Registrar hash da origem/compilação, versão do contrato de unidades e do construtor. O destino deve ser novo; reconstrução não sobrescreve banco existente.
- Ativar FKs da base derivada, conferir integridade e comparar literalmente os payloads de componentes, instalações e desempenho com a compilação.
- Expor a ficha de recursos persistidos no endpoint técnico existente, com as mesmas permissões. Recusar base com origem/contrato incompatíveis ou construção incompleta.
- Sinalizar persistência na ficha sem duplicar as tabelas técnicas já exibidas. Metadados de unidade continuam distintos de aprovação operacional.

## Entrega e cobertura

Base derivada: `prototype/data/db3k-resources-09.sqlite3`. Relatório: `prototype/data/db3k-resources-audit-09.json`. Ambos ficam fora do GitHub; construtor, leitor, testes e documentação são versionados. A compilação integral 06 continua como fonte dos demais dados, sensores e cadeias transitivas.

| Conteúdo persistido | Quantidade |
|---|---:|
| Referências de plataformas e armas (`owners`) | 18.963 |
| Combustíveis (`fuel_records`) | 1.940 |
| Propulsores (`propulsion_records`) | 3.467 |
| Pontos de desempenho (`performance`) | 20.544 |
| Registros de instalação (`installations`) | 28.757 |

São referências de catálogo, não meios físicos ou novas alocações. Os 18.963 donos incluem as seis categorias de plataformas e 3.995 armas. As 28.757 instalações compreendem 15.075 linhas de combustível e 13.682 de propulsão; não equivalem a essa quantidade de motores/tanques físicos. Nenhum multiplicador foi aplicado.

Os 20.544 pontos encontraram propulsor e as 28.757 instalações encontraram dono e componente nas relações compiladas. Não houve vínculo sem destino **neste recorte**; os 199 valores sem destino do grafo integral permanecem documentados em 65. Integridade SQLite: `ok`; verificação de FKs: zero erros. A existência do destino não aprova a semântica física da relação.

Foram comparados literalmente os 54.708 payloads de componentes, desempenho e instalações com a compilação, inclusive ID externo e linha fonte. A auditoria adicional conferiu todas as colunas numéricas de desempenho (regime, faixa, velocidade, limites e consumo), capacidade/tipo de combustível e tipo/quantidade de motores. Nenhuma divergência encontrada.

## Esquema, consulta e segurança

`build` identifica hashes, data, contrato e estado da construção. `owners` identifica o dono por tabela/linha e ID externo. `components` cadastra combustível/propulsor uma vez, com colunas consultáveis, payload literal e metadados de unidade. As views `fuel_records` e `propulsion_records` separam as famílias. `performance` mantém cada ponto e FK para o propulsor; `installations` mantém cada linha de associação e FKs para dono/componente. Há índices para identidade, dono e componente.

Componentes compartilhados não são duplicados; instalações repetidas são preservadas. Vínculos ausentes/nulos ficam com destino nulo, estado e parâmetros originais, como exercitado pelos testes sintéticos. Uma construção incompleta não é servida; o destino existente é recusado em vez de sobrescrito. A integridade referencial usa [FKs do SQLite](https://www.sqlite.org/foreignkeys.html) ativadas explicitamente. As consultas abrem [URIs somente leitura](https://docs.python.org/3/library/sqlite3.html#how-to-work-with-sqlite-uris) e parametrizam os valores.

`GET /api/source-technical?table=DataAircraft&id=3` agora inclui `resource_store`, com proveniência, dono, instalações, componentes distintos e pontos diretamente associados. O contrato de consumo transitivo de 66 permanece separado. O leitor recusa origem incompatível, contrato de unidades diferente ou estado incompleto. Sem arquivo específico, retorna disponibilidade ausente explícita, mantendo a compilação bruta acessível. Não existe endpoint de escrita/promulgação de unidades.

A interface informa a quantidade persistida, e a exportação JSON inclui a ficha de recursos. A consulta continua restrita ao instrutor atribuído; aluno, avaliador e instrutor não atribuído recebem 403. As pendências de unidade/escala de 66 permanecem e `calculation_ready=false`; não há consumo calculado, interpolação, baixa de estoque ou associação automática tanque→motor.

## Validação e rastreabilidade

Os doze verificadores Python passaram, incluindo `check_resource_store.py`. O novo teste cobre componentes sem uso, instalações repetidas/compartilhadas, referências inexistentes/nulas, precisão e limites negativos, capacidade zero/NULL, recusa de sobrescrita, origem errada, construção incompleta, integração HTTP e permissões.

No Edge, a consulta SQL foi comparada com os valores/metadados do grafo bruto nas quatro fichas ID 3: Aircraft (2 instalações/6 pontos), Ship (3/4), Submarine (1/10) e GroundUnit (2/7). Exportação JSON, rótulos de unidade, navegação, perfis completos, ausência de perfil Static/567, acesso e tela de 390 px passaram. As verificações preservaram os parâmetros e a distinção entre componentes diretos e transitivos.

| Artefato | SHA-256 |
|---|---|
| DB3K original | `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d` |
| Compilação 06 | `de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9` |
| Base de recursos 09 | `dab29b753451d05209e9bd164439aa6c3799c60a4cf851035ba3f8e2b1c5a96b` |
| Construtor/leitor `resource_store.py` | `b3f0d825204c0aac04ca55d8a67ab901a8e9300dfc8bf85fc8092dbebb94d0f5` |

Nenhum código ATLANTICADOR, PDF original ou DB3K foi modificado. O relatório de auditoria preserva a versão `db3k-498-units-01` e a proveniência da construção. A disponibilização de meios continua por partido, sem novas referências aprovadas ou alterações nos registros operacionais.
