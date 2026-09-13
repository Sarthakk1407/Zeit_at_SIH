"""Augmentations — all numpy, all run inside DataLoader workers.

Everything here maps to a named item in docs/01-system/workflow.md §5.4:
α-stable structured bursts, input-side clipping, room responses, and a
frequency-dependent head shadow instead of a flat scalar.
"""
import numpy as np
from scipy.signal import fftconvolve, lfilter


def db2lin(db):
    return 10.0 ** (db / 20.0)


def power(x):
    return float(np.mean(x.astype(np.float64) ** 2)) + 1e-12


# ----------------------------------------------------------------- α-stable
def alpha_stable(alpha, n, rng):
    """Symmetric α-stable samples (Chambers–Mallows–Stuck)."""
    U = rng.uniform(-np.pi / 2, np.pi / 2, n)
    W = rng.exponential(1.0, n)
    if abs(alpha - 1.0) < 1e-6:
        return np.tan(U)
    return (np.sin(alpha * U) / np.cos(U) ** (1 / alpha)
            * (np.cos(U - alpha * U) / W) ** ((1 - alpha) / alpha))


def structured_bursts(n, sr, rng, alpha_range=(0.4, 1.8), rate_hz=(0.5, 3.0)):
    """Gunshot-like events: heavy-tailed amplitude and arrival, real attack/decay.

    Plain i.i.d. α-stable noise has no envelope; a real impulse rises in
    under a millisecond and rings for tens to hundreds. So each event is an
    α-stable burst shaped by a fast-attack / exponential-decay envelope.
    """
    out = np.zeros(n)
    n_ev = max(1, rng.poisson(rng.uniform(*rate_hz) * n / sr))
    for _ in range(n_ev):
        a = rng.uniform(*alpha_range)
        att = int(sr * rng.uniform(0.0002, 0.002)) + 1
        dec = rng.uniform(0.02, 0.3)
        L = min(n, att + int(sr * dec * 5))
        t = np.arange(L) / sr
        env = np.minimum(np.arange(L) / att, 1.0) * np.exp(-np.maximum(t - att / sr, 0) / dec)
        burst = alpha_stable(a, L, rng)
        burst /= np.percentile(np.abs(burst), 99) + 1e-9     # scale robustly, never by RMS
        burst = np.clip(burst, -20, 20) * env
        # crude spectral colouring: blasts are low-heavy, cracks bright
        if rng.random() < 0.6:
            k = rng.uniform(0.3, 0.95)
            burst = lfilter([1 - k], [1, -k], burst)
        s = int(rng.integers(0, n))
        e = min(n, s + L)
        out[s:e] += burst[: e - s] * db2lin(rng.uniform(-12, 0))
    return out.astype(np.float32)


# ----------------------------------------------------------------- acoustics
def apply_rir(x, rir):
    rir = rir / (np.max(np.abs(rir)) + 1e-9)
    d = int(np.argmax(np.abs(rir)))                          # keep the direct path aligned
    y = fftconvolve(x, rir)[d:d + len(x)]
    return y.astype(np.float32)


def frac_delay(x, delay_samples):
    """Fractional delay via linear-phase FFT shift (fine for short clips)."""
    if abs(delay_samples) < 1e-6:
        return x
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n)
    return np.fft.irfft(X * np.exp(-2j * np.pi * f * delay_samples), n).astype(np.float32)


def head_shadow(x, sr, shelf_db, corner_hz=1500.0):
    """First-order high-shelf cut: the head blocks highs more than lows."""
    if shelf_db >= -0.1:
        return x
    k = np.exp(-2 * np.pi * corner_hz / sr)
    low = lfilter([1 - k], [1, -k], x)
    g = db2lin(shelf_db)
    return (low + g * (x - low)).astype(np.float32)


def clip(x, over_db, rng):
    """Input-side saturation: the capsule/ADC flat-tops the waveform before any algorithm sees it."""
    peak = np.max(np.abs(x)) + 1e-9
    ceiling = peak / db2lin(over_db)
    if rng.random() < 0.5:
        return np.clip(x, -ceiling, ceiling)
    return (ceiling * np.tanh(x / ceiling)).astype(np.float32)


def mix_at_snr(speech, noise, snr_db):
    """Gain g for `noise` so that 10*log10(P_speech / P(g*noise)) = snr_db."""
    return float(np.sqrt(power(speech) / (power(noise) * 10 ** (snr_db / 10.0))))
