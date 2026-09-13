"""Audio I/O, resampling and the STFT every other file agrees on.

The STFT here must be bit-for-bit the one the Jetson runtime uses:
512-point FFT, 256 hop, square-root periodic Hann for both analysis and
synthesis. Change it here and nowhere else.
"""
from fractions import Fraction

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly

N_FFT = 512
HOP = 256
N_BINS = N_FFT // 2 + 1          # 257


def read_segment(path, sr_out, n_out, rng, start=None):
    """Read a random `n_out`-sample mono segment at `sr_out`. Loops short files.

    Only the needed stretch of the file is read, so 100 GB of corpora costs no
    RAM. Multichannel files use one random channel.
    """
    info = sf.info(path)
    sr = info.samplerate
    need = int(np.ceil(n_out * sr / sr_out)) + 64
    total = info.frames
    if total <= need:
        x, _ = sf.read(path, dtype="float32", always_2d=True)
    else:
        s = int(rng.integers(0, total - need)) if start is None else int(start)
        x, _ = sf.read(path, start=s, frames=need, dtype="float32", always_2d=True)
    x = x[:, int(rng.integers(0, x.shape[1]))]
    x = resample(x, sr, sr_out)
    if len(x) < n_out:                                   # loop, don't zero-pad
        reps = int(np.ceil(n_out / max(len(x), 1)))
        x = np.tile(x, reps)
    return x[:n_out].astype(np.float32)


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    fr = Fraction(sr_out, sr_in).limit_denominator(1000)
    return resample_poly(x, fr.numerator, fr.denominator).astype(np.float32)


def window(device=None, dtype=torch.float32):
    return torch.sqrt(torch.hann_window(N_FFT, periodic=True, device=device, dtype=dtype))


def stft(x):
    """(..., N) waveform -> (..., F=257, T, 2) real/imag."""
    shape = x.shape[:-1]
    X = torch.stft(x.reshape(-1, x.shape[-1]), N_FFT, HOP, N_FFT,
                   window=window(x.device, x.dtype), center=True, return_complex=True)
    X = torch.view_as_real(X)
    return X.reshape(*shape, *X.shape[-3:])


def istft(X, length):
    """(..., F, T, 2) -> (..., N) waveform."""
    shape = X.shape[:-3]
    Xc = torch.view_as_complex(X.reshape(-1, *X.shape[-3:]).contiguous())
    x = torch.istft(Xc, N_FFT, HOP, N_FFT, window=window(X.device, X.dtype),
                    center=True, length=length)
    return x.reshape(*shape, length)
