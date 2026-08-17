"""Markdown and HTML rendering of profile results.

The renderer presents measurements and refuses to interpret them.  It will not
label an instruction as required, removable, or emulatable -- deriving that
policy from these numbers is the design work this instrument exists to inform,
not something the instrument should pre-empt.
"""

from __future__ import annotations

import html
import json

from .decode import EXTENSION_ORDER

READING_NOTE = """\
> **How to read this report.** The static column bounds what the fetch unit may
> ever see; the dynamic column records what one particular run happened to
> execute. They answer different questions and are not interchangeable. An
> instruction absent from the dynamic column was not executed *by this run* --
> that is not evidence it cannot execute.
"""


def _table(headers, rows) -> list[str]:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def _pct(n, total) -> str:
    return f"{(100.0 * n / total):.2f}%" if total else "—"


def render_markdown(profiles: list[dict], title: str = "isaprof report") -> str:
    static = next((p for p in profiles if p.get("pass") == "static"), None)
    dynamic = next((p for p in profiles if p.get("pass") == "dynamic"), None)

    L: list[str] = [f"# {title}", "", READING_NOTE, ""]

    L += ["## Inputs", ""]
    rows = []
    if static:
        rows.append(["static", static["source"], f"RV{static['xlen']}",
                     f"{static['total_decoded']:,} decoded"])
    if dynamic:
        rows.append(["dynamic", dynamic["source"], f"RV{dynamic['xlen']}",
                     f"{dynamic['total_executed']:,} executed"])
    L += _table(["Pass", "Source", "XLEN", "Volume"], rows) + [""]

    if static:
        L += _static_health(static)
    if static or dynamic:
        L += _extension_table(static, dynamic)
        L += _mnemonic_table(static, dynamic)

    return "\n".join(L) + "\n"


def _static_health(static: dict) -> list[str]:
    L = ["## Static sweep health", ""]
    rate = static["unknown_rate"]
    L += _table(
        ["Metric", "Value"],
        [
            ["Distinct known mnemonics", static["distinct_known_mnemonics"]],
            ["Words decoded", f"{static['total_decoded']:,}"],
            ["Undecodable words", f"{static['unknown_count']:,}"],
            ["Undecodable rate", f"{100 * rate:.2f}%"],
        ],
    ) + [""]

    if rate > 0.05:
        L += [
            f"> **Undecodable rate is {100 * rate:.1f}%.** A linear sweep decodes "
            "constant pools, jump tables and padding that share a section with "
            "code. Above roughly 5%, narrow the region list or exclude embedded "
            "data before treating the distinct-mnemonic count as meaningful.",
            "",
        ]

    if static.get("regions"):
        L += ["### Regions swept", ""]
        L += _table(
            ["Region", "Address", "Bytes", "Decoded", "Undecodable"],
            [[r["name"], r["addr"], f"{r['size']:,}", f"{r['decoded']:,}",
              f"{r['unknown']:,}"] for r in static["regions"]],
        ) + [""]
    return L


def _extension_table(static: dict | None, dynamic: dict | None) -> list[str]:
    L = ["## Breakdown by extension", ""]
    s_ext = (static or {}).get("extensions", {})
    d_ext = (dynamic or {}).get("extensions", {})
    s_tot = (static or {}).get("total_decoded", 0)
    d_tot = (dynamic or {}).get("total_executed", 0)

    headers = ["Extension"]
    if static:
        headers += ["Static count", "Static share"]
    if dynamic:
        headers += ["Dynamic count", "Dynamic share"]

    rows = []
    for ext in EXTENSION_ORDER:
        if not s_ext.get(ext) and not d_ext.get(ext):
            continue
        row = [f"`{ext}`"]
        if static:
            row += [f"{s_ext.get(ext, 0):,}", _pct(s_ext.get(ext, 0), s_tot)]
        if dynamic:
            row += [f"{d_ext.get(ext, 0):,}", _pct(d_ext.get(ext, 0), d_tot)]
        rows.append(row)

    return L + _table(headers, rows) + [""]


def _mnemonic_table(static: dict | None, dynamic: dict | None) -> list[str]:
    s_mn = (static or {}).get("mnemonics", {})
    d_mn = (dynamic or {}).get("mnemonics", {})
    d_tot = (dynamic or {}).get("total_executed", 0)

    keys = set(s_mn) | set(d_mn)
    ordered = sorted(keys, key=lambda m: (-d_mn.get(m, 0), -s_mn.get(m, 0), m))

    headers = ["Mnemonic"]
    if static:
        headers.append("Static")
    if dynamic:
        headers += ["Dynamic", "Dynamic share"]

    rows = []
    for m in ordered:
        row = [f"`{m}`"]
        if static:
            row.append(f"{s_mn.get(m, 0):,}")
        if dynamic:
            row += [f"{d_mn.get(m, 0):,}", _pct(d_mn.get(m, 0), d_tot)]
        rows.append(row)

    return ["## Per-instruction counts", ""] + _table(headers, rows) + [""]


_HTML_SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
 body{{font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      max-width:60rem;margin:2rem auto;padding:0 1rem;color:#1a1a1a}}
 table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:14px}}
 th,td{{border:1px solid #d0d0d0;padding:.35rem .6rem;text-align:left}}
 th{{background:#f4f4f4}} code{{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px}}
 blockquote{{border-left:3px solid #999;margin:1rem 0;padding:.2rem 1rem;color:#444}}
 @media(prefers-color-scheme:dark){{
   body{{background:#161616;color:#e8e8e8}} th{{background:#242424}}
   th,td{{border-color:#3a3a3a}} code{{background:#242424}}
 }}
</style></head><body>
{body}
</body></html>
"""


def render_html(profiles: list[dict], title: str = "isaprof report") -> str:
    """Minimal HTML rendering, derived from the markdown so the two agree."""
    md = render_markdown(profiles, title)
    body: list[str] = []
    rows: list[list[str]] = []

    def flush():
        nonlocal rows
        if not rows:
            return
        head, *rest = rows
        body.append("<table><thead><tr>"
                    + "".join(f"<th>{html.escape(c)}</th>" for c in head)
                    + "</tr></thead><tbody>")
        for r in rest:
            body.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
        body.append("</tbody></table>")
        rows = []

    for line in md.splitlines():
        if line.startswith("|") and set(line) <= set("|- "):
            continue
        if line.startswith("|"):
            rows.append([_inline(c.strip()) for c in line.strip("|").split("|")])
            continue
        flush()
        if line.startswith("### "):
            body.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            body.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("> "):
            body.append(f"<blockquote>{_inline(line[2:])}</blockquote>")
        elif line.strip():
            body.append(f"<p>{_inline(line)}</p>")
    flush()

    return _HTML_SHELL.format(title=html.escape(title), body="\n".join(body))


def _inline(text: str) -> str:
    out = html.escape(text)
    while "**" in out:
        out = out.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
    while out.count("`") >= 2:
        out = out.replace("`", "<code>", 1).replace("`", "</code>", 1)
    return out


def load_profiles(paths: list[str]) -> list[dict]:
    out = []
    for p in paths:
        with open(p) as fh:
            data = json.load(fh)
        out.extend(data if isinstance(data, list) else [data])
    return out
