# 63 — Consulta do catálogo ampliado e valores técnicos pendentes

## Resultado — 2026-11-09

Foi implementado o painel **Catálogo cadastrado — referências e valores técnicos**, restrito ao instrutor atribuído ao exercício demonstrativo. Ele consulta as 11.197 referências e os 77.349 valores incorporados ao banco, com busca, filtro de plataforma e paginação de 50 referências.

O painel anterior de candidatos permanece disponível para a amostra inicial e suas observações. Nenhum arquivo de amostra foi substituído e nenhuma nota foi migrada para outro candidato. A consulta ampliada é somente leitura; não acrescenta aprovação técnica, meios ou alocações.

## Uso na interface

1. Entrar como instrutor e localizar **Catálogo cadastrado — referências e valores técnicos**.
2. Informar nome ou ID externo, selecionar o tipo de plataforma quando necessário e clicar **Consultar referências cadastradas**.
3. Navegar pelas páginas e abrir **Valores técnicos brutos** na referência desejada.

Pesquisa composta apenas de dígitos procura ID externo exato. Para nomes, a busca usa trecho literal sem tratar `%` ou `_` como curingas. IDs iguais em tabelas distintas continuam referências distintas; o filtro de plataforma ajuda a selecionar a origem. Uma nova pesquisa começa na página 1.

Cada referência mostra nome literal, tabela, ID externo, ID SISCAN, arquivo/hash de origem e valores brutos com nome do campo SQL, tipo declarado no SQLite e hash da evidência. Zero, NULL e sinais são preservados. Unidade e significado continuam explicitamente pendentes; não são inferidos a partir de nomes ou tipos.

Foram incluídos estados de carregamento, erro recuperável e pesquisa vazia; os controles ficam bloqueados durante uma consulta. O painel reutiliza o estilo existente, oferece rótulos de formulário, região de resultados acessível por teclado e indicação de estado. O navegador não carrega os 77.349 valores de uma vez.

## Contrato da API

`GET /api/catalog-references`

| Parâmetro | Regra |
|---|---|
| page | Inteiro positivo até 1.000.000; padrão 1; páginas além do resultado são ajustadas à última |
| q | Até 120 caracteres após remover espaços externos; dígitos = ID exato; demais termos = trecho de nome por comparação lower do SQLite, sem normalização adicional de acentos |
| table | Vazio ou DataAircraft, DataShip, DataSubmarine, DataGroundUnit |

Parâmetros desconhecidos ou repetidos são recusados. A resposta contém references, total, page, pages e page_size=50. Os itens incluem technical_fields com field_name, value, sqlite_type, unit=null, validation_status=`pending_unit_and_semantics` e evidence_sha256. Catálogo vazio retorna lista vazia e página 1 de 1.

Autenticação é obrigatória (401 para anônimo). Aluno, avaliador ou instrutor sem atribuição recebem 403. Parâmetros inválidos recebem 400; erro de formato/integridade da evidência recebe 503 com mensagem genérica. A autorização segue a mesma regra demonstrativa do catálogo anterior: atribuição ao primeiro exercício da instalação.

As consultas são parametrizadas e limitadas a uma página. A ordem é determinística por hash, tabela, ID externo numérico/textual e ID SISCAN. A leitura de valores é agrupada em uma consulta por página, com vínculo entre hash da importação e origem da referência. Não há leitura dos grandes arquivos JSON em cada requisição. Não há escrita de negócio nesse endpoint.

## Validação executada

O novo `check_reference_catalog.py` foi escrito antes da implementação e falhou inicialmente pela ausência do método. Depois passou, cobrindo:

- autorização por papel e atribuição;
- páginas sucessivas sem repetição, página final e catálogo sem resultados;
- filtros e busca por ID, nome e caracteres literais;
- limites de parâmetros e rejeição de repetidos;
- valores pendentes, NULL, zero, sinal e proveniência;
- consulta sem escrita e preservação de observações antigas;
- resposta segura diante de valor JSON inválido no banco de teste.

Os oito scripts `check_*.py` passaram, incluindo os testes anteriores de alocação por partido, revisão/liberação, notificações, importação bruta e referências. A sintaxe JavaScript foi verificada com Node.

O conector Chrome DevTools não estava disponível; a validação foi feita no Microsoft Edge com Playwright e perfil isolado. Primeiro foi usada uma cópia temporária do banco. Após a revisão da consulta agrupada e atualização da prévia, a verificação foi repetida no serviço efetivo `http://127.0.0.1:8787/`.

No navegador foram percorridas **224 páginas**, obtendo **11.197 IDs de referência distintos e 77.349 valores**. Foram conferidos busca/filtro, navegação anterior/próxima, detalhes de Submarine/3 com MaxDepth=-320, pesquisa vazia, acesso negado a aluno/avaliador e ausência do painel para esses papéis. O painel anterior continuou exibindo 80 candidatos. Não houve erros JavaScript observados.

Foram capturadas e inspecionadas imagens de desktop, largura móvel de 390 px e detalhes técnicos. Não houve transbordamento horizontal na amostra móvel. Os artefatos de teste e capturas ficam em tmp, fora do GitHub. O teste no serviço efetivo efetuou logins locais demonstrativos, sem submissão, alocação ou registro de observações.

## Entrega e limites

Os arquivos de aplicação foram sincronizados para `C:\Users\bozoc\Documents\siscan\prototype`; o serviço local na porta 8787 foi reiniciado com a versão atualizada. O servidor temporário de testes foi encerrado ao final. O DB3K original, a amostra de revisão e o arquivo de evidência foram preservados.

Os valores permanecem pendentes. Esta entrega permite consultar/revisar dados e sua origem, sem resolver as divergências de Area/MastHeight, a semântica de sinais/zeros/NULL, o tipo de tonelada ou o contexto de extremos. Novas anotações continuam disponíveis no painel dos candidatos antigos; esta etapa não adiciona editor de observações para todas as referências ampliadas.
