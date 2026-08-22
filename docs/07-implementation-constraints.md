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
blocks nothing, and so that results survive whichever choice is made.

| ID | Requirement |
|:--:|---|
| **R-7.1** | Area MUST be reported in a normalised, technology-independent unit and as percentage deltas against the stated baseline. |
| **R-7.2** | Absolute figures MAY be reported additionally, always alongside the normalised form. |
| **R-7.3** | Power MUST be reported as relative improvement, with the operating point stated. |
| **R-7.4** | Every measurement MUST record the technology, corner, tool versions and constraints it was taken under. |
| **R-7.5** | The flow MUST be structured so that a PDK change requires configuration changes only, not methodology changes. |

> **On R-7.1.** A percentage reduction is comparable across nodes and survives a
> PDK switch mid-project; a raw absolute figure is neither.

---

## 2. Open and closed data

| ID | Requirement |
|:--:|---|
| **R-7.6** | If a PDK under NDA is selected, the repository MUST maintain a clean split, with no PDK-derived data in the public repository. |
| **R-7.7** | The split MUST be enforced mechanically, not by convention. |
| **R-7.8** | Public results MUST remain complete enough to stand alone. |
| **R-7.9** | Any figure that cannot be published MUST be identified as withheld rather than silently omitted. |

> [!WARNING]
> **On R-7.7.** "Everyone knows not to commit that" fails eventually, and the
> failure mode is an NDA breach that cannot be undone by a later commit.

---

## 3. Technology selection

Not yet decided. When it is, record the reasoning — including the options
rejected — because reviewers will ask.

| ID | Requirement |
|:--:|---|
| **R-7.10** | Node selection MUST be justified against the memory budget, the die-area budget and the target operating frequency. |
| **R-7.11** | Feasibility MUST be confirmed by trial synthesis and a floorplan estimate before commitment. |
| **R-7.12** | Memory macro availability and density MUST be confirmed for the chosen node before the memory budget is frozen. |

> **On R-7.11 and R-7.12.** An older, cheaper, more open node is attractive, but
> density is low and memory macros are large — a design comfortable at one node
> can simply fail to fit at another. Confirm the memory fits the node before
> designing around a memory budget, because memory, not logic, usually decides
> the die.

---

## 4. Physical design

| ID | Requirement |
|:--:|---|
| **R-7.13** | The flow MUST be scripted and reproducible; no manual steps in the signoff path. |
| **R-7.14** | Every configuration MUST run through the same flow with the same constraints. |
| **R-7.15** | Floorplan, power grid and pad ring MUST be documented. |
| **R-7.16** | Power domains and isolation for the duty-cycled domain MUST be verified, including wake and sleep transitions. |
| **R-7.17** | Clock domain crossings MUST be identified and verified. |

> **On R-7.14.** If configurations run through different flows or constraints,
> the comparison between them measures the flow rather than the design — and the
> PPA curve is the project's primary figure.

> **On R-7.16.** Power gating is where duty-cycled designs fail on silicon.
> Verify the transitions, not only the steady states: a domain that works awake
> and works asleep can still corrupt state on the boundary between them.

---

## 5. FPGA prototype

| ID | Requirement |
|:--:|---|
| **R-7.18** | An FPGA prototype MUST support the full application with real sensors. |
| **R-7.19** | The prototype MUST be buildable from the same RTL configuration as the ASIC target, differing only where technology forces it. |
| **R-7.20** | Divergences between prototype and ASIC configurations MUST be enumerated and justified. |

> **On R-7.19 and R-7.20.** Prototype-only divergence is how a bug reaches
> silicon: the thing you verified is not the thing you fabricated. Some
> divergence is unavoidable, so enumerate it and treat each item as unverified
> by the prototype.

---

## 6. Manifest

| ID | Requirement |
|:--:|---|
| **R-7.21** | Every reported result MUST be regenerable from a committed manifest. |
| **R-7.22** | The manifest MUST be produced automatically by the flow, not maintained by hand. |

> **On R-7.22.** Hand-maintained manifests drift from reality, and they drift
> silently — which is worse than having none, because they are trusted.

---

| ← Previous | Index | Next → |
|---|:---:|---|
| [`06 — Verification Requirements`](06-verification-requirements.md) | [`README`](../README.md) | [`08 — Deliverables`](08-deliverables.md) |
