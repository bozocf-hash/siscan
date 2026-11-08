# 43 — Matriz proposta de papéis, permissões e privacidade

**Status:** matriz redigida antes da decisão APR-02. Papéis, princípios de privacidade e regra visual foram aprovados com limites em [49](49_REGISTRO_DECISOES_APR_01_A_APR_20.md); permissões finas por ação/exercício permanecem pendentes. Este documento não substitui essa decisão nem autoriza implementação.

## Camadas de autorização conceitual

1. **Papel de usuário:** funções gerais (administrador, instrutor, aluno, avaliador, observador), que definem capacidades possíveis.
2. **Atribuição de exercício:** associação explícita a um exercício e a uma função naquele exercício; uma conta sem atribuição não recebe acesso por apenas ter papel global.
3. **Escopo de equipe/força:** aluno acessa apenas a equipe e os meios atribuídos. Pertencer a uma equipe não permite consultar respostas de outra equipe.

Permissões efetivas resultam da combinação e devem ser validadas no backend. O filtro da interface não é uma barreira de confidencialidade (19,29,35 DEC-021, ainda proposta quanto à arquitetura).

## Matriz proposta

Legenda: **S** permitido no escopo designado; **A** condicionado à atribuição/configuração do exercício; **P** leitura somente após liberação explícita; **N** negado por padrão. O responsável deve definir exceções.

| Ação/recurso | Administrador | Instrutor | Aluno Azul/Vermelho | Avaliador | Observador |
|---|---:|---:|---:|---:|---:|
| Consultar lista de cenários rascunho | A (admin técnico, atribuído) | S (se autor/atribuído) | N | A | N |
| Consultar cenário publicado de exercício atribuído | A (sem conteúdo acadêmico por padrão) | S | S (atribuição) | S (atribuição) | P |
| Criar/editar cenário | N por padrão; atribuição explícita | S | N | N | N |
| Publicar versão/condições iniciais | N por padrão | S (instrutor responsável) | N | N | N |
| Distribuir meios e atribuições | N por padrão | S | N | N | N |
| Participar de exercício | N como aluno | S como responsável | S (somente atribuído/equipe) | A | A somente leitura |
| Salvar/alterar próprio rascunho | N por padrão | N como aluno | S (próprio; regras de prazo) | N | N |
| Submeter ou revisar própria resposta | N por padrão | N como aluno | S (próprio; dentro de estado/prazo) | N | N |
| Ver própria resposta/estado | A (sem conteúdo por padrão) | S (exercício sob responsabilidade) | S | S (escopo atribuído) | P |
| Ver resposta de outro participante antes da liberação | N por padrão | S (exercício sob responsabilidade) | **N** | A (designado, necessidade pedagógica) | **N** |
| Ver resposta de outro após liberação | A (conforme escopo) | S | P apenas se liberação abranger sua equipe/participante | A/P conforme atribuição | P, somente se explicitamente autorizado |
| Avaliar e comentar submissão | N por padrão | S | N | A (submissões designadas) | N |
| Devolver/reabrir atividade | N por padrão | S | N | A somente se delegado | N |
| Liberar avaliação/resultado | N por padrão | S (responsável do exercício) | N | N por padrão; pode ser delegado somente por decisão | N |
| Consultar histórico didático | A (metadados; conteúdo condicionado) | S no exercício | S apenas próprio/escopo liberado | A | P |
| Consultar auditoria técnica global | A (administrativo, dados mínimos) | A | N | N | N |
| Administrar usuários/contas | S (capacidade administrativa) | N por padrão | N | N | N |

**Proteção central:** até a liberação, a resposta de um aluno/equipe não é retornada a outro aluno em nenhuma rota, consulta, relatório, exportação ou cache. Instrutor e avaliador designado podem ter acesso para avaliação conforme atribuição. Acesso administrativo a conteúdo acadêmico fica negado por padrão; suporte excepcional precisa concessão temporária, justificativa e trilha, a aprovar.

## Regras de privacidade propostas

- Negar por padrão; não usar nome do papel isoladamente como autorização para todo exercício.
- Compartilhar apenas o mínimo necessário por exercício/equipe.
- Separar dados de autoria, conteúdo da submissão e dados agregados do relatório.
- Registrar consulta privilegiada, avaliação, devolução, reabertura e liberação, sujeito a política HIS aprovada.
- Não expor respostas por ids previsíveis, endpoint de lista, exportação, interface de mapa, cache ou histórico antes da autorização.
- Definir retenção, anonimização, retificação e exclusão conforme regras institucionais/legais pendentes.

## Autenticação: sem decisão técnica

Esta matriz não escolhe mecanismo de autenticação. Alternativas a avaliar: contas locais com gestão institucional; identidade federada/SSO; ou mecanismo institucional já existente. A decisão depende de ambiente, políticas de identidade, recuperação de conta, MFA, suporte e privacidade (Q-08/Q-09). No mínimo, deve haver identificador de usuário autenticado para autorização e auditoria, mas o método técnico permanece pendente.

## Perguntas de aprovação

1. Administrador terá acesso a conteúdo de submissões, ou apenas metadados técnicos por padrão?
2. Avaliador pode avaliar, devolver e/ou liberar, ou a liberação sempre é exclusiva do instrutor?
3. Após liberação, quem pode ver respostas de outras equipes: todos, instrutor/avaliador, ou apenas resultados anonimizados?
4. Uma pessoa pode acumular papéis ou equipes no mesmo exercício?
5. Observador acessa só relatórios liberados, ou também dados do cenário durante execução?
6. Qual política institucional de retenção e acesso ao histórico será aplicada?
