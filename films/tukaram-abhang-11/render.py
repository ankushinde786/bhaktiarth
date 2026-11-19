"""Bhakti Arth - one Tukaram abhang as an animated Chinese-ink-wash Short, 9:16, YouTube Shorts safe area.
TEMPLATE (from abhang 8). Per abhang you edit ONLY the blocks marked  # >>> PER-ABHANG  (timings, texts, scene list, scene drawings).
usage (run inside the project folder, which must hold subs.srt and out/assets.npz):
    python3 -I render.py still T...        # stills with the safe-area overlay -> out/still_T.jpg
    python3 -I render.py video [t0 t1]     # render a time range -> out/part_NNNNN.mp4 (run two halves in parallel, detached)"""
import cv2, numpy as np, os, re, subprocess, sys, time, math
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import PchipInterpolator
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, PADX, PADY, FPS = 1080, 1920, 160, 260, 24
S = 1080 / 695.0
# >>> PER-ABHANG: the part boundaries, in seconds, read from the aligned SRT / cues.json
DUR = 76.14          # voice length + 0.7
HOOK_END = 7.7       # end of the spoken hook (hook card fades out, the static abhang card comes in)
EXPL_START = 11.8    # first word of the meaning (static card fades out, explanation + subtitles start)
VIT_A, VIT_B = 25.2, 29.5   # when Vitthal's face is shown with the red tilak (the words about Him directly); also edit K and AMAX below
REC_IN = 51.8        # recitation fades in (about 1 s before the first abhang word)
REC_OUT = 69.1       # recitation fades out (after the last abhang word)
END_T = 69.3         # end card starts
FOLLOW_T = 71.8      # 'फॉलो करा' appears (the spoken follow request)
SEAL_T = 74.4        # seal stamped (the spoken 'राम कृष्ण हरी')
VERM = np.array([176, 46, 34], np.float32) / 255; RED = np.array([196, 28, 24], np.float32) / 255
BLK = np.array([18, 16, 16], np.float32) / 255; GREY = np.array([120, 112, 104], np.float32) / 255; OCHRE = np.array([214, 164, 52], np.float32) / 255
A = np.load(os.path.join(HERE, 'out', 'assets.npz'))
P, T, RDM, REDC, GR = A['P'], A['T'], A['red'], A['Red'], A['grain']
Fig, Gnd, Land, Ring = A['Fig'], A['Gnd'], A['Land'], A['Ring']
TmF, TmL, TmG, TmR, TmT, TmE = A['Tm_fig'], A['Tm_land'], A['Tm_gnd'], A['Tm_ring'], A['Tm_tilak'], A['Tm_erase']
HH, WW = P.shape[:2]
def ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def seg(t, a, b): return float(np.clip((t - a) / (b - a), 0, 1))
def lerpk(t, keys): return float(np.interp(t, [k[0] for k in keys], [k[1] for k in keys]))
def reveal(p, tm, w=.5): return ss((p * (1 + w) - tm) / w)
def B(x, y): return ((x - 38) * S, (y - 62) * S)
def vis(t, a, b, f=.4): return ss(seg(t, a, a + f)) * (1 - ss(seg(t, b - f, b)))
def backout(x): x = np.clip(x, 0, 1); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
FR = '/usr/share/fonts/truetype/freefont/FreeSerif%s.ttf'
def F(sz, bold=False): return ImageFont.truetype(FR % ('Bold' if bold else ''), sz, layout_engine=ImageFont.Layout.RAQM)
TIL = B(390, 349); FEET = B(395, 975)

# >>> PER-ABHANG: half-line times (from cues.json, abhang cues), the half-lines, caption windows (stanza -> first half-line index), scene windows, camera keys, Vitthal visibility
LINE_T = [(52.51, 54.69), (55.51, 57.37), (58.65, 60.98), (61.57, 63.53), (64.84, 66.51), (67.00, 68.56)]
LINES = [
    'विसरले कुळ आपुला आचार।',
    'पती भावे दीर घर सोय॥',
    'सांडिला लौकिक लाज भय चिंता।',
    'रातलें अनंता चित्त माझें॥',
    'मज आतां कोणी आळवाल झणी।',
    'तुका म्हणे कानीं बहिरी जालें॥',
]
CAPS = [(11.8, 20.8, 0), (20.8, 29.8, 2), (29.8, 37.5, 4)]
SC = dict(
    kula=(11.8, 17.2),
    knot=(17.0, 21.0),
    veil=(20.8, 25.2),
    dye=(25.0, 30.0),
    deaf=(29.8, 37.5),
    taal=(37.5, 45.8),
    eyes=(45.6, 52.0),
)
K = [
    (0, 540, 960, 1.0),
    (7.0, 540, 960, 1.05),
    (9.5, 540, 960, 1.0),
    (24.8, 540, 960, 1.0),
    (26.2, 545, 580, 1.35),
    (28.2, 545, 520, 1.55),
    (29.8, 540, 960, 1.0),
    (DUR + 1, 540, 960, 1.0),
]
_kt = [k[0] for k in K]
_cx = PchipInterpolator(_kt, [k[1] for k in K]); _cy = PchipInterpolator(_kt, [k[2] for k in K]); _lz = PchipInterpolator(_kt, [np.log(k[3]) for k in K])
def cam(t):
    cx, cy, z = float(_cx(t)), float(_cy(t)), max(1.0, float(np.exp(_lz(t))))
    return min(max(cx, 540 / z), 1080 - 540 / z), min(max(cy, 960 / z), 1920 - 960 / z), z
AMAX = [
    (0, .14), (1, .15), (6.0, .30), (7.0, .30), (7.7, .07),
    (24.5, .07), (25.4, 1.0), (28.8, 1.0), (29.8, 0.0),
    (51.5, 0.0), (52.2, .07), (68.8, .07), (69.8, .12), (DUR + 1, .12),
]

# ---------------- cropped ink layers ----------------
class Layer:
    def __init__(self, fn):
        im = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(im)); a = np.asarray(im)
        ys, xs = np.nonzero(a); self.y0, self.x0 = int(ys.min()), int(xs.min()); self.m = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32) / 255
def paint(fr, m, y0, x0, col, a=1.0):
    if a <= .002: return
    h, w = m.shape[:2]; ya, xa = max(0, y0), max(0, x0); yb, xb = min(H, y0 + h), min(W, x0 + w)
    if yb <= ya or xb <= xa: return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0, None] * a; roi = fr[ya:yb, xa:xb]; roi[:] = roi * (1 - mm * (1 - col))
def lay(fr, L, col, a=1.0): paint(fr, L.m, L.y0, L.x0, col, a)
def texts(items):
    def fn(d):
        for xy, t, f in items: d.text(xy, t, font=f, fill=255, anchor='mm')
    return Layer(fn)
def fit(txt, size, maxw=900, bold=True):
    while F(size, bold).getlength(txt) > maxw: size -= 4
    return F(size, bold)
f128 = F(128, True)
# >>> PER-ABHANG: hook card text (3-4 short lines, ONE red word = HOOKR) and the title number
HOOK = texts([
    ((540, 380), 'जगाची लाज आणि भीती', fit('जगाची लाज आणि भीती', 105, 860)),
    ((540, 580), 'सगळं सोडून दिलं!', fit('सगळं सोडून दिलं!', 120, 860)),
])
HOOKR = texts([
    ((540, 800), 'कुणासाठी?', fit('कुणासाठी?', 165, 840)),
])
INTRO1 = texts([((540, 225), 'तुकाराम गाथा · अभंग क्र. ११', fit('तुकाराम गाथा · अभंग क्र. ११', 62, 860))])
INTRO2 = texts([((540, 1330), 'आधी अभंग ऐका.', F(72))])
END1 = texts([((540, 620), 'भक्ती अर्थ', F(170, True))]); END2 = texts([((540, 820), 'रोज एक अभंग', F(70))]); END3 = texts([((540, 1200), 'फॉलो करा', F(86, True))])
_rn = np.random.default_rng(3).random((H, W)).astype(np.float32)
_noise = .8 + .6 * cv2.GaussianBlur(_rn, (0, 0), 3)
DRY = (.78 + .22 * cv2.GaussianBlur(np.random.default_rng(9).random((H, W)).astype(np.float32), (0, 0), 1.6) * 2.2).clip(.6, 1.0)
_ensoc = {}
def enso(cx, cy, r, w, prog):
    key = (cx, cy, r, int(prog * 48))
    if key in _ensoc: return _ensoc[key]
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im); n = 260
    for i in range(int(n * key[3] / 48)):
        a = math.radians(-60 + i * 335 / n); a2 = math.radians(-60 + (i + 1) * 335 / n); t = i / n
        d.line([(cx + r * math.cos(a), cy + r * math.sin(a)), (cx + r * math.cos(a2), cy + r * math.sin(a2))], fill=int(255 * (.95 - .35 * t)), width=int(w * (1.15 - .9 * t ** 1.6) + 2))
    m = cv2.GaussianBlur(np.asarray(im, np.float32) / 255, (0, 0), 2.2) * _noise
    y0, y1 = max(0, cy - r - 60), min(H, cy + r + 60); L = (y0, 0, np.clip(m[y0:y1], 0, 1)); _ensoc[key] = L
    if len(_ensoc) > 120: _ensoc.pop(next(iter(_ensoc)))
    return L

# ---------------- brush engine ----------------
def catmull(ctrl, n=80):
    c = np.asarray(ctrl, np.float32); c = np.vstack([c[0] * 2 - c[1], c, c[-1] * 2 - c[-2]]); out = []
    for i in range(1, len(c) - 2):
        p0, p1, p2, p3 = c[i - 1], c[i], c[i + 1], c[i + 2]
        for u in np.linspace(0, 1, max(4, n // (len(ctrl) - 1)), endpoint=False):
            out.append(.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    out.append(c[-2]); return np.array(out, np.float32)
def stroke(fr, pts, a, w, col, alpha=1.0, a0=0.0, taper=True):
    """draw the part [a0,a] of the polyline pts with a tapering brush"""
    if a <= a0 + 1e-3 or alpha <= .002: return
    pts = np.asarray(pts, np.float32); n = len(pts); i0, i1 = int(a0 * (n - 1)), max(int(a * (n - 1)), int(a0 * (n - 1)) + 1)
    sub = pts[i0:i1 + 1]
    if len(sub) < 2: return
    pad = int(w + 6); x0 = int(sub[:, 0].min()) - pad; y0 = int(sub[:, 1].min()) - pad; x1 = int(sub[:, 0].max()) + pad; y1 = int(sub[:, 1].max()) + pad
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for k in range(len(sub) - 1):
        u = (i0 + k) / max(1, n - 1); ww = w * ((.4 + .6 * math.sin(math.pi * min(max(u, 0), 1)) ** .5) if taper else 1)
        cv2.line(m, (int(sub[k, 0] - x0), int(sub[k, 1] - y0)), (int(sub[k + 1, 0] - x0), int(sub[k + 1, 1] - y0)), 255, max(1, int(ww)), cv2.LINE_AA)
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), .9)
    ya, xa = max(0, y0), max(0, x0); yb, xb = min(H, y1), min(W, x1)
    if yb <= ya or xb <= xa: return
    m = m[ya - y0:yb - y0, xa - x0:xb - x0] * DRY[ya:yb, xa:xb]; paint(fr, m, ya, xa, col, alpha)
def wash(fr, poly, col, alpha, soft=3.0, prog=1.0):
    poly = np.asarray(poly, np.float32); pad = int(soft * 3 + 4); x0 = int(poly[:, 0].min()) - pad; y0 = int(poly[:, 1].min()) - pad; x1 = int(poly[:, 0].max()) + pad; y1 = int(poly[:, 1].max()) + pad
    m = np.zeros((y1 - y0, x1 - x0), np.uint8); cv2.fillPoly(m, [(poly - [x0, y0]).astype(np.int32)], 255); m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), soft)
    if prog < 1: yy = np.arange(y1 - y0)[:, None]; m = m * ss((prog * (y1 - y0 + 60) - 30 - yy + 30) / 60)
    ya, xa = max(0, y0), max(0, x0); yb, xb = min(H, y1), min(W, x1)
    if yb <= ya or xb <= xa: return
    paint(fr, m[ya - y0:yb - y0, xa - x0:xb - x0], ya, xa, col, alpha)
def disc(fr, x, y, r, col, a, soft=1.2, clip_y=None):
    R = int(r + 8); x0, y0 = int(x) - R, int(y) - R; m = np.zeros((2 * R, 2 * R), np.uint8); cv2.circle(m, (R, R), int(r), 255, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), soft)
    if clip_y is not None: yy = (np.arange(2 * R) + y0)[:, None]; m = m * ss((clip_y - yy) / 3.0)
    ya, xa = max(0, y0), max(0, x0); yb, xb = min(H, y0 + 2 * R), min(W, x0 + 2 * R)
    if yb > ya and xb > xa: paint(fr, m[ya - y0:yb - y0, xa - x0:xb - x0], ya, xa, col, a)
def ring(fr, x, y, r, w, col, a):
    if a <= .003 or r < 2: return
    R = int(r + w + 8); x0, y0 = int(x) - R, int(y) - R; m = np.zeros((2 * R, 2 * R), np.uint8); cv2.circle(m, (R, R), int(r), 255, max(1, int(w)), cv2.LINE_AA); m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.0)
    ya, xa = max(0, y0), max(0, x0); yb, xb = min(H, y0 + 2 * R), min(W, x0 + 2 * R)
    if yb > ya and xb > xa: paint(fr, m[ya - y0:yb - y0, xa - x0:xb - x0], ya, xa, col, a)
def rot(p, c, ang): ca, sa = math.cos(ang), math.sin(ang); d = np.asarray(p, np.float32) - c; return np.stack([c[0] + d[..., 0] * ca - d[..., 1] * sa, c[1] + d[..., 0] * sa + d[..., 1] * ca], -1)
def leaf(cx, cy, ang, L, Wd, s=1.0):
    u = np.linspace(0, 1, 14); wv = Wd / 2 * np.sin(np.pi * u) ** .8 * (1 - .25 * u); xs = (u - .5) * L
    pts = np.vstack([np.stack([xs, -wv], 1), np.stack([xs[::-1], wv[::-1]], 1)]) * s
    return rot(pts + [cx, cy], np.array([cx, cy], np.float32), ang)
def sparkle(fr, x, y, r, a, col=BLK):
    if a <= .01: return
    for ang in (0, math.pi / 2): stroke(fr, [[x - r * math.cos(ang), y - r * math.sin(ang)], [x + r * math.cos(ang), y + r * math.sin(ang)]], 1, 5, col, a, taper=True)
    for ang in (math.pi / 4, 3 * math.pi / 4): stroke(fr, [[x - .55 * r * math.cos(ang), y - .55 * r * math.sin(ang)], [x + .55 * r * math.cos(ang), y + .55 * r * math.sin(ang)]], 1, 3, col, a * .8)


# ---------------- the explanation drawings ----------------
def petal(cx, cy, ang, L, Wd, s):
    u = np.linspace(0, 1, 16); wv = Wd / 2 * np.sin(np.pi * u ** .8) ** .9; xs = u * L * s
    pts = np.vstack([np.stack([xs, -wv * s], 1), np.stack([xs[::-1], wv[::-1] * s], 1)])
    return rot(pts + [cx, cy], np.array([cx, cy], np.float32), ang - math.pi / 2)
def crescent(fr, x, y, r, col, a):
    R = int(r + 8); m = np.zeros((2 * R, 2 * R), np.uint8); cv2.circle(m, (R, R), int(r), 255, -1, cv2.LINE_AA); cv2.circle(m, (R + int(.42 * r), R - int(.12 * r)), int(.86 * r), 0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.3); x0, y0 = int(x) - R, int(y) - R
    ya, xa = max(0, y0), max(0, x0); yb, xb = min(H, y0 + 2 * R), min(W, x0 + 2 * R)
    if yb > ya and xb > xa: paint(fr, m[ya - y0:yb - y0, xa - x0:xb - x0], ya, xa, col, a)
def sc_sunmoon(fr, t):
    s0, s1 = SC['sunmoon']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    f = 1 - .82 * ss((lt - 1.9) / 1.7); pr = ss(lt / .8)
    sx, sy = 330, 650
    disc(fr, sx, sy, 130 * pr, RED, .9 * a * f, 2)
    for k in range(16):
        ang = k * 2 * math.pi / 16 + lt * .15; r0 = 160; r1 = (225 + 24 * math.sin(t * 3 + k)) * (1 - .45 * ss((lt - 1.9) / 1.7))
        stroke(fr, [[sx + r0 * math.cos(ang), sy + r0 * math.sin(ang)], [sx + r1 * math.cos(ang), sy + r1 * math.sin(ang)]], pr, 8, RED, .7 * a * f, taper=True)
    mx, my = 720, 990
    crescent(fr, mx, my, 125 * pr, BLK, .9 * a * f)
    for i in range(5): sparkle(fr, 560 + 100 * i, 1120 - 40 * (i % 2), 18, a * f * max(0, math.sin(t * 3 + i * 1.7)) ** 2)
    g = ss((lt - 2.5) / 1.2)
    if g > 0:
        gx, gy = 510, 820; s = backout((lt - 2.5) / .6)
        disc(fr, gx, gy, 44 * s, RED, .95 * a, 1.6)
        for k in range(3):
            q = ((lt - 2.8) * .55 + k / 3) % 1; ring(fr, gx, gy, 50 + 300 * q, 4, RED, .5 * (1 - q) * a * g)
def sc_tilak(fr, t):
    s0, s1 = SC['tilak']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    cx, cy = 510, 660
    face = [(cx + 150 * math.cos(q), cy + 190 * math.sin(q)) for q in np.linspace(-math.pi / 2, 3 * math.pi / 2, 40)]
    stroke(fr, np.array(face, np.float32), ss(lt / .9), 9, BLK, .85 * a, taper=False)
    wash(fr, np.array(face, np.float32), BLK, .10 * a * ss(lt / .9), 4)
    p = ss((lt - .7) / .7)
    stroke(fr, [(cx, cy - 150), (cx, cy - 40)], p, 28, BLK, .95 * a)
    if p > .9: disc(fr, cx, cy - 4, 14 * ss((lt - 1.4) / .3), RED, .95 * a)
    for i, y in enumerate((900, 975, 1050)):
        q = ss((lt - 1.5 - .35 * i) / .6); pts = catmull([(cx - 190, y + 18), (cx - 60, y - 6), (cx + 60, y + 8), (cx + 190, y - 14)], 40)
        stroke(fr, pts, q, 26, BLK, .35 * a, taper=True)
    for i in range(6): sparkle(fr, 290 + 90 * i, 840 + 26 * ((i * 5) % 3), 16, a * max(0, math.sin(t * 4 + i * 2.1)) ** 2 * ss((lt - 2) / .6))
def sc_mukut(fr, t):
    s0, s1 = SC['mukut']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    pr = ss(lt / .9); pts = np.array([(320, 900), (320, 700), (420, 800), (510, 640), (600, 800), (700, 700), (700, 900)], np.float32)
    wash(fr, pts, BLK, .5 * a * pr, 2); stroke(fr, np.vstack([pts, pts[:1]]), pr, 9, BLK, .9 * a, taper=False)
    stroke(fr, [(320, 960), (700, 960)], ss((lt - .3) / .5), 20, BLK, .9 * a)
    for i, (x, y) in enumerate([(320, 700), (510, 640), (700, 700)]):
        s = backout((lt - .6 - .15 * i) / .4)
        if s > 0: disc(fr, x, y, 22 * s, RED, .95 * a, 1.5)
    for i in range(5): disc(fr, 360 + 75 * i, 930, 10, RED, .9 * a * ss((lt - 1.0 - .08 * i) / .3))
    for k in range(9):
        ang = -math.pi / 2 + (k - 4) * .28; stroke(fr, [[510 + 210 * math.cos(ang), 760 + 210 * math.sin(ang)], [510 + (300 + 22 * math.sin(t * 5 + k)) * math.cos(ang), 760 + (300 + 22 * math.sin(t * 5 + k)) * math.sin(ang)]], ss((lt - 1.0) / .5), 6, BLK, .45 * a)
def sc_pour(fr, t):
    s0, s1 = SC['pour']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    ang = .95 * ss((lt - .2) / .9); pv = np.array([300, 520], np.float32)
    pot = np.array([(-60, -150), (-60, -110), (-130, -30), (-120, 90), (0, 150), (120, 90), (130, -30), (60, -110), (60, -150)], np.float32) * 1.0
    pot = np.array([(60, -150), (60, -110), (130, -30), (120, 90), (0, 150), (-120, 90), (-130, -30), (-60, -110), (-60, -150)], np.float32)
    P_ = rot(pot + pv, pv, ang); wash(fr, P_, BLK, .6 * a, 2); stroke(fr, np.vstack([P_, P_[:1]]), ss(lt / .6), 8, BLK, .9 * a, taper=False)
    sp = rot(np.array([[60, -150]], np.float32) + pv, pv, ang)[0]
    bx, by = 600, 960; th = np.linspace(0, math.pi, 30); bowl = np.stack([bx + 190 * np.cos(th), by + 80 * np.sin(th)], 1)
    pb = ss(lt / .8); wash(fr, bowl, BLK, .4 * a * pb, 2); stroke(fr, bowl, pb, 10, BLK, .9 * a); stroke(fr, [(bx - 190, by), (bx + 190, by)], pb, 10, BLK, .9 * a)
    sg = ss((lt - 1.0) / .5); st = catmull([sp, (sp[0] + 30, sp[1] + 200), (bx - 20, by - 40)], 40)
    stroke(fr, st, sg, 9, RED, .85 * a, taper=False)
    fill = ss((lt - 1.3) / 1.8)
    if fill > 0: wash(fr, [(bx - 190 + 60 * (1 - fill), by - 4), (bx + 190 - 60 * (1 - fill), by - 4), (bx + 150, by + 56), (bx - 150, by + 56)], RED, .6 * a * fill, 2)
    for k in range(4):
        q = ((lt * 1.2 + k / 4) % 1)
        if sg > .9 and lt > 1.4: i_ = int(q * (len(st) - 1)); disc(fr, st[i_][0], st[i_][1], 9, RED, .9 * a)
    if lt > 2.0:
        for k in range(3):
            q = ((lt - 2.0) * .5 + k / 3) % 1; ring(fr, bx, by - 20, 40 + 240 * q, 4, RED, .5 * (1 - q) * a)
def sc_rain(fr, t):
    s0, s1 = SC['rain']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    cp = ss(lt / 1.0)
    for i, (x, y, r) in enumerate([(330, 470, 120), (470, 420, 150), (620, 470, 135), (740, 500, 100), (540, 520, 130)]):
        disc(fr, x + 10 * math.sin(t * 1.1 + i), y, r * cp, BLK, .55 * a, 14)
    for i in range(18):
        q = (lt * 1.1 + i * .29) % 1; x = 290 + (i * 41 % 460); y = 600 + q * 520
        stroke(fr, [[x, y], [x - 6, y + 46]], 1, 5, BLK, .75 * a * (1 - q * .6) * cp, taper=False)
    for k in range(3):
        q = ((lt * .6 + k / 3) % 1); ring(fr, 510, 1170, 40 + 260 * q, 3, BLK, .4 * (1 - q) * a * cp)
    s = backout((lt - 1.4) / .5)
    if s > 0: disc(fr, 510, 700, 20 * s, RED, .9 * a)
def sc_gather(fr, t):
    s0, s1 = SC['gather']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    for k in range(3):
        q = ((lt * .5 + k / 3) % 1); ring(fr, 510, 880, 40 + 240 * q, 4, RED, .5 * (1 - q) * a * ss(lt / 1.5))
    blob(fr, 510, 880, 30, a * ss(lt / 1.0) * .97)
    for i, (xe, xs_) in enumerate([(300, 70), (400, 40), (620, 980), (720, 1010), (200, 60), (820, 1020)]):
        d = ss((lt - .15 * i) / 2.6); x = xe + (xs_ - xe) * (1 - d) + 5 * math.sin(lt * 5 + i) * (1 - d); y0 = 1020 if i < 4 else 1080; h = 130 if i < 4 else 105
        hy = y0 - 2.6 * h; ib = 4 * math.sin(lt * 6 + i * 2) * (1 - d)
        body = np.array([(x - 9, hy + 36 + ib), (x + 9, hy + 36 + ib), (x + 62, y0), (x - 62, y0)], np.float32)
        wash(fr, body, BLK, .55 * a, 1.5); stroke(fr, np.vstack([body, body[:1]]), 1, 4, BLK, .85 * a, taper=False)
        disc(fr, x, hy + ib, 30, BLK, .9 * a, 1.2)
        sg = 1 if xe < 510 else -1; stroke(fr, [[x + sg * 8, hy + 52 + ib], [x + sg * 70 + sg * 20 * math.sin(lt * 4 + i) * d, hy + 20 + ib]], 1, 7, BLK, .8 * a, taper=True)
def sc_restless(fr, t):
    s0, s1 = SC['restless']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    r = np.random.default_rng(4); ang = np.linspace(0, 8 * math.pi, 22); rad = 80 + 140 * r.random(22)
    ctrl = np.stack([510 + rad * np.cos(ang * 1.3 + 1), 760 + rad * np.sin(ang * .9)], 1); path = catmull(ctrl, 160)
    stroke(fr, path, ss(lt / 2.6), 6, BLK, .7 * a * (1 - ss((lt - 4.4) / 1.0)), taper=False)
    Aa = lambda q: 1 - ss((q - 4.6) / 1.1)
    pos = lambda q: (510 + Aa(q) * (150 * math.sin(q * 7.3) + 70 * math.sin(q * 13.1)), 760 + Aa(q) * (150 * math.cos(q * 6.1) + 70 * math.sin(q * 11.7)))
    tr = [pos(lt - k * .04) for k in range(14, -1, -1)]; da = ss(lt / .5) * a
    stroke(fr, np.array(tr, np.float32), 1, 5, RED, .45 * da); x, y = pos(lt); blob(fr, x, y, 20 + 8 * ss((lt - 5.2) / .6), da * .97)
    if lt > 5.3:
        for k in range(3):
            q = ((lt - 5.3) * .5 + k / 3) % 1; ring(fr, 510, 760, 30 + 200 * q, 4, RED, .5 * (1 - q) * a)
def sc_eyes(fr, t):
    s0, s1 = SC['eyes']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    cl = ss((lt - 1.4) / .9)
    for ex in (350, 670):
        op = max(.02, 1 - cl); pts = np.vstack([np.stack([np.linspace(-120, 120, 20), -62 * op * np.sin(np.pi * np.linspace(0, 1, 20)) ** .9], 1), np.stack([np.linspace(120, -120, 20), 62 * op * np.sin(np.pi * np.linspace(1, 0, 20)) ** .9], 1)]) + [ex, 760]
        if cl < .97: wash(fr, pts, BLK, .22 * a * (1 - cl), 1.5)
        stroke(fr, pts[:20], ss(lt / .7), 9, BLK, .9 * a, taper=True); stroke(fr, pts[20:], ss(lt / .7), 9, BLK, .9 * a * (1 - cl), taper=True)
        if cl < .9: disc(fr, ex, 760, 30 * op, BLK, .85 * a * (1 - cl), 1.2)
        if cl > .5:
            for k in range(5): xx = ex - 90 + 45 * k; stroke(fr, [[xx, 764], [xx + (k - 2) * 7, 764 + 36 * ss((cl - .5) / .5)]], 1, 4, BLK, .7 * a, taper=False)
    g = ss((lt - 2.5) / 1.0)
    if g > 0:
        s = backout((lt - 2.5) / .6); disc(fr, 510, 900, 30 * s, RED, .95 * a, 1.5)
        for k in range(3):
            q = ((lt - 2.7) * .55 + k / 3) % 1; ring(fr, 510, 900, 40 + 260 * q, 4, RED, .5 * (1 - q) * a)
def sc_garland(fr, t):
    s0, s1 = SC['garland']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    ctrl = [(150, 400), (260, 660), (510, 800), (760, 660), (870, 400)]; path = catmull(ctrl, 100)
    stroke(fr, path, ss(lt / .8), 7, BLK, .8 * a, taper=False)
    n = 13
    for i in range(n):
        u = .05 + .9 * i / (n - 1); idx = int(u * (len(path) - 1)); p = path[idx]; q = path[min(len(path) - 1, idx + 2)] - path[max(0, idx - 2)]
        tang = math.atan2(q[1], q[0]); side = 1 if i % 2 else -1; rank = abs(i - (n - 1) / 2); tt = lt - .3 - .11 * (n / 2 - rank)
        sc = backout(tt / .35) if tt > 0 else 0
        if sc <= 0: continue
        sway = .08 * math.sin(t * 2.2 + i * .9); ang = tang + side * 1.05 + sway
        c = p + np.array([math.cos(ang), math.sin(ang)], np.float32) * 38 * sc
        poly = leaf(c[0], c[1], ang, 96, 46, sc)
        wash(fr, poly, BLK, .78 * a, 1.2); stroke(fr, np.vstack([poly[:14], poly[:1]]) if False else poly[:14], 1, 3, BLK, .9 * a, taper=False)
    pt = lt - 2.0
    if pt > 0:
        sc = backout(pt / .4); disc(fr, 510, 800 + 40 * sc, 22 * sc, RED, .95 * a)
        stroke(fr, [[510, 800], [510, 800 + 40 * sc]], 1, 5, BLK, .7 * a, taper=False)
def sc_cloth(fr, t):
    s0, s1 = SC['cloth']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    ph = t * 2.2; xl = lambda y: 270 + 16 * math.sin(y / 75 + ph); xr = lambda y: 750 + 16 * math.sin(y / 75 + ph + 1.2)
    hem = lambda x: 880 + 24 * math.sin(x / 62 + ph * 1.3)
    ys = np.arange(340, 881, 30); left = [(xl(y), y) for y in ys]; xs = np.arange(750, 269, -40); bot = [(x, hem(x) + (x - 270) * .02) for x in xs]
    right = [(xr(y), y) for y in ys[::-1]]
    poly = np.array(left + [(xl(880), hem(270))] + bot[::-1][1:-1] + [(xr(880), hem(750))] + right)
    prog = ss(lt / 1.0); wash(fr, poly, OCHRE, .62 * a, 4, prog)
    for f in (.17, .34, .5, .66, .83):
        pts = [(xl(y) + (xr(y) - xl(y)) * f + 7 * math.sin(y / 50 + ph * 1.5 + f * 9), y) for y in ys]
        stroke(fr, np.array(pts), ss((lt - .3 - f * .5) / .9) * prog, 5, BLK, .5 * a, taper=True)
    stroke(fr, [(240, 330), (510, 322), (780, 330)], ss(lt / .5), 20, BLK, .9 * a, taper=True)
    stroke(fr, catmull([(250, 880), (390, hem(390) + 6), (510, hem(510) + 8), (640, hem(640) + 6), (770, 880)], 40), ss((lt - .8) / .6), 6, BLK, .7 * a)
def sc_ear(fr, t):
    s0, s1 = SC['ear']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    for k, (x, sg) in enumerate([(300, -1), (720, 1)]):
        tt = (lt - .15 * k) / .7
        if tt <= 0: continue
        ang = .09 * math.sin(t * 2.6 + k * 1.7); top = np.array([x, 300], np.float32); s = backout(tt)
        P_ = lambda p: rot(np.asarray(p, np.float32), top, ang)
        ringp = np.array([[x + 28 * math.cos(q), 300 + 28 * math.sin(q) + 28] for q in np.linspace(0, 6.4, 24)]); stroke(fr, P_(ringp), 1, 6, BLK, .9 * a, taper=False)
        stroke(fr, P_([[x, 356], [x, 420]]), 1, 6, BLK, .9 * a, taper=False)
        body = leaf(x, 540, math.pi / 2, 240 * s, 120 * s); body = P_(body)
        wash(fr, body, RED, .85 * a, 1.5); stroke(fr, body[:14], 1, 4, BLK, .8 * a); stroke(fr, body[14:], 1, 4, BLK, .8 * a)
        c = P_([[x, 660]])[0]; disc(fr, c[0], c[1] + 14, 15 * s, BLK, .9 * a)
        for j, (dx, dy, ph) in enumerate([(-85, 470, 0), (90, 560, 1.3), (-60, 700, 2.4)]):
            sparkle(fr, x + dx * sg, dy, 30 + 8 * math.sin(t * 6 + ph + k), a * max(0, math.sin(t * 5 + ph * 2 + k * 2)) ** 2)

def foot(fr, x, y, s, a, lt):
    body = leaf(x, y, math.pi / 2, 250 * s, 112 * s); wash(fr, body, BLK, .8 * a, 1.5); stroke(fr, body[:14], 1, 4, BLK, .8 * a); stroke(fr, body[14:], 1, 4, BLK, .8 * a)
    for k, (dx, dy, r) in enumerate([(-34, -150, 15), (-12, -165, 13), (10, -168, 12), (30, -160, 11), (46, -146, 9)]): disc(fr, x + dx * s, y + dy * s, r * s, BLK, .85 * a)
def sc_lamp(fr, t):
    s0, s1 = SC['lamp']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    th = np.linspace(0, math.pi, 30); bowl = np.stack([510 + 190 * np.cos(th), 900 + 80 * np.sin(th)], 1)
    pb = ss(lt / .8); wash(fr, bowl, BLK, .75 * a * pb, 2); stroke(fr, bowl, pb, 10, BLK, .9 * a); stroke(fr, [(320, 900), (700, 900)], pb, 10, BLK, .9 * a)
    stroke(fr, [(510, 980), (510, 1100)], pb, 14, BLK, .85 * a, taper=False); stroke(fr, [(400, 1100), (620, 1100)], pb, 14, BLK, .85 * a)
    stroke(fr, [(510, 900), (510, 850)], ss((lt - .6) / .3), 7, BLK, .9 * a, taper=False)
    g = ss((lt - 1.0) / 1.4)
    if g > 0:
        fl = 1 + .07 * math.sin(t * 13) + .04 * math.sin(t * 7.3); sw = .09 * math.sin(t * 5.1)
        body = leaf(510, 740, -math.pi / 2 + sw, 230 * g * fl, 115 * g, 1); wash(fr, body, RED, .92 * a, 2)
        for k in range(14):
            ang = k * 2 * math.pi / 14; r0 = 190 * g; r1 = r0 + 30 + 30 * (.5 + .5 * math.sin(t * 3 + k * 1.3))
            stroke(fr, [[510 + r0 * math.cos(ang), 740 + r0 * math.sin(ang) * 1.2], [510 + r1 * math.cos(ang), 740 + r1 * math.sin(ang) * 1.2]], 1, 5, RED, .4 * a * g)
def sc_tulsi(fr, t):
    s0, s1 = SC['tulsi']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    path = catmull([(170, 430), (300, 760), (510, 900), (720, 760), (850, 430)], 100); sw = 6 * math.sin(t * 2.0)
    stroke(fr, path, ss(lt / .8), 4, BLK, .5 * a, taper=False)
    n = 17
    for i in range(n):
        tt = (lt - .1 - .08 * i) / .3
        if tt <= 0: continue
        idx = int((i + .5) / n * (len(path) - 1)); p = path[idx]; s = backout(tt); disc(fr, p[0] + sw * math.sin(i), p[1], 21 * s, BLK, .9 * a, 1.2)
    pt = lt - 1.8
    if pt > 0:
        s = backout(pt / .5); lf = leaf(510 + sw, 990, math.pi / 2, 150 * s, 76 * s); wash(fr, lf, BLK, .8 * a, 1.2); stroke(fr, [[510 + sw, 900], [510 + sw, 1050]], s, 3, BLK, .5 * a, taper=False)
        disc(fr, 510 + sw, 900, 14 * s, RED, .95 * a)
def sc_feet(fr, t):
    s0, s1 = SC['feet']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    wash(fr, [(240, 960), (780, 960), (780, 1070), (240, 1070)], BLK, .25 * a * ss(lt / .6), 2)
    stroke(fr, [(240, 960), (780, 960), (780, 1070), (240, 1070), (240, 960)], ss(lt / .7), 8, BLK, .85 * a, taper=False)
    for x in (400, 560): stroke(fr, [(x, 960), (x, 1070)], ss((lt - .3) / .4), 4, BLK, .45 * a, taper=False)
    for x, d in ((410, 0), (610, .25)):
        s = backout((lt - .3 - d) / .6)
        if s > 0: foot(fr, x, 820, s, a, lt)
    g = ss((lt - 2.6) / 1.0)
    if g > 0:
        s = backout((lt - 2.6) / .5); disc(fr, 510, 560, 30 * s, RED, .95 * a, 1.5)
        for k in range(3):
            q = ((lt - 2.8) * .55 + k / 3) % 1; ring(fr, 510, 560, 40 + 240 * q, 4, RED, .5 * (1 - q) * a)
def sc_murti(fr, t):
    s0, s1 = SC['murti']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    arch = np.array([(510 + 230 * math.cos(q), 700 - 230 * math.sin(q)) for q in np.linspace(math.pi, 0, 30)], np.float32)
    pts = np.vstack([[(280, 1090)], arch, [(740, 1090)]]); stroke(fr, pts, ss(lt / .9), 10, BLK, .9 * a, taper=False)
    wash(fr, np.vstack([arch, [(740, 1090), (280, 1090)]]), BLK, .06 * a, 3)
    stroke(fr, [(300, 1090), (720, 1090)], ss(lt / .6), 16, BLK, .9 * a)
    p = ss((lt - .6) / .8)
    if p > 0:
        wash(fr, leaf(510, 880, math.pi / 2, 300 * p, 140 * p), BLK, .85 * a, 1.5); disc(fr, 510, 690, 46 * p, BLK, .9 * a, 1.2)
        wash(fr, [(470, 650), (550, 650), (530, 590), (510, 560), (490, 590)], BLK, .8 * a * p, 1)
        s = backout((lt - 1.4) / .4)
        if s > 0: disc(fr, 510, 688, 10 * s, RED, .95 * a)
    for sx in (-1, 1):
        g = ss((lt - 1.0) / .8)
        if g > 0:
            fl = 1 + .08 * math.sin(t * 12 + sx); body = leaf(510 + sx * 190, 940, -math.pi / 2, 100 * g * fl, 46 * g); wash(fr, body, RED, .9 * a, 1.5)
def sc_garud(fr, t):
    s0, s1 = SC['garud']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    for i, (x0, x1, y0, y1) in enumerate([(250, 770, 1010, 1070), (320, 700, 950, 1010), (390, 630, 890, 950)]):
        pr = ss((lt - .15 * i) / .5); wash(fr, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], BLK, (.18 + .06 * i) * a * pr, 2)
        stroke(fr, [(x0, y1), (x0, y0), (x1, y0), (x1, y1)], pr, 7, BLK, .85 * a, taper=False)
    p = ss((lt - .8) / .7)
    if p > 0:
        wash(fr, leaf(510, 790, math.pi / 2, 200 * p, 88 * p), BLK, .85 * a, 1.5); disc(fr, 510, 665, 32 * p, BLK, .9 * a, 1.2)
        s = backout((lt - 1.5) / .4)
        if s > 0: disc(fr, 510, 662, 8 * s, RED, .95 * a)
    q = ss((lt - 1.2) / .8)
    if q > 0:
        bx = 280; wash(fr, leaf(bx + 20, 940, -.5, 150 * q, 76 * q), BLK, .7 * a, 1.5); disc(fr, bx - 52, 880, 24 * q, BLK, .85 * a, 1.2)
        wash(fr, [(bx - 74, 876), (bx - 112, 892), (bx - 74, 896)], OCHRE, .8 * a * q, 1); wash(fr, leaf(bx + 40, 860, -1.1, 170 * q, 64 * q), BLK, .6 * a, 1.5)
    for k in range(3):
        r_ = ((lt * .5 + k / 3) % 1); ring(fr, 510, 665, 50 + 230 * r_, 3, RED, .4 * (1 - r_) * a * ss((lt - 1.6) / .6))
def sc_mind(fr, t):
    s0, s1 = SC['mind']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    cx, cy = 510, 760; stroke(fr, np.array([(cx + 230 * math.cos(q), cy + 230 * math.sin(q)) for q in np.linspace(0, 6.4, 50)], np.float32), ss(lt / .9), 7, BLK, .8 * a, taper=False)
    for i, sc in enumerate((.45, .7, 1.0)):
        p = ss((lt - .5 - .6 * i) / .6); al = a * p * (.9 if i == 2 else .3)
        if p > 0:
            wash(fr, leaf(cx, cy + 40, math.pi / 2, 220 * sc, 100 * sc), BLK, .8 * al, 1.5); disc(fr, cx, cy - 100 * sc - 10 + 40 * (1 - sc) * 0, 34 * sc, BLK, .9 * al, 1.2)
    s = backout((lt - 2.0) / .4)
    if s > 0: disc(fr, cx, cy - 88, 9 * s, RED, .95 * a)
    for k in range(3):
        q = ((lt - 1.2) * .6 + k / 3) % 1
        if lt > 1.2: ring(fr, cx, cy, 30 + 200 * q, 4, RED, .5 * (1 - q) * a)
def sc_wilt(fr, t):
    s0, s1 = SC['wilt']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    dr = ss((lt - .9) / 2.2); fade = 1 - .7 * ss((lt - 1.2) / 2.4); tip = np.array([510 + 190 * dr, 700 + 90 * dr], np.float32)
    stem = catmull([(510, 1120), (510, 960), (510 + 70 * dr, 820), tuple(tip)], 50); stroke(fr, stem, ss(lt / .7), 11, BLK, .9 * a * fade, taper=False)
    for sg, yy in ((-1, 1000), (1, 1060)):
        s = backout((lt - .3) / .5)
        if s > 0: wash(fr, leaf(510 + sg * 90 * s, yy + 25 * dr, math.radians(-20 * sg + 30 * dr * sg), 170 * s, 70 * s), BLK, .7 * a * fade, 1.2)
    for k, ad in enumerate((-76, -38, 0, 38, 76)):
        tt = (lt - .1 - .12 * k) / .7
        if tt <= 0: continue
        if lt > 2.9 and k in (0, 4): continue
        s = backout(tt); poly = petal(tip[0], tip[1], math.radians(ad + 75 * dr), 190, 120, s); wash(fr, poly, BLK, .28 * a * fade, 2); stroke(fr, poly[:16], 1, 4, BLK, .75 * a * fade); stroke(fr, poly[16:], 1, 4, BLK, .75 * a * fade)
    for k, ad in enumerate((-76, 76)):
        q = max(0, lt - 2.9)
        if q > 0 or lt > 2.9:
            poly = petal(tip[0] + (-40 if k == 0 else 60) * q, tip[1] + 250 * q * q, math.radians(ad + 75 * dr + 90 * q * (1 if k else -1)), 190, 120, 1)
            pa = (1 - ss(q / 1.0)) * a * fade; wash(fr, poly, BLK, .28 * pa, 2); stroke(fr, poly[:16], 1, 4, BLK, .75 * pa); stroke(fr, poly[16:], 1, 4, BLK, .75 * pa)
    disc(fr, tip[0], tip[1], 30 * ss((lt - 1.0) / .4), RED, .9 * a * fade)
def sc_road(fr, t):
    s0, s1 = SC['road']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    L_ = catmull([(250, 1250), (400, 1050), (470, 900), (490, 790)], 40); R_ = catmull([(770, 1250), (620, 1050), (550, 900), (530, 790)], 40)
    stroke(fr, L_, ss(lt / 1.2), 8, BLK, .8 * a, taper=False); stroke(fr, R_, ss(lt / 1.2), 8, BLK, .8 * a, taper=False)
    wash(fr, np.vstack([L_, R_[::-1]]), BLK, .08 * a * ss(lt / 1.2), 3)
    pt = ss((lt - .5) / .8)
    wash(fr, [(400, 780), (620, 780), (620, 650), (400, 650)], BLK, .35 * a * pt, 2); stroke(fr, [(400, 780), (400, 650), (620, 650), (620, 780)], pt, 7, BLK, .85 * a, taper=False)
    for i, (w_, y) in enumerate([(220, 650), (160, 560), (100, 490)]):
        pr = ss((lt - .8 - .2 * i) / .5); poly = [(510 - w_ / 2, y), (510 + w_ / 2, y), (510 + w_ / 2 - 25, y - 85), (510 - w_ / 2 + 25, y - 85)]
        wash(fr, poly, BLK, .5 * a * pr, 1.5); stroke(fr, np.vstack([poly, poly[:1]]), pr, 5, BLK, .85 * a, taper=False)
    stroke(fr, [(510, 405), (510, 300)], ss((lt - 1.4) / .4), 5, BLK, .9 * a, taper=False)
    fs = ss((lt - 1.6) / .4)
    if fs > 0: sw = 10 * math.sin(t * 6); wash(fr, [(510, 300), (590 + sw, 325), (510, 350)], RED, .9 * a * fs, 1)
    u = ss((lt - 1.0) / 2.3); cp = catmull([(510, 1250), (440, 1060), (505, 900), (510, 800)], 40); i_ = int(u * (len(cp) - 1)); px, py = cp[i_]
    blob(fr, px + 3 * math.sin(t * 5), py, 20, a * ss((lt - .8) / .4) * .97)
    if lt > 3.4:
        for k in range(3):
            q = ((lt - 3.4) * .6 + k / 3) % 1; ring(fr, 510, 600, 40 + 260 * q, 4, RED, .5 * (1 - q) * a)
def sc_wishes(fr, t):
    s0, s1 = SC['wishes']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    r = np.random.default_rng(11)
    for i in range(46):
        x = 230 + 570 * r.random(); y = 560 + 520 * r.random(); rad = 9 + 14 * r.random(); d0 = 1.0 * r.random() * 1.6 + .1
        q = ss((lt - d0) / .5)
        if q <= 0: continue
        up = ss((lt - 1.6 - .8 * r.random()) / 1.8); disc(fr, x + 12 * math.sin(t * 2 + i), y - 220 * up, rad * q, BLK, .6 * a * (1 - up), 1.2)
    g = ss((lt - 3.7) / .8)
    if g > 0:
        s = backout((lt - 3.7) / .5); blob(fr, 510, 820, 30 * s, a * .97)
        for k in range(3):
            q = ((lt - 3.9) * .6 + k / 3) % 1; ring(fr, 510, 820, 40 + 280 * q, 4, RED, .5 * (1 - q) * a)

def sc_lotus(fr, t):
    s0, s1 = SC['lotus']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    cx, cy = 510, 820
    for k in range(3):                                           # water ripples
        r = ((lt * .5 + k / 3) % 1) * 260; ring(fr, cx, cy + 70, r, 4, BLK, .45 * (1 - r / 260) * a)
    layers = [([-78, -40, 0, 40, 78], 330, 120, .0, .22), ([-58, -20, 20, 58], 270, 110, .5, .28), ([-30, 0, 30], 205, 100, 1.0, .34)]
    for angs, L, Wd, t0, al in layers:
        for j, ad in enumerate(angs):
            tt = (lt - .1 - t0 - .12 * j) / .7
            if tt <= 0: continue
            s = backout(tt); poly = petal(cx, cy, math.radians(ad), L, Wd, s)
            wash(fr, poly, BLK, al * a, 2.0); stroke(fr, poly[:16], 1, 4, BLK, .7 * a); stroke(fr, poly[16:], 1, 4, BLK, .7 * a)
    tt = (lt - 2.0) / .4
    if tt > 0: s = backout(tt); disc(fr, cx, cy - 135, 38 * s, RED, .95 * a, 1.6); ring(fr, cx, cy - 135, 38 * s + 14 + 6 * math.sin(t * 3), 3, RED, .5 * a)
def sc_gem(fr, t):
    s0, s1 = SC['gem']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    path = catmull([(190, 300), (330, 520), (510, 640), (690, 520), (830, 300)], 90); stroke(fr, path, ss(lt / .7), 6, BLK, .85 * a, taper=False)
    for i in range(1, 12):
        p = path[int(i / 12 * (len(path) - 1))]; disc(fr, p[0], p[1], 8, BLK, .8 * a * ss((lt - .3 - i * .04) / .3))
    tt = (lt - .5) / .6; cx, cy = 510, 790
    if tt > 0:
        s = backout(tt); dm = np.array([(cx, cy - 150 * s), (cx + 100 * s, cy), (cx, cy + 150 * s), (cx - 100 * s, cy)])
        wash(fr, dm, RED, .88 * a, 1.5); stroke(fr, np.vstack([dm, dm[:1]]), 1, 6, BLK, .9 * a, taper=False)
        for f in [((cx - 100 * s, cy), (cx + 100 * s, cy)), ((cx, cy - 150 * s), (cx, cy + 150 * s)), ((cx - 50 * s, cy - 75 * s), (cx + 50 * s, cy - 75 * s))]:
            stroke(fr, [f[0], f[1]], 1, 3, BLK, .55 * a, taper=False)
        pulse = .5 + .5 * math.sin(t * 4)
        for i in range(14):
            ang = i * 2 * math.pi / 14 + .2; r0 = 130 * s + 20; r1 = r0 + 40 + 40 * (.5 + .5 * math.sin(t * 3 + i * 1.3))
            stroke(fr, [[cx + r0 * math.cos(ang), cy + r0 * math.sin(ang) * 1.15], [cx + r1 * math.cos(ang), cy + r1 * math.sin(ang) * 1.15]], 1, 5, RED, (.45 + .35 * pulse) * a)
        sparkle(fr, cx - 50, cy - 70, 38, a * (.5 + .5 * math.sin(t * 7)) ** 2)
def person(fr, x, yb, h, a, crown=False, red=False, pr=1.0, col=BLK):
    if pr <= 0: return
    hh = h * pr; body = np.array([(x - .06 * h, yb - hh * .72), (x + .06 * h, yb - hh * .72), (x + .24 * h, yb), (x - .24 * h, yb)], np.float32)
    wash(fr, body, col, .62 * a, 1.5); stroke(fr, np.vstack([body, body[:1]]), 1, 4, col, .85 * a, taper=False)
    disc(fr, x, yb - hh * .83, .11 * h, col, .9 * a, 1.2)
    if crown: wash(fr, [(x - .08 * h, yb - hh * .90), (x + .08 * h, yb - hh * .90), (x + .06 * h, yb - hh * 1.02), (x, yb - hh * 1.10), (x - .06 * h, yb - hh * 1.02)], col, .85 * a, 1)
    if red: disc(fr, x, yb - hh * .83, .028 * h, RED, .95 * a)
def sc_garuda(fr, t):
    s0, s1 = SC['garuda']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    p = ss(lt / .8); fl = .1 * math.sin(t * 3.2)
    wash(fr, leaf(510, 850, math.pi / 2, 340 * p, 170 * p), BLK, .85 * a, 1.5)
    for sg in (-1, 1):
        ang = (-2.35 - fl) if sg < 0 else (-.79 + fl); w = leaf(510 + sg * 190, 760, ang, 380 * p, 140 * p); wash(fr, w, BLK, .55 * a, 1.5); stroke(fr, w[:14], 1, 4, BLK, .8 * a); stroke(fr, w[14:], 1, 4, BLK, .8 * a)
        for k in range(4): stroke(fr, [[510 + sg * (80 + 55 * k), 790 - 25 * k], [510 + sg * (150 + 70 * k), 690 - 55 * k - 14 * fl * 6]], p, 4, BLK, .5 * a)
    disc(fr, 510, 600, 54 * p, BLK, .9 * a, 1.2); wash(fr, [(462, 596), (396, 624), (464, 644)], OCHRE, .9 * a * p, 1)
    disc(fr, 494, 590, 8 * p, RED, .95 * a)
    for k in range(5): stroke(fr, [[510 + 18 * (k - 2), 555], [510 + 34 * (k - 2) + 20, 505 - 6 * abs(k - 2)]], p, 5, BLK, .8 * a)
    stroke(fr, [(430, 1070), (590, 1070)], ss((lt - .6) / .5), 12, BLK, .85 * a)
    g = ss((lt - 1.8) / 1.0)
    if g > 0:
        s = backout((lt - 1.8) / .5); disc(fr, 510, 1010, 22 * s, RED, .95 * a, 1.5)
        for k in range(2):
            q = ((lt - 2.0) * .6 + k / 2) % 1; ring(fr, 510, 1010, 30 + 160 * q, 3, RED, .45 * (1 - q) * a)
def sc_mukut2(fr, t):
    s0, s1 = SC['mukut']; a = vis(t, s0, s1, .3); lt = t - s0
    if a <= 0: return
    pr = ss(lt / .6); pts = np.array([(350, 930), (350, 780), (430, 860), (510, 720), (590, 860), (670, 780), (670, 930)], np.float32)
    wash(fr, pts, BLK, .5 * a * pr, 2); stroke(fr, np.vstack([pts, pts[:1]]), pr, 9, BLK, .9 * a, taper=False); stroke(fr, [(350, 985), (670, 985)], pr, 18, BLK, .9 * a)
    for i, (x, y) in enumerate([(350, 780), (510, 720), (670, 780)]):
        s = backout((lt - .4 - .1 * i) / .4)
        if s > 0: disc(fr, x, y, 18 * s, RED, .95 * a, 1.5)
    for k in range(10):
        ang = math.radians(-165 + k * 16.7); r0 = 330 + 20 * (k % 2); x = 510 + r0 * math.cos(ang); y = 840 + r0 * .8 * math.sin(ang); s = backout((lt - .5 - .07 * k) / .35)
        if s > 0:
            disc(fr, x, y, 20 * s, RED, .85 * a, 1.5)
            for j in range(8): aj = j * math.pi / 4 + t; stroke(fr, [[x + 28 * s * math.cos(aj), y + 28 * s * math.sin(aj)], [x + 44 * s * math.cos(aj), y + 44 * s * math.sin(aj)]], 1, 4, RED, .6 * a, taper=False)
def sc_rakh(fr, t):
    s0, s1 = SC['rakh']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    person(fr, 390, 1060, 560, a, crown=True, red=True, pr=ss(lt / .7)); person(fr, 650, 1060, 480, a, red=True, pr=ss((lt - .3) / .7))
    s = backout((lt - 1.0) / .5)
    if s > 0:
        stroke(fr, [[560, 760], [610, 800]], 1, 5, BLK, .8 * a, taper=False); disc(fr, 566, 750, 16 * s, RED, .95 * a)
    for k in range(3):
        q = ((lt * .5 + k / 3) % 1); ring(fr, 520, 700, 40 + 230 * q, 4, RED, .45 * (1 - q) * a * ss((lt - .8) / .5))
def sc_sides(fr, t):
    s0, s1 = SC['sides']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    person(fr, 510, 1060, 600, a, crown=True, red=True, pr=ss(lt / .7))
    for sg in (-1, 1):
        d = ss((lt - .4) / 1.4); x = 510 + sg * (350 - 80 * (1 - d) * -1) if False else 510 + sg * (230 + 200 * (1 - d))
        person(fr, x, 1060, 380, a, pr=ss((lt - .3) / .5))
        if d > .9: stroke(fr, [[x - sg * 24, 800], [x - sg * 70, 840]], 1, 6, BLK, .8 * a, taper=False)
    for k in range(3):
        q = ((lt * .5 + k / 3) % 1); ring(fr, 510, 600, 40 + 280 * q, 4, RED, .4 * (1 - q) * a * ss((lt - 1) / .5))
def sc_sages(fr, t):
    s0, s1 = SC['sages']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    for i, x in enumerate((230, 400, 620, 790)):
        pr = ss((lt - .15 * i) / .5); yb = 1100
        if pr > 0:
            body = np.array([(x - 28, yb - 150 * pr), (x + 28, yb - 150 * pr), (x + 95, yb), (x - 95, yb)], np.float32); wash(fr, body, BLK, .6 * a, 1.5); stroke(fr, np.vstack([body, body[:1]]), 1, 4, BLK, .85 * a, taper=False)
            disc(fr, x, yb - 195 * pr, 36, BLK, .9 * a, 1.2); stroke(fr, [[x - 55, yb - 80], [x - 15 + 10 * math.sin(t * 5 + i), yb - 120]], 1, 6, BLK, .7 * a, taper=False)
    for k in range(9):
        q = ((lt * .35 + k * .17) % 1); x = 250 + 60 * k + 30 * math.sin(lt * 2 + k); y = 900 - 620 * q; al = a * ss(q / .15) * (1 - ss((q - .7) / .3)) * ss((lt - .6) / .5)
        if al > 0.01:
            disc(fr, x, y, 13, RED if k % 3 == 0 else BLK, .9 * al, 1.2); stroke(fr, [[x + 12, y], [x + 12, y - 56]], 1, 4, BLK, .8 * al, taper=False); stroke(fr, [[x + 12, y - 56], [x + 36, y - 40]], 1, 5, BLK, .8 * al, taper=False)
def sc_unique(fr, t):
    s0, s1 = SC['unique']; a = vis(t, s0, s1); lt = t - s0
    if a <= 0: return
    sel = ss((lt - 1.2) / 1.0)
    for r_ in range(4):
        for c_ in range(5):
            x = 230 + 140 * c_; y = 560 + 140 * r_; pr = ss((lt - .06 * (r_ * 5 + c_)) / .4)
            if r_ == 1 and c_ == 2: continue
            disc(fr, x, y, 28 * pr, BLK, (.85 - .5 * sel) * a, 1.2)
    s = backout((lt - 1.0) / .6); disc(fr, 510, 700, (28 + 46 * s) * (1 if lt > 0 else 0), RED if lt > 1.2 else BLK, .95 * a, 1.6)
    if lt < 1.2: disc(fr, 510, 700, 28 * ss(lt / .4), BLK, .85 * a, 1.2)
    for k in range(3):
        q = ((lt - 1.4) * .55 + k / 3) % 1
        if lt > 1.4: ring(fr, 510, 700, 80 + 260 * q, 4, RED, .5 * (1 - q) * a)
def sc_friend(fr, t):
    s0, s1 = SC['friend']; a = vis(t, s0, s1, .5); lt = t - s0
    if a <= 0: return
    pr = ss((lt - .2) / .8); fl = 1 + .18 * math.exp(-((lt - 2.6) ** 2) / .5)
    disc(fr, 510, 500, 150 * pr, RED, .9 * a, 2)
    for k in range(20):
        ang = k * math.pi / 10 + lt * .1; r0 = 190; r1 = (260 + 22 * math.sin(t * 3 + k)) * fl
        stroke(fr, [[510 + r0 * math.cos(ang), 500 + r0 * math.sin(ang)], [510 + r1 * math.cos(ang), 500 + r1 * math.sin(ang)]], pr, 8, RED, .6 * a, taper=True)
    e = ss((lt - 3.4) / .8)
    person(fr, 400, 1110, 480, a, crown=True, red=True, pr=e); person(fr, 640, 1110, 250, a, pr=ss((lt - 3.6) / .8))
    h = ss((lt - 4.6) / .6)
    if h > 0: stroke(fr, [[470, 920], [545 - 20 * 0, 905]], h, 8, BLK, .85 * a, taper=False)
    if lt > 5.2:
        for k in range(3):
            q = ((lt - 5.2) * .6 + k / 3) % 1; ring(fr, 505, 912, 20 + 170 * q, 4, RED, .5 * (1 - q) * a)


def sc_crowd(fr, t):
    s0, s1 = SC['crowd']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    for i, (x, yb, h) in enumerate([(170, 1010, 300), (290, 1010, 300), (410, 1010, 300), (230, 1130, 330), (350, 1130, 330)]):
        person(fr, x, yb, h, a * .85, pr=ss((lt - .1 * i) / .6))
    mv = ss((lt - 1.0) / 1.6); x = 640 + 230 * mv; h = 360 - 120 * mv
    person(fr, x, 1130, h, a, red=True, pr=ss(lt / .6))
    for k in range(3):
        q = ((lt - .6) * .8 + k / 3) % 1
        if lt > .6: yy = 880 + 60 * k; x0 = 480 + 140 * q; stroke(fr, [[x0, yy], [x0 + 130, yy]], 1, 9, BLK, .75 * a * math.sin(math.pi * q), taper=False); stroke(fr, [[x0 + 100, yy - 26], [x0 + 130, yy], [x0 + 100, yy + 26]], 1, 8, BLK, .75 * a * math.sin(math.pi * q), taper=False)
def sc_words(fr, t):
    s0, s1 = SC['words']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    person(fr, 510, 1200, 380, a, red=True, pr=ss(lt / .6))
    for k in range(9):
        ang = k * 2 * math.pi / 9 + .3; d0 = .15 * k; q = ss((lt - d0) / 1.6)
        if q <= 0: continue
        r = 470 - 200 * q; cx_, cy_ = 510 + r * math.cos(ang) * .95, 780 + r * math.sin(ang) * .8
        zz = [[cx_ + (j - 2) * 22, cy_ + (16 if j % 2 else -16)] for j in range(5)]
        stroke(fr, zz, 1, 7, BLK, .75 * a * min(1, q * 3) * (1 - ss((q - .8) / .2)), taper=False)
def sc_drop(fr, t):
    s0, s1 = SC['drop']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    person(fr, 510, 1230, 520, a, pr=ss(lt / .7))
    for k in range(4):
        y = 860 + 90 * k; g = ss((lt - 1.0 - .25 * k) / 1.4)
        if g < 1: ring(fr, 510 + 18 * math.sin(k * 2 + lt * 3) * g, y + 520 * g * g, 150 - 20 * k, 8, BLK, .75 * a * (1 - g))
    s_ = backout((lt - 1.8) / .5)
    if s_ > 0: disc(fr, 510, 1050, 18 * s_, RED, .95 * a)
def sc_drift(fr, t):
    s0, s1 = SC['drift']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    r = np.random.default_rng(23)
    for i in range(30):
        x = 200 + 620 * r.random(); y = 760 + 420 * r.random(); rad = 9 + 14 * r.random(); d0 = .8 * r.random()
        q = ss((lt - d0) / .4)
        if q <= 0: continue
        up = ss((lt - .7 - .7 * r.random()) / 1.6); disc(fr, x + 14 * math.sin(t * 2 + i), y - 380 * up, rad * q, BLK, .6 * a * (1 - up), 1.2)
def sc_dye(fr, t):
    s0, s1 = SC['dye']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x, yb, h = 510, 1250, 640; person(fr, x, yb, h, a * .55, pr=ss(lt / .6))
    p = ss((lt - .7) / 2.0); ycut = yb - h * 1.0 * p
    body = np.array([(x - .06 * h, yb - h * .72), (x + .06 * h, yb - h * .72), (x + .24 * h, yb), (x - .24 * h, yb)], np.int32)
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [body], 255); cv2.circle(m, (x, int(yb - h * .83)), int(.11 * h), 255, -1)
    m[:int(max(0, ycut))] = 0; m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2.0); paint(fr, m, 0, 0, RED, .85 * a)
    for k in range(3):
        q = ((lt - 2.4) * .6 + k / 3) % 1
        if lt > 2.4: ring(fr, x, yb - h * .45, 120 + 300 * q, 4, RED, .5 * (1 - q) * a)


def sc_love(fr, t):
    s0, s1 = SC['love']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    person(fr, 510, 1230, 560, a, pr=ss(lt / .7))
    g = ss((lt - .8) / .8); s_ = backout((lt - .8) / .6)
    if g > 0:
        cy = 1230 - 560 * .45; disc(fr, 510, cy, 34 * s_, RED, .95 * a, 1.6)
        for k in range(14):
            ang = k * 2 * math.pi / 14 + lt * .2; r0 = 60; r1 = 110 + 26 * math.sin(t * 3 + k)
            stroke(fr, [[510 + r0 * math.cos(ang), cy + r0 * math.sin(ang)], [510 + r1 * math.cos(ang), cy + r1 * math.sin(ang)]], g, 7, RED, .6 * a)
        for k in range(3):
            q = ((lt - 1.2) * .5 + k / 3) % 1; ring(fr, 510, cy, 50 + 300 * q, 4, RED, .5 * (1 - q) * a)
def sc_world(fr, t):
    s0, s1 = SC['world']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    cx, cy, R_ = 510, 760, 250; pr = ss(lt / 1.0)
    stroke(fr, np.array([(cx + R_ * math.cos(q), cy + R_ * math.sin(q)) for q in np.linspace(-1.6, 4.7, 60)], np.float32), pr, 9, BLK, .9 * a, taper=False)
    for k, ry in enumerate((.35, .7)):
        pts = np.array([(cx + R_ * math.cos(q) * ry, cy + R_ * math.sin(q)) for q in np.linspace(0, 6.3, 50)], np.float32); stroke(fr, pts, ss((lt - .5 - .2 * k) / .8), 5, BLK, .5 * a, taper=False)
    for k, yy in enumerate((cy - R_ * .5, cy, cy + R_ * .5)):
        w_ = R_ * math.sqrt(max(0, 1 - ((yy - cy) / R_) ** 2)); stroke(fr, [[cx - w_, yy], [cx + w_, yy]], ss((lt - .7 - .2 * k) / .8), 5, BLK, .45 * a, taper=False)
    wash(fr, np.array([(cx + R_ * math.cos(q), cy + R_ * math.sin(q)) for q in np.linspace(0, 6.28, 40)], np.float32), BLK, .12 * a * pr, 3)
    for i in range(4):
        pr_ = ss((lt - 1.2 - .25 * i) / .6); person(fr, 220 + 190 * i + 45 * (i % 2), 1240, 200, a * .8, pr=pr_)
def sc_bowl(fr, t, key='bowl', red=False):
    s0, s1 = SC[key]; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    bx, by = 510, 800; th = np.linspace(0, math.pi, 30); bowl = np.stack([bx + 230 * np.cos(th), by + 230 * np.sin(th)], 1); pb = ss(lt / .7)
    lvl = ss((lt - .6) / 1.0) * (1 - .9 * ss((lt - 1.9) / 1.2))
    if lvl > 0.01:
        yy = by + 230 - 150 * lvl; w_ = 230 * math.sqrt(max(0, 1 - ((yy - by) / 230) ** 2)); wash(fr, [(bx - w_, yy), (bx + w_, yy)] + [(bx + 230 * math.cos(q), by + 230 * math.sin(q)) for q in np.linspace(math.asin(min(1, (yy - by) / 230)), math.pi - math.asin(min(1, (yy - by) / 230)), 20)][::-1], BLK, .35 * a, 2)
    wash(fr, bowl, BLK, .08 * a * pb, 2); stroke(fr, bowl, pb, 10, BLK, .9 * a); stroke(fr, [(bx - 230, by), (bx + 230, by)], pb, 10, BLK, .9 * a)
    stroke(fr, [(bx - 12, by + 215), (bx + 8, by + 245), (bx - 6, by + 262)], ss((lt - 1.0) / .4), 5, BLK, .8 * a, taper=False)
    for k in range(5):
        q = ((lt - 1.4) * .9 + k / 5) % 1
        if lt > 1.4: disc(fr, bx + 2, by + 262 + 330 * q * q, 10, BLK, .8 * a * (1 - q), 1.2)
def sc_bowl2(fr, t): sc_bowl(fr, t, 'bowl2')
def sc_near(fr, t):
    s0, s1 = SC['near']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    mv = ss((lt - .6) / 1.8); xa = 320 + 150 * mv; xb = 700 - 150 * mv
    person(fr, xb, 1230, 560, a, crown=True, red=True, pr=ss(lt / .7)); person(fr, xa, 1230, 330, a, pr=ss((lt - .2) / .7))
    if mv > .98:
        for k in range(3):
            q = ((lt - 2.4) * .6 + k / 3) % 1; ring(fr, 510, 1000, 30 + 240 * q, 4, RED, .5 * (1 - q) * a)

# ---- scenes drawn for abhang 10 (every object is something the words name) ----
def sc_thread(fr, t):                       # "नाहीं काम माझें काज तुम्हांसवें" - the tie with the world is cut, the lone figure walks away
    s0, s1 = SC['thread']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    for i, (x, yb, h) in enumerate([(150, 1030, 250), (260, 1030, 250), (370, 1030, 250), (205, 1130, 280), (315, 1130, 280)]): person(fr, x, yb, h, a * .8, pr=ss((lt - .08 * i) / .6))
    mv = ss((lt - 2.2) / 1.6); x = 720 + 170 * mv; person(fr, x, 1130, 330 - 60 * mv, a, red=True, pr=ss(lt / .6))
    yr = 905; cut = ss((lt - 1.9) / .3)
    if cut < .01:
        pts = [[430 + (x - 430 - 40) * u, yr + 55 * math.sin(math.pi * u) * (1 - 0)] for u in np.linspace(0, 1, 24)]; stroke(fr, pts, ss((lt - .1) / .6), 11, BLK, .9 * a, taper=False)
    else:
        L = [[430 + 100 * u, yr + 40 * u * u * 3 * cut] for u in np.linspace(0, 1, 10)]; R_ = [[x - 40 - 100 * u, yr + 40 * u * u * 3 * cut + 20 * mv] for u in np.linspace(0, 1, 10)]
        stroke(fr, L, 1, 8, BLK, .8 * a * (1 - .6 * cut), taper=True); stroke(fr, R_, 1, 8, BLK, .8 * a * (1 - .6 * cut), taper=True)
def sc_bud(fr, t, key='bud'):               # "होतें गुप्त ठावें केलें आतां" - the hidden love opens like a bud
    s0, s1 = SC[key]; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    p = ss(lt / .8); cx, cy = 510, 930
    stroke(fr, [[cx, 1380], [cx - 14, 1250], [cx + 8, 1100], [cx, cy + 60]], p, 12, BLK, .85 * a)
    for sg in (-1, 1): wash(fr, leaf(cx, 1240, math.pi / 2 + sg * 1.0, 220 * p, 90 * p), BLK, .5 * a, 1.5)
    op = ss((lt - 1.0) / 1.8)
    for k in range(7):
        d = (k - 3) / 3.0; ang = -math.pi / 2 + d * (.18 + 1.2 * op); L = 250 - 25 * abs(d)
        poly = petal(cx, cy + 60, ang, L * p, 110 + 40 * op, 1.0)
        wash(fr, poly, BLK, (.28 + .1 * (1 - abs(d))) * a, 2.0); stroke(fr, np.vstack([poly, poly[:1]]), 1, 4, BLK, .75 * a, taper=False)
    if op > .35:
        q = ss((op - .35) / .65); disc(fr, cx, cy + 40, 46 * q, RED, .95 * a, 1.6)
        for k in range(16):
            ang = k * 2 * math.pi / 16 + lt * .15; stroke(fr, [[cx + 70 * math.cos(ang), cy + 40 + 70 * math.sin(ang)], [cx + (120 + 20 * math.sin(t * 3 + k)) * math.cos(ang), cy + 40 + (120 + 20 * math.sin(t * 3 + k)) * math.sin(ang)]], q, 6, RED, .55 * a)
def sc_known(fr, t):                        # "व्यभिचार माझा पडिला ठाउका" - the love is known: red rings reach the people around
    s0, s1 = SC['known']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    cx, cy = 510, 1120; person(fr, cx, cy + 120, 330, a, red=True, pr=ss(lt / .6))
    ppl = [(170, 900), (300, 760), (510, 690), (720, 760), (850, 900)]
    rr = 60 + 520 * ss((lt - .5) / 2.6)
    for (x, y) in ppl:
        d = math.hypot(x - cx, y - cy); hit = ss((rr - d) / 40.0)
        person(fr, x, y + 90, 170, a * .85, pr=ss((lt - .2) / .6)); 
        if hit > 0: disc(fr, x, y - 60, 9 * hit, RED, .95 * a)
    for k in range(3):
        q = ((lt - .5) * .38 + k / 3) % 1
        if lt > .5: ring(fr, cx, cy, 60 + 520 * q, 4, RED, .55 * (1 - q) * a)
def sc_honour(fr, t):                       # "न सर ती लोकांमाजी जालें" - the turban of respect slips off
    s0, s1 = SC['honour']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x, yb, h = 510, 1250, 540; person(fr, x, yb, h, a, pr=ss(lt / .7)); hy = yb - h * .83
    fall = max(0.0, lt - 1.0); g = min(fall, 1.4); ty = hy - .115 * h + 520 * g * g * .4 if hy - .115 * h + 520 * g * g * .4 < yb - 24 else yb - 24
    tx = x + 150 * ss(fall / 1.4); ang = 1.2 * ss(fall / 1.4)
    th = np.linspace(0, 2 * math.pi, 30); ex, ey = .13 * h * np.cos(th), .06 * h * np.sin(th)
    c, s_ = math.cos(ang), math.sin(ang); poly = np.stack([tx + ex * c - ey * s_, ty + ex * s_ + ey * c], 1).astype(np.float32)
    wash(fr, poly, BLK, .75 * a, 1.5); stroke(fr, np.vstack([poly, poly[:1]]), 1, 5, BLK, .9 * a, taper=False)
    for k in range(3): stroke(fr, [[tx + (ex.min() + .55 * k * .13 * h) * c - .05 * h * s_, ty + (ex.min() + .55 * k * .13 * h) * s_ - .05 * h * c], [tx + (ex.min() + .55 * k * .13 * h + 26) * c + .05 * h * s_, ty + (ex.min() + .55 * k * .13 * h + 26) * s_ + .05 * h * c]], 1, 4, BLK, .6 * a, taper=False)
    disc(fr, tx, ty - .06 * h * math.cos(ang), 10, RED, .95 * a)
def sc_coins(fr, t):                        # "न धरावा लोभ कांहीं मजविशीं" - coins of greed roll up, the open palm sends them away
    s0, s1 = SC['coins']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x, yb, h = 360, 1250, 540; person(fr, x, yb, h, a, red=True, pr=ss(lt / .7))
    sh = yb - h * .66; ar = ss((lt - .5) / .6); stroke(fr, [[x + .06 * h, sh], [x + .2 * h, sh - 30], [x + .3 * h, sh - 70]], ar, 12, BLK, .85 * a)
    stroke(fr, [[x + .3 * h + 18, sh - 150], [x + .3 * h + 18, sh - 20]], ar, 12, BLK, .85 * a)
    for k in range(7):
        q = ((lt - 1.0) * .5 + k * .14) % 1
        if lt < 1.0: continue
        xc = 960 - 640 * q; yc = yb - 60 - 30 * (k % 3) - 200 * (k % 2); wall = x + .3 * h + 60
        if xc < wall: xc = wall + (wall - xc) * .55; fade = 1 - ss((wall - (960 - 640 * q)) / 160)
        else: fade = 1
        ring(fr, xc, yc, 36, 9, BLK, .85 * a * fade); disc(fr, xc, yc, 13, BLK, .5 * a * fade, 1.0)
def _dancer(fr, t, lt, a, cymbals=True):
    x0, yb, h = 510, 1250, 520; sw = 28 * math.sin(lt * 3.0); x = x0 + sw; person(fr, x, yb, h, a, red=True, pr=ss(lt / .7))
    sh = yb - h * .70; up = ss((lt - .5) / .7)
    for sg in (-1, 1):
        hand = (x + sg * (150 + 25 * math.sin(lt * 6 + (0 if sg > 0 else 1.5))), sh - 210 * up)
        stroke(fr, [[x + sg * .06 * h, sh], [x + sg * 100, sh - 90 * up], list(hand)], up, 13, BLK, .85 * a)
        if cymbals and up > .9: disc(fr, hand[0] + sg * 6, hand[1] - 10, 38, BLK, .35 * a, 1.0); ring(fr, hand[0] + sg * 6, hand[1] - 10, 40, 6, BLK, .85 * a)
    return x
def sc_taal(fr, t):                         # "जालें देवपिशी" - mad with love for God: arms up, cymbals, a waving flag
    s0, s1 = SC['taal']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x = _dancer(fr, t, lt, a)
    p = ss((lt - .3) / .8); stroke(fr, [[820, 1300], [820, 760]], p, 10, BLK, .9 * a)
    flag = [[820 + 150 * u * 1.0, 770 + 18 * math.sin(lt * 5 - u * 5) * u + 60 * u * (1 - u) * 0 + (0 if True else 0)] for u in np.linspace(0, 1, 12)]
    top = np.array(flag, np.float32); bot = top + np.array([0, 90], np.float32) + np.stack([np.zeros(12), 10 * np.sin(lt * 5 - np.linspace(0, 5, 12))], 1)
    wash(fr, np.vstack([top, bot[::-1]]), RED, .8 * a * p, 1.5)
    for k in range(3):
        q = ((lt - 1.2) * .6 + k / 3) % 1
        if lt > 1.2: ring(fr, x, 1250 - 520 * .83, 60 + 280 * q, 4, RED, .5 * (1 - q) * a)
def sc_joy(fr, t):                          # takeaway - the God-mad one dances; the fallen turban and the whispers do not matter
    s0, s1 = SC['joy']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x = _dancer(fr, t, lt, a, cymbals=False)
    th = np.linspace(0, 2 * math.pi, 30); poly = np.stack([240 + .13 * 520 * np.cos(th), 1226 + .06 * 520 * np.sin(th)], 1).astype(np.float32)
    wash(fr, poly, BLK, .55 * a, 1.5); stroke(fr, np.vstack([poly, poly[:1]]), 1, 4, BLK, .7 * a, taper=False)
    for k in range(5):
        q = ((lt * .35) + k / 5) % 1; y = 700 + 110 * k; x0 = 40 + 940 * q
        stroke(fr, [[x0 + j * 22, y + (14 if j % 2 else -14)] for j in range(5)], 1, 6, BLK, .45 * a * math.sin(math.pi * q), taper=False)
    if lt > 1.5: sparkle(fr, x, 1250 - 520 * .83 - 130, 20, .9 * a * ss((lt - 1.5) / .5), RED)

def sc_kula(fr, t):
    s0, s1 = SC['kula']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    pr = ss(lt / 0.8)
    wash(fr, [(240, 1140), (440, 1140), (420, 1100), (260, 1100)], BLK, .6 * a * pr, 2.0)
    wash(fr, [(260, 1100), (420, 1100), (405, 990), (275, 990)], BLK, .55 * a * pr, 2.0)
    wash(fr, [(250, 990), (430, 990), (420, 955), (260, 955)], BLK, .6 * a * pr, 2.0)
    disc(fr, 340, 1045, 18, BLK, .75 * a * pr)
    dya = backout((lt - 0.5) / 0.4)
    if dya > 0:
        disc(fr, 340, 1043, 9 * dya, RED, .95 * a)
    t_path1 = catmull([(340, 955), (320, 890), (290, 840)], 25)
    t_path2 = catmull([(340, 955), (345, 870), (340, 810)], 25)
    t_path3 = catmull([(340, 955), (365, 885), (390, 835)], 25)
    stroke(fr, t_path1, pr, 4, BLK, .7 * a, taper=False)
    stroke(fr, t_path2, pr, 5, BLK, .75 * a, taper=False)
    stroke(fr, t_path3, pr, 4, BLK, .7 * a, taper=False)
    sw = 5 * math.sin(lt * 3.5)
    for (lx, ly, rot_) in [(290, 840, -0.4), (340, 810, 0.0), (390, 835, 0.4), (315, 880, -0.6), (365, 875, 0.5)]:
        lf = leaf(lx + sw, ly, rot_, 45 * pr, 22 * pr)
        wash(fr, lf, BLK, .75 * a, 1.2)
    walk = ss((lt - 0.4) / 2.0)
    px = 650 + 40 * walk
    person(fr, px, 1220, 520, a, pr=ss(lt / 0.7))
    stroke(fr, [[470, 1240], [680, 1220], [890, 1210]], ss(lt / 1.0), 10, GREY, .4 * a)

def sc_knot(fr, t):
    s0, s1 = SC['knot']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    slip = ss((lt - 0.8) / 1.8)
    fade_cords = 1 - ss((lt - 2.6) / 0.8)
    lx_shift = -180 * slip
    pts_left = catmull([(200, 900), (350, 860), (510 + lx_shift, 820), (540 + lx_shift * 0.5, 780 + 40 * slip), (480 + lx_shift, 740)], 60)
    stroke(fr, pts_left, ss(lt / 0.8), 12, BLK, .85 * a * fade_cords)
    rx_shift = 180 * slip
    pts_right = catmull([(880, 900), (730, 860), (570 + rx_shift, 820), (540 + rx_shift * 0.5, 860 - 40 * slip), (600 + rx_shift, 900)], 60)
    stroke(fr, pts_right, ss(lt / 0.8), 12, BLK, .85 * a * fade_cords)
    if slip < 0.95:
        loop_a = float(np.clip(1 - slip * 1.1, 0, 1))
        ring(fr, 540, 820, 42 * (1 - 0.3 * slip), 10, BLK, .8 * a * loop_a)
    rt = lt - 1.5
    if rt > 0:
        s_red = backout(rt / 0.5)
        blob(fr, 540, 820, 18 * s_red, .95 * a)
        ring(fr, 540, 820, 50 * ss(rt / 1.2), 4, GREY, .4 * a * (1 - ss(rt / 1.5)))

def sc_veil(fr, t):
    s0, s1 = SC['veil']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x, yb, h = 510, 1220, 520
    person(fr, x, yb, h, a, pr=ss(lt / 0.6))
    drift = ss((lt - 0.6) / 2.0)
    v_alpha = (1 - ss((lt - 2.5) / 0.8)) * a
    vx = x + 260 * drift
    vy = 840 - 220 * drift
    w_pts = catmull([(x - 80 * (1 - drift), 840 - 30 * (1 - drift)),
                     (vx - 60, vy + 40 * math.sin(lt * 4)),
                     (vx + 40, vy - 20 * math.cos(lt * 4)),
                     (vx + 160, vy - 80 + 30 * math.sin(lt * 4 + 1))], 60)
    stroke(fr, w_pts, ss(lt / 0.7), 16, BLK, .75 * v_alpha)
    if drift < 0.8:
        wash(fr, [(x - 70, 860), (x + 70, 860), (vx + 80, vy + 30), (vx, vy - 20)], BLK, .25 * (1 - drift) * a, 3.0)
    s_red = backout((lt - 1.2) / 0.5)
    if s_red > 0:
        blob(fr, x, yb - h * 0.72 + 60, 16 * s_red, .95 * a)

def sc_deaf(fr, t):
    s0, s1 = SC['deaf']; a = vis(t, s0, s1, .4); lt = t - s0
    if a <= 0: return
    x, yb, h = 510, 1220, 520
    person(fr, x, yb, h, a, pr=ss(lt / 0.6))
    up = ss((lt - 0.3) / 0.7)
    sh_y = yb - h * 0.70
    head_y = yb - h * 0.83
    stroke(fr, [[x - 30, sh_y], [x - 85, sh_y - 20 * up], [x - 55, head_y + 10]], up, 11, BLK, .85 * a)
    stroke(fr, [[x + 30, sh_y], [x + 85, sh_y - 20 * up], [x + 55, head_y + 10]], up, 11, BLK, .85 * a)
    ring(fr, x, yb - h * 0.5, 230, 4, GREY, .35 * a * ss(lt / 0.8))
    for side in (-1, 1):
        for k in range(3):
            d0 = 0.4 + 0.3 * k
            p_call = ss((lt - d0) / 1.0)
            if p_call <= 0: continue
            cx_ = x + side * (390 - 70 * p_call)
            cy_ = 750 + 100 * (k - 1) + 20 * math.sin(lt * 3 + k)
            zz = [[cx_ + (j - 1.5) * side * 22, cy_ + (15 if j % 2 else -15)] for j in range(4)]
            fade_call = 1 - ss(p_call / 0.95)
            stroke(fr, zz, min(1.0, p_call * 1.5), 7, GREY, .55 * a * fade_call)
    s_red = backout((lt - 1.2) / 0.5)
    if s_red > 0:
        blob(fr, x, head_y - 12, 12 * s_red, .95 * a)

# >>> PER-ABHANG: new scene drawings go above this line; keep the SC window key and list the function in the frame() scene tuple
# ---------------- the abhang, word by word ----------------
FN = F(60, True); Y0, STEP = 520, 128
WORDS = []
for i, l in enumerate(LINES):
    a, b = LINE_T[i]; ws = l.split(); ch = [len(re.sub(r'[।॥]', '', w_)) for w_ in ws]; tot = sum(ch); cum = 0; sx = 540 - FN.getlength(l) / 2; row = []
    for k, w_ in enumerate(ws):
        x = sx + FN.getlength(' '.join(ws[:k]) + (' ' if k else '')); wl = FN.getlength(w_)
        t0 = a + (b - a) * cum / tot; cum += ch[k]; t1 = a + (b - a) * cum / tot
        def mk(sw, w_=w_, wl=wl):
            im = Image.new('L', (int(wl) + 30, 130), 0); ImageDraw.Draw(im).text((15, 65), w_, font=FN, fill=255, anchor='lm', stroke_width=sw, stroke_fill=255); return np.asarray(im, np.float32) / 255
        row.append(dict(x=x, wl=wl, t0=t0, t1=t1, grey=mk(0), bold=mk(1), y=Y0 + i * STEP))
    WORDS.append(row)
_dk = [(REC_IN + .7, WORDS[0][0]['x'] - 70, Y0 - 58)]
for row in WORDS:
    for w_ in row: _dk.append(((w_['t0'] + w_['t1']) / 2, w_['x'] + w_['wl'] / 2, w_['y'] - 58))
_dk.append((REC_OUT + .4, _dk[-1][1], _dk[-1][2]))
_dt = np.array([k[0] for k in _dk]); assert np.all(np.diff(_dt) > 0), np.diff(_dt)
_dx = PchipInterpolator(_dt, [k[1] for k in _dk]); _dy = PchipInterpolator(_dt, [k[2] for k in _dk])
def blob(img, x, y, r, a, col=VERM, soft=1.2):
    if a <= .003 or r <= .5: return
    R = int(r * 2.2 + 6); x0, y0 = int(x) - R, int(y) - R
    if x0 < 0 or y0 < 0 or x0 + 2 * R >= img.shape[1] or y0 + 2 * R >= img.shape[0]: return
    m = np.zeros((2 * R, 2 * R), np.float32); th = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    rr = r * (.96 + .05 * np.sin(th * 3 + x * .01) + .03 * np.sin(th * 5 + 1))
    pts = np.stack([R + (x - int(x)) + rr * np.cos(th), R + (y - int(y)) + rr * np.sin(th)], 1)
    cv2.fillPoly(m, [(pts * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    m = cv2.GaussianBlur(m, (0, 0), soft) * a; roi = img[y0:y0 + 2 * R, x0:x0 + 2 * R]; roi[:] = roi * (1 - m[..., None]) + col * m[..., None]
def uline(fr, x0, x1, y, h, col, a=1.0):
    if x1 - x0 < 2 or a <= .002: return
    xs = np.arange(int(x0), int(x1), 4); pts = np.stack([xs, y + 3 * np.sin(xs / 37.0)], 1); stroke(fr, pts, 1, h, col, a, taper=False)

# ---------------- subtitles (the user's SRT; only the explanation part) ----------------
def parse_srt(path):
    out = []
    for b in open(path, encoding='utf-8-sig').read().strip().split('\n\n'):
        l = b.strip().splitlines(); m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', l[1])
        f = lambda h, mi, s, ms: int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000
        out.append((f(*m.groups()[:4]), f(*m.groups()[4:]), l[2:]))
    return out
CUES = parse_srt(os.path.join(HERE, 'subs.srt')); SHOW = [i for i, c in enumerate(CUES) if c[0] >= EXPL_START and c[1] <= REC_IN]
SF = F(62); SUBY = 1340; SCX = 510
def wrap(text, font, maxw=860):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        c = (cur + ' ' + w_).strip()
        if font.getlength(c) <= maxw: cur = c
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines
_sc = {}
def sub_img(i):
    if i in _sc: return _sc[i]
    ls = []
    for l_ in CUES[i][2]: ls += wrap(l_, SF)
    im = Image.new('RGBA', (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im); wmax = max(SF.getlength(l_) for l_ in ls); x0 = SCX - wmax / 2 + 20
    for k, l_ in enumerate(ls): d.text((x0, 20 + k * 74), l_, font=SF, fill=(22, 20, 18, 255))
    d.rectangle([x0 - 44, 66, x0 - 27, 83], fill=(176, 46, 34, 255)); _sc[i] = np.asarray(im).astype(np.float32) / 255; return _sc[i]
def over(fr, rgba, y, alpha):
    h = rgba.shape[0]; a = rgba[..., 3:4] * alpha; fr[y:y + h, :rgba.shape[1]] = fr[y:y + h, :rgba.shape[1]] * (1 - a) + rgba[..., :3] * a
def seal_img():
    rng = np.random.default_rng(5); w_, h_ = 480, 150
    im = Image.new('L', (w_, h_), 0); ImageDraw.Draw(im).text((w_ / 2, h_ / 2 - 4), 'राम कृष्ण हरी', font=F(66, True), fill=255, anchor='mm')
    m = 1 - np.asarray(im, np.float32) / 255 * .97
    for _ in range(160): cv2.circle(m, (int(rng.uniform(0, w_)), int(rng.uniform(0, h_))), int(rng.choice([1, 1, 2])), float(rng.uniform(0, .6)), -1)
    m = cv2.GaussianBlur(m, (0, 0), .8); out = np.zeros((h_, w_, 4), np.float32); out[..., :3] = VERM; out[..., 3] = m * .96; return out
SEAL = seal_img()

# ---------------- the painting layer ----------------
CAPL = {}
for _i in range(0, len(LINES), 2):
    CAPL[_i] = texts([((540, 232), LINES[_i], F(42)), ((540, 284), LINES[_i + 1], F(42))])
def vitthal(t):
    cx, cy, z = cam(t); vw, vh = W / z, H / z
    x0 = max(0, int(np.floor(cx + PADX - vw / 2)) - 4); y0 = max(0, int(np.floor(cy + PADY - vh / 2)) - 4)
    x1 = min(WW, int(np.ceil(cx + PADX + vw / 2)) + 4); y1 = min(HH, int(np.ceil(cy + PADY + vh / 2)) + 4)
    sl = (slice(y0, y1), slice(x0, x1)); p = lambda a: a[sl]
    pf = lerpk(t, [(0, .12), (2.8, .5), (5.8, 1.0)]); pl = ss(seg(t, 1.0, 9.0)); pg = ss(seg(t, .5, 4.0)); pr = ss(seg(t, 8.0, 12.0))
    Mk = p(Fig) * reveal(pf, p(TmF)) + p(Gnd) * reveal(pg, p(TmG)) + p(Land) * reveal(pl, p(TmL)) + p(Ring) * reveal(pr, p(TmR)); Mk = np.clip(Mk, 0, 1)
    if 0 < Mk.mean() < .995: Mk = cv2.GaussianBlur(Mk, (0, 0), 2.2)
    am = lerpk(t, AMAX)
    out = p(P) * p(GR)[..., None] * (1 - Mk[..., None] * am * (1 - p(T)))
    tk = ss(seg(t, VIT_A, VIT_A + .8)) * (1 - ss(seg(t, VIT_B, VIT_B + .7))); tp = ss(seg(t, VIT_A, VIT_A + 1.3))
    tk2 = 0; tp2 = 0
    ta = np.maximum(reveal(tp, p(TmT), .35) * tk, reveal(tp2, p(TmT), .35) * tk2) if (tk > 0 or tk2 > 0) else 0
    if np.ndim(ta) and ta.max() > 0:
        al = (p(RDM) * ta)[..., None]; out = out * (1 - al) + p(REDC) * p(GR)[..., None] * al
    tx = W / 2 - z * (cx + PADX - x0); ty = H / 2 - z * (cy + PADY - y0)
    return cv2.warpAffine(out.astype(np.float32), np.array([[z, 0, tx], [0, z, ty]], np.float32), (W, H), flags=cv2.INTER_CUBIC if z > 1.01 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE), (cx, cy, z)
def to_screen(t, p_): cx, cy, z = cam(t); return 540 + (p_[0] - cx) * z, 960 + (p_[1] - cy) * z

# ---------------- the frame ----------------
def frame(t):
    fr, (cx, cy, z) = vitthal(t)
    if t < HOOK_END + .1:                                                    # hook
        ha = 1 - ss(seg(t, HOOK_END - .6, HOOK_END)); ea = enso(540, 800, 310, 28, lerpk(t, [(0, .4), (1.3, 1.0)])); paint(fr, ea[2], ea[0], 0, RED, .8 * ha)
        lay(fr, HOOK, BLK, ha); lay(fr, HOOKR, BLK, ha); lay(fr, HOOKR, RED, .9 * ha); uline(fr, 250, 830, 920, 16, RED, ha * lerpk(t, [(0, .6), (1.0, 1.0)]))
    if HOOK_END - .1 < t < EXPL_START + .1:                                             # today's abhang, static
        sa = ss(seg(t, HOOK_END + .1, HOOK_END + .6)) * (1 - ss(seg(t, EXPL_START - .6, EXPL_START)))
        for row in WORDS:
            for w_ in row: paint(fr, w_['bold'], w_['y'] - 65, int(w_['x']) - 15, BLK, sa)
        lay(fr, INTRO1, BLK, sa); uline(fr, 270, 270 + 540 * ss(seg(t, HOOK_END + .3, HOOK_END + 1.2)), 275, 8, RED, sa)
    if REC_IN - .1 < t < REC_OUT + .7:                                            # the recitation
        la = ss(seg(t, REC_IN, REC_IN + .6)) * (1 - ss(seg(t, REC_OUT, REC_OUT + .6)))
        for i, row in enumerate(WORDS):
            for w_ in row:
                r = ss(seg(t, w_['t0'] - .05, w_['t0'] + .22)); y = w_['y'] - 65; x = int(w_['x']) - 15
                if r < .999: paint(fr, w_['grey'], y, x, GREY, .55 * la * (1 - r))
                if r > .001: paint(fr, w_['bold'], y, x, BLK, la * r)
        for i, (a, b) in enumerate(LINE_T):
            if a - .35 <= t <= b + 1.2:
                row = WORDS[i]; x1 = float(_dx(min(max(t, _dt[0]), _dt[-1]))) if t < b else row[-1]['x'] + row[-1]['wl']
                x1 = min(max(x1, row[0]['x']), row[-1]['x'] + row[-1]['wl']); fade = 1 - ss(seg(t, b + .3, b + 1.1)); uline(fr, row[0]['x'], x1, row[0]['y'] + 46, 7, RED, .8 * fade * la)
        da = ss(seg(t, REC_IN + .4, REC_IN + .8)) * (1 - ss(seg(t, REC_OUT - .1, REC_OUT + .5)))
        if da > 0: tt = min(max(t, _dt[0]), _dt[-1]); blob(fr, float(_dx(tt)), float(_dy(tt)) + 1.5 * math.sin(t * 9), 18, da * .97)
    for fn in (sc_kula, sc_knot, sc_veil, sc_dye, sc_deaf, sc_taal, sc_eyes): fn(fr, t)
    for a, b, i in CAPS:                                           # the original lines, small, while they are explained
        if a <= t <= b:
            ca = ss(seg(t, a, a + .5)) * (1 - ss(seg(t, b - .5, b))); strip = fr[200:340]; dk = float(np.clip((.66 - strip.mean()) * 6, 0, 1))
            ramp = ss(np.minimum(np.arange(140), np.arange(140)[::-1]) / 30.0)[:, None, None]; pa = ramp * dk * ca * .93
            fr[200:340] = strip * (1 - pa) + np.array([.83, .80, .75], np.float32) * pa; lay(fr, CAPL[i], GREY * .6, ca)
    for i in SHOW:
        a, b, _ = CUES[i]
        if a - .01 <= t <= b + .01:
            k = min(ss((t - a) / .25), ss((b - t) / .2)); y_a, y_b = SUBY - 30, SUBY + 190
            strip = fr[y_a:y_b]; dk = float(np.clip((.66 - strip.mean()) * 6, 0, 1))
            ramp = ss(np.minimum(np.arange(y_b - y_a), np.arange(y_b - y_a)[::-1]) / 34.0)[:, None, None]; pa = ramp * dk * float(k) * .93
            fr[y_a:y_b] = strip * (1 - pa) + np.array([.83, .80, .75], np.float32) * pa; over(fr, sub_img(i), SUBY, float(k) * .96)
    if t > END_T:                                                   # end card
        ea = enso(540, 700, 360, 30, seg(t, END_T + .1, END_T + 1.6)); paint(fr, ea[2], ea[0], 0, RED, .8 * ss(seg(t, END_T + .1, END_T + .6)))
        lay(fr, END1, BLK, ss(seg(t, END_T + .4, END_T + 1.1))); lay(fr, END2, BLK, ss(seg(t, END_T + 1.1, END_T + 1.8))); lay(fr, END3, RED, ss(seg(t, FOLLOW_T, FOLLOW_T + .6)))
        su = seg(t, SEAL_T, SEAL_T + .16)
        if su > 0:
            sc = 1 + .22 * (1 - su); s2 = cv2.resize(SEAL, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR); sh, sw = s2.shape[:2]; a_ = s2[..., 3:4] * su; X, Y = 540 - sw // 2, 1350 - sh // 2
            fr[Y:Y + sh, X:X + sw] = fr[Y:Y + sh, X:X + sw] * (1 - a_) + s2[..., :3] * a_
    return np.clip(fr, 0, 1)

def to8(fr): return (fr * 255 + .5).astype(np.uint8)
def safe_overlay(fr):
    o = fr.copy(); cv2.rectangle(o, (40, 120), (980, 1540), (0, .66, .75), 3)
    o[1540:] = o[1540:] * .7 + np.array([0, .6, .7]) * .3; o[740:1540, 980:] = o[740:1540, 980:] * .7 + np.array([.7, 0, .7]) * .3; return o
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for a in sys.argv[2:]:
            f = frame(float(a)); cv2.imwrite(os.path.join(HERE, 'out', f'still_{a}.jpg'), cv2.cvtColor(to8(safe_overlay(f)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
    else:
        t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
        n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS)); outp = os.path.join(HERE, 'out', f'part_{n0:05d}.mp4')
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', outp], stdin=subprocess.PIPE)
        tt = time.time()
        for n in range(n0, n1):
            ff.stdin.write(to8(frame(n / FPS)).tobytes())
            if (n - n0) % 48 == 0: print(n - n0, '/', n1 - n0, round(time.time() - tt), 's', flush=True)
        ff.stdin.close(); ff.wait(); print('done', outp)

