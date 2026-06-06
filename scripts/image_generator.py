import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw


COLOR_THEMES = [
    {"bg1": (26, 67, 53), "bg2": (46, 125, 96), "accent": (212, 175, 55)},
    {"bg1": (13, 52, 89), "bg2": (33, 97, 143), "accent": (255, 193, 7)},
    {"bg1": (62, 39, 35), "bg2": (106, 73, 65), "accent": (212, 175, 55)},
    {"bg1": (27, 27, 27), "bg2": (66, 66, 66), "accent": (255, 215, 0)},
    {"bg1": (1, 87, 106), "bg2": (0, 131, 143), "accent": (255, 235, 59)},
    {"bg1": (46, 27, 57), "bg2": (74, 42, 89), "accent": (212, 175, 55)},
]


def _gradient(draw: ImageDraw, w: int, h: int, c1: tuple, c2: tuple):
    for y in range(h):
        r = y / h
        draw.line([(0, y), (w, y)],
                   fill=(int(c1[0]*(1-r)+c2[0]*r),
                         int(c1[1]*(1-r)+c2[1]*r),
                         int(c1[2]*(1-r)+c2[2]*r)))


def _hexagons(draw: ImageDraw, w: int, h: int, color: tuple, alpha: int = 25):
    s = 80
    for row in range(h // s + 2):
        for col in range(w // s + 2):
            ox = col * s + (s // 2 if row % 2 else 0)
            oy = row * s
            r = s // 3
            draw.regular_polygon((ox, oy, r), 6, fill=(*color, alpha), outline=None)


def _circles(draw: ImageDraw, w: int, h: int, color: tuple, alpha: int = 10):
    for i in range(5):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(40, 120)
        draw.ellipse([x - r, y - r, x + r, y + r], outline=(*color, alpha), width=2)


def _crescent(draw: ImageDraw, cx: int, cy: int, r: int, color: tuple, alpha: int = 15):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, alpha))
    off = r // 3
    draw.ellipse([cx - r + off, cy - r - off, cx + r + off, cy + r - off], fill=(0, 0, 0, 0))


def _stars(draw: ImageDraw, w: int, h: int, color: tuple, alpha: int = 100):
    for i in range(8):
        x = random.randint(0, w)
        y = random.randint(0, h)
        s = random.randint(3, 8)
        draw.regular_polygon((x, y, s), 4, rotation=30, fill=(*color, alpha))


def _pick_theme(prompt: str) -> dict:
    p = prompt.lower()
    if any(w in p for w in ["quran", "surah", "ayat", "book", "read", "recite", "learn"]):
        return {"bg1": (62, 39, 35), "bg2": (106, 73, 65), "accent": (212, 175, 55)}
    if any(w in p for w in ["pray", "fajr", "namaz", "salah", "wudu", "mosque", "dua"]):
        return {"bg1": (13, 52, 89), "bg2": (33, 97, 143), "accent": (255, 193, 7)}
    if any(w in p for w in ["hajj", "umrah", "kaaba", "mecca", "pilgrim"]):
        return {"bg1": (27, 27, 27), "bg2": (50, 50, 50), "accent": (255, 215, 0)}
    if any(w in p for w in ["fast", "ramadan", "iftar", "suhoor"]):
        return {"bg1": (26, 67, 53), "bg2": (46, 125, 96), "accent": (212, 175, 55)}
    if any(w in p for w in ["nature", "garden", "water", "sky", "peace", "calm"]):
        return {"bg1": (1, 87, 106), "bg2": (0, 131, 143), "accent": (255, 235, 59)}
    return random.choice(COLOR_THEMES)


def generate_image(prompt: str, output_path: str, alt_text: str = "") -> str:
    w, h = 1200, 630
    theme = _pick_theme(prompt)

    img = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(img)

    _gradient(draw, w, h, theme["bg1"], theme["bg2"])

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    _hexagons(od, w, h, theme["accent"], 25)
    _circles(od, w, h, theme["accent"], 8)
    _stars(od, w, h, (255, 255, 255), 80)
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    _crescent(draw, w // 2 - 50, h // 2, 220, theme["accent"], 12)

    accent_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ad = ImageDraw.Draw(accent_overlay)
    ad.rectangle([0, h - 4, w, h], fill=(*theme["accent"], 150))
    ad.rectangle([0, 0, w, 4], fill=(*theme["accent"], 150))
    img = Image.alpha_composite(img, accent_overlay)

    if output_path.endswith(".png"):
        img.save(output_path, "PNG")
    else:
        img.convert("RGB").save(output_path, "JPEG", quality=92)
    return output_path


def generate_and_save(prompt: str, alt_text: str, index: int = 1) -> tuple:
    ext = "png"
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_images")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"featured_{index}.{ext}")
    generate_image(prompt, out, alt_text)
    return out, alt_text


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "How to pray Fajr on time every day"
    a = sys.argv[2] if len(sys.argv) > 2 else "Namaz"
    path, _ = generate_and_save(p, a)
    print(f"Image saved to: {path}")
