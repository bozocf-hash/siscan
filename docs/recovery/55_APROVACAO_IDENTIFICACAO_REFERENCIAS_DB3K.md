# 55 — Aprovação da identificação de referências DB3K

O responsável respondeu “siga” à pergunta explícita sobre cadastrar os 80 registros do lote `DB3K-af0a2c626a2dc218` apenas como referências de origem — nome, tabela, ID externo e hash. A autorização é registrada com esse escopo restrito. Não inclui atributos técnicos, unidades físicas individuais ou alocação aos partidos.

O registro das referências utiliza identificadores SISCAN próprios, separados dos IDs externos e dos identificadores temporários de candidato. A chave de origem inclui hash, tabela e ID externo. Repetir o registro da mesma referência preserva seu ID. Uma versão diferente da fonte continua sendo outra referência de origem; a identidade canônica de modelo/configuração/unidade permanece assunto distinto.

O manifesto local `prototype/data/db3k-approval-identification-01.json` identifica pacote, hash, responsável, registro da decisão, escopo e candidatos abrangidos. Ele documenta a decisão; não representa assinatura digital ou mecanismo de autenticação do responsável pelo aplicativo. O banco SISCAN mantém o manifesto e a relação de cada referência com a aprovação. A ferramenta não insere registros na tabela de meios `assets` nem cria alocações.

Permanecem pendentes a validação semântica dos atributos técnicos, seus domínios/unidades e o mapeamento aprovado para modelo, configuração e unidade individual. A consulta do instrutor poderá mostrar a identificação de referência cadastrada sem apresentar esse estado como meio alocável.

O registro local foi executado: 80 referências criadas, com quantidades de meios, alocações e submissões preservadas. A consulta do instrutor mostra o ID interno e a situação “identificação de referência cadastrada”, mantendo a validação técnica pendente. Foram conferidas aprovação de escopo restrito, correspondência do hash do pacote, idempotência, preservação dos IDs e recusa do banco de origem como destino de escrita. No navegador foram conferidos os 80 vínculos, filtros e bloqueio ao aluno.
