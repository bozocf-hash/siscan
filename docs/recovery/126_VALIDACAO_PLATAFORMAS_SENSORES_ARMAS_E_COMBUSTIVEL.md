# 126 — Validação por plataforma: sensores, armas, combustível e consumo

**2026-11-18 · Execução em andamento.** O responsável determinou iniciar agora a validação dos sensores/armamentos de cada plataforma e acrescentou níveis de combustível/consumo. A dispensa das solicitações da skill permanece vigente; serão mantidos contrato, testes e evidências. Preservar os planos anteriores de `technical-catalog`, originais, compilação e bases em uso.

## Recorte executável desta validação

1. Reconferir integralmente valores/inventário da compilação com o DB3K original usando a auditoria existente; verificar hashes antes/depois e acesso somente leitura.
2. Reconferir as relações de pertencimento, componentes e domínios relevantes, recalculando correspondência/chaves, sem confiar apenas no status gravado. Separar vínculo confirmado contra a fonte de FK declarada e hipótese estrutural/nominal.
3. Examinar todas as plataformas das seis categorias. Preservar sensores diretos, sensores de suportes/armas, alternativas de loadout, paióis e reservas separados. Componente compartilhado não é instalação única; referência de masquerade não é equipamento instalado.
4. Conferir campos, presença, tipo, faixas internas e sentinelas sem corrigi-los: alcance/probabilidades de origem, quantidade padrão/máxima/multiplicador, combustível/capacidade, propulsores e todas as linhas de regime/faixa/velocidade/consumo. Inversão de limites e valor não usual são ocorrências para avaliação, não prova automática de erro no Command.
5. Gerar sumário, lista por plataforma e fila rastreável de ocorrências, com tabela/rowid/ID e hashes. Usar arquivos derivados locais separados, fora do Git. Não criar aprovação operacional, conversão implícita ou valores novos.

Capacidade de tanque não é saldo atual. Componentes de combustível/propulsão das armas permanecem separados dos diretamente associados à plataforma. Não somar loadouts alternativos, não multiplicar Consumption por NumberOfEngines por presunção e não produzir consumo médio sem perfil temporal.

## Evidências e significado

Reutilizar 58–59 e 65–69 e `technical_units.py`: unidade SQL comprovada, unidade candidata e pendência são diferentes. A documentação primária [Emissions](https://commandlua.github.io/assets/Tables.html#Emissions) informa alcance de sensor da API em nm; ela não prova sozinha todas as colunas SQL. O template local `DB/Templates/Weapon.html` usa rótulos **Air PoH**, **Surface PoH / Reliability**, **Land PoH / Reliability**, **Sub PoH**, com tokens que diferem dos nomes SQL. Portanto, `*PoK` não será convertido em Pk do CPC só pelo nome ou pelo intervalo numérico.

Dados do catálogo são configurações de referência; saldo, avaria, modo ativo/passivo, estoque atual e condições do exercício pertencem à instância/estado. Homologação física exige evidência específica; validação estrutural/literal não equivale a essa homologação. Nenhum sensor gera uma probabilidade universal de detecção por alcance máximo.

## Entregáveis e verificação

- [ ] Ferramenta repetível de auditoria e diagnóstico, sem alterar fornecedores atuais de dados.
- [ ] Testes com fontes sintéticas: ciclo, instalação repetida, órfão, vínculo adulterado, alternativas, zero/NULL, combustível de arma separado, limites e preservação das fontes.
- [ ] Execução integral da versão DB3K_498 disponível, com contagens reais por categoria e pendências por plataforma.
- [ ] Documento de resultados, índice, comandos, sincronização e Git atualizados; dados proprietários fora do repositório.

Saídas previstas: auditoria literal existente, manifesto/estatísticas, componentes/ocorrências JSONL e plataformas JSONL/CSV. Contextos/evidências de unidade compartilhados para evitar copiar explicações extensas em cada linha. Nenhuma mudança de interface, DDL principal ou execução de combate é necessária para esta missão.
