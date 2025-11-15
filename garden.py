#!/usr/bin/env python3
"""Garden generator: improved version with auto-fit, more plants and colors.

This is a standalone cleaner implementation. Run as:
  python garden.py --count 6 --trees 3 --layout horizontal --auto-fit --color on
"""
from __future__ import annotations

import argparse
import os
import random
import re
import shutil
import sys
from typing import List, Tuple

PETAL_CHARS = ["*", "o", "@", "O", "0", "+", "x", "X"]
CENTER_CHARS = ["@", "*", "O"]
STEM_CHARS = ["|", "!", "i", "l"]

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
    stem_char = rng.choice(STEM_CHARS)
    for _ in range(stem_height):
        lines.append(" " * stem_col + stem_char)
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
    stem = rng.choice(STEM_CHARS)
    for _ in range(1 + s + rng.randint(0, s)):
        lines.append(" " * (2 * s) + stem)
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
    stem_char = rng.choice(STEM_CHARS)
    for _ in range(1 + s + rng.randint(0, 2)):
        lines.append(" " * (2 + s) + stem_char)
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
    stem_char = rng.choice(STEM_CHARS)
    for _ in range(2 + s):
        lines.append(" " * (2 + s) + stem_char)
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
    stem_char = rng.choice(STEM_CHARS)
    for _ in range(1 + s):
        lines.append(" " * (2 + s) + stem_char)
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
    for layer in range(3):
        width = 1 + 2 * (layer + s)
        for row in range(width):
            pad = (4 * s + 2) - row
            foliage = "^" * (1 + 2 * row)
            lines.append(" " * pad + foliage)
    trunk_w = 1 + (s // 2)
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
    trunk_col = len(lines[0]) // 2
    trunk_char = "|"
    for _ in range(1 + size):
        lines.append(" " * trunk_col + trunk_char)
    return lines


def random_tree(size: int = 1, seed: int | None = None, rng: random.Random | None = None) -> Tuple[List[str], str]:
    if rng is None:
        rng = random.Random(seed)
    kind = rng.choice(["pine", "broad", "bonsai", "cherry"])
    if kind == "pine":
        return _make_pine_tree(size, rng), kind
    if kind == "bonsai":
        return _make_broad_tree(max(1, size - 1), rng), kind
    if kind == "cherry":
        canopy = _make_broad_tree(size + 1, rng)
        canopy = [ln.replace("#", "✿" if os.name != "nt" else "o") for ln in canopy]
        return canopy, kind
    return _make_broad_tree(size, rng), kind


def _color_wrap(s: str, color: str, enabled: bool) -> str:
    if not enabled:
        return s
    return f"{ANSI.get(color, '')}{s}{ANSI['reset']}"


def colorize_lines(lines: List[str], plant_kind: str, enabled: bool, rng: random.Random) -> List[str]:
    if not enabled:
        return lines
    colored: List[str] = []
    for line in lines:
        out = []
        for ch in line:
            if ch == " ":
                out.append(ch)
                continue
            if plant_kind.endswith("cherry") or plant_kind.startswith("flower_cherry"):
                c = rng.choice(["magenta", "bright_yellow"])
            elif plant_kind.startswith("flower_sunflower"):
                c = rng.choice(["yellow", "bright_yellow"])
            elif plant_kind.startswith("flower_"):
                c = rng.choice(["bright_green", "green", "bright_yellow", "magenta", "red"])
            elif plant_kind.endswith("bonsai") or plant_kind.startswith("tree_bonsai"):
                c = "bright_green"
            else:
                c = rng.choice(["green", "bright_green"])
            out.append(_color_wrap(ch, c, True))
        colored.append("".join(out))
    return colored


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def _visible_len(s: str) -> int:
    return len(_strip_ansi(s))


def render_horizontal(plants: List[List[str]], cols: int = 3, gap: int = 4) -> List[str]:
    if cols < 1:
        cols = 1
    out_lines: List[str] = []
    for row_start in range(0, len(plants), cols):
        row = plants[row_start: row_start + cols]
        widths = [max((_visible_len(ln) for ln in p), default=0) for p in row]
        heights = [len(p) for p in row]
        max_h = max(heights) if heights else 0
        padded: List[List[str]] = []
        for pi, p in enumerate(row):
            w = widths[pi]
            new_lines: List[str] = []
            for ln in p:
                pad_amount = w - _visible_len(ln)
                new_lines.append(ln + (" " * pad_amount))
            for _ in range(max_h - len(new_lines)):
                new_lines.append(" " * w)
            padded.append(new_lines)
        for r in range(max_h):
            parts = [padded[c][r] for c in range(len(padded))]
            out_lines.append((" " * gap).join(parts).rstrip())
        out_lines.append("")
    return out_lines


def print_garden(plants: List[List[str]], layout: str = "vertical", cols: int = 3, gap: int = 1, auto_fit: bool = False) -> None:
    if layout == "horizontal":
        if auto_fit:
            term_w = shutil.get_terminal_size(fallback=(80, 24)).columns
            max_w = max((max((_visible_len(ln) for ln in p), default=0) for p in plants), default=1)
            cols = max(1, (term_w + gap) // (max_w + gap))
        lines = render_horizontal(plants, cols=cols, gap=gap * 2)
        sys.stdout.write("\n".join(lines) + "\n")
    else:
        out_lines: List[str] = []
        for i, p in enumerate(plants):
            out_lines.extend(p)
            if i != len(plants) - 1:
                out_lines.extend([""] * gap)
        sys.stdout.write("\n".join(out_lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Garden ASCII generator")
    p.add_argument("--count", "-n", type=int, default=6)
    p.add_argument("--size", "-s", type=int, default=1, choices=[1, 2, 3])
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--trees", "-t", type=int, default=0)
    p.add_argument("--color", choices=["auto", "on", "off"], default="auto")
    p.add_argument("--layout", choices=["vertical", "horizontal"], default="vertical")
    p.add_argument("--cols", type=int, default=3)
    p.add_argument("--auto-fit", action="store_true")
    args = p.parse_args(argv)

    rng = random.Random(args.seed)
    plants: List[List[str]] = []
    if args.color == "on":
        use_color = True
    elif args.color == "off":
        use_color = False
    else:
        use_color = sys.stdout.isatty()

    for _ in range(args.count):
        sub_seed = rng.randint(0, 2 ** 31 - 1)
        sub_rng = random.Random(sub_seed)
        lines, kind = random_flower(size=args.size, seed=sub_seed, rng=sub_rng)
        plants.append(colorize_lines(lines, f"flower_{kind}", use_color, sub_rng))

    for _ in range(args.trees):
        sub_seed = rng.randint(0, 2 ** 31 - 1)
        sub_rng = random.Random(sub_seed)
        lines, kind = random_tree(size=args.size, seed=sub_seed, rng=sub_rng)
        plants.append(colorize_lines(lines, f"tree_{kind}", use_color, sub_rng))

    print_garden(plants, layout=args.layout, cols=max(1, args.cols), gap=1, auto_fit=args.auto_fit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
