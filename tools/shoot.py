"""Знімки сторінки headless Chrome через CDP (панель браузера застосунку часто не малює після прокрутки).

python tools/shoot.py URL W H plan.json [тека]

plan.json — список кроків [js, пауза_с, імʼя]: js виконується на сторінці (null — нічого; «HOVER:селектор» —
прокрутити до елемента й навести на його центр мишку), потім пауза,
потім знімок imʼя.jpg (null — без знімка). Значення, яке повертає js, друкується.
Ширина < 900 вмикає мобільну емуляцію (дотик). SHOOT_DPR=2 — знімок з подвоєною щільністю пікселів. Тека за замовчуванням — shots/ у корені репозиторію.

Приклад кроку: ["(()=>{const e=document.querySelector('.dsk .brands');scrollTo(0,e.getBoundingClientRect().top+scrollY);return scrollY})()", 2.5, "brands"]
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT = 9333


async def main(url, w, h, plan, out):
    out.mkdir(parents=True, exist_ok=True)
    mobile = w < 900
    p = subprocess.Popen([CHROME, '--headless=new', f'--remote-debugging-port={PORT}', f'--user-data-dir={tempfile.mkdtemp()}',
                          '--autoplay-policy=no-user-gesture-required', '--hide-scrollbars', f'--window-size={w},{h}', 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        tabs = []
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json'))
                break
            except Exception:
                time.sleep(.2)
        ws_url = [t for t in tabs if t['type'] == 'page'][0]['webSocketDebuggerUrl']
        async with websockets.connect(ws_url, max_size=2 ** 28) as ws:
            n = 0

            async def cmd(method, **params):
                nonlocal n
                n += 1
                my = n
                await ws.send(json.dumps({'id': my, 'method': method, 'params': params}))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get('id') == my:
                        return m.get('result', m.get('error'))

            await cmd('Page.enable')
            await cmd('Runtime.enable')
            await cmd('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=float(os.environ.get('SHOOT_DPR', '1')), mobile=mobile)
            if mobile:
                await cmd('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
            await cmd('Page.navigate', url=url)
            for js, wait, name in plan:
                if js and js.startswith('HOVER:'):
                    sel = json.dumps(js[6:])
                    r = await cmd('Runtime.evaluate', returnByValue=True, expression=(
                        f'(()=>{{const e=document.querySelector({sel});e.scrollIntoView({{block:"center"}});'
                        f'const b=e.getBoundingClientRect();return [b.left+b.width/2,b.top+b.height/2]}})()'))
                    x, y = r['result']['value']
                    await cmd('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y)
                elif js:
                    r = await cmd('Runtime.evaluate', expression=js, returnByValue=True, awaitPromise=True)
                    val = r.get('result', {}).get('value') if isinstance(r, dict) else r
                    if val is not None:
                        print('js:', json.dumps(val, ensure_ascii=False)[:600])
                await asyncio.sleep(wait)
                if name:
                    r = await cmd('Page.captureScreenshot', format='jpeg', quality=82)
                    (out / f'{name}.jpg').write_bytes(base64.b64decode(r['data']))
                    print('shot', out / f'{name}.jpg')
    finally:
        p.kill()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    url, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    plan = json.loads(Path(sys.argv[4]).read_text(encoding='utf-8'))
    out = Path(sys.argv[5]) if len(sys.argv) > 5 else Path(__file__).resolve().parent.parent / 'shots'
    asyncio.run(main(url, w, h, plan, out))
