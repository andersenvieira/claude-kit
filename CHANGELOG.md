# CHANGELOG

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
(7.676 caracteres ÷ 4); repositório completo ~37.798 tokens (151.193 caracteres ÷ 4).
Pendência para a tarefa 2: hooks e `bin/mapa.py` ainda são só para Linux/macOS com Python 3 — a
conversão multiplataforma (Windows/`py`, sem shell fixo) é a próxima tarefa do plano.
