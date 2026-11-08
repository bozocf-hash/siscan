# 11 — Inventário de arquivos e fontes

O inventário cobre a pasta `C:\Users\bozoc\Documents\siscan\` e os arquivos fornecidos na Missão 01. Conteúdo original foi somente lido; fonte ATLANTICADOR foi consultada dentro do ZIP, sem extração.

| Fonte | Localização | Exame e resultado |
|---|---|---|
| Texto Missão 01 | Anexo da conversa | Fonte primária das decisões/restrições organizadas nos documentos 01, 02, 05–10 |
| `atlanticador-main (1).zip` | Raiz `Documents\siscan` | 541 entradas (520 arquivos e 21 diretórios); versão 2.0.0. Auditoria estática da estrutura, frontend, backend, rotas, persistência, dependências, testes existentes, acessos e possíveis integrações, documentada em 03 e 16–22. Não extraído nem executado; sem commit Git verificável |
| `command manual.pdf` | Raiz `Documents\siscan` | 353 páginas digitalizadas; metadado indica título “CMO manual EBOOK.pdf”. OCR aplicado a 353/353 páginas em lotes; análise sintetizada por capítulo. Inspeção visual de páginas selecionadas (pp. 7, 8, 42, 44–46, 61, 135, 142, 146, 150, 193, 197 e 271), não integral; ver limites e qualidade em 12–15 |
| `DB3K_498.db3` | Raiz `Documents\siscan` | SQLite somente leitura (`mode=ro`, `query_only=ON`); integridade estrutural `ok`; 167 tabelas, 75 vínculos FK declarados e metadados consultados. Sem escrita. Integridade/inventário não equivalem a semântica completa, unidades ou domínios. Ver 04 e 09 |
| `01_inventario_tabelas.csv` | Raiz `Documents\siscan` | Inventário detalhado de objetos/tabelas e contagens. Comparado às contagens diretas; mantém detalhe integral |
| `02_dicionario_dados.csv` | Raiz `Documents\siscan` | Colunas, tipos, nullabilidade, default, PK/FK declarada. Usado como apoio ao mapeamento; não define unidades |
| `03_relacionamentos.csv` | Raiz `Documents\siscan` | Relações declaradas e inferidas. Inferências não provam semântica/cardinalidade |
| `04_mapa_dominios.md` | Raiz `Documents\siscan` | Agrupamento heurístico de domínios; conferido contra DB3K, sem validação semântica completa |
| `05_modelo_entidades_relacionamentos.md` | Raiz `Documents\siscan` | Síntese de tabelas/campos candidatos e relações; não é modelo SISCAN aprovado |
| `06_relatorio_recomendacoes_SISCAN.md` | Raiz `Documents\siscan` | Relato anterior read-only, agregados e limitações; comparado com acesso direto ao DB3K |
| Arquivos `docs/recovery/00` a `48` | `Documents\siscan\docs\recovery` | Documentação de recuperação, fontes CMO/DB3K, auditorias ATLANTICADOR e consolidação SISCAN. Missão 04 acrescenta 42–48 e atualiza 00, 11, 35, 38 e 40; consultar 00 para sequência/estado |

## Componentes ATLANTICADOR consultados dentro do ZIP

`AGENTS.md`, `README.md`, `VERSION`, `package.json`, `docs/DEPENDENCIAS.md`, `docs/ESCOPO-1.0.md`, `docs/CONFRONTO-2.0.md`, `docs/VALIDACAO-CONFRONTOS-20261103.md`, `serve.py` (rotas GET/POST e inicialização), módulos de backend listados em 24 e, para a Missão 02-C, a lista completa de `frontend/` (8 páginas, 73 itens em `src/`, 230 assets, 17 vendor), páginas HTML e módulos centrais/auxiliares de viewer, editor, cena, camadas, geometria, renderização, importação/exportação, login, situação, efeitos, Confronto e Calunga. Os detalhes de escopo e caminhos estão em 29–32; nem todo asset nem todos os módulos foram lidos linha a linha.

## Integridade e preservação

Os artefatos e fontes originais (ZIP, PDF e DB3K) não foram editados. O ZIP não foi extraído. Consultas SQLite foram somente leitura. O PDF foi lido por OCR e renderizado temporariamente para inspeção visual seletiva; arquivos intermediários não substituem nem alteram a fonte original. Não foram executados testes nem servidor.

## Missão 02-B — limite de escopo

A análise de backend foi estática sobre o ZIP, com consulta segmentada dos módulos listados acima e registro de rotas/fluxos em 23–28. Não se executou o código, testes, servidor ou `manage.py`; não se abriram bancos de dados operacionais do ATLANTICADOR e não se modificaram código, configuração, ZIP ou DB3K. Os bancos mencionados em 27 são caminhos/esquemas identificados no código, não inventário de dados de uma instalação real. A Missão 02-C permanece pendente de autorização.

## Missão 02-C — limite de escopo

A auditoria frontend examinou estaticamente o ZIP, inventariou os 328 arquivos de `frontend/` e aprofundou páginas e módulos principais. Os 230 assets foram contados, não descritos item a item; nem cada módulo auxiliar foi lido integralmente. Não houve navegador, servidor, script, testes, instalação, rede ou validação funcional/jurídica. Identificou-se no código de UI uma escrita legada `/api/control/events*` que o backend responde com 410. Não foram alterados código, configuração, banco, ZIP ou fontes originais. Documentos 29–34 são análise e proposta, sem autorização de integração ou implementação.

## Missão 03 — consolidação documental

Documentos 35–41 consolidam os documentos recovery 00–34, incluindo referências CMO/DB3K onde pertinentes. Decisões, propostas, evidências e pendências permanecem classificadas; critérios de aceite, interfaces e roadmap são propostas quando assim indicados. A consolidação preserva decisões MPNL de 08, separa modelo SISCAN de dados ATLANTICADOR/DB3K e não cria esquema físico, APIs ou integrações. Nenhum código, banco, configuração, servidor, teste ou script da aplicação foi alterado ou executado. A Missão 04 não foi iniciada.

## Missão 04 — fechamento documental e pauta de aprovação

Documentos 42–48 organizam propostas e a pauta APR-01 a APR-20; o resultado expresso do responsável foi incorporado em 49. DEC-021 (autoridade do backend) e DEC-022 (separação lógica em cinco domínios) passam a DECIDIDO conceitualmente, com limites registrados em 49. O responsável também aprovou em conceito a orientação híbrida futura e implantação centralizada inicial, alteração de cenários publicados em execução sob aviso e registro, graus de confiança 1/2/3 e demais decisões listadas em 49. Os documentos 00, 09, 10, 35, 36, 38, 40, 41–48 foram alinhados ao resultado. O MPNL preserva decisões anteriores e lacunas quantitativas; bases e parâmetros pendentes não foram inferidos. Nenhum desenvolvimento, integração, alteração de código/banco/configuração/originais ou execução de servidor/teste/script ocorreu. A próxima fase continua sem autorização.

## Especificação funcional e fluxograma decisório

O DOCX `C:\Users\bozoc\Documents\siscan\Especificacao_Funcional_Fluxo_Decisorio_SISCAN.docx` foi lido em modo somente leitura. Contém texto e tabelas de requisitos para fluxo documental, responsabilidades, estados, prazos, ocorrências, relatórios e auditoria; declara que não reconstrói o diagrama ou seus conectores e não autoriza implementação.

O arquivo sem extensão `C:\Users\bozoc\Documents\siscan\fluxograma` foi identificado como JPEG, 1124 × 1540 px, uma página, visualmente examinado. Mostra o ciclo Missão → Exame da Situação → EPO → Controle da Operação Planejada, decisões Sim/Não e conectores 1/2/3. A análise e seus limites constam em 50. O responsável confirmou em 08/11/2026 que esta é a versão parametrizada e definitiva aplicável. A imagem não contém legenda externa dos conectores nem valores explícitos de parâmetros; lacunas não foram inferidas. Os originais DOCX e JPEG foram preservados.
