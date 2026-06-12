# Acceptance Criteria

This benchmark is acceptable only if the paper-derived score set is traceable,
multi-level, and mechanically verified. The synthetic driven-qubit task is a
prototype and must not be counted toward paper-derived coverage.

## Source Criteria

- The reference table must originate from workflow `#1069` paper ids.
- Every accepted reference row must cite a `paper_id`, DOI, LKM `source_node_id`,
  source excerpt, level, scoring tolerance, and verification mode.
- Every runnable paper-derived task must list its reference rows and paper ids in
  `benchmark_manifest.csv`.
- Any L3 hidden gold based on a figure, interval, scan, or experimental
  observable must have a `confirmed` row in `data/original_paper_checks.csv`.
- Promoted L3 hidden gold must be checked through
  `POST https://open.bohrium.com/openapi/v1/lkm/papers/content/batch` unless an
  explicit fallback is recorded and justified.

## Coverage Criteria

- The paper-derived runnable set must include at least one task each at L1, L2,
  and L3.
- The paper-derived runnable set must cover at least four distinct source
  papers.
- The reference table must retain at least three accepted rows each for L1, L2,
  and L3, even if not all rows have been promoted to runnable tasks yet.
- Rows marked `needs_original_paper` cannot enter hidden scoring.

## Scoring Criteria

- L1 formula/postprocessing tasks use absolute or relative tolerances no looser
  than `1e-6` unless the reference table justifies otherwise.
- L2 numerical/grid tasks use a paper-specific tolerance and must test the
  branch, grid, or finite-system logic needed by the source claim.
- L3 research-workflow tasks use source-implied tolerances: scan step, displayed
  precision, experimental bandwidth, or exact integer invariant.
- Hidden gold must be stored under `tests/gold` and not in public packet files,
  except for public development gold under `environment/packet/dev_gold.csv`.

## Mechanical Gates

Before declaring the benchmark ready:

```bash
bash benchmarks/floquet-effective-hamiltonian-benchmark/L1-paper-formula-renormalization/scripts/selfcheck.sh
bash benchmarks/floquet-effective-hamiltonian-benchmark/L2-kicked-ssh-quasienergy/scripts/selfcheck.sh
bash benchmarks/floquet-effective-hamiltonian-benchmark/L3-graphene-antidot-critical-amplitudes/scripts/selfcheck.sh
bash benchmarks/floquet-effective-hamiltonian-benchmark/L3-graphene-antidot-photon-windows/scripts/selfcheck.sh
python benchmarks/floquet-effective-hamiltonian-benchmark/scripts/validate_reference.py
```

The synthetic prototype selfcheck may also be run, but it is not part of the
paper-derived acceptance count.
