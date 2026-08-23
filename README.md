<div align="center">

# CARVE-V

### Core Area Reduction by Verified Elimination

**A workload-driven ISA subsetting flow for an application-class RISC-V core.**

[![Licence: Apache-2.0](https://img.shields.io/badge/docs%20%26%20tools-Apache--2.0-blue.svg)](LICENSE)
[![Core: CVA6](https://img.shields.io/badge/core-CVA6-orange.svg)](https://github.com/openhwgroup/cva6)

**Reviewing this?** Start with the
[one-page summary](docs/one-page-summary.md).

</div>

---

## 1. Problem statement

**The gap**

- An application-class RISC-V core implements an instruction set sized for general-purpose computing.
- A fixed-function edge device executes a small, knowable fraction of it.
- The difference is paid for in area, leakage and switching energy — on every part shipped.

**The question**

- Not *whether* the gap can be closed. Disabling an FPU or MMU is a documented configuration change, achievable in about a week.
- Whether it can be closed **methodically, verifiably, and without breaking the software contract**.

**Why the naive approach is unsatisfying** — three points that define the problem:

| | Gap in the naive approach | Consequence |
|:--:|---|---|
| **1** | **No method for the long tail.** Naming the FPU needs no technique. The hard question is the remainder: which integer opcodes, CSRs, compressed subsets, atomics. | Published measurement finds applications using **6–32 distinct instructions**. The tail is most of the opportunity, and intuition does not reach it. A defensible answer needs a criterion stated *before* it is applied, plus an argument that applying it is safe. |
| **2** | **Removing an instruction breaks the software contract.** Prior subsetting work abandons binary compatibility; the resulting part runs recompiled software and nothing else. | A part that is smaller *and* still executes what it no longer implements is a different claim. It requires deciding deliberately what moves across the hardware/software boundary, and at what measured cost. |
| **3** | **The result must be trustworthy enough to fabricate.** Silicon is not simulation. | A pruning step that is merely tested is not one proven equivalent to its baseline. The difference matters when the output cannot be patched. |

**Consequence**

- The deliverable is a **flow** — measured, verified, compatibility-preserving — not a smaller core.
- Whether the reclaimed silicon is worth reclaiming is itself open, and answering it means spending the area and measuring what it bought.

---

## 2. Objectives

| ID | Objective |
|:--:|---|
| **O-1** | Establish a reproducible method for deriving an instruction subset from a target workload, with a deletion criterion that is provably conservative with respect to reachable code. |
| **O-2** | Produce a family of pruned core configurations, each independently buildable and independently measurable. |
| **O-3** | Preserve the software contract: every removed instruction remains executable, at a measured cost. |
| **O-4** | Prove each pruned configuration equivalent to its baseline on the surviving subset. |
| **O-5** | Reinvest the reclaimed area in a domain-specific datapath and measure the resulting change in energy. |
| **O-6** | Carry one configuration through to a fabricated, measured test chip in an always-on edge perception application. |

- **O-1 – O-4** — the research contribution.
- **O-5** — what makes the contribution worth having.
- **O-6** — what makes it real. Component-level walk-through: [`objective-6-test-chip.md`](docs/objective-6-test-chip.md).

### 2.1 Suggested publishable unit

**Paper 1 — O-1 to O-4. Does not depend on silicon arriving.**

- Claim: *a method for deriving an instruction subset from a workload under a conservative criterion, applied to a hand-written application-class core, with binary compatibility preserved by emulation and each pruned configuration proven equivalent to its baseline.*
- Every element is demonstrable in simulation and synthesis.
- Can be submitted while fabrication is pending — de-risks the project against a slipped or failed tapeout.
- Venues: computer-architecture and design-automation conferences; a RISC-V summit for the compatibility contract specifically.

**Paper 2 — O-5 and O-6. Written once silicon is measured.**

- Content: the reinvestment result and the measured part.
- Publishing all six objectives at once makes the method compete for space with a chip result, which reviewers judge on entirely different criteria.

**Test for the split** — if the tapeout were cancelled tomorrow, O-1 to O-4 would still be publishable; O-5 to O-6 would not.

---

## 3. Technical approach

Condensed from the supporting documents. Section links go to the detail.

### 3.1 What is removed

Two groups, distinguished by whether software can tell —
[detail](docs/pruning-and-bridging.md#1-what-can-be-pruned):

- **Software-visible** — a whole extension (floating point, atomics); individual instructions within one (divide/remainder, keeping multiply); encoding subsets; unread CSRs; optional behaviour such as misaligned access support.
  - Every such removal requires a bridge.
- **Not software-visible** — structural sizing (scoreboard entries, caches, predictors); implementation strategy (iterative rather than single-cycle multiplier); unused address translation; verification-only interfaces.
  - No bridge required. Often where most of the area is.

### 3.2 How functionality is preserved

- **Guarantee** — for every instruction the baseline could execute, the pruned part produces the same architectural result. The split between hardware and software is invisible to the program except in timing. [Detail](docs/pruning-and-bridging.md#2-what-the-same-functionality-means).
- **Unit of equivalence** — the pruned core **plus its handler library**. Neither half is a complete implementation.
- **Mechanism** — an unimplemented encoding raises an illegal-instruction exception; the handler decodes it, reproduces the effect on the saved state, and resumes. [Detail](docs/pruning-and-bridging.md#3-the-mechanism).
- **Three conditions** — coverage (every removed encoding has a handler), fidelity (exact architectural effect, side effects included), presence (installed before application code; clean failure if absent).
- **Coverage enforcement** — hardware configuration, handler library and test set are all generated from one removed-encoding set, so they cannot drift. [Detail](docs/pruning-and-bridging.md#how-coverage-is-guaranteed).
- **Scope of cover** — a removed encoding gets a handler whether or not the workload was seen to use it. Two verdicts, not three.

### 3.3 What it costs

- Emulation is a compatibility guarantee, **not** a performance one.
- Whole-program cost ≈ *frequency × (emulated cost − hardware cost)*; low, because removal is measurement-driven and removed instructions are rare. [Detail](docs/pruning-and-bridging.md#4-what-the-bridge-costs).
- Must be **measured, not summed** — trap overhead interacts with pipeline and cache state.
- Averages hide the tail.

### 3.4 Where the boundary cannot move

- Bridging guarantees an instruction **works**, not that it works **in time**. [Detail](docs/pruning-and-bridging.md#5-when-not-to-bridge).
- An unbounded trap on the time-critical path is a failure of what the device sells, not a small slowdown.
- Some instructions therefore stay in hardware with a documented latency justification — a stronger result than removing them and breaking the timing guarantee.

### 3.5 The target part (O-6)

Always-on edge perception node — [detail](docs/objective-6-test-chip.md):

- One application, one hart, quantised arithmetic, everything in on-chip memory, a control loop with a deadline.
- Two power domains: a small always-on domain for trigger detection; a power-gated compute domain holding the pruned core, the domain-specific datapath and memory.
- Same die area as the baseline, spent differently. Figures of merit: energy per inference, worst-case response latency, silicon against prediction.

---

## 4. Supporting documents

| Document | Contents |
|---|---|
| [`one-page-summary.md`](docs/one-page-summary.md) | Everything below, compressed to a single page: problem, proposal, the central idea, objectives, publication split and status. |
| [`objective-6-test-chip.md`](docs/objective-6-test-chip.md) | O-6 illustrated. [What gets fabricated](docs/objective-6-test-chip.md#1-what-gets-fabricated) · [power domains](docs/objective-6-test-chip.md#2-the-idea-in-one-picture) · [inside the compute domain](docs/objective-6-test-chip.md#3-inside-the-compute-domain) · [source to silicon](docs/objective-6-test-chip.md#4-from-source-to-silicon) · [measurement setup](docs/objective-6-test-chip.md#5-measuring-the-finished-part) · [component inventory](docs/objective-6-test-chip.md#6-component-inventory) |
| [`pruning-and-bridging.md`](docs/pruning-and-bridging.md) | What may be pruned and what guarantee replaces it. [What can be pruned](docs/pruning-and-bridging.md#1-what-can-be-pruned) · [what "the same functionality" means](docs/pruning-and-bridging.md#2-what-the-same-functionality-means) · [the mechanism](docs/pruning-and-bridging.md#3-the-mechanism) · [what it costs](docs/pruning-and-bridging.md#4-what-the-bridge-costs) · [when not to bridge](docs/pruning-and-bridging.md#5-when-not-to-bridge) |
| [`pruning-and-bridging-annex.md`](docs/pruning-and-bridging-annex.md) | Handler-level detail, three removals followed through. [Integer division](docs/pruning-and-bridging-annex.md#1-example-integer-division) — an arithmetic result · [atomic operation](docs/pruning-and-bridging-annex.md#2-example-an-atomic-operation) — a guarantee by another mechanism · [misaligned access](docs/pruning-and-bridging-annex.md#3-example-a-misaligned-access) — a structural removal · [three ways this goes wrong](docs/pruning-and-bridging-annex.md#4-three-ways-this-goes-wrong) |

**Suggested reading order for review:** `one-page-summary.md` → this file →
`pruning-and-bridging.md` → `objective-6-test-chip.md`. The annex only if
handler-level detail is wanted.

---

## 5. References

**The core**

- [CVA6](https://github.com/openhwgroup/cva6) — the application-class RISC-V core this work starts from.
- [CVA6 user manual](https://docs.openhwgroup.org/projects/cva6-user-manual/) — parameters, configurations, design documents.

**Prior art on subsetting**

- [Flexing RISC-V Instruction Subset Processors to Extreme Edge](https://arxiv.org/abs/2505.04567) — closest prior work. Source of the 6–32 instruction finding. Targets tiny cores; does not preserve binary compatibility; does not formally verify the pruning.
- [NeCTAr](https://arxiv.org/abs/2503.14708) — heterogeneous RISC-V SoC, concept to tapeout in one semester. Feasibility precedent for a university test chip; not prior art on subsetting.

**Compatibility**

- [Trap-and-emulate for hardware forward-compatibility](https://lists.riscv.org/g/tech-profiles/topic/101153812) — RISC-V discussion of the mechanism and its real cost.
- [RISC-V unprivileged specification](https://docs.riscv.org/reference/isa/v20260120/unpriv/intro.html) — normative source for what an emulated instruction must reproduce.

**Comparison points**

- [Ibex](https://github.com/lowRISC/ibex) — small, production-quality 32-bit core. The direct answer to *why not just use a small core*.
- [X-HEEP](https://arxiv.org/abs/2401.05548) — configurable ultra-low-power RISC-V microcontroller for edge accelerator exploration.

---

## 6. Repository

- `rtl/`, `sw/`, `verif/`, `flow/`, `tools/` — empty placeholders. Directory names are a suggestion, not a required structure.
- [`docs/`](docs/) — the supporting documents listed in §4.

---

## 7. Licence

- Apache-2.0 — documentation and tooling.
- Solderpad Hardware Licence 2.1 — RTL.
- See [`LICENSE`](LICENSE).
