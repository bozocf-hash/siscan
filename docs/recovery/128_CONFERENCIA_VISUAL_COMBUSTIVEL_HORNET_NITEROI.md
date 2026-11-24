# 128 — Conferência visual de combustível: Hornet e Niterói

**2026-11-24 · Conferência amostral concluída.** Continuidade autorizada por “siga”, após quatro capturas do Database Viewer DB3K_498a fornecidas pelo responsável. Complementa [127](127_COMPROVACAO_UNIDADES_ESCALAS_E_COMBUSTIVEL.md); não altera as conclusões históricas daquela execução.

## Identidade e associação

Foram consultados 498 e 498a em SQLite somente leitura (`mode=ro`, `query_only=ON`). **32 registros selecionados são iguais nas duas versões e aos payloads da compilação 06**: duas plataformas, cinco associações, três combustíveis, dois propulsores e vinte pontos de desempenho. Não houve comparação integral nova dos bancos.

| Meio | Identidade visual/SQL | Associações conferidas |
|---|---|---|
| Aircraft/882, F/A-18A Hornet [CF-188A], Canadá, 1982, 330 US Gal Tanks | Nome/configuração visíveis; #882 informado pelo responsável, não visível nas capturas. SQL confirma esse ID com os atributos observados. | DataAircraftFuel → Fuel/173; DataAircraftPropulsion → Propulsion/34 |
| Ship/1351, F 40 Niteroi [Vosper Mk10 Mod], Brasil, 2000 | #1351 visível no cabeçalho; segunda captura mantém o mesmo nome selecionado. | DataShipFuel → Fuel/1542 (componente 1) e /1541 (componente 2); DataShipPropulsion → Propulsion/923 |

**Correção:** o Hornet observado é F/A-18A, não F/A-18C. A identificação inicial do chat não deve ser propagada. Aircraft/8 continua sendo outro registro; não atribuir a captura a ele por compartilhar componentes.

## Capacidade e escala

| Fuel ID / tipo | SQL Capacity (498 = 498a = compilação) | Captura | Conclusão delimitada |
|---|---:|---|---|
| 173 / Aviation Fuel, 2001 | 4925 | 4925,0 kg | Unidade kg e correspondência 1:1 comprovadas nesta associação do Hornet. |
| 1541 / Diesel Fuel, 3001 | 480000 | 480,0 tons; “Secondary fuel tank” | Fator SQL/tela = 1000, exato; base em kg corroborada, sem especificação independente do armazenamento. |
| 1542 / Aviation Fuel, 2001 | 26000 | 26,0 tons | Fator 1000; aviação separada da propulsão naval. |

O rótulo literal é **tons**; o fator observado é compatível com toneladas métricas sobre uma base em kg. Não se tratou a palavra inglesa isoladamente como definição universal. Não houve conversão por densidade. Capacidade cadastrada não é saldo de uma instância. “Secondary fuel tank” é rótulo de posição, não prova de reserva de emergência ou prioridade de consumo.

## Hornet: 16 pontos conferidos — Propulsion/34

Conjunto exibido **2x F404-GE-400**. Regimes SQL 1/2/3/4 correspondem neste painel a Loiter/Cruise/Military/Afterburner. Os quatro campos físicos por ponto (limites de altitude, velocidade e taxa) coincidem com as capturas. Rowids 1143–1158.

| Faixa m | Loiter: nós / kg/min | Cruise: nós / kg/min | Military: nós / kg/min | Afterburner: nós / kg/min |
|---|---|---|---|---|
| 0–3657,6 | 350 / 43,39 | 480 / 54,25 | 580 / 95,04 | 650 / 244,03 |
| 3657,6–7315,2 | 350 / 38,42 | 480 / 48,03 | 570 / 84,12 | 700 / 222,62 |
| 7315,2–10972,8 | 350 / 29,30 | 480 / 36,63 | 550 / 64,15 | 800 / 183,00 |
| 10972,8–13716 | 350 / 21,75 | 480 / 27,19 | 520 / 47,60 | 920 / 174,03 |

Mach exibido não foi objeto de comparação SQL. Há fronteiras de altitude compartilhadas; falta definir seleção de intervalo antes do uso automático exatamente no limite.

## Niterói: quatro pontos conferidos — Propulsion/923

Conjunto **4x MTU 16V 956 TB91 Diesels, 2x Rolls-Royce Olympus TM-3B Gas Turbines, CODOG**, exibido como Diesel; máximo 29 nós.

| Throttle SQL / rótulo visual | Nós | kg/min | rowid |
|---|---:|---:|---:|
| 1 / Creep | 5 | 24,45 | 4672 |
| 2 / Cruise | 18 | 27,16 | 4673 |
| 3 / Full | 25 | 102,81 | 4674 |
| 4 / Flank | 29 | 178,46 | 4675 |

Não aplicar nomes dos regimes aéreos ao navio. A taxa é apresentada associada ao conjunto modelado; não multiplicar novamente pela contagem de motores. O `NumberOfEngines=0` naval não deve zerá-la. A tela não demonstra consumo de cada motor, despacho diesel/turbina, prioridade de tanques ou transição entre regimes.

## Condições restantes para o motor

A associação e as curvas discretas estão documentalmente conferidas neste recorte. Isso fornece evidência para perfis específicos, sem ativação automática do motor com dados reais. Faltam saldo atual, capacidade utilizável, configuração/loadout, reserva de retorno, seleção de faixa, eventual interpolação, vínculo operacional tanque–propulsor e autorização para finalidade de uso. Não usar média única, somar combustível de aviação à autonomia propulsiva naval ou generalizar a outros meios. A homologação global permanece pendente.

## Artefatos e verificação

Entrega local: `C:\Users\bozoc\Documents\siscan\prototype\data\command-fuel-evidence-20261124-v1\`:

- Quatro capturas preservadas sem edição: `hornet-performance.png`, `hornet-fuel.png`, `niteroi-identity.png`, `niteroi-performance-fuel.png`.
- `comparison.json`: registros literais, transcrições, correspondências, limitações e hashes das fontes/capturas/script. SHA-256: `48034c174a374c2a6f2ab7e9a183f375b28ba4751da1573e30796176fae9f0b6`.
- `verify_command_fuel_20261124.py`: diagnóstico somente leitura com verificações assertivas. Reexecutar na raiz do repositório, ajustando apenas `out` para pasta nova; criação recusa sobrescrever entrega anterior. Identidade 498a é registrada por hash e igualdade do recorte, sem presumir equivalência pelo nome.

| Fonte | SHA-256 |
|---|---|
| DB3K_498.db3 do SISCAN | `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d` |
| DB3K_498a.db3 instalado | `866f4cded2e03ad350bab5ed67fef16f74da06c849bcbaf886839b273906a7b4` |
| Compilação 06 | `de164e39e08c8723a6ded0c4517fac076576654f2dc34f0e77a36e2143ce6fe9` |

Passaram todas as verificações do diagnóstico: identidade, 32 registros em três representações, vinte pontos contra capturas, três capacidades/escalas, cópias íntegras e hashes das fontes antes/depois. Não se alegam novos 42 scripts de regressão: os 42 de 127 são históricos. Nenhum código operacional, banco, aprovação, estoque, servidor ou plano alterado. Capturas/dados ficam locais; documentação versionada no GitHub.
