# 120 — Retirada de meios com perda confirmada do mapa

## Regra e correção

O responsável observou que confirmar perda no julgamento mantinha o meio representado no cenário. Corrigida a apresentação no planejamento e na camada CPC: **somente `state.lost === true` do estado oficial retira o marcador ativo**, independentemente da categoria ou da representação Calunga/silhueta. Proposta pendente, prévia, índice zero, condição degradada e estado desconhecido não equivalem a perda confirmada.

O meio permanece cadastrado, com posição anterior, composição de origem, decisão e histórico. A listagem de adjudicados indica **PERDA CONFIRMADA**, desabilita a seleção de plotagem e o remove das referências de destino/seleção por área. Não se excluem registros, posições ou recursos. Este bloqueio é de apresentação/seleção na interface; não redefine contratos de elegibilidade de grupos ou comandos do motor.

Ao preparar um par, o CPC agora lê o estado atual dos integrantes pelas consultas autorizadas `/api/map-units?team=AZUL` e `...?team=VERMELHO`, antes de publicar os marcadores. Dossiê inicial não é transformado em estado corrente. A confirmação usa os estados posteriores presentes no recibo oficial imediatamente, antes da consulta de atualização: falha dessa leitura posterior não mantém um meio perdido no mapa. Projeção complementar indisponível continua sinalizada. Saída/troca durante a consulta descarta resposta atrasada. Consulta do tooltip não redesenha planejamento depois de mudança de partido, marcador ou entrada no CPC.

Retornar um meio ao mapa exige que seu estado oficial deixe de declarar perda por correção explícita do instrutor, respeitando a referência à decisão exigida pelo backend. Aumentar o índice não limpa perda. Posição preservada serve de referência quando houver restituição explicitamente confirmada.

## Evidências

Cinco regressões novas reproduziram as lacunas antes da correção: regra de visibilidade; consulta dos dois partidos; saída durante consulta; falha de consulta; perda confirmada com falha de atualização posterior. Ciclos red/green concluídos. **38 testes JS passaram**: julgamento 13, preparação 13, grupos 9, apresentação 3. Também passaram **10 testes Python de julgamento** e o verificador assertivo `check_map_units.py`. Total de 48 testes nomeados nesta entrega, além do verificador. Sintaxe dos módulos e diff conferidos; nenhuma dependência adicionada.

Navegador real, exercício inteiramente sintético em `http://localhost:61271/`, pasta `%TEMP%/siscan-loss-20261117-v1` e processo próprio: inicialmente dois marcadores; proposta de perda AZUL salva e ainda dois marcadores; confirmação final e somente VERMELHO. Planejamento AZUL com zero marcadores e linha desabilitada **PERDA CONFIRMADA**. Reload e nova preparação, antes mesmo de abrir julgamento: somente VERMELHO. Histórico confirmado continuou consultável com recibo e perda AZUL. Console final sem erros/avisos.

Base isolada: uma proposta, uma decisão, um efeito; duas posições originais em revisão 1, preservadas em (-22.7, -43.1) e (-22.7, -42.9). Zero comandos de plotagem, execuções e estados de recursos; `integrity_check=ok`, nenhuma violação FK. Não se alteraram as bases das prévias anteriores, o principal ou arquivos originais.

Evidência local fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-perda-confirmada-20261117.png`.

## Aplicação e limites

Os adaptadores atualizados são servidos nas prévias existentes após recarregar a página; não é necessário reiniciar o servidor para esta correção. Estados alterados em outra sessão são observados pelas consultas/atualizações existentes; não foi implementado push ou sincronismo entre clientes. Correção não implementa resolução automática, animação de afundamento, destroços ou alteração logística. O histórico não deve ser apagado para produzir desaparecimento visual.
