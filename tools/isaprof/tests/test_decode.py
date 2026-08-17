"""Decoder tests.

The fixture program carries its own expected decoding alongside each encoding,
so this suite checks the decoder against an independently stated intent rather
than against whatever the decoder currently happens to produce.
"""

from __future__ import annotations

import unittest

from isaprof.decode import decode, insn_length

from .fixtures import make_fixtures


class TestFixtureProgram(unittest.TestCase):
    def test_every_fixture_instruction_decodes_as_declared(self):
        for word, mnemonic, extension in make_fixtures.PROGRAM:
            with self.subTest(word=hex(word), expect=mnemonic):
                insn = decode(word, 32)
                self.assertEqual(insn.mnemonic, mnemonic)
                self.assertEqual(insn.extension, extension)

    def test_no_fixture_instruction_is_unknown(self):
        for word, mnemonic, _ in make_fixtures.PROGRAM:
            self.assertTrue(decode(word, 32).is_known, f"{mnemonic} decoded as unknown")


class TestInstructionLength(unittest.TestCase):
    def test_compressed_halfword(self):
        self.assertEqual(insn_length(0x8082), 2)  # c.jr ra
        self.assertEqual(insn_length(0x0001), 2)  # c.nop

    def test_standard_word(self):
        self.assertEqual(insn_length(0x0093), 4)  # low bits 11, not 11111

    def test_compressed_and_standard_agree_with_decode(self):
        self.assertEqual(decode(0x8082, 32).length, 2)
        self.assertEqual(decode(0x00100093, 32).length, 4)


class TestKnownEncodings(unittest.TestCase):
    """Encodings whose values are well known independently of this codebase."""

    def test_canonical_ret(self):
        self.assertEqual(decode(0x8082, 32).mnemonic, "c.jr")

    def test_canonical_nop(self):
        insn = decode(0x00000013, 32)  # addi x0, x0, 0
        self.assertEqual(insn.mnemonic, "addi")

    def test_ecall_and_ebreak(self):
        self.assertEqual(decode(0x00000073, 32).mnemonic, "ecall")
        self.assertEqual(decode(0x00100073, 32).mnemonic, "ebreak")

    def test_wfi_and_mret_are_privileged(self):
        self.assertEqual(decode(0x10500073, 32).extension, "Priv")
        self.assertEqual(decode(0x30200073, 32).extension, "Priv")


class TestWidthSensitivity(unittest.TestCase):
    """RV64-only encodings must not be silently accepted as RV32."""

    def test_ld_is_rv64_only(self):
        ld = (0 << 20) | (1 << 15) | (3 << 12) | (6 << 7) | 0x03
        self.assertEqual(decode(ld, 64).mnemonic, "ld")
        self.assertFalse(decode(ld, 32).is_known)

    def test_addiw_is_rv64_only(self):
        addiw = (1 << 20) | (1 << 15) | (0 << 12) | (2 << 7) | 0x1B
        self.assertEqual(decode(addiw, 64).mnemonic, "addiw")
        self.assertFalse(decode(addiw, 32).is_known)

    def test_compressed_slot_is_reinterpreted_by_width(self):
        # Quadrant 1, funct3=001 is c.jal on RV32 and c.addiw on RV64.
        word = (1 << 13) | (1 << 7) | 1
        self.assertEqual(decode(word, 32).mnemonic, "c.jal")
        self.assertEqual(decode(word, 64).mnemonic, "c.addiw")


class TestUnknownHandling(unittest.TestCase):
    def test_unrecognised_word_is_reported_not_dropped(self):
        insn = decode(0xFFFFFF7F, 32)
        self.assertFalse(insn.is_known)
        self.assertEqual(insn.extension, "unknown")
        self.assertIn("unknown", insn.mnemonic)

    def test_custom_opcodes_are_distinguished_from_unknown(self):
        for op, name in ((0x0B, "custom-0"), (0x2B, "custom-1"),
                         (0x5B, "custom-2"), (0x7B, "custom-3")):
            insn = decode(op, 32)
            self.assertEqual(insn.mnemonic, name)
            self.assertEqual(insn.extension, "custom")


if __name__ == "__main__":
    unittest.main()
