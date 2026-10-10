"""The Ossuary: the Old Delvers' catacombs, deep in the deepslate. A cross-shaped vaulted crypt (the start)
with the altar, the reliquary behind it, the book of names, two side crypts with skeleton spawners and the
crypt keeper's haunt; niche-lined galleries, junctions, stairs and tombs branch out through the jigsaw and
end in collapses, so explorers break in from several sides. Dim: soul lanterns and a few candles."""
from kit import Template, HORIZONTAL, OPPOSITE, facing_of
from designs.ancient_parts import (bars, candle, chain, crumble, dbricks, face_cells, lantern, lateral,
                                   mark_floor, mark_wall, masonry, pbb, post, skull, slab, stair, tiles,
                                   wall_skull)

KEY = 'ossuary'
NAME = 'The Ossuary'
FEATURES = [
    'a cross-shaped, vaulted central crypt of deepslate tiles, bricks and polished blackstone, its stepped dome '
    'hung with a soul-lantern chandelier over the Delvers\' mark inlaid in the floor',
    'walls of loculi: tiers of niches with laid-out bones, skulls, cobwebs and burned-down candles over a course '
    'of bone blocks, in the crypt and along every gallery',
    'the crypt keeper rises in the crossing (crypt_keeper haunt)',
    'the altar, and behind it the reliquary (ossuary/reliquary) under the Delvers\' mark',
    'a lectern, "Names of the Honoured Dead"',
    'polished-deepslate sarcophagi with their chests sealed under the lid (ossuary/sarcophagus): break the lid',
    'two side crypts, each with a skeleton spawner among the bones',
    'galleries, bone-pillar junctions, stairs and tombs branch out and end in collapses',
]
STRUCTURE = {
    'start_pool': 'ossuary/start', 'size': 4, 'horizontal': 60, 'vertical': 20,
    'min_y': -52, 'max_y': -16, 'cover': 12, 'inhabited': False, 'weight': 2, 'clearance': 10,
}
POOLS = {
    'ossuary/start': {'elements': [('ossuary/crypt', 1)]},
    'ossuary/corridors': {'elements': [('ossuary/gallery', 4), ('ossuary/gallery_fallen', 2), ('ossuary/junction', 2), ('ossuary/steps', 2),
                                       ('ossuary/tomb', 2), ('ossuary/collapse', 1)],
                          'fallback': 'ossuary/ends'},
    'ossuary/ends': {'elements': [('ossuary/collapse', 1)]},
}
DOOR = 'ossuary/door'          # every corridor end; corridors join either way round


def door(t, x, y, z, facing):
    """A jigsaw in the outer face at walking height that grows the next corridor."""
    t.jigsaw(x, y, z, f'{facing}_up', DOOR, target=DOOR, pool='ossuary/corridors')


def end_door(t, x, y, z, facing):
    """The jigsaw a dead-end piece hangs from (it grows nothing)."""
    t.jigsaw(x, y, z, f'{facing}_up', DOOR)


# -- tombs and walls of the dead ---------------------------------------------------------------------

def sarcophagus(t, cx, y, cz, axis, head=-1):
    """A polished-deepslate sarcophagus 3 long (along axis 'x' or 'z') and 3 wide, standing on layer y - 1.
    Its chest is sealed under the slab lid: break the lid to open it. `head` (+1/-1) is the skull's end."""
    ax, az = (1, 0) if axis == 'x' else (0, 1)
    sx, sz = az, ax
    for k in (-1, 0, 1):
        x, z = cx + ax * k, cz + az * k
        for s in (-1, 1):
            t.set(x + sx * s, y, z + sz * s, stair('polished_deepslate_stairs', facing_of(-sx * s, -sz * s)))
        if k == 0:
            t.chest(x, y, z, facing_of(sx, sz), 'ossuary/sarcophagus')
            t.set(x, y + 1, z, slab('polished_deepslate_slab'))
        else:
            t.set(x, y, z, 'polished_deepslate')
    hx, hz = cx + ax * head, cz + az * head
    t.set(hx, y + 1, hz, skull(facing=facing_of(-ax * head, -az * head)))
    t.set(cx - ax * head, y + 1, cz - az * head, candle(t.rng.choice((1, 2, 3)), lit=t.rng.random() < 0.3))


def loculus(t, cells, along, facing, rng, lit=0.15):
    """Fill one niche slot (one or two cells side by side in a wall) with what the dead left."""
    r = rng.random()
    if r < 0.38 and len(cells) == 2:                     # a laid-out skeleton: bones, then the skull
        bones, head = (cells[0], cells[1]) if rng.random() < 0.5 else (cells[1], cells[0])
        t.set(*bones, f'bone_block[axis={along}]')
        t.set(*head, skull(facing=facing))
        return
    for c in cells:
        q = rng.random()
        if r < 0.55: t.set(*c, skull(facing=facing) if q < 0.6 else skull(rng))
        elif r < 0.7: t.set(*c, candle(rng.choice((1, 1, 2, 3)), lit=q < lit * 2))
        elif r < 0.82: t.set(*c, 'cobweb' if q < 0.7 else 'air')
        elif r < 0.9: t.set(*c, f'bone_block[axis={along}]')
        else: t.set(*c, 'air')


def catacomb_wall(t, run, y0, top, facing, rng, niche_rows=(1, 3), lit=0.15):
    """The face of a catacomb wall along `run` [(x, z), ...] (in order), from layer y0 (floor + 1) to `top`:
    a plinth, tiers of niches between polished-blackstone pilasters, a course of bone ends between the tiers.
    The masonry behind the face is the niches' back. `facing` points out of the wall into the room."""
    along = 'x' if facing in ('north', 'south') else 'z'
    across = 'z' if along == 'x' else 'x'
    n = len(run)
    for i, (x, z) in enumerate(run):
        pilaster = i % 3 == 0 or i == n - 1
        for y in range(y0, top + 1):
            h = y - y0
            if pilaster:
                t.set(x, y, z, 'chiseled_polished_blackstone' if h == 0 else pbb(rng))
            elif h == 0:
                t.set(x, y, z, 'polished_deepslate')
            elif h in niche_rows:
                pass                                     # filled below, two at a time
            elif h == 2:
                t.set(x, y, z, f'bone_block[axis={across}]')
            else:
                t.set(x, y, z, dbricks(rng))
    for h in niche_rows:
        i = 0
        while i < n:
            if i % 3 == 0 or i == n - 1:
                i += 1
                continue
            j = i + 1 if i + 1 < n and (i + 1) % 3 != 0 and i + 1 != n - 1 else i
            cells = [(run[k][0], y0 + h, run[k][1]) for k in range(i, j + 1)]
            loculus(t, cells, along, facing, rng, lit)
            i = j + 1


def haunches(t, run, y, facing, block='deepslate_tile_stairs'):
    """Upside-down stairs along the top of a wall, springing the vault (`facing` points out of the wall)."""
    for x, z in run:
        t.set(x, y, z, stair(block, OPPOSITE[facing], 'top'))


def cobwebs(t, cells, rng, p):
    for c in cells:
        if rng.random() < p and t.get(*c) == 'air':
            t.set(*c, 'cobweb')


# -- the central crypt (start) --------------------------------------------------------------------

ROOMS = {                                   # interiors (inclusive), floor at y = 0
    'crossing': ((11, 1, 11), (19, 8, 19)),
    'apse': ((12, 1, 5), (18, 6, 10)),
    'reliquary': ((13, 1, 1), (17, 3, 3)),
    'nave': ((12, 1, 20), (18, 6, 29)),
    'west': ((1, 1, 12), (10, 6, 18)),
    'east': ((20, 1, 12), (29, 6, 18)),
    'sw': ((2, 1, 22), (8, 4, 28)),
    'se': ((22, 1, 22), (28, 4, 28)),
}
MASS = [((10, 0, 4), (20, 7, 10)), ((12, 0, 0), (18, 4, 4)), ((10, 0, 20), (20, 7, 30)), ((0, 0, 10), (10, 7, 20)),
        ((20, 0, 10), (30, 7, 20)), ((10, 0, 10), (20, 10, 20)), ((12, 11, 12), (18, 11, 18)),
        ((0, 0, 20), (9, 5, 30)), ((21, 0, 20), (30, 5, 30))]


def crypt_shell(t):
    r = t.rng
    for lo, hi in MASS:
        masonry(t, lo, hi, lambda x, y, z: dbricks(r))
    for lo, hi in ROOMS.values():
        t.carve(lo, hi)
        t.fill((lo[0], 0, lo[2]), (hi[0], 0, hi[2]), lambda x, y, z: tiles(r))
        t.fill((lo[0], hi[1] + 1, lo[2]), (hi[0], hi[1] + 1, hi[2]), lambda x, y, z: tiles(r, 0.1))
    t.carve((12, 9, 12), (18, 9, 18))                         # the stepped dome over the crossing
    t.carve((13, 10, 13), (17, 10, 17))
    t.fill((13, 11, 13), (17, 11, 17), lambda x, y, z: tiles(r, 0.1))
    t.set(15, 11, 15, 'chiseled_polished_blackstone')
    for x in range(12, 19):                                   # runners down the arms
        for z in list(range(5, 11)) + list(range(20, 30)):
            if x == 15: t.set(x, 0, z, 'polished_deepslate')
    for z in range(12, 19):
        for x in list(range(1, 11)) + list(range(20, 30)):
            if z == 15: t.set(x, 0, z, 'polished_deepslate')

    # walls of the dead: two tiers of loculi in every arm, one in the side crypts
    arms = [([(11, z) for z in range(5, 11)], 'east'), ([(19, z) for z in range(5, 11)], 'west'),
            ([(11, z) for z in range(20, 30)], 'east'), ([(19, z) for z in range(20, 30)], 'west'),
            ([(x, 11) for x in range(1, 11)], 'south'), ([(x, 19) for x in range(1, 11)], 'north'),
            ([(x, 11) for x in range(20, 30)], 'south'), ([(x, 19) for x in range(20, 30)], 'north')]
    for run, facing in arms:
        catacomb_wall(t, run, 1, 6, facing, r)
        dx, dz = HORIZONTAL[facing]
        inner = [(x + dx, z + dz) for x, z in run]
        haunches(t, inner, 6, facing)
        for i, (x, z) in enumerate(inner):                    # ribs over the pilasters
            if i % 3 == 0 or i == len(inner) - 1:
                t.set(x, 6, z, stair('polished_blackstone_brick_stairs', OPPOSITE[facing], 'top'))
    for x0, z0 in ((12, 5), (12, 8), (12, 10), (12, 20), (12, 23), (12, 26), (12, 29)):
        t.fill((x0, 7, z0), (x0 + 6, 7, z0), lambda x, y, z: pbb(r))
    for x0, z0 in ((1, 12), (4, 12), (7, 12), (10, 12), (20, 12), (23, 12), (26, 12), (29, 12)):
        t.fill((x0, 7, z0), (x0, 7, z0 + 6), lambda x, y, z: pbb(r))
    for run, facing in (([(1, z) for z in range(22, 29)], 'east'), ([(x, 21) for x in range(2, 9)], 'south'),
                        ([(x, 29) for x in range(2, 9)], 'north'), ([(29, z) for z in range(22, 29)], 'west'),
                        ([(x, 29) for x in range(22, 29)], 'north'), ([(21, z) for z in range(22, 29)], 'east')):
        catacomb_wall(t, run, 1, 4, facing, r, niche_rows=(1,), lit=0.0)

    # the crossing: corner piers and a dome stepping up in rings
    for x, z in ((11, 11), (19, 11), (11, 19), (19, 19)):
        for y in range(1, 9):
            t.set(x, y, z, 'chiseled_polished_blackstone' if y in (1, 6) else pbb(r))
        t.set(x, 8, z, 'chiseled_polished_blackstone')
    for y, lo, hi in ((8, 11, 19), (9, 12, 18), (10, 13, 17)):
        for x in range(lo, hi + 1):
            for z in range(lo, hi + 1):
                if lo < x < hi and lo < z < hi: continue
                if (x in (lo, hi)) and (z in (lo, hi)):
                    if y > 8: t.set(x, y, z, 'polished_blackstone_bricks')
                    continue
                out = 'west' if x == lo else 'east' if x == hi else 'north' if z == lo else 'south'
                t.set(x, y, z, stair('deepslate_tile_stairs', out, 'top'))

    # doorways: three ways out (jigsaws go in last), the reliquary door, the side crypts' doors
    for lo, hi in (((14, 1, 30), (16, 3, 30)), ((0, 1, 14), (0, 3, 16)), ((30, 1, 14), (30, 3, 16))):
        t.carve(lo, hi)
    for x in range(13, 18): t.set(x, 4, 30, 'chiseled_deepslate')
    for z in range(13, 18):
        t.set(0, 4, z, 'chiseled_deepslate')
        t.set(30, 4, z, 'chiseled_deepslate')
    t.carve((15, 1, 4), (15, 2, 4))
    t.carve((9, 1, 26), (11, 2, 26))
    t.carve((26, 1, 19), (26, 2, 21))
    for x, y, z in ((9, 3, 26), (10, 3, 26), (11, 3, 26), (26, 3, 19), (26, 3, 20), (26, 3, 21)):
        t.set(x, y, z, 'chiseled_deepslate')

    # crumbling outer walls, so a passing cave can break in
    for (lo, hi), sides in (((MASS[0]), ('west', 'east')), ((MASS[2]), ('west', 'east')), ((MASS[3]), ('north', 'south')),
                            ((MASS[4]), ('north', 'south')), ((MASS[7]), ('west', 'south')), ((MASS[8]), ('east', 'south'))):
        for side in sides:
            cells = [c for c in face_cells(lo, hi, side) if 1 <= c[1] <= hi[1] - 1 and t.get(*c) and
                     t.get(*c).startswith(('deepslate_bricks', 'cracked_deepslate_bricks'))]
            crumble(t, cells, r, 0.07)


NAMES = [
    "Names of the\nHonoured Dead\n\nHere lie those who\ndug the deepest\nand gave the most\nto the stone.\n\n"
    "Say each name once\nand softly, and\nthe lamps will\nstay lit.",
    "ORM BRASKEL\ncut the first step\nof the Hundred\nStair.\n\nVALDA TWO-LAMPS\nwalked nine days\nin the dark and\n"
    "led the lost\nshift home.",
    "HUSK THE ELDER\nraised the pillars\nof the cistern.\n\nANNIRA DEEPEAR\nheard gold singing\nbehind a wall\n"
    "of iron stone.",
    "TORVEN THE SMITH\nwhose anvil rings\nbelow us still.\n\nKELL AND KELLA,\ntwins, who held up\nthe falling roof\n"
    "until the last\nchild was out.",
    "BRISA LAMPWARD\nkept the lamps for\nsixty winters and\nlet none go out.\n\nGORM WHO-WENT-DOWN\n"
    "followed the vein\npast the last mark.\nWe wait for him.",
    "The stair is shut.\nThe lamps are\ngiven to the\nKeeper. No more\nnames will be cut.\n\n\n"
    "(beneath, in a\nnewer hand)\n\nOne more.",
]


def crypt_furnish(t):
    r = t.rng
    # the altar, and behind it the reliquary under the Delvers' mark
    for x in range(13, 18):
        t.set(x, 1, 7, 'chiseled_polished_blackstone' if x in (13, 17) else 'polished_blackstone_bricks')
        if 14 <= x <= 16: t.set(x, 1, 8, stair('polished_blackstone_brick_stairs', 'north'))
    t.set(15, 1, 7, 'gilded_blackstone')
    t.set(14, 2, 7, candle(3, lit=True))
    t.set(16, 2, 7, candle(2, lit=True))
    t.set(15, 2, 7, skull(facing='south'))
    t.set(13, 2, 7, lantern('soul_lantern'))
    t.set(17, 2, 7, candle(1))
    mark_wall(t, 15, 3, 5, 'south', light='soul_lantern')
    t.set(12, 1, 5, 'bone_block[axis=y]'); t.set(12, 2, 5, skull(r))
    t.set(18, 1, 5, 'cobweb'); t.set(18, 5, 6, 'cobweb')
    t.fill((13, 0, 1), (17, 0, 3), 'polished_blackstone')
    t.set(15, 0, 2, 'gilded_blackstone')
    t.set(15, 1, 1, 'chiseled_polished_blackstone')
    t.chest(15, 2, 1, 'south', 'ossuary/reliquary')
    for x in (14, 16):
        t.set(x, 1, 1, 'polished_blackstone_bricks')
        t.set(x, 2, 1, lantern('soul_lantern'))
    for x in (13, 17):
        for z in (1, 2, 3):
            t.set(x, 1, z, 'bone_block[axis=z]')
            t.set(x, 2, z, skull(facing='east' if x == 13 else 'west') if z != 2 else candle(4, lit=x == 13))
    t.fill((13, 1, 0), (17, 3, 0), lambda x, y, z: 'gilded_blackstone' if (x + y) % 3 == 0 else pbb(r, 0.05))
    t.set(13, 3, 3, 'cobweb'); t.set(17, 3, 1, 'cobweb')
    t.lectern(18, 1, 9, 'west', 'Names of the Honoured Dead', 'the Lampwardens', NAMES)
    t.item_frame(14, 1, 5, 'up', 'stone_pickaxe')                   # someone came for the reliquary once
    t.sign(13, 2, 29, ['Here sleep', 'the Honoured.', 'Go softly,', 'and go lit.'], 'north', wood='dark_oak')
    t.set(18, 1, 10, 'bone_block[axis=y]'); t.set(18, 2, 10, candle(2))

    # the crossing: the mark in the floor, candle stands, the keeper's chandelier, the keeper itself
    mark_floor(t, 15, 0, 16, 'north', ink='bone_block[axis=y]', head='polished_blackstone')
    for x, z in ((12, 12), (18, 12), (12, 18), (18, 18)):
        t.set(x, 1, z, post('polished_blackstone_wall'))
        t.set(x, 2, z, candle(r.choice((2, 3)), lit=r.random() < 0.6))
    for y in range(7, 11): t.set(15, y, 15, 'iron_chain[axis=y,waterlogged=false]')
    t.set(15, 6, 15, lantern('soul_lantern', hanging=True))
    t.haunt(15, 1, 16, 'crypt_keeper')

    # sarcophagi: the honoured pair in the west transept, one in the east, one in each side crypt
    sarcophagus(t, 4, 1, 15, 'x', head=-1)
    sarcophagus(t, 8, 1, 15, 'x', head=1)
    sarcophagus(t, 24, 1, 15, 'x', head=1)
    sarcophagus(t, 3, 1, 25, 'z', head=-1)
    sarcophagus(t, 25, 1, 27, 'x', head=1)

    # the side crypts: a skeleton spawner among heaped bones, no light but a dead candle
    for (sx, sz), heaps in (((6, 24), ((7, 27), (7, 22), (2, 28), (5, 28))),
                            ((23, 24), ((27, 23), (22, 28), (28, 25), (24, 22)))):
        t.spawner(sx, 1, sz, 'minecraft:skeleton')
        for hx, hz in heaps:
            t.set(hx, 1, hz, f'bone_block[axis={r.choice("xzy")}]')
            t.set(hx, 2, hz, skull(r) if r.random() < 0.7 else candle(1))
    for x, y, z in ((2, 4, 22), (8, 4, 28), (8, 4, 22), (22, 4, 28), (28, 4, 22), (28, 4, 28), (5, 1, 22),
                    (27, 1, 27), (2, 3, 22)):
        if t.get(x, y, z) == 'air': t.set(x, y, z, 'cobweb')

    # the arms: one soul lantern each (dim), bones fallen from the niches, webs in the vaults
    for x, z in ((15, 8), (15, 24), (3, 13), (27, 17)):
        t.set(x, 6, z, lantern('soul_lantern', hanging=True))
    for x, z in ((12, 28), (18, 21), (17, 29), (1, 12), (10, 18), (29, 12), (20, 18), (21, 13), (13, 10)):
        if t.get(x, 1, z) == 'air':
            t.set(x, 1, z, r.choice(('bone_block[axis=x]', 'bone_block[axis=z]', skull(r), 'cobbled_deepslate')))
    upper = [(x, 5, z) for lo, hi in (ROOMS['apse'], ROOMS['nave'], ROOMS['west'], ROOMS['east'])
             for x in range(lo[0], hi[0] + 1) for z in range(lo[2], hi[2] + 1)
             if x in (lo[0], hi[0]) or z in (lo[2], hi[2])]
    cobwebs(t, upper, r, 0.12)

    # where the delve stands, and the three ways out
    t.anchor(15, 0, 15, floor='deepslate_tiles')
    door(t, 15, 1, 30, 'south')
    door(t, 0, 1, 15, 'west')
    door(t, 30, 1, 15, 'east')


def crypt():
    t = Template('ossuary/crypt', (31, 12, 31))
    crypt_shell(t)
    crypt_furnish(t)
    return t


# -- corridors ----------------------------------------------------------------------------------------

def gallery(fallen=False):
    """A straight gallery 13 long between walls of loculi, vaulted, with a joint at each end. The fallen one has
    lost part of its vault: a rubble heap under a patch of raw rock, and a side wall gone to rock."""
    t = Template('ossuary/gallery_fallen' if fallen else 'ossuary/gallery', (13, 7, 7), seed=91 if fallen else 17)
    r = t.rng
    masonry(t, (0, 0, 0), (12, 6, 6), lambda x, y, z: dbricks(r))
    t.carve((0, 1, 2), (12, 5, 4))
    t.fill((0, 0, 2), (12, 0, 4), lambda x, y, z: 'polished_deepslate' if z == 3 and x % 4 == 2 else tiles(r))
    t.fill((0, 6, 2), (12, 6, 4), lambda x, y, z: tiles(r, 0.1))
    for run, facing in (([(x, 1) for x in range(13)], 'south'), ([(x, 5) for x in range(13)], 'north')):
        catacomb_wall(t, run, 1, 5, facing, r)
        dx, dz = HORIZONTAL[facing]
        haunches(t, [(x + dx, z + dz) for x, z in run], 5, facing)
    for x in (0, 3, 6, 9, 12):
        t.fill((x, 6, 2), (x, 6, 4), lambda x_, y, z: pbb(r))
        for z, f in ((2, 'south'), (4, 'north')):
            t.set(x, 5, z, stair('polished_blackstone_brick_stairs', OPPOSITE[f], 'top'))
    crumble(t, face_cells((0, 1, 0), (12, 5, 0), 'north') + face_cells((0, 1, 6), (12, 5, 6), 'south'), r, 0.1)
    if fallen:
        for (x, z), h in (((5, 3), 3), ((6, 3), 2), ((4, 3), 2), ((5, 2), 2), ((6, 4), 1), ((7, 2), 1), ((4, 4), 1),
                          ((7, 3), 1), ((5, 4), 1), ((3, 2), 1)):
            for y in range(1, h + 1):
                t.set(x, y, z, r.choice(('cobbled_deepslate', 'cobbled_deepslate', 'deepslate_tiles', 'gravel')))
            t.set(x, h + 1, z, r.choice(('cobbled_deepslate_slab[type=bottom,waterlogged=false]', 'air', 'air')))
        t.set(5, 4, 3, skull(r)); t.set(7, 2, 3, 'bone_block[axis=x]')
        t.fill((4, 6, 2), (7, 6, 4), 'deepslate')                     # the vault gave way to raw rock
        t.fill((4, 5, 2), (7, 5, 4), 'air')
        for x in range(4, 8):                                        # and the south wall with it
            for y in range(2, 6):
                t.set(x, y, 5, r.choice(('deepslate', 'deepslate', 'tuff', 'cobbled_deepslate')))
                t.set(x, y, 6, 'deepslate')
    else:
        t.set(6, 5, 3, lantern('soul_lantern', hanging=True))
        t.set(2, 1, 4, 'bone_block[axis=x]'); t.set(10, 1, 2, skull(r))
    cobwebs(t, [(x, 4, z) for x in range(13) for z in (2, 4)], r, 0.12)
    door(t, 0, 1, 3, 'west')
    door(t, 12, 1, 3, 'east')
    return t


def junction():
    """A square charnel chamber where three galleries meet round a pillar of bones crowned with skulls."""
    t = Template('ossuary/junction', (11, 8, 11), seed=23)
    r = t.rng
    masonry(t, (0, 0, 0), (10, 7, 10), lambda x, y, z: dbricks(r))
    t.carve((2, 1, 2), (8, 5, 8))
    t.carve((3, 6, 3), (7, 6, 7))
    t.fill((2, 0, 2), (8, 0, 8), lambda x, y, z: 'polished_blackstone' if x in (2, 8) or z in (2, 8) else tiles(r))
    for x, z in ((3, 3), (7, 3), (3, 7), (7, 7)):
        t.set(x, 0, z, 'chiseled_deepslate')
    for x in range(3, 8):
        for z in range(3, 8):
            if x in (3, 7) or z in (3, 7):
                out = 'west' if x == 3 else 'east' if x == 7 else 'north' if z == 3 else 'south'
                if x in (3, 7) and z in (3, 7): t.set(x, 6, z, 'polished_blackstone_bricks')
                else: t.set(x, 6, z, stair('deepslate_tile_stairs', out, 'top'))
    catacomb_wall(t, [(9, z) for z in range(1, 10)], 1, 5, 'west', r)
    for x0, z0, side in ((1, 1, 'n'), (1, 9, 's')):
        catacomb_wall(t, [(x, z0) for x in range(1, 4)], 1, 5, 'south' if side == 'n' else 'north', r)
        catacomb_wall(t, [(x, z0) for x in range(7, 10)], 1, 5, 'south' if side == 'n' else 'north', r)
    for z in list(range(1, 4)) + list(range(7, 10)):
        for y in range(1, 6): t.set(1, y, z, pbb(r))
    for y in range(1, 6):                                            # the bone pillar
        t.set(5, y, 5, 'bone_block[axis=y]' if y != 3 else 'chiseled_polished_blackstone')
    for f in ('north', 'south', 'east', 'west'):
        dx, dz = HORIZONTAL[f]
        t.set(5 + dx, 4, 5 + dz, wall_skull(f))
        t.set(5 + dx, 2, 5 + dz, wall_skull(f) if r.random() < 0.7 else candle(2))
    t.set(5, 6, 5, 'polished_blackstone_bricks')
    for x, z in ((2, 2), (8, 8), (2, 8)):
        t.set(x, 1, z, f'bone_block[axis={r.choice("xz")}]')
        t.set(x, 2, z, skull(r))
    t.set(8, 1, 2, candle(3, lit=True))
    for lo, hi in (((0, 1, 4), (1, 3, 6)), ((4, 1, 0), (6, 3, 1)), ((4, 1, 9), (6, 3, 10))):
        t.carve(lo, hi)
    crumble(t, face_cells((0, 1, 0), (10, 5, 10), 'east'), r, 0.08)
    cobwebs(t, [(x, 5, z) for x in range(2, 9) for z in range(2, 9) if x in (2, 8) or z in (2, 8)], r, 0.15)
    door(t, 0, 1, 5, 'west')
    door(t, 5, 1, 0, 'north')
    door(t, 5, 1, 10, 'south')
    return t


def steps():
    """A stair of four steps between two galleries (it goes up or down, whichever end joins first)."""
    t = Template('ossuary/steps', (12, 10, 7), seed=31)
    r = t.rng
    floor = {x: 4 if x <= 2 else 3 if x == 3 else 2 if x == 4 else 1 if x == 5 else 0 for x in range(12)}
    for x in range(12):
        f = floor[x]
        walk = f + 1
        masonry(t, (x, 0, 0), (x, walk + 4, 6), lambda x_, y, z: dbricks(r))
        t.carve((x, walk, 2), (x, walk + 3, 4))
        for z in range(2, 5):
            if 3 <= x <= 5:
                t.set(x, f, z, stair('deepslate_tile_stairs', 'west'))
            else:
                t.set(x, f, z, 'polished_deepslate' if z == 3 else tiles(r))
        t.fill((x, walk + 4, 2), (x, walk + 4, 4), lambda x_, y, z: tiles(r, 0.1))
        for z, facing in ((1, 'south'), (5, 'north')):
            for y in range(walk, walk + 4):
                h = y - walk
                if x % 3 == 0: t.set(x, y, z, pbb(r))
                elif h == 0: t.set(x, y, z, 'polished_deepslate')
                elif h == 2: t.set(x, y, z, f'bone_block[axis={"z"}]')
                elif h == 1 and x % 3 == 1: loculus(t, [(x, y, z)], 'x', facing, r, lit=0.0)
            t.set(x, walk + 3, z + (1 if z == 1 else -1), stair('deepslate_tile_stairs', OPPOSITE[facing], 'top'))
    t.set(4, 7, 3, chain())
    t.set(4, 6, 3, lantern('soul_lantern', hanging=True))
    crumble(t, face_cells((0, 1, 0), (11, 8, 0), 'north') + face_cells((0, 1, 6), (11, 8, 6), 'south'), r, 0.1)
    t.set(9, 1, 2, skull(r)); t.set(1, 5, 4, 'cobweb'); t.set(10, 4, 4, 'cobweb')
    door(t, 0, 5, 3, 'west')
    door(t, 11, 1, 3, 'east')
    return t


def tomb():
    """A dead-end family tomb: two sarcophagi, walls of loculi, a small altar with the mark above it."""
    t = Template('ossuary/tomb', (12, 7, 11), seed=47)
    r = t.rng
    masonry(t, (0, 0, 0), (11, 6, 10), lambda x, y, z: dbricks(r))
    t.carve((2, 1, 2), (9, 4, 8))
    t.carve((0, 1, 4), (1, 3, 6))
    t.fill((0, 0, 2), (9, 0, 8), lambda x, y, z: tiles(r))
    t.fill((2, 5, 2), (9, 5, 8), lambda x, y, z: pbb(r) if x in (2, 5, 9) else tiles(r, 0.1))
    catacomb_wall(t, [(x, 1) for x in range(1, 11)], 1, 4, 'south', r)
    catacomb_wall(t, [(x, 9) for x in range(1, 11)], 1, 4, 'north', r)
    catacomb_wall(t, [(10, z) for z in range(1, 10)], 1, 4, 'west', r, niche_rows=(3,))
    for z in (2, 3, 7, 8):
        for y in range(1, 5): t.set(1, y, z, pbb(r))
    sarcophagus(t, 5, 1, 3, 'x', head=1)
    sarcophagus(t, 5, 1, 7, 'x', head=1)
    for z in (4, 5, 6):                                              # the little altar at the back
        t.set(9, 1, z, 'chiseled_polished_blackstone' if z != 5 else 'polished_blackstone_bricks')
    t.set(9, 2, 4, candle(2, lit=True)); t.set(9, 2, 6, candle(1))
    t.set(9, 2, 5, skull(facing='west'))
    mark_wall(t, 9, 3, 5, 'west', light='soul_lantern')
    t.set(8, 1, 8, 'bone_block[axis=x]'); t.set(8, 2, 8, skull(r))
    t.set(2, 4, 2, 'cobweb'); t.set(2, 4, 8, 'cobweb'); t.set(8, 4, 2, 'cobweb')
    crumble(t, face_cells((0, 1, 0), (11, 4, 10), 'east'), r, 0.1)
    end_door(t, 0, 1, 5, 'west')
    return t


def collapse():
    """Where a gallery fell in: a slope of rubble and bones up to raw rock (a cave beyond breaks through)."""
    t = Template('ossuary/collapse', (6, 6, 5), seed=59)
    r = t.rng
    masonry(t, (0, 0, 0), (2, 5, 4), lambda x, y, z: dbricks(r))
    t.fill((3, 0, 0), (5, 5, 4), 'deepslate')
    t.fill((0, 0, 1), (4, 0, 3), lambda x, y, z: tiles(r, 0.3))
    t.carve((0, 1, 1), (4, 4, 3))
    for x, h in ((1, 0), (2, 1), (3, 2), (4, 3)):
        for z in (1, 2, 3):
            hh = max(0, h + r.choice((-1, 0, 0, 1)))
            for y in range(1, hh + 1):
                t.set(x, y, z, r.choice(('cobbled_deepslate', 'cobbled_deepslate', 'gravel', 'deepslate_tiles', 'tuff')))
            if hh < 4:
                t.set(x, hh + 1, z, r.choice(('cobbled_deepslate_slab[type=bottom,waterlogged=false]', 'air', 'air',
                                               'bone_block[axis=x]')))
    t.set(1, 1, 2, skull(r)); t.set(0, 1, 1, candle(1)); t.set(0, 4, 3, 'cobweb')
    t.fill((2, 5, 1), (4, 5, 3), 'deepslate')
    end_door(t, 0, 1, 2, 'west')
    return t


def pieces():
    return [crypt(), gallery(), gallery(fallen=True), junction(), steps(), tomb(), collapse()]
