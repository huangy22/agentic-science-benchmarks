# Working environment

You are in a container with Python 3. Public development data is in
`./packet/cases.csv`, with reference outputs in `./packet/dev_gold.csv`.

Write your solution as **`run_floquet.py`** in the working directory (`/app`).
The verifier invokes it as:

```bash
python run_floquet.py --params <cases.csv> --out <out.csv>
```

on concealed held-out cases. Do not hardcode public case answers; the graded
cases change the drive amplitude, detuning, phase, time step count, and number of
stroboscopic periods.

---

# L1 - Floquet effective Hamiltonian for a driven qubit

For each row in `cases.csv`, solve the time-periodic Hamiltonian

```text
H(t) = (bias / 2) sigma_z + (coupling + drive cos(omega t + phase)) sigma_x
T = 2 pi / omega
```

where `sigma_x` and `sigma_z` are Pauli matrices and hbar is set to one.

Construct the one-period Floquet propagator

```text
U(T) = Texp[-i integral_0^T H(t) dt]
```

then extract a branch-consistent effective Hamiltonian `H_eff` satisfying

```text
U(T) = exp(-i H_eff T)
```

with quasienergies on the principal branch. Also compute the probability of
transitioning from the initial state `|0>` to `|1>` after `n_periods` repeated
applications of `U(T)`.

## Input

`cases.csv` columns:

```text
case_id,bias,coupling,drive,omega,phase,n_periods,steps
```

- `bias`, `coupling`, `drive`, `omega`, `phase` are real-valued Hamiltonian
  parameters.
- `n_periods` is the number of full driving periods used for the transition
  probability.
- `steps` is a recommended minimum number of midpoint time slices for one
  driving period. You may use this value directly or a more accurate method.

## Output (`out.csv`)

Columns:

```text
case_id,heff_x,heff_y,heff_z,quasienergy_gap,p_down
```

- `heff_x`, `heff_y`, `heff_z`: components of `H_eff = heff_x sigma_x +
  heff_y sigma_y + heff_z sigma_z`.
- `quasienergy_gap`: the principal quasienergy gap.
- `p_down`: probability of finding `|1>` after `n_periods` periods when starting
  from `|0>`.

## Development data

- `packet/cases.csv`: six public development cases.
- `packet/dev_gold.csv`: reference outputs for those cases.

## Scoring

Hidden cases are scored numerically. PASS requires exactly one row per case and
all reported columns within absolute tolerances:

- `heff_x`, `heff_y`, `heff_z`, `quasienergy_gap`: `5e-4`
- `p_down`: `1e-4`

The benchmark is deterministic and should run in seconds with a pure Python
implementation.
