# 42 — Proposta de primeiro caso de uso demonstrável

**Status:** proposta elaborada antes da decisão APR-01. O caso de referência foi aprovado com ajustes e limites em [49](49_REGISTRO_DECISOES_APR_01_A_APR_20.md); em caso de divergência, 49 prevalece. Os critérios e recortes deste documento que não foram expressamente aprovados continuam propostas. Não há autorização para desenvolvimento.

## Objetivo pedagógico

Permitir que um instrutor prepare e publique um exercício acadêmico simples; participantes atribuídos recebam condições iniciais e submetam uma composição/decisão com justificativa; o instrutor avalie manualmente o processo, registre comentários e libere resultados; o sistema gere um relatório rastreável. A demonstração avalia organização, explicitação de premissas e qualidade da justificativa, não a previsão de resultado de combate nem recomendação de emprego de armamentos.

## Participantes e papéis

| Papel | Escopo proposto para esta demonstração |
|---|---|
| Administrador | Provisiona contas/perfis e exercício; não vê conteúdo didático por padrão sem atribuição explícita. |
| Instrutor | Cria cenário/condições iniciais, atribui participantes, acompanha, avalia e libera resultados. |
| Aluno Azul / Aluno Vermelho | Cada um acessa apenas a equipe/exercício atribuído, salva e submete seu trabalho. Equipe é escopo de acesso, não autorização para acessar respostas adversárias. |
| Avaliador | Acesso somente se designado pelo instrutor; pode comentar/avaliar conforme configuração. Liberação final permanece com instrutor nesta proposta. |
| Observador | Leitura somente do conteúdo explicitamente liberado, sem acesso antecipado a rascunhos/submissões. |

Detalhes de identidade, múltiplos papéis e matriz completa estão em [43](43_MATRIZ_PAPEIS_PERMISSOES_E_PRIVACIDADE.md) e submetidos em [48](48_PAUTA_DECISOES_PARA_APROVACAO.md).

## Fluxo proposto

1. **Preparação:** instrutor cria cenário didático versionado, descreve objetivo, período e premissas e seleciona meios disponíveis de um conjunto cadastrado mínimo.
2. **Revisão e publicação:** instrutor revisa versão congelada, define equipes/participantes e abre o exercício. Após publicação, mudanças no cenário exigem nova versão ou reabertura registrada.
3. **Execução do aluno:** aluno lê instruções, monta/seleciona uma composição autorizada e registra resposta e justificativa. A atividade não altera o estado mestre do catálogo.
4. **Rascunho e submissão:** aluno salva rascunho; submete quando pronto. Submissão fica privada para o aluno, instrutor e avaliador designado; não aparece para pares/adversários.
5. **Avaliação:** instrutor (e avaliador designado, se escolhido) consulta a versão submetida, registra avaliação manual e feedback. Sem cálculo tático automático.
6. **Devolução opcional:** instrutor pode devolver para revisão com motivo; a nova tentativa/versionamento preserva o conteúdo anterior e a relação entre versões.
7. **Liberação:** instrutor libera resultado para o aluno e, se explicitamente configurado, para observadores ou grupos. Respostas de outras equipes permanecem ocultas até liberação específica.
8. **Relatório:** sistema compila exercício, cenário/versão, autoria, entrega, justificativas, critérios/avaliação, comentários e datas, respeitando permissões.

## Funcionalidade mínima proposta

- Preparar um cenário e fixar versão/condições iniciais; usar cadastro pequeno de meios já revisado, sem importação ampla do DB3K.
- Criar exercício, atribuir participantes e equipe, abrir/encerrar submissões e manter visibilidade privada.
- Permitir resposta textual estruturada e justificativa, com gravação de rascunho e submissão.
- Permitir avaliação qualitativa manual por instrutor, comentário e liberação do resultado.
- Exibir status da atividade e gerar relatório simples com proveniência e histórico necessário.
- Manter visualização geográfica apenas como contexto/cartografia aprovada; sem validação espacial operacional até GEO ter fontes/CRS definidos.

## Dados mínimos

Identidade e papel do participante; equipe/escopo; exercício e versão do cenário; objetivo/instruções; condições iniciais e referência da fonte; cadastro dos meios selecionáveis com unidade/configuração identificadas; resposta, justificativa e revisão; timestamps; critérios usados na avaliação, avaliador, comentário e liberação; eventos de auditoria. Fontes, datas de referência e qualidade dos dados devem acompanhar atributos relevantes.

Não requer nesta demonstração: curvas de consumo, cálculo de autonomia, logística MPNL quantitativa, mapa de costa para validação, batimetria, PRC numérico, engine NAV, modelos de combate, recomendação tática ou integração operacional com o ATLANTICADOR.

## Resultados esperados

- Instrutor consegue criar/publicar exercício com versão identificada.
- Aluno atribuído consegue produzir resposta e justificativa sem alterar cadastro mestre.
- Instrutor consegue avaliar, devolver opcionalmente e liberar resultado.
- Relatório distingue entrega, avaliação humana, versão e datas.
- Participante não obtém respostas de outro participante antes de liberação autorizada.

## Critérios objetivos de aceite propostos

Todos são **PROPOSTA**, para aprovação e validação futura; não foram executados:

1. Um cenário publicado identifica de forma inequívoca sua versão e condições iniciais.
2. Participante não atribuído não consegue abrir o exercício; aluno Azul não acessa conteúdo de resposta do Vermelho e vice-versa.
3. Antes de liberação, respostas submetidas são consultáveis apenas pelo autor e pelos avaliadores/instrutor explicitamente atribuídos.
4. Salvar rascunho não muda estado da submissão de outro aluno nem versão do cenário.
5. Submeter grava autor, instante, versão-base e conteúdo; edição após submissão cria revisão/estado rastreável, não apaga silenciosamente a entrega anterior.
6. Instrutor consegue avaliar manualmente com comentário e indicar devolução ou avaliação final; não há nota automática de decisão tática.
7. Liberação é uma ação explícita, atribuída ao instrutor, com instante e escopo de destinatários registrados.
8. Relatório inclui cenário/versão, participantes autorizados, respostas, justificativas, avaliação humana, comentários e histórico de liberação.
9. Informações estimadas ou hipóteses aparecem identificadas como tais; relatório não os apresenta como dado confirmado.

## Fora do escopo inicial

Navegação temporal/reversão; múltiplos exercícios sincronizados; GIS com validação de costa; batimetria; simulação tática; cálculo/otimização de PRC ou armas; logística/MPNL automatizado; importação integral DB3K; catálogo completo de plataformas; simulação de combustível; colaboração em tempo real; compartilhamento antecipado de respostas; integração executável ATLANTICADOR; administração institucional avançada; dashboards sofisticados. Isso é proposta de corte, sujeita à aprovação.

## Decisões necessárias antes de qualquer implementação

Confirmar participantes/perfis, tipo de resposta esperada, se há uma ou duas equipes, prazo, tentativas, avaliador, rubrica, dados/cartografia a exibir, relatório, política de revisão/liberação e critério de privacidade. Esta proposta não fixa uma situação tática nem inventa um cenário operacional.
