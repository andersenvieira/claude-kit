# LEIA-PRIMEIRO — manual para a IA aplicar este kit

Você (a IA) está lendo este arquivo porque alguém disse algo como "aplique o kit de <link deste
repositório>". Este arquivo é o manual completo: siga-o na ordem, sem pular etapas, e sem inventar
método diferente do que está escrito aqui.

## 1. Descubra onde você está rodando

- **Claude Code em Linux/macOS**: pasta de configuração é `~/.claude`.
- **Claude Code em Windows**: pasta de configuração é `%USERPROFILE%\.claude`.
- **Claude Code web**: mesma pasta `~/.claude` do ambiente onde a sessão web roda; se o ambiente for
  efêmero, isso também vale ser dito ao usuário (o kit não "fica" depois que o ambiente morre, a
  menos que haja algum volume persistente).
- **Chat do claude.ai (sem Claude Code)**: não há pasta de arquivo nem hooks. Aplicar só o conteúdo
  de `nucleo/preferencias-claude-ai.md`, colado nas Preferências do app/chat. Não tentar criar
  arquivo nenhum.
- **Android (app claude.ai)**: trate como controle remoto de outra sessão — nada a instalar aqui.

Se não tiver certeza de qual ambiente é, pergunte antes de criar qualquer arquivo.

## 2. Regras gerais antes de escrever qualquer coisa

- **Crie cada arquivo com as suas próprias ferramentas de edição (Write/Edit), nunca com um script
  de instalação.** Este kit não tem `.sh`/`.tar.gz` de instalação — é você, a IA, que lê este manual
  e recria os arquivos um a um.
- **Backup do que já existe**: antes de sobrescrever qualquer arquivo que já exista na pasta
  `~/.claude` (ou equivalente), copie o original para `<arquivo>.bak-AAAAMMDD` (data de hoje).
  Nunca sobrescreva sem backup.
- **Nunca toque na seção "Regras desta máquina"** (ou equivalente) que já exista no `CLAUDE.md` do
  usuário. Essa seção é local, não vem deste kit. Se o `CLAUDE.md` atual tiver essa seção, preserve-a
  integralmente ao mesclar o conteúdo de `nucleo/CLAUDE.md`.
- **Bypass de permissão só com ok explícito do usuário.** Ver `settings.md` para as regras de
  mesclagem do `settings.json`.
- **Hook novo ou hook que mudaria de conteúdo: só com ok do usuário, mostrando o nome do hook antes
  de aplicar.** Não instale hook silenciosamente.
- **Regra dos módulos** (`modulos/<nome>/`): se o que o módulo precisa **já existe** na máquina
  (hook, script, configuração), use o que já está lá — não reinstale por cima. Se **não existe**,
  só instale esse módulo quando o usuário pedir explicitamente (ex.: "aplique o kit com vps").
  Nunca instale um módulo "de brinde" junto do núcleo.
- **`aplique a versão vN`**: se o usuário pedir uma versão específica, leia o conteúdo dessa versão
  pela tag/release correspondente no repositório (não a mais nova), e aplique a partir dali.

## 3. Ordem de aplicação

1. Leia `VERSAO` neste repositório — guarde o número.
2. Leia `nucleo/CLAUDE.md` e mescle no `~/.claude/CLAUDE.md` do usuário, preservando a seção
   "Regras desta máquina" existente (regra acima). Se não existir `CLAUDE.md`, crie com o conteúdo
   de `nucleo/CLAUDE.md`.
3. Copie `skills/*` para `~/.claude/skills/` (um subdiretório por skill, mantendo o `SKILL.md` e
   arquivos auxiliares).
4. Copie `agents/*.md` para `~/.claude/agents/`.
5. Copie `commands/*.md` para `~/.claude/commands/`.
6. Se o ambiente tem Python 3.7+ disponível (`python3 --version`, `py --version` ou `python --version`
   funciona e mostra 3.7 ou mais): copie
   `hooks/*.py` para `~/.claude/hooks/` e `bin/mapa.py` para `~/.claude/bin/`, e siga `settings.md`
   para ligar os hooks no `settings.json` (só com ok, mostrando o nome de cada hook). Se não há
   Python, pule os hooks e avise o usuário que essa parte do kit foi pulada por falta de Python.
7. Para cada pasta em `modulos/`: leia o `LEIA.md` dela e decida, pela regra do passo 2, se instala
   agora ou só documenta que existe e fica à espera do pedido do usuário.
8. No fim, **liste para o usuário** o que foi feito: arquivos criados, arquivos com backup, módulos
   aplicados ou pulados, hooks pendentes de ok.
9. **Grave a versão aplicada** em `~/.claude/kit-versao` (um arquivo com só o número da versão).

## 4. Lista exata de arquivos que este kit cria (núcleo, sem módulos)

Ao aplicar o núcleo completo numa máquina nova, os arquivos de destino são:

```
~/.claude/CLAUDE.md
~/.claude/kit-versao
~/.claude/skills/brainstorm/SKILL.md
~/.claude/skills/debug/SKILL.md
~/.claude/skills/engenharia-segura/SKILL.md
~/.claude/skills/executar/SKILL.md
~/.claude/skills/pentest-professor/SKILL.md
~/.claude/skills/pentest-professor/camadas-e-metodologia.md
~/.claude/skills/pentest-professor/laboratorio.md
~/.claude/skills/pentest-professor/relatorio.md
~/.claude/agents/explorador.md
~/.claude/agents/implementador.md
~/.claude/agents/mecanico.md
~/.claude/commands/economia.md
~/.claude/commands/kit-enviar.md
~/.claude/hooks/aviso-risco.py          (se houver Python)
~/.claude/hooks/fiscal-economia.py      (se houver Python)
~/.claude/hooks/titulo-conversa.py      (se houver Python)
~/.claude/hooks/comando-ditado.py       (se houver Python)
~/.claude/bin/mapa.py                   (se houver Python)
```

No chat puro do claude.ai (sem Claude Code), nenhum desses arquivos é criado — só o texto de
`nucleo/preferencias-claude-ai.md` colado nas Preferências.

Módulo `vps` (só quando detectado ou pedido), arquivos adicionais:
```
~/.claude/hooks/sentinela-vps.py
~/.claude/hooks/ai-heartbeat.sh
~/.claude/bin/sessoes.py
```
E a regra do módulo (texto, não arquivo): regras "desta máquina" generalizadas entram na seção já
existente do `CLAUDE.md` local, sem sobrescrever o que já havia.

Módulo `raycast` (só quando detectado ou pedido): nenhum arquivo é criado automaticamente — é
esqueleto a completar; ver `modulos/raycast/LEIA.md`.

## 5. Este arquivo serve de teste

A lista da seção 4 é o critério de aceite usado para conferir se a aplicação do kit numa máquina
nova criou exatamente os arquivos esperados (nem mais, nem menos, fora dos módulos não pedidos).
