# `rtl/`

Hardware description. **Empty by design** — the contents follow from the
methodology in
[`../docs/04-methodology-requirements.md`](../docs/04-methodology-requirements.md),
which has not been written yet.

| Directory | What belongs here |
|---|---|
| `cva6/` | Upstream CVA6, as a git submodule. Pinned commit recorded in the manifest (R-1.3). Do not vendor a copy, and do not edit in place. |
| `slim-config/` | The pruning harness: configuration layered over the core's existing parameter mechanism. One file per configuration in the family. |
| `xtinyml/` | The TinyML coprocessor: interface adapter, decoder, datapath, buffers. |
| `soc/` | Top level: interconnect, memory, peripherals, clock and reset, power domains, pad ring. |

## Constraints that shape what goes here

> [!WARNING]
> **Pruning is configuration, not deletion** (R-3.4). Changes go in
> `slim-config/`, layered over upstream. Editing `cva6/` breaks the submodule
> pin, makes configurations non-composable, and makes formal equivalence against
> the baseline meaningless — the three properties the study rests on.

- Every configuration builds standalone (R-3.5) and is reversible by
  configuration change alone (R-3.7).
- The core builds with the coprocessor absent (R-3.17), so the pruning result
  and the accelerator result stay separately attributable.

Record the upstream commit in the manifest before the first commit, and start
from current upstream — the repository was restructured, and older checkouts do
not match current documentation.

---

[`README`](../README.md) · [`docs/03 — Core Requirements`](../docs/03-core-requirements.md)
