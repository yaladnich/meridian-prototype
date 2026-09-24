"""Збирає головну index.html (v2, підшипник у SVG) і video.html (той самий підшипник відео) з v1.html.

Зміни v2: герой — слайди виробників «ч/б → кольорове фото» з виносками й рядком виробників унизу; під героєм каталог;
«Послуги» з підшипником «креслення → рендер → відео», кроки змінюються за таймером; ізометричні іконки
в «Умовах роботи», рядок логотипів виробників, координати й приціл у блоці замовлення, зерно паперу.

python tools/build_v2.py
"""
import collections
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'v1.html').read_text(encoding='utf-8')

ARROW = ('<svg width="14" height="14" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" class="ico">'
         '<path d="M224.49,136.49l-72,72a12,12,0,0,1-17-17L187,140H40a12,12,0,0,1,0-24H187L135.51,64.48a12,12,0,0,1,'
         '17-17l72,72A12,12,0,0,1,224.49,136.49Z"/></svg>')


def roll(text):
    k, words = 0, []
    for w in text.split(' '):
        chs = ''.join(f'<span class="ch" style="--k: {k + i};"><span>{html.escape(c)}</span><span>{html.escape(c)}</span></span>'
                      for i, c in enumerate(w))
        k += len(w)
        words.append(f'<span class="rw">{chs}</span>')
    return (f'<span class="sr">{html.escape(text)}</span><span class="rl" aria-hidden="true">'
            + '<span class="ch nb"></span>'.join(words) + '</span>')


def tag(x, y, text, d, left=False):
    cls = 'tg lf' if left else 'tg'
    lx = f'calc({x}% - 8px)' if left else f'calc({x}% + 8px)'
    return (f'<span class="mk" style="left: {x}%; top: {y}%; --d: {d:.2f}s;"></span>'
            f'<a href="#" class="{cls}" style="left: {lx}; top: {y}%; --d: {d + .25:.2f}s;"><span class="ld"></span>'
            f'<span class="bx"><span class="tbg" aria-hidden="true"></span><span class="m">{roll(text)}</span>{ARROW}</span></a>')


def an(x, y, lines, d, left=False):
    t = '<br>'.join(html.escape(s) for s in lines)
    return (f'<span class="an{" lf" if left else ""}" style="left: {x}%; top: {y}%; --d: {d:.2f}s;" aria-hidden="true">'
            f'<i></i><span class="al"></span><span class="at m">{t}</span></span>')


# ---------- ізометричні іконки ----------
C, S = 0.8660254, 0.5


def P(x, y, z, ox, oy):
    return ox + (x - y) * C, oy + (x + y) * S - z


def pl(pts, close=False):
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + (' Z' if close else '')


def ell(cx, cy, rx, ry):
    return f'M{cx - rx:.1f} {cy:.1f} A{rx:.1f} {ry:.1f} 0 1 0 {cx + rx:.1f} {cy:.1f} A{rx:.1f} {ry:.1f} 0 1 0 {cx - rx:.1f} {cy:.1f}'


def iso_svg(vis, hid, acc):
    out = ['<svg class="drw iso" viewBox="0 0 200 150" aria-hidden="true">']
    for i, d in enumerate(vis):
        out.append(f'<path class="dr" pathLength="1" d="{d}" style="--d: {.15 + i * .12:.2f}s;"/>')
    for d in hid:
        out.append(f'<path class="hd" d="{d}"/>')
    ax, ay = acc
    out.append(f'<rect class="ia" x="{ax - 3:.1f}" y="{ay - 3:.1f}" width="6" height="6"/>')
    out.append('</svg>')
    return ''.join(out)


def icon_ring():
    cx, cy, h = 100, 58, 28
    R, r = 64, 34
    rx, ry, irx, iry = R, R * .577, r, r * .577
    vis = [ell(cx, cy, rx, ry), ell(cx, cy, irx, iry),
           f'M{cx - rx} {cy} L{cx - rx} {cy + h} A{rx} {ry:.1f} 0 0 0 {cx + rx} {cy + h} L{cx + rx} {cy}']
    hid = [f'M{cx - rx} {cy + h} A{rx} {ry:.1f} 0 0 1 {cx + rx} {cy + h}', ell(cx, cy + h, irx, iry)]
    return iso_svg(vis, hid, (cx + rx, cy + h * .5))


def icon_box():
    L, W, H, ox, oy = 62, 62, 44, 100, 48
    p = lambda x, y, z: P(x, y, z, ox, oy)
    vis = [pl([p(0, 0, H), p(L, 0, H), p(L, W, H), p(0, W, H)], True),
           pl([p(L, 0, H), p(L, 0, 0), p(L, W, 0), p(0, W, 0), p(0, W, H)]),
           pl([p(L, W, H), p(L, W, 0)]),
           pl([p(0, W / 2, H), p(L, W / 2, H), p(L, W / 2, 0)]),
           pl([p(12, W, 10), p(32, W, 10), p(32, W, 24), p(12, W, 24)], True)]
    hid = [pl([p(0, W, 0), p(0, 0, 0), p(L, 0, 0)]), pl([p(0, 0, 0), p(0, 0, H)])]
    return iso_svg(vis, hid, p(L, W / 2, H / 2))


def icon_sheets():
    L, W, ox, oy = 70, 48, 92, 52
    p = lambda x, y, z: P(x, y, z, ox, oy)
    vis = [pl([p(L, 0, 0), p(L, W, 0), p(0, W, 0)]),
           pl([p(L, 0, 9), p(L, W, 9), p(0, W, 9)]),
           pl([p(0, 0, 18), p(L, 0, 18), p(L, W, 18), p(0, W, 18)], True)]
    for y, x2 in ((10, 52), (19, 42), (28, 58)):
        vis.append(pl([p(10, y, 18), p(x2, y, 18)]))
    hid = [pl([p(0, W, 0), p(0, 0, 0), p(L, 0, 0)])]
    return iso_svg(vis, hid, p(L - 12, W - 10, 18))


def icon_nut():
    import math
    R, H, r, ox, oy = 42, 24, 17, 100, 58
    p = lambda x, y, z: P(x, y, z, ox, oy)
    th = [math.radians(60 * k + 15) for k in range(6)]
    V = [(R * math.cos(t), R * math.sin(t)) for t in th]
    face_vis = []
    for k in range(6):
        m = (th[k] + th[(k + 1) % 6]) / 2 if k < 5 else (th[5] + th[0] + 2 * math.pi) / 2
        face_vis.append(math.cos(m) + math.sin(m) > 0)
    vis = [pl([p(x, y, H) for x, y in V], True)]
    hid = []
    for k in range(6):
        a, b = V[k], V[(k + 1) % 6]
        (vis if face_vis[k] else hid).append(pl([p(*a, 0), p(*b, 0)]))
    for k in range(6):
        seen = face_vis[k] or face_vis[k - 1]
        (vis if seen else hid).append(pl([p(*V[k], 0), p(*V[k], H)]))
    cx, cy = p(0, 0, H)
    vis.insert(1, ell(cx, cy, r * 1.2247, r * .7071))
    hid.append(ell(cx, cy + H, r * 1.2247, r * .7071))
    k = face_vis.index(True)
    a, b = V[k], V[(k + 1) % 6]
    return iso_svg(vis, hid, p((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, H / 2))


def icon_wrench():
    """Розвідний ключ, що лежить на площині: контур зверху, товщина пунктиром знизу, отвір у ручці, черв'як і губки."""
    import math
    T, ox, oy, k = 7, 52, 42, .95
    p = lambda u, v, z=0: P(u * k, v * k, z, ox, oy)

    def arc(cx, cy, r, a0, a1, n=24):
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

    hx, hr, jaw, w = 112, 27, 8, 9
    ay = math.degrees(math.asin(jaw / hr))
    ax = math.degrees(math.acos(-w / hr))
    outline = ([(0, -w), (hx - math.sqrt(hr * hr - w * w), -w)]
               + arc(hx, 0, hr, -ax, -ay)
               + [(hx + 6, -jaw), (hx + 6, jaw)]
               + arc(hx, 0, hr, ay, ax)
               + [(0, w)]
               + arc(0, 0, w, 90, 270))
    top = pl([p(u, v, T) for u, v in outline], True)
    bottom = pl([p(u, v, 0) for u, v in outline], True)
    slot = pl([p(u, v, T) for u, v in [(12, -3.5), (38, -3.5)] + arc(38, 0, 3.5, -90, 90, 8) + [(12, 3.5)] + arc(12, 0, 3.5, 90, 270, 8)], True)
    worm = [pl([p(u, -6, T), p(u, 6, T)]) for u in (93, 97, 101)]
    sx = lambda uv: (uv[0] - uv[1])
    sy = lambda uv: (uv[0] + uv[1])
    sil = {min(outline, key=sx), max(outline, key=sx), max(outline, key=sy)}
    edges = [pl([p(u, v, 0), p(u, v, T)]) for u, v in sil]
    return iso_svg([top, slot] + worm + edges, [bottom], p(hx + 6, 0, T))


ICONS = [icon_ring(), icon_box(), icon_sheets(), icon_wrench()]

# ---------- дані каталогу ----------
M = json.loads(re.search(r'const M=(\[.*?\]);', src).group(1))
RAW = json.loads(re.search(r'const RAW=(\[.*?\]);\n', src, re.S).group(1))
COUNT = collections.Counter(M[r[2]] for r in RAW)
ALT = dict(re.findall(r'<img src="assets/bp-(\w+)\.webp" alt="([^"]*)">', src))
PHOTO_IDS = sorted({int(x) for x in re.findall(r'<img src="assets/p(\d+)\.webp"', src)})


def plural(n, one, few, many):
    a, b = n % 10, n % 100
    if a == 1 and b != 11:
        return one
    if 2 <= a <= 4 and not 12 <= b <= 14:
        return few
    return many


def fmt(n):
    return f'{n:,}'.replace(',', '&#160;')


# ---------- рядок логотипів виробників ----------
LOGO_META = json.loads((ROOT / 'assets' / 'v2' / 'logos.json').read_text(encoding='utf-8'))
LOGO_KEY = {'John Deere': 'johndeere', 'Gates': 'gates', 'A&I': 'ai', 'CLAAS': 'claas', 'Geringhoff': 'geringhoff', 'Horsch': 'horsch', 'Kuhn': 'kuhn', 'Kverneland': 'kverneland',
            'AMAZONE': 'amazone', 'Parker': 'parker', 'Vaderstad': 'vaderstad', 'Bednar': 'bednar', 'OLIMAC': 'olimac',
            'Optibelt': 'optibelt', 'Schumacher': 'schumacher'}
LOGO_NAME = {'Vaderstad': 'Väderstad'}


def logo_strip():
    cells = []
    for b in sorted(COUNT, key=lambda x: -COUNT[x]):
        name = html.escape(LOGO_NAME.get(b, b))
        k = LOGO_KEY.get(b)
        if k:
            w, h = LOGO_META[k]
            ar = w / h
            hh = min(40, (3600 / ar) ** .5, 170 / ar)
            cells.append(f'<a href="#" class="lgc" title="{name}"><span class="lgw" style="width: {hh * ar:.0f}px; height: {hh:.0f}px;">'
                         f'<img class="lm" src="assets/v2/logo-{k}.webp" alt="{name}" loading="lazy" decoding="async">'
                         f'<img class="lc" src="assets/v2/logo-{k}-c.webp" alt="" aria-hidden="true" loading="lazy" decoding="async"></span></a>')
        else:
            cells.append(f'<a href="#" class="lgc"><span class="lgt">{name}</span></a>')
    return ('<div class="lgs" data-sec=""><span class="sl"></span><div class="bsh"><span class="m">Виробники в&#160;каталозі · '
            f'{len(COUNT)}</span><span class="bsa"><button type="button" class="slb bsb" data-bs="-1" aria-label="Попередні виробники">{ARROW}</button>'
            f'<button type="button" class="slb" data-bs="1" aria-label="Наступні виробники">{ARROW}</button></span></div>'
            f'<div class="bsv"><div class="lgk">{"".join(cells)}</div></div>'
            '<div class="bsf m g">Оригінальні деталі та&#160;аналоги · логотипи — торгові марки їхніх власників</div></div>')


# ---------- герой: слайди виробників ----------
# виноски: (x %, y %, напис, плашка ліворуч) у координатах фото 3:2; mt — одна виноска для телефона
SLIDES = [
    dict(k='jd', b='John Deere', t=[(42, 74, 'Пальці протирізучі · 7', False), (51, 49, 'Датчики · 15', True), (70, 58, 'Ремені · 14', False)],
         mt=(70, 58, 'Ремені · 14', True)),
    dict(k='claas', b='CLAAS', t=[(47, 58, 'Підшипники · 10', False), (30, 38, 'Ущільнення · 7', True), (62, 70, 'Кільця · 9', False)],
         mt=(44, 60, 'Підшипники · 10', False)),
    dict(k='bednar', b='Bednar', t=[(25, 50, 'Диски · 4', False), (46, 66, 'Долота · 5', False), (57, 44, 'Кронштейни · 15', False)],
         mt=(46, 66, 'Долота · 5', False)),
    dict(k='geringhoff', b='Geringhoff', t=[(86, 64, 'Зірочки · 4', True), (74, 74, 'Ножі · 4', True)],
         mt=(70, 66, 'Зірочки · 4', True)),
    dict(k='olimac', b='OLIMAC', t=[(39, 69, 'Носки вальців · 2', False), (46, 56, 'Підшипники · 5', False)],
         mt=(38, 58, 'Підшипники · 5', False)),
    dict(k='kuhn', b='Kuhn', t=[(40, 44, 'Запчастини Kuhn · 15', False)],
         mt=(40, 44, 'Запчастини Kuhn · 15', False)),
    dict(k='amazone', b='AMAZONE', t=[(60, 74, 'Диски · 3', False), (54, 64, 'Амортизатори · 4', True)],
         mt=(58, 70, 'Диски · 3', True)),
]

CROSSES = ''.join(f'<span class="cr" style="{a}: 10px; {b}: 8px;">+</span>' for a in ('left', 'right') for b in ('top', 'bottom'))
RULERS = '<span class="ru h t"></span><span class="ru h b"></span><span class="ru v l"></span><span class="ru v r"></span>'


def hero(mob, boot, intro_t):
    n, suf = len(SLIDES), '-800' if mob else ''
    slides, plates, cells = [], [], []
    for i, s in enumerate(SLIDES):
        k, alt, first = s['k'], ALT[s['k']], i == 0
        on = ' on' if first else ''
        path = f'assets/v2/bp-{k}{suf}.webp'
        attr = f'src="{path}" loading="lazy"' if first else f'data-src="{path}"'
        fp = ' fetchpriority="high"' if first else ''
        marks = [s['mt']] if mob else s['t']
        tags = ''.join(tag(x, y, t, .15 * j, left=lf) for j, (x, y, t, lf) in enumerate(marks))
        style = ' style="--t0: .15s; --tw: 2.3s;"' if first else ''
        slides.append(f'<div class="hs{on}"{style}>'
                      f'<div class="hl"><div class="hb"><img class="bw" {attr}{fp} alt="" decoding="async"></div></div>'
                      f'<div class="hc"><div class="hb"><img class="bc" {attr} alt="{alt}" decoding="async"></div></div>'
                      f'<div class="ht"><div class="hb">{tags}</div></div>'
                      f'<span class="bpl"></span><span class="bnd u"></span><span class="bnd d"></span><span class="bpn m"></span></div>')
        c = COUNT[s['b']]
        plates.append(f'<div class="hp{on}"><div class="hph m"><span>Виробник</span><span>[{i + 1:02d}]</span></div>'
                      f'<div class="hpb"><b>{s["b"]}</b><span class="m g">{fmt(c)} {plural(c, "товар", "товари", "товарів")} у&#160;каталозі</span>'
                      f'<span class="hpc m g">{alt}</span></div>'
                      f'<a href="#" class="hpl hv"><span class="tbg" aria-hidden="true"></span><span class="m">{roll("Запчастини " + s["b"])}</span>{ARROW}</a></div>')
        cells.append(f'<button type="button" class="hbc hvt{on}"><i class="hbp"></i>'
                     f'<span class="hbt"><img src="assets/v2/bp-{k}-320.webp" alt="" loading="lazy" decoding="async"></span>'
                     f'<span class="hbn"><b class="rt">{roll(s["b"])}</b><span class="m g">{fmt(c)} {plural(c, "товар", "товари", "товарів")}</span></span></button>')
    if mob:
        labs = '<div class="lab" style="left: 14px; top: 14px; --d: 3.2s;"><span class="m">[00] Каталог · v2</span></div>'
    else:
        labs = ('<div class="lab" style="left: 40px; top: 34px; --d: 3.2s;"><span class="m">[00] Каталог запчастин · v2</span>'
                '<span class="m g">1&#160;237 товарів · 16 виробників</span></div>'
                '<div class="lab" style="right: 40px; top: 34px; align-items: flex-end; --d: 3.3s;">'
                '<span class="m g">John Deere · Bednar · Geringhoff · CLAAS</span><span class="m g">OLIMAC · Kuhn · AMAZONE · A&amp;I · AGV</span></div>')
    controls = (f'<div class="hct"><span class="hnum m">01 / {n:02d}</span>'
                f'<button type="button" class="slb bsb" data-hs="-1" aria-label="Попередній виробник">{ARROW}</button>'
                f'<button type="button" class="slb" data-hs="1" aria-label="Наступний виробник">{ARROW}</button></div>')
    return (f'<section class="hero v3h" aria-label="Виробники"><div class="hvw"><div class="hsl">{"".join(slides)}</div>{RULERS}{CROSSES}'
            f'{boot}{intro_t}{labs}<div class="hps">{"".join(plates)}</div>{controls}</div>'
            f'<div class="hstr">{"".join(cells)}</div></section>')


# ---------- «Послуги»: підшипник грає сам, кроки змінюються за таймером ----------
STEPS = [
    dict(k='Постачання', h=['Постачання', 'запчастин'],
         p='Прямі поставки від виробників: оптимальні ціни та швидкість доставки. Понад 20&#160;000 позицій на&#160;складах.'),
    dict(k='Консультації', h=['Консультації'],
         p='Немає номера? Назвіть марку й&#160;модель техніки. Менеджер підбере деталь і&#160;підкаже, що ще варто замінити.'),
    dict(k='Установка', h=['Установка', 'запчастин'],
         p='Діагностуємо, дефектуємо й&#160;ставимо деталі. Ремонтуємо John Deere: двигуни, коробки передач, мости, ТНВД, гідравліку.'),
]


def bearing(mob, base):
    if mob:
        marks = tag(60, 24, 'Підшипники · 85', base, left=True)
    else:
        marks = (tag(25, 66, 'Підшипники · 85', base, left=True)
                 + an(29.5, 42, ['Ролики конічні × 16', 'поз. 01'], base + .2, left=True)
                 + an(64, 24.5, ['Кільце зовнішнє', 'поз. 02'], base + .35)
                 + an(66.5, 44, ['Кільце внутрішнє', 'поз. 03'], base + .5))
    return ('<div class="lay l" aria-hidden="true"><div class="stage"><img class="b3" src="assets/v2/bearing-l.webp" alt="" '
            'width="1600" height="1000" loading="lazy" decoding="async"></div></div>'
            '<div class="lay r"><div class="stage"><img class="b3" src="assets/v2/bearing.webp" '
            'alt="Роликовий підшипник, технічна ілюстрація" width="1600" height="1000" loading="lazy" decoding="async">'
            '<video class="b3 b3v" muted playsinline loop preload="none" aria-hidden="true" '
            'data-src="assets/v2/bearing-1600.webm" data-src-m="assets/v2/bearing-960.webm"></video>'
            f'{marks}</div></div><span class="bnd2 u"></span><span class="bnd2 d"></span><span class="spl2"></span><span class="spn m"></span>')


def bearing_svg(mob):
    """Підшипник, який малює й анімує скрипт SVG_JS; виноски .ca прив'язані до деталей."""
    i = 'm' if mob else 'd'
    if mob:
        marks = f'<span class="ca" data-a="cupT">{tag(0, 0, "Підшипники · 85", 3.0, left=True)}</span>'
    else:
        marks = (f'<span class="ca" data-a="cupF">{tag(0, 0, "Підшипники · 85", 3.0)}</span>'
                 f'<span class="ca" data-a="roll">{an(0, 0, ["Ролики конічні × 16", "поз. 01"], 3.2, left=True)}</span>'
                 f'<span class="ca" data-a="cupT">{an(0, 0, ["Кільце зовнішнє", "поз. 02"], 3.35)}</span>'
                 f'<span class="ca" data-a="cone">{an(0, 0, ["Кільце внутрішнє", "поз. 03"], 3.5, left=True)}</span>')
    return (f'<div class="svis2 sgb" data-id="{i}"><svg class="brg" viewBox="-480 -425 960 660" aria-label="Конічний роликовий підшипник" role="img">'
            f'<defs></defs><g class="brs"></g></svg>{marks}'
            '<span class="bnd2 u"></span><span class="bnd2 d"></span><span class="spl2"></span><span class="spn m"></span></div>')


def services(mob, mode='video'):
    n = len(STEPS)
    hs, hdr, txt, prg = [], [], [], []
    for i, s in enumerate(STEPS):
        on = ' on' if i == 0 else ''
        lines = ''.join(f'<span class="ln"><span style="--i: {j};">{w}</span></span>' for j, w in enumerate(s['h']))
        hs.append(f'<h2 class="stt{on}">{lines}</h2>')
        hdr.append(f'<span class="scn{on}">[0{i + 1}] {s["k"]}</span>')
        txt.append(f'<p class="sct{on}">{s["p"]}</p>')
        prg.append(f'<div class="spr2{on}"><span class="m">0{i + 1} {s["k"]}</span><i><b></b></i></div>')
    return (f'<section class="story sv" data-sec=""><span class="sl"></span><div class="stk">{RULERS}{CROSSES}'
            f'<span class="scl h"></span><span class="scl v"></span>'
            f'<div class="slab m"><span>[04] Послуги</span><span class="g">Працюємо з людьми та для людей</span></div>'
            f'<div class="scnt m">01 / 0{n}</div>'
            f'<div class="shd">{"".join(hs)}</div>{bearing_svg(mob) if mode == "svg" else f'<div class="svis2 v2h">{bearing(mob, 3.0)}</div>'}'
            f'<div class="scd"><div class="sch m">{"".join(hdr)}</div><div class="scb">{"".join(txt)}</div>'
            f'<div class="scf"><i></i></div></div>'
            f'<div class="spg">{"".join(prg)}</div></div></section>')


# ---------- заміни ----------
def sub1(pattern, repl, s, count, flags=re.S):
    out, n = re.subn(pattern, repl, s, flags=flags)
    assert n == count, (pattern[:60], n, count)
    return out


def reroll(s, old, new, count):
    """Замінює напис із «прокруткою літер»: текст для читачів екрана і згенеровані літери."""
    out, n, pos = [], 0, 0
    key = f'<span class="sr">{old}</span><span class="rl" aria-hidden="true">'
    while True:
        i = s.find(key, pos)
        if i < 0:
            break
        j, depth = i + len(f'<span class="sr">{old}</span>'), 0
        k = j
        while True:
            o, c = s.find('<span', k), s.find('</span>', k)
            if o != -1 and o < c:
                depth, k = depth + 1, o + 5
            else:
                depth, k = depth - 1, c + 7
                if depth == 0:
                    break
        out.append(s[pos:i] + roll(new))
        pos, n = k, n + 1
    assert n == count, (old, n, count)
    return ''.join(out) + s[pos:]


def part(s, is_mob, mode='video'):
    old = re.search(r'<section class="hero">.*?</section>', s, re.S).group(0)
    boot = re.search(r'<div class="boot">.*?</div>', old, re.S).group(0)
    intro_t = re.search(r'<div class="intro-t">.*?</div>', old, re.S).group(0)
    s = sub1(r'<section class="hero">.*?</section>', lambda _: hero(is_mob, boot, intro_t), s, 1)
    s = sub1(r'<section class="brands"[^>]*>.*?</section>', '', s, 1)
    cat = re.search(r'<section class="cat"[^>]*>.*?</section>', s, re.S).group(0)
    s = s.replace(cat, '', 1)
    srch = re.search(r'<section class="srch"[^>]*>.*?</section>', s, re.S).group(0)
    s = s.replace(srch, '', 1)
    sbox = re.search(r'<div class="swrap">(.*?)<div class="sdd"[^>]*></div></div>', srch, re.S).group(1)
    ex = re.search(r'<div class="ex">.*?</div>', srch, re.S).group(0)
    cat = cat.replace('<section class="cat" data-sec="">', '<section class="cat" data-sec="">' if is_mob else '<section class="cat" id="search" data-sec="">', 1)
    if is_mob:
        cat = cat.replace('<span class="m">[05] Каталог</span></div>', '<span class="m">[05] Каталог</span><span class="m g ccn">1&#160;237 товарів</span></div>', 1)
    else:
        cat = cat.replace('<span class="m g">1&#160;237 товарів</span></div>', '<span class="m g ccn">1&#160;237 товарів</span></div>', 1)
    assert 'ccn' in cat
    i = cat.index('<div class="filt"')
    cat = cat[:i] + f'<div class="csr">{sbox}{ex}</div>' + cat[i:]
    grid = 'pg2' if is_mob else 'pg4'
    dyn = (f'<div class="cdyn"><div class="{grid} cgr"></div><div class="cnf"></div>'
           '<div class="cmr"><span class="m g"></span><button type="button" class="btn-a hv inv"><span class="tbg" aria-hidden="true"></span>'
           f'<span class="m">{roll("Показати ще")}</span>{ARROW}</button></div></div>')
    anchor = '<a href="#" class="morem' if is_mob else '<div class="pager"'
    i = cat.index(anchor)
    cat = cat[:i] + dyn + cat[i:]
    s = sub1(r'<div class="mq" data-sec="">.*?</div></div>', lambda _: cat + logo_strip(), s, 1)
    for a, b in (('[03] Типи деталей', '[03] Категорії запчастин'), ('[05] Каталог', '[01] Каталог'),
                 ('[06] Умови роботи', '[05] Умови роботи'), ('[07] Під замовлення', '[06] Під замовлення')):
        s = sub1(re.escape(a), b, s, 1)
    if not is_mob:
        s = reroll(s, 'Усі типи', 'Усі категорії', 1)
    s = sub1(r'(?=<section class="facts")', lambda _: services(is_mob, mode), s, 1)
    it = iter(ICONS)
    s = sub1(r'<div class="fb">', lambda _: '<div class="fb">' + next(it), s, 4)
    s = sub1(r'(<section class="ord rv-ln"[^>]*>)', lambda mm: mm[1] + (
        '<span class="xy m" data-c="tl"></span><span class="xy m" data-c="tr"></span>'
        '<span class="xy m" data-c="bl"></span><span class="xy m" data-c="br"></span>'
        '<span class="xh h"></span><span class="xh v"></span><span class="xl m"></span>'), s, 1)
    return s



GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .15 0 0 0 0 .16 0 0 0 0 .15 .9 0 0 0 -.36'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")

CSS = r"""
/* ===== v2 ===== */
.dw::after{content:'';position:fixed;inset:0;z-index:60;pointer-events:none;background-image:url("GRAIN");background-size:220px 220px;opacity:.38}
a.vlk{text-decoration:underline;text-decoration-color:var(--line2);text-underline-offset:3px}
a.vlk:hover{color:var(--ink)}
@keyframes bnU{0%{opacity:1}85%{opacity:1}to{top:0;opacity:0}}
@keyframes bnD{0%{opacity:1}85%{opacity:1}to{top:100%;opacity:0}}
@keyframes hsP{0%{opacity:1;transform:scaleX(0)}99%{opacity:1;transform:scaleX(1)}to{opacity:0;transform:scaleX(1)}}
@keyframes hsO{0%,99%{opacity:1}to{opacity:0}}
@keyframes hsG{from{transform:scaleX(0)}to{transform:scaleX(1)}}
/* герой: слайди виробників «ч/б → колір», рядок виробників унизу */
.v3h{--hh:clamp(460px,40vw,580px);height:auto;overflow:visible;background-image:none}
.mob .v3h{--hh:400px;height:auto}
.dsk .intro{grid-template-columns:minmax(0,4fr) minmax(0,2fr) minmax(0,1fr)}
.dsk .stmt .body{padding-bottom:14px}
.dsk .stmt .btn-o{height:40px}
.hvw{position:relative;height:var(--hh);overflow:hidden}
.hsl{position:absolute;inset:0;overflow:hidden;z-index:0}
.hs{position:absolute;inset:0;visibility:hidden;--t0:0s;--tw:.9s}
.hs.on{visibility:visible;z-index:2}
.hs.pv{visibility:visible;z-index:1}
.hl,.hc,.ht{position:absolute;inset:0;overflow:hidden}
.ht{pointer-events:none;z-index:3}
.ht .tg{pointer-events:auto}
.hb{position:absolute;left:50%;top:50%;aspect-ratio:3/2;width:max(100%,calc(var(--hh) * 1.5));transform:translate(-50%,-50%)}
.hb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.hl img{filter:grayscale(1) contrast(1.12) brightness(1.04)}
.hs.on .hl{animation:hsW var(--tw) cubic-bezier(.65,.05,.3,1) var(--t0) both}
.hs.on .hc{animation:bcR 1.1s cubic-bezier(.65,.05,.3,1) calc(var(--t0) + var(--tw)) both}
@keyframes hsW{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes bcR{from{clip-path:inset(50% 0 50% 0)}to{clip-path:inset(0 0 0 0)}}
.hs .bpl{position:absolute;left:0;right:0;top:50%;height:1px;background:var(--acc);transform-origin:left;transform:scaleX(0);opacity:0;z-index:4;pointer-events:none}
.hs.on .bpl{animation:hsP var(--tw) cubic-bezier(.65,.05,.3,1) var(--t0) both}
.hs .bnd{position:absolute;left:0;right:0;top:50%;height:1px;background:var(--acc);opacity:0;z-index:4;pointer-events:none}
.hs.on .bnd{animation:1.1s cubic-bezier(.65,.05,.3,1) calc(var(--t0) + var(--tw)) forwards}
.hs.on .bnd.u{animation-name:bnU}.hs.on .bnd.d{animation-name:bnD}
.hs .bpn{position:absolute;left:40px;top:calc(50% - 26px);z-index:4;padding:1px 5px;background:var(--paper);opacity:0;counter-reset:n var(--n);pointer-events:none}
.hs .bpn::after{content:counter(n) '%'}
.hs.on .bpn{animation:cnt var(--tw) cubic-bezier(.65,.05,.3,1) var(--t0) both,hsO var(--tw) linear var(--t0) both}
.hs .mk,.hs .tg{animation:none}
.hs.on .mk{animation:pop .5s cubic-bezier(.3,1.6,.5,1) forwards;animation-delay:calc(var(--d) + var(--t0) + var(--tw) + .9s)}
.hs.on .tg{animation:wipe .7s cubic-bezier(.6,.05,.3,1) forwards;animation-delay:calc(var(--d) + var(--t0) + var(--tw) + .9s)}
.v3h .lab .m{padding:2px 6px;background:var(--paper)}
.v3h .boot{right:28px;bottom:24px;width:calc(36ch + 26px);padding:10px 12px;font-family:'Geist Mono',monospace;font-size:11px;background:var(--paper);border:1px solid var(--ink);animation:fadeOut .6s 2.9s forwards}
.v3h .intro-t{left:28px;bottom:24px;width:340px;padding:0;border:1px solid var(--ink)}
.v3h .intro-t .m{display:block;padding:7px 12px;background:var(--ink);color:var(--paper)}
.v3h .intro-t b{padding:12px 12px 14px;font-size:32px}
.mob .v3h .intro-t{left:8px;right:8px;top:auto;bottom:8px;width:auto}
.mob .v3h .intro-t b{font-size:24px;padding:10px 12px 12px}
.mob .v3h .boot{top:8px;right:8px;bottom:auto}
.hps{position:absolute;left:28px;bottom:24px;z-index:5;display:grid;width:340px;animation:fadeUp .8s cubic-bezier(.2,.7,.2,1) 3.6s backwards}
.hp{grid-area:1/1;align-self:end;background:var(--paper);border:1px solid var(--ink);opacity:0;visibility:hidden;transform:translateY(8px);transition:opacity .3s,transform .45s cubic-bezier(.2,.7,.2,1),visibility 0s .45s}
.hp.on{opacity:1;visibility:visible;transform:none;transition:opacity .35s .2s,transform .5s cubic-bezier(.2,.7,.2,1) .2s}
.hph{display:flex;justify-content:space-between;padding:7px 12px;background:var(--ink);color:var(--paper)}
.hpb{display:flex;flex-direction:column;gap:5px;padding:12px 12px 12px}
.hpb b{font-size:38px;line-height:1;font-weight:700;letter-spacing:-.045em;text-transform:uppercase;padding-bottom:.08em}
.hpc{font-size:10.5px}
.hpl{display:flex;align-items:center;justify-content:space-between;height:42px;padding:0 12px;border-top:1px solid var(--ink)}
.hpl .ico{transition:transform .3s}.hpl:hover .ico{transform:translateX(4px)}
.hp{cursor:pointer}
.hp:hover .hpl{color:var(--ai)}
.hp:hover .hpl>.tbg{transform:none}
.hp:hover .hpl .ch>span{transform:translateY(-100%)}
.hp:hover .hpl .ico{transform:translateX(4px)}
@media (max-width:1240px){.hps{width:300px}.hpb b{font-size:30px}}
.hct{position:absolute;right:28px;bottom:18px;z-index:5;display:flex;align-items:center;gap:6px;animation:fadeUp .8s cubic-bezier(.2,.7,.2,1) 3.7s backwards}
.hnum{margin-right:4px;padding:3px 6px;background:var(--paper)}
.hct .slb{transition:background .25s,color .25s}.hct .slb:hover{background:var(--ink);color:var(--paper)}
.hstr{position:relative;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));border-top:1px solid var(--line)}
.hbc{position:relative;display:flex;flex-direction:column;gap:9px;min-width:0;padding:10px 12px 12px;border:0;border-left:1px solid var(--line);background:transparent;color:var(--ink);text-align:left;cursor:pointer;transition:background .25s}
.hbc:first-child{border-left:0}
.hbc:hover{background:var(--p2)}
.hbt{display:block;aspect-ratio:2.4/1;overflow:hidden;background:var(--p2)}
.hbt img{display:block;width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.12) brightness(1.04);transition:filter .45s,transform .6s cubic-bezier(.2,.7,.2,1)}
.hbc.on .hbt img,.hbc:hover .hbt img{filter:none}
.hbc:hover .hbt img{transform:scale(1.04)}
.hbn{display:flex;flex-direction:column;gap:3px;min-width:0}
.hbn b{font-size:clamp(14px,1.35vw,20px);font-weight:700;letter-spacing:-.03em;text-transform:uppercase;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hbn .m{font-size:11px}
.hbp{position:absolute;left:0;right:0;top:0;height:3px;background:var(--acc);transform-origin:left;transform:scaleX(0);z-index:1}
.hbc.on .hbp.run{animation:hsG var(--sd,7000ms) linear forwards}
.v3h.ps .hbp{animation-play-state:paused}
.mob .hs .bpn{left:14px}
.mob .hps{left:8px;right:8px;bottom:8px;width:auto}
.mob .hph,.mob .hpc{display:none}
.mob .hpb{padding:10px 12px}
.mob .hpb b{font-size:28px}
.mob .hpl{height:40px}
.mob .hct{right:8px;bottom:auto;top:8px}
.mob .hct .slb{width:40px;height:40px}
.mob .hstr{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
.mob .hstr::-webkit-scrollbar{display:none}
.mob .hbc{flex:0 0 42%;scroll-snap-align:start;padding:8px 10px 10px}
.mob .hbn b{font-size:16px}
/* каталог: пошук і фільтр виробника по всьому каталогу */
.csr{padding:18px 20px 16px;border-bottom:1px solid var(--line)}
.csr .sbox input{height:64px;font-size:28px}
.csr .ex{margin-top:12px}
.cdyn{display:none}
.cat.fx .cdyn{display:block}
.cat.fx .pg4:not(.cgr),.cat.fx .pg2:not(.cgr),.cat.fx .pager,.cat.fx .morem{display:none}
.cnf{display:none;padding:28px 20px;font-size:17px;line-height:1.55;color:var(--grey);border-bottom:1px solid var(--line)}
.cnf.on{display:block}
.cnf a{color:var(--ink);font-weight:600;white-space:nowrap}
.cmr{display:flex;align-items:center;justify-content:space-between;gap:16px;height:56px;padding-left:20px;border-bottom:1px solid var(--line)}
.cmr .btn-a{height:100%;min-width:240px;padding:0 20px}
.cmr .btn-a[hidden]{display:none}
.ph.np{display:flex;align-items:center;justify-content:center}
.card .ph.np img{object-fit:contain;padding:22px;filter:none;mix-blend-mode:normal}
.card:hover .ph.np img{transform:scale(1.05)}
.mob .csr{padding:12px 16px 14px}
.mob .cnf{padding:18px 16px;font-size:15px}
.mob .cmr{height:52px;padding-left:16px}
.mob .cmr .btn-a{min-width:0}
/* технічні виноски */
.an{position:absolute;z-index:4;display:flex;align-items:center;transform:translateY(-50%);clip-path:inset(0 100% 0 0);animation:wipe .7s cubic-bezier(.6,.05,.3,1) forwards;animation-delay:var(--d)}
.an.lf{flex-direction:row-reverse;transform:translate(-100%,-50%);clip-path:inset(0 0 0 100%)}
.an i{width:8px;height:8px;margin:0 -4px;background:var(--acc);flex-shrink:0;position:relative;z-index:1}
.an .al{width:40px;height:1px;background:var(--ink)}
.an .at{padding:3px 6px;background:var(--paper);font-size:10.5px;line-height:1.4;color:var(--grey);white-space:nowrap;border-left:1px solid var(--ink)}
.an.lf .at{border-left:0;border-right:1px solid var(--ink);text-align:right}
/* «Послуги»: підшипник «креслення → рендер → відео», кроки за таймером */
.story{position:relative}
.sv .stk{position:relative;height:clamp(680px,94vh,880px);overflow:hidden;background-image:linear-gradient(rgba(38,40,38,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(38,40,38,.045) 1px,transparent 1px);background-size:32px 32px}
.stk .ru,.stk .cr{animation:none}
.scl{position:absolute;pointer-events:none;opacity:.7}
.scl.h{left:28px;right:28px;top:57%;height:1px;background:repeating-linear-gradient(90deg,var(--line2) 0 24px,transparent 24px 30px,var(--line2) 30px 33px,transparent 33px 39px)}
.scl.v{top:28px;bottom:28px;left:50%;width:1px;background:repeating-linear-gradient(180deg,var(--line2) 0 24px,transparent 24px 30px,var(--line2) 30px 33px,transparent 33px 39px)}
.slab{position:absolute;left:40px;top:34px;display:flex;flex-direction:column;gap:6px;z-index:3}
.scnt{position:absolute;right:40px;top:34px;z-index:3}
.shd{position:absolute;left:0;right:0;top:9vh;height:2.2em;font-size:clamp(40px,4.6vw,72px);z-index:3;pointer-events:none}
.stt{position:absolute;left:0;right:0;top:0;margin:0;text-align:center;font-size:1em;line-height:1;font-weight:700;letter-spacing:-.045em;text-transform:uppercase;opacity:0;transition:opacity .2s .55s}
.stt.on{opacity:1;transition-delay:0s}
.stt .ln>span{animation:none;transform:translateY(110%);transition:transform .8s cubic-bezier(.2,.7,.2,1);transition-delay:calc(var(--i,0)*90ms)}
.stt.on .ln>span{transform:none}
.stt.off .ln>span{transform:translateY(-110%)}
.svis2{position:absolute;left:50%;top:57%;width:min(980px,68%);aspect-ratio:16/10;transform:translate(-50%,-50%);z-index:2}
.sv .v2h .stage{left:0;top:0;width:100%;height:100%;aspect-ratio:auto;transform:none}
.lay{position:absolute;inset:0}
.lay.l{pointer-events:none;clip-path:inset(0 100% 0 0);animation:lnr 1.6s cubic-bezier(.65,.05,.3,1) .2s forwards paused}
.lay.r{clip-path:inset(50% 0 50% 0);animation:rvl 1.1s cubic-bezier(.65,.05,.3,1) 1.8s forwards paused}
@keyframes lnr{to{clip-path:inset(0 0 0 0)}}
@keyframes rvl{to{clip-path:inset(0 0 0 0)}}
.bnd2{position:absolute;left:-12%;right:-12%;top:50%;height:1px;background:var(--acc);opacity:0;z-index:3;pointer-events:none;animation:1.1s cubic-bezier(.65,.05,.3,1) 1.8s forwards paused}
.bnd2.u{animation-name:bnU}.bnd2.d{animation-name:bnD}
.spl2{position:absolute;left:-12%;right:-12%;top:50%;height:1px;background:var(--acc);transform-origin:left;transform:scaleX(0);opacity:0;z-index:3;pointer-events:none;animation:hsP 1.6s cubic-bezier(.65,.05,.3,1) .2s both paused}
.spn{position:absolute;left:-12%;top:calc(50% - 24px);z-index:3;padding:1px 5px;background:var(--paper);opacity:0;counter-reset:n var(--n);pointer-events:none;animation:cnt 1.6s cubic-bezier(.65,.05,.3,1) .2s both paused,hsO 1.6s linear .2s both paused}
.spn::after{content:counter(n) '%'}
.sv.in .lay.l,.sv.in .lay.r,.sv.in .bnd2,.sv.in .spl2,.sv.in .spn{animation-play-state:running}
.sv .mk,.sv .tg,.sv .an{animation-play-state:paused}
.sv.in .mk,.sv.in .tg,.sv.in .an{animation-play-state:running}
.b3{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;display:block}
.b3v{opacity:0;transition:opacity .25s}
.v2h.vid .b3v{opacity:1}
.v2h.vid .lay.r img.b3{opacity:0;transition:opacity .25s .2s}
.v2h.vid .lay.l{opacity:.35;transition:opacity 1s}
.v2h .mk,.v2h .tg,.v2h .an{transition:opacity .35s}
.v2h.ex .lay.r .mk,.v2h.ex .lay.r .tg,.v2h.ex .lay.r .an{opacity:0;pointer-events:none}
.scd{position:absolute;left:40px;bottom:40px;width:340px;z-index:4;background:var(--paper);border:1px solid var(--ink)}
.sch{display:grid;background:var(--ink);color:var(--paper);padding:9px 12px}
.scb{display:grid;padding:14px 12px 16px}
.sch>span,.sct{grid-area:1/1;opacity:0;transform:translateY(8px);transition:opacity .35s,transform .45s cubic-bezier(.2,.7,.2,1)}
.sch>span.on,.sct.on{opacity:1;transform:none;transition-delay:.12s}
.sct{margin:0;font-size:15px;line-height:1.5}
.scf{height:3px;background:var(--line)}
.scf i{display:block;height:100%;background:var(--acc);transform-origin:left;transform:scaleX(0)}
.spg{position:absolute;right:40px;bottom:40px;width:260px;display:flex;flex-direction:column;gap:12px;z-index:4}
.spr2{display:flex;flex-direction:column;gap:6px;color:var(--grey);transition:color .3s}
.spr2.on{color:var(--ink)}
.spr2 i{display:block;height:2px;background:var(--line)}
.spr2 b{display:block;height:100%;background:var(--ink);transform-origin:left;transform:scaleX(0)}
.spr2.dn b{transform:none}
.scf i.run,.spr2 b.run{animation:hsG var(--sd,5000ms) linear forwards}
.sv.ps .scf i,.sv.ps .spr2 b{animation-play-state:paused}
@media (max-width:1400px){.hd .lg{width:220px}.hd nav a{width:112px}.hd .tel{padding:0 14px}.hd .cart{padding:0 14px}.hd .msg{padding:0 4px}}
.mob .sv .stk{height:620px;background-size:24px 24px}
.mob .slab{left:14px;top:16px}
.mob .slab .g{display:none}
.mob .scnt{right:14px;top:16px}
.mob .stk .cr{display:none}
.mob .shd{top:52px;font-size:34px}
.mob .svis2{width:124%;top:47%}
.mob .scd{left:8px;right:8px;bottom:8px;width:auto}
.mob .sct{font-size:14px}
.mob .spg{display:none}
.mob .scl.h{top:47%;left:14px;right:14px}
.mob .scl.v{top:14px;bottom:14px}
.mob .ord .xy{display:none}
/* іконки месенджерів у футері — плавно, як у шапці */
.ft4 a.ms,.ftm a.ms{transition:color .25s,transform .25s}
.ft4 a.ms:hover,.ftm a.ms:hover{opacity:1}
/* «Умови роботи» як картки: іконка оживає, посилання отримує ховер */
.facts .fc{cursor:pointer;transition:background .3s}
.facts .fc:hover{background:#ECEBE5}
.facts .fc .iso{transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.facts .fc:hover .iso{transform:translateY(-6px)}
.facts.in .fc:hover .iso .hd{stroke:var(--ink);animation:isoAnts 1s linear infinite}
@keyframes isoAnts{to{stroke-dashoffset:-12}}
.facts.in .fc .iso .ia{transition:transform .35s cubic-bezier(.3,1.6,.5,1)}
.facts.in .fc:hover .iso .ia{transform:scale(1.7)}
.facts .fc:hover .fln{color:var(--ai)}
.facts .fc:hover .fln>.tbg{transform:none}
.facts .fc:hover .fln .ch>span{transform:translateY(-100%)}
.facts .fc:hover .fln .ico{transform:translateX(3px)}
/* ізометричні іконки */
.iso{display:block;width:190px;height:auto;margin:-10px 0 2px -12px;overflow:visible}
.iso .dr{stroke-width:1.2}
.iso .hd{fill:none;stroke:var(--grey);stroke-width:.9;stroke-dasharray:3 3;opacity:0;transition:opacity .8s 1.3s}
.iso .ia{fill:var(--acc);transform-box:fill-box;transform-origin:center;transform:scale(0);transition:transform .5s cubic-bezier(.3,1.6,.5,1) 1.5s}
.facts .iso .dr{animation-play-state:paused}
.facts.in .iso .dr{animation-play-state:running}
.facts.in .iso .hd{opacity:1}
.facts.in .iso .ia{transform:none}
.mob .iso{width:150px;margin:-6px 0 0 -8px}
/* рядок логотипів виробників */
.bsb .ico{transform:rotate(180deg)}
.lgs{position:relative}
.bsh{display:flex;align-items:center;justify-content:space-between;padding:8px 8px 8px 20px;border-bottom:1px solid var(--line)}
.bsa{display:flex;gap:6px}
.bsa .slb{transition:background .25s,color .25s}
.bsa .slb:hover{background:var(--ink);color:var(--paper)}
.bsv{overflow:hidden}
.lgk{display:flex;transition:transform .8s cubic-bezier(.6,.05,.3,1)}
.lgc{flex:0 0 calc(100% / 6);height:112px;display:flex;align-items:center;justify-content:center;border-right:1px solid var(--line);transition:background .25s}
.lgc:hover{background:var(--p2)}
.lgw{position:relative;display:block}
.lgw img{position:absolute;inset:0;width:100%;height:100%;transition:opacity .35s}
.lgw .lc,.lgc:hover .lm{opacity:0}
.lgc:hover .lc{opacity:1}
.lgt{font-size:22px;font-weight:700;letter-spacing:-.035em;text-transform:uppercase;line-height:1;white-space:nowrap}
.bsf{padding:9px 20px;border-top:1px solid var(--line);font-size:11px}
.mob .bsh{padding:6px 6px 6px 16px}
.mob .lgc{flex-basis:50%;height:88px}
.mob .lgw{transform:scale(.85)}
.mob .lgt{font-size:18px}
.mob .bsf{padding:8px 16px}
/* блок замовлення: координати й приціл */
.ord .xy{position:absolute;z-index:2;font-size:10px;letter-spacing:.02em;color:#8E8D86;pointer-events:none}
.ord .xy[data-c=tl]{left:10px;top:8px}.ord .xy[data-c=tr]{right:10px;top:8px}
.ord .xy[data-c=bl]{left:10px;bottom:8px}.ord .xy[data-c=br]{right:10px;bottom:8px}
.ord .xh{position:absolute;z-index:1;background:var(--acc);opacity:0;pointer-events:none;transition:opacity .2s}
.ord .xh.h{left:0;right:0;top:0;height:1px}.ord .xh.v{top:0;bottom:0;left:0;width:1px}
.ord .xl{position:absolute;left:0;top:0;z-index:2;font-size:10px;color:var(--acc);opacity:0;pointer-events:none;transition:opacity .2s}
.ord.xo .xh{opacity:.55}.ord.xo .xl{opacity:1}
""".replace('GRAIN', GRAIN)

JS = r"""
<script>
(function () {
  const vis = (el) => el && el.getClientRects().length > 0;

  // герой: слайди виробників, рядок виробників як перемикач, автопрокрутка, пауза під мишею, свайп на телефоні
  const initHero = (h) => {
    if (h.dataset.ok || !vis(h)) return;
    h.dataset.ok = '1';
    const sl = Array.from(h.querySelectorAll('.hs')), pl = Array.from(h.querySelectorAll('.hp'));
    const cells = Array.from(h.querySelectorAll('.hbc')), bars = cells.map((c) => c.querySelector('.hbp'));
    const num = h.querySelector('.hnum'), strip = h.querySelector('.hstr'), n = sl.length;
    const pad = (x) => (x < 10 ? '0' : '') + x;
    const HOLD = 5;
    let i = 0, t = 0, u = 0, hover = false;
    const load = (k) => sl[(k + n) % n].querySelectorAll('img[data-src]').forEach((im) => { im.src = im.dataset.src; im.removeAttribute('data-src'); });
    function arm(ms) {
      clearTimeout(t);
      bars.forEach((b) => b.classList.remove('run'));
      void bars[i].offsetWidth;
      bars[i].style.setProperty('--sd', ms + 'ms');
      bars[i].classList.add('run');
      h.classList.toggle('ps', hover);
      if (!hover) t = setTimeout(() => show(i + 1), ms);
    }
    let req = 0;
    async function show(k) {
      const to = (k + n) % n;
      if (to === i) return;
      const my = ++req;
      load(to);
      const im = sl[to].querySelector('.bc');
      if (!im.complete || !im.naturalWidth) { try { await im.decode(); } catch (e) { /* показати як є */ } }
      if (my !== req) return;
      const prev = i;
      i = to;
      sl.forEach((s) => s.classList.remove('pv'));
      sl[prev].classList.remove('on'); sl[prev].classList.add('pv');
      const s = sl[i];
      s.style.setProperty('--t0', '0s'); s.style.setProperty('--tw', '.9s');
      s.classList.remove('on'); void s.offsetWidth; s.classList.add('on');
      [pl, cells].forEach((l) => l.forEach((e, j) => e.classList.toggle('on', j === i)));
      num.textContent = pad(i + 1) + ' / ' + pad(n);
      if (strip.scrollWidth > strip.clientWidth + 1) strip.scrollTo({ left: cells[i].offsetLeft - 8, behavior: 'smooth' });
      load(i + 1); load(i - 1);
      clearTimeout(u); u = setTimeout(() => sl[prev].classList.remove('pv'), 2100);
      arm((2 + HOLD) * 1000);
    }
    h.querySelectorAll('[data-hs]').forEach((b) => b.addEventListener('click', () => show(i + +b.dataset.hs)));
    cells.forEach((c, j) => c.addEventListener('click', () => show(j)));
    h.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'mouse') return; hover = true; clearTimeout(t); h.classList.add('ps'); });
    h.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'mouse') return; hover = false; arm(HOLD * 1000); });
    const vw = h.querySelector('.hvw');
    let x0 = null;
    vw.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    vw.addEventListener('touchend', (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1));
    });
    load(1); load(n - 1);
    arm((.15 + 2.3 + 1.1 + HOLD) * 1000);
  };
  const heroes = document.querySelectorAll('.v3h');
  heroes.forEach(initHero);
  window.addEventListener('resize', () => heroes.forEach(initHero));

  // підшипник: після проявлення рендера вмикається відео з альфою (Safari без альфи у WebM — лишається рендер)
  const ua = navigator.userAgent;
  const alphaOK = !(/Safari\//.test(ua) && !/(Chrome|Chromium|CriOS|Edg|Firefox|FxiOS)\//.test(ua));
  document.querySelectorAll('.v2h').forEach((h) => {
    const r = h.querySelector('.lay.r'), v = h.querySelector('.b3v');
    let ready = false, revealed = false, onScreen = false, loaded = false;
    const go = () => { if (ready && revealed && onScreen) v.play().catch(() => {}); };
    r.addEventListener('animationend', (e) => { if (e.animationName === 'rvl') { revealed = true; go(); } });
    if (!v || !alphaOK) return;
    const sync = () => { const t = v.currentTime; h.classList.toggle('ex', t > 1.85 && t < 7.15); };
    const tick = () => { sync(); v.requestVideoFrameCallback(tick); };
    if ('requestVideoFrameCallback' in HTMLVideoElement.prototype) v.requestVideoFrameCallback(tick);
    else v.addEventListener('timeupdate', sync);
    v.addEventListener('playing', () => h.classList.add('vid'), { once: true });
    v.addEventListener('canplaythrough', () => { ready = true; go(); }, { once: true });
    const load = () => {
      if (loaded) return;
      loaded = true;
      v.src = matchMedia('(max-width: 899px)').matches ? v.dataset.srcM : v.dataset.src;
      v.preload = 'auto';
      v.load();
    };
    new IntersectionObserver((es) => es.forEach((e) => {
      onScreen = e.isIntersecting;
      if (onScreen) { load(); go(); } else v.pause();
    }), { rootMargin: '300px 0px' }).observe(h);
  });

  // «Послуги»: кроки змінюються самі, поки блок на екрані
  document.querySelectorAll('.sv').forEach((s) => {
    const tts = s.querySelectorAll('.stt'), chs = s.querySelectorAll('.scn'), cts = s.querySelectorAll('.sct');
    const prs = Array.from(s.querySelectorAll('.spr2')), bar = s.querySelector('.scf i'), cnt = s.querySelector('.scnt');
    const n = tts.length, D = 5000;
    let i = 0, t = 0, on = false;
    const run = (el) => { el.classList.remove('run'); void el.offsetWidth; el.classList.add('run'); };
    function go(k) {
      const prev = i;
      i = k % n;
      tts.forEach((e, j) => { e.classList.toggle('on', j === i); e.classList.toggle('off', j === prev && j !== i); });
      [chs, cts].forEach((l) => l.forEach((e, j) => e.classList.toggle('on', j === i)));
      prs.forEach((e, j) => { e.classList.toggle('on', j === i); e.classList.toggle('dn', j < i); e.querySelector('b').classList.remove('run'); });
      run(prs[i].querySelector('b')); run(bar);
      cnt.textContent = '0' + (i + 1) + ' / 0' + n;
      clearTimeout(t); t = setTimeout(() => go(i + 1), D);
    }
    s.style.setProperty('--sd', D + 'ms');
    new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting && !on) { on = true; s.classList.remove('ps'); go(i); }
      else if (!e.isIntersecting && on) { on = false; clearTimeout(t); s.classList.add('ps'); }
    }), { threshold: .25 }).observe(s);
  });

  // каталог: номер або назва й вибір виробника фільтрують сітку по всьому каталогу
  const PHOTO = new Set(PHOTO_IDS_JSON);
  const RENDER = [[/підшипник/i, 'bearing'], [/шестерн/i, 'gear'], [/зірочк/i, 'sprocket']];
  const escH = (x) => String(x).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const pad2 = (x) => (x < 10 ? '0' : '') + x;
  function findAll(q) {
    const qn = norm(q), ql = q.toLowerCase(), out = [];
    for (const p of CAT) {
      let score = 0, via = '', num = '';
      const sn = norm(p.s);
      if (qn && sn === qn) { score = 100; via = 'sku'; num = p.s; }
      else if (qn && sn.startsWith(qn)) { score = 80; via = 'sku'; num = p.s; }
      else {
        for (const o of p.o) { const on = norm(o); if (on === qn) { score = 90; via = 'other'; num = o; break; } if (on.startsWith(qn) && score < 70) { score = 70; via = 'other'; num = o; } }
        if (!score && qn.length >= 3 && sn.includes(qn)) { score = 60; via = 'sku'; num = p.s; }
        if (!score && qn.length >= 3) { for (const o of p.o) { if (norm(o).includes(qn)) { score = 50; via = 'other'; num = o; break; } } }
        if (!score && p.n.toLowerCase().includes(ql)) { score = 40; via = 'name'; num = p.s; }
      }
      if (score) out.push({ p, score, via, num });
    }
    return out.sort((a, b) => b.score - a.score || b.p.id - a.p.id);
  }
  document.querySelectorAll('.cat').forEach((sec) => {
    const inp = sec.querySelector('input[data-q]'), tpl = sec.querySelector('.card');
    if (!inp || !tpl) return;
    const tplC = tpl.cloneNode(true);
    const grid = sec.querySelector('.cgr'), nf = sec.querySelector('.cnf'), bar = sec.querySelector('.cmr');
    const info = bar.querySelector('.m'), more = bar.querySelector('button'), cnt = sec.querySelector('.ccn');
    const cnt0 = cnt.textContent;
    const fl = Array.from(sec.querySelectorAll('.filt a'));
    fl.forEach((a) => {
      a.dataset.b = a.querySelector('.sr').textContent.replace(/\s*\[.*$/, '').trim().replace(/^Усі$/, '');
      const c = a.querySelector(':scope > .m.g'); if (c) c.dataset.t = c.textContent;
    });
    const per = () => (matchMedia('(max-width: 899px)').matches ? 8 : 12);
    let brand = '', list = [], shown = 0, raw = '';
    const hl = (t) => {
      const i = raw ? t.toUpperCase().indexOf(raw.toUpperCase()) : -1;
      return i < 0 ? escH(t) : escH(t.slice(0, i)) + '<mark>' + escH(t.slice(i, i + raw.length)) + '</mark>' + escH(t.slice(i + raw.length));
    };
    function card(r, k) {
      const p = r.p, el = tplC.cloneNode(true);
      el.removeAttribute('data-rv'); el.removeAttribute('style');
      const top = el.querySelectorAll('.top .m');
      top[0].textContent = p.m; top[1].textContent = '[' + pad2(k + 1) + ']';
      const ph = el.querySelector('.ph');
      if (PHOTO.has(p.id)) ph.innerHTML = '<img src="assets/p' + p.id + '.webp" alt="' + escH(p.n + ' ' + p.s + ' ' + p.m) + '" loading="lazy">';
      else {
        const m = RENDER.find((x) => x[0].test(p.n));
        ph.classList.add('np');
        ph.innerHTML = m ? '<img src="assets/v2/t-' + m[1] + '.webp" alt="" loading="lazy">' : '<span class="m">Фото на&#160;запит</span>';
      }
      el.querySelector('.art').innerHTML = 'Арт. ' + (r.via === 'sku' ? hl(p.s) : escH(p.s));
      el.querySelector('.nm').innerHTML = r.via === 'name' ? hl(p.n) : escH(p.n);
      const old = el.querySelector('.oth'); if (old) old.remove();
      if (p.o.length) {
        const o = document.createElement('div');
        o.className = 'oth m g';
        o.innerHTML = 'Інші номери: ' + p.o.map((x) => (r.via === 'other' && x === r.num ? hl(x) : escH(x))).join(', ');
        el.querySelector('.nm').after(o);
      }
      const price = PRICES[p.s];
      el.querySelector('.pr').innerHTML = price
        ? '<span class="prc">' + fmtN(price) + ' грн</span><span class="st"><i></i><span class="m g">В наявності</span></span>'
        : '<span class="m g">Ціна за запитом</span>';
      return el;
    }
    function page() {
      const f = document.createDocumentFragment();
      list.slice(shown, shown + per()).forEach((r, k) => f.appendChild(card(r, shown + k)));
      grid.appendChild(f);
      shown = Math.min(list.length, shown + per());
      info.textContent = list.length ? 'Показано ' + shown + ' з ' + fmtN(list.length) : '';
      more.hidden = shown >= list.length;
      bar.hidden = !list.length;
    }
    function run() {
      raw = inp.value.trim();
      const q = raw.length >= 2;
      sec.classList.toggle('fx', q || !!brand);
      const res = q ? findAll(raw) : CAT.slice().sort((a, b) => b.id - a.id).map((p) => ({ p, via: '', num: '' }));
      const bc = {};
      res.forEach((r) => { bc[r.p.m] = (bc[r.p.m] || 0) + 1; });
      fl.forEach((a) => {
        const c = a.querySelector(':scope > .m.g');
        if (c) c.textContent = q ? '[' + fmtN(a.dataset.b ? bc[a.dataset.b] || 0 : res.length) + ']' : c.dataset.t;
      });
      if (!q && !brand) { cnt.textContent = cnt0; return; }
      list = brand ? res.filter((r) => r.p.m === brand) : res;
      const n = list.length, w = plural(n, 'товар', 'товари', 'товарів');
      cnt.textContent = (q ? 'Знайдено ' : '') + fmtN(n) + ' ' + w + (brand ? ' · ' + brand : '');
      nf.classList.toggle('on', !n);
      nf.innerHTML = n ? '' : 'Нічого не знайдено за «' + escH(raw) + '»' + (brand ? ' у ' + escH(brand) : '')
        + '. Якщо потрібної деталі немає в&#160;каталозі, доставимо її під&#160;замовлення: <a href="tel:+380982430862">+38 (098) 243-08-62</a> або <a href="#order">залиште заявку</a>.';
      grid.innerHTML = ''; shown = 0; page();
    }
    let tm = 0;
    inp.addEventListener('input', () => { clearTimeout(tm); tm = setTimeout(run, 150); });
    inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') { clearTimeout(tm); run(); } });
    sec.querySelectorAll('[data-pick],[data-focusq]').forEach((b) => b.addEventListener('click', () => setTimeout(run, 0)));
    fl.forEach((a) => a.addEventListener('click', () => {
      brand = a.dataset.b;
      fl.forEach((x) => x.classList.toggle('on', x === a));
      run();
    }));
    more.addEventListener('click', page);
  });

  // рядок логотипів: стрілки й автопрокрутка, пауза під мишею
  document.querySelectorAll('.lgs').forEach((st) => {
    const trk = st.querySelector('.lgk'), n = trk.children.length;
    let i = 0, t = 0, hover = false;
    const per = () => (matchMedia('(max-width: 899px)').matches ? 2 : 6);
    const show = () => { const mx = n - per(); if (i > mx) i = 0; if (i < 0) i = mx; trk.style.transform = 'translateX(' + (-i * 100 / per()) + '%)'; };
    const next = () => { clearTimeout(t); t = setTimeout(() => { if (!hover) { i++; show(); } next(); }, 3200); };
    st.querySelectorAll('[data-bs]').forEach((b) => b.addEventListener('click', () => { i += +b.dataset.bs; show(); next(); }));
    st.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') hover = true; });
    st.addEventListener('pointerleave', () => { hover = false; });
    window.addEventListener('resize', show);
    show(); next();
  });

  // картки «Умов роботи» й картка бренду в героях: клік по картці — як по її посиланню
  document.querySelectorAll('.facts .fc, .v3h .hp').forEach((c) => c.addEventListener('click', (e) => {
    if (e.target.closest('a')) return;
    const a = c.querySelector('.fln, .hpl');
    if (a) a.click();
  }));

  // блок замовлення: координати кутів і приціл за курсором
  document.querySelectorAll('.ord').forEach((o) => {
    const set = () => {
      const w = Math.round(o.offsetWidth), h = Math.round(o.offsetHeight);
      const c = { tl: '[0,0]', tr: '[' + w + ',0]', bl: '[0,' + h + ']', br: '[' + w + ',' + h + ']' };
      o.querySelectorAll('.xy').forEach((x) => { x.textContent = c[x.dataset.c]; });
    };
    set();
    window.addEventListener('resize', set);
    const hh = o.querySelector('.xh.h'), hv = o.querySelector('.xh.v'), xl = o.querySelector('.xl');
    o.addEventListener('pointermove', (e) => {
      if (e.pointerType !== 'mouse') return;
      const b = o.getBoundingClientRect(), x = Math.round(e.clientX - b.left), y = Math.round(e.clientY - b.top);
      o.classList.add('xo');
      hh.style.transform = 'translateY(' + y + 'px)';
      hv.style.transform = 'translateX(' + x + 'px)';
      xl.style.transform = 'translate(' + (x + 10) + 'px,' + (y + 8) + 'px)';
      xl.textContent = '[' + x + ',' + y + ']';
    });
    o.addEventListener('pointerleave', () => o.classList.remove('xo'));
  });
})();
</script>
"""


SVG_CSS = r"""
/* підшипник у SVG */
.sgb{aspect-ratio:960/660}
.sgb>svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.sgb .ln{fill:none;stroke:#262826;stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1}
.sgb .ln.th{stroke-width:.9}
.sgb .ca{position:absolute;inset:0;pointer-events:none;z-index:4}
.sgb .ca .tg{pointer-events:auto}
.sgb .ca .tg,.sgb .ca .an{width:max-content}
.mob .sgb{width:120%;top:48%}
"""

SVG_JS = r"""
<script>
(function () {
  // підшипник у SVG: конічний роликопідшипник 35×72×18,25 за моделлю Blender (meridian-3d/scripts/meridian.py):
  // орто-камера 30°, дифузне світло з тим самим напрямком і toon-шкала «темний → середній → світлий» з м'якими переходами
  const NS = 'http://www.w3.org/2000/svg';
  const DEG = Math.PI / 180, CE = Math.cos(30 * DEG), SE = Math.sin(30 * DEG), K = 10;
  const TL = [236, 235, 230], TM = [207, 206, 200], TD = [156, 155, 150];
  const LV = (() => { const v = [-0.369, -0.240, 0.898], n = Math.hypot(v[0], v[1], v[2]); return v.map((x) => x / n); })();
  const VV = [0, -CE, SE];
  const VB = { x: -480, y: -425, w: 960, h: 660 }, CY = VB.y + VB.h / 2, ZOOM = 1.35;
  const P = (x, y, z) => [x * K, -(z * CE + y * SE) * K];
  const f1 = (v) => (Math.round(v * 10) / 10).toString();
  const poly = (pts, close) => pts.length ? 'M' + pts.map((p) => f1(p[0]) + ' ' + f1(p[1])).join('L') + (close ? 'Z' : '') : '';
  const arc = (r, z, a0, a1, n) => { n = n || Math.max(8, Math.round(Math.abs(a1 - a0) / (4 * DEG))); const o = []; for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; o.push(P(r * Math.cos(a), r * Math.sin(a), z)); } return o; };
  const ring = (r, z) => poly(arc(r, z, 0, 2 * Math.PI, 90), true);
  const ease = (x) => x * x * (3 - 2 * x);
  const seg = (t, a, b) => ease(Math.min(1, Math.max(0, (t - a) / (b - a))));
  const depth = (x, y, z) => y * CE - z * SE;
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const mix = (a, b, k) => a.map((x, i) => x + (b[i] - x) * k);
  const hex = (c) => '#' + c.map((x) => Math.round(x).toString(16).padStart(2, '0')).join('');
  function tone(v) {
    if (v <= .10) return TD;
    if (v < .15) return mix(TD, TM, (v - .10) / .05);
    if (v <= .55) return TM;
    if (v < .60) return mix(TM, TL, (v - .55) / .05);
    return TL;
  }

  // геометрія, мм
  const zA = 114.7, TH = 14 * DEG, Lm = 108.7, tanT = 4.3 / Lm, L1 = Lm - 6.75, L2 = Lm + 6.75, R1 = L1 * tanT, R2 = L2 * tanT, CH = .45;
  const THC = Math.asin((Lm * Math.sin(TH) - 1.44) / Lm), WIN = 9.7 * DEG, PITCH = 2 * Math.PI / 16;
  const cagePt = (L) => [L * Math.sin(THC), zA - L * Math.cos(THC)];
  const CG = { s: cagePt(L1 - 2.2), w0: cagePt(L1 - .3), w1: cagePt(L2 + .3), e: cagePt(L2 + 1.6) };

  function hull(pts) {
    const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const q of p) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (let i = p.length - 1; i >= 0; i--) { const q = p[i]; while (up.length > 1 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    return lo.slice(0, -1).concat(up.slice(0, -1));
  }
  // перетин опуклих многокутників (Сазерленд — Ходжмен)
  function clipConvex(subj, clip) {
    const ar = clip.reduce((a, p, i) => { const q = clip[(i + 1) % clip.length]; return a + p[0] * q[1] - q[0] * p[1]; }, 0), sg = ar > 0 ? 1 : -1;
    let out = subj;
    for (let i = 0; i < clip.length && out.length; i++) {
      const a = clip[i], b = clip[(i + 1) % clip.length], inp = out;
      const ins = (p) => sg * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) >= 0;
      const cut = (p, q) => { const d = (a[0] - b[0]) * (p[1] - q[1]) - (a[1] - b[1]) * (p[0] - q[0]); const t = ((a[0] - p[0]) * (p[1] - q[1]) - (a[1] - p[1]) * (p[0] - q[0])) / d; return [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]; };
      out = [];
      for (let j = 0; j < inp.length; j++) {
        const p = inp[j], q = inp[(j + 1) % inp.length], pi = ins(p), qi = ins(q);
        if (pi) { out.push(p); if (!qi) out.push(cut(p, q)); } else if (qi) out.push(cut(p, q));
      }
    }
    return out;
  }
  const loop = (r, z) => arc(r, z, 0, 2 * Math.PI, 72).slice(0, -1);
  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  // нормаль смуги тіла обертання між (r0,z0) і (r1,z1); face = 1 назовні, -1 до осі
  function revNormal(r0, z0, r1, z1, face) {
    let nr = z1 - z0, nz = -(r1 - r0);
    const n = Math.hypot(nr, nz); nr /= n; nz /= n;
    if (Math.sign(nr) !== face && Math.abs(nr) > 1e-6) { nr = -nr; nz = -nz; }
    return [nr, nz];
  }
  // видима дуга (кути), де нормаль дивиться на камеру
  function visArc(nr, nz, a0, a1) {
    if (Math.abs(nr) < 1e-6) return nz > 0 ? [0, 2 * Math.PI] : null;
    const s = nz * SE / (nr * CE);
    if (nr > 0) { if (s >= 1) return [0, 2 * Math.PI]; if (s <= -1) return null; const q = Math.asin(s); return [Math.PI - q, 2 * Math.PI + q]; }
    if (s <= -1) return [0, 2 * Math.PI]; if (s >= 1) return null;
    const q = Math.asin(s); return [q, Math.PI - q];
  }

  function build(box) {
    const id = box.dataset.id, svg = box.querySelector('svg'), scn = svg.querySelector('.brs'), defs = svg.querySelector('defs');
    const clip = el('clipPath', { id: 'brv-' + id }, defs);
    const crect = el('rect', { x: VB.x - 200, y: CY, width: VB.w + 400, height: 0 }, clip);
    const lines = [], fills = [];
    let gid = 0;
    // видимість деталей крізь зовнішнє кільце: всередині — лише в отворі, нижче — в отворі й повз корпус
    const vis = {};
    for (const k of ['in', 'lo']) { const c = el('clipPath', { id: 'brc' + k + '-' + id }, defs); vis[k] = [el('path', {}, c), el('path', { 'clip-rule': 'evenodd' }, c)]; }
    const fill = (g, d, c, extra) => { const e = el('path', Object.assign({ d, fill: c, stroke: c, 'stroke-width': .6, 'stroke-linejoin': 'round', 'clip-path': 'url(#brv-' + id + ')' }, extra || {}), g); fills.push(e); return e; };
    const line = (g, d, thin) => { const e = el('path', { d, class: 'ln' + (thin ? ' th' : ''), pathLength: 1 }, g); lines.push(e); return e; };
    // смуга тіла обертання з градієнтом тону за кутом
    function rev(g, r0, z0, r1, z1, face, range) {
      const [nr, nz] = revNormal(r0, z0, r1, z1, face);
      let va = visArc(nr, nz);
      if (!va) return null;
      if (range) va = va[1] - va[0] >= 2 * Math.PI - 1e-6 ? range : [Math.max(va[0], range[0]), Math.min(va[1], range[1])];
      const [a0, a1] = va, rm = (r0 + r1) / 2, stops = [];
      for (let i = 0; i <= 48; i++) {
        const a = a0 + (a1 - a0) * i / 48;
        stops.push([rm * Math.cos(a) * K, tone(nr * (LV[0] * Math.cos(a) + LV[1] * Math.sin(a)) + nz * LV[2])]);
      }
      const xs = stops.map((s) => s[0]), x0 = Math.min(...xs), x1 = Math.max(...xs);
      const gr = el('linearGradient', { id: 'brg-' + id + '-' + (gid++), gradientUnits: 'userSpaceOnUse', x1: f1(x0), y1: 0, x2: f1(x1 > x0 ? x1 : x0 + 1), y2: 0 }, defs);
      stops.sort((a, b) => a[0] - b[0]).forEach((s) => el('stop', { offset: ((s[0] - x0) / (x1 - x0 || 1)).toFixed(4), 'stop-color': hex(s[1]) }, gr));
      const d = poly(arc(r0, z0, a0, a1).concat(arc(r1, z1, a1, a0)), true);
      fill(g, d, 'url(#' + gr.id + ')', { stroke: 'url(#' + gr.id + ')' });
      return [a0, a1];
    }
    const ann = (g, ri, ro, z) => fill(g, ring(ro, z) + ring(ri, z), hex(tone(LV[2])), { 'fill-rule': 'evenodd' });
    const arcLine = (g, r, z, va, thin) => { if (va) line(g, poly(arc(r, z, va[0], va[1])), thin); };
    const sil = (g, pts) => line(g, poly(pts));

    // зовнішнє кільце: задня частина (доріжка й фаска отвору), передня (торець, фаски, зовнішня стінка)
    const cupB = el('g', {}, scn), cupF = el('g', {}, scn);
    const lip = rev(cupB, 29.2, 18.25, 28.4, 17.35, -1);
    const race = rev(cupB, 28.4, 17.35, 32.4, 3.8, -1);
    const tclip = el('clipPath', { id: 'brt-' + id }, defs);
    el('path', { d: ring(29.2, 18.25) }, tclip);
    arcLine(cupB, 28.4, 17.35, lip, true);
    if (race) line(cupB, poly(arc(32.4, 3.8, race[0], race[1])), true).setAttribute('clip-path', 'url(#brt-' + id + ')');
    const wallV = rev(cupF, 36, 4.05, 36, 17.25, 1);
    const chT = rev(cupF, 36, 17.25, 35, 18.25, 1);
    const chB = rev(cupF, 35.2, 3.25, 36, 4.05, 1);
    ann(cupF, 29.2, 35, 18.25);
    line(cupF, ring(35, 18.25)); line(cupF, ring(29.2, 18.25));
    arcLine(cupF, 36, 17.25, chT, true); arcLine(cupF, 36, 4.05, wallV, true); arcLine(cupF, 35.2, 3.25, [Math.PI, 2 * Math.PI]);
    for (const s of [-1, 1]) sil(cupF, [P(s * 35.2, 0, 3.25), P(s * 36, 0, 4.05), P(s * 36, 0, 17.25), P(s * 35, 0, 18.25)]);

    // внутрішнє кільце (конус): силует тіла, бурт, доріжка, торець з фасками, отвір
    const cone = el('g', {}, scn);
    const prof = [[25.4, 0], [26, .6], [25.92, 2.18], [23.5, 1.58], [20.67, 15.17], [21.95, 15.45], [21.95, 16.5], [21.45, 17], [18.3, 17], [17.5, 16.2]];
    fill(cone, poly(hull(prof.flatMap(([r, z]) => arc(r, z, 0, 2 * Math.PI, 72))), true) + ring(17.5, .8), hex(TM), { 'fill-rule': 'evenodd' });
    rev(cone, 25.4, 0, 26, .6, 1);
    const ribW = rev(cone, 26, .6, 25.92, 2.18, 1);
    rev(cone, 25.92, 2.18, 23.5, 1.58, -1, [Math.PI - 10 * DEG, 2 * Math.PI + 10 * DEG]);
    const rw = rev(cone, 23.5, 1.58, 20.67, 15.17, 1);
    rev(cone, 21.95, 15.45, 21.95, 16.5, 1);
    const cTop = rev(cone, 21.95, 16.5, 21.45, 17, 1);
    ann(cone, 18.3, 21.45, 17);
    const bch = rev(cone, 18.3, 17, 17.5, 16.2, -1);
    const bore = rev(cone, 17.5, 16.2, 17.5, .8, -1);
    line(cone, ring(21.45, 17)); line(cone, ring(18.3, 17));
    arcLine(cone, 21.95, 16.5, cTop, true); arcLine(cone, 21.95, 15.45, [Math.PI, 2 * Math.PI], true); arcLine(cone, 20.67, 15.17, rw, true);
    arcLine(cone, 23.5, 1.58, rw, true); arcLine(cone, 25.92, 2.18, [Math.PI - 10 * DEG, 2 * Math.PI + 10 * DEG], true);
    arcLine(cone, 26, .6, ribW, true); arcLine(cone, 25.4, 0, [Math.PI, 2 * Math.PI]);
    arcLine(cone, 17.5, 16.2, bch, true); arcLine(cone, 17.5, .8, bore, true);
    for (const s of [-1, 1]) sil(cone, [P(s * 25.4, 0, 0), P(s * 26, 0, .6), P(s * 25.92, 0, 2.18), P(s * 23.5, 0, 1.58), P(s * 20.67, 0, 15.17), P(s * 21.95, 0, 15.45), P(s * 21.95, 0, 16.5), P(s * 21.45, 0, 17)]);

    // сепаратор: 16 нерухомих секторів ободів, фланець і 16 перемичок, що обертаються; кожен — окремий шар для сортування
    const cageSec = [];
    for (let k = 0; k < 16; k++) {
      const a0 = k * PITCH, a1 = a0 + PITCH, am = a0 + PITCH / 2, g = el('g', {}, scn);
      for (const [p0, p1] of [[CG.s, CG.w0], [CG.w1, CG.e]]) {
        const [nr, nz] = revNormal(p0[0], p0[1], p1[0], p1[1], 1);
        const nOut = [nr * Math.cos(am), nr * Math.sin(am), nz], face = dot(nOut, VV) > 0 ? 1 : -1;
        const c = hex(tone(dot(nOut.map((x) => x * face), LV)));
        fill(g, poly(arc(p0[0], p0[1], a0, a1, 6).concat(arc(p1[0], p1[1], a1, a0, 6)), true), c);
        line(g, poly(arc(p0[0], p0[1], a0, a1, 6)), true);
        line(g, poly(arc(p1[0], p1[1], a0, a1, 6)), true);
      }
      cageSec.push({ g, d: depth(24 * Math.cos(am), 24 * Math.sin(am), 9) });
    }
    const flange = el('g', {}, scn);
    fill(flange, ring(CG.s[0], CG.s[1]) + ring(CG.s[0] - 2.8, CG.s[1] + .3), hex(TL), { 'fill-rule': 'evenodd' });
    line(flange, ring(CG.s[0] - 2.8, CG.s[1] + .3), true); line(flange, ring(CG.s[0], CG.s[1]), true);
    const bridges = [];
    for (let i = 0; i < 16; i++) { const g = el('g', {}, scn); bridges.push({ g, f: fill(g, '', hex(TM)), l: line(g, '', true) }); }

    // ролики: конічні, вісь нахилена на 14°, грані з тоном за нормаллю, малий торець з фаскою
    const rolls = [];
    for (let i = 0; i < 16; i++) {
      const g = el('g', {}, scn), faces = [];
      for (let j = 0; j < 16; j++) faces.push(fill(g, '', hex(TM)));
      const chf = fill(g, '', hex(TL)), cap = fill(g, '', hex(TL));
      rolls.push({ g, faces, cap, chf, out: line(g, ''), capl: line(g, '', true), chl: line(g, '') });
    }
    return { box, svg, scn, crect, lines, fills, cupB, cupF, cone, cageSec, flange, bridges, rolls, vis, order: [] };
  }

  function rollerGeo(phi, k) {
    const er = [Math.cos(phi), Math.sin(phi), 0];
    const uw = [Math.sin(TH) * er[0], Math.sin(TH) * er[1], -Math.cos(TH)];
    const m = Math.hypot(uw[1], uw[0]), e1 = [uw[1] / m, -uw[0] / m, 0];
    const e2 = [uw[1] * e1[2] - uw[2] * e1[1], uw[2] * e1[0] - uw[0] * e1[2], uw[0] * e1[1] - uw[1] * e1[0]];
    const od = [Math.cos(TH) * er[0] * k, Math.cos(TH) * er[1] * k, Math.sin(TH) * k];
    const N = 16;
    const circ = (L, rho) => {
      const c = [L * uw[0] + od[0], L * uw[1] + od[1], zA + L * uw[2] + od[2]], pts = [];
      for (let j = 0; j < N; j++) {
        const t = 2 * Math.PI * j / N, n = [Math.cos(t) * e1[0] + Math.sin(t) * e2[0], Math.cos(t) * e1[1] + Math.sin(t) * e2[1], Math.cos(t) * e1[2] + Math.sin(t) * e2[2]];
        pts.push({ p: P(c[0] + rho * n[0], c[1] + rho * n[1], c[2] + rho * n[2]), n });
      }
      return { c, pts };
    };
    const a = circ(L1 + CH, R1), b = circ(L2 - CH, R2), cap = circ(L1, R1 - CH);
    const faces = [];
    for (let j = 0; j < N; j++) {
      const j2 = (j + 1) % N, n = a.pts[j].n.map((x, q) => (x + a.pts[j2].n[q]) / 2);
      if (dot(n, VV) <= 0) { faces.push(null); continue; }
      faces.push({ d: poly([a.pts[j].p, a.pts[j2].p, b.pts[j2].p, b.pts[j].p], true), c: hex(tone(dot(n, LV))) });
    }
    const capN = uw.map((x) => -x);
    const chN = capN.map((x, q) => x * .7);
    const mid = [(a.c[0] + b.c[0]) / 2, (a.c[1] + b.c[1]) / 2, (a.c[2] + b.c[2]) / 2];
    return {
      faces, out: hull(a.pts.concat(b.pts, cap.pts).map((x) => x.p)), cap: cap.pts.map((x) => x.p), rim: a.pts.map((x) => x.p),
      capTone: hex(tone(dot(capN, LV))), chTone: hex(tone(dot(chN, LV) + .1)), capC: cap.c, mid,
    };
  }

  // пози за часом (с від кінця проявлення), цикл 8 с — як у рендері Blender
  const e13 = ease(1 / 3);
  function spin(t) {
    if (t < 2) return 22.5 * (ease((t + 1) / 3) - e13);
    if (t < 7) return 22.5 * (1 - e13);
    return 22.5 * (1 - e13) + 22.5 * ease((t - 7) / 3);
  }
  function pose(t) {
    t = ((t % 8) + 8) % 8;
    return {
      spin: spin(t) * DEG,
      cup: 20 * (seg(t, 2.0, 3.1) - seg(t, 5.9, 7.0)),
      cone: -20 * (seg(t, 2.8, 4.0) - seg(t, 5.0, 6.2)),
      roll: 2.5 * (seg(t, 2.2, 3.2) - seg(t, 5.8, 6.8)),
      zoom: seg(t, 1.8, 3.0) - seg(t, 5.9, 7.1),
    };
  }

  function bridge(a0, a1, face) {
    const [nr, nz] = [Math.cos(THC), Math.sin(THC)].map((x) => x * face);
    const am = (a0 + a1) / 2, n = [nr * Math.cos(am), nr * Math.sin(am), nz];
    if (dot(n, VV) <= 0) return null;
    return { d: poly(arc(CG.w0[0], CG.w0[1], a0, a1, 3).concat(arc(CG.w1[0], CG.w1[1], a1, a0, 3)), true), c: hex(tone(dot(n, LV))),
      l: poly([P(CG.w0[0] * Math.cos(a0), CG.w0[0] * Math.sin(a0), CG.w0[1]), P(CG.w1[0] * Math.cos(a0), CG.w1[0] * Math.sin(a0), CG.w1[1])]) +
         poly([P(CG.w0[0] * Math.cos(a1), CG.w0[0] * Math.sin(a1), CG.w0[1]), P(CG.w1[0] * Math.cos(a1), CG.w1[0] * Math.sin(a1), CG.w1[1])]) };
  }

  function render(S, q) {
    const s = 1 / (1 + (ZOOM - 1) * q.zoom);
    S.scn.setAttribute('transform', 'translate(0 ' + f1(CY) + ') scale(' + s.toFixed(4) + ') translate(0 ' + f1(-CY) + ')');
    const dy = (dz) => 'translate(0 ' + f1(-dz * CE * K) + ')';
    S.cupB.setAttribute('transform', dy(q.cup)); S.cupF.setAttribute('transform', dy(q.cup)); S.cone.setAttribute('transform', dy(q.cone));
    const c0 = 3.25 + q.cup, eTop = clipConvex(loop(28.4, 17.35 + q.cup), loop(29.2, 18.25 + q.cup));
    const outside = 'M-3000 -3000H3000V3000H-3000Z' + poly(hull(loop(36, c0).concat(loop(36, 18.25 + q.cup))), true);
    S.vis.in[0].setAttribute('d', poly(eTop, true)); S.vis.in[1].setAttribute('d', outside);
    S.vis.lo[0].setAttribute('d', poly(clipConvex(eTop, loop(33.1, c0)), true)); S.vis.lo[1].setAttribute('d', outside);
    const vid = S.box.dataset.id;
    const occl = (g, zhi) => { const u = 'url(#brc' + (zhi <= c0 ? 'lo' : 'in') + '-' + vid + ')'; if (g.getAttribute('clip-path') !== u) g.setAttribute('clip-path', u); };
    occl(S.cone, 17 + q.cone); occl(S.flange, CG.s[1] + .3);
    S.cageSec.forEach((x) => occl(x.g, CG.s[1] + .3));
    S.bridges.forEach((x) => occl(x.g, CG.w0[1]));
    const coneD = depth(0, 0, 17 + q.cone);
    const items = [
      { g: S.cupB, d: depth(0, 32.4, 3.8 + q.cup) },
      { g: S.cupF, d: depth(0, -36, 10.75 + q.cup) },
      { g: S.cone, d: coneD },
      { g: S.flange, d: coneD - .1 },
    ].concat(S.cageSec);
    // перемички сепаратора
    S.bridges.forEach((b, i) => {
      const c = q.spin + i * PITCH, a0 = c + WIN, a1 = c + PITCH - WIN, am = (a0 + a1) / 2;
      const f = bridge(a0, a1, 1) || bridge(a0, a1, -1);
      b.f.setAttribute('d', f ? f.d : ''); b.l.setAttribute('d', f ? f.l : '');
      if (f) { b.f.setAttribute('fill', f.c); b.f.setAttribute('stroke', f.c); }
      items.push({ g: b.g, d: depth(24.9 * Math.cos(am), 24.9 * Math.sin(am), 9) });
    });
    S.geo = [];
    S.rolls.forEach((r, i) => {
      const g = rollerGeo(2 * Math.PI * i / 16 + q.spin, q.roll);
      S.geo.push(g);
      g.faces.forEach((f, j) => { const e = r.faces[j]; e.setAttribute('d', f ? f.d : ''); if (f) { e.setAttribute('fill', f.c); e.setAttribute('stroke', f.c); } });
      r.chf.setAttribute('d', poly(g.rim, true)); r.chf.setAttribute('fill', g.chTone); r.chf.setAttribute('stroke', g.chTone);
      r.cap.setAttribute('d', poly(g.cap, true)); r.cap.setAttribute('fill', g.capTone); r.cap.setAttribute('stroke', g.capTone);
      r.out.setAttribute('d', poly(g.out, true));
      r.chl.setAttribute('d', poly(g.rim, true));
      r.capl.setAttribute('d', poly(g.cap, true));
      items.push({ g: r.g, d: depth(g.mid[0], g.mid[1], g.mid[2]) });
      occl(r.g, g.capC[2] + R1);
    });
    items.sort((a, b) => b.d - a.d);
    if (items.some((it, i) => S.order[i] !== it.g)) { items.forEach((it) => S.scn.appendChild(it.g)); S.order = items.map((it) => it.g); }
    // виноски йдуть за деталями
    const toBox = (p, dz) => { const X = p[0] * s, Y = CY + (p[1] - dz * CE * K - CY) * s; return [(X - VB.x) / VB.w * 100, (Y - VB.y) / VB.h * 100]; };
    const near = S.geo.reduce((best, g, i) => { const a = Math.atan2(g.capC[1], g.capC[0]); const d = Math.abs(Math.atan2(Math.sin(a - 150 * DEG), Math.cos(a - 150 * DEG))); return d < best.d ? { d, i } : best; }, { d: 9, i: 0 });
    const cc = S.geo[near.i].capC;
    const A = {
      cupF: toBox(P(36 * Math.cos(300 * DEG), 36 * Math.sin(300 * DEG), 10.75), q.cup),
      cupT: toBox(P(32.6 * Math.cos(62 * DEG), 32.6 * Math.sin(62 * DEG), 18.25), q.cup),
      roll: toBox(P(cc[0], cc[1], cc[2]), 0),
      cone: toBox(P(19.9 * Math.cos(245 * DEG), 19.9 * Math.sin(245 * DEG), 17), q.cone),
    };
    S.box.querySelectorAll('.ca').forEach((w) => {
      const [x, y] = A[w.dataset.a];
      w.querySelectorAll('.mk,.an').forEach((e) => { e.style.left = x.toFixed(2) + '%'; e.style.top = y.toFixed(2) + '%'; });
      w.querySelectorAll('.tg').forEach((e) => { e.style.left = 'calc(' + x.toFixed(2) + '% ' + (e.classList.contains('lf') ? '- ' : '+ ') + '8px)'; e.style.top = y.toFixed(2) + '%'; });
    });
  }

  document.querySelectorAll('.sgb').forEach((box) => {
    const S = build(box), sec = box.closest('.sv');
    render(S, pose(0));
    let t0 = null, raf = 0, on = true, loop = 0, last = 0, still = null;
    const DRAW = [.2, 1.8], REV = [1.8, 2.9];
    const reveal = () => {
      if (S.done) return;
      S.done = true;
      S.fills.forEach((e) => { if (e.getAttribute('clip-path') === 'url(#brv-' + box.dataset.id + ')') e.removeAttribute('clip-path'); });
      S.lines.forEach((e) => { e.style.strokeDashoffset = '0'; });
    };
    function frame(now) {
      raf = 0;
      if (t0 === null) t0 = now;
      const t = (now - t0) / 1000;
      if (still !== null) { reveal(); render(S, pose(still)); return; }
      if (t < REV[1] + .05) {
        S.lines.forEach((e, i) => { const k = Math.min(1, Math.max(0, (t - DRAW[0] - (i % 12) * .03) / (DRAW[1] - DRAW[0] - .3))); e.style.strokeDashoffset = (1 - ease(k)).toFixed(3); });
        const r = ease(Math.min(1, Math.max(0, (t - REV[0]) / (REV[1] - REV[0])))), h = r * (VB.h + 40);
        S.crect.setAttribute('y', f1(CY - h / 2)); S.crect.setAttribute('height', f1(h));
      } else {
        reveal();
        loop += Math.min(.1, (now - last) / 1000);
        render(S, pose(loop));
      }
      last = now;
      if (on) raf = requestAnimationFrame(frame);
    }
    const start = () => { if (!raf && on) { last = performance.now(); raf = requestAnimationFrame(frame); } };
    // зупинити на моменті циклу (для порівняння з кадрами рендера): box.brgPose(4.5)
    box.brgPose = (t) => { still = t; on = true; start(); };
    const io = new IntersectionObserver((es) => es.forEach((e) => { on = e.isIntersecting; if (on && sec.classList.contains('in')) start(); }), { rootMargin: '200px 0px' });
    io.observe(box);
    new MutationObserver(() => { if (sec.classList.contains('in')) start(); }).observe(sec, { attributes: true, attributeFilter: ['class'] });
    if (sec.classList.contains('in')) start();
  });
})();
</script>
"""


def build(mode):
    page = src
    title = 'прототип v2' if mode == 'svg' else 'прототип v2 · відео'
    page = sub1(r'<title>.*?</title>', f'<title>Meridian Parts · каталог запчастин · {title}</title>', page, 1)
    dsk, mob = page.index('<div class="dsk">'), page.index('<div class="mob">')
    head, d, m = page[:dsk], page[dsk:mob], page[mob:]
    page = head + part(d, False, mode) + part(m, True, mode)
    js = JS.replace('PHOTO_IDS_JSON', json.dumps(PHOTO_IDS)) + (SVG_JS if mode == 'svg' else '')
    css = CSS + (SVG_CSS if mode == 'svg' else '')
    page = sub1(r'</style>', lambda _: css + '</style>', page, 1)
    page = sub1(r'</script>\s*</body>', lambda _: '</script>' + js + '</body>', page, 1)
    page = sub1(r'\. Wikimedia Commons, CC BY-SA 3\.0 / 4\.0</div>', lambda _: (
        '. Wikimedia Commons, CC BY-SA 3.0 / 4.0. Логотипи BEDNAR і OLIMAC: '
        '<a href="https://commons.wikimedia.org/wiki/File:BEDNAR_logo_2019_RGB.jpg" target="_blank" rel="noopener">Cz-bd-1</a>, '
        '<a href="https://commons.wikimedia.org/wiki/File:OLIMAC_LOGO.png" target="_blank" rel="noopener">Agromacintosh</a>, '
        'Wikimedia Commons, CC BY-SA 4.0. Логотипи виробників — торгові марки їхніх власників.</div>'), page, 2)
    n_order = page.count('<span class="m">Замовити</span>')
    assert n_order >= 16, n_order
    page = page.replace('<span class="m">Замовити</span>', '<span class="m">' + roll('Замовити') + '</span>')
    link = ('<a class="vlk" href="v1.html">перша версія прототипу →</a> · <a class="vlk" href="video.html">версія з відео →</a>' if mode == 'svg'
            else '<a class="vlk" href="./">головна →</a>')
    page = sub1(r'© 2026 Meridian Parts', '© 2026 Meridian Parts · ' + link, page, 2)
    return page


for mode, name in (('svg', 'index.html'), ('video', 'video.html')):
    out = build(mode)
    (ROOT / name).write_text(out, encoding='utf-8')
    print(name, len(out))
