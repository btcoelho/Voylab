"""Tokenizer/grammar conformance only: loads tokenizer files, never weights."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from importlib.metadata import version
from pathlib import Path

TOKENIZER_PATH=Path(os.environ.get("TRONCO_TOKENIZER_PATH",
    "/home/bcoelho/.cache/huggingface/hub/models--unsloth--Qwen2.5-0.5B-Instruct-bnb-4bit/snapshots/216d96b52c97a3c8294776df8477592f6828981c"))

def main():
    import transformers
    import transformers.tokenization_utils as tokenization_utils
    from transformers import AutoTokenizer, PreTrainedTokenizerBase
    tokenization_utils.PreTrainedTokenizerBase=PreTrainedTokenizerBase
    from lmformatenforcer import JsonSchemaParser
    from lmformatenforcer.characterlevelparser import UnionParser
    from lmformatenforcer.tokenenforcer import TokenEnforcer,TokenEnforcerTokenizerData
    from harness import ModelOutputError, public_action_schema, validate_action_shape
    if not TOKENIZER_PATH.is_dir():
        raise FileNotFoundError(f"Tokenizer not found: {TOKENIZER_PATH}")
    tokenizer=AutoTokenizer.from_pretrained(str(TOKENIZER_PATH),local_files_only=True)
    state={"candidate_models":[{"id":"A"},{"id":"B"}],
        "observations":[{"id":"o1","input":{"glyph":"g0"},"output":"0"}],
        "query_menu":[{"id":"q0","input":{"glyph":"g1"}}],
        "remaining_query_budget":1,"working_model":{"id":"A"}}
    prompt="Return one action as JSON.\n"
    token_0=tokenizer.encode("0")[-1]; regular=[]
    for token_id in range(len(tokenizer)):
        if token_id in tokenizer.all_special_ids: continue
        decoded_after_0=tokenizer.decode([token_0,token_id])[1:]
        decoded=tokenizer.decode([token_id])
        regular.append((token_id,decoded_after_0,len(decoded_after_0)>len(decoded)))
    data=TokenEnforcerTokenizerData(regular,lambda ids:tokenizer.decode(ids).rstrip("�"),
        tokenizer.eos_token_id,use_bitmask=False,vocab_size=len(tokenizer))
    schema=public_action_schema(state)
    parser=UnionParser([JsonSchemaParser(branch) for branch in schema["oneOf"]])
    enforcer=TokenEnforcer(data,parser)
    prefix=tokenizer(prompt,add_special_tokens=False)["input_ids"]
    valid={
        "query":'{"action":"query","query_id":"q0"}',
        # Deliberately scientifically wrong, but structurally legal: grammar must not reveal the answer.
        "wrong_but_structural_report":'{"action":"report","verdict":"undetermined","candidate_model_codes":[],"diagnosis":"none_fit","sufficiency":"no_observations","evidence_ids":[],"location":{"feature":"none","values":[]}}'
    }
    invalid={
        "unknown_query_id":'{"action":"query","query_id":"q9"}',
        "unknown_evidence_id":'{"action":"report","verdict":"supported","candidate_model_codes":["A"],"diagnosis":"identified","sufficiency":"identity_resolved","evidence_ids":["ox"],"location":{"feature":"none","values":[]}}',
        "missing_required_key":'{"action":"query"}',
        "extra_key":'{"action":"query","query_id":"q0","extra":1}',
        "wrong_type":'{"action":"query","query_id":42}'
        ,"unknown_location_value":'{"action":"report","verdict":"supported","candidate_model_codes":["A"],"diagnosis":"identified","sufficiency":"identity_resolved","evidence_ids":["o1"],"location":{"feature":"glyph","values":["invented","g0"]}}'
    }
    trace={}
    def check(name,text,active_enforcer):
        generated=tokenizer(text,add_special_tokens=False)["input_ids"]; ids=list(prefix); accepted=[]
        for token_id in generated:
            choices=active_enforcer.get_allowed_tokens(ids).allowed_tokens
            accepted.append(token_id in choices)
            if token_id not in choices: break
            ids.append(token_id)
        eos=tokenizer.eos_token_id
        eos_allowed=eos is not None and eos in active_enforcer.get_allowed_tokens(ids).allowed_tokens
        trace[name]={"tokens":len(generated),"all_payload_tokens_allowed":len(accepted)==len(generated) and all(accepted),
                     "eos_allowed":bool(eos_allowed)}
    for name,text in {**valid,**invalid}.items():
        check(name,text,enforcer)
    duplicate_cases={
        "duplicate_candidate_ids":'{"action":"report","verdict":"supported","candidate_model_codes":["A","A"],"diagnosis":"identified","sufficiency":"identity_resolved","evidence_ids":["o1"],"location":{"feature":"none","values":[]}}',
        "duplicate_evidence_ids":'{"action":"report","verdict":"supported","candidate_model_codes":["A"],"diagnosis":"identified","sufficiency":"identity_resolved","evidence_ids":["o1","o1"],"location":{"feature":"none","values":[]}}',
        "duplicate_location_values":'{"action":"report","verdict":"supported","candidate_model_codes":["A"],"diagnosis":"identified","sufficiency":"identity_resolved","evidence_ids":["o1"],"location":{"feature":"glyph","values":["g0","g0"]}}'
    }
    duplicate_state={"candidate_models":[{"id":"A"},{"id":"B"}],
        "observations":[{"id":"o1","input":{"glyph":"g0"},"output":"0"},
                        {"id":"o2","input":{"glyph":"g1"},"output":"1"}],
        "query_menu":[],"remaining_query_budget":0}
    duplicate_schema=public_action_schema(duplicate_state)
    duplicate_enforcer=TokenEnforcer(data,UnionParser([JsonSchemaParser(branch) for branch in duplicate_schema["oneOf"]]))
    for name,text in duplicate_cases.items():
        check(name,text,duplicate_enforcer)
    duplicate_validator_rejects={}
    for name,text in duplicate_cases.items():
        try:
            validate_action_shape(json.loads(text),duplicate_state)
            duplicate_validator_rejects[name]=False
        except ModelOutputError:
            duplicate_validator_rejects[name]=True
    empty_state={"candidate_models":[{"id":"A"},{"id":"B"},{"id":"C"}],
        "observations":[],"query_menu":[{"id":"q0","input":{"glyph":"g0"}}],
        "remaining_query_budget":0,"working_model":{"id":"A"}}
    empty_parser=UnionParser([JsonSchemaParser(branch) for branch in public_action_schema(empty_state)["oneOf"]])
    empty_enforcer=TokenEnforcer(data,empty_parser)
    check("empty_history_report",
        '{"action":"report","verdict":"undetermined","candidate_model_codes":["A","B","C"],"diagnosis":"ambiguous","sufficiency":"no_observations","evidence_ids":[],"location":{"feature":"none","values":[]}}',
        empty_enforcer)
    check("query_at_zero_budget",'{"action":"query","query_id":"q0"}',empty_enforcer)
    max_state={"candidate_models":[{"id":"A"},{"id":"B"},{"id":"C"}],
        "observations":[{"id":f"o{i+1}","input":{"glyph":("g0","g1")[i%2],
        "setting":("s0","s1")[i%2],"partner":("p0","p1")[i%2],
        "phase":("t0","t1")[i%2]},"output":str(i%2)} for i in range(6)],
        "query_menu":[{"id":f"q{i}","input":{"glyph":"g0"}} for i in range(6)],
        "remaining_query_budget":0,"working_model":{"id":"A"}}
    max_parser=UnionParser([JsonSchemaParser(branch) for branch in public_action_schema(max_state)["oneOf"]])
    max_enforcer=TokenEnforcer(data,max_parser)
    max_report=json.dumps({"action":"report","verdict":"rejected",
        "candidate_model_codes":["A","B","C"],"diagnosis":"ambiguous",
        "sufficiency":"identity_ambiguous","evidence_ids":[f"o{i}" for i in range(1,7)],
        "location":{"feature":"glyph","values":["g0","g1"]}},separators=(",",":"))
    check("largest_bounded_report",max_report,max_enforcer)
    result={"tokenizer_path":str(TOKENIZER_PATH),"tokenizer_name":tokenizer.name_or_path,
        "tokenizer_sha256":{name:hashlib.sha256((TOKENIZER_PATH/name).read_bytes()).hexdigest()
          for name in ("tokenizer.json","tokenizer_config.json") if (TOKENIZER_PATH/name).is_file()},
        "python":sys.version.split()[0],"transformers":transformers.__version__,
        "lm_format_enforcer":version("lm-format-enforcer"),"vocabulary_size":len(tokenizer),
        "model_weights_loaded":False,"model_inference":False,"cases":trace,
        "duplicate_cases_final_validator_rejects":duplicate_validator_rejects,
        "valid_payloads_complete_and_eos_allowed":all(trace[x]["all_payload_tokens_allowed"] and trace[x]["eos_allowed"] for x in (*valid,"empty_history_report","largest_bounded_report")),
        "invalid_payloads_blocked":all(not trace[x]["all_payload_tokens_allowed"] or not trace[x]["eos_allowed"] for x in (*invalid,"query_at_zero_budget")),
        "largest_bounded_report_below_256_tokens":trace["largest_bounded_report"]["tokens"]<256,
        "wrong_semantic_report_remains_structurally_allowed":trace["wrong_but_structural_report"]["all_payload_tokens_allowed"] and trace["wrong_but_structural_report"]["eos_allowed"]}
    if not all((result["valid_payloads_complete_and_eos_allowed"],result["invalid_payloads_blocked"],
                result["wrong_semantic_report_remains_structurally_allowed"],result["largest_bounded_report_below_256_tokens"])):
        raise AssertionError(json.dumps(result,indent=2))
    if not all(trace[name]["all_payload_tokens_allowed"] and trace[name]["eos_allowed"]
               and duplicate_validator_rejects[name] for name in duplicate_cases):
        raise AssertionError("duplicate-handling boundary differs from the declared final-validator policy: " + json.dumps({"cases": {name: trace[name] for name in duplicate_cases}, "validator": duplicate_validator_rejects}, indent=2))
    output=Path(__file__).resolve().parent/"results/tokenizer_preflight_v2_5.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
