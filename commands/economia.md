---
description: Fechar a etapa atual — suíte, ESTADO/HISTORICO e a linha do /clear (regras completas no CLAUDE.md)
---
Feche a etapa atual conforme a seção 7 do CLAUDE.md global: rode a suíte e registre o número, reescreva
`docs/ESTADO_*.md` (máx. ~40 linhas), acrescente ao `docs/HISTORICO_*.md` e termine com a linha única do
`/clear` (com ou sem `continuar`, conforme haja pendência). Não comece nada novo.

No cabeçalho do ESTADO, atualize sempre `titulo:` (nome do assunto em palavras comuns, fácil de falar)
e `ultimo:` (a última ação conversada e o que falta, numa frase). É isso que aparece na lista de
retomada. Atualize também `atualizado:` com a data de hoje: a lista é ordenada por ela, não pela
data do arquivo. Edição só de forma (cabeçalho, limpeza) não mexe em `atualizado:`. Assunto novo no meio da conversa vai para o ESTADO dele, não para o do kit.
