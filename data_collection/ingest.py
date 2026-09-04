#!/usr/bin/env python3
"""
ingest.py -- slice one long take into per-event files and bind them to metadata.

    python3 ingest.py long_session.wav --meta long_session_meta.csv --out events/

Recording one continuous take and cutting it afterwards beats stopping and
starting between shots: you cannot fumble a file name mid-string, and the
background between events is preserved, which is what the noise model needs.

The metadata CSV must have a shot_id column. Every other column is carried
through to the manifest untouched, so the schema can grow without touching
this tool.
"""

import argparse
import csv
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import dsp    # noqa: E402
import provenance  # noqa: E402


def read_meta(path):
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} has no data rows")
    if 'shot_id' not in rows[0]:
        raise ValueError(f"{path} has no shot_id column "
                         f"(found: {', '.join(rows[0].keys())})")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('wav', help='the long continuous recording')
    ap.add_argument('--meta', help='metadata CSV, one row per event')
    ap.add_argument('--out', default='events', help='output directory')
    ap.add_argument('--pre', type=float, default=0.25,
                    help='seconds kept before each onset (default 0.25)')
    ap.add_argument('--post', type=float, default=1.50,
                    help='seconds kept after each onset (default 1.50)')
    ap.add_argument('--min-sep', type=float, default=0.30,
                    help='minimum spacing between events (default 0.30 s)')
    ap.add_argument('--prominence', type=float, default=12.0,
                    help='dB above background to count as an event')
    ap.add_argument('--dry-run', action='store_true',
                    help='detect and report, write nothing')
    ap.add_argument('--allow-synthetic', action='store_true',
                    help='permit synthetic test data (marks the output too)')
    args = ap.parse_args()

    synthetic = provenance.guard(args.wav, 'ingest.py',
                                 allowed=args.allow_synthetic)

    try:
        data, sr, info = wavio.read(args.wav)
    except (wavio.WavError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    x = wavio.to_mono(data)
    if x.size == 0:
        print(f"ERROR: {args.wav} contains no audio", file=sys.stderr)
        return 2

    meta = None
    if args.meta:
        try:
            meta = read_meta(args.meta)
        except (ValueError, FileNotFoundError, OSError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    events = dsp.find_events(x, sr, min_sep_s=args.min_sep,
                             prominence_db=args.prominence)
    print(f"\n  {os.path.basename(args.wav)}: {info['duration_s']:.1f} s, "
          f"{len(events)} event(s) detected")

    mismatch = False
    if meta is not None:
        if len(meta) != len(events):
            mismatch = True
            print(f"\n  *** COUNT MISMATCH ***")
            print(f"      metadata rows : {len(meta)}")
            print(f"      events found  : {len(events)}")
            print("      Events are matched to rows IN ORDER, so a mismatch")
            print("      means every pairing after the gap is wrong. Check the")
            print("      detection with --dry-run before trusting any of it.")
            if len(events) > len(meta):
                print("      More events than rows: likely a double-count or a")
                print("      thump misread as a shot. Try --prominence 15.")
            else:
                print("      Fewer events than rows: a shot was too quiet to")
                print("      detect. Try --prominence 9.")

    pre_n, post_n = int(args.pre * sr), int(args.post * sr)
    os.makedirs(args.out, exist_ok=True) if not args.dry_run else None

    manifest = []
    print(f"\n  {'shot_id':<14} {'onset':>9}  {'peak':>9}  {'SNR':>7}  file")
    print(f"  {'-'*14} {'-'*9}  {'-'*9}  {'-'*7}  {'-'*28}")

    env_db, _ = dsp.moving_rms_db(x, sr)
    floor_db = float(np.percentile(env_db, 10.0))

    for i, ev in enumerate(events):
        ev = int(ev)  # numpy ints leak np.bool_ into the manifest and json dies
        row = meta[i] if (meta is not None and i < len(meta)) else {}
        shot_id = row.get('shot_id') or f"EVENT-{i+1:03d}"

        a = max(0, ev - pre_n)
        b = min(x.size, ev + post_n)
        clip = x[a:b]

        pk = dsp.peak_dbfs(clip)
        snr = pk - floor_db
        # Trust the file, not the log sheet: clipping is measured, not claimed.
        clipped = bool(np.any(np.abs(clip) >= 1.0 - info['lsb'])) \
            if info['format'] != 'float' else bool(np.any(np.abs(clip) >= 0.999))

        name = f"{shot_id}.wav"
        path = os.path.join(args.out, name)
        if not args.dry_run:
            wavio.write(path, clip, sr, 24 if info['format'] != 'float' else 'float32')

        entry = dict(row)
        entry.update({
            'shot_id': shot_id,
            'file': name,
            'source_recording': os.path.basename(args.wav),
            'onset_s': round(ev / sr, 4),
            'clip_start_s': round(a / sr, 4),
            'clip_end_s': round(b / sr, 4),
            'duration_s': round((b - a) / sr, 4),
            'sample_rate_hz': sr,
            'peak_dbfs': round(float(pk), 2),
            'snr_db': round(float(snr), 1),
            'clipped_measured': 'yes' if clipped else 'no',
            'truncated': bool((b - a) < (pre_n + post_n)),
        })
        manifest.append(entry)

        flag = ' CLIPPED' if clipped else ''
        print(f"  {shot_id:<14} {ev/sr:8.3f}s  {pk:8.1f}dB  {snr:6.1f}dB  "
              f"{name}{flag}")

    if not args.dry_run:
        if synthetic:
            provenance.mark(args.out)   # the marker travels with the slices
        mpath = os.path.join(args.out, 'manifest.json')
        with open(mpath, 'w') as f:
            json.dump({'source': os.path.abspath(args.wav),
                       'synthetic_test_data': synthetic,
                       'sample_rate': sr,
                       'noise_floor_dbfs': round(floor_db, 2),
                       'n_events': len(events),
                       'n_meta_rows': len(meta) if meta is not None else None,
                       'count_mismatch': mismatch,
                       'events': manifest}, f, indent=2)
        print(f"\n  -> {len(manifest)} file(s) + manifest.json in {args.out}/")
    else:
        print(f"\n  dry run -- nothing written")

    n_clipped = sum(1 for m in manifest if m['clipped_measured'] == 'yes')
    if n_clipped:
        print(f"  WARNING: {n_clipped} event(s) are clipped and cannot be used "
              "for peak-level work")
    print()
    return 1 if mismatch else 0


if __name__ == '__main__':
    sys.exit(main())
