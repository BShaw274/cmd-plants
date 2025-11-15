#!/usr/bin/env python3
"""Flowers generator (merged and cleaned).

Features:
- All improved styles: round, star, tulip, sunflower, cherry blossom
- Tree styles: pine, broad, bonsai, cherry blossom tree
- ANSI color palettes and Windows fallback (optional colorama)
- Horizontal garden layout with auto-fit and ground alignment (plants bottom-aligned)
- Flowers use green stalks only; trees use brown wider trunks
"""
from __future__ import annotations

import argparse
import os
import random
import re
import shutil
import sys
from typing import List, Tuple

try:
    # optional Windows color support
    if os.name == "nt":
        import colorama

        colorama.init()
except Exception:
    pass

PETAL_CHARS = ["*", "o", "@", "O", "0", "+", "x", "X"]
CENTER_CHARS = ["@", "*", "O", "."]
STEM_CHAR = "|"  # flowers use a plain stalk

# ANSI color map
ANSI = {
    "reset": "\x1b[0m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "bright_yellow": "\x1b[93m",
    "bright_green": "\x1b[92m",
    "brown": "\x1b[38;5;94m",
}


def _make_round_flower(size: int, rng: random.Random) -> List[str]:
    radius = 1 + size
    width_scale = 2
    petal = rng.choice(PETAL_CHARS)
    center = rng.choice(CENTER_CHARS)
    lines: List[str] = []
    for y in range(-radius, radius + 1):
        row = []
        for x in range(-width_scale * radius, width_scale * radius + 1):
            dx = x / float(width_scale)
            d2 = dx * dx + y * y
            noise = rng.random() * 0.6
            if d2 <= (radius + 0.25 - noise) ** 2:
                if abs(x) <= 1 and abs(y) <= 1:
                    row.append(center)
                else:
                    row.append(petal)
            else:
                row.append(" ")
        lines.append("".join(row).rstrip())
    stem_height = rng.randint(1 + size, 2 + 2 * size)
    stem_col = len(lines[0]) // 2
    for _ in range(stem_height):
        lines.append(" " * stem_col + STEM_CHAR)
    return lines


def _make_star_flower(size: int, rng: random.Random) -> List[str]:
    petal = rng.choice(PETAL_CHARS)
    center = rng.choice(CENTER_CHARS)
    s = size
    lines = [
        " " * (2 * s) + petal,
        " " * s + petal + " " * (2 * s - 1) + petal,
        petal + " " * (4 * s - 1) + petal,
        " " * s + petal + " " * (2 * s - 1) + petal,
        " " * (2 * s) + center,
    ]
    for _ in range(1 + s + rng.randint(0, s)):
        lines.append(" " * (2 * s) + STEM_CHAR)
    return lines


def _make_tulip(size: int, rng: random.Random) -> List[str]:
    petal = rng.choice(PETAL_CHARS)
    center = rng.choice(CENTER_CHARS)
    s = size
    lines = [
        " " * (1 + s) + petal + " " * s + petal,
        " " * s + petal + " " * (1 + s) + center + " " * s + petal,
        petal + " " * (3 + s) + petal,
    ]
    leaves = rng.choice(["<>", "/\\", "()", "~~"])
    lines.append(" " * (1 + s) + leaves)
    for _ in range(1 + s + rng.randint(0, 2)):
        lines.append(" " * (2 + s) + STEM_CHAR)
    return lines


def _make_sunflower(size: int, rng: random.Random) -> List[str]:
    petal = rng.choice(["0", "O", "*", "@"])
    center = rng.choice(["@", "0", "O"])
    s = size
    lines = [
        " " * (2 + s) + petal * (3 + s),
        " " * (1 + s) + petal + " " * (1 + s) + center + " " * (1 + s) + petal,
        petal + " " * (3 + s) + petal,
    ]
    for _ in range(2 + s):
        lines.append(" " * (2 + s) + STEM_CHAR)
    return lines


def _make_cherry_flower(size: int, rng: random.Random) -> List[str]:
    petal = rng.choice(["o", "✿", "❀"]) if os.name != "nt" else rng.choice(["o", "*"])
    center = rng.choice([".", "@"])
    s = size
    lines = [
        " " * (1 + s) + petal + " " + petal,
        " " * s + petal + center + petal,
        petal + " " * (1 + s) + petal,
    ]
    for _ in range(1 + s):
        lines.append(" " * (2 + s) + STEM_CHAR)
    return lines


def random_flower(size: int = 1, seed: int | None = None, rng: random.Random | None = None) -> Tuple[List[str], str]:
    if rng is None:
        rng = random.Random(seed)
    kind = rng.choice(["round", "star", "tulip", "sunflower", "cherry"])
    if kind == "round":
        return _make_round_flower(size, rng), kind
    if kind == "star":
        return _make_star_flower(size, rng), kind
    if kind == "sunflower":
        return _make_sunflower(size, rng), kind
    if kind == "cherry":
        return _make_cherry_flower(size, rng), kind
    return _make_tulip(size, rng), kind


def _make_pine_tree(size: int, rng: random.Random) -> List[str]:
    s = max(1, size)
    lines: List[str] = []
    # foliage layers
    for layer in range(3):
        width = 1 + 2 * (layer + s)
        for row in range(width):
            pad = (4 * s + 2) - row
            foliage = "^" * (1 + 2 * row)
            lines.append(" " * pad + foliage)
    # wider trunk for trees
    trunk_w = 1 + s  # wider trunk than flowers
    trunk_pad = (4 * s + 2) - trunk_w // 2
    for _ in range(1 + s):
        lines.append(" " * trunk_pad + ("|" * trunk_w))
    return lines


def _make_broad_tree(size: int, rng: random.Random) -> List[str]:
    radius = 2 + size
    petal = "#"
    lines: List[str] = []
    for y in range(-radius, radius + 1):
        row = []
        for x in range(-2 * radius, 2 * radius + 1):
            dx = x / 2.0
            if dx * dx + y * y <= (radius + 0.2) ** 2:
                row.append(petal)
            else:
                row.append(" ")
        lines.append("".join(row).rstrip())
    trunk_w = 1 + size * 2  # broader trunk
    trunk_col = max(0, len(lines[0]) // 2 - trunk_w // 2)
    for _ in range(1 + size):
        lines.append(" " * trunk_col + ("|" * trunk_w))
    return lines


def _make_stylized_tree(size: int, rng: random.Random) -> List[str]:
    """Return a stylized ASCII tree inspired by the user's sample.

    The art is mostly fixed; size increases add optional extra padding lines
    above the trunk to give taller trees.
    """
    # base art (escaped backslashes doubled)
    art = [
        "           \\\/ |    |/",
        "        \\\/ / \\\||/  /_/___/_",
        "         \\\/   |/ \\\/",
        "    _\\__\\_\\   |  /_____/ _",
        "           \\  | /          /",
        "  __ _-----`  |{,-----------~",
        "            \\ }{",
        "             }{{",
        "             }}{",
        "             {{{}",
        "       , -=-~{ .-^- _",
    ]

    # scaling parameters
    s = max(1, size)
    canopy_extra_rows = s * 2  # more rows for larger sizes
    canopy_variation = max(1, s)  # how much random variation to apply

    lines: List[str] = []

    # create extra canopy rows above the base art to make larger trees fuller
    for r in range(canopy_extra_rows):
        # pattern choices for extra canopy (escaped backslashes)
        patterns = ["\\/", "\\/ \\/", " \\/ \\/"]
        pat = rng.choice(patterns)
        # create a jittered prefix so the canopy is irregular
        prefix_spaces = max(0, 6 - r) + rng.randint(0, canopy_variation)
        lines.append(" " * prefix_spaces + pat * (1 + (r % (1 + canopy_variation))))

    # append the base art (the recognizable stylized tree)
    lines.extend(art)

    # compute trunk width and height scaling with size
    trunk_w = 1 + s * 2
    trunk_h = 2 + s  # taller trunk for larger trees

    # compute final width from the combined lines (use visible length)
    final_width = max(( _visible_len(ln) for ln in lines), default=trunk_w)
    trunk_col = max(0, final_width // 2 - trunk_w // 2)

    # optionally add a small root/basenote line for very large trees
    if s >= 3:
        lines.append(" " * max(0, trunk_col - 2) + "~" * (trunk_w + 4))

    for _ in range(trunk_h):
        lines.append(" " * trunk_col + ("|" * trunk_w))

    return lines


def random_tree(size: int = 1, seed: int | None = None, rng: random.Random | None = None) -> Tuple[List[str], str]:
    if rng is None:
        rng = random.Random(seed)
    kind = rng.choice(["pine", "broad", "bonsai", "cherry", "stylized"])
    if kind == "pine":
        return _make_pine_tree(size, rng), kind
    if kind == "bonsai":
        return _make_broad_tree(max(1, size - 1), rng), kind
    if kind == "cherry":
        canopy = _make_broad_tree(size + 1, rng)
        canopy = [ln.replace("#", ("✿" if os.name != "nt" else "o")) for ln in canopy]
        return canopy, kind
    if kind == "stylized":
        return _make_stylized_tree(size + 1, rng), kind
    return _make_broad_tree(size, rng), kind


def _color_wrap(s: str, color: str, enabled: bool) -> str:
    if not enabled:
        return s
    return f"{ANSI.get(color, '')}{s}{ANSI['reset']}"


def colorize_lines(lines: List[str], plant_kind: str, enabled: bool, rng: random.Random) -> List[str]:
    """Colorize petals, centers, stalks, and trunks by plant kind.

    - Flowers: petals/centers colored; stalks (STEM_CHAR) colored green only.
    - Trees: foliage colored green shades; trunks ('|' repeated) colored brown.
    """
    if not enabled:
        return lines
    colored: List[str] = []
    for line in lines:
        out = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == " ":
                out.append(ch)
                i += 1
                continue

            # detect multi-char trunk segments (e.g., '|||')
            if ch == "|":
                # count consecutive |
                j = i
                while j < len(line) and line[j] == "|":
                    j += 1
                seg = line[i:j]
                if plant_kind.startswith("flower_"):
                    # flower stalks are green
                    out.append(_color_wrap(seg, "green", True))
                else:
                    # tree trunks are brown
                    out.append(_color_wrap(seg, "brown", True))
                i = j
                continue

            # foliage / petals / centers
            if plant_kind.endswith("cherry") or plant_kind.startswith("flower_cherry"):
                c = rng.choice(["magenta", "bright_yellow"])
            elif plant_kind.startswith("flower_sunflower"):
                c = rng.choice(["yellow", "bright_yellow"])
            elif plant_kind.startswith("flower_"):
                c = rng.choice(["bright_green", "green", "bright_yellow", "magenta", "red"])
            else:
                c = rng.choice(["green", "bright_green"])

            out.append(_color_wrap(ch, c, True))
            i += 1

        colored.append("".join(out))
    return colored


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def _visible_len(s: str) -> int:
    return len(_strip_ansi(s))


def render_horizontal(plants: List[List[str]], cols: int = 3, gap: int = 4) -> List[str]:
    """Arrange plants horizontally into rows with bottoms aligned to the ground.

    Plants in each row are bottom-aligned so trunks/stems share the same ground line.
    """
    if cols < 1:
        cols = 1
    out_lines: List[str] = []
    for row_start in range(0, len(plants), cols):
        row = plants[row_start: row_start + cols]
        # compute visible widths and heights
        widths = [max((_visible_len(ln) for ln in p), default=0) for p in row]
        heights = [len(p) for p in row]
        max_h = max(heights) if heights else 0

        # pad each plant at the top so bottoms align
        padded: List[List[str]] = []
        for pi, p in enumerate(row):
            w = widths[pi]
            pad_top = max_h - len(p)
            new_lines: List[str] = []
            # top padding (empty lines of width w)
            for _ in range(pad_top):
                new_lines.append(" " * w)
            # add plant lines padded to width
            for ln in p:
                pad_amount = w - _visible_len(ln)
                new_lines.append(ln + (" " * pad_amount))
            padded.append(new_lines)

        # join horizontally line by line
        for r in range(max_h):
            parts = [padded[c][r] for c in range(len(padded))]
            out_lines.append((" " * gap).join(parts).rstrip())

        # blank line after row
        out_lines.append("")
    return out_lines


def print_garden(plants: List[List[str]], layout: str = "vertical", cols: int = 3, gap: int = 1, auto_fit: bool = False) -> None:
    # when horizontal with auto_fit, compute cols based on terminal width and max plant width
    if layout == "horizontal":
        if auto_fit:
            term_w = shutil.get_terminal_size(fallback=(80, 24)).columns
            max_w = max((max((_visible_len(ln) for ln in p), default=0) for p in plants), default=1)
            cols = max(1, (term_w + gap) // (max_w + gap))
        lines = render_horizontal(plants, cols=cols, gap=gap * 2)
        sys.stdout.write("\n".join(lines) + "\n")
    else:
        # vertical: print plants one after another (no bottom alignment)
        out_lines: List[str] = []
        for i, p in enumerate(plants):
            out_lines.extend(p)
            if i != len(plants) - 1:
                out_lines.extend([""] * gap)
        sys.stdout.write("\n".join(out_lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="ASCII flowers & trees generator")
    p.add_argument("--count", "-n", type=int, default=6, help="Number of flowers to generate")
    p.add_argument("--size", "-s", type=int, default=1, choices=[1, 2, 3], help="Size (1-3)")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
    p.add_argument("--trees", "-t", type=int, default=0, help="Number of trees to generate")
    p.add_argument("--color", choices=["auto", "on", "off"], default="auto", help="Color output")
    p.add_argument("--layout", choices=["vertical", "horizontal"], default="vertical", help="Layout")
    p.add_argument("--cols", type=int, default=3, help="Columns for horizontal layout")
    p.add_argument("--auto-fit", action="store_true", help="Auto-fit columns by terminal width")
    p.add_argument("--no-unicode", action="store_true", help="Disable Unicode glyphs for compatibility")
    args = p.parse_args(argv)

    rng = random.Random(args.seed)
    plants: List[List[str]] = []

    if args.color == "on":
        use_color = True
    elif args.color == "off":
        use_color = False
    else:
        use_color = sys.stdout.isatty()

    # generate flowers
    for _ in range(args.count):
        sub_seed = rng.randint(0, 2 ** 31 - 1)
        sub_rng = random.Random(sub_seed)
        lines, kind = random_flower(size=args.size, seed=sub_seed, rng=sub_rng)
        plants.append(colorize_lines(lines, f"flower_{kind}", use_color, sub_rng))

    # generate trees
    for _ in range(args.trees):
        sub_seed = rng.randint(0, 2 ** 31 - 1)
        sub_rng = random.Random(sub_seed)
        lines, kind = random_tree(size=args.size, seed=sub_seed, rng=sub_rng)
        plants.append(colorize_lines(lines, f"tree_{kind}", use_color, sub_rng))

    print_garden(plants, layout=args.layout, cols=max(1, args.cols), gap=1, auto_fit=args.auto_fit)
    return 0




        
