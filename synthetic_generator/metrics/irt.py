#!/usr/bin/env python3
"""irt.py -- Impulse Recovery Time.

PESQ and STOI average over a whole utterance. A gunshot destroys roughly
200 ms; in a ten-second clip the average barely moves. The standard metrics
hide exactly the damage this problem statement is about.

IRT measures it directly: after an impulse, how long until the signal in each
band comes back to its pre-impulse level?

    python3 irt.py event.wav
    python3 irt.py events/ --csv irt.csv

Reported per octave band and as a single aggregate. Lower is better. A system
that suppresses a gunshot but leaves 400 ms of dead air behind has not solved
the problem the soldier has.

No calibration needed -- IRT is a ratio against each file's own pre-impulse
baseline, so it works on uncalibrated dBFS recordings.
"""
import argparse, csv, json, os, sys
import numpy as np
from scipy.signal import butter, sosfiltfilt

BANDS = [(125, 250), (250, 500), (500, 1000), (1000, 2000),
         (2000, 4000), (4000, 8000)]
RECOVERY = 0.90          # back to 90 % of baseline (in dB terms, see below)
BASELINE_MS = 150.0      # window before onset that defines "normal"
ENV_MS = 5.0             # envelope smoothing


def read_wav(path):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', 'data_collection'))
    import wavio
    x, sr, _ = wavio.read(path)
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x[:, 0]
    return sr, x


def envelope(x, sr, lo, hi):
    ny = sr / 2.0
    hi = min(hi, ny * 0.99)
    if lo >= hi:
        return None
    sos = butter(4, [lo / ny, hi / ny], btype='band', output='sos')
    b = sosfiltfilt(sos, x)
    n = max(1, int(sr * ENV_MS / 1000.0))
    return np.sqrt(np.convolve(b * b, np.ones(n) / n, mode='same')) + 1e-12


def irt_one(path):
    sr, x = read_wav(path)
    if x.size < sr // 4:
        return None
    onset = int(np.argmax(np.abs(x)))
    nb = int(sr * BASELINE_MS / 1000.0)
    if onset < nb + sr // 100:
        return None                      # no clean pre-impulse window

    out, times = {}, []
    for lo, hi in BANDS:
        env = envelope(x, sr, lo, hi)
        if env is None:
            continue
        base = float(np.median(env[onset - nb:onset]))
        peak = float(np.max(env[onset:onset + int(sr * 0.05)]))
        if peak <= base * 2:             # band was not disturbed
            out[f"irt_{lo}_{hi}_ms"] = 0.0
            times.append(0.0)
            continue
        # recovery: envelope back within (1/RECOVERY) of baseline, and stays
        thr = base / RECOVERY
        tail = env[onset:]
        below = tail <= thr
        idx = None
        hold = max(1, int(sr * 0.02))    # must hold 20 ms
        for i in range(len(below) - hold):
            if below[i] and below[i:i + hold].all():
                idx = i
                break
        ms = (idx / sr * 1000.0) if idx is not None else (len(tail) / sr * 1000.0)
        out[f"irt_{lo}_{hi}_ms"] = round(ms, 2)
        times.append(ms)

    out['name'] = os.path.splitext(os.path.basename(path))[0]
    out['irt_mean_ms'] = round(float(np.mean(times)), 2) if times else None
    out['irt_max_ms'] = round(float(np.max(times)), 2) if times else None
    out['sample_rate'] = sr
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target', help='a WAV file or a directory of event WAVs')
    ap.add_argument('--csv')
    ap.add_argument('--json')
    a = ap.parse_args()

    files = ([os.path.join(a.target, f) for f in sorted(os.listdir(a.target))
              if f.lower().endswith('.wav')]
             if os.path.isdir(a.target) else [a.target])

    rows = [r for r in (irt_one(f) for f in files) if r]
    if not rows:
        print("no measurable events (need a clean pre-impulse window)", file=sys.stderr)
        return 1

    mean = [r['irt_mean_ms'] for r in rows if r['irt_mean_ms'] is not None]
    print(f"\n  {len(rows)} event(s)")
    print(f"  IRT mean   {np.mean(mean):8.1f} ms")
    print(f"  IRT median {np.median(mean):8.1f} ms")
    print(f"  IRT p90    {np.percentile(mean, 90):8.1f} ms")
    print(f"  IRT max    {np.max(mean):8.1f} ms\n")
    for lo, hi in BANDS:
        k = f"irt_{lo}_{hi}_ms"
        v = [r[k] for r in rows if k in r]
        if v:
            print(f"    {lo:>5}-{hi:<5} Hz   {np.mean(v):7.1f} ms")

    if a.csv:
        keys = sorted({k for r in rows for k in r})
        with open(a.csv, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        print(f"\n  -> {a.csv}")
    if a.json:
        json.dump(rows, open(a.json, 'w'), indent=2)
        print(f"  -> {a.json}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
