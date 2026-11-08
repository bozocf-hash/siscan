# 22 — Diagrama arquitetural do ATLANTICADOR

O diagrama representa componentes identificados estaticamente no ZIP. A caixa SISCAN e as ligações tracejadas são possibilidades conceituais, não integração implementada nem aprovada.

```mermaid
flowchart LR
  subgraph Browser[Cliente navegador]
    Login[Login e ingresso<br/>login.mjs / party-entry.mjs]
    Viewer[Visualizador<br/>viewer.html / viewer.mjs]
    Editor[Editor local<br/>editor.html / app.mjs]
    MapModules[Mapa, camadas, símbolos,<br/>importação/exportação]
    EffectsUI[UI de efeitos e confrontos]
    Viewer --> MapModules
    Viewer --> EffectsUI
  end

  subgraph App[ATLANTICADOR 2.0.0 — processo Python]
    HTTP[ThreadingHTTPServer<br/>serve.py / Handler]
    Auth[Auth + profiles<br/>login, sessão, autorização]
    Source[SourceStore<br/>polling e cache KMZ]
    Situation[Situation<br/>estado, eventos e transações]
    Effects[EffectWorkflow]
    Confront[Confrontations]
    Struct[StructuredMap opcional]
    HTTP --> Auth
    HTTP --> Source
    HTTP --> Situation
    Situation --> Effects
    Situation --> Confront
    Situation --> Struct
  end

  subgraph Data[Diretório data/ — caminho declarado, não inspecionado como produção]
    MainDB[(situation.sqlite3<br/>estado oficial)]
    AccessDB[(access.sqlite3<br/>bloqueios/ingressos)]
    AuditDB[(access-log.sqlite3<br/>log de acesso)]
    Config[sources.json e caches<br/>KMZ / ícones]
    Accounts[accounts.json<br/>fallback quando aplicável]
  end

  KMZ[Fontes remotas de KMZ<br/>Azul / Vermelho / DIREx]
  Tiles[Provedores externos<br/>de tiles cartográficos]
  DB3K[(DB3K CMO<br/>arquivo externo separado)]
  SISCAN[Módulos SISCAN planejados<br/>GEO · SYM · AST · SCN · FOR · DID<br/>SIM · ANA · NAV · LOG · PRC · HIS · MPNL]

  Login -->|HTTP JSON same-origin| HTTP
  Viewer -->|HTTP JSON same-origin| HTTP
  Editor -->|arquivos locais e rotas conforme função| HTTP
  HTTP -->|HTML / CSS / ES Modules| Browser
  Auth --> MainDB
  Auth --> AccessDB
  Auth --> AuditDB
  Auth --> Accounts
  Situation --> MainDB
  Source --> Config
  Source <-->|leitura/sincronização declarada| KMZ
  MapModules <-->|tiles conforme configuração| Tiles
  SISCAN -.->|contrato/API e autorização ainda pendentes| HTTP
  SISCAN -.->|modelo de dados e versionamento ainda pendentes| MainDB
```

**Nota importante:** o diagrama mostra relações de software encontradas ou caminhos explicitamente declarados no código. O fluxo SISCAN está tracejado porque não existe integração identificada no ZIP. DB3K não tem aresta para ATLANTICADOR: não foi localizada conexão direta no código pesquisado. Nenhum serviço, endpoint ou banco foi iniciado nesta missão.
