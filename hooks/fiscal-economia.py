#!/usr/bin/env python3
"""Fiscal de economia do Claude Code.

Dois eventos, um script:

  SessionStart      aponta os arquivos de retomada (docs/ESTADO*.md) do projeto e
                    entrega o mais recente. As regras ficam no CLAUDE.md global.

  UserPromptSubmit  mede a conversa (tokens de contexto da última resposta e imagens
                    lidas). Passou do limite, avisa o modelo — que grava o estado
                    e pede o /clear — e mostra uma linha para o usuário.

O /clear em si é comando da interface: só o usuário pode dar. O fiscal garante
que a hora certa nunca passe despercebida.

Limites ajustáveis nas constantes abaixo.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Windows usa cp1252 por padrão: entrada/saída do hook sempre em UTF-8.
for _f in (sys.stdin, sys.stdout):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ------------------------------------------------------------------ limites
AVISO = {"ctx_k": 60, "imagens": 25}    # mil tokens de contexto: hora de fechar o assunto
ALERTA = {"ctx_k": 100, "imagens": 60}   # já está caro; não emendar nada
REPETIR_ALERTA_A_CADA_K = 20             # mil tokens de crescimento entre um alerta e outro

ESTADO_DIR = Path.home() / ".claude/fiscal-estado"
USO_CACHE_S = 120                        # uso (5h/semana): 2 min de cache reduz as leituras do token OAuth


def uso_da_conta():
    """Percentual de 5h e semanal (mesma fonte do /usage), com cache; None se falhar."""
    cache = ESTADO_DIR / "uso.json"
    import time
    try:
        c = json.loads(cache.read_text(encoding="utf-8"))
        if time.time() - c["t"] < USO_CACHE_S:
            return c
    except Exception:
        pass
    try:
        import urllib.request
        cred = json.loads((Path.home() / ".claude/.credentials.json").read_text(encoding="utf-8"))
        req = urllib.request.Request("https://api.anthropic.com/api/oauth/usage", headers={
            "Authorization": "Bearer " + cred["claudeAiOauth"]["accessToken"],
            "anthropic-beta": "oauth-2025-04-20"})
        d = json.load(urllib.request.urlopen(req, timeout=3))
        c = {"t": time.time(), "h5": d["five_hour"]["utilization"], "sem": d["seven_day"]["utilization"]}
        ESTADO_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(c), encoding="utf-8")
        return c
    except Exception:
        print("fiscal-economia: medidor de cota indisponível", file=sys.stderr)
        return None


def ler_entrada():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def responder(evento, contexto=None, mensagem=None):
    saida = {}
    if contexto:
        saida["hookSpecificOutput"] = {"hookEventName": evento, "additionalContext": contexto}
    if mensagem:
        saida["systemMessage"] = mensagem
    print(json.dumps(saida, ensure_ascii=False))


def pasta_generica(cwd):
    # Raiz ou pasta dos usuários: /, /home, ~ (Linux/macOS) e C:\, C:\Users (Windows).
    p = Path(cwd)
    return p == Path(p.anchor) or p == Path.home() or p == Path.home().parent


def arquivos_de_retomada(cwd):
    # Só o projeto da pasta atual: ela mesma e o pai (app/ dentro do repo).
    # Subir mais traria os ESTADO de outros projetos vizinhos.
    achados = []
    bases = [Path(cwd), Path(cwd).parent]
    # Sessão da máquina (celular abre em /home; VS Code às vezes em /): ESTADOs de ~/docs.
    if pasta_generica(cwd):
        bases.append(Path.home())
    for base in bases:
        for p in base.glob("docs/ESTADO*.md"):
            if p not in achados:
                achados.append(p)
    # Mais recente primeiro: o assunto em andamento não pode ficar fora dos 5.
    # Vale a data de conversa (`atualizado:`), não a do arquivo: edição em massa de
    # cabeçalhos mexe no arquivo sem ninguém ter falado do assunto.
    achados.sort(key=data_de_conversa, reverse=True)
    return achados


def data_de_conversa(p):
    mtime = p.stat().st_mtime
    arq = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    try:
        for l in p.read_text(encoding="utf-8", errors="ignore").splitlines()[1:12]:
            if l.startswith("atualizado:"):
                data = l.partition(":")[2].strip()[:16]
                # Mesmo dia: a hora do arquivo desempata; data antiga: só ela vale.
                return (arq if arq.startswith(data[:10]) else data, mtime)
    except OSError:
        pass
    return (arq, mtime)


def inicio_de_sessao(dados):
    partes = []
    cwd = dados.get("cwd") or os.getcwd()
    generico = pasta_generica(cwd)
    todos = arquivos_de_retomada(cwd)
    retomada = todos[:5]
    if generico and len(retomada) > 1:
        # Pasta genérica: só o bloco curto do mapa (teto 1.200 caracteres), não a lista inteira.
        try:
            bloco = subprocess.run([sys.executable, str(Path.home() / ".claude/bin/mapa.py"), "abertura"],
                                   capture_output=True, text=True, timeout=5).stdout.strip()
        except OSError:
            bloco = ""
        if bloco:
            responder("SessionStart", bloco + "\nPedido claro: leia o ESTADO dele (caminho acima ou "
                      "`mapa.py busca <termo>`). Só \"continuar\": mostre a lista numerada (data + título em "
                      "palavras comuns + última ação, sem nome de arquivo) e pergunte o número. LONGO = enxugar.")
            return
    if retomada:
        linhas = []
        for p in retomada:
            try:
                n = sum(1 for _ in p.open(encoding="utf-8", errors="ignore"))
            except OSError:
                n = 0
            extra = " — LONGO: enxugue para ~40 linhas e mova o histórico para HISTORICO_*.md" if n > 60 else ""
            # O nome do arquivo não diz do que se falou: mostrar quando, assunto e resumo.
            campos = {}
            try:
                for l in p.read_text(encoding="utf-8", errors="ignore").splitlines()[1:12]:
                    if l.strip() == "---":
                        break
                    k, _, v = l.partition(":")
                    campos[k.strip()] = v.strip()
            except OSError:
                pass
            d = data_de_conversa(p)[0]
            quando = f"{d[8:10]}/{d[5:7]}" + (d[10:] if len(d) > 10 else "")
            desc = " — ".join(x for x in (campos.get("titulo") or campos.get("assunto"),
                                         campos.get("ultimo") or campos.get("resumo")) if x)
            linhas.append(f"- {quando} · {desc or p.stem} ({p}, {n} linhas){extra}")
        partes.append("Arquivos de retomada neste projeto, mais recente primeiro (HISTORICO_*.md não se lê na retomada):\n"
                      + "\n".join(linhas))
        if len(todos) > 5:
            # O usuário não quer assunto escondido: sempre oferecer a lista maior.
            partes.append(
                f"Há mais {len(todos) - 5} ESTADO aqui fora destes 5 (lista completa por data: "
                f"`ls -t {Path(todos[0]).parent}/ESTADO_*.md`; todos os projetos: ~/docs/MAPA.md). "
                "Ao mostrar a lista ao usuário (ele usa voz): numerar, cada item = data + título em palavras comuns + a última ação falada; sem nome de arquivo nem sublinhado. Termine oferecendo: \"ver 10 · ver 15 · ver todos\"."
            )
        if generico and len(retomada) > 1:
            # Pasta genérica (/, /home, ~) com vários assuntos em aberto: não dar prioridade
            # a nenhum. "Continuar" sozinho não escolhe — ver memória continuar-nao-presume-topico.
            mapa = ""
            try:
                mapa = subprocess.run(
                    [sys.executable, str(Path.home() / ".claude/bin/mapa.py"), "abertos"],
                    capture_output=True, text=True, timeout=5,
                ).stdout.strip()
            except OSError:
                pass
            if mapa:
                partes.append("Mapa de assuntos abertos em toda a máquina (`mapa.py abertos`):\n" + mapa)
            partes.append(
                "Vários assuntos em aberto nesta pasta genérica, nenhum é \"o atual\". Se o pedido "
                "já deixar claro o assunto (ou o fio desta conversa já deixou), leia o ESTADO "
                "correspondente (lista acima ou mapa). Se o pedido for só \"continuar\"/\"segue\" sem dizer "
                "qual, mostre a lista numerada e pergunte só o número — sem ler nenhum ESTADO ainda."
            )
        else:
            # Um único ESTADO em aberto (ou pasta de projeto específico): vem inteiro, o
            # usuário não precisa digitar "continuar de".
            atual = max(retomada, key=lambda p: p.stat().st_mtime)
            try:
                corpo = "\n".join(atual.read_text(encoding="utf-8", errors="ignore").splitlines()[:70])
            except OSError:
                corpo = ""
            if corpo:
                partes.append(
                    f"[retomada] ESTADO mais recente ({atual}):\n{corpo}\n\n"
                    "Se o pedido do usuário for \"continuar\"/\"segue\" ou tratar deste assunto, retome "
                    "daqui sem reler o arquivo. Se tiver pendência e o pedido for vago, siga a pendência. "
                    "Se o pedido for de outro assunto, leia o ESTADO desse assunto (lista acima), se houver."
                )
    if partes:
        responder("SessionStart", "\n\n".join(partes))


def medir(transcript):
    """Contexto = entrada total (nova + cache) da última resposta da conversa principal.
    Modelo: o esperado é o da primeira resposta depois do último /model; o atual, o da última."""
    ctx = imagens = 0
    esperado = atual = None
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as f:
            for linha in f:
                imagens += linha.count('"type":"image"') + linha.count('"type": "image"')
                if "<command-name>/model</command-name>" in linha:
                    esperado = None  # troca pedida pelo usuário: vale o que vier depois
                if '"usage"' not in linha:
                    continue
                try:
                    msg = json.loads(linha)
                except Exception:
                    continue
                if msg.get("isSidechain"):
                    continue
                u = (msg.get("message") or {}).get("usage") or {}
                total = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                         + u.get("cache_creation_input_tokens", 0))
                if total:
                    ctx = total
                modelo = (msg.get("message") or {}).get("model") or ""
                if modelo and not modelo.startswith("<"):
                    esperado, atual = esperado or modelo, modelo
    except OSError:
        pass
    return {"ctx_k": ctx / 1000, "imagens": imagens, "esperado": esperado, "atual": atual}


def familia(modelo):
    return next((f for f in ("opus", "fable", "sonnet", "haiku") if f in (modelo or "")), modelo)


def caiu_de_modelo(m):
    """Troca que o usuário não pediu. No opusplan, opus<->sonnet é o normal."""
    de, para = familia(m["esperado"]), familia(m["atual"])
    if not de or not para or m["esperado"] == m["atual"]:
        return False
    try:
        cfg = json.loads((Path.home() / ".claude/settings.json").read_text()).get("model", "")
    except Exception:
        cfg = ""
    return not ("opusplan" in cfg and {de, para} <= {"opus", "sonnet"})


def passou(medida, limite):
    return [k for k in limite if medida[k] >= limite[k]]


def a_cada_mensagem(dados):
    transcript = dados.get("transcript_path")
    sessao = dados.get("session_id") or "sem-sessao"
    if not transcript or not os.path.exists(transcript):
        return

    m = medir(transcript)
    ESTADO_DIR.mkdir(parents=True, exist_ok=True)
    marca = ESTADO_DIR / f"{sessao}.json"
    try:
        visto = json.loads(marca.read_text())
    except Exception:
        visto = {}

    resumo = f"{m['ctx_k']:.0f}k tokens de contexto, {m['imagens']} imagens"
    alerta, aviso = passou(m, ALERTA), passou(m, AVISO)

    nivel = None
    if alerta:
        ultimo = visto.get("alerta_em")
        if ultimo is None or m["ctx_k"] - ultimo >= REPETIR_ALERTA_A_CADA_K:
            nivel, visto["alerta_em"] = "alerta", m["ctx_k"]
    elif aviso:
        nivel, visto["aviso"] = "aviso", True

    def delta(chave, valor):
        ini = visto.setdefault(chave + "_ini", valor)
        ult = visto.get(chave + "_ult", valor)
        visto[chave + "_ult"] = valor
        return f" (+{valor - ult:.0f})" if valor > ult else ""

    uso = uso_da_conta()
    acao = "" if not aviso else " 🔴/clear"
    medidor = f"💬{100 * m['ctx_k'] / ALERTA['ctx_k']:.0f}% · {familia(m['atual']) or '?'}"
    if uso:
        medidor += f" · 5h {uso['h5']:.0f}%{delta('h5', uso['h5'])} · sem {uso['sem']:.0f}%{delta('sem', uso['sem'])}"
    medidor += acao
    regra = ("Comece a resposta com esta linha, em texto pequeno (entre crases), sem comentar: "
             f"`{medidor}`") if aviso else ""
    contexto, mensagem = regra, None
    queda = ""
    if caiu_de_modelo(m) and visto.get("queda") != m["atual"]:
        visto["queda"] = m["atual"]
        queda = (f"🔴 MODELO: a sessão começou em {m['esperado']} e a última resposta veio de {m['atual']} "
                 "(troca que o usuário não pediu). Comece a resposta com a linha "
                 f"\"🔴 caiu para {familia(m['atual'])}\". Pedido de código nível 2–3: pause e pergunte ao usuário "
                 "se segue assim ou espera o modelo voltar; nível 0–1 pode seguir.")
        mensagem = f"Modelo trocou: {m['esperado']} → {m['atual']}"
    marca.write_text(json.dumps(visto))

    if nivel == "aviso":
        contexto = regra + "\n" + (
            f"[fiscal-economia] AVISO: {resumo}. Conversa ficando cara. "
            "Ao terminar o pedido atual (sem emendar outro assunto): grave o estado no "
            "docs/ESTADO_*.md do projeto (feito, falta, decisões, número da suíte). Não faça pergunta "
            "nesta resposta (pergunta em aberto vai para o ESTADO, para a próxima sessão). Termine com UMA linha: "
            "\"Quer acrescentar algo ao ESTADO? Fale agora. Quando terminar: /clear e depois: continuar <assunto>\" "
            "(se nada ficou pendente: \"Quer acrescentar algo? Fale agora; senão /clear e mande o próximo pedido\")."
        )
        mensagem = f"Fiscal de economia: {resumo}. Ao fechar este pedido vale um /clear."
    elif nivel == "alerta":
        contexto = regra + "\n" + (
            f"[fiscal-economia] ALERTA: {resumo}. Cada resposta agora relê tudo isso. "
            "Faça o mínimo para fechar o pedido atual, grave o estado no docs/ESTADO_*.md e "
            "termine pedindo /clear com a linha de retomada (\"continuar\" só se houver pendência). Não comece nada novo nesta sessão "
            "e não faça pergunta (vai para o ESTADO); se o usuário só quiser acrescentar algo, grave no ESTADO e repita a linha do /clear. "
            "Evite ler imagens: prefira checagem por script."
        )
        mensagem = f"Fiscal de economia: {resumo}. Está caro — feche o assunto e dê /clear."

    if queda:
        contexto = queda + ("\n" + contexto if contexto else "")
        mensagem = mensagem if nivel else f"Modelo trocou: {m['esperado']} → {m['atual']}"
    responder("UserPromptSubmit", contexto, mensagem)


def main():
    dados = ler_entrada()
    evento = dados.get("hook_event_name") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if evento == "SessionStart":
        inicio_de_sessao(dados)
    elif evento == "UserPromptSubmit":
        a_cada_mensagem(dados)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # o fiscal nunca pode travar a sessão
        pass
