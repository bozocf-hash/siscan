# Spec: operational-state — estado e adjudicação durável

**2026-11-17. Fase 1 proposta para revisão; não implementada.** Prosseguimento solicitado por “pode seguir” após [108](docs/recovery/108_ENTREGA_PAR_CPC_NO_MAPA.md). A ordem já aprovada em [104](docs/recovery/104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md) é preservada: conferência do par → estado/adjudicação durável → julgamento didático e confirmação no mapa → produtor automático posterior. Não reabrir gates da conferência entregue.

## Objetivo e premissas

Registrar de forma durável o estado individual dos meios e a trilha de propostas, decisões e efeitos confirmados pelo instrutor. Sucesso: após fechar/reabrir a conexão ou reiniciar o serviço, o estado e sua origem continuam consultáveis; rejeição não produz efeitos e confirmação repetida não reaplica alterações.

Premissas propostas: usar o SQLite SISCAN e a biblioteca padrão existentes, com migração aditiva própria; manter IDs de unidade, exercício, partido e configuração; nenhuma alteração no DB3K ou nos snapshots técnicos. Este recorte entrega o provedor interno e seu armazenamento, sem novos botões/rotas ou ligação automática da tela. A proposta de efeitos é declarativa e didática; não contém cálculo militar.

Fontes: [35 DEC-018/019](docs/recovery/35_REGISTRO_MESTRE_DECISOES_SISCAN.md), [49](docs/recovery/49_REGISTRO_DECISOES_APR_01_A_APR_20.md), [80](docs/recovery/80_CONFRONTO_FORCAS_E_ESTADO_OPERATIVO.md), [81](docs/recovery/81_INDICADORES_COMPACTOS_E_RESTRICOES_RECURSOS.md), [104](docs/recovery/104_ESCOPO_LIGACAO_MAPA_ENSAIO_E_ADJUDICACAO.md), [108](docs/recovery/108_ENTREGA_PAR_CPC_NO_MAPA.md) e [mapa de capacidades](CAPABILITY_MAP.md). O plano técnico deverá conferir os contratos físicos do backend antes de propor sua migração.

## Fronteira e dependências

`operational-state` recebe contexto autenticado, identidades/referências verificadas e efeitos explícitos. Reutiliza contexto/transação e convenções de comando do `execution-core`; não importa `force-confrontation`, seu algoritmo ou atributos privados do registro de grupos. O consumidor futuro CPC produz uma proposta pelo contrato deste provedor e reconfere fontes antes de pedir aplicação.

O protótipo atual tem snapshots técnicos imutáveis em `engine_unit_snapshots` e combustível de ensaio por `run_id` em `engine_resource_states`. Nenhum deles é índice operativo oficial. Sua existência não inicializa o novo estado em 100%, não autoriza promover saldo de ensaio a saldo oficial e não atribui superfície a todo meio naval. O provedor de identidades atual continua limitado às instâncias demonstradas, sem expansão implícita do catálogo.

## Estado por unidade

| Informação | Regra |
|---|---|
| Identidade | Exercício, `unit_id`, partido, referência de configuração/snapshot e domínio comprovado; não usar código/nome como chave |
| Revisão | Revisão própria de estado, distinta de posição, composição, snapshot e execução |
| Índice operativo de origem | Número finito no intervalo 0–100, ou ausência explícita; informado pelo instrutor, sem dano percentual deduzido de uma base desconhecida |
| Condição de superfície | Somente com domínio de superfície demonstrado e índice conhecido: >60 combater; 40–60 inclusive navegar; <40 flutuar |
| Perda confirmada | Declaração separada, com autoria/motivo; 0% ou “flutuar” não significa automaticamente afundado/destruído |
| Origem e histórico | Autor, instante do servidor, decisão/efeito de origem e antes/depois; estado não avaliado permanece identificável |
| Recursos e condição efetiva | Não são sobrescritos por índice/avaria. Nesta fatia, restrições por recursos não integradas são explicitamente não avaliadas |

Sem registro, consulta devolve “não avaliado”, sem INSERT implícito por leitura. Não tratar `null` como 0%, prontidão total ou ausência de avarias. Não transferir navegar/flutuar a aeronaves, submarinos ou terrestres. Sem classificações aprovadas para esses domínios, conservar índice/declaração e informar classificação não definida. Não calcular índice da força por média.

Efeito desta primeira fatia é atribuição explícita de índice de origem e/ou declaração de perda, com campos conhecidos e validados, não um incremento de dano presumido. Ausência de campo significa preservar valor; `null` explícito para índice significa retirar a avaliação com justificativa rastreável. Correção posterior é nova decisão que referencia a anterior, nunca UPDATE do histórico. Declarar recuperação de perda exige correção explícita, sem inferir recuperação por um índice maior.

## Proposta, decisão e aplicação

1. **Registrar proposta:** instrutor participante de exercício aberto informa efeitos, justificativa não vazia e referências antes da mudança para unidades autorizadas. Congelar o conteúdo e suas referências com hash canônico, autor e horário do servidor. Não consumir, mover, alterar estado oficial ou relógio.
2. **Revisar:** ajuste cria nova revisão imutável da proposta; confirmação/rejeição aponta uma revisão/hash específicos. Uma revisão antiga não pode ser confirmada após ajuste. Não editar silenciosamente uma proposta já decidida.
3. **Rejeitar:** gravar decisão e autoria, sem publicação de efeitos. Uma proposta rejeitada não é reaberta; nova proposta pode referenciá-la.
4. **Confirmar e aplicar:** verificar autorização atual, exercício aberto/cenário, identidades, adjudicação e revisões de todos os meios. A decisão confirmada, efeitos antes/depois, revisão de estado e recibo são publicados numa única transação. Não deixar estado “confirmado” sem aplicação correspondente.
5. **Repetir ou conflitar:** mesmo identificador de comando e mesmo conteúdo retorna recibo histórico, após autorização atual; identificador reutilizado com outro conteúdo ou revisão desatualizada recusa sem escrita parcial. Duas confirmações concorrentes não podem aplicar a mesma proposta duas vezes.

Fonte didática e eventual execução automática futura devem ser identificadas distintamente. Só a primeira é aceita nesta fatia. Nenhum produtor automático poderá confirmar seus próprios resultados. Não aceitar papel, autor, horário ou revisão atual declarados pelo cliente como prova de autoridade. Proposta/decisão/efeitos são entidades distintas, mesmo quando persistidas na mesma transação.

## Durabilidade e integridade

Armazenar propostas/revisões, decisões, efeitos e recibos no banco SISCAN, com referências imutáveis, restrições de unicidade e integridade. A representação física e a migração serão detalhadas no plano aprovado; não criar um segundo banco ou serviço nesta especificação. Estados correntes são projeções verificáveis do histórico de efeitos confirmados.

Congelar referências suficientes à composição/dossiê para interpretar a decisão sem depender de grupos temporários ainda existirem após reinício. O histórico não referencia somente um ID volátil. A captura congelada não é reserva: futuras confirmações precisam de identidade/disponibilidade/revisão atuais. Revalidar a composição operacional antes de confirmar será obrigação da integração CPC, sem contornar mudanças de composição pela cópia histórica.

Migração aditiva, versionada e transacional, verificável em cópia isolada; falha não deixa schema parcialmente atualizado. Inicialização do provedor não apaga histórico nem altera originais. Verificar integridade na abertura/leitura; inconsistência deve ser recusada e reportada, sem fabricar novo estado ou reconstruir silenciosamente por defaults. Backup/restauração inclui todos esses registros e suas restrições. Banco principal só será migrado no procedimento de entrega aprovado; nesta fase nenhum banco será aberto para escrita.

## Autorização e visibilidade

Instrutor participante consulta propostas/histórico e confirma/rejeita no exercício autorizado. Operador consulta somente estado confirmado das unidades do próprio partido; não recebe proposta, justificativa privada, composição ou snapshots adversários para ocultação no frontend. Recibos não contornam revogação de acesso. Unidades de outro exercício, referências duplicadas, não adjudicadas ou sem identidade verificável recusam o lote.

Leituras não alteram dados. Proposta/revisão/rejeição não alteram estado dos meios; confirmação não altera posições, combustível, munição, tempo, configuração ou aprovação técnica. Um exercício encerrado preserva consulta autorizada e recusa novas mudanças.

## Regras preservadas e exclusões

Mínimo de combustível continua configurado pelo operador/instrutor e margem de pré-alerta fixa em 5 pontos; nenhuma conversão de kg para percentual sem capacidade/unidade comprovadas. Não criar mínimo padrão de 30%. Agregação de armamento e seu limiar continuam pendentes, sem somar munições heterogêneas ou assumir 30% universal.

Esgotamento real de combustível permanece no motor de recursos: superfície/terrestre imobilizam; perda aérea em voo exige o caminho de registro/adjudicação definido para o exercício. Este provedor não inventa o evento nem altera a avaliação de origem ao ler uma restrição. Sem integração de recursos, não anunciar que o novo índice já bloqueia movimento/combate/sensores.

Fora da fatia: persistir grupos, criar novas identidades reais, migrar o DB3K, calcular confronto/detecção/consumo, expandir parâmetros Command, implementar barras/hover, ligar julgamento ao mapa, replay, novas APIs HTTP e regras físicas de avaria. As próximas integrações consumirão este provedor, sem duplicar publicação de efeitos.

## Estrutura e estilo previstos

Código em `siscan-prototype/operational_state.py`; verificadores `check_operational_state.py` e `check_operational_state_storage.py`; documentos em `docs/recovery/`. Plano/lista futuros em `tasks/operational-state/`, preservando os planos antigos. Nomes são proposta de localização, não arquivos de código já existentes.

Python 3.11+, `sqlite3`, biblioteca padrão e estilo do backend existente: funções pequenas, payloads estritos, exceções de permissão/validação/conflito e JSON canônico. Exemplo de forma, sem implementação:

```python
# A sessão vem do servidor; proposta é somente dados, nunca autorização.
result = operational_state.consultar(db, user, unit_id)
```

## Verificação e comandos previstos

Na pasta `prototype` de entrega (`siscan-prototype` no repositório):

```powershell
$pythonState = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonState check_operational_state.py
& $pythonState check_operational_state_storage.py
& $pythonState check_cpc_map.py
& $pythonState check_cpc_group_preparation.py
& $pythonState check_map_units.py
```

Na raiz: `git diff --check`. Os dois primeiros verificadores ainda não existem. Não houve execução de testes nesta fase documental. Não usar descoberta vazia como prova. Testes futuros devem usar bancos/usuários descartáveis e conexões/processos independentes, sem reiniciar a instância do usuário. Planejar migração em cópia, rollback por falha, reinício/recuperação, concorrência e idempotência; não basta consultar a mesma conexão em memória.

## Critérios de aceite

| ID | Evidência exigida antes de concluir a implementação |
|---|---|
| OS-01 | Sem estado retorna ausência; índice valida 0, 40, 60, 80, 100, imediatamente acima/abaixo de 40/60; rejeita booleano, NaN, infinito e fora da faixa |
| OS-02 | Classificação só em superfície demonstrada; perda é explícita e índice não gera destruição ou agregação |
| OS-03 | Operador/outro exercício/revogação não escreve nem recebe dados adversários; papel fornecido no payload não autoriza |
| OS-04 | Registrar/revisar/rejeitar preserva estado, recursos, relógio, posições e snapshots; revisão antiga não confirma |
| OS-05 | Confirmação aplica lote inteiro com antes/depois, autoria e motivo; falha provocada em qualquer integrante reverte tudo |
| OS-06 | Reenvio idêntico devolve recibo sem novo efeito; conteúdo diferente/conflito/concorrência recusa sem duplicação |
| OS-07 | Estado, proposta, decisão e histórico sobrevivem a conexão/processo novos e perda dos grupos temporários; corrupção não vira estado padrão |
| OS-08 | Migração isolada é repetível, preserva dados existentes e reverte falha; backup/restauração mantém relações e recibos |
| OS-09 | Correção gera novo registro e preserva origem; recurso não sobrescreve índice; leitura não grava nem presume prontidão |
| OS-10 | Regressões dos provedores e conferência CPC passam; principal/originais preservados e limitações comunicadas |

## Limites e gate

Sempre: autorização antes da leitura sensível, validação estrita, transação por comando, autoria, histórico e testes com dados isolados. Rever antes de ampliar: efeitos logísticos, índices agregados, APIs/UI, semântica de novos domínios e migração fora do procedimento aprovado. Nunca: publicar resultado pelo operador, copiar algoritmo proprietário, preencher desconhecidos por suposição, apagar histórico ou alterar fonte técnica para representar avaria.

Propostas específicas a revisar: índice absoluto em vez de dano relativo quando a origem é desconhecida; correção explícita e auditável de perdas; fase inicial sem publicação gráfica. Não há dúvida bloqueante para revisar o contrato, mas esses pontos ainda não são decisões aprovadas.

Fase 1 termina nesta especificação. Após aprovação, elaborar o plano técnico/migração em turno próprio e depois tarefas, conforme a skill solicitada. Aprovar este documento não declara implementação concluída nem autoriza executar migração no banco principal neste turno.
