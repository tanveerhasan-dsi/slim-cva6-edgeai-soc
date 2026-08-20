# `sw/`

Software. **Empty by design.**

## Layout

| Directory | What belongs here |
|---|---|
| `bootrom/` | Reset vector, secure boot, handler installation. Must install emulation handlers before any application code runs, and make their presence discoverable at runtime (R-5.18). |
| `emulation/` | The trap-and-emulate handler library — one handler per removed encoding (R-5.1). A linkable library, **never** embedded in a single runtime (R-5.3). |
| `benchmarks/` | Corpus A portable baselines and Corpus B target workload (R-2.15–R-2.17). Corpus B must include the RTOS kernel and every interrupt path (R-2.16). |
| `models/` | Quantised networks with their conversion scripts. Record measured weight **and peak activation** footprints (R-2.6). |

## What makes `emulation/` hard

It is the centre of the project
([`../docs/05-compatibility-requirements.md`](../docs/05-compatibility-requirements.md)),
and three of its requirements are the ones most often discovered late:

| Requirement | Why it bites |
|---|---|
| **Bit-identical side effects**<br>*(R-5.5)* | Producing the right arithmetic result is the easy half. Division by zero, flag updates and CSR effects are where a handler silently diverges from hardware. |
| **Interrupt-context re-entrancy**<br>*(R-5.6)* | After pruning, interrupt handlers will contain emulated instructions. Shared static state in a handler corrupts under nesting, at a rate rare enough to be undebuggable in silicon. |
| **Nested traps**<br>*(R-5.8)* | An emulated load can fault. Rare, therefore usually untested. |

## Build note

> [!IMPORTANT]
> Benchmarks must be built for the **baseline** ISA, not for the pruned subset.
> The point is that pruned hardware still runs unmodified binaries — recompiling
> to avoid removed instructions would test a different and much weaker claim.

---

[`README`](../README.md) · [`docs/05 — Compatibility Requirements`](../docs/05-compatibility-requirements.md)
