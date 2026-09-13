"""The dataset: an index of files on disk, and a dual-microphone mixer on top.

Nothing mixed is ever written to disk. Each item is built fresh:

    Mic 1 = speech                         + g·noise_1          (boom, at the mouth)
    Mic 2 = leak·speech (delayed, shadowed) + g·a·noise_2        (outer earcup)
    target = speech                                              (clean, at Mic 1)

noise_1 / noise_2 are the same noise field reaching two points ~20 cm apart:
two channels of one multichannel RIR when available, otherwise a fractional
delay plus a frequency-dependent head shadow. The public corpora are single
microphone, so this is how the reference channel is made realistic.

Validation and test items are seeded by their index, so they are identical in
every run and every experiment.
"""
import hashlib
import json
import os

import numpy as np
import soundfile as sf
import torch
from torch.utils.data import Dataset

from . import augment as A
from .audio import read_segment, resample

SPLIT_ID = {"train": 0, "val": 1, "test": 2}

AUDIO_EXT = (".wav", ".flac", ".ogg")


# ----------------------------------------------------------------- index
def _split_for(rel, rule):
    """rule 'hash' = deterministic 90/5/5 by path; dict = substring -> split."""
    if isinstance(rule, dict):
        for split, keys in rule.items():
            if any(k in rel for k in keys):
                return split
        return None
    h = int(hashlib.md5(rel.encode()).hexdigest(), 16) % 100
    return "train" if h < 90 else ("val" if h < 95 else "test")


def build_index(cfg, out_path, log=print):
    """Walk every configured source once, record path/role/class/split/sr/frames."""
    rows, root = [], cfg.data.root
    for src in cfg.data.sources:
        p = src["path"]
        if p.startswith("@repo/"):                                # relative to the repository root
            base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), p[6:])
        else:
            base = p if os.path.isabs(p) else os.path.join(root, p)
        if not os.path.isdir(base):
            log(f"  [skip] {src['name']}: not found at {base}")
            continue
        excl = [e.lower() for e in src.get("exclude", [])]
        n = 0
        for dirpath, _, files in os.walk(base):
            for f in files:
                if not f.lower().endswith(AUDIO_EXT) or f.startswith("."):
                    continue
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, base).replace("\\", "/")
                if any(e in rel.lower() for e in excl):
                    continue
                split = _split_for(rel, src.get("split", "hash"))
                if split is None:
                    continue
                try:
                    info = sf.info(p)
                except Exception:
                    continue
                if info.frames < info.samplerate * 0.25:       # under 250 ms: useless
                    continue
                rows.append(dict(path=p, name=src["name"], role=src["role"],
                                 cls=src.get("cls", src["role"]), split=split,
                                 sr=info.samplerate, frames=info.frames,
                                 channels=info.channels))
                n += 1
        log(f"  {src['name']:<14} {n:>8,} files")
    with open(out_path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    log(f"  -> {out_path}  ({len(rows):,} files)")
    return rows


def load_index(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


# ----------------------------------------------------------------- dataset
class DualMicMix(Dataset):
    def __init__(self, cfg, index_rows, split, fixed=False, length=None):
        self.cfg, self.split, self.fixed = cfg, split, fixed
        self.sr = cfg.audio.sample_rate
        self.n = int(cfg.audio.segment_s * self.sr)
        self.mix = cfg.mix
        rows = [r for r in index_rows if r["split"] == split]
        self.speech = {}
        self.noise = {}
        self.rirs = []
        for r in rows:
            if r["role"] == "speech":
                self.speech.setdefault(r["name"], []).append(r)
            elif r["role"] == "noise":
                self.noise.setdefault(r["cls"], []).append(r)
            elif r["role"] == "rir":
                self.rirs.append(r)
        if not self.speech:
            raise RuntimeError(f"no speech files in split '{split}' — check the index")
        if not self.noise and self.mix.get("synthetic_burst_prob", 0) <= 0:
            raise RuntimeError(f"no noise files in split '{split}'")
        self.length = length or (cfg.train.items_per_epoch if split == "train" else cfg.data.get(f"{split}_items", 500))
        self.seed = cfg.run.seed

    def __len__(self):
        return self.length

    # -- helpers -------------------------------------------------------------
    def _rng(self, i):
        if self.fixed:
            return np.random.default_rng([self.seed, SPLIT_ID.get(self.split, 9), i])
        return np.random.default_rng()

    @staticmethod
    def _pick_weighted(groups, weights, rng):
        keys = [k for k in groups if weights.get(k, 0) > 0] or list(groups)
        w = np.array([weights.get(k, 1.0) for k in keys], dtype=float)
        k = keys[int(rng.choice(len(keys), p=w / w.sum()))]
        return groups[k][int(rng.integers(0, len(groups[k])))]

    def _noise_pair(self, rng):
        """One noise source as heard at Mic 1 and Mic 2."""
        m, n, sr = self.mix, self.n, self.sr
        use_synth = (not self.noise) or rng.random() < m.get("synthetic_burst_prob", 0.0)
        src = (A.structured_bursts(n, sr, rng, tuple(m.alpha)) if use_synth else
               read_segment(self._pick_weighted(self.noise, m.noise_class_weights, rng)["path"], sr, n, rng))
        if self.rirs and rng.random() < m.rir_prob:
            r = self._pick_weighted({"r": self.rirs}, {}, rng)
            rir, rsr = sf.read(r["path"], dtype="float32", always_2d=True)
            if rsr != sr:
                rir = np.stack([resample(rir[:, c], rsr, sr) for c in range(rir.shape[1])], axis=1)
            if rir.shape[1] >= 2:                               # two real microphones
                c = rng.choice(rir.shape[1], 2, replace=False)
                n1, n2 = A.apply_rir(src, rir[:, c[0]]), A.apply_rir(src, rir[:, c[1]])
                return n1, n2
            src = A.apply_rir(src, rir[:, 0])
        delay = rng.uniform(*m.mic2_delay_ms) * sr / 1000.0
        n2 = A.head_shadow(A.frac_delay(src, delay), sr, rng.uniform(*m.head_shadow_db))
        return src, n2

    # -- one item ------------------------------------------------------------
    def __getitem__(self, i):
        rng, m, sr = self._rng(i), self.mix, self.sr
        speech = read_segment(self._pick_weighted(self.speech, m.speech_weights, rng)["path"], sr, self.n, rng)
        speech -= speech.mean()

        k = int(rng.integers(m.n_noise_sources[0], m.n_noise_sources[1] + 1))
        n1 = np.zeros(self.n, np.float32); n2 = np.zeros(self.n, np.float32)
        for j in range(k):
            a, b = self._noise_pair(rng)
            g = 1.0 if j == 0 else A.db2lin(rng.uniform(-15, 0))
            n1 += g * a; n2 += g * b

        lo, hi = m.snr_db["low"], m.snr_db["high"]
        snr = rng.uniform(*lo) if rng.random() < m.snr_db["p_low"] else rng.uniform(*hi)
        g = A.mix_at_snr(speech, n1, snr)
        mic1 = speech + g * n1

        leak = A.db2lin(rng.uniform(*m.speech_leak_db))       # Widrow: keep this tiny
        sp2 = A.head_shadow(A.frac_delay(speech, rng.uniform(0.3, 0.7) * sr / 1000.0), sr, -10.0)
        mic2 = leak * sp2 + g * A.db2lin(rng.uniform(*m.mic2_gain_db)) * n2

        # overall level, then optional input clipping per channel (target untouched by clipping)
        peak = max(np.max(np.abs(mic1)), np.max(np.abs(mic2)), 1e-6)
        lvl = A.db2lin(rng.uniform(*m.level_dbfs)) / peak
        mic1, mic2, target = mic1 * lvl, mic2 * lvl, speech * lvl
        if rng.random() < m.clip_prob:
            mic1 = A.clip(mic1, rng.uniform(*m.clip_over_db), rng)
        if rng.random() < m.clip_prob:
            mic2 = A.clip(mic2, rng.uniform(*m.clip_over_db), rng)

        mics = np.stack([mic1, mic2])[: self.cfg.model.mics].astype(np.float32)
        return torch.from_numpy(mics), torch.from_numpy(target.astype(np.float32)), torch.tensor(snr, dtype=torch.float32)


class PairFolder(Dataset):
    """Prepared noisy/clean folders with matching filenames (e.g. VoiceBank-DEMAND).

    Single microphone. Used for the sanity check: reproduce GTCRN's published
    numbers before trusting anything trained on our own mixtures.
    """

    def __init__(self, noisy_dir, clean_dir, sr, segment_s=None):
        self.noisy_dir, self.clean_dir, self.sr = noisy_dir, clean_dir, sr
        self.files = sorted(f for f in os.listdir(clean_dir) if f.lower().endswith(AUDIO_EXT))
        self.n = int(segment_s * sr) if segment_s else None

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        f = self.files[i]
        x, sx = sf.read(os.path.join(self.noisy_dir, f), dtype="float32")
        y, sy = sf.read(os.path.join(self.clean_dir, f), dtype="float32")
        x, y = resample(x, sx, self.sr), resample(y, sy, self.sr)
        L = min(len(x), len(y))
        x, y = x[:L], y[:L]
        if self.n:
            if L < self.n:
                x, y = np.pad(x, (0, self.n - L)), np.pad(y, (0, self.n - L))
            else:
                s = np.random.randint(0, L - self.n + 1)
                x, y = x[s:s + self.n], y[s:s + self.n]
        snr = 10 * np.log10(A.power(y) / A.power(x - y))
        return torch.from_numpy(x[None]), torch.from_numpy(y), torch.tensor(snr, dtype=torch.float32)
