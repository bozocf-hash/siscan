# 68 — Associação da massa de armamento ao payload

## Solicitação e contrato — 2026-11-09

O responsável solicitou associar o peso unitário de cada sistema de armamento ao payload disponível. A entrega deve partir das relações compiladas, manter a identidade de cada instalação/configuração e distinguir massa de arma/munição cadastrada da massa completa de um sistema/lançador.

Critérios: apresentar arma, peso cadastrado, DefaultLoad, MaxLoad, Multiple, carga interna/opcional e massa nominal por linha; comparar separadamente cada loadout com WeightPayload da aeronave quando houver dados suficientes. Não somar configurações alternativas, não multiplicar por ComponentNumber, não aprovar unidades SQL, não baixar estoque nem converter a comparação nominal em autorização de carregamento. Paióis, lançadores instalados e reservas permanecem separados do payload aéreo.

Peso desconhecido/zero, quantidades inválidas, referência ausente, DefaultLoad maior que MaxLoad e Multiple diferente de 1 impedem totalizações completas da parcela afetada. Itens opcionais são mostrados separadamente e não entram automaticamente na carga padrão. Não usar a soma dos MaxLoad de armas distintas como capacidade simultânea comprovada.

O [formulário primário de solicitação de armas do CMO](https://github.com/PygmalionOfCyprus/cmo-db-requests/blob/main/.github/ISSUE_TEMPLATE/22_NEW-WEAPON.yml) identifica Weight em kg. Isso é referência documental proposta para DataWeapon.Weight, não dicionário SQL 498 nem validação da massa do sistema completo. WeightPayload usa a referência do template Aircraft registrada em 58/66. As duas unidades continuam pendentes para uso operacional.

## Implementação e interpretação

`armament_payload.py` produz o contrato `armament-payload-reference-01` a partir dos nós/vínculos já persistidos na compilação 06. O endpoint técnico existente inclui `armament_payload`, e a exportação JSON contém o resultado completo. Não foi criada uma cópia de pesos divergente do banco: cada item aponta para instalação/linha, WeaponRecord e DataWeapon de origem. Os originais e a base específica de combustível/propulsão 09 não são alterados.

A seção **Armamento e payload** permite escolher cada configuração ou instalação. Mostra massa cadastrada, carga padrão, máxima, Multiple, massa nominal por linha e condição interna/opcional. Loadouts alternativos são independentes. Duas instalações do mesmo suporte aparecem separadamente, mesmo que compartilhem o cadastro; reserva do suporte e paiol são grupos próprios. O peso de subcomponentes/ogivas não é somado novamente à arma completa.

A multiplicação nominal ocorre apenas com massa positiva e finita, DefaultLoad/MaxLoad inteiros não negativos, padrão não superior à máxima e Multiple=1. É uma hipótese analítica: ainda falta validar a unidade SQL e se a massa cadastrada corresponde à mesma unidade de contabilização da quantidade. Não é aprovação para o motor. ComponentNumber identifica uma linha/instalação, não é multiplicador. Opcionais ficam fora do total padrão e devem ser escolhidos/validados posteriormente.

Para loadout de aeronave com dados completos e WeightPayload positivo, calcula-se uma diferença nominal entre o payload declarado e a massa padrão. Valores zero/nulos do limite não são tratados como capacidade disponível. Configuração sem linhas de armamento não recebe parecer de compatibilidade. Para outras categorias, não se substitui payload por deslocamento, Cargo_Mass ou capacidade de paiol. `operational_available_payload=null` e `calculation_ready=false` permanecem explícitos.

Não foi deduzida a carga disponível por WeightMax−WeightEmpty: combustível, pessoas, adaptadores, tanques/cargas e condições de peso máximo precisam de contabilização compatível. Também não foram inferidos número/limite de cabides, centro de gravidade, volume, arranjo, capacidade simultânea de lançadores ou interoperabilidade entre armas só porque a massa caberia.

## Conferência integral do recorte

A ferramenta `python -m tools.audit_armament_payload COMPILACAO NOVO_RELATORIO.json` examinou todas as 31.258 configurações e 86.981 linhas DataLoadoutWeapons, com hash da compilação preservado e destino sem sobrescrita. O relatório mantém resumo individual por configuração e os resultados das 77.852 associações aeronave–configuração. São relações de catálogo, não voos, meios físicos ou carregamentos executados.

| Resultado de referência nas associações aéreas | Quantidade |
|---|---:|
| Sem linhas de armamento na configuração | 17.041 |
| Peso incompleto com payload positivo | 35.441 |
| Diferença nominal não negativa | 11.149 |
| Payload não informado/zero | 13.578 |
| Massa nominal superior ao WeightPayload | 643 |

A classificação verifica primeiro ausência de itens, depois payload e então massa. Portanto os grupos são exclusivos, mas payload desconhecido pode coexistir com massa incompleta. Nenhum dos 11.149 casos é aprovação operacional, e nenhum dos 643 casos comprova isoladamente erro físico: unidade, contabilização, definição de payload e configuração exigem avaliação.

No conjunto de loadouts, 11.796 possuem soma nominal padrão definida (incluindo configurações vazias e opcionais fora da soma); 19.462 são incompletos. Há 29.881 ocorrências de massa ausente/zero nas linhas examinadas, não esse número de armas distintas. Uma massa desconhecida é sinalizada e não substituída por zero.

A conferência adicional de WeaponRecord preserva as duas anomalias identificadas antes: ID 9428, DefaultLoad=400 e MaxLoad=100, associado a Oerlikon 20 mm; ID 9750, Multiple=0, associado a foguete Sea Guard. Esses registros pertencem às cadeias de paiol/suporte e não produziram as ocorrências de peso dos loadouts. Nas fichas, quantidade conflitante e Multiple não esclarecido bloqueiam a massa nominal da linha.

Relatório: `prototype/data/db3k-armament-payload-audit-10.json`, SHA-256 `5515f2acac03176b02c5404ebb1f62561e9414a2ed7892ce627ceb84cd8c38f3`, fora do GitHub. Ele usa a compilação de hash `de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9` e a origem DB3K de hash `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`.

## Exemplo conferido e testes

Aircraft/3 SH-60B, loadout 7852: 2 Mk46 com massa cadastrada de 235, 16 DIFAR de 10 e 8 DICASS de 17 resultam em 766 de massa nominal sob hipótese kg. WeightPayload=3031; diferença nominal=2265. Isso não representa 2265 kg operacionais disponíveis.

No loadout 56, o tanque externo 120 USG tem Weight=0. A parcela conhecida é 531 sob hipótese kg, mas o total e a diferença com o payload ficam nulos. A ausência de massa do tanque não é suprida pelo volume no nome nem por densidade presumida; o peso de combustível e tanque exige fontes/contabilização próprias.

Os treze verificadores passaram. `check_armament_payload.py` cobre cálculo nominal por linha, alternativas, opcionais, falta de massa/limite, carga conflitante, Multiple diferente de 1, referências ausentes, instalação repetida, reserva de suporte, subcomponentes sem dupla contagem e auditoria de cobertura/recusa de sobrescrita. Os testes de autorização existentes permanecem válidos para o mesmo endpoint.

Em Edge foram verificadas as configurações 7852 e 56, a tabela/margem nominal, o bloqueio de margem quando há massa incompleta, navios sem payload aéreo inferido, seletores, exportação e tela de 390 px. As consultas anteriores de combustível/propulsão, sensores, perfis e controle de acesso continuam passando. Nenhum dado original foi corrigido ou promovido nesta etapa.
