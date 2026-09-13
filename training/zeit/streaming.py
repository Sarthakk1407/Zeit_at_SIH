"""Frame-by-frame STFT -> model -> ISTFT, in numpy.

Shared by enhance.py (offline, to prove parity) and jetson/realtime.py (live),
so the live headset runs exactly the code the parity check exercised.

Framing matches zeit/audio.py: 512-sample sqrt-Hann window, 256 hop. Output is
delayed by one hop relative to input plus the 512-sample window, i.e. 32 ms
algorithmic latency at 16 kHz.
"""
import numpy as np

N_FFT, HOP = 512, 256
WIN = np.sqrt(np.hanning(N_FFT + 1)[:-1]).astype(np.float32)   # periodic sqrt-Hann


class OnnxStreamer:
    """Holds the ONNX session and its carried state. One call per 256-sample hop."""

    def __init__(self, onnx_path, mics, providers=None):
        import onnxruntime as ort
        self.sess = ort.InferenceSession(onnx_path, providers=providers or ["CPUExecutionProvider"])
        self.mics = mics
        self.reset()

    def reset(self):
        self.conv = np.zeros((1, 6, 16, 10, 33), np.float32)
        self.tra = np.zeros((6, 1, 16), np.float32)
        self.inter = np.zeros((4, 33, 8), np.float32)
        self.inbuf = np.zeros((self.mics, N_FFT), np.float32)
        self.ola = np.zeros(N_FFT - HOP, np.float32)

    def process(self, hop):
        """hop: (mics, 256) float32 -> (256,) enhanced Mic 1."""
        self.inbuf = np.concatenate([self.inbuf[:, HOP:], hop], axis=1)
        X = np.fft.rfft(self.inbuf * WIN, axis=-1)                     # (mics, 257)
        frame = np.stack([X.real, X.imag], axis=-1)[None, :, :, None, :].astype(np.float32)
        enh, self.conv, self.tra, self.inter = self.sess.run(
            None, dict(frame=frame, conv_cache=self.conv, tra_cache=self.tra, inter_cache=self.inter))
        Y = enh[0, :, 0, 0] + 1j * enh[0, :, 0, 1]
        y = np.fft.irfft(Y, N_FFT).astype(np.float32) * WIN
        out = self.ola[:HOP] + y[:HOP]
        self.ola = np.concatenate([self.ola[HOP:], np.zeros(HOP, np.float32)]) + y[HOP:]
        return out

    def bypass(self, hop):
        """What the listener hears with the model off: Mic 1, same latency."""
        self.inbuf = np.concatenate([self.inbuf[:, HOP:], hop], axis=1)
        return self.inbuf[0, :HOP].copy()
