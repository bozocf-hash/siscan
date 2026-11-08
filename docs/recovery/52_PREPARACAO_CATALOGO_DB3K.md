# 52 — Preparação do catálogo DB3K para revisão

Foi criada uma ferramenta local `siscan-prototype/tools/stage_db3k.py` para leitura do SQLite com `mode=ro` e `query_only=ON`. Ela gera outro banco, exclusivamente de candidatos para revisão, sem carregar dados no exercício ou alterar a fonte. O destino deve ser novo; sobrescrita é recusada.

A primeira amostra contém 80 registros: 20 de cada tabela DataShip, DataAircraft, DataSubmarine e DataGroundUnit, ordenados por ID. Não é uma seleção representativa nem um catálogo operacional. Foram recuperados ID e nome literais e códigos disponíveis de categoria, tipo, país e serviço, mantidos como códigos sem interpretação automática. Unidades e atributos técnicos não foram importados.

SHA-256 da fonte lida: `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`. O hash foi conferido antes e depois da leitura. Cada candidato recebe identificador próprio de revisão; esse identificador ainda não é a identidade canônica de modelo, configuração ou unidade SISCAN. Todos permanecem `needs_review`.

Próximos trabalhos: revisão semântica e dos domínios, definição da distinção modelo/configuração/unidade para cada registro selecionado e promoção controlada ao catálogo interno. A alocação por partido continua usando somente meios sintéticos até essa validação. O banco de candidatos contém dados da fonte e permanece local, fora do GitHub.
