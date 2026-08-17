# 01 — Objectives and Scope

## 1. Requirement language

**MUST** — mandatory; failing it fails the acceptance criteria.
**SHOULD** — expected; a deviation must be recorded with its rationale.
**MAY** — permitted; no justification needed either way.

Every requirement is identified (`R-n.m`) and referenced from
[`09-acceptance-criteria.md`](09-acceptance-criteria.md).

## 2. Objectives

| | Objective |
|---|---|
| **O-1** | Establish a reproducible method for deriving an instruction subset from a target workload, with a deletion criterion that is provably conservative. |
| **O-2** | Produce a parameterised family of pruned CVA6 configurations, each independently buildable and measurable. |
| **O-3** | Preserve the software contract: every removed encoding remains executable via emulation, at a measured cost. |
| **O-4** | Prove each pruned configuration equivalent to the baseline on the surviving subset. |
| **O-5** | Reinvest reclaimed area in a TinyML datapath and measure the resulting energy improvement. |
| **O-6** | Carry one configuration through to a fabricated, measured test chip. |

O-1 through O-4 are the research contribution. O-5 makes it worth doing. O-6
makes it real.

## 3. In scope

- The CVA6 core: decode, execute, control and status registers, cache and
  predictor sizing.
- A CV-X-IF-attached TinyML coprocessor.
- SoC integration: interconnect, on-chip memory, peripherals, clocking, reset,
  and power domains.
- Software: boot ROM, emulation handlers, RTOS bring-up, quantised inference
  runtime.
- Verification: architectural compliance, co-simulation, formal equivalence.
- Physical implementation through to signoff and an MPW submission.

## 4. Out of scope

Stated explicitly, because each has consumed university tapeouts before:

- **Custom analogue or mixed-signal IP.** No DRAM PHY, no MIPI PHY, no PLL
  design, no ADC. Hard macros are integrated as vendor IP or omitted.
- **Off-chip DRAM.** The memory budget is on-chip SRAM. See R-2.4.
- **Multi-core and cache coherence.** Single hart.
- **Linux.** Bare-metal and RTOS only for the tapeout configuration.
- **A new ISA extension proposal to RISC-V International.** Custom instructions
  live in the custom opcode space and stay there.
- **Silicon-proven radiation, automotive or safety certification.**

## 5. Core target

| ID | Requirement |
|---|---|
| **R-1.1** | The tapeout configuration MUST be 32-bit (CV32A6 class). |
| **R-1.2** | A 64-bit configuration MUST be maintained through the same pruning harness as a scaling study, reporting how pruning yield varies with XLEN. It is not taped out. |
| **R-1.3** | Work MUST start from a current upstream CVA6, and the exact commit MUST be recorded in the build manifest. |

**On R-1.1.** A 64-bit datapath, register file and ALU cost real area, and an
address space of a few hundred kilobytes cannot use any of it. Choosing RV64
for a device of this class spends a large part of the FPU and MMU savings before
any pruning begins. R-1.2 exists so that this claim is *measured* rather than
assumed — the scaling study is what turns a design preference into a result.

**On R-1.3.** CVA6 was restructured substantially; checkouts predating the
`core/` layout and `config_pkg` do not match current documentation and will
silently waste weeks.

## 6. Constraints that shape everything else

| ID | Constraint |
|---|---|
| **R-1.4** | All PPA figures MUST be reported PDK-agnostically — normalised gate-equivalents and percentage deltas — so results remain publishable whatever PDK is chosen. |
| **R-1.5** | If a PDK under NDA is selected, the repository MUST maintain a clean open/closed split; no PDK-derived data enters the public repository. |
| **R-1.6** | Every reported number MUST be reproducible from a committed manifest: source commit, configuration, tool versions, and command line. |

**On R-1.6.** This is the requirement that most often gets skipped and most
often costs a paper. A number nobody can regenerate six months later is not a
result, and on a project whose entire claim is methodological, an
irreproducible measurement undermines the contribution rather than supporting it.

---

**Previous:** [`00-problem-statement.md`](00-problem-statement.md) ·
**Next:** [`02-application-requirements.md`](02-application-requirements.md)
