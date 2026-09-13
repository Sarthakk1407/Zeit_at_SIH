"""GTCRN, dual-microphone form — block [7], the only trained block in Lane B.

Re-implemented from Rong et al., "GTCRN: A Speech Enhancement Model Requiring
Ultralow Computational Resources", ICASSP 2024, extended to take the Mic 2
reference as extra input channels (the H-GTCRN idea). Printed parameter count
is the one to quote for THIS model; the paper's 23.7 K / official 48.2 K are
for single-channel GTCRN.

Two ways to run the same weights:

    model(spec)                              whole clips, for training
    model.stream(frame, conv, tra, inter)    one 16 ms frame + carried state,
                                             for ONNX / TensorRT on the Jetson

Every time-direction operation is causal, so both give the same output.
`selftest.py` checks that to 1e-4.

Shapes: spec is (B, M, F=257, T, 2) — M microphones, real/imag last.
Output is Mic 1's enhanced spectrum, (B, F, T, 2).
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

LOW_BINS = 65          # bins kept as-is (speech harmonics live here)
ERB_BANDS = 64         # the 192 high bins are merged into these
WIDTH = 33             # frequency axis after the two stride-2 convs
HID = 16               # channel width through the network
DILATIONS = (1, 2, 5)  # GTConvBlock time dilations, encoder order
MAX_CACHE = 2 * max(DILATIONS)


# ----------------------------------------------------------------- ERB bands
def erb_matrix(n_fft=512, fs=16000, low=LOW_BINS, bands=ERB_BANDS):
    """(bands, n_bins-low) triangular ERB filters over the high bins."""
    hz2erb = lambda f: 21.4 * np.log10(0.00437 * f + 1.0)
    erb2hz = lambda e: (10 ** (e / 21.4) - 1.0) / 0.00437
    n_bins = n_fft // 2 + 1
    e = np.linspace(hz2erb(low * fs / n_fft), hz2erb(fs / 2), bands)
    centres = erb2hz(e) * n_fft / fs                        # fractional bin index
    k = np.arange(n_bins, dtype=np.float64)
    W = np.zeros((bands, n_bins))
    for i, c in enumerate(centres):
        left = c - (centres[i - 1] if i > 0 else c - (centres[1] - centres[0]))
        right = (centres[i + 1] if i < bands - 1 else c + (c - centres[i - 1])) - c
        W[i] = np.where(k <= c, 1 - (c - k) / max(left, 1.0), 1 - (k - c) / max(right, 1.0))
    W = np.clip(W, 0, None)[:, low:]
    W /= W.sum(axis=1, keepdims=True) + 1e-12               # each band is a weighted mean
    return torch.tensor(W, dtype=torch.float32)


class ERB(nn.Module):
    def __init__(self):
        super().__init__()
        W = erb_matrix()
        self.register_buffer("fwd", W)                       # 192 -> 64
        inv = W.t() / (W.t().sum(dim=1, keepdim=True) + 1e-12)
        self.register_buffer("inv", inv)                     # 64 -> 192

    def merge(self, x):                                      # (..., 257) -> (..., 129)
        return torch.cat([x[..., :LOW_BINS], x[..., LOW_BINS:] @ self.fwd.t()], dim=-1)

    def split(self, x):                                      # (..., 129) -> (..., 257)
        return torch.cat([x[..., :LOW_BINS], x[..., LOW_BINS:] @ self.inv.t()], dim=-1)


# ----------------------------------------------------------------- building blocks
def sfe(x):
    """Subband feature extraction: each bin with its two neighbours, as channels."""
    p = F.pad(x, (1, 1))
    return torch.cat([p[..., :-2], p[..., 1:-1], p[..., 2:]], dim=1)


def shuffle(a, b):
    B, C, T, Fq = a.shape
    return torch.stack([a, b], dim=2).reshape(B, 2 * C, T, Fq)


class ConvBlock(nn.Module):
    def __init__(self, cin, cout, groups=1, deconv=False, last=False):
        super().__init__()
        conv = nn.ConvTranspose2d if deconv else nn.Conv2d
        self.conv = conv(cin, cout, (1, 5), stride=(1, 2), padding=(0, 2), groups=groups)
        self.bn = nn.BatchNorm2d(cout)
        self.act = nn.Tanh() if last else nn.PReLU()

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))


class TRA(nn.Module):
    """Temporal recurrent attention: per-frame energy through a GRU gates the frame."""

    def __init__(self, c):
        super().__init__()
        self.gru = nn.GRU(c, 2 * c, batch_first=True)
        self.fc = nn.Linear(2 * c, c)

    def forward(self, x, h=None):                            # x (B,C,T,F), h (1,B,2C)
        z = x.pow(2).mean(dim=-1).transpose(1, 2)            # (B,T,C)
        y, h = self.gru(z, h)
        a = torch.sigmoid(self.fc(y)).transpose(1, 2).unsqueeze(-1)
        return x * a, h


class GTConvBlock(nn.Module):
    """Grouped temporal conv: half the channels processed, half passed, then shuffled."""

    def __init__(self, dilation):
        super().__init__()
        c = HID // 2
        self.d = dilation
        self.pc1 = nn.Sequential(nn.Conv2d(3 * c, HID, 1), nn.BatchNorm2d(HID), nn.PReLU())
        self.dconv = nn.Conv2d(HID, HID, (3, 3), padding=(0, 1), dilation=(dilation, 1), groups=HID)
        self.dbn = nn.Sequential(nn.BatchNorm2d(HID), nn.PReLU())
        self.pc2 = nn.Sequential(nn.Conv2d(HID, c, 1), nn.BatchNorm2d(c))
        self.tra = TRA(c)

    def forward(self, x, cache=None, h=None):
        """cache: (B, HID, 2d, F) past frames, or None for zero history."""
        x1, x2 = torch.chunk(x, 2, dim=1)
        y = self.pc1(sfe(x1))
        if cache is None:
            y = F.pad(y, (0, 0, 2 * self.d, 0))
        else:
            y = torch.cat([cache, y], dim=2)
        new_cache = y[:, :, -2 * self.d:]
        y = self.dbn(self.dconv(y))
        y, h = self.tra(self.pc2(y), h)
        return shuffle(y, x2), new_cache, h


class GRNN(nn.Module):
    """Grouped GRU: two half-size GRUs instead of one — half the parameters."""

    def __init__(self, cin, hidden, bidirectional):
        super().__init__()
        self.g1 = nn.GRU(cin // 2, hidden // 2, batch_first=True, bidirectional=bidirectional)
        self.g2 = nn.GRU(cin // 2, hidden // 2, batch_first=True, bidirectional=bidirectional)

    def forward(self, x, h1=None, h2=None):
        a, b = torch.chunk(x, 2, dim=-1)
        ya, h1 = self.g1(a, h1)
        yb, h2 = self.g2(b, h2)
        return torch.cat([ya, yb], dim=-1), h1, h2


class DPGRNN(nn.Module):
    """Dual-path grouped RNN: across frequency (bidirectional, no state) then across time (causal)."""

    def __init__(self):
        super().__init__()
        self.intra = GRNN(HID, HID // 2, bidirectional=True)
        self.intra_fc = nn.Linear(HID, HID)
        self.intra_ln = nn.LayerNorm((WIDTH, HID))
        self.inter = GRNN(HID, HID, bidirectional=False)
        self.inter_fc = nn.Linear(HID, HID)
        self.inter_ln = nn.LayerNorm((WIDTH, HID))

    def forward(self, x, h1=None, h2=None):                  # x (B,C,T,F); h (1, B*F, HID/2)
        B, C, T, Fq = x.shape
        x = x.permute(0, 2, 3, 1)                            # (B,T,F,C)
        y, _, _ = self.intra(x.reshape(B * T, Fq, C))
        x = x + self.intra_ln(self.intra_fc(y).reshape(B, T, Fq, C))
        z = x.transpose(1, 2).reshape(B * Fq, T, C)
        z, h1, h2 = self.inter(z, h1, h2)
        z = self.inter_fc(z).reshape(B, Fq, T, C).transpose(1, 2)
        x = x + self.inter_ln(z)
        return x.permute(0, 3, 1, 2), h1, h2


# ----------------------------------------------------------------- the model
class GTCRN(nn.Module):
    N_GT = 2 * len(DILATIONS)                                # 6 GTConvBlocks carry state

    def __init__(self, mics=2):
        super().__init__()
        self.mics = mics
        self.erb = ERB()
        cin = 9 * mics                                       # (mag, real, imag) x 3 neighbours x mics
        self.enc_conv = nn.ModuleList([ConvBlock(cin, HID), ConvBlock(HID, HID, groups=2)])
        self.enc_gt = nn.ModuleList([GTConvBlock(d) for d in DILATIONS])
        self.dp = nn.ModuleList([DPGRNN(), DPGRNN()])
        self.dec_gt = nn.ModuleList([GTConvBlock(d) for d in reversed(DILATIONS)])
        self.dec_conv = nn.ModuleList([ConvBlock(HID, HID, groups=2, deconv=True),
                                       ConvBlock(HID, 2, deconv=True, last=True)])

    # -- shared core ------------------------------------------------------
    def _core(self, spec, conv, tra, inter):
        """spec (B,M,F,T,2). conv/tra/inter are state lists (None entries = zero history)."""
        B, M, Fq, T, _ = spec.shape
        re, im = spec[..., 0], spec[..., 1]                  # (B,M,F,T)
        mag = torch.sqrt(re ** 2 + im ** 2 + 1e-12)
        feat = torch.stack([mag, re, im], dim=2)             # (B,M,3,F,T)
        feat = feat.reshape(B, 3 * M, Fq, T).transpose(2, 3) # (B,3M,T,F)
        feat = sfe(self.erb.merge(feat))                     # (B,9M,T,129)

        skips = []
        x = feat
        for blk in self.enc_conv:
            x = blk(x); skips.append(x)
        new_conv, new_tra, new_inter = [], [], []
        for i, blk in enumerate(self.enc_gt):
            x, c, h = blk(x, conv[i], tra[i]); skips.append(x)
            new_conv.append(c); new_tra.append(h)
        for i, blk in enumerate(self.dp):
            x, h1, h2 = blk(x, inter[2 * i], inter[2 * i + 1])
            new_inter += [h1, h2]
        for i, blk in enumerate(self.dec_gt):
            x, c, h = blk(x + skips[4 - i], conv[3 + i], tra[3 + i])
            new_conv.append(c); new_tra.append(h)
        x = self.dec_conv[0](x + skips[1])
        m = self.dec_conv[1](x + skips[0])                   # (B,2,T,129) in [-1,1]
        m = self.erb.split(m).transpose(2, 3)                # (B,2,F,T)

        r1, i1 = re[:, 0], im[:, 0]                          # mask Mic 1, the noisy input
        out = torch.stack([r1 * m[:, 0] - i1 * m[:, 1],
                           i1 * m[:, 0] + r1 * m[:, 1]], dim=-1)
        return out, new_conv, new_tra, new_inter

    # -- training / offline --------------------------------------------------
    def forward(self, spec):
        n = self.N_GT
        out, *_ = self._core(spec, [None] * n, [None] * n, [None] * 4)
        return out

    # -- streaming -----------------------------------------------------------
    def init_state(self, batch=1, device=None):
        conv = torch.zeros(batch, self.N_GT, HID, MAX_CACHE, WIDTH, device=device)
        tra = torch.zeros(self.N_GT, batch, HID)
        inter = torch.zeros(4, batch * WIDTH, HID // 2)
        return conv, tra.to(device), inter.to(device)

    def stream(self, frame, conv_cache, tra_cache, inter_cache):
        """One frame. frame (B,M,257,1,2); states as returned by init_state()."""
        dil = list(DILATIONS) + list(reversed(DILATIONS))
        conv = [conv_cache[:, i, :, MAX_CACHE - 2 * d:] for i, d in enumerate(dil)]
        tra = [tra_cache[i:i + 1] for i in range(self.N_GT)]
        inter = [inter_cache[i:i + 1] for i in range(4)]
        out, nc, nt, ni = self._core(frame, conv, tra, inter)
        B = frame.shape[0]
        new_conv = torch.stack(
            [F.pad(c, (0, 0, MAX_CACHE - c.shape[2], 0)) for c in nc], dim=1)
        new_tra = torch.cat(nt, dim=0)
        new_inter = torch.cat(ni, dim=0)
        return out, new_conv, new_tra, new_inter


def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
