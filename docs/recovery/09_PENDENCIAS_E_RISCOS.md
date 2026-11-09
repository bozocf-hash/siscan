# 09 — Pendências e riscos

**Prontidão para o motor, 2026-11-09:** [69](69_PARECER_ENGENHARIA_DADOS_E_PRONTIDAO_MOTOR.md) prioriza ED-01–ED-16: unidade/semântica, camada validada, identidade/snapshot, base das taxas, carga, transações, manifesto, calibração, exceções, referência espacial/temporal, recuperação/concorrência, histórico e MPNL. Os 77.349 atributos importados seguem pendentes; assets ainda não constitui snapshot técnico completo. É possível desenvolver com dados sintéticos, bloqueando somente o cálculo que dependa de dado obrigatório não validado. Não generalizar prontidão estrutural para validade física.

**Massa/payload, 2026-11-09:** [68](68_MASSA_ARMAMENTO_E_PAYLOAD.md) registra a associação e conferência nominal, sem aprovação operacional. A auditoria encontrou 29.881 ocorrências de massa ausente/zero em linhas de loadout e 643 vínculos aéreos com soma nominal acima do WeightPayload. Validar unidade SQL, unidade de contabilização, limite do meio e configuração antes de classificá-los como erros. Persistem WeaponRecord/9428 (400 > 100) e /9750 (Multiple=0), sinalizados sem alteração. Massa de lançador, adaptadores, combustível e limites por ponto não são supridos automaticamente.

**Base de combustível/propulsão persistida, 2026-11-09:** [67](67_BASE_PERSISTIDA_COMBUSTIVEL_E_PROPULSAO.md) registra 54.708 payloads conferidos, 28.757 instalações e 20.544 pontos com destinos encontrados; FKs derivadas sem erro. Isso não resolve as pendências de unidade/escala, fluxo por motor/conjunto, combustível compatível ou efeitos de configuração. As 199 ausências do grafo integral de 65 continuam válidas fora deste recorte. A base específica é separada, consultada somente para leitura e não promove atributos para cálculos.

**Unidades e consumo, 2026-11-09:** [66](66_UNIDADES_E_BASE_DOS_PERFIS_DE_CONSUMO.md) registra rótulos de unidade/evidência na ficha e metadados/perfis por propulsor no backend. O manual confirma kg/kg/min no painel aéreo, sem comprovar a escala SQL ou o fluxo por motor/conjunto. Combustível naval, baterias, SFC, tipo de tonelada e Area mantêm suas pendências específicas. Curvas operacionais exigem essas validações e um perfil temporal; não calcular média simples das linhas nem multiplicar automaticamente pelo número de motores.

**Coleta integral e fichas técnicas, 2026-11-09:** auditoria de 8.010.533 valores sem divergência; fichas reúnem sensores, combustível e propulsão/desempenho sem truncamento ([65](65_LEVANTAMENTO_INTEGRAL_E_DADOS_TECNICOS_COMPILADOS.md)). A fonte tem 20.544 linhas de regime para 3.466 propulsores; somente Static/567 não tem perfis. Três novas regras elevam o total a 243; os 199 valores sem destino incluem 191 Plane=0 da nova relação orbital, além dos oito anteriores. Não representam dados descartados. Permanecem a investigação de unidades/convenções e de códigos incompatíveis, com valores brutos disponíveis agora e sem preenchimento por suposição.

**Compilação e apresentação, 2026-11-09:** entregues grafo medido de 240 regras sobre 167 tabelas e fichas com foto local/componentes para seis categorias ([64](64_COMPILACAO_RELACIONAL_E_FICHAS_TECNICAS.md)). Todas as 75 FKs encontram destinos; oito ocorrências em domínios não declarados estão localizadas. Relações nominais/estruturais continuam distintas de FKs, e unidades/convenções técnicas permanecem em investigação. A compilação não substitui o banco do exercício nem promove instalações/satélites a referências aprovadas. As notas ampliadas previstas foram adiadas conforme a solicitação posterior do responsável.

**Consulta ampliada entregue, 2026-11-09:** o painel do instrutor permite pesquisar e paginar as 11.197 referências/77.349 valores, preservando o painel inicial e suas notas. Foram verificados 224 páginas, valores pendentes, acesso restrito e leitura sem escrita ([63](63_CONSULTA_CATALOGO_AMPLIADO_E_VALORES.md)). A pendência de consulta ampliada deixa de existir; continuam validação semântica/unidades e promoção. A criação de novas notas para todas as referências ampliadas não foi implementada nesta etapa. As menções anteriores à interface limitada aos 80 candidatos são históricas.

**Incorporação bruta concluída, 2026-11-09:** 77.349 valores estão em tabelas de evidência pendente no SISCAN, sem unidade confirmada e sem uso em cálculos ou meios alocáveis. Migração/importação testada, backup e integridade verificados ([62](62_INCORPORACAO_ATRIBUTOS_TECNICOS_BRUTOS.md)). Permanecem pendentes a consulta ampliada na interface, validação semântica/unidades, significado de zero/NULL, diferenças de apresentação e avaliação de extremos. Os estados anteriores de armazenamento apenas externo são históricos.

**Ampliação registrada, 2026-11-09:** a aprovação de identificação para as 11.117 novas referências foi concedida e executada; total 11.197, com 80 IDs anteriores preservados, integridade e idempotência verificadas ([61](61_REGISTRO_REFERENCIAS_AMPLIADAS_DB3K.md)). A decisão de identificação deixa de ser pendência. Continuam pendentes a validação dos 77.349 valores técnicos e a consulta do catálogo ampliado na interface, que ainda utiliza o lote de 80 candidatos. Os estados pendentes de aprovação descritos abaixo são históricos.

**Ampliação preparada, 2026-11-09:** lote separado com 11.197 candidatos conferidos; 11.117 novas referências aguardam decisão do responsável. Perfil de 77.349 valores em 29 pares tabela/campo, com 9.602 zeros e 699 negativos, sem validação de unidades/semântica. Extremos precisam de contexto; não corrigir automaticamente. A interface continua no lote anterior e possui limite de 500 resultados; uma futura troca deve preservar notas e rastreabilidade. Escopo, proposta e hashes em [60](60_EXPANSAO_REFERENCIAS_E_PERFIL_TECNICO_DB3K.md).

**Fechamento atual da amostra, 2026-11-09:** quatro fichas identificadas no visualizador 498a; 18 valores examinados, 17 correspondências numéricas e uma diferença em MastHeight (SQL 3.26; interface 3 m), sem causa comprovada. Area=25.96 aparece com m, sem confirmação de domínio/unidade. IDs 3 e 377 compartilham o nome AAVP-7A1; usar tabela/ID/origem. A amostra não valida o catálogo nem aprova atributos. Permanecem as pendências semânticas e a leitura ampliada do deslocamento pleno naval adicional. Resultado consolidado em [59](59_ROTEIRO_COMPARACAO_VISUAL_DB3K.md); contagens menores abaixo são históricas.

**Avanço submarino, 2026-11-09:** Submarine/3 identificado em 498a; cinco campos coincidem com SQL 498/498a, com MaxDepth=-320 exibido como -320 m. Contagem atual: três fichas, 14 de 18 valores preparados. GroundUnit/3 e a leitura ampliada do deslocamento pleno de Ship/3 seguem pendentes. Não generalizar sinais, zeros, NULL ou unidades; os 580 atributos continuam sem aprovação para uso. Detalhes em [59](59_ROTEIRO_COMPARACAO_VISUAL_DB3K.md); contagens menores abaixo pertencem aos estágios anteriores.

**Avanço naval, 2026-11-09:** Ship/3 identificado em 498a, quatro dimensões comparadas; duas fichas e nove dos 18 valores preparados têm correspondência numérica observada. Zeros recebem apresentação diferente conforme o campo, e tons permanece unidade literal sem domínio confirmado. Full Displacement requer ampliação para leitura segura. Submarine/3 e GroundUnit/3 ainda pendentes. Os 580 valores continuam sem aprovação para uso; detalhes em [59](59_ROTEIRO_COMPARACAO_VISUAL_DB3K.md).

**Resultado atual da observação assistida, 2026-11-09:** o visualizador DB3K_498a foi acessado e o cabeçalho #3 — SH-60B Seahawk (United States - 1991) foi confirmado junto às dimensões. Cinco valores de GENERAL DATA lidos ao longo das capturas coincidem com Aircraft/3 em 498 e 498a. A identificação visual desta ficha deixa de ser pendência; permanecem a ampliação da amostra, a comparação direta no visualizador 498, a divergência com a descrição textual e a validação semântica dos atributos. Fonte, hashes e limites em [59](59_ROTEIRO_COMPARACAO_VISUAL_DB3K.md). Isso complementa os estados históricos abaixo.

## Atualização de evidências locais — 2026-11-08

**Complemento de 2026-11-09:** a janela do jogo confirmou Command v1.05 — Build 1307, mas o visualizador não foi acessado. A seção 6.3.4 do manual digital foi consultada; texto e figura usam versões de banco diferentes (478 e 473). É necessário confirmar o banco ativo antes de comparar com 498. Amostra de quatro registros e 18 valores brutos preparada em [59](59_ROTEIRO_COMPARACAO_VISUAL_DB3K.md); todos seguem sem validação de unidade SQL.

As restrições de fase ao final deste registro descrevem seu encerramento histórico; houve autorização posterior do responsável para desenvolvimento do protótipo. Permanecem válidas as pendências semânticas DB3K.

- **P-03, fonte adicional:** o manual instalado do CMO tem 353 páginas e forneceu texto em três páginas amostradas. Ainda não foi lido integralmente; não confundir essa fonte com o PDF digitalizado anterior.
- **P-04, comparação pendente:** o banco instalado DB3K_498 é binariamente idêntico à fonte de trabalho. Templates fornecem rótulos de apresentação, mas não comprovam conversões SQL. O lançador foi observado com versão 1.05.1307; nenhuma ficha foi examinada, devido às interrupções da interação. Os 580 valores técnicos permanecem pendentes. Evidências e procedimento de retomada em [58](58_FONTES_LOCAIS_CMO_E_TEMPLATES.md).

## Evidência e semântica ainda pendentes

| ID | Pendência | Efeito |
|---|---|---|
| P-01 | ZIP do ATLANTICADOR não informa commit/branch e não é checkout Git | Não é possível atribuir achados a revisão ou comparar mudanças |
| P-02 | Repositório não foi executado e implantação não foi conferida | Estado funcional/configuração em produção não confirmados; inspeção estática apenas |
| P-03 | Manual CMO sem camada de texto útil; 353 páginas submetidas a OCR, mas inspeção visual de páginas/figuras foi por amostragem | OCR pode perder detalhes pequenos; não houve inspeção visual integral. Consultar fonte para decisão específica; controle no documento 12 |
| P-04 | DB3K: integridade estrutural e inventário foram verificados; 75 FKs declaradas foram identificadas, enquanto pares por nomes são inferências. Semântica, unidades e domínios de muitos campos permanecem sem documentação segura | Não converter diretamente catálogo ou relações candidatas em modelo SISCAN; unidades/escalas não podem ser assumidas |
| P-05 | Histórico original de conversas/atas não fornecido | Não confirma evolução, datas ou divergências anteriores à Missão 01 |
| P-06 | Dados geográficos e fontes de parâmetros SISCAN ausentes | Cobertura, licença, resolução e validade não avaliadas |
| P-07 | IDs e correspondências do DB3K não foram validados quanto à estabilidade entre versões nem semântica das tabelas | Risco de vínculo incorreto ao comparar versões ou reutilizar informação |

## Especificações e decisões de produto ainda necessárias

As APR-01 a APR-20 foram apreciadas pelo responsável. O documento [49 — Registro consolidado das decisões](49_REGISTRO_DECISOES_APR_01_A_APR_20.md) prevalece sobre os status anteriores desta lista. A tabela abaixo deve ser lida como lacunas de detalhamento/execução: uma decisão conceitual aprovada não significa que todos os parâmetros e critérios foram fechados.

- **P-08:** critérios verificáveis de aceite, conteúdo do cenário e critérios/etapas do fluxograma da avaliação; rubrica própria por exercício preserva julgamento humano.
- **P-09:** detalhar permissões por ação/exercício, autenticação, isolamento entre equipes, retenção e recuperação de conta; papéis e autoridades APR-02/03 estão decididos conceitualmente.
- **P-10:** fonte/resolução da máscara terrestre, margem, tolerância, coordenadas e tratamento de dados inválidos.
- **P-11:** unidades, calibração, origem, validade e incerteza das curvas de consumo.
- **P-12:** regras técnicas de retrocesso/revisão/ramificação; eventos e avaliações não se apagam (APR-16), mas NAV pode ficar fora da primeira demonstração.
- **P-13:** critérios, escalas, sinergias, incerteza e validação acadêmica do PRC; hipótese First Strike.
- **P-14:** para MPNL, menor unidade efetivamente incluída em cada exercício, dados de demanda/falha, lead time, nível de serviço, compartilhamentos, arredondamentos e premissas orçamentárias. A estrutura organizacional de quatro níveis e a consolidação ascendente estão decididas e documentadas em 08; parâmetros quantitativos não.
- **P-15:** esquema técnico/versionamento de modelo, configuração e unidade, embora IDs próprios SISCAN e snapshot contextual estejam decididos (APR-10); política de alteração de cenário segue APR-11.
- **P-16:** formatos/leiautes/métricas de relatórios e critérios de aceite; produtos mínimos ANA estão decididos conceitualmente (APR-20).
- **P-17:** fronteiras de integração: mapa/autenticação/eventos ATLANTICADOR, persistência e suporte MPNL sem cartografia.
- **P-18:** avaliação das referências CMO nos documentos 13–14, sem adoção automática ou alteração de decisões anteriores.

## Divergências e riscos identificados

- ATLANTICADOR: inspeção estática identificou registros/arbitragem humana e modelos de cálculo no front-end; documentação 2.0 informa que os cálculos não são aplicados automaticamente. Isso não define reutilização no SISCAN.
- DB3K: integridade `ok` comprova integridade estrutural no momento da leitura, não correção semântica. Inventário de tabelas/colunas não equivale a entendimento de domínio. FK declarada é evidência estrutural; correspondência nominal inferida não é vínculo confirmado.
- Tipos/nome de coluna SQLite não asseguram unidade, escala, significado ou regra; campos como comprimento, peso, alcance, altitude e custo exigem fonte de domínio.
- O manual CMO não apresenta esquema relacional formal; relações conceituais do texto não confirmam cardinalidade ou chaves.
- OCR de 353 páginas não significa inspeção visual de 353 páginas; capturas pequenas e tabelas podem conter texto não recuperado.
- ZIP sem referência Git e implantação não acessada não equivalem a estado de produção.
- Controle de acesso apenas no cliente pode expor submissões; autorização deve ser definida e verificada no servidor.
- Recursos logísticos compartilhados podem ser contados em duplicidade; bases técnica, logística e econômica devem permanecer distinguíveis.
- Máscara costeira inadequada à resolução pode rejeitar posições válidas ou aceitar posições em terra.

Não foi possível comparar requisitos com decisões históricas além das fontes fornecidas. As hierarquias e regras MPNL decididas estão consolidadas em 08; lacunas quantitativas permanecem pendentes. A pauta APR-01–APR-20 foi concluída e incorporada em 49. Nenhuma conclusão autoriza auditoria técnica adicional, arquitetura definitiva, implementação ou início da próxima fase.
