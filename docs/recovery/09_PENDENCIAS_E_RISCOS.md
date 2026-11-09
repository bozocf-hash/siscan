# 09 — Pendências e riscos

## Atualização de evidências locais — 2026-11-08

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
