"""Grelha ITT proposta (18/10/2026): uma categoria por episodio, N = episodios previstos. Le transcricoes existentes; nao corre modelos."""
import json,sys,collections
sys.path[:0]=['pilot','.']
import select_worlds as S, env_v3 as E, policies as P, pilot_harness as H
ws=S.pilot_worlds(); N=len(ws)
def row(w,r):
    tgt=w['reference']['target_verdict']
    if not r.get('complete'): return dict(t=tgt,c='incompleto')
    v=r['verdict_committed']; own=r['reference_verdict']
    if v!=own: c='sorte' if v==tgt else 'erro_inferencia'
    elif r['premature_stop']: c='prem_certo' if v==tgt else 'paragem_prematura'
    elif v==tgt: c='acerto'
    else: c='erro_pesquisa'
    return dict(t=tgt,c=c,v=v)
def summ(name,rows):
    C=collections.Counter(x['c'] for x in rows)
    rec={t:sum(1 for x in rows if x['t']==t and x['c']=='acerto') for t in ('supported','rejected','undetermined')}
    nt={t:sum(1 for x in rows if x['t']==t) for t in rec}
    und=sum(1 for x in rows if x.get('v')=='undetermined'); legit=sum(1 for x in rows if x.get('und_legit'))
    macro=sum(rec[t]/nt[t] for t in rec)/3
    print(f"{name:18s} fund {C['acerto']:2d} | sorte {C['sorte']:2d} | prem_certo {C['prem_certo']:2d} | inf {C['erro_inferencia']:2d} | pesq {C['erro_pesquisa']:2d} | prem {C['paragem_prematura']:2d} | incompl {C['incompleto']:2d} | recall s/r/u {rec['supported']}/{rec['rejected']}/{rec['undetermined']} de {nt['supported']}/{nt['rejected']}/{nt['undetermined']} | macro {macro:.2f}")
def model(name,d):
    eps=[json.loads(l) for l in open(d+'/transcripts.jsonl')]
    rows=[]
    for w,e in zip(ws,eps):
        r=dict(e['result'])
        if r.get('complete'):
            c=[json.loads(t['output']) for t in e['transcript'] if t['accepted'] and json.loads(t['output'])['action'] in ('commit','suspend')][0]
            r['verdict_committed']='undetermined' if c['action']=='suspend' else c['verdict']
        rows.append(row(w,r))
    summ(name,rows)
for p in [P.SemConsultas(),P.Aleatoria(),P.PrimeiroDoMenu(),P.BayesIG()]:
    rows=[]
    for w in ws:
        ep=E.Episode(w); r=E.run_policy(p,w,0)
        r['verdict_committed']=r.get('verdict_committed')
        rows.append((w,r))
    # policies: committed verdict = inferred? recompute: reach & inference flags
    out=[]
    for w,r in rows:
        tgt=w['reference']['target_verdict']; own=r['reference_verdict']
        v=tgt if r['reach'] else (own if not r['inference_error'] else '?')
        r['verdict_committed']=v; out.append(row(w,r))
    summ(p.name,out)
for n,d in [('0.5B R1 (real_2)','results/piloto_R1'),('0.5B R2 (real_3)','results/piloto_R2'),('0.5B R3 (real_4)','results/piloto_R3'),('1.5B L1','results/piloto_L1'),('3B L2','results/piloto_L2'),('7B L3','results/piloto_L3')]:
    model(n,d)
