"""Image token-cost calculator. Standard library only.

Shows how patch size, resolution, tiling, and pooling change the number of
visual tokens, and what that costs at an ILLUSTRATIVE price per million
input tokens. Real providers publish their own formulas; verify them.
"""
import math

PRICE_PER_MTOK = 3.00  # illustrative USD per million input tokens


def vit_tokens(w, h, patch=14):
    """Tokens from a plain ViT: one per patch (ceil on each axis)."""
    return math.ceil(w / patch) * math.ceil(h / patch)


def pooled_tokens(w, h, patch=14, pool=2):
    """ViT followed by pool x pool merging of neighbouring patch tokens."""
    return math.ceil(math.ceil(w / patch) / pool) * math.ceil(math.ceil(h / patch) / pool)


def tiled_tokens(w, h, tile=336, patch=14, pool=1, thumbnail=True):
    """AnyRes-style tiling: grid of tile x tile crops plus one thumbnail."""
    gx, gy = math.ceil(w / tile), math.ceil(h / tile)
    per_tile = (tile // patch // pool) ** 2
    return gx * gy * per_tile + (per_tile if thumbnail else 0), gx * gy


def area_tokens(w, h, divisor=750):
    """Area-proportional rule of thumb: tokens ~ w*h/divisor."""
    return math.ceil(w * h / divisor)


def usd(tokens, n_images=1):
    return tokens * n_images * PRICE_PER_MTOK / 1e6


if __name__ == "__main__":
    print("== Plain ViT, patch 14 ==")
    for w, h in [(224, 224), (336, 336), (448, 448), (768, 768), (1024, 768), (1920, 1080)]:
        print(f"{w:>4}x{h:<4} -> {vit_tokens(w, h):>6} tokens")

    print("\n== ViT patch 14 + 2x2 pooling ==")
    for w, h in [(336, 336), (768, 768), (1920, 1080)]:
        print(f"{w:>4}x{h:<4} -> {pooled_tokens(w, h):>6} tokens")

    print("\n== AnyRes tiling, tile 336, patch 14, no pooling, with thumbnail ==")
    for w, h in [(336, 336), (672, 672), (1024, 768), (1920, 1080), (3840, 2160)]:
        t, tiles = tiled_tokens(w, h)
        print(f"{w:>4}x{h:<4} -> {tiles:>3} tiles, {t:>6} tokens")

    print("\n== Area rule w*h/750 ==")
    for w, h in [(768, 768), (1568, 1568), (1920, 1080)]:
        print(f"{w:>4}x{h:<4} -> {area_tokens(w, h):>6} tokens")

    print("\n== Cost of 1,000,000 images at illustrative $3.00 per M tokens ==")
    for label, tok in [("768x768 area rule", area_tokens(768, 768)),
                       ("1920x1080 tiled", tiled_tokens(1920, 1080)[0]),
                       ("3840x2160 tiled", tiled_tokens(3840, 2160)[0])]:
        print(f"{label:<20} {tok:>6} tok/img -> ${usd(tok, 1_000_000):>10,.0f}")

    print("\n== Context budget: 128k window, 4k reserved for text+answer ==")
    for tok in [787, 2765, 14400]:
        print(f"{tok:>5} tok/img -> {(128_000 - 4_000) // tok:>4} images fit")
