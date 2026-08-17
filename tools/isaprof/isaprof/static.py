"""Static pass: which instructions can possibly execute.

A linear sweep of every allocated executable region.  This deliberately
over-approximates: it decodes constant pools, jump tables and alignment padding
that happen to live in `.text` alongside real code.

That over-approximation is the point.  The static pass exists to bound what the
fetch unit may ever see, so erring towards including something is safe while
erring towards excluding it is not.  The `unknown_rate` in the result is the
health signal -- a high rate means the region carries substantial embedded data,
and the region list should be narrowed before the numbers are trusted.
"""

from __future__ import annotations

import struct
from collections import Counter
from dataclasses import dataclass, field

from .decode import EXTENSION_ORDER, decode, insn_length
from .elf import ElfImage, read_elf


@dataclass
class RegionStat:
    name: str
    addr: int
    size: int
    decoded: int
    unknown: int


@dataclass
class StaticProfile:
    """Result of a static sweep. Counts are *occurrences in the image*."""

    source: str
    xlen: int
    mnemonics: Counter = field(default_factory=Counter)
    extensions: Counter = field(default_factory=Counter)
    regions: list[RegionStat] = field(default_factory=list)

    @property
    def total_decoded(self) -> int:
        return sum(self.mnemonics.values())

    @property
    def unknown_count(self) -> int:
        return self.extensions.get("unknown", 0)

    @property
    def unknown_rate(self) -> float:
        total = self.total_decoded
        return (self.unknown_count / total) if total else 0.0

    @property
    def distinct_known(self) -> int:
        return sum(1 for m in self.mnemonics if not m.startswith("unknown"))

    def to_dict(self) -> dict:
        return {
            "pass": "static",
            "source": self.source,
            "xlen": self.xlen,
            "total_decoded": self.total_decoded,
            "distinct_known_mnemonics": self.distinct_known,
            "unknown_count": self.unknown_count,
            "unknown_rate": round(self.unknown_rate, 6),
            "extensions": {
                e: self.extensions[e] for e in EXTENSION_ORDER if self.extensions.get(e)
            },
            "mnemonics": dict(self.mnemonics.most_common()),
            "regions": [
                {
                    "name": r.name,
                    "addr": f"0x{r.addr:x}",
                    "size": r.size,
                    "decoded": r.decoded,
                    "unknown": r.unknown,
                }
                for r in self.regions
            ],
        }


def profile_image(image: ElfImage, xlen: int | None = None) -> StaticProfile:
    xlen = xlen or image.xlen
    prof = StaticProfile(source=image.path, xlen=xlen)

    for region in image.regions:
        decoded = unknown = 0
        data = region.data
        off = 0
        limit = len(data)
        while off + 2 <= limit:
            half = struct.unpack_from("<H", data, off)[0]
            length = insn_length(half)
            if off + length > limit:
                break
            if length == 2:
                word = half
            elif length == 4:
                word = struct.unpack_from("<I", data, off)[0]
            else:
                # Wider encodings are not decoded, but must still be stepped
                # over so the sweep stays aligned with the instruction stream.
                off += length
                continue
            insn = decode(word, xlen)
            prof.mnemonics[insn.mnemonic] += 1
            prof.extensions[insn.extension] += 1
            decoded += 1
            if not insn.is_known:
                unknown += 1
            off += length

        prof.regions.append(
            RegionStat(region.name, region.addr, region.size, decoded, unknown)
        )

    return prof


def profile_elf(path: str, xlen: int | None = None) -> StaticProfile:
    return profile_image(read_elf(path), xlen)
