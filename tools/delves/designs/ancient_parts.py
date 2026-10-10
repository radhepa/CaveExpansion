"""Old Delver masonry shared by the deep, ancient delves (the Ossuary and the Sunken Forge): worn-stone
pickers, block-state helpers, the Delvers' mark (a lantern over crossed picks), room shells, and the
checks that keep lava inside built basins and away from anything that burns.

Not a design module itself (designs/__init__.py only loads the eight keys)."""
from kit import Byte, HORIZONTAL, LEFT, NATURAL, OPPOSITE, RIGHT

ROT16 = {'south': 0, 'west': 4, 'north': 8, 'east': 12}


# -- worn stone -----------------------------------------------------------------------------------

def worn(rng, block, cracked, p):
    return cracked if rng.random() < p else block


def tiles(rng, p=0.15):
    return worn(rng, 'deepslate_tiles', 'cracked_deepslate_tiles', p)


def dbricks(rng, p=0.15):
    return worn(rng, 'deepslate_bricks', 'cracked_deepslate_bricks', p)


def pbb(rng, p=0.12):
    return worn(rng, 'polished_blackstone_bricks', 'cracked_polished_blackstone_bricks', p)


# -- block states ---------------------------------------------------------------------------------

def stair(name, facing, half='bottom', shape='straight'):
    """`facing` is the side the tall back of the step is on (for half=top: the side it hangs from)."""
    return f'{name}[facing={facing},half={half},shape={shape},waterlogged=false]'


def slab(name, kind='bottom'):
    return f'{name}[type={kind},waterlogged=false]'


def post(name, **sides):
    """A wall block. Unlisted sides stay unconnected (the kit only accepts low/tall, so 'none' is left out)."""
    props = ','.join(f'{k}={v}' for k, v in sorted(sides.items()))
    return f'{name}[{props}]' if props else name


def bars(*sides):
    """Iron bars joined toward `sides` (e.g. 'east', 'west')."""
    return 'iron_bars[' + ','.join(f'{d}={"true" if d in sides else "false"}'
                                   for d in ('east', 'north', 'south', 'west')) + ',waterlogged=false]'


def chain(axis='y'):
    return f'iron_chain[axis={axis},waterlogged=false]'


def skull(rng=None, facing=None):
    """A skeleton skull on the floor, looking toward `facing` (or anywhere)."""
    rot = ROT16[facing] if facing else rng.randrange(16)
    return f'skeleton_skull[rotation={rot}]'


def wall_skull(facing):
    """A skull on the wall behind it, looking toward `facing`."""
    return f'skeleton_wall_skull[facing={facing}]'


def candle(n=1, lit=False, color=None):
    return f'{color + "_" if color else ""}candle[candles={n},lit={"true" if lit else "false"},waterlogged=false]'


def lantern(kind='lantern', hanging=False):
    return f'{kind}[hanging={"true" if hanging else "false"},waterlogged=false]'


def frame(t, x, y, z, facing, item, rotation=0):
    """An item frame (see Template.item_frame) whose item is turned `rotation` eighths of a turn."""
    t.item_frame(x, y, z, facing, item)
    if rotation:
        t.entities[-1]['nbt']['ItemRotation'] = Byte(rotation)


def lateral(facing):
    """Unit step to the viewer's right when standing in front of a wall that faces `facing`."""
    return HORIZONTAL[LEFT[facing]]


# -- the Delvers' mark --------------------------------------------------------------------------------

def mark_wall(t, x, y, z, facing, light='lantern', pick='iron_pickaxe', bracket='polished_blackstone_brick_stairs'):
    """The Old Delvers' mark on a wall: a lantern on a stone bracket over two crossed picks.
    (x, y, z) is the open cell in front of the wall at pick height; `facing` points out of the wall."""
    dx, dz = HORIZONTAL[facing]
    rx, rz = lateral(facing)
    wx, wz = x - dx, z - dz                                    # the wall right behind
    for k in (-1, 0, 1):
        t.set(wx + rx * k, y, wz + rz * k, 'polished_blackstone')
    t.set(wx, y + 1, wz, 'chiseled_polished_blackstone')
    t.set(wx, y + 2, wz, 'gilded_blackstone')
    t.set(x, y, z, stair(bracket, OPPOSITE[facing], 'top'))
    t.set(x, y + 1, z, lantern(light))
    # Picks hang left and right of the bracket, heads up and out, handles meeting under the lantern.
    frame(t, x - rx, y, z - rz, facing, pick, rotation=6)
    frame(t, x + rx, y, z + rz, facing, pick, rotation=0)


def mark_floor(t, cx, y, cz, up, ink='polished_blackstone', head='polished_deepslate', gold='gilded_blackstone'):
    """The mark inlaid in the floor layer y: two crossed picks centred on (cx, cz), a lantern above them
    toward `up`. Spans 7 across and 9 along `up` (from 2 behind the centre to 6 ahead)."""
    ux, uz = HORIZONTAL[up]
    rx, rz = HORIZONTAL[RIGHT[up]]

    def put(u, v, block):
        t.set(cx + rx * u + ux * v, y, cz + rz * u + uz * v, block)

    for k in (-2, -1, 1, 2):
        put(k, k, ink)
        put(k, -k, ink)
    put(0, 0, 'chiseled_polished_blackstone')
    for u, v in ((-1, 3), (-3, 1), (1, 3), (3, 1)):             # the pick heads, across each handle's top
        put(u, v, head)
    put(0, 5, 'gold_block')                                    # the lantern: a gold flame in a gilded cage
    for u, v in ((-1, 5), (1, 5), (0, 4), (0, 6)):
        put(u, v, gold)


# -- rooms ------------------------------------------------------------------------------------------

def masonry(t, lo, hi, block):
    """Solid masonry over the box lo..hi; `block` may be a callable (x, y, z) -> spec."""
    t.fill(lo, hi, block)


def crumble(t, cells, rng, p, soft='deepslate'):
    """Turn some wall cells into soft rock: in solid ground they read as fallen facing, and where a cave runs
    alongside they are skipped, so the cave breaks into the room."""
    for c in cells:
        if rng.random() < p:
            t.set(*c, soft)


def face_cells(lo, hi, side):
    """Cells of one vertical face of the box lo..hi (inclusive): side in north/south/east/west."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    if side == 'north': return [(x, y, z0) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    if side == 'south': return [(x, y, z1) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    if side == 'west': return [(x0, y, z) for z in range(z0, z1 + 1) for y in range(y0, y1 + 1)]
    return [(x1, y, z) for z in range(z0, z1 + 1) for y in range(y0, y1 + 1)]


# -- lava safety --------------------------------------------------------------------------------------

# Blocks lava can flow into (they don't block motion and can't hold a fluid), or that may not be there.
_LAVA_GIVES_WAY = ('cobweb', 'torch', 'carpet', 'rail', 'button', 'pressure_plate', 'banner', 'lichen', 'vine',
                   'haunt', 'jigsaw', 'fire', 'skull', 'head', 'flower', 'grass', 'fern', 'mushroom', 'roots')
_WOODS = ('oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry', 'pale_oak', 'bamboo')
_BURNS = ('lectern', 'bookshelf', 'wool', 'carpet', 'coal_block', 'hay_block', 'scaffolding', 'composter', 'target',
          'leaves', 'moss', 'dried_kelp_block')


def lava_leaks(t):
    """Lava cells that could run: every lava source needs lava or a built, fluid-tight block on its four sides
    and below (never air, the world's own rock, a soft block that may be skipped, or the template's edge)."""
    bad = []
    for (x, y, z), (name, _) in t.blocks.items():
        if name != 'minecraft:lava': continue
        for n in ((x + 1, y, z), (x - 1, y, z), (x, y, z + 1), (x, y, z - 1), (x, y - 1, z)):
            b = t.blocks.get(n) if t.inside(*n) else None
            if b is None:
                bad.append(((x, y, z), n, 'unset/outside'))
                continue
            short = b[0].split(':')[1]
            if b[0] == 'minecraft:lava': continue
            if short == 'air' or b[0] in NATURAL or any(w in short for w in _LAVA_GIVES_WAY):
                bad.append(((x, y, z), n, short))
    return bad


def burns(short):
    if any(w in short for w in _BURNS): return True
    return any(short.startswith(w + '_') for w in _WOODS) and not short.endswith(('_door', '_trapdoor', '_sign',
                                                                                      '_button', '_pressure_plate'))


def fire_risks(t, reach=3):
    """Flammable blocks lava could set alight (it lights air up to about three blocks up and across)."""
    lava = [p for p, (n, _) in t.blocks.items() if n == 'minecraft:lava']
    out = []
    for (x, y, z), (name, _) in t.blocks.items():
        if not burns(name.split(':')[1]): continue
        for lx, ly, lz in lava:
            if abs(x - lx) <= reach and abs(z - lz) <= reach and -1 <= y - ly <= reach:
                out.append(((x, y, z), name, (lx, ly, lz)))
                break
    return out


def check_lava(t):
    leaks, fires = lava_leaks(t), fire_risks(t)
    assert not leaks, f'{t.name}: lava could run at {leaks[:6]}'
    assert not fires, f'{t.name}: flammable blocks next to lava {fires[:6]}'
