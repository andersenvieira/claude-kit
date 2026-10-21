# CHANGELOG

## v1.3 — 2026-10-21
`bin/mapa.py`: comandos `frentes` (abertos agrupados por projeto), `marcar <ESTADO_X> <status>`
(troca o status no cabeçalho) e `abertura` (bloco curto de retomada, até 1.200 caracteres: prioridade 1
e urgência alta primeiro, depois os mais recentes); status novo `pausado`; `checar` avisa quando há
mais de 5 abertos.
`hooks/fiscal-economia.py`: na pasta genérica o início de sessão mostra só o bloco curto do
`mapa.py abertura`; alerta quando o modelo da sessão troca sem o usuário pedir (no `opusplan`, a troca
Opus↔Sonnet é normal e não alerta); o medidor mostra a família do modelo.
Peso aproximado em tokens: núcleo ~1.919; repositório completo ~22.843 (91.374 caracteres ÷ 4).

## v1.2 — 2026-10-21
`commands/kit-enviar.md`: passo 1 passa a cobrir a máquina sem clone local do kit — clona com
`gh repo clone <conta>/claude-kit` (conta inferida do endereço de onde o kit foi aplicado) antes do
`git pull`; a condição de parada do passo final deixa de ser "sem clone" e passa a ser "sem
`gh`/`git` configurado ou sem permissão de push".
Peso aproximado em tokens: núcleo sempre carregado (`nucleo/CLAUDE.md`) ~1.919 tokens
(7.676 caracteres ÷ 4); repositório completo ~21.627 tokens (86.508 caracteres ÷ 4).

## v1.1 — 2026-10-21
`LEIA-PRIMEIRO.md`: a IA não acrescenta nada à seção "Regras desta máquina" nem a cria quando não
existe; decisões da instalação ficam só no resumo final. (Teste real da T4: a IA registrava "bypass
não ligado" dentro da seção.)

## v1 — 2026-10-21
Primeira versão pública do kit: núcleo (`CLAUDE.md` genérico + preferências para claude.ai), skills
(brainstorm, debug, executar, engenharia-segura, pentest-professor), agentes (explorador,
implementador, mecanico), comandos (economia, kit-enviar), hooks opcionais em Python (aviso-risco,
fiscal-economia, titulo-conversa, comando-ditado) + `bin/mapa.py`, regras de mesclagem de
`settings.json` (`settings.md`), módulo `vps` (inativo até detecção/pedido) e esqueleto do módulo
`raycast` (a completar).
Peso aproximado em tokens: núcleo sempre carregado (`nucleo/CLAUDE.md`) ~1.919 tokens
(7.676 caracteres ÷ 4); repositório completo ~21.361 tokens (85.443 caracteres ÷ 4).
(Corrigido depois: a primeira medição dizia ~37.798 tokens porque contou arquivos fora do repositório.)
Pendência para a tarefa 2: hooks e `bin/mapa.py` ainda são só para Linux/macOS com Python 3 — a
conversão multiplataforma (Windows/`py`, sem shell fixo) é a próxima tarefa do plano.
