# 82 — Pesquisa e proposta conceitual do CPC

Complementação posterior em [83 — Algoritmo conceitual CPC](83_ALGORITMO_CONCEITUAL_CPC_REFERENCIA_COMMAND.md): investigação do manual oficial/instalação do Command e pseudocódigo próprio para ensaio, adjudicação e aplicação de efeitos. A proposta não recupera código proprietário nem fornece coeficientes físicos validados.

**Data da pesquisa: 2026-11-11. Estado: estudo preliminar para discussão.** Pedido do responsável: fundamentar o CPC — Comparação de Poderes Combatentes — nas interações de superfície, submarinas e aéreas, com apuração assistida ou julgamento didático do instrutor. Não é especificação aprovada, modelo calibrado ou implementação. Nenhum coeficiente de plataforma/armamento foi aprovado ou calculado neste estudo.

## Conclusão proposta

Construir um CPC **multimodelo, didático e auditável**, com quatro responsabilidades separadas: caracterizar as forças no contexto do exercício; comparar capacidades por critérios explícitos; produzir uma proposta quando houver modelo adequado; registrar a decisão oficial do instrutor e os efeitos confirmados. O consumo de recursos é um registro próprio, não uma porcentagem presumida a partir do resultado do confronto.

Essa é uma recomendação para o SISCAN, fundamentada nas referências abaixo; não representa um modelo pronto encontrado na literatura. O projeto deve poder funcionar no modo didático manual enquanto os modelos numéricos continuam em desenvolvimento.

## Referências consultadas e alcance da leitura

| Fonte primária | Conteúdo efetivamente consultado | Contribuição e limite |
|---|---|---|
| [UK MOD, Wargaming Handbook, 2017](https://www.gov.uk/government/publications/defence-wargaming-handbook) — [PDF](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/641040/doctrine_uk_wargaming_handbook.pdf) | Seção 3.10–3.12, páginas impressas 43–44, páginas PDF 55–56 (índices 54–55) | Distingue arbitragem livre, por regras e semirrígida; no último caso o árbitro pode modificar a apuração. Sustenta os dois caminhos do SISCAN, sem fornecer parâmetros de armas. Não houve leitura integral das 112 páginas. |
| [HM Treasury, MCDA, orientação de 2024](https://www.gov.uk/government/publications/green-book-supplementary-guidance-use-of-multi-criteria-decision-analysis/use-of-multi-criteria-decision-analysis-in-options-appraisal-of-economic-cases) | HTML: definição, critérios, ponderação e análise de sensibilidade | Fundamenta comparação transparente e teste da influência dos pesos. É orientação de avaliação de opções de políticas públicas, não modelo de combate. Sua aplicação ao CPC é uma adaptação proposta. A orientação diferencia MCDA de mera soma arbitrária de pontos. |
| [Hughes, 1995, Naval Research Logistics, DOI](https://doi.org/10.1002/1520-6750(199503)42:2%3C267::AID-NAV3220420209%3E3.0.CO;2-Y) | Página editorial e resumo do artigo “A salvo model of warships in missile combat used to evaluate their staying power” | Exemplo de família especializada de análise exploratória naval. Não foi lido o texto integral nem extraídos equações/coeficientes. Não autoriza generalizar o modelo para todos os encontros ou converter atributos DB3K diretamente em probabilidades. |
| [NASA-STD-7009, página oficial da revisão B](https://standards.nasa.gov/standard/NASA/NASA-STD-7009) e [FAQ de modelagem/simulação](https://public.ksc.nasa.gov/mns/faq/) | Escopo oficial e definições de verificação, validação e usos permitidos | Apoiam distinguir código correto, representação adequada ao uso e limites declarados. Não oferecem parâmetros militares nem certificam o SISCAN. Não houve auditoria de conformidade à norma. |

Foram também localizadas páginas institucionais NPS/RAND e material histórico de MCDA de 2009. Não foram usados para inferir coeficientes ou afirmar validação naval cruzada. A orientação MCDA de 2024 substituiu a antiga orientação no portal britânico; este estudo utiliza o documento de 2024, sem afirmar que seja norma militar ou método universal.

## Relação com as decisões existentes

Preservar 35 DEC-001/018/019, APRs em 49, autorização de dados em 53, lacunas técnicas de 66/69 e decisões de confronto/indicadores em 80/81. Nome funcional solicitado: **CPC**. Manter por enquanto o ID estável `force-confrontation` no mapa de capacidades. A relação nominal de CPC com PRC/SIM deverá ser esclarecida na futura especificação; não apagar os conceitos anteriores silenciosamente.

O operador configura/seleciona a funcionalidade dentro dos limites do exercício. O instrutor sempre define o resultado oficial. Configurar rubrica, iniciar apuração, confirmar resultado e aplicar efeito são permissões diferentes. Informação usada internamente no encontro não é automaticamente revelada ao adversário, conforme APR-06.

## Comparar não equivale a prever o vencedor

Proponho começar com um **perfil por dimensões**, condicionado ao objetivo didático e ao cenário: composição/configuração, estado operativo, qualidade da informação disponível, compatibilidade de capacidades declaradas, sustentação/estoques e limitações dos dados. Cada dimensão explicita evidência e lacunas; não gera vantagem universal por tipo de plataforma.

Um indicador agregado, se adotado, deve ter regra, escalas, pesos e finalidade aprovados. Não confundir uma nota de comparação com probabilidade de vitória ou dano esperado. Uma capacidade obrigatória ausente não deve ser compensada apenas por notas altas em atributos sem relação com aquela função. “Desconhecido” também não equivale a “inexistente”.

Sensibilidade é obrigatória na proposta: verificar se pequenas alterações dos julgamentos didáticos mudam radicalmente a conclusão; mostrar essa instabilidade ao instrutor. Não escolher pesos para forçar um resultado desejado e depois apresentá-lo como descoberta física. Se o objetivo for impor um resultado de ensino, usar e identificar o modo didático direto.

## Interações: contratos próprios, base comum

| Família pedida | Tratamento conceitual proposto |
|---|---|
| Superfície → superfície | Rubrica e pacote de modelo próprios para o encontro; composição e condição de cada unidade preservadas |
| Superfície → submarino | Tratar informação conhecida/desconhecida e compatibilidade declarada sem supor contato ou capacidade a partir do nome da plataforma |
| Submarino → superfície | Contrato direcional distinto; não obter parâmetros invertendo os do encontro anterior |
| Aéreo → superfície | Considerar a configuração/carga e estados explicitamente registrados; não equiparar quantidade de aeronaves a quantidade de navios |
| Superfície → aéreo | Contrato direcional próprio, com informação, configuração e condições documentadas; não reutilizar automaticamente os critérios aéreo → superfície |

Essa tabela define fronteiras de modelos, não descreve procedimentos de ataque ou coeficientes de eficácia. Não fornece parâmetros de emprego de sistemas reais. Outras famílias poderão ser acrescentadas após delimitação e validação de seu uso didático.

O motor comum valida identidade, versão da composição, estado/estoques, domínio dos dados, permissões e histórico. O pacote específico declara entradas obrigatórias, hipóteses, condições em que vale e efeitos abstratos que pode propor. Se faltar entrada essencial, responder “modelo não aplicável / dados insuficientes” e permitir arbitragem manual identificada, sem inventar zeros.

## Duas modalidades com a mesma trilha de decisão

**Assistida:** selecionar forças/contexto e pacote aprovado → congelar entradas/versões → conferir aplicabilidade → gerar comparação/apuração → instrutor aceita, ajusta ou rejeita → registrar decisão → aplicar efeitos confirmados.

**Didática direta:** instrutor seleciona meios e efeitos, inclusive estado operativo desejado → sistema valida domínio, identidade e permissões → registra a origem manual → aplica os efeitos. Não apresentar esse resultado como se tivesse sido calculado.

“Automático” significa execução dos cálculos/consistência pelo software. Não significa publicação automática de vitória, dano ou estado. Se houver sorteio em um modelo futuro, registrar versão do gerador e semente para reprodução; resultados repetidos são análise de cenários condicionada ao modelo, não probabilidades reais demonstradas.

Proposta, decisão e aplicação têm identidades próprias. Falha na gravação de efeitos reverte o lote; repetir o comando não duplica efeitos ou consumo. Mudança posterior do instrutor gera nova decisão/retificação, preservando a anterior. Uma retificação do dano não deve, por si só, devolver munição já consumida.

## Armamento: estoque, utilização e resultado separados

O backend deve manter quantidades por tipo/configuração e unidade de contabilização validada, mesmo que a ficha mostre uma barra geral. Uma ação de utilização confirmada registra quantidade utilizada e estado anterior/posterior. Não deduzir disparos do percentual de avaria, nem deduzir dano da simples quantidade debitada. Uso confirmado pode consumir recurso sem produzir efeito no outro meio.

Antes de confirmação de utilização, uma reserva de estoque, se adotada, é distinta de consumo. A política de reserva/liberação deve ser especificada; não descontar duas vezes a mesma ação ao confirmar depois seu resultado.

Para a barra geral, submeter ao responsável alternativas:

- Percentual de carga de referência por classe, com agregação explicitamente aprovada: preserva diferenças entre classes, mas exige definir referência e pesos.
- Indicador baseado em classes essenciais ao papel didático: evita que uma classe abundante esconda a ausência de outra necessária, mas exige declarar essa essencialidade.

Minha recomendação de pesquisa é combinar resumo agregado com indicação de lacunas críticas, sem soma simples de munições heterogêneas. Não definir agora pesos, classes essenciais ou limiar universal. O exemplo de 30% de 81 não se torna padrão por esta proposta. A regra de restrição efetiva permanece separada da avaliação de origem do instrutor.

## Como construir parâmetros com respaldo

Para cada critério/hipótese, registrar grandeza, unidade, contexto, fonte/localização, versão/configuração, limites e grau de confiança existente no projeto. Para cada regra didática, registrar quem a aprovou e para qual objetivo de ensino. Parâmetro de ensino e estimativa física são categorias diferentes.

Sequência proposta de pesquisa: definir a pergunta de aprendizagem e a escala temporal; escolher uma família de encontro; identificar os dados realmente necessários; explicitar lacunas; discutir rubrica com especialistas/instrutor; testar casos fictícios com resultados esperados; fazer análise de sensibilidade; só então comparar com evidências independentes apropriadas ao uso. Não usar o mesmo conjunto para ajustar e declarar validado o modelo. Não declarar validade fora das condições avaliadas.

Uma biblioteca de parâmetros deve apresentar **pendente / fundamentado / aprovado para o uso indicado**, sem preencher uma constante só porque o programa exige um número. Acesso ao DB3K e boa integridade estrutural não demonstram taxas de eficácia, probabilidade de acerto ou resposta a dano. Não extraí tais constantes nesta pesquisa.

## Primeiras entregas recomendadas

1. CPC didático direto e registro de efeitos/decisões, ligado ao estado operativo e aos recursos, com autorização do instrutor.
2. Comparação por dimensões e relatório explicável, usando entradas controladas e recusando lacunas obrigatórias.
3. Primeiro pacote assistido restrito e revisável, com hipóteses explícitas e sensibilidade; ampliar para outras famílias somente após verificar o recorte.

É uma ordem conceitual para discutir, não plano de tarefas aprovado. Ponytail: um único serviço de orquestração pode usar os provedores existentes; não criar cinco sistemas independentes ou um framework genérico antes de demonstrar a primeira necessidade.

## Verificações a exigir na futura especificação

Trocar rótulos Azul/Vermelho sem mudar entradas não muda a lógica; dado desconhecido não vira zero; confronto não expõe informação adversária; operador não confirma resultado oficial; proposta não altera estado; lote confirmado é idempotente e atômico; consumo não excede estoque nem ocorre duas vezes; retificação preserva histórico; avaliação de origem e restrição efetiva são distintas; as faixas de 80 e o pré-alerta M+5 de 81 continuam válidos. Teste de software não é calibração física.

## Próximas decisões

Escolher o primeiro objetivo didático/família e a profundidade de abstração; definir composição versus interação temporal; aprovar rubrica e evidências; estabelecer referência/agregação da barra de armamento; esclarecer vínculo nominal CPC/PRC/SIM. O núcleo manual pode ser especificado sem esperar coeficientes físicos universais, preservando todas essas pendências.

Pesquisa consultiva, sem alterações em código, bancos, atributos ou resultados do exercício. Não houve leitura integral dos livros/artigos citados, validação de sistemas reais ou implementação de modelo de confronto.
