#!/usr/bin/env python3
"""
report.py -- turn a measured session into one self-contained HTML page.

    python3 report.py features.json --audio events/ --out report.html

Reads what analyze.py wrote and renders the session's acoustic signature: the
1/3-octave spectrum with its spread, the scalar metrics event by event, and a
waveform sheet. Everything is embedded as base64, so the page is a single file
that opens with no internet and no server -- which is the only kind of report
that is any use at a range.

This describes REAL measured data. It is the reference the dataset is judged
against later; it makes no claims about synthetic audio.
"""

import argparse
import base64
import io
import json
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402

# Validated reference palette. The report commits to a single light look: it is
# a measurement document meant to be printed and put in front of judges, and a
# baked PNG cannot follow a theme toggle anyway.
SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK2 = '#52514e'
MUTED = '#8a8981'
GRID = '#e5e4df'
SERIES1 = '#2a78d6'
SERIES1_FILL = '#9ec5f4'
GOOD = '#0ca30c'
WARN = '#fab219'
CRIT = '#d03b3b'

plt.rcParams.update({
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
    'savefig.facecolor': SURFACE,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
    'text.color': INK, 'xtick.color': INK2, 'ytick.color': INK2,
    'grid.color': GRID, 'grid.linewidth': 0.8,
    'axes.spines.top': False, 'axes.spines.right': False,
    'font.size': 9, 'axes.titlesize': 10, 'axes.titleweight': 'semibold',
    'axes.titlelocation': 'left', 'axes.titlepad': 10,
    'lines.linewidth': 2.0, 'lines.markersize': 5,
})


def fig_to_uri(fig, dpi=120):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def hz_fmt(v, _pos=None):
    if v >= 1000:
        return f"{v/1000:g}k"
    return f"{v:g}"


def fig_signature(doc):
    """The headline chart: mean 1/3-octave spectrum with its spread.

    One series, so no legend box -- the title names it. The shaded band is the
    same hue as the line because it is the same quantity's uncertainty, not a
    second series.
    """
    agg = doc['aggregate']
    if 'third_octave_mean_db' not in agg:
        return None
    f = np.array(agg['third_octave_hz'], dtype=float)
    m = np.array(agg['third_octave_mean_db'], dtype=float)
    s = np.array(agg['third_octave_std_db'], dtype=float)

    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.fill_between(f, m - s, m + s, color=SERIES1_FILL, alpha=0.55, lw=0,
                    zorder=1)
    ax.semilogx(f, m, color=SERIES1, zorder=3, solid_capstyle='round')
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(FuncFormatter(hz_fmt))
    ax.set_xlabel('1/3-octave band centre (Hz)')
    unit = 'dB SPL' if doc.get('calibrated') else 'dBFS (uncalibrated)'
    ax.set_ylabel(unit)
    ax.set_title(f"Measured spectrum — mean of {doc['n_events']} events, "
                 "shaded ±1 s.d.")
    ax.grid(True, which='both', axis='y', alpha=0.7)
    ax.grid(True, which='major', axis='x', alpha=0.5)
    ax.set_axisbelow(True)

    # Label the peak band directly rather than numbering every point
    i = int(np.argmax(m))
    rel = (m[i] - m.min()) / max(float(np.ptp(m)), 1e-9)
    dy = -16 if rel > 0.8 else 10          # keep it clear of the title
    ax.annotate(f"peak {m[i]:.0f} {unit.split()[0]} @ {hz_fmt(f[i])}Hz",
                xy=(f[i], m[i]), xytext=(10, dy), textcoords='offset points',
                color=INK2, fontsize=8.5)
    return fig_to_uri(fig)


def fig_consistency(doc):
    """Per-event scalars as small multiples.

    The spread here is the tolerance any later synthetic generator has to land
    inside, so it is worth seeing event by event rather than as one number.
    """
    metrics = [('peak_db', 'Peak level'), ('sel_db', 'SEL'),
               ('rise_time_ms', 'Rise time (ms)'),
               ('b_duration_ms', 'B-duration (ms)'),
               ('crest_factor_db', 'Crest factor (dB)'),
               ('centroid_hz', 'Spectral centroid (Hz)')]
    have = [(k, t) for k, t in metrics if k in doc['aggregate']]
    if not have:
        return None

    n = len(have)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(9.5, 2.5 * rows),
                             squeeze=False)
    for ax, (key, title) in zip(axes.flat, have):
        vals = [e.get(key) for e in doc['events']]
        idx = [i + 1 for i, v in enumerate(vals) if v is not None]
        vv = [v for v in vals if v is not None]
        a = doc['aggregate'][key]
        ax.axhspan(a['mean'] - a['std'], a['mean'] + a['std'],
                   color=SERIES1_FILL, alpha=0.45, lw=0)
        ax.axhline(a['mean'], color=SERIES1, lw=1.5)
        ax.plot(idx, vv, 'o', color=SERIES1, markersize=5,
                markeredgecolor=SURFACE, markeredgewidth=1.2)
        ax.set_title(title)
        ax.set_xlabel('event')
        ax.grid(True, axis='y', alpha=0.7)
        ax.set_axisbelow(True)
        ax.margins(x=0.12)

        # A metric with (near-)zero spread would otherwise auto-scale to its
        # own rounding noise, and matplotlib would add a "+7.531" offset --
        # so a perfectly repeatable measurement reads as wild scatter. Floor
        # the half-range at 1% of the mean so flat looks flat.
        ax.ticklabel_format(useOffset=False, style='plain', axis='y')
        lo, hi = min(vv), max(vv)
        centre = 0.5 * (lo + hi)
        half = max(0.75 * (hi - lo), abs(a['mean']) * 0.01, 1e-9)
        ax.set_ylim(centre - half, centre + half)
        if a['std'] < abs(a['mean']) * 1e-4:
            ax.text(0.5, 0.06, 'no measurable variation', ha='center',
                    transform=ax.transAxes, fontsize=8, color=MUTED)
    for ax in axes.flat[n:]:
        ax.axis('off')
    fig.tight_layout()
    return fig_to_uri(fig)


def fig_waveforms(audio_dir, doc, limit=12):
    """Waveform sheet, so the eye can catch what no metric does."""
    import glob
    files = sorted(glob.glob(os.path.join(audio_dir, '*.wav')))[:limit]
    if not files:
        return None
    cols = 4
    rows = int(np.ceil(len(files) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(9.5, 1.7 * rows),
                             squeeze=False)
    for ax, fp in zip(axes.flat, files):
        try:
            d, sr, _ = wavio.read(fp)
        except wavio.WavError:
            ax.axis('off')
            continue
        x = wavio.to_mono(d)
        t = np.arange(len(x)) / sr
        clipped = bool(np.any(np.abs(x) >= 0.999))
        ax.plot(t, x, lw=0.35, color=CRIT if clipped else SERIES1)
        ax.set_ylim(-1.05, 1.05)
        ax.set_xticks([])
        ax.set_yticks([])
        name = os.path.splitext(os.path.basename(fp))[0]
        ax.set_title(f"{name}{'  CLIPPED' if clipped else ''}", fontsize=7.5,
                     color=CRIT if clipped else INK2)
        for sp in ax.spines.values():
            sp.set_color(CRIT if clipped else GRID)
    for ax in axes.flat[len(files):]:
        ax.axis('off')
    fig.tight_layout()
    return fig_to_uri(fig)


CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin:0; background:#f4f4f1; color:#0b0b0b;
  font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
.wrap { max-width:1000px; margin:0 auto; padding:32px 24px 80px; }
header { border-bottom:2px solid #0b0b0b; padding-bottom:16px; margin-bottom:28px; }
h1 { margin:0 0 4px; font-size:24px; letter-spacing:-0.01em; }
.sub { color:#52514e; font-size:13px; }
h2 { font-size:15px; margin:34px 0 12px; letter-spacing:-0.005em; }
.card { background:#fcfcfb; border:1px solid #e5e4df; border-radius:10px;
  padding:18px; margin-bottom:18px; }
.tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:12px; margin-bottom:22px; }
.tile { background:#fcfcfb; border:1px solid #e5e4df; border-radius:10px; padding:14px 16px; }
.tile .k { font-size:11px; text-transform:uppercase; letter-spacing:.06em;
  color:#8a8981; margin-bottom:6px; }
.tile .v { font-size:24px; font-weight:600; letter-spacing:-0.02em; }
.tile .u { font-size:12px; color:#52514e; font-weight:400; margin-left:3px; }
img { width:100%; display:block; border-radius:6px; }
table { border-collapse:collapse; width:100%; font-size:12.5px; }
th,td { text-align:right; padding:7px 10px; border-bottom:1px solid #e5e4df; }
th:first-child, td:first-child { text-align:left; }
th { font-weight:600; color:#52514e; font-size:11px; text-transform:uppercase;
  letter-spacing:.05em; }
tbody tr:hover { background:#f4f4f1; }
.scroll { overflow-x:auto; }
.note { font-size:12.5px; color:#52514e; }
.badge { display:inline-block; padding:3px 9px; border-radius:999px;
  font-size:11px; font-weight:600; }
.badge.good { background:#e6f6e6; color:#0a7d0a; }
.badge.crit { background:#fbe9e9; color:#b32f2f; }
.synthetic { background:#d03b3b; color:#fff; padding:14px 18px; border-radius:10px;
  margin-bottom:22px; font-weight:600; font-size:14px; }
.synthetic span { display:block; font-weight:400; font-size:12.5px;
  margin-top:5px; opacity:.92; }
.foot { margin-top:40px; padding-top:16px; border-top:1px solid #e5e4df;
  font-size:12px; color:#8a8981; }
"""


def tile(k, v, u=''):
    return (f'<div class="tile"><div class="k">{k}</div>'
            f'<div class="v">{v}<span class="u">{u}</span></div></div>')


def scalar_table(doc):
    rows = []
    labels = {'peak_db': 'Peak level', 'sel_db': 'SEL', 'leq_db': 'Leq',
              'rise_time_ms': 'Rise time (ms)',
              'a_duration_ms': 'A-duration (ms)',
              'b_duration_ms': 'B-duration (ms)',
              'crest_factor_db': 'Crest factor (dB)',
              'centroid_hz': 'Spectral centroid (Hz)',
              'rolloff95_hz': '95% rolloff (Hz)',
              'peak_freq_hz': 'Peak frequency (Hz)'}
    for k, lab in labels.items():
        a = doc['aggregate'].get(k)
        if not a:
            continue
        rows.append(f"<tr><td>{lab}</td><td>{a['mean']:.2f}</td>"
                    f"<td>{a['std']:.2f}</td><td>{a['min']:.2f}</td>"
                    f"<td>{a['max']:.2f}</td><td>{a['n']}</td></tr>")
    return ("<div class='scroll'><table><thead><tr><th>Metric</th><th>Mean</th>"
            "<th>s.d.</th><th>Min</th><th>Max</th><th>n</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def spectrum_table(doc):
    agg = doc['aggregate']
    if 'third_octave_mean_db' not in agg:
        return ''
    f = agg['third_octave_hz']
    m = agg['third_octave_mean_db']
    s = agg['third_octave_std_db']
    rows = ''.join(f"<tr><td>{hz_fmt(fi)}</td><td>{mi:.2f}</td>"
                   f"<td>{si:.2f}</td></tr>" for fi, mi, si in zip(f, m, s))
    return ("<div class='scroll'><table><thead><tr><th>Band (Hz)</th>"
            "<th>Mean level</th><th>s.d.</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")


def build(doc, audio_dir, out):
    cal = doc.get('calibrated')
    agg = doc['aggregate']
    unit = 'dB SPL' if cal else 'dBFS'

    tiles = [tile('Events measured', doc['n_events'])]
    if 'peak_db' in agg:
        tiles.append(tile('Mean peak', f"{agg['peak_db']['mean']:.1f}", unit))
    if 'sel_db' in agg:
        tiles.append(tile('Mean SEL', f"{agg['sel_db']['mean']:.1f}", unit))
    if 'rise_time_ms' in agg:
        tiles.append(tile('Rise time', f"{agg['rise_time_ms']['mean']:.2f}", 'ms'))
    if 'centroid_hz' in agg:
        tiles.append(tile('Centroid', f"{agg['centroid_hz']['mean']:.0f}", 'Hz'))

    badge = ('<span class="badge good">CALIBRATED</span>' if cal else
             '<span class="badge crit">UNCALIBRATED</span>')
    calnote = ('' if cal else
               '<div class="card"><span class="badge crit">UNCALIBRATED</span> '
               '<span class="note">Levels are relative to full scale and cannot '
               'be compared with any measurement made elsewhere, including a '
               'later synthetic set. Record the calibration tone and re-run '
               '<code>calibrate.py</code>, then regenerate this report.</span></div>')

    synth_banner = ('<div class="synthetic">SYNTHETIC TEST DATA — NOT A MEASUREMENT'
                    '<span>Generated by make_test_data.py to exercise the toolkit. '
                    'Nothing on this page describes anything that was recorded. '
                    'It must not be used as a reference or shown as a result.</span>'
                    '</div>') if doc.get('synthetic_test_data') else ''

    parts = [f"<header><h1>Acoustic signature — {doc['label']}</h1>",
             f"<div class='sub'>{doc['n_events']} measured events &middot; "
             f"{badge} &middot; source <code>{os.path.basename(doc['source'])}</code>"
             "</div></header>",
             f"<div class='tiles'>{''.join(tiles)}</div>", calnote]

    sig = fig_signature(doc)
    if sig:
        parts.append("<h2>Spectrum</h2><div class='card'>"
                     f"<img src='{sig}' alt='Mean 1/3-octave spectrum with "
                     "plus or minus one standard deviation'></div>")
        parts.append("<div class='card'>" + spectrum_table(doc) + "</div>")

    con = fig_consistency(doc)
    if con:
        parts.append("<h2>Event-to-event consistency</h2>"
                     "<p class='note'>Each dot is one event; the line is the "
                     "mean and the band is ±1 s.d. A wide band means the "
                     "measurement is not yet repeatable — check the geometry "
                     "and the gain before trusting it as a reference.</p>"
                     f"<div class='card'><img src='{con}' alt='Per-event values "
                     "for each scalar metric'></div>")

    parts.append("<h2>Measured values</h2><div class='card'>"
                 + scalar_table(doc) + "</div>")

    if audio_dir and os.path.isdir(audio_dir):
        wf = fig_waveforms(audio_dir, doc)
        if wf:
            parts.append("<h2>Waveforms</h2><p class='note'>Red outline marks a "
                         "clipped event: its peak is destroyed and it must not "
                         "be used for level work.</p>"
                         f"<div class='card'><img src='{wf}' alt='Waveform of "
                         "each event'></div>")

    parts.append("<div class='foot'>Generated by report.py from analyze.py "
                 "output. All levels measured with a single pipeline so that "
                 "later comparisons measure the audio, not the method.</div>")

    title_prefix = ('SYNTHETIC — ' if doc.get('synthetic_test_data') else '')
    html = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{title_prefix}Acoustic signature — {doc['label']}</title>"
            f"<style>{CSS}</style></head><body><div class='wrap'>"
            + ''.join(parts) + "</div></body></html>")
    with open(out, 'w') as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('features', help='features.json from analyze.py')
    ap.add_argument('--audio', help='directory of event WAVs, for the waveform sheet')
    ap.add_argument('--out', default='report.html')
    args = ap.parse_args()

    try:
        with open(args.features) as f:
            doc = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR reading {args.features}: {e}", file=sys.stderr)
        return 2
    if 'aggregate' not in doc or 'events' not in doc:
        print(f"ERROR: {args.features} is not analyze.py output", file=sys.stderr)
        return 2

    build(doc, args.audio, args.out)
    size = os.path.getsize(args.out) / 1024
    print(f"\n  -> {args.out}   ({size:.0f} KB, self-contained)\n"
          f"     open it with:  open {args.out}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
