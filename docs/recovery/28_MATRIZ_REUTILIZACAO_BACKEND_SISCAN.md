# 28 — Matriz de avaliação de reutilização do backend no SISCAN

Esta matriz é documental. Nenhum componente está aprovado para cópia, integração ou implementação. “Reutilizar com adaptação” significa apenas candidato a estudo; depende de decisão do responsável, requisitos SISCAN e auditorias próprias.

| Componente ATLANTICADOR | Avaliação para SISCAN | Justificativa/evidência | Condição ou questão |
|---|---|---|---|
| Fluxo `expected_revision` e conflito explícito | **Reutilizar com adaptação** | Controle otimista em efeitos e confrontos (`effect_workflow.py:217-256`; `confrontations.py:120-128`). | Definir agregados, concorrência e mensagens de conflito do SISCAN. |
| Histórico por ação e ator | **Reutilizar com adaptação** | Log de domínio em situação e snapshots; auditoria de acesso separada. | Política de retenção, campos, acesso e requisitos legais ainda não definidos aqui. |
| Aprovação em etapas e aprovadores distintos | **Reavaliar** | Fluxos variam entre efeito, proposta e confronto. | Comparar com alçadas/processos aprovados do SISCAN; não transplantar papéis. |
| Confronto como registro de arbitragem humana | **Referência conceitual** | Pareceres, revisão e efetivação humana; código nega automação tática. | Confirmar se e como o SISCAN tratará arbitragem. |
| Modelo específico de células/partidos/DIREx | **Isolar** | Funções, permissões e destinatários são próprios do ATLANTICADOR. | Não assumir equivalência com estrutura organizacional MPNL/SISCAN. |
| Cadastro de perfis e fallback JSON/SQLite | **Reavaliar** | Múltiplas fontes de identidade e migração (`profile_store.py`, `auth.py`). | Definir fonte mestre e evitar duplicidade de contas no SISCAN. |
| Hash PBKDF2/sessão HTTP | **Referência conceitual** | Controles observados no código, ainda sem validação de segurança. | Identidade/autenticação da solução final requer projeto e revisão próprios. |
| `serve.py` e despacho manual de rotas | **Isolar** | HTTP, auth e serviços fortemente acoplados; sem contrato OpenAPI. | Decidir arquitetura de API do SISCAN independentemente. |
| Persistência JSON em SQLite | **Reavaliar** | Flexibilidade, mas relacionamentos e domínio parcialmente embutidos em JSON. | Confrontar com modelo conceitual e integridade requerida no SISCAN. |
| Auditoria append-only de acesso | **Reutilizar com adaptação** | Lista restrita de eventos/recursos, índice temporal e triggers (`access_audit.py`). | Definir auditoria de domínio e acesso completa, segregação e retenção. |
| `SourceStore` e sincronização de KMZ | **Isolar** | Importação de fontes específicas e dependência externa. | Só considerar se ingestão cartográfica for requisito confirmado. |
| Baseline KMZ e snapshots oficiais | **Referência conceitual** | Versionamento de fonte e publicação imutável como padrão observado. | Avaliar estratégia cartográfica SISCAN e preservação de origem. |
| Modo `structured_map` e exportação por deltas | **Reavaliar** | Opção técnica específica, não testada nesta auditoria. | Comparar necessidade, formato e desempenho antes de qualquer decisão. |
| Geometria/Calunga e templates de mapa | **Isolar** | Conceitos ligados à interface e convenções do simulador. | Vocabulário cartográfico SISCAN próprio. |
| Banco DB3K | **Isolar como fonte** | É banco externo distinto; foi analisado em trilha de recuperação independente. | Mapeamentos semânticos só com evidências e validação explícita. |
| Comandos `manage.py` | **Não aplicável nesta fase** | Não executados; podem alterar dados. | Avaliar operação individualmente apenas em missão autorizada. |

## Categorias

- **Preservar:** os documentos e decisões SISCAN existentes, sem substituí-los por desenho do ATLANTICADOR.
- **Reutilizar com adaptação:** apenas padrões conceituais passíveis de estudo, como revisão otimista ou trilha de mudanças.
- **Isolar:** código, papéis, dados e convenções que pertencem ao simulador.
- **Reavaliar:** pontos sem requisito ou evidência suficiente; não há implementação implícita.

## Relação com decisões atuais

Esta matriz não altera o modelo conceitual SISCAN, a hierarquia MPNL de quatro níveis, a MPNL-001, ou decisões registradas nos documentos 01–10. Cada relação ainda é proposta/inferência e depende de autorização expressa para próxima fase.
