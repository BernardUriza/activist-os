#!/usr/bin/env python3
"""Derive the full Activist OS branding collection from the two Gemini masters.

Masters (never overwritten): activist-os-logo-v1.png, activist-os-icon-v1.png.
Re-run after regenerating a master:  python3 web/branding/derive.py
"""

from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
LOGO = Image.open(HERE / "activist-os-logo-v1.png").convert("RGBA")
ICON = Image.open(HERE / "activist-os-icon-v1.png").convert("RGBA")

CHARCOAL = (23, 23, 27)
PURPLE_TINT = (76, 60, 110)


def cover_fit(img, w, h, zoom=1.0):
    """object-cover into (w, h) with optional zoom, center-cropped."""
    scale = max(w / img.width, h / img.height) * zoom
    rw, rh = int(img.width * scale), int(img.height * scale)
    img = img.resize((rw, rh), Image.Resampling.LANCZOS)
    x, y = (rw - w) // 2, (rh - h) // 2
    return img.crop((x, y, x + w, y + h))


def ramp_mask(w, h, stops, horizontal=False):
    """Gradient alpha mask from (position, opacity) stops, values 0..1."""
    n = w if horizontal else h
    line = Image.new("L", (n, 1))
    px = line.load()
    assert px is not None
    for i in range(n):
        t = i / (n - 1)
        for (p0, a0), (p1, a1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                f = (t - p0) / (p1 - p0) if p1 > p0 else 0
                px[i, 0] = int(255 * (a0 + (a1 - a0) * f))
                break
    return line.resize((w, h)) if horizontal else line.rotate(-90, expand=True).resize((w, h))


def shade(img, stops, horizontal=False, color=CHARCOAL):
    """Composite a gradient shadow layer over img (rancho-studio overlays)."""
    layer = Image.new("RGBA", img.size, color + (255,))
    layer.putalpha(ramp_mask(img.width, img.height, stops, horizontal))
    return Image.alpha_composite(img, layer)


def background(w, h):
    """The 'render entre sombras' treatment, baked."""
    bg = cover_fit(ICON, w, h, zoom=1.25)            # scale-125 + object-cover
    bg = bg.filter(ImageFilter.GaussianBlur(3))      # blur-[3px]
    bg = ImageEnhance.Brightness(bg).enhance(0.45)   # opacity-40 over dark
    # gradient-to-b from-charcoal/80 via-charcoal/40 to-charcoal/90
    bg = shade(bg, [(0.0, 0.8), (0.5, 0.4), (1.0, 0.9)])
    # gradient-to-r from-charcoal via-charcoal/10 to-charcoal
    bg = shade(bg, [(0.0, 1.0), (0.5, 0.1), (1.0, 1.0)], horizontal=True)
    # warm/purple tint at 20% so the band belongs to the palette
    tint = Image.new("RGBA", bg.size, PURPLE_TINT + (51,))
    return Image.alpha_composite(bg, tint)


def keyed(img, threshold=42, boost=2.4):
    """Knock out the dark background: alpha from luminance, RGB preserved."""
    lum = img.convert("L").point(lambda v: 0 if v < threshold else min(255, int((v - threshold) * boost)))
    out = img.copy()
    out.putalpha(lum)
    return out


def social_card(w, h, logo_frac=0.52):
    """Brand lockup left, emblem art bleeding off the right edge."""
    card = background(w, h)
    # quiet the bg so the lockup owns the card (flatten the center flame)
    card = Image.alpha_composite(card, Image.new("RGBA", card.size, CHARCOAL + (140,)))
    # emblem bleeding off the right, brighter than the bg wash
    eh = int(h * 1.15)
    emblem = keyed(ICON.resize((eh, eh), Image.Resampling.LANCZOS))
    fade = ramp_mask(eh, eh, [(0.0, 0.0), (0.45, 1.0), (1.0, 1.0)], horizontal=True)
    emblem.putalpha(ImageChops.multiply(emblem.split()[3], fade))
    card.alpha_composite(emblem, (w - int(eh * 0.78), (h - eh) // 2))
    # full lockup (emblem + wordmark + tagline) on the left, background knocked out
    lw = int(w * logo_frac)
    lh = int(LOGO.height * (lw / LOGO.width))
    lock = keyed(LOGO.resize((lw, lh), Image.Resampling.LANCZOS))
    pos = (int(w * 0.05), (h - lh) // 2)
    card.alpha_composite(lock, pos)
    card.alpha_composite(lock, pos)  # double pass for punch over the dark wash
    return card


def main():
    out = {}

    # ── Icons ──
    for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")]:
        ICON.resize((size, size), Image.Resampling.LANCZOS).save(HERE / name)
        out[name] = (size, size)

    ico = ICON.resize((48, 48), Image.Resampling.LANCZOS).convert("RGB")
    ico.save(HERE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    out["favicon.ico"] = (48, 48)

    # ── Logo set ──
    LOGO.save(HERE / "logo-full.png")
    out["logo-full.png"] = LOGO.size
    ICON.save(HERE / "emblem.png")
    out["emblem.png"] = ICON.size

    # mono white: luminance -> alpha (masters are light-on-dark, no alpha)
    lum = LOGO.convert("L")
    lum = lum.point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 1.4)))
    white = Image.new("L", LOGO.size, 255)
    mono = Image.merge("RGBA", (white, white, white, lum))
    mono.save(HERE / "logo-white.png")
    out["logo-white.png"] = mono.size

    # ── Social cards ──
    for w, h, name in [(1200, 630, "og-image.png"), (1200, 600, "twitter-card.png"),
                       (1584, 396, "linkedin-banner.png")]:
        social_card(w, h, logo_frac=0.40 if h < 500 else 0.52).convert("RGB").save(HERE / name)
        out[name] = (w, h)

    # ── Hero backgrounds ──
    for w, h, name in [(1920, 1080, "bg-hero-1920.png"), (3440, 1440, "bg-hero-3440.png")]:
        background(w, h).convert("RGB").save(HERE / name)
        out[name] = (w, h)

    for name, (w, h) in out.items():
        print(f"{name}\t{w}x{h}")


if __name__ == "__main__":
    main()
