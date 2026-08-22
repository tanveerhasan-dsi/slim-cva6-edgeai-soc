# 09 — Acceptance Criteria

Gates are defined by **artifact and evidence**, never by elapsed time. A gate is
passed when its evidence exists and is reproducible.

---

## The gates

| Gate | What must be evidenced | Fails if |
|:--:|---|---|
| **1 — Method established** | A deletion criterion stated formally before it was applied, conservative with respect to reachable code, with its soundness argument, failure-mode analysis, stated granularity and stated limits. Pipeline reproducible from a manifest. <br>*R-4.1–R-4.5, R-4.7–R-4.12, R-4.14–R-4.17, R-4.20–R-4.22; D-1* | The criterion is described only by the configurations it produced. A method is assessable; a list of removals is not. |
| **2 — Baseline characterised** | The unmodified core characterised with its configuration stated explicitly; comparison cores measured under the same flow; both corpora built; measurements regenerable. <br>*R-1.1–R-1.3, R-1.6, R-2.15–R-2.17, R-2.23, R-3.1–R-3.3* | The baseline configuration is unstated. Every later delta is meaningless without it, and a generous baseline inflates everything that follows. |
| **3 — Subset report reproducible** | The whole target workload profiled, including kernel and interrupt paths; every encoding classified with traceable evidence; over-approximation quantified; re-runs reproduce identical classifications. <br>*R-2.16, R-4.5, R-4.6, R-4.9, R-4.13* | The corpus omits boot code, fault handlers or driver paths — where an erroneous removal becomes a field hang rather than a bench failure. |
| **4 — Configurations build and measure** | Every configuration independently builds, simulates and synthesises; composable and reversible; each traced to its criterion; per-configuration deltas reported **including nil results**; savings attributed to the correct cause. <br>*R-3.4–R-3.12, R-3.18, R-3.19, R-4.16–R-4.19* | Every configuration succeeded — not because success is suspicious, but because a study with no nil results has almost certainly not reported them. |
| **5 — Equivalence proven** | Each configuration proven equivalent on the surviving subset, with the assumption set stated and justified, unproven properties listed with their bounded arguments, and equivalence re-established in CI. <br>*R-6.7–R-6.10* | Assumptions are implicit. An unstated assumption does not make the proof stronger; it makes it unfalsifiable. |
| **6 — Compatibility demonstrated** | Handlers for every removed encoding, bit-identical including side effects, re-entrant and nested-trap tested; compliance run **both** with and without handlers and both published; cost data and measured whole-program slowdown; real-time path analysed; clean diagnosable failure without handlers. <br>*R-5.1–R-5.18, R-6.1–R-6.6, R-6.11–R-6.13* | Only the passing compliance run is published. |
| **7 — Reinvestment measured** | Coprocessor coupled to the pipeline in the custom opcode space; dimensions derived from measured area; throughput stated in cycles including fill and drain; core still buildable without it; energy improvement measured against the baseline. <br>*R-2.18, R-3.13–R-3.17* | Throughput is quoted as one matrix product per cycle. |
| **8 — Prototype closes the loop** | Full application on FPGA with real sensors; measured latency **and worst-case jitter** against the pre-allocated budget; handlers exercised under interrupt load. <br>*R-2.12–R-2.14, R-6.14–R-6.16* | Only mean latency is reported. The thesis is a determinism claim, and the mean conceals the tail it depends on. |
| **9 — Signoff** | Timing closed at all corners with margin recorded; physical verification clean; power analysed including wake transitions; checklist archived; bring-up, test and debug access in place; manifest generated automatically. <br>*R-6.17–R-6.24, R-7.1–R-7.22* | — |
| **10 — Silicon measured** | Part brought up on its board; throughput against power measured; closed-loop latency and jitter measured on silicon and compared against the pre-silicon predictions, disagreements included. <br>*R-2.19–R-2.22; D-10, D-11* | — |

The requirements not cited above are the device, memory and architecture
constraints of [`02`](02-application-requirements.md) §§1–5 and the reporting
constraints of [`01`](01-objectives-and-scope.md) §6. They are evidenced through
the deliverables in [`08`](08-deliverables.md), and through the implementation
constraints gated at Gate 9, rather than at a gate of their own.

---

## How the work is judged overall

Four questions, in order of weight:

| # | Question | Why it ranks there |
|:--:|---|---|
| **1** | Is the method sound, and would it work on a different workload? | The method is the contribution. A subset that happens to be correct for one binary is a result about that binary. |
| **2** | Is the compatibility claim real? | Bit-identical, verified against a reference, compliant with handlers installed, measured cost. |
| **3** | Are the measurements honest? | Baseline stated, nil results reported, attribution correct, predictions recorded in advance. |
| **4** | Does the silicon work? | — |

(4) is last deliberately. A working chip with an unjustified subset is an
engineering exercise. A sound, verified, reproducible method that produced a
chip is a contribution — and it remains one even if the silicon disappoints,
provided the disappointment is measured and explained.

---

| ← Previous | Index | Next → |
|---|:---:|---|
| [`08 — Deliverables`](08-deliverables.md) | [`README`](../README.md) | [`10 — References`](10-references.md) |
