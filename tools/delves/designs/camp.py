"""Delvers' Camp: a working Guild mine camp. A timbered hall carved in the rock (bunks, mess, cookfire, forge,
ore bins, assay benches, the foreman's corner) with rail drifts running out to the working faces, and the
ladder shaft the shift climbs to the surface. Lit everywhere: lanterns under every beam.

Pieces (all drifts share the Guild cross-section from guild_parts.py, along x, centre line z = 2):
  camp/hall      the start piece: residents, beds, job sites, the Ore Ledger, the foreman's chest
  camp/drift     a straight rail drift          camp/stope   a drift with a side working cut into an ore seam
  camp/turn_r    a bend to the right            camp/turn_l  the same bend, mirrored
  camp/fork      a junction with a siding       camp/face    a dead-end working face (ore cart, scaffold)
  camp/shaft     the way up: ladder and scaffold, capped in rock
  camp/cap       a drift's end
"""
from kit import Template
from designs.guild_parts import (POST, PLANK, FLOOR, pick, rock, line, veins, floor, rails, lantern, timber,
                                 drift, jig, mirrored, candle, cart)

KEY = 'camp'
NAME = "Delvers' Camp"
FEATURES = [
    'a timbered hall carved into the rock: three aisles of spruce posts and beams, lanterns under every beam',
    'four bunks set into rock niches, a mess table with a half-eaten supper, a smoker and a cookfire hearth',
    "a forge corner: two blast furnaces under a brick chimney, an anvil, a grindstone, a quench tub, a tool rack",
    'ore bins heaped with raw iron, raw copper, coal and a little gold, fed by the rail from the drifts',
    "the foreman's corner: the Ore Ledger on a lectern, the foreman's chest, a survey map on the wall",
    'three miners and their foreman at four prospecting tables; they trade and tell you where other delves are',
    'rail drifts propped with timber every four blocks, branching and turning, lit all the way',
    'working faces where the walls are thick with coal, iron, copper, redstone, lapis and a little gold',
    'chest minecarts of ore on the rails; the ladder-and-scaffold shaft "we use", capped in rock',
]
STRUCTURE = {
    'start_pool': 'camp/start', 'size': 5, 'horizontal': 46, 'vertical': 24,
    'min_y': -4, 'max_y': 36, 'cover': 10, 'inhabited': True, 'weight': 3, 'clearance': 10,
}
POOLS = {
    'camp/start': {'elements': [('camp/hall', 1)]},
    'camp/drifts': {'elements': [('camp/drift', 5), ('camp/stope', 3), ('camp/turn_r', 2), ('camp/turn_l', 2),
                                 ('camp/fork', 2), ('camp/face', 2)], 'fallback': 'camp/caps'},
    'camp/shafts': {'elements': [('camp/shaft', 1)], 'fallback': 'camp/caps'},
    'camp/caps': {'elements': [('camp/cap', 2), ('camp/face', 1)]},
}

DOOR = 'camp/drift_in'          # every piece joins the one before it by this jigsaw
OUT = dict(target=DOOR, pool='camp/drifts')
LIVING = [('spruce_planks', 9), ('stripped_spruce_wood[axis=x]', 1)]
WORK = [('cobblestone', 6), ('stone_bricks', 3), ('packed_mud', 2)]

# -- the hall ---------------------------------------------------------------------------------------
# 27 x 10 x 21. Inside x 1..25, z 1..19, floor y = 0, open to y 6 with a vault above. Cross-beams at x = 5, 10,
# 15, 20; posts in two rows (z = 7, 13) split it into a north aisle (living), a centre aisle (hearth, rail yard)
# and a south aisle (foreman, assay benches, ore bins). Doors: N (x 12) and S (x 16) and E (z 10) to drifts,
# W (z 10) to the shaft.
HX, HY, HZ = 27, 10, 21
BEAMS_X = (5, 10, 15, 20)
ROWS_Z = (7, 13)


def hall_frame(t, rng):
    # floor: planks where people live (bunks, mess, foreman), rammed stone where they work
    for x in range(1, HX - 1):
        for z in range(1, HZ - 1):
            living = (z <= 6 and x <= 19) or (z >= 14 and x <= 6)
            t.set(x, 0, z, pick(rng, LIVING if living else WORK))
    # the room and its vault
    t.carve((1, 1, 1), (HX - 2, 6, HZ - 2))
    t.carve((2, 7, 2), (HX - 3, 7, HZ - 3))
    t.fill((4, 8, 4), (HX - 5, 8, HZ - 5), lambda x, y, z: 'air' if rng.random() < 0.8 else None)  # a ragged vault
    # rock walls (a few old veins in them: the hall was cut along a seam)
    line(t, (1, 1, 1), (HX - 2, 6, HZ - 2), rng, ore=0.06)
    line(t, (2, 7, 2), (HX - 3, 7, HZ - 3), rng, ore=0.03)
    # doorways
    t.carve((HX - 1, 1, 9), (HX - 1, 3, 11))      # E: the rail road out
    t.carve((0, 1, 9), (0, 3, 11))                # W: to the shaft
    t.carve((11, 1, 0), (13, 3, 0))               # N
    t.carve((15, 1, HZ - 1), (17, 3, HZ - 1))     # S
    for x, z in ((HX - 1, 9), (HX - 1, 10), (HX - 1, 11), (0, 9), (0, 10), (0, 11), (11, 0), (12, 0), (13, 0),
                 (15, HZ - 1), (16, HZ - 1), (17, HZ - 1)):
        t.set(x, 0, z, pick(rng, WORK))
    # door frames: a post either side and a lintel log over each doorway
    for (x0, z0, x1, z1, axis) in ((HX - 1, 8, HX - 1, 12, 'z'), (0, 8, 0, 12, 'z'), (10, 0, 14, 0, 'x'),
                                   (14, HZ - 1, 18, HZ - 1, 'x')):
        for (x, z) in ((x0, z0), (x1, z1)):
            for y in range(1, 4): t.set(x, y, z, POST)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                t.set(x, 4, z, f'spruce_log[axis={axis}]')
    # timber: cross-beams on wall posts and two rows of posts, two long beams over the rows
    for z in ROWS_Z:
        for x in range(1, HX - 1):
            t.set(x, 6, z, 'spruce_log[axis=x]')
        for x in (1, HX - 2):
            for y in range(1, 6): t.set(x, y, z, POST)
    for x in BEAMS_X:
        for z in range(1, HZ - 1):
            t.set(x, 6, z, 'spruce_log[axis=z]')
        for z in (1, HZ - 2) + ROWS_Z:
            for y in range(1, 6): t.set(x, y, z, POST)
    # wall plates along the long walls carry the beam ends
    for z in (1, HZ - 2):
        for x in range(1, HX - 1):
            if x not in BEAMS_X: t.set(x, 6, z, 'spruce_log[axis=x]')
    # lanterns under the beams, and one in every doorway
    for x in BEAMS_X:
        for z in (4, 10, 16):
            lantern(t, x, 5, z)
    for z in ROWS_Z:
        for x in (3, 8, 13, 18, 23):
            lantern(t, x, 5, z)
    for x in (2, 24):
        lantern(t, x, 5, HZ - 2)
    for (x, z) in ((HX - 1, 10), (0, 10), (12, 0), (16, HZ - 1)):
        lantern(t, x, 3, z)


def hall_bunks(t, rng):
    """North aisle, west: four beds tucked into niches cut in the rock, nightstands between."""
    for x, color in ((1, 'brown'), (3, 'red'), (7, 'cyan'), (9, 'green')):
        t.carve((x, 1, 0), (x, 2, 0))
        t.set(x, 3, 0, PLANK)                      # the niche's lintel
        t.bed(x, 1, 1, 'north', color=color)       # head in the niche, foot in the hall
        t.set(x, 1, 2, 'brown_carpet')
    for x in (2, 8):                               # nightstands, a candle on each
        t.carve((x, 1, 0), (x, 2, 0))
        t.set(x, 3, 0, PLANK)
        t.set(x, 1, 0, 'barrel[facing=up,open=false]')
        candle(t, x, 2, 0, n=2, lit=True, color='white')
    t.set(4, 1, 1, 'chest[facing=south,type=single,waterlogged=false]')    # a miner's own kit (empty)
    t.set(6, 1, 1, 'barrel[facing=south,open=false]')
    t.item_frame(5, 2, 2, 'south', 'copper_helmet')                        # hung on the post
    t.item_frame(5, 3, 2, 'south', 'stone_pickaxe')
    t.set(4, 2, 1, 'lantern[hanging=false,waterlogged=false]')
    t.set(1, 1, 6, 'barrel[facing=up,open=false]')
    t.set(1, 2, 6, 'lantern[hanging=false,waterlogged=false]')


def hall_mess(t, rng):
    """North aisle, middle: the mess table with stools, a smoker and the stores along the wall."""
    for x in range(16, 20):
        for z in (3, 4):
            t.set(x, 1, z, 'spruce_slab[type=top,waterlogged=false]')
        t.set(x, 1, 2, 'spruce_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]')
        if x != 18: t.set(x, 1, 5, 'spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]')
    t.set(18, 1, 5, 'spruce_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]')   # pushed back
    # supper, half eaten
    t.set(17, 2, 4, 'cake[bites=3]')
    candle(t, 18, 2, 3, n=3, lit=True)
    for (x, z, item) in ((16, 3, 'bread'), (19, 4, 'cooked_mutton'), (16, 4, 'bowl'), (19, 3, 'baked_potato')):
        t.item_frame(x, 2, z, 'up', item)
    # along the wall
    t.set(16, 1, 1, 'smoker[facing=south,lit=true]')
    t.barrel(17, 1, 1, 'south', 'camp/supplies')
    t.set(18, 1, 1, 'water_cauldron[level=2]')
    t.set(19, 1, 1, 'barrel[facing=up,open=false]')
    t.set(19, 2, 1, 'barrel[facing=up,open=false]')
    t.set(14, 1, 1, 'barrel[facing=up,open=false]')


def hall_forge(t, rng):
    """North aisle, east: two blast furnaces under a brick chimney, anvil, grindstone, quench tub, tool rack."""
    t.set(21, 1, 1, 'stone_bricks')
    t.set(22, 1, 1, 'blast_furnace[facing=south,lit=true]')
    t.set(23, 1, 1, 'blast_furnace[facing=south,lit=true]')
    t.set(24, 1, 1, 'stone_bricks')
    for y in (2, 3):
        for x in range(21, 25):
            t.set(x, y, 1, 'cracked_stone_bricks' if (x + y) % 3 == 0 else 'stone_bricks')
    for y in range(4, 7):
        for x in range(21, 25):
            t.set(x, y, 1, 'stone_bricks' if x in (22, 23) else 'stone_brick_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]' % ('east' if x == 21 else 'west') if y == 4 else 'stone_bricks')
    for x in range(21, 25):
        t.set(x, 3, 2, 'stone_brick_slab[type=top,waterlogged=false]')   # the hood
    for x in range(20, 26):
        t.set(x, 0, 2, 'stone_bricks')                                    # fireproof hearthstone
    t.set(22, 1, 4, 'chipped_anvil[facing=west]')
    t.set(24, 1, 4, 'grindstone[face=floor,facing=north]')
    t.set(25, 1, 1, 'water_cauldron[level=3]')                            # quench tub
    t.set(25, 1, 2, 'barrel[facing=up,open=false]')
    t.set(25, 2, 2, 'lantern[hanging=false,waterlogged=false]')
    t.set(21, 1, 5, 'coal_block')
    t.set(21, 1, 6, 'coal_block')
    t.set(22, 1, 6, 'cobblestone_slab[type=bottom,waterlogged=false]')
    # tool rack: a plank board on the end wall with the shift's tools on it
    for z in (3, 4, 5):
        for y in (2, 3):
            t.set(HX - 1, y, z, PLANK)
    for (y, z, item) in ((2, 3, 'iron_pickaxe'), (2, 4, 'stone_pickaxe'), (2, 5, 'iron_shovel'),
                         (3, 3, 'iron_axe'), (3, 4, 'stone_shovel'), (3, 5, 'flint_and_steel')):
        t.item_frame(HX - 2, y, z, 'west', item)


def hall_hearth(t, rng):
    """Centre aisle, west: the cookfire in a ring of stone, benches either side, a woodpile."""
    t.set(7, 1, 10, 'campfire[facing=east,lit=true,signal_fire=false,waterlogged=false]')
    for x in (6, 7, 8):
        for z in (9, 10, 11):
            if (x, z) != (7, 10):
                t.set(x, 1, z, 'cobblestone_slab[type=bottom,waterlogged=false]')
    for x in (6, 7, 8):
        t.set(x, 1, 8, 'spruce_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]')
        t.set(x, 1, 12, 'spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]')
    for (x, y, z) in ((1, 1, 8), (2, 1, 8), (1, 2, 8), (1, 1, 12), (2, 1, 12), (1, 2, 12)):
        t.set(x, y, z, 'spruce_log[axis=x]')                                # woodpile either side of the W door
    # the shift tally on the post, and the Guild's saying by the rail door
    t.sign(10, 2, 8, ['SHIFT TALLY', 'Iron IIII IIII', 'Coal IIII IIII I', 'Copper IIII II'], facing='south')
    t.sign(HX - 2, 2, 8, ['MIND THE ROOF', 'Light behind', 'you, light', 'ahead.'], facing='south')


def hall_yard(t, rng):
    """Centre aisle, east: the rail yard. The rail from the E drift ends at a log buffer; ore carts wait on it."""
    rails(t, 'x', 18, HX - 2, 10, 1)
    t.set(17, 1, 10, 'stripped_spruce_log[axis=z]')                     # buffer
    cart(t, 22, 1, 10, loot='camp/ore_cart', facing='east')
    cart(t, 19, 1, 10, facing='east')
    rails(t, 'z', 1, 3, 12, 1)                                          # stubs to the N and S drifts
    rails(t, 'z', 16, HZ - 2, 16, 1)
    t.barrel(14, 1, 8, 'up', 'camp/supplies')
    t.set(14, 1, 12, 'crafting_table')
    t.set(11, 1, 12, 'barrel[facing=up,open=false]')
    t.set(11, 2, 12, 'lantern[hanging=false,waterlogged=false]')


def hall_foreman(t, rng):
    """South aisle, west: the foreman's corner behind a fence: the Ore Ledger, the chest, a map on the wall."""
    for z in range(14, HZ - 1):
        if z == 16:
            t.set(7, 1, z, 'spruce_fence_gate[facing=east,in_wall=false,open=false,powered=false]')
            continue
        props = (['north=true'] if z > 14 else []) + (['south=true'] if z < HZ - 2 else [])
        t.set(7, 1, z, 'spruce_fence[' + ','.join(props) + ']')
    for x in range(2, 6):
        for z in (16, 17):
            t.set(x, 1, z, 'red_carpet')
    t.lectern(4, 1, 15, 'south', 'Ore Ledger', 'the Foreman', LEDGER)
    t.chest(1, 1, HZ - 2, 'east', 'camp/foreman')
    t.set(2, 1, HZ - 2, 'bookshelf')
    t.set(2, 2, HZ - 2, 'lantern[hanging=false,waterlogged=false]')
    t.set(3, 1, HZ - 2, 'deepdelves:prospecting_table[facing=north]')
    t.set(5, 1, HZ - 2, 'barrel[facing=up,open=false]')
    t.set(1, 1, 14, 'spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]')
    # survey board on the end wall
    for z in (15, 16, 17):
        for y in (2, 3):
            t.set(0, y, z, PLANK)
    t.item_frame(1, 3, 16, 'east', 'map')
    t.item_frame(1, 2, 15, 'east', 'compass')
    t.item_frame(1, 2, 17, 'east', 'clock')
    t.sign(5, 2, 14, ['FOREMAN', '', 'knock on', 'the post'], facing='south')


def hall_assay(t, rng):
    """South aisle, middle: three assay benches (prospecting tables) under a board of ore samples."""
    for x in range(8, 15):
        for y in (2, 3):
            t.set(x, y, HZ - 1, PLANK)
    for x in (9, 11, 13):
        t.set(x, 1, HZ - 2, 'deepdelves:prospecting_table[facing=north]')
    t.barrel(12, 1, HZ - 2, 'north', 'camp/supplies')
    t.set(8, 1, HZ - 2, 'barrel[facing=up,open=false]')
    t.set(8, 2, HZ - 2, 'lantern[hanging=false,waterlogged=false]')
    t.set(12, 2, HZ - 2, 'lantern[hanging=false,waterlogged=false]')
    t.set(14, 1, HZ - 2, 'stonecutter[facing=north]')
    for (x, y, item) in ((9, 2, 'raw_iron'), (11, 2, 'raw_copper'), (13, 2, 'raw_gold'), (8, 3, 'coal'),
                         (12, 3, 'redstone'), (14, 3, 'lapis_lazuli')):
        t.item_frame(x, y, HZ - 2, 'north', item)


def hall_bins(t, rng):
    """South aisle, east: three ore bins heaped toward the back (raw iron, raw copper, coal with a little gold)."""
    z0, z1 = 15, HZ - 2
    for x in (20, 23):                          # dividers, a post at the front of each
        for z in range(z0 + 1, z1 + 1):
            for y in (1, 2): t.set(x, y, z, PLANK)
        for y in (1, 2, 3): t.set(x, y, z0, POST)
    for x in (18, 19, 21, 22, 24, 25):
        t.set(x, 1, z0, 'spruce_slab[type=bottom,waterlogged=false]')    # the lip
    heaps = {18: 'raw_iron_block', 19: 'raw_iron_block', 21: 'raw_copper_block', 22: 'raw_copper_block',
             24: 'coal_block', 25: 'coal_block'}
    for x, block in heaps.items():
        for z in range(z0 + 1, z1 + 1):
            h = 1 + (z - z0 - 1) // 2 + (1 if rng.random() < 0.3 else 0)
            for y in range(1, min(h, 3) + 1):
                t.set(x, y, z, block)
    t.set(25, 1, z0 + 1, 'raw_gold_block')
    t.set(24, 2, z1, 'raw_gold_block')
    t.sign(20, 2, z0 - 1, ['COPPER | IRON'], facing='north')      # as you face the bins
    t.sign(23, 2, z0 - 1, ['COAL | COPPER', '', 'gold to the', 'foreman!'], facing='north')


LEDGER = [
    "ORE LEDGER\n\nCamp of the\nDelvers' Guild,\nthis shift.\nKept by the\nforeman.\n\nMind the roof.\nLight behind you,\nlight ahead.",
    "Week the first.\nIron  41 carts\nCoal  58 carts\nCopper 37 carts\nGold  3 (to me)\nRedstone, lapis:\na sack each.\n\nNo. 1 drift is\nrunning well.",
    "Week the second.\nIron  44\nCoal  52\nCopper 40\nGold  5\nNew face cut off\nthe fork. Props\nevery four blocks,\nno less: I counted.\nTwo hissers in\nNo. 2 drift, a\nrattler at the fork.",
    "Bread on the first\nprop each shift for\nluck, and the rail\nrung once for every\ncart sent up. Old\nways; keep them.\n\nNobody robs a\npillar in my camp.",
    "Talk at the fire\nagain: picks heard\nunder the stone\nwhere none of ours\nwork, and lights\nseen far off in the\ndark. Someone's\nbeen deeper than us\nonce. I tell the\nlads: stay on the\nrails.",
    "Light to you, and\nthe roof over you.\n\nThe empty hook\nstays empty. We\nremember the Seam.\n\nStone gives,\nstone takes.",
]


def hall():
    t = Template('camp/hall', (HX, HY, HZ))
    rng = t.rng
    hall_frame(t, rng)
    hall_bunks(t, rng)
    hall_mess(t, rng)
    hall_forge(t, rng)
    hall_hearth(t, rng)
    hall_yard(t, rng)
    hall_foreman(t, rng)
    hall_assay(t, rng)
    hall_bins(t, rng)
    # the empty hook: a bare chain under the beam, kept for the Buried Seam's lost shift
    t.set(11, 5, ROWS_Z[1], 'iron_chain[axis=y,waterlogged=false]')
    t.sign(11, 2, ROWS_Z[1], ['THE EMPTY HOOK', 'kept for the', "Seam's lost", 'shift'], facing='east')
    # a crust of bread on the first prop, for luck
    t.item_frame(HX - 2, 2, 12, 'west', 'bread')
    t.anchor(13, 0, 10, floor='chiseled_stone_bricks')
    # the camp: the foreman in the corner, a miner at the fire, one at the table, one at the benches
    t.resident(5, 1, 18, 'foreman', facing='north')
    t.resident(9, 1, 10, 'miner', facing='west')
    t.resident(15, 1, 4, 'miner', facing='east')
    t.resident(11, 1, 17, 'miner', facing='south')
    # jigsaws: three rail drifts and the way up
    jig(t, HX - 1, 1, 10, 'east', 'camp/door', **OUT)
    jig(t, 12, 1, 0, 'north', 'camp/door', **OUT)
    jig(t, 16, 1, HZ - 1, 'south', 'camp/door', **OUT)
    jig(t, 0, 1, 10, 'west', 'camp/way_up', target=DOOR, pool='camp/shafts', rail=False)
    t.notes['empty_hook'] = (11, 5, ROWS_Z[1])
    return t



# -- drifts -----------------------------------------------------------------------------------------
# Every drift runs along x with its centre line on z = 2 (or wherever its in-jigsaw sits), the Guild section.

def spare_props(t, x0, x1, z, y=1):
    """Spare timbers stacked along a wall."""
    for x in range(x0, x1 + 1):
        t.set(x, y, z, 'stripped_spruce_log[axis=x]')


def straight():
    """A rail drift, 12 long: timber every four blocks, two lanterns, a niche of spare props, a few veins."""
    t = Template('camp/drift', (12, 6, 5))
    rng = t.rng
    drift(t, 'x', 0, 11, 2, 0, rng, ore=0.07)
    for u in (1, 5, 9):
        timber(t, 'x', u, 2, 0)
    rails(t, 'x', 0, 11, 2, 1)
    lantern(t, 1, 3, 2)
    lantern(t, 9, 3, 2)
    t.carve((6, 1, 4), (8, 2, 4))                 # a niche in the wall: spare props and a water barrel
    spare_props(t, 6, 7, 4)
    t.set(6, 2, 4, 'stripped_spruce_log[axis=x]')
    t.set(8, 1, 4, 'barrel[facing=up,open=false]')
    t.item_frame(5, 2, 1, 'south', 'bread')        # a crust on the prop, for luck
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 11, 1, 2, 'east', 'camp/drift_out', **OUT)
    return t


def stope():
    """A drift with a working cut into the seam beside it: the face is thick with ore, a scaffold against it,
    a cart waiting on the rail."""
    t = Template('camp/stope', (12, 7, 9))
    rng = t.rng
    c = 6
    drift(t, 'x', 0, 11, c, 0, rng, ore=0.05)
    # the working: x 2..9, z 1..3, a step higher roof
    floor(t, (2, 0, 1), (9, 0, 4), rng, FLOOR)
    t.carve((2, 1, 1), (9, 5, 4))
    line(t, (2, 1, 1), (9, 5, 4), rng, ore=0.6, ceiling=True)
    veins(t, [(x, y, 0) for x in range(1, 11) for y in range(1, 6)], rng, p=0.5)
    for u in (1, 5, 10):
        timber(t, 'x', u, c, 0)
    for x in (2, 9):                                # cribbing posts at the working's mouth
        for y in range(1, 5): t.set(x, y, 4, POST)
    for x in range(2, 10):
        t.set(x, 5, 4, 'spruce_log[axis=x]')
    rails(t, 'x', 0, 11, c, 1)
    cart(t, 7, 1, c, facing='east')
    for y in (1, 2, 3):
        t.set(4, y, 1, 'scaffolding[bottom=false,distance=0,waterlogged=false]')
    t.set(7, 1, 1, 'barrel[facing=up,open=false]')
    t.item_frame(8, 2, 1, 'south', 'iron_pickaxe')
    lantern(t, 1, 3, c)
    lantern(t, 10, 3, c)
    lantern(t, 5, 4, 2)
    lantern(t, 8, 4, 2)
    for x in (5, 8):
        for z in (1, 2, 3):
            t.set(x, 5, z, 'spruce_log[axis=z]')
    t.sign(2, 2, 5, ['FACE NO. 2', 'iron & coal', 'IIII IIII II'], facing='south')
    jig(t, 0, 1, c, 'west', DOOR)
    jig(t, 11, 1, c, 'east', 'camp/drift_out', **OUT)
    return t


def turn():
    """A bend: in from the west, out to the south (camp/turn_l is its mirror image). A cribbed corner post carries
    the beams; the rail curves round."""
    t = Template('camp/turn_r', (7, 6, 7))
    rng = t.rng
    drift(t, 'x', 0, 5, 2, 0, rng, ore=0.06)
    drift(t, 'z', 1, 6, 4, 0, rng, ore=0.06)
    timber(t, 'x', 1, 2, 0)
    timber(t, 'z', 5, 4, 0)
    for y in (1, 2, 3):
        t.set(6, y, 2, POST)
        t.set(2, y, 4, POST)
    for x in range(2, 7):
        t.set(x, 4, 2, 'spruce_log[axis=x]')
    rails(t, 'x', 0, 3, 2, 1)
    t.set(4, 1, 2, 'rail[shape=south_west]')
    rails(t, 'z', 3, 6, 4, 1)
    lantern(t, 4, 3, 2)
    lantern(t, 4, 3, 5)
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 4, 1, 6, 'south', 'camp/drift_out', **OUT)
    return t


def fork():
    """A junction: the drift runs on and a branch leaves to the side, a waymark on the post."""
    t = Template('camp/fork', (11, 6, 9))
    rng = t.rng
    drift(t, 'x', 0, 10, 2, 0, rng, ore=0.05)
    drift(t, 'z', 3, 8, 5, 0, rng, ore=0.05)
    for u in (1, 9):
        timber(t, 'x', u, 2, 0)
    for x in (3, 7):                               # the junction's frame: posts each side of the branch mouth
        for y in (1, 2, 3):
            t.set(x, y, 4, POST)
            t.set(x, y, 0, POST)
        for z in range(0, 5):
            t.set(x, 4, z, 'spruce_log[axis=z]')
    for x in range(3, 8):
        t.set(x, 4, 4, 'spruce_log[axis=x]')
    timber(t, 'z', 7, 5, 0)
    rails(t, 'x', 0, 10, 2, 1)
    t.set(5, 1, 2, 'rail[shape=south_west]')       # the switch is set for the branch
    rails(t, 'z', 3, 8, 5, 1)
    lantern(t, 1, 3, 2)
    lantern(t, 9, 3, 2)
    lantern(t, 5, 3, 7)
    t.sign(3, 2, 1, ['<< CAMP', '', 'FACES >>', 'mind the roof'], facing='south')
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 10, 1, 2, 'east', 'camp/drift_out', **OUT)
    jig(t, 5, 1, 8, 'south', 'camp/drift_out', **OUT)
    return t


def face():
    """A working face at the end of a drift: a chamber whose walls and roof are crowded with ore, a scaffold up
    the face, the ore cart being loaded, tools on the props. Ends the branch. (The drift comes in from the east
    here so the face itself is the far wall in the previews.)"""
    t = Template('camp/face', (12, 7, 10))
    rng = t.rng
    c = 5
    drift(t, 'x', 9, 11, c, 0, rng, ore=0.08)
    floor(t, (2, 0, 2), (8, 0, 8), rng, FLOOR)
    t.carve((2, 1, 2), (8, 5, 8))
    # rock around the chamber thick with ore; the face (x = 0..1) and the far side are two blocks deep
    line(t, (2, 1, 2), (8, 5, 8), rng, ore=0.55, ceiling=True)
    for y in range(0, 7):
        for z in range(0, 10):
            if (0, y, z) not in t.blocks: t.set(0, y, z, rock(rng, 0.35))
        for x in range(0, 10):
            if (x, y, 0) not in t.blocks: t.set(x, y, 0, rock(rng, 0.3))
    veins(t, [(1, y, z) for y in range(1, 6) for z in range(2, 9)], rng, p=0.4)
    # cribbing: four posts and a frame of beams
    for (x, z) in ((3, 2), (3, 8), (7, 2), (7, 8)):
        for y in range(1, 5): t.set(x, y, z, POST)
    for x in range(2, 9):
        for z in (2, 8): t.set(x, 5, z, 'spruce_log[axis=x]')
    for z in range(3, 8):
        t.set(3, 5, z, 'spruce_log[axis=z]')
        t.set(7, 5, z, 'spruce_log[axis=z]')
    timber(t, 'x', 10, c, 0)
    rails(t, 'x', 5, 11, c, 1)
    t.set(4, 1, c, 'stripped_spruce_log[axis=z]')               # buffer
    cart(t, 6, 1, c, loot='camp/ore_cart', facing='west')
    for y in (1, 2, 3, 4):
        t.set(2, y, 3, 'scaffolding[bottom=false,distance=0,waterlogged=false]')
    t.set(2, 1, 7, 'barrel[facing=up,open=false]')
    t.set(2, 2, 7, 'lantern[hanging=false,waterlogged=false]')
    t.set(4, 1, 8, 'raw_iron_block')
    t.set(5, 1, 8, 'cobblestone_slab[type=bottom,waterlogged=false]')
    t.set(4, 1, 2, 'raw_copper_block')
    t.item_frame(7, 2, 3, 'south', 'iron_pickaxe')
    t.item_frame(3, 2, 7, 'north', 'iron_shovel')
    lantern(t, 5, 4, 2)
    lantern(t, 5, 4, 8)
    lantern(t, 3, 4, 5)
    lantern(t, 10, 3, c)
    t.sign(7, 2, 7, ['FACE', 'IIII IIII IIII', 'IIII II', 'good iron'], facing='north')
    jig(t, 11, 1, c, 'east', DOOR)
    return t


def cap():
    """A drift's end: the rail stops at a buffer before the face they haven't got to yet."""
    t = Template('camp/cap', (5, 6, 5))
    rng = t.rng
    drift(t, 'x', 0, 3, 2, 0, rng, ore=0.1)
    line(t, (0, 1, 1), (3, 3, 3), rng, ore=0.35)
    veins(t, [(4, y, z) for y in range(1, 4) for z in range(1, 4)], rng, p=0.5)
    timber(t, 'x', 1, 2, 0)
    rails(t, 'x', 0, 2, 2, 1)
    t.set(3, 1, 2, 'stripped_spruce_log[axis=z]')
    lantern(t, 1, 3, 2)
    t.set(3, 1, 1, 'barrel[facing=up,open=false]')
    jig(t, 0, 1, 2, 'west', DOOR)
    return t


def shaft():
    """The way up the shift uses: a short passage to a timber-cribbed shaft with a ladder, a scaffold hoist and a
    landing, climbing to a rock plug they haven't broken through yet."""
    H = 16
    t = Template('camp/shaft', (9, H, 5))
    rng = t.rng
    drift(t, 'x', 0, 3, 2, 0, rng, ore=0.05)
    timber(t, 'x', 1, 2, 0)
    lantern(t, 1, 3, 2)
    # the shaft: open x 5..7, z 1..3, cribbed all round with planks on log corners
    floor(t, (4, 0, 0), (8, 0, 4), rng, [('cobblestone', 3), ('spruce_planks', 2)])
    t.carve((5, 1, 1), (7, H - 3, 3))
    for y in range(1, H - 2):
        for x in range(4, 9):
            for z in range(0, 5):
                if 5 <= x <= 7 and 1 <= z <= 3: continue
                corner = x in (4, 8) and z in (0, 4)
                t.set(x, y, z, 'stripped_spruce_log[axis=y]' if corner else
                      ('spruce_log[axis=x]' if z in (0, 4) else 'spruce_log[axis=z]') if y % 4 == 0 else PLANK)
    t.carve((4, 1, 1), (4, 3, 3))                  # the way in from the passage
    for y in (1, 2, 3):
        t.set(4, y, 0, POST)
        t.set(4, y, 4, POST)
    # ladder up the far side, a scaffold hoist in a corner, a landing halfway, cross-beams with lanterns
    for y in range(1, H - 2):
        t.set(7, y, 2, 'ladder[facing=west,waterlogged=false]')
    for y in range(1, H - 4):
        t.set(5, y, 3, 'scaffolding[bottom=false,distance=0,waterlogged=false]')
    for z in (1, 2):
        t.set(5, 8, z, 'spruce_slab[type=top,waterlogged=false]')
    for y in (5, 11):
        for z in (1, 2):
            t.set(6, y, z, 'spruce_log[axis=z]')
        lantern(t, 6, y - 1, 1)
    for y in range(9, H - 3):
        t.set(6, y, 3, 'iron_chain[axis=y,waterlogged=false]')    # the hoist rope
    t.set(6, 8, 3, 'barrel[facing=up,open=false]')
    t.set(6, 1, 1, 'barrel[facing=up,open=false]')
    t.set(6, 2, 1, 'lantern[hanging=false,waterlogged=false]')
    # the cap: a plug of rock and rubble they haven't broken through, a hatch under it
    t.fill((5, H - 2, 1), (7, H - 2, 3), lambda x, y, z: pick(rng, [('cobblestone', 3), ('cobbled_deepslate', 1)]))
    t.fill((5, H - 1, 1), (7, H - 1, 3), lambda x, y, z: pick(rng, [('gravel', 2), ('stone', 3), ('andesite', 1)]))
    t.set(7, H - 3, 2, 'spruce_trapdoor[facing=west,half=top,open=false,powered=false,waterlogged=false]')
    t.set(7, H - 4, 2, 'ladder[facing=west,waterlogged=false]')
    lantern(t, 6, H - 3, 2)
    t.sign(5, 2, 2, ['THE WAY UP', 'we use. 20 more', 'to go: dig on', 'top, mind roof'], facing='east')
    jig(t, 0, 1, 2, 'west', DOOR, rail=False)
    return t


def pieces():
    r = turn()
    return [hall(), straight(), stope(), r, mirrored(r, 'camp/turn_l'), fork(), face(), cap(), shaft()]
