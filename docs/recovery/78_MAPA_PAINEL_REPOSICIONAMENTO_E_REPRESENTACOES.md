# 78 — Painel, reposicionamento, silhuetas e ficha resumida

## Entrega — 2026-11-09

O responsável apontou sobreposição de painéis, dificuldade de reposicionar, necessidade de identidade igual ao cadastro, silhuetas e ficha automática ao passar o mouse. O adaptador agora ocupa o painel lateral original do ATLANTICADOR, com abas “Camadas” e “Meios adjudicados”; removeu-se a janela fixa adicional à direita. O botão “Meios” na barra abre a aba correspondente. As ferramentas originais permanecem no mesmo editor.

Reposicionamento: botão direito no símbolo (ou clique para abrir sua ficha), “Reposicionar”, clique no destino. Alternativa: alterar coordenadas e confirmar no formulário. Esc cancela antes da gravação. Cursor indica escolha de destino. Durante essa escolha, os ícones deixam de interceptar o clique, permitindo deslocamentos pequenos, inclusive dentro da área antes ocupada pelo próprio ícone. Identidade, revisões e gravação transacional continuam no serviço de 77.

O editor original captura `contextmenu` no contêiner; o adaptador trata primeiro somente os marcadores SISCAN para que o menu original não consuma o evento. Os demais elementos conservam seu comportamento. Abas compartilham a lateral, preservando controles originais de abertura/fechamento/redimensionamento.

## Representação visual

`static/unit-silhouettes.mjs` contém vetores ilustrativos próprios para fragata, corveta, contratorpedeiro, torpedeiro, navio de apoio, porta-aviões, submarino, aeronave e helicóptero, além de símbolo neutro não classificado. Não são desenhos em escala ou representações técnicas de classes específicas. “Catálogo de silhuetas” permite visualizar e aplicar uma família aos meios selecionados.

Nome e categoria cadastrados orientam a classificação inicial conservadora. “Apoio” isoladamente não é interpretado como navio de apoio. Quando não há descrição suficiente, mantém-se não classificado. O operador pode escolher a família visual por meio; essa preferência fica no navegador, por usuário/partido/ID, sem alterar tipo físico ou atributos no banco e sem se tornar classificação técnica compartilhada.

Código e nome exibidos são os valores exatos do asset adjudicado. Nenhum nome é substituído pelo rótulo da silhueta e nenhuma unidade é criada pela troca visual. O marcador mostra código/nome; a ficha apresenta a identificação completa.

O seletor “Motor Calunga · simbologia militar” usa o gerador existente no ATLANTICADOR. Foram ligados os conjuntos aéreo, de superfície e submarino às famílias com correspondência explícita no catálogo local. Por exemplo, porta-aviões corresponde a “Navio Aeródromo”. A cópia derivada corrige os caminhos `/vendor/` para `/atlanticador/vendor/`. Não houve alteração do ZIP original nem publicação dos assets originais no GitHub.

Sem correspondência reconhecida, o adaptador conserva a silhueta e informa o fallback. Não inventa SIDC específico. O uso do motor existente não constitui certificação de conformidade com uma edição de norma OTAN/MIL-STD. Partido de exercício e hostilidade são conceitos distintos: não transformar automaticamente todos os meios vermelhos em inimigos na classificação militar.

## Ficha automática e dados

Passar o mouse abre a ficha resumida e consulta novamente a lista autorizada do partido para conferir os dados. Falha de consulta é indicada; não é apresentada como confirmação de disponibilidade. Se a adjudicação deixou de existir, a consulta remove o item da lista apresentada. Clique mantém acesso à ficha e à ação de reposicionamento.

São exibidos código, nome, categoria, adjudicação ao partido, combustível (saldo/capacidade, kg, quando houver estado vinculado), capacidade de combate e disponibilidade operacional. **Adjudicado ao partido não significa operacionalmente disponível.** Os dois últimos campos ainda não têm valores estruturados validados nesse vínculo e são retornados como null/“não informado”. Não são inferidos de armamento, categoria ou quantidade de combustível.

O combustível estruturado atualmente disponível nesse vínculo é do ensaio sintético controlado, identificado explicitamente na ficha. Asset sem estado de combustível vinculado recebe “não informado”, sem substituir por zero. A integração completa com atributos de modelos/configurações Command e o estado operacional real continua pendente de seus contratos e aprovações.

## Verificação e preservação

- Passaram os 20 verificadores Python e `node check_map_visuals.mjs`. O teste de mapa verifica nomes preservados, ausência explícita de dados não cadastrados e leitura de combustível/capacidade do estado sintético quando a unidade correspondente é adjudicada.
- O teste vetorial cobre as nove famílias, fallback neutro, classificação conservadora e SVG com caminhos/cores controlados.
- Edge/Playwright em base isolada: painel dentro da lateral original, alternância de abas, silhueta por meio, hover com código/nome do cadastro, botão direito e deslocamento pequeno gravado no backend. Conferidos SVGs gerados pelo motor para fragata, corveta, contratorpedeiro, apoio, porta-aviões, submarino, aeronave e helicóptero. Layout de 390 px sem transbordamento da página e nenhuma exceção JavaScript.
- Na instância em uso, conferidos painel e catálogo sem criar ou reposicionar os meios do usuário. Os testes de movimento foram isolados. Backup consistente: `prototype/data/siscan-before-map-visuals-18.sqlite3`. Comparação bidirecional EXCEPT preservou todas as linhas das 26 tabelas anteriores conferidas, excluindo sessões transitórias. Nenhuma alteração de saldo, cenário, adjudicação, nome, posição ou snapshot foi aplicada pela entrega. Sem alteração de schema.
- `integrity_check=ok`, zero violações FK. Recibo local `prototype/data/map-visual-delivery-receipt-18.json`, SHA-256 `19f13cc7aa928743f8233a75ba3bd572654ad0a7231b4a2aa36abdf18ffbdf93`. Backups, recibos e frontend extraído permanecem fora do repositório.

## Continuidade

Mantidas pendências de 76/77: cadastro e vínculos de bases/apoios, compatibilidade/capacidade física, validação terra/água, transferências efetivas e estado operacional. A troca de silhueta não resolve essas pendências. O débito por perfil de combustível continua autorizado, ainda não entregue. Preferências visuais locais não foram promovidas a atributos oficiais de configuração.
