"""Standalone, stdlib-only replay of the frozen v2.3 synthetic pilot."""
import argparse
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line]

def strict_object(raw):
    def hook(pairs):
        result={}
        for k,v in pairs:
            if k in result: raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    value=json.loads(raw,object_pairs_hook=hook,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    if not isinstance(value,dict): raise ValueError('not an object')
    return value

def prediction(card,row):
    text=card['statement'].lower()
    fields=('glyph','phase') if 'glyph and phase' in text else ('glyph',) if 'only on glyph' in text else ('setting',) if 'only on setting' in text else None
    if fields is None: raise ValueError('unsupported model statement')
    key='|'.join(row['input'][field] for field in fields)
    return card['table'].get(key,object())==row['output']

def labels(state):
    cards={c['id']:c for c in state['candidate_models']}; rows=state['observations']
    viable=sorted(cid for cid,card in cards.items() if all(prediction(card,r) for r in rows))
    working=cards[state['working_model']['id']]
    verdict='undetermined' if not rows else 'supported' if all(prediction(working,r) for r in rows) else 'rejected'
    diagnosis='none_fit' if not viable else 'identified' if len(viable)==1 else 'ambiguous'
    sufficiency='no_observations' if not rows else 'no_candidate_fits' if not viable else 'identity_resolved' if len(viable)==1 else 'identity_ambiguous'
    return {'candidates':viable,'diagnosis':diagnosis,'sufficiency':sufficiency,'verdict':verdict}

def score(state,action):
    rows=state['observations']; cards={c['id']:c for c in state['candidate_models']};
    ids={r['id'] for r in rows}; cardids=set(cards)
    legal=(action.get('action')=='report' and set(action.get('evidence_ids',[]))<=ids
           and set(action.get('candidate_model_codes',[]))<=cardids)
    truth=labels(state); working=cards[state['working_model']['id']]
    cited=[r for r in rows if r['id'] in set(action.get('evidence_ids',[]))]
    v=action.get('verdict')
    if v=='supported': cert=bool(rows) and all(any(c['input']==r['input'] and c['output']==r['output'] for c in cited) for r in rows)
    elif v=='rejected': cert=any(not prediction(working,r) for r in cited)
    else: cert=not rows and not action.get('evidence_ids',[])
    loc=action.get('location',{'feature':'none','values':[]}); locok=loc=={'feature':'none','values':[]}
    if loc.get('feature')!='none':
        vals=set(loc.get('values',[])); locok=len(vals)==2
        if locok:
            locok=any(all(a['input'][f]==b['input'][f] for f in ('glyph','setting','partner','phase') if f!=loc['feature'])
                       and a['input'][loc['feature']]!=b['input'][loc['feature']]
                       and a['output']!=b['output'] and {a['input'][loc['feature']],b['input'][loc['feature']]}==vals
                       for a,b in combinations(cited,2))
    components={'legal':legal,'expected_verdict':truth['verdict'],
       'expected_candidate_model_codes':truth['candidates'],'expected_diagnosis':truth['diagnosis'],
       'expected_sufficiency':truth['sufficiency'],'verdict_correct':v==truth['verdict'],
       'candidates_correct':set(action.get('candidate_model_codes',[]))==set(truth['candidates']),
       'diagnosis_correct':action.get('diagnosis')==truth['diagnosis'],
       'sufficiency_correct':action.get('sufficiency')==truth['sufficiency'],
       'evidence_certificate_sufficient':cert,'location_supported':None if locok else False}
    components['joint_success']=legal and all((components['verdict_correct'],components['candidates_correct'],
       components['diagnosis_correct'],components['sufficiency_correct'],cert,locok))
    return components

def replay(trial_dir):
    trial=Path(trial_dir); run=trial/'run_20261017'
    schedule={x['episode_id']:x for x in load_jsonl(trial/'public_schedule.jsonl')}
    events=load_jsonl(run/'events.jsonl'); outcomes={x['episode_id']:x for x in json.loads((run/'outcomes.json').read_text(encoding='utf-8'))}
    if len(schedule)!=10 or set(schedule)!=set(outcomes): raise AssertionError('episode set mismatch')
    if [e['sequence'] for e in events]!=list(range(1,len(events)+1)): raise AssertionError('journal sequence gap')
    ep_at={}; ep=None; raw={}; actions=defaultdict(list); gens=Counter(); prompts=defaultdict(list); malformed=[]
    for e in events:
        if e['kind']=='episode_start': ep=e['episode_id']
        ep_at[e['sequence']]=ep
        if e['kind']=='generation': gens[e['episode_id']]+=1
        if e['kind']=='prompt':
            p=e['prompt']; payload=p.split('<|im_start|>user\n',1)[1].split('<|im_end|>',1)[0]
            if hashlib.sha256(p.encode()).hexdigest()!=e['prompt_sha256'] or json.loads(payload)!=schedule[e['episode_id']]['public_state']:
                raise AssertionError('prompt/hash mismatch')
            prompts[e['episode_id']].append(p)
        if e['kind']=='raw_action':
            try: raw[e['sequence']]=(ep,strict_object(e['raw']))
            except (ValueError,json.JSONDecodeError):
                gen=next(x for x in reversed(events[:e['sequence']-1]) if x['kind']=='generation')
                malformed.append({'episode_id':ep,'tokens':gen['generated_token_count'],'eos':gen['eos_terminated']})
        if e['kind']=='action_result':
            owner,action=raw[e['raw_sequence']]
            if action!=e['action']: raise AssertionError('decoded action differs from durable raw output')
            actions[owner].append((action,e['result']))
    per=[]
    for ep,item in schedule.items():
        truth=labels(item['public_state'])
        if truth!=item['expected_initial']: raise AssertionError(f'{ep}: schedule labels disagree')
        reports=[]
        for action,result in actions[ep]:
            if action.get('action')=='report' and result.get('accepted'):
                computed=score(item['public_state'],action); stored=outcomes[ep]['evaluation']
                required=set(computed)
                if not required<=set(stored) or any(stored[k]!=computed[k] for k in required):
                    raise AssertionError(f'{ep}: report scoring mismatch')
                reports.append(computed)
        actual=outcomes[ep]
        status='model_output_failure' if ep=='pilot_01' and 'JSONDecodeError' in actual.get('error','') else actual['status']
        if actual['status']=='call_limit_no_report': status='call_limit_no_valid_terminal_action'
        per.append({'episode_id':ep,'stratum':item['design_stratum'],'status':status,'calls':gens[ep],
                    'reports_attempted':sum(a.get('action')=='report' for a,r in actions[ep]),
                    'illegal_actions':sum(not r.get('accepted') for a,r in actions[ep]),
                    'legal_reports':len(reports),'score':reports[-1] if reports else None,
                    'distinct_prompts':len(set(prompts[ep]))})
    total=len(per); successes=sum(bool(x['score'] and x['score']['joint_success']) for x in per)
    status_counts=dict(Counter(x['status'] for x in per))
    return {'protocol':'TRONCO-01-v2.3-pilot-v0.1','replay':'independent stdlib reference; saved data only',
       'new_model_calls':0,'episodes':per,'summary':{'episodes':total,'generation_calls':sum(gens.values()),
       'malformed':len(malformed),'legal_reports':sum(x['legal_reports'] for x in per),
       'illegal_decoded_actions':sum(x['illegal_actions'] for x in per),'accepted_queries':sum(r.get('accepted') and 'observation' in r for values in actions.values() for a,r in values),
       'joint_successes':successes,'joint_rate_all_episodes':successes/total if total else None,
       'status_counts':status_counts,'malformed_at_token_limit_without_eos':sum(x['tokens']==256 and not x['eos'] for x in malformed)},
       'missing_initial_preregistration':'Only its SHA-256 is retained; original contents unavailable.'}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--trial-dir',type=Path,default=ROOT/'fixtures/v23')
    parser.add_argument('--output',type=Path); args=parser.parse_args()
    result=replay(args.trial_dir); rendered=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output: args.output.write_text(rendered,encoding='utf-8')
    print(rendered,end='')

if __name__=='__main__': main()
