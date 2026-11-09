# 58 — Instalação local do CMO e evidências dos templates

## Instalação e identidade da fonte

Foi identificada a instalação em `C:\Program Files (x86)\Matrix Games\Command Modern Operations`. O registro do Windows informa Command: Modern Operations 1.05.1307. Os metadados FileVersion/ProductVersion do executável retornam 1.0.0.0, insuficientes para confirmar o build funcional. O programa não foi iniciado nem suas configurações alteradas nesta inspeção.

O arquivo instalado `DB\DB3K_498.db3` e o arquivo de trabalho `C:\Users\bozoc\Documents\siscan\DB3K_498.db3` apresentaram o mesmo SHA-256: `1b31fc60d799bfb8b7e6be02a24bc4431fa0d1b1ed519a058245ea57d0e4846d`. Isso confirma identidade binária dos dois arquivos examinados, sem equivaler a validação dos atributos.

## Evidência dos templates locais

Foram lidos os arquivos de apresentação em `DB\Templates`. Eles contêm tokens de substituição e rótulos de medidas. Não foi inspecionado o mecanismo que transforma os valores SQL nesses tokens, portanto não se afirma ausência de conversões intermediárias.

| Template | Tokens e rótulos observados | Limite |
|---|---|---|
| Ship.html | Length, Beam, Draft e Height acompanhados de m | Evidência de apresentação; confirmar vínculo ao campo SQL e conversões |
| Aircraft.html | Length, Span e Height acompanhados de m; EmptyWeight e MaxWeight acompanhados de kg | Os nomes de massa diferem de WeightEmpty/WeightMax no SQL; não equiparar sem comprovar o mapeamento |
| Submarine.html | MaxDepth, Length, Beam, Draft e Height acompanhados de m | Não resolve domínio, significado de zero ou condição operacional dos valores |
| GroundUnit.html | MastHeight, Length e Width acompanhados de m | Evidência específica do template terrestre |
| GroundUnit.html | Area acompanhada de m | Rótulo dimensional que requer investigação; não converter para m² nem declarar a unidade SQL como m |
| Ship.html e Submarine.html | Tokens Displacement_Empty, Displacement_Standard e Displacement_Full sem unidade fixa imediatamente após o token | Não inferir unidade de armazenamento a partir do nome; o token pode conter texto formatado |

Os 15 pares tabela/campo de dimensão com tokens homônimos e rótulo m abrangem 300 valores na amostra. Essa contagem descreve cobertura de evidência de apresentação, não aprovação ou validação SQL. Os 580 valores técnicos continuam pendentes.

SHA-256 dos templates examinados:

| Arquivo | SHA-256 |
|---|---|
| Ship.html | b3ca20d803d12e0901ee808742f20800f9b98018b03859b07fa7959f0d81411a |
| Aircraft.html | 75b4da2b57c7fcc781679a1333609bfe6c4c19feb4e2169be36c59df4f0d80d3 |
| Submarine.html | 00cab36de4f97f659c09e177898e4493807bfbcf077dddc0dd10f79e2b2b538f |
| GroundUnit.html | a2c3ca7eb1c7247e618bd5599ff58dab5eeca1a86dd88e29e59e698c5a68cce6 |

## Manual digital adicional

Foi localizado `Manuals\CMO manual EBOOK.pdf`, com 353 páginas e tamanho 8.495.078 bytes. As páginas PDF 1, 11 e 208 forneceram texto por extração direta, com 12, 1.759 e 1.390 caracteres respectivamente. Essas verificações amostrais mostram uma nova fonte digital potencialmente mais útil que o PDF digitalizado usado na recuperação anterior.

Não houve leitura integral ou inspeção visual das 353 páginas deste novo arquivo. A descoberta não substitui retroativamente os limites de OCR/amostragem registrados em 12–15. O manual instalado e o PDF enviado foram preservados.

## Próxima verificação necessária

A identidade binária do banco permite comparar o mesmo DBID com o visualizador desta instalação, registrando campo, unidade exibida e eventual conversão. Ainda é necessário demonstrar a relação entre a coluna SQL e o valor apresentado, especialmente nas massas, deslocamentos e Area. Templates são evidências de apresentação; nenhuma grandeza deve ser promovida automaticamente com base somente neles.
