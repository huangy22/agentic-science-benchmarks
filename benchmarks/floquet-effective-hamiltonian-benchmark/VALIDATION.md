# Validation Record

This file records what has been independently checked for the Floquet effective
Hamiltonian benchmark and what remains a lower-fidelity postprocessing proxy.

## Source And Provenance Checks

- Workflow source: `data/workflow_1069.json` and
  `data/workflow_1069_paper_ids.txt`.
- LKM graph source: `data/lkm_source_manifest.csv` records inspected paper
  graphs and selected source nodes.
- Original content source: promoted original-paper checks use
  `POST https://open.bohrium.com/openapi/v1/lkm/papers/content/batch` and
  machine-checkable terms in `data/original_paper_check_terms.csv`.
- Mechanical gate:

```bash
python benchmarks/floquet-effective-hamiltonian-benchmark/scripts/validate_reference.py
python benchmarks/floquet-effective-hamiltonian-benchmark/scripts/verify_lkm_content_checks.py --use-gaia-credentials-file
```

## Verifier Contract

The paper-derived tasks now use a Harbor-style verifier pattern:

- `tests/test.sh` hides `tests/hidden` and `tests/gold` from group/world access
  when running as root.
- Agent code is executed as `nobody` when the runtime permits privilege drop.
- Predictions are written to a temporary directory outside the task tree.
- The verifier writes a binary reward to `/logs/verifier/reward.txt` in
  container mode, or to `.verifier_logs/reward.txt` during local selfcheck.
- `scripts/selfcheck.sh` runs oracle PASS checks and constructs perturbed hidden
  predictions that must FAIL the scorer.

## Current Reproduction Depth

| task | source basis | validation depth |
|---|---|---|
| `L1-paper-formula-renormalization` | Four accepted LKM formula references | Closed-form numerical postprocessing; oracle and perturbed-output checks. |
| `L2-kicked-ssh-quasienergy` | Accepted kicked SSH quasienergy reference | Computes the one-period SU(2) Floquet propagator before extracting principal quasienergy. |
| `L2-square-well-complex-quasienergies` | LKM graph plus content-batch text | Interprets paper-reported complex quasienergies into decay widths and stability order. |
| `L3-graphene-antidot-critical-amplitudes` | LKM graph plus content-batch scan text | Recovers critical amplitudes from hidden scan grids with source-implied tolerance. |
| `L3-graphene-antidot-photon-windows` | LKM graph plus content-batch window text | Recovers photon-energy validity windows from hidden boolean grids. |
| `L3-pt-bbh-mode-counts` | LKM graph conclusions 4/5 plus content-batch text | Converts paper-reported topological indices into boundary/corner mode counts; this remains an index-counting proxy rather than a full BBH lattice diagonalization. |

## Known Limits

- The graphene L3 tasks reproduce figure/table-derived observables through
  hidden grids, not a full Dirac-Floquet diagonalization.
- The PT-BBH task is provenance-complete and scorer-hardened, but it is still a
  topological-index postprocessing task. A future higher-grade L3/L4 task should
  require constructing the driven BBH Floquet operator and computing invariants
  from Hamiltonian parameters.
- The square-well task validates the original reported complex quasienergies and
  derived widths, but does not solve the underlying secular equation end to end.
