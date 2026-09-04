#!/usr/bin/env python3
"""
session.py -- one folder for the whole trip, and a check that nothing is missing.

    python3 session.py init   --name S1 --out ~/ANC_data --hours 3.5
    python3 session.py status ~/ANC_data/SESSION_S1
    python3 session.py backup ~/ANC_data/SESSION_S1 /Volumes/USB

Files scattered across ad-hoc --out directories is how a range day gets lost.
Everything from one trip lives under one dated folder with a fixed layout, so
the answer to "where is it" is never a guess.

`status` is the one to run BEFORE packing up. It compares what is on disk
against what the plan asked for and prints what is still missing, while a
re-shoot is still possible.
"""

import argparse
import csv
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# Recordings live directly in DATA/ as numbered folders. Only the things that
# are shared across every recording get a folder, and they are '_'-prefixed so
# they sort away from the recordings you actually browse.
LAYOUT = {
    '_calibration':  'calibration tone + calibration.json (once per gain)',
    '_ir':           'range impulse responses (once per trip)',
}

def init(args):
    root = os.path.abspath(os.path.expanduser(args.out))
    existing = [d for d in glob.glob(os.path.join(root, '[0-9]*_*'))
                if os.path.isdir(d)]
    if existing:
        print(f"ERROR: {root} already holds {len(existing)} recording(s).\n"
              "Initialising again would sit on top of them. Use a different\n"
              "--out, or just run capture.py -- it does not need init.",
              file=sys.stderr)
        return 2

    os.makedirs(root, exist_ok=True)
    for d, purpose in LAYOUT.items():
        os.makedirs(os.path.join(root, d), exist_ok=True)
        with open(os.path.join(root, d, 'README.txt'), 'w') as f:
            f.write(purpose + '\n')

    subprocess.run([sys.executable, os.path.join(HERE, 'plan.py'),
                    '--out', os.path.join(root, '_plan'),
                    '--name', args.name, '--hours', str(args.hours)],
                   check=False)
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_signals.py'),
                    '--out', os.path.join(root, '_playback'),
                    '--sr', str(args.sr)], check=False)

    meta = {'name': args.name, 'created': datetime.now().isoformat(),
            'sample_rate': args.sr, 'bit_depth': args.bits,
            'operator': args.operator or '', 'toolkit_dir': HERE,
            'layout': 'recordings are numbered folders directly in this '
                      'directory; _-prefixed folders are shared assets'}
    with open(os.path.join(root, '_DATA.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"\n  data folder ready: {root}\n")
    print(f"    NNN_name/          one folder per recording (capture.py makes these)")
    for d, p in LAYOUT.items():
        print(f"    {d:<18} {p}")
    print(f"    _plan/             RUN_SHEET.txt + metadata_{args.name}.csv")
    print(f"    _playback/         sweep, tones, pink noise, order sheet")
    print(f"\n  PRINT: {os.path.join(root, '_plan', 'RUN_SHEET.txt')}")
    print(f"\n  Now just record -- capture.py handles the rest:\n"
          f"      python3 capture.py --device N\n")
    return 0


def _wavs(d):
    return sorted(glob.glob(os.path.join(d, '*.wav')))


def status(args):
    root = os.path.abspath(os.path.expanduser(args.session))
    if not os.path.isdir(root):
        print(f"ERROR: no such session: {root}", file=sys.stderr)
        return 2

    print(f"\n  {os.path.basename(root)}")
    print("  " + "=" * 66)

    problems, warnings = [], []

    takes = sorted(d for d in glob.glob(os.path.join(root, '[0-9]*_*'))
                   if os.path.isdir(d))
    raw = [os.path.join(t, 'raw.wav') for t in takes
           if os.path.exists(os.path.join(t, 'raw.wav'))]
    print(f"\n  recordings           {len(takes)}")
    if not takes:
        problems.append("nothing recorded yet -- run capture.py")

    # Calibration -- without it every level is relative forever
    cals = glob.glob(os.path.join(root, '_calibration', '*.json'))
    if cals:
        with open(cals[0]) as f:
            c = json.load(f)
        print(f"  calibration          YES   full scale = "
              f"{c.get('full_scale_spl_db', '?')} dB SPL")
        if c.get('warnings'):
            warnings.append(f"calibration has warnings: {c['warnings'][0]}")
    else:
        print(f"  calibration          MISSING")
        problems.append("no calibration.json -- every level stays relative "
                        "and cannot be compared with anything")

    irs = (glob.glob(os.path.join(root, '_ir', '*_ir.json'))
           + glob.glob(os.path.join(root, '[0-9]*_*', 'ir', '*_ir.json')))
    if irs:
        with open(irs[0]) as f:
            ir = json.load(f)
        dnr = ir.get('direct_to_noise_db')
        print(f"  impulse response     YES   RT60 "
              f"{ir.get('rt60_broadband_t20_s')} s, D/N {dnr} dB")
        if dnr is not None and dnr < 35:
            warnings.append(f"IR direct-to-noise is only {dnr} dB -- the RT60 "
                            "is fitting noise; use a balloon pop instead")
    else:
        print(f"  impulse response     MISSING")
        problems.append("no impulse response -- the range acoustics cannot be "
                        "recovered after you leave")

    # Each take carries its own verdict
    nogo, unvalidated = [], []
    for t in takes:
        vj = os.path.join(t, 'validate.json')
        if not os.path.exists(vj):
            unvalidated.append(os.path.basename(t))
            continue
        try:
            with open(vj) as f:
                if json.load(f).get('verdict') == 'NO-GO':
                    nogo.append(os.path.basename(t))
        except (OSError, json.JSONDecodeError):
            unvalidated.append(os.path.basename(t))
    print(f"  validated            {len(takes) - len(unvalidated)} of {len(takes)}"
          + (f"   ({len(unvalidated)} NOT CHECKED)" if unvalidated else ""))
    if unvalidated:
        problems.append(f"{len(unvalidated)} take(s) never validated: "
                        + ", ".join(unvalidated[:3]))
    if nogo:
        problems.append(f"{len(nogo)} take(s) are NO-GO: " + ", ".join(nogo[:3]))

    n_events = sum(len(_wavs(os.path.join(t, 'events'))) for t in takes)
    print(f"  sliced events        {n_events}")

    # Against the plan
    plan_csv = glob.glob(os.path.join(root, '_plan', 'metadata_*.csv'))
    if plan_csv:
        with open(plan_csv[0], newline='') as f:
            rows = list(csv.DictReader(f))
        shot_rows = [r for r in rows if r.get('tier') == 'T1']
        done = sum(1 for r in shot_rows if r.get('timestamp'))
        print(f"  plan                 {len(rows)} events planned "
              f"({len(shot_rows)} shots), {done} logged")
        if done < len(shot_rows):
            warnings.append(f"{len(shot_rows) - done} planned shot row(s) have "
                            "no timestamp filled in")
        holdout = sum(1 for r in rows if r.get('split') == 'holdout')
        if holdout == 0:
            problems.append("no holdout rows -- the comparison will be "
                            "circular and indefensible")
    else:
        warnings.append("no plan CSV found in plan/")

    analysed = sum(1 for t in takes
                   if os.path.exists(os.path.join(t, 'analysis',
                                                  'features.json')))
    print(f"  analysed             {analysed} of {len(takes)}")

    # Size and backup -- one copy of a one-shot session is not a copy
    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fs in os.walk(root) for f in fs)
    print(f"  total size           {total/1e6:.1f} MB")

    bk = os.path.join(root, '.backups.json')
    if os.path.exists(bk):
        with open(bk) as f:
            b = json.load(f)
        print(f"  backups              {len(b)}   last: {b[-1]['when'][:16]} "
              f"-> {b[-1]['dest']}")
    else:
        print(f"  backups              NONE")
        problems.append("no backup taken -- one copy of a trip you cannot "
                        "repeat is not a copy. Run: session.py backup")

    print("\n  " + "=" * 66)
    if problems:
        print(f"  {len(problems)} PROBLEM(S):")
        for p in problems:
            print(f"    * {p}")
    if warnings:
        print(f"  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"    - {w}")
    if not problems and not warnings:
        print("  Session is complete.")
    print()
    return 1 if problems else 0


def backup(args):
    root = os.path.abspath(os.path.expanduser(args.session))
    dest_root = os.path.abspath(os.path.expanduser(args.dest))
    if not os.path.isdir(root):
        print(f"ERROR: no such session: {root}", file=sys.stderr)
        return 2
    if not os.path.isdir(dest_root):
        print(f"ERROR: destination does not exist: {dest_root}\n"
              "Plug the drive in first.", file=sys.stderr)
        return 2

    dest = os.path.join(dest_root, os.path.basename(root))
    print(f"\n  copying {root}\n       -> {dest}")
    shutil.copytree(root, dest, dirs_exist_ok=True)

    # Verify by size and count rather than trusting copytree silently
    def walk(p):
        return {os.path.relpath(os.path.join(dp, f), p): os.path.getsize(
            os.path.join(dp, f)) for dp, _, fs in os.walk(p) for f in fs}
    a, b = walk(root), walk(dest)
    missing = [k for k in a if k not in b or b[k] != a[k]]
    if missing:
        print(f"\n  *** BACKUP INCOMPLETE: {len(missing)} file(s) differ ***")
        for m in missing[:5]:
            print(f"      {m}")
        return 1

    rec = os.path.join(root, '.backups.json')
    hist = []
    if os.path.exists(rec):
        with open(rec) as f:
            hist = json.load(f)
    hist.append({'when': datetime.now().isoformat(), 'dest': dest,
                 'files': len(a), 'bytes': sum(a.values())})
    with open(rec, 'w') as f:
        json.dump(hist, f, indent=2)

    print(f"\n  verified: {len(a)} files, {sum(a.values())/1e6:.1f} MB\n")
    return 0


ENGINE_FILES = ['analyze.py', 'dsp.py', 'wavio.py']


def _sha(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(buf)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _reference_set(root):
    """Everything the reference claim rests on: the audio and the numbers."""
    out = {}
    for p in sorted(glob.glob(os.path.join(root, '[0-9]*_*', '**'),
                              recursive=True)):
        base = os.path.basename(p)
        if not os.path.isfile(p):
            continue
        if base.endswith('README.txt') or base.endswith('.m4a'):
            continue          # listening copies are not part of the reference
        if p.endswith('.wav') or base in ('features.json', 'features.csv',
                                          'manifest.json', 'take.json'):
            out[os.path.relpath(p, root)] = _sha(p)
    return out


def freeze(args):
    """Lock the reference so a later comparison cannot quietly move it.

    A claim that synthetic data matches real data only means something if the
    real side is fixed. This records a checksum of every recording, every
    sliced event and the measured features -- plus a checksum of the
    measurement engine itself, because re-running a modified analyze.py would
    change the numbers without touching a single audio file.
    """
    root = os.path.abspath(os.path.expanduser(args.session))
    lock_path = os.path.join(root, 'REFERENCE.lock')
    if os.path.exists(lock_path) and not args.force:
        print(f"ERROR: {lock_path} already exists.\n"
              "The reference is already frozen. Re-freezing after the fact is\n"
              "exactly what the lock exists to prevent. Pass --force only if\n"
              "you are deliberately starting the reference over.",
              file=sys.stderr)
        return 2

    files = _reference_set(root)
    if not files:
        print("ERROR: nothing to freeze -- no audio or analysis present.",
              file=sys.stderr)
        return 2

    engine = {}
    for fn in ENGINE_FILES:
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            engine[fn] = _sha(p)

    lock = {'frozen': datetime.now().isoformat(),
            'n_files': len(files), 'files': files,
            'engine': engine,
            'note': 'Checksums of the real reference and of the measurement '
                    'engine that produced it. Verify before any comparison.'}
    with open(lock_path, 'w') as f:
        json.dump(lock, f, indent=2)

    print(f"\n  frozen {len(files)} file(s) + {len(engine)} engine file(s)")
    print(f"  -> {lock_path}\n")
    print("  From here on, measure synthetic data with this SAME engine and\n"
          "  run `session.py verify` before quoting any comparison.\n")
    return 0


def verify(args):
    root = os.path.abspath(os.path.expanduser(args.session))
    lock_path = os.path.join(root, 'REFERENCE.lock')
    if not os.path.exists(lock_path):
        print(f"ERROR: no REFERENCE.lock in {root}\n"
              "The reference was never frozen, so there is nothing to verify\n"
              "and no way to show it has not moved. Run: session.py freeze",
              file=sys.stderr)
        return 2
    with open(lock_path) as f:
        lock = json.load(f)

    now = _reference_set(root)
    old = lock['files']
    changed = [k for k in old if k in now and now[k] != old[k]]
    missing = [k for k in old if k not in now]
    added = [k for k in now if k not in old]

    print(f"\n  reference frozen {lock['frozen'][:16]}, "
          f"{lock['n_files']} file(s)")

    engine_changed = []
    for fn, h in lock.get('engine', {}).items():
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            engine_changed.append(f"{fn} (gone)")
        elif _sha(p) != h:
            engine_changed.append(fn)

    ok = True
    if changed:
        ok = False
        print(f"\n  *** {len(changed)} REFERENCE FILE(S) CHANGED ***")
        for k in changed[:8]:
            print(f"      {k}")
        print("  The real data is not what it was when frozen. Any comparison\n"
              "  against it is void until this is explained.")
    if missing:
        ok = False
        print(f"\n  *** {len(missing)} FILE(S) MISSING ***")
        for k in missing[:8]:
            print(f"      {k}")
    if added:
        print(f"\n  {len(added)} file(s) added since freezing "
              "(not part of the reference):")
        for k in added[:5]:
            print(f"      {k}")
    if engine_changed:
        ok = False
        print(f"\n  *** MEASUREMENT ENGINE CHANGED: "
              f"{', '.join(engine_changed)} ***")
        print("  The code that produced these numbers is not the code on disk.\n"
              "  Re-measuring synthetic data with a different engine makes the\n"
              "  comparison meaningless. Restore the engine, or re-freeze and\n"
              "  re-measure BOTH sides.")

    print()
    if ok:
        print("  Reference intact. Safe to compare against.\n")
        return 0
    return 1


LISTEN_README = """\
LISTENING COPIES -- NOT DATA

Compressed copies of the recordings, for playing on a phone, emailing, or
dropping into a slide. They are convenient and they are lossy.

Never measure anything from these files, and never put them in the dataset.
Measured on a real gunshot event at 256 kbps AAC:

  * everything above ~20 kHz is gone (-83 dB at the 32 kHz band), which is
    half the bandwidth the 96 kHz recording exists to capture
  * the spectral centroid moved 248 Hz, against a real shot-to-shot standard
    deviation of 1.4 Hz -- 173 times the variation being measured

Mid-band level and timing survive well, which is exactly what makes this
dangerous: the files sound right.

The real data is in 00_raw/ and 03_events/ as 24-bit WAV.
"""


def listen(args):
    """Make compressed copies for listening, in their own marked folder."""
    root = os.path.abspath(os.path.expanduser(args.session))
    if not os.path.isdir(root):
        print(f"ERROR: no such session: {root}", file=sys.stderr)
        return 2
    if not shutil.which('afconvert'):
        print("ERROR: afconvert not found (macOS built-in).", file=sys.stderr)
        return 2

    out = os.path.join(root, '_listening')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'README.txt'), 'w') as f:
        f.write(LISTEN_README)

    srcs = sorted(glob.glob(os.path.join(root, '[0-9]*_*', 'raw.wav')))
    srcs += sorted(glob.glob(os.path.join(root, '[0-9]*_*', 'events', '*.wav')))
    if not srcs:
        print("ERROR: no WAV files to convert.", file=sys.stderr)
        return 2

    def _sr_of(path):
        r = subprocess.run(['afinfo', path], capture_output=True, text=True)
        for tok in r.stdout.replace(',', ' ').split():
            if tok.isdigit() and 8000 <= int(tok) <= 384000:
                return int(tok)
        return 48000

    n_ok, failed = 0, []
    for src in srcs:
        rel = os.path.relpath(os.path.dirname(src), root)
        d = os.path.join(out, rel)
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, os.path.splitext(os.path.basename(src))[0] + '.m4a')

        # AAC bitrates are constrained by sample rate and channel count: a
        # 16 kHz mono file rejects 256 kbps outright with '!dat'. Cap to
        # something the format will actually accept, then fall back to letting
        # the encoder choose rather than failing the file entirely.
        sr_in = _sr_of(src)
        capped = min(args.bitrate, max(32000, sr_in * 4))
        attempts = [['-b', str(capped)], ['-b', str(min(64000, capped))], []]

        ok = False
        last = ''
        for extra in attempts:
            r = subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac']
                               + extra + [src, dst],
                               capture_output=True, text=True)
            if r.returncode == 0:
                ok = True
                break
            last = r.stderr.strip()
        if ok:
            n_ok += 1
        else:
            failed.append((os.path.basename(src), last[:70]))

    src_bytes = sum(os.path.getsize(p) for p in srcs)
    out_bytes = sum(os.path.getsize(os.path.join(dp, f))
                    for dp, _, fs in os.walk(out) for f in fs)
    if failed:
        print(f"\n  *** {len(failed)} FILE(S) COULD NOT BE CONVERTED ***",
              file=sys.stderr)
        for name, err in failed[:5]:
            print(f"      {name}: {err}", file=sys.stderr)

    print(f"\n  {n_ok} of {len(srcs)} converted")
    print(f"  {src_bytes/1e6:.1f} MB WAV  ->  {out_bytes/1e6:.1f} MB AAC")
    print(f"  -> {out}")
    print(f"\n  These are for LISTENING. The originals are untouched, and the\n"
          f"  dataset stays 24-bit WAV. Read {os.path.join(out, 'README.txt')}\n")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('init', help='create a session folder')
    p.add_argument('--name', default='S1')
    p.add_argument('--out', default='../DATA')
    p.add_argument('--hours', type=float, default=3.5)
    p.add_argument('--sr', type=int, default=96000)
    p.add_argument('--bits', type=int, default=24)
    p.add_argument('--operator', default='')
    p.set_defaults(fn=init)

    p = sub.add_parser('status', help='what is present, what is missing')
    p.add_argument('session')
    p.set_defaults(fn=status)

    p = sub.add_parser('listen', help='compressed copies for playing/sharing')
    p.add_argument('session')
    p.add_argument('--bitrate', type=int, default=256000)
    p.set_defaults(fn=listen)

    p = sub.add_parser('freeze', help='lock the reference before any comparison')
    p.add_argument('session')
    p.add_argument('--force', action='store_true',
                   help='overwrite an existing lock (starts the reference over)')
    p.set_defaults(fn=freeze)

    p = sub.add_parser('verify', help='prove the reference has not moved')
    p.add_argument('session')
    p.set_defaults(fn=verify)

    p = sub.add_parser('backup', help='copy the session and verify it')
    p.add_argument('session')
    p.add_argument('dest')
    p.set_defaults(fn=backup)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
