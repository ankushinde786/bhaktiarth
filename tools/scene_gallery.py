"""Render a contact sheet of every sc_* drawing in engine/render.py (so you can pick scenes by looking).
usage: from a project folder that holds render.py, subs.srt and out/assets.npz:
    python3 -I scene_gallery.py [out.jpg]
Each drawing is shown at two moments (early / late) with its function name."""
import importlib.util, os, re, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.getcwd(); spec = importlib.util.spec_from_file_location('render', os.path.join(HERE, 'render.py')); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
src = open(os.path.join(HERE, 'render.py'), encoding='utf-8').read()
names = re.findall(r'^def (sc_\w+)\(fr, t[,)]', src, re.M)
out = sys.argv[1] if len(sys.argv) > 1 else 'scene_gallery.jpg'
tw, th = 270, 480; cols = 8; items = []
for n in names:
    fn = getattr(R, n); body = src[src.index('def ' + n + '('):]; body = body[:body.index('\ndef ', 5)] if '\ndef ' in body[5:] else body
    keys = re.findall(r"SC\['(\w+)'\]", body)
    if not keys: continue
    R.SC[keys[0]] = (0.0, 12.0)
    for lt in (1.4, 3.8):
        fr = np.ones((R.H, R.W, 3), np.float32) * np.array([.86, .83, .78], np.float32)
        try: fn(fr, lt)
        except Exception as e: print(n, 'failed', e); continue
        items.append((n, lt, cv2.resize(fr, (tw, th), interpolation=cv2.INTER_AREA)))
F = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', 20)
rows = (len(items) + cols - 1) // cols; sheet = Image.new('RGB', (cols * tw, rows * (th + 26)), (245, 240, 230)); d = ImageDraw.Draw(sheet)
for i, (n, lt, im) in enumerate(items):
    x, y = (i % cols) * tw, (i // cols) * (th + 26); sheet.paste(Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)), (x, y)); d.text((x + 6, y + th + 2), f'{n}  t={lt}', font=F, fill=(20, 20, 20))
sheet.save(out, quality=85); print(len(names), 'scenes ->', out)
