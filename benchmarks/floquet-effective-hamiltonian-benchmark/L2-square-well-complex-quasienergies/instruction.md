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

# L2 - Driven square-well complex quasienergies

This task comes from `flq_l2_driven_square_well_quasienergies` in
`data/floquet_reference.csv`, sourced from paper id `812308293425823745`.

The paper reports two complex Floquet quasienergies for a driven metastable
square-well/barrier model at `omega / V0 = 0.62`. For a quasienergy

```text
epsilon / V0 = E - i gamma
```

the decay width in units of `V0` is

```text
Gamma / V0 = -2 Im(epsilon / V0) = 2 gamma.
```

The more stable state is the one with the smaller decay width.

## Input

`cases.csv` columns:

```text
case_id,paper_id,reference_case_id,omega_over_V0,eps_a_real,eps_a_imag,eps_b_real,eps_b_imag
```

The imaginary parts are negative for decaying metastable states.

## Output

Write `out.csv` with exactly:

```text
case_id,less_stable_energy,less_stable_width,more_stable_energy,more_stable_width,energy_splitting,width_ratio
```

where:

- `less_stable_*` corresponds to the larger decay width;
- `more_stable_*` corresponds to the smaller decay width;
- `energy_splitting = less_stable_energy - more_stable_energy`;
- `width_ratio = less_stable_width / more_stable_width`.

## Scoring

PASS requires one row per case and absolute error at most `5e-6` for all
reported quantities.
