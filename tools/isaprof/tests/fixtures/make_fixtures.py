#!/usr/bin/env python3
"""Generate the test fixtures.

The fixtures are checked in so the suite runs without a RISC-V toolchain, but
they are generated rather than hand-pasted so they stay auditable: every
instruction below is assembled from its field encoding, and the expected
decoding is stated alongside it.

Run from this directory:  python3 make_fixtures.py
"""

from __future__ import annotations

import struct

OUT_ELF = "sample.elf"
OUT_TRACE = "spike_trace.log"

BASE_ADDR = 0x80000000


# --- instruction assemblers ------------------------------------------------

def r(f7, rs2, rs1, f3, rd, op):
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def i(imm, rs1, f3, rd, op):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def s(imm, rs2, rs1, f3, op):
    hi, lo = (imm >> 5) & 0x7F, imm & 0x1F
    return (hi << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (lo << 7) | op


def b(imm, rs2, rs1, f3, op):
    hi = ((imm >> 12) & 1) << 6 | ((imm >> 5) & 0x3F)
    lo = ((imm >> 1) & 0xF) << 1 | ((imm >> 11) & 1)
    return (hi << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (lo << 7) | op


def u(imm, rd, op):
    return ((imm & 0xFFFFF) << 12) | (rd << 7) | op


# (encoding, expected mnemonic, expected extension)
PROGRAM = [
    (u(0x1, 1, 0x37), "lui", "I"),
    (u(0x0, 2, 0x17), "auipc", "I"),
    (i(1, 0, 0, 1, 0x13), "addi", "I"),
    (r(0x00, 2, 1, 0, 3, 0x33), "add", "I"),
    (r(0x20, 2, 1, 0, 3, 0x33), "sub", "I"),
    (r(0x00, 2, 1, 7, 4, 0x33), "and", "I"),
    (r(0x01, 2, 1, 0, 4, 0x33), "mul", "M"),
    (r(0x01, 2, 1, 4, 5, 0x33), "div", "M"),
    (r(0x01, 2, 1, 6, 5, 0x33), "rem", "M"),
    (i(0, 1, 2, 6, 0x03), "lw", "I"),
    (s(0, 6, 1, 2, 0x23), "sw", "I"),
    (b(8, 2, 1, 0, 0x63), "beq", "I"),
    (b(8, 2, 1, 1, 0x63), "bne", "I"),
    (0x0000006F, "jal", "I"),
    (i(0, 1, 0, 0, 0x67), "jalr", "I"),
    (i(0x300, 0, 2, 7, 0x73), "csrrs", "Zicsr"),
    (i(0x300, 0, 1, 0, 0x73), "csrrw", "Zicsr"),
    (0x00000073, "ecall", "I"),
    (0x30200073, "mret", "Priv"),
    (i(0, 0, 0, 0, 0x0F), "fence", "I"),
    (i(0, 0, 1, 0, 0x0F), "fence.i", "Zifencei"),
    (r(0x00, 2, 1, 0, 0, 0x53), "fadd.s", "F"),
    (r(0x01, 2, 1, 0, 0, 0x53), "fadd.d", "D"),
    (i(0, 1, 2, 3, 0x07), "flw", "F"),
    (i(0, 1, 3, 3, 0x07), "fld", "D"),
    (r(0x00, 9, 10, 2, 8, 0x2F), "amoadd.w", "A"),
    (r(0x08, 9, 10, 2, 8, 0x2F), "lr.w", "A"),
    (r(0x10, 2, 1, 2, 5, 0x33), "sh1add", "Zba"),
    (r(0x05, 2, 1, 4, 5, 0x33), "min", "Zbb"),
    (r(0x20, 2, 1, 7, 5, 0x33), "andn", "Zbb"),
    (r(0x00, 2, 1, 0, 5, 0x0B), "custom-0", "custom"),
    # Compressed. 0x8082 is the canonical `ret`, which doubles as a check that
    # the compressed quadrant-2 decoding is right.
    (0x0085, "c.addi", "C"),
    (0x0001, "c.nop", "C"),
    (0x808A, "c.mv", "C"),
    (0x8082, "c.jr", "C"),
]


def build_text() -> bytes:
    out = bytearray()
    for word, _, _ in PROGRAM:
        if (word & 3) != 3:
            out += struct.pack("<H", word)
        else:
            out += struct.pack("<I", word)
    return bytes(out)


def build_elf(text: bytes) -> bytes:
    shstr = b"\0.text\0.shstrtab\0"
    name_text, name_shstr = 1, 7

    ehsize, shentsize, shnum, shstrndx = 52, 40, 3, 2
    text_off = ehsize
    shstr_off = text_off + len(text)
    sh_off = (shstr_off + len(shstr) + 3) & ~3

    eh = bytearray(ehsize)
    eh[0:4] = b"\x7fELF"
    eh[4] = 1          # ELFCLASS32
    eh[5] = 1          # ELFDATA2LSB
    eh[6] = 1          # EV_CURRENT
    struct.pack_into("<HH", eh, 16, 2, 243)          # ET_EXEC, EM_RISCV
    struct.pack_into("<I", eh, 20, 1)                # e_version
    struct.pack_into("<I", eh, 24, BASE_ADDR)        # e_entry
    struct.pack_into("<I", eh, 28, 0)                # e_phoff
    struct.pack_into("<I", eh, 32, sh_off)           # e_shoff
    struct.pack_into("<I", eh, 36, 0)                # e_flags
    struct.pack_into("<HHHHHH", eh, 40,
                     ehsize, 0, 0, shentsize, shnum, shstrndx)

    def shdr(name, typ, flags, addr, off, size, align):
        return struct.pack("<10I", name, typ, flags, addr, off, size, 0, 0,
                           align, 0)

    sections = (
        shdr(0, 0, 0, 0, 0, 0, 0)                                 # SHT_NULL
        + shdr(name_text, 1, 0x2 | 0x4, BASE_ADDR, text_off, len(text), 4)
        + shdr(name_shstr, 3, 0, 0, shstr_off, len(shstr), 1)
    )

    buf = bytearray(eh)
    buf += text
    buf += shstr
    buf += b"\0" * (sh_off - len(buf))
    buf += sections
    return bytes(buf)


def build_trace() -> str:
    """A Spike-style commit log exercising the encoding-extraction path."""
    lines = [
        "# isaprof fixture: Spike-style commit log",
        "warning: tohost/fromhost symbols not in ELF; can't communicate with target",
    ]
    addr = BASE_ADDR
    # Weight the loop body so the dynamic profile is visibly skewed, the way a
    # real kernel is -- a flat histogram would not exercise the ranking output.
    stream = (
        [PROGRAM[3]] * 40      # add
        + [PROGRAM[6]] * 25    # mul
        + [PROGRAM[9]] * 18    # lw
        + [PROGRAM[10]] * 12   # sw
        + [PROGRAM[11]] * 8    # beq
        + [PROGRAM[7]] * 2     # div  -- rare, but present
        + [PROGRAM[21]] * 1    # fadd.s -- rarer still
    )
    for word, mnemonic, _ in stream:
        lines.append(f"core   0: 0x{addr:016x} (0x{word:08x}) {mnemonic}")
        addr += 4
    return "\n".join(lines) + "\n"


def main() -> None:
    text = build_text()
    with open(OUT_ELF, "wb") as fh:
        fh.write(build_elf(text))
    with open(OUT_TRACE, "w") as fh:
        fh.write(build_trace())
    print(f"{OUT_ELF}: {len(text)} bytes of text, {len(PROGRAM)} instructions")
    print(f"{OUT_TRACE}: written")


if __name__ == "__main__":
    main()
