<div align="center">

# CARVE-V

### Core Area Reduction by Verified Elimination

**A workload-driven ISA subsetting flow for an application-class RISC-V core.**

[![Licence: Apache-2.0](https://img.shields.io/badge/docs%20%26%20tools-Apache--2.0-blue.svg)](LICENSE)
[![Core: CVA6](https://img.shields.io/badge/core-CVA6-orange.svg)](https://github.com/openhwgroup/cva6)

</div>

---

## Problem statement

An application-class RISC-V core implements an instruction set sized for
general-purpose computing. A fixed-function edge device executes a small,
knowable fraction of it. The difference is paid for in silicon area, in leakage,
and in switching energy — on every part shipped, for the life of the product.

The question is not *whether* that gap can be closed. It obviously can: the
configuration knobs to disable a floating-point unit or a memory management unit
are already documented, and turning them off takes about a week. The question is
whether the gap can be closed **methodically, verifiably, and without breaking
the software contract**.

Three things make the naive approach unsatisfying, and together they define the
problem worth working on.

**There is no method for the long tail.** Naming the floating-point unit
requires no technique. The genuinely hard question is the remainder of the
instruction set — which base integer opcodes, which control and status
registers, which compressed subsets, which atomics. Published measurement finds
applications using between 6 and 32 distinct instructions, so the tail is most
of the available opportunity, and intuition does not reach it. A defensible
answer needs a criterion that can be stated before it is applied, and an
argument for why applying it is safe.

**Removing an instruction normally breaks the software contract.** Existing
subsetting work targets very small cores and simply abandons binary
compatibility: the resulting part runs recompiled software and nothing else. A
part that is smaller *and* still executes the instructions it no longer
implements is a materially different claim, and it requires deciding
deliberately what moves across the hardware/software boundary — and at what
measured cost.

**The result has to be trustworthy enough to fabricate.** Silicon is not
simulation. A pruning step that is merely tested is not the same as one that is
proven equivalent to its baseline, and the difference matters when the output is
a physical part that cannot be patched.

Closing the gap therefore means producing a *flow* — measured, verified, and
compatibility-preserving — rather than a smaller core. Whether the silicon
reclaimed that way is worth reclaiming is itself an open question, and answering
it means spending the area on something and measuring what it bought.

---

## Objectives

| ID | Objective |
|:--:|---|
| **O-1** | Establish a reproducible method for deriving an instruction subset from a target workload, with a deletion criterion that is provably conservative with respect to reachable code. |
| **O-2** | Produce a family of pruned core configurations, each independently buildable and independently measurable. |
| **O-3** | Preserve the software contract: every removed instruction remains executable, at a measured cost. |
| **O-4** | Prove each pruned configuration equivalent to its baseline on the surviving subset. |
| **O-5** | Reinvest the reclaimed area in a domain-specific datapath and measure the resulting change in energy. |
| **O-6** | Carry one configuration through to a fabricated, measured test chip in an always-on edge perception application. See [`docs/objective-6-test-chip.md`](docs/objective-6-test-chip.md) for a visual walk-through. |

O-1 through O-4 are the research contribution. O-5 is what makes the
contribution worth having. O-6 is what makes it real.

### Suggested publishable unit

**O-1 through O-4 form a self-contained conference paper, and one that does not
depend on the silicon arriving.** The claim would be: *a method for deriving an
instruction subset from a workload under a conservative criterion, applied to a
hand-written application-class core, with binary compatibility preserved by
emulation and each pruned configuration proven equivalent to its baseline.*
Every element of that claim is demonstrable in simulation and synthesis, so the
paper can be written and submitted while fabrication is still pending — which
also de-risks the whole project against a slipped or failed tapeout.

The natural venues are the computer-architecture and design-automation
conferences, or a RISC-V summit for the compatibility contract specifically.

**O-5 and O-6 are a second paper**, written once silicon is measured: the
reinvestment result and the measured part. Attempting to publish all six
objectives at once produces a paper whose most interesting contribution — the
method — competes for space with a chip result that a reviewer will judge on
entirely different criteria.

A useful test for the split: if the tapeout were cancelled tomorrow, O-1 to O-4
would still be publishable, and O-5 to O-6 would not.

---

## References

**The core**

- [CVA6](https://github.com/openhwgroup/cva6) — the application-class RISC-V
  core this work starts from.
- [CVA6 user manual](https://docs.openhwgroup.org/projects/cva6-user-manual/) —
  parameters, configurations and design documents.

**Prior art on subsetting**

- [Flexing RISC-V Instruction Subset Processors to Extreme Edge](https://arxiv.org/abs/2505.04567)
  — the closest prior work. Establishes the 6–32 instruction finding above.
  Targets tiny cores; does not preserve binary compatibility and does not
  formally verify the pruning.
- [NeCTAr](https://arxiv.org/abs/2503.14708) — a heterogeneous RISC-V SoC taken
  from concept to tapeout in a single semester. The feasibility precedent for a
  university test chip; not prior art on subsetting.

**Compatibility**

- [Trap-and-emulate for hardware forward-compatibility](https://lists.riscv.org/g/tech-profiles/topic/101153812)
  — RISC-V discussion of the mechanism and its real cost.
- [RISC-V unprivileged specification](https://docs.riscv.org/reference/isa/v20260120/unpriv/intro.html)
  — the normative source for what an emulated instruction must reproduce.

**Comparison points**

- [Ibex](https://github.com/lowRISC/ibex) — small, production-quality 32-bit
  core; the direct answer to *why not just use a small core*.
- [X-HEEP](https://arxiv.org/abs/2401.05548) — configurable ultra-low-power
  RISC-V microcontroller for edge accelerator exploration.

---

## Repository

`rtl/`, `sw/`, `verif/`, `flow/` and `tools/` are empty placeholders. The
directory names are a suggestion for where work lands, not a required structure.

Two supporting notes live in [`docs/`](docs/):

- [`objective-6-test-chip.md`](docs/objective-6-test-chip.md) — the components
  involved in O-6, illustrated.
- [`pruning-and-bridging.md`](docs/pruning-and-bridging.md) — what can be pruned,
  and how the trimmed processor still supports the same functionality
  afterwards. Worked examples are in its
  [annex](docs/pruning-and-bridging-annex.md).

---

## Licence

Apache-2.0 for documentation and tooling; Solderpad Hardware Licence 2.1 for
RTL. See [`LICENSE`](LICENSE).
