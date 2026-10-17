# TRONCO-01 research record

Research and evaluation artifacts for TRONCO-01, assembled from completed development work dated 2026-10-17.

## Status

- G0 through G2 sentinel materials and their analysis reports are included.
- G2 stopped at its preregistered five-world sentinel; the remaining 20 scheduled worlds were not evaluated.
- G2.1 is a proposed next block only and has not been run.
- The later validity-audit sequence v1 through v2.7 is included, together with its independent checks, mutation checks, frozen packages, and the recorded v2.7 model assay.
- M17 is not approved. Diagnostic and confirmation reserves remain closed; no fine-tuning was performed.
- Results are development evidence on synthetic worlds; they do not establish confirmation or external validity.
- The AutoRA/DiscoveryWorld comparison found a task-aware selection policy that beat random selection, but a simple public cue matched it; it does not show an AutoRA-specific gain.
- The independent AutoSciLab audit reproduces hidden-ground-truth use in the inspected wrapper. It is an audit result, not a general finding about every benchmark or dependency used by that wrapper.

## Contents

- `reports/`: analyses, protocols, audit data, and next-step reviews.
- `packages/`: reproducible ZIP snapshots for the recorded TRONCO-01 stages.
- `tools/`: small scripts used for the AutoRA/DiscoveryWorld and AutoSciLab checks.
- `SHA256SUMS.txt`: SHA-256 hashes for the published artifacts.

The reports also include a 17 October survey of 30 possible components and benchmarks. Its first candidates for a controlled offline audit are MechBench (mechanism evaluation), the set-valued method in HypoSpace (underdetermination), ALF (active experiment selection), and Autonomous Science Bench (budgeted lab separation). The survey is a source and implementation triage; it does not reproduce claimed benchmark performance.

Archives were checked for credential files and model-weight files before publication. This repository is private. No project-wide license has been assigned; source and data retain their applicable ownership and licensing.
