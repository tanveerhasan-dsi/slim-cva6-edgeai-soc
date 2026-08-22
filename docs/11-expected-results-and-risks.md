# 11 — Expected Results and Risks

Predictions recorded **before any measurement exists**. Some will be wrong; that
is what makes them worth recording.

> Read these once, then write down your own before measuring. Published
> predictions anchor, and D-11 asks how the predictions fared — a question only
> answerable if yours were committed independently.

---

## Predictions

| # | Prediction | Confidence |
|:--:|---|---|
| **P-1** | Decoder-level ISA pruning generates the headline and delivers the least silicon; configuration-level and structural changes carry most of the area. | High on direction, low on magnitude |
| **P-2** | The area reduction will fall short of the intuitive estimate as a whole-die figure, with the FPU the single largest contributor. | High |
| **P-3** | The proposed array dimension will not be comfortably affordable; expect a smaller array or a larger die. | Medium-high |
| **P-4** | Emulation overhead will be negligible on average and material in the tail. | High on the mean, medium on the tail |
| **P-5** | Peak activation working set will bind the memory budget before weight size does. | Medium |
| **P-6** | Formal equivalence will not close on the full core with open tooling. | High |
| **P-7** | The first question at every review will be "why not just use a small core?" | — |

---

### P-1 — The headline and the silicon come from different places

Core area is dominated by caches, branch-prediction structures, the scoreboard
and the register file. Decode logic is a small fraction of a core that is itself
a fraction of the die once memory is counted. Removing a large share of
*opcodes* is not removing that share of *gates*, and the two are routinely
conflated.

If this is wrong, it is the more interesting outcome and should lead the paper.
Either way, predicting it converts a vulnerability into a finding: unaccompanied
by honest area attribution, a reviewer will derive the discrepancy themselves
and trust everything else less.

### P-2 — The intuitive estimate will not reproduce

Three compounding effects: the hypervisor extension is not enabled by default,
so removing it removes nothing; L2 coherence does not exist in the core to
remove; and percentages quoted against core logic get silently reinterpreted as
die percentages once memory is in the floorplan.

**Action.** Report core-logic and whole-die deltas separately and label them.
Most disputes about the headline number will be disputes about the denominator.

### P-3 — The array will not be comfortably affordable

Processing elements, accumulator width and double-buffered staging together are
comparable in area to the entire non-cache core, and buffers usually dominate.

**Action.** Derive the dimension from measured area (R-3.15) and do not commit
to one before trial synthesis. A smaller array that fits is a result; a larger
one that forced the die to grow undermines the reinvestment claim.

### P-4 — Negligible on average, material in the tail

Cost is frequency times trap cost, and removed instructions are removed
precisely because they are rare. But tail latency does not average, and
worst-case interrupt-path latency is the metric the application sells.

**Action.** R-5.12 exists for this. Analyse the real-time path separately, and
be prepared to retain an instruction in hardware purely for latency reasons.

### P-5 — Activations will bind before weights

Weight size is the number everyone quotes. Intermediate tensors frequently
exceed it, and radar front-ends have awkward intermediate representations.

**Action.** R-2.6. Measure both before freezing the memory budget.

### P-6 — Formal equivalence will not fully close

Expect to prove equivalence on the decode and execute paths under stated
assumptions and to fall back to bounded checking elsewhere.

**Action.** R-6.9. Plan for a partial result and state its bound precisely.

### P-7 — "Why not just use a small core?"

**Action.** Measure the comparison cores under the identical flow (R-2.23) and
put them in the first results table. Expect them to be smaller in absolute
terms, and answer with the actual argument: the contribution is a flow that
applies to hand-written application-class RTL, plus a compatibility guarantee
neither baseline offers.

Being smaller than a small core was never the claim. Trying to win on raw area
is how this project loses the argument.

---

## Risks

| # | Risk | Mitigation |
|:--:|---|---|
| **K-1** | The application is a moving target: the front-end choice changes the network, which changes the subset, which changes the RTL. | Freeze the target corpus before D-3; treat later changes as a pipeline re-run (R-4.10), never a manual patch. |
| **K-2** | Scope creep into mixed-signal — someone will propose a sensor needing a PHY. | R-2.2 is a hard boundary. This has sunk university tapeouts before. |
| **K-3** | Toolchain drift invalidating the subset. | Wire the pipeline re-run into CI ([`06`](06-verification-requirements.md) §9.4). This will otherwise be forgotten, and the failure is silent. |
| **K-4** | Formal effort consuming the schedule. | Time-box it; fall back to bounded checking with the bound stated. |
| **K-5** | The demo overtaking the engineering — a flying demonstrator is compelling and a large distraction. | The chip result must stand on bench measurement alone. The airframe is presentation, not evidence. |
| **K-6** | Publishing only flattering configurations, the strongest pressure at write-up. | R-4.18 and R-3.12 are requirements precisely so this is a compliance question rather than a judgement call under deadline. |

---

| ← Previous | Index | Next → |
|---|:---:|---|
| [`10 — References`](10-references.md) | [`README`](../README.md) | — |
