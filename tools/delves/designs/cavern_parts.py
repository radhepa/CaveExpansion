"""Shared helpers for the natural caverns (Hermit's Hollow, The Glimmering).

A cavern here is 2.5D: every column (x, z) inside a noisy outline has a floor height and a ceiling height. The
air between them is carved (always placed); the floor is a built block (or a soft one over a built sub-floor);
the rock around the air is lined with soft natural blocks in layers (placed only where the world is solid).
Noise is seeded value noise (numpy), so a design always builds the same.
"""
import itertools
import math
from collections import deque

import numpy as np

from kit import NATURAL

SOFT = set(NATURAL)
SIDES = ((1, 0), (-1, 0), (0, 1), (0, -1))
NEIGHBOURS6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
DIR = {(1, 0): 'east', (-1, 0): 'west', (0, 1): 'south', (0, -1): 'north'}


def noise(size, seed, scale, octaves=3, persistence=0.5):
    """Smooth value noise (fBm) on a grid of `size` (2 or 3 dims), roughly in [-1, 1]; `scale` is the feature size
    of the first octave in blocks."""
    rng = np.random.default_rng(seed)
    dims = len(size)
    grids = np.meshgrid(*[np.arange(n, dtype=float) for n in size], indexing='ij')
    total = np.zeros(size)
    norm, amp, s = 0.0, 1.0, float(scale)
    for _ in range(octaves):
        shift = rng.random(dims) * 4
        coords = [g / s + sh for g, sh in zip(grids, shift)]
        lattice = rng.random(tuple(int(n / s + 6) for n in size)) * 2 - 1
        idx = [np.floor(c).astype(int) for c in coords]
        fr = [c - i for c, i in zip(coords, idx)]
        fr = [f * f * (3 - 2 * f) for f in fr]
        val = np.zeros(size)
        for corner in itertools.product((0, 1), repeat=dims):
            w = np.ones(size)
            for d, b in enumerate(corner):
                w = w * (fr[d] if b else 1 - fr[d])
            val += w * lattice[tuple(i + b for i, b in zip(idx, corner))]
        total += amp * val
        norm += amp
        amp *= persistence
        s /= 2
    out = total / norm
    return out / max(1e-9, np.abs(out).max())


def relax(heights, max_step=1, lower=True, fixed=()):
    """Make neighbouring columns differ by at most `max_step` (so the floor is walkable). With lower=True the
    high cells come down; otherwise the low cells come up. Cells in `fixed` never change."""
    queue = deque(heights)
    while queue:
        c = queue.popleft()
        x, z = c
        for dx, dz in SIDES:
            n = (x + dx, z + dz)
            if n not in heights or n in fixed: continue
            if lower and heights[n] > heights[c] + max_step:
                heights[n] = heights[c] + max_step
                queue.append(n)
            elif not lower and heights[n] < heights[c] - max_step:
                heights[n] = heights[c] - max_step
                queue.append(n)
    return heights


class Cavern:
    """Open columns: floor[(x, z)] is the y of the floor block (people walk at y + 1), ceil[(x, z)] the highest
    open y. `blocked` holds cells inside a column's range that stay rock (wall bumps)."""

    def __init__(self, t):
        self.t = t
        self.floor = {}
        self.ceil = {}
        self.blocked = set()

    def add_column(self, x, z, floor, ceil):
        if not (0 <= x < self.t.size[0] and 0 <= z < self.t.size[2]): return
        floor = max(0, floor)
        ceil = min(self.t.size[1] - 1, ceil)
        if ceil <= floor: return
        c = (x, z)
        if c in self.floor:
            self.floor[c] = min(self.floor[c], floor)
            self.ceil[c] = max(self.ceil[c], ceil)
        else:
            self.floor[c], self.ceil[c] = floor, ceil

    def is_open(self, x, y, z):
        c = (x, z)
        return c in self.floor and self.floor[c] < y <= self.ceil[c] and (x, y, z) not in self.blocked

    def cells(self):
        for (x, z), f in self.floor.items():
            for y in range(f + 1, self.ceil[(x, z)] + 1):
                if (x, y, z) not in self.blocked: yield x, y, z

    def carve(self):
        for p in self.cells():
            self.t.set(*p, 'air')

    def walk_y(self, x, z):
        return self.floor[(x, z)] + 1

    def headroom(self, x, z):
        c = (x, z)
        return self.ceil[c] - self.floor[c] if c in self.floor else 0

    def kind(self, x, y, z):
        if self.is_open(x, y + 1, z): return 'floor'
        if self.is_open(x, y - 1, z): return 'ceiling'
        return 'wall'

    def lining(self, pick, depth=2):
        """Line the rock around the air with what `pick(x, y, z, d, kind)` returns (d = 1 next to the air), only
        in cells still unset. kind is 'floor', 'ceiling' or 'wall' (or 'deep' for d > 1)."""
        t = self.t
        seen = set()
        frontier = set(self.cells())
        seen |= frontier
        for d in range(1, depth + 1):
            nxt = set()
            for (x, y, z) in frontier:
                for dx, dy, dz in NEIGHBOURS6:
                    n = (x + dx, y + dy, z + dz)
                    if n in seen or not t.inside(*n) or self.is_open(*n): continue
                    seen.add(n)
                    nxt.add(n)
            for n in sorted(nxt):
                if n in t.blocks: continue
                b = pick(*n, d, self.kind(*n) if d == 1 else 'deep')
                if b: t.set(*n, b)
            frontier = nxt

    def ceiling_cells(self):
        """(x, y, z) of each open column's top air cell whose block above is rock (something can hang there)."""
        for (x, z), c in self.ceil.items():
            if c + 1 < self.t.size[1]: yield x, c, z


def seal_water(t, water, block):
    """Every water cell's sides and bottom must be a built block, or the pool drains into the rock's caves.
    Unset, air or soft neighbours become `block` (a spec or a callable (x, y, z) -> spec)."""
    water = set(water)
    for (x, y, z) in sorted(water):
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
            n = (x + dx, y + dy, z + dz)
            if n in water or not t.inside(*n): continue
            name = t.name_at(*n)
            if name is None or name in SOFT or name == 'minecraft:air':
                t.set(*n, block(*n) if callable(block) else block)


def is_built(t, x, y, z):
    """True if the cell holds a block that is always placed and solid enough to stand on."""
    name = t.name_at(x, y, z)
    return name is not None and name not in SOFT and name != 'minecraft:air'


def hang(t, x, y, z, length, kind='vines', rng=None, berries=0.6):
    """Hang something down from the rock above (x, y + 1, z): glow-berry vines, or a pointed-dripstone
    stalactite. Stops at the first non-air cell. Returns the cells used."""
    used = []
    for i in range(length):
        if t.name_at(x, y - i, z) != 'minecraft:air' or y - i - 1 < 0: break
        used.append((x, y - i, z))
    if not used: return used
    if kind == 'vines':
        for i, p in enumerate(used):
            lit = (rng.random() < berries) if rng else True
            last = i == len(used) - 1
            t.set(*p, f'cave_vines[berries={"true" if lit else "false"}]' if last
                  else f'cave_vines_plant[berries={"true" if lit else "false"}]')
    else:
        drip(t, used, 'down')
    return used


def drip(t, cells, direction):
    """Pointed dripstone along `cells` (ordered from the rock outwards): base, middle..., frustum, tip."""
    n = len(cells)
    for i, p in enumerate(cells):
        if i == n - 1: th = 'tip'
        elif i == n - 2: th = 'frustum'
        elif i == 0: th = 'base'
        else: th = 'middle'
        if n == 2 and i == 0: th = 'frustum'
        t.set(*p, f'pointed_dripstone[thickness={th},vertical_direction={direction},waterlogged=false]')


def stalagmite(t, x, y, z, length):
    """A pointed-dripstone stalagmite rising from the floor block at (x, y - 1, z)."""
    cells = []
    for i in range(length):
        if t.name_at(x, y + i, z) != 'minecraft:air' or t.name_at(x, y + i + 1, z) != 'minecraft:air': break
        cells.append((x, y + i, z))
    if cells: drip(t, cells, 'up')
    return cells


def stairs_on_steps(t, cav, cells, stair, protect=()):
    """Where a walking cell is one block lower than a neighbour in `cells`, set a stair (facing up the slope) on
    it, so the step is walked rather than jumped."""
    for (x, z) in sorted(cells):
        if (x, z) not in cav.floor or (x, z) in protect: continue
        y = cav.walk_y(x, z)
        if t.name_at(x, y, z) != 'minecraft:air' or t.name_at(x, y + 1, z) != 'minecraft:air': continue
        for (dx, dz) in SIDES:
            n = (x + dx, z + dz)
            if n in cells and n in cav.floor and cav.walk_y(*n) == y + 1:
                t.set(x, y, z, f'{stair}[facing={DIR[(dx, dz)]},half=bottom,shape=straight,waterlogged=false]')
                break


def path4(points):
    """The cells of a polyline through (x, z) points, each one sharing a side with the last (walkable)."""
    out = [tuple(points[0])]
    for (x1, z1) in points[1:]:
        x, z = out[-1]
        while (x, z) != (x1, z1):
            dx, dz = x1 - x, z1 - z
            if abs(dx) >= abs(dz): x += (dx > 0) - (dx < 0)
            else: z += (dz > 0) - (dz < 0)
            out.append((x, z))
    return out


def side_of(route, i):
    """The two cells beside route[i], across the way the route runs there."""
    a = route[max(0, i - 1)]
    b = route[min(len(route) - 1, i + 1)]
    dx, dz = b[0] - a[0], b[1] - a[1]
    x, z = route[i]
    if abs(dx) >= abs(dz): return (x, z - 1), (x, z + 1)
    return (x - 1, z), (x + 1, z)


def polar(x, z, cx, cz):
    """Angle (0..2pi) and distance of (x, z) from (cx, cz)."""
    a = math.atan2(z - cz, x - cx)
    return a % (2 * math.pi), math.hypot(x - cx, z - cz)


def ring_noise(seed, n=64, octaves=3):
    """A smooth closed curve of noise around a circle: f(angle) in about [-1, 1]."""
    rng = np.random.default_rng(seed)
    coeffs = [(rng.normal() / (k ** 1.2), rng.random() * 2 * math.pi) for k in range(1, 3 * octaves + 1)]

    def f(a):
        return sum(c * math.cos(k * a + ph) for k, (c, ph) in enumerate(coeffs, start=1)) / 1.4
    return f
