"""Tests for the ELF reader, the passes, the policy, the renderer, and the CLI.

`TestMeasurementPolicySeparation` is a structural guard rather than a
correctness check: measurement and judgement stay in separate modules, because
the policy is expected to be replaced and replacing it must not require touching
the measurement.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from isaprof import cli
from isaprof.classify import classify as apply_policy
from isaprof.dynamic import profile_trace
from isaprof.elf import ElfError, read_elf
from isaprof.report import render_html, render_markdown
from isaprof.static import profile_elf

from .fixtures import make_fixtures

HERE = os.path.dirname(os.path.abspath(__file__))
ELF = os.path.join(HERE, "fixtures", "sample.elf")
TRACE = os.path.join(HERE, "fixtures", "spike_trace.log")


class TestElfReader(unittest.TestCase):
    def test_reads_riscv_elf32(self):
        img = read_elf(ELF)
        self.assertFalse(img.is_64bit)
        self.assertEqual(img.xlen, 32)
        self.assertEqual(img.entry, make_fixtures.BASE_ADDR)

    def test_finds_the_text_section_by_name(self):
        img = read_elf(ELF)
        self.assertEqual([r.name for r in img.regions], [".text"])
        self.assertEqual(img.regions[0].addr, make_fixtures.BASE_ADDR)

    def test_rejects_non_elf(self):
        with tempfile.NamedTemporaryFile(suffix=".elf", delete=False) as fh:
            fh.write(b"this is not an ELF file")
            path = fh.name
        try:
            with self.assertRaises(ElfError):
                read_elf(path)
        finally:
            os.unlink(path)

    def test_rejects_non_riscv_machine(self):
        with open(ELF, "rb") as fh:
            buf = bytearray(fh.read())
        buf[18:20] = (62).to_bytes(2, "little")  # EM_X86_64
        with tempfile.NamedTemporaryFile(suffix=".elf", delete=False) as fh:
            fh.write(buf)
            path = fh.name
        try:
            with self.assertRaises(ElfError) as ctx:
                read_elf(path)
            self.assertIn("RISC-V", str(ctx.exception))
        finally:
            os.unlink(path)


class TestStaticPass(unittest.TestCase):
    def setUp(self):
        self.prof = profile_elf(ELF)

    def test_decodes_every_instruction_in_the_image(self):
        self.assertEqual(self.prof.total_decoded, len(make_fixtures.PROGRAM))

    def test_clean_fixture_has_no_undecodable_words(self):
        self.assertEqual(self.prof.unknown_count, 0)
        self.assertEqual(self.prof.unknown_rate, 0.0)

    def test_static_sweep_finds_instructions_that_never_execute(self):
        # The whole justification for the static pass: `ecall` is present in the
        # image but absent from the trace. A dynamic-only view would miss it.
        dyn = profile_trace(TRACE, xlen=32)
        self.assertIn("ecall", self.prof.mnemonics)
        self.assertNotIn("ecall", dyn.mnemonics)

    def test_extension_attribution(self):
        ext = self.prof.extensions
        for name in ("I", "M", "A", "F", "D", "C", "Zicsr", "Zifencei", "custom"):
            self.assertGreater(ext.get(name, 0), 0, f"no {name} instructions counted")

    def test_serialises_to_json(self):
        d = self.prof.to_dict()
        self.assertEqual(d["pass"], "static")
        self.assertEqual(d["total_decoded"], len(make_fixtures.PROGRAM))
        json.dumps(d)  # must be JSON-clean


class TestDynamicPass(unittest.TestCase):
    def setUp(self):
        self.prof = profile_trace(TRACE, xlen=32)

    def test_counts_executions_not_occurrences(self):
        # `add` appears once in the image but 40 times in the trace.
        self.assertEqual(self.prof.mnemonics["add"], 40)
        self.assertEqual(profile_elf(ELF).mnemonics["add"], 1)

    def test_skips_comments_and_noise_lines(self):
        self.assertGreater(self.prof.lines_read, self.prof.lines_matched)
        self.assertGreater(self.prof.lines_matched, 0)

    def test_rare_instructions_are_still_recorded(self):
        self.assertEqual(self.prof.mnemonics["fadd.s"], 1)
        self.assertEqual(self.prof.mnemonics["div"], 2)

    def test_hex_format_accepts_preaggregated_counts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("# pre-aggregated histogram\n0x00000073 5\n8082,3\n")
            path = fh.name
        try:
            prof = profile_trace(path, xlen=32, fmt="hex")
            self.assertEqual(prof.mnemonics["ecall"], 5)
            self.assertEqual(prof.mnemonics["c.jr"], 3)
        finally:
            os.unlink(path)


class TestReport(unittest.TestCase):
    def setUp(self):
        self.profiles = [profile_elf(ELF).to_dict(),
                         profile_trace(TRACE, xlen=32).to_dict()]

    def test_markdown_contains_both_passes(self):
        md = render_markdown(self.profiles)
        self.assertIn("Breakdown by extension", md)
        self.assertIn("Per-instruction counts", md)
        self.assertIn("Static", md)
        self.assertIn("Dynamic", md)

    def test_markdown_carries_the_reading_note(self):
        md = render_markdown(self.profiles)
        self.assertIn("not evidence it cannot execute", md)

    def test_html_is_self_contained(self):
        out = render_html(self.profiles)
        self.assertIn("<!doctype html>", out)
        self.assertIn("<table>", out)
        self.assertNotIn("http://", out)
        self.assertNotIn("https://", out)

    def test_renders_from_a_single_pass(self):
        md = render_markdown([self.profiles[0]])
        self.assertIn("Static sweep health", md)


class TestCli(unittest.TestCase):
    def test_static_then_report_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            js = os.path.join(d, "static.json")
            md = os.path.join(d, "report.md")
            self.assertEqual(cli.main(["static", ELF, "--json", js]), 0)
            self.assertEqual(cli.main(["report", js, "-o", md]), 0)
            with open(md) as fh:
                self.assertIn("Per-instruction counts", fh.read())

    def test_dynamic_writes_json(self):
        with tempfile.TemporaryDirectory() as d:
            js = os.path.join(d, "dyn.json")
            self.assertEqual(cli.main(["dynamic", TRACE, "--json", js]), 0)
            with open(js) as fh:
                self.assertEqual(json.load(fh)["pass"], "dynamic")

    def test_missing_file_is_an_error_not_a_traceback(self):
        self.assertEqual(cli.main(["static", "/nonexistent/x.elf"]), 2)


class TestClassification(unittest.TestCase):
    """The reference policy: reachability decides, frequency prices."""

    def setUp(self):
        self.static = profile_elf(ELF).to_dict()
        self.dynamic = profile_trace(TRACE, xlen=32).to_dict()
        self.result = apply_policy(self.static, self.dynamic)
        self.by_mn = {e["mnemonic"]: e for e in self.result["classification"]}

    def test_only_two_verdicts_exist(self):
        # 'absent' is deliberately not a verdict: an instruction outside the
        # analysed image is outside the program, not outside the ISA.
        self.assertEqual({e["verdict"] for e in self.result["classification"]},
                         {"keep", "emulate"})

    def test_unobserved_instruction_is_emulated_never_dropped(self):
        # `fence.i` is in the image and absent from the trace. The policy must
        # keep it executable, not declare it gone.
        self.assertIn("fence.i", self.by_mn)
        self.assertEqual(self.by_mn["fence.i"]["verdict"], "emulate")
        self.assertEqual(self.by_mn["fence.i"]["dynamic_executions"], 0)

    def test_realtime_critical_survives_zero_frequency(self):
        # `jalr` never executes in the fixture trace, but is on the interrupt
        # path, so R-5.12 keeps it in hardware regardless.
        self.assertEqual(self.by_mn["jalr"]["dynamic_executions"], 0)
        self.assertEqual(self.by_mn["jalr"]["verdict"], "keep")
        self.assertIn("R-5.12", self.by_mn["jalr"]["rationale"])

    def test_executed_instruction_is_kept(self):
        self.assertEqual(self.by_mn["mul"]["verdict"], "keep")
        self.assertEqual(self.by_mn["mul"]["dynamic_executions"], 25)

    def test_emulation_cost_is_priced_only_for_emulated(self):
        for e in self.result["classification"]:
            if e["verdict"] == "keep":
                self.assertIsNone(e["estimated_emulation_cycles"])
                self.assertEqual(e["estimated_slowdown_cycles"], 0)
            else:
                self.assertIsNotNone(e["estimated_emulation_cycles"])

    def test_without_dynamic_profile_everything_reachable_is_kept(self):
        safe = apply_policy(self.static, None)
        self.assertEqual(safe["summary"]["emulate"], 0)
        self.assertEqual(safe["summary"]["keep"], safe["summary"]["reachable"])
        self.assertFalse(safe["had_dynamic_profile"])

    def test_acceleration_candidates_ranked_by_frequency(self):
        cands = self.result["acceleration_candidates"]
        self.assertEqual(cands[0]["mnemonic"], "add")
        self.assertEqual([c["executions"] for c in cands],
                         sorted((c["executions"] for c in cands), reverse=True))

    def test_caveats_are_carried_with_the_result(self):
        joined = " ".join(self.result["caveats"])
        self.assertIn("'absent' is deliberately not a verdict", joined)
        self.assertIn("R-4.22", joined)

    def test_cli_classify_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            s, dy, out = (os.path.join(d, n) for n in
                          ("s.json", "d.json", "subset.json"))
            self.assertEqual(cli.main(["static", ELF, "--json", s]), 0)
            self.assertEqual(cli.main(["dynamic", TRACE, "--json", dy]), 0)
            self.assertEqual(cli.main(["classify", s, dy, "-o", out]), 0)
            with open(out) as fh:
                self.assertEqual(json.load(fh)["pass"], "classification")

    def test_cli_classify_rejects_a_dynamic_profile_as_first_argument(self):
        with tempfile.TemporaryDirectory() as d:
            dy = os.path.join(d, "d.json")
            cli.main(["dynamic", TRACE, "--json", dy])
            self.assertEqual(cli.main(["classify", dy]), 2)


class TestMeasurementPolicySeparation(unittest.TestCase):
    """Measuring and judging stay in different modules.

    Not style: the policy is expected to be replaced, and replacing it must not
    require touching the measurement passes.
    """

    def test_measurement_modules_do_not_import_the_policy(self):
        import isaprof.dynamic as dyn
        import isaprof.static as st
        for mod in (st, dyn):
            with open(mod.__file__) as fh:
                src = fh.read()
            self.assertNotIn("from .classify", src)
            self.assertNotIn("import classify", src)

    def test_measurement_output_carries_no_verdicts(self):
        for prof in (profile_elf(ELF).to_dict(),
                     profile_trace(TRACE, xlen=32).to_dict()):
            blob = json.dumps(prof)
            for word in ('"verdict"', '"keep"', '"emulate"'):
                self.assertNotIn(word, blob)


if __name__ == "__main__":
    unittest.main()
