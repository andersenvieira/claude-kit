#!/usr/bin/env python3
"""UserPromptSubmit: "/clear." ditado por voz chega como mensagem, não como comando.
Barra a mensagem (não gasta resposta) e diz para reenviar sem a pontuação."""
import json, re, sys

# Windows usa cp1252 por padrão: entrada/saída do hook sempre em UTF-8.
for _f in (sys.stdin, sys.stdout):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    dados = json.load(sys.stdin)
except Exception:
    sys.exit(0)
texto = (dados.get("prompt") or "").strip()
m = re.fullmatch(r"/\s*([A-Za-z][\w:-]*)(\s+[^\n]*?)?\s*[.!?,;:…]+", texto)
if m:
    cmd = "/" + m.group(1).lower() + (m.group(2) or "").rstrip(" .!?,;:…")
    print(json.dumps({"decision": "block",
                      "reason": f"Ditado com pontuação: mande só  {cmd}  (sem o ponto). Dica: digite / e toque no comando da lista."}))
sys.exit(0)
