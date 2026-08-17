"""The reference classification policy.

Kept in its own module, separate from `static.py` and `dynamic.py`, because the
distinction matters: those two measure, and this one *judges*. Measurements are
facts about a binary; a classification is a design decision with assumptions
baked into it. Replacing the policy must never require touching the measurement.

The policy in one sentence: **reachability decides, frequency prices.**

  * An instruction present in the linked image must be supported by the part --
    in hardware, or in software via a handler.
  * An instruction reachable but never observed executing is a candidate for
    removal *from hardware*, never from the part.
  * Instructions on the real-time interrupt path stay in hardware regardless,
    because emulation cost is incompatible with the determinism claim (R-5.12).

See docs/04-methodology-requirements.md section 9 for the reasoning, and R-4.22:
using this policy unmodified is a decision that must be stated and checked, not
a default to inherit silently.
"""

from __future__ import annotations

# Instructions whose emulation cost is incompatible with a hard real-time
# interrupt path (R-5.12). These stay in hardware even where the subset would
# allow removal -- a retained instruction with a documented latency
# justification beats a removed one that breaks the determinism claim.
#
# This list is correct for the application in docs/02. Check it against the
# actual interrupt paths before relying on it.
REALTIME_CRITICAL = frozenset({
    # trap entry and exit
    "csrrw", "csrrs", "csrrc", "csrrwi", "csrrsi", "csrrci",
    "mret", "sret", "wfi",
    # ISR data path
    "lw", "sw", "lb", "lbu", "lh", "lhu", "sb", "sh",
    # ISR control and address formation
    "add", "addi", "sub", "and", "andi", "or", "ori", "xor", "xori",
    "beq", "bne", "blt", "bge", "bltu", "bgeu",
    "jal", "jalr", "lui", "auipc",
})

#: Emulation handler cost in cycles, including trap entry and return.
#: ESTIMATES ONLY -- replace with measured values once handlers exist. R-5.10
#: requires whole-program slowdown to be measured, not summed from this table.
ESTIMATED_TRAP_COST = {
    "div": 120, "divu": 120, "rem": 130, "remu": 130,
    "mul": 90, "mulh": 110, "mulhsu": 110, "mulhu": 110,
}
DEFAULT_TRAP_COST = 100

KEEP, EMULATE = "keep", "emulate"

CAVEATS = (
    "'absent' is deliberately not a verdict. An instruction outside the static "
    "image is outside the analysed program, not outside the ISA; externally "
    "supplied binaries are covered by the compatibility contract, not by this "
    "classification.",
    "Emulation cycle costs are estimates. R-5.10 requires whole-program "
    "slowdown to be measured, not summed from this table.",
    "Undecodable words in the image indicate embedded data or an unrecognised "
    "encoding. Resolve them before trusting this output.",
    "Using this policy unmodified is a decision (R-4.22). Its real-time list "
    "encodes assumptions about the interrupt paths -- verify them.",
)


def trap_cost(mnemonic: str) -> int:
    return ESTIMATED_TRAP_COST.get(mnemonic, DEFAULT_TRAP_COST)


def classify(static: dict, dynamic: dict | None = None) -> dict:
    """Apply the reference policy to a static profile and optional dynamic one.

    Without a dynamic profile every reachable instruction is kept: that is the
    safe answer, and a useless one, because nothing can be priced.
    """
    s_mn = static.get("mnemonics", {})
    d_mn = (dynamic or {}).get("mnemonics", {})
    d_total = (dynamic or {}).get("total_executed", 0)

    reachable = {m for m in s_mn if not m.startswith("unknown")}
    undecodable = sorted(m for m in s_mn if m.startswith("unknown"))

    have_evidence = dynamic is not None

    entries = []
    for mn in sorted(reachable):
        freq = d_mn.get(mn, 0)

        # The policy, in four branches. The first is the one that matters:
        # with no trace at all, "executed zero times" is not an observation,
        # it is the absence of one. Reading it as evidence of non-execution is
        # exactly the mistake this policy exists to prevent, so a missing
        # dynamic profile keeps everything rather than proposing removals.
        if not have_evidence:
            verdict = KEEP
            why = "no dynamic profile supplied: no evidence on which to remove"
        elif mn in REALTIME_CRITICAL:
            verdict = KEEP
            why = "on the real-time interrupt path (R-5.12)"
        elif freq == 0:
            verdict = EMULATE
            why = ("reachable but unobserved: removable from hardware, "
                   "MUST remain executable in software")
        else:
            verdict = KEEP
            why = f"executed {freq:,} times"

        cost = trap_cost(mn) if verdict == EMULATE else None
        entries.append({
            "mnemonic": mn,
            "verdict": verdict,
            "rationale": why,
            "static_occurrences": s_mn[mn],
            "dynamic_executions": freq,
            "dynamic_share": round(freq / d_total, 6) if d_total else None,
            "estimated_emulation_cycles": cost,
            "estimated_slowdown_cycles": (freq * cost) if cost else 0,
        })

    hot = sorted(
        ((m, c) for m, c in d_mn.items() if not m.startswith("unknown")),
        key=lambda kv: -kv[1],
    )[:15]

    return {
        "pass": "classification",
        "policy_version": "reference-1",
        "source_static": static.get("source"),
        "source_dynamic": (dynamic or {}).get("source"),
        "had_dynamic_profile": dynamic is not None,
        "summary": {
            "reachable": len(reachable),
            "keep": sum(1 for e in entries if e["verdict"] == KEEP),
            "emulate": sum(1 for e in entries if e["verdict"] == EMULATE),
            "undecodable_in_image": len(undecodable),
            "estimated_total_slowdown_cycles":
                sum(e["estimated_slowdown_cycles"] for e in entries),
        },
        "classification": entries,
        "acceleration_candidates": [
            {"mnemonic": m, "executions": c,
             "share": round(c / d_total, 6) if d_total else None}
            for m, c in hot
        ],
        "undecodable": undecodable,
        "caveats": list(CAVEATS),
    }
