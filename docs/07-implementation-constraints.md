# 07 — Implementation Constraints

**Contents:**
[1. PDK-agnostic reporting](#1-pdk-agnostic-reporting) ·
[2. Open and closed data](#2-open-and-closed-data) ·
[3. Technology selection](#3-technology-selection) ·
[4. Physical design](#4-physical-design) ·
[5. FPGA prototype](#5-fpga-prototype) ·
[6. Manifest](#6-manifest)

---

## 1. PDK-agnostic reporting

The target PDK is not yet selected. The specification is written so that this
does not block anything, and so that results survive whichever choice is made.

| ID | Requirement |
|:--:|---|
| **R-7.1** | Area MUST be reported in normalised gate-equivalents and as percentage deltas against the stated baseline. |
| **R-7.2** | Absolute figures MAY be reported additionally, always alongside the normalised form. |
| **R-7.3** | Power MUST be reported as relative improvement, with the operating point stated. |
| **R-7.4** | Every measurement MUST record PDK, library corner, tool versions and constraints. |
| **R-7.5** | The flow MUST be structured so that a PDK change requires configuration changes only, not methodology changes. |

> **On R-7.1.** Normalised reporting is what makes the result portable. A
> percentage reduction is comparable across nodes and survives a PDK switch
> mid-project; a raw µm² figure is neither, and re-deriving a whole results
> section after a PDK change is a real and avoidable cost.

---

## 2. Open and closed data

| ID | Requirement |
|:--:|---|
| **R-7.6** | If a PDK under NDA is selected, the repository MUST maintain a clean split, with no PDK-derived data in the public repository. |
| **R-7.7** | The split MUST be enforced mechanically — directory boundaries and CI checks — not by convention. |
| **R-7.8** | Public results MUST remain complete enough to stand alone: normalised deltas and curves, without absolute figures if necessary. |
| **R-7.9** | Any figure that cannot be published MUST be identified as withheld rather than silently omitted. |

> [!CAUTION]
> **On R-7.7.** "Everyone knows not to commit that" fails eventually, and the
> failure mode is an **NDA breach that cannot be undone by a later commit**.
> Directory boundaries and a CI check are cheap; a leak is not.

---

## 3. Technology selection

Not yet decided. When it is, record the reasoning — including the options
rejected — because reviewers will ask why.

| ID | Requirement |
|:--:|---|
| **R-7.10** | Node selection MUST be justified against the SRAM budget from R-2.4, the die-area budget, and the target operating frequency. |
| **R-7.11** | Feasibility MUST be confirmed by trial synthesis and a floorplan estimate **before** commitment. |
| **R-7.12** | SRAM macro availability and density MUST be confirmed for the chosen node before the memory budget is frozen. |

> [!WARNING]
> **On R-7.11 and R-7.12.** A mature open PDK at 130 nm is attractive for openness
> and cost, but density is low and SRAM macros are large — a design comfortable at
> 65 nm can simply fail to fit. **The order matters:** confirm the memory fits the
> node before designing around a memory budget, because SRAM, not logic, is what
> usually decides the die.

---

## 4. Physical design

| ID | Requirement |
|:--:|---|
| **R-7.13** | The flow MUST be scripted and reproducible; no manual GUI steps in the signoff path. |
| **R-7.14** | Every configuration MUST run through the same flow with the same constraints. |
| **R-7.15** | Floorplan, power grid and pad ring MUST be documented. |
| **R-7.16** | Power domains and isolation for the duty-cycled compute domain MUST be verified, including wake and sleep transitions. |
| **R-7.17** | Clock domain crossings MUST be identified and verified. |

> [!IMPORTANT]
> **On R-7.14.** If configurations run through different flows or constraints, the
> comparison between them is not a measurement of the design — it is a
> measurement of the flow. The entire PPA curve depends on this being held fixed.

> [!WARNING]
> **On R-7.16.** Power gating is where duty-cycled designs fail on silicon:
> retention, isolation, and the wake sequence. Verify the *transitions*, not only
> the steady states — a domain that works awake and works asleep can still corrupt
> state on the boundary between them.

---

## 5. FPGA prototype

| ID | Requirement |
|:--:|---|
| **R-7.18** | An FPGA prototype MUST support the full application with real sensors. |
| **R-7.19** | The prototype MUST be buildable from the same RTL configuration as the ASIC target, differing only in technology mapping and memory instantiation. |
| **R-7.20** | Divergences between prototype and ASIC configurations MUST be enumerated and justified. |

> [!CAUTION]
> **On R-7.19 and R-7.20.** Prototype-only divergence is how a bug reaches
> silicon: *the thing you verified is not the thing you fabricated.* Some
> divergence is unavoidable — memories especially — so enumerate it, and treat
> each item as unverified by the prototype.

---

## 6. Manifest

| ID | Requirement |
|:--:|---|
| **R-7.21** | Every reported result MUST be regenerable from a committed manifest recording source commits, configuration, tool versions, constraints and command lines. |
| **R-7.22** | The manifest MUST be produced automatically by the flow, not maintained by hand. |

> [!WARNING]
> **On R-7.22.** Hand-maintained manifests drift from reality, and they drift
> *silently* — which is worse than having none, because they are trusted.
> **Generate it.**

---

| ← Previous | Index | Next → |
|---|:---:|---|
| [`06 — Verification Requirements`](06-verification-requirements.md) | [`README`](../README.md) | [`08 — Deliverables`](08-deliverables.md) |
