#!/usr/bin/env python3
"""
calibrate.py -- turn dBFS into absolute pressure.

Without this, every level in the dataset is relative and no peak SPL claim can
be made. Record the 1 kHz tone, read the SPL meter at the microphone, and give
both to this tool.

    python3 calibrate.py cal_tone_recorded.wav --spl-db 94.0

Writes calibration.json. Every later tool takes --cal calibration.json to
report absolute SPL instead of dBFS.
"""

import argparse
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import dsp    # noqa: E402

P_REF = 20e-6


def steady_segment(x, sr, freq, trim_s=1.0):
    """The middle of the tone, band-limited around the calibration frequency.

    Trimming the ends drops the fades and any handling at the start; the
    band-pass keeps range noise out of the level measurement.
    """
    a = int(trim_s * sr)
    b = len(x) - int(trim_s * sr)
    if b - a < sr // 2:
        a, b = 0, len(x)
    seg = x[a:b]
    return dsp.bandpass(seg, sr, freq / 1.5, freq * 1.5), (a, b)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('wav', help='recording of the calibration tone')
    ap.add_argument('--spl-db', type=float, required=True,
                    help='SPL meter reading at the mic, dB re 20 uPa')
    ap.add_argument('--freq', type=float, default=1000.0)
    ap.add_argument('--out', default='calibration.json')
    ap.add_argument('--weighting', default='Z', choices=['Z', 'A', 'C'],
                    help='weighting the SPL meter was set to (recorded only)')
    args = ap.parse_args()

    try:
        data, sr, info = wavio.read(args.wav)
    except (wavio.WavError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    x = wavio.to_mono(data)
    if x.size == 0:
        print(f"ERROR: {args.wav} contains no audio", file=sys.stderr)
        return 2

    seg, (a, b) = steady_segment(x, sr, args.freq)
    rms_fs = dsp.rms(seg)
    if rms_fs <= 0:
        print("ERROR: calibration tone is silent -- wrong file?", file=sys.stderr)
        return 2

    rms_dbfs = 20 * np.log10(rms_fs)
    pa_rms = P_REF * 10 ** (args.spl_db / 20.0)
    scale = pa_rms / rms_fs                     # Pa per unit of full scale
    full_scale_spl = 20 * np.log10(scale / P_REF)

    # Sanity: full scale should land somewhere a real recorder can sit. Below
    # 100 dB means the tone was far too quiet or the meter reading is wrong;
    # above 180 dB is past what any microphone survives.
    warnings = []
    if not (100.0 <= full_scale_spl <= 180.0):
        warnings.append(
            f"full-scale SPL of {full_scale_spl:.1f} dB is implausible -- "
            "check the meter reading and that this is the right file")
    if rms_dbfs > -3.0:
        warnings.append(f"tone is very hot ({rms_dbfs:.1f} dBFS), may be clipped")
    if rms_dbfs < -50.0:
        warnings.append(f"tone is very quiet ({rms_dbfs:.1f} dBFS), poor SNR")

    # How pure is it? A dirty tone means the meter and the file disagree.
    tot = dsp.rms(x[a:b])
    purity = 20 * np.log10((rms_fs + dsp.EPS) / (tot + dsp.EPS))
    if purity < -3.0:
        warnings.append(f"only {10**(purity/10)*100:.0f}% of energy is at "
                        f"{args.freq:.0f} Hz -- noisy calibration")

    out = {
        'source_file': os.path.abspath(args.wav),
        'sample_rate': sr,
        'cal_frequency_hz': args.freq,
        'spl_meter_db': args.spl_db,
        'weighting': args.weighting,
        'tone_rms_dbfs': round(float(rms_dbfs), 3),
        'pa_per_fullscale': float(scale),
        'full_scale_spl_db': round(float(full_scale_spl), 2),
        'warnings': warnings,
    }
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=2)

    print(f"\n  tone level          {rms_dbfs:8.2f} dBFS")
    print(f"  SPL meter said      {args.spl_db:8.2f} dB ({args.weighting})")
    print(f"  scale factor        {scale:.6g} Pa per full scale")
    print(f"  full scale (1.0) =  {full_scale_spl:8.2f} dB SPL")
    print(f"\n  -> {args.out}")
    if warnings:
        print("\n  WARNINGS:")
        for w in warnings:
            print(f"    * {w}")
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
