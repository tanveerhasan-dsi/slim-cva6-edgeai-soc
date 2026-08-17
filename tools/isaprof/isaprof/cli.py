"""Command-line entry point for isaprof.

Deliberately dependency-free (argparse, not click) so the instrument runs on a
bare Python 3 install.  A measurement tool that first requires a working
environment is a measurement tool nobody runs.

`static` and `dynamic` measure.  `classify` judges, using the reference policy
in `classify.py`.  The separation is deliberate: swapping the policy must not
require touching the measurement, and a classification is a design decision
rather than a fact about a binary.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .classify import classify as apply_policy
from .dynamic import profile_trace
from .elf import ElfError
from .report import load_profiles, render_html, render_markdown
from .static import profile_elf


def _write(path: str | None, text: str) -> None:
    if path and path != "-":
        with open(path, "w") as fh:
            fh.write(text)
        print(f"wrote {path}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def _summarise_static(prof) -> None:
    print(f"  source            {prof.source}", file=sys.stderr)
    print(f"  xlen              RV{prof.xlen}", file=sys.stderr)
    print(f"  words decoded     {prof.total_decoded:,}", file=sys.stderr)
    print(f"  distinct known    {prof.distinct_known}", file=sys.stderr)
    print(f"  undecodable       {prof.unknown_count:,} "
          f"({100 * prof.unknown_rate:.2f}%)", file=sys.stderr)
    if prof.unknown_rate > 0.05:
        print("  note: >5% undecodable — the swept regions likely contain "
              "embedded data; narrow them before trusting the counts.",
              file=sys.stderr)


def cmd_static(args) -> int:
    try:
        prof = profile_elf(args.elf, args.xlen)
    except (ElfError, OSError) as exc:
        print(f"isaprof: {exc}", file=sys.stderr)
        return 2

    print("static pass", file=sys.stderr)
    _summarise_static(prof)

    if args.json:
        _write(args.json, json.dumps(prof.to_dict(), indent=2) + "\n")
    if args.top:
        print("", file=sys.stderr)
        for mn, n in prof.mnemonics.most_common(args.top):
            print(f"  {n:>10,}  {mn}", file=sys.stderr)
    return 0


def cmd_dynamic(args) -> int:
    try:
        prof = profile_trace(args.trace, args.xlen, args.format)
    except OSError as exc:
        print(f"isaprof: {exc}", file=sys.stderr)
        return 2

    print("dynamic pass", file=sys.stderr)
    print(f"  source            {prof.source}", file=sys.stderr)
    print(f"  lines read        {prof.lines_read:,}", file=sys.stderr)
    print(f"  lines matched     {prof.lines_matched:,}", file=sys.stderr)
    print(f"  executions        {prof.total_executed:,}", file=sys.stderr)
    print(f"  distinct known    {prof.distinct_known}", file=sys.stderr)
    if prof.lines_read and not prof.lines_matched:
        print("  note: no instruction encodings recognised — check --format.",
              file=sys.stderr)

    if args.json:
        _write(args.json, json.dumps(prof.to_dict(), indent=2) + "\n")
    if args.top:
        print("", file=sys.stderr)
        for mn, n in prof.mnemonics.most_common(args.top):
            print(f"  {n:>12,}  {mn}", file=sys.stderr)
    return 0


def cmd_report(args) -> int:
    try:
        profiles = load_profiles(args.profiles)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"isaprof: {exc}", file=sys.stderr)
        return 2

    if not profiles:
        print("isaprof: no profiles given", file=sys.stderr)
        return 2

    render = render_html if args.format == "html" else render_markdown
    _write(args.output, render(profiles, args.title))
    return 0


def cmd_classify(args) -> int:
    try:
        profiles = load_profiles([args.static] + ([args.dynamic] if args.dynamic else []))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"isaprof: {exc}", file=sys.stderr)
        return 2

    static = next((p for p in profiles if p.get("pass") == "static"), None)
    dynamic = next((p for p in profiles if p.get("pass") == "dynamic"), None)

    if static is None:
        print("isaprof: a static profile is required to classify", file=sys.stderr)
        return 2
    if dynamic is None:
        print("isaprof: no dynamic profile given; every reachable instruction "
              "will be kept and no emulation cost can be estimated.",
              file=sys.stderr)

    result = apply_policy(static, dynamic)
    s = result["summary"]

    print("classification (policy: reference-1)", file=sys.stderr)
    print(f"  reachable         {s['reachable']}", file=sys.stderr)
    print(f"  keep              {s['keep']}", file=sys.stderr)
    print(f"  emulate           {s['emulate']}", file=sys.stderr)
    if s["undecodable_in_image"]:
        print(f"  undecodable       {s['undecodable_in_image']} "
              "— resolve before trusting this output", file=sys.stderr)

    _write(args.output, json.dumps(result, indent=2) + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="isaprof",
        description="Measure which RISC-V instructions a workload can and does "
                    "execute, and classify them under the reference policy.",
    )
    p.add_argument("--version", action="version", version=f"isaprof {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser(
        "static",
        help="sweep an ELF for every instruction that may execute",
        description="Linear sweep of allocated executable regions. "
                    "Over-approximates by design.",
    )
    s.add_argument("elf")
    s.add_argument("--xlen", type=int, choices=(32, 64),
                   help="override the width inferred from the ELF class")
    s.add_argument("--json", metavar="PATH", help="write the profile as JSON")
    s.add_argument("--top", type=int, default=0, metavar="N",
                   help="also print the N most common mnemonics")
    s.set_defaults(func=cmd_static)

    d = sub.add_parser(
        "dynamic",
        help="count executions from a simulator trace",
        description="Extracts instruction encodings from a trace and decodes "
                    "them with the same decoder the static pass uses.",
    )
    d.add_argument("trace")
    d.add_argument("--xlen", type=int, choices=(32, 64), default=32)
    d.add_argument("--format", choices=("auto", "spike", "hex"), default="auto")
    d.add_argument("--json", metavar="PATH", help="write the profile as JSON")
    d.add_argument("--top", type=int, default=0, metavar="N",
                   help="also print the N most executed mnemonics")
    d.set_defaults(func=cmd_dynamic)

    r = sub.add_parser(
        "report",
        help="render one or more JSON profiles as a report",
    )
    r.add_argument("profiles", nargs="+", metavar="PROFILE.json")
    r.add_argument("-o", "--output", help="output path (default: stdout)")
    r.add_argument("--format", choices=("markdown", "html"), default="markdown")
    r.add_argument("--title", default="isaprof report")
    r.set_defaults(func=cmd_report)

    c = sub.add_parser(
        "classify",
        help="apply the reference policy to measured profiles",
        description="Reachability decides, frequency prices. See "
                    "docs/04-methodology-requirements.md section 9. Using this "
                    "policy unmodified is a decision, not a default (R-4.22).",
    )
    c.add_argument("static", metavar="STATIC.json")
    c.add_argument("dynamic", nargs="?", metavar="DYNAMIC.json")
    c.add_argument("-o", "--output", help="output path (default: stdout)")
    c.set_defaults(func=cmd_classify)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
