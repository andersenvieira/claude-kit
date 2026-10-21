#!/usr/bin/env python3
"""Mapa de assuntos: índice dos ESTADO_*.md gerado dos cabeçalhos (sem IA, custo zero de token).

  mapa.py                gera ~/docs/MAPA.md
  mapa.py busca <termo>  só as linhas que casam (assunto, projeto, palavra, resumo), até 10
  mapa.py abertos        só o que tem pendência
  mapa.py frentes        abertos agrupados por projeto, numerados (para triagem)
  mapa.py marcar <ESTADO_X> <aberto|pausado|fechado|arquivado>   troca o status no cabeçalho
  mapa.py checar         ESTADO sem cabeçalho, >60 linhas, relaciona quebrado
  mapa.py iniciar        põe cabeçalho rascunho nos ESTADO que não têm (não toca nos que têm)

Cabeçalho (primeiras linhas do ESTADO):
---
assunto: nome curto
projeto: FILACARD-V2
palavras: cartão, uid, passarelli
status: aberto | pausado | fechado | arquivado
relaciona: ESTADO_X, ESTADO_Y
atualizado: 2026-10-12
resumo: uma linha
---
"""
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

# Windows usa cp1252 por padrão: entrada/saída do hook sempre em UTF-8.
for _f in (sys.stdin, sys.stdout):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

HOME = Path.home()
RAIZES = [HOME / "docs", HOME / "dev" / "docs"] + sorted((HOME / "dev").glob("*/docs"))
SAIDA = HOME / "docs" / "MAPA.md"
MAX_ATIVOS = 5
CAMPOS = ["assunto", "projeto", "palavras", "status", "relaciona", "atualizado", "resumo"]
LIMITE = 60


def achar():
    """ESTADO ativos (docs/ e docs/arquivo/**). Ignora HISTORICO, FICHA, REGRAS, PLANO."""
    vistos = []
    for r in RAIZES:
        if r.is_dir():
            vistos += [p for p in r.rglob("ESTADO*.md") if "node_modules" not in p.parts]
    return sorted(set(vistos))


def cabecalho(texto):
    m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None, texto
    d = {}
    for ln in m.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            d[k.strip()] = v.strip()
    return d, texto[m.end():]


def projeto_de(p):
    partes = p.parts
    if "dev" in partes:
        i = partes.index("dev")
        if i + 1 < len(partes) and partes[i + 1] != "docs":
            return partes[i + 1]
    return "GERAL"


def ler(p):
    texto = p.read_text(encoding="utf-8", errors="ignore")
    d, corpo = cabecalho(texto)
    return d, texto, len(texto.splitlines())


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def lista(valor):
    return [x.strip() for x in (valor or "").split(",") if x.strip()]


def registros():
    out = []
    for p in achar():
        d, _, n = ler(p)
        out.append({"path": p, "linhas": n, "d": d})
    return out


def rascunho(p, texto):
    """Cabeçalho provisório a partir de nome, caminho, data e seções do arquivo."""
    nome = re.sub(r"^ESTADO[-_]?", "", p.stem).replace("_", " ").replace("-", " ").strip().lower() or p.stem
    titulo = next((l.lstrip("# ").strip() for l in texto.splitlines() if l.startswith("# ")), "")
    sec = re.search(r"^##\s*(falta|pend[eê]ncias?|pr[oó]xima a[cç][aã]o|pendente)[^\n]*\n(.*?)(?=^## |\Z)",
                    texto, re.S | re.M | re.I)
    corpo = sec.group(2).strip().lower() if sec else ""
    aberto = bool(corpo) and not re.match(r"^(-\s*)?(nada|nenhuma|sem pend|tudo fechado)", corpo)
    mt = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
    return {"assunto": nome, "projeto": projeto_de(p), "palavras": nome.replace(" ", ", "),
            "status": "aberto" if aberto else "fechado", "relaciona": "", "atualizado": mt,
            "resumo": titulo[:110]}


def iniciar():
    n = 0
    for r in registros():
        if r["d"] is None:
            texto = r["path"].read_text(encoding="utf-8", errors="ignore")
            h = rascunho(r["path"], texto)
            bloco = "---\n" + "\n".join(f"{k}: {h[k]}" for k in CAMPOS) + "\n---\n"
            r["path"].write_text(bloco + texto, encoding="utf-8")
            n += 1
    print(f"{n} cabeçalhos rascunho criados (revisar palavras/relaciona/status).")


def gerar():
    regs = [r for r in registros() if r["d"]]
    por_proj = {}
    idx = {}
    for r in regs:
        d = r["d"]
        por_proj.setdefault(d.get("projeto", "?"), []).append(r)
        for w in lista(d.get("palavras")) + [d.get("assunto", "")]:
            if w:
                idx.setdefault(norm(w), set()).add(d.get("assunto", r["path"].stem))
    L = [f"# MAPA de assuntos (gerado por ~/.claude/bin/mapa.py em {date.today()} — não editar à mão)",
         "Uso: `mapa.py busca <palavra>` antes de ler qualquer ESTADO. Cabeçalho de cada ESTADO é a fonte.", ""]
    for proj in sorted(por_proj):
        L.append(f"## {proj}")
        L.append("| assunto | status | palavras | resumo | arquivo |")
        L.append("|---|---|---|---|---|")
        for r in sorted(por_proj[proj], key=lambda r: r["d"].get("assunto", "")):
            d = r["d"]
            rel = str(r["path"]).replace(str(HOME), "~")
            L.append(f"| {d.get('assunto','')} | {d.get('status','')} | {d.get('palavras','')} | "
                     f"{d.get('resumo','')} | {rel} |")
        L.append("")
    L.append("## Índice de palavras → assuntos")
    for w in sorted(idx):
        L.append(f"- **{w}**: {'; '.join(sorted(idx[w]))}")
    SAIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{SAIDA}: {len(regs)} assuntos, {len(idx)} palavras.")


def linha(r):
    d = r["d"] or {}
    rel = str(r["path"]).replace(str(HOME), "~")
    rel_ = f" → {d['relaciona']}" if d.get("relaciona") else ""
    return (f"[{d.get('status','?')}] {d.get('projeto','?')}/{d.get('assunto','?')} — "
            f"{d.get('resumo','')} ({rel}){rel_}")


def busca(termo):
    t = norm(termo)
    achados = []
    for r in registros():
        d = r["d"]
        if not d:
            continue
        alvo = norm(" ".join([d.get("assunto", ""), d.get("projeto", ""), d.get("palavras", ""),
                              d.get("resumo", ""), r["path"].name]))
        if t in alvo:
            achados.append(r)
    for r in achados[:10]:
        print(linha(r))
    if len(achados) > 10:
        print(f"... +{len(achados) - 10} (refine o termo)")
    if not achados:
        print("nada achado")


def abertos():
    for r in registros():
        if r["d"] and r["d"].get("status") == "aberto":
            d = r["d"]
            print(f"- {d.get('projeto')}/{d.get('assunto')}: {d.get('resumo','')} ({str(r['path']).replace(str(HOME), '~')})")


def frentes():
    abs_ = [r for r in registros() if r["d"] and r["d"].get("status") == "aberto"]
    abs_.sort(key=lambda r: (r["d"].get("projeto", "?"), -r["path"].stat().st_mtime))
    pj = None
    for i, r in enumerate(abs_, 1):
        d = r["d"]
        if d.get("projeto") != pj:
            pj = d.get("projeto")
            print(f"\n{pj}")
        dt = datetime.fromtimestamp(r["path"].stat().st_mtime).strftime("%d/%m")
        print(f"{i:>3}. {dt} {d.get('assunto')} — {d.get('resumo','')} [{r['path'].stem}]")
    print(f"\n{len(abs_)} abertos (meta ≤{MAX_ATIVOS})")


def marcar(nome, status):
    if status not in ("aberto", "pausado", "fechado", "arquivado"):
        sys.exit(f"status inválido: {status}")
    alvo = [r for r in registros() if r["path"].stem == nome.removesuffix(".md")]
    if len(alvo) != 1:
        sys.exit(f"{len(alvo)} arquivos com o nome {nome}")
    p = alvo[0]["path"]
    _, t, _ = ler(p)
    novo, n = re.subn(r"(?m)^status:.*$", f"status: {status}", t, count=1)
    if not n:
        sys.exit(f"sem campo status: {p}")
    p.write_text(novo, encoding="utf-8")
    print(f"{p.stem}: {status}")


def abertura(teto=1200):
    """Bloco curto para o início de sessão: prioridade 1, depois urgência alta, depois os mais recentes."""
    abs_ = [r for r in registros() if r["d"] and r["d"].get("status") == "aberto"]
    def chave(r):
        d = r["d"]
        return (d.get("prioridade") != "1", d.get("urgencia") != "alta",
                -r["path"].stat().st_mtime)
    abs_.sort(key=chave)
    por_proj = {}
    for r in abs_:
        pj = r["d"].get("projeto", "?")
        por_proj[pj] = por_proj.get(pj, 0) + 1
    contagem = "Abertos por projeto: " + " · ".join(
        f"{k} {v}" for k, v in sorted(por_proj.items(), key=lambda kv: -kv[1]))
    rodape = f"\n{contagem} (total {len(abs_)})\n0. assunto novo · ver 10 · ver 15 · ver todos (`mapa.py abertos`)"
    itens = abs_[:5]
    cab = "Retomada (prioridade 1 e urgência alta primeiro; ESTADO = caminho abaixo):"
    fixo = len(cab) + len(rodape)
    def item(i, r, corte):
        d = r["d"]
        dt = datetime.fromtimestamp(r["path"].stat().st_mtime).strftime("%d/%m")
        res = d.get("resumo", "")
        res = res if len(res) <= corte else res[:corte - 1] + "…"
        longo = " LONGO" if r["linhas"] > LIMITE else ""
        return f"\n{i}. {dt} {d.get('projeto')}/{d.get('assunto')}: {res} ({str(r['path']).replace(str(HOME), '~')}){longo}"
    for corte in (110, 90, 70, 50, 30):
        corpo = "".join(item(i, r, corte) for i, r in enumerate(itens, 1))
        if fixo + len(corpo) <= teto:
            break
    print(cab + corpo + rodape)


def checar():
    regs = registros()
    nomes = {r["path"].stem for r in regs}
    probs = []
    for r in regs:
        d, p = r["d"], str(r["path"]).replace(str(HOME), "~")
        if not d:
            probs.append(f"sem cabeçalho: {p}")
            continue
        for c in CAMPOS:
            if not d.get(c) and c != "relaciona":
                probs.append(f"campo '{c}' vazio: {p}")
        if r["linhas"] > LIMITE and d.get("status") != "arquivado":
            probs.append(f"{r['linhas']} linhas (>{LIMITE}): {p}")
        for x in lista(d.get("relaciona")):
            if x not in nomes:
                probs.append(f"relaciona inexistente '{x}': {p}")
    n_ab = sum(1 for r in regs if r["d"] and r["d"].get("status") == "aberto")
    if n_ab > MAX_ATIVOS:
        probs.append(f"{n_ab} abertos (>{MAX_ATIVOS}): pausar com `mapa.py marcar ESTADO_X pausado`")
    print("\n".join(probs) if probs else "0 problemas")
    return len(probs)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "gerar"
    if cmd == "busca" and len(sys.argv) > 2:
        busca(" ".join(sys.argv[2:]))
    elif cmd == "abertos":
        abertos()
    elif cmd == "frentes":
        frentes()
    elif cmd == "marcar" and len(sys.argv) > 3:
        marcar(sys.argv[2], sys.argv[3])
    elif cmd == "abertura":
        abertura()
    elif cmd == "checar":
        sys.exit(1 if checar() else 0)
    elif cmd == "iniciar":
        iniciar()
    else:
        gerar()
