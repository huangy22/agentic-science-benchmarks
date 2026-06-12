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

# L2 - Kicked SSH Z-kick quasienergy

This task comes from `flq_l2_kicked_ssh_quasienergy_formula` in
`data/floquet_reference.csv`, sourced from paper id `812585024850231297`.

For each row, compute the principal-branch quasienergy for the unidirectional
Z-kick case by constructing the one-period Floquet propagator

```text
U_F(k) = exp(-i alpha_z sigma_z) exp[-i T (dx sigma_x + dy sigma_y + dz sigma_z)].
```

The principal quasienergy is the positive value `epsilon` in `[0, pi/T]` whose
phase eigenvalues are `exp(+/- i epsilon T)`. Clamp only the trace-derived
cosine to `[-1, 1]` to protect against floating roundoff. All hidden inputs have
nonzero `sqrt(dx^2 + dy^2 + dz^2)`.

## Input

`cases.csv` columns:

```text
case_id,paper_id,reference_case_id,dx,dy,dz,alpha_z,T
```

## Output

Write `out.csv` with exactly:

```text
case_id,epsilon
```

## Scoring

PASS requires one row per case and absolute error at most `1e-7`.
