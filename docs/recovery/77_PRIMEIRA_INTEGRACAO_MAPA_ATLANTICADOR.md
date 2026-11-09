# 77 — Primeira integração do mapa ATLANTICADOR

**Complemento:** [78](78_MAPA_PAINEL_REPOSICIONAMENTO_E_REPRESENTACOES.md) substitui a janela adicional por abas na lateral original, melhora o reposicionamento e acrescenta silhuetas/calungas e ficha automática. Os registros abaixo descrevem a primeira entrega.

Entrega de 2026-11-09: reutiliza o editor original do ZIP local, com mapa Leaflet, navegação, fundos e ferramentas existentes. O adaptador SISCAN adiciona o painel “Inserir meios adjudicados”. Não foi criado mapa alternativo. O ZIP original é preservado; a cópia derivada fica em `prototype/data/atlanticador`, fora do GitHub. Exemplos de forças do editor foram removidos da cópia derivada para não confundi-los com meios adjudicados. Licenças e atribuições do frontend original permanecem na cópia.

## Fluxo entregue

Após entrar no SISCAN, usar “Mapa ATLANTICADOR · inserir meios adjudicados”. Escolher o partido (instrutor) ou consultar somente o próprio (operador). Selecionar meios, clicar no mapa ou digitar latitude/longitude em graus decimais e confirmar “Inserir / reposicionar selecionados”. Referência de posição permite reutilizar coordenadas de um meio já plotado; **ainda não é cadastro de base fixa**.

O mapa mostra marcadores dos meios adjudicados do partido consultado. “Selecionar área” desativa o arraste de navegação; arrastar um retângulo seleciona os meios plotados dentro dele e atualiza a lista. “Concluir seleção de área” restaura navegação. Seleção pela lista é alternativa ao gesto. Selecionar não grava nem move unidades automaticamente.

## Backend e rastreabilidade

`map_units.py`: GET `/api/map-units?team=AZUL|VERMELHO` consulta apenas assets com adjudicação ativa. POST na mesma rota exige sessão/origem/CSRF, UUID de comando, partido, latitude, longitude e lista de IDs com revisão esperada. Instrutor precisa de atribuição ao exercício; operador precisa pertencer ao partido. Avaliador não recebe acesso aos dados. Não confundir o seletor de perspectivas dos rascunhos locais do editor com autorização sobre meios SISCAN.

`map_unit_positions` mantém uma posição por identidade existente; não cria inventário. `map_plot_commands` garante repetição idempotente e impede reutilizar chave com conteúdo diferente. Revisão antiga retorna 409; meio não adjudicado é recusado; coordenadas inválidas são recusadas. `BEGIN IMMEDIATE` aplica o lote, registro do comando e evento `map.units_plotted` juntos. Evento preserva posições anteriores, pedido e autor. Revogar adjudicação remove o meio da consulta, preservando seu histórico no banco.

Script reproduzível: `python tools/prepare_atlantic_map.py <ZIP-original> <destino-data/atlanticador>`. Ele copia o frontend, esvazia somente os exemplos demonstrativos da cópia e acrescenta a instalação do adaptador ao módulo do editor. `siscan-origin.json` registra SHA-256 do ZIP. Código original não é publicado novamente neste repositório; adaptador, serviço, testes e preparador são versionados.

## Verificação

Passaram os 20 scripts Python, incluindo `check_map_units.py`: adjudicação, isolamento entre partidos, lote, identidade preservada, repetição, conflito de revisão e rollback com falha de auditoria. A conferência da previsão de combustível preparada anteriormente também está testada; isso ainda não entrega débito por perfil.

Edge/Playwright em cópia isolada: editor original carregado, meio adjudicado inserido por coordenadas, posição relida do backend, seleção por retângulo destacando o meio, layout móvel de 390 px sem transbordamento da página e nenhuma exceção JavaScript. Fundos de mapa dependem dos provedores configurados no editor original.

Instância local: editor e lista conferidos sem inserir posições no banco em uso. Backup consistente `prototype/data/siscan-before-map-17.sqlite3`. Todas as tabelas anteriores, exceto sessões transitórias, foram comparadas em ambas as direções por EXCEPT; nenhuma linha antiga removida, alterada ou acrescentada. As duas tabelas novas começam vazias. Combustível, adjudicações, cenário e snapshots permanecem preservados. Recibo local: `prototype/data/map-delivery-receipt-17.json`. Integridade SQLite e FKs conferidas.

Foram preservadas 24 tabelas anteriores conferidas. SHA-256 do recibo: `cd6bc615c5def0be1a79db0d7fd9116570f93bb34b67b8178cb73e4ca508992c`.

## Limites e próxima entrega

Posições são de planejamento. Não há validação terra/água operacional, compatibilidade ou capacidade de apoio aprovada. Não há cadastro integrado de bases fixas/logísticas conjuntas/terrestres, vínculo persistido de hospedagem, transferência efetiva, acompanhamento automático do porta-aviões ou confirmação de pouso. Essas capacidades seguem os requisitos de 76 e APR-12, sem serem simuladas por uma simples mudança de coordenadas.

Ferramentas originais de rascunho/importação/exportação continuam locais; não publicar seus desenhos como estado oficial SISCAN nem presumir que suas exportações incluem os novos marcadores. Esta entrega não transfere as permissões de rascunho do ATLANTICADOR para o backend SISCAN. Próximo recorte: cadastro/vínculo de apoios e referência de base fixa dentro do mesmo mapa, respeitando as decisões já registradas.
