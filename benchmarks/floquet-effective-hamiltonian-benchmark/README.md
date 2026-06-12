# Floquet Effective Hamiltonian Benchmark

This benchmark is derived from Gaia workflow family `#1069`, "Floquet effective
Hamiltonian derivation and analysis", hosted at
`http://101.126.75.25:8001/api/families/1069`.

The suite follows the organization of
`kunyuan/dfpt-lambda-benchmark`: every task has a `task.toml`, an
`instruction.md`, public development data under `environment/packet`, hidden
test data under `tests/hidden`, a scorer under `tests`, and a reference solution
under `solution`.

## Current Task

- `L1-driven-qubit-effective-hamiltonian/`: recover the branch-consistent
  effective Hamiltonian, quasienergy gap, and stroboscopic transition probability
  for a periodically driven two-level Hamiltonian.

The task is intentionally dry-lab and numeric. Agents must implement a generic
Floquet solver rather than hardcoding public examples. Hidden cases change the
drive amplitudes, detunings, phases, and period counts.

## Workflow Source

Workflow `#1069` describes a reusable Floquet workflow:

1. Define a time-periodic Hamiltonian.
2. Choose a Floquet approach.
3. Construct an effective Floquet Hamiltonian or Floquet matrix.
4. Compute quasienergies and Floquet states.
5. Evaluate observables and stroboscopic dynamics.

The L1 task instantiates these steps in the smallest setting that still checks
the core scientific computation: a driven qubit with a sinusoidal transverse
drive. The verifier compares the submitted effective Hamiltonian components,
quasienergy gap, and multi-period transition probability to an independent
midpoint-product Floquet propagator.

## Run

```bash
bash benchmarks/floquet-effective-hamiltonian-benchmark/L1-driven-qubit-effective-hamiltonian/scripts/selfcheck.sh
```
