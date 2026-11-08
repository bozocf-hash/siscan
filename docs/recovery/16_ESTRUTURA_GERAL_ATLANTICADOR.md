# 16 — Estrutura geral do ATLANTICADOR

## Fonte e identificação

**CONFIRMADO:** fonte disponível em `C:\Users\bozoc\Documents\siscan\atlanticador-main (1).zip`. O ZIP contém o diretório de projeto `atlanticador-main/`, `VERSION` e `package.json` declaram `2.0.0`. O arquivo tem 541 entradas no ZIP: 520 arquivos e 21 entradas de diretório. Não há checkout Git/commit verificável no artefato. O conteúdo abaixo foi lido diretamente do arquivo compactado; não foi extraído, executado ou alterado.

## Mapa hierárquico

```text
atlanticador-main/
├── AGENTS.md, README.md, LICENSE, VERSION, package.json, .gitignore
├── start-atlanticador.cmd          inicialização declarada para Windows
├── serve.py, manage.py             servidor HTTP e comandos administrativos
├── auth.py, profiles.py            sessão, credenciais e perfis
├── profile_store.py                leitura do diretório de contas no SQLite
├── access_audit.py, access_blocks.py
├── situation.py                    estado oficial, eventos e transações
├── sources.py                      ingestão/sincronização de fontes KMZ
├── structured_map.py                transporte estruturado de mapa (opcional)
├── official_kmz.py                 leitura e transformação de snapshots KMZ
├── effect_workflow.py, effect_kmz.py, effect_annul.py
├── confrontations.py               fluxo de confrontos e arbitragem
├── party_proposals.py, unit_conditions.py, record_queries.py
├── map_templates.py, export_deltas.py
├── calunga.py, function_roles.py
├── config/
│   └── sources.example.json        exemplo de fontes Azul/Vermelho/DIREx
├── frontend/                       328 arquivos
│   ├── index.html, login.html, azul.html, vermelho.html, tutores.html
│   ├── viewer.html                 visualizador operacional
│   ├── editor.html                 editor cartográfico local
│   ├── direx.html
│   ├── src/                        73 módulos/arquivos de interface
│   ├── assets/                     login, tutoriais e ícones/estados
│   └── vendor/                     Leaflet e bibliotecas distribuídas localmente
├── docs/                           50 arquivos de documentação/artefatos
│   └── integration-structured-v2/  evidências e registros JSON de integração
├── tests/                           90 arquivos de teste/probes (não executados)
├── scripts/                         18 scripts administrativos/manutenção
└── tools/
    └── deploy_structured.py         ferramenta de implantação específica
```

Os números acima são arquivos por diretório no pacote. O diretório `frontend/src/` contém código e CSS; assets e vendor estão contados separadamente dentro de `frontend/`. O mapa é estrutural e não representa ordem de carregamento ou dependência.

## Arquivos centrais

| Caminho no ZIP | Responsabilidade observada | Estado da evidência |
|---|---|---|
| `VERSION`, `package.json` | Identificam versão `2.0.0`; npm declara testes Node e engine Node `>=20` | **CONFIRMADO** no texto dos arquivos |
| `start-atlanticador.cmd` | Chama `py -3.12 serve.py` no diretório do pacote | **IDENTIFICADO**; não executado |
| `serve.py` | `Handler` HTTP, rotas JSON, arquivos estáticos e montagem de serviços | **CONFIRMADO** por leitura estática |
| `situation.py` | Estado oficial e transações SQLite | **CONFIRMADO** por leitura estática |
| `auth.py`, `profiles.py` | Login/sessões, papéis, partido e fontes permitidas | **CONFIRMADO** por leitura estática |
| `sources.py`, `config/sources.example.json` | Leitura/sincronização de KMZ e definição-exemplo de três fontes | **CONFIRMADO**; configuração de produção não está no ZIP |
| `frontend/viewer.html`, `src/viewer.mjs` | UI cartográfica operacional | **IDENTIFICADO**; não iniciado nesta auditoria |
| `frontend/editor.html`, `src/app.mjs` | Editor local de geometria/camadas | **IDENTIFICADO**; não iniciado nesta auditoria |
| `docs/` | Especificações, escopo, dependências, segurança, modos, integração e validações | **CONFIRMADO**; documentos têm datas/escopos diferentes |
| `tests/` | 90 arquivos de testes e verificações automatizadas | Existência **CONFIRMADA**; execução não autorizada e não realizada |

## Linguagens, distribuição e dependências

Backend está em Python, usando em `serve.py` a biblioteca padrão `http.server`, SQLite e módulos internos. Frontend é HTML/CSS/JavaScript com ES Modules, sem framework ou bundler declarado no `package.json`. Bibliotecas vendorizadas documentadas em `docs/DEPENDENCIAS.md`: Leaflet 1.9.4, leaflet-rotate 0.2.8, polygon-clipping 0.15.7, fflate 0.8.2, html-to-image 1.11.13 e jsPDF 2.5.2. A interface carrega as cópias locais; mosaicos/cartografia base podem depender de fontes externas.

`package.json` declara `npm test` (`node --test tests/*.test.mjs`) e `npm run test:browser`, além de Node >=20. Há também testes Python e ferramentas sob `tests/`; essa presença não comprova aprovação atual.

## Limites

O ZIP é fotografia estática versionada como 2.0.0, sem Git. O diretório operacional `data/`, arquivos privados, configuração real de fontes, banco em produção, contas, logs, deployment e serviço ativo não foram inspecionados como estado de produção. A listagem do pacote não confirma comportamento em execução nem compatibilidade com o SISCAN.
