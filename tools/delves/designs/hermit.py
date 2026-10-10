"""Hermit's Hollow: a cosy, mossy mushroom-grove cave where an old Guild miner stayed below decades ago.

The hollow (start piece) is a natural cavern: carved air, a soft lining of moss, rooted dirt, dirt and clay,
and a built floor of podzol, mycelium, packed mud and trodden dirt paths. In it stand a giant red and a giant
brown mushroom (shroomlight tucked under their caps), the hermit's spruce-and-mushroom-stem hut, a lily-pad
pond in a mud basin, a slow mushroom garden, a nether-wart patch for the brews, and a campfire yard. Glow
berries hang from the roof. One way in is a winding, lantern-lit crawl (jigsaw) that climbs toward the outside.
"""

from kit import Byte, Template
from .cavern_parts import Cavern, noise, relax, seal_water, hang, polar, ring_noise, path4, side_of

KEY = 'hermit'
NAME = "Hermit's Hollow"
FEATURES = [
    'a mossy natural cave with two giant mushrooms, the Bishop (red) and Old Thatch (brown), shroomlight under their caps',
    "the hermit's spruce-and-mushroom-stem hut: bed, brewing stand, cauldron, shelves, pantry and keepsake chest",
    'a lectern, "Notes on the Deep": a Guild miner who stayed below, mushrooms, quiet and warnings of the deep',
    'a still pond with lily pads and dripleaf in a mud basin (and Mudge the axolotl), glow berries overhead',
    'a slow mushroom garden named for the lost shift of the Buried Seam, nether wart for the brews, a campfire yard',
    'a winding, lantern-lit crawl that climbs toward the outside and ends in an old roof-fall',
    'home of one resident: the hermit (a cleric), who keeps the brewing stand',
]
STRUCTURE = {
    'start_pool': 'hermit/start', 'size': 4, 'horizontal': 64, 'vertical': 16,
    'min_y': 12, 'max_y': 44, 'cover': 10, 'inhabited': True, 'weight': 2, 'clearance': 10,
}
POOLS = {
    'hermit/start': {'elements': [('hermit/hollow', 1)]},
    'hermit/crawls': {'elements': [('hermit/crawl', 3), ('hermit/crawl_bend', 2)], 'fallback': 'hermit/crawl_ends'},
    'hermit/crawl_ends': {'elements': [('hermit/crawl_end', 1)]},
}

BOOK = [
    "I dug for the Delvers' Guild, with Tamsin for my pick-partner. The day the Seam came down I was up top "
    "fetching lamp oil. Tamsin had said the roof was singing wrong. Nobody listened. I did not either.",
    "We dug nine days. Then the Guild sealed the drift and went home. I stayed. Somebody ought to stay where "
    "they can hear them. That was thirty years ago, near enough. I have learned to like quiet.",
    "Mushrooms want dark, damp and patience. The red one is the Bishop. The brown one is Old Thatch. The "
    "little ones are the shift: Tamsin, Pell, Bramble, Wick. No blue one yet. Slow is a kind of light.",
    "Mudge lives in the pond. Mudge is not a fish. Glow berries keep the hollow lit and taste of nothing, "
    "which is a comfort. Do not eat the roots. Pell's first lantern sits by my brews. I think it is his.",
    "Below, the stone turns to glass that sings: the old ones' holy place. Some years I go down and light "
    "their candles. Deeper, the dead lie in rows. Never go into the Hush. The Listener does not sleep. "
    "Light to you.",
]

# -- small builders -------------------------------------------------------------------------------

FACES = (('north', (0, 0, -1)), ('south', (0, 0, 1)), ('east', (1, 0, 0)), ('west', (-1, 0, 0)),
         ('up', (0, 1, 0)), ('down', (0, -1, 0)))


def place_mushroom(t, blocks):
    """blocks: {(x, y, z): 'red_mushroom_block' | 'brown_mushroom_block' | 'mushroom_stem'}. A face shows the
    cap (or stem) where it meets the open, the pores where it meets another mushroom block."""
    for (x, y, z), name in blocks.items():
        props = ','.join(f'{f}={"false" if (x + d[0], y + d[1], z + d[2]) in blocks else "true"}' for f, d in FACES)
        t.set(x, y, z, f'{name}[{props}]')


def red_mushroom(t, x0, y0, z0, height):
    """A giant red mushroom on the floor at y0 (the stem's first block): a domed cap, its top at y0 + height,
    its skirt hanging three blocks down. Shroomlight is tucked under the top. Returns the cap's cells."""
    top = y0 + height
    b = {}
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            d2 = dx * dx + dz * dz
            if d2 <= 5: b[(x0 + dx, top, z0 + dz)] = 'red_mushroom_block'
            if 5 < d2 <= 13: b[(x0 + dx, top - 1, z0 + dz)] = 'red_mushroom_block'
            if 9 <= d2 <= 13:
                b[(x0 + dx, top - 2, z0 + dz)] = 'red_mushroom_block'
                b[(x0 + dx, top - 3, z0 + dz)] = 'red_mushroom_block'
    for y in range(y0, top): b[(x0, y, z0)] = 'mushroom_stem'
    place_mushroom(t, b)
    for dx, dz in ((1, 0), (-1, 1), (0, -1), (-1, -1)):
        t.set(x0 + dx, top - 1, z0 + dz, 'shroomlight')
    # the hermit's lantern, hung on a chain from the gills
    for y in range(top - 2, y0 + 3, -1): t.set(x0 + 1, y, z0, 'iron_chain[axis=y,waterlogged=false]')
    t.set(x0 + 1, y0 + 3, z0, 'lantern[hanging=true,waterlogged=false]')
    return b


def brown_mushroom(t, x0, y0, z0, height):
    """A giant brown mushroom: a flat, wide cap at y0 + height on a tall stem, shroomlight under the cap."""
    top = y0 + height
    b = {}
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            d2 = dx * dx + dz * dz
            if d2 <= 17: b[(x0 + dx, top, z0 + dz)] = 'brown_mushroom_block'
            if d2 <= 4 and (dx, dz) != (0, 0): b[(x0 + dx, top + 1, z0 + dz)] = 'brown_mushroom_block'
    b[(x0, top + 1, z0)] = 'brown_mushroom_block'
    for y in range(y0, top): b[(x0, y, z0)] = 'mushroom_stem'
    place_mushroom(t, b)
    for dx, dz in ((2, 1), (-2, -1), (1, -3), (-1, 3), (3, -1)):
        t.set(x0 + dx, top - 1, z0 + dz, 'shroomlight')
    return b


def lamp_post(t, x, y, z, tall=2):
    """A spruce-fence post with a lantern on top, standing on the floor at y - 1."""
    for i in range(tall): t.set(x, y + i, z, 'spruce_fence')
    t.set(x, y + tall, z, 'lantern[hanging=false,waterlogged=false]')


def line_cells(points, width=1):
    """Cells along a polyline of (x, z) points; width 2 adds the cell to the +x/+z side."""
    out = set()
    for (x0, z0), (x1, z1) in zip(points, points[1:]):
        n = max(abs(x1 - x0), abs(z1 - z0)) * 3 + 1
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            z = round(z0 + (z1 - z0) * i / n)
            out.add((x, z))
            if width > 1:
                out.add((x + 1, z)); out.add((x, z + 1))
    return out


# -- the hollow (start piece) ---------------------------------------------------------------------

SX, SY, SZ = 28, 18, 28
CX, CZ = 14, 14
FB = 2              # the floor block's y in the flat middle; people walk at W
W = FB + 1
RED = (8, 8)        # stem of the giant red mushroom
BROWN = (19, 20)    # stem of the giant brown mushroom
POND = (19.5, 8.0)
HUT = (4, 13, 10, 19)   # x0, z0, x1, z1 of the hut's walls
DOOR = (10, 16)
GARDEN = (10, 20, 14, 23)
WART = (5, 21, 8, 22)
FIRE = (16, 14)
EXIT_Z = 14


def shape_hollow(t):
    """Carve the cave, lay its floor and fill the pond. Returns (cavern, water cells, path cells)."""
    cav = Cavern(t)
    edge = ring_noise(5)
    roof = noise((SX, SZ), 11, 5)
    bank = noise((SX, SZ), 12, 4)
    forced = {}

    def force(x0, z0, x1, z1, ceil):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                forced[(x, z)] = max(forced.get((x, z), 0), ceil)

    force(HUT[0] - 1, HUT[1] - 1, HUT[2] + 1, HUT[3] + 1, 11)
    force(RED[0] - 3, RED[1] - 3, RED[0] + 3, RED[1] + 3, 12)
    force(BROWN[0] - 4, BROWN[1] - 4, BROWN[0] + 4, BROWN[1] + 4, 11)
    force(WART[0] - 1, WART[1] - 1, GARDEN[2], GARDEN[3], 7)
    force(20, EXIT_Z - 1, 24, EXIT_Z + 1, W + 2)
    force(25, EXIT_Z, SX - 1, EXIT_Z, W + 1)
    for x in range(SX):
        for z in range(SZ):
            a, r = polar(x, z, CX, CZ)
            R = min(12.6, 11.4 + 1.5 * edge(a))
            u = r / R
            if u < 1:
                h = 11.0 * (1 - u ** 4) ** 0.5 + 1.6 * roof[x, z]
                lift = 0 if u < 0.7 else max(0, round((u - 0.7) * 7 + 1.2 * bank[x, z]))
                cav.add_column(x, z, FB + min(lift, 3), FB + max(1, round(h)))
            if (x, z) in forced:
                cav.add_column(x, z, FB, forced[(x, z)])
                cav.floor[(x, z)] = FB
    relax(cav.floor, 1, lower=True)

    # the pond: water flush with the floor, two deep in the middle
    patch = noise((SX, SZ), 13, 5)
    water = set()
    for x in range(14, 26):
        for z in range(3, 14):
            e = ((x - POND[0]) / 3.7) ** 2 + ((z - POND[1]) / 2.7) ** 2 + 0.3 * patch[x, z]
            if e < 1 and (x, z) in cav.floor:
                cav.floor[(x, z)] = FB
                cav.ceil[(x, z)] = max(cav.ceil[(x, z)], W + 4)
                water.add((x, FB, z))
                if e < 0.5: water.add((x, FB - 1, z))
    cav.carve()

    # the floor: built and natural-looking in the middle, soft moss/roots on the banks over a built bed
    moss = noise((SX, SZ), 14, 3)
    for (x, z), f in cav.floor.items():
        t.set(x, f - 1, z, 'packed_mud')
        if (x, f, z) in water: continue
        p, m = patch[x, z], moss[x, z]
        if f > FB:
            top = 'moss_block' if m > -0.3 else ('rooted_dirt' if p > 0 else 'dirt')
        elif (x - RED[0]) ** 2 + (z - RED[1]) ** 2 < 22 or p > 0.5:
            top = 'mycelium[snowy=false]'
        elif p < -0.55:
            top = 'packed_mud'
        elif m > 0.6:
            top = 'mossy_cobblestone'
        else:
            top = 'podzol[snowy=false]'
        t.set(x, f, z, top)
    for (x, y, z) in water:
        t.set(x, y, z, 'water')
        if (x, y - 1, z) not in water:
            t.set(x, y - 1, z, 'muddy_mangrove_roots[axis=y]' if (x + z) % 3 else 'packed_mud')

    # trodden paths: door, yard, pond, the way out, the red mushroom, the garden
    paths = set()
    for pts in ([(DOOR[0] + 1, DOOR[1]), (13, 15), (FIRE[0] - 1, FIRE[1] - 1), (19, 13), (22, EXIT_Z), (SX - 1, EXIT_Z)],
                [(13, 15), (12, 12), (10, 10)], [(17, 12), (18, 11)], [(13, 16), (12, 19), (12, 21)],
                [(12, 17), (11, 20), (9, 21)]):
        paths |= line_cells(pts)
    for (x, z) in paths:
        if (x, z) in cav.floor and cav.floor[(x, z)] == FB and (x, FB, z) not in water:
            t.set(x, FB, z, 'dirt_path')
    return cav, water, paths


def hut(t):
    """The hermit's hut: mushroom-stem walls on spruce posts under a spruce gable roof."""
    x0, z0, x1, z1 = HUT
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            t.set(x, FB, z, 'spruce_planks')
            for y in range(W, W + 3):
                inner = x0 < x < x1 and z0 < z < z1
                corner = x in (x0, x1) and z in (z0, z1)
                if inner: t.set(x, y, z, 'air')
                elif corner: t.set(x, y, z, 'spruce_log[axis=y]')
                elif y == W + 2: t.set(x, y, z, f'stripped_spruce_log[axis={"x" if z in (z0, z1) else "z"}]')
                else: t.set(x, y, z, 'mushroom_stem')
    # gable roof, ridge running along z, one block of eave all round
    for z in range(z0 - 1, z1 + 2):
        for step in range(4):
            y = W + 3 + step
            xa, xb = x0 - 1 + step, x1 + 1 - step
            if xa == xb - 2 and step == 3:
                t.set(xa + 1, y, z, 'spruce_slab[type=bottom,waterlogged=false]')
            for x in range(xa + 1, xb):
                if step < 3: t.set(x, y, z, 'spruce_planks')
            t.set(xa, y, z, 'spruce_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]')
            t.set(xb, y, z, 'spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]')
    # door and windows
    t.door(x1, W, DOOR[1], 'east', hinge='left')
    t.set(7, W + 1, z0, 'glass_pane[east=true,west=true,north=false,south=false,waterlogged=false]')
    t.set(7, W + 1, z1, 'glass_pane[east=true,west=true,north=false,south=false,waterlogged=false]')
    t.set(x0, W + 1, 16, 'glass_pane[north=true,south=true,east=false,west=false,waterlogged=false]')
    # inside: north wall row (z0 + 1)
    t.barrel(5, W, 14, 'up', 'hermit/pantry')
    t.set(6, W, 14, 'water_cauldron[level=2]')
    t.set(7, W, 14, 'brewing_stand')
    t.set(8, W, 14, 'spruce_slab[type=top,waterlogged=false]')
    t.set(8, W + 1, 14, 'lantern[hanging=false,waterlogged=false]')    # Pell's first lantern, found at the Seam
    t.set(9, W, 14, 'chiseled_bookshelf[facing=south]')
    t.set(9, W + 1, 14, 'candle[candles=2,lit=true,waterlogged=false]')
    t.set(5, W + 1, 14, 'spruce_shelf[facing=south]')
    t.set(6, W + 1, 14, 'spruce_shelf[facing=south]')
    # table, chair, bed, lectern, keepsake chest, the old pick on the wall
    t.set(7, W, 16, 'spruce_fence')
    t.set(7, W + 1, 16, 'candle[candles=3,lit=true,waterlogged=false]')
    t.set(6, W, 16, 'spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]')
    t.bed(5, W, 17, 'south', color='brown')
    t.set(6, W, 18, 'potted_brown_mushroom')
    t.lectern(7, W, 18, 'north', 'Notes on the Deep', 'The Hermit', BOOK)
    t.set(8, W, 18, 'barrel[facing=up,open=false]')
    t.set(8, W + 1, 18, 'candle[candles=1,lit=true,waterlogged=false]')
    t.chest(9, W, 18, 'north', 'hermit/shelf')
    t.item_frame(9, W + 1, 17, 'west', 'iron_pickaxe')
    t.set(7, W + 2, 16, 'lantern[hanging=true,waterlogged=false]')
    # outside: porch lanterns under the eave, the sign, a bench against the wall
    t.set(x1 + 1, W + 2, 15, 'lantern[hanging=true,waterlogged=false]')
    t.set(x1 + 1, W + 2, 17, 'lantern[hanging=true,waterlogged=false]')
    t.set(x0, W + 2, z1 + 1, 'lantern[hanging=true,waterlogged=false]')    # under the back eave
    t.sign(x1 + 1, W + 1, 14, ['PLEASE DO NOT', 'EAT THE', 'BLUE ONES', ''], facing='east')
    t.set(x1 + 1, W, z0, 'spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]')


def grounds(t, cav, water, paths):
    """Mushrooms, garden, nether wart, the campfire yard and the pond's edge."""
    rng = t.rng
    red_mushroom(t, RED[0], W, RED[1], 7)
    brown_mushroom(t, BROWN[0], W, BROWN[1], 6)
    t.sign(RED[0] + 1, W + 1, RED[1], ['THE BISHOP', '', 'mind his hat', ''], facing='east')
    t.sign(BROWN[0] - 1, W + 1, BROWN[1], ['OLD THATCH', '', 'keeps the', 'drips off'], facing='west')
    # nether wart for the brews, in soul sand
    for x in range(WART[0], WART[2] + 1):
        for z in range(WART[1], WART[3] + 1):
            t.set(x, FB, z, 'soul_sand')
            t.set(x, W, z, f'nether_wart[age={rng.choice((2, 3, 3))}]')
    # the slow garden: rows of mushrooms on mycelium, a composter, a sign
    gx0, gz0, gx1, gz1 = GARDEN
    for x in range(gx0, gx1 + 1):
        for z in range(gz0, gz1 + 1):
            if (x, z) in paths: continue
            t.set(x, FB, z, 'mycelium[snowy=false]')
            if z != gz0 + 1 and rng.random() < 0.75:
                t.set(x, W, z, 'red_mushroom' if (x + z) % 2 else 'brown_mushroom')
    t.set(gx1, W, gz0 + 1, 'composter[level=5]')
    t.sign(gx1, W, gz0 - 1, ['SLOW GARDEN', 'Tamsin. Pell.', 'Bramble. Wick.', 'Grow easy.'], facing='north', wall=False)
    # campfire yard with log seats
    fx, fz = FIRE
    t.set(fx, W, fz, 'campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]')
    for x, z, axis in ((fx, fz - 2, 'x'), (fx + 1, fz - 2, 'x'), (fx + 2, fz, 'z'), (fx + 2, fz + 1, 'z')):
        t.set(x, W, z, f'stripped_spruce_log[axis={axis}]')
    # the pond: lily pads, dripleaf, a few glow lichen on the shore stones, a bench and a sign
    tops = sorted(p for p in water if (p[0], p[1] + 1, p[2]) not in water)
    for (x, y, z) in tops:
        if rng.random() < 0.3: t.set(x, y + 1, z, 'lily_pad')
    shore = sorted({(x + dx, z + dz) for (x, y, z) in tops for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if (x + dx, y, z + dz) not in water and (x + dx, z + dz) in cav.floor})
    for i, (x, z) in enumerate(shore):
        if cav.floor[(x, z)] != FB or (x, z) in paths: continue
        if i % 5 == 0: t.set(x, FB, z, 'mossy_cobblestone')
        if i % 7 == 3 and t.get(x, W, z) == 'air':
            t.set(x, W, z, 'glow_lichen[down=true,east=false,north=false,south=false,up=false,west=false,waterlogged=false]')
        elif i % 9 == 4 and t.get(x, W, z) == 'air':
            t.set(x, W, z, 'small_dripleaf[facing=south,half=lower,waterlogged=false]')
            t.set(x, W + 1, z, 'small_dripleaf[facing=south,half=upper,waterlogged=false]')
    deep = [p for p in tops if (p[0], p[1] - 1, p[2]) in water]
    for (x, y, z) in deep[1::6][:3]:
        t.set(x, y, z, 'big_dripleaf[facing=west,tilt=none,waterlogged=true]')
    mx, my, mz = deep[len(deep) // 2] if deep else tops[0]
    t.entities.append({'pos': [mx + .5, float(my - 1 if (mx, my - 1, mz) in water else my), mz + .5],
                       'blockPos': [mx, my - 1 if (mx, my - 1, mz) in water else my, mz],
                       'nbt': {'id': 'minecraft:axolotl', 'PersistenceRequired': Byte(1),
                               'FromBucket': Byte(1), 'CustomName': {'text': 'Mudge'}}})
    t.notes['pet'] = 'Mudge (axolotl)'
    t.sign(20, W, 12, ['NO FISHING.', 'THERE ARE', 'NO FISH.', 'ONLY MUDGE.'], facing='south', wall=False)


def mossy_lining(rock, rng, deep_ores=True):
    """Soft lining for the hermit's rock: moss, rooted dirt, dirt and clay next to the air, earth and stone
    behind it (with a little coal and copper for whoever digs)."""
    def pick(x, y, z, d, kind):
        v = rock[x, y, z]
        if d == 1:
            if kind == 'ceiling':
                return 'rooted_dirt' if v > 0.3 else ('moss_block' if v > -0.5 else 'dirt')
            if kind == 'floor':
                return 'moss_block' if v > -0.3 else 'rooted_dirt'
            if v > 0.55: return 'clay'
            if v > 0.28: return 'rooted_dirt'
            if v < -0.62: return 'stone'
            if v < -0.48: return 'dirt'
            return 'moss_block'
        if deep_ores and rng.random() < 0.025: return rng.choice(('coal_ore', 'copper_ore'))
        return 'dirt' if v > -0.1 else ('clay' if v > -0.25 else 'stone')
    return pick


def place_lamp(t, cav, x, z, tall=2):
    """A lantern post on a built floor cell with air above it (skipped where something is in the way)."""
    if (x, z) not in cav.floor: return False
    f = cav.floor[(x, z)]
    if any(t.get(x, y, z) != 'air' for y in range(f + 1, f + tall + 2)): return False
    if t.name_at(x, f, z) in (None, 'minecraft:water') or t.name_at(x, f, z) in SOFT_FLOOR: return False
    lamp_post(t, x, f + 1, z, tall)
    return True


SOFT_FLOOR = {'minecraft:moss_block', 'minecraft:rooted_dirt', 'minecraft:dirt'}


def light_up(t, cav, rounds=16):
    """Hang glow berries over whatever walkable cell is still dark (a rough check: kit.dark_spots)."""
    from kit import dark_spots
    for _ in range(rounds):
        spots = dark_spots(t)
        if not spots: return
        done = []
        for (x, y, z) in spots:
            if any(abs(x - a) + abs(z - b) < 5 for a, b in done): continue
            c = cav.ceil.get((x, z))
            if c is None or c - y < 3: continue
            if hang(t, x, c, z, c - y - 1, 'vines', None):
                done.append((x, z))
        if not done: return


def hollow():
    t = Template('hermit/hollow', (SX, SY, SZ), seed='hermit/hollow')
    rng = t.rng
    cav, water, paths = shape_hollow(t)
    hut(t)
    grounds(t, cav, water, paths)

    # the way out: a lantern niche, the Guild's saying, then the crawl (jigsaw) in the outer face
    t.set(24, FB, EXIT_Z + 2, 'mossy_cobblestone')
    t.set(24, W, EXIT_Z + 2, 'lantern[hanging=false,waterlogged=false]')
    t.sign(21, W, EXIT_Z + 1, ['LIGHT TO YOU.', '', 'And the roof', 'over you.'], facing='east', wall=False)
    t.jigsaw(SX - 1, W, EXIT_Z, 'east_up', 'hermit/hollow_door', target='hermit/crawl_in', pool='hermit/crawls')

    # moss carpet and small plants on the free podzol
    moss = noise((SX, SZ), 16, 3)
    for (x, z), f in sorted(cav.floor.items()):
        if t.name_at(x, f, z) != 'minecraft:podzol' or t.get(x, f + 1, z) != 'air' or (x, z) in paths: continue
        if moss[x, z] > 0.25: t.set(x, f + 1, z, 'moss_carpet')
        elif rng.random() < 0.18: t.set(x, f + 1, z, rng.choice(('short_grass', 'fern', 'brown_mushroom', 'red_mushroom')))

    # the rock: soft moss, roots, dirt and clay; roots, glow berries and spore blossoms from the roof
    rock = noise((SX, SY, SZ), 15, 4)
    cav.lining(mossy_lining(rock, rng), depth=2)
    blossoms = 0
    for (x, c, z) in sorted(cav.ceiling_cells()):
        if t.get(x, c, z) != 'air': continue
        above, room = t.name_at(x, c + 1, z), c - cav.floor[(x, z)]
        if above == 'minecraft:rooted_dirt' and rng.random() < 0.45:
            t.set(x, c, z, 'hanging_roots')
        elif above == 'minecraft:moss_block' and room >= 6 and blossoms < 3 and abs(x - CX) + abs(z - CZ) < 7 \
                and rng.random() < 0.15:
            t.set(x, c, z, 'spore_blossom')
            blossoms += 1
        elif above in ('minecraft:moss_block', 'minecraft:dirt') and room >= 4 and rng.random() < 0.08:
            hang(t, x, c, z, rng.randint(1, min(6, room - 3)), 'vines', rng, berries=0.7)

    for (x, z) in ((12, 10), (22, 11), (9, 23), (23, 18), (15, 5), (5, 11), (16, 24), (25, 9)):
        place_lamp(t, cav, x, z)
    seal_water(t, water, lambda x, y, z: 'mossy_cobblestone' if y == FB else 'packed_mud')

    t.anchor(CX, FB, CZ, floor='dirt_path')
    t.resident(13, W, 15, 'hermit', facing='east')
    t.notes['job_site'] = (7, W, 14)
    light_up(t, cav)
    return t


# -- the crawl (jigsaw tunnels toward the outside) -----------------------------------------------------

def crawl_lining(rock, rng):
    def pick(x, y, z, d, kind):
        v = rock[x, y, z]
        if d == 1:
            if kind == 'ceiling': return 'rooted_dirt' if v > 0.45 else ('moss_block' if v > 0.1 else 'stone')
            if v > 0.42: return 'moss_block'
            if v > 0.22: return 'dirt'
            if v < -0.55: return 'andesite'
            return 'stone'
        return 'coal_ore' if rng.random() < 0.02 else 'stone'
    return pick


def crawl_piece(name, size, points, step_at, exit_orient, lamps, widen, sign=None, rubble=None):
    """A winding squeeze, 2 high and mostly 1 wide, rising one block on mossy steps. `points` is the route
    (entry at x = 0); `lamps` are (route index, side 0/1) for lantern niches; `widen` route indices get a
    second cell beside them."""
    t = Template(name, size, seed=name)
    rng = t.rng
    cav = Cavern(t)
    route = path4(points)
    floor_of = {}
    for i, (x, z) in enumerate(route):
        f = 0 if i < step_at else 1
        h = 3 if i in (step_at - 1, step_at) or (0 < i < len(route) - 1 and rng.random() < 0.2) else 2
        cav.add_column(x, z, f, f + h)
        floor_of[(x, z)] = f
    for i in widen:
        n = side_of(route, i)[i % 2]
        if n not in floor_of and 0 < n[0] < size[0] - 1 and 0 <= n[1] < size[2]:
            cav.add_column(n[0], n[1], floor_of[route[i]], floor_of[route[i]] + 2)
    cav.carve()
    for (x, z), f in cav.floor.items():
        r = rng.random()
        t.set(x, f, z, 'dirt_path' if r < 0.5 else 'mossy_cobblestone' if r < 0.7 else
              'cobblestone' if r < 0.85 else 'packed_mud')
    if step_at < len(route):
        (x, z), (nx, nz) = route[step_at - 1], route[step_at]
        t.set(x, floor_of[(x, z)] + 1, z, f'mossy_cobblestone_stairs[facing={DIRS[(nx - x, nz - z)]},half=bottom,'
                                          f'shape=straight,waterlogged=false]')
    for i, s in lamps:
        nx, nz = side_of(route, i)[s]
        f = floor_of[route[i]]
        if (nx, nz) in cav.floor or not t.inside(nx, f, nz): continue
        t.set(nx, f, nz, 'mossy_cobblestone')
        t.set(nx, f + 1, nz, 'lantern[hanging=false,waterlogged=false]')
    if rubble:
        for (x, y, z), b in rubble.items(): t.set(x, y, z, b)
    if sign:
        x, y, z, facing, lines = sign
        t.sign(x, y, z, lines, facing=facing)
    rock = noise(size, sum(map(ord, name)), 3)
    cav.lining(crawl_lining(rock, rng), depth=2)
    for (x, c, z) in cav.ceiling_cells():
        if t.name_at(x, c + 1, z) == 'minecraft:rooted_dirt' and t.get(x, c, z) == 'air' and rng.random() < 0.5:
            t.set(x, c, z, 'hanging_roots')
    x0, z0 = route[0]
    t.jigsaw(x0, 1, z0, 'west_up', 'hermit/crawl_in')
    if exit_orient:
        x1, z1 = route[-1]
        t.jigsaw(x1, floor_of[(x1, z1)] + 1, z1, exit_orient, 'hermit/crawl_out', target='hermit/crawl_in',
                 pool='hermit/crawls')
    return t


DIRS = {(1, 0): 'east', (-1, 0): 'west', (0, 1): 'south', (0, -1): 'north'}


def crawl():
    return crawl_piece('hermit/crawl', (13, 6, 9), [(0, 4), (3, 4), (3, 2), (7, 2), (7, 6), (12, 6)], 12,
                       'east_up', lamps=[(4, 1), (15, 1)], widen=[1, 7, 16])


def crawl_bend():
    return crawl_piece('hermit/crawl_bend', (10, 6, 10), [(0, 4), (4, 4), (4, 6), (6, 6), (6, 9)], 10,
                       'south_up', lamps=[(2, 1), (10, 0)], widen=[3, 5])


def crawl_end():
    """The crawl ends in an old roof-fall, with the Guild's warning on it."""
    rubble = {(6, 1, 2): 'mossy_cobblestone', (6, 2, 2): 'cobblestone', (6, 3, 2): 'mossy_cobblestone',
              (5, 1, 2): 'mossy_cobblestone_slab[type=bottom,waterlogged=false]', (7, 1, 2): 'cobblestone',
              (6, 1, 1): 'cobblestone', (6, 1, 3): 'mossy_cobblestone', (6, 2, 3): 'cobblestone_slab[type=bottom,waterlogged=false]'}
    return crawl_piece('hermit/crawl_end', (8, 6, 7), [(0, 3), (3, 3), (3, 2), (5, 2)], 99, None,
                       lamps=[(3, 1)], widen=[1], rubble=rubble,
                       sign=(5, 2, 2, 'west', ['MIND THE ROOF.', '', 'Stone gives,', 'stone takes.']))


def pieces():
    return [hollow(), crawl(), crawl_bend(), crawl_end()]
