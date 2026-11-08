# Protótipo didático SISCAN

Para preparar uma amostra DB3K para revisão, execute `python tools/stage_db3k.py CAMINHO_DA_FONTE CAMINHO_DE_UM_NOVO_BANCO --limit-per-table 20`. A ferramenta não alimenta o exercício: nomes/IDs e códigos originais ficam em um banco separado, com origem e status pendente de revisão. O arquivo de origem é aberto somente para leitura. Confira a ferramenta com `python check_db3k_staging.py`.

Para consultar a amostra na interface, guarde o banco gerado em `data/db3k-review-01.sqlite3`. Um instrutor atribuído ao exercício pode abrir “Catálogo Command / DB3K para revisão” e pesquisar nome/ID ou filtrar a tabela de origem. A consulta retorna no máximo 500 candidatos pendentes, identifica a fonte pelo hash e não oferece promoção ou alocação. Execute `python check_candidate_catalog.py` para conferir autorização e preservação da fonte. O banco de candidatos permanece fora do GitHub.

Para investigar descrições literais dos códigos, na pasta do protótipo execute `python -m tools.inspect_db3k_domains CAMINHO_DB3K CAMINHO_AMOSTRA NOVO_RELATORIO.json`. O relatório distingue correspondência literal, ausência de código/domínio e vínculo sem FK; não aprova semântica nem altera a amostra. Confira com `python check_db3k_domains.py`. Guarde resultados em `data/` para mantê-los fora do GitHub.

A tela consulta as descrições do arquivo local `data/db3k-domains-01.json`. Os hashes da fonte e da amostra devem corresponder aos do relatório; se houver divergência ou formato inválido, a consulta mantém os códigos originais e informa que as descrições não foram carregadas. Cada candidato oferece “Descrições e evidências dos códigos”, sem aprovação ou promoção automática.

Em “Observações da revisão”, o instrutor atribuído pode acrescentar anotações de até 4000 caracteres. O histórico preserva autor, horário UTC, candidato, hash da fonte e exercício; anotações são adicionadas, não substituídas. Elas ficam no banco do protótipo e não alteram o DB3K, a amostra ou a situação pendente dos candidatos. A troca da amostra exige reabrir a consulta antes de registrar anotações para sua fonte.

Primeiro incremento local do fluxo aprovado: cenário fictício, consulta aos meios sintéticos da equipe, composição de grupamento, documento/justificativa, revisão humana e liberação pelo instrutor. Esta pasta é independente; não integra nem altera ATLANTICADOR ou DB3K.

## Limites

- Dados são sintéticos e demonstrativos; não usar informações operacionais, pessoais ou do DB3K.
- Aplicação de demonstração local, vinculada somente a `127.0.0.1`. Não publicar em rede nem usar com alunos antes de especificação e revisão de segurança.
- Sem mapa operacional, cálculo tático, motor de simulação, recomendação, MPNL, relatório PDF autenticado ou integração externa.
- A configuração sem limite de tentativas é apenas a configuração desta instância demonstrativa; o instrutor pode configurá-la por exercício. Prazos podem ficar sem data.
- A rubrica é narrativa, sem notas ou critérios automáticos.

## Execução local

Requer Python 3.11 ou posterior. No PowerShell:

```powershell
$env:SISCAN_INSTRUCTOR_PASSWORD = 'defina-uma-senha-local-forte'
$env:SISCAN_EVALUATOR_PASSWORD = 'defina-outra-senha-local-forte'
$env:SISCAN_STUDENT_PASSWORD = 'defina-uma-senha-local-forte'
python app.py
```

Contas sintéticas: `instrutor`, `avaliador`, `azul-01` a `azul-08`, `vermelho-01` a `vermelho-08`. As senhas de aluno usam a variável comum de demonstração; por isso, não reutilize este mecanismo em ambiente real. O banco local é criado em `data/siscan-demo.sqlite3`.

## Fluxo implementado

1. Instrutor aloca meios sintéticos ao partido Azul ou Vermelho no painel “Alocar meios ao partido”. Aluno autenticado vê os meios recebidos e o fluxograma confirmado; prepara composição e salva rascunho. Todos os alunos atribuídos ao partido acessam o mesmo conjunto disponibilizado.
2. Ao submeter sem justificativa, o sistema apresenta a advertência aprovada e registra a ausência se o aluno confirmar.
3. Avaliador pode comentar, validar ou devolver. Versões anteriores são preservadas.
4. Instrutor acompanha todas as equipes, solicita revisão ou libera o resultado após validação.
5. Instrutor pode alterar título/objetivo do cenário durante o exercício após o aviso obrigatório; cada mudança cria versão e registra autoria, horário e justificativa quando informada.
6. Eventos de autoria, revisão, submissão, liberação e mudança de cenário ficam registrados no backend.
7. Novas submissões notificam instrutores/avaliadores atribuídos; devoluções e liberações notificam o aluno. Cada destinatário registra a leitura das próprias notificações. A leitura não significa concordância nem altera prazos. Notificações são internas, atualizadas ao recarregar o painel, e começam com as ações realizadas após este incremento.

O fluxograma confirmado é exibido como referência de leitura. Este incremento implementa apenas a trilha de composição e revisão documental; não automatiza as decisões “Sim/Não” do diagrama.

O relatório individual oferece impressão e salvamento como PDF pelo navegador, com layout de papel. Essa cópia não possui QR Code nem validação de autenticidade; a emissão autenticável permanece pendente.

As alocações começam vazias. O instrutor deve configurá-las, inclusive em instâncias demonstrativas já existentes. Retirar um meio bloqueia sua seleção em novos salvamentos; documentos anteriores continuam preservados. A auditoria registra os meios adicionados/retirados e notifica os alunos do partido. Este catálogo ainda não usa dados DB3K.

## Verificação da impressão

`python check_workflow.py --print-fixture` cria um relatório HTML isolado em `tmp/print/report.html`, com justificativa longa e dados sintéticos. O arquivo temporário não é versionado. A conferência realizada no Edge gerou quatro páginas A4; as páginas foram renderizadas e inspecionadas, o conteúdo final e o histórico foram recuperados por extração de texto e os controles de impressão ficaram ocultos. Isso verifica a amostra usada; documentos com outros conteúdos continuam sujeitos a revisão de paginação.

A regra vigente é alocação por partido, conforme correção expressa do responsável. Registros antigos por aluno permanecem apenas como histórico e não concedem acesso; as alocações por partido devem ser configuradas pelo instrutor.
