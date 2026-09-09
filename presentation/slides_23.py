"""Slides 2 and 3 — the two flowchart slides.

Kept in their own module because they are the only slides with real diagram
geometry: a fork, a feedback loop, a decision node, two parallel paths and a
merge. Everything is drawn from explicit coordinates so PowerPoint and the
preview renderer agree.
"""
import os
from pptx.util import Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

def _mentor_image():
    """Find the approval screenshot and crop it to the email body.

    The raw capture is a whole browser window; at slide scale the Gmail
    sidebar and toolbar are unreadable noise. Cropping is done here rather
    than by hand so the build stays reproducible from the original file.
    """
    import glob
    from PIL import Image
    for pat in ("mentor-approval.png", "mentor_approval.png",
                "mentor approval.png", "mentor*approval*.png"):
        hits = [h for h in glob.glob(pat) if "crop" not in h]
        if hits:
            src = hits[0]
            break
    else:
        return None
    out = "mentor-approval-crop.png"
    im = Image.open(src)
    if im.width > 1200:                       # full-window capture
        im = im.crop((330, 214, im.width, 678))
    im.save(out)
    return out, im.width / im.height

from deckkit import (INK, STEEL, MID, PALE, PALER, RUST, RUSTPL, GREEN, GREENPL,
                     WHITE, FONT, _in, textbox, block, chip, rule, vrule,
                     pointer_label, stat, flow, flow_label, diamond, band,
                     check_fit)


# =====================================================================
def slide2(s2, PTS2, title_fn):
    title_fn(s2, "ZEIT — Two-Lane Impulse-Adaptive Noise Cancellation", 25)
    L, R = 0.55, 8.92
    LW, RW = 8.05, 3.86

    textbox(s2, L, 1.20, 12.2, 0.22, [(PTS2[0].upper(), 9, True, MID)])
    pointer_label(s2, L, 1.46, LW, PTS2[1])

    # ---------------- lane bands
    band(s2, 2.35, 1.72, 6.25, 0.94, "Lane A",
         "hearing protection  ·  under 1 ms  ·  FxLMS, no neural network", RUST)
    band(s2, 2.35, 2.94, 6.25, 0.94, "Lane B",
         "transmit to radio  ·  25.3 ms  ·  eleven blocks", INK)

    # ---------------- microphones (inputs)
    mics = [("Mic 3 · error", 2.00, RUSTPL, RUST),
            ("Mic 2 · reference", 2.61, PALE, STEEL),
            ("Mic 1 · voice", 3.22, PALE, INK)]
    for t, y, f, e in mics:
        chip(s2, L, y, 1.45, 0.48, t, fill=f, line=e, ts=8.5, tag="s2.mic")

    # ---------------- lane contents
    laneA = ["FxLMS filter", "Anti-noise driver", "The ear"]
    laneB = ["Engine · 11 blocks", "Vocoder · MELPe", "Radio link"]
    xs = [2.55, 4.55, 6.55]
    for x, t in zip(xs, laneA):
        chip(s2, x, 2.00, 1.72, 0.48, t, fill=WHITE, line=RUST, ts=8.5,
             tag="s2.A")
    for x, t in zip(xs, laneB):
        f = GREENPL if t.startswith("Radio") else WHITE
        e = GREEN if t.startswith("Radio") else INK
        chip(s2, x, 3.22, 1.72, 0.48, t, fill=f, line=e, ts=8.5, tag="s2.B")

    # ---------------- flow: inputs into the lanes
    flow(s2, [(2.00, 2.24), (2.55, 2.24)], RUST)                    # mic3 → FxLMS
    flow(s2, [(2.00, 3.46), (2.55, 3.46)], INK)                     # mic1 → engine
    flow(s2, [(2.00, 2.85), (2.22, 2.85), (2.22, 2.34), (2.55, 2.34)], STEEL)
    flow(s2, [(2.22, 2.85), (2.22, 3.36), (2.55, 3.36)], STEEL)     # mic2 → both

    # ---------------- flow: along each lane
    for x in (4.27, 6.27):
        flow(s2, [(x, 2.24), (x + 0.28, 2.24)], RUST)
        flow(s2, [(x, 3.46), (x + 0.28, 3.46)], INK)

    # ---------------- the closed loop that makes Lane A adaptive
    flow(s2, [(7.41, 2.48), (7.41, 2.74), (3.41, 2.74), (3.41, 2.48)], RUST)
    flow_label(s2, 3.90, 2.76, 3.10,
               "error signal — what still reaches the ear", RUST, 6.8)

    # ---------------- requirement → mechanism
    pointer_label(s2, L, 3.98, LW, PTS2[2])
    rows = [("Impulsive noise — gunshots, artillery",
             "Detect-and-react transient path; α-stable augmentation trained through the clipping"),
            ("Adaptive",
             "Live kurtosis classifier retunes γ and β every frame, not tuned once offline"),
            ("High speech intelligibility",
             "Voice guard, plus DNSMOS SIG reported separately so over-suppression is visible"),
            ("Real-time on embedded hardware",
             "23.7 K parameters at 39.6 MMAC/s — a Raspberry Pi 5, not a Jetson")]
    y = 4.22
    for req, mech in rows:
        block(s2, L, y, LW, 0.54, fill=PALER, radius=0.10)
        textbox(s2, L + 0.14, y + 0.08, 2.90, 0.38, [(req, 9, True, INK)],
                tag="s2.req")
        textbox(s2, L + 3.10, y + 0.05, LW - 3.28, 0.44,
                [(mech, 8.5, False, STEEL)], line_spacing=0.94)
        y += 0.60

    # ---------------- differentiation
    pointer_label(s2, R, 1.46, RW, PTS2[3])
    diffs = [("Two lanes, not one",
              "Protection needs under a millisecond; transmit tolerates 25 ms. Fusing them makes both impossible."),
             ("Detect, do not predict",
              "Published deep ANC buys latency by predicting noise. A gunshot is unpredictable by definition."),
             ("Crack before blast",
              "The supersonic shockwave arrives 42.3 ms ahead of the muzzle blast. Physical look-ahead, not algorithmic."),
             ("RMS is undefined here",
              "Heavy-tailed noise has infinite variance. We scale on percentile and fractional lower-order moments."),
             ("Measured, not downloaded",
              "Calibrated gunshot data, holdout split assigned before capture, checksum-frozen reference.")]
    y = 1.70
    for i, (h, d) in enumerate(diffs, 1):
        block(s2, R, y, RW, 0.96, fill=WHITE, line=MID, line_w=0.75, radius=0.08)
        block(s2, R + 0.13, y + 0.13, 0.30, 0.30, fill=RUST, radius=0.5,
              shape=MSO_SHAPE.OVAL)
        textbox(s2, R + 0.13, y + 0.17, 0.30, 0.24, [(str(i), 10, True, WHITE)],
                align=PP_ALIGN.CENTER)
        textbox(s2, R + 0.52, y + 0.13, RW - 0.66, 0.24, [(h, 10, True, INK)],
                tag="s2.diff")
        textbox(s2, R + 0.52, y + 0.37, RW - 0.66, 0.54, [(d, 8, False, STEEL)],
                line_spacing=0.94)
        y += 1.02


# =====================================================================
def slide3(s3, PTS3, title_fn):
    title_fn(s3, "TECHNICAL APPROACH", 27)

    # ---------------- technologies
    pointer_label(s3, 0.55, 1.16, 12.2, PTS3[0])
    tech = [("C++17", "real-time path"), ("ONNX Runtime", "inference on ARM"),
            ("PyTorch", "training, offline"), ("GTCRN", "23.7 K params"),
            ("Aux-IVA", "blind separation"), ("BMRI", "impulsive path"),
            ("PFFFT", "BSD FFT, not GPL"), ("Raspberry Pi 5", "8 GB, the engine"),
            ("UMC202HD", "2-ch capture")]
    x = 0.55
    for t, sub in tech:
        chip(s3, x, 1.36, 1.28, 0.48, t, sub, fill=PALE, ts=8.5, ss=6.5,
             tag="s3.tech")
        x += 1.36

    pointer_label(s3, 0.55, 2.02, 12.2, PTS3[1])

    # ---------------- hardware chain
    textbox(s3, 0.55, 2.22, 12.2, 0.18,
            [("HARDWARE CHAIN — no development computer in the signal path",
              7.5, True, MID)])
    hw = [("3 microphones", "voice · reference · error"), ("UMC202HD", "24-bit, 48 V"),
          ("Raspberry Pi 5", "blocks 1–11"), ("Communication unit", "MELPe 2400 bps"),
          ("Earcups", "return audio")]
    x = 0.55
    for i, (t, sub) in enumerate(hw):
        chip(s3, x, 2.36, 2.20, 0.46, t, sub, fill=WHITE, line=STEEL, ts=8.5,
             ss=6.5, tag="s3.hw")
        if i < len(hw) - 1:
            flow(s3, [(x + 2.20, 2.59), (x + 2.44, 2.59)], STEEL, 1.5, size=0.11)
        x += 2.44

    # ---------------- Lane B chain: sequence → decision → two paths → merge
    textbox(s3, 0.55, 2.96, 12.2, 0.18,
            [("LANE B SIGNAL CHAIN — one 20 ms frame, 10 ms hop, 25.3 ms end to end",
              7.5, True, MID)])

    row1 = [("01", "Audio in"), ("02", "Aux-IVA"), ("03", "Normalise"),
            ("04", "STFT + ERB")]
    x = 0.55
    for n, t in row1:
        _numbered(s3, x, 3.14, 1.48, 0.48, n, t, PALE, None, INK)
        flow(s3, [(x + 1.48, 3.38), (x + 1.66, 3.38)], STEEL, 1.5, size=0.11)
        x += 1.66

    diamond(s3, 7.10, 2.905, 2.40, 0.95, "05  Classifier", "kurtosis → γ, β",
            ts=8.5, ss=6.5)
    textbox(s3, 9.66, 3.24, 3.10, 0.34,
            [("the adaptive decision — what makes the system adapt per "
              "frame rather than being tuned once", 6.8, False, RUST)],
            line_spacing=0.94)

    # branch out of the decision node
    flow(s3, [(8.30, 3.855), (8.30, 4.00), (6.85, 4.00), (6.85, 4.20)], RUST)
    flow(s3, [(8.30, 4.00), (9.95, 4.00), (9.95, 4.20)], INK)
    flow_label(s3, 5.75, 3.79, 2.20, "impulsive frame", RUST, 6.8)
    flow_label(s3, 9.10, 3.79, 2.60, "stationary / non-stationary", INK, 6.8)

    _numbered(s3, 5.65, 4.20, 2.40, 0.50, "06", "BMRI — detect and interpolate",
              RUSTPL, RUST, INK)
    _numbered(s3, 8.75, 4.20, 2.40, 0.50, "07", "GTCRN — learned mask",
              INK, INK, WHITE)

    # merge the two paths back together
    flow(s3, [(6.85, 4.70), (6.85, 4.90), (4.34, 4.90)], RUST, head=False)
    flow(s3, [(9.95, 4.70), (9.95, 4.90), (4.34, 4.90)], INK, head=False)
    flow(s3, [(4.34, 4.90), (4.34, 5.10)], STEEL)
    flow_label(s3, 4.55, 4.94, 2.20, "recombine", STEEL, 6.8)

    row3 = [("08", "Deep filter"), ("09", "Voice guard"), ("10", "Residual"),
            ("11", "ISTFT"), ("→", "Radio")]
    x = 3.60
    for i, (n, t) in enumerate(row3):
        f, e, fg = (GREENPL, GREEN, INK) if n == "→" else (PALE, None, INK)
        _numbered(s3, x, 5.10, 1.48, 0.48, n, t, f, e, fg)
        if i < len(row3) - 1:
            flow(s3, [(x + 1.48, 5.34), (x + 1.66, 5.34)], STEEL, 1.5, size=0.11)
        x += 1.66

    # ---------------- offline pipeline, with its validation loop
    textbox(s3, 0.55, 5.72, 12.2, 0.18,
            [("OFFLINE PIPELINE — none of this ships; it shapes the weights that do",
              7.5, True, MID)])
    off = [("Range capture", "96 kHz · calibrated"), ("Measure", "16 quantities"),
           ("Validate", "against holdout"), ("Mix + augment", "α-stable, clipped"),
           ("Train", "SI-SNR + L1"), ("Prune + quantise", "structured, INT8"),
           ("Export ONNX", "the only boundary"), ("C++ engine", "parity-tested")]
    x = 0.55
    for i, (t, sub) in enumerate(off):
        chip(s3, x, 5.88, 1.42, 0.44, t, sub, fill=PALER, line=MID, ts=7.5,
             ss=6.2, tag="s3.off")
        if i < len(off) - 1:
            flow(s3, [(x + 1.42, 6.10), (x + 1.50, 6.10)], MID, 1.2, size=0.09)
        x += 1.52

    # retune loop: validation failure feeds back to the generator
    flow(s3, [(3.68, 6.32), (3.68, 6.48), (1.97, 6.48), (1.97, 6.32)], RUST, 1.25)
    flow_label(s3, 1.30, 6.50, 3.10, "mismatch → retune the generator", RUST, 6.5)

    textbox(s3, 6.20, 6.48, 6.55, 0.22,
            [("25.3 ms algorithmic  ·  10 ms compute per hop  ·  under 1 ms Lane A  "
              "·  39.6 MMAC/s", 8, True, INK)], align=PP_ALIGN.RIGHT)


def _numbered(slide, x, y, w, h, num, text, fill, line, fg):
    sh = block(slide, x, y, w, h, fill=fill, line=line, radius=0.10)
    tf = sh.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(0)
    r = p.add_run(); r.text = num
    r.font.size = Pt(6.5); r.font.bold = True; r.font.name = FONT
    r.font.color.rgb = MID if fg == INK else WHITE
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run(); r2.text = text
    r2.font.size = Pt(8); r2.font.bold = True; r2.font.name = FONT
    r2.font.color.rgb = fg
    check_fit("blk", text, w, 8, True, lines=2)
    return sh
