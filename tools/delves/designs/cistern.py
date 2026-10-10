"""The Drowned Cistern: a waterworks of the Old Delvers, long abandoned and half flooded. A vaulted hall of stone
bricks and deepslate tiles, a groin vault on two rows of pillars, walkways along three walls, the floor a black
basin of still water five deep (seven over the sump), a pillared causeway across the middle, and under the west
wall, behind a rusted grate, the sunken vault. Off the east walkway, the sluice room: its great copper wheel, its
levers, its chained gate, and the waterwarden's ledger beside what is left of the waterwarden.

Start piece 'cistern/hall' (32 x 20 x 27): basin floor y 2, water y 3..7, walkway floor y 8 (people walk at y 9),
vault springing at y 14, crown at y 18. Hall walls x 4 / 25, z 0 / 26; basin x 5..21, z 4..22; walkways z 1..3,
z 23..25 and x 22..24; the causeway x 11..15; the sunken vault x 1..3, z 11..15 (y 1..5); the sluice room x 25..31,
z 8..18. Dim on purpose: a few sea lanterns under water, soul lanterns and candle stubs.
"""
import math

from kit import Template
from designs.masonry_parts import (OLD_BRICKS, OLD_TILES, ROCK, connect, hang, line, line_rock, mix, pick, rubble,
                                   slab, stair)

KEY = 'cistern'
NAME = 'The Drowned Cistern'
FEATURES = [
    'a vaulted Old Delver reservoir: groin vaults on two rows of pillars, ribs of polished deepslate',
    'the basin: still water five blocks deep held in deepslate-tile walls, seven over the sump',
    'a pillared causeway across the middle, arched underneath so you can swim beneath it',
    'walkways along three walls with broken railings, ledge barrels and burned-down candles',
    'the sunken vault behind a rusted iron grate at the bottom of the sump (one bar gone): its chest',
    "the Old Delvers' lantern-and-picks mark inlaid in gold over the vault",
    'the sluice room: a great oxidized-copper wheel dipping into the channel, a chained sluice gate, three levers',
    "the Waterwarden's Ledger on its lectern, beside the waterwarden's bones",
    'the drowned wake by the water stairs',
    'a corner of the vault fallen in, open to the caves; old conduits lead away in two or three directions',
]
STRUCTURE = {
    'start_pool': 'cistern/start', 'size': 2, 'horizontal': 56, 'vertical': 24,
    'min_y': -24, 'max_y': 16, 'cover': 10, 'inhabited': False, 'weight': 2, 'require': None, 'clearance': 10,
}
POOLS = {
    'cistern/start': {'elements': [('cistern/hall', 1)]},
    'cistern/tunnels': {'elements': [('cistern/conduit', 4), ('cistern/steps_up', 1), ('cistern/steps_down', 1),
                                     ('cistern/bend_left', 1), ('cistern/bend_right', 1)],
                        'fallback': 'cistern/ends'},
    'cistern/ends': {'elements': [('cistern/collapse', 2), ('cistern/outfall', 1)]},
}

SX, SY, SZ = 32, 20, 27
BF, WT, WF, WW = 2, 7, 8, 9     # basin floor, water top, walkway floor, walking height
H0, RISE = 14, 4                # vault springing and rise
XL = [4, 9, 13, 17, 25]         # vault bay lines (walls and pillar rows)
ZL = [0, 8, 13, 18, 26]
PILLARS = [(x, z) for x in (9, 17) for z in (8, 13, 18)]
PIERS = (8, 13, 18)             # causeway piers (z)
WATER = 'water[level=0]'

LEDGER = [
    'LEDGER OF THE WATERS\nkept by the Warden of the Seventh Cistern\n\nLevel at the ninth mark. Sluice open two '
    'turns. The forge-halls drink well. The lamps below burn clear.',
    'Level at the eleventh mark. The water rises and no rain falls above. The wheel will not turn past three. '
    'Sent a diver to the grate. He says the water is warm, and it hums.',
    'The vault is shut and the grate set with our mark. What we keep there is not to be spent.\n\nLevel at the '
    'twelfth mark. The diver did not come up. His lamp did.',
    'The halls above are emptying. The smiths went down and did not come back up. I keep the waters. The level '
    'does not fall. At night I hear the wheel turning, and no hand on it.',
    'Last mark. The water is at the walk.\n\nWhoever reads: do not open the sluice. Do not swim at night. They are '
    'still at their posts below, and they are still keeping the water.',
]


# -- the basin, the sump and the sunken vault -------------------------------------------------------------

def basin(t, rng):
    """Solid deepslate-tile substructure under the whole hall, then the water let into it."""
    t.fill((4, BF, 0), (25, WF, 26), mix(rng, OLD_TILES))
    t.fill((5, BF + 1, 4), (21, WT, 22), WATER)
    t.carve((5, WF, 4), (21, WF, 22))                                  # open water under the hall
    # the sump in front of the vault: two deeper
    t.fill((4, 0, 10), (8, BF - 1, 16), mix(rng, OLD_TILES))
    t.fill((5, 1, 11), (7, BF, 15), WATER)
    # sea lanterns in the basin floor, few and far apart
    for x, z in ((6, 6), (19, 20), (16, 5)):
        t.set(x, BF, z, 'sea_lantern')
    # weed and wreckage on the floor
    for _ in range(26):
        x, z = rng.randint(5, 21), rng.randint(4, 22)
        if t.name_at(x, BF + 1, z) != 'minecraft:water': continue
        r = rng.random()
        if r < 0.45:
            t.set(x, BF + 1, z, 'seagrass')
        elif r < 0.7:
            h = rng.randint(1, 3)
            for y in range(BF + 1, BF + h):
                t.set(x, y, z, 'kelp_plant')
            t.set(x, BF + h, z, 'kelp[age=20]')
        elif r < 0.85:
            t.set(x, BF + 1, z, f'sea_pickle[pickles={rng.randint(1, 3)},waterlogged=true]')
        else:
            t.set(x, BF + 1, z, pick(rng, [('cobbled_deepslate', 2), ('cracked_deepslate_tiles', 1),
                                         ('stone_bricks', 1)]))


def vault(t, rng):
    """The sunken vault under the west wall: flooded, gold-inlaid, behind a grate with one bar rusted away."""
    t.fill((0, 0, 10), (4, 6, 16), mix(rng, OLD_TILES))
    t.fill((1, 0, 11), (3, 0, 15), 'polished_blackstone_bricks')
    t.fill((1, 1, 11), (3, 5, 15), WATER)
    for z in (11, 15):
        t.set(1, 5, z, stair('polished_blackstone_brick', 'west', 'top', wet=True))
        t.set(1, 1, z, 'gold_block')
    t.fill((1, 1, 12), (1, 1, 14), slab('polished_blackstone', wet=True))
    t.chest(1, 2, 13, 'east', 'cistern/vault', custom_name='Waterwarden\'s Trust')
    name, props = t.blocks[(1, 2, 13)]
    t.blocks[(1, 2, 13)] = (name, {**props, 'waterlogged': 'true'})
    t.set(1, 1, 13, 'polished_blackstone')
    t.set(3, 1, 12, 'bone_block[axis=x]')
    t.set(3, 1, 14, f'sea_pickle[pickles=2,waterlogged=true]')
    t.set(2, 5, 13, 'sea_lantern')
    # the grate across the vault mouth (x = 4): iron bars, under water, with the gap a diver once made
    line(t, (4, 1, 11), (4, 5, 15), 'iron_bars', wet=True)
    t.fill((4, 1, 13), (4, 2, 13), WATER)
    connect(t, [(4, y, z) for y in (1, 2) for z in (12, 14)], wet=True)
    t.notes['vault'] = (1, 2, 13)


# -- the vaulted hall --------------------------------------------------------------------------------------

def _arc(v, lines):
    for a, b in zip(lines, lines[1:]):
        if a <= v <= b:
            return math.sin(math.pi * (v - a) / (b - a))
    return 0.0


def crown(x, z):
    """The vault's underside over (x, z): the first solid block above the hall's air (a groin vault: the higher of
    the two barrel vaults crossing there)."""
    return H0 + round(RISE * max(_arc(x, XL), _arc(z, ZL)))


def collapsed(x, z):
    """The north-east corner of the vault that fell in."""
    return 18 <= x <= 24 and z <= 6 and (x - 18) + (6 - z) * 0.9 >= 2.5


def hall(t, rng):
    for x in range(4, 26):
        for z in range(0, 27):
            c = crown(x, z)
            if x in (4, 25) or z in (0, 26):                          # the walls, up to the vault
                for y in range(WF + 1, c + 1):
                    b = pick(rng, OLD_BRICKS)
                    if y == WF + 1: b = pick(rng, OLD_TILES)
                    if y == H0: b = 'polished_deepslate'
                    t.set(x, y, z, b)
                continue
            t.carve((x, WF + 1, z), (x, c - 1, z))
            rib = x in XL or z in ZL or abs(_arc(x, XL) - _arc(z, ZL)) < 0.12
            near = [crown(x + dx, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            for y in range(c, min(SY - 1, max([c] + near)) + 1):
                t.set(x, y, z, 'polished_deepslate' if rib and y == c else pick(rng, OLD_BRICKS))
    for x, z in PILLARS:
        c = crown(x, z)
        t.fill((x, BF + 1, z), (x, c - 1, z), mix(rng, OLD_BRICKS))
        t.set(x, BF + 1, z, 'polished_deepslate')
        t.set(x, WF, z, 'chiseled_deepslate')
        t.set(x, c - 1, z, 'chiseled_stone_bricks')
        for f, (dx, dz) in (('east', (-1, 0)), ('west', (1, 0)), ('south', (0, -1)), ('north', (0, 1))):
            t.set(x + dx, c - 1, z + dz, stair('stone_brick', f, 'top'))   # capitals
    for x, z in ((9, 13), (17, 8)):
        t.set(x, BF + 2, z, 'sea_lantern')                               # a glow low in two pillars


def collapse(t, rng):
    """The fallen corner: the vault open to the rock above, the north wall broken through, rubble on the walk and
    a mound of it in the water."""
    for x in range(18, 25):
        for z in range(0, 7):
            if not collapsed(x, z): continue
            lo = crown(x, z) - (1 if rng.random() < 0.5 else 0)
            hi = SY - 1 - (rng.randint(0, 2) if z > 2 else 0)
            t.carve((x, lo, z), (x, hi, z))
    for x in range(19, 23):
        top = WF + 3 + rng.randint(1, 4)
        t.carve((x, WF + 2, 0), (x, top, 0))
    walk = [(x, WW, z) for x in range(18, 25) for z in range(1, 4) if rng.random() < 0.7]
    walk += [(x, WW + 1, z) for x in range(20, 24) for z in range(1, 3) if rng.random() < 0.5]
    rubble(t, rng, walk, (('cobbled_deepslate', 4), ('stone_bricks', 2), ('cracked_stone_bricks', 2),
                          ('gravel', 1), ('polished_deepslate', 1)))
    mound = [(x, y, z) for x in range(17, 22) for z in range(4, 8) for y in range(BF + 1, WF + 1)
             if y <= BF + 6 - abs(x - 20) - abs(z - 5) + rng.randint(-1, 0)]
    rubble(t, rng, mound, (('cobbled_deepslate', 4), ('stone_bricks', 2), ('cracked_stone_bricks', 2)))
    for x, y, z in mound:
        if y == WF: t.set(x, y, z, pick(rng, [('cobbled_deepslate', 1), ('cracked_stone_bricks', 1)]))


def causeway(t, rng):
    """A five-wide causeway across the basin on three piers, arched underneath, a landing in the middle."""
    t.fill((11, WF, 4), (15, WF, 22), mix(rng, OLD_BRICKS))
    t.fill((10, WF, 12), (16, WF, 14), mix(rng, OLD_BRICKS))
    for x in range(10, 17):                                              # corbels under the landing's wings
        if 11 <= x <= 15: continue
        for z in (12, 13, 14):
            t.set(x, WT, z, stair('stone_brick', 'west' if x > 13 else 'east', 'top', wet=True))
    for z in PIERS:
        t.fill((11, BF + 1, z), (15, WT, z), mix(rng, OLD_TILES))
        for side in (-1, 1):
            for x in range(11, 16):
                t.set(x, WT, z + side, stair('deepslate_tile', 'south' if side < 0 else 'north', 'top', wet=True))
    for x in range(11, 16):
        t.set(x, WT, 4, stair('deepslate_tile', 'north', 'top', wet=True))
        t.set(x, WT, 22, stair('deepslate_tile', 'south', 'top', wet=True))
    for z in range(4, 23):
        t.set(11, WF, z, 'polished_deepslate')
        t.set(15, WF, z, 'polished_deepslate')
    t.anchor(13, WF, 13, floor='chiseled_stone_bricks')
    rail = []
    for z in range(4, 23):
        for x in ((10, 16) if 12 <= z <= 14 else (11, 15)):
            if (12 <= z <= 14 and x in (10, 16) and z == 13) or rng.random() < 0.18: continue
            rail.append((x, WW, z))
    for p in rail:
        t.set(*p, pick(rng, [('stone_brick_wall', 3), ('mossy_stone_brick_wall', 1)]))
    connect(t, rail)


def railings(t, rng):
    """Low walls along the walkways' water edge, broken here and there."""
    cells = [(x, WW, 3) for x in range(5, 10)]
    cells += [(x, WW, 23) for x in range(5, 22) if not (6 <= x <= 7 or 10 <= x <= 16)]
    cells += [(22, WW, z) for z in range(4, 23) if z not in (20, 21)]
    cells = [p for p in cells if rng.random() > 0.2]
    for p in cells:
        t.set(*p, pick(rng, [('stone_brick_wall', 3), ('mossy_stone_brick_wall', 2)]))
    connect(t, cells)


def water_stairs(t, rng):
    """Two flights from the walkways down into the water."""
    for i in range(5):
        for x in (6, 7):
            t.set(x, WT - i, 22 - i, stair('stone_brick', 'south', wet=True))
        for z in (20, 21):
            t.set(21 - i, WT - i, z, stair('stone_brick', 'east', wet=True))


def doors(t, rng):
    """Arched doors to the old conduits (jigsaws), and the way into the sluice room."""
    for x0, z, face in ((8, 0, 'north'), (16, SZ - 1, 'south')):
        t.carve((x0, WW, z), (x0 + 2, WW + 2, z))
        t.set(x0, WW + 2, z, stair('stone_brick', 'west', 'top'))
        t.set(x0 + 2, WW + 2, z, stair('stone_brick', 'east', 'top'))
        t.set(x0 + 1, WW + 3, z, 'chiseled_stone_bricks')
        t.jigsaw(x0 + 1, WW, z, face + '_up', 'cistern/door', target='cistern/tunnel_in', pool='cistern/tunnels')
    t.carve((25, WW, 10), (25, WW + 2, 11))
    t.set(25, WW + 2, 10, stair('stone_brick', 'north', 'top'))
    t.set(25, WW + 2, 11, stair('stone_brick', 'south', 'top'))
    t.sign(9, WW + 3, 1, ['VII'], facing='south')


MARK = {  # the Old Delvers' mark over the vault, on the west wall: (y, z) -> block
    (15, 13): 'gold_block', (14, 12): 'polished_blackstone', (14, 13): 'polished_blackstone',
    (14, 14): 'polished_blackstone', (13, 12): 'gold_block', (13, 13): 'gilded_blackstone', (13, 14): 'gold_block',
    (12, 12): 'gold_block', (12, 13): 'gilded_blackstone', (12, 14): 'gold_block', (11, 13): 'polished_blackstone',
    (12, 10): 'gold_block', (13, 11): 'gold_block', (12, 16): 'gold_block', (13, 15): 'gold_block',
    (11, 11): 'polished_blackstone_bricks', (10, 12): 'polished_blackstone_bricks', (9, 13): 'polished_blackstone_bricks',
    (11, 15): 'polished_blackstone_bricks', (10, 14): 'polished_blackstone_bricks',
}


def furnish(t, rng):
    for (y, z), b in MARK.items():
        t.set(4, y, z, b)
    for x, z in ((5, 1), (24, 24), (24, 16)):
        t.barrel(x, WW, z, 'up', 'cistern/ledge')
    for x, z, n, lit in ((6, 1, 3, True), (23, 25, 2, False), (24, 23, 1, True), (5, 25, 4, False), (12, 13, 2, True),
                         (14, 5, 1, False), (14, 21, 3, True)):
        t.set(x, WW, z, f'candle[candles={n},lit={"true" if lit else "false"}]')
    t.haunt(12, WW, 12, 'drowned')
    for x, z in ((13, 13), (6, 24), (23, 6 + 12)):
        c = crown(x, z)
        hang(t, x, c - 3, z, chain=2, lamp='soul_lantern')
    for z in (5, 9, 17, 21):                                             # glow lichen just above the water
        t.set(5, WF, z, 'glow_lichen[west=true]')
    for x in (8, 18):
        t.set(x, WF, 22, 'glow_lichen[south=true]')
    t.set(22, WW, 25, 'bone_block[axis=z]')                              # someone who sat down by the door
    t.set(22, WW + 1, 25, 'skeleton_skull[rotation=3]')
    for x, y, z in ((5, H0 - 1, 1), (24, H0 - 2, 25), (10, H0 - 1, 9), (16, H0 - 1, 17), (5, H0, 25)):
        if t.name_at(x, y, z) == 'minecraft:air': t.set(x, y, z, 'cobweb')
    # centuries of seepage: stalactites from the vault
    for x, z in ((7, 10), (15, 16), (19, 11), (11, 20), (20, 24), (6, 5), (16, 3), (23, 21)):
        c = crown(x, z)
        if t.name_at(x, c - 1, z) == 'minecraft:air' and t.name_at(x, c, z) not in (None, 'minecraft:air'):
            t.set(x, c - 1, z, 'pointed_dripstone[thickness=tip,vertical_direction=down]')
            if (x + z) % 3 == 0 and t.name_at(x, c - 2, z) == 'minecraft:air':
                t.set(x, c - 1, z, 'pointed_dripstone[thickness=frustum,vertical_direction=down]')
                t.set(x, c - 2, z, 'pointed_dripstone[thickness=tip,vertical_direction=down]')
    # the walks: the waterworks' old pots and buckets, moss where the damp gets in
    for x, z in ((7, 1), (8, 25), (20, 25)):
        t.pot(x, WW, z, 'south', sherds=['brick', 'brick', 'brick', 'brick'])
    for x, z, lvl in ((24, 9, 0), (24, 12, 1)):
        t.set(x, WW, z, 'cauldron' if lvl == 0 else f'water_cauldron[level={lvl}]')
    for _ in range(14):
        x, z = rng.choice([(rng.randint(5, 21), rng.choice((1, 2, 24, 25))), (rng.choice((23, 24)), rng.randint(4, 22))])
        if t.name_at(x, WW, z) == 'minecraft:air' and t.name_at(x, WF, z) not in (None, 'minecraft:air'):
            t.set(x, WW, z, 'moss_carpet')
    # a diver who did not come up: bones on the basin floor, his trident beside him
    t.set(19, BF + 1, 10, 'bone_block[axis=x]')
    t.set(20, BF + 1, 10, 'bone_block[axis=x]')
    t.item_frame(19, BF + 1, 11, 'up', 'trident')


# -- the sluice room ---------------------------------------------------------------------------------------

def sluice(t, rng):
    """The valve room: the channel from the basin runs in under a chained sluice gate to the great wheel; three
    levers on the wall; the waterwarden's lectern and what is left of the waterwarden."""
    t.fill((25, WF - 4, 8), (31, 17, 18), mix(rng, OLD_BRICKS))
    t.fill((26, WF, 9), (30, WF, 17), mix(rng, OLD_TILES))
    t.carve((26, WW, 9), (30, 16, 17))
    for z in (11, 15):
        t.fill((26, 16, z), (30, 16, z), 'polished_deepslate')           # ceiling beams
    t.carve((25, WW, 10), (25, WW + 2, 11))
    # the channel: under the walkway from the basin, through the grate, along the floor to the wheel
    t.fill((22, WF - 2, 13), (24, WT, 13), WATER)
    t.fill((25, WF - 2, 13), (25, WT, 13), 'iron_bars[north=true,south=true,east=false,west=false,waterlogged=true]')
    t.fill((26, WF - 2, 13), (30, WT, 13), WATER)
    t.carve((26, WF, 13), (30, WF, 13))
    # the sluice gate: a frame over the channel, the gate raised a little on its chains
    for z in (12, 14):
        t.fill((26, WW, z), (26, WW + 4, z), 'polished_deepslate')
    t.fill((26, WW + 5, 12), (26, WW + 5, 14), 'polished_deepslate')
    t.fill((26, WF - 2, 13), (26, WW, 13), 'iron_bars[east=false,west=false,north=true,south=true,waterlogged=true]')
    t.set(26, WF, 13, 'iron_bars[east=false,west=false,north=true,south=true]')
    t.set(26, WW, 13, 'iron_bars[east=false,west=false,north=true,south=true]')
    for y in range(WW + 1, WW + 5):
        t.set(26, y, 13, 'iron_chain[axis=y]')
    # the wheel: oxidized copper, axle in the east wall, its rim dipping into the channel
    cy, cz, r = 11, 13, 3
    for y in range(cy - r - 1, cy + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            d = math.hypot(y - cy, z - cz)
            if abs(d - r) < 0.5:
                bolt = (y - cy == 0) or (z - cz == 0)
                t.set(30, y, z, 'oxidized_copper' if bolt else 'oxidized_cut_copper')
            elif d < r - 0.5 and (y == cy or z == cz) and (y, z) != (cy, cz):
                t.set(30, y, z, f'oxidized_copper_chain[axis={"y" if z == cz else "z"}]')
    t.set(30, cy, cz, 'oxidized_copper_grate')
    t.set(31, cy, cz, 'oxidized_copper')
    # the lever panel on the north wall
    for x in (27, 28, 29):
        t.set(x, WW + 1, 8, 'polished_blackstone_bricks')
        t.set(x, WW + 1, 9, f'lever[face=wall,facing=south,powered={"true" if x == 28 else "false"}]')
    t.set(28, WW + 2, 8, 'chiseled_polished_blackstone')
    t.set(28, WW + 3, 8, 'gold_block')
    for x, z, n in ((27, 11, 3), (29, 15, 2)):
        for i in range(n):
            t.set(x, 15 - i, z, 'iron_chain[axis=y]')
    # the waterwarden's desk, and the waterwarden
    t.lectern(27, WW, 17, 'north', "Waterwarden's Ledger", 'The Warden', LEDGER)
    t.set(28, WW, 17, 'polished_blackstone_slab[type=top]')
    t.set(28, WW + 1, 17, 'candle[candles=3,lit=false]')
    t.set(26, WW, 16, 'bone_block[axis=y]')
    t.set(26, WW + 1, 16, 'skeleton_skull[rotation=10]')
    t.set(27, WW, 15, 'bone_block[axis=x]')
    t.barrel(30, WW, 9, 'up', 'cistern/ledge')
    t.set(30, WW + 1, 9, 'candle[candles=1,lit=true]')
    hang(t, 28, 14, 15, chain=1, lamp='soul_lantern')
    t.set(30, 15, 9, 'cobweb')
    # a third way out: the old service door in the east wall
    t.carve((31, WW, 17), (31, WW + 2, 17))
    t.jigsaw(31, WW, 17, 'east_up', 'cistern/door', target='cistern/tunnel_in', pool='cistern/tunnels')


def cistern_hall():
    t = Template('cistern/hall', (SX, SY, SZ))
    rng = t.rng
    basin(t, rng)
    vault(t, rng)
    hall(t, rng)
    causeway(t, rng)
    railings(t, rng)
    water_stairs(t, rng)
    collapse(t, rng)
    sluice(t, rng)
    doors(t, rng)
    furnish(t, rng)
    line_rock(t, rng, ROCK)
    return t


# -- the old conduits: three-wide brick tunnels with a gutter, a trickle still in it ------------------------

def _conduit_slice(t, rng, z, y=0, x0=1, gutter=True, wet=False):
    """One cross-section of a conduit along z: walls x0-1 / x0+3, floor at y, air y+1..y+4 (arched)."""
    xa, xb = x0 - 1, x0 + 3
    for yy in range(y, y + 6):
        for x in (xa, xb):
            t.set(x, yy, z, pick(rng, OLD_BRICKS))
    for x in range(x0, x0 + 3):
        t.set(x, y, z, pick(rng, OLD_TILES))
        t.set(x, y + 5, z, pick(rng, OLD_BRICKS))
    if gutter:
        t.set(x0, y, z, slab('stone_brick', wet=wet))
    t.carve((x0, y + 1, z), (x0 + 2, y + 3, z))
    t.set(x0, y + 4, z, stair('stone_brick', 'west', 'top'))
    t.set(x0 + 1, y + 4, z, 'air')
    t.set(x0 + 2, y + 4, z, stair('stone_brick', 'east', 'top'))


def _decay(t, rng, cells):
    """Cobwebs, roots and lichen in an abandoned conduit."""
    for (x, y, z) in cells:
        if t.name_at(x, y, z) != 'minecraft:air': continue
        r = rng.random()
        if r < 0.08: t.set(x, y, z, 'cobweb')


def conduit():
    t = Template('cistern/conduit', (5, 7, 12))
    rng = t.rng
    for z in range(12):
        _conduit_slice(t, rng, z, wet=0 < z < 11)
    _decay(t, rng, [(x, 3, z) for x in (1, 3) for z in range(12)])
    t.set(0, 2, 6, 'air')                                              # a niche with an old pot in it
    t.set(0, 1, 6, 'stone_bricks')
    t.pot(0, 2, 6, 'east')
    t.set(3, 1, 4, 'candle[candles=2,lit=false]')
    t.set(3, 2, 8, 'glow_lichen[east=true]')
    rubble(t, rng, [(3, 1, 9), (3, 1, 10), (2, 1, 10)], (('cobbled_deepslate', 2), ('cracked_stone_bricks', 1)))
    t.carve((1, 5, 9), (3, 5, 10))                                    # where those fell from
    t.jigsaw(2, 1, 0, 'north_up', 'cistern/tunnel_in')
    t.jigsaw(2, 1, 11, 'south_up', 'cistern/tunnel_out', target='cistern/tunnel_in', pool='cistern/tunnels')
    line_rock(t, rng, ROCK)
    return t


def steps(up):
    """The conduit climbing (or dropping) three blocks over twelve in flights of steps."""
    t = Template('cistern/steps_up' if up else 'cistern/steps_down', (5, 11, 12))
    rng = t.rng
    level = (lambda z: z // 3) if up else (lambda z: 3 - z // 3)
    for z in range(12):
        y = level(z)
        _conduit_slice(t, rng, z, y, gutter=False)
        if y > 0: t.fill((1, 0, z), (3, y - 1, z), mix(rng, OLD_TILES))
        step = (up and z % 3 == 0 and z > 0) or (not up and z % 3 == 2 and z < 11)
        if step:
            for x in (1, 2, 3):
                t.set(x, y, z, stair('stone_brick', 'south' if up else 'north'))
    _decay(t, rng, [(x, level(z) + 3, z) for x in (1, 3) for z in range(12)])
    t.jigsaw(2, level(0) + 1, 0, 'north_up', 'cistern/tunnel_in')
    t.jigsaw(2, level(11) + 1, 11, 'south_up', 'cistern/tunnel_out', target='cistern/tunnel_in', pool='cistern/tunnels')
    line_rock(t, rng, ROCK)
    return t


def bend(left):
    """The conduit turning a corner (left = out of the east side when you walk in from the north face)."""
    t = Template('cistern/bend_left' if left else 'cistern/bend_right', (8, 7, 7))
    rng = t.rng
    mx = (lambda x: x) if left else (lambda x: 7 - x)
    for x in range(8):
        for z in range(7):
            for y in range(6):
                t.set(mx(x), y, z, pick(rng, OLD_TILES if y == 0 else OLD_BRICKS))
    for x in range(1, 4):                                              # in from the north face
        t.carve((mx(x), 1, 0), (mx(x), 3, 5))
    for z in range(3, 6):                                              # out through the side
        t.carve((mx(1), 1, z), (mx(7), 3, z))
    t.carve((mx(2), 4, 0), (mx(2), 4, 4))
    t.carve((mx(2), 4, 4), (mx(7), 4, 4))
    t.set(mx(1), 0, 5, slab('stone_brick'))
    t.set(mx(3), 3, 5, 'cobweb')
    t.jigsaw(mx(2), 1, 0, 'north_up', 'cistern/tunnel_in')
    t.jigsaw(mx(7), 1, 4, ('east' if left else 'west') + '_up', 'cistern/tunnel_out', target='cistern/tunnel_in',
             pool='cistern/tunnels')
    line_rock(t, rng, ROCK)
    return t


def _raw_cave(t, rng, z0):
    """A rough natural cave from z0 to the far face of the piece, open there (the world goes on)."""
    sx, sy, sz = t.size
    for z in range(z0, sz):
        k = z - z0
        half = 1.6 + 0.5 * k + rng.random() * 0.8
        lo = 1 if k < 2 else rng.randint(0, 1)
        hi = 3 + min(k, 3) + rng.randint(0, 1)
        for x in range(sx):
            if abs(x - sx // 2) <= half:
                t.carve((x, lo, z), (x, min(sy - 2, hi - (1 if abs(x - sx // 2) > half - 1 else 0)), z))


def collapse_end():
    """A conduit choked by a fall of its own roof, a crawl over the top into raw cave."""
    t = Template('cistern/collapse', (7, 8, 10))
    rng = t.rng
    for z in range(5):
        _conduit_slice(t, rng, z, x0=2, gutter=z < 3)
    _raw_cave(t, rng, 5)
    pile = [(x, y, z) for z in (2, 3, 4) for x in (2, 3, 4) for y in (1, 2, 3)
            if y <= (z - 1) + (1 if x != 3 else 0) and not (z == 4 and y == 3 and x == 3)]
    rubble(t, rng, pile, (('cobbled_deepslate', 3), ('stone_bricks', 2), ('cracked_stone_bricks', 2), ('gravel', 1)))
    t.carve((3, 4, 3), (3, 5, 4))                                      # where the roof came down
    t.set(2, 1, 1, 'candle[candles=1,lit=false]')
    t.jigsaw(3, 1, 0, 'north_up', 'cistern/tunnel_in')
    line_rock(t, rng, ROCK)
    return t


def outfall_end():
    """The conduit's mouth: a rusted grate, one bar gone, and the raw cave beyond it."""
    t = Template('cistern/outfall', (7, 8, 10))
    rng = t.rng
    for z in range(5):
        _conduit_slice(t, rng, z, x0=2, gutter=True, wet=0 < z < 4)
    _raw_cave(t, rng, 5)
    line(t, (2, 1, 4), (4, 3, 4), 'iron_bars')
    t.fill((3, 1, 4), (3, 2, 4), 'air')
    connect(t, [(x, y, 4) for x in (2, 4) for y in (1, 2, 3)] + [(3, 3, 4)])
    t.set(2, 0, 4, slab('stone_brick'))
    t.set(4, 1, 6, 'bone_block[axis=z]')
    t.jigsaw(3, 1, 0, 'north_up', 'cistern/tunnel_in')
    line_rock(t, rng, ROCK)
    return t


def pieces():
    return [cistern_hall(), conduit(), steps(True), steps(False), bend(True), bend(False), collapse_end(),
            outfall_end()]
