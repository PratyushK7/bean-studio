import json,glob,re,statistics,sys
FMT=[("What if",r"^what if|^what would happen|^what happens if"),
 ("How many / how much / how long",r"^how (many|much|long|far|big|fast|hot|cold|deep|high|old)"),
 ("How it works / how X is made",r"^how (do|does|did|is|are|was|to)\b|how .* (works?|made)\b"),
 ("Why",r"^why\b|\bwhy\b"),
 ("Superlative (most/deadliest/biggest)",r"\b(most|deadliest|largest|biggest|smallest|fastest|strongest|worst|best|oldest|longest|weirdest|rarest|only)\b"),
 ("Would you / you vs / survive",r"would you|could you|can you|survive|\bvs\.?\b|versus"),
 ("Myth / truth / wrong",r"\bmyth|\btruth|\bwrong\b|actually|\blie\b|isn.t|aren.t|not what|you think|really"),
 ("Story / history (real event)",r"\b(1[0-9]{3}|20[0-2][0-9])\b|\bman who\b|\bwoman who\b|\bguy who\b|\bstory\b|history|happened"),
 ("Is it possible / can X",r"^(is|are|can|could|does|do)\b"),
 ("Experiment / test / tried",r"\btried\b|\btest\b|experiment|\bi (built|made|bought|spent)\b|\bwe (built|made)\b"),
 ("Number-first / list",r"^\d|\b\d+ (things|ways|reasons|facts|signs)\b"),
 ("Cryptic / statement",r".")]
def fmt(t):
    for n,p in FMT:
        if re.search(p,t,re.I): return n
def load(kind):
    rows=[]
    for f in glob.glob(kind+"/*.json"):
        try: d=json.load(open(f,encoding='utf-8'))
        except Exception: continue
        if not isinstance(d,dict): continue
        ch=d.get('channel') or d.get('uploader') or f
        vs=[e for e in (d.get('entries') or []) if e and e.get('view_count')]
        if len(vs)<8: continue
        med=statistics.median(e['view_count'] for e in vs)
        for e in vs:
            t=re.sub(r"\s*#\S+","",e.get('title','')).strip()
            rows.append(dict(ch=ch,t=t,v=e['view_count'],m=e['view_count']/med,f=fmt(t)))
    return rows
for kind in ("shorts","long"):
    rows=load(kind); chs=sorted(set(r['ch'] for r in rows))
    print(f"\n===== {kind.upper()}: {len(rows)} videos, {len(chs)} channels: {', '.join(chs)}")
    by={}
    for r in rows: by.setdefault(r['f'],[]).append(r)
    print(f"{'format':40} {'n':>4} {'median x':>8} {'% at 2x+':>8}")
    for f,rs in sorted(by.items(),key=lambda x:-statistics.median(r['m'] for r in x[1])):
        if len(rs)<6: continue
        print(f"{f:40} {len(rs):4d} {statistics.median(r['m'] for r in rs):8.2f} {100*sum(r['m']>=2 for r in rs)/len(rs):7.0f}%")
    print("\n-- top outliers")
    for r in sorted(rows,key=lambda r:-r['m'])[:int(sys.argv[1]) if len(sys.argv)>1 else 45]:
        print(f"{r['m']:6.1f}x {r['v']:>11,}  {r['ch'][:18]:18} [{r['f'][:14]:14}] {r['t'][:80]}")
