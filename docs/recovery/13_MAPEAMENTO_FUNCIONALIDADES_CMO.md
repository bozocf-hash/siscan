# 13 — Mapeamento de funcionalidades do CMO

Páginas físicas do PDF. A classificação indica somente a natureza da possível relação com SISCAN; não aprova requisito, cópia ou implementação.

| Conceito no CMO | Descrição encontrada | Página | Possível relação com SISCAN | Situação |
|---|---|---:|---|---|
| Cenário | Contexto temporal, geográfico e de forças; duração e carga/gravação | 23–25, 82–147 | Delimitação de exercício, estado e configuração | Referência conceitual |
| Versão do banco no cenário | Cenário associa catálogo/versionamento de dados usado | 207–221 | Proveniência e reprodutibilidade | Possível requisito |
| Lados e postura | Lados jogáveis/não jogáveis e relações de postura | 87–100 | Participantes, equipes e relações do exercício | Necessita de avaliação |
| Ordem de batalha (OOB) | Visualização hierárquica de forças/unidades | 154–158 | Estrutura de participantes e organização do exercício | Referência conceitual |
| Unidade/hospedeira | Uma unidade pode hospedar outras, instalações e componentes | 19–21, 100–117 | Hierarquia, lotação e vínculo de plataforma/componente | Necessita de avaliação |
| Grupos | Organização de unidades com parâmetros e membros | 19–21, 104–117, 160 | Agrupamento de elementos do exercício | Referência conceitual |
| Plataforma/catálogo | Navio, aeronave, submarino, arma, sensor, instalação e outros | 207–221, 271–275 | Separar catálogo de instância de cenário | Possível requisito |
| Mounts, magazines e componentes | Componentes instalados, estoques e recarga | 19–21, 50–57, 271–273 | Inventário de recursos se necessário ao escopo acadêmico | Necessita de avaliação |
| Sensores e observação | Classes radar/ESM/sonar/óptica, ativos/passivos | 21, 48–57, 223–229 | Separar observação, fonte e decisão adjudicada | Referência conceitual |
| Missão | Tarefa atribuída a unidades/grupos por área ou alvo, com parâmetros | 60–65, 180–199 | Planejamento de atividades e participantes | Possível requisito |
| Tipos de missão | Ferry, Support, Patrol, Strike, Mining, Mine-clearing, Cargo | 182–199 | Taxonomia de tarefas sujeita ao cenário SISCAN | Não aplicável |
| Ponto de referência/área | Geometria nomeada, área por pontos ou referência móvel | 91–99, 200–206 | Geografia do exercício e validação de zonas | Possível requisito |
| Eventos | Trigger+action, com repetição, atividade e probabilidade | 124–140 | Registro de ocorrências/regras; avaliar governança humana | Necessita de avaliação |
| Briefing | Texto informativo por lado/cenário | 96–99, 155–156 | Orientação e premissas do exercício | Já contemplado na concepção do SISCAN |
| Pontuação | Score configurável e apresentado como resultado | 94–99, 172–174 | Avaliação acadêmica se compatível com rubrica aprovada | Já contemplado na concepção do SISCAN |
| Mensagens/log | Log de mensagens/eventos e notificações | 38–41, 163–166 | Trilha de auditoria/comunicação | Possível requisito |
| Histórico/recorder | Grava sessão `.rec`; histórico de atualização do produto | 41, 165–168, 291–351 | Reprodutibilidade e histórico de decisões; formato específico não aplicável | Referência conceitual |
| Relatórios/perdas | Apresentação de perdas, gastos e pontuação | 168–174 | Relatórios de execução e indicadores | Possível requisito |
| Banco/templates | Catálogos CWDB/DB3K, manutenção/rebuild e templates | 207–221 | Versionamento, proveniência e configuração | Referência conceitual |
| Overlays geográficos | Imagem georreferenciada e world file | 268–271 | Camadas cartográficas, sujeitas a fonte/licença/resolução | Necessita de avaliação |
| Combate/diagnóstico | Modelos por domínio, sensores/armas, danos e razões de não engajamento | 222–265 | Separar observação, modelo, arbitragem e resultado | Não aplicável |
| Lua/automação | Scripts/ações configuráveis em eventos/editor | 119–140 | Automação exigiria governança, segurança e escopo próprios | Não aplicável |
| Instalação/interface CMO | Procedimentos e menus específicos do produto | 14–15, 27–81 | Sem dependência necessária no SISCAN | Não aplicável |

“Já contemplado” refere-se à concepção documental SISCAN recuperada, não a implementação. “Não aplicável” refere-se à função específica do simulador não ser transposta automaticamente; não descarta necessariamente todo conceito subjacente.
