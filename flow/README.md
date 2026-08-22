# `flow/`

Physical implementation. **Empty by design**, and PDK-agnostic until a
technology is selected.

| Directory | What belongs here |
|---|---|
| `synth/` | Synthesis scripts and constraints. Identical across every configuration (R-7.14). |
| `pnr/` | Place-and-route, floorplan, power grid, pad ring. Scripted end to end (R-7.13). |
| `fpga/` | Prototype build. Same RTL configuration as the ASIC target, differing only where technology forces it (R-7.19). |

## The rule that makes the results mean anything

Every configuration runs the same flow with the same constraints (R-7.14). If
configurations differ in flow or constraints, the PPA curve measures the flow
rather than the design — and the curve is the project's primary figure.

## Reporting

Normalised, technology-independent units and percentage deltas (R-7.1).
Absolute figures only alongside the normalised form (R-7.2). This is what lets
results survive a PDK change mid-project.

## If a PDK under NDA is selected

> [!WARNING]
> The open/closed split is enforced mechanically, not by convention (R-7.7).
> "Everyone knows not to commit that" fails eventually, and that particular
> failure cannot be undone by a later commit.

Withheld figures are marked as withheld, never silently omitted (R-7.9).

## Before committing to a node

Confirm memory macro availability and density first (R-7.12), then trial-
synthesise and floorplan (R-7.11). Memory, not logic, usually decides the die.

---

[`README`](../README.md) · [`docs/07 — Implementation Constraints`](../docs/07-implementation-constraints.md)
