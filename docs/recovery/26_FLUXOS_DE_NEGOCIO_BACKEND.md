# 26 — Fluxos de negócio do backend

Descrição estática de sequências implementadas no ATLANTICADOR 2.0.0. Estados e permissões são aqueles expressos no pacote e não são decisões do SISCAN.

## 1. Inicialização e requisição

`main()` interpreta host/porta, diretório de dados, sincronização e modos opcionais; inicializa configuração de fontes, `Auth`, `SourceStore` e `Situation`; agenda atualização de fontes e verificação periódica de efeitos; por fim inicia `ThreadingHTTPServer` (`serve.py:411-452`). **Nada disso foi executado nesta missão.** Requisições passam pelo handler, autenticação, controles transversais e despacho para métodos do serviço (`serve.py:110-408`).

## 2. Ingresso, login e sessão

1. Usuário escolhe partido pelo ingresso; recebe cookie temporário de 30 segundos (`serve.py:304-317`).
2. Identificação valida usuário/sequência e controles de ingresso.
3. Login verifica credenciais, bloqueios e tentativa; sessão é mantida em memória e enviada por cookie `HttpOnly`/`SameSite=Strict` (e `Secure` opcional) (`auth.py:81-162`).
4. Perfis de partido podem exigir troca da senha; a troca persiste em SQLite após migração ou fallback JSON e invalida sessões concorrentes (`auth.py:167-227`).
5. Logout remove sessão e registra evento. A auditoria de acesso não armazena senha, cookie ou corpo de requisição (`access_audit.py:1-40`).

## 3. Fontes cartográficas e situação oficial

`SourceStore` obtém/valida arquivos KMZ e mantém cache/situação das fontes. Validação examina limites do arquivo compactado e XML/KML (`sources.py:21-86`). A consulta `/api/sources` filtra fontes por perfil. O fechamento manual exige baselines das fontes, comparação com versões esperadas e atualização da situação; publica snapshots/current e registro de publicação para consulta (`situation.py:136-187`). Há modo estruturado opcional para exportação por deltas; o transporte padrão inclui KMZ. A sincronização/configuração efetivas dependem de ambiente não examinado.

## 4. Efeito oficial

1. Adjunto/chefe de célula cria rascunho; edição pode ser reservada por token com expiração de 60 segundos (`effect_workflow.py:63-88,149-162`).
2. Alterações submetem revisão esperada e validações de texto, gatilho, operações, elementos, geometria e revisões atuais (`effect_workflow.py:164-256`).
3. Envio requer situação fechada. Chefia da célula e DIREx participam da cadeia de aprovação, com aprovadores distintos; a direção tem decisão final conforme estado (`effect_workflow.py:276-350`).
4. Uma segunda aprovação pode aplicar imediatamente ou programar `effective_from`; aplicação atualiza elementos, histórico público, estado do efeito e exportação (`effect_workflow.py:258-275,340-368`).
5. O verificador periódico aplica efeitos vencidos; divergência ou falha gera status de conflito, não uma aplicação silenciosa (`effect_workflow.py:352-368`).
6. Poder administrativo especial permite efetivar/anular com fundamento, sob regras específicas. Essa exceção é explicitamente privilegiada.

## 5. Propostas dos partidos

Proposta nasce como rascunho no fluxo de efeito. O partido só pode alterar/empregar meios da própria origem; adição de contato inimigo tem restrições e confirmação. Seleciona destinatários agrupados por célula, passa por aprovação interna (com regras específicas para TO/FTC e comandos menores) e chega à DIREx como blocos de tipo adição/movimento/dano/condição (`party_proposals.py:8-20,58-147`). A DIREx recebe blocos e pode acolher/rejeitar por categoria no restante do módulo. A proposta não aplica diretamente o mapa; eventual adoção vira fluxo de efeito. Não inferir equivalência com trâmite SISCAN.

## 6. Confronto e arbitragem humana

Movimento e Manobra cria confronto após situação oficial fechada e seleciona feições pontuais dos dois partidos. Unidade guarda revisão esperada, fonte, posição, estado e confirmações de identidade/posição. O registro aceita iniciativa, descrição, operações e simulação armazenada como dados auxiliares; mudanças de contexto invalidam respostas/revisões (`confrontations.py:100-153,197-242`). Células enviam pareceres por domínio, inclusive formulário/valores e bypass justificado; alterações invalidam o aceite (`confrontations.py:302-364`). Para envio exige base fechada, dois lados, identificação e respostas de todas as células, além de resultado que efetivamente altere a situação. Aprovação é sequencial; na efetivação o resultado validado é aplicado como efeito (`confrontations.py:378-486`). Código declara que o registro não implementa simulação nem aconselhamento tático automático (`confrontations.py:1`).

## 7. Consulta de eventos legados

Há modelos internos de evento/histórico e consulta filtrada. A escrita HTTP legada `/api/control/events*` foi desativada com 410 (`serve.py:401`). Logo, não se deve documentar `Situation.propose/decision` como rota de escrita operacional deste pacote.

## 8. Rastreabilidade e possíveis referências SISCAN

Revisão otimista via `expected_revision`, histórico/auditoria, etapas de aprovação e publicação versionada podem servir como referências conceituais para processos que precisem de rastreabilidade. Nomenclaturas, células, estados, papéis, limiares, procedimentos e formato cartográfico são particulares e precisam de avaliação. A comparação componente por componente está em [28](28_MATRIZ_REUTILIZACAO_BACKEND_SISCAN.md).
