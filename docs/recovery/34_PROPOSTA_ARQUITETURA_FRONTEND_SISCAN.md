# 34 — Proposta conceitual de arquitetura do frontend SISCAN

**Natureza:** proposta de organização para avaliação, derivada da auditoria estática. Não aprovada, não implementada e não substitui decisões existentes. Preserva o frontend ATLANTICADOR como ponto de referência cartográfica quando tecnicamente viável, sem acoplar a UI SISCAN a detalhes internos do simulador ou DB3K.

## Princípios

1. Manter inicialmente HTML/ES Modules/Leaflet do ambiente existente; reescrita tecnológica só com justificativa documentada.
2. Distinguir visualizador cartográfico, editor de cenário e telas didáticas.
3. Separar modelo de apresentação de entidades de domínio e da persistência.
4. Falar com backend por interfaces estáveis e adaptadores; não acessar esquema SQLite/DB3K diretamente no browser.
5. Separar dados geográficos de dados didáticos, mesmo quando apresentados em sobreposição.
6. Autorização vem do backend; filtros de interface não protegem dados.
7. Classificações da Missão 02-C não aprovam cópia de código.

## Organização em camadas proposta

| Camada frontend | Papel conceitual | Relação aos módulos SISCAN |
|---|---|---|
| `shell` e navegação | Layout, sessão, navegação e componentes comuns; perfis instrutor, aluno, avaliador e administrador conforme permissões retornadas pelo servidor | Navegação para GEO, AST, SCN, FOR, DID, SIM, ANA, NAV, LOG, PRC, MPNL e HIS. |
| `api-client` / adaptadores | Encapsula endpoints, serialização, erros, sessão e tipos de resposta; não expõe DB | Interfaces do backend por módulo e contrato versionado futuro. |
| `geo-viewer` | Leaflet, projeções/coordenadas, camadas, geometrias, seleção e apresentação cartográfica | GEO; fornece componentes cartográficos aos outros módulos por API UI. |
| `sym` | Catálogo, geração e validação de símbolos com proveniência/licença | SYM; desacoplado da biblioteca específica até liberar uso. |
| `domain-ui` | Telas e formulários próprios de plataforma, cenário e força | AST, SCN, FOR; modelos definidos pelo SISCAN, não por JSON do ATLANTICADOR. |
| `didactic` | Ferramentas de exercício, etapas, hipóteses e adjudicação explícita | DID, SIM, PRC. Não confundir recurso visual com simulação validada. |
| `analysis` | Consultas, gráficos, relatórios, navegação temporal e logística | ANA, NAV, LOG, MPNL. |
| `history` | Exibição de histórico e trilhas do servidor | HIS; somente leitura conforme permissões e filtros do backend. |
| `local-draft` | Rascunhos transitórios no browser com exportação/importação controlada | Rascunhos SCN; estado local não se torna dado oficial até ação explícita validada pelo servidor. |

## Interface cartográfica e telas didáticas

Viewer deve ter contrato de entrada explícito (camadas, geometria, CRS, propriedades de apresentação) e ações de retorno declaradas (seleção, viewport, edição se habilitada). TELAS DID/ANA/LOG podem consumir o viewer via eventos/props/adaptadores em vez de acoplar diretamente a `viewer.mjs`. Edição de cenário deve operar sobre DTOs de rascunho versionados; publicação/validação pertence ao backend. A distinção dos estados local, submetido, aprovado e publicado deve ser visível.

## Dados, papéis e permissões

Backend retorna dados de domínio já autorizados e capability set para instrutor/aluno/avaliador/administrador. Frontend controla affordances e mensagens; API autoriza cada leitura/escrita. Não armazenar credenciais ou dados sensíveis em `localStorage`; usar armazenamento local apenas para preferências e rascunhos explicitamente permitidos, com escopo/expiração e identificação de versão. Não manter cópias de estado oficial como fonte de verdade.

## Comunicação e contratos

Criar, em fase posterior autorizada, interfaces de API documentadas por módulo, com schemas de request/response, paginação, revisão/versionamento, erro uniforme e limites para arquivo/geometria. O browser consome o contrato; mapeadores convertem DTOs para modelos de visualização. As rotas internas atuais do ATLANTICADOR servem de evidência de integração, não como contrato obrigatório do SISCAN.

## Integração cartográfica existente

Recomendação conceitual: preservar Leaflet e os componentes cartográficos que passem por revisão técnica/legal; primeiro separar dependências e contratos, sem reescrever a interface inteira. Manter um adaptador para fontes/camadas ATLANTICADOR apenas enquanto necessário à transição. Não transferir automaticamente modelos de efeitos, party/DIREx, Calunga, workflows, nem estruturas de persistência.

## Questões antes de aprovar arquitetura

- Quais componentes ATLANTICADOR estão licenciados e podem ser redistribuídos?
- Qual biblioteca/formato geográfico e CRS serão oficiais para GEO?
- SISCAN requer editor cartográfico ou viewer com marcações didáticas controladas?
- Quais dados dos módulos AST/SCN/FOR podem ser expostos em mapa e sob qual permissão?
- Como SIM, PRC e arbitragem humana se distinguem e que resultados são persistidos?
- Quais preferências/rascunhos podem permanecer no browser e por quanto tempo?
- Quais perfis e capacidades concretas o backend deve emitir?

Esta proposta deve ser lida junto das decisões SISCAN nos documentos 01–10 e da matriz de avaliação 33. Ela não inicia implementação nem altera decisões existentes.
