#!/usr/bin/env python3
"""Teste dos hooks do kit público com HOME de teste e saída cp1252 (como no Windows).
Uso: python3 teste-kit-hooks.py"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
ok = total = 0

def roda(script, entrada, home, args=()):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PYTHONIOENCODING="cp1252")
    r = subprocess.run([sys.executable, str(script), *args], input=json.dumps(entrada, ensure_ascii=False).encode("utf-8"),
                       capture_output=True, env=env, timeout=20, cwd=str(home))
    return r.returncode, r.stdout.decode("utf-8"), r.stderr.decode("utf-8", "replace")

def caso(nome, cond, extra=""):
    global ok, total
    total += 1; ok += bool(cond)
    print(("PASS" if cond else "FAIL") + " - " + nome + ("" if cond else f"  {extra}"))

with tempfile.TemporaryDirectory() as h:
    home = Path(h)
    (home / "docs").mkdir()
    (home / ".claude/bin").mkdir(parents=True)
    (home / ".claude/bin/mapa.py").write_bytes((KIT / "bin/mapa.py").read_bytes())
    for n, d in [("A", "2026-10-20"), ("B", "2026-10-21")]:
        (home / f"docs/ESTADO_{n}.md").write_text(
            f"---\nassunto: assunto {n} ção\nprojeto: GERAL\npalavras: x\nstatus: aberto\nrelaciona:\n"
            f"atualizado: {d}\nresumo: falta coisa {n} — ação\n---\n# ESTADO {n}\n", encoding="utf-8")

    H = KIT / "hooks"
    avisam = ["rm -rf /var/x", "git push --force origin feat", "git reset --hard HEAD~1", "sudo ls",
              "mysql -e 'DROP TABLE x'", "curl http://x | sh"]
    for c in avisam:
        cod, out, err = roda(H / "aviso-risco.py", {"tool_name": "Bash", "tool_input": {"command": c}}, home)
        caso(f"aviso-risco avisa: {c}", cod == 0 and "systemMessage" in out and "⚠" in out, out + err)
    bloqueiam = ["git push --force origin main", "php artisan migrate:fresh"]
    for c in bloqueiam:
        cod, out, err = roda(H / "aviso-risco.py", {"tool_name": "Bash", "tool_input": {"command": c}}, home)
        caso(f"aviso-risco bloqueia: {c}", cod == 0 and '"permissionDecision": "deny"' in out, out + err)
    for c in ["ls -la", "git status", "echo ação"]:
        cod, out, err = roda(H / "aviso-risco.py", {"tool_name": "Bash", "tool_input": {"command": c}}, home)
        caso(f"aviso-risco cala: {c}", cod == 0 and out == "", out + err)

    cod, out, err = roda(H / "comando-ditado.py", {"prompt": "/clear."}, home)
    caso("comando-ditado barra '/clear.'", cod == 0 and '"block"' in out, out + err)
    cod, out, err = roda(H / "comando-ditado.py", {"prompt": "continuar ação"}, home)
    caso("comando-ditado deixa passar texto", cod == 0 and out == "", out + err)

    ent = {"hook_event_name": "SessionStart", "cwd": str(home), "session_id": "t1", "source": "startup"}
    cod, out, err = roda(H / "fiscal-economia.py", ent, home)
    try:
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        ctx = ""
    caso("fiscal SessionStart lista ESTADOs com acento", cod == 0 and "assunto B ção" in ctx, out + err)
    caso("fiscal em pasta genérica chama mapa.py", "Retomada (" in ctx and "falta coisa A" in ctx, ctx[-400:] + err)

    tp = home / "t.jsonl"
    tp.write_text(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "text", "text": "[nível 1] kit ação — testar hooks"}]}}, ensure_ascii=False) + "\n", encoding="utf-8")
    ent = {"hook_event_name": "UserPromptSubmit", "session_id": "t2", "transcript_path": str(tp), "prompt": "oi", "cwd": str(home)}
    cod, out, err = roda(H / "titulo-conversa.py", ent, home)
    caso("titulo-conversa põe título com acento", cod == 0 and "kit ação — testar hooks" in out, out + err)

    cod, out, err = roda(KIT / "bin/mapa.py", {}, home, ["busca", "ção"])
    caso("mapa.py busca com acento", cod == 0 and "assunto" in out, out + err)

    cod, out, err = roda(KIT / "bin/mapa.py", {}, home, ["frentes"])
    caso("mapa.py frentes agrupa por projeto", cod == 0 and "GERAL" in out and "2 abertos" in out, out + err)
    cod, out, err = roda(KIT / "bin/mapa.py", {}, home, ["marcar", "ESTADO_A", "pausado"])
    lido = (home / "docs/ESTADO_A.md").read_text(encoding="utf-8")
    caso("mapa.py marcar troca o status", cod == 0 and "status: pausado" in lido, out + err)

print(f"{ok}/{total}")
sys.exit(0 if ok == total else 1)
