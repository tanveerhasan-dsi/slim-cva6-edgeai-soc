"""Dynamic pass: how often each instruction actually executes.

Traces are consumed by extracting the *instruction encoding* from each line and
decoding it with the same decoder the static pass uses.  Parsing the simulator's
own mnemonic text would be fragile across versions and, worse, would name
instructions differently from the static pass -- making the two passes
incomparable exactly where comparing them matters.

Supported inputs:

* ``spike``  -- Spike ``-l`` / ``--log-commits`` output, and anything else that
  prints the encoding in parentheses, e.g.
  ``core   0: 0x80000000 (0x00000297) auipc t0, 0x0``
* ``hex``    -- one instruction word per line, with or without ``0x``; a
  trailing count after whitespace or a comma is honoured, so pre-aggregated
  histograms from a QEMU TCG plugin can be fed in directly.

A dynamic profile must never be used to decide what to delete.  Frequency zero
means "not executed by this run", not "cannot execute" -- only the static pass
can support a deletion argument.  Frequency is for ranking what to accelerate
and for costing emulation.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .decode import EXTENSION_ORDER, decode

#: Encoding printed in parentheses, as Spike and most trace tools emit it.
_PAREN_ENCODING = re.compile(r"\((0x)?([0-9a-fA-F]{4,8})\)")
#: A bare hex word, optionally followed by a repeat count.
_BARE_HEX = re.compile(
    r"^\s*(?:0[xX])?([0-9a-fA-F]{4,8})\s*(?:[,\s]\s*(\d+))?\s*$"
)


@dataclass
class DynamicProfile:
    """Result of a trace sweep. Counts are *executions*."""

    source: str
    xlen: int
    fmt: str
    mnemonics: Counter = field(default_factory=Counter)
    extensions: Counter = field(default_factory=Counter)
    lines_read: int = 0
    lines_matched: int = 0

    @property
    def total_executed(self) -> int:
        return sum(self.mnemonics.values())

    @property
    def distinct_known(self) -> int:
        return sum(1 for m in self.mnemonics if not m.startswith("unknown"))

    def to_dict(self) -> dict:
        total = self.total_executed
        return {
            "pass": "dynamic",
            "source": self.source,
            "format": self.fmt,
            "xlen": self.xlen,
            "total_executed": total,
            "distinct_known_mnemonics": self.distinct_known,
            "lines_read": self.lines_read,
            "lines_matched": self.lines_matched,
            "extensions": {
                e: self.extensions[e] for e in EXTENSION_ORDER if self.extensions.get(e)
            },
            "mnemonics": dict(self.mnemonics.most_common()),
        }


def _record(prof: DynamicProfile, raw: str, count: int) -> None:
    word = int(raw, 16)
    # A 4-hex-digit token is a compressed instruction only if its low bits say
    # so; otherwise it is a zero-padded 32-bit word.
    insn = decode(word, prof.xlen)
    prof.mnemonics[insn.mnemonic] += count
    prof.extensions[insn.extension] += count


def profile_trace(path: str, xlen: int = 32, fmt: str = "auto") -> DynamicProfile:
    prof = DynamicProfile(source=path, xlen=xlen, fmt=fmt)

    with open(path, "r", errors="replace") as fh:
        for line in fh:
            prof.lines_read += 1
            if not line.strip() or line.lstrip().startswith("#"):
                continue

            if fmt in ("auto", "spike"):
                m = _PAREN_ENCODING.search(line)
                if m:
                    _record(prof, m.group(2), 1)
                    prof.lines_matched += 1
                    continue
                if fmt == "spike":
                    continue

            if fmt in ("auto", "hex"):
                m = _BARE_HEX.match(line)
                if m:
                    _record(prof, m.group(1), int(m.group(2) or 1))
                    prof.lines_matched += 1

    if prof.fmt == "auto":
        prof.fmt = "auto"
    return prof
