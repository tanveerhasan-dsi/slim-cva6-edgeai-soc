"""RISC-V instruction decoder, to the level of mnemonic and extension.

This is not a disassembler.  It answers exactly one question -- "what
instruction is this, and which extension does it belong to" -- because that is
the only question the measurement instrument needs answered.  Operand fields are
decoded only where they distinguish one mnemonic from another.

Covers RV32/RV64 I, M, A, F, D, C, Zicsr, Zifencei, the machine/supervisor
privileged instructions, and a working subset of Zba/Zbb/Zbs.  Anything else is
reported as `unknown` with its encoding preserved -- an unrecognised opcode in a
binary is a finding, not an error, and must never be silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass

# Extension identifiers used throughout the reports.
I, M, A, F, D, C = "I", "M", "A", "F", "D", "C"
ZICSR, ZIFENCEI, PRIV = "Zicsr", "Zifencei", "Priv"
ZBA, ZBB, ZBS = "Zba", "Zbb", "Zbs"
CUSTOM, UNKNOWN = "custom", "unknown"

#: Order used when presenting a per-extension breakdown.
EXTENSION_ORDER = (
    I, M, A, F, D, C, ZICSR, ZIFENCEI, ZBA, ZBB, ZBS, PRIV, CUSTOM, UNKNOWN,
)


@dataclass(frozen=True)
class Insn:
    """One decoded instruction."""

    mnemonic: str
    extension: str
    length: int  # bytes consumed: 2 for compressed, 4 otherwise
    word: int

    @property
    def is_known(self) -> bool:
        return self.extension != UNKNOWN


def insn_length(half: int) -> int:
    """Bytes consumed by an instruction, from its first halfword.

    RISC-V encodes length in the low bits; anything wider than 32-bit is
    reported as its true length so the walker stays aligned, even though no
    such encoding is decoded here.
    """
    if (half & 0x3) != 0x3:
        return 2
    if (half & 0x1F) != 0x1F:
        return 4
    if (half & 0x3F) == 0x1F:
        return 6
    if (half & 0x7F) == 0x3F:
        return 8
    return 4


def decode(word: int, xlen: int = 32) -> Insn:
    """Decode one instruction word. `word` is 16- or 32-bit, little-endian."""
    if (word & 0x3) != 0x3:
        return _decode_compressed(word & 0xFFFF, xlen)
    return _decode_32(word & 0xFFFFFFFF, xlen)


# --------------------------------------------------------------------------
# 32-bit encodings
# --------------------------------------------------------------------------

_BRANCH = {0: "beq", 1: "bne", 4: "blt", 5: "bge", 6: "bltu", 7: "bgeu"}
_LOAD = {0: "lb", 1: "lh", 2: "lw", 3: "ld", 4: "lbu", 5: "lhu", 6: "lwu"}
_STORE = {0: "sb", 1: "sh", 2: "sw", 3: "sd"}
_OPIMM = {0: "addi", 2: "slti", 3: "sltiu", 4: "xori", 6: "ori", 7: "andi"}
_OP = {0: "add", 1: "sll", 2: "slt", 3: "sltu", 4: "xor", 5: "srl", 6: "or", 7: "and"}
_MULDIV = {
    0: "mul", 1: "mulh", 2: "mulhsu", 3: "mulhu",
    4: "div", 5: "divu", 6: "rem", 7: "remu",
}
_CSR = {1: "csrrw", 2: "csrrs", 3: "csrrc", 5: "csrrwi", 6: "csrrsi", 7: "csrrci"}
_AMO = {
    0x00: "amoadd", 0x01: "amoswap", 0x02: "lr", 0x03: "sc", 0x04: "amoxor",
    0x08: "amoor", 0x0C: "amoand", 0x10: "amomin", 0x14: "amomax",
    0x18: "amominu", 0x1C: "amomaxu",
}
_SYSTEM_PRIV = {
    0x000: ("ecall", I), 0x001: ("ebreak", I),
    0x102: ("sret", PRIV), 0x302: ("mret", PRIV), 0x105: ("wfi", PRIV),
}
_CUSTOM_OPCODES = {0x0B: "custom-0", 0x2B: "custom-1", 0x5B: "custom-2", 0x7B: "custom-3"}


def _decode_32(w: int, xlen: int) -> Insn:
    op = w & 0x7F
    f3 = (w >> 12) & 0x7
    f7 = (w >> 25) & 0x7F
    rs2 = (w >> 20) & 0x1F

    def hit(mn, ext):
        return Insn(mn, ext, 4, w)

    if op == 0x37:
        return hit("lui", I)
    if op == 0x17:
        return hit("auipc", I)
    if op == 0x6F:
        return hit("jal", I)
    if op == 0x67 and f3 == 0:
        return hit("jalr", I)

    if op == 0x63:
        mn = _BRANCH.get(f3)
        return hit(mn, I) if mn else _unknown(w)

    if op == 0x03:
        mn = _LOAD.get(f3)
        if mn in ("ld", "lwu") and xlen < 64:
            return _unknown(w)
        return hit(mn, I) if mn else _unknown(w)

    if op == 0x23:
        mn = _STORE.get(f3)
        if mn == "sd" and xlen < 64:
            return _unknown(w)
        return hit(mn, I) if mn else _unknown(w)

    if op == 0x07:  # LOAD-FP
        return hit("flw", F) if f3 == 2 else hit("fld", D) if f3 == 3 else _unknown(w)
    if op == 0x27:  # STORE-FP
        return hit("fsw", F) if f3 == 2 else hit("fsd", D) if f3 == 3 else _unknown(w)

    if op == 0x0F:
        if f3 == 0:
            return hit("fence", I)
        if f3 == 1:
            return hit("fence.i", ZIFENCEI)
        return _unknown(w)

    if op == 0x13:
        return _op_imm(w, f3, f7, rs2, xlen)
    if op == 0x33:
        return _op(w, f3, f7)
    if op == 0x1B and xlen >= 64:
        return _op_imm32(w, f3, f7)
    if op == 0x3B and xlen >= 64:
        return _op32(w, f3, f7)

    if op == 0x2F:
        return _amo(w, f3, f7, xlen)

    if op == 0x73:
        if f3 == 0:
            imm = (w >> 20) & 0xFFF
            known = _SYSTEM_PRIV.get(imm)
            if known:
                return hit(*known)
            if f7 == 0x09:
                return hit("sfence.vma", PRIV)
            return _unknown(w)
        mn = _CSR.get(f3)
        return hit(mn, ZICSR) if mn else _unknown(w)

    if op in (0x43, 0x47, 0x4B, 0x4F):
        base = {0x43: "fmadd", 0x47: "fmsub", 0x4B: "fnmsub", 0x4F: "fnmadd"}[op]
        fmt = (w >> 25) & 0x3
        if fmt == 0:
            return hit(f"{base}.s", F)
        if fmt == 1:
            return hit(f"{base}.d", D)
        return _unknown(w)

    if op == 0x53:
        return _op_fp(w, f3, f7, rs2)

    if op in _CUSTOM_OPCODES:
        return Insn(_CUSTOM_OPCODES[op], CUSTOM, 4, w)

    return _unknown(w)


def _op_imm(w, f3, f7, rs2, xlen) -> Insn:
    if f3 in _OPIMM:
        return Insn(_OPIMM[f3], I, 4, w)
    shift_top = f7 >> 1 if xlen >= 64 else f7
    if f3 == 1:
        if shift_top == 0:
            return Insn("slli", I, 4, w)
        if f7 == 0x30:
            mn = {0: "clz", 1: "ctz", 2: "cpop", 4: "sext.b", 5: "sext.h"}.get(rs2)
            if mn:
                return Insn(mn, ZBB, 4, w)
        if f7 == 0x28:
            return Insn("bseti", ZBS, 4, w)
        if f7 == 0x24:
            return Insn("bclri", ZBS, 4, w)
        if f7 == 0x34:
            return Insn("binvi", ZBS, 4, w)
        return _unknown(w)
    if f3 == 5:
        if shift_top == 0:
            return Insn("srli", I, 4, w)
        if shift_top == 0x10:
            return Insn("srai", I, 4, w)
        if f7 == 0x30:
            return Insn("rori", ZBB, 4, w)
        if f7 == 0x24:
            return Insn("bexti", ZBS, 4, w)
        if f7 == 0x34 and rs2 == 0x18:
            return Insn("rev8", ZBB, 4, w)
        if f7 == 0x28 and rs2 == 0x07:
            return Insn("orc.b", ZBB, 4, w)
        return _unknown(w)
    return _unknown(w)


def _op(w, f3, f7) -> Insn:
    if f7 == 0x00 and f3 in _OP:
        return Insn(_OP[f3], I, 4, w)
    if f7 == 0x20:
        if f3 == 0:
            return Insn("sub", I, 4, w)
        if f3 == 5:
            return Insn("sra", I, 4, w)
        mn = {7: "andn", 6: "orn", 4: "xnor"}.get(f3)
        if mn:
            return Insn(mn, ZBB, 4, w)
        return _unknown(w)
    if f7 == 0x01 and f3 in _MULDIV:
        return Insn(_MULDIV[f3], M, 4, w)
    if f7 == 0x10:
        mn = {2: "sh1add", 4: "sh2add", 6: "sh3add"}.get(f3)
        if mn:
            return Insn(mn, ZBA, 4, w)
    if f7 == 0x05:
        mn = {4: "min", 5: "minu", 6: "max", 7: "maxu"}.get(f3)
        if mn:
            return Insn(mn, ZBB, 4, w)
    if f7 == 0x30:
        mn = {1: "rol", 5: "ror"}.get(f3)
        if mn:
            return Insn(mn, ZBB, 4, w)
    if f7 == 0x24 and f3 == 1:
        return Insn("bclr", ZBS, 4, w)
    if f7 == 0x24 and f3 == 5:
        return Insn("bext", ZBS, 4, w)
    if f7 == 0x34 and f3 == 1:
        return Insn("binv", ZBS, 4, w)
    if f7 == 0x28 and f3 == 1:
        return Insn("bset", ZBS, 4, w)
    return _unknown(w)


def _op_imm32(w, f3, f7) -> Insn:
    if f3 == 0:
        return Insn("addiw", I, 4, w)
    if f3 == 1:
        if f7 == 0:
            return Insn("slliw", I, 4, w)
        if f7 == 0x30:
            return Insn("clzw", ZBB, 4, w)
        if f7 == 0x04:
            return Insn("slli.uw", ZBA, 4, w)
    if f3 == 5:
        if f7 == 0:
            return Insn("srliw", I, 4, w)
        if f7 == 0x20:
            return Insn("sraiw", I, 4, w)
        if f7 == 0x30:
            return Insn("roriw", ZBB, 4, w)
    return _unknown(w)


def _op32(w, f3, f7) -> Insn:
    if f7 == 0x00:
        mn = {0: "addw", 1: "sllw", 5: "srlw"}.get(f3)
        if mn:
            return Insn(mn, I, 4, w)
    if f7 == 0x20:
        mn = {0: "subw", 5: "sraw"}.get(f3)
        if mn:
            return Insn(mn, I, 4, w)
    if f7 == 0x01:
        mn = {0: "mulw", 4: "divw", 5: "divuw", 6: "remw", 7: "remuw"}.get(f3)
        if mn:
            return Insn(mn, M, 4, w)
    if f7 == 0x04 and f3 == 0:
        return Insn("add.uw", ZBA, 4, w)
    if f7 == 0x10:
        mn = {2: "sh1add.uw", 4: "sh2add.uw", 6: "sh3add.uw"}.get(f3)
        if mn:
            return Insn(mn, ZBA, 4, w)
    if f7 == 0x30:
        mn = {1: "rolw", 5: "rorw"}.get(f3)
        if mn:
            return Insn(mn, ZBB, 4, w)
    return _unknown(w)


def _amo(w, f3, f7, xlen) -> Insn:
    width = {2: "w", 3: "d"}.get(f3)
    if width is None or (width == "d" and xlen < 64):
        return _unknown(w)
    base = _AMO.get(f7 >> 2)
    if base is None:
        return _unknown(w)
    return Insn(f"{base}.{width}", A, 4, w)


_FP_BY_F7 = {
    0x00: ("fadd.s", F), 0x01: ("fadd.d", D),
    0x04: ("fsub.s", F), 0x05: ("fsub.d", D),
    0x08: ("fmul.s", F), 0x09: ("fmul.d", D),
    0x0C: ("fdiv.s", F), 0x0D: ("fdiv.d", D),
    0x2C: ("fsqrt.s", F), 0x2D: ("fsqrt.d", D),
}


def _op_fp(w, f3, f7, rs2) -> Insn:
    simple = _FP_BY_F7.get(f7)
    if simple:
        return Insn(simple[0], simple[1], 4, w)

    ext = D if (f7 & 1) else F
    sfx = "d" if (f7 & 1) else "s"

    if f7 in (0x10, 0x11):
        mn = {0: "fsgnj", 1: "fsgnjn", 2: "fsgnjx"}.get(f3)
        return Insn(f"{mn}.{sfx}", ext, 4, w) if mn else _unknown(w)
    if f7 in (0x14, 0x15):
        mn = {0: "fmin", 1: "fmax"}.get(f3)
        return Insn(f"{mn}.{sfx}", ext, 4, w) if mn else _unknown(w)
    if f7 in (0x50, 0x51):
        mn = {0: "fle", 1: "flt", 2: "feq"}.get(f3)
        return Insn(f"{mn}.{sfx}", ext, 4, w) if mn else _unknown(w)
    if f7 in (0x60, 0x61):
        mn = {0: "fcvt.w", 1: "fcvt.wu", 2: "fcvt.l", 3: "fcvt.lu"}.get(rs2)
        return Insn(f"{mn}.{sfx}", ext, 4, w) if mn else _unknown(w)
    if f7 in (0x68, 0x69):
        mn = {0: "w", 1: "wu", 2: "l", 3: "lu"}.get(rs2)
        return Insn(f"fcvt.{sfx}.{mn}", ext, 4, w) if mn else _unknown(w)
    if f7 in (0x70, 0x71):
        if f3 == 0:
            return Insn("fmv.x.w" if sfx == "s" else "fmv.x.d", ext, 4, w)
        if f3 == 1:
            return Insn(f"fclass.{sfx}", ext, 4, w)
        return _unknown(w)
    if f7 in (0x78, 0x79):
        return Insn("fmv.w.x" if sfx == "s" else "fmv.d.x", ext, 4, w)
    if f7 == 0x20 and rs2 == 1:
        return Insn("fcvt.s.d", D, 4, w)
    if f7 == 0x21 and rs2 == 0:
        return Insn("fcvt.d.s", D, 4, w)
    return _unknown(w)


def _unknown(w: int) -> Insn:
    return Insn(f"unknown:{w:08x}", UNKNOWN, 4, w)


# --------------------------------------------------------------------------
# 16-bit (compressed) encodings
# --------------------------------------------------------------------------

def _decode_compressed(w: int, xlen: int) -> Insn:
    quad = w & 0x3
    f3 = (w >> 13) & 0x7

    def hit(mn, ext=C):
        return Insn(mn, ext, 2, w)

    if w == 0:
        return Insn("c.illegal", UNKNOWN, 2, w)

    if quad == 0:
        if f3 == 0:
            return hit("c.addi4spn")
        if f3 == 1:
            return hit("c.fld", D)
        if f3 == 2:
            return hit("c.lw")
        if f3 == 3:
            return hit("c.ld") if xlen >= 64 else hit("c.flw", F)
        if f3 == 5:
            return hit("c.fsd", D)
        if f3 == 6:
            return hit("c.sw")
        if f3 == 7:
            return hit("c.sd") if xlen >= 64 else hit("c.fsw", F)
        return Insn(f"unknown:c{w:04x}", UNKNOWN, 2, w)

    if quad == 1:
        if f3 == 0:
            return hit("c.nop" if ((w >> 7) & 0x1F) == 0 else "c.addi")
        if f3 == 1:
            return hit("c.addiw") if xlen >= 64 else hit("c.jal")
        if f3 == 2:
            return hit("c.li")
        if f3 == 3:
            return hit("c.addi16sp" if ((w >> 7) & 0x1F) == 2 else "c.lui")
        if f3 == 4:
            return _c_misc_alu(w, xlen)
        if f3 == 5:
            return hit("c.j")
        if f3 == 6:
            return hit("c.beqz")
        if f3 == 7:
            return hit("c.bnez")

    if quad == 2:
        if f3 == 0:
            return hit("c.slli")
        if f3 == 1:
            return hit("c.fldsp", D)
        if f3 == 2:
            return hit("c.lwsp")
        if f3 == 3:
            return hit("c.ldsp") if xlen >= 64 else hit("c.flwsp", F)
        if f3 == 4:
            rs2 = (w >> 2) & 0x1F
            rd = (w >> 7) & 0x1F
            bit12 = (w >> 12) & 1
            if not bit12:
                return hit("c.jr" if rs2 == 0 else "c.mv")
            if rd == 0 and rs2 == 0:
                return hit("c.ebreak")
            return hit("c.jalr" if rs2 == 0 else "c.add")
        if f3 == 5:
            return hit("c.fsdsp", D)
        if f3 == 6:
            return hit("c.swsp")
        if f3 == 7:
            return hit("c.sdsp") if xlen >= 64 else hit("c.fswsp", F)

    return Insn(f"unknown:c{w:04x}", UNKNOWN, 2, w)


def _c_misc_alu(w: int, xlen: int) -> Insn:
    sel = (w >> 10) & 0x3
    if sel == 0:
        return Insn("c.srli", C, 2, w)
    if sel == 1:
        return Insn("c.srai", C, 2, w)
    if sel == 2:
        return Insn("c.andi", C, 2, w)
    op = (w >> 5) & 0x3
    if ((w >> 12) & 1) == 0:
        return Insn({0: "c.sub", 1: "c.xor", 2: "c.or", 3: "c.and"}[op], C, 2, w)
    if op in (0, 1) and xlen >= 64:
        return Insn({0: "c.subw", 1: "c.addw"}[op], C, 2, w)
    return Insn(f"unknown:c{w:04x}", UNKNOWN, 2, w)
