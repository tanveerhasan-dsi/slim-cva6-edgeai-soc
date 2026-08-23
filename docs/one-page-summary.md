# CARVE-V — One-Page Summary

*Core Area Reduction by Verified Elimination. Prepared for review; full detail in
[`README`](../README.md).*

---

**In one sentence.** Remove a large fraction of the instruction set from an
application-class RISC-V core under a measured criterion, keep every removed
instruction working through software emulation, prove each pruned configuration
equivalent to its baseline, and spend the reclaimed area on a domain-specific
datapath — demonstrated in an always-on micro-UAV perception part.

---

### Problem

- An application-class core implements an ISA sized for general-purpose computing; a fixed-function edge device uses a small fraction of it. The difference costs area, leakage and switching energy on every part shipped.
- Closing it naively — disabling an FPU or MMU — is a documented configuration change with no method for the long tail. Published measurement finds applications using **6–32 distinct instructions**.

### Application

- **Always-on micro-UAV perception node** — obstacle avoidance from mmWave radar point clouds; airframe health monitoring from IMU and acoustic vibration. Duty-cycled: a microwatt always-on domain wakes a power-gated compute domain on a trigger.
- The application is what makes each deletion arguable from the workload — quantised models → no floating point; a control-loop deadline → the MMU is a *liability*, not merely unused; one application on one hart → no virtual memory or atomics; on-chip networks → no DRAM interface.
- **Radar rather than a camera** is a feasibility judgement: camera-class detection needs megabytes of weights and a hard analogue PHY, both out of reach for a first university tapeout.
- Figures of merit: energy per inference; **worst-case** sensor-to-actuator latency and jitter; area at equal die size.

### Proposal

- Derive the subset from **measured reachability**, under a criterion stated before it is applied.
- Preserve binary compatibility: every removed encoding is emulated, so the part stays a legal implementation.
- **Formally prove** each configuration equivalent to the baseline on the surviving subset.
- Reinvest the reclaimed area and measure what it bought.

### The central idea

- The unit that is functionally equivalent to the original core is **the pruned core plus its handler library** — neither half alone.
- An unimplemented encoding traps; the handler reproduces its architectural effect exactly and resumes — invisible to the program except in timing.
- Emulation is a **compatibility guarantee, not a performance one**. Whole-program cost stays low because removal is measurement-driven, but an unbounded trap on the time-critical path is disqualifying — so some instructions stay in hardware for latency reasons alone.

### Objectives

The research contribution:

- **O-1** — Reproducible subsetting method with a conservative deletion criterion.
- **O-2** — A family of pruned configurations, each buildable and measurable.
- **O-3** — Software contract preserved, at a measured cost.
- **O-4** — Formal equivalence to baseline on the surviving subset.

Then: **O-5** — reclaimed area reinvested, energy change measured (what makes it
worth doing); **O-6** — one configuration fabricated and measured in the
perception part above (what makes it real).

### Publication

- **Paper 1 — O-1 to O-4.** Demonstrable in simulation and synthesis, so it can be submitted while fabrication is pending; de-risks the project against a slipped tapeout.
- **Paper 2 — O-5 and O-6**, once silicon is measured.
- Test for the split: if the tapeout were cancelled tomorrow, Paper 1 would still stand.

### Status

- Specification stage: problem, objectives and the compatibility argument are written. No RTL, tooling or measurements yet; directory structure is placeholder only.

### Where to read further

- [`pruning-and-bridging.md`](pruning-and-bridging.md) — what may be pruned, and what guarantee replaces it.
- [`pruning-and-bridging-annex.md`](pruning-and-bridging-annex.md) — what that looks like in handler code.
- [`objective-6-test-chip.md`](objective-6-test-chip.md) — what the fabricated part consists of.

---

[`README`](../README.md)
