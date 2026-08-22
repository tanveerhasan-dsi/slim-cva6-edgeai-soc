# 03 — Core Requirements

> [!NOTE]
> **§§1–6 are requirements.** **[§7](#7-reference-tinyml-datapath) is reference
> guidance** for the reinvestment half.

**Contents:**
[1. Baseline](#1-baseline) ·
[2. The pruning harness](#2-the-pruning-harness) ·
[3. What may be removed](#3-what-may-be-removed) ·
[4. Two removals that remove nothing](#4-two-removals-that-remove-nothing) ·
[5. Reinvestment](#5-reinvestment) ·
[6. Scaling study](#6-scaling-study) ·
[7. Reference TinyML datapath](#7-reference-tinyml-datapath)

---

## 1. Baseline

| ID | Requirement |
|:--:|---|
| **R-3.1** | The baseline MUST be an unmodified current-upstream CVA6, characterised under the same flow, tool versions and constraints as every pruned configuration. |
| **R-3.2** | The baseline configuration MUST be stated explicitly, because every reported delta is relative to it. |
| **R-3.3** | Baseline characterisation MUST be complete before any pruning work begins. |

> **On R-3.2.** "30% smaller" is meaningless without it. A reduction measured
> against a maximally-configured baseline is a different claim from one measured
> against a lean baseline, and the first is easy to produce by choosing a fat
> starting point.

---

## 2. The pruning harness

| ID | Requirement |
|:--:|---|
| **R-3.4** | Pruning MUST be expressed as build-time configuration layered over the core's existing parameter mechanism, not as edits to core RTL. |
| **R-3.5** | Every configuration MUST be independently buildable, simulatable and synthesisable. |
| **R-3.6** | Configurations MUST be composable, so the contribution of each removal can be isolated. |
| **R-3.7** | The harness MUST be reversible: any configuration returns to baseline behaviour by configuration change alone. |
| **R-3.8** | Adding a pruning option MUST NOT require touching unrelated modules. |

> **On R-3.4 and R-3.7.** A branch full of deletions cannot produce a curve,
> cannot be bisected when something breaks, and cannot be equivalence-checked
> against anything. Parameterisation is what makes the measurement possible —
> a methodological requirement, not a code-hygiene preference.

> **On R-3.6.** Removals interact: dropping a functional unit may also shrink
> the scoreboard. Isolation is what makes attribution honest.

---

## 3. What may be removed

Deliberately **not** enumerated here. Deriving the taxonomy of what can be
pruned, and at what granularity, is the design work — see
[`04-methodology-requirements.md`](04-methodology-requirements.md).

| ID | Requirement |
|:--:|---|
| **R-3.9** | Every removal MUST trace to a specific criterion from the methodology, recorded in the manifest. |
| **R-3.10** | No removal MAY rest solely on an instruction being absent from a dynamic trace. |
| **R-3.11** | Removals MUST be classified by whether they alter the software-visible ISA. Those that do trigger the obligations in [`05`](05-compatibility-requirements.md). |

---

## 4. Two removals that remove nothing

Both appear in almost every first draft, and both are worth checking before they
reach a slide.

- **The hypervisor extension** is disabled by default, is 64-bit only, and is
  still maturing. A default 32-bit build contains no such logic, so there is
  nothing to remove and no area to claim.
- **"L2 coherence"** does not exist in the core; it appears only in a
  multi-core configuration built around it.

| ID | Requirement |
|:--:|---|
| **R-3.12** | Every claimed removal MUST be evidenced by a measured area or power delta against the stated baseline. A removal producing no measurable delta MUST be reported as producing none. |

> **On R-3.12.** Reporting a removal that saved nothing is a finding, and the
> sort of finding that makes the rest of the numbers credible. A results table
> where every intervention succeeded reads as unfalsified rather than strong.

---

## 5. Reinvestment

| ID | Requirement |
|:--:|---|
| **R-3.13** | The TinyML datapath MUST be coupled to the core's execution pipeline rather than attached as a bus peripheral. |
| **R-3.14** | Custom instructions MUST occupy the RISC-V custom opcode space. |
| **R-3.15** | The datapath's dimensions MUST be derived from the measured area budget, not assumed in advance. |
| **R-3.16** | Throughput MUST be specified in cycles, including fill and drain latency. |
| **R-3.17** | The core MUST remain independently buildable and prunable with the coprocessor absent. |

> **On R-3.13.** Tight coupling means custom instructions are fetched, decoded
> and dispatched natively. Attaching over a bus instead would make the
> accelerator a peripheral — a different and much less interesting result.

> **On R-3.16.** A systolic array does not retire a matrix product in one cycle.
> Quoting single-cycle throughput loses a technical audience, and the error
> propagates into every derived performance figure.

> **On R-3.17.** The pruning study and the accelerator study must be separable,
> or neither can be attributed. It also protects the schedule: if the
> coprocessor slips, the core result survives independently.

---

## 6. Scaling study

| ID | Requirement |
|:--:|---|
| **R-3.18** | A 64-bit configuration MUST pass through the same harness, reporting how pruning yield varies with XLEN. |
| **R-3.19** | The scaling study MUST be reported even if it weakens the case for the chosen width. |

> **On R-3.19.** A study that only confirms decisions already made is not a
> study.

---

## 7. Reference TinyML datapath

> [!NOTE]
> **Reference guidance.** A sketch satisfying [§5](#5-reinvestment), not a
> specification. Dimensions in particular are expected to change once measured.

### 7.1 Attachment

A coprocessor interface into the execute stage, rather than a bus attachment, so
the core's decoder stays clean and the pruning and accelerator studies remain
separately attributable.

> Check early whether the chosen interface lets the coprocessor issue its own
> memory accesses. A datapath that assumed it can, when the implementation does
> not support it, needs a DMA path or core-issued loads — and discovering that
> late is a redesign.

### 7.2 Instruction set

A small set in the custom opcode space, covering: staging operands into the
array, launching a tiled matrix product, activation at the array edge,
short-vector multiply-accumulate, requantisation, and strided loads.

Requantisation earns its slot: it is pure overhead in software and runs once per
output element.

### 7.3 The array

Weight-stationary, quantised, with the dimension derived from measured area
(R-3.15). The originating proposal's dimension is recorded as a hypothesis, and
[`11`](11-expected-results-and-risks.md) predicts it will not fit comfortably.

Throughput stated in cycles including fill and drain (R-3.16), then measured.

### 7.4 Software, in stages

Build the software path incrementally and keep every intermediate result: a
reference implementation with no custom instructions, then the short-vector
operations alone, then the full array. Without intermediate points the energy
improvement cannot be attributed to any specific piece of hardware.

### 7.5 Sizing against the memory budget

The array's staging buffers compete with model weights for the same memory. This
is one joint budget, not two, and it is the most likely source of a late
floorplan surprise — buffers, not multipliers, usually dominate accelerator
area. Size buffers and weights together before committing to a dimension.

---

| ← Previous | Index | Next → |
|---|:---:|---|
| [`02 — Application Requirements`](02-application-requirements.md) | [`README`](../README.md) | [`04 — Methodology Requirements`](04-methodology-requirements.md) |
