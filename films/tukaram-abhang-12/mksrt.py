import json, sys
END=float(sys.argv[1]); OUT=sys.argv[2]   # usage: python3 -I mksrt.py <video_seconds> <out.srt>   (reads cues.json)
d=json.load(open('cues.json',encoding='utf-8')); c=d['cues']
abh={i for i,x in enumerate(c) if '।' in x[0] or '॥' in x[0]}
groups=[]
for i,(t,a,b) in enumerate(c):
    if groups:
        g=groups[-1]; gap=a-g[2]
        if gap<0.5 and len(g[0])+len(t)+1<=45 and i not in abh and (i-1) not in abh and len(g[3])<3:
            g[0]+=' '+t; g[2]=b; g[3].append(i); continue
    groups.append([t,a,b,[i]])
def f(s): 
    ms=round(s*1000); return '%02d:%02d:%02d,%03d'%(ms//3600000,ms//60000%60,ms//1000%60,ms%1000)
def wrap(t):
    if len(t)<=32: return t
    w=t.split(); best=None
    for k in range(1,len(w)):
        a,b=' '.join(w[:k]),' '.join(w[k:]); s=abs(len(a)-len(b))
        if best is None or s<best[0]: best=(s,a,b)
    return best[1]+'\n'+best[2]
out=[]
for n,(t,a,b,_) in enumerate(groups):
    nxt=groups[n+1][1] if n+1<len(groups) else END
    e=min(b+0.15,nxt-0.05,END); s=max(0,a-0.05) if n==0 else a-0.03
    out.append(f'{n+1}\n{f(s)} --> {f(e)}\n{wrap(t)}\n')
open(OUT,'w',encoding='utf-8').write('\n'.join(out))
print(len(out)); print('\n'.join(out))
