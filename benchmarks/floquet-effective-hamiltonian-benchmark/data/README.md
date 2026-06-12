# Floquet Benchmark Data

This directory is the benchmark's evidence ledger. It follows the data-first
pattern used by `kunyuan/dfpt-lambda-benchmark`: collect source-backed reference
values first, then promote only sufficiently specified rows into runnable
benchmark tracks.

## Files

| file | role |
|---|---|
| `workflow_1069.json` | Workflow-family definition for Floquet effective Hamiltonian derivation and analysis. |
| `workflow_1069_paper_ids.txt` | The 191 paper ids returned by workflow family `#1069`. |
| `floquet_reference.csv` | Curated candidate/gold cases across L1, L2, and L3. This is the main reference table. |
| `lkm_source_manifest.csv` | Paper-graph audit manifest for the LKM payloads inspected while building `floquet_reference.csv`. |
| `original_paper_checks.csv` | Short original-paper verification ledger for rows promoted beyond LKM-only evidence. |

## Original Paper Content

For original-text verification, prefer the Bohrium LKM batch content endpoint:

```text
POST https://open.bohrium.com/openapi/v1/lkm/papers/content/batch
payload: {"paper_ids": ["<paper_id>", "..."]}
```

The response returns `data.items[]` with a `markdown_url` and image metadata.
Use the markdown content to confirm figure/table intervals, parameter
conventions, and display precision before a row is promoted into hidden scoring.
External arXiv/PDF/source-file checks are acceptable fallbacks only when the LKM
content endpoint is unavailable or incomplete; record the fallback explicitly in
`original_paper_checks.csv`.

## Reference-Repo Pattern

The reference repository `kunyuan/dfpt-lambda-benchmark` uses:

- a central `data/lambda_reference.csv` / `.json` as the paper-derived gold
  table;
- `data/lkm_extraction.json` and `lambda_per_condition.json` to preserve the
  extraction path from LKM paper records into per-condition references;
- runnable tracks whose hidden gold is derived from the reference table rather
  than invented in the task folder;
- explicit status notes for runnable, validated, and still-hardening levels.

This Floquet benchmark mirrors that shape, with smaller initial scope:

- `floquet_reference.csv` is the source of candidate gold;
- `lkm_source_manifest.csv` records which paper graphs were inspected and which
  source nodes were selected;
- L1/L2/L3 rows distinguish formula postprocessing, finite Floquet numerics, and
  research-workflow reproduction;
- rows marked `needs_original_paper` are excluded from hidden scoring until an
  original-paper or figure/table check confirms the exact scoring target.
- runnable L3 hidden gold must have a matching `confirmed` row in
  `original_paper_checks.csv`.

## Current Source Boundary

The current accepted references are grounded in Bohrium LKM paper graphs,
reasoning search over workflow `#1069` paper ids, and targeted original-text
checks for promoted L3 hidden gold. Full raw LKM JSON payloads are not committed
because they are large and may contain unstable service metadata; the stable
audit surface is the paper id, source node id, source excerpt, graph/content
status, and bibliographic metadata recorded here.

Before a row becomes hidden grading gold, run a second-source check against the
original paper text, figures, or tables, preferably through
`/papers/content/batch`, when any of the following are true:

- the gold is read from a figure, window, or qualitative visual transition;
- the LKM node does not specify Hamiltonian convention or boundary conditions;
- the verifier requires parameter values beyond those in the LKM excerpt;
- the row has `status=needs_original_paper`.
