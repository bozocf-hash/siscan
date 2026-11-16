# 98 — Entrega da preparação dos grupamentos CPC

**Data: 2026-11-16. Estado: recorte implementado e verificado.** Especificação, plano e tarefas receberam aprovações distintas; a lista de 96 foi aprovada por “siga”. Entrega referente a GPREP-01–06, sem ampliar o escopo para execução do confronto ou interface. A concepção gráfica de 97 mantém obrigatoriamente o mapa ATLANTICADOR já definido.

## Código e uso

Novo módulo `siscan-prototype/cpc_group_preparation.py`, com a função pública `preparar_dossie_grupamentos`. Novo verificador `siscan-prototype/check_cpc_group_preparation.py`. Biblioteca padrão e import do contrato existente de `unit_groups`; sem banco, servidor, motor temporal ou exportador.

Exemplo de chamada após obter contexto/vistas de provedores internos confiáveis:

```python
from cpc_group_preparation import preparar_dossie_grupamentos

dossie = preparar_dossie_grupamentos(
    exercise_id=exercise_id,
    autorizar_instrutor=autorizar_instrutor,
    registro=registro,
    inventarios={"AZUL": inventario_azul, "VERMELHO": inventario_vermelho},
    selecao={
        "AZUL": {"group_id": grupo_azul, "expected_revision": revisao_azul},
        "VERMELHO": {"group_id": grupo_vermelho, "expected_revision": revisao_vermelho},
    },
)
```

O autorizador recebe o exercício e deve retornar `True` estrito. Não é papel informado no pedido: a camada confiável deve vinculá-lo à identidade/permissão real. Esta entrega não implementa autenticação HTTP ou permite a um cliente fornecer seu próprio autorizador. Negativa é conferida antes de consultar grupos ou copiar inventários; exceções do provedor abortam sem consulta.

São usados somente métodos públicos do registro: preparação por partido e consulta atual na conferência final. O consumidor não acessa `_state` ou `_lock`. Campos extras na seleção, UUID/revisão inválidos ou visão de inventário malformada geram recusa; as regras existentes de contexto, disponibilidade, domínio, identidade, hash/configuração e grupo ativo são reaproveitadas.

## Saída e preservação

Envelope `siscan-cpc-group-preparation-01`, exercício, partidos em ordem AZUL/VERMELHO, manifesto da composição e snapshots integrais dos integrantes selecionados. Não inclui unidades externas à composição. `preparation_sha256` identifica JSON canônico sem o próprio hash; não usa horário de parede ou UUID aleatório. Mesmas entradas mantêm o hash; nova revisão/snapshot selecionado muda o conteúdo identificado.

Estado global: `status=requires_instructor_review`, `simulation_started=False`, `official_calculation_ready=False`. As classificações individuais permanecem como fornecidas, sem promoção ou rebaixamento silencioso. Recursos desconhecidos ficam desconhecidos. Não há soma de combustível, munições heterogêneas, estado operativo ou poder de combate do grupo.

Entradas e retorno não compartilham estruturas mutáveis. A operação não cria grupos/recibos, não move meios, não avança relógio, não consome recursos ou resolve combate. Arquivamento/revisão observados durante a captura recusam a preparação inteira; falha no segundo partido não publica resultado parcial do primeiro.

## Consistência e erros

O provedor deve entregar uma vista consistente do inventário; copiar um objeto externo sendo alterado não cria uma transação. As consultas finais têm locks separados: detectam divergências observadas de grupo ativo/revisão/hash, sem garantir instantâneo atômico dos dois partidos. Alteração após a conferência pode tornar o dossiê histórico imediatamente. Preparar não reserva disponibilidade futura; futura execução terá de revalidar seus próprios contratos.

`ValueError` cobre formato/conteúdo inválido; `KeyError`, grupo ausente no contexto; `GroupConflict`, revisão ou referências incompatíveis; `PermissionError`, autorização/indisponibilidade de contexto. Não há repetição automática ou conversão de falha em dossiê vazio válido.

## Verificações executadas

Desenvolvimento incremental: 9 testes de fluxo/autorização; 13 após conflitos observados; 21 após cópias/hash. As falhas relevantes foram observadas antes da implementação correspondente. Revisão do código cobriu correção, simplicidade, fronteiras, autorização e custo de cópia; sem alteração dos provedores existentes.

Resultado final: **21 testes novos de preparação e 29 testes do registro passaram**. Descoberta CPC: **102 testes passaram, incluindo os 21 novos e os 81 anteriores**. São 131 testes distintos nesta verificação; não somar novamente os 21 executados isoladamente. `git diff --check` passou. Não foi executada bateria de subsistemas não alterados.

| Critérios | Evidência |
|---|---|
| GP-01–02 | Dois partidos com registro real, somente membros selecionados; combinações naval/aéreo e aéreo/aéreo sem inferência MPNL |
| GP-03 | Autorização estrita; negativa não consulta registro nem copia inventário; erro do autorizador aborta; cada chamada exige nova autorização |
| GP-04–05 | Contexto/revisão inválidos, arquivamento, indisponibilidade e snapshot divergente recusados |
| GP-06–07 | Revisão/arquivamento provocados entre as chamadas são detectados; falha no segundo partido preserva entradas/registro |
| GP-08–09 | Edição de retorno/entrada independente; mapas reordenados mantêm conteúdo/hash; nova revisão/snapshot muda o hash |
| GP-10 | Dados extras, desconhecidos, origem e flags individuais preservados; unidade não participante não entra no hash |
| GP-11–12 | Comparações antes/depois e imports isolados; sem execução/efeitos, status exige revisão do instrutor |

Comandos na raiz do repositório:

```powershell
$pythonCpc = 'C:\Users\bozoc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCpc .\siscan-prototype\check_cpc_group_preparation.py
& $pythonCpc .\siscan-prototype\check_unit_groups.py
& $pythonCpc -m unittest discover -s .\siscan-prototype -p 'check_cpc_*.py'
git diff --check
```

Na pasta canônica `C:\Users\bozoc\Documents\siscan\prototype`, retirar o prefixo `siscan-prototype` dos caminhos. O verificador novo não inicializa banco real, servidor ou navegador.

## Demonstração e Git

Artefato local `prototype/data/cpc_group_preparation_demo_20261116.json`: dois grupamentos sintéticos, dois integrantes selecionados por partido, com snapshots integrais, hash e simulação não iniciada. Gerado por chamada real à função usando fixture controlada; não é execução de combate. Artefato fora do Git, sem dados oficiais. IDs de grupos desta demonstração são fictícios, gerados ao cadastrar a fixture; reconstituir novos grupos não significa reproduzir os mesmos IDs/hash.

Checkpoints de código: `8581616` (preparação autorizada), `caba034` (conflitos observados) e `0c74a09` (conteúdo/hash). Controles e documentação de entrega são registrados posteriormente. Sincronização com a pasta canônica deve conferir SHA-256; não sobrescrever artefato local divergente.

## Continuidade

GPREP-01–06 concluídas para o recorte em memória. Documentos 94–96 registram etapas históricas; gates de especificação, plano e tarefas estão satisfeitos. Não apresentar esta preparação como confronto de grupamentos executável ou como interface já conectada.

Próxima fatia sugerida: especificar seleção/consulta dos grupamentos no **mesmo mapa ATLANTICADOR definido**, conforme 97, resolvendo vínculo de identidades e posições sem expor dados adversários. Reprodução de eventos, execução temporal e adjudicação oficial continuam integrações separadas. Não há persistência, migração, dependência nova ou mudança de banco/originais/estado do exercício.
