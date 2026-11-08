# 33 — Matriz de avaliação de reutilização do frontend

Classificações para discussão, sem autorização para copiar, alterar ou integrar código. Evidências vêm do ZIP e documentos 29–32.

| Componente | Classe | Evidência/razão | Verificações necessárias |
|---|---|---|---|
| Visualizador Leaflet (`viewer.mjs`, `renderer.mjs`) | **Candidato à reutilização com adaptação** | Fontes, seleção, camadas e renderização são separáveis em módulos parcialmente distintos. | Licença e versão; dados; acessibilidade; tiles; interfaces SISCAN e testes. |
| Editor de cena (`app.mjs`) | **Reavaliar** | Editor local rico, com armazenamento e workflow próprios. | Separar modelo neutro de rascunho e semântica ATLANTICADOR; decidir se SISCAN precisa editor ou só viewer. |
| Camadas/árvore (`scene.mjs`, `layer-tree.mjs`) | **Candidato à reutilização com adaptação** | Nós, grupos, visibilidade e ordenação de apresentação. | Compatibilidade com GEO/SCN, permissões e ciclo de vida de dados. |
| Geometria (`geometry.mjs`, `render-geometry.mjs`) | **Candidato à reutilização com adaptação** | Operações espaciais e otimização visual. | Testes geométricos, unidades, precisão, casos extremos e dependências. |
| Conversão WGS84/UTM (`utm.mjs`) | **Reavaliar** | Implementação própria e zonas/hemisférios com limites explícitos. | Comparar com biblioteca/geodésia adotada, datum, casos extremos e precisão. |
| Movimentação e edição de feições | **Reavaliar** | Há movimento no modelo local e workflow efetivo separado. | Definir semântica GEO/SCN/NAV e garantir não confundir rascunho com alteração oficial. |
| Calunga (`vendor/calunga`, generator) | **Não reutilizar neste momento** | Origem externa declarada; sem licença única confirmada; bundle adaptado e notices diversos. | Parecer jurídico, notices, titularidade, licença e conformidade simbólica. |
| Símbolos genéricos SVG (`symbols.mjs`, `assets.mjs`) | **Candidato à reutilização com adaptação** | Separação parcial de geração/apresentação. | Auditar assets, direitos, semântica e requisitos do módulo SYM. |
| Importação KML/KMZ/GeoJSON | **Reavaliar** | Leitores de formatos e worker locais; limites não testados. | Segurança de arquivo, CRS, tamanhos, perda de atributos e teste de interoperabilidade. |
| Exportação PNG/KML/GeoTIFF/CSV | **Reavaliar** | Exportadores presentes; tiles/canvas e metadados podem afetar resultado. | Precisão, georreferenciamento, acessibilidade, licença e necessidade real. |
| UI comum (feedback, docks, botões, tutorial) | **Referência conceitual** | Padrões reutilizáveis de interação são distinguíveis de regras de domínio. | Acessibilidade, design system e independência de IDs/DOM atuais. |
| Módulos de efeitos | **Isolar** | Regras e endpoints específicos de efeitos ATLANTICADOR. | Não portar vocabulário/regra; considerar apenas padrões aprovados de interação. |
| Fluxos/módulos Confronto e modelos auxiliares | **Não reutilizar neste momento** | Específicos de arbitragem do ATLANTICADOR; não equivalem a SIM/PRC SISCAN. | Revisão de requisitos SISCAN em missão futura autorizada. |
| Módulos de cenário e workflow local | **Reavaliar** | Cena de trabalho, comparação e proposta com convenções próprias. | Confrontar com entidades e regras SCN/FOR/SIM aprovadas. |
| Chamadas API distribuídas por tela | **Isolar** | Não há cliente tipado/contrato central; endpoints acoplados ao backend local. | Definir interfaces de frontend SISCAN sem expor banco ou APIs internas. |
| Integração Leaflet com backend de situação | **Reavaliar** | Dados oficiais e previews dependem de formato/contratos ATLANTICADOR. | Projetar API SISCAN e camada adaptadora cartográfica. |

## Leitura da matriz

**Referência conceitual** pode inspirar organização/interação, não copiar implementação. **Candidato** requer avaliação de adaptação. **Reavaliar** depende de requisitos/evidência adicionais. **Isolar** mantém regra/dado ATLANTICADOR fora da solução SISCAN. **Não reutilizar neste momento** significa que não há justificativa/aprovação suficiente nesta fase.
