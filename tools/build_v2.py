"""Збирає v2.html з index.html.

Зміни v2: герой «креслення → рендер → відео підшипника», бренди «креслення → кольорове фото» з єдиним грейдом,
закріплений під час прокрутки блок «Послуги», ізометричні іконки в «Умовах роботи», стрічка виробників зі стрілками,
координати й приціл у блоці замовлення, зерно паперу.

python tools/build_v2.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'index.html').read_text(encoding='utf-8')

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


ICONS = [icon_ring(), icon_box(), icon_sheets(), icon_nut()]

# ---------- «Послуги» ----------
STEPS = [
    dict(k='Постачання', h=['Постачання', 'запчастин'], img='gear', alt='Шестерня',
         p='Прямі поставки від виробників: оптимальні ціни та швидкість доставки. Понад 20&#160;000 позицій на&#160;складах.',
         tag=(84, 50, 'Шестерні · 14'), an=(40, 33, ['Шпонковий паз', 'z = 24']), mt=(30, 30, 'Шестерні · 14')),
    dict(k='Консультації', h=['Консультації'], img='bearing', alt='Роликовий підшипник',
         p='Немає номера? Назвіть марку й&#160;модель техніки. Менеджер підбере деталь і&#160;підкаже, що ще варто замінити.',
         tag=(85, 52, 'Підшипники · 85'), an=(27, 44, ['Ролики циліндричні', '× 16']), mt=(30, 32, 'Підшипники · 85')),
    dict(k='Установка', h=['Установка', 'запчастин'], img='sprocket', alt='Зірочка',
         p='Діагностуємо, дефектуємо й&#160;ставимо деталі. Ремонтуємо John Deere: двигуни, коробки передач, мости, ТНВД, гідравліку.',
         tag=(85, 48, 'Зірочки · 13'), an=(38, 40, ['Зірочка ланцюгова', 'z = 15']), mt=(30, 33, 'Зірочки · 13')),
]


def story(mob):
    n = len(STEPS)
    hs, pts, hdr, txt, prg = [], [], [], [], []
    for i, s in enumerate(STEPS):
        on = ' on' if i == 0 else ''
        lines = ''.join(f'<span class="ln"><span style="--i: {j};">{w}</span></span>' for j, w in enumerate(s['h']))
        hs.append(f'<h2 class="stt{on}">{lines}</h2>')
        if mob:
            x, y, t = s['mt']
            marks = tag(x, y, t, .35)
        else:
            marks = tag(*s['tag'][:2], s['tag'][2], .35) + an(*s['an'][:2], s['an'][2], .6, left=True)
        pts.append(f'<div class="spt{on}"><img class="spl" src="assets/v2/t-{s["img"]}-l.webp" alt="" loading="lazy" decoding="async">'
                   f'<img class="spr" src="assets/v2/t-{s["img"]}.webp" alt="{s["alt"]}" loading="lazy" decoding="async">'
                   f'<span class="sbd"><span class="sbp m"></span></span>{marks}</div>')
        hdr.append(f'<span class="scn{on}">[0{i + 1}] {s["k"]}</span>')
        txt.append(f'<p class="sct{on}">{s["p"]}</p>')
        prg.append(f'<div class="spr2{" on" if i == 0 else ""}"><span class="m">0{i + 1} {s["k"]}</span><i><b></b></i></div>')
    crs = ''.join(f'<span class="cr" style="{a}: 10px; {b}: 8px;">+</span>' for a in ('left', 'right') for b in ('top', 'bottom'))
    return (f'<section class="story" data-sec=""><span class="sl"></span><div class="sto"><div class="stk">'
            f'<span class="ru h t"></span><span class="ru h b"></span><span class="ru v l"></span><span class="ru v r"></span>{crs}'
            f'<span class="scl h"></span><span class="scl v"></span>'
            f'<div class="slab m"><span>[06] Послуги</span><span class="g">Працюємо з людьми та для людей</span></div>'
            f'<div class="scnt m">01 / 0{n}</div>'
            f'<div class="shd">{"".join(hs)}</div><div class="svis">{"".join(pts)}</div>'
            f'<div class="scd"><div class="sch m">{"".join(hdr)}</div><div class="scb">{"".join(txt)}</div>'
            f'<div class="scf m g">[Гортайте далі]</div></div>'
            f'<div class="spg">{"".join(prg)}</div>'
            f'</div></div></section>')


# ---------- герой ----------
def hero_stage(mob):
    if mob:
        marks = tag(60, 24, 'Підшипники · 85', 3.9, left=True)
    else:
        marks = (tag(25, 66, 'Підшипники · 85', 3.9, left=True)
                 + an(29.5, 42, ['Ролики циліндричні × 16', 'поз. 01'], 4.1, left=True)
                 + an(64, 24.5, ['Кільце зовнішнє', 'поз. 02'], 4.25)
                 + an(66.5, 44, ['Кільце внутрішнє', 'поз. 03'], 4.4))
    return ('<div class="lay l" aria-hidden="true"><div class="stage"><img class="b3" src="assets/v2/bearing-l.webp" alt="" '
            'width="1600" height="1000" fetchpriority="high" decoding="async"></div></div>'
            '<div class="lay r"><div class="stage"><img class="b3" src="assets/v2/bearing.webp" '
            'alt="Роликовий підшипник, технічна ілюстрація" width="1600" height="1000" decoding="async">'
            '<video class="b3 b3v" muted playsinline loop preload="none" aria-hidden="true" '
            'data-src="assets/v2/bearing-1600.webm" data-src-m="assets/v2/bearing-960.webm"></video>'
            f'{marks}</div></div><span class="bnd2 u"></span><span class="bnd2 d"></span>')


# ---------- заміни ----------
def sub1(pattern, repl, s, count, flags=re.S):
    out, n = re.subn(pattern, repl, s, flags=flags)
    assert n == count, (pattern[:60], n, count)
    return out


page = src
page = sub1(r'<title>.*?</title>', '<title>Meridian Parts · каталог запчастин · прототип v2</title>', page, 1)
page = sub1(r'<section class="hero">', '<section class="hero v2h">', page, 2)

dsk, mob = page.index('<div class="dsk">'), page.index('<div class="mob">')
head, d, m = page[:dsk], page[dsk:mob], page[mob:]


def part(s, is_mob):
    s = sub1(r'<div class="stage">.*?</div>(?=<span class="pgl">)', lambda _: hero_stage(is_mob), s, 1)
    if not is_mob:
        s = sub1(r'Вид спереду · розріз А–А', 'Ізометрія · підшипник роликовий', s, 1)
    s = sub1(r'<div class="mq" data-sec="">.*?</div></div>', lambda _: (
        '<div class="bstr" data-sec=""><span class="sl"></span><div class="bsh"><span class="m">Виробники в&#160;каталозі</span>'
        '<span class="bsa"><button type="button" class="slb bsb" data-bs="-1" aria-label="Попередні виробники">' + ARROW + '</button>'
        '<button type="button" class="slb" data-bs="1" aria-label="Наступні виробники">' + ARROW + '</button></span></div>'
        '<div class="bsv"><div class="bsk"></div></div>'
        '<div class="bsf m g">Оригінальні деталі та&#160;аналоги · John Deere, Bednar, Geringhoff, CLAAS та&#160;інші</div></div>'), s, 1)
    s = sub1(r'<div class="bph">', '<div class="bph bv">', s, 2)
    s = sub1(r'<a href="#" class="bsp">', '<a href="#" class="bsp bv">', s, 5)
    s = sub1(r'<img src="assets/bp-(\w+)\.webp" alt="([^"]*)">', lambda mm: (
        f'<img class="bl" src="assets/v2/bp-{mm[1]}-l.webp" alt="" loading="lazy" decoding="async">'
        f'<img class="bc" src="assets/v2/bp-{mm[1]}.webp" alt="{mm[2]}" loading="lazy" decoding="async">'
        f'<span class="bpl"></span><span class="bnd u"></span><span class="bnd d"></span><span class="bpn m"></span>'
        f'<span class="bcp m">{mm[2]}</span>'), s, 7)
    s = sub1(r'(?=<section class="facts")', lambda _: story(is_mob), s, 1)
    s = sub1(r'\[06\] Умови роботи', '[07] Умови роботи', s, 1)
    s = sub1(r'\[07\] Під замовлення', '[08] Під замовлення', s, 1)
    it = iter(ICONS)
    s = sub1(r'<div class="fb">', lambda _: '<div class="fb">' + next(it), s, 4)
    s = sub1(r'(<section class="ord rv-ln"[^>]*>)', lambda mm: mm[1] + (
        '<span class="xy m" data-c="tl"></span><span class="xy m" data-c="tr"></span>'
        '<span class="xy m" data-c="bl"></span><span class="xy m" data-c="br"></span>'
        '<span class="xh h"></span><span class="xh v"></span><span class="xl m"></span>'), s, 1)
    return s


page = head + part(d, False) + part(m, True)

GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .15 0 0 0 0 .16 0 0 0 0 .15 .9 0 0 0 -.36'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")

CSS = r"""
/* ===== v2 ===== */
.dw::after{content:'';position:fixed;inset:0;z-index:60;pointer-events:none;background-image:url("GRAIN");background-size:220px 220px;opacity:.38}
a.vlk{text-decoration:underline;text-decoration-color:var(--line2);text-underline-offset:3px}
a.vlk:hover{color:var(--ink)}
/* герой: креслення → рендер → відео */
.v2h .stage{width:min(1040px,84%);aspect-ratio:16/10}
.lay{position:absolute;inset:0}
.lay.l{pointer-events:none;clip-path:inset(0 100% 0 0);animation:lnr 2.3s cubic-bezier(.65,.05,.3,1) .15s forwards}
.lay.r{clip-path:inset(63% 0 37% 0);animation:rvl 1.2s cubic-bezier(.65,.05,.3,1) 2.45s forwards}
@keyframes lnr{to{clip-path:inset(0 0 0 0)}}
@keyframes rvl{to{clip-path:inset(0 0 0 0)}}
.b3{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;display:block}
.b3v{opacity:0;transition:opacity .25s}
.v2h.vid .b3v{opacity:1}
.v2h.vid .lay.r img.b3{opacity:0;transition:opacity .25s .2s}
.v2h.vid .lay.l{opacity:.35;transition:opacity 1s}
.bnd2{position:absolute;left:0;right:0;top:63%;height:1px;background:var(--acc);opacity:0;z-index:3;pointer-events:none;animation:1.2s cubic-bezier(.65,.05,.3,1) 2.45s forwards}
.bnd2.u{animation-name:bnU}.bnd2.d{animation-name:bnD}
@keyframes bnU{0%{opacity:1}85%{opacity:1}to{top:0;opacity:0}}
@keyframes bnD{0%{opacity:1}85%{opacity:1}to{top:100%;opacity:0}}
.v2h .mk,.v2h .tg,.v2h .an{transition:opacity .35s}
.v2h.ex .lay.r .mk,.v2h.ex .lay.r .tg,.v2h.ex .lay.r .an{opacity:0;pointer-events:none}
/* технічні виноски */
.an{position:absolute;z-index:4;display:flex;align-items:center;transform:translateY(-50%);clip-path:inset(0 100% 0 0);animation:wipe .7s cubic-bezier(.6,.05,.3,1) forwards;animation-delay:var(--d)}
.an.lf{flex-direction:row-reverse;transform:translate(-100%,-50%);clip-path:inset(0 0 0 100%)}
.an i{width:8px;height:8px;margin:0 -4px;background:var(--acc);flex-shrink:0;position:relative;z-index:1}
.an .al{width:40px;height:1px;background:var(--ink)}
.an .at{padding:3px 6px;background:var(--paper);font-size:10.5px;line-height:1.4;color:var(--grey);white-space:nowrap;border-left:1px solid var(--ink)}
.an.lf .at{border-left:0;border-right:1px solid var(--ink);text-align:right}
.mob .v2h .stage{width:128%;aspect-ratio:16/10;top:54%}
/* бренди: креслення → кольорове фото */
.bv img{filter:none;mix-blend-mode:normal}
.bv .bl,.bv .bc{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bph.bv .bl,.bsp.bv .bl{clip-path:none}
.bv .bc{animation:bcR 1.1s cubic-bezier(.65,.05,.3,1) .9s both paused}
@keyframes bcR{from{clip-path:inset(50% 0 50% 0)}to{clip-path:inset(0 0 0 0)}}
.bcell:hover .bph.bv img,.bsc:hover .bsp.bv img{filter:none;transform:scale(1.03)}
.bv .bpl{position:absolute;left:0;right:0;top:50%;height:1px;background:var(--acc);transform-origin:left;transform:scaleX(0);z-index:2;animation:pg .9s cubic-bezier(.65,.05,.3,1) forwards paused,fadeOut .2s .95s forwards paused}
.bv .bnd{position:absolute;left:0;right:0;top:50%;height:1px;background:var(--acc);opacity:0;z-index:2;animation:1.1s cubic-bezier(.65,.05,.3,1) .9s forwards paused}
.bv .bnd.u{animation-name:bnU}.bv .bnd.d{animation-name:bnD}
.bv .bpn{position:absolute;left:10px;top:calc(50% - 22px);z-index:2;padding:1px 4px;background:var(--paper);counter-reset:n var(--n);animation:cnt .9s cubic-bezier(.65,.05,.3,1) forwards paused,fadeOut .2s .95s forwards paused}
.bv .bpn::after{content:counter(n) '%'}
.bv .bcp{position:absolute;left:10px;bottom:10px;z-index:2;padding:3px 6px;background:var(--paper);font-size:10.5px;opacity:0;transition:opacity .5s 2s}
.bsp.bv .bcp{display:none}
.bcell.in .bv>*,.bsc.in .bv>*{animation-play-state:running}
.bcell.in .bv .bcp{opacity:1}
.bph.bv .mk,.bph.bv .tg{animation-delay:calc(var(--d) + .8s)}
/* стрічка виробників */
.bstr{position:relative}
.bsh{display:flex;align-items:center;justify-content:space-between;padding:8px 8px 8px 20px;border-bottom:1px solid var(--line)}
.bsa{display:flex;gap:6px}
.bsa .slb{transition:background .25s,color .25s}
.bsa .slb:hover{background:var(--ink);color:var(--paper)}
.bsb .ico{transform:rotate(180deg)}
.bsv{overflow:hidden}
.bsk{display:flex;transition:transform .8s cubic-bezier(.6,.05,.3,1)}
.bsc2{flex:0 0 20%;height:104px;display:flex;flex-direction:column;justify-content:center;gap:6px;padding:0 20px;border-right:1px solid var(--line);transition:background .25s}
.bsc2 b{font-size:26px;font-weight:700;letter-spacing:-.035em;text-transform:uppercase;line-height:1.1;white-space:nowrap}
.bsc2:hover{background:var(--p2)}
.bsf{padding:9px 20px;border-top:1px solid var(--line);font-size:11px}
.mob .bsh{padding:6px 6px 6px 16px}
.mob .bsc2{flex-basis:50%;height:84px;padding:0 16px}
.mob .bsc2 b{font-size:19px}
.mob .bsf{padding:8px 16px}
/* «Послуги»: закріплений блок */
.story{position:relative}
.sto{position:relative;height:340vh}
.stk{position:sticky;top:0;height:100vh;overflow:hidden;background-image:linear-gradient(rgba(38,40,38,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(38,40,38,.045) 1px,transparent 1px);background-size:32px 32px}
.stk .ru,.stk .cr{animation:none}
.scl{position:absolute;pointer-events:none;opacity:.7}
.scl.h{left:28px;right:28px;top:56%;height:1px;background:repeating-linear-gradient(90deg,var(--line2) 0 24px,transparent 24px 30px,var(--line2) 30px 33px,transparent 33px 39px)}
.scl.v{top:28px;bottom:28px;left:50%;width:1px;background:repeating-linear-gradient(180deg,var(--line2) 0 24px,transparent 24px 30px,var(--line2) 30px 33px,transparent 33px 39px)}
.slab{position:absolute;left:40px;top:34px;display:flex;flex-direction:column;gap:6px;z-index:3}
.scnt{position:absolute;right:40px;top:34px;z-index:3}
.shd{position:absolute;left:0;right:0;top:9vh;height:2.2em;font-size:clamp(40px,4.6vw,72px);z-index:3;pointer-events:none}
.stt{position:absolute;left:0;right:0;top:0;margin:0;text-align:center;font-size:1em;line-height:1;font-weight:700;letter-spacing:-.045em;text-transform:uppercase;opacity:0;transition:opacity .2s .55s}
.stt.on{opacity:1;transition-delay:0s}
.stt .ln>span{animation:none;transform:translateY(110%);transition:transform .8s cubic-bezier(.2,.7,.2,1);transition-delay:calc(var(--i,0)*90ms)}
.stt.on .ln>span{transform:none}
.stt.off .ln>span{transform:translateY(-110%)}
.svis{position:absolute;left:50%;top:57%;width:min(80vh,780px);aspect-ratio:1;transform:translate(-50%,-50%);z-index:2}
.spt{position:absolute;inset:0;opacity:0;visibility:hidden;transition:opacity .45s,visibility 0s .45s}
.spt.on{opacity:1;visibility:visible;transition:opacity .45s}
.spl,.spr{position:absolute;inset:0;width:100%;height:100%;display:block}
.spr{clip-path:inset(0 0 calc(100% - var(--y,0%)) 0)}
.sbd{position:absolute;left:-18%;right:-18%;top:var(--y,0%);height:1px;background:var(--acc);opacity:var(--bo,0);z-index:3;pointer-events:none}
.sbp{position:absolute;left:0;bottom:6px;padding:1px 4px;background:var(--paper)}
.spt .mk,.spt .tg,.spt .an{animation-play-state:paused}
.story.in .spt.on .mk,.story.in .spt.on .tg,.story.in .spt.on .an{animation-play-state:running}
.scd{position:absolute;left:40px;bottom:40px;width:340px;z-index:4;background:var(--paper);border:1px solid var(--ink)}
.sch{display:grid;background:var(--ink);color:var(--paper);padding:9px 12px}
.scb{display:grid;padding:14px 12px 16px}
.sch>span,.sct{grid-area:1/1;opacity:0;transform:translateY(8px);transition:opacity .35s,transform .45s cubic-bezier(.2,.7,.2,1)}
.sch>span.on,.sct.on{opacity:1;transform:none;transition-delay:.12s}
.sct{margin:0;font-size:15px;line-height:1.5}
.scf{padding:8px 12px;border-top:1px solid var(--line);font-size:11px}
.spg{position:absolute;right:40px;bottom:40px;width:260px;display:flex;flex-direction:column;gap:12px;z-index:4}
.spr2{display:flex;flex-direction:column;gap:6px;color:var(--grey);transition:color .3s}
.spr2.on{color:var(--ink)}
.spr2 i{display:block;height:2px;background:var(--line)}
.spr2 b{display:block;height:100%;background:var(--ink);transform-origin:left;transform:scaleX(var(--p,0))}
@media (max-width:1240px){.dsk .svis{left:56%}.hd .cart{padding:0 14px}.hd .msg{padding:0 4px}}
.mob .sto{height:320vh}
.mob .stk{height:100svh;background-size:24px 24px}
.mob .slab{left:14px;top:16px}
.mob .slab .g{display:none}
.mob .scnt{right:14px;top:16px}
.mob .stk .cr{display:none}
.mob .ord .xy{display:none}
.mob .shd{top:52px;font-size:34px}
.mob .svis{width:min(100vw,56svh);top:49%}
.mob .scd{left:8px;right:8px;bottom:8px;width:auto}
.mob .sct{font-size:14px}
.mob .spg{display:none}
.mob .scl.h{top:48%;left:14px;right:14px}
.mob .scl.v{top:14px;bottom:14px}
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
  const ARROW = "ARROW_SVG";
  const vis = (el) => el && el.getClientRects().length > 0;

  // герой: після проявлення рендера вмикається відео з альфою (Safari без альфи у WebM — лишається рендер)
  const ua = navigator.userAgent;
  const alphaOK = !(/Safari\//.test(ua) && !/(Chrome|Chromium|CriOS|Edg|Firefox|FxiOS)\//.test(ua));
  document.querySelectorAll('.v2h').forEach((h) => {
    const r = h.querySelector('.lay.r'), v = h.querySelector('.b3v');
    let ready = false, revealed = false, onScreen = true;
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
      if (!vis(h)) return;
      v.src = matchMedia('(max-width: 899px)').matches ? v.dataset.srcM : v.dataset.src;
      v.preload = 'auto';
      v.load();
    };
    if (document.readyState === 'complete') load(); else window.addEventListener('load', load, { once: true });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((es) => es.forEach((e) => {
        onScreen = e.isIntersecting;
        if (onScreen) go(); else v.pause();
      })).observe(h);
    }
  });

  // стрічка виробників: кількість товарів рахується з каталогу
  const cnt = {};
  CAT.forEach((p) => { cnt[p.m] = (cnt[p.m] || 0) + 1; });
  const brands = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a]);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  document.querySelectorAll('.bstr').forEach((st) => {
    const trk = st.querySelector('.bsk');
    trk.innerHTML = brands.map((b) => '<a href="#" class="bsc2"><b>' + esc(b) + '</b><span class="m g">'
      + fmtN(cnt[b]) + ' ' + plural(cnt[b], 'товар', 'товари', 'товарів') + '</span></a>').join('');
    let i = 0, t = 0, hover = false;
    const per = () => (matchMedia('(max-width: 899px)').matches ? 2 : 5);
    const show = () => { const mx = brands.length - per(); if (i > mx) i = 0; if (i < 0) i = mx; trk.style.transform = 'translateX(' + (-i * 100 / per()) + '%)'; };
    const next = () => { clearTimeout(t); t = setTimeout(() => { if (!hover) { i++; show(); } next(); }, 3200); };
    st.querySelectorAll('[data-bs]').forEach((b) => b.addEventListener('click', () => { i += +b.dataset.bs; show(); next(); }));
    st.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') hover = true; });
    st.addEventListener('pointerleave', () => { hover = false; });
    show(); next();
  });

  // «Послуги»: крок за прокруткою, смуга проявляє рендер деталі
  const ease = (x) => (x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
  const stories = Array.from(document.querySelectorAll('.story')).map((s) => ({
    sto: s.querySelector('.sto'), cur: -1, cnt: s.querySelector('.scnt'),
    tts: s.querySelectorAll('.stt'), pts: Array.from(s.querySelectorAll('.spt')),
    chs: s.querySelectorAll('.scn'), cts: s.querySelectorAll('.sct'), prs: s.querySelectorAll('.spr2'),
  }));
  let raf = 0;
  function upd() {
    raf = 0;
    const vh = window.innerHeight || 800;
    stories.forEach((o) => {
      const r = o.sto.getBoundingClientRect();
      if (!r.height || r.bottom < -vh || r.top > vh * 2) return;
      const n = o.pts.length;
      const p = Math.max(0, Math.min(.9999, -r.top / (r.height - vh)));
      const seg = p * n, i = Math.floor(seg), t = seg - i;
      if (i !== o.cur) {
        o.tts.forEach((e, k) => { e.classList.toggle('on', k === i); e.classList.toggle('off', k < i); });
        [o.pts, o.chs, o.cts, o.prs].forEach((l) => l.forEach((e, k) => e.classList.toggle('on', k === i)));
        o.pts.forEach((e, k) => { if (k !== i) { e.style.setProperty('--y', k < i ? '100%' : '0%'); e.style.setProperty('--bo', 0); } });
        o.cnt.textContent = '0' + (i + 1) + ' / 0' + n;
        o.cur = i;
      }
      const y = ease(Math.max(0, Math.min(1, (t - .06) / .6)));
      const pt = o.pts[i];
      pt.style.setProperty('--y', (y >= 1 ? 100 : 22 + y * 56).toFixed(2) + '%');
      pt.style.setProperty('--bo', y > 0 && y < 1 ? 1 : 0);
      pt.querySelector('.sbp').textContent = Math.round(y * 100) + '%';
      o.prs.forEach((e, k) => e.style.setProperty('--p', k < i ? 1 : k > i ? 0 : t.toFixed(3)));
    });
  }
  const req = () => { if (!raf) raf = requestAnimationFrame(upd); };
  window.addEventListener('scroll', req, { passive: true });
  window.addEventListener('resize', req);
  upd();

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
""".replace('ARROW_SVG', ARROW.replace('"', '\\"'))

page = sub1(r'</style>', lambda _: CSS + '</style>', page, 1)
page = sub1(r'</script>\s*</body>', lambda _: '</script>' + JS + '</body>', page, 1)
page = sub1(r'© 2026 Meridian Parts', '© 2026 Meridian Parts · <a class="vlk" href="index.html">прототип v2, перша версія →</a>', page, 2)
page = sub1(r'\[00\] Каталог запчастин<', '[00] Каталог запчастин · v2<', page, 1)
page = sub1(r'\[00\] Каталог · 1&#160;237 товарів', '[00] Каталог · v2', page, 1)

(ROOT / 'v2.html').write_text(page, encoding='utf-8')
print('v2.html', len(page))
