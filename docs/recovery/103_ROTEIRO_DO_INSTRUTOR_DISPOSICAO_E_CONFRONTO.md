# 103 — Roteiro do instrutor: disposição das forças e confronto

**Elaborado em 2026-11-16 e disponibilizado na pasta SISCAN em 2026-11-17.** Atende ao pedido de explicar como o confronto ocorrerá na tela. O mapa definido é o ATLANTICADOR integrado ao SISCAN. Esta tela de grupamentos organiza as forças; **a execução de confronto por grupamentos e a adjudicação de efeitos ainda não estão conectadas a ela**. Não existe um botão de combate funcionando nesta entrega.

## O que está disponível e o que ainda falta

| Etapa | Situação |
|---|---|
| Plotar/reposicionar meios adjudicados no mapa | Disponível, com regras existentes |
| Criar, consultar, selecionar, enquadrar e arquivar grupamentos elegíveis | Implementado e verificado na prévia isolada da entrega 102 |
| Preparar dossiê inicial AZUL/VERMELHO com snapshots | Biblioteca de backend entregue em 98; sem acionamento nesta tela |
| Executar ensaio temporal de dois grupamentos | Ainda não integrado; o ensaio CPC existente é de unidades individuais e parâmetros sintéticos |
| Reproduzir eventos do confronto no mapa | Concepção em 97; ainda não implementada |
| Julgamento didático, confirmação e aplicação oficial de efeitos nos meios | Requisitos definidos; integração própria ainda pendente |

Código instalado e processo ativo são coisas diferentes. A entrega gráfica pode ser conferida na prévia de teste; o servidor principal em 8787 não é reiniciado automaticamente. O roteiro pressupõe que a instância aberta esteja executando a versão com a aba de grupos.

## Parte A — Passos que o instrutor já pode seguir na prévia

1. **Entrar com perfil de instrutor.** Conferir exercício e perfil antes de abrir o mapa. Se o seletor de partido estiver bloqueado em AZUL ou VERMELHO, a sessão é de operador; ela não permite organizar ou consultar livremente o adversário.
2. **Abrir o mapa ATLANTICADOR existente.** Usar a aba “Meios” do painel para consultar os meios adjudicados ao partido. Plotar por clique/coordenadas ou reposicionar pelas ferramentas anteriores quando necessário. Criar um grupo não posiciona os seus integrantes automaticamente.
3. **Escolher o partido no seletor “Partido SISCAN”.** O instrutor pode alternar AZUL/VERMELHO. Cada troca atualiza lista/realce; não junta inventários dos dois partidos. A seleção de grupo não é o agrupamento de camadas do editor.
4. **Abrir a aba “Grupos” (nome acessível: “Grupamentos”).** Em “Nova composição”, informar designação, domínio e integrantes elegíveis; acionar “Criar grupamento”. Unidade sem instância/snapshot/domínio demonstrado aparece pendente ou indisponível. O catálogo técnico completo não representa automaticamente unidades prontas para agrupamento; a integração atual reconhece a configuração aérea sintética controlada.
5. **Conferir o grupo criado.** Selecioná-lo na lista para realçar os marcadores já plotados. “Enquadrar integrantes” altera apenas a câmera. A lista mostra nomes/códigos do cadastro, posição disponível e pendências; clicar num integrante abre a consulta no painel. “Sem posição” não significa perda ou ausência de meio.
6. **Repetir para o outro partido.** O instrutor pode conferir cada composição; esta tela ainda não seleciona os dois grupos como um par de confronto. Para liberar integrantes de um grupo, usar “Arquivar grupamento” e “Confirmar arquivamento” no painel. Cancelar não altera a composição. Para recompor nesta primeira versão, arquivar e criar outro grupo; não há edição gráfica dos membros.

**Aqui termina o fluxo implementado nesta tela.** Os grupos/histórico são temporários e se perdem ao reiniciar o servidor. Não é possível executar um confronto nesta aba, comparar o resultado ou aplicar perdas oficiais por seus controles atuais.

## Parte B — Fluxo previsto para realizar o confronto

Os passos abaixo descrevem a experiência desejada, fundamentada em 80/81/97. **São etapas futuras, não botões já existentes.** Não substituem a especificação de execução/visibilidade/adjudicação que ainda precisa ser desenvolvida.

1. **Selecionar a composição AZUL e a VERMELHA para um ensaio.** Fixar as revisões escolhidas e vincular os IDs dos integrantes aos estados/snapshots. O backend deve reconferir autorização, adjudicação e disponibilidade antes de executar; uma preparação antiga não reserva recursos.
2. **Conferir a situação inicial.** Instrutor revisa posições de início, configuração, estoques e origem/unidade dos dados. Definir explicitamente a relação entre posições geográficas do mapa e posições temporais do ensaio. Dados essenciais ausentes devem gerar pendência, sem substituir desconhecido por zero ou inventar coeficientes.
3. **Escolher a forma de adjudicação.** No modo assistido, o sistema executa apenas regras didáticas/modelos previamente definidos e apresenta uma proposta explicável. Na arbitragem didática direta, o instrutor registra os efeitos desejados para o exercício sem precisar aceitar ou executar um cálculo automático. Ambos precisam preservar justificativa e rastreabilidade.
4. **Acompanhar a apuração.** Quando a execução/reprodução estiver integrada, eventos registrados poderão ser consultados no mesmo mapa e numa linha do tempo: tempo, envolvidos e mudanças de estado/estoque. Animação só representa fatos existentes no registro; não inventa trajetórias ou dados de detecção. Voltar no replay não desfaz efeitos oficiais.
5. **Revisar a proposta e decidir.** Conferir estado inicial/final, combustível, munição, avarias/perdas propostas e pendências por meio. O instrutor poderá confirmar, ajustar ou rejeitar, registrando autoria e justificativa. **Resultado automático não vira resultado oficial por terminar o ensaio.**
6. **Aplicar e consultar o resultado oficial.** Somente após confirmação autorizada o backend publica efeitos rastreáveis, com controle de revisão e aplicação única. O mapa/ficha distinguem ensaio de estado oficial e preservam o histórico. O operador recebe somente o que sua visibilidade permitir.

```mermaid
flowchart LR
    A[Dispor e compor no mapa existente] --> B[Selecionar dois grupos e conferir dados]
    B --> C[Ensaio assistido ou arbitragem didática]
    C --> D[Proposta de resultado]
    D --> E[Instrutor confirma ou ajusta]
    E --> F[Estado oficial e histórico]
```

Só a preparação gráfica de A está entregue neste recorte. O dossiê de 98 é parte do backend de B; C–F não são execução disponível na interface atual.

## Como ler os indicadores quando forem integrados

Para superfície, preservar os limites confirmados: acima de 60% combater; de 40% a 60%, incluindo os limites, navegar; abaixo de 40% flutuar. O índice e as avarias confirmados pelo instrutor não são deduzidos de combustível ou munição.

Combustível: mínimo M definido pelo operador, sem padrão; pré-alerta fixo em M+5 pontos, vermelho em M ou menos. Percentual só com base/unidade validada. O indicador geral de armamento ainda exige método de agregação e definição do limiar: o exemplo de 30% não foi fixado como regra universal. Não somar tipos heterogêneos para fabricar o percentual.

Esgotamento: superfície/terrestre imobilizam; aeronave em voo tem perda proposta para adjudicação. Ficha de grupo não recebe média automática de poder ou estado dos integrantes. Estas regras orientam a integração futura; as três barras não foram implementadas pela aba de grupos.

## Próximo passo para o instrutor conseguir confrontar pela tela

Depois da composição gráfica, falta especificar e integrar a seleção do par AZUL/VERMELHO e a conferência inicial ao dossiê de 98. Em seguida, executar um recorte didático controlado e integrar proposta/decisão/efeitos, mantendo o mesmo mapa. Não apresentar a composição como se já entregasse todo esse fluxo.
