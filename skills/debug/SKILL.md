---
name: debug
description: Bug, teste falhando ou comportamento inesperado de causa desconhecida (nível 2 da triagem) — achar a causa raiz antes de corrigir.
---
# Debug sistemático enxuto

Regra de ferro: **nenhuma correção antes de conhecer a causa raiz.** Chute que "parece funcionar" esconde o bug.

1. **Reproduzir.** Comando/passo exato que mostra o erro. Leia a mensagem de erro e o stack inteiros — muitas vezes a resposta está lá.
2. **O que mudou?** `git log -5`, `git diff`, deploy/config recente, dados novos.
3. **Isolar.** Siga o dado do sintoma para trás até onde ele fica errado. Compare com um caso que funciona. Em sistema com várias camadas, instrumente a fronteira de cada uma (log curto) antes de supor.
4. **Uma hipótese por vez.** Escreva "acho que X porque Y", teste com a menor mudança possível. Não empilhe correções.
5. **Corrigir com prova.** Primeiro um teste (ou script) que falha pelo motivo certo; depois a correção; rode e veja passar. Rode também a suíte afetada.
6. **Três tentativas falharam?** Pare. Provavelmente o entendimento/arquitetura está errado — traga ao usuário o que foi descartado e a próxima hipótese, em vez de tentar a quarta.

Busca ampla em muitos arquivos: agente `explorador` (Haiku). Resposta final: causa (arquivo:linha), correção, prova (teste antes/depois).
