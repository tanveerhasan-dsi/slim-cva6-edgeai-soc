# verif/

Verification. Empty by design.

| Directory | What belongs here |
|---|---|
| `compliance/` | RISCOF configuration and `riscv-arch-test` results — run **twice**, with and without handlers installed (R-6.11–R-6.13). |
| `cosim/` | Co-simulation against a reference model over the RVFI trace port, covering emulation handlers as well as native instructions (R-6.3, R-6.4). |
| `formal/` | Equivalence proofs: pruned configuration against baseline, on the surviving subset (R-6.7–R-6.10). |

## Two things this directory exists to prevent

**Advancing on a benchmark.** CoreMark completing proves the core is not
comprehensively broken. It is a smoke test, not a gate (R-6.1). Each stage in
[`../docs/06-verification-requirements.md`](../docs/06-verification-requirements.md)
has its own stated criterion.

**Testing only what survived.** The most valuable stimulus for a pruned core is
the instructions it no longer implements (R-6.5). Confirming that a removed
encoding traps cleanly — rather than matching some other decoder arm and
executing as a different instruction — is the test that catches the
characteristic bug of this project.

## On the formal assumption set

The equivalence proof is conditional on the decoder never seeing a removed
opcode (R-6.8). That assumption is discharged by the compatibility contract in
`sw/emulation/`. The proof and the handlers are two halves of one claim; state
the assumption explicitly, or the result is void without anyone noticing.

## Publishing

Both compliance runs get published (R-6.15, R-6.13). The bare run characterises
the hardware; the handler run characterises the part. Both are true, they answer
different questions, and the delta between them quantifies exactly what was
moved into software.
