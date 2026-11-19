"""Mix: the user's voice-over untouched; music + animation sounds together sit at 5 % of the voice level.
Synthesised in numpy (no samples, no downloads). Output: out/mix.wav (48 kHz stereo) and out/levels.txt.
Run with: python3 -I mix.py   (from the project folder)"""
import json, wave, sys, os
import numpy as np
from scipy.signal import resample_poly, butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 82.74   # voice length + 0.7 (python3 -I mix.py 82.74)
N = int(round(DUR * SR))
rng = np.random.default_rng(20261115)
t_ax = lambda d: np.arange(int(d * SR)) / SR

# ---------- voice ----------
w = wave.open(os.path.join(HERE, 'voice.wav'))
v24 = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
voice = resample_poly(v24, 2, 1)
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]

def add(buf, snd, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf[0]): return
    n = min(len(snd), len(buf[0]) - i)
    l, r = g * np.cos((pan + 1) * np.pi / 4), g * np.sin((pan + 1) * np.pi / 4)
    buf[0][i:i + n] += snd[:n] * l; buf[1][i:i + n] += snd[:n] * r

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)
def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)

# ---------- instruments ----------
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def pluck(midi, dur=5.0, vel=.8, bend=.012, bright=1.0):
    """guqin-like: additive partials with decays shortening upward, a small downward pitch glide, a soft noise transient"""
    f0 = mtof(midi); t = t_ax(dur); y = np.zeros_like(t)
    for k in range(1, 11):
        f = f0 * k * (1 + .0004 * k * k)
        if f > 9000: break
        a = vel / (k ** (1.25 / bright)); tau = dur * .26 / (1 + .55 * (k - 1))
        gl = 1 + bend * np.exp(-t / .12)
        y += a * np.sin(2 * np.pi * np.cumsum(f * gl) / SR + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    n = bp(rng.standard_normal(len(t)), 600, 4500) * np.exp(-t / .02) * .25 * vel
    y += n
    y *= np.minimum(1, t / .004)
    return y
def pad(midi, dur):
    t = t_ax(dur); f = mtof(midi)
    y = np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2 * t + 1) + .2 * np.sin(2 * np.pi * f * 3 * t + 2)
    y *= (1 + .08 * np.sin(2 * np.pi * .23 * t + midi))
    e = np.minimum(1, t / (dur * .35)) * np.minimum(1, (dur - t) / (dur * .35))
    return y * e
def pulse(dur=.9):
    t = t_ax(dur); return np.sin(2 * np.pi * 52 * np.exp(-t * 1.8) * t * 2.2 + 0) * np.exp(-t / .22)

# ---------- foley ----------
def brush(d):
    t = t_ax(d); e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    n = bp(rng.standard_normal(len(t)), 900, 5200) * (.6 + .4 * np.abs(bp(rng.standard_normal(len(t)), 3, 12, 1)) / 3)
    return n * e * .6
def ink(): t = t_ax(.5); return np.sin(2 * np.pi * 150 * np.exp(-t * 3) * t * 1.0) * np.exp(-t / .12) * .9 + lp(rng.standard_normal(len(t)), 1600) * np.exp(-t / .03) * .35
def pop():
    t = t_ax(.12); return (bp(rng.standard_normal(len(t)), 2200, 6500) * np.exp(-t / .008) * .8 + np.sin(2 * np.pi * (1200 - 4000 * t) * t) * np.exp(-t / .02) * .5)
def thud():
    t = t_ax(1.0); return np.sin(2 * np.pi * 68 * np.exp(-t * .8) * t) * np.exp(-t / .3) + lp(rng.standard_normal(len(t)), 300) * np.exp(-t / .12) * .7
def rustle(d):
    t = t_ax(d); e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    g = np.abs(lp(rng.standard_normal(len(t)), 40, 1)); g = g / g.max()
    return bp(rng.standard_normal(len(t)), 2500, 8000) * e * (.25 + g) * .55
def drip():
    t = t_ax(.5); return np.sin(2 * np.pi * (1500 - 2200 * np.minimum(t, .09)) * t) * np.exp(-t / .07) * .8 + np.sin(2 * np.pi * 330 * t) * np.exp(-t / .3) * .15
def seal_snd():
    t = t_ax(.7); th = np.sin(2 * np.pi * 88 * np.exp(-t * 1.5) * t) * np.exp(-t / .16)
    cr = (rng.random(len(t)) < .004) * rng.standard_normal(len(t)); cr = hp(cr, 1500) * np.exp(-t / .12) * 2.2
    return th * .9 + cr * .5
def ring():
    t = t_ax(4.0); return (np.sin(2 * np.pi * 587 * t) + .4 * np.sin(2 * np.pi * 587 * 2.76 * t)) * np.exp(-t / 1.0) * .6

# >>> PER-ABHANG: the sound events and the score below follow the picture timings (edit the times; the 5.00 % bed normalisation is automatic)
ev = [{'t': .05, 'type': 'brush', 'd': 1.3}, {'t': .1, 'type': 'ink'}, {'t': 1.5, 'type': 'brush', 'd': 3.5}, {'t': 7.0, 'type': 'ink'}, {'t': 7.7, 'type': 'brush', 'd': 1.2}, {'t': 8.5, 'type': 'rustle', 'd': 1.5}]
ev += [{'t': 11.8, 'type': 'brush', 'd': 1.5}, {'t': 13.0, 'type': 'ring'}, {'t': 15.0, 'type': 'drip'},
 {'t': 17.0, 'type': 'brush', 'd': 1.4}, {'t': 18.5, 'type': 'pop'}, {'t': 19.5, 'type': 'ring'},
 {'t': 20.8, 'type': 'brush', 'd': 1.5}, {'t': 22.0, 'type': 'rustle', 'd': 1.2}, {'t': 23.5, 'type': 'drip'},
 {'t': 25.0, 'type': 'brush', 'd': 1.2}, {'t': 26.5, 'type': 'ring'}, {'t': 28.0, 'type': 'drip'},
 {'t': 29.8, 'type': 'brush', 'd': 1.5}, {'t': 31.5, 'type': 'pop'}, {'t': 33.5, 'type': 'pop'}, {'t': 35.5, 'type': 'ring'},
 {'t': 37.5, 'type': 'brush', 'd': 1.8}, {'t': 39.5, 'type': 'ring'}, {'t': 41.5, 'type': 'pop'}, {'t': 43.5, 'type': 'drip'},
 {'t': 45.6, 'type': 'brush', 'd': 1.5}, {'t': 47.5, 'type': 'pop'}, {'t': 49.0, 'type': 'ink'}, {'t': 50.5, 'type': 'ring'}]
LT = [(52.51, 54.69), (55.51, 57.37), (58.65, 60.98), (61.57, 63.53), (64.84, 66.51), (67.00, 68.56)]
for a_, b_ in LT: ev.append({'t': a_, 'type': 'brush', 'd': .9}); ev.append({'t': a_ - .02, 'type': 'pop'})
ev += [{'t': 69.3, 'type': 'rustle', 'd': 1.0}, {'t': 70.0, 'type': 'brush', 'd': 1.5}, {'t': 71.8, 'type': 'ink'}, {'t': 74.4, 'type': 'seal'}, {'t': 75.0, 'type': 'ring'}]
sfx = [np.zeros(N), np.zeros(N)]
for e in ev:
    ty, at, d = e['type'], e['t'], e.get('d', 1.0)
    if ty == 'brush': add(sfx, brush(d), at, .7, rng.uniform(-.3, .3))
    elif ty == 'ink': add(sfx, ink(), at, .9)
    elif ty == 'pop': add(sfx, pop(), at, .8, rng.uniform(-.6, .6))
    elif ty == 'thud': add(sfx, thud(), at, 1.0)
    elif ty == 'rustle': add(sfx, rustle(d), at, .8)
    elif ty == 'drip': add(sfx, drip(), at, .9)
    elif ty == 'seal': add(sfx, seal_snd(), at, 1.0)
    elif ty == 'ring': add(sfx, ring(), at, .8)
# ambience beds: paper-room tone, a low wind under the heavy section
tt = np.arange(N) / SR
room = lp(rng.standard_normal(N), 900) * .05
wind = 0 * tt
for c in (0, 1): sfx[c] += room + wind * (1 if c == 0 else .8)

# ---------- score (pentatonic on D, unmetred) ----------
mus = [np.zeros(N), np.zeros(N)]
P = lambda at, m, dur=5.0, vel=.8, pan=0.0, **k: add(mus, pluck(m, dur, vel, **k), at, 1.0, pan)
for at, m, vel in [(.3, 62, .6), (1.6, 69, .45), (3.0, 74, .4), (4.4, 71, .4), (5.6, 66, .4)]: P(at, m, 4, vel, (m - 66) / 20)
for at, m, vel in [(7.6, 50, .8), (9.2, 57, .5), (10.8, 64, .45)]: P(at, m, 5, vel, 0.0)
add(mus, pad(38, 40) * .4 + pad(45, 40) * .3, 8.0, 1.0)
for at, m, vel in [(11.8, 62, .5), (14.0, 69, .45), (17.0, 50, .6), (19.0, 57, .5), (21.0, 64, .45), (23.0, 55, .45), (25.2, 62, .5), (27.5, 69, .45), (30.0, 67, .45), (33.0, 64, .4), (35.5, 57, .45),
                   (38.0, 62, .5), (41.0, 50, .6), (44.0, 64, .45), (46.0, 57, .4), (48.5, 62, .5), (50.5, 66, .4)]: P(at, m, 5, vel, (m - 60) / 30)
for (a_, b_), m in zip(LT, [62, 64, 66, 62, 69, 66]): P(a_ + .1, m, 4, .45, (m - 62) / 24)
for at, m, vel in [(69.5, 62, .55), (71.8, 57, .45), (74.4, 50, .8), (75.0, 62, .6)]: P(at, m, 5, vel, 0.0)
fadeout = np.clip((DUR - tt) / 2.0, 0, 1)
for c in (0, 1): mus[c] *= fadeout; sfx[c] *= np.clip((DUR - tt) / 0.8, 0, 1)

# ---------- levels: the bed sits at 5 % of the voice ----------
def active_rms(x, win=int(.05 * SR), rel=.05):
    n = len(x) // win; r = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1))
    sel = r > rel * np.percentile(r, 95); return np.sqrt((r[sel] ** 2).mean()), sel
vr, vsel = active_rms(voice)                       # voice RMS over speaking frames
TARGET = .05
m_mono = (mus[0] + mus[1]) / 2; s_mono = (sfx[0] + sfx[1]) / 2
mr, _ = active_rms(m_mono); sr_, _ = active_rms(s_mono)
gm = TARGET * .85 * vr / mr; gs = TARGET * .53 * vr / sr_      # sqrt(.85² + .53²) × 5 % = 5 % together
bed = [mus[c] * gm + sfx[c] * gs for c in (0, 1)]
_w = int(.05 * SR); _n = len(voice) // _w * _w; _bm = ((bed[0] + bed[1]) / 2)[:_n].reshape(-1, _w); _br = np.sqrt((_bm ** 2).mean(1)); _sel = vsel[:len(_br)]
_k = TARGET * vr / np.sqrt((_br[_sel] ** 2).mean()); bed = [b_ * _k for b_ in bed]; gm *= _k; gs *= _k
out = np.stack([voice + bed[0], voice + bed[1]], 1)
pk = np.abs(out).max()
if pk > .98: out *= .98 / pk
# report
n = len(voice) // int(.05 * SR) * int(.05 * SR); win = int(.05 * SR)
vwin = np.sqrt((voice[:n].reshape(-1, win) ** 2).mean(1)); bwin = np.sqrt((((bed[0] + bed[1]) / 2)[:n].reshape(-1, win) ** 2).mean(1))
rep = [f"voice speaking-frame RMS : {vr:.5f}  ({20 * np.log10(vr):.1f} dBFS)",
       f"music stem RMS (active)  : {mr * gm:.5f}  = {mr * gm / vr * 100:.2f} % of voice",
       f"sfx stem RMS (active)    : {sr_ * gs:.5f}  = {sr_ * gs / vr * 100:.2f} % of voice",
       f"bed (music+sfx) RMS over speaking frames: {np.sqrt((bwin[vsel[:len(bwin)]] ** 2).mean()):.5f} = {np.sqrt((bwin[vsel[:len(bwin)]] ** 2).mean()) / vr * 100:.2f} % of voice",
       f"bed peak {max(np.abs(bed[0]).max(), np.abs(bed[1]).max()):.4f}  voice peak {np.abs(voice).max():.4f}  mix peak {np.abs(out).max():.4f}",
       ]
open(os.path.join(HERE, 'out', 'levels.txt'), 'w').write("\n".join(rep) + "\n"); print("\n".join(rep))
pcm = (np.clip(out, -1, 1) * 32767).astype('<i2')
wv = wave.open(os.path.join(HERE, 'out', 'mix.wav'), 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(pcm.tobytes()); wv.close()
print('mix.wav written', len(pcm) / SR, 's')
