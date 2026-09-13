#!/usr/bin/env python3
"""prune.py -- magnitude pruning, then fine-tune with train.py --init.

    python prune.py runs/.../best.pt --amount 0.3
    python train.py configs/base.yaml train.epochs=30 train.lr=2e-4 --init runs/.../pruned_30.pt

Removes the smallest-magnitude weights across every conv, linear and GRU
layer (globally, so layers that matter keep more), makes the zeros permanent,
and saves a checkpoint. Always fine-tune afterwards, then re-run evaluate.py
and compare against the unpruned model at the same input SNRs.

Honest limit: this is unstructured pruning. The zeros shrink the compressed
model and are the input to the α-stable vs Gaussian prune-ability study, but
TensorRT still multiplies them, so they do not by themselves cut latency.
Structured (whole-channel) pruning is the step that does, and is the next one
to add here.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import torch                                                   # noqa: E402
import torch.nn.utils.prune as P                               # noqa: E402

from zeit.config import Cfg                                    # noqa: E402
from zeit.model import GTCRN                                   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("--amount", type=float, default=0.3)
    a = ap.parse_args()

    ck = torch.load(a.checkpoint, map_location="cpu")
    model = GTCRN(mics=Cfg(ck["cfg"]).model.mics)
    model.load_state_dict(ck["model"])

    params = []
    for mod in model.modules():
        if isinstance(mod, (torch.nn.Conv2d, torch.nn.ConvTranspose2d, torch.nn.Linear)):
            params.append((mod, "weight"))
        elif isinstance(mod, torch.nn.GRU):
            params += [(mod, n) for n, _ in mod.named_parameters() if "weight" in n]
    P.global_unstructured(params, pruning_method=P.L1Unstructured, amount=a.amount)
    for mod, name in params:
        P.remove(mod, name)

    total = sum(p.numel() for m, n in params for p in [getattr(m, n)])
    zeros = sum(int((getattr(m, n) == 0).sum()) for m, n in params)
    out = os.path.join(os.path.dirname(a.checkpoint), f"pruned_{int(a.amount * 100)}.pt")
    torch.save(dict(ck, model=model.state_dict()), out)
    print(f"  pruned {zeros:,} of {total:,} weights ({zeros / total:.1%})  ->  {out}")
    print("  next: fine-tune with train.py --init, then evaluate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
