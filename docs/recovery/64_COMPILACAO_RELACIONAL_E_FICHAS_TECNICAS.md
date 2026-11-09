# 64 — Compilação relacional completa da fonte e fichas técnicas

## Objetivo e entrega — 2026-11-09

O responsável solicitou retomar a associação automática dos dados Command, sem montagem manual de cada vínculo no chat, e apresentar os meios por categoria em fichas com foto, dados técnicos e componentes, usando a navegação do CMO como referência.

Foi criada uma compilação separada da fonte integral: **167 tabelas, 766.989 registros**, preservando todos os campos das linhas examinadas, e um grafo de **240 regras de relacionamento**. A nova tela do instrutor permite navegar em seis categorias, selecionar um meio, ver sua imagem local quando disponível e abrir equipamentos relacionados. Não replica código ou templates de apresentação do CMO; a interface usa componentes próprios do SISCAN.

As observações de revisão que estavam previstas como próximo incremento foram adiadas em favor desta solicitação. As notas existentes e os dados do exercício foram preservados.

## Fonte e compilação

Fonte original: `C:\Users\bozoc\Documents\siscan\DB3K_498.db3`, SHA-256 `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`. Ela foi aberta com SQLite mode=ro/query_only e seu hash foi conferido ao final.

O compilador `tools/compile_db3k.py` gera um novo banco sem substituir arquivos existentes. O esquema neutro contém source, tables, records, relations e links: inventário de colunas, todas as linhas em JSON, identidade por tabela/rowid da fonte, regras e destinos medidos. Não se reutiliza o ID externo como identidade de unidade SISCAN. Valores binários, quando presentes, recebem representação base64 explícita; valores numéricos/NULL não são convertidos em unidades ou estimativas.

Artefato entregue: `C:\Users\bozoc\Documents\siscan\prototype\data\db3k-compiled-05.sqlite3`.

| Evidência | Regras | Vínculos com destino único | Sem correspondência |
|---|---:|---:|---:|
| FK declarada | 75 | 684.229 | 0 |
| Padrão estrutural de componentes/parentesco | 60 | 402.711 | 0 |
| Domínio nominal específico | 105 | 750.922 | 8 |
| Total | 240 | 1.837.862 | 8 |

Uma ocorrência corresponde a uma linha/campo submetida a determinada regra; não é quantidade de unidades físicas nem de equipamentos instalados. Tabelas vazias não fornecem prova empírica de cardinalidade. Correspondência com destino único mede integridade do vínculo proposto, sem equivaler a comprovação semântica para as relações não declaradas.

O CSV inicial `03_relacionamentos.csv` contém muitas hipóteses geradas por nomes idênticos de coluna contra PKs. Ele não foi usado como conjunto de relações confirmadas. O compilador aplica FKs e regras específicas por família, e mede os resultados em todas as linhas. Um teste impede, por exemplo, associar Type de assinatura a EnumShipType; seu domínio é EnumSignatureType.

### Cadeias de componentes

Foram montados os vínculos das plataformas com sensores, comunicações, combustível, propulsão, suportes, paióis, configurações de carga, instalações auxiliares e assinaturas, quando presentes. A cadeia de armamento preserva o registro intermediário:

```text
Plataforma → associação de suporte → DataMount
DataMount → DataMountWeapons → DataWeaponRecord → DataWeapon
Aeronave → DataAircraftLoadouts → DataLoadout
DataLoadout → DataLoadoutWeapons → DataWeaponRecord → DataWeapon
DataWeapon → sensores, propulsão, combustível, comunicações e ogivas
DataPropulsion → DataPropulsionPerformance
```

Em DataMountWeapons, os 6.151 ComponentID encontram DataWeaponRecord; apenas 3.035 encontravam DataWeapon diretamente. Em DataLoadoutWeapons, os 86.981 encontram DataWeaponRecord; a ligação direta a DataWeapon encontrava 59.154. Isso demonstra por que a tabela intermediária deve ser preservada. Os parâmetros da associação (ComponentNumber, arcos, Optional, Internal, entre outros) permanecem junto ao vínculo, sem interpretação automática de quantidade ou efeito.

### Oito ocorrências sem correspondência

| Origem | IDs de origem | Valor sem destino na regra aplicada |
|---|---|---|
| DataAircraft.Visibility → EnumAircraftCockpitVisibility | 1850, 4276, 6065 | Texto literal `B,C,C` com sequência literal `\\r\\n`; não é um ID único do domínio |
| DataAircraft.AutonomousControlLevel → EnumAircraftAutonomousControlLevel | 5487, 5703 | 25 |
| Mesmo campo | 5687 | 15 |
| DataWeaponWRA.ShooterQty → EnumWeaponWRAShooterQty | 2192, 2904 | 99 |

Esses valores foram preservados e não receberam destino inventado. Não se conclui automaticamente que sejam erros; podem representar regra, formato especial ou documentação ausente. O JSON local de pendências preserva os valores exatos. Campos como MissonID em órbitas e ESMPreciseEmitterID não foram forçados a relacionamentos apenas por conterem ID no nome. Todos os campos continuam no registro bruto, inclusive os que não possuem regra relacional definida.

## Navegação e apresentação

| Categoria na tela | Registros da fonte |
|---|---:|
| Aeronaves | 6.047 |
| Navios | 4.035 |
| Submarinos | 699 |
| Meios terrestres | 416 |
| Instalações | 3.625 |
| Satélites | 146 |
| Total navegável nas seis categorias | 14.968 |

O instrutor entra diretamente em **Catálogo técnico**. A aba **Exercício e revisão** preserva configuração, alocações, submissões, notificações, referências cadastradas e a revisão dos 80 candidatos anteriores. A seleção de aba é mantida durante atualizações internas do painel.

A ficha contém título, país/ano quando recuperados da fonte, foto, dados gerais, equipamentos agrupados, demais atributos e rastreabilidade. A busca aceita trecho de nome ou ID numérico exato, com 50 resultados por página. Ligações de componentes abrem fichas de sensores, suportes, paióis, configurações, registros de arma e armas, preservando a cadeia. Os detalhes mostram parâmetros brutos e a classe de evidência da ligação. A ficha limita a 1.000 linhas de associação por abertura, com aviso explícito se esse limite for alcançado.

Fotos são servidas da instalação local em `C:\Program Files (x86)\Matrix Games\Command Modern Operations\DB\Images\DB3000`, por tabela/ID e somente ao instrutor autorizado. São identificadas como ilustrativas; nome de arquivo não comprova identidade de unidade física ou versão da foto. Quando ausentes, a ficha informa a ausência. Nenhuma foto foi copiada para o GitHub nem baixada da internet.

As unidades continuam em revisão. Não se acrescenta m/kg/m² a valores por inferência, não se altera o sinal de MaxDepth e não se transforma zero em ausência. A ficha mostra os valores SQL; por exemplo, MastHeight do AAVP-7A1 aparece como 3.26, preservando a diferença com a apresentação 3 m do CMO. As categorias de instalações/satélites vêm da compilação de origem e não foram automaticamente promovidas às 11.197 referências aprovadas.

## API, acesso e segurança

- GET `/api/source-platforms?table=DataShip&q=&page=1`: lista de categoria e contagens, 50 por página.
- GET `/api/source-platform?table=DataShip&id=3`: ficha bruta, domínios, grupos, links diretos e proveniência.
- GET `/api/source-photo?table=DataShip&id=3`: imagem JPEG local quando existente.

Todas as rotas exigem sessão e instrutor atribuído ao exercício demonstrativo, seguindo a mesma regra do catálogo anterior. Consultas usam SQLite somente leitura, nomes de tabela permitidos e parâmetros SQL. Identificadores não aceitam caminhos; o diretório de fotos é fixo. Textos da fonte são apresentados com textContent, sem executar HTML. Não foi alterada a autenticação nem houve publicação externa do serviço.

## Verificação e rastreabilidade

O teste `check_compilation.py` cobre preservação da fonte, leitura de todas as tabelas da fixture, FKs, cadeia suporte/registro/arma, NULL, vínculos ausentes, rejeição de sobrescrita, colisão de domínio de assinatura, consulta da ficha, autorização, parâmetros inválidos e ausência de imagem. Os nove scripts check_*.py passaram. A sintaxe dos dois arquivos JavaScript foi conferida.

A auditoria real verificou `integrity_check=ok`, todas as 75 FKs com destino único e as oito ocorrências não resolvidas. Foram exportados `db3k-association-audit-05.csv`, `db3k-association-unresolved-05.json`, `db3k-compiled-05.json` e `db3k-compilation-manifest-05.json` em prototype/data, fora do GitHub.

| Artefato | SHA-256 |
|---|---|
| Compilação SQLite | bce0f97be890d6e588adaed4cc2e6e34fd2ec4d130b04e350f400460fa516954 |
| Código do compilador usado | b666f5c2ed93eab0e07a93b94848881df323fc7628c3bcc215513e3d7459d122 |

No Edge/Playwright, com perfil isolado, foram conferidos os seis grupos e total de 14.968 plataformas, fotos locais, dados gerais, navegação navio→sensor, valores negativos/fracionários, largura móvel de 390 px, preservação do painel de 80 candidatos e bloqueio de lista/ficha/foto ao aluno. A verificação passou tanto na cópia isolada quanto no serviço atualizado em 8787, sem erro JavaScript observado. As imagens de desktop e móvel foram inspecionadas visualmente.

O banco do exercício não foi substituído. Na verificação anterior à entrega havia 11.197 referências, 77.349 valores brutos, oito meios sintéticos, duas alocações e zero submissões; as alocações criadas pelo responsável foram preservadas. Os testes de navegação não enviaram submissão, alocação ou anotação. O serviço temporário de teste foi encerrado ao final.

## Limites restantes

A compilação cobre todas as linhas e colunas das 167 tabelas desta versão e os vínculos das 240 regras implementadas. Não é uma afirmação de que toda relação semântica possível do software proprietário foi descoberta. As relações estruturais/nominais têm evidência e cobertura explícitas, mantendo a distinção em relação às FKs. Unidades, convenções especiais e significado dos oito casos exigem investigação documental adicional, que pode continuar autonomamente a partir dos registros localizados. A visualização não promove dados para cálculo, arbitragem ou alocação automática.
