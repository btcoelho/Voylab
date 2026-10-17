from __future__ import annotations
import ast
import contextlib
import compileall
import json
import os
from pathlib import Path
import subprocess
import sys
import io
from types import SimpleNamespace

repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo))

commit = subprocess.run(
    ["git", "-C", str(repo), "rev-parse", "HEAD"],
    check=True, capture_output=True, text=True,
).stdout.strip()
result = {"repo": str(repo), "commit": commit, "tests": {}, "credentials_present": {
    "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
    "TOGETHER_API_KEY": bool(os.environ.get("TOGETHER_API_KEY")),
}}
result["tests"]["python_compile"] = bool(
    compileall.compile_dir(str(repo / "autoscilab"), quiet=1)
    and compileall.compile_dir(str(repo / "scripts"), quiet=1)
    and compileall.compile_dir(str(repo / "newtonbench_vendor"), quiet=1)
)
assert result["tests"]["python_compile"]

from autoscilab.oracle.grnbench import GRNBenchOracle
from autoscilab.data.store import ExperimentStore
from autoscilab.grn_autoscilab.loop import (
    GRNMEIGraphConfig,
    _build_reasoning_prompt,
    _lineage_summary,
    _store_to_table,
)

with contextlib.redirect_stdout(io.StringIO()):
    oracle = GRNBenchOracle(
        domain_id="g2_incoherent_feedforward",
        difficulty="medium",
        noise_level=0.0,
        law_version="v1",
        grammar_mode="none",
    )
params = {name: (lo * hi) ** 0.5 for name, (lo, hi) in oracle.parameter_bounds.items()}
r1 = oracle.run(params)
r2 = oracle.run(params)
assert r1.measurement == r2.measurement
assert set(r1.metadata["marker_panel"]) >= {"A", "B", "C", "R", "reporter"}
assert "graph_edges" in r1.metadata and "motif_id" in r1.metadata
store = ExperimentStore(oracle.domain, oracle.parameter_names)
store.add(r1)
table = _store_to_table(store)
assert "reporter" in table and "graph_edges" not in table and "motif_id" not in table
result["tests"]["grn_oracle_determinism_and_observation_projection"] = {
    "passed": True,
    "measurement": r1.measurement,
    "public_table_has_marker_panel": True,
    "oracle_result_also_contains_hidden_truth_metadata": True,
}

truth = oracle.ground_truth_adjacency
wrong = truth.copy()
wrong[wrong != 0] = 0
assert oracle.evaluate_graph({"adjacency": truth.tolist()})["edge_f1"] == 1.0
assert oracle.evaluate_graph({"adjacency": wrong.tolist()})["edge_f1"] == 0.0
lineage = SimpleNamespace(
    hypothesis_id="h1",
    hypothesis_text="mechanism candidate",
    exact_graph={"adjacency": wrong.tolist()},
    exact_fit=SimpleNamespace(summary="fit candidate A"),
    best_fit=SimpleNamespace(
        summary="fit candidate B",
        graph={"adjacency": truth.tolist()},
    ),
    drift_steps=0,
    drift_summary="no drift",
)
summary = _lineage_summary(oracle, [lineage])
assert "edge_f1=0.000" in summary and "edge_f1=1.000" in summary
prompt = _build_reasoning_prompt(
    GRNMEIGraphConfig(domain_id=oracle.domain),
    oracle,
    store,
    "candidate",
    summary,
    10,
)
assert "edge_f1=1.000" in prompt and "edge_f1=0.000" in prompt
result["tests"]["grn_ground_truth_score_reaches_llm_prompt"] = {
    "passed": True,
    "minimal_counterexample": summary,
    "prompt_contains_oracle_derived_edge_f1": True,
}

src = (repo / "autoscilab" / "loop" / "discovery.py").read_text(encoding="utf-8")
assert "mid_run_gt_eval: bool = True" in src
assert "gt_eval = self._oracle.evaluate_law(eq.law_str)" in src
assert "self._last_gt_eval = gt_eval" in src
assert "gt_metrics_str=gt_metrics_str" in src
assert '"GT RMSLE: "' in src or "GT RMSLE:" in src
assert "self._best_gt_equation = eq" in src
assert "final_eq = self._best_gt_equation" in src
result["tests"]["newton_ground_truth_used_during_inference"] = {
    "passed": True,
    "evidence": [
        "mid_run_gt_eval defaults true",
        "evaluate_law is called before the run ends",
        "GT RMSLE is inserted in validation prompt passed back to LLM",
        "GT metrics select/cap candidate and confidence; final equation can be replaced by GT-best",
    ],
}

result["tests"]["license_file_present"] = any(
    (repo / name).exists() for name in ("LICENSE", "LICENSE.txt", "COPYING")
)
tracked = subprocess.run(
    ["git", "-C", str(repo), "ls-files", "*test*"],
    check=True, capture_output=True, text=True,
).stdout.splitlines()
result["tests"]["tracked_test_files"] = tracked
result["decision"] = "not_valid_for_unbiased_scientific_performance_claims_without_repair"
payload = json.dumps(result, indent=2, ensure_ascii=False)
if len(sys.argv) > 2:
    Path(sys.argv[2]).resolve().write_text(payload + "\n", encoding="utf-8")
print(payload)
