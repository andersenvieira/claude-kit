# settings.json — regras de mesclagem

Este arquivo não é um `settings.json` pronto para copiar. É a instrução de como misturar o kit no
`settings.json` que já existe em `~/.claude/` (ou criar um novo, se não existir nenhum), sem apagar
nada que já estava lá e sem nenhum segredo/token entrando no arquivo.

1. **Ler o `settings.json` atual primeiro.** Se não existir, criar um novo só com o que o kit precisa.
2. **`permissions.deny`**: unir listas — manter cada entrada já existente e acrescentar só as que
   faltarem do kit (ex.: `Bash(sudo rm:*)`, `Bash(mkfs:*)`, `Bash(dd:*)`, `Bash(*migrate:fresh*)`,
   `Bash(*migrate:refresh*)`, `Bash(*db:wipe*)`, bloqueio de leitura de chave SSH). Nunca remover uma
   entrada de `deny` que já estava lá. Sem duplicar.
3. **`permissions.defaultMode: bypassPermissions`**: só ligar com o ok explícito do usuário — é a
   trocar "menos interrupção" por "menos rede de segurança". Se o usuário não confirmar, deixar no
   modo padrão do Claude Code.
4. **`hooks`**: para cada hook do kit (aviso-risco, fiscal-economia, titulo-conversa, comando-ditado),
   verificar se o `settings.json` atual já tem um hook com esse nome/arquivo.
   - Se não tem: perguntar o nome do hook e o que ele faz, esperar o ok, só então acrescentar o bloco
     (sem remover os hooks que já existiam nos mesmos eventos — acrescentar à lista, não substituir).
   - Se já tem um hook com o mesmo nome mas conteúdo diferente: mostrar a diferença e perguntar antes
     de sobrescrever.
   - Nunca apagar hook que já existia e não é do kit.
   - Comando do hook, conforme o Python que respondeu no LEIA-PRIMEIRO (passo 6):
     - Linux/macOS: `python3 ~/.claude/hooks/<nome>.py`
     - Windows: `py "%USERPROFILE%\.claude\hooks\<nome>.py"` (ou `python` no lugar de `py`, se só
       `python --version` funcionou).
   - Eventos: aviso-risco = `PreToolUse` (matcher `Bash`); fiscal-economia = `SessionStart` e
     `UserPromptSubmit`; titulo-conversa e comando-ditado = `UserPromptSubmit`.
5. **`env` e outras chaves de nível raiz** (`model`, etc.): preservar o que já existe; só acrescentar
   chave nova se o usuário pedir.
6. **Nunca escrever segredo** neste arquivo nem em exemplo dele (token, senha, chave, IP real). Se
   algo do ambiente do usuário tiver isso, deixa de fora do kit público e vira nota em pasta privada.
7. Depois de mesclar, mostrar o diff final ao usuário antes de salvar, se a mudança não for trivial.
