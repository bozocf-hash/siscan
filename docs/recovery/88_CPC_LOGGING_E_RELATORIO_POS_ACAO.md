# 88 — CPC: logging estruturado e relatório pós-ação

**Data: 2026-11-16. Estado: implementado e verificado.** Pedido expresso: armazenar eventos estruturados, exportar TXT/CSV, incluir estado inicial e balanço final e executar 60 turnos. Complementa [86](86_CPC_TURNOS_COMBUSTIVEL_E_MOVIMENTO.md) e [87](87_REGRA_ESGOTAMENTO_COMBUSTIVEL_POR_DOMINIO.md). Não encerra a integração oficial do CPC ou valida sua eficácia física.

## Código consolidado

- `siscan-prototype/cpc_reporting.py`: `HistoricoCombate`, captura de snapshots, balanço e `exportar_relatorio_pos_acao`.
- `cpc_time.py`: journal da execução e publicação dos eventos junto com o turno; `SimulacaoTemporal.eventos` e método de exportação delegado.
- `cpc_combat.py`: captura dos eventos de detecção/combate e parâmetro CLI `--relatorio`, aceitando um ou mais destinos.
- `check_cpc_reporting.py`: testes do histórico, contabilidade, formatos e preservação de arquivos.

Não foram introduzidos dependências, tabelas ou migrações. O logger usa listas/dicionários e a biblioteca padrão do Python. `print` continua como apresentação opcional no terminal, não como armazenamento dos resultados.

## Registro estruturado

Cada evento do journal tem `execucao_id`, `sequencia`, `minuto`, `tipo`, `nivel`, `origem`, `unidade_id`, `alvo_id`, `acao_id` e `dados`. A sequência é global e crescente na execução. `minuto` indica o fim do intervalo simulado; eventos da mesma fase não representam uma prioridade física por ordem de impressão.

Tipos registrados incluem: início/fim de turno, movimento, consumo de combustível, detecção bem-sucedida ou falha, disparo, consumo de armamento, tentativa de defesa, interceptação, erro, acerto, dano aplicado, destruição proposta, mudança de estado de voo, perda aérea proposta, suspensão de ação e estado final por unidade em cada minuto. A imobilização por combustível é observável no estado/saldo, sem converter o meio em perda.

Detecção registra distância/alcance e, quando houve sorteio, probabilidade efetiva e sorteio. Combate reaproveita os sorteios existentes; logging não acrescenta aleatoriedade. Consumo defensivo é registrado mesmo quando falha; ausência de tentativa não cria débito.

Movimento registra distância percorrida e deslocamento resultante separadamente. Isso evita representar como parada uma ida e volta com saldo líquido de posição próximo de zero. Unidades são explícitas nos nomes de campos: kg, MN, nós e pontos de dano abstratos.

`simulacao.eventos` retorna uma cópia da lista, protegendo a trilha de edição acidental. O gerenciador também mantém eventos locais de chamadas diretas; o relatório completo do loop deve ser obtido pela `SimulacaoTemporal`. Eventos anteriores ao início desse loop não são debitados novamente em seu balanço.

O snapshot inicial é congelado antes do primeiro turno efetivamente publicado, respeitando a configuração feita depois da criação da simulação. Snapshots finais são capturados após cada turno. Erro de configuração ou conflito não publica eventos parciais; as garantias de não publicar tempo/estado/RNG permanecem válidas.

## Formatos

**TXT:** cabeçalho com estado inicial e metadados; linhas JSON por evento; estado final; rodapé “Batalha Encerrada” com sobreviventes, destruições propostas por dano, perdas aéreas propostas por combustível, imobilizações e recursos gastos. O título identifica ensaio não adjudicado.

**CSV:** UTF-8 com BOM, separador `;`, decimais com ponto e um único cabeçalho de colunas. `secao` distingue `cabecalho`, `evento` e `rodape`. As colunas comuns são estáveis; campos escalares observados são expandidos em colunas adicionais para análise. `dados_json` conserva o payload completo e seus tipos, inclusive listas/nulos; colunas adicionais podem variar com os tipos de evento presentes. Há linhas de estado inicial/final por unidade e uma última linha `balanco`.

Metadados incluem schema `cpc-pos-acao-1`, identificador da execução, origem, versão Python, semente declarada, passo de um minuto e hashes SHA-256 dos módulos do algoritmo. A semente é declarada pelo chamador, não inferida do gerador; comparações exigem também as mesmas entradas, comandos e versões.

Campos textuais com prefixo de fórmula são protegidos no CSV; o valor literal permanece no JSON. Valores numéricos negativos continuam numéricos. Dados ausentes não são preenchidos com zero.

## Contabilidade e autoridade

- “Mísseis gastos” soma apenas consumos classificados como `missil_antinavio` ou `missil_ar_ar`, uma vez por débito. Não soma novamente o evento de disparo.
- Estoques `defesa_ponto` são recursos/itens ou pacotes defensivos; não se presume que cada unidade represente um míssil. O rodapé mantém essa contagem separada.
- No relatório do modelo abstrato, HP zerado gera `destruicao_proposta`; isso não transforma o índice operativo de 80/81 em afundamento real ou resultado oficial. Não houve nova aplicação física de avarias por essa classificação do relatório.
- Perda aérea por combustível é categoria separada. A união de IDs evita contar duas vezes uma unidade com mais de uma causa proposta. Indisponíveis iniciais também são identificados.
- Meios navais/terrestres com tanque vazio permanecem sobreviventes se não houver outra causa de perda, e aparecem como imobilizados.

O instrutor continua definindo os efeitos oficiais. Exportar registra um retrato até o minuto indicado; não encerra o exercício nem confirma proposta. É possível exportar dois formatos do mesmo histórico sem alterar estoques/estado ou gerar outro confronto.

## Execução de 60 turnos no terminal

No PowerShell:

```powershell
Set-Location 'C:\Users\bozoc\Documents\siscan\prototype'
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$ensaioId = Get-Date -Format 'yyyyMMdd_HHmmss'
& $pythonCpc cpc_combat.py --turnos 60 --semente 7 --relatorio "data/cpc_$ensaioId.txt" "data/cpc_$ensaioId.csv"
```

O executável foi verificado nos testes e na demonstração. O alias simples `python` aponta para WindowsApps e falhou nesta máquina; por isso a instrução usa o caminho confirmado, sem alterar aliases ou instalar dependências.

São 60 minutos simulados, sem esperar uma hora real. A demonstração consulta somente as identidades F/A-18C e Niterói no catálogo compilado, em modo somente leitura. Seus parâmetros permanecem fictícios: a aeronave perde combustível e tem perda proposta no minuto 3; o relógio registra os minutos seguintes até 60. Isso não é evidência de 60 minutos de engajamento ativo.

Arquivos existentes nunca são sobrescritos. O método usa criação exclusiva; falha de renderização/escrita remove apenas o arquivo novo que criou, sem deixar um relatório parcial com aparência de completo. Formatos diferentes de `.txt`/`.csv` são recusados. O diretório pai pode ser criado automaticamente.

## Evidências

**81 testes passaram:** os 69 anteriores mais 12 de logging/exportação. Incluem execução de 60 turnos, eventos correlacionados, perdas sem duplicação, gastos ofensivos/defensivos separados, snapshot congelado, histórico protegido de edição acidental, CSV com seções/números, preservação de arquivos, proteção de células, remoção de exportação parcial, distinção de distância percorrida e rejeição de extensão indevida.

Execução demonstrativa de 60 turnos gerou TXT e CSV, **314 eventos**, 60 registros `turno_concluido` e balanço coerente: uma Niterói sobrevivente, uma perda aérea proposta por combustível, zero destruições propostas por dano, um míssil gasto e dois pacotes defensivos consumidos. Os formatos pertencem à mesma execução e reproduzem os mesmos dados. Artefatos de demonstração ficam em `prototype/data`, fora do Git.

Nenhum banco, original, mapa ou estado oficial do exercício foi alterado. Histórico permanece em memória até exportação; não há journal durável durante o processo, autenticação/adjudicação do instrutor, assinatura criptográfica do relatório ou calibração dos parâmetros. Hashes de código e replay verificável não equivalem a validade física do modelo. Integração oficial e comparação com evidências independentes continuam pendentes.
