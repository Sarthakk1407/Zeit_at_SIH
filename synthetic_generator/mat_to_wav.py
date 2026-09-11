#!/usr/bin/env python3
"""mat_to_wav.py -- NOISEX-92 ships as MATLAB .mat files. Turn them into WAV.

    python3 mat_to_wav.py "/Volumes/ZEIT V.1.0/zeit-data/NOISEX92"

NOISEX-92 is sampled at 19.98 kHz. The .mat files hold one variable each, a
single vector of samples. Written out as 16-bit PCM WAV so every other tool in
the toolkit can read them.
"""
import argparse, os, sys
import numpy as np
from scipy.io import loadmat

SR = 19980   # NOISEX-92 sample rate

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder')
    ap.add_argument('--sr', type=int, default=SR)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data_collection'))
    import wavio

    mats = sorted(f for f in os.listdir(a.folder) if f.lower().endswith('.mat'))
    if not mats:
        print("no .mat files here"); return 1
    print(f"\n  {len(mats)} .mat files in {a.folder}\n")
    print(f"  {'file':<20}{'samples':>10}{'seconds':>9}{'peak':>8}")
    for m in mats:
        d = loadmat(os.path.join(a.folder, m))
        keys = [k for k in d if not k.startswith('__')]
        if not keys:
            print(f"  {m:<20}  no data variable"); continue
        x = np.asarray(d[keys[0]], dtype=np.float64).squeeze()
        if x.ndim > 1: x = x[:, 0]
        pk = float(np.max(np.abs(x))) or 1.0
        x = (x / pk) * 0.98                      # normalise, leave headroom
        out = os.path.join(a.folder, os.path.splitext(m)[0] + ".wav")
        wavio.write(out, x, a.sr, bit_depth=16)
        print(f"  {m:<20}{len(x):>10,}{len(x)/a.sr:>9.1f}{pk:>8.3f}  -> {os.path.basename(out)}")
    print(f"\n  done. WAVs written at {a.sr} Hz, 16-bit.\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
