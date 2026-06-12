# Working environment

You are in a container with Python 3. Public development data is in
`./packet/cases.csv`, with reference outputs in `./packet/dev_gold.csv`.

Write your solution as **`run_floquet.py`** in the working directory (`/app`).
The verifier invokes it as:

```bash
python run_floquet.py --params <cases.csv> --out <out.csv>
```

on concealed held-out cases.

---

# L3 - Floquet graphene antidot critical amplitudes

This task is tied to `flq_l3_graphene_antidot_critical_amplitudes` in
`data/floquet_reference.csv`, sourced from paper id `867767689039315299`
(`Floquet Graphene Antidot Lattices`).

The source paper varies the circularly polarized drive amplitude and identifies
two critical amplitudes:

- `E0c1`: the Gamma-point quasienergy gap closes and the Dirac dispersion is
  dynamically restored.
- `E0c2`: the M-point quasienergy gap closes before the semi-Dirac regime.

The full paper calculation uses nonperturbative extended-space Floquet
diagonalization. This benchmark gives you the resulting scan-like gap data and
asks you to recover the critical amplitudes. That makes it a workflow recovery
task: identify the correct observable and transition point from Floquet scan
outputs, not merely evaluate a closed-form formula.

## Input

`cases.csv` columns:

```text
case_id,paper_id,reference_case_id,scan_file
```

Each scan file is a CSV with:

```text
E0,gamma_gap,m_gap
```

`E0` is the drive amplitude in atomic units. `gamma_gap` and `m_gap` are
quasienergy-gap observables at the Gamma and M points.

## Output

Write `out.csv` with exactly:

```text
case_id,E0c1,E0c2
```

Report the drive amplitudes in atomic units.

## Scoring

PASS requires one row per case and absolute error at most `0.05` a.u. for both
critical amplitudes. The tolerance follows the source paper's stated scan
resolution.
