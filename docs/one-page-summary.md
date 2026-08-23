# CARVE-V — One-Page Summary

*Core Area Reduction by Verified Elimination. Prepared for review; full detail in
[`README`](../README.md).*

---

**In one sentence.** Remove a large fraction of the instruction set from an
application-class RISC-V core under a measured criterion, keep every removed
instruction working through software emulation, prove each pruned configuration
equivalent to its baseline, and spend the reclaimed area on a domain-specific
datapath.

---

### Problem

- An application-class core implements an ISA sized for general-purpose computing; a fixed-function edge device uses a small fraction of it.
- The difference costs area, leakage and switching energy on every part shipped.
- Closing the gap naively — disabling an FPU or MMU — is a documented configuration change, not a contribution, and it has no method for the long tail. Published measurement finds applications using **6–32 distinct instructions**.

### Proposal

- Derive the subset from **measured reachability** of the target workload, under a criterion stated before it is applied.
- Preserve binary compatibility: every removed encoding is emulated, so the part stays a legal implementation.
- **Formally prove** each pruned configuration equivalent to the baseline on the surviving subset.
- Reinvest the reclaimed area and measure what it bought.

### The central idea

- The unit that is functionally equivalent to the original core is **the pruned core plus its handler library** — neither half alone.
- An unimplemented encoding traps; the handler reproduces its architectural effect exactly and resumes. The program cannot tell the difference except in timing.
- Emulation is a **compatibility guarantee, not a performance one**. Whole-program cost stays low because removal is measurement-driven, but an unbounded trap on the time-critical path is disqualifying — some instructions stay in hardware for latency reasons alone.

### Objectives

| | | |
|:--:|---|---|
| **O-1** | Reproducible subsetting method with a conservative deletion criterion | *contribution* |
| **O-2** | A family of pruned configurations, each buildable and measurable | *contribution* |
| **O-3** | Software contract preserved, at a measured cost | *contribution* |
| **O-4** | Formal equivalence to baseline on the surviving subset | *contribution* |
| **O-5** | Reclaimed area reinvested, energy change measured | *makes it worth doing* |
| **O-6** | One configuration fabricated and measured, in an always-on edge perception part | *makes it real* |

### Publication

- **Paper 1 — O-1 to O-4.** Demonstrable in simulation and synthesis, so it can be submitted while fabrication is pending. De-risks the project against a slipped tapeout.
- **Paper 2 — O-5 and O-6.** Written once silicon is measured.
- Test for the split: if the tapeout were cancelled tomorrow, Paper 1 would still stand.

### Status

- Specification stage. Problem, objectives and the compatibility argument are written; no RTL, tooling or measurements yet.
- Directory structure is placeholder only.

### Where to read further

| Question | Document |
|---|---|
| What may be pruned, and what guarantee replaces it | [`pruning-and-bridging.md`](pruning-and-bridging.md) |
| What that looks like in handler code | [`pruning-and-bridging-annex.md`](pruning-and-bridging-annex.md) |
| What the fabricated part consists of | [`objective-6-test-chip.md`](objective-6-test-chip.md) |

---

[`README`](../README.md)
