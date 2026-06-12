# Floquet Benchmark Curation Protocol

This benchmark must be built from workflow `#1069` papers, not from synthetic
toy data. Each accepted case needs a traceable source in the LKM paper graph or,
when the LKM graph is insufficient, an explicit original-paper check before it
can enter a scored hidden set.

## Data Sources

1. Workflow family metadata:
   `http://101.126.75.25:8001/api/families/1069`.
2. Workflow family paper ids:
   `http://101.126.75.25:8001/api/families/1069/papers?format=json`.
3. Bohrium LKM paper graph:
   `POST https://open.bohrium.com/openapi/v1/lkm/papers/graph`.
4. Bohrium LKM reasoning search scoped to workflow paper ids:
   `POST https://open.bohrium.com/openapi/v1/lkm/reasoning/search`.
5. Original paper text or figures, used only for cases marked
   `needs_original_paper` before promotion into a scored split.

The access key is never stored in this repository. Raw LKM graph JSON should be
kept outside the repo unless a short, source-node-linked excerpt is needed for
audit.

## Levels

### L1: Formula / Postprocessing

Paper-derived formulas whose inputs can be varied in hidden cases and scored by
closed-form numerical checks. Examples: Bessel-renormalized tunneling, Raman
coupling renormalization, and high-frequency effective terms.

Acceptance:
- the formula appears in a source LKM node;
- the output is scalar/vector numeric;
- the verifier can generate hidden numeric inputs without changing the physics.

### L2: Numerical Floquet Reproduction

Finite-system exact diagonalization, Floquet matrix diagonalization, one-period
unitary construction, or topological invariant computation. Gold can be a
reported quasienergy, critical parameter, invariant, or spectrum agreement.

Acceptance:
- model and parameter set are sufficiently specified by the paper graph or paper;
- the computation is runnable without proprietary code;
- the verifier compares a numeric result with a clear tolerance.

### L3: Research Workflow Reproduction

Paper-level reproduction tasks that require selecting the appropriate Floquet
construction and validating a main conclusion-level observable: gap closure,
Dirac-point migration, Chern/winding/edge-mode count, or experimental sideband
spacing.

Acceptance:
- the task uses a real paper's model, drive protocol, and observable;
- source provenance includes `paper_id` and `source_node_id`;
- any figure-derived or table-derived gold is cross-checked against the original
  paper before entering hidden scoring.

## Required Reference Fields

Each row in `data/floquet_reference.csv` must include:

- `case_id`
- `level`
- `status`
- `paper_id`
- `title`
- `doi`
- `model_system`
- `drive_protocol`
- `expected_method`
- `gold_observable`
- `gold_value`
- `tolerance`
- `verification_mode`
- `source_node_id`
- `source_excerpt`
- `quality_notes`

## Status Values

- `accepted_reference`: enough LKM evidence exists to design a benchmark case.
- `needs_original_paper`: promising case, but exact values or figure/table
  details must be checked in the original paper.
- `rejected`: not suitable for scoring, usually because the claim is qualitative,
  underspecified, or not specific to Floquet effective Hamiltonian analysis.

Only `accepted_reference` rows can be used for initial public development cases.
Hidden cases should be promoted only after a second source check. Rows marked
`needs_original_paper` are intentionally kept in the table as future candidates,
but they cannot be counted as scored hidden gold.

## Scoring Standards

- Closed-form L1 formulas: absolute or relative tolerance no looser than `1e-6`
  for dimensionless outputs unless special functions or root finding make that
  unrealistic.
- L2 finite Floquet numerics: tolerance should reflect model truncation and
  reported precision; default target is `1e-3` to `1e-2` for dimensionless
  quasienergies or invariants.
- L3 research reproductions: use paper-specific tolerance. Critical amplitudes
  and measured frequencies should default to the resolution implied by the paper
  or LKM claim, e.g. scan step, displayed precision, or experimental bandwidth.
- Qualitative topological labels are not enough by themselves; they must be tied
  to an invariant, gap closing, mode count, or measured spacing.

## Quality Gates

Before a case enters a runnable benchmark:

1. It has a source LKM node and a short excerpt stored in the reference table.
2. The expected method is explicit enough for a skilled agent to infer the
   computation without seeing the gold.
3. The gold observable is numeric, categorical-with-invariant, or otherwise
   machine-checkable.
4. The tolerance is justified by the source precision or verifier precision.
5. No row is synthetic unless explicitly labeled as a prototype outside the
   paper-derived benchmark.
6. The paper appears in `data/lkm_source_manifest.csv` with an `ok` graph status,
   unless the row is explicitly rejected or awaiting original-paper recovery.
7. Any hidden-scoring row whose gold comes from a figure, interval, experimental
   spectrum, or Hamiltonian-convention-sensitive calculation has an original
   paper check recorded before it is promoted.
