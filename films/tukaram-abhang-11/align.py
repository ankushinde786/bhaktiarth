"""Sync an SRT to a voice-over: detect pauses in the audio, match the script's phrases to the speech between them (DP on speaking rate)."""
import numpy as np, wave, re, math, sys, json
from scipy.ndimage import median_filter
wav, script, out = sys.argv[1:4]
w = wave.open(wav); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
if w.getnchannels() > 1: x = x.reshape(-1, w.getnchannels()).mean(1)
hop = int(sr * .01); fr = x[:len(x) // hop * hop].reshape(-1, hop); db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9); H = .01; T = len(db) * H
th = float(sys.argv[4]) if len(sys.argv) > 4 else -33
quiet = median_filter(db, size=5) < th
pauses = []; i = 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]: j += 1
        if (j - i) * H >= .15: pauses.append((i * H, j * H))
        i = j
    else: i += 1
lead = pauses[0] if pauses and pauses[0][0] < .01 else None; trail = pauses[-1] if pauses and pauses[-1][1] > T - .02 else None
start = lead[1] if lead else 0.0; end = trail[0] if trail else T
inner = [p for p in pauses if p[0] > start + .05 and p[1] < end - .05]
txt = open(script, encoding='utf-8').read(); ph = []; ty = []; para_end = []
for p in re.split(r'\n\s*\n', txt):
    for line in p.strip().splitlines():
        for s in re.findall(r'[^।.?!,:;॥]+[।.?!,:;॥]*', line):
            s = s.strip()
            if s: ph.append(s); ty.append(s[-1])
    para_end.append(len(ph) - 1)
ch = [len(re.sub(r'[\s।.?!,:;॥]', '', s)) for s in ph]; P = len(ph); M = len(inner)
print('speech %.2f-%.2f  pauses %d  phrases %d  paragraphs %d' % (start, end, M, P, len(para_end)))
def between(k1, k2):
    a = start if k1 == 0 else inner[k1 - 1][1]; b = end if k2 == M + 1 else inner[k2 - 1][0]; s = b - a
    for q in range(k1 + 1, k2): s -= inner[q - 1][1] - inner[q - 1][0]
    return s
plen = lambda k: 0 if k in (0, M + 1) else inner[k - 1][1] - inner[k - 1][0]
exp = lambda c: .8 if c in '।॥.?!' else .3
R, SIG, INF = 10.5, .33, 1e18
dp = [[INF] * (M + 2) for _ in range(P + 1)]; bk = [[None] * (M + 2) for _ in range(P + 1)]; dp[0][0] = 0
for p in range(P):
    last = p == P - 1
    for k in range(M + 2):
        if dp[p][k] >= INF: continue
        for k2 in range(k + 1, M + 2):
            if last != (k2 == M + 1): continue
            sp = between(k, k2)
            if sp <= .15: continue
            c = (ch[p] / 10) * (math.log(ch[p] / sp / R) / SIG) ** 2
            if not last:
                L = plen(k2); e = exp(ty[p]); c += 6 * max(0, e - L) / e
                if p in para_end: c += 4 * max(0, .7 - L)          # paragraph ends are the long pauses
            c += .6 * (k2 - k - 1); v = dp[p][k] + c
            if v < dp[p + 1][k2]: dp[p + 1][k2] = v; bk[p + 1][k2] = k
path = [M + 1]; p = P; k = M + 1
while p > 0: k = bk[p][k]; path.append(k); p -= 1
path.reverse(); cues = []
for p in range(P):
    k1, k2 = path[p], path[p + 1]; a = start if k1 == 0 else inner[k1 - 1][1]; b = end if k2 == M + 1 else inner[k2 - 1][0]
    cues.append([ph[p], a, b]); print(f'{p + 1:2d} {a:7.2f}-{b:7.2f} rate {ch[p] / between(k1, k2):5.1f} gap {plen(k2):4.2f}  {ph[p]}')
json.dump({'cues': cues, 'para_end': para_end}, open('cues.json', 'w'), ensure_ascii=False)
