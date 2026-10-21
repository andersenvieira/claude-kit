# /kit-enviar

Manda de volta para o repositório público do kit uma melhoria feita na config local
(`~/.claude/CLAUDE.md`, `skills/`, `agents/`, `commands/`, `hooks/`, `bin/`, `settings.md`, módulos).

Passos:

1. **Clone e pull antes de tudo**: procure o clone local do repositório do kit (pasta com `VERSAO`,
   `LEIA-PRIMEIRO.md` e remoto `claude-kit`). Se não houver, clone numa pasta temporária com
   `gh repo clone <conta>/claude-kit` (a conta é a do endereço de onde o kit foi aplicado; na dúvida, perguntar). Depois
   `git pull` — conflito entre máquinas se resolve pelo próprio git, não por esta skill.
2. **Comparar local × repositório**: para cada arquivo que o kit instalou em `~/.claude/` (ou
   equivalente), olhar a versão atual na máquina contra a versão no clone do repositório. Ignorar
   arquivos que o usuário não tocou.
3. **Mostrar o diff** de cada arquivo mudado antes de aplicar qualquer coisa no repositório — o
   usuário decide o que entra.
4. **Grep anti-segredo** no que vai subir: `grep -rniE '/var/www|token|senha|password|secret|chave|ip
   privado'` (ajustar ao conteúdo real) nos arquivos a enviar. Qualquer ocorrência de valor real
   (não regra genérica) para fora do commit antes de seguir.
5. **Subir a `VERSAO`**: incrementar o número.
6. **Escrever a linha do `CHANGELOG.md`** da nova versão: o que mudou + peso aproximado em tokens
   (contar caracteres do conteúdo que o núcleo carrega sempre — `nucleo/CLAUDE.md` — e do total do
   repositório; dividir por 4 para uma estimativa de tokens).
7. **Commit + push** usando `gh` (já logado na máquina) ou `git` direto, mensagem curta dizendo o que
   mudou.
8. Reportar ao usuário: versão nova, arquivos mudados, peso em tokens, link do commit.

Sem `gh`/`git` configurado, ou sem permissão de push no repositório: avisar e parar — não inventar
outro jeito de publicar.
