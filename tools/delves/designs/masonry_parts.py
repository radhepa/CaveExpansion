"""Shared helpers for the masonry delves (Deepwatch Post, the Drowned Cistern): weighted block mixes, stairs,
panes and walls that connect to their neighbours (jigsaw pieces keep their stored shapes, so connections have
to be written into the template), merlons, braziers, lamp posts, rubble and a rock lining for carved spaces.

Not a design module (designs.modules() only loads the delve keys)."""
from kit import NATURAL

DIRS = {'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0)}
SIX = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))

STONE_BRICKS = [('stone_bricks', 12), ('cracked_stone_bricks', 2), ('mossy_stone_bricks', 1)]
DEEP_BRICKS = [('deepslate_bricks', 12), ('cracked_deepslate_bricks', 2)]
DEEP_TILES = [('deepslate_tiles', 12), ('cracked_deepslate_tiles', 2)]
OLD_BRICKS = [('stone_bricks', 8), ('cracked_stone_bricks', 4), ('mossy_stone_bricks', 4)]
OLD_TILES = [('deepslate_tiles', 8), ('cracked_deepslate_tiles', 4)]
ROAD = [('cobblestone', 5), ('cobbled_deepslate', 5), ('polished_andesite', 2), ('stone_bricks', 2),
        ('mossy_cobblestone', 1)]
ROCK = [('deepslate', 4), ('tuff', 3), ('stone', 2), ('andesite', 1)]

# Things a pane/wall/fence does not lean on (thin, or not a full face).
_THIN = ('air', 'water', 'lava', 'lantern', 'torch', 'candle', 'carpet', 'rail', 'sign', 'banner', 'button', 'lever',
         'chain', 'door', 'trapdoor', 'campfire', 'bed', 'chest', 'barrel', 'skull', 'head', 'pot', 'slab', 'stairs',
         'ladder', 'lectern', 'cobweb', 'jigsaw', 'haunt', 'dummy', 'target', 'pickle', 'kelp', 'seagrass', 'lichen',
         'anvil', 'grindstone', 'cauldron', 'bell', 'rod', 'flower', 'mushroom', 'leaf_litter')


def pick(rng, choices):
    """[(spec, weight), ...] -> one spec."""
    total = sum(w for _, w in choices)
    r = rng.random() * total
    for s, w in choices:
        r -= w
        if r < 0: return s
    return choices[-1][0]


def mix(rng, choices):
    """A fill callable that picks a weighted variant per cell."""
    return lambda x, y, z: pick(rng, choices)


def stair(block, facing, half='bottom', shape='straight', wet=False):
    """'stone_brick' -> 'stone_brick_stairs[facing=..,half=..,shape=..]'. Stairs climb toward `facing`."""
    w = ',waterlogged=true' if wet else ''
    return f'{block}_stairs[facing={facing},half={half},shape={shape}{w}]'


def slab(block, half='bottom', wet=False):
    w = ',waterlogged=true' if wet else ''
    return f'{block}_slab[type={half}{w}]'


def _family(name):
    n = name.split(':')[1]
    if n.endswith('_bars') or n.endswith('pane'): return 'pane'
    if n.endswith('_wall') and 'sign' not in n and 'banner' not in n and 'torch' not in n: return 'wall'
    if n.endswith('_fence') or n.endswith('fence_gate'): return 'fence'
    return None


def _leans_on(t, p):
    """Would a pane/wall/fence at a neighbour connect to the block at p? Unset counts as rock (it usually is)."""
    b = t.blocks.get(p)
    if b is None: return True
    n = b[0].split(':')[1]
    return not any(k in n for k in _THIN)


def connect(t, cells, wet=False):
    """Give every pane (bars), wall or fence in `cells` its side connections from what is around it."""
    for (x, y, z) in cells:
        b = t.blocks.get((x, y, z))
        if b is None: continue
        name, props = b
        fam = _family(name)
        if fam is None: continue
        props = {k: v for k, v in props.items() if k not in DIRS}
        for side, (dx, dz) in DIRS.items():
            n = (x + dx, y, z + dz)
            nb = t.blocks.get(n)
            same = nb is not None and _family(nb[0]) is not None
            if same or (t.inside(*n) and _leans_on(t, n)) or not t.inside(*n):
                props[side] = 'low' if fam == 'wall' else 'true'
            elif fam == 'pane':
                props[side] = 'false'
        if wet: props['waterlogged'] = 'true'
        t.blocks[(x, y, z)] = (name, props)


def line(t, a, b, block, wet=False):
    """A straight run of panes/walls/fences from a to b (inclusive), connected."""
    t.fill(a, b, block)
    cells = [(x, y, z) for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1)
             for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1)
             for z in range(min(a[2], b[2]), max(a[2], b[2]) + 1)]
    connect(t, cells, wet)
    return cells


def merlons(t, x0, z0, x1, z1, y, block, start=0, sides=('north', 'south', 'west', 'east')):
    """Crenellations: every other block along the chosen edges of the rectangle (x0,z0)-(x1,z1) at height y."""
    cells = []
    if 'north' in sides: cells += [(x, z0) for x in range(x0, x1 + 1)]
    if 'south' in sides: cells += [(x, z1) for x in range(x0, x1 + 1)]
    if 'west' in sides: cells += [(x0, z) for z in range(z0, z1 + 1)]
    if 'east' in sides: cells += [(x1, z) for z in range(z0, z1 + 1)]
    for (x, z) in set(cells):
        corner = x in (x0, x1) and z in (z0, z1)
        if corner or (x + z + start) % 2 == 0:
            t.set(x, y, z, block(x, y, z) if callable(block) else block)


def brazier(t, x, y, z, base='polished_deepslate', soul=False):
    """A fire bowl: a stone plinth at y with a lit campfire on it (y + 1)."""
    t.set(x, y, z, base)
    t.set(x, y + 1, z, ('soul_campfire' if soul else 'campfire') + '[facing=north,lit=true,signal_fire=false]')


def lamp_post(t, x, y, z, height=2, post='spruce_fence', lamp='lantern'):
    """A fence post `height` tall standing on the block below y, a lantern on top."""
    for i in range(height):
        t.set(x, y + i, z, post)
    t.set(x, y + height, z, f'{lamp}[hanging=false]')


def hang(t, x, y, z, chain=0, lamp='lantern', chain_block='iron_chain'):
    """A lantern hanging at y with `chain` links above it."""
    t.set(x, y, z, f'{lamp}[hanging=true]')
    for i in range(1, chain + 1):
        t.set(x, y + i, z, f'{chain_block}[axis=y]')


def rubble(t, rng, cells, choices=(('cobblestone', 4), ('cobbled_deepslate', 4), ('gravel', 2),
                                       ('stone_bricks', 1), ('cracked_stone_bricks', 1))):
    for p in cells:
        t.set(*p, pick(rng, list(choices)))


def line_rock(t, rng, choices=ROCK, skip=None):
    """Line the living rock around carved space: every unset cell touching 'air' gets a soft NATURAL block (it
    only replaces solid ground in the world, so real caves stay open)."""
    for name, _ in choices: assert 'minecraft:' + name in NATURAL, name
    air = [p for p, (n, _) in t.blocks.items() if n == 'minecraft:air']
    for (x, y, z) in air:
        for dx, dy, dz in SIX:
            p = (x + dx, y + dy, z + dz)
            if not t.inside(*p) or p in t.blocks: continue
            if skip and skip(*p): continue
            t.set(*p, pick(rng, list(choices)))
