#!/usr/bin/env python3
"""Build the handbook pages from their templates and the saved proof logs.

    python build_handbook.py

    src/handbook.html  ->  index.html        the System Handbook
    src/audit.html     ->  zeit-audit.html   the design review (shares the handbook's style)

The handbook's terminal panels are not typed: each is the saved output of a real
run, read from proof/*.txt and inserted as it stands. To refresh one, re-run the
command, save its output over the file, and build again.

    training/           python selftest.py          > handbook/proof/training-selftest.txt
    training/           python bench_latency.py     > handbook/proof/latency-benchmark.txt
    data_collection/    python selftest.py testdata/ > handbook/proof/capture-selftest.txt
    data_collection/    python validate.py good_shots.wav --expect-events 5
    synthetic_generator/experiments/  python p1_normalisation.py
    handbook/proof/     node gunshot_run.mjs        > gunshot-run.txt

Placeholders in the template:
    {{TERM[.wide]|file|folder|command|lines|caption}}   lines = "all" or "2-10,26-36"
    {{SHOTLOG}}   the gunshot run, set as time / lane / event rows
    {{IRTBARS}}   the recovery-time bars, from synthetic_generator/metrics/irt_real.json
    {{DATE}}      today's date
    {{STYLE}}     (audit only) the handbook template's own <style> block
"""
import datetime
import html
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
PROOF = os.path.join(HERE, "proof")
REPO = os.path.dirname(HERE)
PROMPT = "PS D:\\Builds2\\Zeit_at_SIH\\%s> "


def read(name):
    with open(os.path.join(PROOF, name), encoding="utf-8") as f:
        return [l.rstrip() for l in f.read().split("\n")]


def pick(lines, spec):
    """Whole file, or the named 1-based ranges with a dim marker where lines are skipped."""
    if spec == "all":
        while lines and not lines[0].strip():
            lines = lines[1:]
        while lines and not lines[-1].strip():
            lines = lines[:-1]
        return [(l, False) for l in lines]
    out, last = [], None
    for part in spec.split(","):
        a, b = (int(x) for x in part.split("-")) if "-" in part else (int(part), int(part))
        if last is not None and a > last + 1:
            out.append(("    ...", True))
        out += [(l, False) for l in lines[a - 1:b]]
        last = b
    return out


def term(m):
    wide, name, folder, cmd, spec, caption = m.groups()
    rows = pick(read(name), spec)
    first, rest = (cmd.split(" ", 1) + [""])[:2]
    body = ['%s<span class="c">%s</span> %s' % (html.escape(PROMPT % folder.replace("/", "\\")),
                                                 html.escape(first), html.escape(rest))]
    for text, dim in rows:
        body.append('<span class="dim">%s</span>' % html.escape(text) if dim else html.escape(text))
    return ('<figure class="term%s">\n<div class="bar-t"><span class="tab">Windows PowerShell</span>'
            '<span class="ctl">–▢✕</span></div>\n<pre>%s</pre>\n'
            '<figcaption>%s <a href="proof/%s">proof/%s</a></figcaption>\n</figure>'
            % (" wide" if wide else "", "\n".join(body), caption, name, name))


def shotlog(_):
    lines = [l for l in read("gunshot-run.txt") if l.strip()]
    out = ['<div class="shot">']
    for l in lines[:2]:
        out.append('<div class="hd">%s</div>' % html.escape(l))
    for l in lines[2:]:
        m = re.match(r"\s*(T\+[\d.]+ ms)\s+(\S+)\s+(.*)", l)
        if not m:
            continue
        t, k, text = m.groups()
        out.append('<div class="ev"><span class="t">%s</span><span class="k k-%s">%s</span>'
                   '<span>%s</span></div>' % (t, k, k, html.escape(text)))
    out.append("</div>")
    return "\n".join(out)


def irtbars(_):
    with open(os.path.join(REPO, "synthetic_generator", "metrics", "irt_real.json")) as f:
        ev = json.load(f)
    bands = [("125_250", "125–250 Hz"), ("250_500", "250–500 Hz"), ("500_1000", "0.5–1 kHz"),
             ("1000_2000", "1–2 kHz"), ("2000_4000", "2–4 kHz"), ("4000_8000", "4–8 kHz")]
    vals = [statistics.mean(e["irt_%s_ms" % k] for e in ev) for k, _ in bands]
    top = max(vals)
    x0, slot, bw, base, px = 40.0, 472.0 / len(bands), 46.0, 250.0, 156.0 / 450.0
    out = []
    for i, ((_, label), v) in enumerate(zip(bands, vals)):
        x = x0 + i * slot + (slot - bw) / 2
        h = v * px
        peak = v == top
        out.append(
            '<g><title>%s: %.0f ms (mean of %d impulses)</title>'
            '<path d="M%.1f %.1fv%.1fa4 4 0 0 1 4 -4h%.1fa4 4 0 0 1 4 4v%.1fz" fill="var(--%s)"/>'
            '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12.5" font-weight="%s" '
            'fill="var(--ink)">%.0f</text>'
            '<text x="%.1f" y="270" text-anchor="middle" font-size="11.5" font-weight="%s" '
            'fill="var(--%s)">%s</text></g>'
            % (label, v, len(ev), x, base, -(h - 4), bw - 8, h - 4, "blue" if peak else "blue-l",
               x + bw / 2, base - h - 6, "800" if peak else "600", v,
               x + bw / 2, "700" if peak else "400", "ink" if peak else "muted", label))
    out.append('<text x="276" y="292" text-anchor="middle" font-size="11.5" fill="var(--muted)">'
               'frequency band</text>')
    return "\n        ".join(out)


def fill(page):
    page = re.sub(r"\{\{TERM(\.wide)?\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|(.*?)\}\}", term, page)
    if "{{SHOTLOG}}" in page:
        page = page.replace("{{SHOTLOG}}", shotlog(None))
    if "{{IRTBARS}}" in page:
        page = page.replace("{{IRTBARS}}", irtbars(None))
    page = page.replace("{{DATE}}", datetime.date.today().strftime("%d %B %Y").lstrip("0"))
    left = re.findall(r"\{\{[A-Z]+", page)
    if left:
        raise SystemExit("unfilled placeholders: %s" % left)
    return page


def main():
    with open(os.path.join(HERE, "src", "handbook.html"), encoding="utf-8") as f:
        handbook = f.read()
    style = re.search(r"<style>.*?</style>", handbook, flags=re.S).group(0)
    with open(os.path.join(HERE, "src", "audit.html"), encoding="utf-8") as f:
        audit = f.read().replace("{{STYLE}}", style)
    for name, page in (("index.html", handbook), ("zeit-audit.html", audit)):
        page = fill(page)
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
        print("wrote %-16s (%d KB)" % (name, len(page.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
