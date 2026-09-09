"""Shared drawing helpers for the ZEIT SIH deck.

python-pptx gives us shapes and text but no layout help, so this module supplies
the primitives the deck is actually made of: chips, arrows, stat callouts, label
strips — plus a text-fit checker.

The fit checker matters more than usual here. LibreOffice is not available in
this environment, so slides cannot be rendered for visual QA. Instead every text
box is measured against the real Arial metrics from C:/Windows/Fonts, and
anything that would overflow is reported before the file ships.
"""
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------------------------------------------------------------- palette
# "Instrument": slate structure, steel support, one signal-rust accent.
INK    = RGBColor(0x13, 0x20, 0x2A)   # near-black slate — structure, headers
STEEL  = RGBColor(0x4A, 0x65, 0x72)   # secondary blocks
MID    = RGBColor(0x8F, 0xA3, 0xAD)   # muted rules, captions
PALE   = RGBColor(0xED, 0xF0, 0xF2)   # block fills
PALER  = RGBColor(0xF7, 0xF9, 0xFA)
RUST   = RGBColor(0xB3, 0x54, 0x1E)   # accent: the impulsive path, key numbers
RUSTPL = RGBColor(0xF7, 0xEC, 0xE4)
GREEN  = RGBColor(0x1E, 0x6B, 0x52)   # output / meets-target
GREENPL= RGBColor(0xE6, 0xF0, 0xEC)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
FONT   = "Arial"

EMU_IN = 914400


def _in(v):
    return Emu(int(round(v * EMU_IN)))


# ---------------------------------------------------------------- text fit
_FONTS = {}


def _font(bold, size_pt):
    from PIL import ImageFont
    path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    key = (bold, int(size_pt * 4))
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, int(round(size_pt * 4)))
    return _FONTS[key]


def text_width_in(s, size_pt, bold=False):
    """Width of a single line, in inches, using real Arial metrics."""
    try:
        f = _font(bold, size_pt)
        return (f.getlength(s) / 4.0) / 72.0
    except Exception:
        return len(s) * size_pt * 0.5 / 72.0


ISSUES = []


def check_fit(tag, s, box_w_in, size_pt, bold=False, lines=1, pad=0.14):
    """Record a warning if a string cannot fit the width it was given."""
    w = text_width_in(s, size_pt, bold)
    avail = (box_w_in - pad) * lines
    if w > avail:
        ISSUES.append("%-30s %5.2f\" needed vs %5.2f\" available  |  %s"
                      % (tag, w, avail, s[:60]))


# ---------------------------------------------------------------- primitives
def style_run(r, size, bold=False, color=INK, italic=False, font=FONT):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font


def textbox(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.TOP, line_spacing=None, tag=None):
    """lines = [(text, size, bold, color) | (text, size, bold, color, space_after)]"""
    tb = slide.shapes.add_textbox(_in(x), _in(y), _in(w), _in(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, spec in enumerate(lines):
        txt, size, bold, color = spec[0], spec[1], spec[2], spec[3]
        space_after = spec[4] if len(spec) > 4 else 0
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line_spacing:
            p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = txt
        style_run(r, size, bold, color)
        if tag:
            check_fit("%s[%d]" % (tag, i), txt, w, size, bold)
    return tb


def block(slide, x, y, w, h, fill=PALE, line=None, line_w=1.0, radius=None,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = slide.shapes.add_shape(shape, _in(x), _in(y), _in(w), _in(h))
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    sh.text_frame.word_wrap = True
    sh.text_frame.margin_left = sh.text_frame.margin_right = _in(0.05)
    sh.text_frame.margin_top = sh.text_frame.margin_bottom = _in(0.03)
    return sh


def chip(slide, x, y, w, h, title, sub=None, fill=PALE, fg=INK,
         ts=10.5, ss=7.5, line=None, radius=0.14, tag=None):
    """A labelled block — the deck's basic flowchart unit."""
    sh = block(slide, x, y, w, h, fill=fill, line=line, radius=radius)
    tf = sh.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(0)
    r = p.add_run()
    r.text = title
    style_run(r, ts, True, fg)
    if tag:
        check_fit(tag, title, w, ts, True)
    if sub:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(1)
        r2 = p2.add_run()
        r2.text = sub
        style_run(r2, ss, False, fg)
        if tag:
            check_fit(tag + ".sub", sub, w, ss, False)
    return sh


def arrow(slide, x, y, w, h=0.14, color=STEEL, direction="right"):
    shp = {"right": MSO_SHAPE.RIGHT_ARROW, "down": MSO_SHAPE.DOWN_ARROW,
           "left": MSO_SHAPE.LEFT_ARROW, "up": MSO_SHAPE.UP_ARROW}[direction]
    sh = slide.shapes.add_shape(shp, _in(x), _in(y), _in(w), _in(h))
    sh.shadow.inherit = False
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return sh


def rule(slide, x, y, w, color=MID, weight=0.75):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, _in(x), _in(y),
                                    _in(x + w), _in(y))
    ln.line.color.rgb = color
    ln.line.width = Pt(weight)
    return ln


def vrule(slide, x, y, h, color=MID, weight=0.75):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, _in(x), _in(y),
                                    _in(x), _in(y + h))
    ln.line.color.rgb = color
    ln.line.width = Pt(weight)
    return ln


def elbow(slide, x1, y1, x2, y2, color=STEEL, weight=1.25):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.ELBOW, _in(x1), _in(y1),
                                    _in(x2), _in(y2))
    ln.line.color.rgb = color
    ln.line.width = Pt(weight)
    return ln


def pointer_label(slide, x, y, w, text, size=9.5, color=RUST):
    """The template's mandated pointer text, kept verbatim as a section label."""
    tb = textbox(slide, x, y, w, 0.22,
                 [(text.upper(), size, True, color)])
    tb.text_frame.paragraphs[0].runs[0].font.name = FONT
    check_fit("pointer", text.upper(), w, size, True)
    return tb


def stat(slide, x, y, w, value, label, vs=26, ls=8, color=INK, sub=None):
    textbox(slide, x, y, w, 0.42, [(value, vs, True, color)], tag="stat.v")
    textbox(slide, x, y + 0.40, w, 0.17, [(label, ls, False, STEEL)], tag="stat.l")
    if sub:
        textbox(slide, x, y + 0.58, w, 0.24, [(sub, 7, False, MID)], tag="stat.s")


def delete_shape(sh):
    e = sh._element
    e.getparent().remove(e)


def set_ph_text(shape, text, size=None, bold=None, color=None):
    """Replace placeholder text, keeping the first run's formatting."""
    tf = shape.text_frame
    p = tf.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for extra in p.runs[1:]:
            extra._r.getparent().remove(extra._r)
        r = p.runs[0]
    else:
        r = p.add_run()
        r.text = text
    if size is not None:
        r.font.size = Pt(size)
    if bold is not None:
        r.font.bold = bold
    if color is not None:
        r.font.color.rgb = color
    for extra in tf.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    return shape

# ---------------------------------------------------------------- flow lines
# Connectors are built from explicit segments plus a triangle head rather than
# from connector arrowheads, so PowerPoint and the preview renderer draw
# identical geometry.
def _head(slide, x, y, direction, color, size=0.13):
    tri = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,
                                 _in(x - size / 2), _in(y - size / 2),
                                 _in(size), _in(size))
    tri.shadow.inherit = False
    tri.fill.solid()
    tri.fill.fore_color.rgb = color
    tri.line.fill.background()
    tri.rotation = {"up": 0, "right": 90, "down": 180, "left": 270}[direction]
    return tri


def flow(slide, pts, color=STEEL, weight=1.5, head=True, size=0.13):
    """Polyline through pts [(x,y), ...] with an arrowhead on the last segment."""
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                        _in(x1), _in(y1), _in(x2), _in(y2))
        ln.line.color.rgb = color
        ln.line.width = Pt(weight)
    if head:
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        if abs(x2 - x1) >= abs(y2 - y1):
            d = "right" if x2 > x1 else "left"
        else:
            d = "down" if y2 > y1 else "up"
        _head(slide, x2, y2, d, color, size)


def flow_label(slide, x, y, w, text, color=STEEL, size=7):
    tb = textbox(slide, x, y, w, 0.18, [(text, size, False, color)],
                 align=PP_ALIGN.CENTER)
    check_fit("flowlabel", text, w, size, False)
    return tb


def diamond(slide, x, y, w, h, title, sub=None, fill=RUSTPL, line=RUST,
            fg=INK, ts=9, ss=6.5):
    """Decision node — the point the two paths diverge from.

    A diamond only offers about half its bounding width to text, and less than
    that away from the vertical centre. Both strings are checked against that
    inscribed width rather than against w, which is what made the label wrap in
    PowerPoint while the preview showed it fitting.
    """
    inscribed = w * 0.46
    check_fit("diamond", title, inscribed, ts, True, pad=0.04)
    if sub:
        check_fit("diamond.sub", sub, inscribed, ss, False, pad=0.04)
    sh = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, _in(x), _in(y), _in(w), _in(h))
    sh.shadow.inherit = False
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line; sh.line.width = Pt(1.25)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = _in(0.04)
    tf.margin_top = tf.margin_bottom = _in(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.space_after = Pt(0)
    r = p.add_run(); r.text = title
    style_run(r, ts, True, fg)
    if sub:
        p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = sub
        style_run(r2, ss, False, fg)
    return sh


def band(slide, x, y, w, h, label, sub=None, color=STEEL, fill=None):
    """A labelled lane behind a row of flow blocks."""
    sh = block(slide, x, y, w, h, fill=fill or PALER, line=color, line_w=0.75,
               radius=0.05)
    textbox(slide, x + 0.12, y + 0.07, w - 0.24, 0.18,
            [(label.upper() + ("  ·  " + sub if sub else ""), 7.5, True, color)])
    return sh
