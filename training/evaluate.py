#!/usr/bin/env python3
"""evaluate.py -- score a checkpoint on the fixed test set, as curves against input SNR.

    python evaluate.py runs/gtcrn_dualmic-1a2b3c4d/best.pt
    python evaluate.py runs/.../best.pt --items 500 --out report/

Writes per_item.csv, by_snr.csv and summary.json. Every PS target is reported
per input-SNR bucket with the crossing point stated — never as one number.
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import torch                                                   # noqa: E402
from torch.utils.data import DataLoader                        # noqa: E402

from zeit import metrics                                       # noqa: E402
from zeit.audio import istft, stft                             # noqa: E402
from zeit.config import Cfg                                    # noqa: E402
from zeit.data import DualMicMix, PairFolder, load_index       # noqa: E402
from zeit.model import GTCRN                                   # noqa: E402

TARGETS = dict(snr_out=15.0, stoi=0.85, pesq=2.5)


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0])
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("--items", type=int, default=0, help="default: data.test_items")
    ap.add_argument("--out")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()

    ck = torch.load(a.checkpoint, map_location="cpu")
    cfg = Cfg(ck["cfg"])
    model = GTCRN(mics=cfg.model.mics)
    model.load_state_dict(ck["model"]); model.eval().to(a.device)

    if "pairs" in cfg:
        ds = PairFolder(cfg.pairs.test_noisy, cfg.pairs.test_clean, cfg.audio.sample_rate)
        bs = 1                                               # full-length files differ in length
    else:
        idx = cfg.data.index if os.path.isabs(cfg.data.index) else os.path.join(HERE, cfg.data.index)
        ds = DualMicMix(cfg, load_index(idx), "test", fixed=True,
                        length=a.items or cfg.data.get("test_items", 2000))
        bs = 16
    dl = DataLoader(ds, bs, shuffle=False, num_workers=min(8, os.cpu_count() or 1))

    rows = []
    with torch.no_grad():
        for mics, clean, _ in dl:
            N = clean.shape[-1]
            est = istft(model(stft(mics.to(a.device))).float(), N).cpu().numpy()
            c, n = clean.numpy(), mics[:, 0].numpy()
            for k in range(len(est)):
                rows.append(metrics.all_metrics(est[k], c[k], n[k], cfg.audio.sample_rate))
            if a.items and len(rows) >= a.items:
                break
            print(f"\r  {len(rows)} items", end="", flush=True)
    print()

    curves = metrics.bucket(rows)
    summary = {k: float(np.nanmean([r[k] for r in rows])) for k in rows[0]}
    crossing = {}
    for k, t in TARGETS.items():
        ok = [c_["bucket"] for c_ in curves if c_.get(k, float("nan")) >= t]
        crossing[k] = ok[0] if ok else "never"
    out = a.out or os.path.join(os.path.dirname(a.checkpoint), "eval")
    os.makedirs(out, exist_ok=True)
    write_csv(os.path.join(out, "per_item.csv"), rows)
    write_csv(os.path.join(out, "by_snr.csv"), curves)
    json.dump(dict(checkpoint=a.checkpoint, cfg_hash=ck.get("cfg_hash"), params=ck.get("params"),
                   n=len(rows), mean=summary, target_first_met_in_bucket=crossing),
              open(os.path.join(out, "summary.json"), "w"), indent=2)

    print(f"\n  {'input SNR':<11}{'n':>5}{'SNR out':>9}{'dSNR':>7}{'SI-SNR':>8}{'PESQ':>6}{'STOI':>6}")
    for c_ in curves:
        print(f"  {c_['bucket']:<11}{c_['n']:>5}{c_['snr_out']:>9.2f}{c_['snr_delta']:>7.2f}"
              f"{c_['si_snr_out']:>8.2f}{c_.get('pesq', float('nan')):>6.2f}{c_.get('stoi', float('nan')):>6.2f}")
    print(f"\n  PS targets first met at input SNR: {crossing}\n  -> {out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
