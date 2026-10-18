"""Compara a consulta decisiva de um passo (scoring.can_still_determine) com a versao de k passos, nos estados de commit das transcricoes."""
import json,sys,collections
sys.path[:0]=['pilot','.']
import select_worlds as S, env_v3 as E, generator_v3 as g, scoring as sc
def det_k(A,w,T,free,k):
    if g.verdict(A,w,T)!='undetermined': return True
    if k==0: return False
    for q in free:
        for y in {h[q] for h in A}:
            if det_k(frozenset(h for h in A if h[q]==y),w,T,[x for x in free if x!=q],k-1): return True
    return False
ws=S.pilot_worlds(); diff=collections.Counter()
for name in ['piloto_R3','piloto_L1','piloto_L2']:
    eps=[json.loads(l) for l in open(f'results/{name}/transcripts.jsonl')]
    for w,e in zip(ws,eps):
        ep=E.Episode(w); hid=w['hidden']
        for t in e['transcript']:
            a=json.loads(t['output'])
            if t['phase']=='explore' and a['action'] in ('commit','suspend') and t['accepted']:
                A=g.admissible_idx(sc.history_rows(w,ep.queried)); free=[q for q in hid['menu'] if q not in ep.queried]
                if g.verdict(A,hid['w'],hid['T'])=='undetermined' and ep.left>0:
                    one=sc.can_still_determine(A,hid['w'],hid['T'],free); k=det_k(A,hid['w'],hid['T'],free,ep.left)
                    diff[(name,ep.left,one,k)]+=1
            act=H_conv=a
            if 'env_action' in t: act=t['env_action']
            ep.step(act)
for k,v in sorted(diff.items()): print(k,v)
