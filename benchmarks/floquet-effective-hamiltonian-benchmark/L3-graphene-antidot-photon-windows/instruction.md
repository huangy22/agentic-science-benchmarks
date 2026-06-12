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

# L3 - Floquet graphene antidot photon-energy windows

This task is tied to `flq_l3_graphene_antidot_photon_windows` in
`data/floquet_reference.csv`, sourced from paper id `867767689039315299`.

For each graphene antidot geometry, the paper chooses photon energies satisfying
two constraints:

1. the two static energy bands remain inside the first Floquet Brillouin zone;
2. the photon energy is low enough to avoid transitions from the first valence
   band to the second conduction band.

The input gives a grid of photon energies and whether each constraint is
satisfied. Recover the contiguous valid photon-energy window where both
constraints hold.

## Input

`cases.csv` columns:

```text
case_id,paper_id,reference_case_id,geometry,grid_file
```

Each grid file is a CSV with:

```text
photon_energy_eV,first_zone_ok,two_band_ok
```

The `*_ok` fields are `0` or `1`.

## Output

Write `out.csv` with exactly:

```text
case_id,window_low_eV,window_high_eV
```

## Scoring

PASS requires one row per case and absolute error at most `0.01 eV` for both
window endpoints. The tolerance follows the precision of the source-paper
reported intervals.
