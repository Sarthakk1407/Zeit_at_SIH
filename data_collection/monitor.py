#!/usr/bin/env python3
"""
monitor.py -- live scope. A window showing what the microphone is doing, now.

    python3 monitor.py --device 3
    python3 monitor.py --device 3 --test-mode      # laptop mic / earbuds
    python3 monitor.py --device 3 --channels 2     # staggered-gain array

Four panels, each answering a question you otherwise only get to ask after the
take is already ruined:

  waveform   is it clipping, is there handling noise, is anything arriving
  spectrum   is the top of the band ALIVE -- an empty top means the device
             resampled and your 96 kHz file is really 44.1 kHz wearing a label
  level      peak hold against the -18..-12 dBFS gain target
  rumble     sub-50 Hz energy, i.e. wind getting into the windshield

Close the window to quit. Press r to reset the peak hold.
"""

import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp  # noqa: E402

SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK2 = '#52514e'
GRID = '#e5e4df'
BLUE = '#2a78d6'
BLUE_FILL = '#9ec5f4'
GOOD = '#0ca30c'
WARN = '#fab219'
CRIT = '#d03b3b'


def need_sd():
    try:
        import sounddevice as sd
        return sd
    except ImportError:
        print("\n  sounddevice is not installed:\n"
              "      python3 -m pip install sounddevice\n", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--device', required=True,
                    help='device number OR part of its name, e.g. "MacBook"')
    ap.add_argument('--sr', type=int, default=96000)
    ap.add_argument('--channels', type=int, default=1)
    ap.add_argument('--test-mode', action='store_true',
                    help='allow laptop mic / earbuds / virtual devices')
    ap.add_argument('--window', '--seconds', type=float, default=2.0,
                    dest='window',
                    help='how many seconds of history the waveform and '
                         'spectrogram show (--seconds is accepted too)')
    ap.add_argument('--fps', type=float, default=20.0)
    ap.add_argument('--no-mark', action='store_true',
                    help='do not write the synthetic marker (the caller will)')
    ap.add_argument('--snapshot', metavar='PNG',
                    help='headless: capture --seconds of audio, render ONE '
                         'frame to this PNG and exit. No window. Use it to '
                         'check the display without a screen.')
    ap.add_argument('--duration', type=float, metavar='SEC',
                    help='close the window automatically after about N '
                         'seconds. Approximate -- window setup and teardown '
                         'add a few seconds, and the whole time is captured. '
                         'The printed duration is the real one.')
    ap.add_argument('--record', metavar='FILE',
                    help='ALSO write everything to this WAV while monitoring -- '
                         'without it the monitor saves nothing and a take you '
                         'watched go perfectly leaves no record at all')
    args = ap.parse_args()

    sd = need_sd()
    import record as R  # reuse the device guard, so the traps stay in one place
    args.device = R.resolve_device(sd, args.device)
    _info, sr = R.check_device(sd, args.device, args.sr, args.channels,
                               args.test_mode)
    # Open the device's own channel count and slice; see R.open_channels.
    open_ch = R.open_channels(_info, args.channels)

    import matplotlib
    if args.snapshot:
        matplotlib.use('Agg')
    else:
        matplotlib.use('macosx' if sys.platform == 'darwin' else 'TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    nch = args.channels
    N = int(args.window * sr)
    ring = np.zeros((N, nch))
    widx = [0]
    # Per-channel, matching record.py. The display indexes state['hold'][c];
    # a scalar here made update() throw on every frame, and FuncAnimation
    # swallowed the exception -- the window opened and never drew anything.
    state = R._peak_state(nch)
    state['over'] = 0
    if args.record and os.path.exists(args.record):
        print(f"\n  REFUSING: {args.record} already exists.\n", file=sys.stderr)
        return 2

    # Stream straight to disk. Holding a long take in RAM until the window
    # closes means a crash, a full disk or a flat battery loses everything --
    # and an hour at 48 kHz is ~700 MB before the final copy. A writer thread
    # keeps blocking file I/O out of the audio callback.
    import queue as _queue
    import threading as _threading
    import wavio as _wavio

    writer = None
    wq = _queue.Queue()
    if args.record:
        writer = _wavio.StreamWriter(args.record, sr, nch, 24)

        def _drain():
            while True:
                blk = wq.get()
                if blk is None:
                    break
                try:
                    writer.append(blk)
                except Exception as e:
                    print(f"\n  WRITE FAILED: {e}", file=sys.stderr)
        wt = _threading.Thread(target=_drain, daemon=True)
        wt.start()

    def cb(indata, frames, t, status):
        if status:
            state['over'] += 1
        if open_ch != nch:
            indata = indata[:, :nch]
        if writer is not None:
            wq.put(indata.copy())
        n = len(indata)
        i = widx[0]
        if i + n <= N:
            ring[i:i + n] = indata
        else:
            k = N - i
            ring[i:] = indata[:k]
            ring[:n - k] = indata[k:]
        widx[0] = (i + n) % N
        R._update_peaks(state, indata)

    plt.rcParams.update({
        'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
        'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'text.color': INK,
        'xtick.color': INK2, 'ytick.color': INK2, 'grid.color': GRID,
        'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 9,
        'axes.titlesize': 10, 'axes.titleweight': 'semibold',
        'axes.titlelocation': 'left',
    })
    fig = plt.figure(figsize=(14, 9))
    fig.canvas.manager.set_window_title(f"monitor — device {args.device} @ {sr} Hz")
    gs = fig.add_gridspec(4, 3, width_ratios=[1.5, 1.5, 1.25],
                          height_ratios=[1, 1.5, 1.2, 0.9],
                          hspace=0.62, wspace=0.30)

    # --- waveform
    ax_w = fig.add_subplot(gs[0, 0:2])
    DISP = 2000  # decimated display points; plotting 192k points kills the fps
    tw = np.linspace(-args.window, 0, DISP)
    wlines = [ax_w.plot(tw, np.zeros(DISP), lw=0.6,
                        color=BLUE if c == 0 else '#eb6834')[0]
              for c in range(nch)]
    ax_w.set_ylim(-1.05, 1.05)
    ax_w.set_xlim(-args.window, 0)
    wscale = [1.0]
    ax_w.axhline(1.0, color=CRIT, lw=0.7, ls='--')
    ax_w.axhline(-1.0, color=CRIT, lw=0.7, ls='--')
    ax_w.set_ylabel('amplitude')
    ax_w.set_title('waveform')
    ax_w.grid(alpha=0.4)

    # --- spectrogram waterfall
    ax_g = fig.add_subplot(gs[1, 0:2])
    SG_N = 512
    SG_COLS = 240
    sg_freqs = np.fft.rfftfreq(SG_N, 1.0 / sr)
    sgram = np.full((len(sg_freqs), SG_COLS), -120.0)
    im = ax_g.imshow(sgram, origin='lower', aspect='auto', cmap='magma',
                     vmin=-110, vmax=-20,
                     extent=[-args.window, 0, sg_freqs[0], sg_freqs[-1]])
    ax_g.set_ylabel('frequency (Hz)')
    ax_g.set_title('spectrogram — impulses show as vertical broadband lines')
    fig.colorbar(im, ax=ax_g, pad=0.01, label='dB')

    # --- spectrum
    ax_s = fig.add_subplot(gs[2, 0:2])
    NFFT = 16384
    freqs = np.fft.rfftfreq(NFFT, 1.0 / sr)
    slines = [ax_s.semilogx(freqs[1:], np.full(len(freqs) - 1, -140.0), lw=1.2,
                            color=BLUE if c == 0 else '#eb6834')[0]
              for c in range(nch)]
    ax_s.set_xlim(20, sr / 2)
    ax_s.set_ylim(-140, 0)
    sscale = [0.0]
    ax_s.set_ylabel('dBFS')
    ax_s.set_xlabel('Hz')
    ax_s.set_title('spectrum — a flat dead top means the device is resampling')
    ax_s.grid(alpha=0.4, which='both')
    ax_s.axvspan(sr / 2 * 0.9, sr / 2, color=CRIT, alpha=0.07)

    # --- level
    ax_l = fig.add_subplot(gs[3, 0])
    ax_l.set_xlim(-72, 0)
    ax_l.set_ylim(-0.5, nch - 0.5)
    ax_l.axvspan(-18, -12, color=GOOD, alpha=0.16)
    ax_l.axvline(0, color=CRIT, lw=1.2)
    # Grow from the floor to the level, not from 0 leftwards: a bar whose
    # LEFT edge is the reading reads backwards at a glance.
    LFLOOR = -72.0
    bars = ax_l.barh(range(nch), [0.0] * nch, left=LFLOOR, height=0.5,
                     color=BLUE)
    holds = [ax_l.axvline(-120, color=INK, lw=1.6) for _ in range(nch)]
    ax_l.set_yticks(range(nch))
    ax_l.set_yticklabels([f"ch{c+1}" + (' HOT' if nch == 2 and c == 0 else
                                        ' COLD' if nch == 2 else '')
                          for c in range(nch)])
    ax_l.set_xlabel('dBFS  (green = gain target)')
    ax_l.set_title('level, black = peak hold')
    ax_l.grid(alpha=0.4, axis='x')

    # --- rumble
    ax_r = fig.add_subplot(gs[3, 1])
    ax_r.set_xlim(-40, 5)
    ax_r.set_ylim(-0.5, 0.5)
    rbar = ax_r.barh([0], [-40], height=0.4, color=GOOD)
    ax_r.axvline(-10, color=WARN, lw=1.2, ls='--')
    ax_r.axvline(-3, color=CRIT, lw=1.2, ls='--')
    ax_r.set_yticks([])
    ax_r.set_xlabel('sub-50 Hz vs total (dB)')
    ax_r.set_title('wind / rumble')
    ax_r.grid(alpha=0.4, axis='x')

    # --- live measurement readout: the numbers the dataset is actually made of
    ax_m = fig.add_subplot(gs[:, 2])
    ax_m.axis('off')
    ax_m.set_title('measured, live', loc='left')
    metrics_txt = ax_m.text(0.0, 0.985, '', va='top', ha='left',
                            family='monospace', fontsize=9.5, color=INK,
                            transform=ax_m.transAxes, linespacing=1.55)

    txt = fig.text(0.99, 0.985, '', ha='right', va='top', fontsize=11,
                   family='monospace', color=INK)

    win = np.hanning(NFFT)
    sg_win = np.hanning(SG_N)
    slow = {'n': 0, 'lines': 'measuring...'}

    def snapshot():
        i = widx[0]
        return np.concatenate([ring[i:], ring[:i]], axis=0)

    def measure(buf, sp, freqs_):
        """The same quantities analyze.py records, computed on what is on screen."""
        x0 = buf[:, 0]
        pk = float(np.max(np.abs(x0))) if x0.size else 0.0
        rms = float(np.sqrt(np.mean(x0 ** 2))) if x0.size else 0.0
        d = lambda v: 20 * np.log10(v) if v > 0 else -120.0

        power = sp[1:] ** 2
        tot = float(np.sum(power)) + 1e-24
        f1 = freqs_[1:]
        centroid = float(np.sum(f1 * power) / tot)
        cum = np.cumsum(power) / tot
        roll = float(f1[int(np.argmax(cum >= 0.95))])
        peak_f = float(f1[int(np.argmax(power))])

        def band(lo, hi):
            m = (f1 >= lo) & (f1 < hi)
            return 10 * np.log10(float(np.sum(power[m])) / tot + 1e-12)

        nyq = sr / 2.0
        zeros = float(np.mean(x0 == 0.0)) * 100.0
        ev = 0
        try:
            ev = len(dsp.find_events(x0, sr))
        except Exception:
            pass

        L = []
        L.append(f"{'LEVEL':<12}")
        L.append(f"  peak      {d(pk):8.1f} dBFS")
        L.append(f"  peak hold {state['hold'][0]:8.1f} dBFS")
        L.append(f"  rms/Leq   {d(rms):8.1f} dBFS")
        L.append(f"  crest     {d(pk) - d(rms):8.1f} dB")
        L.append("")
        L.append(f"{'FREQUENCY':<12}")
        L.append(f"  centroid  {centroid:8.0f} Hz")
        L.append(f"  peak freq {peak_f:8.0f} Hz")
        L.append(f"  95% roll  {roll:8.0f} Hz")
        L.append("")
        L.append(f"{'BAND SPLIT':<12}")
        L.append(f"  <100 Hz   {band(0, 100):8.1f} dB")
        L.append(f"  100-1k    {band(100, 1000):8.1f} dB")
        L.append(f"  1k-8k     {band(1000, 8000):8.1f} dB")
        L.append(f"  >8k       {band(8000, nyq):8.1f} dB")
        L.append("")
        L.append(f"{'QUALITY':<12}")
        L.append(f"  clips     {state['clips'][0]:8d}")
        L.append(f"  dropouts  {zeros:8.2f} %")
        L.append(f"  dropped   {state['over']:8d} blk")
        L.append(f"  events    {ev:8d}")
        return '\n'.join(L)

    def update(_):
        buf = snapshot()
        step = max(len(buf) // DISP, 1)
        for c in range(nch):
            seg = buf[:step * DISP, c].reshape(DISP, step)
            wlines[c].set_ydata(np.where(
                np.abs(seg.max(axis=1)) >= np.abs(seg.min(axis=1)),
                seg.max(axis=1), seg.min(axis=1)))

        # Auto-zoom while the signal is quiet. Fixed +/-1 is right for a
        # gunshot -- clipping is what you must see -- but at -46 dBFS a room
        # tone is a flat line on that scale and the panel looks broken.
        pk_all = float(np.max(np.abs(buf))) if buf.size else 0.0
        want = 1.05 if pk_all > 0.4 else max(pk_all * 1.6, 1e-4)
        if abs(want - wscale[0]) / max(wscale[0], 1e-9) > 0.25:
            wscale[0] = want
            ax_w.set_ylim(-want, want)
            ax_w.set_title('waveform' + ('' if want >= 1.0 else
                                         f'   (zoomed to +/-{want:.3f})'))

        # spectrogram: recompute the whole visible window, cheap at 512 pts
        hop = max(len(buf) // SG_COLS, 1)
        cols = []
        for k in range(SG_COLS):
            a = k * hop
            seg = buf[a:a + SG_N, 0]
            if len(seg) < SG_N:
                seg = np.pad(seg, (0, SG_N - len(seg)))
            m = np.abs(np.fft.rfft(seg * sg_win)) / (SG_N / 4)
            cols.append(20 * np.log10(m + 1e-12))
        sg = np.array(cols).T
        im.set_data(sg)
        top = float(np.percentile(sg, 99.5))
        im.set_clim(top - 70.0, top)

        tail = buf[-NFFT:]
        rum_db = -40.0
        sp0 = None
        for c in range(nch):
            seg = tail[:, c]
            if len(seg) < NFFT:
                continue
            sp = np.abs(np.fft.rfft(seg * win)) / (NFFT / 4)
            sdb = 20 * np.log10(sp[1:] + 1e-12)
            slines[c].set_ydata(sdb)
            if c == 0:
                hi = float(np.max(sdb))
                if abs(hi - sscale[0]) > 6.0:
                    sscale[0] = hi
                    ax_s.set_ylim(hi - 100.0, hi + 10.0)
            pk = float(np.max(np.abs(seg)))
            db = 20 * np.log10(pk) if pk > 0 else -120.0
            bars[c].set_width(max(db, LFLOOR) - LFLOOR)
            bars[c].set_color(CRIT if db >= -0.1 else
                              WARN if db > -6 else BLUE)
            holds[c].set_xdata([state['hold'][c], state['hold'][c]])
            if c == 0:
                sp0 = sp
                power = sp[1:] ** 2
                lf_p = float(np.sum(power[freqs[1:] < 50]))
                rum_db = 10 * np.log10((lf_p + 1e-24) /
                                       (float(np.sum(power)) + 1e-24))
        rbar[0].set_width(max(min(rum_db, 5), -40))
        rbar[0].set_color(CRIT if rum_db > -3 else
                          WARN if rum_db > -10 else GOOD)

        # The full metric set is heavier than a frame; refresh it ~2x a second
        slow['n'] += 1
        if sp0 is not None and (slow['n'] == 1 or
                                slow['n'] % max(int(args.fps // 2), 1) == 0):
            slow['lines'] = measure(buf, sp0, freqs)
        metrics_txt.set_text(slow['lines'])

        msg = f"peak hold {state['hold'][0]:6.1f} dBFS"
        if state['clips'][0]:
            msg += f"   CLIPS {state['clips'][0]}"
        if state['over']:
            msg += f"   dropouts {state['over']}"
        txt.set_text(msg)
        txt.set_color(CRIT if state['clips'][0] else INK)
        _maybe_autoclose()
        return wlines + slines + list(bars) + holds + [rbar[0], txt, im,
                                                       metrics_txt]

    # Timed from when the STREAM opens, not the first animation frame: window
    # creation can take several seconds and audio is captured throughout.
    t_start = [None]

    def _maybe_autoclose():
        import time as _t
        if not args.duration or t_start[0] is None:
            return
        if _t.time() - t_start[0] >= args.duration:
            plt.close(fig)

    def on_key(e):
        if e.key == 'r':
            state['hold'] = [-120.0] * nch
            state['clips'] = [0] * nch
    fig.canvas.mpl_connect('key_press_event', on_key)

    print(f"\n  live monitor: device {args.device}, {sr} Hz, {nch} ch")
    print("  close the window to quit, press r to reset the peak hold\n")
    import time as _time
    if args.snapshot:
        # Fill the ring from a plain blocking read, render one frame, done.
        n = int(args.window * sr)
        rec = sd.rec(n, samplerate=sr, channels=open_ch, device=args.device,
                     dtype='float32')
        sd.wait()
        cb(rec, n, None, None)
        update(0)
        fig.savefig(args.snapshot, dpi=100, bbox_inches='tight')
        pk = float(np.max(np.abs(rec)))
        print(f"\n  snapshot -> {args.snapshot}")
        print(f"  {args.window:.1f} s from device {args.device} at {sr} Hz, "
              f"peak {20*np.log10(pk) if pk>0 else -999:.1f} dBFS\n")
        return 0

    with sd.InputStream(device=args.device, channels=open_ch, samplerate=sr,
                        dtype='float32', blocksize=2048, callback=cb):
        t_start[0] = _time.time()
        _anim = FuncAnimation(fig, update, interval=1000 / args.fps,
                              blit=False, cache_frame_data=False)
        plt.show()

    if args.record is None:
        print("\n  Nothing was saved -- the monitor is a view, not a recorder.\n"
              "  Pass --record FILE to keep what you just watched.\n")
        return 0

    wq.put(None)
    wt.join(timeout=10)
    writer.close()

    if writer.frames == 0:
        print("\n  *** NOTHING WAS CAPTURED -- no audio reached the callback.\n"
              f"  {args.record} is empty. Check the device is not muted and\n"
              "  that microphone permission is granted.\n", file=sys.stderr)
        return 2

    if args.test_mode and not args.no_mark:
        import provenance
        provenance.mark(os.path.dirname(os.path.abspath(args.record)) or '.')

    size = os.path.getsize(args.record)
    dur = writer.frames / sr
    print(f"\n  wrote {args.record}")
    print(f"  {dur:.2f} s   {sr} Hz   24-bit   {nch} ch   {size/1e6:.1f} MB")
    for c in range(nch):
        print(f"  ch{c+1} peak {state['hold'][c]:.1f} dBFS   "
              f"clips {state['clips'][c]}"
              + (f"   dropouts {state['over']}" if state['over'] else ""))
    print(f"\n  Check it now:\n      python3 validate.py {args.record} "
          f"--expect-sr {sr}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
