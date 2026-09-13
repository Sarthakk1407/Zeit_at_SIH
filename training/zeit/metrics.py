"""Evaluation metrics — the PS targets, plus the ones that keep them honest.

PS targets: SNR > 15 dB, STOI > 0.85, PESQ > 2.5.

"SNR > 15 dB" is ambiguous, so both readings are reported:
  snr_out   the output SNR, 10·log10(|s|² / |s − ŝ|²)
  snr_delta the improvement, snr_out − snr_in
Every metric is reported per input-SNR bucket (a curve), never as one number.
"""
import numpy as np


def snr(est, ref):
    ref = ref.astype(np.float64); est = est.astype(np.float64)
    return float(10 * np.log10(np.sum(ref ** 2) / (np.sum((ref - est) ** 2) + 1e-12) + 1e-12))


def si_snr(est, ref):
    ref = ref - ref.mean(); est = est - est.mean()
    s = np.dot(est, ref) * ref / (np.dot(ref, ref) + 1e-12)
    return float(10 * np.log10(np.dot(s, s) / (np.dot(est - s, est - s) + 1e-12) + 1e-12))


def pesq_wb(est, ref, sr=16000):
    try:
        from pesq import pesq
        return float(pesq(sr, ref, est, "wb"))
    except Exception:
        return float("nan")                # silent clips, or pesq not installed


def stoi(est, ref, sr=16000):
    try:
        from pystoi import stoi as _stoi
        return float(_stoi(ref, est, sr, extended=False))
    except Exception:
        return float("nan")


def all_metrics(est, ref, noisy, sr=16000, slow=True):
    m = dict(snr_in=snr(noisy, ref), snr_out=snr(est, ref),
             si_snr_in=si_snr(noisy, ref), si_snr_out=si_snr(est, ref))
    m["snr_delta"] = m["snr_out"] - m["snr_in"]
    if slow:
        m.update(pesq=pesq_wb(est, ref, sr), stoi=stoi(est, ref, sr),
                 pesq_in=pesq_wb(noisy, ref, sr), stoi_in=stoi(noisy, ref, sr))
    return m


def bucket(rows, key="snr_in", edges=(-15, -10, -5, 0, 5, 10, 15, 20)):
    """Mean of every metric per input-SNR bucket -> the curves the report shows."""
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = [r for r in rows if lo <= r[key] < hi]
        if not sel:
            continue
        agg = {"bucket": f"[{lo},{hi})", "n": len(sel)}
        for k in sel[0]:
            if isinstance(sel[0][k], (int, float)):
                v = np.array([r[k] for r in sel], dtype=float)
                agg[k] = float(np.nanmean(v)) if np.isfinite(v).any() else float("nan")
        out.append(agg)
    return out
