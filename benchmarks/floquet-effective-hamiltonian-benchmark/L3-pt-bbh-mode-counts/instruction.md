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

# L3 - PT-BBH Floquet invariant mode counts

This task comes from `flq_l3_pt_bbh_indices_same_gap` in
`data/floquet_reference.csv`, sourced from paper id `1121428643831087110`.

The paper uses Floquet engineering in a PT-symmetric extended BBH model. For a
given case, you are provided the chiral indices `N0`, `Npi`, and the real Chern
number `VR`.

Use the paper's counting rules:

```text
zero_gap_corner_states = 4 * abs(N0)
pi_gap_corner_states = 4 * abs(Npi)
first_order_boundary_pairs = VR
```

The same-gap coexistence flag is `1` when the zero gap contains both
second-order corner states and a first-order boundary pair, and `0` otherwise.

## Input

`cases.csv` columns:

```text
case_id,paper_id,reference_case_id,N0,Npi,VR
```

## Output

Write `out.csv` with exactly:

```text
case_id,zero_gap_corner_states,pi_gap_corner_states,first_order_boundary_pairs,total_corner_states,same_gap_coexistence
```

All output fields except `case_id` must be integers.

## Scoring

PASS requires exact integer agreement for every concealed case.
