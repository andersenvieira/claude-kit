# CHANGELOG

## v1.6 — 2026-10-23
`hooks/aviso-risco.py`: passa a BLOQUEAR (`permissionDecision: deny`) só os catastróficos — `sudo` com
`dd/mkfs/shred/wipefs`, `rm` recursivo em `/`, `~`, `/home`, `/etc`, `/var`, `/usr`, `/opt` (flags separadas ou
longas também), `find / -delete`, `chmod -R` aberto na raiz, `migrate:fresh|refresh`, `db:wipe`. Novos avisos:
`rm -r` com flags separadas, `git clean -f`, `find -delete`, `curl | python`. Demais padrões seguem só avisando.
`nucleo/CLAUDE.md`: §2 nível 3 só para funcionalidade nova/mudança de fluxo (na dúvida 2×3, pergunta);
§6 descreve o bloqueio.
Mais bloqueios: `DROP DATABASE`, `TRUNCATE`, `DELETE` sem `WHERE`, `redis flush`, `crontab -r`, `rm -r -f` em
`/var/www`, `/var/lib/mysql`, `~/.ssh`, home e `.git`, `ufw disable|reset`, `iptables -F`, desligar o SSH, `passwd -l`,
`userdel`, `reboot|shutdown|poweroff|halt`, `rclone sync|purge|delete`, `docker system prune -a`, `docker volume rm`,
`compose down -v`, fork bomb, `chmod|chown -R /`, `mv` de diretório de sistema, `git filter-branch`, `git push --force`
na main/master, `git clean -x` (apaga ignorados como `.env`) e ler chave/credencial pelo Bash (o `deny Read` não
cobre `cat`). Só vale na posição de comando: palavra solta em grep/echo/commit não bloqueia. Cada bloqueio vai para
`~/.claude/state/aviso-risco-bloqueios.log` (segredos mascarados). `ufw status` e `iptables -L` não avisam mais.
`testes/teste-aviso-risco.sh`: 93 casos (bloqueia / avisa / passa), incluindo falsos positivos e o registro.
`testes/teste-kit-hooks.py`: 19 casos multiplataforma (cp1252/HOME isolado) integrados ao repositório.
`hooks/fiscal-economia.py`: cache do medidor OAuth ampliado para 120s e aviso em `stderr` se indisponível.
`modulos/vps/`: sanitização de saída em `sentinela-vps.py` e regra detalhada de aprovação de `cron`/serviços em `LEIA.md`.
`settings.md`: incluídos `sudo dd`, `sudo mkfs`, `sudo shred` e `shred` nas sugestões de `deny`.
Rodar as suítes em `testes/` a cada mudança nos hooks.

## v1.5 — 2026-10-21
§8 Memória: índice `MEMORY.md` ≤4k caracteres, agrupado; históricas em `memory/arquivo/` + `LEIA.md`; conferir órfãs.

## v1.4 — 2026-10-21
Módulo `raycast` preenchido (antes só esqueleto): atalhos de estudo de pentest para Raycast (Windows)
e Ulauncher (Linux), com os mesmos comandos em `.ps1` e `.sh`.
`modulos/raycast/AULA.md`: aula que mapeia os atalhos que o usuário já tem (sub-rede, dispositivos,
ping, testar-porta, meus-ips, status-vpn) às fases de recon/enumeração, com boas práticas e aviso de
escopo. `modulos/raycast/scripts/`: `desec-abrir` (abre a academia), `desec-2fa` (TOTP lido do cofre
do sistema — SecretManagement/secret-tool —, mostra e copia; função TOTP pura no Windows), `desec-vpn`
(liga a VPN do lab, modo `wsl` padrão ou `kali` por SSH, flag de instalar; mostra o comando e confirma
antes do sudo), `desec-nota` (cria nota no Obsidian pelo modelo). `modulos/raycast/modelos/relatorio-pentest.md`:
template de relatório. Semente 2FA e `.ovpn` nunca entram no kit — ficam no cofre do sistema e em `~/desec/`.
Peso aproximado em tokens: repositório completo ~28.808 (115.234 caracteres ÷ 4).

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
