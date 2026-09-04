#!/usr/bin/env python3
"""
ir_extract.py -- recover the range impulse response and its RT60.

Sweep method (preferred):
    python3 ir_extract.py sweep_recorded.wav --inverse inverse_filter.wav

Balloon-pop fallback, when wind or traffic ruined the sweep:
    python3 ir_extract.py balloon_pop.wav --balloon

The IR is what lets the synthetic training data carry the acoustics of a real
range. Getting it is the single highest-value thing on the range-day list
after the shots themselves, because it cannot be recovered afterwards.
"""

import argparse
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import dsp    # noqa: E402

OCTAVES = [62.5, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]


def deconvolve(rec, inv):
    """Linear (not circular) deconvolution of the sweep recording."""
    n = len(rec) + len(inv) - 1
    nfft = int(2 ** np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(rec, nfft) * np.fft.rfft(inv, nfft), nfft)


def trim_ir(ir, sr, pre_ms=5.0, length_s=3.0):
    """Cut the IR to start just before the direct sound."""
    pk = int(np.argmax(np.abs(ir)))
    a = max(0, pk - int(pre_ms * 1e-3 * sr))
    b = min(len(ir), a + int(length_s * sr))
    return ir[a:b], pk


def band_rt60(ir, sr):
    """RT60 per octave band via Schroeder integration. Reports T20 and T30."""
    rows = []
    for fc in OCTAVES:
        if fc * 1.5 >= sr / 2:
            continue
        lo, hi = dsp.band_edges(fc, fraction=1)
        y = dsp.bandpass(ir, sr, lo, hi)
        edc = dsp.schroeder_edc(y, sr)
        t20, r20 = dsp.rt60_from_edc(edc, sr, -5.0, -25.0)
        t30, r30 = dsp.rt60_from_edc(edc, sr, -5.0, -35.0)
        rows.append({'band_hz': fc, 't20_s': t20, 't20_r2': r20,
                     't30_s': t30, 't30_r2': r30})
    return rows


def plot(ir, sr, rows, path, title):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(3, 1, figsize=(9, 10))
    t = np.arange(len(ir)) / sr

    ax[0].plot(t, ir, lw=0.5, color='#1f77b4')
    ax[0].set_title(f"{title} -- impulse response")
    ax[0].set_xlabel('time (s)')
    ax[0].set_ylabel('amplitude')
    ax[0].grid(alpha=0.3)

    edc = dsp.schroeder_edc(ir, sr)
    ax[1].plot(t, edc, color='#d62728')
    ax[1].axhline(-5, ls='--', c='gray', lw=0.8)
    ax[1].axhline(-25, ls='--', c='gray', lw=0.8)
    ax[1].axhline(-35, ls=':', c='gray', lw=0.8)
    ax[1].set_ylim(-70, 2)
    ax[1].set_title('energy decay curve (broadband)')
    ax[1].set_xlabel('time (s)')
    ax[1].set_ylabel('dB')
    ax[1].grid(alpha=0.3)

    f = [r['band_hz'] for r in rows]
    t20 = [r['t20_s'] for r in rows]
    t30 = [r['t30_s'] for r in rows]
    ax[2].semilogx(f, t20, 'o-', label='T20')
    ax[2].semilogx(f, t30, 's--', label='T30')
    ax[2].set_xticks(f)
    ax[2].set_xticklabels([f"{int(x)}" for x in f])
    ax[2].set_title('reverberation time per octave band')
    ax[2].set_xlabel('band centre (Hz)')
    ax[2].set_ylabel('RT60 (s)')
    ax[2].grid(alpha=0.3, which='both')
    ax[2].legend()

    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('wav', help='sweep recording, or balloon pop with --balloon')
    ap.add_argument('--inverse', help='inverse filter from gen_signals.py')
    ap.add_argument('--balloon', action='store_true',
                    help='treat the input as a direct impulse, no deconvolution')
    ap.add_argument('--out', default='ir_out', help='output directory')
    ap.add_argument('--length', type=float, default=3.0, help='IR length (s)')
    args = ap.parse_args()

    if not args.balloon and not args.inverse:
        print("ERROR: give --inverse FILE, or --balloon for the fallback path",
              file=sys.stderr)
        return 2

    try:
        rec, sr, info = wavio.read(args.wav)
    except (wavio.WavError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    rec = wavio.to_mono(rec)
    if rec.size == 0:
        print(f"ERROR: {args.wav} contains no audio", file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.wav))[0]

    if args.balloon:
        method = 'balloon-pop (direct window)'
        ir, pk = trim_ir(rec, sr, length_s=args.length)
    else:
        try:
            inv, inv_sr, _ = wavio.read(args.inverse)
        except (wavio.WavError, FileNotFoundError) as e:
            print(f"ERROR reading inverse filter: {e}", file=sys.stderr)
            return 2
        inv = wavio.to_mono(inv)
        if inv_sr != sr:
            print(f"ERROR: sample-rate mismatch -- recording is {sr} Hz but the "
                  f"inverse filter is {inv_sr} Hz. Deconvolution would be "
                  "meaningless.", file=sys.stderr)
            return 2
        method = 'exponential sweep (Farina deconvolution)'
        full = deconvolve(rec, inv)
        ir, pk = trim_ir(full, sr, length_s=args.length)

    peak = np.max(np.abs(ir))
    if peak > 0:
        ir = ir / peak

    # Direct-to-noise: if the tail never gets clear of the floor the RT60 fit
    # is fitting noise, and the number would be fiction.
    tail = ir[-int(0.2 * sr):] if len(ir) > int(0.2 * sr) else ir[-10:]
    dnr = 20 * np.log10(1.0 / (dsp.rms(tail) + dsp.EPS))

    rows = band_rt60(ir, sr)
    broadband_t20, r2 = dsp.rt60_from_edc(dsp.schroeder_edc(ir, sr), sr)

    ir_path = os.path.join(args.out, f"{stem}_ir.wav")
    png_path = os.path.join(args.out, f"{stem}_ir.png")
    json_path = os.path.join(args.out, f"{stem}_ir.json")
    wavio.write(ir_path, ir, sr, 'float32')
    plot(ir, sr, rows, png_path, stem)

    valid = [r['t20_s'] for r in rows if np.isfinite(r['t20_s'])]
    result = {
        'source_file': os.path.abspath(args.wav),
        'method': method,
        'sample_rate': sr,
        'ir_length_s': len(ir) / sr,
        'direct_to_noise_db': round(float(dnr), 1),
        'rt60_broadband_t20_s': (round(float(broadband_t20), 3)
                                 if np.isfinite(broadband_t20) else None),
        'bands': [{k: (round(v, 4) if isinstance(v, float) and np.isfinite(v)
                       else (None if isinstance(v, float) else v))
                   for k, v in r.items()} for r in rows],
    }
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n  method              {method}")
    print(f"  direct-to-noise     {dnr:.1f} dB"
          + ("" if dnr > 35 else "   <-- LOW, RT60 below is unreliable"))
    print(f"  broadband RT60(T20) "
          + (f"{broadband_t20:.3f} s  (fit r2={r2:.3f})"
             if np.isfinite(broadband_t20) else "could not fit"))
    print(f"\n  {'band':>7}  {'T20':>7}  {'T30':>7}   fit quality")
    for r in rows:
        q = ('good' if (np.isfinite(r['t20_r2']) and r['t20_r2'] > 0.98)
             else 'poor')
        def _s(v):
            return f"{v:7.3f}" if np.isfinite(v) else '    n/a'
        print(f"  {int(r['band_hz']):>7}  {_s(r['t20_s'])}  "
              f"{_s(r['t30_s'])}   {q}")
    if valid:
        print(f"\n  mean T20 across bands: {np.mean(valid):.3f} s")
    print(f"\n  -> {ir_path}\n  -> {png_path}\n  -> {json_path}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
