#!/usr/bin/env python3
"""
selftest.py -- prove the toolkit works before range day.

    python3 make_test_data.py --out testdata/
    python3 selftest.py testdata/

Runs every tool over the synthetic data and checks that validate.py returns
the right verdict for each deliberately broken file. If this does not print
ALL CHECKS PASSED, do not go to the range.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# (filename, expected verdict, which check must fail, extra CLI args)
#
# bad_buried needs --expect-events: validate.py cannot know whether a file was
# meant to contain shots. A quiet file is correct for ambience and a disaster
# for a shot take, and only the operator knows which this is. That is why the
# range procedure is to always pass the number of rounds actually fired.
EXPECT = [
    ('good_shots.wav',               'GO',    None,               ['--expect-events', '5']),
    ('good_float32.wav',             'GO',    None,               []),
    ('bad_clipped_on_impulse.wav',   'NO-GO', 'Clipping',         []),
    ('warn_clipped_off_impulse.wav', 'GO',    None,               []),
    ('bad_windy.wav',                'NO-GO', 'Wind / rumble',    []),
    ('bad_truncated.wav',            'NO-GO', 'Impulse complete', []),
    ('bad_starts_loud.wav',          'NO-GO', 'Impulse complete', []),
    ('bad_wrong_rate.wav',           'NO-GO', 'Format',           []),
    ('bad_dc_offset.wav',            'NO-GO', 'DC offset',        []),
    ('bad_buried.wav',               'NO-GO', 'Events found',     ['--expect-events', '3']),
    ('bad_handling.wav',             'NO-GO', 'Handling noise',   []),
    ('bad_resampled.wav',            'NO-GO', 'Bandwidth',        []),
    ('bad_gated.wav',                'NO-GO', 'Dropouts',         []),
    ('ambience.wav',                 'GO',    None,               []),
]


def run(args, **kw):
    return subprocess.run([sys.executable] + args, capture_output=True,
                          text=True, cwd=HERE, **kw)


def main():
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print(__doc__)
        return 0
    data = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'testdata')
    if not os.path.isdir(data):
        print(f"no such directory: {data}\nrun make_test_data.py first")
        return 2

    out = os.path.join(data, '_selftest_out')
    os.makedirs(out, exist_ok=True)
    fails = []

    print(f"\n== validate.py verdicts ==\n")
    print(f"  {'file':<30} {'expect':<7} {'actual':<7} {'failing check':<20}")
    print(f"  {'-'*30} {'-'*7} {'-'*7} {'-'*20}")

    import json
    for name, want, want_check, extra in EXPECT:
        wav = os.path.join(data, name)
        jf = os.path.join(out, name + '.json')
        r = run(['validate.py', wav, '--no-color', '--json', jf] + extra)
        if r.returncode == 2:
            fails.append(f"{name}: validate.py could not read the file")
            print(f"  {name:<30} {want:<7} {'ERROR':<7} {r.stdout.strip()[:40]}")
            continue
        got = 'GO' if r.returncode == 0 else 'NO-GO'

        failing = ''
        if os.path.exists(jf):
            with open(jf) as f:
                rep = json.load(f)
            bad = [c['check'] for c in rep['file_checks']
                   if c['status'] == 'FAIL']
            for ch in rep['per_channel']:
                bad += [c['check'] for c in ch['checks']
                        if c['status'] == 'FAIL']
            failing = ', '.join(bad)

        ok = (got == want)
        if ok and want_check and want_check not in failing:
            ok = False
            failing += f"  (wanted {want_check})"
        if not ok:
            fails.append(f"{name}: expected {want}"
                         + (f" via {want_check}" if want_check else '')
                         + f", got {got} via [{failing or 'none'}]")
        mark = 'ok' if ok else '<-- MISMATCH'
        print(f"  {name:<30} {want:<7} {got:<7} {failing[:20]:<20} {mark}")

    print(f"\n== other tools ==\n")

    checks = [
        ('calibrate.py', ['calibrate.py', os.path.join(data, 'cal_tone_recorded.wav'),
                          '--spl-db', '94.0', '--out', os.path.join(out, 'cal.json')]),
        ('ir_extract.py (sweep)', ['ir_extract.py', os.path.join(data, 'sweep_recorded.wav'),
                                   '--inverse', os.path.join(data, 'inverse_filter.wav'),
                                   '--out', out]),
        ('ir_extract.py (balloon)', ['ir_extract.py', os.path.join(data, 'balloon_pop.wav'),
                                     '--balloon', '--out', out]),
        ('ingest.py', ['ingest.py', os.path.join(data, 'long_session.wav'),
                       '--meta', os.path.join(data, 'long_session_meta.csv'),
                       '--out', os.path.join(out, 'events'),
                       '--allow-synthetic']),
        ('quicklook.py', ['quicklook.py', os.path.join(data, 'good_shots.wav'),
                          '--out', os.path.join(out, 'looks')]),
        ('analyze.py (calibrated)',
         ['analyze.py', os.path.join(out, 'events'),
          '--cal', os.path.join(out, 'cal.json'), '--label', 'toolkit-check',
          '--out', os.path.join(out, 'features.json'),
          '--csv', os.path.join(out, 'features.csv'), '--allow-synthetic']),
        ('analyze.py (uncalibrated)',
         ['analyze.py', os.path.join(data, 'good_shots.wav'),
          '--label', 'toolkit-check-uncal', '--allow-synthetic',
          '--out', os.path.join(out, 'features_uncal.json')]),
        ('report.py', ['report.py', os.path.join(out, 'features.json'),
                       '--audio', os.path.join(out, 'events'),
                       '--out', os.path.join(out, 'report.html')]),
    ]
    for label, args in checks:
        r = run(args)
        if r.returncode == 0:
            print(f"  [ ok ] {label}")
        else:
            print(f"  [FAIL] {label}")
            tail = (r.stderr or r.stdout).strip().splitlines()[-4:]
            for line in tail:
                print(f"         {line}")
            fails.append(f"{label}: exit {r.returncode}")

    print(f"\n== lossless round-trip ==\n")
    # A sliced event must be bit-identical to its region of the raw take.
    # An asymmetric read/write scale once cost exactly 1 LSB, and only near
    # full scale -- i.e. on the peak, the one number the dataset exists for.
    try:
        sys.path.insert(0, HERE)
        import numpy as _np
        import wavio as _w
        import tempfile as _tf
        rt_ok = True
        for _bd, _full in ((16, 2 ** 15), (24, 2 ** 23), (32, 2 ** 31)):
            _n = _np.array([_full - 1, -_full, _full // 2, 0, 1, -1],
                           dtype=_np.int64)
            _p = os.path.join(_tf.gettempdir(), f'_st_rt{_bd}.wav')
            _w.write(_p, _n / _full, 48000, _bd)
            _d, _, _ = _w.read(_p)
            if not _np.array_equal(_np.round(_d * _full).astype(_np.int64), _n):
                rt_ok = False
                print(f"  [FAIL] {_bd}-bit round-trip is lossy")
                fails.append(f"{_bd}-bit WAV round-trip is not bit-exact")
            else:
                print(f"  [ ok ] {_bd}-bit round-trip is bit-exact")
        del rt_ok
    except Exception as e:
        print(f"  [FAIL] round-trip check errored: {e}")
        fails.append(f"round-trip check errored: {e}")

    print(f"\n== monitor write path ==\n")
    # monitor.py --record once had NO write path at all: audio was collected
    # and thrown away on exit, silently, and a real take was lost. The file
    # still parsed and still ran. Check the code path exists, since it cannot
    # be exercised here without an audio device and a window.
    _mon = open(os.path.join(HERE, 'monitor.py')).read()
    for _needle, _what in [
            ('StreamWriter(args.record', 'opens a streaming writer'),
            ('wq.put(indata', 'feeds every block to disk, not to RAM'),
            ('writer.close()', 'finalises the header on exit'),
            ('NOTHING WAS CAPTURED', 'fails loudly on an empty capture'),
            ("args.record is None", 'warns when not recording')]:
        if _needle in _mon:
            print(f"  [ ok ] monitor.py {_what}")
        else:
            print(f"  [FAIL] monitor.py no longer {_what}")
            fails.append(f"monitor.py lost its write path: {_what}")

    print(f"\n== provenance guard ==\n")
    for label, args_ in [
            ('ingest.py refuses synthetic',
             ['ingest.py', os.path.join(data, 'long_session.wav'),
              '--out', os.path.join(out, 'guard_ev')]),
            ('analyze.py refuses synthetic',
             ['analyze.py', os.path.join(data, 'good_shots.wav'),
              '--out', os.path.join(out, 'guard.json')])]:
        r = run(args_)
        if r.returncode == 3:
            print(f"  [ ok ] {label}")
        else:
            print(f"  [FAIL] {label} (exit {r.returncode}, wanted 3)")
            fails.append(f"{label}: guard did not fire")

    print()
    if fails:
        print(f"  {len(fails)} PROBLEM(S) -- DO NOT GO TO THE RANGE:")
        for f in fails:
            print(f"    * {f}")
        return 1
    print("  ALL CHECKS PASSED -- toolkit is range-ready.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
