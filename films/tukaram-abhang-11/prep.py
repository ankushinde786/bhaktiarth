"""Prepare the user's Vitthal ink-wash painting for animation.
Crops the scroll to 9:16, separates the ink (transmittance T) from the paper (P), removes the stray Chinese
inscription and the generator watermark, and builds region masks / reveal time-maps. Saves out/assets.npz."""
import cv2, numpy as np, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
S = 1080 / 695.0                       # crop -> base scale
X0, Y0, CW, CH = 38, 62, 695, 1235     # crop of the original (inside the scroll mount)
W, H = 1080, 1920
PADX, PADY = 160, 260
rng = np.random.default_rng(7)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)   # usage (from the project folder): python3 -I prep.py <vitthal_reference.png>

im = cv2.cvtColor(cv2.imread(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'ref.png')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
crop = im[Y0:Y0 + CH, X0:X0 + CW].copy()

# ---- paper model: robust cubic fit on the pixels that are paper ----
ys, xs = np.mgrid[0:CH, 0:CW].astype(np.float32); u = xs / CW - .5; v = ys / CH - .5
def feats(u, v): return np.stack([np.ones_like(u), u, v, u * u, u * v, v * v, u ** 3, u * u * v, u * v * v, v ** 3], -1)
F = feats(u, v); lum = crop.mean(2)
bad = np.zeros((CH, CW), bool)                                  # stray marks excluded from the fit
def ob(x0, y0, x1, y1): bad[max(0, y0 - Y0):max(0, y1 - Y0), max(0, x0 - X0):max(0, x1 - X0)] = True
ob(630, 95, 730, 350); ob(612, 1215, 690, 1295)
mask = (lum > np.percentile(lum, 70)) & ~bad
P = None
for it in range(5):
    A = F[::3, ::3][mask[::3, ::3]]; Pc = np.zeros_like(crop)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, crop[::3, ::3, c][mask[::3, ::3]], rcond=None); Pc[..., c] = F @ coef
    mask = (lum > Pc.mean(2) * (.965 - .01 * it)) & ~bad
P = np.clip(Pc, .2, 1)
T = np.clip(crop / P, 0, 1)
# red tilak (kept as its own layer)
red = np.clip((crop[..., 0] - np.maximum(crop[..., 1], crop[..., 2]) - .12) / .12, 0, 1)
tilak_box = np.zeros((CH, CW), np.float32); tilak_box[300 - Y0:410 - Y0, 355 - X0:425 - X0] = 1
red *= tilak_box; red = cv2.GaussianBlur(red, (0, 0), 1.0)
Tm_ = T.copy(); Tm_[red > .05] = np.array([.06, .06, .06])      # under the tilak: the dark face
# erase the Chinese inscription and the watermark: inpaint T from the paper around them
em = np.zeros((CH, CW), np.uint8)
for (a, b, c, d) in [(630, 95, 730, 350), (612, 1215, 690, 1295)]: em[b - Y0:d - Y0, a - X0:c - X0] = 255
em = cv2.dilate(em, np.ones((9, 9), np.uint8))
T8 = (np.clip(Tm_, 0, 1) * 255).astype(np.uint8)
T8 = cv2.inpaint(T8, em, 9, cv2.INPAINT_TELEA)
soft = cv2.GaussianBlur(em.astype(np.float32) / 255, (0, 0), 3)[..., None]
Tm_ = Tm_ * (1 - soft) + (T8.astype(np.float32) / 255) * soft
Tred = crop.copy()

up = lambda a, interp=cv2.INTER_CUBIC: cv2.resize(a, (W, H), interpolation=interp)
Tb = np.clip(up(Tm_), 0, 1)
sh = cv2.GaussianBlur(Tb, (0, 0), 1.4); Tb = np.clip(Tb + .55 * (Tb - sh), 0, 1)      # a little crispness after the 1.55x upscale
Pb = up(P); redb = np.clip(up(red), 0, 1); Redc = np.clip(up(Tred), 0, 1)

# ---- padded canvas (the scroll's mount shows when we pull back) ----
def pad(a, val=None):
    if val is None: return cv2.copyMakeBorder(a, PADY, PADY, PADX, PADX, cv2.BORDER_REPLICATE)
    return cv2.copyMakeBorder(a, PADY, PADY, PADX, PADX, cv2.BORDER_CONSTANT, value=val)
Pp = pad(Pb); Hh, Ww = Pp.shape[:2]
yy, xx = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
dx = np.maximum(np.maximum(PADX - xx, xx - (PADX + W - 1)), 0); dy = np.maximum(np.maximum(PADY - yy, yy - (PADY + H - 1)), 0)
d = np.hypot(dx, dy)
outside = d > 0
Pp_blur = cv2.GaussianBlur(Pp, (0, 0), 30)
Pp = np.where(outside[..., None], Pp_blur, Pp)
mount = (.90 - .10 * np.clip(d / 260, 0, 1)) * (1 - .12 * np.exp(-((d - 2) / 3) ** 2) * outside)       # darker mount, thin edge line
Pp = Pp * np.where(outside, mount, 1)[..., None]
Tp = pad(Tb, (1, 1, 1)); redp = pad(redb[..., None], 0)[..., 0] if False else cv2.copyMakeBorder(redb, PADY, PADY, PADX, PADX, cv2.BORDER_CONSTANT, value=0)
Redp = cv2.copyMakeBorder(Redc, PADY, PADY, PADX, PADX, cv2.BORDER_CONSTANT, value=(1, 0, 0))

# ---- grain (paper fibre) ----
def nz(sig, seed):
    r = np.random.default_rng(seed).standard_normal((Hh, Ww)).astype(np.float32); r = cv2.GaussianBlur(r, (0, 0), sig); return r / r.std()
grain = 1 + .010 * nz(.7, 1) + .012 * nz(2.2, 2) + .010 * nz(9, 3)
fib = np.zeros((Hh, Ww), np.float32)
for _ in range(2600):
    x, y = rng.integers(0, Ww), rng.integers(0, Hh); a = rng.uniform(0, np.pi); l = rng.uniform(8, 30)
    cv2.line(fib, (int(x), int(y)), (int(x + l * np.cos(a)), int(y + l * np.sin(a))), float(rng.uniform(.4, 1)), 1, cv2.LINE_AA)
grain = (grain - .014 * cv2.GaussianBlur(fib, (0, 0), .6)).astype(np.float32)

# ---- coordinates in the original's frame, for regions ----
xo = ((xx - PADX) / S + X0).astype(np.float32); yo = ((yy - PADY) / S + Y0).astype(np.float32)
ss = lambda x: (lambda c: c * c * (3 - 2 * c))(np.clip(x, 0, 1))
def sbox(x0, x1, y0, y1, soft):
    return ss((xo - x0) / soft) * ss((x1 - xo) / soft) * ss((yo - y0) / soft) * ss((y1 - yo) / soft)
Fig = sbox(205, 580, 108, 1005, 16)
Gnd = ss((yo - 985) / 36)
Land = np.clip(1 - Fig - Gnd, 0, 1)
r = np.hypot(xo - 395, yo - 308); Ring = ss((26 - np.abs(r - 178)) / 12) * ss((448 - yo) / 14) * Fig
FigN = Fig * (1 - Ring)
# time maps (0 = first to appear)
def fbm(seed):
    n = nz(6, seed) * .5 + nz(22, seed + 1) * .35 + nz(70, seed + 2) * .35; n = (n - n.min()) / (n.max() - n.min()); return ss((n - .15) / .7)
n1, n2, n3, n4 = fbm(11), fbm(21), fbm(31), fbm(41)
yup = np.clip((1005 - yo) / (1005 - 108), 0, 1)
Tm_fig = (.88 * yup + .12 * n1).astype(np.float32)
Tm_land = (.65 * np.clip((1300 - yo) / 1200, 0, 1) + .35 * n2).astype(np.float32)
Tm_gnd = (.55 * np.clip((xo - 50) / 520, 0, 1) + .45 * n3).astype(np.float32)
Tm_ring = (((np.arctan2(yo - 308, xo - 395) + np.pi) / (2 * np.pi)) * .9 + .1 * n1).astype(np.float32)
rad = np.hypot(xo - 395, (yo - 420) * .9)
nsm = nz(40, 51) * .6 + nz(110, 52) * .4; nsm = (nsm - nsm.min()) / (nsm.max() - nsm.min())
Tm_erase = (.62 * np.clip(1 - rad / 700, 0, 1) + .38 * nsm).astype(np.float32)
tdist = np.hypot(xo - 390, (yo - 350) * .8); Tm_tilak = np.clip(tdist / 60, 0, 1).astype(np.float32)

np.savez_compressed(os.path.join(HERE, 'out', 'assets.npz'), P=Pp.astype(np.float32), T=Tp.astype(np.float32), red=redp.astype(np.float32), Red=Redp.astype(np.float32),
    grain=grain, Fig=FigN.astype(np.float32), Gnd=Gnd.astype(np.float32), Land=Land.astype(np.float32), Ring=Ring.astype(np.float32),
    Tm_fig=Tm_fig, Tm_land=Tm_land, Tm_gnd=Tm_gnd, Tm_ring=Tm_ring, Tm_erase=Tm_erase, Tm_tilak=Tm_tilak)
print('assets saved', Pp.shape, 'paper mean', P.mean((0, 1)).round(3))
# preview: everything revealed, and a paper-only view
full = np.clip(Pp * grain[..., None] * (1 - (1 - Tp) ), 0, 1)
cv2.imwrite(os.path.join(HERE, 'out', 'prep_full.jpg'), cv2.cvtColor((cv2.resize(full, None, fx=.4, fy=.4) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
