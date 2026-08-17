"""Minimal read-only ELF parser, sufficient to recover executable bytes.

Deliberately dependency-free: the toolchain a team has installed should not
determine whether the measurement instrument runs.  Only the subset of ELF
needed to answer "which bytes will the fetch unit ever see" is implemented.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

EM_RISCV = 243

SHF_EXECINSTR = 0x4
SHF_ALLOC = 0x2
SHT_NOBITS = 8

PT_LOAD = 1
PF_X = 0x1


class ElfError(Exception):
    """Raised when a file is not a RISC-V ELF we can read."""


@dataclass(frozen=True)
class CodeRegion:
    """A contiguous run of allocated, executable bytes."""

    name: str
    addr: int
    data: bytes

    @property
    def size(self) -> int:
        return len(self.data)


@dataclass(frozen=True)
class ElfImage:
    path: str
    is_64bit: bool
    entry: int
    regions: tuple[CodeRegion, ...]

    @property
    def xlen(self) -> int:
        return 64 if self.is_64bit else 32

    @property
    def total_code_bytes(self) -> int:
        return sum(r.size for r in self.regions)


def _u(fmt: str, buf: bytes, off: int):
    return struct.unpack_from(fmt, buf, off)


def read_elf(path: str) -> ElfImage:
    """Parse `path` and return its allocated executable regions.

    Section headers are preferred because they carry names, which make the
    resulting report far easier to act on.  Program headers are used as a
    fallback for stripped images.
    """
    with open(path, "rb") as fh:
        buf = fh.read()

    if len(buf) < 64 or buf[:4] != b"\x7fELF":
        raise ElfError(f"{path}: not an ELF file")

    ei_class, ei_data = buf[4], buf[5]
    if ei_data != 1:
        raise ElfError(f"{path}: only little-endian ELF is supported")
    if ei_class not in (1, 2):
        raise ElfError(f"{path}: unknown ELF class {ei_class}")

    is_64 = ei_class == 2
    machine = _u("<H", buf, 18)[0]
    if machine != EM_RISCV:
        raise ElfError(
            f"{path}: e_machine is {machine}, expected {EM_RISCV} (RISC-V). "
            "isaprof only decodes RISC-V images."
        )

    if is_64:
        entry = _u("<Q", buf, 24)[0]
        e_phoff, e_shoff = _u("<Q", buf, 32)[0], _u("<Q", buf, 40)[0]
        e_phentsize, e_phnum = _u("<H", buf, 54)[0], _u("<H", buf, 56)[0]
        e_shentsize, e_shnum = _u("<H", buf, 58)[0], _u("<H", buf, 60)[0]
        e_shstrndx = _u("<H", buf, 62)[0]
    else:
        entry = _u("<I", buf, 24)[0]
        e_phoff, e_shoff = _u("<I", buf, 28)[0], _u("<I", buf, 32)[0]
        e_phentsize, e_phnum = _u("<H", buf, 42)[0], _u("<H", buf, 44)[0]
        e_shentsize, e_shnum = _u("<H", buf, 46)[0], _u("<H", buf, 48)[0]
        e_shstrndx = _u("<H", buf, 50)[0]

    regions: list[CodeRegion] = []

    if e_shoff and e_shnum:
        regions = _sections(buf, is_64, e_shoff, e_shentsize, e_shnum, e_shstrndx)

    if not regions and e_phoff and e_phnum:
        regions = _segments(buf, is_64, e_phoff, e_phentsize, e_phnum)

    if not regions:
        raise ElfError(f"{path}: no allocated executable bytes found")

    regions.sort(key=lambda r: r.addr)
    return ElfImage(path=path, is_64bit=is_64, entry=entry, regions=tuple(regions))


def _sections(buf, is_64, off, entsize, num, shstrndx) -> list[CodeRegion]:
    raw = []
    for i in range(num):
        base = off + i * entsize
        if base + entsize > len(buf):
            break
        if is_64:
            name, typ, flags = _u("<IIQ", buf, base)
            addr, offset, size = _u("<QQQ", buf, base + 16)
        else:
            name, typ, flags, addr, offset, size = _u("<IIIIII", buf, base)
        raw.append((name, typ, flags, addr, offset, size))

    strtab = b""
    if shstrndx < len(raw):
        _, _, _, _, stoff, stsize = raw[shstrndx]
        strtab = buf[stoff : stoff + stsize]

    out = []
    for name, typ, flags, addr, offset, size in raw:
        if typ == SHT_NOBITS or not size:
            continue
        if not (flags & SHF_EXECINSTR) or not (flags & SHF_ALLOC):
            continue
        if offset + size > len(buf):
            continue
        out.append(CodeRegion(_cstr(strtab, name), addr, buf[offset : offset + size]))
    return out


def _segments(buf, is_64, off, entsize, num) -> list[CodeRegion]:
    out = []
    for i in range(num):
        base = off + i * entsize
        if base + entsize > len(buf):
            break
        if is_64:
            p_type, p_flags = _u("<II", buf, base)
            p_offset, p_vaddr = _u("<QQ", buf, base + 8)
            p_filesz = _u("<Q", buf, base + 32)[0]
        else:
            p_type = _u("<I", buf, base)[0]
            p_offset, p_vaddr = _u("<II", buf, base + 4)
            p_filesz = _u("<I", buf, base + 16)[0]
            p_flags = _u("<I", buf, base + 24)[0]
        if p_type != PT_LOAD or not (p_flags & PF_X) or not p_filesz:
            continue
        if p_offset + p_filesz > len(buf):
            continue
        out.append(
            CodeRegion(f"seg{i}", p_vaddr, buf[p_offset : p_offset + p_filesz])
        )
    return out


def _cstr(tab: bytes, off: int) -> str:
    if off >= len(tab):
        return "?"
    end = tab.find(b"\0", off)
    return tab[off : end if end >= 0 else len(tab)].decode("utf-8", "replace")
