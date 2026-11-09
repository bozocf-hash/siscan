# 69 — Parecer de engenharia de dados e prontidão para o motor SISCAN

## Parecer executivo — 2026-11-09

**Podemos continuar a programação e desenvolver o núcleo do motor. Ainda não podemos tratar todo o catálogo Command como entrada física validada para uma simulação oficial.** A base atual é suficiente para preservação, consulta, investigação e associações técnicas. O passo necessário é transformar um recorte desses dados em entradas operacionais versionadas, com unidades, significado e condições de uso comprovados.

Não recomendo esperar um banco universalmente “perfeito”. Recomendo critérios verificáveis por funcionalidade: o motor pode ser desenvolvido com casos sintéticos controlados enquanto os dados de cada capacidade são validados. Uma lacuna de sensor não precisa impedir testar o relógio ou uma transferência logística; uma unidade de consumo desconhecida precisa impedir aquele cálculo de combustível. Campo obrigatório ausente não deve produzir resultado silencioso ou zero presumido.

Este parecer atende ao pedido atual de avaliação e descritivo. Não implementa o motor, não promove atributos, não altera decisões anteriores e não aprova parâmetros numéricos. A autorização de programação concedida posteriormente na conversa continua válida; as restrições históricas das missões documentais não devem ser interpretadas como cancelamento dessa autorização. A promoção de dados permanece sujeita à autoridade registrada em 53.

## 1. O que foi comprovado

Foram consultados código/esquemas atuais, decisões 49/51/53, relatórios e documentos 65–68 e o banco do exercício em modo somente leitura. As contagens e estados abaixo foram reconferidos; não houve nova inspeção visual do Command nem calibração física nesta avaliação.

| Camada | Evidência atual | O que ela permite afirmar |
|---|---|---|
| Fonte/compilação | 167 tabelas, 766.989 registros, 8.010.533 valores comparados sem divergência na auditoria 07 | Os valores da fonte foram preservados; não foram demonstradas todas as unidades/semânticas |
| Relações compiladas | 243 regras, 199 valores sem destino identificados em 65 | Há grafo de consulta rastreável; regras estruturais/nominais não equivalem a FKs originalmente declaradas ou semântica física aprovada |
| Combustível/propulsão | 1.940 combustíveis, 3.467 propulsores, 20.544 pontos e 28.757 instalações na base 09 | O recorte tem persistência SQL, auditoria literal e vínculos encontrados; não valida escala/consumo operacional |
| Armamento/payload | 31.258 loadouts, 86.981 linhas e 77.852 vínculos aéreos examinados em 68 | É possível conferir massa nominal por configuração sob hipóteses explícitas |
| Referências internas | 11.197 referências com UUID SISCAN | Existe identificação de referência; não equivale a unidade física ou configuração operacional aprovada |
| Evidências técnicas importadas | 77.349 valores, todos com unit=NULL e status pending_unit_and_semantics | O banco ainda mantém a barreira entre evidência bruta e atributo utilizável |
| Exercício demonstrativo | 8 meios sintéticos, 2 registros de alocação por partido, 0 alocações individuais | Há fluxo didático inicial, não população operacional de todo o catálogo |
| Integridade do banco demonstrativo | integrity_check=ok e foreign_key_check sem erros nesta consulta | Integridade estrutural neste instante; não comprova todas as regras de negócio |
| Verificação de software | 13 verificadores e testes Edge registrados na entrega 68 | Comportamentos cobertos passaram; não certifica modelos físicos, carga concorrente ou precisão de resultados do motor |

Os 77.349 valores são um recorte importado, não a quantidade de dados levantados: o levantamento integral está na compilação. Não é necessário extrair novamente todo o DB3K para iniciar a próxima etapa.

Os contratos de consulta de consumo e armamento mantêm `calculation_ready=false`. A associação nominal de massa continua sendo análise sob hipóteses; alterar essa flag isoladamente não constitui validação nem aprovação para o motor.

## 2. Prontidão por capacidade

| Capacidade | Situação | Condição para prosseguir |
|---|---|---|
| Catálogo, fichas, busca, componentes e evidências | Disponível no protótipo | Manter rastreabilidade e distinção entre fonte e aprovação |
| Núcleo de estados, tempo e eventos | Pode começar a ser programado | Contrato pequeno e casos sintéticos com resultados esperados |
| Identidade modelo/configuração/unidade e snapshots técnicos | Precisa ser implementada além da referência literal | Aplicar APR-10 e impedir mudança retroativa de atributos em uso |
| Consumo/autonomia com dados Command | Ainda não pronto para resultados oficiais | Validar unidades, base da taxa, combustível compatível, regime/faixa e modelo de cálculo |
| Peso/carga com dados Command | Conferência nominal disponível | Validar massa/unidade de contabilização, limite operacional e demais cargas/restrições |
| Sensores, detecção e alcance efetivo | Dados recuperados; modelo não validado | Definir modelo, referências espaciais e condições; alcance cadastrado não implica detecção garantida |
| Estoques e movimentação de recursos | Precisa de estado/transações de simulação | Conservação, exclusividade, unidade compatível e repetição de comando sem dupla baixa |
| Combate e julgamento didático | Não decorrem automaticamente do DB3K | Respeitar arbitragem/avaliação humana e decisões do SISCAN; não substituir por cópia de algoritmo CMO |

## 3. Lacunas prioritárias e critérios de aceite

**P0** significa requisito antes de usar a capacidade em um resultado numérico oficial. Não significa paralisar toda a programação. **P1** significa requisito de consistência/abrangência antes de ampliar o uso; **P2**, melhoria cuja necessidade deve ser demonstrada pelo uso/escala.

| ID | Prioridade | O que falta | Entrega e critério verificável |
|---|---|---|---|
| ED-01 | P0 | Dicionário semântico para os campos consumidos pelo motor | Definição da grandeza, entidade/condição, unidade nativa/canônica, domínio, sinal, significado de zero/NULL/sentinelas e evidência aplicável à versão. Nenhum campo obrigatório do recorte sem definição |
| ED-02 | P0 | Conversão e validação de unidades | Regra explícita, dimensão e fator/offset quando aplicáveis; valor bruto preservado. Recusar kg versus litros sem densidade válida, energia versus massa, ou tipo de tonelada não confirmado |
| ED-03 | P0 | Catálogo técnico validado, separado da evidência bruta | Registrar valor utilizável, escopo, versão, evidências, revisão e aprovação do responsável conforme 53. Sem promoção em lote só porque o valor existe ou um teste passou |
| ED-04 | P0 | Identidade e configuração de unidade no cenário | Separar modelo, configuração e unidade individual, com IDs internos estáveis e snapshot técnico/configuração. Uma atualização de fonte não muda cenário ou execução já existentes |
| ED-05 | P0 para consumo | Semântica da taxa e do abastecimento | Comprovar unidade temporal, fluxo por motor/conjunto, modo de propulsão, tanque/tipo compatível, condições e carga. Não multiplicar taxa por NumberOfEngines por suposição |
| ED-06 | P0 para consumo | Modelo de curvas e regras fora da cobertura | Especificar seleção/interpolação por regime/faixa, limites e aplicabilidade por categoria. Zero nuclear, bateria, AIP, arma e combustível líquido não recebem tratamento genérico. Pontos, fronteiras e casos fora da cobertura têm resposta testada |
| ED-07 | P0 para carga | Unidade de armamento, massa e capacidade simultânea | Resolver DefaultLoad/MaxLoad/Multiple por tipo; distinguir arma, rajada/conjunto, munição e lançador. Validar payload efetivamente utilizável, outras massas e limites de configuração/ponto quando disponíveis. Nenhuma aprovação apenas por soma de pesos |
| ED-08 | P0 | Estado mutável e transações de recursos | Persistir combustível atual, munição/estoque, configuração efetiva, disponibilidade e revisões. Uma transferência confirma origem/destino de forma atômica; um comando repetido não baixa duas vezes; saldo não fica negativo |
| ED-09 | P0 | Manifesto consistente das bases e do motor | Vincular versão/hash da origem, compilação, bases derivadas, regras de associação/unidades e algoritmo. Conferir conjunto compatível ao iniciar execução; recusar mistura de builds ou snapshot incompleto |
| ED-10 | P0 | Casos de referência e calibração do recorte | Casos sintéticos com valores esperados, conservação/unidades, limites e repetibilidade; dados externos validados quando necessários. Tolerâncias declaradas antes do teste e justificadas pelo modelo. Testar lógica e depois precisão física, separadamente |
| ED-11 | P1 | Tratamento persistente de anomalias e dados faltantes | Cada pendência tem entidade/campo, evidência, impacto, decisão e versão de correção/isenção. Não alterar fonte para esconder erro. Toda ausência que afete o recorte deve ser resolvida ou impedir a função explicitamente |
| ED-12 | P0 ao ativar sensores/geografia | Contrato espacial e temporal | Definir CRS, distância, altitude ASL/AGL/profundidade, horário UTC e tempo de simulação; validar domínio terra/água e condições pertinentes. Geografia sintética inicial continua identificada |
| ED-13 | P1 antes de ampliar usuários | Migrações, concorrência e recuperação | Migrações numeradas, teste em cópia, backup consistente e restauração comprovada; teste dos 16 alunos mais equipe docente previstos em APR-05. Medir contenção/tempo antes de escolher mudança de SGBD |
| ED-14 | P1 | Integração do histórico e permissões com simulação | Associar evento a partido/exercício, estado anterior/posterior e versão do modelo; preservar autor e permissões. Histórico didático atual não substitui log técnico de execução |
| ED-15 | P1 para logística organizacional | Correspondência com MPNL | Necessidade nasce no menor escalão considerado e é consolidada preservando origem/recursos compartilhados; uma disponibilidade não é contada por aluno. Preservar quatro níveis e decisões de 08, sem introduzir subunidade no Exército |
| ED-16 | P2 | Otimização e ampliação dos dados | Índices/consultas/caches orientados por medição e invalidação por versão; normalizar outras famílias segundo os cálculos que realmente as utilizam. Não exigir dezenas de novas tabelas ou outro SGBD sem necessidade demonstrada |

## 4. Achados concretos no estado atual

**A barreira de promoção precisa de uma camada própria.** `catalog_technical_values` possui CHECK que exige unit=NULL e estado pendente. Isso é adequado para evidência bruta. Não se deve remover esse controle para colocar dados em produção; a proposta é criar um registro validado referenciando a evidência, com unidade, escopo/condição e aprovação. Os nomes e o esquema físico dessa nova camada ainda são proposta técnica.

**Meios do exercício ainda não são snapshots técnicos completos.** `assets` contém identificação, categoria, fiche textual e source_label. Não há ali uma relação técnica versionada completa com modelo/configuração/componentes/atributos de execução. `scenario_versions` já preserva versões de informações do exercício, mas não demonstra um snapshot imutável do catálogo e das condições de cada meio. É necessário complementar, preservando os oito meios sintéticos existentes.

**A conferência cruzada de builds é parcial.** O leitor de recursos verifica origem, versão do contrato e estado completo. A base guarda o hash da compilação, mas o leitor não o compara com o hash da compilação efetivamente carregada em cada consulta. Recomenda-se validar o manifesto do conjunto no início da execução/ativação de versão, sem recalcular arquivos grandes a cada leitura. O manifesto também precisa identificar o código das regras e conversões, não apenas o arquivo DB3K.

**O banco didático não é ainda um estado de simulação.** A estrutura atual contém usuários, exercício, submissões, alocações, eventos e notificações. Não constitui por si só um ledger de combustível/munição ou estado de movimento. As novas operações precisam de regras de conservação, revisão de estado, ordenação de eventos e política de repetição/rejeição. FKs garantem existência, não compatibilidade de partido, configuração, recurso ou unidade; essas invariantes exigem regras/testes próprios. [Referência SQLite](https://www.sqlite.org/foreignkeys.html).

**A demonstração de integridade não certifica o domínio físico.** Os 199 valores sem destino do grafo precisam de triagem por impacto, sem forçar um destino. A ausência de regimes em Static/567 pode ser não aplicabilidade, não erro a preencher. Zero, NULL e “não aplicável” precisam de estados distintos. Amostra visual ou nome semelhante não substitui especificação da coluna/versão.

## 5. Pendências quantitativas já localizadas

- 77.349 atributos importados continuam pendentes de unidade/semântica; isso não significa que faltem os outros valores na compilação.
- Os 199 valores sem destino incluem 191 ocorrências orbitais Plane=0 e oito anteriores, conforme 65. Não é necessário bloquear consumo por uma pendência orbital que o recorte não usa.
- 29.881 ocorrências de massa ausente/zero nas linhas de loadout. Não equivalem a 29.881 armas distintas; um cadastro pode ser reutilizado.
- 19.462 loadouts têm massa nominal padrão incompleta. Os 11.796 com soma definida incluem configurações vazias, sem equivaler a 11.796 configurações operacionais aprovadas.
- Nos vínculos aeronave–loadout: 643 excessos nominais e 13.578 casos classificados como payload desconhecido/zero. Classificação e coexistência de lacunas estão em 68. Excesso nominal não é prova isolada de defeito físico.
- WeaponRecord/9428 mantém DefaultLoad=400 versus MaxLoad=100; /9750 mantém Multiple=0. Corrigir exige evidência/decisão versionada, não inversão automática dos números.
- Consumo ainda exige comprovar escala, combustível e base por motor/conjunto; massa exige validar a unidade de contabilização. Esses são bloqueios do cálculo correspondente, mesmo com todos os vínculos encontrados.

## 6. Organização proposta dos dados para o motor

Manter cinco responsabilidades lógicas, sem impor cinco bancos físicos:

1. **Fonte preservada:** DB3K, arquivos de origem, metadados e hashes; nunca corrigir o original em lugar.
2. **Integração técnica:** registros compilados, relações, bases específicas e evidências, com pendências explicitadas.
3. **Catálogo validado:** modelos/configurações, medições canônicas, regras de compatibilidade, revisões e aprovação no escopo da função.
4. **Cenário e execução:** unidades individuais, partido, configuração/atributos congelados por versão e estado mutável controlado por transações.
5. **Resultados e história:** eventos, cálculos, justificativas, evidências, versões e avaliação humana, com acesso conforme decisões do projeto.

Entidades conceituais necessárias: versão de fonte; identidade técnica e mapeamento externo; versão de configuração; medição/evidência/decisão de validação; snapshot técnico da unidade; execução e seu manifesto; estado do meio/recurso; movimentação de estoque; evento de simulação; resultado com entradas e versão da regra. São responsabilidades a detalhar por entrega, não uma arquitetura definitiva aprovada neste parecer.

O contrato de cada cálculo deve declarar entradas obrigatórias, unidades canônicas, validade/condições, saídas, incerteza, modelo/versão e motivo de recusa. Dado sem aprovação não deve se tornar oficial por uma flag alterada na interface. Graus de confiança seguem APR-19 — Confirmado, Provável, Possível — separados de status de validação e aprovação; não atribuir pontuações arbitrárias ou confiança por nome de campo.

## 7. Sequência recomendada de desenvolvimento

| Ordem | Entrega pequena e verificável | Saída esperada |
|---|---|---|
| 1 | Contrato mínimo de entrada validada e manifesto | O backend aceita um conjunto sintético correto e recusa unidade/versão incompatível ou campo obrigatório ausente |
| 2 | Uma unidade individual, configuração e snapshot por partido | A unidade preserva identidade, o snapshot não muda com atualização do catálogo e dois alunos do mesmo partido não duplicam o recurso |
| 3 | Relógio/estado/eventos e recursos transacionais | Avanço simples reproduzível, histórico preservado, saldo consistente e comando repetido sem duplicidade |
| 4 | Um recorte de consumo/autonomia com dados sintéticos conhecidos | Resultados calculados e testados, incluindo limite de combustível, sem depender de unidades Command ainda pendentes |
| 5 | Validação técnica de uma configuração real de referência | Fonte, unidades, base da taxa, massa/carga e condições comprovadas; aprovação do responsável para seu escopo |
| 6 | Execução do mesmo fluxo com o recorte aprovado | Resultado rastreável ao manifesto e comparação com referência; outros registros não são aprovados por extensão |
| 7 | Ampliação por categoria/capacidade | Cada novo domínio adiciona seus contratos/casos, preservando diferenças aéreas, navais, submarinas e terrestres |

Pode haver trabalho de dados e programação no mesmo ciclo; não é necessário paralisar a aplicação enquanto se investiga um campo. A equipe/automação deve fazer os cruzamentos em lote, separar exceções e trazer ao responsável decisões concretas. Não transferir ao usuário conferência manual item por item de todo o catálogo.

Não começar por um motor universal de consumo, detecção e combate ao mesmo tempo. O primeiro recorte acima é uma recomendação técnica, não uma afirmação de que essas funcionalidades já existem. Não introduz defaults de reserva, combustível, precisão, sensores, marchas adicionais ou métodos MPNL ainda não definidos.

## 8. Definição de pronto para usar uma capacidade no motor

Para o recorte publicado, exigir:

- Todos os campos obrigatórios definidos e validados, com unidade/condição e origem; exceção não resolvida impede a função afetada.
- Relações necessárias sem ambiguidade; alternativas e componentes compartilhados não duplicam massa, estoque ou consumo.
- Conjunto de versões compatível, snapshot técnico reproduzível e aprovação rastreada conforme autoridade de 53.
- Modelo documentado, limites de aplicação e tolerâncias justificadas; dados fora da cobertura geram resposta explícita.
- Testes de unidade, conservação, limites, repetibilidade, autorização e concorrência pertinentes; rejeições deixam o estado anterior consistente.
- Resultado identifica cenário, conjunto de dados, algoritmo, entradas, condições e limitações. Se houver aleatoriedade, registrar sua parametrização/semente conforme modelo definido.
- Backup e restauração do estado operacional demonstrados antes do uso persistente com usuários; definir objetivos de recuperação, retenção e acesso. A [API de backup do SQLite](https://www.sqlite.org/backup.html) é referência para cópias consistentes de banco em uso, sem confundir cópia simples de arquivo ativo com recuperação testada.

Não é exigido resolver todos os campos de todas as 167 tabelas antes do primeiro recorte. É exigido não ocultar uma dependência do cálculo escolhido. SQLite não foi demonstrado como impedimento atual; não há nesta avaliação evidência para exigir migração imediata de SGBD ou alegar atendimento de desempenho em produção.

## 9. Preservação de decisões e limites deste trabalho

Permanecem: meios disponibilizados por partido Azul/Vermelho, acesso compartilhado dos alunos desse partido, backend como autoridade, isolamento do adversário por padrão, aprovação de dados pelo responsável, identidade/snapshots APR-10, histórico de alterações em execução APR-11 e arbitragem/avaliação humana APR-05. Preservar MPNL-001, inventário/manutenção/disponibilidade/ciclo de vida e a separação entre necessidade logística, importância organizacional e valor de combate.

Este trabalho atualiza documentos. Não modifica código, schema, bancos, atributos, permissões ou o servidor. Não executa novos testes de software ou de carga; referencia os testes concluídos na entrega 68 e realiza consultas estruturais/de contagem somente leitura. Não reabre APRs aprovadas nem declara aprovação de um novo modelo físico.

Evidências principais: `app.py` (schema, assets, alocações e inicialização), `tools/register_source_references.py`, `tools/import_technical_values.py`, `source_catalog.py`, `technical_units.py`, `resource_store.py`, `armament_payload.py`, documentos 49/51/53/65–68 e relatórios locais abaixo. Não foram encontrados arquivos de motor/migrações entre os caminhos pesquisados; isso é limite da inspeção do protótipo, não prova de ausência em todo arquivo histórico do projeto.

| Relatório consultado | SHA-256 |
|---|---|
| db3k-full-value-audit-07.json | `8264c556c826a3d3ce525744529b64b15121586e12ac6a3ed347c75b612f27f7` |
| db3k-resources-audit-09.json | `7a7634beb36130c72146d4984ee0645e596f0725898541d336feea3d6c1e3876` |
| db3k-armament-payload-audit-10.json | `5515f2acac03176b02c5404ebb1f62561e9414a2ed7892ce627ceb84cd8c38f3` |
