# 14 — Referências conceituais CMO ↔ SISCAN

## Enquadramento

O manual CMO documenta um simulador comercial e não apresenta um modelo relacional formal. As correspondências abaixo são hipóteses para apoiar a compreensão do SISCAN; não são decisão de produto, requisito aprovado, recomendação de replicação ou autorização para alterar decisões anteriores. ATLANTICADOR e DB3K não foram modificados.

| Conceito no CMO | Descrição encontrada | Página | Possível relação com SISCAN | Situação |
|---|---|---:|---|---|
| Cenário/estado inicial | Configura tempo, geografia, forças, duração e condições | 82–100 | Entidade de exercício com versão/estado e proveniência | Possível requisito |
| Catálogo separado | Catálogo de plataformas/componentes tem versão; cenário registra a versão usada | 207–221 | Dados de referência separados de instâncias e execução | Referência conceitual |
| Participante/lado | Lados e posturas organizam participantes | 87–100 | Participante/equipe e relação contextual | Necessita de avaliação |
| Unidade, grupo e hospedagem | Unidades agrupadas ou hospedadas por outras | 19–21, 104–117 | Estrutura hierárquica, agregação e lotação | Necessita de avaliação |
| Composição de plataforma | Mounts, magazines, sensores e componentes associados à unidade | 19–21, 50–57, 271–273 | Recursos/capacidades com vínculos e validade | Necessita de avaliação |
| Missão, participante e área | Tarefas atribuídas a unidades/grupos em área ou contra alvo | 180–206 | Atividade planejada, responsável, zona e objetivo | Possível requisito |
| Evento, gatilho e ação | Condição aciona ação configurada | 124–140 | Ocorrência, regra, decisão e efeito auditáveis | Necessita de avaliação |
| Observação e decisão | Sensores produzem contatos; engajamento depende de modelos e regras | 21, 223–265 | Distinguir observado, incerto, adjudicado e resultado | Referência conceitual |
| Briefing/premissas | Texto informativo associado a cenário/lado | 96–99 | Instruções e contexto da execução | Já contemplado na concepção do SISCAN |
| Pontuação/avaliação | Score configurado e apresentado como resultado | 94–99, 172–174 | Indicadores vinculados à rubrica acadêmica aprovada | Já contemplado na concepção do SISCAN |
| Mensagens/trilha | Log de eventos/notificações e gravação de sessão | 38–41, 163–168 | Auditoria, autoria, horário e reconstrução | Possível requisito |
| Relatórios | Perdas, dispêndios, score e atividade | 168–174 | Relatórios de execução sem copiar métricas do jogo | Possível requisito |
| Área/camada geográfica | Pontos, áreas e overlay georreferenciado | 200–206, 268–271 | Zonas espaciais e apresentação cartográfica | Necessita de avaliação |
| Versionamento/changelog | Versões de catálogo/cenário e histórico de atualização | 207–221, 291–351 | Rastrear modelo, parâmetros e dados de cada execução | Referência conceitual |

## Relações a validar, sem inferir esquema

O manual sugere relações conceituais cenário–lado–unidade; unidade–grupo/hospedeira–componente; missão–unidade–área/alvo; evento–gatilho–ação; cenário–catálogo versionado; execução–mensagens–relatórios. Isso não determina cardinalidades, chaves, persistência, temporalidade ou permissões. IDs e formatos são próprios do CMO; não inferir compatibilidade ou copiar estruturas proprietárias.

## Questões para avaliação futura

- Quais entidades e vínculos já aprovados cobrem exercício, participante, força, atividade, evento, avaliação e relatório?
- O cenário precisa ser imutável/versionado após início? Como registrar mudança e autoria?
- Como distinguir dado observado, adjudicação, hipótese, estimativa e resultado?
- Áreas geográficas são necessárias ao escopo acadêmico e com quais fontes/licenças?
- A pontuação segue rubrica explícita e validada ou exige indicadores diferentes?
- Qual nível de catálogo de plataforma/componentes é necessário sem importar DB3K como esquema SISCAN?

Essas perguntas não alteram decisões anteriores nem iniciam implementação. Permanecem para avaliação do responsável.
