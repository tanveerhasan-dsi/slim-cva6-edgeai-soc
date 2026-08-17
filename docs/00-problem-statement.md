# 00 — Problem Statement

## 1. The problem

An application-class RISC-V core implements an ISA sized for general-purpose
computing. A fixed-function edge device executes a small, knowable fraction of
it. The gap is paid for in silicon area, leakage, and switching energy on every
part shipped, forever.

The question this project exists to answer is not *whether* that gap can be
closed — it obviously can — but whether it can be closed **methodically,
verifiably, and without breaking the software contract**.

## 2. Why the obvious version of this project fails

The obvious version is: disable the FPU, disable the MMU, re-synthesise, publish
the area delta. It takes about a week and it fails at review, for three
compounding reasons.

**It is a configuration change, not a contribution.** CVA6 already exposes those
knobs. Turning them off is using the core as documented.

**It has no method for the long tail.** Naming the FPU requires no technique.
The genuinely hard question is the remaining ISA: which base integer opcodes,
which CSRs, which compressed subsets, which atomics. Published measurement finds
applications using **6–32 distinct instructions** (geometric mean 18), i.e.
**31–84% of RV32E** — meaning the tail is most of the opportunity, and intuition
does not reach it.

**It invites one unanswerable question.** *Why not just use Ibex, or X-HEEP?*
If the deliverable is a smaller core, that question has no good answer. Both are
already small, both are proven, and neither cost a tapeout to obtain.

## 3. The contribution this project does make

Not the smaller core. The **flow that produces it**, and the guarantee it
carries:

| Claim | What makes it defensible |
|---|---|
| The subset is correct | Derived from measured reachability, not from block size |
| The pruning is sound | Formally equivalence-checked against the baseline |
| The software still runs | Trap-and-emulate handlers for every removed encoding |
| The area was worth reclaiming | Reinvested in a datapath with measured energy gains |

The third row is the differentiator. Existing subsetting work targets very small
cores and simply abandons binary compatibility. Defining an explicit
**hardware/software ISA contract** — where the part remains architecturally
compliant *with handlers installed*, despite the missing gates — is not
something the literature has combined with a verified pruning flow.

## 4. Prior art, stated honestly

Cite these accurately. Overstating novelty is the fastest way to lose a review.

**Chipyard** (UC Berkeley SLICE Lab) — agile SoC framework: Chisel, FIRRTL,
Rocket Chip generators, Hammer for VLSI, FireSim for FPGA-accelerated emulation.
CVA6 is already an integrated core option alongside Rocket, BOOM, Gemmini,
Saturn and NVDLA, so a slim CVA6 drops into this flow rather than fighting it.

**NeCTAr** — a heterogeneous RISC-V SoC for language-model inference in Intel
16: 4 mm², 320 kB SRAM, 400 MHz at 0.85 V, 132 GOPS/W, delivered concept-to-
tapeout as a single semester-long class project. This is the feasibility
precedent for a university team attempting silicon at all.

**"Flexing RISC-V Instruction Subset Processors to Extreme Edge"**
(arXiv:2505.04567) — the closest prior work. Establishes the 6–32 instruction
finding above. Targets tiny cores; does not preserve binary compatibility; does
not formally verify the pruning.

**Property-driven automatic generation of reduced component hardware** — a
granted US patent covering automatic generation of reduced-ISA hardware. Read it
before claiming novelty on automation alone.

### How this project differs

1. Berkeley parameterises **generators** — Chisel elaborates only what is
   configured, so "removal" is a natural consequence of the methodology. This
   project prunes an **existing, hand-written SystemVerilog** application-class
   core. That is the harder problem, and the one that generalises to the
   overwhelming majority of shipping RTL, which is not generated.
2. Prior subsetting work **abandons the software contract**. This project makes
   preserving it a requirement.
3. Prior work **validates in simulation**. This project requires formal
   equivalence, because the output is silicon.

## 5. What success looks like

A test chip, and a defensible claim of this shape:

> *A large fraction of the implemented ISA was removed from an application-class
> RISC-V core under a measured reachability criterion; the pruned core was
> proven equivalent to the baseline on the surviving subset; full binary
> compatibility was retained through emulation at a measured cost; and the
> reclaimed area was reinvested in a domain datapath, yielding a measured
> improvement in inference energy at equal or smaller die area.*

Every clause in that sentence is a requirement in this specification, and every
clause must be **measured**, not asserted.

## 6. A caution about the headline number

It is tempting to lead with a large area-reduction percentage. Resist committing
to one before measuring.

On an application-class core, area is dominated by caches, branch prediction
structures, the scoreboard and the register file — **not** by decode logic. It
is entirely possible for a dramatic-sounding ISA reduction to move total area
very little, while unglamorous structural resizing moves it a great deal.

Discovering this at review is bad. Predicting it in advance, and letting the
measurement adjudicate, is a stronger result either way — including the case
where the prediction turns out wrong.

---

**Next:** [`01-objectives-and-scope.md`](01-objectives-and-scope.md)
