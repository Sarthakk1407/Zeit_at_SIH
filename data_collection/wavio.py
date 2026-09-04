"""
Self-contained WAV reader/writer. numpy only.

Why not soundfile: the range has no internet. If libsndfile is missing or the
wheel is broken on range day, the whole toolkit is dead. This is a plain RIFF
parser -- 16/24/32-bit int, 32/64-bit float, WAVE_FORMAT_EXTENSIBLE.

Everything returns float64 in [-1, 1]. The integer full-scale info needed for
honest clipping detection is preserved in the returned `info` dict.
"""

import os
import struct
import numpy as np

FMT_PCM = 0x0001
FMT_FLOAT = 0x0003
FMT_EXTENSIBLE = 0xFFFE


class WavError(Exception):
    pass


def _chunks(buf):
    """Yield (chunk_id, payload_bytes) walking the RIFF chunk list."""
    pos = 12  # skip 'RIFF' + size + 'WAVE'
    n = len(buf)
    while pos + 8 <= n:
        cid = buf[pos:pos + 4]
        (size,) = struct.unpack('<I', buf[pos + 4:pos + 8])
        start = pos + 8
        end = start + size
        if end > n:
            # Truncated final chunk -- common when a recorder loses power
            # mid-write. Salvage what is there rather than failing.
            end = n
        yield cid, buf[start:end]
        pos = end + (size & 1)  # chunks are word-aligned


def read(path):
    """Read a WAV file.

    Returns (data, sr, info) where data is float64 of shape (n,) for mono or
    (n, channels) for multichannel.
    """
    with open(path, 'rb') as f:
        buf = f.read()

    if len(buf) < 12 or buf[0:4] != b'RIFF' or buf[8:12] != b'WAVE':
        raise WavError(f"{path}: not a RIFF/WAVE file (bad header)")

    fmt = None
    data_bytes = None
    truncated = False

    for cid, payload in _chunks(buf):
        if cid == b'fmt ':
            fmt = payload
        elif cid == b'data':
            data_bytes = payload

    if fmt is None:
        raise WavError(f"{path}: no 'fmt ' chunk found")
    if data_bytes is None:
        raise WavError(f"{path}: no 'data' chunk found")
    if len(fmt) < 16:
        raise WavError(f"{path}: 'fmt ' chunk is too short ({len(fmt)} bytes)")

    audio_fmt, channels, sr, _byte_rate, block_align, bits = struct.unpack(
        '<HHIIHH', fmt[:16])

    if audio_fmt == FMT_EXTENSIBLE:
        if len(fmt) < 40:
            raise WavError(f"{path}: EXTENSIBLE fmt chunk truncated")
        # SubFormat GUID's first 2 bytes carry the real format code
        (audio_fmt,) = struct.unpack('<H', fmt[24:26])

    if channels < 1:
        raise WavError(f"{path}: invalid channel count {channels}")
    if sr < 1:
        raise WavError(f"{path}: invalid sample rate {sr}")

    bytes_per_sample = bits // 8
    frame_bytes = bytes_per_sample * channels
    if frame_bytes == 0:
        raise WavError(f"{path}: invalid bit depth {bits}")

    n_frames = len(data_bytes) // frame_bytes
    usable = n_frames * frame_bytes
    if usable != len(data_bytes):
        truncated = True
        data_bytes = data_bytes[:usable]

    if audio_fmt == FMT_PCM:
        if bits == 16:
            raw = np.frombuffer(data_bytes, dtype='<i2').astype(np.float64)
            full = 2.0 ** 15
        elif bits == 24:
            b = np.frombuffer(data_bytes, dtype=np.uint8).reshape(-1, 3)
            # little-endian 24-bit -> signed 32-bit
            ints = (b[:, 0].astype(np.int32)
                    | (b[:, 1].astype(np.int32) << 8)
                    | (b[:, 2].astype(np.int8).astype(np.int32) << 16))
            raw = ints.astype(np.float64)
            full = 2.0 ** 23
        elif bits == 32:
            raw = np.frombuffer(data_bytes, dtype='<i4').astype(np.float64)
            full = 2.0 ** 31
        elif bits == 8:
            # 8-bit WAV is unsigned, offset binary
            raw = np.frombuffer(data_bytes, dtype=np.uint8).astype(np.float64) - 128.0
            full = 2.0 ** 7
        else:
            raise WavError(f"{path}: unsupported PCM bit depth {bits}")
        data = raw / full
        lsb = 1.0 / full
    elif audio_fmt == FMT_FLOAT:
        if bits == 32:
            data = np.frombuffer(data_bytes, dtype='<f4').astype(np.float64)
        elif bits == 64:
            data = np.frombuffer(data_bytes, dtype='<f8').astype(np.float64)
        else:
            raise WavError(f"{path}: unsupported float bit depth {bits}")
        lsb = 0.0  # float has no meaningful LSB for clip detection
    else:
        raise WavError(
            f"{path}: unsupported audio format code 0x{audio_fmt:04X} "
            "(only PCM and IEEE float are supported)")

    if channels > 1:
        data = data.reshape(-1, channels)

    info = {
        'sample_rate': sr,
        'channels': channels,
        'bit_depth': bits,
        'format': 'float' if audio_fmt == FMT_FLOAT else 'pcm',
        'n_frames': n_frames,
        'duration_s': n_frames / float(sr),
        'lsb': lsb,
        'block_align': block_align,
        'truncated_data_chunk': truncated,
    }
    return np.ascontiguousarray(data), sr, info


def write(path, data, sr, bit_depth=24):
    """Write a WAV file. data may be (n,) or (n, channels), float in [-1, 1]."""
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        channels = 1
        flat = data
    elif data.ndim == 2:
        channels = data.shape[1]
        flat = data.reshape(-1)
    else:
        raise WavError("data must be 1-D or 2-D")

    # NOTE: must test the string case first and by identity of type, because
    # in Python `32 == 32.0` is True -- a naive `in ('float32', 32.0)` test
    # silently turns requested 32-bit PCM into float. That bit us once already.
    if isinstance(bit_depth, str):
        if bit_depth.lower() not in ('float32', 'float'):
            raise WavError(f"unsupported bit_depth {bit_depth!r}")
        payload = flat.astype('<f4').tobytes()
        bits, audio_fmt = 32, FMT_FLOAT
    # Scale by 2**(bits-1) and clip -- NOT by 2**(bits-1)-1. read() divides by
    # 2**(bits-1), so multiplying back by one less is asymmetric and costs a
    # least-significant bit on the way out. It only bites near full scale,
    # which in a gunshot dataset is precisely the peak -- the one number the
    # whole exercise exists to capture. Caught by checking that a sliced event
    # is bit-identical to its source region; it was off by exactly 1 LSB.
    elif bit_depth == 16:
        q = np.clip(np.round(flat * 32768.0), -32768, 32767).astype('<i2')
        payload = q.tobytes()
        bits, audio_fmt = 16, FMT_PCM
    elif bit_depth == 24:
        q = np.clip(np.round(flat * 8388608.0), -8388608, 8388607).astype('<i4')
        b = q.view(np.uint8).reshape(-1, 4)[:, :3]  # little-endian: drop MSB
        payload = np.ascontiguousarray(b).tobytes()
        bits, audio_fmt = 24, FMT_PCM
    elif bit_depth == 32:
        q = np.clip(np.round(flat * 2147483648.0),
                    -2147483648, 2147483647).astype('<i4')
        payload = q.tobytes()
        bits, audio_fmt = 32, FMT_PCM
    else:
        raise WavError(f"unsupported bit_depth {bit_depth!r}")

    block_align = channels * bits // 8
    fmt_chunk = struct.pack('<HHIIHH', audio_fmt, channels, sr,
                            sr * block_align, block_align, bits)
    if len(payload) & 1:
        payload_padded = payload + b'\x00'
    else:
        payload_padded = payload

    riff_size = 4 + (8 + len(fmt_chunk)) + (8 + len(payload_padded))
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', riff_size) + b'WAVE')
        f.write(b'fmt ' + struct.pack('<I', len(fmt_chunk)) + fmt_chunk)
        f.write(b'data' + struct.pack('<I', len(payload)) + payload_padded)


def to_mono(data):
    """Collapse to mono by averaging channels."""
    if data.ndim == 1:
        return data
    return data.mean(axis=1)


class StreamWriter:
    """Append-as-you-go WAV writer.

    Holding a whole take in RAM until the window closes means a crash, a full
    disk or a flat battery loses the entire recording -- and a one-hour take at
    48 kHz is ~700 MB of float32 before the final copy. This writes each block
    straight to disk instead.

    The header is written with placeholder sizes and patched on close. If the
    process dies first the sizes stay wrong, but read() already salvages a
    truncated data chunk, so the audio up to the crash is still recoverable.
    """

    def __init__(self, path, sr, channels=1, bit_depth=24):
        if bit_depth not in (16, 24, 32):
            raise WavError(f"StreamWriter supports 16/24/32-bit, not {bit_depth}")
        self.path = path
        self.sr = sr
        self.channels = channels
        self.bits = bit_depth
        self.frames = 0
        self._f = open(path, 'wb')
        self._write_header(0)

    def _write_header(self, data_bytes):
        block_align = self.channels * self.bits // 8
        fmt = struct.pack('<HHIIHH', FMT_PCM, self.channels, self.sr,
                          self.sr * block_align, block_align, self.bits)
        self._f.seek(0)
        self._f.write(b'RIFF' + struct.pack('<I', 4 + 8 + len(fmt) + 8 + data_bytes)
                      + b'WAVE')
        self._f.write(b'fmt ' + struct.pack('<I', len(fmt)) + fmt)
        self._f.write(b'data' + struct.pack('<I', data_bytes))

    def append(self, block):
        """block: (n, channels) or (n,) float in [-1, 1]."""
        a = np.asarray(block, dtype=np.float64)
        if a.ndim == 1:
            a = a[:, None]
        flat = a.reshape(-1)
        if self.bits == 16:
            q = np.clip(np.round(flat * 32768.0), -32768, 32767).astype('<i2')
            payload = q.tobytes()
        elif self.bits == 24:
            q = np.clip(np.round(flat * 8388608.0),
                        -8388608, 8388607).astype('<i4')
            b = q.view(np.uint8).reshape(-1, 4)[:, :3]
            payload = np.ascontiguousarray(b).tobytes()
        else:
            q = np.clip(np.round(flat * 2147483648.0),
                        -2147483648, 2147483647).astype('<i4')
            payload = q.tobytes()
        self._f.write(payload)
        self.frames += a.shape[0]

    def close(self):
        if self._f is None:
            return
        data_bytes = self.frames * self.channels * self.bits // 8
        if data_bytes & 1:
            self._f.write(b'\x00')
        self._write_header(data_bytes)
        self._f.flush()
        os.fsync(self._f.fileno())
        self._f.close()
        self._f = None
