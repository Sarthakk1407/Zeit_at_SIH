# -*- coding: utf-8 -*-
"""Tentative PCB layout for the Lane A module, drawn to scale.

Lane A has to close its loop in under a millisecond, so it cannot sit behind a
general-purpose scheduler on the Pi. It is its own board, clipped inside the
earcup. This draws that board at 32 x 24 mm — small enough to fit the cup,
large enough for the codec, the DSP and four connectors.

Output: hw/pcb-lane-a.png
"""
import os

from PIL import Image, ImageDraw, ImageFont

MM = 46                      # pixels per millimetre
BW, BH = 34.0, 26.0          # board size in millimetres
PAD = 58                     # canvas margin in pixels

W = int(BW * MM) + PAD * 2
H = int(BH * MM) + PAD * 2

# A real board's palette: soldermask, immersion-gold pads, white silkscreen.
MASK = (14, 104, 66)
MASK_HI = (18, 124, 79)
COPPER = (206, 160, 62)
GOLD = (226, 186, 92)
SILK = (238, 244, 240)
SILK_DIM = (176, 198, 186)
BODY = (24, 26, 30)
BODY_HI = (46, 50, 56)
METAL = (176, 182, 190)
INK = (11, 23, 36)
BLUE = (0, 112, 192)


def font(sz, bold=False):
    for n in (("arialbd.ttf" if bold else "arial.ttf"),
              ("Arialbd.ttf" if bold else "Arial.ttf")):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + n, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def mm(v):
    return int(round(v * MM))


def X(v):
    return PAD + mm(v)


def Y(v):
    return PAD + mm(v)


im = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(im, "RGBA")

# ---------------------------------------------------------------- board
board = [X(0), Y(0), X(BW), Y(BH)]
d.rounded_rectangle(board, radius=mm(1.6), fill=MASK)
# a faint top-light so the mask is not a flat slab
d.rounded_rectangle([board[0], board[1], board[2], board[1] + mm(6)],
                    radius=mm(1.6), fill=MASK_HI + (90,))

# ground pour: a light hatch, the way a plane reads on a layout viewer.
# Drawn on its own layer and masked to the board, or it bleeds past the edge.
hatch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(hatch)
for i in range(-int(BH * MM), int(BW * MM), 14):
    hd.line([X(0) + i, Y(0), X(0) + i + mm(BH), Y(BH)],
            fill=MASK_HI + (70,), width=1)
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).rounded_rectangle(board, radius=mm(1.6), fill=255)
im.paste(Image.alpha_composite(im.convert("RGBA"), hatch).convert("RGB"),
         (0, 0), mask)
d = ImageDraw.Draw(im, "RGBA")

# ---------------------------------------------------------------- copper
def trace(pts, w=3.0, col=COPPER):
    px = [(X(a), Y(b)) for a, b in pts]
    d.line(px, fill=col, width=int(w), joint="curve")


# analogue in from the two microphones, kept short and on the left
trace([(1.6, 6.2), (5.4, 6.2), (6.6, 7.4), (10.4, 7.4)], 3)
trace([(1.6, 9.0), (4.8, 9.0), (6.2, 10.4), (10.4, 10.4)], 3)
# codec to DSP bus
for i, yy in enumerate((11.6, 12.4, 13.2, 14.0)):
    trace([(16.4, yy), (18.4, yy), (19.6, yy + 0.6), (21.4, yy + 0.6)], 2.4)
# DSP out to the driver amplifier
trace([(27.4, 12.0), (29.2, 12.0), (30.0, 13.2), (30.0, 15.9)], 3.4)
# power rail along the bottom
trace([(1.6, 23.2), (32.2, 23.2)], 5, (196, 150, 56))
trace([(1.6, 21.6), (32.2, 21.6)], 4, (196, 150, 56))


def part(x, y, w, h, label, sub=None, fill=BODY, pins=0, side="lr",
         lab_above=True, fs=17):
    """A component: body, pins, and a silkscreen label."""
    x0, y0, x1, y1 = X(x), Y(y), X(x + w), Y(y + h)
    if pins:
        step = (y1 - y0) / (pins + 1.0)
        for i in range(1, pins + 1):
            py = y0 + step * i
            if "l" in side:
                d.rectangle([x0 - mm(0.5), py - 2, x0, py + 2], fill=GOLD)
            if "r" in side:
                d.rectangle([x1, py - 2, x1 + mm(0.5), py + 2], fill=GOLD)
    d.rounded_rectangle([x0, y0, x1, y1], radius=3, fill=fill)
    d.rounded_rectangle([x0, y0, x1, y0 + max(3, (y1 - y0) // 5)], radius=3,
                        fill=BODY_HI)
    # pin-1 dot
    d.ellipse([x0 + 5, y0 + 5, x0 + 11, y0 + 11], fill=SILK_DIM)
    f = font(fs, True)
    tw = d.textlength(label, font=f)
    ly = y0 - fs - 6 if lab_above else y1 + 6
    d.text(((x0 + x1) / 2 - tw / 2, ly), label, font=f, fill=SILK)
    if sub:
        f2 = font(fs - 4)
        tw2 = d.textlength(sub, font=f2)
        d.text(((x0 + x1) / 2 - tw2 / 2, ly + fs + 1 if lab_above else ly + fs + 1),
               sub, font=f2, fill=SILK_DIM)


def connector(x, y, w, h, n, label):
    """A pin header: gold pads in a white silkscreen outline."""
    x0, y0, x1, y1 = X(x), Y(y), X(x + w), Y(y + h)
    d.rectangle([x0, y0, x1, y1], outline=SILK, width=2)
    step = (x1 - x0) / (n + 0.0)
    for i in range(n):
        cx = x0 + step * (i + 0.5)
        d.ellipse([cx - 6, (y0 + y1) / 2 - 6, cx + 6, (y0 + y1) / 2 + 6],
                  fill=GOLD, outline=(150, 112, 40))
        d.ellipse([cx - 2, (y0 + y1) / 2 - 2, cx + 2, (y0 + y1) / 2 + 2],
                  fill=MASK)
    f = font(15, True)
    tw = d.textlength(label, font=f)
    d.text(((x0 + x1) / 2 - tw / 2, y1 + 4), label, font=f, fill=SILK)


# ---------------------------------------------------------------- parts
part(10.4, 5.4, 6.0, 6.0, "CODEC", "24-bit · 2-in 1-out", pins=6)
part(21.4, 8.4, 6.0, 6.6, "ANC DSP", "FxLMS core", pins=7)
part(28.0, 16.4, 3.4, 3.0, "AMP", None, fill=(30, 34, 40), pins=3, side="l",
     lab_above=False, fs=14)
part(17.6, 17.4, 3.0, 2.2, "LDO", None, fill=(30, 34, 40), pins=3, side="lr",
     lab_above=False, fs=14)

# crystal
d.rounded_rectangle([X(22.0), Y(16.6), X(24.6), Y(18.2)], radius=3, fill=METAL)
d.text((X(22.0), Y(18.5)), "24 MHz", font=font(13, True), fill=SILK)

# passives
for px, py in ((7.0, 12.6), (7.9, 12.6), (8.8, 12.6), (7.0, 14.0), (7.9, 14.0),
               (13.0, 16.2), (14.0, 16.2), (15.0, 16.2), (25.4, 16.6),
               (26.4, 16.6), (12.0, 20.0), (13.0, 20.0), (14.0, 20.0)):
    d.rectangle([X(px), Y(py), X(px + 0.6), Y(py + 0.32)], fill=(222, 226, 232))

# ---------------------------------------------------------------- connectors
connector(0.9, 5.4, 3.4, 1.6, 2, "J1  MIC 2")
connector(0.9, 8.2, 3.4, 1.6, 2, "J2  MIC 3")
connector(29.7, 3.0, 3.4, 1.6, 2, "J3  DRIVER")
connector(0.9, 15.4, 5.0, 1.6, 4, "J4  PWR / I2C")

# mounting holes
for hx, hy in ((1.7, 1.7), (BW - 1.7, 1.7), (1.7, BH - 1.7), (BW - 1.7, BH - 1.7)):
    d.ellipse([X(hx) - mm(0.8), Y(hy) - mm(0.8), X(hx) + mm(0.8), Y(hy) + mm(0.8)],
              fill=(250, 250, 250))
    d.ellipse([X(hx) - mm(0.5), Y(hy) - mm(0.5), X(hx) + mm(0.5), Y(hy) + mm(0.5)],
              fill=(198, 202, 208))

# silkscreen identity
d.text((X(6.6), Y(21.8)), "ZEIT  LANE-A  ANC MODULE", font=font(19, True),
       fill=SILK)
d.text((X(6.6), Y(23.3)), "rev A  ·  34 x 26 mm  ·  2-layer  ·  FxLMS loop, < 1 ms",
       font=font(14), fill=SILK_DIM)

# ---------------------------------------------------------------- dimensions
f = font(17, True)
d.line([X(0), Y(BH) + 22, X(BW), Y(BH) + 22], fill=INK, width=2)
for e in (0, BW):
    d.line([X(e), Y(BH) + 14, X(e), Y(BH) + 30], fill=INK, width=2)
lab = "34 mm"
d.text((X(BW / 2) - d.textlength(lab, font=f) / 2, Y(BH) + 28), lab, font=f,
       fill=INK)

d.line([X(BW) + 22, Y(0), X(BW) + 22, Y(BH)], fill=INK, width=2)
for e in (0, BH):
    d.line([X(BW) + 14, Y(e), X(BW) + 30, Y(e)], fill=INK, width=2)
d.text((X(BW) + 30, Y(BH / 2) - 10), "26 mm", font=f, fill=INK)

im.save(os.path.join("hw", "pcb-lane-a.png"), quality=95)
print("hw/pcb-lane-a.png", im.size)
