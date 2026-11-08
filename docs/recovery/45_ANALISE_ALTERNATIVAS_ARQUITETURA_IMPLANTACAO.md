# 45 — Análise de alternativas de arquitetura e implantação

**Resultado:** comparação conceitual elaborada antes das APR-06–APR-09. O responsável aprovou conceitualmente autoridade do backend, separação lógica em cinco domínios, orientação futura híbrida e implantação inicial centralizada, com ressalvas em [49](49_REGISTRO_DECISOES_APR_01_A_APR_20.md). Onde a análise abaixo divergir, 49 prevalece. A aprovação conceitual não autoriza implementação, integração ou definição de tecnologia.

## Contexto observado

O ATLANTICADOR 2.0.0 está organizado como aplicação Python com frontend estático servido na mesma origem, rotas JSON no próprio `serve.py`, serviços internos e SQLite; não foi identificado contrato OpenAPI (17, 23–28). O frontend usa módulos ES, Leaflet, API same-origin e estado de rascunho local (29–34). A rota frontend de eventos diverge do backend (POST 410), mostrando risco de tratar interfaces internas como contrato estável (31). Não há integração SISCAN comprovada.

## Alternativas

| Alternativa | Descrição | Vantagens | Desvantagens/riscos | Dependências |
|---|---|---|---|---|
| A — SISCAN como módulo integrado no processo/produto ATLANTICADOR | Acrescentar domínios SISCAN ao aplicativo existente, compartindo deploy, autenticação, backend/API e potencialmente persistência; separar logicamente dados didáticos. | Reaproveita servidor/origem e potencialmente viewer; menor duplicação de deploy. | Acoplamento aos ciclos, papéis, APIs e modelo de dados ATLANTICADOR; risco de misturar estados/cartografia/ensino; escalar evolução separada é mais difícil; API interna ainda sem contrato estável. | Permissão de modificação/redistribuição; refatoração de limites; contrato de dados; isolamento de acesso e persistência. |
| B — SISCAN como aplicação lógica independente que consome serviços documentados do ATLANTICADOR | SISCAN mantém domínios, backend e dados próprios; adapta ou consome serviços do ATLANTICADOR para cartografia, enquanto cada sistema mantém autoridade sobre seus dados. | Independência de evolução; separa exercício didático; reduz acesso direto a banco; pode preservar viewer como componente/cliente. | Dependência de disponibilidade/versionamento de serviços; identidade entre sistemas; sincronização e mapeamento; atualmente API não é contrato externo e há divergência `events`/410. | API estável e versionada, adaptador, SSO/identidade se aprovado, mapeamento de fontes e política de falhas. |
| C — SISCAN independente com componentes cartográficos avaliados/adaptados, sem depender do backend ATLANTICADOR | SISCAN tem backend/persistência próprios e avalia reutilizar Leaflet/utilitários UI sob licenças; ATLANTICADOR permanece fonte de referência. | Maior independência de releases e dados do simulador; separação forte de autoridade e domínio. | Pode duplicar trabalho de integração/cartografia; cada componente exige licença, validação, manutenção e adaptador; risco de reescrita sem razão. | Decisão de compatibilidade cartográfica; licenças; interfaces GEO/SYM; capacidade de manter componentes. |
| D — Aplicação independente e construção de cartografia própria | SISCAN desenvolve toda experiência cartográfica e serviços próprios, sem reuso de código/runtime ATLANTICADOR. | Máximo controle sobre requisitos, dados e segurança de fronteira. | Maior escopo e custo; perda de recursos existentes; pode contrariar intenção de evitar reescrita desnecessária. | Justificativa técnica de não reuso, fontes geográficas, tecnologia, equipe e cronograma. |

## Comparação por critérios

| Critério | A integrada | B independente + serviços ATLANTICADOR | C independente + componentes adaptados | D própria |
|---|---|---|---|---|
| Independência de evolução | Baixa | Alta no domínio, depende do contrato externo | Alta | Alta |
| Preservar viewer existente | Alta potencial | Alta potencial via serviço/componente | Potencial, após licença/adaptação | Baixa |
| Isolamento didático e MPNL | Exige fronteiras fortes | Mais direto | Mais direto | Mais direto |
| Dependência de APIs atuais | Alta | Muito alta até contrato estável | Baixa no backend ATLANTICADOR | Nenhuma direta |
| Exposição a risco de schema atual | Alta se banco/serviços compartilhados | Baixa se somente DTOs oficiais | Baixa | Nenhuma |
| Requisitos de licença | Código, bundle, deploy | API e componentes incorporados | Componentes reutilizados | Dependências novas/implementadas |
| Prontidão demonstrada | Não verificada | Não verificada | Não verificada | Não verificada |

## Recomendação técnica proposta

**Orientação aprovada em APR-08/09:** adotar conceitualmente a alternativa híbrida C para evolução futura; o primeiro protótipo e primeiras simulações são centralizados, com backend/banco em servidor central e navegador nos terminais. O ATLANTICADOR é tratado conceitualmente como módulo terrestre com interfaces controladas e edição/gestão própria de indicadores. A comparação abaixo permanece material de análise; não define contratos, serviços ou tecnologia. Não há integração autorizada ou realizada.

As recomendações originais desta análise foram superadas nos pontos cobertos pelas APR-06/07. A decisão atual está em 49; detalhes técnicos continuam pendentes.

## Autoridade de dados e separação de estados

### DEC-021 — autoridade do backend (DECIDIDO conceitualmente em APR-06)

O backend é autoridade para autenticação, autorização e persistência oficial; a visão adversária fica bloqueada por padrão no primeiro protótipo e só pode ser autorizada pelo instrutor sob controle do backend. Rascunho local não se torna oficial por si só. A especificação técnica e as permissões detalhadas permanecem pendentes (49 APR-06).

### DEC-022 — separação lógica dos domínios (DECIDIDO conceitualmente em APR-07)

Manter cinco domínios logicamente separados: cartográfico, didático, técnico, logístico e histórico, integrados por interfaces/regras controladas. Não exige bancos físicos separados. Contratos e desenho técnico são pendentes (49 APR-07).

## Interfaces conceituais, ainda sem contratos

- SISCAN ↔ componente cartográfico: leitura de camadas, versão/CRS, seleção e viewport; edição se explicitamente autorizada.
- SISCAN backend ↔ frontend: exercício e versões, escopos/capacidades, rascunho/submissão/avaliação, eventos e erros versionados.
- SISCAN ↔ serviços ATLANTICADOR, se alternativa B: adaptador de API com autenticação, autorização, timeout, mapeamento e política de indisponibilidade; sem acesso às tabelas privadas.
- Importação DB3K não é interface de integração pronta; exige proveniência, semântica/unidades e versão.

## Riscos e condições bloqueadoras

1. Não há API externa estável comprovada; a divergência de eventos demonstra incompatibilidade de superfície.
2. O responsável informou em APR-15 que o uso do Calunga é aberto e sem restrições institucionais, acadêmicas ou comerciais; a integração foi aprovada conceitualmente. Não houve inspeção técnica da licença nem integração. Assets e outras dependências mantêm sua avaliação própria.
3. Compartilhar identidade de usuário não significa compartilhar autorização ou conteúdo didático.
4. Qualquer cenário/exercício persistido deve preservar versão e histórico conforme política a aprovar.
5. MPNL precisa poder funcionar sem viewer/cartografia, segundo concepção 01/08.
6. Nenhum banco DB3K ou `situation.sqlite3` deve ser exposto diretamente ao frontend ou tratado como esquema SISCAN.

## Questões para responsável

APR-06–APR-09 encerraram as decisões conceituais sobre autoridade, domínios e orientação de implantação. Interfaces, especificação técnica, identidade/versionamento e bases seguem pendentes conforme 49. O documento 48 é pauta histórica; 49 registra as decisões atuais.
