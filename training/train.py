#!/usr/bin/env python3
"""train.py -- train GTCRN on freshly mixed dual-microphone data.

    python train.py configs/base.yaml
    python train.py configs/base.yaml train.batch_size=16 train.num_workers=4
    python train.py configs/base.yaml --resume runs/gtcrn_dualmic-1a2b3c4d/last.pt
    python train.py configs/base.yaml --init runs/.../pruned.pt      # fine-tune after pruning

Writes runs/<name>-<confighash>/ with best.pt (by validation SI-SNR), last.pt,
config.yaml, history.json and TensorBoard logs.
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import torch                                                   # noqa: E402
import yaml                                                    # noqa: E402
from torch.utils.data import DataLoader                        # noqa: E402

from zeit import config, metrics                               # noqa: E402
from zeit.audio import istft, stft                             # noqa: E402
from zeit.data import DualMicMix, PairFolder, load_index       # noqa: E402
from zeit.losses import HybridLoss, si_snr                     # noqa: E402
from zeit.model import GTCRN, count_params                     # noqa: E402


def pick_device(name):
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def make_datasets(cfg):
    if "pairs" in cfg:
        p = cfg.pairs
        tr = PairFolder(p.train_noisy, p.train_clean, cfg.audio.sample_rate, cfg.audio.segment_s)
        va = PairFolder(p.test_noisy, p.test_clean, cfg.audio.sample_rate, cfg.audio.segment_s)
        return tr, va
    idx_path = cfg.data.index if os.path.isabs(cfg.data.index) else os.path.join(HERE, cfg.data.index)
    if not os.path.exists(idx_path):
        sys.exit(f"no index at {idx_path} -- run build_index.py first")
    rows = load_index(idx_path)
    tr = DualMicMix(cfg, rows, "train")
    va = DualMicMix(cfg, rows, "val", fixed=True, length=cfg.data.val_items)
    return tr, va


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("overrides", nargs="*")
    ap.add_argument("--resume")
    ap.add_argument("--init", help="start from these weights (fresh optimiser)")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--max-steps", type=int, default=0, help="stop early (smoke tests)")
    a = ap.parse_args()

    cfg = config.load(a.config, a.overrides)
    h = config.config_hash(cfg)
    out = os.path.join(HERE, cfg.run.out_dir, f"{cfg.run.name}-{h}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "config.yaml"), "w") as f:
        yaml.safe_dump(dict(cfg), f, sort_keys=False)

    torch.manual_seed(cfg.run.seed); np.random.seed(cfg.run.seed)
    dev = pick_device(a.device)
    T = cfg.train
    amp = bool(T.amp) and dev.type == "cuda"

    tr_ds, va_ds = make_datasets(cfg)
    tr = DataLoader(tr_ds, T.batch_size, shuffle="pairs" in cfg, num_workers=T.num_workers,
                    drop_last=True, pin_memory=dev.type == "cuda",
                    persistent_workers=T.num_workers > 0)
    va = DataLoader(va_ds, T.batch_size, shuffle=False, num_workers=T.num_workers)

    model = GTCRN(mics=cfg.model.mics).to(dev)
    n_params = count_params(model)
    print(f"\n  run      {out}\n  device   {dev}   amp={amp}\n  params   {n_params:,}\n"
          f"  train    {len(tr_ds):,} items/epoch   val {len(va_ds):,}\n")

    opt = torch.optim.AdamW(model.parameters(), lr=T.lr, weight_decay=T.weight_decay)
    steps_per_epoch = len(tr)
    total = T.epochs * steps_per_epoch
    warm = T.warmup_epochs * steps_per_epoch
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / max(warm, 1) if s < warm
        else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(total - warm, 1))))
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    loss_fn = HybridLoss(cfg.loss.w_complex, cfg.loss.w_mag,
                         cfg.loss.w_sisnr, cfg.loss.w_mrstft)

    start, best, stale, history = 0, -1e9, 0, []
    if a.resume:
        ck = torch.load(a.resume, map_location=dev)
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"])
        sched.load_state_dict(ck["sched"]); start = ck["epoch"] + 1
        best, history = ck.get("best", best), ck.get("history", [])
    elif a.init:
        model.load_state_dict(torch.load(a.init, map_location=dev)["model"])

    try:
        from torch.utils.tensorboard import SummaryWriter
        tb = SummaryWriter(os.path.join(out, "tb"))
    except Exception:
        tb = None

    step = start * steps_per_epoch
    for epoch in range(start, T.epochs):
        model.train()
        t0, run_loss = time.time(), 0.0
        for i, (mics, clean, _) in enumerate(tr):
            mics, clean = mics.to(dev, non_blocking=True), clean.to(dev, non_blocking=True)
            N = clean.shape[-1]
            with torch.no_grad():
                X, Y = stft(mics), stft(clean)                 # STFT stays float32
            with torch.autocast("cuda", dtype=torch.float16, enabled=amp):
                est = model(X)
            loss, parts = loss_fn(est.float(), Y, N)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            gn = torch.nn.utils.clip_grad_norm_(model.parameters(), T.grad_clip)
            scaler.step(opt); scaler.update(); sched.step()
            run_loss += float(loss); step += 1
            if tb and step % 50 == 0:
                tb.add_scalar("train/loss", float(loss), step)
                tb.add_scalar("train/grad_norm", float(gn), step)
                for k, v in parts.items():
                    tb.add_scalar(f"train/{k}", v, step)
            if i % 100 == 0:
                print(f"  ep {epoch:3d}  it {i:5d}/{steps_per_epoch}  loss {float(loss):8.4f}  "
                      f"lr {sched.get_last_lr()[0]:.2e}", flush=True)
            if a.max_steps and step >= a.max_steps:
                break

        # ---- validation: SI-SNR every epoch, PESQ/STOI every few ----------
        model.eval()
        slow = (epoch % T.eval_pesq_every == 0) or epoch == T.epochs - 1
        vals, rows = [], []
        with torch.no_grad():
            for j, (mics, clean, _) in enumerate(va):
                mics, clean = mics.to(dev), clean.to(dev)
                N = clean.shape[-1]
                est = istft(model(stft(mics)).float(), N)
                vals.append(si_snr(est, clean).cpu())
                if slow and len(rows) < 200:
                    e, c, n = est.cpu().numpy(), clean.cpu().numpy(), mics[:, 0].cpu().numpy()
                    rows += [metrics.all_metrics(e[k], c[k], n[k]) for k in range(len(e))]
                if a.max_steps and j >= 1:
                    break
        v_sisnr = float(torch.cat(vals).mean())
        rec = dict(epoch=epoch, train_loss=run_loss / max(i + 1, 1), val_si_snr=v_sisnr,
                   minutes=(time.time() - t0) / 60)
        if rows:
            for k in ("pesq", "stoi", "snr_out", "snr_delta"):
                rec[f"val_{k}"] = float(np.nanmean([r[k] for r in rows]))
        history.append(rec)
        print("  " + "  ".join(f"{k} {v:.3f}" if isinstance(v, float) else f"{k} {v}" for k, v in rec.items()))
        if tb:
            for k, v in rec.items():
                if k.startswith("val_"):
                    tb.add_scalar(f"val/{k[4:]}", v, epoch)

        ck = dict(model=model.state_dict(), opt=opt.state_dict(), sched=sched.state_dict(),
                  epoch=epoch, best=max(best, v_sisnr), history=history, cfg=dict(cfg),
                  cfg_hash=h, params=n_params)
        torch.save(ck, os.path.join(out, "last.pt"))
        if v_sisnr > best:
            best, stale = v_sisnr, 0
            torch.save(ck, os.path.join(out, "best.pt"))
            print(f"  ** new best val SI-SNR {best:.2f} dB -> best.pt")
        else:
            stale += 1
        with open(os.path.join(out, "history.json"), "w") as f:
            json.dump(history, f, indent=1)
        if stale >= T.early_stop_patience or (a.max_steps and step >= a.max_steps):
            break

    print(f"\n  done. best val SI-SNR {best:.2f} dB   ->  {out}/best.pt\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
