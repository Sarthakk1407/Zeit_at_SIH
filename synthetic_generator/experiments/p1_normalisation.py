#!/usr/bin/env python3
"""p1_normalisation.py -- why RMS is invalid for impulsive noise, measured.

    python3 p1_normalisation.py
    python3 p1_normalisation.py --events "data for training/REFERENCE_REAL/events_impulse"

The claim: RMS is a second moment, sqrt(E[x^2]). For alpha-stable noise with
alpha < 2 the second moment is INFINITE, so the estimate never settles -- give it
a longer window and the answer changes. Normalising by it scales every training
example by a number that does not converge.

This script measures that instead of asserting it. Three estimators, four alpha
values, growing window lengths. The one that wanders is RMS.

Outputs a table, a JSON, and a PNG.
"""
import argparse, json, os, sys
import numpy as np

RNG = np.random.default_rng(0)

def alpha_stable(alpha, n, rng=RNG):
    """Symmetric alpha-stable via Chambers-Mallows-Stuck."""
    U = rng.uniform(-np.pi/2, np.pi/2, n)
    W = rng.exponential(1.0, n)
    if abs(alpha - 1.0) < 1e-9:
        return np.tan(U)
    return (np.sin(alpha*U) / np.cos(U)**(1/alpha)
            * (np.cos(U - alpha*U) / W)**((1-alpha)/alpha))

def rms(x):    return float(np.sqrt(np.mean(x**2)))
def p90(x):    return float(np.percentile(np.abs(x), 90))
def flom(x, p): return float(np.mean(np.abs(x)**p)**(1/p))

# FLOM converges only when p < alpha. Two values so the rule is visible:
# p=0.5 is valid for alpha>0.5, p=0.2 is valid for every alpha we test.
EST = {"RMS":         rms,
       "P90":         p90,
       "FLOM p=0.5":  lambda x: flom(x, 0.5),
       "FLOM p=0.2":  lambda x: flom(x, 0.2)}

def instability(alpha, lengths, trials=12):
    """Spread of each estimator across independent draws, per window length.

    A converging estimator settles: its spread shrinks as N grows.
    A non-converging one does not.
    """
    out = {k: [] for k in EST}
    for N in lengths:
        vals = {k: [] for k in EST}
        for _ in range(trials):
            x = alpha_stable(alpha, N)          # raw draw -- do NOT pre-normalise,
            for k, f in EST.items():            # that would rig the comparison
                vals[k].append(f(x))
        for k in EST:
            v = np.array(vals[k])
            out[k].append(float(np.std(v) / (np.abs(np.mean(v)) + 1e-12)))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--events', help='directory of real event WAVs to also test')
    ap.add_argument('--out', default='synthetic_generator/experiments')
    a = ap.parse_args()

    lengths = [1_000, 10_000, 100_000, 1_000_000]
    alphas  = [2.0, 1.5, 1.0, 0.5]
    res = {}

    print("\nRELATIVE SPREAD of each estimator across 12 independent draws.")
    print("Lower = settles down. If it does not fall as N grows, it does not converge.\n")
    for al in alphas:
        r = instability(al, lengths)
        res[f"alpha={al}"] = {"lengths": lengths, **r}
        tag = {2.0:"Gaussian", 1.5:"", 1.0:"Cauchy", 0.5:"very heavy"}[al]
        print(f"  alpha = {al}  {tag}")
        print(f"    {'N':>10} " + "".join(f"{k:>16}" for k in EST))
        for i, N in enumerate(lengths):
            print(f"    {N:>10,} " + "".join(f"{r[k][i]:>16.4f}" for k in EST))
        print()

    # verdict
    print("  VERDICT")
    for al in alphas:
        r = res[f"alpha={al}"]
        for k in EST:
            first, last = r[k][0], r[k][-1]
            shrink = last / (first + 1e-12)
            if al == 2.0: continue
            if shrink > 0.5:
                ok = "" if k == "RMS" else "   (p < alpha violated)" if "FLOM" in k and float(k[-3:]) >= al else ""
                print(f"    alpha={al:<4} {k:<12} spread only fell to {shrink:5.2f}x "
                      f"over a 1000x longer window -- NOT settling{ok}")
    print()

    # real events -- the right test is WITHIN one event: grow the window and
    # see whether the estimate settles. Comparing across different events would
    # only measure that different gunshots really are different.
    if a.events and os.path.isdir(a.events):
        sys.path.insert(0, 'data_collection')
        import wavio
        files = sorted(f for f in os.listdir(a.events) if f.endswith('.wav'))
        Ns = [2000, 5000, 10000, 20000, 40000, 80000]
        drift = {k: [] for k in EST}
        for f in files:
            x, sr, _ = wavio.read(os.path.join(a.events, f))
            if x.ndim > 1: x = x[:, 0]
            if len(x) < Ns[-1]: continue
            for k, fn in EST.items():
                v = np.array([fn(x[:N]) for N in Ns])
                v = v[v > 0]
                if len(v) > 1: drift[k].append(float(v.max() / v.min()))
        n_used = len(drift['RMS'])
        print(f"  REAL EVENTS -- within-event convergence  ({n_used} of {len(files)} files)\n")
        print(f"  Window grown {Ns[0]:,} -> {Ns[-1]:,} samples inside ONE event.")
        print(f"  Ratio = largest estimate / smallest. 1.00 would mean perfectly settled.\n")
        print(f"    {'estimator':<14}{'median ratio':>14}{'worst':>10}")
        for k in EST:
            d = np.array(drift[k])
            print(f"    {k:<14}{np.median(d):>14.2f}{d.max():>10.2f}")
        res["real_within_event"] = {k: drift[k] for k in EST}
        rms_med = np.median(drift['RMS']); p90_med = np.median(drift['P90'])
        print(f"\n    RMS wanders {rms_med/p90_med:.1f}x more than the 90th percentile")
        print(f"    on the same audio, over the same windows.\n")

    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, "p1_normalisation.json")
    json.dump(res, open(jp, "w"), indent=2)
    print(f"  -> {jp}")

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, len(alphas), figsize=(4*len(alphas), 3.4), sharey=True)
        for ax, al in zip(axes, alphas):
            r = res[f"alpha={al}"]
            for k in EST: ax.loglog(lengths, r[k], marker='o', label=k)
            ax.set_title(f"alpha = {al}"); ax.set_xlabel("window length N"); ax.grid(alpha=.3)
        axes[0].set_ylabel("relative spread (lower = converging)"); axes[0].legend(fontsize=8)
        fig.suptitle("RMS does not converge for alpha < 2; percentile and FLOM do")
        fig.tight_layout()
        pp = os.path.join(a.out, "p1_normalisation.png"); fig.savefig(pp, dpi=130)
        print(f"  -> {pp}")
    except Exception as e:
        print(f"  (plot skipped: {type(e).__name__})")
    return 0

if __name__ == '__main__':
    sys.exit(main())
