#!/usr/bin/env python3
"""
record.py -- capture takes straight into the toolkit, with a live peak meter.

    python3 record.py --list                      # what can I record from?
    python3 record.py --meter --device 3          # set the gain (records nothing)
    python3 record.py --device 3 --out take001.wav
    python3 record.py --device 3 --out take001.wav --duration 60

Meter mode is the point. Gain on a one-shot gunshot session cannot be set by
ear or by a slow bar-graph: the crest factor is enormous and an average-reading
meter under-reads the peak by 30 dB or more. This shows true sample peak with
a hold, so you can pop a balloon at the real distance and see exactly where it
landed.

Needs one extra package (install at home, not at the range):
    python3 -m pip install sounddevice
"""

import argparse
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavio  # noqa: E402
import provenance  # noqa: E402

# Names that mean "this is a Bluetooth headset profile": 16 kHz, mono, AGC,
# noise suppression. A file recorded from one of these looks fine in a file
# browser and is scientifically worthless.
BLUETOOTH_HINTS = ('airpod', 'airdope', 'buds', 'bluetooth', 'hfp', 'hands-free',
                   'headset', 'wireless', 'bt ')
VIRTUAL_HINTS = ('blackhole', 'soundflower', 'loopback', 'aggregate', 'eshare',
                 'screaming bee', 'virtual', 'zoom audio', 'teams audio')


def need_sd():
    try:
        import sounddevice as sd
        return sd
    except ImportError:
        print("\n  sounddevice is not installed. It is the only extra package\n"
              "  this toolkit needs, and only for recording:\n\n"
              "      python3 -m pip install sounddevice\n\n"
              "  Do it at home. There is no internet at the range.\n",
              file=sys.stderr)
        sys.exit(2)


def classify(name):
    low = name.lower()
    if any(h in low for h in BLUETOOTH_HINTS):
        return 'BLUETOOTH'
    if any(h in low for h in VIRTUAL_HINTS):
        return 'VIRTUAL'
    return ''


def open_channels(info, wanted):
    """How many channels to actually open the stream with.

    CoreAudio's AUHAL refuses some device/channel combinations outright --
    asking a 2-channel USB interface for 1 channel returns -10863 "cannot do
    in current context" and the stream dies mid-run. Opening the device's own
    channel count always works; take the channels you want from the block.
    """
    dev_ch = int(info['max_input_channels'])
    return dev_ch if dev_ch > wanted else wanted


def resolve_device(sd, spec):
    """Accept an index OR a name fragment.

    PortAudio indices are not stable: unplugging a Bluetooth headset renumbers
    everything after it, so a device noted down the day before can silently
    become a different microphone. A name fragment survives that.
    """
    if spec is None:
        return None
    s = str(spec).strip()
    if s.lstrip('-').isdigit():
        return int(s)
    hits = [(i, d['name']) for i, d in enumerate(sd.query_devices())
            if d['max_input_channels'] > 0 and s.lower() in d['name'].lower()]
    if not hits:
        print(f"\n  No input device matching {s!r}. Run --list.\n",
              file=sys.stderr)
        sys.exit(2)
    if len(hits) > 1:
        print(f"\n  {s!r} matches more than one device:", file=sys.stderr)
        for i, n in hits:
            print(f"      {i}  {n}", file=sys.stderr)
        print("  Be more specific, or use the number.\n", file=sys.stderr)
        sys.exit(2)
    return hits[0][0]


def list_devices(sd):
    print(f"\n  {'#':>3}  {'in':>3}  {'default sr':>10}  device")
    print(f"  {'-'*3}  {'-'*3}  {'-'*10}  {'-'*44}")
    default_in = sd.default.device[0]
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] < 1:
            continue
        tag = classify(d['name'])
        mark = ' <- current default' if i == default_in else ''
        warn = f"  ** {tag}, DO NOT USE **" if tag else ''
        print(f"  {i:>3}  {d['max_input_channels']:>3}  "
              f"{d['default_samplerate']:>10.0f}  {d['name']}{mark}{warn}")
    print("\n  Pick the USB interface. If you cannot see it here, it is not\n"
          "  plugged in or not powered -- fix that before anything else.\n")


def check_device(sd, dev, sr, nch=1, test_mode=False):
    """Refuse the traps before a take is wasted on them.

    test_mode exists so the signal chain can be exercised on whatever hardware
    is to hand -- laptop mic, earbuds -- before the real interface arrives.
    Anything captured that way is marked as test data and cannot reach the
    dataset, which is the only reason it is safe to allow at all.
    """
    info = sd.query_devices(dev, 'input')
    tag = classify(info['name'])
    print(f"\n  device   {dev}: {info['name']}")
    print(f"  channels {info['max_input_channels']}   "
          f"device default rate {info['default_samplerate']:.0f} Hz")

    if tag and not test_mode:
        why = ("a Bluetooth headset: 16 kHz mono through AGC and noise\n"
               "  suppression. Nothing above ~8 kHz survives and the peaks are\n"
               "  already destroyed."
               if tag == 'BLUETOOTH' else
               "a virtual/loopback device, not a microphone.")
        print(f"\n  *** REFUSING: this is {why} ***\n"
              f"  Use the wired interface for real data.\n\n"
              f"  To exercise the toolkit on it anyway, pass --test-mode. The\n"
              f"  recording will be marked as test data and barred from the\n"
              f"  dataset.\n", file=sys.stderr)
        sys.exit(2)
    if tag and test_mode:
        print(f"\n  *** TEST MODE: {tag} device. This is a rig check, NOT data. "
              f"***")

    if info['max_input_channels'] < nch:
        print(f"\n  *** This device has only {info['max_input_channels']} input\n"
              f"  channel(s); {nch} were requested. A staggered-gain array needs\n"
              f"  a 2-in interface -- one mic cannot be two channels.\n",
              file=sys.stderr)
        sys.exit(2)

    try:
        # Validate the config we will ACTUALLY open with, not the one asked
        # for. The stream opens the device's own channel count (see
        # open_channels), so checking `nch` here validates a combination we
        # never use -- and on a 2-channel device that is exactly the one
        # CoreAudio rejects.
        sd.check_input_settings(device=dev, samplerate=sr,
                                channels=open_channels(info, nch),
                                dtype='float32')
    except Exception as e:
        print(f"\n  *** {sr} Hz is not available on this device: {e}\n"
              f"  Try --sr {int(info['default_samplerate'])}, or check the\n"
              f"  interface's own control panel.\n", file=sys.stderr)
        sys.exit(2)

    # check_input_settings is NOT a capability test on macOS. Asked for 96 kHz
    # on a 16 kHz Bluetooth headset it answers yes, because CoreAudio will
    # resample rather than refuse -- observed here on both the laptop mic and
    # the earbuds. The device's own default rate is the honest number, so
    # compare against that and say so BEFORE the take, not after.
    native = int(info['default_samplerate'])
    if sr > native:
        msg = (f"\n  *** {sr} Hz REQUESTED, DEVICE RUNS AT {native} Hz ***\n"
               f"  CoreAudio will upsample. The file will be labelled {sr} Hz\n"
               f"  and contain only {native / 2000:.1f} kHz of real bandwidth.\n"
               f"  Set the device itself to {sr} Hz in Audio MIDI Setup.")
        if test_mode:
            print(msg + f"\n  Test mode: continuing at {native} Hz instead.\n")
            return info, native
        print(msg + "\n", file=sys.stderr)
        sys.exit(2)
    return info, sr


def bar(db, lo=-60.0, width=42):
    """Headroom bar. The last 12 dB are the ones that matter."""
    frac = max(0.0, min(1.0, (db - lo) / (0.0 - lo)))
    n = int(frac * width)
    filled = '#' * n + '-' * (width - n)
    # mark -12 dBFS, the gain target
    tgt = int(((-12.0 - lo) / (0.0 - lo)) * width)
    filled = filled[:tgt] + '|' + filled[tgt + 1:] if tgt < width else filled
    return filled


def _peak_state(nch):
    return {'hold': [-120.0] * nch, 'clips': [0] * nch, 'db': [-120.0] * nch}


def _update_peaks(state, indata):
    for c in range(indata.shape[1]):
        pk = float(np.max(np.abs(indata[:, c]))) if indata.size else 0.0
        db = 20 * np.log10(pk) if pk > 0 else -120.0
        state['db'][c] = db
        if db > state['hold'][c]:
            state['hold'][c] = db
        if pk >= 0.999:
            state['clips'][c] += 1


TTY = sys.stdout.isatty()


def _cursor_up(n):
    """Redraw in place on a terminal; plain lines when piped to a log."""
    return f"\033[{n}A" if TTY else ""


def _clear_eol():
    return "\033[K" if TTY else ""


def _channel_line(c, db, hold, clips, roles):
    flag = ''
    if hold >= -0.1:
        flag = ' *** CLIPPING ***'
    elif hold > -6.0:
        flag = ' too hot'
    elif -18.0 <= hold <= -12.0:
        flag = ' <- in target'
    role = roles.get(c, '')
    return (f"  ch{c+1} {role:<6}[{bar(db)}] now {db:7.1f}  "
            f"hold {hold:7.1f}  clips {clips:<4}{flag}")


def meter(sd, dev, sr, nch=1, blocksize=2048, test_mode=False):
    _info, sr = check_device(sd, dev, sr, nch, test_mode)
    open_ch = open_channels(_info, nch)
    roles = ({0: 'HOT', 1: 'COLD'} if nch == 2 else {})
    print(f"\n  LIVE PEAK METER, {nch} channel(s) -- nothing is being recorded.\n"
          "  Fire your proxy (balloon pop / firecracker) at the real distance\n"
          "  and angle, then read the HOLD value.\n")
    if nch >= 2:
        print("  STAGGERED-GAIN ARRAY -- the two channels have different jobs:\n"
              "    ch1 HOT   proxy peak at -18 to -12 dBFS. Captures the tail,\n"
              "              the reverberation and the mechanical detail. This\n"
              "              channel is EXPECTED to clip on the blast itself.\n"
              "    ch2 COLD  18-24 dB less gain. Its only job is to catch the\n"
              "              blast peak unclipped. It will look far too quiet\n"
              "              between shots -- that is correct, leave it alone.\n")
    else:
        print("  TARGET: proxy peak between -18 and -12 dBFS.\n"
              "  Then back the gain off further for the louder real source.\n")
    print("  Ctrl-C to stop.\n")

    state = _peak_state(nch)

    def cb(indata, frames, t, status):
        if open_ch != nch:
            indata = indata[:, :nch]
        _update_peaks(state, indata)

    first = [True]
    try:
        with sd.InputStream(device=dev, channels=open_ch, samplerate=sr,
                            dtype='float32', blocksize=blocksize, callback=cb):
            while True:
                if not first[0]:
                    sys.stdout.write(_cursor_up(nch))
                first[0] = False
                for c in range(nch):
                    sys.stdout.write('\r' + _channel_line(
                        c, state['db'][c], state['hold'][c],
                        state['clips'][c], roles) + _clear_eol() + '\n')
                sys.stdout.flush()
                time.sleep(0.05)
    except KeyboardInterrupt:
        print()
        for c in range(nch):
            print(f"  ch{c+1}: peak hold {state['hold'][c]:.1f} dBFS, "
                  f"clipped blocks {state['clips'][c]}")
        if nch >= 2:
            sep = state['hold'][0] - state['hold'][1]
            print(f"\n  channel separation: {sep:.1f} dB")
            if sep < 12.0:
                print("  TOO CLOSE. The point of the array is that the cold\n"
                      "  channel survives what the hot one cannot. Open the gap\n"
                      "  to 18-24 dB or you have two copies of one recording.\n")
            elif sep > 30.0:
                print("  Very wide -- the cold channel may be down in its own\n"
                      "  noise floor. 18-24 dB is the useful range.\n")
            else:
                print("  Good separation.\n")
        else:
            h = state['hold'][0]
            if state['clips'][0]:
                print("  Gain is too high. Reduce it and run the meter again.\n")
            elif h > -6.0:
                print("  Too hot for a louder source. Reduce gain.\n")
            elif h < -40.0:
                print("  Very quiet -- check the mic is powered and the right\n"
                      "  input is selected before deciding to raise gain.\n")
            else:
                print("  Usable. Remember: the real source will be louder than\n"
                      "  the proxy, so leave headroom for it.\n")


def record(sd, dev, sr, out, duration, bits, nch=1, test_mode=False):
    info, sr = check_device(sd, dev, sr, nch, test_mode)
    # Same reason as monitor.py: asking a 2-channel device for 1 channel is a
    # combination CoreAudio does not honour cleanly -- it returns -10863, and
    # when it does hand data back it can be corrupt, showing as full-scale
    # spikes that look exactly like clipping but are not acoustic at all.
    open_ch = open_channels(info, nch)
    if os.path.exists(out):
        print(f"\n  REFUSING: {out} already exists. Pick another name --\n"
              "  overwriting a take you cannot re-shoot is not recoverable.\n",
              file=sys.stderr)
        sys.exit(2)

    chunks = []
    state = _peak_state(nch)
    roles = ({0: 'HOT', 1: 'COLD'} if nch == 2 else {})

    def cb(indata, frames, t, status):
        if status:
            state.setdefault('glitches', []).append(str(status))
        if open_ch != nch:
            indata = indata[:, :nch]
        chunks.append(indata.copy())
        _update_peaks(state, indata)

    print(f"\n  RECORDING {nch} ch to {out}"
          + (f" for {duration:.0f} s" if duration else " -- Ctrl-C to stop"))
    print()
    t0 = time.time()
    first = [True]
    try:
        with sd.InputStream(device=dev, channels=open_ch, samplerate=sr,
                            dtype='float32', blocksize=2048, callback=cb):
            while True:
                el = time.time() - t0
                if not first[0]:
                    sys.stdout.write(_cursor_up(nch + 1))
                first[0] = False
                sys.stdout.write(f"\r  {el:6.1f}s elapsed{_clear_eol()}\n")
                for c in range(nch):
                    sys.stdout.write('\r' + _channel_line(
                        c, state['db'][c], state['hold'][c],
                        state['clips'][c], roles) + _clear_eol() + '\n')
                sys.stdout.flush()
                if duration and el >= duration:
                    break
                time.sleep(0.05 if TTY else 1.0)
    except KeyboardInterrupt:
        pass

    if not chunks:
        print("\n  nothing captured.", file=sys.stderr)
        sys.exit(2)

    x = np.concatenate(chunks, axis=0).astype(np.float64)
    if nch == 1:
        x = x[:, 0]
    wavio.write(out, x, sr, bits)
    if test_mode:
        provenance.mark(os.path.dirname(os.path.abspath(out)) or '.')

    print(f"\n  wrote {out}   {len(x)/sr:.2f} s   {sr} Hz   {bits}-bit   {nch} ch")
    for c in range(nch):
        print(f"    ch{c+1} {roles.get(c,''):<6} peak {state['hold'][c]:7.1f} dBFS"
              f"   clipped blocks {state['clips'][c]}")

    glitches = state.get('glitches')
    if glitches:
        # An overflow means samples were dropped. On a shot take that is not a
        # cosmetic warning -- the missing samples may be the peak itself.
        print(f"\n  *** {len(glitches)} STREAM GLITCH(ES): {glitches[0]}\n"
              "  Samples were dropped. Raise the blocksize or close other apps,\n"
              "  and treat this take as suspect.")

    if nch >= 2:
        sep = state['hold'][0] - state['hold'][1]
        print(f"\n  channel separation {sep:.1f} dB", end='')
        if state['clips'][1] == 0:
            print("  -- cold channel is clean, the peak is captured.")
        else:
            print("\n  *** COLD CHANNEL CLIPPED. The peak is gone from BOTH\n"
                  "  channels. Reduce ch2 gain and re-shoot. ***")

    print(f"\n  Now check it, before you change anything:\n"
          f"      python3 validate.py {out} --array\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--list', action='store_true', help='list input devices')
    ap.add_argument('--meter', action='store_true',
                    help='live peak meter for gain setting, records nothing')
    ap.add_argument('--device', help='device number OR part of its name, e.g. '
                                     '--device "MacBook" (numbers shift when '
                                     'something is plugged in or removed)')
    ap.add_argument('--sr', type=int, default=96000)
    ap.add_argument('--bits', type=int, default=24, choices=[16, 24, 32])
    ap.add_argument('--test-mode', action='store_true',
                    help='allow laptop mic / earbuds / virtual devices for a rig '
                         'check; output is marked as test data and barred from '
                         'the dataset')
    ap.add_argument('--channels', type=int, default=1, metavar='N',
                    help='input channels; use 2 for a staggered-gain array')
    ap.add_argument('--duration', type=float, help='seconds; omit for Ctrl-C')
    ap.add_argument('--out', help='output WAV path')
    args = ap.parse_args()

    sd = need_sd()

    if args.list:
        list_devices(sd)
        return 0
    if args.device is None:
        print("  --device is required. Run --list first.", file=sys.stderr)
        return 2
    args.device = resolve_device(sd, args.device)
    if args.meter:
        meter(sd, args.device, args.sr, args.channels, test_mode=args.test_mode)
        return 0
    if not args.out:
        print("  --out is required when recording.", file=sys.stderr)
        return 2
    record(sd, args.device, args.sr, args.out, args.duration,
           args.bits, args.channels, test_mode=args.test_mode)
    return 0


if __name__ == '__main__':
    sys.exit(main())
