"""
Shared DSP helpers for the field toolkit. numpy + scipy only.

Deliberately conservative: every function here runs at the range on a laptop
on battery, so nothing iterates over the whole file more than it must.
"""

import numpy as np
from scipy import signal

EPS = 1e-20
P_REF = 20e-6  # reference pressure, Pa


# ---------------------------------------------------------------- levels ----

def rms(x):
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(x * x)))


def dbfs(x):
    """Level in dB relative to full scale (1.0). Accepts scalar or array."""
    return 20.0 * np.log10(np.maximum(np.abs(x), EPS))


def rms_dbfs(x):
    return 20.0 * np.log10(max(rms(x), EPS))


def peak_dbfs(x):
    x = np.asarray(x)
    if x.size == 0:
        return -np.inf
    return 20.0 * np.log10(max(float(np.max(np.abs(x))), EPS))


def spl_from_pa(p):
    """SPL in dB re 20 uPa from a pressure value (Pa)."""
    return 20.0 * np.log10(max(abs(float(p)), EPS) / P_REF)


# --------------------------------------------------------------- filters ----

def _sos_band(sr, lo, hi, order=4):
    nyq = sr / 2.0
    lo = max(lo, 1.0)
    hi = min(hi, nyq * 0.999)
    if lo >= hi:
        return None
    return signal.butter(order, [lo / nyq, hi / nyq], btype='band', output='sos')


def bandpass(x, sr, lo, hi, order=4):
    sos = _sos_band(sr, lo, hi, order)
    if sos is None:
        return np.zeros_like(x)
    return signal.sosfiltfilt(sos, x)


def highpass(x, sr, fc, order=4):
    nyq = sr / 2.0
    sos = signal.butter(order, min(fc / nyq, 0.999), btype='high', output='sos')
    return signal.sosfiltfilt(sos, x)


def lowpass(x, sr, fc, order=4):
    nyq = sr / 2.0
    sos = signal.butter(order, min(fc / nyq, 0.999), btype='low', output='sos')
    return signal.sosfiltfilt(sos, x)


# ------------------------------------------------------------ band tables ---

def band_centers(sr, fraction=3, fmin=25.0, fmax=None):
    """Nominal 1/1- or 1/3-octave centres up to just under Nyquist."""
    if fmax is None:
        fmax = sr / 2.0 * 0.8
    step = 1.0 / fraction
    n = np.arange(-20, 40, 1.0)
    f = 1000.0 * (2.0 ** (n * step))
    return f[(f >= fmin) & (f <= fmax)]


def band_edges(fc, fraction=3):
    factor = 2.0 ** (1.0 / (2.0 * fraction))
    return fc / factor, fc * factor


def band_levels(x, sr, fraction=3, fmin=25.0, fmax=None, scale_pa=None):
    """Per-band RMS level. Returns (centres, levels_db).

    If scale_pa is given the levels are absolute SPL (dB re 20 uPa);
    otherwise they are dBFS.
    """
    centres = band_centers(sr, fraction, fmin, fmax)
    out = []
    for fc in centres:
        lo, hi = band_edges(fc, fraction)
        y = bandpass(x, sr, lo, hi)
        r = rms(y)
        if scale_pa is not None:
            out.append(spl_from_pa(r * scale_pa))
        else:
            out.append(20.0 * np.log10(max(r, EPS)))
    return centres, np.array(out)


# ---------------------------------------------------------- onset finding ---

def moving_rms_db(x, sr, win_s=0.005, hop_s=0.001):
    """Moving-RMS envelope in dB, one value per hop.

    Uses a cumulative sum rather than a framed gather: O(n) time and one
    temporary array, instead of the win/hop-times blow-up a stride trick
    costs. On a 60 s / 96 kHz file that is the difference between ~230 MB
    and ~46 MB, and it is why validate.py stays inside its time budget.
    """
    x = np.asarray(x, dtype=np.float64)
    win = max(int(win_s * sr), 8)
    hop = max(int(hop_s * sr), 1)
    if x.size <= win:
        return np.array([20.0 * np.log10(rms(x) + EPS)]), hop
    c = np.cumsum(np.concatenate(([0.0], x * x)))
    s = np.maximum(c[win:] - c[:-win], 0.0)
    env = np.sqrt(s / win)[::hop]
    return 20.0 * np.log10(env + EPS), hop


def spectral_flux_at(x, sr, centre, half_ms=25.0, n_fft=512):
    """Positive spectral flux in a short window around `centre` (samples).

    Used to confirm a candidate found by energy: a real impulsive event has a
    broadband spectral jump, a wind gust or a gain change does not.
    """
    half = int(half_ms * 1e-3 * sr)
    a = max(centre - half, 0)
    b = min(centre + half, len(x))
    seg = x[a:b]
    if len(seg) < 2 * n_fft:
        return 0.0
    hop = n_fft // 2
    n_frames = 1 + (len(seg) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    frames = seg[idx] * np.hanning(n_fft)
    spec = np.abs(np.fft.rfft(frames, axis=1))
    if spec.shape[0] < 2:
        return 0.0
    flux = np.maximum(np.diff(spec, axis=0), 0.0).sum(axis=1)
    denom = spec[:-1].sum(axis=1) + EPS
    return float(np.max(flux / denom))


def find_events(x, sr, min_sep_s=0.30, threshold=None, prominence_db=12.0,
                hp_hz=200.0, flux_min=0.25):
    """Locate impulsive events. Returns sample indices of each onset.

    hp_hz removes wind/handling rumble before detection -- without it a gust
    reads as an onset. Detection runs on the high-passed copy; returned
    indices refer to the original signal.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.size < sr // 100:
        return np.array([], dtype=int)

    xd = highpass(x, sr, hp_hz) if hp_hz else x
    env_db, hop = moving_rms_db(xd, sr)
    if env_db.size < 3:
        return np.array([], dtype=int)

    # Low percentile is robust to the events themselves
    floor_db = float(np.percentile(env_db, 20.0))
    peak_db = float(np.percentile(env_db, 99.99))
    thr = (max(floor_db + prominence_db, peak_db - 40.0)
           if threshold is None else threshold)

    min_sep_frames = max(int(min_sep_s * sr / hop), 1)
    peaks, _ = signal.find_peaks(env_db, height=thr, distance=min_sep_frames)

    onsets = []
    for p in peaks:
        if flux_min > 0:
            if spectral_flux_at(xd, sr, int(p) * hop) < flux_min:
                continue  # energy rose, but not broadband -- not an impulse
        # Walk back to the threshold crossing: that is the true onset,
        # and it is where the cut must go.
        j = int(p)
        limit = floor_db + 0.5 * prominence_db
        while j > 0 and env_db[j] > limit:
            j -= 1
        onsets.append(j * hop)
    return np.array(sorted(set(onsets)), dtype=int)


# -------------------------------------------------------------- reverb ------

def schroeder_edc(ir, sr):
    """Backward-integrated energy decay curve, in dB, normalised to 0 at t=0."""
    e = np.asarray(ir, dtype=np.float64) ** 2
    edc = np.cumsum(e[::-1])[::-1]
    edc = edc / max(edc[0], EPS)
    return 10.0 * np.log10(np.maximum(edc, EPS))


def rt60_from_edc(edc_db, sr, lo_db=-5.0, hi_db=-25.0):
    """Fit the EDC between two levels and extrapolate to 60 dB of decay.

    Returns (rt60_s, r_squared) or (nan, nan) if the decay never gets there.
    """
    try:
        i0 = int(np.argmax(edc_db <= lo_db))
        i1 = int(np.argmax(edc_db <= hi_db))
    except ValueError:
        return float('nan'), float('nan')
    if i1 <= i0 or i1 == 0:
        return float('nan'), float('nan')

    t = np.arange(i0, i1) / sr
    y = edc_db[i0:i1]
    if len(t) < 10:
        return float('nan'), float('nan')

    A = np.vstack([t, np.ones_like(t)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    slope = coef[0]
    if slope >= -EPS:
        return float('nan'), float('nan')

    pred = A @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return float(-60.0 / slope), r2


# --------------------------------------------------------------- misc -------

def fmt_db(v, width=7):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return '   n/a '.rjust(width)
    return f"{v:{width}.1f}"
