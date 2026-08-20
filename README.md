<!-- Project charter. Requirements state what must be true of the result;
     reference sections state one way to achieve it. Keep the two labelled. -->

<div align="center">

# CARVE-V

### Core Area Reduction by Verified Elimination

**A workload-driven ISA subsetting flow for CVA6, taped out as an always-on micro-UAV perception SoC.**

[![Licence: Apache-2.0](https://img.shields.io/badge/docs%20%26%20tools-Apache--2.0-blue.svg)](LICENSE)
[![RTL: SHL-2.1](https://img.shields.io/badge/RTL-Solderpad%202.1-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](tools/isaprof/)
[![isaprof: 46 tests, zero deps](https://img.shields.io/badge/isaprof-46%20tests%20%C2%B7%20zero%20deps-brightgreen.svg)](tools/isaprof/)
[![Core: CV32A6](https://img.shields.io/badge/core-CVA6%20%C2%B7%20CV32A6-orange.svg)](https://github.com/openhwgroup/cva6)
[![Status: specification](https://img.shields.io/badge/status-specification-lightgrey.svg)](docs/)

</div>

> [!IMPORTANT]
> **How to read this repository.** Each document carries **requirements**
> (numbered `R-n.m`, stating what must be true) followed by a **reference
> design** section (stating one way to satisfy them). Where the team has
> measured data and the reference has estimates, the team's judgement wins.
>
> Two things are **not** open to revision:
>
> 1. the deletion criterion in [`04`](docs/04-methodology-requirements.md) §2, and
> 2. the compatibility obligation in [`05`](docs/05-compatibility-requirements.md) §1.
>
> Both fail in silicon, where nothing can be fixed.

---

## Contents

- [The one-sentence thesis](#the-one-sentence-thesis)
- [The trap this project is designed to avoid](#the-trap-this-project-is-designed-to-avoid)
- [The chip](#the-chip)
- [What is in this repository](#what-is-in-this-repository)
- [Start here](#start-here)
- [First deliverable](#first-deliverable)
- [Two facts worth knowing before you start](#two-facts-worth-knowing-before-you-start)
- [Licence](#licence)

---

## The one-sentence thesis

> Remove a large fraction of the implemented ISA from CVA6; prove the pruned
> core functionally equivalent on the surviving subset; retain full binary
> compatibility through trap-and-emulate; and spend the reclaimed silicon on a
> TinyML datapath — netting materially better inference energy in the same die
> area.

**Subtract, then reinvest.** Both halves are required. That is what separates
this from a configuration change.

---

## The trap this project is designed to avoid

"Disable the FPU and re-synthesise" is a week of work. It produces a smaller
core, a plausible graph, and one unanswerable question at review:

> [!CAUTION]
> *Why didn't you just use Ibex, or X-HEEP? They're already small.*

There is no good answer to that if the contribution is a config file. So the
contribution here is not the smaller core — it is the **automated, verified,
compatibility-preserving flow** that produces it, and the demonstration that the
reclaimed area buys something worth having.

Three things follow from that, and they are the requirements that matter:

| # | Requirement that matters | Why |
|:--:|---|---|
| **1** | **Deletion must be driven by measured evidence**, not by which blocks look large | Any team can name the FPU. The long tail — which base integer opcodes, which CSRs, which compressed subsets — is where a method is needed, and where intuition silently fails. |
| **2** | **Removed instructions must keep working** | Every deleted encoding gets an M-mode emulation handler, so the part still passes architectural compliance with handlers installed. A chip that is smaller *and* still runs the binaries is a result; a chip that is smaller because it runs less is a configuration. |
| **3** | **Every pruning step must be formally equivalence-checked** against the baseline | This is the standard for silicon you are paying to fabricate, as opposed to silicon you are simulating. |

---

## The chip

An always-on autonomous micro-UAV perception node: obstacle avoidance from
**mmWave radar** point clouds, plus airframe health monitoring from IMU and
acoustic vibration.

```mermaid
flowchart TD
    SENS["Radar / IMU / mic<br/>SPI, I2S"]
    AO["ALWAYS-ON DOMAIN — uW class<br/>front-end + trigger detect<br/>never gated"]
    CORE["SLIM CVA6 (CV32A6)<br/>pruned to the measured subset"]
    ML["Xtinyml DATAPATH<br/>weight-stationary<br/>INT8 / INT4 array"]
    MEM["ON-CHIP SRAM ONLY<br/>weights + activations + code + data"]
    PWM(["PWM to motors"])

    SENS --> AO
    AO -->|wake| CORE
    CORE <-->|"CV-X-IF (execute stage)"| ML
    CORE --> MEM
    ML --> MEM
    CORE --> PWM

    linkStyle 1 stroke-width:2px
```

The application is not decoration. It is what makes each deletion *arguable
from the workload* rather than from taste — the point a reviewer will press
hardest:

| Property of the workload | What it licenses |
|---|---|
| Models are int8/int4-quantised end to end | **No floating point needed** |
| Flight control needs deterministic loop latency | **The MMU is a liability**, not merely unused — page-walk and TLB-miss jitter are disqualifying |
| Single application, single core | **No virtual memory, no atomics** |
| Radar and IMU networks fit in a few hundred kilobytes | **No DRAM controller and no DRAM PHY** |
| SPI-rate sensor ingest | **No MIPI PHY** |

The last two omissions are what keep this inside a university MPW.

> [!NOTE]
> That last point is load-bearing. Camera-class vision would need multiple
> megabytes of weights and a MIPI PHY, and both are outside reach for a first
> tapeout. **Choosing radar is what makes the arithmetic close.**

---

## What is in this repository

| Path | What it is |
|---|---|
| [`docs/`](docs/) | Requirements, reference design, acceptance criteria, recorded predictions |
| [`tools/isaprof/`](tools/isaprof/) | **Working.** Measurement and the reference policy, zero dependencies |
| [`rtl/`](rtl/) [`sw/`](sw/) [`verif/`](verif/) [`flow/`](flow/) | Scaffolding — each directory states what belongs in it |

### Documents

| № | Document | Requirements | Reference design |
|:--:|---|---|---|
| **00** | [Problem statement](docs/00-problem-statement.md) | The problem, prior art, novelty claim | — |
| **01** | [Objectives and scope](docs/01-objectives-and-scope.md) | Objectives, scope, core target | — |
| **02** | [Application requirements](docs/02-application-requirements.md) | The SoC and its workload | §9 Architecture |
| **03** | [Core requirements](docs/03-core-requirements.md) | Core, pruning harness, reinvestment | §7 Xtinyml datapath |
| **04** | [Methodology requirements](docs/04-methodology-requirements.md) | **The deletion criterion** | §9 Subsetting method |
| **05** | [Compatibility requirements](docs/05-compatibility-requirements.md) | **The ISA contract** | §7 Contract design |
| **06** | [Verification requirements](docs/06-verification-requirements.md) | Compliance, cosim, formal, CI | §9 Verification strategy |
| **07** | [Implementation constraints](docs/07-implementation-constraints.md) | PDK-agnostic reporting | — |
| **08** | [Deliverables](docs/08-deliverables.md) | Artifacts and their dependencies | — |
| **09** | [Acceptance criteria](docs/09-acceptance-criteria.md) | How the work is judged | — |
| **10** | [References](docs/10-references.md) | Annotated bibliography | — |
| **11** | [Expected results and risks](docs/11-expected-results-and-risks.md) | — | Predictions and risks |

---

## Start here

The instrument runs immediately: **no toolchain, no `pip install`, no PDK.**

```bash
cd tools/isaprof
python3 -m unittest discover -s tests -t .

python3 -m isaprof static  tests/fixtures/sample.elf      --json s.json
python3 -m isaprof dynamic tests/fixtures/spike_trace.log --json d.json
python3 -m isaprof classify s.json d.json -o subset.json
python3 -m isaprof report   s.json d.json -o report.md
```

Then read, in order:

[`00`](docs/00-problem-statement.md) →
[`01`](docs/01-objectives-and-scope.md) →
[`02`](docs/02-application-requirements.md) →
[`09`](docs/09-acceptance-criteria.md)

---

## First deliverable

A **subsetting methodology** satisfying
[`docs/04`](docs/04-methodology-requirements.md) §§1–8, supported by an
`isaprof` run over Corpus B.

§9 of that document gives a reference method that satisfies those requirements,
and `isaprof classify` implements its policy. Adopting it unmodified is
permitted — but it is a *decision* that must be stated and its assumptions
checked against your actual workload ([R-4.22](docs/04-methodology-requirements.md#7-the-instrument)),
not a default to inherit silently.

> [!TIP]
> **Before reading [`11`](docs/11-expected-results-and-risks.md), write down your
> own predictions.** Published predictions anchor. D-11 asks how they fared, and
> that question is only answerable if yours were committed independently.

---

## Two facts worth knowing before you start

> [!WARNING]
> **Do not begin from a stale CVA6.** CVA6 was restructured substantially; a
> checkout predating the `core/` layout and `config_pkg` will not match any
> current documentation. Start from current upstream and record the commit.

> [!WARNING]
> **Two popular "removals" remove nothing.** The hypervisor extension is gated
> behind `CVA6Cfg.RVH`, defaults to `0`, is CV64-only, and is still maturing — a
> default build has no H-extension logic to strip. Likewise, CVA6 has no L2 in
> the core, so "remove L2 coherence" is not a saving; coherence appears only in
> the OpenPiton configuration. Claiming area from either will not survive review.

---

## Licence

Apache-2.0 for documentation and tooling; Solderpad Hardware Licence 2.1 for
RTL. See [`LICENSE`](LICENSE).

---

<div align="center">

**[Documents](docs/) · [Contributing](CONTRIBUTING.md) · [isaprof](tools/isaprof/)**

</div>
