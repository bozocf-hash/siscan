# 127 — Comprovação de unidades, escalas e condições de combustível

**2026-11-18 · Investigação e implementação em andamento.** Autorização expressa para aprofundar a comprovação após 126. Manter originais, resultados anteriores e estado operacional. Não repetir a auditoria literal integral já concluída para tratar isso como nova comprovação física.

## Método e escopo

Separar: definição documental da grandeza/unidade; correspondência numérica entre fonte identificada e SQL; condição de configuração/regime/faixa/base da taxa; aprovação para uma finalidade; saldo atual da instância. Comparar valores originais sem substituí-los por números mais recentes encontrados na internet. Converter somente unidades explicitamente identificadas, com fator de referência e sem conversão massa↔volume por densidade presumida.

### Evidências de partida novas

- [Planilha de propulsão publicada pelo Command](https://www.warfaresims.com/WarSimsWP/wp-content/uploads/2014/07/F-22-Engine-Stats.jpg), vinculada ao [Mega-FAQ oficial](https://command.matrixgames.com/?page_id=2920): IDs de propulsor, número de motores e colunas de altitude em ft/m, velocidade em kt e consumo em kg/min. Imagem examinada visualmente; versão histórica, sem extrapolação automática para todo o DB3K_498.
- Registro SQL `DataPropulsion/734 — 2x F119-PW-100`: identidade e parâmetros de motor coincidem com a linha da imagem. `DataPropulsionPerformance`, rowid 3701, faixa 1/regime 3, coincide em velocidade 650, limites 0/3657,6 e consumo 267,47. Investigar a extensão exata dessa correspondência, sem promover todos os regimes/propulsores.
- Pontos de faixas superiores têm correspondências e diferenças que devem aparecer separadamente. Não corrigir limites SQL ou arredondar números para fabricar igualdade.
- [Rafale — fabricante](https://www.dassault-aviation.com/en/defense/rafale/specifications-and-performance-data/) documenta capacidade interna em massa e distingue combustível externo. Comparação com o Rafale M histórico no SQL exige registrar variante/configuração/época; proximidade numérica não homologa o campo inteiro.
- [F-15E — USAF](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/viewType/Print/viewClass/f-15e-strike-eagle/) qualifica a capacidade publicada como incluindo tanques conformais e externos. Não comparar esse total diretamente à linha de combustível interno do catálogo.
- [API Fuel](https://commandlua.github.io/assets/DataTypes.html#Fuel): tipos separados, capacidade máxima e quantidade atual distintos. A lista documental pode não cobrir extensões do banco; não corrigir um código SQL por ausência na página.

### Acesso visual e manual

Tentativas de abrir o Command: timeout; lançador: erro Windows de acesso negado. Não houve comparação nova no aplicativo até esse momento. Foi solicitada ajuda para manter Windows desbloqueado/Command aberto; a investigação independente continua. Manual instalado, página PDF 80, texto lido e página renderizada/inspecionada: consumo depende de velocidade, altitude e regime. Sem leitura integral ou OCR novo. A skill PDF foi aplicada nesta leitura; a skill Computer Use foi usada na tentativa de acesso.

## Próximas verificações desta execução

- [ ] Registrar e comparar a amostra documental de propulsão com o SQL por ID/faixa/regime/campo e hash.
- [ ] Classificar todos os tipos de combustível e de propulsão com evidência, cobertura e pendências específicas de unidade/base.
- [ ] Verificar condições de cálculo: capacidade vs saldo, reservatório/tipo, escala, conjunto vs motor, configuração, regime/faixa, consumo zero e limites.
- [ ] Testar funções de comprovação/recusa, executar diagnósticos reais, registrar resultados e sincronizar a entrega.

Hipóteses sintéticas de teste podem comprovar o comportamento do software, não a unidade física de um registro real. Não liberar o catálogo inteiro ou o motor com base em uma amostra.
