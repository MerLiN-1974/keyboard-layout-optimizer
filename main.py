#!/usr/bin/env python3
"""
Keyboard Layout Optimization via Simulated Annealing


Notes:
- Cost is total Euclidean distance between consecutive characters.
- Coordinates are fixed (QWERTY-staggered grid). Optimization swaps assignments.

This base code uses Python "types" - these are optional, but very helpful
for debugging and to help with editing.

"""

import argparse
import json
import math
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt  # type: ignore

Point = Tuple[float, float]
Layout = Dict[str, Point]


def qwerty_coordinates(chars: str) -> Layout:
    """Return QWERTY grid coordinates for the provided character set.

    The grid is a simple staggered layout (units are arbitrary):
    - Row 0: qwertyuiop at y=0, x in [0..9]
    - Row 1: asdfghjkl at y=1, x in [0.5..8.5]
    - Row 2: zxcvbnm at y=2, x in [1..6]
    - Space at (4.5, 3)
    Characters not present in the grid default to the space position.
    """
    row0 = "qwertyuiop"
    row1 = "asdfghjkl"
    row2 = "zxcvbnm"

    coords: Layout = {}
    for i, c in enumerate(row0):
        coords[c] = (float(i), 0.0)
    for i, c in enumerate(row1):
        coords[c] = (0.5 + float(i), 1.0)
    for i, c in enumerate(row2):
        coords[c] = (1.0 + float(i), 2.0)
    coords[" "] = (4.5, 3.0)

    # Backfill for requested chars; unknowns get space position.
    space_xy = coords[" "]
    for ch in chars:
        if ch not in coords:
            coords[ch] = space_xy
    return coords


def initial_layout() -> Layout:
    """Create an initial layout mapping chars to some arbitrary positions of letters."""

    # Start with identity for letters and space; others mapped to space.
    base_keys = "abcdefghijklmnopqrstuvwxyz "

    # Get coords - or use coords of space as default
    layout = qwerty_coordinates(base_keys)
    return layout


def preprocess_text(text: str, chars: str) -> str:
    """Lowercase and filter to the allowed character set; map others to space."""
    allowed_chars = set(chars)
    text = text.lower()
    result = ""

    for ch in text:
        if ch in allowed_chars:
            result += ch
        else:
            result += " "

    return result


def path_length_cost(text: str, layout: Layout) -> float:
    """Sum Euclidean distances across consecutive characters in text."""
    len_text = len(text)

    if len_text < 2:
        return 0.0

    total = 0.0

    for i in range(len_text - 1):
        a = text[i]
        b = text[i + 1]

        xa, ya = layout.get(a, layout[" "])
        xb, yb = layout.get(b, layout[" "])

        dx = xb - xa
        dy = yb - ya

        total += math.hypot(dx, dy)

    return total


def swap_two(layout: Layout, rng: random.Random) -> Layout:
    """Swap two random characters and return a new layour"""

    x, y = rng.sample(list(layout.keys()), 2)
    new_layout = dict(layout)
    new_layout[x], new_layout[y] = new_layout[y], new_layout[x]
    return new_layout


def json_layout(layout: Layout, path: str) -> None:
    layout_list = {k: [float(v[0]), float(v[1])] for k, v in layout.items()}

    with open(path, "w", encoding="utf-8") as file:
        json.dump(layout_list, file, indent=2, ensure_ascii=False)


def json_traces(best_trace: List[float], current_trace: List[float], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"best": best_trace, "current": current_trace}, f, indent=2)


######
# Define any other useful functions, such as to create new layout etc.
######


# Dataclass is like a C struct - you can use it just to store data if you wish
# It provides some convenience functions for assignments, printing etc.
@dataclass
class SAParams:
    iters: int = 50000
    t0: float = 1.0  # Initial temperature setting
    alpha: float = 0.999  # geometric decay per iteration
    epoch: int = 1  # iterations per temperature step (1 = per-iter decay)


def simulated_annealing(
    text: str,
    layout: Layout,
    params: SAParams,
    rng: random.Random,
) -> Tuple[Layout, float, List[float], List[float]]:
    """Simulated annealing to minimize path-length cost over character swaps.

    Returns best layout, best cost, and two lists:
    - best cost up to now (monotonically decreasing)
    - cost of current solution (may occasionally go up)
    These will be used for plotting
    """
    current_layout = layout
    current_cost = path_length_cost(text, current_layout)
    best_layout = current_layout
    best_cost = current_cost
    best_trace: List[float] = []
    current_trace: List[float] = []

    T = params.t0

    for i in range(params.iters):
        new_layout = swap_two(current_layout, rng)
        new_cost = path_length_cost(text, new_layout)
        delta = new_cost - current_cost

        accepted = False

        if delta > 0:
            if T > 10 ** (-12):
                p = math.exp(-delta / T)
                if rng.random() < p:
                    accepted = True
        else:
            accepted = True

        if accepted:
            current_layout = new_layout
            current_cost = new_cost

        if current_cost < best_cost:
            best_cost = current_cost
            best_layout = current_layout

        current_trace.append(current_cost)
        best_trace.append(best_cost)

        if params.epoch > 0 and ((i + 1) % params.epoch == 0):
            T *= params.alpha

    return best_layout, best_cost, best_trace, current_trace


def plot_costs(layout: Layout, best_trace: List[float], current_trace: List[float]) -> None:
    # Plot cost trace
    out_dir = "."
    plt.figure(figsize=(6, 3))
    plt.plot(best_trace, lw=1.5)
    plt.plot(current_trace, lw=1.5)
    plt.xlabel("Iteration")
    plt.ylabel("Best Cost")
    plt.title("Best Cost vs Iteration")
    plt.tight_layout()
    path = os.path.join(out_dir, "cost_trace.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

    # Plot layout scatter
    xs, ys, labels = [], [], []
    for ch, (x, y) in layout.items():
        xs.append(x)
        ys.append(y)
        labels.append(ch)

    plt.figure(figsize=(6, 3))
    plt.scatter(xs, ys, s=250, c="#1f77b4")
    for x, y, ch in zip(xs, ys, labels):
        plt.text(
            x,
            y,
            ch,
            ha="center",
            va="center",
            color="white",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.15", fc="#1f77b4", ec="none", alpha=0.9),
        )
    plt.gca().invert_yaxis()
    plt.title("Optimized Layout")
    plt.axis("equal")
    plt.tight_layout()
    path = os.path.join(out_dir, "layout.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def load_text(filename) -> str:
    if filename is not None:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback demo text
    return "the quick brown fox jumps over the lazy dog\nAPL is the best course ever\n"


def main(filename: str | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Keyboard layout optimization via simulated annealing"
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--file", type=str, default="sample_text.txt", help="Path to input text file")
    src.add_argument("--text", type=str, default=None, help="Inline text string to optimize for")
    parser.add_argument("--iters", type=int, default=50000, help="Number of SA iterations")
    parser.add_argument("--t0", type=float, default=1.0, help="Initial temperature")
    parser.add_argument("--alpha", type=float, default=0.999, help="Geometric decay factor")
    parser.add_argument("--epoch", type=int, default=1, help="Iterations per temperature update")

    args = parser.parse_args()

    rng = random.Random(0)
    chars = "abcdefghijklmnopqrstuvwxyz "

    # Initial assignment - QWERTY
    layout0 = initial_layout()

    # Prepare text and evaluate baseline
    if args.text is not None:
        raw_text = args.text
    else:
        raw_text = load_text(args.file)
    text = preprocess_text(raw_text, chars)

    # Annealing - give parameter values
    params = SAParams(iters=args.iters, t0=args.t0, alpha=args.alpha, epoch=args.epoch)
    start = time.time()
    best_layout, best_cost, best_trace, current_trace = simulated_annealing(
        text, layout0, params, rng
    )
    dur = time.time() - start

    baseline_cost = path_length_cost(text, layout0)
    print(f"Baseline (QWERTY assignment) cost: {baseline_cost:.4f}")
    print(f"Optimized cost: {best_cost:.4f} (improvement {baseline_cost - best_cost:.4f})")
    print(f"Runtime: {dur:.2f}s over {params.iters} iterations")

    outdir = "."
    json_layout(best_layout, os.path.join(outdir, "layout.json"))
    json_traces(best_trace, current_trace, os.path.join(outdir, "cost_trace.json"))

    # Plot cost traces and final layout
    plot_costs(best_layout, best_trace, current_trace)


if __name__ == "__main__":
    main()
