# 75 — Nível mínimo de combustível definido pelo operador

## Decisão expressa e contrato — 2026-11-09

O responsável determinou incluir alerta de nível mínimo antes de aplicar perfis ao estoque e confirmou: operador do próprio partido e instrutor podem definir o limite. Implementar por unidade, em kg, compartilhado entre operadores do partido. Autoridade conferida no backend: operador precisa de alocação ativa da unidade ao próprio partido; instrutor precisa estar atribuído ao exercício. Sem padrão presumido. Ausência de configuração aparece explicitamente; zero é um limite válido, não ausência. Permitir desativação explícita.

Alerta ativo quando saldo <= mínimo. Distinguir acima, no mínimo, abaixo e combustível esgotado. Não bloquear automaticamente consumo ao atingir reserva; insuficiência física continua recusando o intervalo inteiro. Prévia deve informar o instante previsto de atingir o mínimo, além do esgotamento e déficit. Valores de 0 até capacidade cadastrada, precisão máxima de 1 g, entrada em kg; sem números negativos, NaN ou infinito.

Persistir versões imutáveis com autoria e comando idempotente; conferir revisões do limite e da execução para evitar sobrescrita concorrente. Configuração não altera saldo/relógio/snapshot técnico nem a taxa de consumo. Mantém-se por identidade da unidade nas continuações. É parâmetro de alerta, não alteração da configuração física sujeita ao fluxo didático APR-05.

Leitura do alerta somente no escopo permitido. Históricos não devem apresentar o limite atual como se fosse vigente no passado. Registrar o limite aplicado no resultado de cada novo consumo e eventos de cruzamento na mesma transação. Repetição de comando não cria novo débito nem evento. Na alteração de limite, informar imediatamente se o saldo atual já está no mínimo/abaixo. Alerta persistente na interface; não pressupor SMS, e-mail, som ou monitoramento fora do aplicativo.

## Implementação entregue

No protótipo, “operador” corresponde ao aluno atribuído ao partido, com alocação ativa do meio. Não cria papel administrativo novo. A permissão para ajustar esse alerta não autoriza mudar equipamentos, taxas, inventário ou configurações físicas.

`fuel_limits.py` concentra autorização, validação, versões e avaliação do limite. `engine_fuel_limits` registra unidade, execução em que foi configurado, versão, mínimo em gramas ou null, autor, horário, comando e conteúdo original. Versões são protegidas contra atualização/exclusão; último registro da unidade determina o limite vigente, inclusive após continuação da execução. O mínimo não é copiado para dentro da configuração técnica.

POST `/api/engine-fuel-limit` exige `command_id`, `run_id`, `unit_id`, `expected_revision`, `expected_limit_revision` e `minimum_kg`. Este último é string decimal sem expoente, até três casas, ou null para desativar explicitamente. Sessão, origem e CSRF são exigidos. Revisão antiga de execução/limite ou chave reutilizada com conteúdo diferente gera 409; acesso indevido, 403; valor inválido ou acima da capacidade, 400. Repetição idêntica informa a versão já salva sem criar registro/evento adicional. O cliente consulta novamente o estado após o sucesso.

`BEGIN IMMEDIATE` serializa alteração de limite e consumo. `engine_runtime.py` devolve `minimum_alert` para estados correntes visíveis. Histórico devolve null nesse campo: limite vigente hoje não é aplicado retrospectivamente. Cada novo comando de consumo preserva o limite/status utilizado no resultado imutável. Cruzamento de acima para igual/abaixo produz `engine.fuel_minimum_reached`, com unidade, execução, comando, antes/depois e limite/versionamento. Permanecer abaixo não repete o evento a cada avanço. Esgotamento gera `engine.fuel_exhausted` separadamente, inclusive sem mínimo configurado. Configurar um mínimo acima do saldo atual gera alerta imediato e auditoria `engine.fuel_limit_changed`; não representa débito de combustível.

Saldo, relógio, ledger, resultado e eventos de cruzamento pertencem à mesma transação; falha em qualquer gravação reverte tudo. O alerta não autoriza saldo negativo ou consumo sem combustível. Não há confirmação adicional para consumir a reserva: esta versão implementa alerta informativo, sem nova regra de bloqueio operacional.

`static/fuel-limits.js` permite salvar/desativar o alerta por meio no painel de execução. Mostra saldo conferido, mínimo, status e versão. Atualiza os avisos a cada 10 s enquanto a aba/painel estão visíveis, sem reescrever um formulário que o operador está editando. Se o meio deixar de estar disponível, seu cartão é ocultado na próxima conferência. Falha de consulta identifica que o último estado pode estar desatualizado; não equivale a normalização do saldo. O operador deve atualizar o estado antes de salvar se outro comando modificou a revisão.

`engine_profiles.py` usa o limite vigente na prévia, fixa valor/versão no manifesto e calcula quando será atingido; a curva tem linha tracejada de mínimo, com texto equivalente. O plano continua sem débito. Prévia não reserva saldo nem congela a política para uma futura execução. A aplicação transacional de perfis precisará conferir também a versão do limite utilizado.

## Verificação — 2026-11-09

- Passaram os 19 scripts Python. `check_fuel_limits.py` cobre operador sem alocação, compartilhamento entre colegas, privacidade adversária, igualdade e valores abaixo do mínimo, ausência/configuração zero/desativação, valor acima da capacidade, precisão inválida, NaN/infinito, revisão antiga e repetição idempotente.
- Falha injetada na auditoria de configuração não deixa versão parcial. Falha no registro do cruzamento reverte saldo, relógio, histórico e eventos. Comando repetido não duplica débito nem alerta. Esgotamento com mínimo zero é distinto de ausência de limite.
- Testes de continuidade foram atualizados para distinguir atributos históricos preservados do novo campo de política corrente: históricos têm `minimum_alert=null`, sem remover verificações dos saldos/snapshots anteriores.
- Edge/Playwright em cópia isolada: aluno azul define 500 kg, colega lê o mesmo estado, vermelho recebe 403 ao tentar alterar, requisição sem CSRF é recusada. Prévia com saldo-base 510 kg indica atingir mínimo em 12,5 min no plano padrão e desenha a linha tracejada. Instrutor avança 5 min: aluno recebe “mínimo atingido” a 500 kg pela atualização periódica. Mais 1 min: “abaixo do mínimo” a 498 kg. Alteração para 600 kg alerta imediatamente; desativação é explícita. Tela de 390 px sem transbordamento e sem exceção JavaScript.
- Na instância local, os controles foram conferidos sem impor limite a nenhuma unidade nem alterar alocações. Os ensaios de 500/600 kg e seus débitos ocorreram somente na cópia isolada. Criada continuação por atualização do algoritmo, com motivo registrado, conservando 45 min e 510 kg por unidade. Atual: `f9a6b9fd-0366-44ba-b40c-a2e9e239a8d4`, revisão zero de comandos desta sucessora. Nenhum consumo adicional foi aplicado na entrega local.
- Backup consistente anterior: `prototype/data/siscan-before-fuel-limits-16.sqlite3`. Comparação EXCEPT: todas as linhas das 23 tabelas anteriores conferidas foram preservadas, excluindo sessões transitórias. Inserções previstas: uma execução, dois estados, dois snapshots, uma relação de continuidade e um evento. Nova tabela de limites vazia, aguardando escolha do operador. Sem mudança de assets, cenário, alocações ou movimentos de combustível anteriores.
- `integrity_check=ok`, zero violações FK. SHA-256 de DB3K original, compilação 06 e recursos 09 permanece igual ao registrado em 74. Nenhum dado Command foi modificado ou promovido.
- Recibo local `prototype/data/fuel-limits-receipt-16.json`, SHA-256 `90f32bb3f93812ff6991b222911507b3d3e5a237d13888855d16dc91b658e007`. Manifesto da continuação `ccd62b1ff1463aae85ef6bfe8c5641235479d30a55058e7c9ba5120235b02681`. Recibo e bancos não são publicados no GitHub.

## Continuidade e limites

O requisito solicitado foi incluído antes do débito por perfil. A próxima fatia continua sendo fixar o contrato de regimes e aplicar perfis em transação idempotente, incorporando limite/versão e eventos de cruzamento. Unidades físicas e curvas Command ainda exigem comprovação e aprovação. Uma futura mudança da capacidade/configuração física deverá revalidar a compatibilidade do limite; esta entrega não implementa tais mudanças.

Não há notificação externa, alarme sonoro ou monitoramento com o aplicativo fechado. O alerta atualiza após um comando local ou pela conferência periódica visível; não é garantia de entrega em tempo real fora da interface.
