# 99 — Especificação dos grupamentos no mapa definido

**Atualização de gate:** especificação aprovada por “siga”; plano proposto em [100](100_PLANO_GRUPAMENTOS_NO_MAPA.md). O conteúdo abaixo registra a preparação histórica da Fase 1, sem implementação da extensão.

**Data: 2026-11-16. Estado: Fase 1 do recorte gráfico proposta para revisão.** Após a entrega 98, o responsável orientou “siga”. A extensão está em [SPEC-unit-registry.md](../../SPEC-unit-registry.md), seção Recorte 2, preservando a primeira entrega e os IDs do mapa de capacidades.

Fluxo proposto: criar, consultar e arquivar grupos no painel lateral do mesmo mapa ATLANTICADOR integrado ao SISCAN; selecionar grupo realça seus integrantes já plotados. Não cria segundo mapa, move meios ou executa confronto. O backend confere sessão/partido, adjudicação, vínculo unit_id/asset_id e snapshot/domínio antes de aceitar a composição.

Inspeção local: `map_units.listing` usa assets.id; `engine_units.list_units` expõe vínculo explícito a unit_id e referências de snapshot/configuração; `app.py` ainda não integra RegistroGrupamentos; `static/atlantic-bridge.mjs` já possui painel, lista/seleção e índice de marcadores reutilizáveis. Não confundir group_name das submissões com grupo versionado. A criação atual de instâncias pelo motor é sintética, não cobre automaticamente todo o catálogo real.

Essas lacunas exigem uma ponte autorizada, não associação por nome ou dado inventado. Meio sem snapshot/domínio demonstrado fica pendente de agrupamento e continua disponível às operações de plotagem já autorizadas. A normalização da configuração sintética será explícita; outras configurações exigem evidência própria.

O registro permanece em memória neste recorte, com aviso visível de perda ao reiniciar. A interface não deve prometer persistência ou reconstruir grupos de submissões/dossiês. Arquivar permite liberar vínculos sem apagar meios ou posições. Persistência e cadastro de instâncias reais não estão incluídos nesta proposta.

Doze critérios GM-01–GM-12 cobrem mapa preservado, identidade, elegibilidade, visibilidade, reenvio, seleção, arquivamento, respostas atrasadas, aviso de reinício, acessibilidade e testes isolados. Não existe validação visual ou código gráfico novo nesta etapa; não foram executados testes de software por ser documentação.

Skills aplicadas: Spec Driven Development, Ponytail, API and Interface Design e Frontend UI Engineering. A skill [spec-driven-development](C:/Users/bozoc/.codex/skills/spec-driven-development/SKILL.md) exige “Stop after writing the spec (CRITICAL)”; por isso a próxima etapa é revisão desta extensão antes do plano. Gates anteriores continuam concluídos.
