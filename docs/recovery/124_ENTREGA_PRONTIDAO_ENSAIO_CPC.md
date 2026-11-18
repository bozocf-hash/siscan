# 124 — Entrega da prontidão das entradas do ensaio CPC

**Execução em 2026-11-17; encerramento em 2026-11-18 · Recorte 4-A implementado e verificado.** Especificação, plano e tarefas aprovados; o responsável também dispensou novas solicitações da skill Spec Driven Development para executar este recorte. O diagnóstico foi implementado sequencialmente, mantendo as verificações técnicas. Contrato: [SPEC-force-confrontation](../../SPEC-force-confrontation.md#recorte-4-a--prontidão-para-o-ensaio-automático-controlado); execução das tarefas em [READY-01–12](../../tasks/force-confrontation/prontidao/todo.md).

## O que o instrutor recebe

No mapa ATLANTICADOR, preparar o par AZUL/VERMELHO e acionar **Prontidão** (nome acessível: **Conferir prontidão do ensaio**). O painel apresenta pendências reais por meio/cenário, recorte não suportado ou **Entradas prontas para ensaio controlado**. **Voltar ao julgamento** restaura o fluxo didático anterior.

O formulário progressivo separa identificação/cenário, fatores de assinatura e, por meio, condição inicial, sensores, logística, geometria e estoques. Não há valores numéricos preenchidos por padrão. Cada grandeza tem unidade; o instrutor precisa declarar explicitamente a origem hipotética. Não é necessário editar JSON. **Ver campo** abre a seção correspondente à pendência. Lista vazia de armamento exige declaração expressa e produz aviso, sem criar capacidade de engajamento.

Hipóteses existem somente na memória da tela. Editá-las invalida a conferência anterior; sair oferece descarte, e cancelar conserva a edição. Aceitar o descarte reinicia os campos mesmo ao reabrir o mesmo par. Resposta atrasada, erro ou perda da autorização não restaura diagnóstico antigo.

## Implementação e fronteiras

- `cpc_readiness.py`: contexto público CPC, escopo SQL de leitura com SAVEPOINT, validação estrita e reconferência da base. Sem importação de fixtures ou chamada ao motor/RNG.
- `POST /api/cpc/trial-readiness`: sessão, exercício aberto, participação de instrutor e CSRF obrigatórios. Payload estrito e limite de 64.000 bytes. Diagnóstico negativo válido retorna 200; erros usam o contrato CPC existente. Operador não recebe os integrantes adversários.
- `static/cpc-readiness.mjs`: controlador e formulário progressivo no painel existente; integração em `cpc-preparation.mjs` e estilos específicos em `map-interface.css`. Sem dependência nova.
- Formatos `siscan-cpc-trial-readiness-01` e `siscan-cpc-trial-hypotheses-01`; hashes canônicos ligam consulta, base e hipóteses. Descritores aceitam hipótese didática expressa ou indisponibilidade. Não há provedor de parâmetros físicos aprovados neste recorte; alegar uma origem aprovada no pedido é recusado.

O único domínio de instância atualmente demonstrado pelo provedor é o **aéreo sintético**, com um integrante utilizável por partido. Configuração maior ou outro domínio recebe não suporte, sem reduzir o grupo ao primeiro integrante. Perda oficial confirmada exclui o meio e nenhuma hipótese o recupera. A demonstração não usa F/A-18 ou Niterói como plataformas físicas validadas.

São conferidos pontos abstratos de vida/dano, disponibilidade, radar/assinatura/probabilidade, estoques identificados individualmente, quantidade inteira, Pk/alcance, combustível kg, taxa kg/min, velocidade kn, raio NM, teto m, reserva/situação de voo, posições locais NM, rumos, duração e semente. Fatores didáticos de assinatura são exatos, sem interpolação. Geometria cartesiana explicitamente hipotética não é conversão das coordenadas do mapa. Estoque defensivo de superfície, seu custo e sua eficácia não foram habilitados: o domínio inteiro permanece não suportado, sem defesa ilimitada implícita.

Mesmo com prontidão positiva, `official_calculation_ready`, `simulation_started` e `official_effects_applied` permanecem **false**. Prontidão das entradas não significa confronto executado, emprego recomendado, vitória prevista ou dados Command aprovados.

## Verificação executada

Na raiz do repositório, com Python local 3.11+ e Node já disponíveis:

```powershell
$pythonCpc = 'C:/Users/bozoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pythonCpc -m unittest discover -s siscan-prototype -p 'check_cpc_*.py'
node --test siscan-prototype/check_cpc_readiness.mjs siscan-prototype/check_cpc_judgment.mjs siscan-prototype/check_cpc_preparation.mjs siscan-prototype/check_map_presentation.mjs siscan-prototype/check_map_groups.mjs
& $pythonCpc siscan-prototype/check_map_units.py
node siscan-prototype/check_map_visuals.mjs
git diff --check
```

**154 testes Python + 46 testes JavaScript passaram (200 testes nomeados distintos), além de dois verificadores por assertions de plotagem/silhuetas.** Dentro desse total, a prontidão possui 11 testes de serviço, 6 HTTP e 8 JS. Reexecuções focadas não aumentam a contagem. As últimas ampliações de cobertura (domínio de superfície recusado, 401/403 e erro de consulta) passaram nos mesmos 11/8 casos focados. Não foram enfraquecidos testes anteriores.

| Critério | Evidência observada |
|---|---|
| AUTO-READY-01 | Testes negam operador antes de ler contexto; HTTP exige sessão/CSRF e recusa AZUL/VERMELHO. Navegador do operador mostra só seu meio, sem CPC. |
| AUTO-READY-02 | Hash antigo recusado; reconferência com base alterada e arquivamento real durante diagnóstico recusam o resultado. |
| AUTO-READY-03 | Consulta sem perfil gera pendências; perfil parcial conserva lacunas; tela inicia com campos vazios. |
| AUTO-READY-04 | Perfil completo sintético passou por serviço, HTTP e formulário; origem não demonstrada é recusada. |
| AUTO-READY-05 | Testes de cardinalidade e domínio; provedores existentes verificam elegibilidade sem escolher representante. |
| AUTO-READY-06 | Perda oficial excluída mesmo com perfil; grupo vazio bloqueia; regressões preservam retirada do mapa. |
| AUTO-READY-07 | Testes de zero, falso, negativos permitidos, unidades, tipo inteiro, NaN e inteiro excessivo. |
| AUTO-READY-08 | Distância incompatível recusada; posições locais derivam distância com aviso, sem leitura geográfica implícita. |
| AUTO-READY-09 | Comparações SQL/registro/RNG, positiva e negativa; exceção libera SAVEPOINT. Base do navegador permaneceu sem efeitos. |
| AUTO-READY-10 | Promises controladas verificam invalidação/resposta atrasada; erro e revogação limpam resultado. Edição e descarte percorridos na tela. |
| AUTO-READY-11 | Painel real em 1280×720 e 320×720, seções recolhíveis, rótulos e foco na conclusão; retorno ao julgamento preservado. Controles nativos suportam teclado; não foi uma auditoria WCAG completa/leitor de tela. |
| AUTO-READY-12 | Testes de serviço/HTTP/JS, regressões e navegador com fixture/base/processo próprios. |

### Percurso real e preservação

Harness final em `http://localhost:61273/`, diretório `%TEMP%/siscan-readiness-20261117-v1`, processo próprio. Instrutor **1**, AZUL **2**, VERMELHO **3**, senha exclusivamente sintética **somente-teste-local**. Login na raiz e mapa em `/atlanticador/editor.html`. A prévia anterior 61272 testou somente o primeiro diagnóstico; a entrega completa foi conferida em 61273.

Percurso observado: preparar par → consulta sem hipóteses → perfil parcial → perfil completo armado → prontidão → edição invalida → nova conferência → cancelamento de saída conserva → descarte aceito retorna ao julgamento → reentrada com formulário vazio → novo perfil completo explicitamente sem armamento, com aviso. Semente zero também foi aceita. Não houve execução de combate em nenhum desses passos.

Após o percurso, leitura SQLite somente leitura confirmou `integrity_check=ok`: propostas, decisões, efeitos, comandos operativos, execuções e saldos de ensaio, comandos de plotagem: **todos zero**. Permaneceram **duas posições, revisão 1**, criadas pela fixture. Sessões de login são escritas legítimas do harness e não efeitos do diagnóstico. Os testes HTTP também comparam dumps antes/depois de consultas positivas/negativas.

Console do mapa sem avisos/erros capturados. Em 320 px, documento com 320 px e painel com largura/scroll de 260 px, sem transbordamento horizontal. Override removido; tamanho natural de 1280×720 reconferido. Captura fora do Git: `C:/Users/bozoc/.codex/visualizations/2026/11/07/01a1b83c-fb2b-7343-90c8-6eecfff70486/siscan-prontidao-cpc-20261117.png`.

Não houve migração/reinício do principal 8787, alteração do DB3K, PDF, ZIP ou frontend extraído original. Os dados/processos anteriores foram preservados. A sincronização documental/de código para `C:/Users/bozoc/Documents/siscan` não atualiza as rotas importadas por um processo Python antigo.

Sincronização concluída: 18 arquivos conferidos previamente contra a base Git `6354781` e comparados byte a byte no destino, com `siscan-prototype/` mapeado para `prototype/`. Links relativos dos documentos conferidos e hashes dos planos anteriores `tasks/plan.md` e `tasks/todo.md` preservados. Commits sequenciais na branch `codex/initial-siscan`, no repositório autorizado `bozocf-hash/siscan`; bancos, originais e captura não integram a versão.

## Continuidade

Permanecem necessários: política de ações/alvos/iniciativa, resolvedor de múltiplos meios, adaptação geográfica explícita, parâmetros/dados validados para cada domínio, contabilização defensiva aplicável, tradução do ensaio em proposta e proveniência durável própria. A decisão oficial continua sempre com o instrutor. O formulário não persiste perfis nem converte seu preenchimento em aprovação de dados técnicos.

Roteiro atualizado em [103](103_ROTEIRO_DO_INSTRUTOR_DISPOSICAO_E_CONFRONTO.md). A entrega fecha a conferência das entradas; a implementação do confronto automático continua uma capacidade seguinte, não anunciada como concluída.
