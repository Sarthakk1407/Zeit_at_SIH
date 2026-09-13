"""Losses. The PS asks for SI-SNR, L1/L2 and a perceptual term — all three are here.

    total = w_complex·(complex compressed spectrum, L2)      GTCRN's hybrid loss
          + w_mag    ·(compressed magnitude, L2)
          + w_sisnr  ·(−SI-SNR, in bels)
          + w_mrstft ·(multi-resolution STFT: spectral convergence + L1 log-mag)

The magnitude compression (|X|^0.3) is the perceptual part: it weights quiet
spectral detail closer to how the ear does, instead of letting loud bins
dominate. Squared error is dominated by outliers under heavy-tailed noise
(workflow.md cross-finding C), which is why the L1 multi-resolution term is on
by default.
"""
import torch
import torch.nn.functional as F

from .audio import istft


def si_snr(est, ref, eps=1e-8):
    """Scale-invariant SNR in dB, per item. est/ref (B, N)."""
    est = est - est.mean(dim=-1, keepdim=True)
    ref = ref - ref.mean(dim=-1, keepdim=True)
    proj = (est * ref).sum(-1, keepdim=True) * ref / (ref.pow(2).sum(-1, keepdim=True) + eps)
    noise = est - proj
    return 10 * torch.log10(proj.pow(2).sum(-1) / (noise.pow(2).sum(-1) + eps) + eps)


def _mrstft(est, ref, cfgs=((1024, 256), (512, 128), (256, 64))):
    loss = 0.0
    for n_fft, hop in cfgs:
        w = torch.hann_window(n_fft, device=est.device, dtype=est.dtype)
        E = torch.stft(est, n_fft, hop, window=w, return_complex=True).abs() + 1e-7
        R = torch.stft(ref, n_fft, hop, window=w, return_complex=True).abs() + 1e-7
        sc = torch.linalg.norm(R - E, dim=(-2, -1)) / (torch.linalg.norm(R, dim=(-2, -1)) + 1e-7)
        loss = loss + sc.mean() + F.l1_loss(torch.log(E), torch.log(R))
    return loss / len(cfgs)


class HybridLoss(torch.nn.Module):
    def __init__(self, w_complex=30.0, w_mag=70.0, w_sisnr=1.0, w_mrstft=1.0, compress=0.3):
        super().__init__()
        self.w = dict(complex=w_complex, mag=w_mag, sisnr=w_sisnr, mrstft=w_mrstft)
        self.c = compress

    def forward(self, est_spec, ref_spec, length):
        """est/ref spec (B, F, T, 2). Returns (total, dict of parts)."""
        er, ei = est_spec[..., 0], est_spec[..., 1]
        rr, ri = ref_spec[..., 0], ref_spec[..., 1]
        em = torch.sqrt(er ** 2 + ei ** 2 + 1e-12)
        rm = torch.sqrt(rr ** 2 + ri ** 2 + 1e-12)
        ec, rc = em ** (self.c - 1), rm ** (self.c - 1)
        l_complex = F.mse_loss(er * ec, rr * rc) + F.mse_loss(ei * ec, ri * rc)
        l_mag = F.mse_loss(em ** self.c, rm ** self.c)

        est = istft(est_spec, length)
        ref = istft(ref_spec, length)
        l_sisnr = -si_snr(est, ref).mean() / 10.0
        parts = dict(complex=l_complex, mag=l_mag, sisnr=l_sisnr)
        if self.w["mrstft"] > 0:
            parts["mrstft"] = _mrstft(est, ref)
        total = sum(self.w[k] * v for k, v in parts.items())
        return total, {k: float(v.detach()) for k, v in parts.items()}
