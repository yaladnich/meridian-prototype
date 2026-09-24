"""Ресурси для v2.html: кольоровий грейд фото брендів, креслення й рендери деталей, відео підшипника з альфою.

python tools/v2_assets.py            # усе
python tools/v2_assets.py brands     # лише фото брендів
"""
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
    jobs = sys.argv[1:] or ['brands', 'parts', 'video']
    for j in jobs:
        globals()[j]()
