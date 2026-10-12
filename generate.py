"""Generate printable keypad overlays for the TTP229 16-key touch module.

Usage:  python3 generate.py
Needs:  pip install reportlab
Output: layouts/<name>.pdf  (A4, 6 color variants, print at 100%)
        all_layouts.pdf     (one of each layout, for trying them out)
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor

# ---- Board geometry (mm) ----
W, H = 49.3, 64.5          # PCB size
M = 1.5                    # margin between board edge and key grid
P = (W - 2 * M) / 4        # key pitch (~11.6 mm)
G = 0.8                    # gap between keys
S = P - G                  # key size (~10.8 mm)

# ---- Styles ----
# n = main (theme color), f = function (gray), r = red, g = green
FIXED = {"f": ("#455A64", "#FFFFFF"), "r": ("#D32F2F", "#FFFFFF"), "g": ("#2E7D32", "#FFFFFF")}
THEMES = [("#FFFFFF", "#111111"), ("#111111", "#FFFFFF"), ("#1565C0", "#FFFFFF"),
          ("#6A1B9A", "#FFFFFF"), ("#00838F", "#FFFFFF"), ("#F9A825", "#111111")]

# Each layout: 4 rows x 4 cols, top row first, matching module keys 1..16.
# A cell is None (unused) or (label, style). Labels starting with "@" are icons.
def row(*cells):
    return [None if c is None else (c if isinstance(c, tuple) else (c, "n")) for c in cells]

F, R, Gr = "f", "r", "g"
LAYOUTS = [
    ("01-numpad", "Numpad (original)", [
        row("1", "2", "3", None), row("4", "5", "6", None),
        row("7", "8", "9", None), row(("C", R), "0", ("OK", Gr), None)]),
    ("02-calculator", "Calculator", [
        row("7", "8", "9", ("÷", F)), row("4", "5", "6", ("×", F)),
        row("1", "2", "3", ("-", F)), row(("C", R), "0", ("=", Gr), ("+", F))]),
    ("03-matrix-4x4", "Classic 4x4 keypad", [
        row("1", "2", "3", ("A", F)), row("4", "5", "6", ("B", F)),
        row("7", "8", "9", ("C", F)), row(("*", F), "0", ("#", F), ("D", F))]),
    ("04-hex", "Hexadecimal 0-F", [
        row("0", "1", "2", "3"), row("4", "5", "6", "7"),
        row("8", "9", ("A", F), ("B", F)), row(("C", F), ("D", F), ("E", F), ("F", F))]),
    ("05-phone-menu", "Phone + menu", [
        row("1", "2", "3", ("@up", F)), row("4", "5", "6", ("@down", F)),
        row("7", "8", "9", ("ESC", R)), row(("*", F), "0", ("#", F), ("OK", Gr))]),
    ("06-alarm-lock", "Alarm / door lock", [
        row("1", "2", "3", ("ARM", F)), row("4", "5", "6", ("STAY", F)),
        row("7", "8", "9", ("OFF", F)), row(("C", R), "0", ("OK", Gr), ("SOS", R))]),
    ("07-smart-home", "Smart home", [
        row("L1", "L2", "L3", "L4"), row("FAN", "AC", "TV", "PLUG"),
        row(("OPEN", F), ("STOP", F), ("CLOSE", F), ("NIGHT", F)),
        row("SCENE\n1", "SCENE\n2", ("ALL\nON", Gr), ("ALL\nOFF", R))]),
    ("08-gamepad", "Game pad", [
        row(("L1", F), ("@up", F), ("R1", F), "X"), row(("@left", F), ("OK", Gr), ("@right", F), "Y"),
        row(("L2", F), ("@down", F), ("R2", F), "A"), row(("SEL", F), ("HOME", F), ("START", F), "B")]),
    ("09-media", "Media remote", [
        row(("@prev", F), ("@playpause", Gr), ("@next", F), ("@stop", F)),
        row(("VOL-", F), ("MUTE", F), ("VOL+", F), ("@rec", R)),
        row("1", "2", "3", "4"),
        row(("BACK", F), ("HOME", F), ("MENU", F), ("PWR", R))]),
    ("10-elevator", "Elevator panel", [
        row("9", "10", "11", "12"), row("5", "6", "7", "8"),
        row("1", "2", "3", "4"), row("G", ("OPEN", F), ("CLOSE", F), ("ALARM", R))]),
    ("11-music", "Music notes", [
        row("C", "D", "E", "F"), row("G", "A", "B", "C'"),
        row(("C#", F), ("D#", F), ("F#", F), ("G#", F)), row(("A#", F), ("REC", R), ("PLAY", Gr), ("STOP", F))]),
]


def draw_icon(c, name, cx, cy, s, col):
    """Simple vector icons (mm coordinates, centered)."""
    c.setFillColor(HexColor(col)); c.setStrokeColor(HexColor(col))
    u = s * 0.18

    def tri(points):
        p = c.beginPath(); p.moveTo(points[0][0] * mm, points[0][1] * mm)
        for x, y in points[1:]:
            p.lineTo(x * mm, y * mm)
        p.close(); c.drawPath(p, stroke=0, fill=1)

    if name == "up":     tri([(cx - u, cy - u * .7), (cx + u, cy - u * .7), (cx, cy + u)])
    elif name == "down": tri([(cx - u, cy + u * .7), (cx + u, cy + u * .7), (cx, cy - u)])
    elif name == "left": tri([(cx + u * .7, cy - u), (cx + u * .7, cy + u), (cx - u, cy)])
    elif name == "right": tri([(cx - u * .7, cy - u), (cx - u * .7, cy + u), (cx + u, cy)])
    elif name == "stop": c.rect((cx - u * .8) * mm, (cy - u * .8) * mm, 1.6 * u * mm, 1.6 * u * mm, stroke=0, fill=1)
    elif name == "rec":  c.circle(cx * mm, cy * mm, u * .9 * mm, stroke=0, fill=1)
    elif name == "next":
        tri([(cx - u, cy - u * .8), (cx - u, cy + u * .8), (cx + u * .4, cy)])
        c.rect((cx + u * .45) * mm, (cy - u * .8) * mm, u * .35 * mm, 1.6 * u * mm, stroke=0, fill=1)
    elif name == "prev":
        tri([(cx + u, cy - u * .8), (cx + u, cy + u * .8), (cx - u * .4, cy)])
        c.rect((cx - u * .8) * mm, (cy - u * .8) * mm, u * .35 * mm, 1.6 * u * mm, stroke=0, fill=1)
    elif name == "playpause":
        tri([(cx - u * 1.2, cy - u * .8), (cx - u * 1.2, cy + u * .8), (cx + u * .1, cy)])
        c.rect((cx + u * .35) * mm, (cy - u * .8) * mm, u * .3 * mm, 1.6 * u * mm, stroke=0, fill=1)
        c.rect((cx + u * .9) * mm, (cy - u * .8) * mm, u * .3 * mm, 1.6 * u * mm, stroke=0, fill=1)


def draw_label(c, text, cx, cy, s, col):
    c.setFillColor(HexColor(col))
    lines = text.split("\n")
    maxw = s * 0.82 * mm
    fs = 18 if len(text) == 1 else 14
    for ln in lines:
        while fs > 5 and stringWidth(ln, "Helvetica-Bold", fs) > maxw:
            fs -= 0.5
    if len(lines) > 1:
        fs = min(fs, 9)
    c.setFont("Helvetica-Bold", fs)
    lh = fs * 1.1
    y0 = cy * mm + (len(lines) - 1) * lh / 2 - fs * 0.35
    for i, ln in enumerate(lines):
        c.drawCentredString(cx * mm, y0 - i * lh, ln)


def overlay(c, x0, y0, grid, theme, title):
    c.setStrokeColor(HexColor("#000000")); c.setLineWidth(0.3); c.setDash(2, 1.5)
    c.rect(x0 * mm, y0 * mm, W * mm, H * mm); c.setDash()
    top = H - M - 4 * P
    c.setFillColor(HexColor("#888888")); c.setFont("Helvetica", 5)
    c.drawCentredString((x0 + W / 2) * mm, (y0 + H - top / 2 + 1) * mm, f"TTP229 - {title}")
    c.drawCentredString((x0 + W / 2) * mm, (y0 + H - top / 2 - 2.5) * mm, "pins side (top)")
    for r in range(4):
        for col in range(4):
            cell = grid[r][col]
            kx = x0 + M + col * P + G / 2
            ky = y0 + M + (3 - r) * P + G / 2
            if cell is None:
                c.setStrokeColor(HexColor("#cccccc")); c.setLineWidth(0.2)
                c.roundRect(kx * mm, ky * mm, S * mm, S * mm, 1.2 * mm, stroke=1, fill=0)
                continue
            label, style = cell
            fill, txt = theme if style == "n" else FIXED[style]
            c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#111111")); c.setLineWidth(0.4)
            c.roundRect(kx * mm, ky * mm, S * mm, S * mm, 1.2 * mm,
                        stroke=1 if fill.upper() == "#FFFFFF" else 0, fill=1)
            cx, cy = kx + S / 2, ky + S / 2
            if label.startswith("@"):
                draw_icon(c, label[1:], cx, cy, S, txt)
            else:
                draw_label(c, label, cx, cy, S, txt)


def ruler(c, pw, title):
    c.setFont("Helvetica-Bold", 12); c.setFillColor(HexColor("#000000"))
    c.drawString(15 * mm, (297 - 15) * mm, f"TTP229 keypad overlay - {title}")
    c.setFont("Helvetica", 8)
    c.drawString(15 * mm, (297 - 21) * mm,
                 "Print on A4 at 100% (Actual size, no 'Fit to page'). Board 49.3 x 64.5 mm. "
                 "Pins at top. Cut on dashed line.")
    ry = 28
    c.setStrokeColor(HexColor("#000000")); c.setLineWidth(0.4)
    c.line(15 * mm, ry * mm, 115 * mm, ry * mm)
    c.setFont("Helvetica", 6)
    for i in range(101):
        t = 3 if i % 10 == 0 else (2 if i % 5 == 0 else 1)
        c.line((15 + i) * mm, ry * mm, (15 + i) * mm, (ry + t) * mm)
        if i % 10 == 0:
            c.drawCentredString((15 + i) * mm, (ry + 4) * mm, str(i))
    c.setFont("Helvetica", 8)
    c.drawString(15 * mm, (ry - 6) * mm, "Check: this ruler must measure exactly 100 mm. If not, printer scaling is wrong.")


XS = [15, 15 + W + 12, 15 + 2 * (W + 12)]
YS = [297 - 30 - H, 297 - 30 - 2 * H - 12, 297 - 30 - 3 * H - 24]


def main():
    os.makedirs("layouts", exist_ok=True)
    for slug, title, grid in LAYOUTS:
        c = canvas.Canvas(f"layouts/{slug}.pdf", pagesize=A4)
        c.setTitle(f"TTP229 keypad overlay - {title}")
        ruler(c, 210, title)
        k = 0
        for yy in YS[:2]:
            for xx in XS:
                overlay(c, xx, yy, grid, THEMES[k], title); k += 1
        c.showPage(); c.save()

    # Sampler: one copy of every layout (blue theme), 9 per page
    c = canvas.Canvas("all_layouts.pdf", pagesize=A4)
    c.setTitle("TTP229 keypad overlay - all layouts")
    for start in range(0, len(LAYOUTS), 9):
        ruler(c, 210, "all layouts")
        for i, (slug, title, grid) in enumerate(LAYOUTS[start:start + 9]):
            overlay(c, XS[i % 3], YS[i // 3], grid, THEMES[2], title)
        c.showPage()
    c.save()


if __name__ == "__main__":
    main()
