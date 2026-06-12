# L1 Paper Formula Renormalization

This is the first runnable paper-derived task in the Floquet benchmark. It
packages the accepted L1 rows from `../data/floquet_reference.csv` into a
formula-evaluation benchmark with hidden numerical cases.

The task covers four source papers:

- `812123278570160133`: Bose-Hubbard tunneling renormalization
  `J_eff/J = J0(K / hbar omega)`.
- `867750313874948107`: Raman-coupling renormalization in a driven ultracold
  Fermi gas.
- `867773104561062088`: binary BEC tunneling suppression
  `Omega_eff/Omega = J0(2 mu / omega)`.
- `867768599207478048`: high-frequency photoinduced magnon Dzyaloshinskii-Moriya
  term.

Run:

```bash
bash scripts/selfcheck.sh
```
