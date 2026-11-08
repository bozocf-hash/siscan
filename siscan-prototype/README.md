# Protótipo didático SISCAN

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

1. Aluno autenticado vê somente meios da própria equipe e o fluxograma confirmado para consulta; prepara composição e salva rascunho.
2. Ao submeter sem justificativa, o sistema apresenta a advertência aprovada e registra a ausência se o aluno confirmar.
3. Avaliador pode comentar, validar ou devolver. Versões anteriores são preservadas.
4. Instrutor acompanha todas as equipes, solicita revisão ou libera o resultado após validação.
5. Instrutor pode alterar título/objetivo do cenário durante o exercício após o aviso obrigatório; cada mudança cria versão e registra autoria, horário e justificativa quando informada.
6. Eventos de autoria, revisão, submissão, liberação e mudança de cenário ficam registrados no backend.
7. Novas submissões notificam instrutores/avaliadores atribuídos; devoluções e liberações notificam o aluno. Cada destinatário registra a leitura das próprias notificações. A leitura não significa concordância nem altera prazos. Notificações são internas, atualizadas ao recarregar o painel, e começam com as ações realizadas após este incremento.

O fluxograma confirmado é exibido como referência de leitura. Este incremento implementa apenas a trilha de composição e revisão documental; não automatiza as decisões “Sim/Não” do diagrama.

O relatório individual oferece impressão e salvamento como PDF pelo navegador, com layout de papel. Essa cópia não possui QR Code nem validação de autenticidade; a emissão autenticável permanece pendente.

## Verificação da impressão

`python check_workflow.py --print-fixture` cria um relatório HTML isolado em `tmp/print/report.html`, com justificativa longa e dados sintéticos. O arquivo temporário não é versionado. A conferência realizada no Edge gerou quatro páginas A4; as páginas foram renderizadas e inspecionadas, o conteúdo final e o histórico foram recuperados por extração de texto e os controles de impressão ficaram ocultos. Isso verifica a amostra usada; documentos com outros conteúdos continuam sujeitos a revisão de paginação.
