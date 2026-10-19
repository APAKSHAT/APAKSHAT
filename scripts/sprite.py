"""Static mascot sprite as a half-pixel grid: {(x, y): '#rrggbb'}.

Each logical pixel is 2x2 sub-cells so the eye glint (a half pixel) survives.
Mirrors the idle pose of the animated mascot.svg (eye centred, arms down)."""

HALF = [
    "....OO......",
    "...OHHO.....",
    "...OHHO.....",
    "....OHHO....",
    ".....OOOOOOO",
    "....OBBBBBBB",
    "...OBBBBBOOO",
    "...OBBBBOWWW",
    "..OBBBBOWWWW",
    "..OBBBBOWWWW",
    "..OBBBBOWWWW",
    "..OBBBBOWWWW",
    "..OBBBBBOWWW",
    "..OBBBBBBOOO",
    "..OBBPPBBBBB",
    "..OBBBBBKBBB",
    "..OBBBBBBKWK",
    "...OBBBBBBBB",
    "....OBBBBBBB",
    ".....OOOOOOO",
    "....OFFFO...",
    "....OOOOO...",
]
C = {
    "O": "#4a37b8", "E": "#1d1442", "L": "#b9a6ff", "M": "#8467f5", "D": "#5a3fd6",
    "W": "#f4f1ff", "H": "#2cb67d", "P": "#ff7eb6", "K": "#1d1442", "F": "#6a55e8",
}


def logical():
    """{(x, y): color} in logical pixels, x shifted by +1 so the left arm sits at x=0."""
    grid = [r + r[::-1] for r in HALF]
    W, H = len(grid[0]), len(grid)
    at = lambda x, y: grid[y][x] if 0 <= x < W and 0 <= y < H else "."
    near_w = lambda x, y: any(at(x + dx, y + dy) == "W" for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    def shade(x, y):
        edge = lambda c: c in ".O"
        if (edge(at(x, y - 1)) or edge(at(x - 1, y))) and (x < 13 or y < 7):
            return "L"
        if (edge(at(x, y + 1)) or edge(at(x + 1, y))) and (x > 10 or y > 15):
            return "D"
        return "D" if y >= 17 else "M"

    px = {}
    for y in range(H):
        for x in range(W):
            c = grid[y][x]
            if c == ".":
                continue
            if c == "O" and near_w(x, y):
                c = "E"
            px[(x + 1, y)] = C[shade(x, y)] if c == "B" else C[c]

    # arms
    for side in (0, 1):
        fx = (lambda x: x) if side == 0 else (lambda x: W - 1 - x)
        for x, y in [(0, 11), (1, 11), (-1, 12), (-1, 13), (-1, 14), (0, 15), (1, 15)]:
            px[(fx(x) + 1, y)] = C["O"]
        for x, y in [(0, 12), (1, 12), (0, 13), (1, 13), (0, 14), (1, 14)]:
            px[(fx(x) + 1, y)] = C["L"] if y == 12 else C["M"]

    # iris + pupil
    for x, y in [(11, 8), (12, 8), (11, 11), (12, 11)] + [(xx, yy) for xx in range(10, 14) for yy in (9, 10)]:
        px[(x + 1, y)] = "#2cb67d"
    px[(10 + 1, 8)] = "#1a9e66"
    for x, y in [(11, 9), (12, 9), (11, 10), (12, 10)]:
        px[(x + 1, y)] = "#0f0e17"
    return px, W + 2, H


def subpixels():
    """2x grid with the half-pixel eye glint."""
    px, W, H = logical()
    sub = {}
    for (x, y), c in px.items():
        for dx in (0, 1):
            for dy in (0, 1):
                sub[(2 * x + dx, 2 * y + dy)] = c
    sub[(2 * 13, 2 * 9)] = "#fffffe"  # glint: top-left quarter of logical (12, 9), shifted +1
    return sub, 2 * W, 2 * H


if __name__ == "__main__":
    px, W, H = logical()
    for y in range(H):
        print("".join("#" if (x, y) in px else "." for x in range(W)))
