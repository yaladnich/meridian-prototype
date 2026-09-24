"""Ресурси для v2.html: кольоровий грейд фото брендів, логотипи виробників, креслення й рендери деталей, відео підшипника з альфою.

python tools/v2_assets.py            # усе
python tools/v2_assets.py brands     # лише фото брендів
"""
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC3D = Path('C:/Users/Yalad/meridian-3d')
OUT = ROOT / 'assets' / 'v2'
OUT.mkdir(parents=True, exist_ok=True)

BRANDS = ['jd', 'claas', 'bednar', 'geringhoff', 'olimac', 'kuhn', 'amazone']
TILES = ['gear', 'bearing', 'sprocket']
LOGOS_LUM = {'vaderstad', 'bednar'}
LOGOS = ['claas', 'geringhoff', 'horsch', 'kuhn', 'kverneland', 'amazone', 'parker', 'vaderstad', 'bednar', 'olimac', 'optibelt', 'schumacher']


def lum(a):
    return a[..., 0] * .2126 + a[..., 1] * .7152 + a[..., 2] * .0722


def grade(a):
    """Спільний грейд «чистий, соковитий»: насиченість ×1,12, м'яка S-крива 25 %, трохи холодніші тіні."""
    L = lum(a)[..., None]
    a = np.clip(L + (a - L) * 1.12, 0, 1)
    a = a * .75 + a * a * (3 - 2 * a) * .25
    L = lum(a)[..., None]
    return np.clip(a + np.array([-.012, 0, .018]) * (1 - L) ** 2, 0, 1)


def save_rgb(a, path, q):
    Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).save(path, 'WEBP', quality=q, method=6)


def brands():
    """Слайди героя: до 1600 px для ПК, 800 px для телефона, 320 px — мініатюри в рядку виробників."""
    for n in BRANDS:
        src = Image.open(ROOT / 'assets' / f'bp-{n}.webp').convert('RGB')
        for suf, w, q in (('', 1600, 80), ('-800', 800, 76), ('-320', 320, 74)):
            im = src if src.width <= w else src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
            save_rgb(grade(np.asarray(im).astype(np.float32) / 255), OUT / f'bp-{n}{suf}.webp', q)
        print('brand', n)


def logos():
    """Логотипи виробників: одноколірні (#262826, білий фон вибито) і кольорові для наведення; розміри — у logos.json."""
    import cairosvg
    meta = {}
    for k in LOGOS:
        src = next((ROOT / 'assets' / 'logos' / 'src').glob(f'{k}.*'))
        if src.suffix == '.svg':
            im = Image.open(io.BytesIO(cairosvg.svg2png(url=str(src), output_width=1400))).convert('RGBA')
        else:
            im = Image.open(src).convert('RGBA')
        a = np.asarray(im).astype(np.float32) / 255
        mn = a[..., :3].min(axis=2)
        white = np.clip((mn - .72) / .21, 0, 1)
        keep = a[..., 3] * (1 - white * white * (3 - 2 * white))
        # світлий напис на темній плашці або темний на жовтій: одноколірна версія за яскравістю
        ink = a[..., 3] * np.clip((.72 - lum(a[..., :3])) / .45, 0, 1) if k in LOGOS_LUM else keep
        ys, xs = np.where(keep > .04)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        ink, keep, rgb = ink[y0:y1, x0:x1], keep[y0:y1, x0:x1], a[y0:y1, x0:x1, :3]
        h = 120
        w = round((x1 - x0) * h / (y1 - y0))
        mono = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
        mono[..., 0], mono[..., 1], mono[..., 2], mono[..., 3] = .149, .157, .149, ink
        col = np.dstack([rgb, keep])
        for arr, suf in ((mono, ''), (col, '-c')):
            out = Image.fromarray((arr * 255 + .5).astype(np.uint8), 'RGBA').resize((w, h), Image.LANCZOS)
            out.save(OUT / f'logo-{k}{suf}.webp', 'WEBP', quality=90, alpha_quality=90, method=6)
        meta[k] = [w, h]
        print('logo', k, w, h)
    (OUT / 'logos.json').write_text(json.dumps(meta), encoding='utf-8')


def line_alpha(rgba, lo=60, hi=150):
    """Лише контури Freestyle (#262826) з рендера: темне → непрозора туш, тони → прозорість."""
    a = np.asarray(rgba).astype(np.float32)
    L = lum(a[..., :3] / 255) * 255
    k = np.clip((hi - L) / (hi - lo), 0, 1) * (a[..., 3] / 255)
    out = np.zeros(a.shape, np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = 0x26, 0x28, 0x26
    out[..., 3] = (k * 255 + .5).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def parts():
    im = Image.open(SRC3D / 'out' / 'hero-bearing-poster.png').convert('RGBA')
    im.save(OUT / 'bearing.webp', 'WEBP', quality=86, alpha_quality=90, method=6)
    line_alpha(im).save(OUT / 'bearing-l.webp', 'WEBP', quality=90, alpha_quality=90, method=6)
    for n in TILES:
        im = Image.open(SRC3D / 'out' / f'tile-{n}-poster.png').convert('RGBA')
        im.save(OUT / f't-{n}.webp', 'WEBP', quality=86, alpha_quality=90, method=6)
        line_alpha(im).save(OUT / f't-{n}-l.webp', 'WEBP', quality=90, alpha_quality=90, method=6)
        print('tile', n)


def video():
    frames = str(SRC3D / 'frames' / 'hero-bearing' / '%04d.png')
    for w, crf in ((1600, 36), (960, 36)):
        dst = OUT / f'bearing-{w}.webm'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '24', '-i', frames,
                        '-vf', f'scale={w}:-2:flags=lanczos', '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p',
                        '-b:v', '0', '-crf', str(crf), '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2',
                        '-auto-alt-ref', '0', '-an', str(dst)], check=True)
        print('video', dst.name, dst.stat().st_size)


if __name__ == '__main__':
    jobs = sys.argv[1:] or ['brands', 'logos', 'parts', 'video']
    for j in jobs:
        globals()[j]()
