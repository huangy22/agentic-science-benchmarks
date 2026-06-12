# Agentic Science Benchmarks

Benchmark definitions derived from workflow families in the Gaia workflow atlas.

## Layout

- `benchmarks/`: self-contained benchmark suites. Each suite follows the same
  task shape used by `kunyuan/dfpt-lambda-benchmark`: task metadata, instructions,
  a lightweight execution environment, public development packets, hidden tests,
  scoring scripts, and an optional reference solution.

## Benchmarks

- `benchmarks/floquet-effective-hamiltonian-benchmark/`: a numeric dry-lab
  benchmark derived from workflow family `#1069`, "Floquet effective Hamiltonian
  derivation and analysis".
