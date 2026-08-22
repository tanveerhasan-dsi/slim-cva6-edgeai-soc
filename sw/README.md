# `sw/`

Software. **Empty by design.**

| Directory | What belongs here |
|---|---|
| `bootrom/` | Reset vector, secure boot, handler installation. Handlers must be installed before any application code runs, and their presence discoverable at runtime (R-5.18). |
| `emulation/` | The trap-and-emulate handler library — one handler per removed encoding (R-5.1), as a linkable library rather than embedded in a runtime (R-5.3). |
| `benchmarks/` | Both workload corpora (R-2.15–R-2.17). The target corpus must include the kernel and every interrupt path (R-2.16). |
| `models/` | Quantised networks with their conversion scripts. Record measured weight **and peak activation** footprints (R-2.6). |

## What makes `emulation/` hard

It is the centre of the project
([`../docs/05-compatibility-requirements.md`](../docs/05-compatibility-requirements.md)),
and three of its requirements are the ones most often discovered late:

| Requirement | Why it bites |
|---|---|
| Bit-identical side effects *(R-5.5)* | The arithmetic is the easy half; the architecturally specified edge cases are where a handler silently diverges. |
| Interrupt-context re-entrancy *(R-5.6)* | After pruning, interrupt handlers contain emulated instructions. Shared static state corrupts under nesting, at a rate rare enough to be undebuggable in silicon. |
| Nested traps *(R-5.8)* | An emulated load can fault. Rare, therefore usually untested. |

## Build note

Benchmarks are built for the **baseline** ISA, not the pruned subset. The point
is that pruned hardware still runs unmodified binaries; recompiling to avoid
removed instructions would test a different and much weaker claim.

---

[`README`](../README.md) · [`docs/05 — Compatibility Requirements`](../docs/05-compatibility-requirements.md)
