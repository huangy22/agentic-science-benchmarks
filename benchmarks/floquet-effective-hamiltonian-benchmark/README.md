# Floquet Effective Hamiltonian Benchmark

This benchmark is derived from Gaia workflow family `#1069`, "Floquet effective
Hamiltonian derivation and analysis", hosted at
`http://101.126.75.25:8001/api/families/1069`.

The suite follows the organization of
`kunyuan/dfpt-lambda-benchmark`: every task has a `task.toml`, an
`instruction.md`, public development data under `environment/packet`, hidden
test data under `tests/hidden`, a scorer under `tests`, and a reference solution
under `solution`.

## Reference Set First

The main benchmark is being rebuilt around paper-derived gold, following the
data-provenance pattern of `kunyuan/dfpt-lambda-benchmark`.

- `data/floquet_reference.csv`: curated cross-paper reference cases extracted
  from LKM paper graphs and reasoning search over workflow `#1069` paper ids.
- `data/lkm_source_manifest.csv`: graph-status and source-node audit table for
  the inspected LKM paper payloads.
- `data/README.md`: data-source ledger and mapping from the
  `dfpt-lambda-benchmark` pattern to this Floquet benchmark.
- `curation_protocol.md`: acceptance, rejection, difficulty-level, and scoring
  criteria for turning those references into runnable tasks.

- `L1-paper-formula-renormalization/`: the current runnable paper-derived task,
  built from the accepted L1 rows of `data/floquet_reference.csv`.
- `L1-driven-qubit-effective-hamiltonian/`: retained only as a synthetic
  prototype for verifier mechanics. It is not the paper-derived benchmark.

The reference table currently contains 15 candidate cases, 13 of them accepted
as LKM-graph-backed references, spanning 9 papers. It deliberately keeps
`needs_original_paper` rows in the table as promising but not-yet-hidden-scored
targets.

## Data-Source Model

This repository should not treat a generated toy example as the benchmark gold.
The intended source chain is:

1. workflow `#1069` metadata and paper ids;
2. Bohrium LKM reasoning search scoped to those ids;
3. per-paper LKM graph retrieval for selected candidates;
4. source-node excerpts stored in `data/floquet_reference.csv`;
5. original-paper text, figure, or table checks before hidden grading when the
   LKM graph does not fully specify the scoring target.

This mirrors the `dfpt-lambda-benchmark` split between central reference data,
extraction/provenance artifacts, and runnable task folders.

## Workflow Source

Workflow `#1069` describes a reusable Floquet workflow:

1. Define a time-periodic Hamiltonian.
2. Choose a Floquet approach.
3. Construct an effective Floquet Hamiltonian or Floquet matrix.
4. Compute quasienergies and Floquet states.
5. Evaluate observables and stroboscopic dynamics.

The paper-derived benchmark cases must instantiate these steps from actual
literature claims: model specification, drive protocol, Floquet construction,
gold observable, and a source LKM node or original-paper cross-check.

## Run

```bash
bash benchmarks/floquet-effective-hamiltonian-benchmark/L1-paper-formula-renormalization/scripts/selfcheck.sh
bash benchmarks/floquet-effective-hamiltonian-benchmark/L1-driven-qubit-effective-hamiltonian/scripts/selfcheck.sh
python benchmarks/floquet-effective-hamiltonian-benchmark/scripts/validate_reference.py
```
