#!/usr/bin/env python3
"""
analyze.py -- the measurement engine. Turns a recording into an acoustic
signature: a fixed set of numbers describing what a gunshot actually is.

    python3 analyze.py events/ --cal calibration.json --label real --out real.json
    python3 analyze.py synth/  --cal calibration.json --label synthetic --out synth.json

This is deliberately ONE engine used for both real and synthetic audio. If the
two were measured by different code, any difference between them would be
partly a difference in the measuring, and the comparison would prove nothing.
Everything downstream -- report.py, compare.py -- reads the JSON this writes.

Metrics are the standard ones for impulse noise so the numbers mean something
to somebody outside this project:
  peak SPL, SEL, Leq          level
  rise time, A- and B-duration  temporal shape
  1/3-octave spectrum          frequency content
  centroid, rolloff, band split  spectral summary
"""

import argparse
import glob
import json
import os
import sys
import numpy as np
from scipy import signal as sg
from scipy.fft import next_fast_len

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import dsp    # noqa: E402
import provenance  # noqa: E402

P_REF = 20e-6
T0 = 1.0  # reference duration for SEL, seconds

SCHEMA = 1  # bump if the feature set changes, so old files are not compared


def envelope(x, sr, smooth_ms=0.5):
    """Analytic (Hilbert) envelope, lightly smoothed.

    Hilbert rather than a moving RMS because rise time and A-duration are
    sub-millisecond quantities: a 5 ms RMS window would smear the very thing
    being measured.
    """
    n = len(x)
    # Hilbert is O(n log n) but pads to a fast length internally; help it.
    nfast = next_fast_len(n)
    env = np.abs(sg.hilbert(x, N=nfast))[:n]
    w = max(int(smooth_ms * 1e-3 * sr), 1)
    if w > 1:
        env = np.convolve(env, np.ones(w) / w, mode='same')
    return env


def temporal_features(x, sr):
    """Rise time, A-duration, B-duration, crest factor."""
    env = envelope(x, sr)
    pk_i = int(np.argmax(env))
    pk = float(env[pk_i])
    out = {}

    if pk <= 0:
        return {'rise_time_ms': None, 'a_duration_ms': None,
                'b_duration_ms': None, 'crest_factor_db': None,
                'peak_index': pk_i}

    # Rise time: 10% -> 90% of peak amplitude, on the leading edge only
    lead = env[:pk_i + 1]
    try:
        i10 = int(np.flatnonzero(lead >= 0.10 * pk)[0])
        i90 = int(np.flatnonzero(lead >= 0.90 * pk)[0])
        out['rise_time_ms'] = round((i90 - i10) / sr * 1e3, 4)
    except IndexError:
        out['rise_time_ms'] = None

    # A-duration: the initial positive pressure phase of the blast wave --
    # from the pressure leaving zero to its first return to zero.
    sign = np.sign(x[pk_i])
    j = pk_i
    while j > 0 and np.sign(x[j]) == sign:
        j -= 1
    k = pk_i
    while k < len(x) - 1 and np.sign(x[k]) == sign:
        k += 1
    out['a_duration_ms'] = round((k - j) / sr * 1e3, 4)

    # B-duration: total time the envelope stays within 20 dB of the peak.
    # The standard impulse-noise measure of how long the event actually lasts.
    thr = pk * 10 ** (-20.0 / 20.0)
    out['b_duration_ms'] = round(float(np.sum(env >= thr)) / sr * 1e3, 4)

    r = dsp.rms(x)
    out['crest_factor_db'] = (round(20 * np.log10(pk / r), 2)
                              if r > 0 else None)

    # Kurtosis of the pressure signal: the standard impulsiveness descriptor
    # in noise-exposure work. Gaussian noise sits at 3; a gunshot is orders of
    # magnitude above it. Crest factor says how tall the peak is, kurtosis says
    # how much of the record is peak -- they are not the same claim.
    xm = x - np.mean(x)
    var = float(np.mean(xm ** 2))
    out['kurtosis'] = (round(float(np.mean(xm ** 4) / (var ** 2)), 2)
                       if var > 0 else None)

    out['peak_index'] = pk_i
    return out


def level_features(x, sr, scale_pa):
    """Peak, SEL and Leq. Absolute SPL when calibrated, else dBFS."""
    pk = float(np.max(np.abs(x)))
    energy = float(np.sum(x * x)) / sr  # integral of x^2 dt

    if scale_pa:
        p_pk = pk * scale_pa
        peak = 20 * np.log10(max(p_pk, dsp.EPS) / P_REF)
        sel = 10 * np.log10(max(energy * scale_pa ** 2, dsp.EPS)
                            / (T0 * P_REF ** 2))
        leq = 10 * np.log10(max(energy / (len(x) / sr) * scale_pa ** 2,
                                dsp.EPS) / P_REF ** 2)
        unit = 'dB SPL (re 20 uPa)'
    else:
        peak = 20 * np.log10(max(pk, dsp.EPS))
        sel = 10 * np.log10(max(energy / T0, dsp.EPS))
        leq = 10 * np.log10(max(energy / (len(x) / sr), dsp.EPS))
        unit = 'dBFS (UNCALIBRATED)'

    return {'peak_db': round(peak, 2), 'sel_db': round(sel, 2),
            'leq_db': round(leq, 2), 'level_unit': unit,
            'calibrated': bool(scale_pa)}


def spectral_features(x, sr, scale_pa):
    """1/3-octave spectrum plus centroid, rolloff and a coarse band split."""
    centres, levels = dsp.band_levels(x, sr, fraction=3, scale_pa=scale_pa)

    # Welch PSD for the summary statistics -- more stable than a single FFT
    nper = min(4096, len(x))
    f, pxx = sg.welch(x, fs=sr, nperseg=nper)
    tot = float(np.sum(pxx))
    if tot <= 0:
        return {'third_octave_hz': centres.round(1).tolist(),
                'third_octave_db': [None] * len(centres),
                'centroid_hz': None, 'rolloff95_hz': None,
                'peak_freq_hz': None, 'band_split_db': {}}

    centroid = float(np.sum(f * pxx) / tot)
    cum = np.cumsum(pxx) / tot
    rolloff = float(f[int(np.argmax(cum >= 0.95))])
    peak_f = float(f[int(np.argmax(pxx))])

    edges = [(0, 100), (100, 1000), (1000, 8000), (8000, sr / 2)]
    split = {}
    for lo, hi in edges:
        m = (f >= lo) & (f < hi)
        frac = float(np.sum(pxx[m]) / tot) if np.any(m) else 0.0
        key = f"{int(lo)}_{int(hi)}Hz"
        split[key] = round(10 * np.log10(max(frac, 1e-12)), 2)

    return {'third_octave_hz': centres.round(1).tolist(),
            'third_octave_db': [round(float(v), 2) for v in levels],
            'centroid_hz': round(centroid, 1),
            'rolloff95_hz': round(rolloff, 1),
            'peak_freq_hz': round(peak_f, 1),
            'band_split_db': split}


def analyze_one(x, sr, name, scale_pa):
    if x.size < sr // 100:
        return None
    feat = {'name': name, 'sample_rate': sr,
            'duration_s': round(len(x) / sr, 4)}
    feat.update(level_features(x, sr, scale_pa))
    feat.update(temporal_features(x, sr))
    feat.update(spectral_features(x, sr, scale_pa))
    return feat


def collect(target, sr_expect, pre, post):
    """Yield (name, mono_signal, sr) for a file or a directory of files."""
    if not os.path.exists(target):
        raise ValueError(f"no such file or directory: {target}")
    if os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, '*.wav')))
        if not files:
            raise ValueError(f"no .wav files in {target}")
        for fp in files:
            d, sr, _ = wavio.read(fp)
            yield os.path.splitext(os.path.basename(fp))[0], wavio.to_mono(d), sr
    else:
        d, sr, _ = wavio.read(target)
        x = wavio.to_mono(d)
        events = dsp.find_events(x, sr)
        stem = os.path.splitext(os.path.basename(target))[0]
        if not len(events):
            yield stem, x, sr
        else:
            for i, ev in enumerate(events, start=1):
                ev = int(ev)
                a, b = max(0, ev - int(pre * sr)), min(x.size, ev + int(post * sr))
                yield f"{stem}_ev{i:03d}", x[a:b], sr


def aggregate(feats):
    """Mean and spread of the scalar features across events.

    The spread matters as much as the mean: it is the tolerance any synthetic
    generator has to land inside before a match can be claimed.
    """
    keys = ['peak_db', 'sel_db', 'leq_db', 'rise_time_ms', 'a_duration_ms',
            'b_duration_ms', 'crest_factor_db', 'kurtosis', 'centroid_hz',
            'rolloff95_hz', 'peak_freq_hz']
    out = {}
    for k in keys:
        vals = [f[k] for f in feats if f.get(k) is not None]
        if vals:
            out[k] = {'mean': round(float(np.mean(vals)), 3),
                      'std': round(float(np.std(vals)), 3),
                      'min': round(float(np.min(vals)), 3),
                      'max': round(float(np.max(vals)), 3),
                      'n': len(vals)}

    spectra = [f['third_octave_db'] for f in feats
               if f.get('third_octave_db') and None not in f['third_octave_db']]
    if spectra:
        arr = np.array(spectra, dtype=float)
        out['third_octave_hz'] = feats[0]['third_octave_hz']
        out['third_octave_mean_db'] = np.mean(arr, axis=0).round(2).tolist()
        out['third_octave_std_db'] = np.std(arr, axis=0).round(2).tolist()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target', help='event WAV, or a directory of event WAVs')
    ap.add_argument('--cal', help='calibration.json, for absolute SPL')
    ap.add_argument('--label', default='real',
                    help='what this set is, e.g. real / synthetic / v2')
    ap.add_argument('--out', default='features.json')
    ap.add_argument('--csv', help='also write a flat CSV of the scalar features')
    ap.add_argument('--allow-synthetic', action='store_true',
                    help='permit synthetic test data, and stamp the output as '
                         'not being measurements')
    ap.add_argument('--pre', type=float, default=0.25)
    ap.add_argument('--post', type=float, default=1.50)
    args = ap.parse_args()

    synthetic = provenance.guard(args.target, 'analyze.py',
                                 allowed=args.allow_synthetic)

    scale_pa = None
    if args.cal:
        try:
            with open(args.cal) as f:
                scale_pa = float(json.load(f)['pa_per_fullscale'])
        except (OSError, KeyError, ValueError) as e:
            print(f"ERROR reading calibration: {e}", file=sys.stderr)
            return 2

    try:
        items = list(collect(args.target, None, args.pre, args.post))
    except (ValueError, FileNotFoundError, wavio.WavError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    feats = []
    for name, x, sr in items:
        f = analyze_one(x, sr, name, scale_pa)
        if f:
            feats.append(f)

    if not feats:
        print("ERROR: nothing analysable found", file=sys.stderr)
        return 2

    agg = aggregate(feats)
    doc = {'schema': SCHEMA, 'label': args.label,
           'source': os.path.abspath(args.target),
           'synthetic_test_data': synthetic,
           'calibrated': bool(scale_pa),
           'n_events': len(feats), 'aggregate': agg, 'events': feats}
    with open(args.out, 'w') as f:
        json.dump(doc, f, indent=2)

    unit = feats[0]['level_unit']
    print(f"\n  {args.label}: {len(feats)} event(s)   levels in {unit}")
    if not scale_pa:
        print("  WARNING: uncalibrated. Levels are relative and cannot be\n"
              "           compared against anything measured elsewhere.")
    print(f"\n  {'metric':<20} {'mean':>10} {'std':>8} {'min':>10} {'max':>10}")
    print(f"  {'-'*20} {'-'*10} {'-'*8} {'-'*10} {'-'*10}")
    for k in ['peak_db', 'sel_db', 'leq_db', 'rise_time_ms', 'a_duration_ms',
              'b_duration_ms', 'crest_factor_db', 'kurtosis', 'centroid_hz',
              'rolloff95_hz']:
        if k in agg:
            a = agg[k]
            print(f"  {k:<20} {a['mean']:>10.2f} {a['std']:>8.2f} "
                  f"{a['min']:>10.2f} {a['max']:>10.2f}")

    if args.csv:
        import csv as _csv
        cols = ['name', 'peak_db', 'sel_db', 'leq_db', 'rise_time_ms',
                'a_duration_ms', 'b_duration_ms', 'crest_factor_db',
                'kurtosis', 'centroid_hz', 'rolloff95_hz', 'peak_freq_hz',
                'duration_s']
        with open(args.csv, 'w', newline='') as f:
            w = _csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
            w.writeheader()
            w.writerows(feats)
        print(f"\n  -> {args.csv}")
    print(f"  -> {args.out}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
