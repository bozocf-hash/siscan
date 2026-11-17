# 104 — Ligação entre mapa, ensaio e decisão do instrutor

**Data: 2026-11-17. Estado: recorte de integração proposto para revisão.** O responsável pediu continuar a ligação que falta entre mapa, ensaio e confirmação do resultado. Esta proposta usa as capacidades já identificadas no mapa do projeto, sem substituir o ATLANTICADOR ou reabrir entregas 93/98/102.

## Objetivo visível

O instrutor deve conseguir selecionar as composições AZUL/VERMELHO no mapa existente, conferir a situação inicial, registrar uma proposta de resultado, revisá-la e confirmar seus efeitos. Somente o resultado confirmado passa a ser estado oficial dos meios. Cancelar ou rejeitar uma proposta não altera o exercício.

Esta ligação envolve três responsabilidades verificáveis separadamente: preparação/apuração, publicação do estado oficial e histórico durável. Por isso, esta etapa delimita responsabilidades e ordem antes de novas especificações ou alterações de banco, conforme a skill Spec Driven Development solicitada pelo responsável. Os IDs existentes são preservados.

## Evidência encontrada

- 102: composição/consulta/arquivo já integrados ao mapa, com registro temporário; não há seleção de par ou botão de execução CPC.
- `cpc_group_preparation.py`: dossiê AZUL/VERMELHO em memória, com snapshots e revisões, sem efeitos; ainda não possui rota gráfica.
- `map_units.py`: disponibilidade operacional/capacidade de combate ainda são não informadas; não existe provedor de adjudicação oficial nessas consultas.
- `engine_runtime.py`: relógio e contabilidade de combustível têm referências/revisões próprias; não são estado de avarias ou índice operativo e não podem ser alterados como atalho para julgar confronto.
- CPC 84–88: ensaio de unidades individuais com parâmetros sintéticos explícitos. Os snapshots atualmente elegíveis na ponte gráfica são do contrato aéreo sintético de combustível; não fornecem automaticamente HP, probabilidade de acerto, detecção, armamentos e demais entradas necessárias à resolução de combate.

Inspeção desta etapa foi de código/documentação. Não houve nova auditoria do DB3K, leitura visual do mapa ou execução de testes; nenhuma funcionalidade descrita abaixo já está implementada por este documento.

## Primeira integração proposta: julgamento didático completo

Começar pelo caminho de arbitragem direta já previsto em 80 e 103. O sistema registra o que o instrutor decidiu, mostra uma prévia e aplica somente após confirmação. **Não há sorteio ou resultado de combate calculado nesse modo.** Chamar a entrada de “julgamento didático”, sem apresentá-la como simulação automática executada.

O instrutor informa efeitos nas unidades selecionadas e justificativa, com revisão antes de confirmar. A proposta não consome combustível/munição, move unidades, muda o relógio ou altera avarias. Dados logísticos disponíveis podem ser exibidos com origem/unidade e momento; desconhecidos continuam desconhecidos. Débito de recursos não é deduzido de um percentual de avaria.

O ensaio automático será um caminho posterior para produzir propostas pelo mesmo contrato, limitado inicialmente a regras didáticas e entradas sintéticas verificadas. Não preencher os parâmetros ausentes por valores presumidos nem converter campos de catálogo em eficácia validada. A aprovação da ponte gráfica não homologa algoritmo automático.

## Responsabilidades — IDs existentes

| Capacidade | Responsabilidade nesta ligação | Consome |
|---|---|---|
| `unit-registry` / `party-inventory` | Entregar composição, identidade, snapshots e disponibilidade autorizada; não julgar combate | Provedores já existentes |
| `force-confrontation` | Selecionar par, preparar dossiê, registrar proposta didática e pedir confirmação/aplicação; apresentar o fluxo no mesmo mapa | Composições/inventário, contexto/revisões e contrato de estado oficial |
| `operational-state` | Ser a autoridade de leitura/aplicação dos efeitos confirmados por unidade; manter avaliação de origem distinta de restrição por recursos | Identidade, autorização/contexto e revisão atual do exercício/unidade |
| `execution-core` | Fornecer contexto/revisões e suporte de comandos/recibos/histórico transacional; não calcular resultado militar | Identidades e contratos existentes de execução |
| `verification-recovery` | Conferir autorização, concorrência, persistência/recuperação e ausência de efeitos por proposta/rejeição/reenvio | Contratos das capacidades acima |

Não criar um serviço independente de mapa nem um segundo motor. A apuração consome/solicita efeitos ao provedor de estado; o provedor não executa nem importa o modelo de confronto. Contratos compartilhados de identidade/contexto não devem introduzir dependência circular.

## Ordem proposta

1. **Seleção do par e conferência no mapa:** escolher grupos/revisões, preparar dossiê por backend autorizado e mostrar os integrantes/pendências. Reutilizar o painel existente. Esta parte pode avançar antes do publicador de efeitos, mas não terá botão que finja confirmar estado oficial.
2. **Contrato e armazenamento de estado/adjudicação:** especificar o estado por unidade e um registro durável de proposta, decisão e efeitos, com versões, autoria, referências antes/depois e recuperação. Preparar o provedor antes de ligar a publicação. Migração do banco SISCAN exige especificação/plano próprios; DB3K/originais continuam intocados.
3. **Julgamento didático → prévia → confirmação → mapa:** registrar a proposta, permitir revisar/ajustar/rejeitar e aplicar por comando autorizado, verificando contexto/revisões/disponibilidade. Resultado confirmado e seus efeitos devem ser publicados de forma rastreável e sem aplicação parcial ou repetida.
4. **Ensaio automático como produtor de proposta:** fechar rubrica/entradas e adaptador de estados individuais, depois ligar sua saída ao mesmo caminho de revisão/decisão. Não duplicar o publicador ou permitir aplicação automática ao terminar o ensaio.

Etapas 1–3 fecham o primeiro fluxo gráfico completo de arbitragem didática. A etapa 1 sozinha não será anunciada como entrega do confronto. O caminho automático permanece explicitamente pendente até as entradas/regras serem definidas e verificadas.

## Experiência do instrutor proposta

```text
Mesmo mapa → Selecionar AZUL/VERMELHO → Conferir situação inicial
          → Julgamento didático → Prévia dos efeitos
          → Rejeitar / Ajustar / Confirmar
          → Estado oficial e histórico no mesmo mapa
```

Na conferência, mostrar revisões e dados ausentes. Na prévia, identificar claramente proposta, autor e motivo, sem pintar o mapa como se as perdas já fossem oficiais. Na confirmação, mostrar efeitos finais por unidade e exigir ação explícita do instrutor; não juntar a essa ação um avanço do relógio ou consumo não informado.

No mapa, estado confirmado pode ser consultado em ficha/realce, com autoria/momento; a proposta rejeitada fica apenas no histórico autorizado. Não abrir painéis sobrepostos. Operadores veem somente dados/efeitos autorizados; não receber a composição adversária completa para ocultá-la por CSS.

## Invariantes do fluxo completo

- Somente instrutor atribuído ao exercício confirma/ajusta efeitos oficiais; operador não ganha essa autoridade por poder compor forças.
- Proposta, decisão e aplicação são registros distintos. Edição anterior à confirmação cria revisão rastreável; correção posterior não apaga o histórico original.
- Confirmação usa revisão esperada e comando idempotente. Conflito, perda de disponibilidade ou referência incompatível recusam o lote sem efeitos parciais; recibo antigo não contorna autorização atual.
- Resultado e referências congeladas precisam sobreviver ao reinício; o registro temporário de grupos não é armazenamento suficiente para decisões oficiais. Perda de um grupo temporário não pode apagar um resultado já confirmado.
- Aplicação não altera snapshots técnicos, configuração original, DB3K, fonte ou aprovação de dados. Estado de exercício é uma camada própria.
- Índice inicialmente desconhecido não vira 100%. Não calcular dano percentual quando a base anterior não é conhecida. Faixas de superfície preservam >60 combater, 40–60 inclusive navegar, <40 flutuar; não transferir essas faixas automaticamente a aeronaves/terrestres.
- Condição de origem e restrição por recurso continuam separadas. Mínimo de combustível do operador e margem fixa de 5 pontos são preservados; limiar/agregação de armamento ainda exigem definição própria. Não instituir 30% universal ou somar munições heterogêneas.

## Critérios de conclusão da ligação

O primeiro fluxo completo só estará entregue quando o instrutor puder percorrer as etapas no navegador, o estado oficial mudar apenas após confirmação, rejeição não produzir efeitos, reenvio não duplicar aplicação e o histórico/estado sobreviverem ao reinício. A verificação deve usar dados isolados e comprovar a visibilidade por partido e o antes/depois por unidade.

Seleção/preparação, estado oficial e persistência serão especificados nos módulos correspondentes antes do código. Esta proposta não detalha schema/rotas ou transforma instrução de continuidade em aprovação de DDL. Manter os planos anteriores abertos e seus gates já cumpridos.

## Gate desta proposta

Solicitar revisão do recorte e da ordem, especialmente do caminho didático completo antes do automático. A skill [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) orienta: “Propose a capability map before writing any spec.” Esta proposta aplica os IDs já existentes à integração pedida, sem reabrir a concepção geral. Depois de aprovada, especificar cada contrato afetado, preservando suas fronteiras e dependências.
