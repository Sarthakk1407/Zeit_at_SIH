#!/usr/bin/env python3
"""
quicklook.py -- one PNG per event, plus a contact sheet for the whole session.

    python3 quicklook.py good_shots.wav --out looks/      # detect and plot
    python3 quicklook.py events/ --out looks/             # plot sliced events
    python3 quicklook.py events/ --out looks/ --cal calibration.json

Eyes catch things no check does: a doubled report, a ricochet, a shot that
fired while someone was talking. The contact sheet exists so that scanning a
whole session takes ten seconds rather than ten minutes.
"""

import argparse
import glob
import json
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')  # must precede pyplot: there is no display at a range
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import dsp    # noqa: E402


def load_cal(path):
    if not path:
        return None
    with open(path) as f:
        c = json.load(f)
    return float(c['pa_per_fullscale'])


def one_event(x, sr, title, path, scale_pa=None):
    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1.4, 1], hspace=0.42)
    t = np.arange(len(x)) / sr

    # --- waveform
    ax = fig.add_subplot(gs[0])
    ax.plot(t, x, lw=0.4, color='#1f77b4')
    pk = dsp.peak_dbfs(x)
    ax.axhline(1.0, color='r', lw=0.6, ls='--')
    ax.axhline(-1.0, color='r', lw=0.6, ls='--')
    ax.set_ylim(-1.05, 1.05)
    ax.set_ylabel('amplitude')
    ax.grid(alpha=0.3)
    sub = f"peak {pk:.1f} dBFS"
    if scale_pa:
        sub += f"   =  {dsp.spl_from_pa(np.max(np.abs(x)) * scale_pa):.1f} dB SPL peak"
    ax.set_title(f"{title}\n{sub}", fontsize=11, loc='left')

    # --- spectrogram, log frequency
    ax = fig.add_subplot(gs[1])
    nfft = 1024
    f, tt, S = __import__('scipy.signal', fromlist=['spectrogram']).spectrogram(
        x, fs=sr, nperseg=nfft, noverlap=nfft * 3 // 4, scaling='spectrum')
    S_db = 10 * np.log10(S + 1e-20)
    vmax = S_db.max()
    im = ax.pcolormesh(tt, f, S_db, shading='auto',
                       vmin=vmax - 90, vmax=vmax, cmap='magma')
    ax.set_yscale('log')
    ax.set_ylim(20, sr / 2)
    ax.set_ylabel('frequency (Hz)')
    ax.set_xlabel('time (s)')
    fig.colorbar(im, ax=ax, pad=0.01, label='dB')

    # --- 1/3-octave levels
    ax = fig.add_subplot(gs[2])
    centres, levels = dsp.band_levels(x, sr, fraction=3, scale_pa=scale_pa)
    ax.semilogx(centres, levels, 'o-', ms=3, color='#2ca02c')
    ax.set_xlabel('1/3-octave band centre (Hz)')
    ax.set_ylabel('dB SPL' if scale_pa else 'dBFS')
    ax.grid(alpha=0.3, which='both')
    ax.set_xlim(20, sr / 2)

    fig.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def contact_sheet(items, path, cols=4):
    n = len(items)
    if n == 0:
        return
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3.2 * cols, 1.9 * rows),
                             squeeze=False)
    for i, ax in enumerate(axes.flat):
        if i >= n:
            ax.axis('off')
            continue
        name, x, sr = items[i]
        t = np.arange(len(x)) / sr
        clipped = np.any(np.abs(x) >= 0.999)
        ax.plot(t, x, lw=0.3, color='#d62728' if clipped else '#1f77b4')
        ax.set_ylim(-1.05, 1.05)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"{name}  {dsp.peak_dbfs(x):.0f} dBFS"
                     + ("  CLIP" if clipped else ""), fontsize=7)
        for s in ax.spines.values():
            s.set_color('#d62728' if clipped else '#cccccc')
            s.set_linewidth(1.5 if clipped else 0.5)
    fig.suptitle(f"contact sheet -- {n} event(s), red = clipped", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target', help='a WAV file, or a directory of event WAVs')
    ap.add_argument('--out', default='looks')
    ap.add_argument('--cal', help='calibration.json for absolute SPL')
    ap.add_argument('--pre', type=float, default=0.25)
    ap.add_argument('--post', type=float, default=1.50)
    ap.add_argument('--sheet-only', action='store_true',
                    help='skip per-event pages, contact sheet only')
    args = ap.parse_args()

    try:
        scale = load_cal(args.cal)
    except (OSError, KeyError, ValueError) as e:
        print(f"ERROR reading calibration: {e}", file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    items = []

    if not os.path.exists(args.target):
        print(f"ERROR: no such file or directory: {args.target}", file=sys.stderr)
        return 2

    if os.path.isdir(args.target):
        files = sorted(glob.glob(os.path.join(args.target, '*.wav')))
        if not files:
            print(f"ERROR: no .wav files in {args.target}", file=sys.stderr)
            return 2
        for fp in files:
            try:
                d, sr, _ = wavio.read(fp)
            except wavio.WavError as e:
                print(f"  skipping {os.path.basename(fp)}: {e}", file=sys.stderr)
                continue
            items.append((os.path.splitext(os.path.basename(fp))[0],
                          wavio.to_mono(d), sr))
    else:
        try:
            d, sr, info = wavio.read(args.target)
        except (wavio.WavError, FileNotFoundError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        x = wavio.to_mono(d)
        if x.size == 0:
            print(f"ERROR: {args.target} contains no audio", file=sys.stderr)
            return 2
        events = dsp.find_events(x, sr)
        stem = os.path.splitext(os.path.basename(args.target))[0]
        if not len(events):
            print("  no events detected -- plotting the whole file")
            items.append((stem, x, sr))
        else:
            pre_n, post_n = int(args.pre * sr), int(args.post * sr)
            for i, ev in enumerate(events, start=1):
                ev = int(ev)
                a, b = max(0, ev - pre_n), min(x.size, ev + post_n)
                items.append((f"{stem}_ev{i:03d}", x[a:b], sr))

    print(f"\n  {len(items)} event(s) to plot")
    if not args.sheet_only:
        for name, x, sr in items:
            p = os.path.join(args.out, f"{name}.png")
            one_event(x, sr, name, p, scale)
            print(f"    -> {os.path.basename(p)}")

    sheet = os.path.join(args.out, 'contact_sheet.png')
    contact_sheet(items, sheet)
    print(f"\n  -> {sheet}")
    if scale:
        print(f"  levels are absolute SPL (cal: {args.cal})")
    else:
        print("  levels are dBFS -- pass --cal calibration.json for absolute SPL")
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
