#!/usr/bin/env python3
"""Aviso de risco do Claude Code.

Com `permissions.defaultMode: bypassPermissions` quase nada pede confirmação.
Este hook (PreToolUse, matcher Bash) compensa isso: olha o comando prestes a
rodar e, se bater num padrão arriscado, mostra um aviso curto ao usuário.

Nunca bloqueia. Não usa "decision": "block" nem permissionDecision — só
`systemMessage`. Comando sem risco: sai calado (nenhuma saída).
"""
import json
import re
import sys

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
    (r"\bsudo\b",
     "comando com privilégio elevado — revise antes de rodar: sudo"),
    (r"\b(ufw|iptables)\b",
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
    mensagem = avaliar(comando)
    if mensagem:
        print(json.dumps({"systemMessage": "⚠ " + mensagem}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # o aviso nunca pode travar a sessão
        pass
