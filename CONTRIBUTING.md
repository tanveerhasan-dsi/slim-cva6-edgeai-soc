# Contributing

## Before anything else

Read [`docs/04-methodology-requirements.md`](docs/04-methodology-requirements.md).
Every RTL change traces back to a criterion stated there. If the methodology
document does not exist yet, writing it is the work — not the RTL.

## What every change must carry

| Change | Must include |
|---|---|
| A pruning configuration | The criterion it traces to (R-3.9), a build, and a measured delta — **including when the delta is nil** (R-3.12) |
| An RTL change | Regression pass, co-simulation pass, and re-established formal equivalence (R-6.10) |
| An emulation handler | Reference-model verification, cost measurement, re-entrancy and nested-trap tests (R-5.4–R-5.8) |
| A measurement | A manifest entry sufficient to regenerate it (R-1.6, R-7.21) |
| A tool change | Tests. `tools/isaprof` runs `python3 -m unittest discover -s tests -t .` |

## Rules that are not style preferences

**Never edit `rtl/cva6/` in place.** It is a pinned submodule. Pruning is
parameterisation layered in `rtl/slim-config/` (R-3.4). Editing upstream breaks
the pin, makes configurations non-composable, and makes equivalence against the
baseline meaningless.

**Never commit PDK-derived data.** Not library files, not extracted parasitics,
not absolute area figures from an NDA PDK. See R-7.6–R-7.9. This one cannot be
undone by a later commit.

**Report nil results.** A configuration that saved nothing is a finding
(R-4.18). A results table where every intervention succeeded reads as
unfalsified, not as strong.

## Measurement discipline

Every configuration is measured under identical flow, constraints and tool
versions (R-4.16, R-7.14). If you change the flow, re-measure everything —
a mixed results table is worse than no table, because it looks like a
measurement of the design when it is a measurement of the flow.

Attribute savings to the correct cause (R-4.19). If a configuration both shrinks
a cache and removes an extension, the delta belongs to both. Reporting the total
under the ISA heading overstates the result the project is actually claiming.

## Predictions

Record predictions **before** measuring, in a committed file, and leave them
unchanged afterwards.

The disagreements are the most informative part of the work. On a project whose
contribution is a method, evidence that the method could surprise its authors is
what makes it credible.

## Measurement and policy stay separate in `tools/isaprof`

`static.py` and `dynamic.py` measure; `classify.py` judges. A test enforces the
separation (`TestMeasurementPolicySeparation`), and it is not a formality: the
policy is expected to be replaced, and replacing it must not require touching
the measurement passes.

If you change the policy, say so in the methodology document too. A policy that
drifts in code while the documented method stays still is worse than either — it
looks argued-about when it is not.

## Commits

State what changed and why, and reference the requirement ID where one applies.
For measurements, include enough for someone else to regenerate the number.
