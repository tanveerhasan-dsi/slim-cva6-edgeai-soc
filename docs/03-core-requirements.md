# 03 — Core Requirements

## 1. Baseline

| ID | Requirement |
|---|---|
| **R-3.1** | The baseline MUST be an unmodified current-upstream CVA6, characterised under the same flow, tool versions and constraints as every pruned configuration. |
| **R-3.2** | The baseline configuration MUST be stated explicitly — cache sizes, predictor sizes, enabled extensions — because every reported delta is relative to it. |
| **R-3.3** | Baseline characterisation MUST be complete before any pruning work begins. |

**On R-3.2.** "30% smaller" is meaningless without it. A reduction measured
against a maximally-configured CVA6 with an FPU, an MMU and large caches is a
very different claim from one measured against a lean baseline — and the first
is easy to produce by choosing a fat starting point. State the baseline, or the
number can be dismissed.

## 2. The pruning harness

| ID | Requirement |
|---|---|
| **R-3.4** | Pruning MUST be expressed as build-time parameters layered over CVA6's existing configuration mechanism, not as edits to core RTL. |
| **R-3.5** | Every configuration MUST be independently buildable, simulatable and synthesisable. |
| **R-3.6** | Configurations MUST be composable, so the contribution of each removal can be isolated. |
| **R-3.7** | The harness MUST be reversible: any configuration returns to baseline behaviour by parameter change alone. |
| **R-3.8** | Adding a pruning option MUST NOT require touching unrelated modules. |

**On R-3.4 and R-3.7.** A branch full of deletions cannot produce a curve,
cannot be bisected when something breaks, and cannot be equivalence-checked
against anything. Parameterisation is what makes the measurement possible at
all — this is a methodological requirement, not a code-hygiene preference.

**On R-3.6.** Removals interact. Dropping a functional unit may also shrink the
scoreboard, and attributing that saving to the wrong cause produces a
plausible, well-presented, wrong conclusion. Isolation is what makes
attribution honest.

## 3. What may be removed

Deliberately **not** enumerated here. Deriving the taxonomy of what can be
pruned, at what granularity, is the design work — see
[`04-methodology-requirements.md`](04-methodology-requirements.md).

| ID | Requirement |
|---|---|
| **R-3.9** | Every removal MUST trace to a specific criterion from the methodology, recorded in the manifest. |
| **R-3.10** | No removal MAY rest solely on an instruction being absent from a dynamic trace. |
| **R-3.11** | Removals MUST be classified by whether they alter the software-visible ISA. Those that do trigger the obligations in [`05-compatibility-requirements.md`](05-compatibility-requirements.md). |

## 4. Two removals that remove nothing

Both appear in almost every first draft of this project. Both are worth
checking before they reach a slide.

**The hypervisor extension.** Gated behind `CVA6Cfg.RVH` / `CVA6ConfigHExtEn`,
defaults to `0`, CV64-only, and still maturing upstream. A default CV32 build
contains no H-extension logic. There is nothing to remove and no area to claim.

**"L2 coherence."** CVA6 has no L2 cache in the core. Coherence appears only in
the OpenPiton configuration. Removing it from a standalone CVA6 is removing
something that was never instantiated.

| ID | Requirement |
|---|---|
| **R-3.12** | Every claimed removal MUST be evidenced by a measured area or power delta against the stated baseline. A removal producing no measurable delta MUST be reported as producing none. |

**On R-3.12.** Reporting a removal that saved nothing is not a weak result — it
is a finding, and it is the sort of finding that makes the rest of the numbers
credible. A results table where every intervention succeeded reads as
unfalsified rather than as strong.

## 5. Reinvestment

| ID | Requirement |
|---|---|
| **R-3.13** | The TinyML datapath MUST attach over CV-X-IF, not over a peripheral bus. |
| **R-3.14** | Custom instructions MUST occupy the RISC-V custom opcode space. |
| **R-3.15** | The datapath's dimensions MUST be derived from the measured area budget, not assumed in advance. |
| **R-3.16** | Throughput MUST be specified in cycles including fill and drain latency. |
| **R-3.17** | The core MUST remain independently buildable and prunable with the coprocessor absent. |

**On R-3.13.** CVA6 implements the five mandatory CV-X-IF interfaces
(compressed, issue, register, commit, result) and the coprocessor sits in the
execute stage. Custom instructions are therefore fetched, decoded and dispatched
natively. Attaching over AXI instead would make the accelerator a peripheral —
a different and much less interesting result.

**On R-3.16.** A systolic array does not retire a matrix product in one cycle.
A 16×16 array holds 256 processing elements; a 16×16×16 product is 4096
multiply-accumulates and streams over at least 16 cycles, plus fill and drain.
Quoting single-cycle throughput is the fastest way to lose a technical audience,
and the error propagates into every derived performance figure.

**On R-3.17.** The pruning study and the accelerator study must be separable, or
neither can be attributed. It also protects the schedule: if the coprocessor
slips, the core result survives independently.

## 6. Scaling study

| ID | Requirement |
|---|---|
| **R-3.18** | A 64-bit configuration MUST pass through the same harness, reporting how pruning yield varies with XLEN. |
| **R-3.19** | The scaling study MUST be reported even if it weakens the case for the chosen width. |

**On R-3.19.** The 32-bit choice is a design judgement. Measuring it turns that
judgement into a result — and a study that only confirms decisions already made
is not a study.

---

# 7. Reference Xtinyml datapath

A design satisfying §5. Dimensions in particular are expected to change once
measured.

## 7.1 Attachment

CV-X-IF, not a peripheral bus. CVA6 implements the five mandatory interfaces —
compressed, issue, register, commit, result — and the coprocessor sits in the
**execute stage**, so custom instructions are fetched, decoded and dispatched
natively by the pruned core.

Two consequences worth stating explicitly:

- The core's decoder stays clean, keeping the pruning study and the accelerator
  study independently attributable (R-3.17).
- **The memory interfaces are optional and not implemented in CVA6.** The
  coprocessor cannot issue its own loads and stores through the interface. Check
  this against the datapath design early — a design that assumed
  coprocessor-initiated memory access needs a DMA path or core-issued loads, and
  discovering that late is a redesign.

## 7.2 Instruction set

The naming comes from the originating proposal and is kept because it
communicates instantly, which matters more than elegance here.

| Instruction | Function |
|---|---|
| `MAT_LOAD` | Stage weights or activations into the array's buffers |
| `MAT_MUL` | Launch a tiled matrix product |
| `MAT_ACT_RELU` | Activation at the array edge, avoiding a round trip |
| `DOT4_I8` | 4×int8 SIMD multiply-accumulate into a 32-bit accumulator |
| `SHNR_SAT` | Saturating rounding shift-narrow — requantisation |
| `LD_STRIDE` | Strided / im2col load helper |

All in the RISC-V custom opcode space (R-3.14). `custom-0` … `custom-3` is how
`isaprof` reports them, so they appear in a profile without special handling.

`SHNR_SAT` earns its slot: requantisation between layers is pure overhead in
software and runs once per output element.

## 7.3 The array

Weight-stationary, int8 with an int4 mode. Dimension derived from measured area
(R-3.15) — the originating proposal's 16×16 is recorded as a hypothesis, and
[`11`](11-expected-results-and-risks.md) predicts it will not fit comfortably.

Throughput stated in cycles including fill and drain (R-3.16): cycles per tile,
tiles per layer, cycles per inference. Then measured.

## 7.4 Software, in three stages

Build the software path in this order, and keep all three results:

1. **Reference C**, no custom instructions — correctness and the energy baseline.
2. **`DOT4_I8` + `SHNR_SAT` only**, no array — isolates the SIMD contribution.
3. **Full array** — isolates the array contribution.

Same discipline as the pruning tiers, for the same reason. Without intermediate
points the energy improvement cannot be attributed to any specific piece of
hardware, and "we added an accelerator and things got faster" is not a result
anyone can build on.

## 7.5 Sizing against the memory budget

The array's staging buffers compete with model weights for the same SRAM. This
is one joint budget, not two, and it is the most likely source of a late
floorplan surprise.

Buffers, not multipliers, usually dominate accelerator area — double-buffering
to hide load latency doubles the staging cost. Size buffers and weights together
before committing to an array dimension.

---

**Previous:** [`02-application-requirements.md`](02-application-requirements.md) ·
**Next:** [`04-methodology-requirements.md`](04-methodology-requirements.md)
