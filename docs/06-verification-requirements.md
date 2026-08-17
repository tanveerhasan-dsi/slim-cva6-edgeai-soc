# 06 — Verification Requirements

## 1. The standard

This design is fabricated. A bug found after tapeout is not a bug fix, it is a
schedule and a budget. Verification requirements are correspondingly stricter
than for RTL that only ever runs in simulation.

The staged flow below is adopted deliberately, and **each stage gates the next**.

| Stage | Infrastructure | Gate |
|---|---|---|
| 1 — Simulation | Verilator / commercial simulator | Every configuration builds and boots; directed and random tests pass |
| 2 — Co-simulation | Spike, over the RVFI trace port | Instruction-by-instruction agreement with the reference model |
| 3 — Compliance | RISCOF / `riscv-arch-test` | Passes with handlers; failures without handlers documented |
| 4 — Formal | Equivalence checking | Pruned core proven equivalent to baseline on the surviving subset |
| 5 — Prototype | FPGA (Kintex UltraScale+ class) | Full application runs at speed, closed-loop |
| 6 — Signoff | Synthesis, place-and-route, STA, power | Timing, DRC and LVS clean at target corners |

## 2. Running CoreMark is not a gate

CoreMark booting proves the core is not comprehensively broken. It is a smoke
test. It says nothing about the instructions your workload actually needs, and
nothing at all about the ones you removed.

| ID | Requirement |
|---|---|
| **R-6.1** | No configuration MAY advance a stage on the strength of a benchmark completing. Each gate MUST be evidenced by its stated criterion. |

## 3. Simulation and co-simulation

| ID | Requirement |
|---|---|
| **R-6.2** | Every configuration MUST build and pass the regression suite. A configuration that only synthesises is not verified. |
| **R-6.3** | Co-simulation against a reference model over RVFI MUST be run for every configuration. |
| **R-6.4** | Co-simulation MUST cover the emulation handlers, not just native instructions. |
| **R-6.5** | Constrained-random stimulus MUST include the removed encodings, to confirm they trap as specified. |
| **R-6.6** | Functional coverage MUST be collected and reported per configuration. |

**On R-6.5.** The most valuable stimulus for a pruned core is the instructions
it no longer implements. Testing only what remains verifies the part you did not
change. Confirming that a removed encoding traps cleanly — rather than
executing as some other instruction because a decoder `casez` still matches it —
is the test that catches the characteristic bug of this entire project.

## 4. Formal equivalence

| ID | Requirement |
|---|---|
| **R-6.7** | Each pruned configuration MUST be formally proven equivalent to the baseline **on the surviving subset**. |
| **R-6.8** | The assumption set MUST be stated explicitly, and MUST itself be justified. |
| **R-6.9** | Any property that cannot be proven MUST be listed, with the bounded-verification argument used instead. |
| **R-6.10** | Equivalence MUST be re-established after every RTL change, in CI. |

**On R-6.8.** The proof is conditional on the decoder never seeing a removed
opcode. That assumption is exactly what the compatibility contract in
[`05`](05-compatibility-requirements.md) is responsible for discharging — the
formal argument and the trap handlers are two halves of one claim, and an
unstated assumption here silently voids the result.

**On R-6.9.** Full equivalence on a pipelined core with caches may not close.
Saying so, and stating what was proven instead, is a stronger position than a
green tick over an unstated bound.

## 5. Compliance

| ID | Requirement |
|---|---|
| **R-6.11** | RISCOF MUST be run with handlers installed; the configuration MUST pass. |
| **R-6.12** | It MUST also be run without handlers; every failure MUST be documented and mapped to a specific removal. |
| **R-6.13** | Both results MUST be published together. |

## 6. FPGA prototype

| ID | Requirement |
|---|---|
| **R-6.14** | The full application MUST run on FPGA before RTL freeze, with real sensors in the loop. |
| **R-6.15** | The closed-loop latency and jitter of R-2.12/R-2.13 MUST be measured on the prototype, and used to validate the pre-silicon model. |
| **R-6.16** | The prototype MUST exercise the emulation handlers under realistic interrupt load. |

**On R-6.15.** The prototype is the last opportunity to discover that the
latency budget does not close. Finding it there costs a re-spin of a
configuration; finding it after fabrication costs the tapeout.

**On R-6.16.** Handler correctness under interrupt load is precisely what unit
tests do not reach. Run it on hardware, under load, for long enough for the rare
interleavings to occur.

## 7. Continuous integration

| ID | Requirement |
|---|---|
| **R-6.17** | CI MUST gate every merge on: all configurations building; the regression suite; co-simulation; formal equivalence; and the `isaprof` self-test. |
| **R-6.18** | A configuration failing any gate MUST NOT be merged. |
| **R-6.19** | CI MUST record tool versions and source commits for every run, satisfying R-1.6. |

**On R-6.17.** Verification that is run when someone remembers is verification
that stops being run around the time the schedule gets tight — which is
precisely when it starts to matter. Gate it, or it is decoration.

## 8. Signoff

| ID | Requirement |
|---|---|
| **R-6.20** | Timing MUST close at all specified corners, with margin recorded. |
| **R-6.21** | DRC and LVS MUST be clean. |
| **R-6.22** | Power MUST be analysed for both the always-on and the duty-cycled domains, including the wake transition. |
| **R-6.23** | A signoff checklist MUST be completed and archived with the submission. |
| **R-6.24** | Scan, JTAG debug and a bring-up plan MUST exist before submission. |

**On R-6.24.** A chip you cannot debug is a chip you cannot bring up. Decide how
you will observe internal state on silicon while you can still add the logic to
do it — this is the item most often deferred and most often regretted.

---

# 9. Reference verification strategy

## 9.1 The characteristic bug of this project

Understand this before writing a single test.

A removed instruction whose decode arm is deleted may still **match a different
arm**. SystemVerilog `casez` and priority-encoded decoders are full of
don't-care bits; deleting one branch can widen another. The instruction does not
trap — it executes as something else, silently, with plausible-looking results.

This is the bug that reaches silicon, because every test exercising the
*surviving* ISA passes.

Therefore: for every removed encoding, assert that it raises an
illegal-instruction exception. **Generate this test set mechanically from the
subset manifest**, so it cannot drift from the configuration (R-6.5).

## 9.2 Formal equivalence — plan for a partial result

The proof is: *pruned core ≡ baseline core, given the decoder never observes a
removed opcode.*

That assumption is discharged by the compatibility contract. The proof and the
handlers are two halves of one claim — state the assumption explicitly (R-6.8),
or the result is void without anyone noticing.

Expect full equivalence on a pipelined core with caches **not to close** with
open tooling ([`11`](11-expected-results-and-risks.md), P-6). Plan for it:

- Prove equivalence on the decode and execute datapath.
- Fall back to bounded model checking for the memory subsystem, and **state the
  bound**.
- List every unproven property (R-6.9).

A precisely-bounded proof is a legitimate contribution; an unbounded green tick
is not, and reviewers of formal claims know the difference. Time-box this —
equivalence checking will absorb unlimited effort.

## 9.3 Handler verification

The handler library needs verification separate from the core's:

- **Against a reference model, instruction by instruction.** Exhaustive where
  feasible — `div`/`rem` over 32-bit operands is not, so use directed corner
  cases plus constrained-random.
- **Corner cases that matter:** division by zero, signed overflow
  (`INT_MIN / -1`), and every architecturally-specified result that is *not* a
  trap.
- **Re-entrancy under nesting**, exercised on FPGA under realistic interrupt
  load (R-6.16). Unit tests do not reach the rare interleavings.
- **Nested traps**: an emulated instruction that itself faults.

## 9.4 One CI gate the requirements do not name

Re-run the subsetting pipeline on every toolchain change.

A compiler upgrade can emit an instruction the analysis never saw, silently
invalidating the subset. This is exactly the check that gets forgotten, and its
failure mode is a hang in the field rather than a red build.

## 9.5 What to measure on the FPGA

The prototype is the last chance to discover that the latency budget does not
close. Finding it there costs a configuration re-spin; finding it after
fabrication costs the tapeout.

Measure worst-case sensor-to-PWM latency and **jitter** (R-2.13), under
realistic interrupt load, with handlers installed, for long enough that rare
interleavings occur. Report the distribution, not the mean — the thesis is a
determinism claim, and the mean is precisely the statistic that conceals the
tail the claim depends on.

---

**Previous:** [`05-compatibility-requirements.md`](05-compatibility-requirements.md) ·
**Next:** [`07-implementation-constraints.md`](07-implementation-constraints.md)
