#!/usr/bin/env python3
"""
make_test_data.py -- synthesise fake recordings, including deliberately bad
ones, so every tool can be proved to work BEFORE range day.

    python3 make_test_data.py --out testdata/

The point is not realism. The point is that each failure mode the range can
throw at you exists here as a file, so you find out today that validate.py
catches it -- not tomorrow when the range is behind you.
"""

import argparse
import csv
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import gen_signals  # noqa: E402
import provenance  # noqa: E402

SR = 96000


def friedlander(sr, peak=0.7, tau=0.0012, dur=0.06):
    """Friedlander blast wave: the standard idealisation of a muzzle blast.

    p(t) = P0 (1 - t/tau) exp(-t/tau): near-instant rise, sharp positive
    phase, then the negative underpressure phase. Not a substitute for real
    data -- it is here so the tools have something shaped like a gunshot.
    """
    n = int(dur * sr)
    t = np.arange(n) / sr
    w = peak * (1.0 - t / tau) * np.exp(-t / tau)
    w[0] = 0.0  # enforce the rise rather than starting at full amplitude
    return w


def room_ir(sr, rt60=0.8, n_early=12, seed=0):
    """Crude range IR: a few discrete early reflections then a noise tail."""
    rng = np.random.default_rng(seed)
    n = int(rt60 * 1.5 * sr)
    ir = np.zeros(n)
    ir[0] = 1.0
    for _ in range(n_early):
        d = rng.integers(int(0.004 * sr), int(0.08 * sr))
        if d < n:
            ir[d] += rng.uniform(-0.5, 0.5)
    tail = rng.standard_normal(n) * np.exp(-np.arange(n) / (rt60 * sr / 6.9))
    ir += 0.25 * tail
    return ir / np.max(np.abs(ir))


def session(sr, dur_s, shot_times, peak=0.7, floor=0.0008, rt60=0.6, seed=1):
    """A background-noise bed with blast waves convolved into a room.

    `peak` is the final peak of the finished signal, not the amplitude of the
    blast before convolution. Convolving with a 12-reflection room IR raises
    the amplitude by an amount that depends on the IR seed, so setting the
    pre-convolution level leaves the output peak unpredictable -- which had
    every 'clean' test file silently clipping at 1.0.
    """
    rng = np.random.default_rng(seed)
    n = int(dur_s * sr)
    shots = np.zeros(n)
    ir = room_ir(sr, rt60=rt60, seed=seed)
    for t in shot_times:
        w = friedlander(sr, peak=rng.uniform(0.85, 1.0))
        ev = np.convolve(w, ir)[:int(0.6 * sr)]
        a = int(t * sr)
        b = min(a + len(ev), n)
        shots[a:b] += ev[:b - a]
    m = np.max(np.abs(shots))
    if m > 0:
        shots *= peak / m
    return shots + floor * rng.standard_normal(n)


def add_wind(x, sr, level=0.25, seed=3):
    """Low-frequency wind buffeting: band-limited noise below ~40 Hz."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(len(x))
    spec = np.fft.rfft(w)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    spec[f > 40.0] = 0.0
    spec[f < 2.0] = 0.0
    wind = np.fft.irfft(spec, len(x))
    wind = wind / (np.max(np.abs(wind)) + 1e-12) * level
    # Gusty, not constant
    env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * np.arange(len(x)) / sr)
    return x + wind * env


def add_thumps(x, sr, times, level=0.3, seed=4):
    """Cable tugs / stand knocks: LF only, no broadband component."""
    rng = np.random.default_rng(seed)
    for t in times:
        n = int(0.15 * sr)
        tt = np.arange(n) / sr
        thump = (level * np.sin(2 * np.pi * rng.uniform(25, 60) * tt)
                 * np.exp(-tt / 0.03))
        a = int(t * sr)
        b = min(a + n, len(x))
        x[a:b] += thump[:b - a]
    return x


CASES = []


def case(name, verdict, why):
    def deco(fn):
        CASES.append({'name': name, 'verdict': verdict, 'why': why, 'fn': fn})
        return fn
    return deco


@case('good_shots.wav', 'GO', 'clean 5-shot take, nothing wrong')
def _good(sr):
    return session(sr, 30.0, [3.0, 8.5, 14.0, 20.2, 26.0]), sr, 24


@case('good_float32.wav', 'GO', 'same but 32-bit float, tests float path')
def _float(sr):
    return session(sr, 20.0, [3.0, 9.0, 15.0], seed=9), sr, 'float32'


@case('bad_clipped_on_impulse.wav', 'NO-GO', 'gain too hot, peaks destroyed')
def _clip_on(sr):
    # Drive it 8 dB into the rails so the flat tops sit on the impulse itself
    x = session(sr, 20.0, [3.0, 9.0, 15.0], peak=2.5)
    return np.clip(x, -1.0, 1.0), sr, 24


@case('warn_clipped_off_impulse.wav', 'GO',
      'sustained non-impulsive clipping -- ugly, not fatal')
def _clip_off(sr):
    """Clipping that is NOT on an impulse: a generator or feedback tone that
    rode into the rails between shots.

    An earlier version of this case used a 2 ms full-scale bump, which was a
    bad test: a 2 ms flat-topped burst IS a broadband impulse, so validate.py
    rightly called it clipping-on-an-impulse and failed the file. The tool
    cannot know which impulse was the shot, so any clipped impulse has to be
    fatal. Only sustained, narrowband clipping is survivable, and that is what
    this file now contains.
    """
    x = session(sr, 20.0, [3.0, 9.0, 15.0], peak=0.5)
    n = int(0.4 * sr)
    t = np.arange(n) / sr
    env = np.minimum(t / 0.10, 1.0) * np.minimum((t[-1] - t) / 0.10, 1.0)
    a = int(12.0 * sr)
    x[a:a + n] += 1.4 * np.sin(2 * np.pi * 220 * t) * env
    return np.clip(x, -1.0, 1.0), sr, 24


@case('bad_windy.wav', 'NO-GO', 'no windshield, sub-50 Hz dominates')
def _windy(sr):
    x = session(sr, 20.0, [4.0, 10.0, 16.0], peak=0.35)
    return add_wind(x, sr, level=0.25), sr, 24


@case('bad_truncated.wav', 'NO-GO', 'recorder stopped during the decay')
def _trunc(sr):
    x = session(sr, 20.0, [3.0, 9.0, 19.85])
    return x, sr, 24


@case('bad_starts_loud.wav', 'NO-GO', 'recorder started late, first shot cut')
def _starts_loud(sr):
    x = session(sr, 20.0, [3.0, 9.0, 15.0])
    return x[int(2.995 * sr):], sr, 24


@case('bad_wrong_rate.wav', 'NO-GO', 'recorder left at 48 kHz')
def _rate(sr):
    return session(48000, 20.0, [3.0, 9.0, 15.0]), 48000, 24


@case('bad_dc_offset.wav', 'NO-GO', 'DC offset from a bad input stage')
def _dc(sr):
    x = session(sr, 20.0, [3.0, 9.0, 15.0], peak=0.5)
    return x + 0.05, sr, 24


@case('bad_buried.wav', 'NO-GO', 'too far / gain too low, shots in the floor')
def _buried(sr):
    return session(sr, 20.0, [3.0, 9.0, 15.0], peak=0.02, floor=0.006), sr, 24


@case('bad_handling.wav', 'NO-GO', 'someone kept knocking the stand')
def _handling(sr):
    x = session(sr, 25.0, [3.0, 10.0, 17.0], peak=0.5)
    return add_thumps(x, sr, [5.5, 7.2, 12.8, 14.4, 21.0], level=0.12), sr, 24


@case('bad_resampled.wav', 'NO-GO',
      'device ran at 48 kHz; the OS upsampled to a 96 kHz label')
def _resampled(sr):
    """A file whose header lies about its bandwidth.

    Reproduces what was actually observed on this machine: a 44.1 kHz mic
    accepted a 96 kHz request and CoreAudio silently upsampled. Header
    correct, Format check green, and everything above the original Nyquist
    digitally empty. At a range that is a session lost to a file that looks
    right in every other respect.

    Modelled by zeroing the upper half of the spectrum, which is what the real
    resampler left behind -- not by scipy's resample_poly, whose anti-imaging
    filter is far better than the OS one and leaves a gentler floor than any
    device actually produces.
    """
    x = session(sr, 20.0, [3.0, 9.0, 15.0], peak=0.6, seed=41)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    spec[f > sr / 4.0] = 0.0        # nothing above the ORIGINAL Nyquist
    return np.fft.irfft(spec, len(x)), sr, 24


@case('bad_gated.wav', 'NO-GO',
      'Bluetooth noise gate replaced audio with digital silence')
def _gated(sr):
    """Audio punched out into exact zeros by a noise gate.

    Reproduces a real Bluetooth headset take: 8.3% of a 33 s recording was
    exact digital zero, including a 580 ms hole at the start, and it passed
    every other check while sounding chopped. A real microphone never outputs
    an exact zero -- there is always self-noise.
    """
    x = session(sr, 20.0, [3.0, 9.0, 15.0], peak=0.5, seed=53)
    for start, dur in ((0.0, 0.58), (5.5, 0.25), (11.7, 0.18), (17.0, 0.30)):
        a = int(start * sr)
        x[a:a + int(dur * sr)] = 0.0
    return x, sr, 24


@case('ambience.wav', 'GO', 'range ambience, no events -- warns, does not fail')
def _amb(sr):
    rng = np.random.default_rng(11)
    return 0.0015 * rng.standard_normal(int(20.0 * sr)), sr, 24


def make_calibration(out, sr):
    """A 1 kHz tone as a recorder would capture it, for calibrate.py.

    Recorded at -20 dBFS while the SPL meter reads 94.0 dB -- the classic
    calibrator level. calibrate.py must recover a scale factor that puts
    full scale at 114 dB SPL.
    """
    x = gen_signals.cal_tone(sr, dur=10.0, dbfs=-20.0)
    rng = np.random.default_rng(5)
    x = x + 0.0002 * rng.standard_normal(len(x))
    wavio.write(os.path.join(out, 'cal_tone_recorded.wav'), x, sr, 24)
    return 94.0


def make_sweep_recording(out, sr):
    """A sweep as recorded in a reverberant range, for ir_extract.py."""
    sweep, inv = gen_signals.log_sweep(sr, dur=10.0)
    ir = room_ir(sr, rt60=0.9, seed=21)
    rec = np.convolve(sweep, ir)
    rec = rec / (np.max(np.abs(rec)) + 1e-12) * 0.6
    rng = np.random.default_rng(6)
    rec = rec + 0.0003 * rng.standard_normal(len(rec))
    wavio.write(os.path.join(out, 'sweep_recorded.wav'), rec, sr, 24)
    wavio.write(os.path.join(out, 'inverse_filter.wav'), inv, sr, 'float32')

    # Balloon-pop fallback: an impulse straight into the same room
    pop = np.zeros(int(2.0 * sr))
    pop[int(0.2 * sr)] = 1.0
    pop = np.convolve(pop, ir)[:int(2.5 * sr)]
    pop = pop / (np.max(np.abs(pop)) + 1e-12) * 0.7
    pop += 0.0003 * rng.standard_normal(len(pop))
    wavio.write(os.path.join(out, 'balloon_pop.wav'), pop, sr, 24)
    return 0.9


META_COLS = ['shot_id', 'session', 'tier', 'timestamp', 'recorder',
             'gain_setting', 'sample_rate_hz', 'bit_depth', 'source_type',
             'distance_m', 'azimuth_deg', 'mic_height_cm', 'source_height_cm',
             'ground_surface', 'clipped', 'temp_c', 'humidity_pct',
             'wind_kmh', 'wind_direction', 'split', 'notes']


def make_long_session(out, sr):
    """A continuous take plus its metadata CSV, for ingest.py."""
    times = [4.0, 11.5, 19.0, 27.5, 35.0, 42.5, 51.0, 58.5]
    x = session(sr, 65.0, times, peak=0.6, seed=31)
    wavio.write(os.path.join(out, 'long_session.wav'), x, sr, 24)

    path = os.path.join(out, 'long_session_meta.csv')
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=META_COLS)
        w.writeheader()
        for i, _ in enumerate(times, start=1):
            w.writerow({
                'shot_id': f'SHOT-{i:03d}', 'session': 'S1', 'tier': 'T1',
                'timestamp': '', 'recorder': 'A', 'gain_setting': '5',
                'sample_rate_hz': sr, 'bit_depth': 24,
                'source_type': 'air_rifle', 'distance_m': '10.0',
                'azimuth_deg': '90', 'mic_height_cm': '120',
                'source_height_cm': '120', 'ground_surface': 'concrete',
                'clipped': 'no', 'temp_c': '31', 'humidity_pct': '58',
                'wind_kmh': '6', 'wind_direction': 'NW',
                'split': 'fit' if i <= 6 else 'holdout', 'notes': '',
            })
    return len(times)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='testdata')
    ap.add_argument('--sr', type=int, default=SR)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # Stamp it before writing a single file: audio that escapes this directory
    # unmarked is indistinguishable from a real recording.
    provenance.mark(args.out)
    print(f"Writing synthetic test data to {args.out}/\n")
    print(f"  {'file':<32} {'expected':<7} why")
    print(f"  {'-'*32} {'-'*7} {'-'*40}")

    for c in CASES:
        x, sr, bd = c['fn'](args.sr)
        wavio.write(os.path.join(args.out, c['name']), x, sr, bd)
        print(f"  {c['name']:<32} {c['verdict']:<7} {c['why']}")

    spl = make_calibration(args.out, args.sr)
    print(f"\n  cal_tone_recorded.wav            -- SPL meter read {spl} dB")
    rt = make_sweep_recording(args.out, args.sr)
    print(f"  sweep_recorded.wav + inverse_filter.wav  -- true RT60 ~{rt} s")
    print("  balloon_pop.wav                  -- fallback IR path")
    n = make_long_session(args.out, args.sr)
    print(f"  long_session.wav + long_session_meta.csv -- {n} events to slice")

    print(f"\nNow prove the tools work:  python3 selftest.py {args.out}")


if __name__ == '__main__':
    main()
