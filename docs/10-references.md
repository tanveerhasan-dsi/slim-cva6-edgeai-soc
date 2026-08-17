# 10 — References

Annotated. Read the annotation before citing — several of these are routinely
cited for claims they do not make.

## CVA6

- **[CVA6 user manual](https://docs.openhwgroup.org/projects/cva6-user-manual/)**
  — the authoritative source. Parameters, configurations, design documents.
- **[Parameters and Configuration](https://docs.openhwgroup.org/projects/cva6-user-manual/01_cva6_user/Parameters_Configuration.html)**
  — start here for the pruning harness. `config_pkg` / `build_config_pkg` are
  the mechanism R-3.4 requires you to build on.
- **[CV32A65X design document](https://docs.openhwgroup.org/projects/cva6-user-manual/04_cv32a65x/design/design.html)**
  and **[CV32A60X](https://docs.openhwgroup.org/projects/cva6-user-manual/07_cv32a60x/design/design.html)**
  — the 32-bit configurations closest to the tapeout target.
- **[openhwgroup/cva6](https://github.com/openhwgroup/cva6)** — upstream.
  Note R-1.3: start from current upstream. The repository was restructured;
  anything predating the `core/` layout and `config_pkg` will not match the
  documentation above.

> **Caution.** `CVA6Cfg.RVH` (hypervisor) defaults to `0`, is CV64-only, and is
> still maturing. A default CV32 build has no H-extension logic to remove.
> Similarly, CVA6 has no L2 in the core — coherence appears only in the
> OpenPiton configuration. See [`03`](03-core-requirements.md) §4.

## CV-X-IF

- **[CV-X-IF specification](https://docs.openhwgroup.org/projects/openhw-group-core-v-xif/en/latest/intro.html)**
  — the interface itself.
- **[CV-X-IF in CVA6](https://docs.openhwgroup.org/projects/cva6-user-manual/01_cva6_user/CVX_Interface_Coprocessor.html)**
  — CVA6 implements the five mandatory interfaces (compressed, issue, register,
  commit, result); the coprocessor sits in the execute stage. The memory
  interfaces are optional and **not** implemented — check this against your
  datapath's requirements early.
- **[Custom instructions in CVA6](https://cva6.readthedocs.io/en/latest/01_cva6_user/Custom_Instructions.html)**

## Berkeley methodology

- **[Chipyard](https://github.com/ucb-bar/chipyard)** ·
  **[SLICE Lab](https://slice.eecs.berkeley.edu/projects/chipyard/)** ·
  **[Components](https://chipyard.readthedocs.io/en/latest/Chipyard-Basics/Chipyard-Components.html)**
  — CVA6 is an integrated core option, so a slim CVA6 can use this flow.
- **[NeCTAr](https://arxiv.org/html/2503.14708v1)** — heterogeneous RISC-V SoC
  in Intel 16: 4 mm², 320 kB SRAM, 400 MHz at 0.85 V, 132 GOPS/W, concept to
  tapeout in one semester-long class. Cite as the **feasibility precedent** for
  a university tapeout — not as prior art on ISA subsetting, which it is not.

## ISA subsetting

- **[Flexing RISC-V Instruction Subset Processors to Extreme Edge](https://arxiv.org/pdf/2505.04567)**
  — the closest prior work, and the one to distinguish yourself from carefully.
  Establishes that applications use 6–32 distinct instructions (geomean 18),
  31–84% of RV32E. Targets tiny cores; does **not** preserve binary
  compatibility; does **not** formally verify the pruning.
- **Property-driven automatic generation of reduced component hardware** (US
  patent 12437133) — read before claiming novelty on automation alone.

## Compatibility

- **[Trap-and-emulate for hardware forward-compatibility](https://lists.riscv.org/g/tech-profiles/topic/101153812)**
  — RISC-V tech-profiles discussion. Useful for the honest framing: trap-and-
  emulate is a compatibility mechanism with real and sometimes severe cost, not
  a free equivalence.
- **[riscv-atomic-emulation-trap](https://github.com/esp-rs/riscv-atomic-emulation-trap)**
  — a working handler for atomics on cores without the A extension. The nearest
  existing model for [`05`](05-compatibility-requirements.md).
- **[RISC-V unprivileged specification](https://docs.riscv.org/reference/isa/v20260120/unpriv/intro.html)**
  — the normative source for the bit-identical requirement in R-5.4.

## Benchmarks

- **[MLPerf Tiny](https://mlcommons.org/2026/07/mlperf-tiny-v1-4-results/)** ·
  **[rules](https://github.com/mlcommons/tiny/blob/master/benchmark/MLPerfTiny_Rules.adoc)**
  — Corpus A portable baselines. Follow the closed-division rules if you intend
  the numbers to be comparable.
- **Embench-IoT** — embedded integer benchmarks, better suited to this class of
  device than CoreMark.
- **CoreMark** — include for comparability. Note R-6.1: it is a smoke test, not
  a gate.

## Comparison baselines

- **[Ibex](https://github.com/lowRISC/ibex)** — small, production-quality 32-bit
  core. The direct answer to *why not just use a small core*, so measure it
  rather than arguing about it.
- **[X-HEEP](https://arxiv.org/pdf/2401.05548)** — configurable ultra-low-power
  RISC-V microcontroller for edge accelerator exploration. The closest existing
  system to this project's target, and therefore the most important baseline.

## Verification

- **[RISCOF](https://github.com/riscv-software-src/riscof)** — the compliance
  framework for R-5.13 and R-6.11.
- **[riscv-arch-test](https://github.com/riscv-non-isa/riscv-arch-test)** — the
  architectural test suite.
- **[core-v-verif](https://github.com/openhwgroup/core-v-verif)** — the CVA6
  verification environment, including RVFI-based co-simulation.
- **[SymbiYosys](https://github.com/YosysHQ/sby)** — open formal flow, if a
  commercial equivalence checker is unavailable.

---

**Previous:** [`09-acceptance-criteria.md`](09-acceptance-criteria.md) ·
**Next:** [`11-expected-results-and-risks.md`](11-expected-results-and-risks.md)
