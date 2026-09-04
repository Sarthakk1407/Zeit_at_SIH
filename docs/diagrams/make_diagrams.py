#!/usr/bin/env python3
"""Generate the system diagrams for the ZEIT docs. matplotlib only."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import textwrap

# validated palette
BG      = '#fcfcfb'
INK     = '#0b0b0b'
INK2    = '#52514e'
MUTED   = '#8a8981'
GRID    = '#e5e4df'
BLUE    = '#2a78d6'
BLUE_L  = '#cde2fb'
ORANGE  = '#eb6834'
ORANGE_L= '#fbe3d8'
AQUA    = '#1baf7a'
AQUA_L  = '#d6f2e7'
VIOLET  = '#4a3aa7'
VIOLET_L= '#e0dcf5'
RED     = '#d03b3b'
GOLD    = '#eda100'
GOLD_L  = '#fbeecd'

plt.rcParams.update({
    'figure.facecolor': BG, 'axes.facecolor': BG, 'savefig.facecolor': BG,
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Helvetica Neue', 'Helvetica'],
})


def box(ax, x, y, w, h, title, sub=None, fc='#ffffff', ec=BLUE, lw=1.6,
        tsize=10, ssize=7.6, tcol=INK, scol=INK2, r=0.02, wrap=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0,rounding_size={r}",
                 linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2))
    if sub:
        if wrap:
            sub = '\n'.join(textwrap.wrap(sub, wrap))
        ax.text(x + w/2, y + h*0.62, title, ha='center', va='center',
                fontsize=tsize, color=tcol, weight='semibold', zorder=3)
        ax.text(x + w/2, y + h*0.26, sub, ha='center', va='center',
                fontsize=ssize, color=scol, zorder=3, linespacing=1.35)
    else:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center',
                fontsize=tsize, color=tcol, weight='semibold', zorder=3)


def arrow(ax, p0, p1, color=INK2, lw=1.5, style='-|>', rad=0.0, ls='-'):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=13,
                 linewidth=lw, color=color, linestyle=ls, zorder=1,
                 connectionstyle=f"arc3,rad={rad}",
                 shrinkA=2, shrinkB=2))


def label(ax, x, y, s, size=8, color=MUTED, ha='center', style='normal',
          weight='normal'):
    ax.text(x, y, s, ha=ha, va='center', fontsize=size, color=color,
            style=style, weight=weight, zorder=4)


# ══════════════════════════════════ 1. SIGNAL PATH ═══════════════════════════
fig, ax = plt.subplots(figsize=(13, 9.5))
ax.set_xlim(0, 13); ax.set_ylim(0, 9.5); ax.axis('off')

ax.text(0.4, 9.1, 'ON-DEVICE SIGNAL PATH', fontsize=15, weight='bold', color=INK)
ax.text(0.4, 8.72, 'the only code that ships — every block labelled with the paper it comes from',
        fontsize=9.5, color=INK2)

W, H = 3.0, 0.82
CX = 5.0                      # centre column x
LX, RX = 1.5, 8.6             # left / right columns

# mics
box(ax, LX-0.7, 7.55, 2.5, 0.72, 'Mic 1 — primary', 'at the mouth, inside the mask',
    fc=GOLD_L, ec=GOLD, tsize=9.5, ssize=7.2)
box(ax, RX-0.4, 7.55, 2.5, 0.72, 'Mic 2 — reference', 'helmet exterior, outward facing',
    fc=GOLD_L, ec=GOLD, tsize=9.5, ssize=7.2)
label(ax, 6.5, 7.32, 'Widrow 1975  ·  Mic 2 must carry ZERO voice', 8.2, RED, weight='semibold')

# A
box(ax, CX, 6.35, W, H, '[A]  robust normalisation',
    '90th-percentile or FLOM — never RMS', fc=BLUE_L, ec=BLUE)
label(ax, CX+W+0.15, 6.76, 'Shao & Nikias 1993\nGap 2.2 · cross-finding B', 7.6, INK2, ha='left')
arrow(ax, (LX+0.55, 7.55), (CX+0.7, 6.35+H), rad=-0.15)
arrow(ax, (RX+0.85, 7.55), (CX+W-0.7, 6.35+H), rad=0.15)

# B
box(ax, CX, 5.25, W, H, '[B]  STFT + ERB analysis',
    'complex spectrum, ERB bands', fc=BLUE_L, ec=BLUE)
label(ax, CX+W+0.15, 5.66, 'DCCRN · GTCRN\nDeepFilterNet2 · IS³', 7.6, INK2, ha='left')
arrow(ax, (CX+W/2, 6.35), (CX+W/2, 5.25+H))

# split
box(ax, LX-0.7, 3.95, 2.9, H, '[C]  transient classifier',
    'kurtosis → tunes γ, β', fc=VIOLET_L, ec=VIOLET)
label(ax, LX-0.7, 3.72, 'BMRI Innovation 1  ·  ← this is the "adaptive"', 7.8, VIOLET,
      ha='left', weight='semibold')
box(ax, RX-0.4, 3.95, 2.9, H, '[D]  neural core',
    'GTCRN-class · grouped conv/RNN', fc=AQUA_L, ec=AQUA)
label(ax, RX-0.4, 3.72, 'GTCRN 2024 · H-GTCRN  ·  ← this is the "AI/ML"', 7.8, AQUA,
      ha='left', weight='semibold')
arrow(ax, (CX+0.5, 5.25), (LX+1.5, 3.95+H), rad=0.18)
arrow(ax, (CX+W-0.5, 5.25), (RX+1.4, 3.95+H), rad=-0.18)

# two paths
box(ax, LX-0.7, 2.4, 2.9, H, '[E]  impulsive path',
    'AR detect + interpolate', fc=ORANGE_L, ec=ORANGE)
label(ax, LX-0.7, 2.17, 'BMRI 2015 — detect & react, do NOT predict', 7.8, ORANGE, ha='left')
box(ax, RX-0.4, 2.4, 2.9, H, '[F]  stationary path',
    'learned mask + deep filtering', fc=AQUA_L, ec=AQUA)
label(ax, RX-0.4, 2.17, 'H-GTCRN ablation · DeepFilterNet2', 7.8, INK2, ha='left')
arrow(ax, (LX+0.75, 3.95), (LX+0.75, 2.4+H), color=ORANGE)
arrow(ax, (RX+1.05, 3.95), (RX+1.05, 2.4+H), color=AQUA)
arrow(ax, (RX+0.1, 3.95), (RX+0.75, 2.4+H), color=AQUA, rad=0.1)

# merge
box(ax, CX, 1.25, W, H, '[G]  intelligibility guard',
    'spectral correction, kills LF rumble', fc=BLUE_L, ec=BLUE)
label(ax, CX+W+0.15, 1.66, 'BMRI Innovation 3\nthe PS intelligibility clause', 7.6, INK2, ha='left')
arrow(ax, (LX+1.6, 2.4), (CX+0.6, 1.25+H), rad=-0.15)
arrow(ax, (RX+0.4, 2.4), (CX+W-0.6, 1.25+H), rad=0.15)

box(ax, CX, 0.25, W, 0.72, '[H] LMS residual  →  [I] ISTFT',
    'optional · Widrow', fc='#ffffff', ec=MUTED, tsize=9.5, ssize=7.2)
arrow(ax, (CX+W/2, 1.25), (CX+W/2, 0.97))
label(ax, CX+W+0.15, 0.6, '→  enhanced speech', 9.5, INK, ha='left', weight='semibold')

# the why callout
ax.add_patch(Rectangle((0.35, 0.25), 3.9, 1.35, facecolor='#fff', edgecolor=RED,
             linewidth=1.4, zorder=2))
ax.text(0.55, 1.42, 'WHY TWO PATHS', fontsize=9, weight='bold', color=RED, zorder=3)
ax.text(0.55, 0.95, 'Deep ANC buys latency back by\npredicting ahead. A gunshot is\n'
        'unpredictable by definition — so the\nimpulsive path reacts instead.',
        fontsize=8, color=INK2, va='center', zorder=3, linespacing=1.45)
for dpi, name in ((150, '1_signal_path.png'), (74, '1_signal_path_preview.png')):
    fig.savefig(name, dpi=dpi, bbox_inches='tight')
plt.close(fig)
print('  1_signal_path.png')


# ═══════════════════════════ 2. THREE LAYERS — WHAT GOES WHERE ═══════════════
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis('off')
ax.text(0.3, 8.6, 'WHERE EVERYTHING GOES', fontsize=15, weight='bold', color=INK)
ax.text(0.3, 8.22, 'three places — confusing them is the most common mistake',
        fontsize=9.5, color=INK2)

lanes = [
    (0.3,  4.35, 'HARDWARE', 'the physical device', GOLD, GOLD_L,
     [('Mic 1 — primary, at the mouth', 'Widrow'),
      ('Mic 2 — reference, helmet exterior', 'Widrow'),
      ('Isolation: Mic 2 carries ZERO voice', 'Widrow'),
      ('Dynamic mic for the blast path', 'Gap 1.5'),
      ('Our real headset geometry + spacing', 'Gap 2.4'),
      ('ADC 48 kHz / 24-bit', '—'),
      ('Edge board (undecided)', 'DeepFilterNet2 = RPi4'),
      ('USB power meter', 'Gap 2.3 — nobody reports W')]),
    (4.85, 4.35, 'ON-DEVICE', 'real time — every ms counts', BLUE, BLUE_L,
     [('[A] robust normalisation', 'Shao & Nikias'),
      ('[B] STFT + ERB', 'DCCRN / GTCRN'),
      ('[C] transient classifier', 'BMRI'),
      ('[D] neural core', 'GTCRN / H-GTCRN'),
      ('[E] impulsive path', 'BMRI'),
      ('[F] stationary path', 'H-GTCRN / DFN2'),
      ('[G] intelligibility guard', 'BMRI'),
      ('[H] LMS residual (optional)', 'Widrow')]),
    (9.4, 4.35, 'OFF-DEVICE', 'offline — none of it ships', AQUA, AQUA_L,
     [('Real gunshot capture', 'OURS'),
      ('Synthetic generator', 'IS³ template'),
      ('α-stable augmentation', 'Yuan et al.'),
      ('Sub-0.5 α, allowed to clip', 'Gap 3.3'),
      ('Input saturation model', 'Gap 1.5'),
      ('RIR spread + HRTF shadow', 'Gaps 1.6, 2.5'),
      ('Structured pruning', 'Tan et al.'),
      ('Quantization', 'Gap 2.7')]),
]
for lx, lw_, name, sub, col, fill, items in lanes:
    ax.add_patch(FancyBboxPatch((lx, 0.75), lw_, 7.2,
                 boxstyle="round,pad=0,rounding_size=0.06",
                 linewidth=2, edgecolor=col, facecolor=fill, alpha=0.35, zorder=1))
    ax.text(lx + lw_/2, 7.62, name, ha='center', fontsize=12, weight='bold', color=col)
    ax.text(lx + lw_/2, 7.28, sub, ha='center', fontsize=8, color=INK2, style='italic')
    y = 6.75
    for what, src in items:
        ax.add_patch(FancyBboxPatch((lx+0.18, y-0.28), lw_-0.36, 0.6,
                     boxstyle="round,pad=0,rounding_size=0.03",
                     linewidth=1.1, edgecolor=col, facecolor='#ffffff', zorder=2))
        ax.text(lx+0.34, y+0.05, what, fontsize=8.4, color=INK, va='center', zorder=3)
        ax.text(lx+0.34, y-0.16, src, fontsize=7, color=MUTED, va='center', zorder=3)
        y -= 0.78

arrow(ax, (4.68, 4.3), (4.98, 4.3), color=MUTED, lw=2)
arrow(ax, (13.9, 4.3), (9.28, 4.3), color=AQUA, lw=2, rad=0.0)
ax.text(11.6, 4.55, 'shapes the weights that ship', fontsize=8.5, color=AQUA,
        ha='center', style='italic')
ax.text(0.3, 0.35, 'Only FIVE sources put code on the device:  Widrow · Shao & Nikias · BMRI · GTCRN · H-GTCRN.'
        '     The other nine are baseline, method or evidence.',
        fontsize=9, color=INK, weight='semibold')
for dpi, name in ((150, '2_where_everything_goes.png'),):
    fig.savefig(name, dpi=dpi, bbox_inches='tight')
plt.close(fig)
print('  2_where_everything_goes.png')


# ═══════════════════════════════ 3. STAGE ORDER ══════════════════════════════
fig, ax = plt.subplots(figsize=(13, 8.5))
ax.set_xlim(0, 13); ax.set_ylim(0, 8.5); ax.axis('off')
ax.text(0.3, 8.1, 'THE ORDER', fontsize=15, weight='bold', color=INK)
ax.text(0.3, 7.72, 'what blocks what — and the one branch that needs no hardware at all',
        fontsize=9.5, color=INK2)

def stage(x, y, w, h, tag, title, sub, col, fill, status, scol):
    box(ax, x, y, w, h, title, sub, fc=fill, ec=col, tsize=10, ssize=7.4)
    ax.text(x+0.14, y+h-0.16, tag, fontsize=8, weight='bold', color=col, va='top')
    ax.text(x+w-0.14, y+h-0.16, status, fontsize=7.4, weight='bold', color=scol,
            va='top', ha='right')

stage(0.3, 6.05, 3.4, 1.15, 'STAGE 0', 'foundations',
      'toolkit · baselines · corpora · speech set', MUTED, '#f4f4f1', 'PARALLEL', MUTED)
stage(0.3, 4.35, 3.4, 1.15, 'STAGE 1', 'real reference',
      'range trip → calibrate → IR → freeze', GOLD, GOLD_L, 'BUILT, WAITING', GOLD)
stage(4.6, 4.35, 3.9, 1.15, 'STAGE 2', 'baseline collapse',
      'normalisation fix · impulsive grid · latency chart',
      RED, '#fbe9e9', 'START TODAY', RED)
stage(0.3, 2.75, 3.4, 1.15, 'STAGE 3', 'synthetic generator',
      'build → measure → compare vs holdout', BLUE, BLUE_L, '', BLUE)
stage(4.6, 2.75, 3.9, 1.15, 'STAGE 4', 'training data',
      'mix at SNRs · augment · convolve RIRs', BLUE, BLUE_L, '', BLUE)
stage(9.4, 2.75, 3.3, 1.15, 'STAGE 5', 'model',
      'two-path · train · evaluate', AQUA, AQUA_L, '', AQUA)
stage(9.4, 1.15, 3.3, 1.15, 'STAGE 6', 'edge',
      'prune · quantize · deploy · measure W', VIOLET, VIOLET_L, '', VIOLET)
stage(4.6, 1.15, 3.9, 1.15, 'STAGE 7', 'the extra experiment',
      'α-stable vs prune-ability', VIOLET, VIOLET_L, 'one exp, two wins', VIOLET)

arrow(ax, (2.0, 6.05), (2.0, 5.5), lw=1.8)
arrow(ax, (3.7, 6.35), (6.5, 5.5), lw=1.8, color=RED, rad=-0.12)
arrow(ax, (2.0, 4.35), (2.0, 3.9), lw=1.8)
arrow(ax, (5.6, 4.35), (3.3, 3.9), lw=1.8, color=RED, rad=0.15)
arrow(ax, (3.7, 3.3), (4.6, 3.3), lw=1.8)
arrow(ax, (8.5, 3.3), (9.4, 3.3), lw=1.8)
arrow(ax, (11.05, 2.75), (11.05, 2.3), lw=1.8)
arrow(ax, (9.4, 1.7), (8.5, 1.7), lw=1.8)

ax.add_patch(Rectangle((0.3, 0.2), 8.2, 0.72, facecolor='#fff', edgecolor=RED,
             linewidth=1.5, zorder=2))
ax.text(0.5, 0.72, 'STAGE 2 NEEDS NO RANGE DATA AND NO HARDWARE.', fontsize=9.5,
        weight='bold', color=RED, zorder=3)
ax.text(0.5, 0.42, 'Public corpora only. It produces the baseline-collapse table and the '
        'latency chart — the two findings the whole story argues from.',
        fontsize=8.2, color=INK2, zorder=3)
fig.savefig('3_the_order.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print('  3_the_order.png')
