#!/usr/bin/env python3
"""
validate.py -- GO / NO-GO on one recording, at the range, in under 10 seconds.

This is the only tool that matters on range day. Run it after the first three
shots and after every change of source, gain, distance or microphone.

    python3 validate.py recording.wav
    python3 validate.py recording.wav --expect-sr 96000 --expect-bits 24

Exit code 0 = GO, 1 = NO-GO, 2 = could not read the file at all.
"""

import argparse
import json
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import dsp    # noqa: E402

PASS, WARN, FAIL = 'PASS', 'WARN', 'FAIL'

BANNER_GO = r"""
   ██████    ██████
  ██        ██    ██
  ██   ███  ██    ██
  ██    ██  ██    ██
   ██████    ██████
"""

BANNER_NOGO = r"""
  ███    ██  ██████        ██████   ██████
  ████   ██ ██    ██      ██       ██    ██
  ██ ██  ██ ██    ██ ████ ██   ███ ██    ██
  ██  ██ ██ ██    ██      ██    ██ ██    ██
  ██   ████  ██████        ██████   ██████
"""


class Ansi:
    def __init__(self, enabled):
        self.on = enabled

    def _w(self, code, s):
        return f"\033[{code}m{s}\033[0m" if self.on else s

    def green(self, s):
        return self._w('1;32', s)

    def red(self, s):
        return self._w('1;31', s)

    def yellow(self, s):
        return self._w('1;33', s)

    def bold(self, s):
        return self._w('1', s)

    def dim(self, s):
        return self._w('2', s)


class Report:
    def __init__(self):
        self.rows = []

    def add(self, status, name, value, note=''):
        self.rows.append({'status': status, 'check': name,
                          'value': value, 'note': note})

    @property
    def verdict(self):
        return 'NO-GO' if any(r['status'] == FAIL for r in self.rows) else 'GO'

    @property
    def failures(self):
        return [r for r in self.rows if r['status'] == FAIL]

    @property
    def warnings(self):
        return [r for r in self.rows if r['status'] == WARN]


# ------------------------------------------------------------- the checks ---

def check_format(rep, info, expect_sr, expect_bits):
    sr, bits = info['sample_rate'], info['bit_depth']
    fmt = info['format']
    label = f"{sr} Hz / {bits}-bit {fmt}"
    if expect_sr and sr != expect_sr:
        rep.add(FAIL, 'Format', label, f"expected {expect_sr} Hz -- WRONG RATE")
    elif expect_bits and bits != expect_bits and fmt != 'float':
        rep.add(FAIL, 'Format', label, f"expected {expect_bits}-bit")
    elif info['channels'] > 1:
        # Not mixed down -- every channel is checked on its own, which is the
        # only way a staggered-gain array's redundancy can be seen.
        rep.add(PASS, 'Format', label + f" x{info['channels']}ch",
                'each channel checked separately')
    else:
        rep.add(PASS, 'Format', label, '')

    if info['truncated_data_chunk']:
        rep.add(FAIL, 'File integrity', 'data chunk short',
                'recorder cut mid-write -- file is damaged')


def check_clipping(rep, x, info, events, sr):
    if info['format'] == 'float':
        limit = 0.999
        kind = 'float, |x|>=0.999'
    else:
        limit = 1.0 - info['lsb']
        kind = f"{info['bit_depth']}-bit full scale"

    clipped = np.abs(x) >= limit
    n_clip = int(clipped.sum())
    pct = 100.0 * n_clip / max(x.size, 1)

    if n_clip == 0:
        rep.add(PASS, 'Clipping', '0.000%', kind)
        return

    # Where the clipping sits decides whether the file is salvageable.
    # Clipping on the impulse destroys the peak -- the single number the
    # whole dataset exists to capture. Clipping elsewhere is ugly, not fatal.
    idx = np.flatnonzero(clipped)
    on_impulse = 0
    if len(events):
        win = int(0.05 * sr)
        for ev in events:
            on_impulse += int(np.sum((idx >= ev - win) & (idx <= ev + win)))
    elsewhere = n_clip - on_impulse

    if on_impulse > 0:
        rep.add(FAIL, 'Clipping', f"{pct:.3f}%",
                f"{on_impulse} clipped samples ON the impulse -- "
                "peak destroyed, REDUCE GAIN AND RESHOOT")
    elif pct > 0.001:
        rep.add(WARN, 'Clipping', f"{pct:.3f}%",
                f"{elsewhere} samples, none on an impulse")
    else:
        rep.add(PASS, 'Clipping', f"{pct:.3f}%", 'negligible, off-impulse')


def check_bandwidth(rep, x, sr):
    """Does the file actually contain the bandwidth its header claims?

    Found by running a rig check: a MacBook mic whose native rate is 44.1 kHz
    happily accepted a 96 kHz request, and CoreAudio silently upsampled. The
    header said 96 kHz, the Format check passed, and everything above ~21 kHz
    was digital zero. At a range that is a session lost to a file that looks
    correct in every other respect.

    A resample leaves a CLIFF: the spectrum falls to the numerical floor
    (~-130 dB relative) and stays there. Genuine acoustic content never does
    that -- there is always a noise floor -- so the test is for the cliff, not
    for a gentle roll-off, and a naturally dull source will not trip it.
    """
    from scipy import signal as _sg

    nyq = sr / 2.0
    nper = min(8192, len(x))
    if nper < 256:
        rep.add(WARN, 'Bandwidth', 'n/a', 'file too short to measure')
        return

    f, pxx = _sg.welch(x, fs=sr, nperseg=nper)
    pdb = 10 * np.log10(pxx + 1e-30)
    pdb -= pdb.max()

    # Two independent signatures, because neither alone is safe:
    #
    #  1. numerical emptiness -- interpolation puts exactly zero energy above
    #     the original Nyquist, so the top of the band sits at the numerical
    #     floor. Real recordings never do: mic self-noise, preamp noise and
    #     ADC dither fill the spectrum all the way up.
    #  2. a cliff -- the drop at the original Nyquist is near-vertical, where
    #     a dull source or a gentle mic roll-off is not.
    #
    # Measured on this machine: a real CoreAudio upsample gave -135 dB and a
    # 62 dB cliff; a merely low-passed but genuine recording gave -81 dB and
    # 19 dB. An earlier version tested only where content ended, and failed
    # the dull-but-real file -- which is exactly the false positive that
    # teaches an operator to ignore warnings.
    top = pdb[f > 0.9 * nyq]
    top_level = float(np.median(top)) if top.size else -np.inf

    w = max(int(0.02 * len(f)), 3)
    steps = np.array([np.median(pdb[i - w:i]) - np.median(pdb[i:i + w])
                      for i in range(w, len(pdb) - w)])
    cliff = float(steps.max()) if steps.size else 0.0

    alive = f[pdb > -110.0]
    cutoff = float(alive.max()) if alive.size else 0.0
    val = f"{cutoff/1000:.1f} kHz of {nyq/1000:.0f} kHz"

    if top_level < -125.0 or cliff > 45.0:
        # Two causes, same consequence: the OS resampled up from a lower rate,
        # or the microphone's own DSP low-passes and leaves the top of the band
        # numerically empty (a laptop MEMS array does exactly this at ~20 kHz).
        # Either way the header overstates what the file actually contains.
        rep.add(FAIL, 'Bandwidth', val,
                f"header says {sr} Hz but content stops at {cutoff/1000:.1f} kHz "
                f"and the top of the band is digitally empty ({top_level:.0f} dB, "
                f"{cliff:.0f} dB cliff) -- the device resampled, or the mic "
                f"itself cannot reach {nyq/1000:.0f} kHz")
    elif cliff > 25.0 and cutoff < 0.6 * nyq:
        rep.add(WARN, 'Bandwidth', val,
                f"sharp {cliff:.0f} dB roll-off -- check the device is really "
                f"running at {sr} Hz")
    else:
        rep.add(PASS, 'Bandwidth', val, 'noise floor reaches Nyquist')


def check_dropouts(rep, x, sr):
    """Runs of exact digital zero -- gating, or dropped samples.

    A real microphone never produces an exact zero: there is always self-noise
    and dither. Exact zeros mean something in the chain replaced audio with
    silence -- a Bluetooth noise gate, an aggressive suppressor, or a driver
    dropping buffers.

    Found on a real take: a Bluetooth headset gated 8.3% of a 33 s recording
    into digital silence, including a 580 ms hole at the start, and the file
    passed every other check while sounding chopped.
    """
    z = (x == 0.0)
    if not z.any():
        rep.add(PASS, 'Dropouts', '0.00%', 'no digital silence')
        return

    # Only CONTIGUOUS runs count. Scattered single-sample zeros are ordinary
    # quantisation: a quiet passage sits near the LSB and individual samples
    # round to exactly zero. A real Digitek take was 2.97% zeros with a longest
    # run of 0 ms -- entirely single samples -- and an earlier version of this
    # check failed it as "gating", which would have failed every quiet take at
    # the range. Gating and dropped buffers produce RUNS, not speckle.
    edges = np.flatnonzero(np.diff(np.concatenate(([0], z.view(np.int8), [0]))))
    starts, ends = edges[0::2], edges[1::2]
    lengths = ends - starts
    min_run = max(int(0.001 * sr), 8)        # 1 ms of consecutive silence
    real = lengths[lengths >= min_run]

    longest_ms = (float(real.max()) / sr * 1000.0) if real.size else 0.0
    gated_frac = float(real.sum()) / x.size if real.size else 0.0
    speckle = float(z.mean())
    val = f"{gated_frac*100:.2f}%  max {longest_ms:.0f} ms"

    if gated_frac > 0.005 or longest_ms > 50.0:
        rep.add(FAIL, 'Dropouts', val,
                f"{real.size} run(s) of digital silence -- a noise gate or "
                "dropped buffers. A real mic never outputs exact zero")
    elif gated_frac > 0.001:
        rep.add(WARN, 'Dropouts', val, f"{real.size} short silent run(s)")
    else:
        rep.add(PASS, 'Dropouts', val,
                f"{speckle*100:.2f}% single-sample zeros = quantisation, not gating")


def check_dc(rep, x):
    dc = float(np.mean(x))
    dc_db = 20 * np.log10(max(abs(dc), dsp.EPS))
    val = f"{dc:+.5f} ({dc_db:.0f} dBFS)"
    if abs(dc) > 0.01:
        rep.add(FAIL, 'DC offset', val, 'large offset -- check input coupling')
    elif abs(dc) > 0.002:
        rep.add(WARN, 'DC offset', val, 'measurable offset, high-pass later')
    else:
        rep.add(PASS, 'DC offset', val, '')


def check_noise_floor(rep, env_db, sr):
    floor = float(np.percentile(env_db, 10.0))
    val = f"{floor:.1f} dBFS"
    if floor > -35.0:
        rep.add(FAIL, 'Noise floor', val,
                'floor is very high -- gain too hot or site too noisy')
    elif floor > -50.0:
        rep.add(WARN, 'Noise floor', val, 'higher than ideal, usable')
    else:
        rep.add(PASS, 'Noise floor', val, '')
    return floor


def check_wind(rep, x, sr, events):
    """Sub-50 Hz energy relative to total, measured away from the impulses.

    Gunshots have real low-frequency content, so measuring this over the whole
    file would report the shot, not the wind. Only the background matters.
    """
    mask = np.ones(x.size, dtype=bool)
    if len(events):
        win = int(0.3 * sr)
        for ev in events:
            mask[max(0, ev - win // 4):min(x.size, ev + win)] = False
    bg = x[mask]
    if bg.size < sr // 10:
        rep.add(WARN, 'Wind / rumble', 'n/a', 'not enough background to judge')
        return

    lf = dsp.lowpass(bg, sr, 50.0)
    ratio_db = 20 * np.log10((dsp.rms(lf) + dsp.EPS) / (dsp.rms(bg) + dsp.EPS))
    val = f"{ratio_db:+.1f} dB below total"
    if ratio_db > -3.0:
        rep.add(FAIL, 'Wind / rumble', val,
                'background dominated by <50 Hz -- FIT THE WINDSHIELD')
    elif ratio_db > -10.0:
        rep.add(WARN, 'Wind / rumble', val, 'noticeable rumble, high-pass later')
    else:
        rep.add(PASS, 'Wind / rumble', val, '')


def check_truncation(rep, x, sr, events, floor_db, env_db, hop):
    """Is a transient cut off by the start or the end of the file?"""
    edge = int(0.05 * sr)
    if x.size < 2 * edge:
        rep.add(FAIL, 'Impulse complete', 'file too short', 'under 100 ms')
        return

    head_db = 20 * np.log10(dsp.rms(x[:edge]) + dsp.EPS)
    tail_db = 20 * np.log10(dsp.rms(x[-edge:]) + dsp.EPS)
    problems = []
    if head_db > floor_db + 12.0:
        problems.append(f"file STARTS loud ({head_db:.0f} dBFS)")
    if tail_db > floor_db + 12.0:
        problems.append(f"file ENDS loud ({tail_db:.0f} dBFS)")

    # An event too close to the end has had its decay tail cut off, which
    # ruins it for reverberation work even if the peak survived.
    if len(events):
        tail_needed = int(0.5 * sr)
        late = [e for e in events if e > x.size - tail_needed]
        if late:
            problems.append(f"{len(late)} event(s) within 0.5 s of file end")
        early = [e for e in events if e < int(0.05 * sr)]
        if early:
            problems.append(f"{len(early)} event(s) within 50 ms of file start")

    if problems:
        rep.add(FAIL, 'Impulse complete', 'TRUNCATED', '; '.join(problems))
    else:
        rep.add(PASS, 'Impulse complete', 'clean edges', '')


def check_event_snr(rep, x, sr, events, floor_db, expect=None):
    if not len(events):
        if expect:
            rep.add(FAIL, 'Events found', '0',
                    f"expected {expect} -- shots are buried in the floor, "
                    "move closer or raise gain")
        else:
            rep.add(WARN, 'Events found', '0',
                    'none detected -- fine for ambience/cal, wrong for a shot file')
        return []

    if expect and len(events) != expect:
        rep.add(FAIL, 'Events found', f"{len(events)}, expected {expect}",
                'count mismatch -- a shot was missed, clipped or double-counted')

    snrs = []
    for ev in events:
        a, b = ev, min(ev + int(0.1 * sr), x.size)
        pk = dsp.peak_dbfs(x[a:b])
        snrs.append(pk - floor_db)
    snrs = np.array(snrs)
    worst = float(snrs.min())
    val = f"{len(events)} events, worst SNR {worst:.0f} dB"
    if worst < 20.0:
        rep.add(FAIL, 'Events found', val,
                'buried in the floor -- move closer or raise gain')
    elif worst < 30.0:
        rep.add(WARN, 'Events found', val, 'usable but thin')
    else:
        rep.add(PASS, 'Events found', val, f"median {np.median(snrs):.0f} dB")
    return snrs


def check_handling(rep, x, sr, events):
    """Low-frequency thumps that are not part of a real impulsive event.

    A cable tug or a knock on the stand shows up below 100 Hz with no
    broadband component. It looks like a shot to a naive detector and it
    poisons the dataset.

    Two things make this hard, and both were found the expensive way:

    1. Thresholding on a low percentile does not work. Low-passing to 100 Hz
       leaves a narrowband signal whose envelope is Rayleigh-distributed, and
       its natural fades swing well over 15 dB. On stationary range ambience
       the envelope crest is ~12 dB, a real knock is 60 dB+ -- so the test is
       crest above the MEDIAN, not above the floor.

    2. Excluding candidates that line up with a detected event does not work
       either, because a loud enough thump IS detected as an event and then
       excludes itself. The honest discriminator is spectral shape: measured
       on this data a gunshot sits at -2 to -16 dB LF/HF while a stand knock
       sits at +33 dB, so +10 dB splits them with ~20 dB of margin on each side.
    """
    from scipy import signal as _sg

    lf = dsp.lowpass(x, sr, 100.0)
    env, hop = dsp.moving_rms_db(lf, sr)
    if env.size < 8:
        rep.add(PASS, 'Handling noise', 'n/a', 'file too short to judge')
        return

    med = float(np.percentile(env, 50.0))
    crest = float(np.percentile(env, 99.9)) - med
    if crest < 15.0:
        rep.add(PASS, 'Handling noise', 'none', f"LF crest only {crest:.0f} dB")
        return

    peaks, _ = _sg.find_peaks(env, height=med + 15.0,
                              distance=max(int(0.3 * sr / hop), 1))

    pre, post = int(0.01 * sr), int(0.05 * sr)
    thumps = []
    for p in peaks:
        smp = int(p) * hop
        w = x[max(0, smp - pre):min(x.size, smp + post)]
        if w.size < pre:
            continue
        lf_r = dsp.rms(dsp.lowpass(w, sr, 100.0))
        hf_r = dsp.rms(dsp.highpass(w, sr, 500.0))
        ratio = 20 * np.log10((lf_r + dsp.EPS) / (hf_r + dsp.EPS))
        if ratio > 10.0:  # LF-only: nothing that goes bang looks like this
            thumps.append(smp)

    if not thumps:
        rep.add(PASS, 'Handling noise', 'none', 'all LF is broadband, i.e. real')
    elif len(thumps) > 3:
        rep.add(FAIL, 'Handling noise', f"{len(thumps)} thumps",
                'stop touching the stand/cable during takes')
    else:
        rep.add(WARN, 'Handling noise', f"{len(thumps)} thumps",
                'at ' + ', '.join(f"{t/sr:.1f}s" for t in thumps[:3]))


# ------------------------------------------------------------- rendering ----

# In a staggered-gain array these two checks are covered by redundancy: the hot
# channel is SUPPOSED to clip on the blast, and the cold channel is SUPPOSED to
# have the quiet detail down in its floor. Either is only fatal when EVERY
# channel fails it. Everything else -- wind, DC, truncation, handling -- is a
# real defect of that channel and is not covered by having a second one.
REDUNDANT = {'Clipping', 'Events found'}


def check_channel(x, sr, info, expect_events):
    rep = Report()
    events = dsp.find_events(x, sr)
    env_db, hop = dsp.moving_rms_db(x, sr)
    check_clipping(rep, x, info, events, sr)
    check_bandwidth(rep, x, sr)
    check_dropouts(rep, x, sr)
    check_dc(rep, x)
    floor_db = check_noise_floor(rep, env_db, sr)
    check_wind(rep, x, sr, events)
    check_truncation(rep, x, sr, events, floor_db, env_db, hop)
    check_event_snr(rep, x, sr, events, floor_db, expect_events)
    check_handling(rep, x, sr, events)
    return rep, events


def combine(file_rep, ch_reps, array_mode):
    """Roll per-channel reports into one verdict."""
    file_fails = [f"{r['check']}: {r['note'] or r['value']}"
                  for r in file_rep.rows if r['status'] == FAIL]
    if file_fails:
        return 'NO-GO', file_fails

    if not array_mode or len(ch_reps) < 2:
        bad = [f"ch{i+1} {r['check']}"
               for i, rep in enumerate(ch_reps)
               for r in rep.rows if r['status'] == FAIL]
        return ('NO-GO' if bad else 'GO'), bad

    reasons = []
    names = {r['check'] for rep in ch_reps for r in rep.rows}
    for name in names:
        states = []
        for rep in ch_reps:
            states += [r['status'] for r in rep.rows if r['check'] == name]
        if not states:
            continue
        if name in REDUNDANT:
            if all(st == FAIL for st in states):
                reasons.append(f"{name}: EVERY channel failed -- "
                               "the array did not cover it")
        elif FAIL in states:
            ch = [f"ch{i+1}" for i, rep in enumerate(ch_reps)
                  if any(r['check'] == name and r['status'] == FAIL
                         for r in rep.rows)]
            reasons.append(f"{name}: {', '.join(ch)}")
    return ('NO-GO' if reasons else 'GO'), reasons


def render(file_rep, ch_reps, verdict, reasons, path, info, elapsed, c,
           array_mode):
    W = 78
    print()
    print(c.bold('=' * W))
    print(c.bold(f" {os.path.basename(path)}"))
    print(f" {info['duration_s']:.2f} s   {info['sample_rate']} Hz   "
          f"{info['bit_depth']}-bit {info['format']}   "
          f"{info['channels']} ch   {info['n_frames']:,} frames"
          + ("   [staggered-gain array]" if array_mode else ""))
    print(c.bold('=' * W))

    def tag(st):
        return (c.green(' PASS ') if st == PASS
                else c.yellow(' WARN ') if st == WARN else c.red(' FAIL '))

    for r in file_rep.rows:
        print(f"[{tag(r['status'])}] {r['check']:<18} {r['value']:<26} "
              f"{c.dim(r['note'])}")

    roles = {0: 'HOT', 1: 'COLD'} if (array_mode and len(ch_reps) == 2) else {}
    for i, rep in enumerate(ch_reps):
        if len(ch_reps) > 1:
            role = roles.get(i, '')
            print(c.bold(f"\n -- channel {i+1} {role} " + '-' * (W - 16)))
        for r in rep.rows:
            st = r['status']
            # An expected clip on the hot channel is not a defect, and calling
            # it one trains the operator to ignore real failures.
            note = r['note']
            if array_mode and i == 0 and r['check'] == 'Clipping' and st == FAIL:
                note += '  [expected on HOT -- cold channel must cover it]'
            print(f"[{tag(st)}] {r['check']:<18} {r['value']:<26} {c.dim(note)}")

    print(c.bold('-' * W))
    if verdict == 'GO':
        print(c.green(BANNER_GO))
        warns = sum(len(r.warnings) for r in ch_reps) + len(file_rep.warnings)
        if array_mode and len(ch_reps) >= 2:
            print(c.green(" Array covered the shot: the peak survives on at "
                          "least one channel."))
        if warns:
            print(c.yellow(f" {warns} warning(s) -- read them before you move on."))
        elif not array_mode:
            print(c.green(" Clean. Carry on."))
    else:
        print(c.red(BANNER_NOGO))
        print(c.red(" DO NOT MOVE ON. Fix these now:"))
        for r in reasons:
            print(c.red(f"   * {r}"))
        print(c.red(" There is no second visit to this range."))
    print(c.dim(f"\n checked in {elapsed:.1f} s"))
    print(c.bold('=' * W))
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('wav', help='recording to check')
    ap.add_argument('--expect-sr', type=int, default=96000,
                    help='required sample rate, 0 to skip (default 96000)')
    ap.add_argument('--expect-bits', type=int, default=24,
                    help='required bit depth, 0 to skip (default 24)')
    ap.add_argument('--expect-events', type=int, default=0, metavar='N',
                    help='how many shots you actually fired into this file; '
                         'a mismatch becomes a hard FAIL (default: do not check)')
    ap.add_argument('--array', action='store_true',
                    help='treat channels as a staggered-gain array: clipping on '
                         'the hot channel is expected, and only fatal if every '
                         'channel loses the peak')
    ap.add_argument('--json', metavar='PATH', help='also write the report as JSON')
    ap.add_argument('--no-color', action='store_true')
    args = ap.parse_args()

    c = Ansi(sys.stdout.isatty() and not args.no_color)
    t0 = time.time()

    try:
        data, sr, info = wavio.read(args.wav)
    except wavio.WavError as e:
        print(c.red(f"\n CANNOT READ FILE\n   {e}\n"))
        return 2
    except FileNotFoundError:
        print(c.red(f"\n FILE NOT FOUND: {args.wav}\n"))
        return 2
    except Exception as e:  # malformed input must fail loudly, never silently
        print(c.red(f"\n UNREADABLE: {type(e).__name__}: {e}\n"))
        return 2

    if data.size == 0:
        print(c.red(f"\n EMPTY FILE: {args.wav} contains no audio\n"))
        return 2

    file_rep = Report()
    check_format(file_rep, info, args.expect_sr, args.expect_bits)

    if data.ndim == 1:
        channels = [data]
    else:
        channels = [np.ascontiguousarray(data[:, i])
                    for i in range(data.shape[1])]

    if args.array and len(channels) < 2:
        file_rep.add(WARN, 'Array mode', f"{len(channels)} channel",
                     '--array given but the file is mono')

    ch_reps, ch_events = [], []
    for x in channels:
        rep, events = check_channel(x, sr, info, args.expect_events)
        ch_reps.append(rep)
        ch_events.append(events)

    verdict, reasons = combine(file_rep, ch_reps, args.array)
    elapsed = time.time() - t0
    render(file_rep, ch_reps, verdict, reasons, args.wav, info, elapsed, c,
           args.array)

    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'file': os.path.abspath(args.wav),
                       'verdict': verdict,
                       'reasons': reasons,
                       'array_mode': args.array,
                       'duration_s': info['duration_s'],
                       'sample_rate': info['sample_rate'],
                       'bit_depth': info['bit_depth'],
                       'channels': info['channels'],
                       'file_checks': file_rep.rows,
                       'per_channel': [
                           {'channel': i + 1,
                            'n_events': int(len(ch_events[i])),
                            'event_times_s': [round(e / sr, 4)
                                              for e in ch_events[i]],
                            'checks': rep.rows}
                           for i, rep in enumerate(ch_reps)]}, f, indent=2)

    return 0 if verdict == 'GO' else 1


if __name__ == '__main__':
    sys.exit(main())
