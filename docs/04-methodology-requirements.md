# 04 — Methodology Requirements and Reference Method

> **Sections 1–8 are requirements** — what must be true of the subsetting
> method. **Section 9 is a reference method** that satisfies them.
>
> The reference method is a starting point, not a specification. Where the team
> has measured data and this document has estimates, the team's judgement wins.
> What is *not* negotiable is §2 — the deletion criterion — because getting it
> wrong is not recoverable in silicon.

## 1. What is being asked for

A **reproducible procedure** that takes a workload and produces a defensible
instruction subset, plus the evidence that the procedure is sound.

Not a list of instructions. A list is an output; the assessable contribution is
the process that generated it and the argument for why that process is safe.

## 2. The deletion criterion

| ID | Requirement |
|---|---|
| **R-4.1** | The method MUST define an explicit deletion criterion, stated before it is applied. |
| **R-4.2** | The criterion MUST be **conservative with respect to reachable code**: no instruction the program can execute may be classified as removable. |
| **R-4.3** | The method MUST state its failure mode — what happens when the criterion is wrong — and argue why that failure mode is acceptable. |
| **R-4.4** | Absence from an execution trace MUST NOT, alone, justify removal. |
| **R-4.5** | Where the criterion over-approximates, the method MUST say so and quantify by how much. |

**On R-4.2 and R-4.4.** These are safety requirements, and they are the only
part of the method specified here, because getting them wrong is not recoverable
in silicon.

An instruction that a profiling run never executed is not an instruction that
*cannot* execute. Coverage is a property of the stimulus, not of the program.
The interrupt path that only runs on a fault, the error handler that only runs
on a sensor timeout, the libc branch that only runs on an allocation failure —
none of these appear in a healthy run, and all of them are reachable. A method
that treats "not observed" as "not present" will produce a chip that works on
the bench and hangs in flight.

Your criterion must be bounded by what the program *can* do. How you establish
that bound is your design decision.

**On R-4.3.** Every criterion has a failure mode. An over-approximating one
wastes area; an under-approximating one produces a broken chip. These are not
symmetric, and the method must be explicit about which side it errs towards and
why.

## 3. Evidence and reproducibility

| ID | Requirement |
|---|---|
| **R-4.6** | Every classification MUST trace to specific, recorded evidence. |
| **R-4.7** | The full pipeline — workload → evidence → classification → configuration — MUST be reproducible from a committed manifest. |
| **R-4.8** | The manifest MUST record source commits, tool versions, workload binaries and command lines. |
| **R-4.9** | Re-running the pipeline on unchanged inputs MUST produce identical classifications. |
| **R-4.10** | The method MUST be re-runnable when the workload changes, without manual re-derivation. |

**On R-4.10.** The workload *will* change — models get retrained, the RTOS gets
updated, a driver gets rewritten. A method that requires a person to redo the
analysis by hand is a one-off measurement wearing the costume of a flow, and it
will not survive first contact with a schedule.

## 4. Granularity

| ID | Requirement |
|---|---|
| **R-4.11** | The method MUST state the granularity at which it classifies — instruction, instruction group, functional unit, or structural resource — and justify the choice. |
| **R-4.12** | Where hardware granularity is coarser than classification granularity, the method MUST say how the mismatch is resolved. |

**On R-4.12.** Hardware rarely divides where the ISA does. A single functional
unit may implement several instructions; removing one of them may save nothing
at all unless the others go too. Classification granularity and implementation
granularity are different things, and conflating them produces predicted
savings that synthesis does not deliver.

## 5. Coverage of the whole workload

| ID | Requirement |
|---|---|
| **R-4.13** | Evidence MUST cover the complete linked image: application, libraries, runtime, RTOS kernel, boot code, exception and interrupt paths. |
| **R-4.14** | The method MUST state how it handles code not present at analysis time — dynamically loaded, self-modifying, or externally supplied. |
| **R-4.15** | Any excluded region MUST be listed with its justification. |

## 6. Measurement discipline

| ID | Requirement |
|---|---|
| **R-4.16** | Each configuration MUST be measured under identical flow, constraints and tool versions. |
| **R-4.17** | Results MUST be reported as a curve across configurations, not a single point. |
| **R-4.18** | Configurations that save nothing MUST be reported. |
| **R-4.19** | Where a saving is attributable to a structural change rather than an ISA change, the report MUST attribute it correctly. |

**On R-4.19.** This is where a subsetting study most easily misleads — usually
without intending to. If shrinking a cache and removing an extension happen in
the same configuration, the area delta belongs to both, and reporting the total
under the ISA heading overstates the ISA result. Attribution is what
distinguishes a measurement from a marketing figure, and reviewers of this
particular claim will look for it.

## 7. The instrument

[`tools/isaprof/`](../tools/isaprof/) is provided, working, and dependency-free.
It performs three operations:

- **`static`** — a linear sweep of every allocated executable region of an ELF.
- **`dynamic`** — execution counts extracted from a simulator trace.
- **`classify`** — applies the reference policy of §9 to those measurements.

Measurement and policy are kept in separate modules on purpose. `static` and
`dynamic` are facts; `classify` is a judgement, and it is the part expected to
be replaced. Swapping the policy must not require touching the measurement.

| ID | Requirement |
|---|---|
| **R-4.20** | The method MAY use `isaprof`, extend it, or replace it — but MUST justify the choice and MUST NOT rely on unstated behaviour. |
| **R-4.21** | If replaced, the substitute MUST satisfy every requirement in this document. |
| **R-4.22** | If the reference policy is used unmodified, that MUST be stated as a decision, with its assumptions checked against the actual workload. |

**On R-4.22.** A default that nobody examined is not a decision. The reference
policy embeds assumptions — notably its real-time-critical instruction list —
that are correct for the application in
[`02`](02-application-requirements.md) and may not be correct for a variant of
it.

Read [`tools/isaprof/README.md`](../tools/isaprof/README.md) before designing
around it — in particular how the two passes differ in what they can support,
and the undecodable-rate signal, which tells you when a static sweep is not yet
trustworthy.

## 8. Deliverable

A methodology document containing:

1. The deletion criterion, stated formally.
2. The soundness argument for R-4.2, and the failure-mode analysis for R-4.3.
3. The classification granularity and its justification (R-4.11, R-4.12).
4. The evidence pipeline and manifest format.
5. The configuration family the method produces.
6. Known limitations and the conditions under which the method does not apply.

Item 6 is not a formality. A method with no stated limits has not been examined
closely enough to have found them.

---

# 9. Reference method

A method satisfying §§1–8. Adopt, adapt, or replace — but read §9.1 first,
because that part is not a preference.

## 9.1 The doctrine: two criteria, two purposes

| | Static criterion | Dynamic criterion |
|---|---|---|
| Question | What *can* execute? | What *does* execute, how often? |
| Source | Linear sweep of the linked image | Simulator trace |
| Bias | Over-approximates | Under-approximates |
| **Governs** | **Deletion** | **Acceleration and emulation cost** |

**Deletion decisions key off the static criterion only.** Frequency never
justifies removal.

The failure mode is seductive: profile the workload, observe that some
instruction executed zero times, delete it. But zero executions is a property of
the *stimulus*, not of the program. The fault handler that runs on sensor
timeout, the libc path that runs on allocation failure, the RTOS path that runs
on priority inversion — none appear in a healthy profiling run, and all are
reachable. A dynamic-driven deletion produces a chip that passes on the bench
and hangs in flight, months later, at altitude.

The dynamic criterion is essential; it just answers a different question. What
should the accelerator target, and what will emulation cost —
`Σ (dynamic frequency × trap cost)`, computable only from frequency data.

### The over-approximation is deliberate

A linear sweep decodes constant pools, jump tables and alignment padding
alongside real code, inflating the subset. Good: the two errors are not
symmetric. Over-approximating wastes area; under-approximating produces broken
silicon. Bias towards the recoverable error.

Quantify the inflation (R-4.5) via `isaprof`'s undecodable rate, and narrow the
swept regions when it exceeds ~5%.

## 9.2 The three pruning tiers

Each tier independently selectable. The point is not the taxonomy but that it
**separates savings by mechanism**, which is what makes attribution honest
(R-4.19).

### Tier 0 — existing CVA6 knobs, no RTL change

FPU disabled. MMU absent in CV32A6. A-extension disabled. RVFI disabled for the
silicon build. PMP entries reduced to the measured requirement. BTB/BHT/RAS and
I$/D$ resized to the measured working set.

Costs almost nothing to implement, and predicted to **deliver most of the area**
— see [`11-expected-results-and-risks.md`](11-expected-results-and-risks.md).

### Tier 1 — new decoder-level parameters

Unused compressed subsets dropped. `div`/`rem` removed and emulated. Unread
CSRs removed. Multiplier narrowed or made iterative. Unused ALU operations
pruned.

The tier that generates the headline ("we removed 40% of the ISA") and is
predicted to deliver the **least silicon**. Report both facts together.

### Tier 2 — structural

Scoreboard entries reduced. Commit stage simplified toward single-issue.
Misaligned-access support dropped. Unused functional-unit ports collapsed.

Highest effort, highest risk to timing closure, predicted second-largest
contributor after Tier 0.

## 9.3 Granularity and the mismatch problem

Classification granularity is the *instruction*. Implementation granularity is
the *functional unit*. These do not align, which is why R-4.12 exists.

Removing one instruction from a shared unit usually saves nothing — the unit
remains, minus one decoder arm. Savings appear only when an entire unit's
instruction set is removable. So: classify per instruction, then **group by
implementing structure** before predicting savings, and report at group level.

A team that classifies per instruction and predicts savings per instruction will
produce a projection synthesis does not honour, and will not know why.

## 9.4 The harness

A `cva6_slim_config_pkg.sv` layer over CVA6's `config_pkg` / `build_config_pkg`,
exposing `SLIM_*` parameters. Never edit upstream RTL — that breaks the
submodule pin, destroys composability, and voids the equivalence proof against
the baseline.

Every combination buildable, measurable, reversible. The output is not a chip;
it is a **curve**.

## 9.5 Procedure

1. Build Corpus B, including RTOS kernel, ISRs, boot and fault paths.
2. Static sweep every linked image. Union across the corpus → **must-keep set**.
3. Dynamic trace the same corpus → frequency ranking.
4. Complement of the must-keep set → **removal candidates**.
5. Group candidates by implementing structure (§9.3).
6. Per group: estimate saving, estimate emulation cost from step 3, classify as
   *remove*, *remove-and-emulate*, or *retain*.
7. Generate configurations; build; measure; plot.
8. Record every nil result.

Step 8 is not bookkeeping. A results table where every intervention worked reads
as unfalsified.

## 9.6 The reference policy, and why `absent` is not a verdict

`isaprof classify` implements steps 2–4 and 6. Its policy in one sentence:
**reachability decides; frequency prices.** Instructions on the real-time
interrupt path are retained in hardware regardless of the subset, because
emulation cost is incompatible with the determinism claim (R-5.12).

The obvious three-way split — keep / emulate / absent — is wrong. An instruction
outside the static image is outside the *analysed program*, not outside the ISA,
and the part may still meet it: a bring-up test, a third-party binary, a
recompilation after a toolchain upgrade. Labelling it `absent` invites the
reader to conclude nothing needs to handle it. Covering that case is the
compatibility contract's job. **Two verdicts, not three.**

## 9.7 Where this method is weak

Stated because §8 item 6 demands it, and a reference should meet its own bar:

- **Indirect jumps.** A linear sweep bounds what is *in* the image, not what is
  reachable. Computed jumps into data would defeat it — acceptable here only
  because the target is a static, single-application bare-metal image.
- **Externally supplied code.** Any post-fabrication binary not analysed at
  design time is outside the guarantee. The compatibility contract is what makes
  this survivable rather than fatal.
- **Self-modifying code.** Out of scope; state it as an assumption rather than
  assuming it silently.
- **Toolchain drift.** A compiler upgrade can introduce instructions the
  analysis never saw. The pipeline must be re-runnable (R-4.10) and must
  actually be re-run on every toolchain change — a requirement that will be
  forgotten unless it is wired into CI.

---

**Previous:** [`03-core-requirements.md`](03-core-requirements.md) ·
**Next:** [`05-compatibility-requirements.md`](05-compatibility-requirements.md)
