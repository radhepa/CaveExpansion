"""The Sunken Forge: the Old Delvers' great forge-hall over a lava lake. The start piece is the whole hall:
the great hearth with its bellows, banks of blast furnaces and smokers behind lava channels bridged by stone,
the colossal anvil under a hanging hammer, the Smith's Rule on its lectern, forge stores, and across the lake,
over a broken bridge, the masterwork vault. Passages, forks, stairs and storerooms lead out through the jigsaw.
Lit by the lava; dark everywhere else. Every lava source sits in a built basin (see ancient_parts.check_lava)."""
from kit import Template, HORIZONTAL, OPPOSITE
from designs.ancient_parts import (bars, chain, check_lava, crumble, face_cells, lantern, mark_wall, masonry,
                                   pbb, post, slab, stair, tiles)

KEY = 'forge'
NAME = 'The Sunken Forge'
FEATURES = [
    'a great forge-hall of polished blackstone bricks and deepslate tiles over a lava lake, pillars capped in '
    'gold under a ribbed vault, iron chains hanging from the beams',
    'the great hearth: lava behind an iron grate, two stone-and-leather bellows blowing into it through copper '
    'nozzles, the Delvers\' mark on its chimney breast',
    'banks of blast furnaces and smokers along both walls, behind lava channels bridged by stone',
    'the colossal anvil (iron blocks on a blackstone foot) on its dais, a great hammer hanging over it on chains, '
    'working anvils and quench troughs round it',
    'a lectern, "The Smith\'s Rule"',
    'forge stores in the corners and side rooms (forge/supplies)',
    'the masterwork vault on an island across the lava, reached over a narrow, broken bridge (forge/vault)',
    'crucibles of lava hanging over the lake',
    'cinders rise in the hall (cinder haunt)',
    'passages, forks, stairs and storerooms lead out and end in rubble',
]
STRUCTURE = {
    'start_pool': 'forge/start', 'size': 4, 'horizontal': 60, 'vertical': 20,
    'min_y': -50, 'max_y': -28, 'cover': 12, 'inhabited': False, 'weight': 1, 'clearance': 14,
    'chance': 0.45,   # the rarest delve: it takes under half the spots the set offers it
}
POOLS = {
    'forge/start': {'elements': [('forge/hall', 1)]},
    'forge/passages': {'elements': [('forge/passage', 3), ('forge/passage_slag', 2), ('forge/fork', 2), ('forge/stair', 2), ('forge/stores', 2),
                                    ('forge/rubble', 1)],
                       'fallback': 'forge/ends'},
    'forge/ends': {'elements': [('forge/rubble', 1)]},
}
DOOR = 'forge/door'


def door(t, x, y, z, facing):
    t.jigsaw(x, y, z, f'{facing}_up', DOOR, target=DOOR, pool='forge/passages')


def end_door(t, x, y, z, facing):
    t.jigsaw(x, y, z, f'{facing}_up', DOOR)


RULE = [
    "THE SMITH'S RULE\n\nas it is kept at\nthe Forge under\nthe Lantern.\n\nRead it before you\nlift the hammer.\n"
    "Read it again when\nyou set it down.",
    "I. The fire is lent\nto us, not given.\nReturn it as you\nfound it.\n\nII. Strike once\nwith thought, not\n"
    "twice in anger.\n\nIII. What the stone\ngives, make worthy.",
    "IV. Quench in\nsilence. The iron\nis listening.\n\nV. No blade leaves\nthis hall unnamed,\nand no name is\n"
    "given unearned.\n\nVI. Feed the lake\nnothing that lives.",
    "VII. The masterwork\nstays across the\nfire. Who would\ntake it must cross\nas the metal does:\n"
    "through the heat,\nand alone.\n\nVIII. When the\nlamps fail, bank\nthe hearth and go\nup. Do not wait.\n\n- Torven",
]


# -- the forge-hall (start) ---------------------------------------------------------------------------
# x 0..30 runs from the hearth end to the vault end, z 0..22 across. Layers: y 0 footing, y 1..2 the platform's
# fill (or the lake's two layers of lava), y 3 the hall floor (walk at y 4), the vault of the roof at y 16.

SIZE = (31, 17, 23)
LAKE_X = 19                                   # the lake runs from here to the far wall
ISLAND = ((24, 7), (29, 15))                  # the vault's island, walls included (x, z)
CHANNELS = (3, 19)                            # lava channels along the furnace banks (z), x 7..18
PILLARS = [(x, z) for x in (5, 10, 15, 21) for z in (6, 16)]


def wall_stone(r):
    def pick(x, y, z):
        if y <= 3: return 'polished_blackstone'
        if y == 4: return 'polished_blackstone_bricks'
        if y in (9, 13): return 'gilded_blackstone' if r.random() < 0.12 else 'deepslate_tiles'
        return pbb(r)
    return pick


def on_island(x, z):
    (x0, z0), (x1, z1) = ISLAND
    return x0 <= x <= x1 and z0 <= z <= z1


def hall_shell(t):
    r = t.rng
    sx, sy, sz = SIZE
    for lo, hi in (((0, 0, 0), (sx - 1, sy - 1, 0)), ((0, 0, sz - 1), (sx - 1, sy - 1, sz - 1)),
                   ((0, 0, 0), (0, sy - 1, sz - 1)), ((sx - 1, 0, 0), (sx - 1, sy - 1, sz - 1))):
        masonry(t, lo, hi, wall_stone(r))
    t.fill((1, 16, 1), (29, 16, 21), lambda x, y, z: tiles(r, 0.08))
    t.fill((1, 0, 1), (29, 0, 21), 'polished_blackstone')
    t.carve((1, 4, 1), (29, 15, 21))
    # the platform and its floor; the lake (two layers of lava) beyond it; the island under the vault
    t.fill((1, 1, 1), (LAKE_X - 1, 2, 21), 'polished_blackstone')
    for x in range(1, LAKE_X):
        for z in range(1, 22):
            edge = z in (1, 21) or x in (1, LAKE_X - 1)
            aisle = 9 <= z <= 13 and x >= 4
            t.set(x, 3, z, 'polished_blackstone_bricks' if edge else 'polished_deepslate' if aisle and z in (9, 13)
                  else tiles(r, 0.2))
    for x in range(LAKE_X, 30):
        for z in range(1, 22):
            if on_island(x, z):
                t.fill((x, 1, z), (x, 2, z), 'polished_blackstone')
            else:
                t.fill((x, 1, z), (x, 2, z), 'lava')
                t.set(x, 3, z, 'air')
    # lava channels in the floor, a trench one deep, running into the lake
    for z in CHANNELS:
        for x in range(7, LAKE_X):
            t.set(x, 2, z, 'lava')
            t.set(x, 3, z, 'air')
        for x in range(7, LAKE_X):                                   # kerbs either side
            for dz in (-1, 1):
                if t.get(x, 3, z + dz) and 'tiles' in t.get(x, 3, z + dz):
                    t.set(x, 3, z + dz, 'polished_blackstone')
    # pillars (two in the lake) with gold capitals, beams and arches under a ribbed vault
    for px, pz in PILLARS:
        base = 1 if px >= LAKE_X else 4
        for y in range(base, 16):
            b = pbb(r, 0.08)
            if y == base or y == 13: b = 'chiseled_polished_blackstone'
            if y == 12: b = 'gold_block' if px >= LAKE_X else 'gilded_blackstone'   # gold only out in the lava
            t.set(px, y, pz, b)
        if px < LAKE_X: t.set(px, 3, pz, 'polished_blackstone')
    for pz in (6, 16):
        t.fill((1, 15, pz), (29, 15, pz), lambda x, y, z: pbb(r, 0.05))
    for px in (5, 10, 15, 21):
        t.fill((px, 15, 1), (px, 15, 21), lambda x, y, z: pbb(r, 0.05))
    for px, pz in PILLARS:
        for f in ('north', 'south', 'east', 'west'):
            dx, dz = HORIZONTAL[f]
            t.set(px + dx, 14, pz + dz, stair('polished_blackstone_brick_stairs', OPPOSITE[f], 'top'))
    for x in range(1, 30):                                            # cornice along the long walls
        for z, f in ((1, 'north'), (21, 'south')):
            if t.get(x, 15, z) == 'air': t.set(x, 15, z, stair('polished_blackstone_brick_stairs', f, 'top'))
    for z in range(1, 22):
        for x, f in ((1, 'west'), (29, 'east')):
            if t.get(x, 15, z) == 'air': t.set(x, 15, z, stair('polished_blackstone_brick_stairs', f, 'top'))


def hall_hearth(t):
    """The great hearth against the end wall: lava behind a grate, bellows either side, the mark above."""
    r = t.rng
    for z in range(8, 15):
        for y in range(4, 6):
            if 9 <= z <= 13:
                t.set(1, y, z, pbb(r, 0.05))
                t.set(2, y, z, 'lava' if y == 4 else 'air')
                t.set(3, y, z, bars('north', 'south'))
            else:
                t.set(1, y, z, pbb(r, 0.05))
                t.set(3, y, z, 'chiseled_polished_blackstone')
        t.set(1, 6, z, pbb(r, 0.05)); t.set(2, 6, z, pbb(r, 0.05))
        t.set(3, 6, z, 'gold_block' if z in (8, 14) else stair('polished_blackstone_brick_stairs', 'west', 'top'))
    t.set(2, 4, 8, 'lightning_rod[facing=south,powered=false,waterlogged=false]')     # the bellows' nozzles
    t.set(2, 4, 14, 'lightning_rod[facing=north,powered=false,waterlogged=false]')
    t.set(2, 5, 8, pbb(r, 0)); t.set(2, 5, 14, pbb(r, 0))
    for y in range(7, 10):                                                           # the chimney breast
        for z in range(9, 14):
            t.set(1, y, z, pbb(r, 0.05)); t.set(2, y, z, pbb(r, 0.05))
    for y in range(10, 16):
        for z in range(10, 13): t.set(1, y, z, pbb(r, 0.05))
    for y in (7, 9): t.set(2, y, 9, stair('polished_blackstone_brick_stairs', 'south', 'top')); t.set(2, y, 13, stair('polished_blackstone_brick_stairs', 'north', 'top'))
    mark_wall(t, 3, 8, 11, 'east', light='lantern', pick='golden_pickaxe')
    # bellows: a leather bag between stone boards, tapering to the nozzle, a chain to work them from above
    for bag, taper, f in (((5, 6), 7, 'north'), ((16, 17), 15, 'south')):
        for z in bag:
            for x in (1, 2):
                t.set(x, 4, z, 'brown_terracotta')
                t.set(x, 5, z, slab('polished_blackstone_slab'))
        for x in (1, 2):
            t.set(x, 4, taper, stair('polished_blackstone_brick_stairs', f))
        for y in range(6, 15): t.set(1, y, bag[0] if f == 'north' else bag[1], chain())


def hall_works(t):
    """Furnace banks behind the channels, the colossal anvil and its hammer, the book, the stores."""
    r = t.rng
    for z, f, wall in ((1, 'south', 'north'), (21, 'north', 'south')):
        for x in range(7, 18):
            if z == 1 and 12 <= x <= 14: continue                     # the third doorway
            if x in (7, 11, 15):
                for y in range(4, 15): t.set(x, y, z, 'chiseled_polished_blackstone' if y in (4, 12) else pbb(r))
                continue
            kind = 'smoker' if x in (9, 13, 17) else 'blast_furnace'
            t.set(x, 4, z, f'{kind}[facing={f},lit=false]')
            t.set(x, 5, z, stair('polished_blackstone_brick_stairs', wall))
            t.set(x, 6, z, pbb(r))
            t.set(x, 7, z, stair('polished_blackstone_brick_stairs', wall))
    for x, z in ((9, 3), (16, 3), (13, 19), (9, 19), (17, 19)):                  # bridges over the channels
        t.set(x, 3, z, slab('polished_blackstone_brick_slab', 'top'))
    for x in (12, 13, 14):
        t.set(x, 3, 3, 'chiseled_polished_blackstone')
    # the colossal anvil on its dais
    for x in range(7, 14):
        for z in range(9, 14):
            corner = x in (7, 13) and z in (9, 13)
            if corner: b = 'chiseled_polished_blackstone'
            elif z == 9: b = stair('polished_blackstone_brick_stairs', 'south')
            elif z == 13: b = stair('polished_blackstone_brick_stairs', 'north')
            elif x == 7: b = stair('polished_blackstone_brick_stairs', 'east')
            elif x == 13: b = stair('polished_blackstone_brick_stairs', 'west')
            else: b = 'polished_blackstone_bricks'
            t.set(x, 4, z, b)
    t.fill((8, 5, 10), (12, 5, 12), 'polished_blackstone')
    t.fill((9, 6, 11), (11, 6, 11), 'polished_blackstone')
    for x in (9, 10, 11):
        t.set(x, 6, 10, stair('polished_blackstone_stairs', 'south', 'top'))
        t.set(x, 6, 12, stair('polished_blackstone_stairs', 'north', 'top'))
    t.set(8, 6, 11, stair('polished_blackstone_stairs', 'east', 'top'))
    t.set(12, 6, 11, stair('polished_blackstone_stairs', 'west', 'top'))
    t.fill((8, 7, 10), (12, 7, 12), 'iron_block')
    t.set(13, 7, 11, 'iron_block')
    t.set(14, 7, 11, 'heavy_core[waterlogged=false]')
    t.set(7, 7, 11, stair('polished_blackstone_brick_stairs', 'east', 'top'))
    for y in range(13, 15):                                        # the great hammer, hung over it on chains
        t.set(9, y, 11, chain()); t.set(11, y, 11, chain())
    t.fill((9, 12, 11), (11, 12, 11), 'polished_basalt[axis=x]')
    for y in range(9, 12): t.set(10, y, 11, post('polished_blackstone_wall'))
    t.item_frame(11, 8, 11, 'up', 'iron_sword')                    # the last work, never finished
    for spec, (x, z) in (('anvil[facing=east]', (6, 9)), ('chipped_anvil[facing=north]', (14, 13)),
                         ('damaged_anvil[facing=south]', (14, 9)), ('chipped_anvil[facing=west]', (12, 2)),
                         ('anvil[facing=east]', (10, 20))):
        t.set(x, 4, z, spec)
    for x, z in ((6, 13), (14, 10), (16, 2), (8, 20)):
        t.set(x, 4, z, 'water_cauldron[level=3]' if r.random() < 0.6 else 'cauldron')
    t.lectern(6, 4, 11, 'west', "The Smith's Rule", 'Torven of the Forge', RULE)
    # the stores in the two corners by the doors
    t.chest(1, 4, 2, 'east', 'forge/supplies')
    t.set(1, 4, 1, 'barrel[facing=up,open=false]')
    t.set(2, 4, 1, 'barrel[facing=up,open=false]'); t.set(1, 5, 1, 'barrel[facing=east,open=false]')
    t.set(1, 4, 3, 'raw_iron_block'); t.set(3, 4, 1, 'smithing_table')
    t.chest(1, 4, 20, 'east', 'forge/supplies')
    t.set(1, 4, 21, 'barrel[facing=up,open=false]')
    t.set(2, 4, 21, 'barrel[facing=up,open=false]'); t.set(1, 4, 19, 'raw_gold_block')
    t.set(3, 4, 21, 'cauldron')
    t.set(17, 4, 20, 'barrel[facing=up,open=false]')
    for x, z, ax in ((8, 15, 'x'), (4, 7, 'z'), (16, 18, 'x')):          # chains dropped on the floor
        t.set(x, 4, z, chain(ax))


def hall_vault(t):
    """The lake's edge, the broken bridge and the masterwork vault on its island across the lava."""
    r = t.rng
    edge = LAKE_X - 1
    for z in range(1, 22):                                             # a broken parapet along the shore
        if z in CHANNELS or 10 <= z <= 12 or z in (6, 16) or r.random() < 0.25: continue
        t.set(edge, 4, z, post('polished_blackstone_brick_wall', north='low', south='low'))
    for x, b in ((19, 'polished_blackstone_bricks'), (20, 'cracked_polished_blackstone_bricks'),
                 (22, slab('polished_blackstone_brick_slab', 'top')), (23, 'polished_blackstone_bricks')):
        t.set(x, 3, 11, b)                                             # x = 21: the gap you jump
    for y in range(10, 15): t.set(21, y, 11, chain())                  # a snapped chain over the gap
    # the vault: walls on the island, a gilded door facing the bridge, the hall's far wall at its back
    (x0, z0), (x1, z1) = ISLAND
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            t.set(x, 3, z, 'gilded_blackstone' if (x + z) % 2 == 0 and x > x0 and z0 < z < z1 else 'polished_blackstone')
            for y in range(4, 10):
                wall = x == x0 or z in (z0, z1)
                if wall:
                    b = 'polished_blackstone' if x == x0 and z in (z0, z1) else pbb(r, 0.06)
                    if y == 9: b = 'deepslate_tiles'
                    t.set(x, y, z, b)
                else:
                    t.set(x, y, z, tiles(r, 0.05) if y == 9 else 'air')
            if x == x0 or z in (z0, z1):
                t.set(x, 10, z, post('polished_blackstone_brick_wall'))
    for z in (z0, z1): t.set(x0, 10, z, 'gold_block')
    t.set(27, 3, 11, 'gold_block')
    t.carve((x0, 4, 11), (x0, 6, 11))
    t.set(x0, 3, 11, 'chiseled_polished_blackstone')
    for z in (10, 12):
        for y in range(4, 7): t.set(x0, y, z, 'chiseled_polished_blackstone')
    t.set(x0, 7, 11, 'gold_block'); t.set(x0, 8, 11, 'gilded_blackstone')
    t.set(x0, 7, 10, stair('polished_blackstone_brick_stairs', 'north', 'top'))
    t.set(x0, 7, 12, stair('polished_blackstone_brick_stairs', 'south', 'top'))
    t.set(28, 4, 11, 'chiseled_polished_blackstone')
    t.chest(28, 5, 11, 'west', 'forge/vault', custom_name='The Masterwork')
    t.notes['vault'] = (28, 5, 11)
    mark_wall(t, 29, 6, 11, 'west', light='lantern', pick='golden_pickaxe')
    for z in (8, 14): t.set(29, 4, z, 'lava_cauldron')
    t.set(25, 4, 8, 'smithing_table'); t.set(25, 4, 14, 'anvil[facing=north]')
    t.set(29, 4, 11, 'polished_blackstone_bricks'); t.set(29, 5, 11, 'air')
    for z in (9, 13):
        t.set(28, 4, z, 'polished_blackstone_bricks')
        t.set(28, 5, z, 'candle[candles=3,lit=false,waterlogged=false]')
    # crucibles of lava hanging over the lake on chains
    for x, z, low in ((26, 4, 8), (26, 18, 9), (20, 2, 10)):
        for y in range(low + 1, 16): t.set(x, y, z, chain())
        t.set(x, low, z, 'lava_cauldron')


def hall():
    t = Template('forge/hall', SIZE, seed=7)
    r = t.rng
    hall_shell(t)
    hall_hearth(t)
    hall_works(t)
    hall_vault(t)
    for x, z in ((8, 4), (16, 4), (6, 18), (12, 18), (17, 14)):          # heat under foot near the lava
        t.set(x, 3, z, 'magma_block')
    for x, y, z in ((3, 14, 3), (29, 14, 21), (2, 13, 20), (10, 14, 1)):
        if t.get(x, y, z) == 'air': t.set(x, y, z, 'cobweb')
    t.haunt(16, 4, 11, 'cinder')
    for lo, hi in (((4, 4, 0), (6, 6, 0)), ((4, 4, 22), (6, 6, 22)), ((12, 4, 0), (14, 6, 0))):
        t.carve(lo, hi)
        for x in range(lo[0], hi[0] + 1): t.set(x, 7, lo[2], 'chiseled_polished_blackstone')
        t.set(lo[0] + 1, 8, lo[2], 'gilded_blackstone')
    walls = [c for side, (lo, hi) in (('north', ((0, 6, 0), (30, 14, 0))), ('south', ((0, 6, 22), (30, 14, 22))),
                                      ('west', ((0, 6, 0), (0, 14, 22))))
             for c in face_cells(lo, hi, side) if (t.get(*c) or '').startswith(('polished_blackstone_bricks', 'cracked_'))]
    crumble(t, walls, r, 0.05, soft='blackstone')
    t.anchor(11, 3, 15, floor='deepslate_tiles')
    door(t, 5, 4, 0, 'north')
    door(t, 5, 4, 22, 'south')
    door(t, 13, 4, 0, 'north')
    check_lava(t)
    return t


# -- passages -----------------------------------------------------------------------------------------

def passage(slag=False):
    """A straight Delver passage, 11 long, ribbed every five; the slag one is half choked with old slag."""
    t = Template('forge/passage_slag' if slag else 'forge/passage', (11, 7, 5), seed=113 if slag else 101)
    r = t.rng
    masonry(t, (0, 0, 0), (10, 6, 4), lambda x, y, z: 'deepslate_tiles' if y == 3 and z in (0, 4) else pbb(r))
    t.carve((0, 1, 1), (10, 5, 3))
    t.fill((0, 0, 1), (10, 0, 3), lambda x, y, z: 'polished_blackstone' if z == 2 and x % 5 == 0 else tiles(r, 0.2))
    for x in range(11):
        for z, f in ((1, 'north'), (3, 'south')):
            rib = x % 5 == 0
            t.set(x, 5, z, stair('polished_blackstone_brick_stairs' if rib else 'deepslate_tile_stairs', f, 'top'))
        if x % 5 == 0:
            t.set(x, 6, 2, 'chiseled_polished_blackstone')
            for z in (0, 4): t.set(x, 1, z, 'chiseled_polished_blackstone')
    crumble(t, face_cells((0, 1, 0), (10, 5, 0), 'north') + face_cells((0, 1, 4), (10, 5, 4), 'south'), r, 0.1,
            soft='blackstone')
    if slag:
        for x, z, h in ((3, 1, 2), (4, 1, 3), (5, 1, 2), (6, 1, 1), (4, 2, 1), (7, 1, 1), (2, 1, 1)):
            for y in range(1, h + 1):
                t.set(x, y, z, r.choice(('blackstone', 'basalt[axis=y]', 'cobbled_deepslate', 'blackstone')))
        t.set(5, 1, 2, 'magma_block'); t.set(6, 1, 3, slab('cobbled_deepslate_slab'))
        t.set(8, 1, 3, 'chipped_anvil[facing=north]')
    else:
        for y in range(2, 5): t.set(5, y, 2, chain())
        t.set(2, 1, 3, chain('x')); t.set(8, 4, 1, 'cobweb')
    door(t, 0, 1, 2, 'west')
    door(t, 10, 1, 2, 'east')
    return t


def fork():
    """Where three passages meet: a square room round a cold brazier, the Delvers' mark on the blind wall."""
    t = Template('forge/fork', (9, 7, 9), seed=127)
    r = t.rng
    masonry(t, (0, 0, 0), (8, 6, 8), lambda x, y, z: 'deepslate_tiles' if y == 3 else pbb(r))
    t.carve((1, 1, 1), (7, 5, 7))
    t.fill((1, 0, 1), (7, 0, 7), lambda x, y, z: 'polished_blackstone_bricks' if x in (1, 7) or z in (1, 7) else tiles(r))
    for x, z in ((1, 1), (7, 1), (1, 7), (7, 7)):
        for y in range(1, 6): t.set(x, y, z, 'chiseled_polished_blackstone' if y in (1, 5) else pbb(r))
    for x in range(2, 7):
        for z, f in ((1, 'north'), (7, 'south')): t.set(x, 5, z, stair('polished_blackstone_brick_stairs', f, 'top'))
    for z in range(2, 7):
        for x, f in ((1, 'west'), (7, 'east')): t.set(x, 5, z, stair('polished_blackstone_brick_stairs', f, 'top'))
    t.set(4, 1, 4, 'polished_blackstone_bricks')
    t.set(4, 2, 4, 'campfire[facing=north,lit=false,signal_fire=false,waterlogged=false]')
    for y in range(3, 6): t.set(4, y, 4, chain())
    mark_wall(t, 4, 2, 7, 'north', light='lantern', pick='iron_pickaxe')
    t.set(2, 1, 6, 'barrel[facing=up,open=false]'); t.set(6, 1, 2, 'cauldron'); t.set(2, 4, 2, 'cobweb')
    for lo, hi in (((0, 1, 3), (0, 3, 5)), ((3, 1, 0), (5, 3, 0)), ((8, 1, 3), (8, 3, 5))):
        t.carve(lo, hi)
    crumble(t, face_cells((0, 1, 8), (8, 5, 8), 'south'), r, 0.08, soft='blackstone')
    door(t, 0, 1, 4, 'west')
    door(t, 4, 1, 0, 'north')
    door(t, 8, 1, 4, 'east')
    return t


def stair_piece():
    """Four steps up or down between passages."""
    t = Template('forge/stair', (12, 10, 5), seed=131)
    r = t.rng
    floor = {x: 4 if x <= 2 else 3 if x == 3 else 2 if x == 4 else 1 if x == 5 else 0 for x in range(12)}
    for x in range(12):
        f = floor[x]
        masonry(t, (x, 0, 0), (x, f + 5, 4), lambda x_, y, z: 'deepslate_tiles' if y == f + 3 and z in (0, 4) else pbb(r))
        t.carve((x, f + 1, 1), (x, f + 4, 3))
        for z in range(1, 4):
            t.set(x, f, z, stair('polished_blackstone_brick_stairs', 'west') if 3 <= x <= 5 else tiles(r, 0.15))
        for z, side in ((1, 'north'), (3, 'south')):
            t.set(x, f + 4, z, stair('deepslate_tile_stairs', side, 'top'))
    crumble(t, face_cells((0, 1, 0), (11, 8, 0), 'north') + face_cells((0, 1, 4), (11, 8, 4), 'south'), r, 0.1,
            soft='blackstone')
    t.set(9, 1, 1, chain('z')); t.set(1, 8, 3, 'cobweb')
    door(t, 0, 5, 2, 'west')
    door(t, 11, 1, 2, 'east')
    return t


def stores():
    """A dead-end forge store: barrels and a chest of supplies, racks of bars, heaps of ore and coal."""
    t = Template('forge/stores', (9, 6, 9), seed=137)
    r = t.rng
    masonry(t, (0, 0, 0), (8, 5, 8), lambda x, y, z: pbb(r))
    t.carve((1, 1, 1), (7, 4, 7))
    t.carve((0, 1, 3), (0, 3, 5))
    t.fill((1, 0, 1), (7, 0, 7), lambda x, y, z: tiles(r, 0.2))
    t.fill((1, 5, 1), (7, 5, 7), lambda x, y, z: 'polished_blackstone_bricks' if x == 4 else tiles(r, 0.1))
    t.set(7, 1, 1, 'barrel[facing=up,open=false]')
    t.set(7, 1, 7, 'barrel[facing=up,open=false]')
    t.chest(7, 1, 4, 'west', 'forge/supplies')
    for x, y, z in ((6, 1, 1), (7, 2, 1), (6, 1, 7), (7, 1, 6), (7, 1, 2)):
        t.set(x, y, z, f'barrel[facing={r.choice(("up", "north", "east"))},open=false]')
    for x in range(2, 6):                                             # racks of bars along both walls
        t.set(x, 2, 1, bars('east', 'west')); t.set(x, 2, 7, bars('east', 'west'))
        t.set(x, 1, 1, 'polished_blackstone_slab[type=top,waterlogged=false]')
        t.set(x, 1, 7, 'polished_blackstone_slab[type=top,waterlogged=false]')
    for x, z, b in ((3, 3, 'raw_iron_block'), (4, 3, 'raw_iron_block'), (3, 5, 'raw_copper_block'),
                    (4, 5, 'coal_block'), (5, 5, 'coal_block'), (3, 4, 'raw_gold_block')):
        t.set(x, 1, z, b)
    t.set(4, 2, 3, 'raw_iron_block'); t.set(5, 1, 3, chain('x')); t.set(1, 4, 7, 'cobweb'); t.set(6, 4, 2, 'cobweb')
    t.set(1, 1, 1, 'chipped_anvil[facing=east]')
    crumble(t, face_cells((0, 1, 0), (8, 4, 8), 'east'), r, 0.06, soft='blackstone')
    end_door(t, 0, 1, 4, 'west')
    return t


def rubble():
    """A passage that fell in long ago: a slope of slag and blackstone up to raw rock."""
    t = Template('forge/rubble', (6, 6, 5), seed=139)
    r = t.rng
    masonry(t, (0, 0, 0), (2, 5, 4), lambda x, y, z: pbb(r, 0.3))
    t.fill((3, 0, 0), (5, 5, 4), 'blackstone')
    t.fill((0, 0, 1), (4, 0, 3), lambda x, y, z: tiles(r, 0.4))
    t.carve((0, 1, 1), (4, 4, 3))
    for x, h in ((1, 0), (2, 1), (3, 2), (4, 3)):
        for z in (1, 2, 3):
            hh = max(0, h + r.choice((-1, 0, 0, 1)))
            for y in range(1, hh + 1):
                t.set(x, y, z, r.choice(('cobbled_deepslate', 'blackstone', 'basalt[axis=y]', 'gravel',
                                         'cracked_polished_blackstone_bricks')))
            if hh < 4 and r.random() < 0.5:
                t.set(x, hh + 1, z, slab('cobbled_deepslate_slab'))
    t.fill((2, 5, 1), (4, 5, 3), 'blackstone')
    t.set(1, 1, 1, chain('z')); t.set(0, 4, 3, 'cobweb')
    end_door(t, 0, 1, 2, 'west')
    return t


def pieces():
    return [hall(), passage(), passage(slag=True), fork(), stair_piece(), stores(), rubble()]
