# 09 — Acceptance Criteria

Gates are defined by **artifact and evidence**, never by elapsed time. A gate is
passed when its evidence exists and is reproducible.

## Gate 1 — Method established

| Criterion | Evidence |
|---|---|
| Deletion criterion stated formally, before application | D-1 |
| Conservative with respect to reachable code, with soundness argument | R-4.2, R-4.3 |
| Removal never justified by trace absence alone | R-4.4 |
| Granularity stated and justified | R-4.11, R-4.12 |
| Pipeline reproducible from a committed manifest | R-4.7–R-4.9 |
| Limitations stated | D-1 item 6 |

**Fails if:** the criterion is described only by the configurations it produced.
A method is assessable; a list of removals is not.

## Gate 2 — Baseline characterised

| Criterion | Evidence |
|---|---|
| Unmodified CVA6 characterised, configuration stated explicitly | R-3.1, R-3.2 |
| Ibex and X-HEEP measured under the same flow | R-2.23 |
| Both workload tiers built and running | R-2.15–R-2.17 |
| Measurements regenerable | R-1.6 |

**Fails if:** the baseline configuration is unstated. Every later delta is
meaningless without it, and a generously-configured baseline inflates every
result that follows.

## Gate 3 — Subset report reproducible

| Criterion | Evidence |
|---|---|
| Full Corpus B corpus profiled, including RTOS and interrupt paths | R-2.16, R-4.13 |
| Every encoding classified, with traceable evidence | R-4.6 |
| Over-approximation quantified | R-4.5 |
| Re-run on unchanged inputs reproduces identical classifications | R-4.9 |

**Fails if:** the corpus omits boot code, fault handlers or driver paths. Those
paths are where an erroneous removal becomes a field hang rather than a bench
failure.

## Gate 4 — Configurations build and measure

| Criterion | Evidence |
|---|---|
| Every configuration independently builds, simulates and synthesises | R-3.5 |
| Composable and reversible | R-3.6, R-3.7 |
| Each traced to its criterion | R-3.9 |
| Per-configuration deltas reported, **including nil results** | R-3.12, R-4.18 |
| Savings attributed to the correct cause | R-4.19 |

**Fails if:** every configuration succeeded. Not because success is suspicious
in itself, but because a study with no nil results has almost certainly not
reported them.

## Gate 5 — Equivalence proven

| Criterion | Evidence |
|---|---|
| Each configuration proven equivalent on the surviving subset | R-6.7 |
| Assumption set stated and justified | R-6.8 |
| Unproven properties listed with bounded-verification arguments | R-6.9 |
| Re-established in CI | R-6.10 |

**Fails if:** assumptions are implicit. An unstated assumption does not make the
proof stronger — it makes it unfalsifiable.

## Gate 6 — Compatibility demonstrated

| Criterion | Evidence |
|---|---|
| Handlers for every removed encoding | R-5.1 |
| Bit-identical results including side effects | R-5.4, R-5.5 |
| Re-entrant, interrupt-safe, nested traps tested | R-5.6, R-5.8 |
| RISCOF passes with handlers | R-5.13 |
| RISCOF run without handlers, failures documented | R-5.14 |
| **Both** results published | R-5.15 |
| Cost table and measured whole-program slowdown | R-5.9, R-5.10 |
| Real-time path analysed | R-5.12 |
| Behaviour without handlers is a clean diagnosable trap | R-5.17 |

**Fails if:** only the passing compliance run is published.

## Gate 7 — Reinvestment measured

| Criterion | Evidence |
|---|---|
| Coprocessor over CV-X-IF, custom opcode space | R-3.13, R-3.14 |
| Dimensions derived from measured area budget | R-3.15 |
| Throughput in cycles including fill and drain | R-3.16 |
| Core still buildable without the coprocessor | R-3.17 |
| Energy improvement measured against baseline | R-2.18 |

**Fails if:** throughput is quoted as one product per cycle. A 16×16 array is
256 processing elements against 4096 multiply-accumulates.

## Gate 8 — Prototype closes the loop

| Criterion | Evidence |
|---|---|
| Full application on FPGA with real sensors | R-6.14 |
| Measured latency **and worst-case jitter** | R-2.12, R-2.13, R-6.15 |
| Measured against the pre-allocated budget | R-2.14 |
| Handlers exercised under interrupt load | R-6.16 |

**Fails if:** only mean latency is reported. The thesis is a determinism claim,
and the mean is the statistic that conceals the tail it depends on.

## Gate 9 — Signoff

| Criterion | Evidence |
|---|---|
| Timing closed at all corners, margin recorded | R-6.20 |
| DRC and LVS clean | R-6.21 |
| Power analysed including wake transitions | R-6.22, R-7.16 |
| Checklist complete and archived | R-6.23 |
| Bring-up plan, scan and debug access | R-6.24 |
| Manifest generated automatically | R-7.21, R-7.22 |

## Gate 10 — Silicon measured

| Criterion | Evidence |
|---|---|
| Chip brought up on the daughterboard | D-10 |
| FPS against milliwatts measured | R-2.19 |
| Closed-loop latency and jitter measured on silicon | R-2.20 |
| Silicon compared against pre-silicon predictions, disagreements included | D-11 |

---

## How the work will be judged overall

Four questions, in order of weight:

1. **Is the method sound, and would it work on a different workload?** The
   method is the contribution. A subset that happens to be correct for one
   binary is a result about that binary.
2. **Is the compatibility claim real?** Bit-identical, verified against a
   reference, compliant with handlers installed, measured cost.
3. **Are the measurements honest?** Baseline stated, nil results reported,
   attribution correct, predictions recorded in advance.
4. **Does the silicon work?**

Note that (4) is last. A working chip with an unjustified subset is an
engineering exercise. A sound, verified, reproducible method that produced a
chip is a contribution — and it remains one even if the silicon disappoints,
provided the disappointment is measured and explained.

---

**Previous:** [`08-deliverables.md`](08-deliverables.md) ·
**Next:** [`10-references.md`](10-references.md)
