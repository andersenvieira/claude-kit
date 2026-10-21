#!/usr/bin/env python3
"""Título da conversa a partir da marca da triagem.

UserPromptSubmit: lê o transcript, acha a última linha minha no formato
`[nível N · etiqueta] assunto — ação` e devolve sessionTitle = "assunto — ação".
Sem marca ainda (1ª mensagem): título provisório (só o assunto) via
classifica() do bin/sessoes.py, se existir. Respeita /rename: se o título do
transcript não é o último que o hook pôs, a sessão fica parada.
Qualquer erro: sai calado (exit 0). Estado em TITULO_ESTADO_DIR (padrão
~/.claude/fiscal-estado/titulos).
"""
import importlib.util
import json
import os
import re
import sys

# Windows usa cp1252 por padrão: entrada/saída do hook sempre em UTF-8.
for _f in (sys.stdin, sys.stdout):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

HOME = os.path.expanduser('~')
MAX = 60
TAIL = 2 * 1024 * 1024
SESSOES = f'{HOME}/.claude/bin/sessoes.py'
MARCA = re.compile(r'^\s*\[n[ií]vel\s+\d+[^\]]*\]\s*(.+?)\s*$', re.I)


def limpa(s):
    # tira markdown simples
    return re.sub(r'[`*_#]', '', s).strip()


def acha_marca(linhas):
    """Última marca (assunto, ação) nas mensagens minhas; None se não houver."""
    achada = None
    for l in linhas:
        try:
            o = json.loads(l)
        except Exception:
            continue
        if not isinstance(o, dict) or o.get('type') != 'assistant' or o.get('isSidechain'):
            continue
        cont = (o.get('message') or {}).get('content')
        if isinstance(cont, str):
            cont = [{'type': 'text', 'text': cont}]
        for b in cont or []:
            if not isinstance(b, dict) or b.get('type') != 'text':
                continue
            for t in str(b.get('text', '')).splitlines():
                m = MARCA.match(t)
                if not m:
                    continue
                resto = limpa(m.group(1))
                partes = re.split(r'\s+—\s+|\s+-\s+', resto, maxsplit=1)
                if len(partes) == 2 and partes[0] and partes[1]:
                    achada = (partes[0].strip(), partes[1].strip())
    return achada


def titulo_de(assunto, acao=None, maximo=MAX):
    """'assunto — ação' cortado: corta a ação primeiro, o assunto só se preciso."""
    if not acao:
        return assunto[:maximo].rstrip()
    t = f'{assunto} — {acao}'
    if len(t) <= maximo:
        return t
    sobra = maximo - len(assunto) - 3
    if sobra >= 4:
        return f'{assunto} — {acao[:sobra].rstrip()}'
    return assunto[:maximo].rstrip()


def custom_atual(linhas):
    atual = None
    for l in linhas:
        if '"custom-title"' not in l:
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        if isinstance(o, dict) and o.get('type') == 'custom-title' and o.get('customTitle'):
            atual = o['customTitle']
    return atual


def decide(linhas, guardado, provisorio):
    """Devolve ('parar'|'nada'|'por', título). provisorio() -> str|None."""
    atual = custom_atual(linhas)
    if guardado and atual and atual != guardado:
        return 'parar', None  # o usuário renomeou (sem guardado, custom-title é automático)
    marca = acha_marca(linhas)
    titulo = titulo_de(*marca) if marca else provisorio()
    if not titulo or titulo == atual:
        return 'nada', None
    return 'por', titulo


def le_linhas(caminho):
    tam = os.path.getsize(caminho)
    with open(caminho, 'rb') as f:
        if tam > TAIL:
            f.seek(tam - TAIL)
            f.readline()  # descarta linha cortada
        dados = f.read()
    return dados.decode('utf-8', 'replace').splitlines()


def provisorio_de(prompt, cwd):
    try:
        spec = importlib.util.spec_from_file_location('sessoes_t', SESSOES)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assunto = m.classifica(prompt, prompt, cwd, m.assuntos_mapa())[0]
        if assunto.startswith('sem assunto'):
            return None
        return titulo_de(assunto)
    except Exception:
        return None


def main():
    try:
        d = json.load(sys.stdin)
        sid, tp = d['session_id'], d['transcript_path']
        pasta = os.environ.get('TITULO_ESTADO_DIR') or f'{HOME}/.claude/fiscal-estado/titulos'
        os.makedirs(pasta, exist_ok=True)
        arq, parado = os.path.join(pasta, sid), os.path.join(pasta, sid + '.parado')
        if os.path.exists(parado):
            return
        guardado = open(arq, encoding='utf-8').read() if os.path.exists(arq) else None
        linhas = le_linhas(tp)
        acao, titulo = decide(linhas, guardado,
                              lambda: provisorio_de(d.get('prompt', ''), d.get('cwd', '')))
        if acao == 'parar':
            open(parado, 'w').close()
        elif acao == 'por':
            open(arq, 'w', encoding='utf-8').write(titulo)
            print(json.dumps({'hookSpecificOutput': {
                'hookEventName': 'UserPromptSubmit', 'sessionTitle': titulo}},
                ensure_ascii=False))
    except Exception:
        pass


if __name__ == '__main__':
    main()
    sys.exit(0)
