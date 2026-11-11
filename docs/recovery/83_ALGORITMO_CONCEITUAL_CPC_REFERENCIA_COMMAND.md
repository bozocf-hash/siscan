# 83 — Algoritmo conceitual do CPC: investigação do Command e proposta própria

**Data: 2026-11-11. Estado: proposta de algoritmo didático para discussão; não implementado ou validado.** Complementa [82](82_PESQUISA_E_PROPOSTA_CONCEITUAL_CPC.md), atendendo ao pedido de desenvolver a lógica de avaliação, além da pesquisa bibliográfica. Preserva decisões de [80](80_CONFRONTO_FORCAS_E_ESTADO_OPERATIVO.md) e [81](81_INDICADORES_COMPACTOS_E_RESTRICOES_RECURSOS.md).

## 1. O que foi possível encontrar

O manual oficial descreve uma simulação por pulsos, com frequências diferentes entre subsistemas e combinação de processos determinísticos e estocásticos. Também documenta gravação de estados para retomada de cenários. Essa descrição sustenta uma organização temporal, mas não publica todas as fórmulas internas. [Manual oficial, §7.6](https://command.matrixgames.com/manual/07-6-simulation-philosophy-and-engine-internals/).

As interfaces distinguem atuação automática e manual e oferecem políticas por unidade, grupo, missão e partido. Para o SISCAN, a distinção entre restrição técnica e autorização de atuação é uma adaptação conceitual útil. Não foram transcritos procedimentos de emprego ou critérios de seleção de armamentos. [Manual oficial, §5.3](https://command.matrixgames.com/manual/05-3-shortcut-buttons-and-windows/).

O catálogo distingue configurações de plataformas por versão e época. Portanto, vincular apenas um nome de classe a uma unidade não identifica necessariamente sua configuração. [Manual oficial, §9](https://command.matrixgames.com/manual/09-databases/).

**Não foi extraído um algoritmo executável do Command.** Na instalação local, a busca por arquivos `.cs`, `.csproj`, `.sln`, `.cpp`, `.vb` e `.fs` encontrou somente `Launcher/Localization/stringsEnglish.Designer.cs`, referente à localização do lançador. Isso não comprova ausência de fonte em qualquer outro lugar, mas não fornece código do motor. Não houve descompilação, execução de confronto ou alteração da instalação.

## 2. Evidência local e limites de leitura

| Evidência | Verificação desta complementação | Limite |
|---|---|---|
| `Manuals/CMO manual EBOOK.pdf` da instalação | 353 páginas; extração pontual de texto nas páginas PDF 258–260; SHA-256 `da3f75ec537b2a64e77c432324c02410dd2c12f6d999e4813b96ab7c04df51c1` | Sem OCR novo ou inspeção visual de figuras nesta complementação. Não constitui nova leitura integral |
| Manual HTML oficial | Seções 7.6, 5.3 e 9 consultadas em 2026-11-11 | Numeração/edição diferentes do manual local; não atribuir a seção HTML 7.6 às páginas locais 258–260 |
| `DB3K_498.db3` original | Abertura SQLite somente leitura; nomes de campos consultados em `DataWeapon`, `DataSensor`, `DataAircraft`, `DataShip`; SHA-256 `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d` | Consulta de esquema, não validação semântica de valores/unidades ou inventário novo de todos os campos |
| Fontes de programa locais | Busca pelas extensões descritas acima | Não houve auditoria binária ou inspeção de código-fonte de combate |

Exemplos de campos efetivamente encontrados: `Weight` em `DataWeapon`; `RangeMin`, `RangeMax` e `DirectionFindingAccuracy` em `DataSensor`; `WeightPayload`, `DamagePoints` e `FuelOffloadRate` em `DataAircraft`; `DamagePoints` em `DataShip`. São identificadores do esquema, não unidades confirmadas nem autorização para cálculo. Não converter `DamagePoints` automaticamente na barra de 0–100% ou em condição de afundamento.

O banco pode conter parâmetros de modelos além dos campos amostrados. A consulta não sustenta dizer que todos estão ausentes ou que bastaria uma associação SQL para reproduzir a simulação. Os relacionamentos já compilados continuam úteis como origem dos dados; comportamento temporal e critérios de apuração precisam de regras próprias.

## 3. Algoritmo proposto: executar um ensaio e adjudicar seus efeitos

**Esta seção é desenho próprio do SISCAN**, não reprodução do código do Command. Escopo: simulação didática abstrata, rastreável e configurada para um exercício. Não estabelece eficácia de armamentos reais ou lógica operacional de escolha de alvos.

Dividir a avaliação em quatro partes:

1. **Estado inicial:** composição, configurações, recursos, condições e informações disponíveis a cada partido, numa revisão imutável.
2. **Ensaio temporal:** processar eventos e regras didáticas aprovadas em uma cópia isolada; produzir trajetória e efeitos propostos.
3. **Adjudicação:** instrutor aceita, altera ou rejeita a proposta; pode produzir resultado didático direto.
4. **Aplicação:** validar novamente a revisão e gravar somente efeitos autorizados, preservando histórico e recursos.

Não substituir essas partes por uma divisão entre duas notas globais de forças. A comparação deve mostrar o que mudou, por qual evento e sob qual regra. Um resumo por força pode reunir quantidades/estados por categoria; uma nota universal ou probabilidade de vitória não é consequência automática disso.

### Entradas mínimas

| Entrada | Finalidade |
|---|---|
| ID e revisão do exercício; unidades/configurações/snapshots | Evitar calcular com uma composição e aplicar em outra |
| Estado de origem do instrutor e restrições vigentes | Preservar diferença entre avaria e limitação por recursos |
| Estoques por item, combustível e bases percentuais validadas | Impedir criação, dupla contagem ou perda de unidades |
| Visão informacional separada de cada partido | Não fornecer ao agente automático a verdade completa do adversário |
| Objetivo e horizonte do ensaio | Definir o que se está avaliando e quando parar |
| ID/versão das regras didáticas e âmbito de uso aprovado | Identificar o fundamento de cada transição |
| Política de automação permitida; origem das decisões | Separar automação configurada pelo operador de autoridade do instrutor |
| Agenda temporal, regra de simultaneidade e semente, se houver sorteio | Permitir reprodução e comparação de alternativas |

Esses são contratos candidatos, ainda sem novos endpoints ou tabelas. Dados essenciais ausentes produzem diagnóstico de inaplicabilidade; não ativam valores padrão ocultos.

### Pseudocódigo de orquestração

```text
ensaiar(pedido, revisao, regras):
    verificar_acesso_e_escopo(pedido)
    inicial = obter_snapshot_imutavel(revisao)
    exigir_entradas_e_uso_aprovado(inicial, regras)
    estado = copiar_para_ensaio(inicial)
    agenda = ordenar_eventos(pedido, regras)

    enquanto houver_eventos_antes_do_fim(agenda):
        instante, lote = retirar_proximo_lote(agenda)
        atualizar_recursos_no_intervalo(estado, instante, regras)
        anterior = congelar(estado)
        visoes = construir_visoes_autorizadas(estado)
        intencoes = avaliar_regras_didaticas(visoes, lote, regras)
        validas = validar_lote_capacidade_politica_e_recursos(intencoes, estado)
        efeitos = apurar_eventos_abstratos(validas, anterior, regras)
        estado = aplicar_lote_no_ensaio(estado, efeitos)
        registrar_causas_versoes_e_deltas(instante, validas, efeitos)
        atualizar_agenda_sem_reprocessar_eventos(agenda, efeitos)

    retornar proposta(inicial, estado, historico, limites_do_modelo)

confirmar(proposta, decisao_do_instrutor, chave_idempotente):
    verificar_identidade_e_autoridade_do_instrutor()
    validar_efeitos_aceitos_e_retificacoes(decisao_do_instrutor)
    em_transacao:
        exigir_revisao_original_ou_solicitar_novo_ensaio()
        retornar_recibo_se_chave_ja_processada()
        aplicar_somente_deltas_autorizados()
        registrar_decisao_historico_e_nova_revisao()
```

O pseudocódigo define orquestração e consistência. **`apurar_eventos_abstratos` continua dependendo de uma rubrica didática explícita; não representa uma fórmula de combate já descoberta.** Sua primeira versão pode ser uma tabela de transições do exercício, aprovada pelo instrutor, com condições fictícias e efeitos abstratos. Não preencher esse ponto com probabilidades inventadas para sistemas reais.

### Relógio e simultaneidade

Recomendação própria: começar com uma agenda de eventos com ordenação reproduzível e limites de execução, reutilizando os contratos do relógio existente. Não copiar a duração de pulso do Command como requisito do SISCAN. Combustível é integrado uma vez para cada intervalo; eventos no mesmo instante não podem debitar novamente esse intervalo.

Para efeitos declarados simultâneos, avaliar todas as propostas contra o mesmo estado de referência e resolver os deltas num único lote. Conflitos de recursos compartilhados precisam de regra didática explícita. Ordenar por ID dá repetibilidade de armazenamento, mas não deve dar prioridade substantiva permanente ao Azul ou à primeira unidade. Não adotar concorrência de threads como fonte de incerteza.

Se faltar regra para um conflito, interromper o ensaio com diagnóstico. Limites de tempo/eventos e ausência de progresso impedem ciclos infinitos. O motivo de término integra o relatório.

## 4. Estados, recursos e perdas

| Registro | Interpretação proposta |
|---|---|
| Intenção | Ação candidata; ainda não representa consumo |
| Reserva, se necessária | Compromisso temporário no ensaio; distinto do débito |
| Utilização proposta | Débito no estado isolado; ainda não altera estoque oficial |
| Utilização confirmada | Débito oficial exatamente uma vez, com identidade própria |
| Efeito proposto | Alteração abstrata de estado, com regra e causa |
| Resultado adjudicado | Efeito aceito/alterado pelo instrutor e aplicado na revisão correspondente |

Conservação por item: `saldo_final = saldo_inicial + entradas_confirmadas - utilizações_confirmadas`, com saldo não negativo e unidade de contabilização constante. Combustível utiliza o perfil validado e o intervalo correspondente; não inferir consumo a partir do percentual de avaria.

Neste primeiro desenho, nenhum consumo do ensaio é oficial antes de adjudicação. Se o instrutor aceitar utilização e rejeitar dano, o débito permanece porque são efeitos separados. Se uma utilização já foi confirmada em outro fluxo, a proposta referencia seu ID e não a debita novamente. Uma retificação posterior do dano também não devolve recurso automaticamente.

Perda de aeronave ou afundamento seriam eventos distintos, identificados e confirmados, sem presumir que qualquer índice abaixo de um limiar os produz. As faixas atuais de superfície são somente: >60 combater; 40–60 navegar; <40 flutuar. Não aplicar a aeronaves ou submarinos por analogia.

Derivar indicadores após os efeitos: condição de origem preservada; restrição de armamento não melhora avaria; combustível em relação ao mínimo M do operador, com margem fixa de 5 pontos conforme 81. Agregação de munição e seu limiar exato continuam pendentes. Não converter o exemplo de 30% em requisito fixo.

## 5. Exemplo de funcionamento, sem parâmetros de sistemas reais

Unidade fictícia U tem estoque de referência conhecido. Uma regra de exercício propõe utilizar dois itens; o ensaio mostra o saldo reduzido e registra a causa. Outra regra propõe alteração de condição de uma unidade V. O instrutor pode aceitar ambos, aceitar apenas a utilização ou substituir a alteração de V por uma consequência didática. A aplicação oficial reflete exclusivamente a decisão registrada.

Se alguém editar a composição ou consumir estoque depois do snapshot, a proposta fica desatualizada e não pode sobrescrever a revisão nova. Reexecutar a confirmação com a mesma chave retorna o recibo anterior. Essa sequência fecha a avaliação administrativa e didática sem fingir que dois itens correspondem a um dano físico universal.

## 6. Como chegar a um modelo utilizável

A separação de ambientes, inspirada na discussão de credibilidade de simulação de 82, deve ser concreta:

- **Desenvolvimento/verificação:** casos fictícios, entradas controladas, resultados esperados e reprodução do histórico. Demonstra que o software implementa as regras declaradas.
- **Avaliação do modelo:** confrontar o comportamento com evidência independente adequada ao objetivo de ensino; registrar sensibilidade, limitações e domínio de aplicabilidade. Não equivale a comparar apenas com outro jogo.
- **Exercício:** somente versões aprovadas para aquele uso, com confirmação oficial do instrutor e rastro de alterações.

Usar o Command como referência conceitual/interface ou comparador exploratório não o transforma em verdade física. Concordância entre dois programas não valida automaticamente nenhum deles. NASA não fornece os coeficientes de combate que faltam.

Critérios candidatos de aceitação do núcleo: proposta não altera exercício; replay reproduz eventos com mesmas versões; não há vazamento entre partidos; estoque não fica negativo; consumo não duplica; simultaneidade não favorece um partido por ID; revisão obsoleta é recusada; confirmação exige instrutor; alteração direta tem origem manual; faixas de 80/81 são preservadas; lacuna essencial impede aplicação automática.

## 7. Resultado e próximo recorte

Há material suficiente para desenhar o **núcleo de ensaio, adjudicação e aplicação de efeitos** e testá-lo com regras fictícias. Ainda não há fundamento recuperado para afirmar que temos um simulador físico validado para todas as interações entre meios reais.

Recomendação: especificar esse núcleo como primeiro recorte do CPC (`force-confrontation`), com rubrica didática transparente, antes de ampliar profundidade dos modelos. O núcleo atende modo automático de apuração e modo didático direto; a autoridade final permanece a mesma. As cinco famílias direcionais de 82 permanecem fronteiras possíveis, não cinco modelos prontos.

Este estudo não altera o ciclo de aprovação em andamento de `technical-catalog`, não aprova novas tarefas/DDL e não inicia implementação. A especificação própria deverá fechar representação das regras, simultaneidade, prazo do ensaio e critérios de encerramento. Nenhum código, banco, original, posição ou estado do exercício foi modificado nesta complementação.
