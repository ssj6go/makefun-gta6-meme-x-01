#!/usr/bin/env python3
"""Build the GTA 6 meme for make.fun bounty gta6-meme-x-01.

Concept: "Waited 13 years for GTA 6. My agent won $100 just by waiting."
The make.fun ghost (the real press-kit mark) IS the Vice City sun: it sits
where the background's sun glows, so the brand is worked into the scene
instead of pasted on as a sticker.

Inputs:
  bg.png            AI-generated Vice City sunset (no text), committed here.
  mark-1024.png     the real make.fun ghost mark, downloaded from the press
                    kit at https://make.fun/press/mark-1024.png (cached in
                    the system temp dir; never committed to the repo).

Output: meme.png, 1024x1024.
"""

import os
import sys
import tempfile
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MARK_URL = "https://make.fun/press/mark-1024.png"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SIZE = 1024

TOP_LINES = ["WAITED 13 YEARS", "FOR GTA 6"]
BOTTOM_LINES = ["MY AGENT WON $100", "JUST BY WAITING"]


def get_mark():
    cache = os.path.join(tempfile.gettempdir(), "makefun-mark-1024.png")
    for _ in range(3):
        if not os.path.exists(cache):
            try:
                urllib.request.urlretrieve(MARK_URL, cache)
            except Exception:
                if os.path.exists(cache):
                    os.remove(cache)
                continue
        try:
            im = Image.open(cache)
            im.load()
            if im.size == (1024, 1024):
                return im.convert("RGBA")
        except Exception:
            pass
        os.remove(cache)
    raise RuntimeError("could not download a valid make.fun mark")


def fit_font(draw, text, max_width, start_size):
    size = start_size
    while size > 20:
        font = ImageFont.truetype(FONT_PATH, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(FONT_PATH, 20)


def draw_caption(draw, lines, top_y, max_width, start_size, line_gap):
    """Draw centred white-on-black-outline caption lines. Returns bottom y."""
    y = top_y
    for text in lines:
        font = fit_font(draw, text, max_width, start_size)
        w = draw.textlength(text, font=font)
        x = (SIZE - w) / 2
        stroke = max(3, font.size // 12)
        draw.text((x, y), text, font=font, fill="white",
                  stroke_width=stroke, stroke_fill="black")
        y += font.size + line_gap
    return y


def main():
    bg_path = os.path.join(SCRIPT_DIR, "bg.png")
    out_path = os.path.join(SCRIPT_DIR, "meme.png")

    img = Image.open(bg_path).convert("RGB").resize((SIZE, SIZE),
                                                   Image.LANCZOS)

    # The make.fun ghost as the Vice City sun: the background's sun glows at
    # about (515, 510), so the mark sits exactly there, larger than the sun
    # disc, with a soft magenta glow behind it to melt it into the sunset.
    mark = get_mark()
    mark_size = 450
    mark = mark.resize((mark_size, mark_size), Image.LANCZOS)
    cx, cy = 515, 505
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([cx - 310, cy - 310, cx + 310, cy + 310],
                      fill=(255, 0, 128, 140))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img = img.convert("RGBA")
    img.alpha_composite(glow)
    img.alpha_composite(mark, (cx - mark_size // 2, cy - mark_size // 2))
    img = img.convert("RGB")

    draw = ImageDraw.Draw(img)
    draw_caption(draw, TOP_LINES, top_y=36, max_width=940,
                 start_size=72, line_gap=6)
    # Bottom caption: measure first so it sits just above the lower edge.
    bottom_font = fit_font(draw, BOTTOM_LINES[0], 940, 64)
    bottom_h = 2 * (bottom_font.size + 6)
    draw_caption(draw, BOTTOM_LINES, top_y=SIZE - 40 - bottom_h,
                 max_width=940, start_size=64, line_gap=6)

    img.save(out_path, "PNG")
    print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    sys.exit(main())
