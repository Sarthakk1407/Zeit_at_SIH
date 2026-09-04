#!/usr/bin/env python3
"""
capture.py -- one command for one take. Watch it, name it, and it processes itself.

    python3 capture.py --device 3

Opens the live monitor. Everything you see is being recorded. Close the window
and it asks what the take was, files it under its own name, and runs the whole
pipeline: validate, slice, measure, plot, report, compressed copy.

    python3 capture.py --device 3 --name "air rifle 5m"     # skip the prompt
    python3 capture.py --device 3 --type cal --spl-db 94.0  # calibration tone
    python3 capture.py --device 3 --type ir                 # sweep or balloon

Every take gets its own folder, numbered in order, so a session of forty takes
stays legible:

    takes/003_air-rifle-5m/
        raw.wav          the recording, untouched
        validate.json    the GO / NO-GO verdict
        events/          per-shot slices + manifest
        analysis/        features.json + .csv
        report.html      open this
        quicklook/       waveform + spectrogram per event
        listening/       compressed copy for playing
        take.json        what this take was
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def slug(text):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', (text or '').strip().lower())
    return re.sub(r'-+', '-', s).strip('-')[:48]


def find_data_root(explicit):
    """The DATA folder. Recordings live directly inside it, numbered.

    Organised by recording, not by session: a session wrapper buries the thing
    you actually look for. Session-wide assets (calibration, impulse response,
    plan, playback) sit in _-prefixed folders so they sort out of the way.
    """
    if explicit:
        p = os.path.abspath(os.path.expanduser(explicit))
    else:
        p = os.path.join(os.path.dirname(HERE), 'DATA')
    if not os.path.isdir(p):
        print(f"ERROR: no DATA folder at {p}\n"
              f"Make one first:\n"
              f"    python3 session.py init --out {p}", file=sys.stderr)
        sys.exit(2)
    return p


def next_number(root):
    n = 0
    for d in os.listdir(root):
        m = re.match(r'^(\d+)_', d)
        if m and os.path.isdir(os.path.join(root, d)):
            n = max(n, int(m.group(1)))
    return n + 1


def write_index(root):
    """One readable listing of every recording, newest last."""
    rows = []
    for d in sorted(glob.glob(os.path.join(root, '[0-9]*_*'))):
        tj = os.path.join(d, 'take.json')
        if not os.path.isdir(d) or not os.path.exists(tj):
            continue
        try:
            with open(tj) as f:
                t = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        n_ev = len(glob.glob(os.path.join(d, 'events', '*.wav')))
        rows.append((t.get('number', 0), os.path.basename(d),
                     t.get('type', '?'), t.get('verdict', '?'),
                     t.get('recorded', '')[:16].replace('T', ' '),
                     t.get('sample_rate_actual', '?'), n_ev,
                     'yes' if t.get('calibrated') else 'no'))
    lines = ['# Recordings', '',
             f'{len(rows)} recording(s) in `{os.path.basename(root)}/`', '',
             '| # | folder | type | verdict | when | rate | events | cal |',
             '|---|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r[0]:03d} | `{r[1]}` | {r[2]} | **{r[3]}** | "
                     f"{r[4]} | {r[5]} | {r[6]} | {r[7]} |")
    ok = sum(1 for r in rows if r[3] == 'GO')
    lines += ['', f'{ok} GO, {len(rows) - ok} NO-GO.', '',
              'Session-wide assets are in the `_`-prefixed folders.']
    with open(os.path.join(root, '_index.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


def run(args_list, label, quiet=False):
    r = subprocess.run([sys.executable] + args_list, cwd=HERE,
                       capture_output=True, text=True)
    mark = 'ok  ' if r.returncode == 0 else 'FAIL'
    print(f"    [{mark}] {label}")
    if r.returncode != 0 and not quiet:
        tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
        for line in tail:
            print(f"           {line}")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--device', required=True,
                    help='device number OR part of its name, e.g. "MacBook" -- '
                         'a name is safer, numbers shift when devices come and go')
    ap.add_argument('--device2', metavar='DEV',
                    help='ALSO record a second device in parallel (its own file). '
                         'Two separate streams, so they are not sample-locked -- '
                         'align on the impulse if you need them together. Use it '
                         'for redundancy: if one clips, the other survives.')
    ap.add_argument('--sr2', type=int,
                    help='sample rate for --device2 (default: its native rate)')
    ap.add_argument('--data', help='DATA folder (default: ../DATA)')
    ap.add_argument('--name', help='name the take, skipping the prompt')
    ap.add_argument('--type', default='shot',
                    choices=['shot', 'cal', 'ir', 'ambience', 'speech', 'mech'],
                    help='what this take is (default: shot)')
    ap.add_argument('--sr', type=int, default=96000)
    ap.add_argument('--channels', type=int, default=1)
    ap.add_argument('--test-mode', action='store_true')
    ap.add_argument('--duration', type=float,
                    help='auto-close the window after about N seconds')
    ap.add_argument('--expect-events', type=int, default=0,
                    help='how many shots you fired into this take')
    ap.add_argument('--spl-db', type=float, help='SPL meter reading, for --type cal')
    ap.add_argument('--inverse', help='inverse filter, for --type ir')
    args = ap.parse_args()

    root = find_data_root(args.data)
    num = next_number(root)

    print(f"\n  data    : {root}")
    print(f"  recording: {num:03d}  ({args.type})")
    print(f"\n  Opening the monitor. Everything you see is being recorded.")
    print(f"  Close the window when the take is done.\n")

    scratch = os.path.join(root, '.capture')
    os.makedirs(scratch, exist_ok=True)
    tmp = os.path.join(scratch, f'{num:03d}.wav')
    if os.path.exists(tmp):
        os.remove(tmp)

    mon = ['monitor.py', '--device', str(args.device), '--sr', str(args.sr),
           '--channels', str(args.channels), '--record', tmp]
    if args.test_mode:
        mon += ['--test-mode', '--no-mark']
    if args.duration:
        mon += ['--duration', str(args.duration)]
    # Second device, recorded in this process while the monitor window owns the
    # first. Started before the window opens and stopped when it closes, so the
    # two files cover the same take even though they are separate streams.
    tmp2 = None
    stream2 = take2 = None
    if args.device2:
        sys.path.insert(0, HERE)
        import sounddevice as _sd
        import record as _R
        dev2 = _R.resolve_device(_sd, args.device2)
        info2 = _sd.query_devices(dev2, 'input')
        sr2 = args.sr2 or int(info2['default_samplerate'])
        ch2 = int(info2['max_input_channels'])
        take2 = []

        def _cb2(indata, frames, t, status):
            take2.append(indata.copy())

        try:
            stream2 = _sd.InputStream(device=dev2, channels=ch2, samplerate=sr2,
                                      dtype='float32', blocksize=2048,
                                      callback=_cb2)
            stream2.start()
            print(f"  also recording: {info2['name']} @ {sr2} Hz, {ch2} ch")
        except Exception as e:
            print(f"  second device FAILED to start: {e}", file=sys.stderr)
            stream2 = None

    r = subprocess.run([sys.executable] + mon, cwd=HERE)

    if stream2 is not None:
        try:
            stream2.stop()
            stream2.close()
        except Exception:
            pass
        if take2:
            import numpy as _np
            import wavio as _w
            tmp2 = os.path.join(scratch, f'{num:03d}_dev2.wav')
            _w.write(tmp2, _np.concatenate(take2, axis=0).astype(_np.float64),
                     sr2, 24)
            print(f"  second device: {sum(len(b) for b in take2)/sr2:.2f} s captured")
        else:
            print("  second device captured nothing", file=sys.stderr)

    if not os.path.exists(tmp):
        print("\n  Nothing was recorded -- no folder created.\n", file=sys.stderr)
        return 2

    # --- name it
    name = args.name
    if not name and sys.stdin.isatty():
        try:
            name = input(f"\n  Name this recording [take-{num:03d}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            name = ''
    label = slug(name) or f"take-{num:03d}"
    folder = os.path.join(root, f"{num:03d}_{label}")
    os.makedirs(folder, exist_ok=True)

    raw = os.path.join(folder, 'raw.wav')
    os.replace(tmp, raw)
    if tmp2 and os.path.exists(tmp2):
        os.replace(tmp2, os.path.join(folder, 'raw_device2.wav'))
    if args.test_mode:
        sys.path.insert(0, HERE)
        import provenance
        provenance.mark(folder)      # this recording only, never the DATA root

    # Validate against the rate the file ACTUALLY has, not the one requested.
    # A device that cannot do 96 kHz records at its own rate (test mode falls
    # back deliberately), and checking against the request then fails every
    # take for a mismatch the operator did not cause.
    sys.path.insert(0, HERE)
    import wavio
    _, actual_sr, _ = wavio.read(raw)
    if actual_sr != args.sr:
        print(f"\n  note: recorded at {actual_sr} Hz, not the {args.sr} Hz "
              f"requested -- checking against {actual_sr} Hz")
    print(f"\n  -> {os.path.basename(folder)}/raw.wav")
    print(f"\n  processing:")

    # --- the pipeline
    val_json = os.path.join(folder, 'validate.json')
    vargs = ['validate.py', raw, '--no-color', '--json', val_json,
             '--expect-sr', str(actual_sr), '--expect-bits', '24']
    if args.channels > 1:
        vargs.append('--array')
    if args.expect_events:
        vargs += ['--expect-events', str(args.expect_events)]
    rv = run(vargs, 'validate', quiet=True)
    verdict = 'NO-GO' if rv.returncode == 1 else ('ERROR' if rv.returncode else 'GO')

    cal = os.path.join(root, '_calibration', 'calibration.json')
    has_cal = os.path.exists(cal)

    if args.type == 'cal':
        if args.spl_db is None:
            print("    [--  ] calibrate: needs --spl-db <meter reading>")
        else:
            os.makedirs(os.path.dirname(cal), exist_ok=True)
            run(['calibrate.py', raw, '--spl-db', str(args.spl_db),
                 '--out', cal], 'calibrate -> _calibration/calibration.json')
            has_cal = os.path.exists(cal)
    elif args.type == 'ir':
        irargs = ['ir_extract.py', raw, '--out', os.path.join(folder, 'ir')]
        irargs += ['--inverse', args.inverse] if args.inverse else ['--balloon']
        run(irargs, 'impulse response')
    else:
        ev = os.path.join(folder, 'events')
        ing = ['ingest.py', raw, '--out', ev, '--allow-synthetic']
        run(ing, 'slice events', quiet=True)

        target = ev if glob.glob(os.path.join(ev, '*.wav')) else raw
        feats = os.path.join(folder, 'analysis', 'features.json')
        os.makedirs(os.path.dirname(feats), exist_ok=True)
        aargs = ['analyze.py', target, '--label', label, '--out', feats,
                 '--csv', feats.replace('.json', '.csv'), '--allow-synthetic']
        if has_cal:
            aargs += ['--cal', cal]
        run(aargs, 'measure' + ('' if has_cal else '  (uncalibrated)'))

        if os.path.exists(feats):
            rargs = ['report.py', feats, '--out', os.path.join(folder, 'report.html')]
            if target != raw:
                rargs += ['--audio', ev]
            run(rargs, 'report.html')
        run(['quicklook.py', target, '--out', os.path.join(folder, 'quicklook')]
            + (['--cal', cal] if has_cal else []), 'quicklook')

    # --- take record
    meta = {'number': num, 'name': label, 'given_name': name or '',
            'type': args.type, 'recorded': datetime.now().isoformat(),
            'device': args.device, 'device2': args.device2 or None,
            'sample_rate_requested': args.sr,
            'sample_rate_actual': actual_sr,
            'channels': args.channels, 'test_mode': args.test_mode,
            'verdict': verdict, 'calibrated': has_cal}
    with open(os.path.join(folder, 'take.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    write_index(root)

    print(f"\n  {'-'*60}")
    print(f"  recording {num:03d}  {label}   ->  {verdict}")
    if verdict == 'NO-GO':
        with open(val_json) as f:
            rep = json.load(f)
        for reason in rep.get('reasons', [])[:4]:
            print(f"    * {reason}")
        print(f"  Fix it and shoot again -- this take is not usable.")
    print(f"  {os.path.relpath(folder, os.getcwd())}")
    print(f"  all recordings: {os.path.join(root, '_index.md')}")
    print(f"  {'-'*60}\n")
    return 0 if verdict == 'GO' else 1


if __name__ == '__main__':
    sys.exit(main())
