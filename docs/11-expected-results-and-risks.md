# 11 — Expected Results and Risks

Predictions recorded **before any measurement exists**. Some will be wrong. That
is what makes them worth recording.

> **Read these once, then write down your own before measuring.** Published
> predictions anchor — that is a real effect, and it works against you here.
> D-11 asks how the predictions fared; that question is only answerable if
> yours were committed independently.

---

## P-1 — Tier 1 will generate the headline and deliver the least silicon

**Prediction.** Decoder-level ISA pruning moves total area very little on an
application-class core. Expect **Tier 0 and Tier 2 to carry most of the
savings**, with Tier 1 contributing single-digit percentages at best.

**Reasoning.** CVA6 area is dominated by caches, branch-prediction structures,
the scoreboard and the register file. Decode logic is a small fraction of a core
that is itself a fraction of the die once SRAM is counted. Removing 40% of
*opcodes* is not removing 40% of *gates*, and the two are routinely conflated.

**Confidence.** High on direction, low on magnitude.

**If wrong**, it is the more interesting outcome and should lead the paper.

**Why this matters more than the number.** The project's natural headline is "we
removed N% of the ISA". Unaccompanied by honest area attribution, a reviewer
will derive the discrepancy themselves and trust everything else less.
Predicting it converts a vulnerability into a finding.

---

## P-2 — The area reduction will fall short of the intuitive estimate

**Prediction.** The frequently-quoted "30–40% by dropping FPU, MMU and
virtualisation" will not reproduce as a whole-die figure. Expect a substantially
smaller whole-die number, with the FPU the single largest contributor.

**Reasoning.** Three compounding effects:

1. The hypervisor extension is **not enabled by default** (`CVA6Cfg.RVH = 0`,
   CV64-only). Removing it removes nothing.
2. "L2 coherence" does not exist in the core to remove.
3. Percentages quoted against core logic get silently reinterpreted as die
   percentages once SRAM is in the floorplan.

**Confidence.** High.

**Action.** Report core-logic and whole-die deltas separately and label them.
Most disputes about this project's headline number will be disputes about which
denominator was used.

---

## P-3 — A 16×16 INT8 array will not be "easily" affordable

**Prediction.** A 16×16 systolic array with accumulators and staging buffers is
comparable in area to the entire non-cache CVA6 core. It will not fit
comfortably in the reclaimed area; expect either a smaller array or a larger die.

**Reasoning.** 256 processing elements plus accumulator width plus
double-buffered staging. Buffers, not multipliers, usually dominate.

**Confidence.** Medium-high.

**Action.** Derive the dimension from measured area (R-3.15). Do not commit to
16×16 in any document before trial synthesis. An 8×8 array that fits is a
result; a 16×16 array that forced the die to grow undermines the reinvestment
claim entirely.

---

## P-4 — Emulation overhead will be negligible on average and unacceptable in the tail

**Prediction.** Whole-program slowdown from trap-and-emulate will be small —
low single-digit percent — because removed instructions are removed precisely
*because* they are rare. But worst-case interrupt-path latency will be
materially affected, and that is the metric the application sells.

**Reasoning.** `Σ (frequency × trap cost)` is small when frequency is small.
Tail latency does not average.

**Confidence.** High on the mean, medium on the tail.

**Action.** R-5.12 exists for this. Analyse the real-time path separately and be
prepared to retain an instruction in hardware purely for latency reasons, even
where the subset says it could go.

---

## P-5 — Peak activation working set will bind before weight size

**Prediction.** The SRAM budget will be set by peak activation working set, not
by weight footprint.

**Reasoning.** Weight size is the number everyone quotes. Convolutional
intermediate tensors frequently exceed it, and radar point-cloud front-ends have
awkward intermediate representations.

**Confidence.** Medium.

**Action.** R-2.6. Measure both before freezing the memory budget. Discovering
this after SRAM macros are placed is expensive.

---

## P-6 — Formal equivalence will not close on the full core

**Prediction.** Full equivalence on a pipelined core with caches will not close
with open tooling. Expect to prove equivalence on the decode and execute paths
under stated assumptions, and to fall back to bounded model checking elsewhere.

**Confidence.** High.

**Action.** R-6.9. Plan for a partial result and state its bound precisely.

---

## P-7 — The reviewer question will be "why not Ibex?"

**Prediction.** First question at every review, regardless of framing.

**Action.** Measure Ibex and X-HEEP under the identical flow (R-2.23) and put
them in the first results table. Expect Ibex to be smaller than the pruned CVA6
in absolute terms — and answer with the actual argument: the contribution is a
*flow* applying to hand-written application-class RTL, plus a compatibility
guarantee neither baseline offers.

Being smaller than Ibex was never the claim. Trying to win on raw area is how
this project loses the argument.

---

# Risks

**R-1 — The application is a moving target.** Radar front-end choice changes the
network, which changes the subset, which changes the RTL.
*Mitigation:* freeze Corpus B before D-3; treat later changes as a pipeline
re-run (R-4.10), never a manual patch.

**R-2 — Scope creep into mixed-signal.** Someone will propose a sensor needing a
PHY. *Mitigation:* R-2.2 is a hard boundary. This has sunk university tapeouts
before.

**R-3 — Toolchain drift invalidating the subset.** A compiler upgrade emits an
instruction the analysis never saw. *Mitigation:* wire the pipeline re-run into
CI ([`06`](06-verification-requirements.md) §9.4). This will otherwise be
forgotten, and the failure is silent.

**R-4 — Formal effort consuming the schedule.** Equivalence checking absorbs
unlimited time. *Mitigation:* time-box; fall back to bounded checking with the
bound stated.

**R-5 — The demo overtaking the engineering.** A flying drone is a compelling
demonstration and a large distraction — airframe, flight controller, safety,
mechanical integration. *Mitigation:* the chip result must stand on bench
measurement alone. The drone is presentation, not evidence.

**R-6 — Publishing only flattering configurations.** The strongest pressure at
write-up. *Mitigation:* R-4.18 and R-3.12 are requirements precisely so this is
a compliance question rather than a judgement call under deadline.

---

**Previous:** [`10-references.md`](10-references.md) ·
**Index:** [`../README.md`](../README.md)
