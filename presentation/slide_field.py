"""Live-range data-collection evidence for the Feasibility slide.

The deck's strongest feasibility claim is that the gunshot data is *measured, not
downloaded*. That was only asserted in prose. These are the photographs of the
team executing the capture at an indoor range, plus the methodology that makes
the recording usable rather than merely dramatic.

The photographs live in `shooting-range/`. They are centre-cropped to a common
4:3 frame and downscaled here so the build stays reproducible from the originals
and the deck does not carry 4 MB phone captures.
"""
import glob
import os

from deckkit import (LABEL, INK, STEEL, MID, PALE, PALER, RUST, RUSTPL, GREEN, WHITE,
                     FONT, _in, textbox, block, rule, pointer_label, check_fit)

SRC_DIR = "shooting-range"

# The three frames, chosen to read as evidence: the whole range, the shot being
# fired beside the operator, and the waveform on the capture laptop.
PICKS = ["IMG-20260909-WA0052.jpg",   # hero — range, targets, shooter, laptop
         "IMG-20260909-WA0077.jpg",   # the shot, fired next to the capture rig
         "IMG-20260909-WA0075.jpg"]   # operator reading the signal on the laptop

TARGET_AR = 4.0 / 3.0                  # a uniform landscape frame for the strip
MAXW_PX = 1000


def prep_images():
    """Centre-crop each pick to 4:3 and downscale. Returns list of output paths.

    Missing files are skipped rather than fatal, so the build never breaks on a
    renamed capture; whatever is present is used.
    """
    from PIL import Image
    out = []
    for i, name in enumerate(PICKS, 1):
        hits = glob.glob(os.path.join(SRC_DIR, name))
        if not hits:
            # tolerate a moved/renamed file: take the i-th image in the folder
            pool = sorted(glob.glob(os.path.join(SRC_DIR, "*.jpg")) +
                          glob.glob(os.path.join(SRC_DIR, "*.jpeg")))
            if len(pool) >= i:
                hits = [pool[i - 1]]
        if not hits:
            continue
        im = Image.open(hits[0]).convert("RGB")
        w, h = im.size
        ar = w / h
        if ar > TARGET_AR:                     # too wide — trim the sides
            nw = int(round(h * TARGET_AR))
            x0 = (w - nw) // 2
            im = im.crop((x0, 0, x0 + nw, h))
        else:                                  # too tall — trim top and bottom
            nh = int(round(w / TARGET_AR))
            y0 = int((h - nh) * 0.60)          # bias down: the people/pistol/laptop
                                               # sit in the lower half, not the wall
            im = im.crop((0, y0, w, y0 + nh))
        if im.width > MAXW_PX:
            im = im.resize((MAXW_PX, int(round(MAXW_PX / TARGET_AR))),
                           Image.LANCZOS)
        p = "field-%d.jpg" % i
        im.save(p, quality=86)
        out.append(p)
    return out


def build(slide, y0=2.56, ph=1.30):
    """Draw the field-evidence band on the Feasibility slide.

    Left: a three-frame contact strip of the range capture.
    Right: the methodology that makes the recording a defensible reference.
    """
    pointer_label(slide, 0.55, y0, 8.4,
                  "Proof of execution — live-range gunshot capture (our own data)")
    # a small tag so a judge reads "ours", not "a stock photo"
    tag = textbox(slide, 9.05, y0 - 0.01, 3.7, 0.20,
                  [("PRIMARY DATA · NOT A PUBLIC DATASET", 8, True, RUST)])
    tag.text_frame.paragraphs[0].alignment = 2   # right

    # ---------------- contact strip
    paths = prep_images()
    pw, gap = 1.90, 0.13
    py = y0 + 0.24
    x = 0.55
    for p in paths:
        block(slide, x - 0.05, py - 0.05, pw + 0.10, ph + 0.10, fill=WHITE,
              line=MID, line_w=0.75, radius=0.03)
        slide.shapes.add_picture(p, _in(x), _in(py), width=_in(pw),
                                 height=_in(ph))
        x += pw + gap
    strip_right = x - gap
    if not paths:                              # never leave a hole
        block(slide, 0.55, py, 3 * pw + 2 * gap, ph, fill=PALER, line=MID,
              line_w=0.75, radius=0.03)
        strip_right = 0.55 + 3 * pw + 2 * gap

    textbox(slide, 0.55, py + ph + 0.06, strip_right - 0.55, 0.18,
            [("Indoor range · staggered-gain two-channel rig · captured live on the "
              "ZEIT toolkit laptop", 7.6, False, LABEL)], tag="field.cap")

    # ---------------- methodology, to the right of the strip
    mx = strip_right + 0.30
    mw = 13.03 - mx
    textbox(slide, mx, py, mw, 0.18,
            [("WHY THE RECORDING IS USABLE, NOT JUST DRAMATIC", 8, True, RUST)])
    facts = [
        "2-channel staggered gain 18–24 dB apart — the cold channel survives the clip",
        "96 kHz · 24-bit uncompressed WAV · limiter and high-pass OFF",
        "Calibrated to absolute dB SPL with a reference tone, not relative dBFS",
        "54 quantities measured per shot · 16 categories · frozen signature",
        "Holdout split assigned before the first shot · SHA-256 freezes data + engine",
        "GO / NO-GO validation after every three shots — a range is not repeatable",
    ]
    fy = py + 0.24
    for f in facts:
        block(slide, mx, fy + 0.055, 0.075, 0.075, fill=RUST, radius=0.5)
        textbox(slide, mx + 0.18, fy, mw - 0.18, 0.20, [(f, 8, False, STEEL)],
                tag="field.fact")
        fy += 0.215
    return py + ph            # bottom of the strip, for callers that need it
