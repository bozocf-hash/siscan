# 03 — Auditoria do ATLANTICADOR

## Fonte e método

**IDENTIFICADO:** foi inspecionado estaticamente `atlanticador-main (1).zip`, em `C:\Users\bozoc\Documents\siscan\`, sem extraí-lo nem alterar seu conteúdo. O arquivo contém 541 entradas; a versão declara `2.0.0` em `VERSION` e `package.json`. Foram lidos `AGENTS.md`, README, dependências, escopo 1.0, `serve.py`, `situation.py`, `confrontations.py`, módulos de front-end e documentos do fluxo Confronto. Não foram executados testes nem iniciado o servidor. ZIP não fornece histórico Git/commit verificável. Conclusões refletem a fotografia do arquivo compactado, não necessariamente o checkout ou implantação atual.

## Tecnologias e estrutura observadas

| Área | Identificado no arquivo |
|---|---|
| Servidor | `serve.py`: `http.server` (`SimpleHTTPRequestHandler`, `ThreadingHTTPServer`) da biblioteca padrão Python; módulos próprios de auth, perfis, fontes e situação |
| Persistência | SQLite importado e usado por `Situation`; a situação e os confrontos são mantidos no banco operacional `situation.sqlite3` criado no diretório de dados. Isso é distinto do DB3K do CMO |
| Front-end | HTML, CSS e JavaScript em ES Modules, sob `frontend/`; `package.json` declara Node >=20 para scripts de teste, sem etapa obrigatória de build para a interface descrita |
| Mapa | Documentação `docs/DEPENDENCIAS.md` identifica Leaflet 1.9.4, leaflet-rotate 0.2.8, polygon-clipping 0.15.7, fflate 0.8.2, html-to-image 1.11.13 e jsPDF 2.5.2; dependências distribuídas localmente |
| Cartografia/fontes | Módulos incluem `cartography.mjs`, `geometry.mjs`, `kml.mjs`, `map-import.mjs`, `map-export*.mjs`, `layer-tree.mjs`, `viewer.mjs`; servidor possui `sources.py`, `structured_map.py` e `official_kmz.py` |
| Acesso e auditoria | `auth.py`, `profiles.py`, `profile_store.py`, `access_audit.py`, `access_blocks.py`; README/escopo descrevem autenticação e segregação de dados por perfil/partido |
| Efeitos/situação | `situation.py`, `effect_workflow.py`, `effect_kmz.py`, `effect_annul.py`, `unit_conditions.py`, módulos de histórico e edição |
| Simbologia | `calunga.py`, `frontend/src/calunga-generator.mjs`, `symbols.mjs`, catálogo/artefatos de ícones. Não se validou o catálogo visual inteiro |
| Testes | ZIP contém testes Python, Node e navegador e scripts para executá-los. **Não executados** nesta missão |

## Recursos evidenciados e estado

O README define o produto como apoio à representação e controle da situação operacional em exercícios simulados. O escopo 1.0 separa um visualizador autenticado de KMZ por partido de capacidades mais amplas do editor anterior. Documentação posterior do ZIP descreve versão 2.0 com efeitos e confrontos. Portanto, o repositório agrega camadas históricas e escopos distintos: não tratar todos os recursos do README como parte do fluxo atual sem checar a rota/versão implantada.

**IDENTIFICADO no código/documentação:** servidor autenticado, perfis, filtros de fonte no servidor, visualização/camadas, ingestão/fontes KMZ, situação oficial, registro de eventos/efeitos e fluxo de revisão/aprovação; módulos geográficos e de exportação; simbologia Calunga. A documentação cita PNG/PDF/KMZ/GeoJSON em módulos/versões do editor. Disponibilidade operacional de cada recurso depende do modo e configuração; não foi executado.

### Confrontos — distinção necessária

- `confrontations.py` persiste registros de confronto, permissões por célula, tropas selecionadas, revisões, operações, pareceres/histórico e fluxo de aprovação com efeito vinculado.
- `frontend/src/confrontations.mjs` apresenta o fluxo e `confrontation-models.mjs` implementa funções puras de comparação/modelagem, com colunas identificadas como DAMEPLAN puro, DAMEPLAN base, CombaTer, SBE adaptado e convenção ATLANTICADOR. Há parâmetros editáveis e cálculos de PRC/degradação; isso é mais do que simples CRUD de formulário.
- `confrontation-game.mjs` gera comparação abstrata em pontos por perfis de dificuldade, usando aleatoriedade; seu cabeçalho diz que não usa características de tropas nem tabelas doutrinárias.
- A documentação `docs/CONFRONTO-2.0.md` diz expressamente que o fluxo principal é arbitragem humana, que modelos não aplicam automaticamente resultados nem recomendam movimento/estado, e que a decisão final revalida revisões antes de aplicar um efeito único. `docs/VALIDACAO-CONFRONTOS-20261103.md` registra validação anterior, não repetida nesta missão.

**Conclusão:** há modelos matemáticos de apoio ao exercício, mas a evidência não autoriza chamar o sistema de motor determinístico/autônomo de simulação de combate. Essa distinção também não transforma o módulo de confrontos terrestre do ATLANTICADOR em requisito aprovado do SISCAN naval.

## Integração com SISCAN

**DECIDIDO no contexto SISCAN:** reaproveitar o ATLANTICADOR onde adequado. **INFERÊNCIA:** capacidades úteis a avaliar incluem mapa/camadas, geometria, simbologia, autenticação e trilha de eventos. **PENDENTE:** contratos, banco, isolamento de dados, operação sem mapa para MPNL, fronteiras entre módulos e se os fluxos existentes são reutilizáveis. A arquitetura SISCAN não deve assumir que o modelo atual do ATLANTICADOR cubra unidades navais, navegação temporal ou logística proposta.

## Limitações

Inspeção estática de um ZIP, sem checkout Git, configuração privada, banco operacional, dados de exercícios, execução ou verificação visual completa. Não se confirmou implantação, estado do serviço, dependências em tempo de execução, nem todas as 541 entradas. Nenhum arquivo fonte foi modificado.
