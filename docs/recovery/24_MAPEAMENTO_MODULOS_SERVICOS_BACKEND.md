# 24 — Mapeamento de módulos e serviços do backend

Inventário estático do pacote ATLANTICADOR 2.0.0. Caminhos relativos ao ZIP (`atlanticador-main/`). Linhas indicam a localização examinada e não comprovam funcionamento.

| Módulo | Responsabilidade observada | Dependências / dados | Relação possível com SISCAN (avaliação, não decisão) |
|---|---|---|---|
| `serve.py:26-452` | Inicialização HTTP, rotas, cookies, validação de requisições, códigos de erro e despacho | `Auth`, `SourceStore`, `Situation`, diretório frontend | Isolar como referência de endpoints e separação de responsabilidades; não portar o handler diretamente. |
| `auth.py:25-227` | Hash/verificação de senha, login, sessão, ingresso e troca de senha | `profile_store`, `AccessBlocks`, `AccessAudit`; SQLite/JSON | Reavaliar requisitos próprios de identidade, sessão e trilha SISCAN; nenhuma adoção presumida. |
| `profiles.py` | Perfil público, partido e fontes permitidas | Contas, papéis e organização | Referência para autorização contextual, após comparar com modelo de acesso do SISCAN. |
| `function_roles.py` | Funções iniciais e classificação de permissões | Normalização de nomes de funções | Isolar: regras são específicas da DIREx/ATLANTICADOR. |
| `profile_store.py:9-34` | Leitura do cadastro SQLite após migração, fallback JSON | `situation.sqlite3`, `accounts.json` | Reavaliar fonte mestre e ciclo de migração; evitar duplicação de cadastro. |
| `situation.py:28-342` | Transação, atores, estado, baseline, snapshots, eventos e papéis | SQLite WAL; mixins de confronto, efeito e mapa | Referência conceitual; separar domínios e validar compatibilidade com decisões SISCAN. |
| `record_queries.py` | Listagem/paginação e filtros de registros serializados | tabelas `effect_records` e `confrontations` | Referência de consulta; formato JSON interno não é contrato para SISCAN. |
| `effect_workflow.py:48-368` | Rascunho, edição concorrente, validação, aprovação, aplicação e agenda de efeitos | `effect_records`, `effect_editors`, elementos, triggers, audit; mixin de propostas/mapa | Potencial referência de workflow auditável; regras e estados requerem avaliação independente. |
| `party_proposals.py:8-213` | Proposta de partido, destinatários e intake por blocos DIREx | Efeitos, perfis, células, revisão | Isolar regras organizacionais específicas; só referência para tramitação. |
| `confrontations.py:38-486` | Registro e arbitragem manual de confrontos, respostas por célula, efetivação | `confrontations`, elementos, efeitos e auditoria | Referência conceitual para decisão humana rastreável; não importar cálculo nem política do simulador. |
| `effect_annul.py` | Anulação/reversão do efeito aplicado | Elementos, histórico e snapshots | Reavaliar necessidade de reversibilidade e trilha no SISCAN. |
| `unit_conditions.py` | Normalização/consulta de condições de unidade | Estados JSON de elementos | Referência para vocabulário de estados; requer glossário/domínio SISCAN próprio. |
| `sources.py:21-300` | Fontes configuráveis, download e validação de KMZ, cache, ciclo de sincronização | `sources.json`, rede HTTP, cache de arquivos | Isolar dependência cartográfica externa; revisar segurança, proveniência e conectividade se necessário. |
| `official_kmz.py:1-204` | Leitura/validação e serialização KML/KMZ, baseline/snapshot | `sources.validate_kmz`, XML, ZIP | Formato de intercâmbio de mapas possível; não assumir como modelo de domínio. |
| `structured_map.py` | Modo estruturado, exportação e materialização de mudanças | `map_templates`, `export_deltas`, DB situação | Reavaliar contra arquitetura geográfica do SISCAN. |
| `export_deltas.py` | Captura/restauração de deltas para materialização de exportações | `map_exports`, estados/efeitos | Referência de publicação incremental; não presumir necessidade. |
| `map_templates.py` | Templates e adaptação de elementos para mapa | elementos e configuração cartográfica | Isolar detalhes de apresentação. |
| `calunga.py` | Normalização de anotações/elementos gráficos | adições de efeitos/propostas | Referência de anotação geográfica; depende de semântica própria. |
| `access_blocks.py:9-70` | Bloqueio de conta, histórico e janela temporária de ingresso | `access.sqlite3` | Reavaliar com política de acesso SISCAN. |
| `access_audit.py:13-40` | Eventos restritos de acesso em log append-only | `access-log.sqlite3`, journal fallback | Referência para trilha mínima; requisitos legais/operacionais precisam avaliação. |
| `manage.py` | Comandos de manutenção/migração | arquivos de dados e cadastro | Não foi executado; avaliar cada operação antes de qualquer uso. |

### Dependências entre serviços

`serve.py` despacha chamadas para `Auth`, `SourceStore` e `Situation`. `Situation` compartilha conexão/transação com mixins. `Confrontations` cria um efeito aplicável por `EffectWorkflow`; `PartyProposals` também compõe `EffectWorkflow`. `EffectWorkflow` consulta estado de elementos e pode chamar a materialização cartográfica. `StructuredMap` usa templates e deltas. Autenticação consulta perfis e módulos de bloqueio/auditoria. Essa composição cria dependências cruzadas e torna inadequado tratar os módulos como componentes isoláveis sem análise de contratos.

### Classificação para avaliação futura

As indicações “referência”, “isolar” e “reavaliar” são classificações documentais desta auditoria, não decisões de arquitetura. A matriz por componente e decisão está em [28](28_MATRIZ_REUTILIZACAO_BACKEND_SISCAN.md).
