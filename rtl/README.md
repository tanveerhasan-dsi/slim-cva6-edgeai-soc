# rtl/

Hardware description. Empty by design — the contents follow from the
methodology in [`../docs/04-methodology-requirements.md`](../docs/04-methodology-requirements.md),
which has not been written yet.

| Directory | What belongs here |
|---|---|
| `cva6/` | Upstream CVA6, as a git submodule. Pinned commit recorded in the manifest (R-1.3). Do not vendor a copy, and do not edit in place. |
| `slim-config/` | The pruning harness: parameter packages layered over CVA6's `config_pkg` / `build_config_pkg`. One file per configuration in the family. |
| `xtinyml/` | The CV-X-IF coprocessor: interface adapter, decoder, datapath, buffers. |
| `soc/` | Top level: interconnect, memory, peripherals, clock and reset, power domains, pad ring. |

## Constraints that shape what goes here

**Pruning is parameterisation, not deletion** (R-3.4). Changes go in
`slim-config/`, layered over upstream. Editing `cva6/` breaks the submodule
pin, makes configurations non-composable, and makes formal equivalence against
the baseline meaningless — the three properties the whole study rests on.

**Every configuration must build standalone** (R-3.5) and be **reversible by
parameter change alone** (R-3.7).

**The core must build with `xtinyml/` absent** (R-3.17), so the pruning result
and the accelerator result stay separately attributable.

## Before the first commit

Record the upstream CVA6 commit in the manifest. Start from current upstream —
the repository was restructured, and a checkout predating the `core/` layout
and `config_pkg` will not match any current documentation.
