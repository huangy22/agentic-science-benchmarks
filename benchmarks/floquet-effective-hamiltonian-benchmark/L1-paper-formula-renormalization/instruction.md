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

# L1 - Paper-derived Floquet renormalization formulas

For each row, evaluate the paper-derived Floquet effective-Hamiltonian formula
identified by the `formula` column. The input also includes `paper_id` and
`reference_case_id`, which point back to
`data/floquet_reference.csv`.

## Formula families

`bh_bessel_tunneling`

From `flq_l1_bh_bessel_tunneling`:

```text
value_1 = J0(x)
value_2 = 0
value_3 = 0
```

where `x = K / (hbar omega)`.

`raman_coupling`

From `flq_l1_raman_coupling_renormalization`:

```text
value_1 = Omega12' / Omega12 = J0(x)
value_2 = Omega13' / Omega13 = J0(x)
value_3 = Omega23' / Omega23 = J0(2 x sin(phi0 / 2))
```

where `x = delta_m / omega`.

`binary_bec_tunneling`

From `flq_l1_binary_bec_tunneling_suppression`:

```text
value_1 = Omega_eff / Omega = J0(x)
value_2 = 0
value_3 = 0
```

where `x = 2 mu / omega`.

`magnon_dm`

From `flq_l1_magnon_dm_high_frequency`:

```text
value_1 = sqrt(3) J^2 J1(E0)^2 / omega
value_2 = sqrt(3) J^2 E0^2 / (4 omega)
value_3 = 0
```

`value_2` is the small-drive approximation.

## Input

`cases.csv` columns:

```text
case_id,formula,paper_id,reference_case_id,x,phi0,J,omega,E0
```

Unused numeric columns are set to zero for that formula family.

## Output

Write `out.csv` with exactly:

```text
case_id,value_1,value_2,value_3
```

Use finite decimal or scientific-notation floats. Hidden cases change the
numeric parameters within the same paper-derived formulas, so do not hardcode
the public answers.

## Scoring

PASS requires one row per case and all values within absolute tolerance `1e-6`.
The task is deterministic and should run in less than a second with a pure
Python implementation.
