"""Audit of world identity (18/10/2026). Reads only generated sets already used; changes no historical file.

For each set: legacy world_id uniqueness, uid uniqueness, content uniqueness, structure groups (hidden mechanism + W),
and group overlap between sets. Writes the pilot mapping (order -> legacy id, uid, content hash, group).
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "pilot")]
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import run_policies as rp  # noqa: E402
import select_worlds as S  # noqa: E402


def describe(ws):
    ids = collections.Counter(w["world_id"] for w in ws)
    return {"worlds": len(ws), "legacy_ids": len(ids), "max_worlds_per_legacy_id": max(ids.values()),
            "uids": len({w["uid"] for w in ws}), "contents": len({g.content_sha(w) for w in ws}),
            "structure_groups": len({g.structure_group(w) for w in ws})}


def main():
    sets = {"piloto": S.pilot_worlds()}
    for name, seeds in (("dev", a.DEV_SEEDS), ("substituto", rp.SUBSTITUTE_SEEDS), ("confirmacao", rp.CONFIRM_SEEDS)):
        sets[name] = a.dev_set(seeds=seeds, with_indirect=True, balanced=True)
    out = {"sets": {k: describe(v) for k, v in sets.items()}}
    groups = {k: {g.structure_group(w) for w in v} for k, v in sets.items()}
    contents = {k: {g.content_sha(w) for w in v} for k, v in sets.items()}
    names = [k for k in sets if k != "piloto"]
    out["overlap_between_seed_sets"] = {
        f"{x}|{y}": {"shared_structure_groups": len(groups[x] & groups[y]), "shared_contents": len(contents[x] & contents[y])}
        for i, x in enumerate(names) for y in names[i + 1:]}
    out["pilot_subset_of_dev"] = contents["piloto"] <= contents["dev"]
    out["pilot_mapping"] = [{"order": n, "world_id": w["world_id"], "uid": w["uid"], "content_sha256": g.content_sha(w),
                             "structure_group": g.structure_group(w)} for n, w in enumerate(sets["piloto"])]
    out["pilot_worlds_sha256"] = S.worlds_sha(sets["piloto"])
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
