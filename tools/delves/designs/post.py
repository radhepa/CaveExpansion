"""Deepwatch Post: a fortified checkpoint of the Deepwatch built across a cave road. The road comes up out of the
deep, crosses a lit killing ground, passes under a raised portcullis between two archer towers and runs on past
the keep, the mess yard, the armory and the drill yard. In the keep's middle hall stands the Deepgate: a shut
iron door, a lever, and a stair down to a sealed chamber under the keep.

Layout of the start piece (31 x 22 x 31, floor y 7, people walk at y 8; the road runs along x at z 19..23):
  x 0..5     the outer yard (killing ground): braziers, stakes, a burn pile, the HALT sign
  x 6..12    the wall line: curtain wall (z 0..11), tower A (z 12..18), gate passage (z 19..23), tower B (z 24..30)
  x 11..30   the keep along the back (z 0..10): barracks | Deepgate hall | captain's room; under it the sealed chamber
             the courtyard (z 11..18): mess under a lean-to, cookfire, braziers
             the armory (x 12..21, z 24..30) and the drill yard (x 22..30, z 24..30)
Canon (shared with the dialogue): motto "Below, we hold." / "Above, they sleep."; the watch report "Lamp lit, road
watched, gate shut."; the Deepgate is an Old Delver arch with their lantern mark, shut by the Watch's own iron
door, the lever locked (the captain wears the key); behind it the Long Stair goes on down past any map. Twelve went
down on the Long Patrol and five came back; the seven are chalked on the barracks wall. The Deep Dark is the Hush.
"""
import math

from kit import Template
from designs.masonry_parts import (DEEP_BRICKS, DEEP_TILES, ROAD, STONE_BRICKS, brazier, connect, hang, lamp_post,
                                   line, line_rock, merlons, mix, pick, rubble, slab, stair)

KEY = 'post'
NAME = 'Deepwatch Post'
FEATURES = [
    'a barbican across a cave road: the road runs in under a raised iron portcullis and out the far side',
    'two archer towers with arrow slits, ladders and braziers on top; crenellated curtain wall and gatehouse walk',
    'a lit killing ground outside the gate: braziers, stakes, a burn pile of bones and a tally of the season\'s kills',
    'the keep: barracks with five bunks and footlockers, the captain\'s room with the Deepwatch Log and his chest',
    'a mess under a lean-to with a cookfire, smoker and half-eaten meal; Deepwatch banners everywhere',
    'armory and drill yard: training dummies and archery targets for the garrison, weapon racks, anvil, grindstone',
    "the Deepgate: an Old Delver arch with the gold lantern mark, shut with the Watch's iron door and a locked lever",
    'behind it the stair down to a sealed chamber with its chest, where the Long Stair goes on down behind bars',
    'the names of the seven lost on the Long Patrol chalked on the barracks wall; the oath and the motto on signs',
    "a hisser tally by the gate and the marked watch-candle in the gate tower's guard room",
    'garrison: two knights, two archers and the Watch Captain',
    'the cave road runs on out of both ends through lamp-lit tunnels, past a roadside watch niche',
]
STRUCTURE = {
    'start_pool': 'post/start', 'size': 2, 'horizontal': 60, 'vertical': 24,
    'min_y': -20, 'max_y': 8, 'cover': 10, 'inhabited': True, 'weight': 2, 'require': None, 'clearance': 10,
}
POOLS = {
    'post/start': {'elements': [('post/barbican', 1)]},
    'post/road': {'elements': [('post/road', 4), ('post/road_left', 1), ('post/road_right', 1), ('post/road_rise', 1),
                               ('post/road_fall', 1), ('post/waypost', 2)], 'fallback': 'post/road_ends'},
    'post/road_ends': {'elements': [('post/road_end', 1)]},
}

F, W = 7, 8                     # floor and walking height in the start piece (the sealed chamber is under it)
SX, SY, SZ = 31, 22, 31
ROAD_Z = (19, 23)               # the road band
BANNER = [('minecraft:circle', 'white'), ('minecraft:flower', 'white'), ('minecraft:triangles_bottom', 'black'),
          ('minecraft:border', 'gray')]     # the Deepwatch: a white lamp-glow on black


def deepwatch_banner(t, x, y, z, facing):
    t.banner(x, y, z, facing, 'black', BANNER)


LOG = [
    'DEEPWATCH LOG\nPost of the Lower Road\n\nThe first leaves are in a hand none here can read. We keep them. '
    'We write on.\n\nBelow, we hold.',
    'Day 112. Lamp lit, road watched, gate shut.\n\nSpiders, two, shot in the outer yard. Bones burned. '
    'Hissers, one, shot early at the gate. All hands present.',
    'THE LONG PATROL\n\nTwelve down the Long Stair by order from above.\n\n\nThe stair goes on.',
    'The five sleep little and want no lamp. Hale stands his watch facing the Deepgate. He says the Hush is '
    'nearer than it was. He says the Listener has learned our bell.',
    'Day 131. Knocking at the Deepgate. Three knocks, at the second bell.\n\nLogged. Not answered.\n\n'
    'Lamp lit, road watched, gate shut.',
    'Orders from above: no warden goes down. The lever stays locked; the key stays on the Captain. '
    'Arrows short, send more.\n\nBelow, we hold.\nAbove, they sleep.',
]


# -- the open cave the post stands in ---------------------------------------------------------------

def in_keep(x, z): return x >= 11 and z <= 10
def in_armory(x, z): return 12 <= x <= 21 and z >= 24
def on_road(z): return ROAD_Z[0] <= z <= ROAD_Z[1]


def _ceiling(x, z, rng):
    """The top air cell of the cave over (x, z), or None where the living rock stays (keep, armory, ragged edges)."""
    if in_keep(x, z) or in_armory(x, z): return None
    edge = x in (0, SX - 1) or z in (0, SZ - 1)
    wall_line = 4 <= x <= 13
    if edge and not wall_line and not (on_road(z) and x in (0, SX - 1)): return None
    if wall_line: return SY - 1
    d = math.hypot(x - 9, z - 21)
    wobble = 1.2 * math.sin(x * 0.7 + z * 0.3) + 0.8 * math.sin(z * 0.9 - x * 0.4)
    top = round(SY - 1 - 0.33 * d + wobble)
    if x >= 22 and z >= 24: top = min(top, F + 7)     # the drill yard sits under a lower roof
    return max(F + 7, min(SY - 1, top))


def cavern(t, rng):
    for x in range(SX):
        for z in range(SZ):
            top = _ceiling(x, z, rng)
            if top is None: continue
            t.carve((x, W, z), (x, top, z))
            if on_road(z):
                block = pick(rng, ROAD)
            elif x <= 5 or (x <= 7 and z <= 11):          # outer yard: rough cobbles
                block = pick(rng, [('cobbled_deepslate', 5), ('cobblestone', 4), ('mossy_cobblestone', 1)])
            elif x >= 22 and z >= 24:                     # drill yard: trodden earth
                block = pick(rng, [('packed_mud', 3), ('dirt_path', 2), ('cobblestone', 1)])
            else:                                         # courtyard flagstones
                block = pick(rng, [('stone_bricks', 6), ('polished_andesite', 3), ('cracked_stone_bricks', 1)])
            t.set(x, F, z, block)
    # ragged cave walls: knock a few cells back into rock along the edge band (never over the road or walls)
    for x in range(1, SX - 1):
        for z in (1, SZ - 2):
            if 4 <= x <= 13 or on_road(z) or in_keep(x, z) or in_armory(x, z): continue
            if rng.random() < 0.45:
                for y in range(W + 2 + rng.randint(0, 2), SY):
                    t.set(x, y, z, None)
    for z in range(1, SZ - 1):
        for x in (1, SX - 2):
            if on_road(z) or in_keep(x, z) or in_armory(x, z): continue
            if rng.random() < 0.45:
                for y in range(W + 2 + rng.randint(0, 2), SY):
                    t.set(x, y, z, None)


def road(t, rng):
    """The road band across the whole piece, with jigsaws to the road tunnels at both ends."""
    z0, z1 = ROAD_Z
    for x in range(SX):
        for z in range(z0, z1 + 1):
            t.set(x, F, z, pick(rng, ROAD))
            if z == 21 and x % 3 == 0: t.set(x, F, z, 'polished_andesite')    # a worn middle line
    t.carve((0, W, z0), (0, W + 4, z1))
    t.carve((SX - 1, W, z0), (SX - 1, W + 4, z1))
    t.jigsaw(0, W, 21, 'west_up', 'post/road_w', target='post/road_in', pool='post/road')
    t.jigsaw(SX - 1, W, 21, 'east_up', 'post/road_e', target='post/road_in', pool='post/road')


# -- the wall line: towers, gatehouse, curtain wall -----------------------------------------------------

UP = F + 6          # towers' loft floor, gatehouse roof and curtain top (walk at UP + 1)
TOP = F + 10        # tower roofs (walk at TOP + 1)


def tower(t, rng, x0, z0, ground_doors, upper_doors, slits):
    """A 7 x 7 archer tower: guard room below, an archers' loft with arrow slits, a fighting top with a brazier.
    ground_doors: [(x, z, facing)]; upper_doors: [(x, z)] open arches onto the wall walks; slits: [(x, z, y)]."""
    x1, z1 = x0 + 6, z0 + 6
    t.fill((x0, F, z0), (x1, TOP, z1), mix(rng, STONE_BRICKS))
    t.fill((x0, F, z0), (x1, F + 1, z1), mix(rng, DEEP_BRICKS))           # plinth course
    t.fill((x0, UP, z0), (x1, UP, z1), 'polished_deepslate')               # string course at the loft
    for x, z in ((x0, z0), (x0, z1), (x1, z0), (x1, z1)):                  # quoins
        for y in range(F + 2, TOP + 1, 2):
            t.set(x, y, z, 'deepslate_bricks')
    t.fill((x0 + 1, F, z0 + 1), (x1 - 1, F, z1 - 1), mix(rng, [('stone_bricks', 3), ('polished_andesite', 1)]))
    t.carve((x0 + 1, W, z0 + 1), (x1 - 1, UP - 1, z1 - 1))
    t.fill((x0 + 1, UP, z0 + 1), (x1 - 1, UP, z1 - 1), 'spruce_planks')
    t.carve((x0 + 1, UP + 1, z0 + 1), (x1 - 1, TOP - 1, z1 - 1))
    for y in range(W, TOP + 1):                                            # ladder up through both floors
        t.set(x1 - 1, y, z0 + 1, 'ladder[facing=west]')
    t.carve((x0, TOP + 1, z0), (x1, TOP + 3, z1))
    merlons(t, x0, z0, x1, z1, TOP + 1, mix(rng, STONE_BRICKS))
    t.set(x0 + 3, TOP + 1, z0 + 3, 'campfire[facing=north,lit=true,signal_fire=false]')
    hang(t, x0 + 3, W + 2, z0 + 3, chain=UP - W - 3)                       # lamps on chains in both rooms
    hang(t, x0 + 3, TOP - 2, z0 + 3, chain=1)
    for x, z, facing in ground_doors:
        t.door(x, W, z, facing, 'spruce_door', hinge='left')
    for x, z in upper_doors:
        t.carve((x, UP + 1, z), (x, UP + 2, z))
    for x, z, y in slits:
        t.carve((x, y, z), (x, y + 1, z))
    # the archers' loft: arrows, a rack and a stool
    t.set(x0 + 1, UP + 1, z1 - 1, 'barrel[facing=up,open=false]')
    t.set(x0 + 2, UP + 1, z1 - 1, 'fletching_table')
    t.set(x1 - 1, UP + 1, z1 - 1, stair('spruce', 'east'))


def gatehouse(t, rng):
    """The vaulted gate passage between the towers, a raised portcullis over the outer mouth, a walk on top."""
    z0, z1 = ROAD_Z
    t.fill((6, UP, z0), (12, UP, z1), mix(rng, STONE_BRICKS))
    t.carve((6, W, z0), (12, UP - 1, z1))
    for x in range(7, 13):                                                  # rounded vault corners
        t.set(x, UP - 1, z0, stair('stone_brick', 'north', 'top'))
        t.set(x, UP - 1, z1, stair('stone_brick', 'south', 'top'))
    for z in range(z0, z1 + 1):                                             # corbels over the outer mouth
        t.set(5, UP, z, stair('deepslate_brick', 'east', 'top'))
    line(t, (6, UP - 2, z0), (6, UP - 1, z1), 'iron_bars')                 # the portcullis, raised
    for z in (z0 + 1, z1 - 1):
        t.set(7, UP - 1, z, 'iron_chain[axis=y]')                          # its hoist chains
    t.carve((6, UP + 1, z0), (12, UP + 3, z1))
    merlons(t, 6, z0, 12, z1, UP + 1, mix(rng, STONE_BRICKS), start=1, sides=('west', 'east'))
    for x in (6, 12):
        t.set(x, UP + 2, 21, 'lantern[hanging=false]')
    for x, z, f in ((7, 18, 'south'), (11, 24, 'north'), (11, 18, 'south'), (7, 24, 'north')):
        t.set(x, W + 2, z + (1 if f == 'south' else -1), f'wall_torch[facing={f}]')
    t.sign(7, W + 1, z0, ['HISSERS', 'IIII IIII IIII', 'IIII IIII II', 'Shoot early.'], facing='south')
    t.sign(10, W + 1, z1, ['Below,', 'we hold.'], facing='north')
    deepwatch_banner(t, 13, UP, 21, 'east')


def curtain(t, rng):
    """The curtain wall from tower A to the back of the cave, a walk on top behind merlons."""
    t.fill((8, F, 0), (10, UP, 11), mix(rng, STONE_BRICKS))
    t.fill((8, F, 0), (10, F + 1, 11), mix(rng, DEEP_BRICKS))
    t.carve((8, UP + 1, 0), (10, UP + 3, 11))
    merlons(t, 8, 0, 10, 11, UP + 1, mix(rng, STONE_BRICKS), sides=('west',))
    for z in (2, 6, 10):
        t.set(8, UP + 2, z, 'lantern[hanging=false]')


def wall_line(t, rng):
    tower(t, rng, 6, 12, ground_doors=[(12, 15, 'east'), (9, 18, 'south')], upper_doors=[(9, 12), (9, 18)],
          slits=[(6, 14, UP + 1), (6, 16, UP + 1), (6, 15, W + 1), (7, 12, UP + 1), (6, 13, W + 1)])
    tower(t, rng, 6, 24, ground_doors=[(9, 24, 'north'), (12, 27, 'east')], upper_doors=[(9, 24)],
          slits=[(6, 26, UP + 1), (6, 28, UP + 1), (6, 27, W + 1), (6, 29, W + 1)])
    gatehouse(t, rng)
    curtain(t, rng)
    for z in (15, 27):
        deepwatch_banner(t, 5, UP - 1, z, 'west')
    # tower A's guard room keeps the watch-candle on its table
    t.set(8, W, 16, 'spruce_fence')
    t.set(8, W + 1, 16, 'white_candle[candles=1,lit=true]')
    t.set(8, W, 17, stair('spruce', 'south'))
    t.sign(7, W + 1, 16, ['WATCH-CANDLE', 'One mark burns', 'down, one watch', 'is kept.'], facing='east')


# -- the keep: barracks | Deepgate hall | captain's room ----------------------------------------------------

KR = F + 5          # keep roof (the rock sits right on it)
HALL = F + 8        # the Deepgate hall is taller: its roof


def keep(t, rng):
    t.fill((11, F, 0), (30, KR, 10), mix(rng, STONE_BRICKS))
    t.fill((11, F, 10), (30, F + 1, 10), mix(rng, DEEP_BRICKS))           # plinth along the front
    t.fill((18, KR + 1, 0), (24, HALL, 10), mix(rng, STONE_BRICKS))        # the hall rises above the keep line
    for x in range(11, 31):                                                # cornice over the courtyard
        if 18 <= x <= 24: continue
        t.set(x, KR, 11, stair('deepslate_brick', 'north', 'top'))
    for x in (18, 24):                                                     # the hall's front corners
        for y in range(F, HALL + 1):
            if y % 2: t.set(x, y, 10, 'polished_deepslate')
    merlons(t, 18, 10, 24, 10, HALL + 1, mix(rng, STONE_BRICKS), sides=('south',))
    t.fill((18, HALL, 11), (24, HALL, 11), stair('deepslate_brick', 'north', 'top'))
    # rooms
    t.fill((12, F, 1), (17, F, 9), 'spruce_planks')
    t.carve((12, W, 1), (17, KR - 1, 9))
    t.fill((19, F, 1), (23, F, 9), mix(rng, DEEP_TILES))
    t.carve((19, W, 1), (23, HALL - 1, 9))
    t.fill((25, F, 1), (29, F, 9), 'spruce_planks')
    t.carve((25, W, 1), (29, KR - 1, 9))
    # doors and windows on the courtyard
    t.door(15, W, 10, 'south', 'spruce_door')
    t.door(27, W, 10, 'south', 'spruce_door')
    for x in (13, 17, 25, 29):
        line(t, (x, W + 1, 10), (x, W + 2, 10), 'iron_bars')
    t.carve((20, W, 10), (22, W + 3, 10))                                   # the hall's arch
    t.set(20, W + 3, 10, stair('stone_brick', 'west', 'top'))
    t.set(22, W + 3, 10, stair('stone_brick', 'east', 'top'))
    t.set(21, W + 4, 10, 'chiseled_stone_bricks')
    deepwatch_banner(t, 21, W + 6, 11, 'south')
    brazier(t, 19, W, 11)
    brazier(t, 23, W, 11)


def barracks(t, rng):
    """Five bunks with footlockers, the lost chalked on the wall, the oath over the door."""
    for z in (1, 3, 5, 7, 9):
        t.bed(13, W, z, 'west', color='gray')
    t.barrel(12, W, 2, 'up', 'post/barracks')
    t.barrel(12, W, 6, 'up', 'post/barracks')
    t.set(12, W, 4, 'lantern[hanging=false]')
    t.set(12, W, 8, 'lantern[hanging=false]')
    for z in (3, 7):
        hang(t, 15, KR - 1, z)
    # the card table by the door
    t.set(16, W, 8, 'spruce_trapdoor[facing=north,half=top,open=false]')
    t.set(17, W, 8, stair('spruce', 'east'))
    t.set(16, W, 7, stair('spruce', 'north'))
    t.set(16, W + 1, 8, 'white_candle[candles=2,lit=true]')
    # the seven who did not come back up the Long Stair, chalked on the wall
    t.sign(17, W + 1, 3, ['GONE DOWN', 'Gared  Tomas', 'Willem  Mott', 'Brannick'], facing='west', color='white')
    t.sign(17, W + 1, 5, ['Elsbet  Corran', '', 'The stair', 'goes on.'], facing='west', color='white')
    t.sign(15, W + 1, 1, ['I keep the lamp.', 'I hold the road.', 'I do not', 'go down.'], facing='south')
    deepwatch_banner(t, 16, W + 2, 1, 'south')
    t.item_frame(17, W + 1, 7, 'west', 'shield')


def captain(t, rng):
    """The Watch Captain's room: the Deepwatch Log on its lectern, his chest, his bed and his maps."""
    t.bed(29, W, 2, 'north', color='black')
    t.chest(28, W, 1, 'south', 'post/captain')
    t.lectern(25, W, 4, 'east', 'Deepwatch Log', 'The Watch', LOG)
    t.set(26, W, 4, stair('spruce', 'east'))
    t.set(25, W, 2, 'cartography_table')
    t.set(25, W + 1, 2, 'white_candle[candles=3,lit=true]')
    for z in (6, 7):
        t.fill((25, W, z), (25, W + 1, z), 'bookshelf')
    for z in range(4, 9):
        t.set(27, W, z, 'black_carpet')
    t.set(29, W, 8, 'barrel[facing=up,open=false]')
    t.set(29, W + 1, 8, 'lantern[hanging=false]')
    deepwatch_banner(t, 27, W + 2, 1, 'south')
    t.item_frame(29, W + 1, 5, 'west', 'iron_sword')
    t.item_frame(25, W + 2, 3, 'east', 'spyglass')
    for z in (3, 7):
        hang(t, 27, KR - 1, z)


# -- the Deepgate and the sealed chamber under the keep ------------------------------------------------------

CF = F - 5          # the chamber's floor (people walk at CF + 1; its ceiling is the keep's floor)
GATE_Z = 6          # the gate wall across the Deepgate hall


def deepgate(t, rng):
    """An Old Delver arch carved with their lantern mark, walled up by the Watch around its own iron door; a locked
    lever beside it; behind it a stair down into the sealed chamber."""
    z = GATE_Z
    t.fill((19, W, z), (23, HALL - 1, z), mix(rng, DEEP_TILES))                    # the old work
    for x in (19, 23):
        t.fill((x, W, z), (x, W + 3, z), 'polished_blackstone_bricks')            # the arch's jambs
        t.set(x, W + 4, z, 'chiseled_polished_blackstone')
    t.set(20, W + 4, z, stair('polished_blackstone_brick', 'west', 'top'))
    t.set(22, W + 4, z, stair('polished_blackstone_brick', 'east', 'top'))
    t.fill((20, W, z), (22, W + 3, z), mix(rng, STONE_BRICKS))                     # the Watch's infill
    t.door(21, W, z, 'north', 'iron_door', hinge='left')
    t.set(21, W + 2, z, 'polished_andesite')                                       # the Watch's lintel
    # the lantern mark over the arch: a gold lamp with a dark heart
    for x, y in ((21, W + 6), (20, W + 5), (22, W + 5), (21, W + 4)):
        t.set(x, y, z, 'gold_block')
    t.set(21, W + 5, z, 'chiseled_polished_blackstone')
    t.set(20, W + 1, z + 1, 'lever[face=wall,facing=south,powered=false]')
    t.sign(22, W + 2, z + 1, ['THE DEEPGATE', 'Shut by order', 'of the Watch.'], facing='south')
    t.sign(22, W + 1, z + 1, ['If it knocks:', 'log it.', 'Never answer.'], facing='south')
    t.sign(19, W + 1, z + 1, ['Lever locked.', 'The Captain', 'wears the key.'], facing='south')
    for x, f in ((19, 'east'), (23, 'west')):
        deepwatch_banner(t, x, W + 3, 8, f)
    hang(t, 21, HALL - 3, 8, chain=2)
    # the stair behind the gate: four steps down to the chamber, ledges and rails either side
    t.carve((20, CF + 1, 1), (22, HALL - 1, z - 1))
    for i, sz in enumerate(range(z - 1, 1, -1)):                                  # z 5, 4, 3, 2
        y = F - 1 - i
        for x in (20, 21, 22):
            t.set(x, y, sz, stair('deepslate_tile', 'south'))
            if y - 1 > CF: t.fill((x, CF + 1, sz), (x, y - 1, sz), mix(rng, DEEP_TILES))
    t.fill((20, CF, 1), (22, CF, 1), mix(rng, DEEP_TILES))
    for x in (19, 23):
        line(t, (x, W, 1), (x, W, z - 1), 'deepslate_tile_wall')
    hang(t, 21, HALL - 3, 3, chain=2)
    t.notes['deepgate_door'] = (21, W, z)


def chamber(t, rng):
    """The sealed chamber under the keep (built before the Deepgate's stair): the Watch's strongbox at one end, at
    the other the Old Delvers' Long Stair going on down behind the Watch's bars."""
    x0, x1, z0, z1 = 12, 26, 1, 8
    t.fill((x0 - 1, CF, z0 - 1), (x1 + 1, F - 1, z1 + 1), 'polished_deepslate')
    t.fill((x0, CF, z0), (x1, CF, z1), mix(rng, DEEP_TILES))
    t.carve((x0, CF + 1, z0), (x1, F - 1, z1))
    for x in (16, 26):
        t.fill((x, CF + 1, 6), (x, F - 1, 6), 'polished_deepslate')               # two square piers
    # the strongbox end
    t.fill((x0, CF + 1, 3), (x0 + 1, CF + 1, 5), slab('polished_blackstone'))
    t.chest(x0, CF + 1, 4, 'east', 'post/deepgate', custom_name='Deepgate Strongbox')
    t.notes['deepgate'] = (x0, CF + 1, 4)
    deepwatch_banner(t, x0, CF + 3, 4, 'east')
    for z in (2, 6):
        t.set(x0, CF + 1, z, 'lantern[hanging=false]')
    for x in (19, 23):
        t.set(x, CF + 1, 1, 'lantern[hanging=false]')                      # either side of the stair's foot
    # the Long Stair, going on down behind the bars (the template ends; the stair does not)
    sx = x1 + 1
    t.fill((sx, CF + 1, 2), (sx, CF + 3, 6), 'polished_blackstone_bricks')
    t.fill((sx, CF + 4, 2), (sx, CF + 4, 6), 'deepslate_tiles')
    t.set(sx, CF + 4, 4, 'gold_block')
    t.carve((sx, CF + 1, 3), (sx, CF + 3, 5))
    line(t, (sx, CF + 1, 3), (sx, CF + 3, 5), 'iron_bars')
    t.fill((sx + 1, 0, 2), (SX - 1, F - 1, 6), mix(rng, DEEP_TILES))
    for i, x in enumerate(range(sx + 1, SX)):
        y = CF - 1 - i                                       # 1, 0, then below the template
        t.carve((x, max(0, y + 1), 3), (x, CF + 3 - i, 5))
        if y >= 0:
            for z in (3, 4, 5):
                t.set(x, y, z, stair('deepslate_tile', 'west'))
    t.sign(x1, CF + 3, 2, ['THE LONG STAIR', 'goes on.', 'Sealed by', 'the Watch.'], facing='west')
    t.item_frame(24, CF + 1, 7, 'up', 'iron_helmet')
    t.set(x1, CF + 1, 8, 'cobweb')
    for x in (14, 19, 23):
        hang(t, x, F - 1, 7)
    hang(t, 15, F - 1, 3)
    hang(t, 25, F - 1, 3)


# -- the yards: courtyard and mess, armory, drill yard, the killing ground outside the gate -----------------

def courtyard(t, rng):
    """The mess under a lean-to against the barracks, a cookfire, braziers, the roster and the supply stack."""
    for x in (13, 17):                                                     # lean-to posts and roof
        t.fill((x, W, 14), (x, W + 2, 14), 'stripped_spruce_log[axis=y]')
    t.fill((13, W + 3, 11), (17, W + 3, 14), slab('spruce'))
    t.fill((14, W, 13), (16, W, 13), slab('spruce', 'top'))               # the table
    for x in (14, 16):
        t.set(x, W, 12, stair('spruce', 'north'))
    for x in (14, 15, 16):
        t.set(x, W, 14, stair('spruce', 'south'))
    t.set(14, W + 1, 13, 'cake[bites=4]')
    t.set(16, W + 1, 13, 'lantern[hanging=false]')
    t.barrel(13, W, 11, 'up', 'post/barracks')
    t.barrel(17, W, 11, 'up', 'post/barracks')
    hang(t, 15, W + 2, 12)
    # the cook corner against tower A
    t.set(13, W, 17, 'smoker[facing=east,lit=true]')
    t.set(13, W, 16, 'water_cauldron[level=3]')
    t.set(15, W, 17, 'campfire[facing=north,lit=true,signal_fire=false]')
    t.set(16, W, 17, 'barrel[facing=up,open=false]')
    # braziers and lamps over the yard, the roster by the captain's door, the stores
    brazier(t, 27, W, 15)
    lamp_post(t, 21, W, 17)
    lamp_post(t, 28, W, 11)
    lamp_post(t, 24, W, 18)
    lamp_post(t, 29, W, 18, height=1)
    t.sign(26, W + 1, 11, ['WATCH ROSTER', 'Gate: Oswin', 'Wall: Hale', 'Deepgate: Capt.'], facing='south')
    for x, z, h in ((28, 17, 2), (29, 17, 1), (28, 18, 1), (29, 15, 1)):
        t.fill((x, W, z), (x, W + h - 1, z), 'barrel[facing=up,open=false]')
    t.set(29, W, 16, 'hay_block[axis=x]')
    line(t, (17, W, 18), (19, W, 18), 'spruce_fence')                    # a rack of spears by the road
    for x in (17, 18, 19):
        t.set(x, W + 1, 18, 'lightning_rod[facing=up,powered=false]')


def armory(t, rng):
    """Racks, anvil and grindstone, the armory chest; its yard (dummies and targets) is next door."""
    t.fill((13, F, 24), (21, KR, 30), mix(rng, STONE_BRICKS))
    t.fill((13, F, 24), (21, F + 1, 24), mix(rng, DEEP_BRICKS))
    for x in range(13, 22):
        t.set(x, KR, 23, stair('deepslate_brick', 'south', 'top'))
    t.fill((14, F, 25), (20, F, 29), mix(rng, [('polished_andesite', 3), ('stone_bricks', 2)]))
    t.carve((14, W, 25), (20, KR - 1, 29))
    t.carve((13, W, 27), (13, W + 1, 27))                                 # through to tower B's door
    t.carve((16, W, 24), (17, W + 2, 24))                                 # the arch onto the road
    t.set(16, W + 2, 24, stair('stone_brick', 'west', 'top'))
    t.set(17, W + 2, 24, stair('stone_brick', 'east', 'top'))
    for x in (14, 19):
        line(t, (x, W + 1, 24), (x, W + 2, 24), 'iron_bars')
    t.chest(20, W, 29, 'west', 'post/armory')
    t.set(20, W, 25, 'anvil[facing=north]')
    t.set(20, W, 27, 'grindstone[face=floor,facing=north]')
    t.set(14, W, 29, 'smithing_table')
    t.set(15, W, 29, 'barrel[facing=up,open=false]')
    t.set(14, W, 25, 'barrel[facing=up,open=false]')
    t.set(14, W + 1, 25, 'barrel[facing=up,open=false]')
    for x, item in ((15, 'iron_sword'), (16, 'bow'), (17, 'crossbow'), (18, 'iron_axe'), (19, 'shield')):
        t.item_frame(x, W + 1, 29, 'north', item)
    t.item_frame(20, W + 2, 26, 'west', 'iron_helmet')
    deepwatch_banner(t, 17, W + 3, 29, 'north')
    for x in (15, 19):
        hang(t, x, KR - 1, 27)
    for x in (14, 18):
        hang(t, x, KR - 1, 23)                                             # lamps under the cornice, over the road


def drill_yard(t, rng):
    """Where the garrison trains: dummies for the knights (and the captain), targets for the archers."""
    for x in range(22, 30):
        if x in (25, 26): continue
        t.set(x, W, 24, 'spruce_fence')
    connect(t, [(x, W, 24) for x in range(22, 30)])
    t.set(25, W, 24, 'spruce_fence_gate[facing=north,in_wall=false,open=true]')
    t.set(26, W, 24, 'spruce_fence_gate[facing=north,in_wall=false,open=true]')
    for x in (23, 25, 27):
        t.set(x, W, 29, 'villagefriends:training_dummy[facing=north]')
    for z in (25, 27):
        t.set(28, W, z, 'villagefriends:archery_target[facing=west]')
    t.fill((29, W, 25), (29, W + 1, 27), 'hay_block[axis=z]')
    t.set(22, W, 27, 'hay_block[axis=y]')
    brazier(t, 24, W, 26)
    lamp_post(t, 22, W, 29)
    lamp_post(t, 29, W, 29, height=1)
    t.set(27, W + 1, 24, 'lantern[hanging=false]')                        # a lamp on the fence over the road
    t.sign(22, W, 25, ['DRILL', 'Shields up.', 'Shoot early.'], facing='east', wall=False)


def outer_yard(t, rng):
    """The killing ground outside the gate: braziers, stakes, the burn pile, the HALT sign and a tally."""
    for x, z in ((3, 9), (3, 15), (3, 27)):
        brazier(t, x, W, z)
    lamp_post(t, 6, W, 3)
    lamp_post(t, 3, W, 1, height=1)
    for z in (18, 24):
        lamp_post(t, 1, W, z, height=1)                                    # the road's first lamps
    for z in range(2, 11, 2):                                              # stakes
        t.fill((1, W, z), (1, W + rng.randint(0, 1), z), 'spruce_fence')
    for z in (25, 29):
        t.fill((1, W, z), (1, W + 1, z), 'spruce_fence')
    t.set(3, W, 4, 'campfire[facing=north,lit=false,signal_fire=false]')  # the burn pile, cold
    for x, z in ((2, 3), (2, 4), (3, 5), (4, 4)):
        t.set(x, W, z, 'bone_block[axis=y]')
    t.set(2, W + 1, 4, 'bone_block[axis=x]')
    t.set(2, W + 1, 3, 'skeleton_skull[rotation=6]')
    t.set(4, W + 1, 4, 'zombie_head[rotation=10]')
    t.set(3, W + 1, 5, 'skeleton_skull[rotation=2]')
    t.sign(4, W, 18, ['HALT.', 'Deepwatch Post.', 'Name yourself', 'at the gate.'], facing='west', wall=False)
    t.sign(26, W, 18, ['Above,', 'they sleep.'], facing='east', wall=False)
    t.sign(7, W + 1, 6, ['THIS SEASON', 'Zombies  41', 'Spiders  27', 'Skeletons  19'], facing='west')


def barbican():
    t = Template('post/barbican', (SX, SY, SZ))
    rng = t.rng
    cavern(t, rng)
    road(t, rng)
    wall_line(t, rng)
    keep(t, rng)
    barracks(t, rng)
    captain(t, rng)
    chamber(t, rng)
    deepgate(t, rng)
    courtyard(t, rng)
    armory(t, rng)
    drill_yard(t, rng)
    outer_yard(t, rng)
    t.anchor(22, F, 16, floor='polished_andesite')
    t.resident(21, W, 8, 'captain', 'south')
    t.resident(13, W, 21, 'warden_knight', 'west')
    t.resident(20, W, 14, 'warden_knight', 'south')
    t.resident(24, W, 28, 'warden_archer', 'east')
    t.resident(18, W, 16, 'warden_archer', 'west')
    line_rock(t, rng)
    return t


# -- the cave road beyond the post (every piece lit: the Watch keeps its road) -------------------------------

RZ = 9              # road pieces are 9 wide: rock 0, wall 1, road 2..6, wall 7, rock 8; the road is 5 high


def _road_run(t, rng, xs, level, h=5):
    """Floor, air and ragged walls for the road over columns xs; level(x) is the floor's y there."""
    for x in xs:
        y = level(x)
        for z in range(2, 7):
            t.set(x, y, z, pick(rng, ROAD))
        t.carve((x, y + 1, 2), (x, y + h, 6))
        for z in (1, 7):
            if rng.random() < 0.45:
                t.carve((x, y + 2, z), (x, y + 2 + rng.randint(0, 2), z))
        if rng.random() < 0.5:
            z = rng.randint(3, 5)
            t.carve((x, y + h + 1, z), (x, y + h + 1, z))


def _arch(t, rng, x, y):
    """A Deepwatch arch over the road at column x (floor at y): stone posts, a lintel and a hanging lamp."""
    for z in (1, 7):
        t.fill((x, y, z), (x, y + 4, z), mix(rng, STONE_BRICKS))
    t.fill((x, y + 5, 1), (x, y + 5, 7), mix(rng, STONE_BRICKS))
    t.set(x, y + 4, 2, stair('stone_brick', 'north', 'top'))
    t.set(x, y + 4, 6, stair('stone_brick', 'south', 'top'))
    hang(t, x, y + 4, 4)


def _niche_lamp(t, x, y, z):
    """A lantern on a stone sill in the road's wall (z = 1 or 7), floor at y."""
    t.set(x, y, z, 'stone_bricks')
    t.set(x, y + 1, z, 'lantern[hanging=false]')
    t.set(x, y + 2, z, 'air')


def road_straight():
    t = Template('post/road', (12, 8, RZ))
    rng = t.rng
    _road_run(t, rng, range(12), lambda x: 0)
    _arch(t, rng, 6, 0)
    for x, z in ((1, 1), (2, 7), (10, 1), (10, 7)):
        _niche_lamp(t, x, 1, z)
    t.jigsaw(0, 1, 4, 'west_up', 'post/road_in')
    t.jigsaw(11, 1, 4, 'east_up', 'post/road_out', target='post/road_in', pool='post/road')
    line_rock(t, rng)
    return t


def road_bend(right):
    """The road turning left (out north) or right (out south)."""
    t = Template('post/road_right' if right else 'post/road_left', (9, 8, RZ))
    rng = t.rng
    out_z, inner_z, outer_z = (8, 7, 1) if right else (0, 1, 7)
    _road_run(t, rng, range(7), lambda x: 0)
    for z in (range(0, 7) if not right else range(2, 9)):
        for x in range(2, 7):
            t.set(x, 0, z, pick(rng, ROAD))
            t.carve((x, 1, z), (x, 5, z))
    _niche_lamp(t, 1, 1, inner_z)
    _niche_lamp(t, 7, 1, outer_z)
    _niche_lamp(t, 7, 1, 4)
    t.jigsaw(0, 1, 4, 'west_up', 'post/road_in')
    t.jigsaw(4, 1, out_z, ('south' if right else 'north') + '_up', 'post/road_out', target='post/road_in',
             pool='post/road')
    line_rock(t, rng)
    return t


def road_slope(rise):
    """The road climbing (rise) or dropping three blocks over twelve, in steps."""
    t = Template('post/road_rise' if rise else 'post/road_fall', (12, 11, RZ))
    rng = t.rng
    level = (lambda x: x // 3) if rise else (lambda x: 3 - x // 3)
    _road_run(t, rng, range(12), level)
    for x in range(12):
        y = level(x)
        step = (rise and x % 3 == 0 and x > 0) or (not rise and x % 3 == 2 and x < 11)
        if step:
            for z in range(2, 7):
                t.set(x, y, z, stair('stone_brick', 'east' if rise else 'west'))
        if y > 0: t.fill((x, 0, 2), (x, y - 1, 6), mix(rng, [('cobblestone', 1), ('cobbled_deepslate', 1)]))
    _arch(t, rng, 7 if rise else 4, level(7 if rise else 4))
    _niche_lamp(t, 1, level(1) + 1, 1)
    if rise:
        _niche_lamp(t, 4, level(4) + 1, 7)
    else:
        _niche_lamp(t, 6, level(6) + 1, 1)
    _niche_lamp(t, 10, level(10) + 1, 7)
    t.jigsaw(0, level(0) + 1, 4, 'west_up', 'post/road_in')
    t.jigsaw(11, level(11) + 1, 4, 'east_up', 'post/road_out', target='post/road_in', pool='post/road')
    line_rock(t, rng)
    return t


def waypost():
    """A roadside watch niche: a bench, a lamp, a Deepwatch banner and a way-sign."""
    t = Template('post/waypost', (12, 8, 12))
    rng = t.rng
    _road_run(t, rng, range(12), lambda x: 0)
    t.fill((4, 0, 7), (8, 0, 10), mix(rng, STONE_BRICKS))
    t.carve((4, 1, 7), (8, 4, 9))
    t.fill((4, 5, 7), (8, 5, 10), mix(rng, STONE_BRICKS))
    t.fill((4, 1, 10), (8, 4, 10), mix(rng, STONE_BRICKS))
    for x in (4, 8):
        t.fill((x, 1, 7), (x, 4, 7), 'stripped_spruce_log[axis=y]')
    for x in (5, 6, 7):
        t.set(x, 1, 9, stair('spruce', 'south'))
    t.set(6, 2, 9, 'air')
    deepwatch_banner(t, 6, 3, 9, 'north')
    hang(t, 6, 4, 8)
    t.set(5, 1, 8, 'barrel[facing=up,open=false]')
    t.set(7, 1, 8, 'lantern[hanging=false]')
    t.sign(4, 2, 6, ['DEEPWATCH POST', 'along the road.', 'Keep a light', 'burning.'], facing='north')
    _niche_lamp(t, 1, 1, 1)
    _niche_lamp(t, 10, 1, 1)
    _niche_lamp(t, 10, 1, 7)
    t.jigsaw(0, 1, 4, 'west_up', 'post/road_in')
    t.jigsaw(11, 1, 4, 'east_up', 'post/road_out', target='post/road_in', pool='post/road')
    line_rock(t, rng)
    return t


def road_end():
    """Where the Watch's road gives out: the paving stops and a raw cave runs on into the dark."""
    t = Template('post/road_end', (9, 9, RZ))
    rng = t.rng
    _road_run(t, rng, range(4), lambda x: 0)
    for x in range(3, 9):                                  # the raw cave beyond, ragged and open at the far end
        w = 2 + (x % 2)
        lo = 1 if x < 6 else rng.randint(1, 2)
        t.carve((x, lo, 4 - w), (x, lo + 3 + rng.randint(0, 1), 4 + w - (x % 2)))
    rubble(t, rng, [(5, 1, 2), (6, 1, 2), (6, 2, 2), (7, 1, 6), (5, 1, 6)])
    t.set(7, 0, 4, 'cobbled_deepslate')
    lamp_post(t, 7, 1, 4, height=1)                                       # the Watch's last lamp
    lamp_post(t, 2, 1, 2, height=1)
    t.sign(3, 1, 6, ['ROAD ENDS.', 'Light behind you,', 'light ahead.'], facing='east', wall=False)
    t.jigsaw(0, 1, 4, 'west_up', 'post/road_in')
    line_rock(t, rng)
    return t


def pieces():
    return [barbican(), road_straight(), road_bend(False), road_bend(True), road_slope(True), road_slope(False),
            waypost(), road_end()]
