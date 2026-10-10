"""The Delvers' Guild mining look, shared by the Delvers' Camp (camp.py) and the Buried Seam (seam.py): timber
props, rails, rock lining with ore veins, rubble, remains.

Every drift of both delves has the same cross-section, so their pieces could join and they read as one
Guild:
    a drift runs along an axis; across it, w = c-2 and c+2 are its walls (the timber posts stand in them),
    w = c-1..c+1 is the open tunnel with the rail on w = c; y = y0 floor, y0+1..y0+3 open, y0+4 the beams.
Jigsaws sit on the centre line at y0 + 1 (on the rail), their final state is the rail itself.
"""
from kit import Template, NATURAL, chance  # noqa: F401  (Template is re-exported for the designs)

POST = 'stripped_spruce_log[axis=y]'
PLANK = 'spruce_planks'

# Natural rock lining (soft: only where the world is solid). Mostly plain stone with the odd patch.
ROCK = [('stone', 14), ('andesite', 4), ('tuff', 3), ('gravel', 1), ('diorite', 1), ('granite', 1)]
# An ordinary Guild working: plenty of coal, iron and copper, a little gold, redstone and lapis.
VEIN = [('coal_ore', 30), ('iron_ore', 24), ('copper_ore', 22), ('gold_ore', 5), ('redstone_ore', 9), ('lapis_ore', 6)]
# Built floors of a drift: rammed cobble and packed earth.
FLOOR = [('cobblestone', 6), ('packed_mud', 3), ('cobbled_deepslate', 2), ('mossy_cobblestone', 1)]
# Fallen roof: built rubble (always there) with soft gravel, tuff and andesite in it.
RUBBLE = [('cobblestone', 7), ('cobbled_deepslate', 4), ('mossy_cobblestone', 2), ('gravel', 4), ('tuff', 3),
          ('andesite', 2), ('stone', 1)]
RUBBLE_TOP = ['cobblestone_slab[type=bottom]', 'cobbled_deepslate_slab[type=bottom]', 'tuff_slab[type=bottom]',
              'mossy_cobblestone_slab[type=bottom]']

for _spec, _ in ROCK + VEIN:
    assert 'minecraft:' + _spec in NATURAL, _spec


def pick(rng, table):
    """A weighted choice from [(spec, weight)]."""
    total = sum(w for _, w in table)
    r = rng.random() * total
    for spec, w in table:
        r -= w
        if r < 0: return spec
    return table[-1][0]


def rock(rng, ore=0.0, ores=VEIN):
    """A lining block: rock, or (with chance `ore`) an ore from `ores`."""
    return pick(rng, ores) if rng.random() < ore else pick(rng, ROCK)


def xz(axis, u, w):
    """Map along/across coordinates of a drift to (x, z)."""
    return (u, w) if axis == 'x' else (w, u)


def line(t, a, b, rng, ore=0.0, ores=VEIN, ceiling=False, floor=False, sides=True):
    """Line the rock around the open box a..b (one block thick) with NATURAL blocks, only where nothing is set
    yet. Walls by default; the ceiling and the ground under the floor only when asked."""
    for y in range(a[1] - 1, b[1] + 2):
        for z in range(a[2] - 1, b[2] + 2):
            for x in range(a[0] - 1, b[0] + 2):
                inx, iny, inz = a[0] <= x <= b[0], a[1] <= y <= b[1], a[2] <= z <= b[2]
                if inx and iny and inz: continue
                if y > b[1]:
                    if not (ceiling and inx and inz): continue
                elif y < a[1]:
                    if not (floor and inx and inz): continue
                elif not sides:
                    continue
                if t.inside(x, y, z) and (x, y, z) not in t.blocks:
                    t.set(x, y, z, rock(rng, ore, ores))


def veins(t, cells, rng, ores=VEIN, p=0.5, clumps=True):
    """Turn lining cells (only NATURAL ones) into ore: each cell with chance p, and in clumps (a hit spreads to a
    neighbour of the same ore) so a face reads as seams rather than confetti."""
    cells = [c for c in cells if t.name_at(*c) in NATURAL]
    for c in cells:
        if rng.random() >= p: continue
        ore = pick(rng, ores)
        t.set(*c, ore)
        if clumps:
            x, y, z = c
            for n in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if n in cells and rng.random() < 0.45: t.set(*n, ore)


def floor(t, a, b, rng, mix=FLOOR):
    """A built floor over the box a..b (usually one layer)."""
    t.fill(a, b, lambda x, y, z: pick(rng, mix))


def rails(t, axis, u0, u1, c, y, rng=None, gap=0.0, twist=0.0):
    """A straight rail along `axis` from u0 to u1 on the centre line c at height y. With an rng, `gap` drops rails
    and `twist` leaves one knocked askew (a wrecked line)."""
    shape = 'east_west' if axis == 'x' else 'north_south'
    other = 'north_south' if axis == 'x' else 'east_west'
    for u in range(min(u0, u1), max(u0, u1) + 1):
        x, z = xz(axis, u, c)
        if rng is not None and chance(rng, gap): continue
        s = shape
        if rng is not None and chance(rng, twist): s = rng.choice([other, 'north_east', 'south_west', 'north_west'])
        t.set(x, y, z, f'rail[shape={s}]')


def lantern(t, x, y, z, hanging=True, kind='lantern'):
    t.set(x, y, z, f'{kind}[hanging={"true" if hanging else "false"},waterlogged=false]')


def timber(t, axis, u, c, y0, state='whole', rng=None, post=POST, height=3):
    """A timber set across a drift at u: two posts in the side walls (w = c-2, c+2) and a log beam over them at
    y0 + height + 1. state: 'whole', 'no_beam', 'left'/'right' (one post gone, the beam's end on the floor),
    'broken' (a snapped post: a stump and a fence splinter) or 'sag' (the beam bowed: slabs where it cracked)."""
    beam_axis = 'z' if axis == 'x' else 'x'
    beam = f'spruce_log[axis={beam_axis}]'
    top = y0 + height + 1
    lo, hi = c - 2, c + 2
    posts = {lo: True, hi: True}
    if state == 'left': posts[lo] = False
    if state == 'right': posts[hi] = False
    for w, standing in posts.items():
        x, z = xz(axis, u, w)
        if standing:
            for y in range(y0 + 1, top):
                t.set(x, y, z, post)
        elif state in ('left', 'right'):
            t.set(x, y0 + 1, z, f'spruce_log[axis={beam_axis}]')   # the fallen post lies at its foot
    if state == 'broken':
        x, z = xz(axis, u, hi)
        t.set(x, y0 + 2, z, 'spruce_fence')
        t.set(x, y0 + 3, z, None)
    if state == 'no_beam':
        return
    for w in range(lo, hi + 1):
        x, z = xz(axis, u, w)
        if state == 'sag' and w in (c - 1, c, c + 1):
            t.set(x, top - 1 if w == c else top, z,
                  'spruce_slab[type=top]' if w == c else 'spruce_slab[type=bottom]')
            if w == c: t.set(x, top, z, None)
            continue
        if state in ('left', 'right') and w == (lo if state == 'left' else hi):
            continue
        t.set(x, top, z, beam)
    if state in ('left', 'right'):
        # the beam has dropped at the missing post's end: a sloped plank run down to the floor
        w0 = lo if state == 'left' else hi
        step = 1 if state == 'left' else -1
        for i, h in enumerate((y0 + 1, y0 + 2, y0 + 3)):
            x, z = xz(axis, u, w0 + step * i)
            facing = {('x', 1): 'south', ('x', -1): 'north', ('z', 1): 'east', ('z', -1): 'west'}[(axis, step)]
            t.set(x, h, z, f'spruce_stairs[facing={facing},half=bottom,shape=straight]')


def drift(t, axis, u0, u1, c, y0, rng, mix=FLOOR, ore=0.04, ores=VEIN, height=3):
    """Open a standard drift along `axis` from u0 to u1 (inclusive) on centre line c: a built floor under the
    whole width (w = c-2..c+2), the open tunnel (w = c-1..c+1, `height` high) and a rock lining in its side walls.
    Build the props after this (they overwrite the lining)."""
    for u in range(min(u0, u1), max(u0, u1) + 1):
        for w in range(c - 2, c + 3):
            x, z = xz(axis, u, w)
            t.set(x, y0, z, pick(rng, mix))
            for y in range(y0 + 1, y0 + height + 1):
                if c - 1 <= w <= c + 1:
                    t.set(x, y, z, 'air')
                elif (x, y, z) not in t.blocks:
                    t.set(x, y, z, rock(rng, ore, ores))


def jig(t, x, y, z, facing, name, target='minecraft:empty', pool='minecraft:empty', rail=True):
    """A horizontal jigsaw on a drift's centre line; it leaves the rail (or air) behind."""
    shape = 'east_west' if facing in ('east', 'west') else 'north_south'
    t.jigsaw(x, y, z, f'{facing}_up', name, target=target, pool=pool,
             final=f'rail[shape={shape}]' if rail else 'air')


def heap(t, x0, x1, z0, z1, y0, height, rng, mix=RUBBLE, slabs=0.5, keep=()):
    """A rubble heap on the floor at y0: height(x, z) full blocks (a float: the fraction tops it with a slab).
    Only open (air) or unset cells are filled; `keep` lists cells to leave alone."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            h = height(x, z)
            if h <= 0: continue
            full = int(h)
            for y in range(y0 + 1, y0 + 1 + full):
                if not t.inside(x, y, z) or (x, y, z) in keep: continue
                if t.name_at(x, y, z) in (None, 'minecraft:air'):
                    t.set(x, y, z, pick(rng, mix))
            y = y0 + 1 + full
            if h - full >= 0.3 and chance(rng, slabs) and t.inside(x, y, z) and (x, y, z) not in keep \
                    and t.name_at(x, y, z) in (None, 'minecraft:air'):
                t.set(x, y, z, rng.choice(RUBBLE_TOP))


def webs(t, cells, rng, p=0.5):
    """Cobwebs in the open cells among `cells`."""
    for c in cells:
        if t.inside(*c) and t.name_at(*c) == 'minecraft:air' and chance(rng, p):
            t.set(*c, 'cobweb')


def candle(t, x, y, z, n=1, lit=False, color=None):
    name = f'{color}_candle' if color else 'candle'
    t.set(x, y, z, f'{name}[candles={n},lit={"true" if lit else "false"},waterlogged=false]')


def skull(t, x, y, z, rotation=0):
    t.set(x, y, z, f'skeleton_skull[rotation={rotation}]')


def remains(t, cells, rng, skull_at=None, rotation=None):
    """What's left of a miner: bone blocks lying about (`cells`, a list of (x, y, z, axis)) and a skull."""
    for x, y, z, axis in cells:
        t.set(x, y, z, f'bone_block[axis={axis}]')
    if skull_at:
        skull(t, *skull_at, rotation=rng.randrange(16) if rotation is None else rotation)


def cart(t, x, y, z, loot=None, facing='east', yaw=None):
    """A minecart (a chest minecart with `loot`). `yaw` (degrees) knocks it askew: a derailed cart."""
    from kit import Float
    t.minecart(x, y, z, loot=loot, facing=facing)
    if yaw is not None:
        t.entities[-1]['nbt']['Rotation'] = [Float(float(yaw)), Float(0.0)]


def sign_lines(*lines):
    return [s[:15] for s in lines]


# -- mirroring (a left turn is a right turn seen in a mirror; jigsaw rotation alone never makes one) --------

_FLIP_Z = {'north': 'south', 'south': 'north'}
_FLIP_SHAPE = {'inner_left': 'inner_right', 'inner_right': 'inner_left', 'outer_left': 'outer_right',
               'outer_right': 'outer_left', 'left': 'right', 'right': 'left'}


def _mirror_props(name, props):
    out = dict(props)
    if 'facing' in props: out['facing'] = _FLIP_Z.get(props['facing'], props['facing'])
    if 'orientation' in props:
        a, b = props['orientation'].split('_')
        out['orientation'] = f'{_FLIP_Z.get(a, a)}_{_FLIP_Z.get(b, b)}'
    if 'shape' in props:
        s = props['shape']
        if name.endswith('rail'):
            s = {'north_east': 'south_east', 'south_east': 'north_east', 'north_west': 'south_west',
                 'south_west': 'north_west', 'ascending_north': 'ascending_south',
                 'ascending_south': 'ascending_north'}.get(s, s)
        else:
            s = _FLIP_SHAPE.get(s, s)
        out['shape'] = s
    if 'hinge' in props: out['hinge'] = _FLIP_SHAPE[props['hinge']]
    if 'north' in props or 'south' in props:
        n, s = props.get('north'), props.get('south')
        out.pop('north', None); out.pop('south', None)
        if s is not None: out['north'] = s
        if n is not None: out['south'] = n
    if 'rotation' in props:   # standing signs, skulls, banners: 16 steps, 0 = south
        out['rotation'] = str((8 - int(props['rotation'])) % 16)
    return out


def mirrored(t, name):
    """A copy of template t mirrored front to back (z), renamed `name`."""
    from kit import Byte, Float
    sx, sy, sz = t.size
    m = Template(name, t.size)
    for (x, y, z), (bname, props) in t.blocks.items():
        m.blocks[(x, y, sz - 1 - z)] = (bname, _mirror_props(bname, props))
    for (x, y, z), nbt in t.nbt.items():
        m.nbt[(x, y, sz - 1 - z)] = nbt
    for j in t.jigsaws:
        x, y, z = j['pos']
        a, b = j['orientation'].split('_')
        m.jigsaws.append({**j, 'pos': (x, y, sz - 1 - z), 'orientation': f'{_FLIP_Z.get(a, a)}_{_FLIP_Z.get(b, b)}'})
    for e in t.entities:
        nbt = dict(e['nbt'])
        x, y, z = e['blockPos']
        px, py, pz = e['pos']
        if 'Rotation' in nbt:
            nbt['Rotation'] = [Float(180.0 - nbt['Rotation'][0]), nbt['Rotation'][1]]
        if 'Facing' in nbt and int(nbt['Facing']) in (2, 3):
            nbt['Facing'] = Byte(5 - int(nbt['Facing']))
        if 'block_pos' in nbt:
            bx, by, bz = nbt['block_pos']
            nbt['block_pos'] = type(nbt['block_pos'])([bx, by, sz - 1 - bz])
        m.entities.append({'pos': [px, py, sz - pz], 'blockPos': [x, y, sz - 1 - z], 'nbt': nbt})
    m.notes = {k: (list(v) if isinstance(v, list) else v) for k, v in t.notes.items()}
    if 'anchor' in m.notes:
        x, y, z = m.notes['anchor']
        m.notes['anchor'] = (x, y, sz - 1 - z)
    return m
