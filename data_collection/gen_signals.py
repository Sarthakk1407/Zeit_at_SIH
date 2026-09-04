#!/usr/bin/env python3
"""
gen_signals.py -- generate the playback signals to take to the range.

Run this at home, the day before. Copy the output folder to the phone/laptop
you will play from. Nothing here needs to run at the range.

    python3 gen_signals.py --out playback/
"""

import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402


def log_sweep(sr, f1=20.0, f2=20000.0, dur=10.0, pad=0.5, fade=0.05,
              amplitude=0.5):
    """Farina exponential sine sweep plus its matched inverse filter.

    Returns (sweep_with_pad, inverse_filter). Convolving the two gives a
    band-limited unit impulse, which is what ir_extract.py relies on.
    """
    f2 = min(f2, sr / 2.0 * 0.98)
    n = int(round(dur * sr))
    t = np.arange(n) / sr
    w1, w2 = 2 * np.pi * f1, 2 * np.pi * f2
    K = np.log(w2 / w1)
    L = dur / K
    sweep = np.sin(w1 * L * (np.exp(t / L) - 1.0))

    # Fade the ends or the loudspeaker will click and smear the IR
    nf = int(round(fade * sr))
    if nf > 0:
        ramp = 0.5 * (1 - np.cos(np.pi * np.arange(nf) / nf))
        sweep[:nf] *= ramp
        sweep[-nf:] *= ramp[::-1]

    # Inverse: time-reversed sweep with a -6 dB/octave amplitude envelope,
    # which undoes the sweep's pink energy distribution.
    inv = sweep[::-1] * np.exp(-t / L)

    # Normalise so that conv(sweep, inv) peaks at exactly 1.0
    nfft = int(2 ** np.ceil(np.log2(2 * n)))
    conv = np.fft.irfft(np.fft.rfft(sweep, nfft) * np.fft.rfft(inv, nfft), nfft)
    peak = np.max(np.abs(conv))
    if peak > 0:
        inv = inv / peak

    npad = int(round(pad * sr))
    out = np.concatenate([np.zeros(npad), sweep * amplitude, np.zeros(npad)])
    return out, inv


def cal_tone(sr, freq=1000.0, dur=30.0, dbfs=-20.0, fade=0.05):
    n = int(round(dur * sr))
    t = np.arange(n) / sr
    amp = 10.0 ** (dbfs / 20.0) * np.sqrt(2.0)  # dBFS is RMS; convert to peak
    x = amp * np.sin(2 * np.pi * freq * t)
    nf = int(round(fade * sr))
    if nf > 0:
        ramp = 0.5 * (1 - np.cos(np.pi * np.arange(nf) / nf))
        x[:nf] *= ramp
        x[-nf:] *= ramp[::-1]
    return x


def pink_noise(sr, dur=30.0, dbfs=-20.0, seed=0):
    """Pink noise by 1/sqrt(f) shaping in the frequency domain."""
    rng = np.random.default_rng(seed)
    n = int(round(dur * sr))
    white = rng.standard_normal(n)
    spec = np.fft.rfft(white)
    f = np.fft.rfftfreq(n, 1.0 / sr)
    shape = np.ones_like(f)
    shape[1:] = 1.0 / np.sqrt(f[1:])
    shape[0] = 0.0  # kill DC
    x = np.fft.irfft(spec * shape, n)
    r = np.sqrt(np.mean(x * x))
    if r > 0:
        x = x / r * 10.0 ** (dbfs / 20.0)
    return np.clip(x, -1.0, 1.0)


SHEET = """
==========================================================================
 PLAYBACK ORDER SHEET  --  keep this on the table, tick each line
==========================================================================
 Session: ____________   Date: ____________   Operator: ________________
 Recorder gain setting: ______   Sample rate: {sr} Hz   Depth: 24-bit

 Play each file ONCE through the speaker. Keep the recorder rolling the
 whole time. Announce the file name out loud before playing it -- the
 slate is what saves you when the file names get confused later.

 --------------------------------------------------------------------
 [ ]  1. cal_1k_-20dBFS.wav    30 s   Note SPL meter reading: ______ dB
 [ ]  2. cal_1k_-12dBFS.wav    30 s   Note SPL meter reading: ______ dB
 [ ]  3. cal_1k_-06dBFS.wav    30 s   Note SPL meter reading: ______ dB
          -> run: python3 calibrate.py <file> --spl-db <reading>

 [ ]  4. MIC COVERED, 60 s of silence. No speaking. Noise floor.
          -> run: python3 validate.py <file>

 [ ]  5. sweep_20-20k_10s.wav  11 s   Speaker at 1 m, ON-AXIS
          -> mic response reference

 [ ]  6. sweep_20-20k_10s.wav  11 s   Speaker AT THE FIRING POINT
          -> range impulse response. THIS IS THE ONE THAT MATTERS.
          -> run: python3 ir_extract.py <file> --inverse inverse_filter.wav

 [ ]  7. BALLOON POP at the firing point, x3
          -> backup IR if the sweep is ruined by wind or traffic

 [ ]  8. pink_30s.wav          30 s   Speaker at firing point
          -> spectral cross-check on the IR

 --------------------------------------------------------------------
 AFTER EVERY SOURCE CHANGE, AND AFTER THE FIRST 3 SHOTS:
     python3 validate.py <most recent file>
 If it says NO-GO, fix it NOW. There is no second visit.
 --------------------------------------------------------------------
 Wind speed at start: ______ km/h    Temp: ______ C   Humidity: ______ %
 Wind speed at end:   ______ km/h    Temp: ______ C   Humidity: ______ %
==========================================================================
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='playback', help='output directory')
    ap.add_argument('--sr', type=int, default=96000, help='sample rate (Hz)')
    ap.add_argument('--bits', '--bit-depth', type=int, default=24,
                    choices=[16, 24, 32], dest='bits',
                    help='sample depth (--bit-depth is accepted too)')
    ap.add_argument('--sweep-dur', type=float, default=10.0)
    ap.add_argument('--tone-dur', type=float, default=30.0)
    ap.add_argument('--noise-dur', type=float, default=30.0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    sr, bd = args.sr, args.bits

    print(f"Generating playback signals at {sr} Hz / {bd}-bit into {args.out}/")

    sweep, inv = log_sweep(sr, dur=args.sweep_dur)
    wavio.write(os.path.join(args.out, 'sweep_20-20k_10s.wav'), sweep, sr, bd)
    # The inverse filter is a processing asset, not something you play.
    # Float32 keeps its huge dynamic range intact.
    wavio.write(os.path.join(args.out, 'inverse_filter.wav'), inv, sr, 'float32')
    print(f"  sweep_20-20k_10s.wav   {len(sweep)/sr:6.2f} s")
    print(f"  inverse_filter.wav     {len(inv)/sr:6.2f} s  (float32, do NOT play)")

    for level in (-20, -12, -6):
        x = cal_tone(sr, dur=args.tone_dur, dbfs=float(level))
        name = f"cal_1k_-{abs(level):02d}dBFS.wav"
        wavio.write(os.path.join(args.out, name), x, sr, bd)
        print(f"  {name:22s} {len(x)/sr:6.2f} s  RMS {level} dBFS")

    pn = pink_noise(sr, dur=args.noise_dur)
    wavio.write(os.path.join(args.out, 'pink_30s.wav'), pn, sr, bd)
    print(f"  pink_30s.wav           {len(pn)/sr:6.2f} s")

    sheet_path = os.path.join(args.out, 'PLAYBACK_ORDER.txt')
    with open(sheet_path, 'w') as f:
        f.write(SHEET.format(sr=sr))
    print(f"\n  {sheet_path}  <- PRINT THIS. Paper, not phone.")

    # Self-check: the whole point of the inverse filter is that it collapses
    # the sweep to an impulse. Prove it here, not at the range.
    n = len(sweep) + len(inv)
    nfft = int(2 ** np.ceil(np.log2(n)))
    imp = np.fft.irfft(np.fft.rfft(sweep, nfft) * np.fft.rfft(inv, nfft), nfft)
    pk = int(np.argmax(np.abs(imp)))
    main_lobe = np.abs(imp[max(0, pk - 20):pk + 20])
    side = np.abs(np.delete(np.abs(imp), slice(max(0, pk - 200), pk + 200)))
    ratio = 20 * np.log10(main_lobe.max() / max(side.max(), 1e-20))
    print(f"\n  self-check: sweep * inverse -> impulse, "
          f"peak/sidelobe = {ratio:.1f} dB", end='')
    print("  OK" if ratio > 40 else "  *** SUSPECT ***")


if __name__ == '__main__':
    main()
