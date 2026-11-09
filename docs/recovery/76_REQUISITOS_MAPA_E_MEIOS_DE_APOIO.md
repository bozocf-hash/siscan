# 76 — Composição gráfica, posicionamento e vínculos de apoio

**Entrega inicial:** [77](77_PRIMEIRA_INTEGRACAO_MAPA_ATLANTICADOR.md) implementa a primeira plotagem adjudicada e seleção por área no editor original. As passagens abaixo sobre integração ainda não entregue representam a especificação anterior a essa fatia. Criação/vínculo de apoios, compatibilidade e transferência efetiva continuam pendentes.

## Solicitação do responsável — 2026-11-09

**Esclarecimento posterior:** reutilizar o mapa existente do ATLANTICADOR. Fluxo desejado: escolher a unidade, clicar na posição do mapa e plotar. Não criar uma interface cartográfica paralela. O mapa sintético separado inicialmente considerado não será a interface deste fluxo. Essa escolha não comprova validação operacional da cartografia nem altera as restrições de acesso por partido.

**Fluxo refinado e confirmado pelo responsável:** o operador escolhe primeiro o local, por mouse, latitude/longitude ou referência de base fixa. Abre o ponto/unidade de apoio escolhido e utiliza a aba com nome **“Inserir meios adjudicados”**. Seleciona e insere nesse local os meios adjudicados disponíveis ao seu partido. Repete a distribuição nos locais que considerar apropriados. A escolha inicial de um meio antes de indicar posição é uma possibilidade auxiliar; não deve substituir esse fluxo principal de local → aba → meios.

As três formas de selecionar posição devem alimentar o mesmo destino de inserção. Referência de base fixa deve resolver a posição cadastrada dessa base; a referência e as coordenadas utilizadas precisam ser rastreáveis. Coordenadas digitadas exigem validação e indicação clara dos eixos/formato. O adaptador deve tratar explicitamente a diferença entre pares latitude/longitude do Leaflet e longitude/latitude usados em geometrias, sem trocar eixos silenciosamente.

A aba lista os meios adjudicados disponíveis, permitindo selecionar unidades individuais ou um conjunto para inserir. A distribuição deve atualizar a disponibilidade e preservar IDs; clicar novamente ou repetir uma gravação não deve duplicar o mesmo meio nem gerar inventário ilimitado. A criação de instâncias pelo operador deve respeitar os recursos adjudicados ao partido. Reposicionar uma unidade existente não equivale a criar outra.

## Seleção gráfica por área — solicitação adicional

O responsável solicitou clicar e arrastar para delimitar uma área de busca/seleção e selecionar os meios presentes nela. Implementar no mapa existente do ATLANTICADOR, com modo explícito “Selecionar área”, separando essa interação do arraste de navegação e da plotagem de unidades. O primeiro gesto delimita um retângulo e destaca os meios selecionados, com quantidade e lista para conferência. Oferecer limpar seleção e alternativa de seleção pela lista.

A seleção considera as posições exibidas das unidades e preserva seus IDs, sem duplicar meios representados em um apoio ou grupo. Quando símbolos estiverem agrupados/sobrepostos, a lista deve permitir conferir quais unidades foram incluídas. Selecionar não move, transfere, vincula ou exclui automaticamente: ações posteriores sobre o conjunto são explícitas e continuam sujeitas às permissões e regras aplicáveis.

Área de seleção não equivale a área de detecção de sensor nem concede visão adversária. Selecionar somente os meios que o usuário está autorizado a consultar; o backend mantém o controle das operações sobre os IDs selecionados. Não utilizar a busca espacial para revelar meios ocultos. A integração, os casos geométricos e a seleção em lote ainda precisam de implementação e testes no mapa reutilizado.

Selecionar graficamente unidades individuais e posicioná-las no mapa; organizar meios em base naval, base aérea ou plataforma móvel de apoio (exemplo: porta-aviões). Interface deve ser simples: lista dos meios disponíveis ao partido, mapa e ficha do apoio selecionado com seus meios vinculados. Aceitar seleção seguida de clique e arrastar/soltar, com alternativa acessível por formulário.

## Decisão complementar do responsável — 2026-11-09

O operador cria os meios, cria os apoios permitidos, escolhe sua localização e distribui os meios. A criação/posição inicial dos apoios não fica reservada exclusivamente ao instrutor. O escopo continua sendo o próprio partido, conforme APR-06; esta decisão não concede visão ou edição adversária.

Há dois tipos distintos de apoio a detalhar: **bases de apoio logístico conjuntas** e **bases de apoio logístico terrestres**. São bases definidas pelo usuário/operador, inclusive quanto à localização. Não fundir os dois tipos nem presumir que compartilham capacidades, composição, restrições ou procedimentos. O responsável indicou que as regras serão discutidas posteriormente.

A lista de tipos de apoio que o operador poderá criar permanece aberta: a autorização não deve ser interpretada como permissão irrestrita para criar qualquer tipo de apoio. Também não significa aprovação automática dos atributos físicos importados do Command. Criar uma unidade individual e promover dados técnicos são operações distintas.

## Referências e limites já decididos

APR-06: backend controla visibilidade por partido. APR-10: unidade individual conserva identidade, distinta do modelo/configuração. APR-12: em transferência de aeronave durante execução, vínculo efetivo muda somente após pouso e confirmação; indicar destino no mapa não equivale a concluir transferência. APR-14: iniciar com geografia sintética e máscara terra/água independente do fundo. Não declarar posicionamento geográfico operacional sem fonte/CRS/máscara aprovados.

Não foi identificada implementação cartográfica na interface `siscan-prototype/static` pesquisada. O mapa a reutilizar está no ZIP original `atlanticador-main (1).zip`: `frontend/viewer.html`, `frontend/src/viewer.mjs`, editor `frontend/src/app.mjs`, modelo/cena e Leaflet local em `frontend/vendor/`. Documento 19 descreve esses componentes. A integração deve preservar a identidade SISCAN e validar no backend a criação/posição, sem presumir que as permissões locais de edição do viewer equivalem às permissões SISCAN. A integração e a plotagem vinculada ao catálogo ainda não foram entregues.

## Comportamento a detalhar para implementação

1. Operador seleciona o destino no mapa existente, por clique, coordenadas ou referência de base fixa; pode criar apoio de tipo permitido e consultar seus atributos/vínculos.
2. Abre a aba “Inserir meios adjudicados” no destino e escolhe uma ou várias unidades disponíveis ao partido para inserir, respeitando instâncias/UUIDs e disponibilidade adjudicada.
3. Vincular ao apoio por ação gráfica explícita e confirmar resultado; apresentar incompatibilidades ou dados de capacidade desconhecidos.
4. Permitir posição independente quando o meio estiver fora do apoio; manter separados posição e vínculo administrativo/logístico.
5. Ao mover uma plataforma móvel, seus meios embarcados acompanham sua posição enquanto embarcados. Meios desdobrados não devem ser movidos automaticamente com a base de origem.
6. Tratar composição inicial e transferência durante exercício em fluxos distintos. Preservar origem/destino/autoria/horário, sem substituir histórico.

Uma base naval pode concentrar meios de diferentes naturezas conforme apoios efetivamente cadastrados. Não inferir que todos os meios da Marinha são navios, nem que toda aeronave pertence à Força Aérea. Natureza do meio, partido e Força são atributos distintos. Porta-aviões é uma unidade móvel que também pode prestar apoio, não uma base fixa em coordenada permanente.

Compatibilidade/capacidade: avaliar tipos de instalações, vagas, capacidades, convés/pista e restrições documentadas por configuração. Valor desconhecido não equivale a capacidade ilimitada. Cadastro de vínculo planejado não comprova compatibilidade física. Dados Command permanecem sujeitos à validação vigente.

## Decisões pendentes

- Detalhar os tipos de apoio criáveis pelo operador e as regras próprias das bases logísticas conjuntas e terrestres. A autoridade de criação/posicionamento pelo operador já foi confirmada.
- A origem funcional foi esclarecida: meios adjudicados disponíveis ao partido. Detalhar tecnicamente reserva/contabilização, criação de instâncias a partir dessa disponibilidade e tratamento concorrente, sem permitir duplicação.
- Confirmar limites de edição durante preparação e execução, inclusive procedimentos por natureza de meio além da transferência aérea já aprovada em APR-12.
- Definir primeiro recorte verificável com geografia sintética, sem antecipar escolhas definitivas de fornecedor cartográfico.

O trabalho de combustível continua autorizado: na mesma conversa o responsável escolheu relógio comum ao executar perfil, demais meios consumindo à taxa constante. A conferência do manifesto da previsão foi preparada/testada localmente; o débito por perfil ainda não foi entregue. Esta solicitação cartográfica acrescenta escopo e não apaga esse trabalho nem as decisões de alerta mínimo.
