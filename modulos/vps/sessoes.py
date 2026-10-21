#!/usr/bin/env python3
"""Catálogo único das sessões do Claude (VS Code, Desktop, terminal, celular).

Fonte: ~/.claude/projects/*/*.jsonl (mesmo formato em todas as ferramentas)
       + títulos das abas do Desktop (~/.config/Claude/claude-code-sessions).
Assunto: palavras do ~/docs/MAPA.md. Origem é só etiqueta.
Saída: ~/docs/SESSOES.md (leitura) e ~/docs/sessoes.json (ficha padronizada).
Uso: sessoes.py            -> gera os dois arquivos
     sessoes.py busca <txt> -> lista fichas que batem com o texto
"""
import json, os, re, sys, glob, time
from collections import Counter, defaultdict
from datetime import datetime

HOME = os.path.expanduser('~')
PROJ = f'{HOME}/.claude/projects'
DESK = f'{HOME}/.config/Claude/claude-code-sessions'
MAPA = f'{HOME}/docs/MAPA.md'
SAIDA_MD = f'{HOME}/docs/SESSOES.md'
SAIDA_JSON = f'{HOME}/docs/sessoes.json'

ORIGEM = {'claude-vscode': 'VS Code', 'claude-desktop': 'Desktop', 'cli': 'Terminal', 'sdk-cli': 'Celular/SDK'}

SEGREDO = [
    (re.compile(r'\b(sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[bap]-[A-Za-z0-9-]{10,})'), '[segredo]'),
    (re.compile(r'(?i)\b(senha|password|passwd|token|secret|api[_-]?key)\b(\s*[:=]\s*|\s+(?:é|e)\s+)\S+'), r'\1\2[oculto]'),
    (re.compile(r'\b[A-Za-z0-9+/=_-]{40,}\b'), '[oculto]'),
]


def mascara(t):
    for rx, sub in SEGREDO:
        t = rx.sub(sub, t)
    return t


def limpa(t, n=110):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = ' '.join(t.split())
    return mascara(t[:n] + ('…' if len(t) > n else ''))


def texto_user(msg):
    c = msg.get('content') if isinstance(msg, dict) else None
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return ' '.join(p.get('text', '') for p in c if isinstance(p, dict) and p.get('type') == 'text')
    return ''


def titulos_desktop():
    t = {}
    for f in glob.glob(f'{DESK}/**/*', recursive=True):
        if not os.path.isfile(f):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if isinstance(d, dict) and d.get('cliSessionId') and d.get('title'):
            t[d['cliSessionId']] = d['title']
    return t


def assuntos_mapa():
    """[(assunto, projeto, status, palavras[], arquivo)] a partir das tabelas do MAPA.md."""
    out, proj = [], ''
    for l in open(MAPA, encoding='utf-8'):
        if l.startswith('## '):
            proj = l[3:].strip()
        elif l.startswith('| ') and not l.startswith('| assunto') and not l.startswith('|---'):
            c = [x.strip() for x in l.strip().strip('|').split('|')]
            if len(c) >= 5:
                pal = [p.strip().lower() for p in c[2].split(',') if len(p.strip()) >= 4]
                out.append((c[0], proj, c[1], pal, c[4]))
    return out


def toques_estado(msg):
    """[(ferramenta, caminho)] de docs/ESTADO_*.md lidos/editados numa mensagem do assistente."""
    c, out = msg.get('content') if isinstance(msg, dict) else None, []
    for b in c if isinstance(c, list) else []:
        if isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('name') in ('Read', 'Edit', 'Write'):
            fp = (b.get('input') or {}).get('file_path') or ''
            if re.search(r'/docs/ESTADO_[^/]+\.md$', fp):
                out.append((b['name'], fp))
    return out


def mais_frequente(caminhos):
    """Caminho mais repetido da lista; empate fica com o último a aparecer."""
    n = Counter(caminhos)
    return max(reversed(caminhos), key=lambda c: n[c]) if caminhos else ''


def assunto_estado(caminho):
    """Valor de 'assunto:' no frontmatter do ESTADO ('' se o arquivo sumiu ou não tem)."""
    try:
        linhas = open(caminho, encoding='utf-8', errors='replace').read().split('\n')
    except OSError:
        return ''
    if not linhas or linhas[0].strip() != '---':
        return ''
    for l in linhas[1:]:
        if l.strip() == '---':
            break
        if l.startswith('assunto:'):
            x = l[8:].strip().strip('"\'')
            return x if '/' not in x and len(x) <= 60 else ''
    return ''


def assunto_dos_estados(toques):
    """Assunto pelos ESTADO tocados: editados primeiro; só lidos se repetido (>=2) ou único."""
    edit = [p for t, p in toques if t != 'Read']
    lidos = [p for t, p in toques if t == 'Read']
    for p in (mais_frequente(edit), mais_frequente(lidos) if lidos and (Counter(lidos).most_common(1)[0][1] >= 2 or len(set(lidos)) == 1) else ''):
        x = assunto_estado(p) if p else ''
        if x:
            return x
    return ''


def casa_mapa(assunto, mapa):
    """Assunto citado -> (assunto, projeto, arquivo); entrada do mapa se bater, senão só o nome."""
    for a in mapa:
        if a[0].lower() == assunto.lower():
            return a[0], a[1], a[4]
    return assunto, '', ''


def assunto_da_sessao(titulo_app, titulo, estado, texto, cwd, mapa):
    """(a) título do app 'X — Y'; (b) último ESTADO tocado; (c) classifica por palavras."""
    x = titulo_app.split(' — ')[0].strip() if ' — ' in titulo_app else ''
    x = x or assunto_dos_estados(estado)
    if x:
        return casa_mapa(x, mapa)
    return classifica(titulo, texto, cwd, mapa)


def le_sessao(f):
    ent, cwd, custom, ultima, prompts, ts = Counter(), '', '', '', [], []
    estado = []
    with open(f, encoding='utf-8', errors='replace') as fh:
        for l in fh:
            try:
                d = json.loads(l)
            except Exception:
                continue
            if d.get('entrypoint'):
                ent[d['entrypoint']] += 1
            cwd = cwd or d.get('cwd', '')
            if d.get('timestamp'):
                ts.append(d['timestamp'])
            tp = d.get('type')
            if tp == 'assistant':
                estado += toques_estado(d.get('message', {}))
            if tp == 'custom-title' and d.get('customTitle'):
                custom = d['customTitle']
            elif tp == 'last-prompt' and d.get('lastPrompt'):
                ultima = d['lastPrompt']
            elif tp == 'user' and not d.get('isMeta') and not d.get('isSidechain') and not d.get('toolUseResult'):
                t = texto_user(d.get('message', {})).strip()
                if t and not t.startswith('<') and not t.startswith('Caveat:'):
                    prompts.append(t)
    return ent, cwd, custom, ultima, prompts, ts, estado


def local(iso):
    """Timestamp UTC do jsonl -> 'AAAA-MM-DDTHH:MM' no fuso da máquina (Manaus)."""
    try:
        return datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone().strftime('%Y-%m-%dT%H:%M')
    except ValueError:
        return iso[:16]


def classifica(titulo, texto, cwd, mapa):
    titulo, texto = titulo.lower(), texto.lower()
    melhor, pts = None, (0, 0)
    for a in mapa:
        p = sum(5 * titulo.count(k) + texto.count(k) for k in a[3]) + (8 if a[0] in titulo else 0)
        # empate: ganha quem tem mais palavras do próprio nome no texto ("vps" separa os dois "painel")
        p = (p, sum(1 for w in a[0].split() if len(w) >= 3 and re.search(rf'\b{re.escape(w)}\b', texto)))
        if p > pts:
            melhor, pts = a, p
    if melhor and pts[0] >= 2:
        return melhor[0], melhor[1], melhor[4]
    proj = os.path.basename(cwd.rstrip('/')) or '/'
    return f'sem assunto · {proj}', '', ''


def gera():
    mapa, desk, fichas = assuntos_mapa(), titulos_desktop(), []
    for f in glob.glob(f'{PROJ}/*/*.jsonl'):
        sid = os.path.basename(f)[:-6]
        ent, cwd, custom, ultima, prompts, ts, estado = le_sessao(f)
        if not prompts:
            continue
        titulo = custom or desk.get(sid) or prompts[0]
        assunto, projeto, arq = assunto_da_sessao(custom or desk.get(sid) or '', titulo, estado, ' '.join(prompts[:6] + [ultima]), cwd, mapa)
        fichas.append({
            'id': sid,
            'assunto': assunto,
            'projeto': projeto,
            'estado': arq,
            'titulo': limpa(titulo, 80),
            'primeira': limpa(prompts[0]),
            'ultima': limpa(ultima or prompts[-1]),
            'origem': ORIGEM.get(ent.most_common(1)[0][0], ent.most_common(1)[0][0]) if ent else 'Terminal',
            'pasta': cwd,
            'inicio': local(min(ts)) if ts else '',
            'fim': local(max(ts)) if ts else '',
            'perguntas': len(prompts),
            'mb': round(os.path.getsize(f) / 1e6, 1),
            'retomar': f'cd {cwd or HOME} && claude --resume {sid}',
        })
    fichas.sort(key=lambda x: x['fim'], reverse=True)
    json.dump(fichas, open(SAIDA_JSON, 'w'), ensure_ascii=False, indent=1)

    grupos = defaultdict(list)
    for x in fichas:
        grupos[x['assunto']].append(x)
    ordem = sorted(grupos, key=lambda g: (g.startswith('sem assunto'), -max(time.mktime(time.strptime(s['fim'], '%Y-%m-%dT%H:%M')) for s in grupos[g] if s['fim'])))
    hoje = time.strftime('%Y-%m-%d %H:%M')
    md = [f'# SESSÕES do Claude — catálogo único (gerado por ~/.claude/bin/sessoes.py em {hoje} — não editar à mão)',
          '', f'{len(fichas)} sessões em {len(grupos)} assuntos. Horários de Manaus. Busca: `sessoes.py busca <palavra>`. Ficha completa: ~/docs/sessoes.json.', '',
          '## Índice', '']
    for g in ordem:
        md.append(f'- {g} ({len(grupos[g])}) — última {grupos[g][0]["fim"][:10]}')
    for g in ordem:
        s0 = grupos[g][0]
        md += ['', f'## {g}' + (f' · {s0["projeto"]}' if s0['projeto'] else ''), '']
        if s0['estado']:
            md.append(f'ESTADO: {s0["estado"]}')
            md.append('')
        for s in grupos[g]:
            md.append(f'- **{s["fim"][:10]} {s["fim"][11:]} · {s["origem"]} · {s["perguntas"]} perguntas · {s["mb"]} MB** — {s["titulo"]}')
            md.append(f'  - última: {s["ultima"]}')
            md.append(f'  - retomar: `{s["retomar"]}`')
    open(SAIDA_MD, 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(f'{len(fichas)} sessões, {len(grupos)} assuntos → {SAIDA_MD}')


def busca(txt):
    txt = txt.lower()
    for s in json.load(open(SAIDA_JSON)):
        if txt in ' '.join(str(v) for v in s.values()).lower():
            print(f'{s["fim"][:16]} · {s["origem"]} · {s["assunto"]} — {s["titulo"]}\n   {s["retomar"]}')


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'busca':
        busca(' '.join(sys.argv[2:]))
    else:
        gera()
