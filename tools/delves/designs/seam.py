"""The Buried Seam: a Delvers' Guild camp lost to a cave-in. The shift cut gold out of the pillars that held their
own roof; the gallery came down between them and the way out. The same Guild timber and rails as the Delvers'
Camp, wrecked: props snapped or gone, beams sagging, rails twisted and missing, rubble, cobwebs, bones.

Pieces (drifts share the Guild cross-section from guild_parts.py, along x, centre line z = 2):
  seam/gallery   the start piece: the wrecked gallery, robbed pillars, the cave-in, the foreman's shack with
                 "The Last Shift", the derailed cart, and behind the fall the rich seam (seam/rich chest)
  seam/drift     a wrecked drift              seam/sag     the roof half down, a crawl over the rubble
  seam/turn_r    a bend, a prop down          seam/turn_l  the same, mirrored
  seam/fall      a drift plugged by a fall (dig through)
  seam/stope     an abandoned working with ore, remains and a restless miner (also ends a branch)
  seam/nest      a side drift choked with cobwebs round a cave-spider spawner
  seam/cap       a drift ending in a collapse
"""
from kit import Template
from designs.guild_parts import (POST, PLANK, RUBBLE, pick, rock, line, veins, floor, rails, lantern, timber,
                                 drift, jig, heap, webs, candle, skull, remains, cart, mirrored)

KEY = 'seam'
NAME = 'The Buried Seam'
FEATURES = [
    'a Guild gallery wrecked by a cave-in: snapped and missing props, sagging beams, twisted rails with gaps',
    'robbed pillars: the rock left to hold the roof, cut to the waist for the gold in it',
    'the fall itself: a rubble slope up to a broken dome in the roof, crushed beams sticking out of it',
    "the foreman's shack, a candle still in the window: the lectern holds \"The Last Shift\", the log cut off mid-line",
    'a derailed chest minecart and the remains of the shift at the foot of the fall',
    'behind the fall, the rich seam: a sealed chamber crowded with gold, iron, redstone, lapis, a few diamonds and '
    'raw gold blocks, with the seam/rich chest and what is left of Tamsin and Young Pell',
    'restless miners rise in the gallery and in an old working',
    'a side drift choked with cobwebs round a cave-spider spawner',
    'drifts half buried by falls you must dig through or crawl over; dim: a few candles, one last lantern',
]
STRUCTURE = {
    'start_pool': 'seam/start', 'size': 5, 'horizontal': 46, 'vertical': 24,
    'min_y': -12, 'max_y': 32, 'cover': 10, 'inhabited': False, 'weight': 3, 'clearance': 10,
}
POOLS = {
    'seam/start': {'elements': [('seam/gallery', 1)]},
    'seam/drifts': {'elements': [('seam/drift', 5), ('seam/sag', 3), ('seam/turn_r', 2), ('seam/turn_l', 2),
                                 ('seam/fall', 2), ('seam/stope', 2)], 'fallback': 'seam/caps'},
    'seam/nests': {'elements': [('seam/nest', 1)], 'fallback': 'seam/caps'},
    'seam/caps': {'elements': [('seam/cap', 3), ('seam/stope', 1)]},
}

DOOR = 'seam/drift_in'
OUT = dict(target=DOOR, pool='seam/drifts')
# Floors of a mine left alone for years: moss has crept over the cobble.
OLD_FLOOR = [('cobblestone', 5), ('mossy_cobblestone', 3), ('cobbled_deepslate', 2), ('packed_mud', 2)]
# The rich seam: gold above all, and the rest the shift died for.
RICH = [('gold_ore', 26), ('deepslate_gold_ore', 8), ('iron_ore', 14), ('redstone_ore', 12), ('lapis_ore', 10),
        ('deepslate_redstone_ore', 4), ('copper_ore', 6), ('coal_ore', 4)]
WEB_FLOOR = 'cobweb'

LAST_SHIFT = [
    "THE LAST SHIFT\n\nLog of the camp at\nthe Seam, kept for\nthe Guild by\nforeman\nAldo Marrick.\n\nLight to you, and\nthe roof over you.",
    "Day 31. Iron poor,\ncoal worse. Tamsin\nsounded the gallery\nroof: rings true.\nBread on the first\nprop. Young Pell's\nfirst shift. Pell\nlit the first\nlantern proud as a\nlord.",
    "Day 36. Gold in the\npillars. Thick as\nfat in the stone we\nleft to hold the\nroof. Tamsin says\nleave it. The Guild\npays by the cart.\nWe took the edges\noff two pillars.\nOnly the edges.",
    "Day 39. The roof is\ntalking. Ticks in\nthe night, dust\ndown the props like\nflour. Tamsin\nsounded it and said\nnothing, which is\nworse. The face\npast the pillars is\nthe richest I have\nseen. Diamonds.\nThree more days.",
    "Day 41. Took the\nthird pillar to the\nwaist. Props\ngroaning. Tamsin\nand Pell at the\nrich face, the rest\nat the carts. Rang\nthe rail twice for\ntwo carts up. Dust\nagain, louder. I am\ngoing to call them\nout of the",
]

# -- the gallery ------------------------------------------------------------------------------------
# 29 x 12 x 19. The gallery runs x 1..21, z 5..17 (rail on z 11); the fall fills x 19..21 to the roof; the rich
# chamber lies behind it (x 22..26, z 8..14). The shack stands in the north-west corner. Exits: W (z 11) and S
# (x 6, straight out of the south wall) to drifts, N (x 10, up a short passage) to the spider drift.
GX, GY, GZ = 29, 12, 19
G0, G1 = 5, 17                      # gallery z range
RAIL_Z = 11
CH = (22, 26, 8, 14)                # rich chamber x0, x1, z0, z1


def gallery_frame(t, rng):
    """Floor, the open gallery and its ragged vault, the passages out, the rock around."""
    floor(t, (1, 0, G0), (21, 0, G1), rng, OLD_FLOOR)
    drift(t, 'z', 0, G0 - 1, 10, 0, rng, mix=OLD_FLOOR, ore=0.05)        # N: to the spider drift
    t.carve((1, 1, G0), (21, 6, G1))
    t.fill((2, 7, G0 + 1), (18, 7, G1 - 1), lambda x, y, z: 'air' if rng.random() < 0.85 else None)
    line(t, (1, 1, G0), (21, 6, G1), rng, ore=0.05)
    # W door, framed
    t.carve((0, 1, 10), (0, 3, 12))
    for z in (10, 11, 12): t.set(0, 0, z, pick(rng, OLD_FLOOR))
    for z in (9, 13):
        for y in (1, 2, 3): t.set(0, y, z, POST)
    for z in range(9, 14): t.set(0, 4, z, 'spruce_log[axis=z]')
    # S door, straight out of the gallery wall
    t.carve((5, 1, GZ - 1), (7, 3, GZ - 1))
    for x in (5, 6, 7): t.set(x, 0, GZ - 1, pick(rng, OLD_FLOOR))
    for x in (4, 8):
        for y in (1, 2, 3): t.set(x, y, GZ - 1, POST)
    for x in range(4, 9): t.set(x, 4, GZ - 1, 'spruce_log[axis=x]')


def slanted_beam(t, x, points):
    """A beam that has come down at one end: (z, y) for each block along it."""
    for z, y in points:
        t.set(x, y, z, 'spruce_log[axis=z]')


def gallery_timber(t, rng):
    """The props as the fall left them, and the robbed pillars."""
    # x 4: still whole, the last lantern hanging from it
    for z in (G0, G1):
        for y in range(1, 6): t.set(4, y, z, POST)
    for z in range(G0, G1 + 1): t.set(4, 6, z, 'spruce_log[axis=z]')
    lantern(t, 4, 5, RAIL_Z + 2)
    # x 8: the beam has cracked in the middle and sags
    for z in (G0, G1):
        for y in range(1, 6): t.set(8, y, z, POST)
    for z in range(G0, G1 + 1):
        if z in (9, 13): t.set(8, 6, z, 'spruce_slab[type=bottom,waterlogged=false]')
        elif 10 <= z <= 12: t.set(8, 5, z, 'spruce_log[axis=z]')
        else: t.set(8, 6, z, 'spruce_log[axis=z]')
    # x 12: the north post is gone and the beam's end is down on the floor
    for y in range(1, 6): t.set(12, y, G1, POST)
    slanted_beam(t, 12, [(17, 6), (16, 6), (15, 6), (14, 5), (13, 5), (12, 4), (11, 4), (10, 3), (9, 3), (8, 2),
                         (7, 1), (6, 1)])
    t.set(12, 1, G0, 'stripped_spruce_log[axis=x]')                     # the post, lying where it fell
    t.set(13, 1, G0, 'stripped_spruce_log[axis=x]')
    # x 16: half buried, its south post snapped
    for y in range(1, 6): t.set(16, y, G0, POST)
    t.set(16, 1, G1, POST)
    t.set(16, 2, G1, 'spruce_fence')
    for z in range(G0, 12): t.set(16, 6, z, 'spruce_log[axis=z]')
    # robbed pillars: rock left standing to hold the roof, its gold cut out to the waist
    north = [(9, 6), (10, 6), (9, 7), (10, 7)]
    south = [(9, 15), (10, 15), (9, 16), (10, 16)]
    for (x, z) in north + south:
        for y in range(1, 7):
            t.set(x, y, z, rock(rng, 0.15, [('gold_ore', 3), ('iron_ore', 1)]))
    for y in (2, 3, 4):                                                 # the north one, to the waist
        for (x, z) in ((9, 7), (10, 7), (9, 6)):
            t.set(x, y, z, 'air')
        t.set(10, y, 6, 'gold_ore' if y == 3 else 'stone')
    for y in (2, 3):                                                    # the south one, "only the edges"
        t.set(10, y, 15, 'air')
        t.set(9, y, 15, 'gold_ore')
    t.set(9, 1, 8, 'cobblestone')                                       # chips at the pillar's foot
    t.set(10, 1, 8, 'gravel')
    t.set(11, 1, 14, 'cobblestone_slab[type=bottom,waterlogged=false]')


def gallery_collapse(t, rng):
    """The fall: a dome broken out of the roof, a rubble slope up into it and a solid wall of rubble beyond, crushed
    timber in it, the shift's remains at its foot, the derailed cart."""
    for x in range(13, 21):                               # the dome the roof fell out of
        for z in range(G0 + 1, G1):
            for y in range(7, 11):
                if (x - 17) ** 2 + (z - 11) ** 2 * 1.3 + ((y - 6) * 1.7) ** 2 < 34 + rng.random() * 6:
                    t.set(x, y, z, 'air')
    noise = {(x, z): rng.random() for x in range(12, 22) for z in range(G0, G1 + 1)}

    def height(x, z):
        if x >= 19: return 99
        return max(0.0, (x - 13.3) * 1.45 + noise[(x, z)] * 0.9 - abs(z - 11) * 0.18)
    heap(t, 12, 18, G0, G1, 0, height, rng, slabs=0.6)
    for x in range(19, 22):                               # the wall: every open cell of the gallery filled
        for z in range(G0, G1 + 1):
            for y in range(1, 11):
                if t.name_at(x, y, z) == 'minecraft:air':
                    t.set(x, y, z, pick(rng, RUBBLE))
    # what the dome lets down onto the slope and the beams crushed into it
    for (x, z) in ((15, 8), (16, 13), (17, 10)):
        y = 1
        while t.name_at(x, y, z) not in (None, 'minecraft:air') and y < 9: y += 1
        if t.name_at(x, y, z) == 'minecraft:air': t.set(x, y, z, 'spruce_log[axis=x]')
    for (x, z, axis) in ((14, 9, 'z'), (14, 10, 'z'), (17, 14, 'x'), (18, 14, 'x')):
        y = 1
        while t.name_at(x, y, z) not in (None, 'minecraft:air') and y < 9: y += 1
        if t.name_at(x, y, z) == 'minecraft:air': t.set(x, y, z, f'spruce_log[axis={axis}]')
    if t.name_at(15, 4, 12) == 'minecraft:air':
        t.set(15, 4, 12, 'spruce_fence')                      # a snapped post end
    # the shift, where the fall caught them
    remains(t, [(13, 1, 8, 'x'), (14, 1, 13, 'z')], rng, skull_at=(13, 1, 9), rotation=4)
    remains(t, [(12, 1, 15, 'x')], rng, skull_at=(13, 1, 15), rotation=2)
    candle(t, 13, 1, 10, n=2, lit=False, color='white')
    # the cart, knocked off the line
    cart(t, 11, 1, 13, loot='seam/cart', facing='east', yaw=-62.0)
    t.set(12, 1, 12, 'rail[shape=north_east]')
    t.set(12, 1, 13, 'gravel')


def gallery_shack(t, rng):
    """The foreman's shack: plank walls on log corners, the door left open, a candle burning in the window."""
    x0, x1, z0, z1 = 1, 7, G0, 9
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            t.set(x, 0, z, PLANK)
            for y in (1, 2, 3):
                edge = x in (x0, x1) or z in (z0, z1)
                corner = x in (x0, x1) and z in (z0, z1)
                if corner: t.set(x, y, z, 'spruce_log[axis=y]')
                elif edge: t.set(x, y, z, PLANK if rng.random() > 0.08 or y == 1 else 'air')
                else: t.set(x, y, z, 'air')
            t.set(x, 4, z, 'spruce_slab[type=bottom,waterlogged=false]' if rng.random() > 0.1 else 'air')
    t.set(3, 5, 6, 'cobblestone')                                      # a stone come down on the roof
    t.set(4, 5, 7, 'gravel')
    t.door(4, 1, z1, 'south', kind='spruce_door', hinge='left', open_=True)
    t.set(x1, 2, 7, 'air')                                             # the window, a candle in it
    candle(t, x1, 2, 7, n=1, lit=True)
    t.set(x1, 3, 7, PLANK)
    # inside: the log, the strongbox, a cot, the foreman's things
    t.lectern(5, 1, z0 + 1, 'south', 'The Last Shift', 'Aldo Marrick', LAST_SHIFT)
    t.chest(2, 1, z0 + 1, 'south', 'seam/shack')
    t.bed(2, 1, z1 - 1, 'north', color='brown')
    t.set(6, 1, z1 - 1, 'barrel[facing=up,open=false]')
    candle(t, 6, 2, z1 - 1, n=3, lit=False)
    t.set(6, 1, z0 + 1, 'spruce_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]')
    t.item_frame(3, 2, z0 + 1, 'south', 'paper')
    t.item_frame(4, 3, z0 + 1, 'south', 'compass')
    webs(t, [(6, 3, z0 + 1), (2, 3, z1 - 1), (3, 3, z1 - 1)], rng, p=1.0)
    t.sign(5, 2, z1 + 1, ['FOREMAN', 'A. Marrick', '', 'knock'], facing='south')


def gallery_rich(t, rng):
    """Behind the fall, the rich seam they died for: walls and roof crowded with ore, raw gold, a few diamonds,
    the seam/rich chest, and Tamsin and Young Pell, with Pell's first lantern beside them."""
    cx0, cx1, cz0, cz1 = CH
    floor(t, (cx0, 0, cz0), (cx1, 0, cz1), rng, [('cobblestone', 3), ('cobbled_deepslate', 2), ('mossy_cobblestone', 1)])
    t.carve((cx0, 1, cz0), (cx1, 4, cz1))
    t.carve((cx0 + 1, 5, cz0 + 1), (cx1 - 1, 5, cz1 - 1))
    line(t, (cx0, 1, cz0), (cx1, 4, cz1), rng, ore=0.8, ores=RICH, ceiling=True)
    line(t, (cx0 + 1, 5, cz0 + 1), (cx1 - 1, 5, cz1 - 1), rng, ore=0.8, ores=RICH, ceiling=True)
    line(t, (cx0 - 1, 0, cz0 - 1), (cx1 + 1, 5, cz1 + 1), rng, ore=0.4, ores=RICH)
    for pos in ((27, 2, 10), (27, 3, 13), (24, 6, 11), (23, 2, 7)):      # the few diamonds
        t.set(*pos, 'diamond_ore')
    t.set(27, 1, 11, 'deepslate_diamond_ore')
    for pos in ((27, 2, 12), (25, 6, 10), (26, 3, 15)):                  # raw gold, in the rock and in a heap
        t.set(*pos, 'raw_gold_block')
    t.set(26, 1, 13, 'raw_gold_block')
    t.set(26, 1, 14, 'raw_gold_block')
    t.set(26, 2, 14, 'gold_ore')
    # the far side of the fall spills in
    heap(t, cx0, cx0 + 1, cz0, cz1, 0, lambda x, z: (2.6 if x == cx0 else 1.4) - abs(z - 11) * 0.2, rng)
    # the rich chest, what's left of the two at the face, Pell's first lantern
    t.chest(cx1, 1, 9, 'west', 'seam/rich')
    remains(t, [(25, 1, 12, 'x'), (24, 1, 12, 'x')], rng, skull_at=(25, 1, 11), rotation=6)       # Tamsin
    remains(t, [(25, 1, 9, 'z')], rng, skull_at=(24, 1, 9), rotation=10)                          # Pell
    t.item_frame(24, 1, 10, 'up', 'lantern')
    candle(t, 23, 1, 13, n=1, lit=False)
    candle(t, cx1, 1, 12, n=2, lit=False, color='brown')
    t.item_frame(24, 2, cz0, 'south', 'iron_pickaxe')
    webs(t, [(x, 4, z) for x in range(cx0, cx1 + 1) for z in (cz0, cz1)], rng, p=0.4)
    t.notes['rich_seam'] = (24, 1, 11)


def gallery():
    t = Template('seam/gallery', (GX, GY, GZ))
    rng = t.rng
    gallery_frame(t, rng)
    gallery_timber(t, rng)
    rails(t, 'x', 1, 14, RAIL_Z, 1, rng, gap=0.25, twist=0.12)
    rails(t, 'z', 14, G1, 6, 1, rng, gap=0.3, twist=0.1)
    gallery_collapse(t, rng)
    gallery_rich(t, rng)
    gallery_shack(t, rng)
    # years of cobwebs in the roof corners and round the props
    corners = [(x, y, z) for x in range(1, 19) for y in (4, 5, 6) for z in (G0, G0 + 1, G1 - 1, G1)]
    corners += [(x, y, z) for x in (3, 5, 7, 9, 11, 13, 15) for y in (5, 6) for z in range(G0, G1 + 1)]
    webs(t, corners, rng, p=0.09)
    webs(t, [(x, y, z) for x in (9, 10, 11) for y in (2, 3) for z in (1, 2, 3)], rng, p=0.35)
    # burnt-down candles where the shift left them
    candle(t, 1, 1, 15, n=4, lit=False)
    candle(t, 3, 1, G1, n=1, lit=False, color='brown')
    t.set(2, 1, G1, 'barrel[facing=up,open=false]')
    t.set(2, 2, G1, 'skeleton_skull[rotation=3]')
    t.item_frame(4, 2, G1 - 1, 'north', 'bread')                    # the crust on the first prop, gone green
    # the restless shift
    t.haunt(11, 1, 8, 'restless_miner')
    for y in (2, 3): t.set(11, y, 8, 'air')
    t.anchor(6, 0, RAIL_Z, floor='mossy_cobblestone')
    jig(t, 0, 1, RAIL_Z, 'west', 'seam/door', **OUT)
    jig(t, 6, 1, GZ - 1, 'south', 'seam/door', **OUT)
    jig(t, 10, 1, 0, 'north', 'seam/side', target=DOOR, pool='seam/nests', rail=False)
    return t


# -- drifts -----------------------------------------------------------------------------------------

def lichen(t, cells):
    """Glow lichen creeping over the floor (it holds to the built floor, so it is always there)."""
    for c in cells:
        if t.name_at(*c) == 'minecraft:air':
            t.set(*c, 'glow_lichen[down=true,east=false,north=false,south=false,up=false,west=false,waterlogged=false]')


def roof_webs(t, x0, x1, rng, c=2, p=0.25):
    webs(t, [(x, y, z) for x in range(x0, x1 + 1) for y in (2, 3) for z in (c - 1, c + 1)], rng, p=p)


def wrecked():
    """A drift as the shift left it: one prop whole, one snapped, one beam bowed; the rail half gone."""
    t = Template('seam/drift', (12, 6, 5))
    rng = t.rng
    drift(t, 'x', 0, 11, 2, 0, rng, mix=OLD_FLOOR, ore=0.06)
    timber(t, 'x', 1, 2, 0)
    timber(t, 'x', 5, 2, 0, state='broken')
    timber(t, 'x', 9, 2, 0, state='sag')
    rails(t, 'x', 0, 11, 2, 1, rng, gap=0.35, twist=0.12)
    heap(t, 6, 8, 3, 3, 0, lambda x, z: 1.6 - abs(x - 7) * 0.7, rng)
    roof_webs(t, 0, 11, rng)
    candle(t, 3, 1, 1, n=1, lit=False)
    lichen(t, [(10, 1, 1), (10, 1, 3), (11, 1, 3)])
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 11, 1, 2, 'east', 'seam/drift_out', **OUT)
    return t


def sag():
    """The roof half down: a beam fallen across, a bank of rubble to crawl over, two blocks of headroom."""
    t = Template('seam/sag', (12, 6, 5))
    rng = t.rng
    drift(t, 'x', 0, 11, 2, 0, rng, mix=OLD_FLOOR, ore=0.05)
    timber(t, 'x', 1, 2, 0)
    timber(t, 'x', 5, 2, 0, state='left')
    timber(t, 'x', 10, 2, 0, state='no_beam')
    rails(t, 'x', 0, 3, 2, 1, rng, gap=0.3)
    rails(t, 'x', 9, 11, 2, 1, rng, gap=0.3)
    for x in range(4, 9):                         # the bank: a full layer, and a second one along one wall
        for z in (1, 2, 3):
            if t.name_at(x, 1, z) == 'minecraft:air': t.set(x, 1, z, pick(rng, RUBBLE))
        if 5 <= x <= 7 and t.name_at(x, 2, 3) == 'minecraft:air': t.set(x, 2, 3, pick(rng, RUBBLE))
    for x in (3, 9):
        t.set(x, 1, 2, 'cobblestone_slab[type=bottom,waterlogged=false]')
    for x in (4, 6, 7, 8):                        # the hole it came from
        for z in (1, 2, 3):
            if rng.random() < 0.6: t.set(x, 4, z, 'air')
    t.set(7, 2, 1, 'spruce_log[axis=x]')           # a beam lying on the bank
    t.set(8, 2, 1, 'spruce_log[axis=x]')
    remains(t, [(6, 2, 2, 'z')], rng, skull_at=(6, 2, 1), rotation=12)
    roof_webs(t, 0, 3, rng, p=0.4)
    roof_webs(t, 9, 11, rng, p=0.4)
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 11, 1, 2, 'east', 'seam/drift_out', **OUT)
    return t


def bend():
    """A bend: in from the west, out to the south (seam/turn_l is its mirror). The corner post has given way."""
    t = Template('seam/turn_r', (7, 6, 7))
    rng = t.rng
    drift(t, 'x', 0, 5, 2, 0, rng, mix=OLD_FLOOR, ore=0.06)
    drift(t, 'z', 1, 6, 4, 0, rng, mix=OLD_FLOOR, ore=0.06)
    timber(t, 'x', 1, 2, 0, state='sag')
    timber(t, 'z', 5, 4, 0, state='broken')
    t.set(6, 1, 2, POST)                           # the corner post, snapped at the knee
    t.set(6, 2, 2, 'spruce_fence')
    t.set(5, 1, 1, 'spruce_log[axis=x]')           # its top half on the floor
    rails(t, 'x', 0, 3, 2, 1, rng, gap=0.3)
    t.set(4, 1, 2, 'rail[shape=south_west]')
    rails(t, 'z', 3, 6, 4, 1, rng, gap=0.4, twist=0.2)
    heap(t, 5, 5, 1, 3, 0, lambda x, z: 1.5, rng)
    webs(t, [(x, y, z) for x in range(1, 6) for y in (2, 3) for z in (1, 3)], rng, p=0.3)
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 4, 1, 6, 'south', 'seam/drift_out', **OUT)
    return t


def fall():
    """A drift plugged by a fall from wall to wall; the drift goes on beyond it, if you dig."""
    t = Template('seam/fall', (12, 6, 5))
    rng = t.rng
    drift(t, 'x', 0, 11, 2, 0, rng, mix=OLD_FLOOR, ore=0.05)
    timber(t, 'x', 1, 2, 0, state='sag')
    timber(t, 'x', 9, 2, 0)
    t.set(5, 1, 0, POST)                           # a post stump in the wall where the fall broke it
    t.set(5, 1, 4, POST)
    rails(t, 'x', 0, 3, 2, 1, rng, gap=0.2)
    rails(t, 'x', 9, 11, 2, 1, rng, gap=0.4)
    for x in range(3, 9):                          # the plug, with slopes either side
        full = 4 <= x <= 7
        for z in (1, 2, 3):
            top = 3 if full else 1
            for y in range(1, top + 1):
                t.set(x, y, z, pick(rng, RUBBLE))
            if full: t.set(x, 4, z, pick(rng, RUBBLE))
    t.set(2, 1, 2, 'cobblestone_slab[type=bottom,waterlogged=false]')
    t.set(6, 2, 2, 'spruce_log[axis=x]')           # a beam inside the plug
    t.set(5, 3, 1, 'spruce_log[axis=z]')
    skull(t, 3, 2, 1, rotation=5)                  # someone was on the wrong side of it
    t.set(3, 2, 3, 'bone_block[axis=z]')
    roof_webs(t, 0, 2, rng, p=0.5)
    roof_webs(t, 9, 11, rng, p=0.4)
    jig(t, 0, 1, 2, 'west', DOOR)
    jig(t, 11, 1, 2, 'east', 'seam/drift_out', **OUT)
    return t


def working():
    """An abandoned working at a drift's end: ore still in the face, a toppled scaffold, a miner who never left
    (a restless miner rises here). Ends the branch."""
    t = Template('seam/stope', (12, 7, 10))
    rng = t.rng
    c = 5
    drift(t, 'x', 9, 11, c, 0, rng, mix=OLD_FLOOR, ore=0.06)
    floor(t, (2, 0, 2), (8, 0, 8), rng, OLD_FLOOR)
    t.carve((2, 1, 2), (8, 5, 8))
    line(t, (2, 1, 2), (8, 5, 8), rng, ore=0.45, ceiling=True)
    for y in range(0, 7):
        for z in range(0, 10):
            if (0, y, z) not in t.blocks: t.set(0, y, z, rock(rng, 0.25))
    veins(t, [(1, y, z) for y in range(1, 6) for z in range(2, 9)], rng, p=0.35)
    for (x, z) in ((3, 2), (7, 2), (7, 8)):         # three cribbing posts stand; the fourth is down
        for y in range(1, 5): t.set(x, y, z, POST)
    t.set(3, 1, 8, POST)
    t.set(4, 1, 7, 'stripped_spruce_log[axis=x]')
    t.set(5, 1, 7, 'stripped_spruce_log[axis=x]')
    for x in range(2, 9): t.set(x, 5, 2, 'spruce_log[axis=x]')
    for z in range(3, 8): t.set(7, 5, z, 'spruce_log[axis=z]')
    for x in (5, 6): t.set(x, 4, 8, 'spruce_slab[type=bottom,waterlogged=false]')    # the beam hanging off
    timber(t, 'x', 10, c, 0, state='sag')
    rails(t, 'x', 5, 11, c, 1, rng, gap=0.35)
    # a toppled scaffold and a cart on its side
    for x in (2, 3, 4): t.set(x, 1, 3, 'scaffolding[bottom=true,distance=0,waterlogged=false]')
    t.set(2, 2, 3, 'scaffolding[bottom=false,distance=0,waterlogged=false]')
    t.minecart(4, 1, 6, facing='north')
    heap(t, 2, 3, 4, 8, 0, lambda x, z: 1.3 if x == 2 else 0.6, rng)
    remains(t, [(5, 1, 4, 'x')], rng, skull_at=(6, 1, 4), rotation=9)
    t.item_frame(7, 2, 3, 'south', 'iron_pickaxe')
    candle(t, 2, 1, 7, n=2, lit=False)
    webs(t, [(x, y, z) for x in range(2, 9) for y in (4, 5) for z in (3, 7)], rng, p=0.35)
    lichen(t, [(8, 1, 3), (8, 1, 4), (6, 1, 6)])
    t.haunt(5, 1, 5, 'restless_miner')
    for y in (2, 3): t.set(5, y, 5, 'air')
    jig(t, 11, 1, c, 'east', DOOR)
    return t


def nest():
    """A side drift the spiders took: a chamber choked with cobwebs round a cave-spider spawner, a warning on the
    prop at its mouth, a victim wrapped in the webs. The drift goes on beyond."""
    t = Template('seam/nest', (11, 6, 11))
    rng = t.rng
    c = 5
    drift(t, 'x', 0, 2, c, 0, rng, mix=OLD_FLOOR, ore=0.05)
    drift(t, 'x', 9, 10, c, 0, rng, mix=OLD_FLOOR, ore=0.05)
    floor(t, (3, 0, 1), (8, 0, 9), rng, OLD_FLOOR)
    t.carve((3, 1, 1), (8, 4, 9))
    for (x, z) in ((3, 1), (8, 1), (3, 9), (8, 9), (3, 2), (8, 8)):   # rounded off: a natural pocket they broke into
        t.set(x, 4, z, None)
    line(t, (3, 1, 1), (8, 4, 9), rng, ore=0.05, ceiling=False)
    timber(t, 'x', 1, c, 0, state='broken')
    t.spawner(6, 1, 5, 'minecraft:cave_spider')
    webs(t, [(x, y, z) for x in range(3, 9) for y in range(1, 5) for z in range(1, 10)
             if (x, z) != (6, 5) and abs(z - c) + abs(x - 6) > 1], rng, p=0.33)
    webs(t, [(x, y, z) for x in range(0, 3) for y in (2, 3) for z in (4, 6)], rng, p=0.5)
    remains(t, [(4, 1, 8, 'x')], rng, skull_at=(5, 1, 8), rotation=1)
    t.set(4, 2, 8, 'cobweb')
    t.set(5, 2, 8, 'cobweb')
    lichen(t, [(7, 1, 2), (4, 1, 3), (8, 1, 7)])
    t.set(2, 1, 3, POST)                           # a warning nailed up at the mouth
    t.set(2, 2, 3, POST)
    t.sign(2, 2, 4, ['KEEP OUT', 'spiders', '', '- A.M.'], facing='south')
    jig(t, 0, 1, c, 'west', DOOR, rail=False)
    jig(t, 10, 1, c, 'east', 'seam/drift_out', **OUT)
    return t


def cap():
    """A drift that ends where the roof came down: rubble to the roof, a hand of bone in it."""
    t = Template('seam/cap', (5, 6, 5))
    rng = t.rng
    drift(t, 'x', 0, 4, 2, 0, rng, mix=OLD_FLOOR, ore=0.06)
    timber(t, 'x', 1, 2, 0, state='right')
    heap(t, 2, 4, 1, 3, 0, lambda x, z: (x - 1.6) * 1.6, rng)
    for z in (1, 2, 3):
        for y in (1, 2, 3):
            if t.name_at(4, y, z) == 'minecraft:air': t.set(4, y, z, pick(rng, RUBBLE))
    if t.name_at(2, 2, 2) == 'minecraft:air':
        skull(t, 2, 2, 2, rotation=4)
    roof_webs(t, 0, 2, rng, p=0.4)
    rails(t, 'x', 0, 1, 2, 1, rng, gap=0.3)
    jig(t, 0, 1, 2, 'west', DOOR)
    return t


def pieces():
    b = bend()
    return [gallery(), wrecked(), sag(), b, mirrored(b, 'seam/turn_l'), fall(), working(), nest(), cap()]
