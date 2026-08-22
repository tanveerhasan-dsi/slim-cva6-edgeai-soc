# 00 — Problem Statement

**Contents:**
[1. The problem](#1-the-problem) ·
[2. Why the obvious version fails](#2-why-the-obvious-version-fails) ·
[3. The contribution](#3-the-contribution) ·
[4. Prior art](#4-prior-art) ·
[5. What success looks like](#5-what-success-looks-like) ·
[6. A caution about the headline number](#6-a-caution-about-the-headline-number)

---

## 1. The problem

An application-class RISC-V core implements an ISA sized for general-purpose
computing. A fixed-function edge device executes a small, knowable fraction of
it. The gap is paid for in silicon area, leakage and switching energy on every
part shipped.

The question is not *whether* that gap can be closed — it obviously can — but
whether it can be closed **methodically, verifiably, and without breaking the
software contract**.

---

## 2. Why the obvious version fails

The obvious version is: disable the FPU, disable the MMU, re-synthesise, publish
the area delta. It takes about a week and it fails at review.

| Failure | Why it is fatal |
|---|---|
| It is a configuration change, not a contribution | CVA6 already exposes those knobs. Turning them off is using the core as documented. |
| It has no method for the long tail | Naming the FPU requires no technique. The hard question is the remaining ISA — base integer opcodes, CSRs, compressed subsets, atomics. |
| It invites one hard question | *Why not just use Ibex, or X-HEEP?* If the deliverable is a smaller core, both are already small, already proven, and neither cost a tapeout. |

> Published measurement finds applications using 6–32 distinct instructions
> (geometric mean 18) — the tail is most of the opportunity, and intuition does
> not reach it.

---

## 3. The contribution

Not the smaller core. The **flow that produces it**, and the guarantee it
carries:

| Claim | What makes it defensible |
|---|---|
| The subset is correct | Derived from measured reachability, not from block size |
| The pruning is sound | Formally equivalence-checked against the baseline |
| **The software still runs** | **Emulation for every removed encoding** |
| The area was worth reclaiming | Reinvested in a datapath with measured energy gains |

The third row is the differentiator. Existing subsetting work targets very small
cores and abandons binary compatibility. An explicit **hardware/software ISA
contract** — where the part stays architecturally compliant despite the missing
gates — is not something the literature has combined with a verified pruning
flow.

---

## 4. Prior art

Cite these accurately; overstating novelty costs more than it gains.

| Work | What it actually is |
|---|---|
| **Chipyard**<br>*UC Berkeley SLICE Lab* | Agile SoC framework built on generators. CVA6 is already an integrated core option, so a slim CVA6 drops into this flow rather than fighting it. |
| **NeCTAr** | A heterogeneous RISC-V SoC delivered concept-to-tapeout as a single semester-long class project. The **feasibility precedent** for a university team attempting silicon at all. |
| **Flexing RISC-V Instruction Subset Processors to Extreme Edge** | The **closest prior work**. Establishes the 6–32 instruction finding above. Targets tiny cores; does not preserve binary compatibility; does not formally verify the pruning. |
| **Property-driven automatic generation of reduced component hardware** | A granted US patent on automatic generation of reduced-ISA hardware. Read it before claiming novelty on automation alone. |

Full citations and links: [`10-references.md`](10-references.md).

### How this project differs

1. Generator-based flows elaborate only what is configured, so "removal" falls
   out of the methodology. This project prunes an **existing, hand-written
   SystemVerilog** core — the harder problem, and the one that generalises to
   the overwhelming majority of shipping RTL.
2. Prior subsetting work **abandons the software contract**. This project makes
   preserving it a requirement.
3. Prior work **validates in simulation**. This project requires formal
   equivalence, because the output is silicon.

---

## 5. What success looks like

A test chip, and a defensible claim of this shape:

> *A large fraction of the implemented ISA was removed from an application-class
> RISC-V core under a measured reachability criterion; the pruned core was
> proven equivalent to the baseline on the surviving subset; full binary
> compatibility was retained through emulation at a measured cost; and the
> reclaimed area was reinvested in a domain datapath, yielding a measured
> improvement in inference energy at equal or smaller die area.*

Every clause is a requirement in this specification, and every clause must be
**measured**, not asserted.

---

## 6. A caution about the headline number

It is tempting to lead with a large area-reduction percentage. Resist committing
to one before measuring.

On an application-class core, area is dominated by caches, branch prediction
structures, the scoreboard and the register file — not by decode logic. A
dramatic-sounding ISA reduction can move total area very little, while
unglamorous structural resizing moves it a great deal. Predicting that in
advance, and letting the measurement adjudicate, is a stronger result either
way.

---

| ← Previous | Index | Next → |
|---|:---:|---|
| — | [`README`](../README.md) | [`01 — Objectives and Scope`](01-objectives-and-scope.md) |
