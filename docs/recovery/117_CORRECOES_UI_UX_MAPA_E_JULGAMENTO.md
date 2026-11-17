# 117 — Correções de UI/UX do mapa e julgamento

## Contrato de apresentação

Solicitação: preservar cores dos partidos no Calunga; reduzir símbolos e fichas; simplificar operação e julgamento. Referência: tokens e painéis do ATLANTICADOR preparado, sem alterar seus arquivos originais.

- Mapa como área principal; símbolos de 36 × 28 px e rótulo curto pelo código do catálogo. Nome completo acessível por foco, ponteiro e ficha.
- Fonte Segoe UI/system-ui, texto de painel de 12–13 px; paleta navy, texto claro, bordas discretas e ação principal dourada do ATLANTICADOR.
- Coordenadas, aparência, referências e detalhes técnicos sob expansão explícita. Nada de retirar validações, permissões ou informação de origem.
- Julgamento progressivo: preparar forças → definir efeitos → revisar proposta → confirmar aplicação → consultar resultado. Salvar proposta e aplicar efeitos continuam ações distintas.
- Em tela pequena: painel limitado a parte do mapa, rolagem interna e controles de toque acessíveis; sem transbordamento horizontal.
- Estados de erro, espera, resposta incerta e proposta desatualizada continuam explícitos; alterações locais não se perdem sem confirmação.

## Verificação

Implementação nos adaptadores SISCAN; nenhuma dependência adicionada. A geração Calunga já devolve `symbol_svg` e `hostile_symbol_svg`. A causa era o uso exclusivo do primeiro. Agora a afiliação seleciona o SVG original correto, compartilhado por planejamento e CPC; não há recoloração CSS do desenho militar.

Símbolos de 60 × 40 passaram a 36 × 28 px, com alvo de interação de 40 × 38 px. Rótulo pelo código, nome completo acessível e ficha compacta, sem preencher valores desconhecidos. Referências de configuração, coordenadas e aparência permanecem consultáveis por expansão.

Preparar forças → Definir efeitos → Revisar efeitos → Salvar proposta → Avançar para confirmação → Confirmar aplicação. Editar, cancelar aplicação, rejeitar, reenviar intenção incerta e consultar histórico preservam seus contratos. Campos de índice/perda aparecem ao marcar o meio. Revisar esconde a edição, mostra antes/depois e mantém retorno à edição. A confirmação é a única ação de aplicação. Resultado tem recibo e correção referenciada. Registro do histórico já carregado passa a refletir a decisão recém-confirmada/rejeitada.

### Testes executados nesta correção

- 33 testes JS: julgamento (12), preparação (10), grupos (9), apresentação/afiliação (2).
- 19 testes Python HTTP: julgamento (5), CPC mapa (6), grupos (8).
- 1 teste Python adicional de assets (8 subcasos): autenticação e MIME/cache de CSS/MJS para instrutor e operadores dos dois partidos.
- Total: **53 testes nomeados passaram**. Também passou o verificador assertivo `check_map_visuals.mjs`. Não se declara reexecução dos 183 testes históricos acumulados.
- Sintaxe dos módulos alterados e revisão do diff verificadas; sem mudança nos comandos de combate, escopo SQL ou regras de autorização.

### Inspeção real

Prévia isolada `http://localhost:61270/`, processo do harness, pasta `%TEMP%/siscan-ux-20261117-v1`. Usuário 1 instrutor; 2 AZUL; 3 VERMELHO. Senha exclusivamente de teste: `somente-teste-local`. Não foi iniciado/reiniciado o principal em 8787 nem o processo anterior em 61269; bases preservadas. Um processo Python anterior precisa ser atualizado para servir os novos assets; use 61270 nesta entrega.

Calunga real apresentou preenchimento amigo `rgb(128,224,255)` e hostil `rgb(255,128,128)`, ambas as famílias em 36 × 28 px. Ficha observada por foco de teclado: conteúdo de aproximadamente 210 × 125–140 px; nome completo, origem de planejamento, índice conhecido ou não avaliado, revisão e combustível não informado. A largura explícita evita a caixa estreita e excessivamente alta causada por shrink-to-fit com quebra de palavras.

Percurso real: preparar → editar → revisar → voltar à edição → salvar → avançar → cancelar aplicação → retomar após reload → confirmar → consultar resultado. Dados inteiramente sintéticos: AZUL 55%, VERMELHO 45%; duas decisões independentes. Cancelar não aplicou a proposta; aplicar exigiu o botão final separado. Foco acompanha a etapa e seleção no mapa abre a consulta do integrante. Histórico/recibos sobreviveram aos reloads.

Larguras 320, 390, 768, 1024, 1280 e 1440 px examinadas por geometria/inspeção; sem transbordamento horizontal observado. Amostra desktop com painel de 340 px; largura ajustável pelo separador original preservada; viewport 320 com painel de 296 px. Em tela estreita, painel inferior limitado a 54%, rolagem interna e controles de toque; referências e composição expansíveis. Isso não constitui auditoria integral WCAG ou teste de todo aparelho.

Evidência fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-ui-ux-revisao-20261117.png` e `siscan-ui-ux-final-20261117.png`.

## Limites e continuidade

Esta correção melhora apresentação e operação do julgamento didático existente. Não implementa animação/reprodução temporal de confronto nem resolução automática por grupamentos. Mantidos os requisitos de 97, 104 e 113; não representa calibração física dos dados Command. Ativação do principal continua sujeita à preparação de backup/migração e preservação de grupos temporários já descritas em 116. Originais ATLANTICADOR, PDF e DB3K preservados.

Na revisão foi corrigida também uma corrida: se o carregamento assíncrono Calunga terminava depois da entrada no CPC, tentava redesenhar marcadores de planejamento já removidos. A conclusão agora atualiza somente a camada do modo vigente. Troca rápida reproduzida novamente em uma aba nova, com console final sem erros/avisos. Enquadramento considera a área coberta pelo painel inferior: a 390 × 844, ambos os marcadores ficaram entre y=239 e 277, acima do painel em y=386.

Operador AZUL verificado em sessão separada: um meio próprio, seletor de partido bloqueado e nenhuma aba CPC. Na base de teste, `integrity_check=ok`, nenhuma violação de FK, duas posições, zero comandos de plotagem, zero execuções e zero estados de recursos. Nenhuma simulação foi acionada pela correção visual.
