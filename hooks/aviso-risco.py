#!/usr/bin/env python3
"""Aviso de risco do Claude Code.

Com `permissions.defaultMode: bypassPermissions` quase nada pede confirmação.
Este hook (PreToolUse, matcher Bash) compensa isso: olha o comando prestes a
rodar e, se bater num padrão arriscado, mostra um aviso curto ao usuário.

Avisa (systemMessage) nos padrões de risco e BLOQUEIA (permissionDecision "deny")
só os catastróficos listados em BLOQUEAR. Comando sem risco: sai calado.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

# Registro dos bloqueios (um por linha, segredos mascarados). Para o teste: AVISO_RISCO_LOG=<arquivo>.
LOG = Path(os.environ.get("AVISO_RISCO_LOG") or (Path.home() / ".claude/state/aviso-risco-bloqueios.log"))
_SEGREDO = re.compile(r"(?i)(senha|password|passwd|token|secret|api[_-]?key)(\s*[=:]\s*|\s+)\S+")


def registrar(motivo, comando):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        c = _SEGREDO.sub(r"\1=[oculto]", comando).replace("\n", " ")[:200]
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\t" + motivo + "\t" + c + "\n")
        os.chmod(LOG, 0o600)
    except Exception:
        pass  # o registro nunca pode travar a sessão


# Windows usa cp1252 por padrão: entrada/saída do hook sempre em UTF-8.
for _f in (sys.stdin, sys.stdout):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ------------------------------------------------------------- padrões
# (regex, mensagem) — primeira que bater vence. case-insensitive.
PADROES = [
    (r"\brm\s+(-\w*r\w*f\w*|-\w*f\w*r\w*)\b",
     "comando apaga arquivos recursivamente sem confirmação — revise antes de rodar: rm -rf"),
    (r"\bgit\s+push\b.*(--force\b(?!-with-lease)|(?<!--force-with-lease)\s-f\b)",
     "push força sobrescrita do histórico remoto — revise antes de rodar: git push --force"),
    (r"\bgit\s+push\b.*--force-with-lease\b",
     "push sobrescreve o remoto (mesmo com --force-with-lease) — revise antes de rodar"),
    (r"\bgit\s+reset\s+--hard\b",
     "reset duro descarta alterações locais sem volta — revise antes de rodar: git reset --hard"),
    (r"\b(drop\s+table|drop\s+database|truncate)\b",
     "comando apaga tabela/banco inteiro no SQL — revise antes de rodar"),
    (r"\brm\b[^;&|]*(\s-\w*r\b|--recursive)",
     "rm recursivo — revise antes de rodar (flags separadas ou longas também)"),
    (r"\bgit\s+clean\b[^;&|]*-\w*f", "git clean apaga arquivos não versionados — revise"),
    (r"\bfind\b[^;&|]*-delete\b", "find -delete apaga arquivos — revise"),
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(python3?|perl|ruby|node)\b", "executa script baixado direto no interpretador — revise"),
    (r"/etc/ssh/sshd_config", "mexe na configuração do SSH — faça backup antes e teste o acesso"),
    (r"\bsudo\b",
     "comando com privilégio elevado — revise antes de rodar: sudo"),
    (r"\b(ufw|iptables)\b(?!\s+(?:-\w+\s+)*(?:status|-L|-S|--list)\b)",
     "comando mexe no firewall — revise antes de rodar"),
    (r"\bsystemctl\s+(stop|disable|restart)\b",
     "comando para/reinicia um serviço do sistema — revise antes de rodar"),
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(sh|bash)\b",
     "executa script baixado da internet direto no shell — revise antes de rodar"),
    (r"\bmkfs\b",
     "comando formata disco — revise antes de rodar: mkfs"),
    (r"\bdd\s+(if|of)=",
     "escrita bruta em disco/dispositivo — revise antes de rodar: dd"),
    (r"\b(migrate:fresh|migrate:refresh|db:wipe)\b",
     "comando reinicializa o banco de dados (apaga dados) — revise antes de rodar"),
]

# Catastróficos: bloqueados. Cobre rm com flags separadas/longas, sudo/bash -c, find -delete etc.
BLOQUEAR = [
    (r"\brm\b(?=[^;&|]*(\s-\w*r|--recursive))(?=[^;&|]*(\s-\w*f|--force))[^;&|]*\s(/|~|\$HOME|/home|/etc|/var|/usr|/opt)(/?\*?)(\s|$)",
     "rm recursivo em diretório de sistema/home"),
    (r"\bsudo\b[^;&|]*\b(dd|mkfs\w*|shred|wipefs|fdisk|parted)\b", "sudo com comando destrutivo de disco"),
    (r"(^|[;&|]\s*)(sudo\s+)?(mkfs\w*|wipefs|shred)\s", "formatação/apagamento de disco"),
    (r"\bdd\s+[^|;&]*\bof=/dev/", "escrita bruta em dispositivo"),
    (r">\s*/dev/(sd|nvme|vd)\w+", "redirecionamento para disco"),
    (r"\bfind\b[^;&|]*\s/(\s|$)[^;&|]*-delete", "find -delete na raiz"),
    (r"\bchmod\s+-R\s+[0-7]*7\s+/(\s|$)", "chmod -R aberto na raiz"),
    (r"(^|[;&|]\s*)(php\s+)?artisan\s+(migrate:fresh|migrate:refresh|db:wipe)\b", "reinicializa o banco (regra: nunca sem pedido e backup)"),
]
# Posição de comando: início da linha, depois de ; & | ( e opcionalmente sudo. Evita bloquear a palavra
# solta em grep/echo/commit.
_P = r"(?:^|[;&|(]\s*)(?:sudo\s+(?:-\S+\s+)*)?"
_RM = r"\brm\b(?=[^;&|]*(?:\s-\w*r|--recursive))(?=[^;&|]*(?:\s-\w*f|--force))[^;&|]*\s"
BLOQUEAR_EXTRA = [
    # apagar dados
    (r"\b(?:mysql|mariadb|psql)\b[^|]*\bdrop\s+(?:database|schema)\b", "DROP DATABASE/SCHEMA"),
    (_P + r"mysqladmin\b[^;&|]*\bdrop\b", "mysqladmin drop"),
    (r"\b(?:mysql|mariadb|psql)\b[^|]*\btruncate\b", "TRUNCATE em banco (regra: nunca sem pedido e backup)"),
    (r"\b(?:mysql|mariadb|psql)\b[^|]*\bdelete\s+from\s+[\w.`\"]+\s*(?:;|\"|'|$)", "DELETE sem WHERE"),
    (r"\bredis-cli\b[^;&|]*\bflush(?:all|db)\b", "redis flush"),
    (r"\bcrontab\b[^;&|]*\s-r\b", "crontab -r apaga todas as rotinas"),
    (_RM + r"(?:/var/lib/mysql|/var/www|/root|~/\.ssh|\$HOME/\.ssh|/home/\w+|\.git)/?\*?(?:\s|$)", "rm recursivo em dados/home/.git"),
    (_P + r"truncate\s+-s\s*0\s+\S*(?:/var/lib/|\.sqlite|\.db\b)", "truncate em arquivo de banco"),
    # perder o acesso à máquina
    (_P + r"ufw\s+(?:--force\s+)?(?:disable|reset)\b", "ufw disable/reset"),
    (_P + r"iptables\b[^;&|]*(?:\s-F\b|\s-X\b|-P\s+INPUT\s+DROP)", "iptables derruba regras/entrada"),
    (_P + r"nft\s+flush\s+ruleset", "nft flush ruleset"),
    (_P + r"systemctl\s+(?:disable|stop|mask)\s+[^;&|]*\b(?:ssh|sshd)(?:\.service)?\b", "desligar o SSH"),
    (_P + r"passwd\s+(?:-\w+\s+)*-l\b", "passwd -l trava conta"),
    (_P + r"userdel\b", "userdel remove usuário"),
    # derrubar a máquina
    (_P + r"(?:reboot|shutdown|poweroff|halt)\b", "reiniciar/desligar a máquina"),
    (_P + r"systemctl\s+(?:reboot|poweroff|halt)\b", "reiniciar/desligar a máquina"),
    (_P + r"init\s+[06]\b", "init 0/6"),
    (_P + r"kill\s+-9\s+(?:-1|1)\s*$", "kill -9 no init"),
    (r":\s*\(\s*\)\s*\{[^}]*:\s*\|\s*:", "fork bomb"),
    # backup no Drive e docker
    (_P + r"rclone\s+(?:sync|purge|delete|deletefile|cleanup)\b", "rclone apaga no destino"),
    (_P + r"docker\s+system\s+prune\b[^;&|]*(?:\s-a\b|--all|--volumes)", "docker system prune -a/--volumes"),
    (_P + r"docker\s+volume\s+(?:rm|prune)\b", "docker volume rm/prune"),
    (_P + r"docker(?:\s+compose|-compose)\s+down\b[^;&|]*(?:\s-v\b|--volumes)", "docker compose down -v"),
    # arquivos de sistema e git
    (_P + r"(?:chmod|chown)\s+-R\s+[^;&|]*\s/(?:\s|$)", "chmod/chown -R na raiz"),
    (_P + r"mv\s+(?:-\w+\s+)*(?:/|/home|/etc|/var|/usr|/opt|/home/\w+)/?\s", "mv de diretório de sistema/home"),
    (_P + r"git\s+filter-(?:branch|repo)\b", "git filter-branch/repo reescreve o histórico"),
    (r"\bgit\s+push\b(?=[^;&|]*(?:--force\b(?!-with-lease)|\s-f\b))[^;&|]*\b(?:main|master)\b", "git push --force na main/master"),
    (_P + r"git\s+clean\b[^;&|]*\s-\w*[xX]", "git clean -x/-X apaga também os ignorados (.env, uploads)"),
    # segredo pelo Bash (o deny Read não cobre cat)
    (r"\b(?:cat|less|more|head|tail|cp|scp|base64|xxd|strings)\b[^;&|]*(?:\.ssh/id_\w+\b(?!\.pub)|_rsa\b(?!\.pub)|\.credentials\.json|\.claude/\.api-key)", "ler chave/credencial pelo Bash"),
]
BLOQUEAR += BLOQUEAR_EXTRA

BLOQUEAR = [(re.compile(p, re.IGNORECASE), m) for p, m in BLOQUEAR]

PADROES = [(re.compile(p, re.IGNORECASE), m) for p, m in PADROES]


def ler_entrada():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def avaliar(comando):
    if not comando:
        return None
    for padrao, mensagem in PADROES:
        if padrao.search(comando):
            return mensagem
    return None


def main():
    dados = ler_entrada()
    if dados.get("tool_name") != "Bash":
        return
    comando = (dados.get("tool_input") or {}).get("command") or ""
    for padrao, motivo in BLOQUEAR:
        if padrao.search(comando):
            registrar(motivo, comando)
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                  "permissionDecision": "deny",
                  "permissionDecisionReason": "Bloqueado pelo aviso-risco: " + motivo + ". Peça ao usuário."}},
                  ensure_ascii=False))
            return
    mensagem = avaliar(comando)
    if mensagem:
        print(json.dumps({"systemMessage": "⚠ " + mensagem}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # o aviso nunca pode travar a sessão
        pass
