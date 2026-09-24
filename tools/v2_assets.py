"""Ресурси для v2.html: кольоровий грейд і креслення фото брендів, креслення й рендери деталей, відео підшипника з альфою.

python tools/v2_assets.py            # усе
python tools/v2_assets.py brands     # лише фото брендів
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC3D = Path('C:/Users/Yalad/meridian-3d')
OUT = ROOT / 'assets' / 'v2'
OUT.mkdir(parents=True, exist_ok=True)

INK = np.array([0x26, 0x28, 0x26]) / 255
PAPER = np.array([0xF1, 0xF0, 0xEB]) / 255
BRANDS = ['jd', 'claas', 'bednar', 'geringhoff', 'olimac', 'kuhn', 'amazone']
TILES = ['gear', 'bearing', 'sprocket']


def lum(a):
    return a[..., 0] * .2126 + a[..., 1] * .7152 + a[..., 2] * .0722


def grade(a, sat=.62, tone=.35):
    """Спільний грейд: приглушена насиченість, м'яка S-крива, тонування в діапазон ink→paper."""
    L = lum(a)[..., None]
    a = np.clip(L + (a - L) * sat, 0, 1)
    a = a * a * (3 - 2 * a) * .35 + a * .65
    L = lum(a)[..., None]
    duo = INK + (PAPER - INK) * L
    a = a * (1 - tone) + duo * tone
    return np.clip(INK + (PAPER - INK) * a, 0, 1)


def xdog(a, s=1.0, k=1.6, p=18, eps=.35, phi=14):
    g = lum(a).astype(np.float32)
    g1 = cv2.GaussianBlur(g, (0, 0), s)
    g2 = cv2.GaussianBlur(g, (0, 0), s * k)
    d = (1 + p) * g1 - p * g2
    return np.clip(np.where(d >= eps, 1.0, 1 + np.tanh(phi * (d - eps))), 0, 1)


def sketch(a, hatch=.24):
    """Контури Canny по згладженому фото + легке штрихування XDoG. Повертає щільність туші 0..1."""
    u8 = (a * 255).astype(np.uint8)
    sm = cv2.edgePreservingFilter(cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), flags=1, sigma_s=40, sigma_r=.25)
    g = cv2.GaussianBlur(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY), (0, 0), 1.1)
    med = float(np.median(g))
    ed = cv2.Canny(g, .66 * med * .6, min(255, 1.33 * med) * .9, L2gradient=True).astype(np.float32) / 255
    ed = np.clip(cv2.GaussianBlur(ed, (0, 0), .6) * 1.8, 0, 1)
    return np.clip(np.maximum(ed, (1 - xdog(a)) * hatch), 0, 1)


def on_paper(ink):
    return PAPER[None, None, :] * (1 - ink[..., None]) + INK[None, None, :] * ink[..., None]


def save_rgb(a, path, q):
    Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).save(path, 'WEBP', quality=q, method=6)


def brands():
    """Слайди героя: повний розмір (до 1600 px) для ПК і 800 px для телефона; до кожного — креслення."""
    for n in BRANDS:
        src = Image.open(ROOT / 'assets' / f'bp-{n}.webp').convert('RGB')
        for suf, w, q in (('', 1600, 80), ('-800', 800, 76)):
            im = src if src.width <= w else src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
            a = np.asarray(im).astype(np.float32) / 255
            save_rgb(grade(a), OUT / f'bp-{n}{suf}.webp', q)
            save_rgb(on_paper(sketch(a)), OUT / f'bp-{n}{suf}-l.webp', 55)
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
