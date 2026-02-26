"""Generate webshare-og.png — 1200×630 Open Graph image for webshare-demo.html."""
from PIL import Image, ImageDraw
import math, os

W, H = 1200, 630
OUT = os.path.join(os.path.dirname(__file__), "webshare-og.png")

img = Image.new("RGB", (W, H))
px  = img.load()

# ── Background: vertical gradient #0f0f13 → #1e1b2e ─────────────────────────
bg_top    = (0x0f, 0x0f, 0x13)
bg_bottom = (0x1e, 0x1b, 0x2e)
for y in range(H):
    t = y / (H - 1)
    r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * t)
    g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * t)
    b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)

# ── Radial purple glow centred at (600, 265) ────────────────────────────────
CX, CY, RADIUS = W // 2, 265, 420
for y in range(H):
    for x in range(W):
        dist = math.hypot(x - CX, y - CY)
        if dist < RADIUS:
            alpha = max(0.0, 1.0 - dist / RADIUS)
            # purple-to-blue glow: rgba(124,58,237,0.38) fading out
            strength = alpha ** 1.6 * 0.38
            base = px[x, y]
            glow_r = int(124 * 0.6 + 96 * 0.4)   # blend purple + blue
            glow_g = int( 58 * 0.6 + 165 * 0.4)
            glow_b = int(237 * 0.6 + 250 * 0.4)
            px[x, y] = (
                int(base[0] * (1 - strength) + glow_r * strength),
                int(base[1] * (1 - strength) + glow_g * strength),
                int(base[2] * (1 - strength) + glow_b * strength),
            )

draw = ImageDraw.Draw(img)

# ── Try to load a system font, fall back to Pillow default ──────────────────
def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    from PIL import ImageFont
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title    = load_font(74, bold=True)
font_subtitle = load_font(34)

# ── Helper: horizontally centred text ───────────────────────────────────────
def centre_text(draw, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw   = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=fill)

# ── Title: horizontal gradient purple → blue via per-pixel mask ─────────────
# Draw title on a temp image then tint it left→right
title_text = "Web Share API Demo"
title_y    = 220

title_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
title_draw  = ImageDraw.Draw(title_layer)
centre_text(title_draw, title_y, title_text, font_title, (255, 255, 255, 255))

tint_layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
tint_px     = tint_layer.load()
title_px    = title_layer.load()

purple = (167, 139, 250)
blue   = ( 96, 165, 250)
for x in range(W):
    t = x / (W - 1)
    tr = int(purple[0] + (blue[0] - purple[0]) * t)
    tg = int(purple[1] + (blue[1] - purple[1]) * t)
    tb = int(purple[2] + (blue[2] - purple[2]) * t)
    for y in range(H):
        a = title_px[x, y][3]
        if a > 0:
            tint_px[x, y] = (tr, tg, tb, a)

img = Image.alpha_composite(img.convert("RGBA"), tint_layer).convert("RGB")
draw = ImageDraw.Draw(img)

# ── Subtitle ─────────────────────────────────────────────────────────────────
centre_text(draw, 318, "Native sharing + social media fallbacks",
            font_subtitle, (255, 255, 255, 133))

# ── Save ─────────────────────────────────────────────────────────────────────
img.save(OUT, "PNG", optimize=True)
print(f"Saved {OUT}  ({os.path.getsize(OUT) // 1024} KB)")
