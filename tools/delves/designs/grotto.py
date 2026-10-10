"""The Glimmering: a vast natural amethyst-and-calcite cavern, the Old Delvers' holy place.

The start piece is one great cavern (carved air) lined like a geode, in soft layers: crystal and calcite with
budding amethyst, smooth-basalt veins and dripstone on the inner face, calcite behind it and a smooth-basalt
shell outside (so a strip-miner breaking in meets basalt, then calcite, then crystal). The floor is soft
calcite and crystal over a built sub-floor, so it holds even where a cave runs under it. In the middle stands
the Old Delvers' crystal shrine: a worn tiled platform, a ring of deepslate-tile pillars crowned with candles
and amethyst, and a dais with the Great Lantern (their mark), the shrine chest and offering pots. A still pool
glows from below. Worn processional paths come down from three tunnel mouths (jigsaw tunnels with caps).
Abandoned and dim: candles someone still lights, crystal, glow lichen and the pool. No haunt, no residents.
"""
import math

from kit import Template
from .cavern_parts import (Cavern, noise, relax, seal_water, hang, stalagmite, stairs_on_steps, polar,
                           ring_noise, path4, side_of, SOFT)

KEY = 'grotto'
NAME = 'The Glimmering'
FEATURES = [
    'a vast natural cavern lined like a geode: amethyst, budding amethyst, calcite, smooth-basalt veins',
    'crystal clusters and buds, dripstone stalactites and glow lichen glittering in the dark',
    "the Old Delvers' crystal shrine: a ring of deepslate-tile pillars crowned with candles and amethyst",
    'a dais with the Great Lantern (the Old Delvers\' mark), the shrine chest and offering pots',
    'a still pool glowing from below with sea lanterns and froglights, crystals growing under the water',
    'old carvings (signs) in the Old Delvers\' voice, worn processional paths with tile steps',
    'three tunnel mouths (jigsaw passages ending in old collapses); no guardians: the reward is finding it',
]
STRUCTURE = {
    'start_pool': 'grotto/start', 'size': 3, 'horizontal': 60, 'vertical': 20,
    'min_y': -44, 'max_y': -8, 'cover': 12, 'inhabited': False, 'weight': 2, 'clearance': 14,
}
POOLS = {
    'grotto/start': {'elements': [('grotto/glimmering', 1)]},
    'grotto/tunnels': {'elements': [('grotto/passage', 3), ('grotto/turn', 2), ('grotto/cap', 1)],
                       'fallback': 'grotto/caps'},
    'grotto/caps': {'elements': [('grotto/cap', 1)]},
}

# Carvings in the Old Delvers' voice (pale signs, black letters, like cut stone).
CARVINGS = [
    ['WE CAME DOWN', 'WITH LANTERNS', 'AND THE STONE', 'LIT BACK.'],
    ['A LANTERN', 'OVER TWO PICKS', 'MARKS THE', "DELVERS' WAY."],
    ['BRING NO PICK', 'TO THESE WALLS', 'HERE WE ONLY', 'LOOK.'],
    ['LEAVE A LIGHT', 'FOR THOSE', 'WHO COME', 'AFTER.'],
]
POOL_CARVING = ['THE WATER', 'REMEMBERS', 'EVERY FACE', 'IT HAS SEEN.']
MOUTH_CARVING = ['GO SOFTLY.', 'THE STONE', 'IS LISTENING.', '']

SX, SY, SZ = 36, 22, 36
CX, CZ = 18, 18
FB = 3              # the floor block's y at the shrine; people walk at W
W = FB + 1
POOL = (8.5, 26.5, 4.4, 3.0)      # centre x, z and radii of the pool
# tunnel mouths: (face cell x, z), the jigsaw's orientation, the floor's y at the mouth
MOUTHS = [((SX - 1, 18), 'east_up', FB + 3), ((20, 0), 'north_up', FB + 2), ((0, 13), 'west_up', FB + 1)]
PILLARS = 8
PILLAR_R = 6.6
DAIS_R = 3


def worn_tile(rng):
    r = rng.random()
    return ('deepslate_tiles' if r < 0.55 else 'cracked_deepslate_tiles' if r < 0.8 else
            'polished_deepslate' if r < 0.93 else 'cobbled_deepslate')


def geode(vein, mix, rng):
    """Soft lining in a geode's layers: crystal and calcite with basalt veins on the inner face (dripstone on
    the roof, tuff on the floor), calcite behind it, smooth basalt outside."""
    def pick(x, y, z, d, kind):
        v, m = vein[x, y, z], mix[x, y, z]
        if d >= 3: return 'smooth_basalt'
        if d == 2: return 'smooth_basalt' if abs(v) < 0.05 else 'calcite'
        if abs(v) < 0.055: return 'smooth_basalt'
        if kind == 'ceiling' and m < -0.36: return 'dripstone_block'
        if kind == 'floor' and m < -0.4: return 'tuff'
        if m > 0.2: return 'budding_amethyst' if rng.random() < 0.35 else 'amethyst_block'
        if m > -0.05: return 'amethyst_block' if rng.random() < 0.6 else 'calcite'
        return 'calcite'
    return pick


def soft_floor(vein, mix, rng, x, y, z):
    """The top of the cavern floor away from the paths: soft, so it looks like the rest of the geode."""
    v, m = vein[x, y, z], mix[x, y, z]
    if abs(v) < 0.06: return 'smooth_basalt'
    if m < -0.4: return 'tuff'
    if m > 0.3 and rng.random() < 0.3: return 'budding_amethyst'
    if m > 0.15: return 'amethyst_block'
    return 'calcite'


def sub_floor(name):
    """The built bed under a soft floor block, chosen to look like it if the soft block is skipped."""
    return {'minecraft:tuff': 'polished_tuff', 'minecraft:smooth_basalt': 'polished_basalt[axis=y]'}.get(
        name, 'polished_diorite')


PROPS = ('stairs', 'slab', 'candle', '_sign', 'decorated_pot', 'chest', 'lantern')


def underpin(t):
    """Anything that stands on the floor (steps, slabs, candles, signs, pots) gets a built block under it in
    place of a soft one, so it never hangs in the air where the world's cave took the soft block away."""
    for (x, y, z), (name, props) in sorted(t.blocks.items()):
        if y == 0 or not any(w in name for w in PROPS) or 'wall_sign' in name or props.get('hanging') == 'true':
            continue
        if name in ('minecraft:sea_lantern',): continue
        below = t.name_at(x, y - 1, z)
        if below in SOFT: t.set(x, y - 1, z, sub_floor(below))


# Centre lines from each mouth's face cell to the edge of the shrine platform.
ROUTES = [[(SX - 1, 18), (30, 18), (26, 18)],
          [(20, 0), (20, 5), (19, 10)],
          [(0, 13), (4, 13), (7, 17), (11, 18)]]
CORRIDOR = 6        # route cells from the face that are tunnel, not cavern


def shape(t):
    """Carve the cavern, its three mouths and the pool's alcove; lay the floor (soft over a built bed, worn
    tiles on the paths, steps where they drop). Returns (cavern, water cells, path cells -> floor y)."""
    rng = t.rng
    cav = Cavern(t)
    edge = ring_noise(31)
    roof = noise((SX, SZ), 32, 7)
    bank = noise((SX, SZ), 33, 5)
    px, pz, rx, rz = POOL
    pa = math.atan2(pz - CZ, px - CX)
    for x in range(SX):
        for z in range(SZ):
            a, r = polar(x, z, CX, CZ)
            da = (a - pa + math.pi) % (2 * math.pi) - math.pi
            R = max(12.5, min(16.4, 14.4 + 1.9 * edge(a) + 2.0 * math.exp(-da * da / 0.25)))
            u = r / R
            if u >= 1: continue
            dome = (16.0 * (1 - u ** 3) ** 0.5 + 2.5 * math.exp(-((x - 24) ** 2 + (z - 12) ** 2) / 40)
                    + 1.4 * roof[x, z])
            lift = 0 if u < 0.5 else max(0, round((u - 0.5) * 10 + 1.5 * bank[x, z]))
            cav.add_column(x, z, FB + min(lift, 5), min(SY - 2, FB + max(1, round(dome))))

    fixed = set()
    # the shrine platform and the pool's alcove are flat at FB
    for x in range(SX):
        for z in range(SZ):
            e = ((x - px) / rx) ** 2 + ((z - pz) / rz) ** 2
            if math.hypot(x - CX, z - CZ) <= 8.6 or e < 1.5:
                cav.add_column(x, z, FB, FB + (5 if e < 1.5 else 8))
                cav.floor[(x, z)] = FB
                fixed.add((x, z))
    # mouths: a short natural tunnel from each face, then a worn path stepping down to the platform
    paths = {}
    for ((fx, fz), orient, fy), pts in zip(MOUTHS, ROUTES):
        route = path4(pts)
        for i, c in enumerate(route):
            h = fy if i < CORRIDOR else max(FB, fy - (i - CORRIDOR + 2) // 2)
            cells = [c] + list(side_of(route, i)) if i < CORRIDOR else [c, side_of(route, i)[i // 3 % 2]]
            for (x, z) in cells:
                if not (0 <= x < SX and 0 <= z < SZ) or (x, z) in fixed and (x, z) not in paths: continue
                tall = h + 4 + (1 if rng.random() < 0.4 else 0) - (1 if (x, z) != c else 0)
                cav.add_column(x, z, h, tall)
                cav.floor[(x, z)] = h
                cav.ceil[(x, z)] = max(cav.ceil[(x, z)], tall)
                paths[(x, z)] = h
                fixed.add((x, z))
    relax(cav.floor, 1, lower=True, fixed=fixed)
    relax(cav.floor, 1, lower=False, fixed=fixed)
    for c in cav.floor:
        cav.ceil[c] = max(cav.ceil[c], cav.floor[c] + 2)

    # the pool: still water flush with the platform, up to three deep
    water = set()
    for x in range(SX):
        for z in range(SZ):
            e = ((x - px) / rx) ** 2 + ((z - pz) / rz) ** 2 + 0.25 * bank[x, z]
            if e < 1 and (x, z) in cav.floor and math.hypot(x - CX, z - CZ) > 9.6:
                water.add((x, FB, z))
                if e < 0.6: water.add((x, FB - 1, z))
                if e < 0.25: water.add((x, FB - 2, z))
    cav.carve()

    # the floor: soft geode on a built bed; worn tiles on the paths (a few gone to calcite)
    vein = noise((SX, SY, SZ), 34, 7)
    mix = noise((SX, SY, SZ), 35, 5)
    for (x, z), f in sorted(cav.floor.items()):
        if (x, f, z) in water: continue
        if (x, z) in paths and rng.random() > 0.08:
            t.set(x, f, z, worn_tile(rng))
            t.set(x, f - 1, z, 'cobbled_deepslate')
        else:
            top = soft_floor(vein, mix, rng, x, f, z)
            t.set(x, f, z, top)
            t.set(x, f - 1, z, sub_floor('minecraft:' + top))
    stairs_on_steps(t, cav, set(paths), 'deepslate_tile_stairs')

    # the pool's bed: pale stone, a few lights and crystals under the water
    glows = ['sea_lantern', 'pearlescent_froglight[axis=y]', 'sea_lantern', 'verdant_froglight[axis=y]']
    bottoms = sorted(p for p in water if (p[0], p[1] - 1, p[2]) not in water)
    for (x, y, z) in water: t.set(x, y, z, 'water')
    for i, (x, y, z) in enumerate(bottoms):
        t.set(x, y - 1, z, 'polished_diorite' if (x * 7 + z * 3) % 5 else 'polished_tuff')
    deep = [p for p in bottoms if p[1] <= FB - 1]
    for i, (x, y, z) in enumerate(deep[2::max(1, len(deep) // 4)][:4]):
        t.set(x, y - 1, z, glows[i])
    for (x, y, z) in deep[1::5][:5]:
        t.set(x, y, z, rng.choice(('amethyst_cluster', 'large_amethyst_bud')) + '[facing=up,waterlogged=true]')
    return cav, water, paths, vein, mix


DIR = {(1, 0): 'east', (-1, 0): 'west', (0, 1): 'south', (0, -1): 'north'}
STAIR = '{}[facing={},half={},shape=straight,waterlogged=false]'


def pillar(t, x, z, height, top, rng):
    """A deepslate-tile pillar on the platform with a flared base and capital, crowned by `top` (or broken
    off short when height < 4, its fallen piece lying on the floor)."""
    t.set(x, W, z, 'polished_deepslate')
    for (dx, dz) in DIR:
        if t.get(x + dx, W, z + dz) == 'air':
            t.set(x + dx, W, z + dz, STAIR.format('deepslate_tile_stairs', DIR[(-dx, -dz)], 'bottom'))
    if height < 4:
        for y in range(W + 1, W + height):
            t.set(x, y, z, 'cracked_deepslate_tiles' if y == W + height - 1 else 'deepslate_tiles')
        return
    for y in range(W + 1, W + height - 1):
        t.set(x, y, z, 'chiseled_deepslate' if y == W + 2 else 'deepslate_tiles')
    cap = W + height - 1
    t.set(x, cap, z, 'polished_deepslate')
    for (dx, dz) in DIR:
        t.set(x + dx, cap, z + dz, STAIR.format('deepslate_tile_stairs', DIR[(-dx, -dz)], 'top'))
    t.set(x, cap + 1, z, top)


def great_lantern(t):
    """The Old Delvers' mark made large: a blackstone lantern on the dais, its heart a pearlescent froglight
    behind iron bars between two crystals."""
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            x, z = CX + dx, CZ + dz
            t.set(x, W + 1, z, 'gilded_blackstone' if (dx, dz) == (0, 0) else 'polished_blackstone_bricks')
            t.set(x, W + 5, z, 'polished_blackstone' if (dx, dz) == (0, 0) else
                  'polished_blackstone_brick_slab[type=bottom,waterlogged=false]')
            for y in range(W + 2, W + 5):
                if dx and dz: t.set(x, y, z, 'polished_blackstone_wall[up=true]')
                elif dx: t.set(x, y, z, 'iron_bars[north=true,south=true,east=false,west=false,waterlogged=false]')
                elif dz: t.set(x, y, z, 'iron_bars[east=true,west=true,north=false,south=false,waterlogged=false]')
    t.set(CX, W + 2, CZ, 'amethyst_cluster[facing=up,waterlogged=false]')
    t.set(CX, W + 3, CZ, 'pearlescent_froglight[axis=y]')
    t.set(CX, W + 4, CZ, 'amethyst_cluster[facing=down,waterlogged=false]')
    t.set(CX, W + 6, CZ, 'polished_blackstone_wall[up=true]')
    t.set(CX, W + 7, CZ, 'iron_chain[axis=y,waterlogged=false]')


def shrine(t, cav, paths):
    """The platform, the pillar ring, the dais with the Great Lantern, the chest, the pots, the carvings."""
    rng = t.rng
    for (x, z), f in sorted(cav.floor.items()):
        d = math.hypot(x - CX, z - CZ)
        if d > 8.6 or f != FB or t.get(x, FB, z) == 'water': continue
        if 4.6 < d <= 5.4: b = 'polished_deepslate'
        elif d > 7.9 and rng.random() < 0.3: b = 'calcite'          # the crystal creeping over the edge
        else: b = worn_tile(rng)
        t.set(x, FB, z, b)
        t.set(x, FB - 1, z, 'cobbled_deepslate')
    # the dais: seven across with its corners cut, stepped all round
    for dx in range(-DAIS_R, DAIS_R + 1):
        for dz in range(-DAIS_R, DAIS_R + 1):
            m = max(abs(dx), abs(dz))
            if abs(dx) == DAIS_R and abs(dz) == DAIS_R: continue
            x, z = CX + dx, CZ + dz
            if m == DAIS_R:
                inward = (-1 if dx > 0 else 1, 0) if abs(dx) == DAIS_R else (0, -1 if dz > 0 else 1)
                t.set(x, W, z, STAIR.format('deepslate_tile_stairs', DIR[inward], 'bottom'))
            else:
                t.set(x, W, z, 'polished_deepslate' if m == 2 else 'chiseled_deepslate')
    great_lantern(t)
    t.chest(CX, W + 1, CZ - 2, 'north', 'grotto/shrine')
    t.pot(CX - 2, W + 1, CZ - 2, 'north', loot='grotto/pot', sherds=['miner_pottery_sherd', 'prize_pottery_sherd', 'heart_pottery_sherd', 'miner_pottery_sherd'])
    t.pot(CX + 2, W + 1, CZ - 2, 'north', loot='grotto/pot', sherds=['prize_pottery_sherd', 'shelter_pottery_sherd', 'miner_pottery_sherd', 'plenty_pottery_sherd'])
    t.pot(CX - 2, W + 1, CZ + 2, 'south', loot='grotto/pot', sherds=['explorer_pottery_sherd', 'miner_pottery_sherd', 'prize_pottery_sherd', 'heart_pottery_sherd'])
    t.pot(CX + 2, W + 1, CZ + 2, 'south', sherds=['mourner_pottery_sherd', 'brick', 'brick', 'miner_pottery_sherd'])
    for (x, z, n) in ((CX - 2, CZ, 3), (CX + 2, CZ, 3), (CX, CZ + 2, 4), (CX - 1, CZ - 2, 2), (CX + 1, CZ - 2, 2)):
        t.set(x, W + 1, z, f'purple_candle[candles={n},lit=true,waterlogged=false]')
    # the ring of pillars: candles and crystal on their crowns, two broken, four carved
    heights = [7, 6, 2, 7, 6, 7, 3, 6]
    tops = ['purple_candle[candles=4,lit=true,waterlogged=false]', 'amethyst_cluster[facing=up,waterlogged=false]',
            None, 'white_candle[candles=3,lit=false,waterlogged=false]', 'amethyst_cluster[facing=up,waterlogged=false]',
            'purple_candle[candles=4,lit=false,waterlogged=false]', None, 'amethyst_cluster[facing=up,waterlogged=false]']
    carvings = iter(CARVINGS)
    for k in range(PILLARS):
        a = math.radians(22.5 + 45 * k)
        x, z = round(CX + PILLAR_R * math.cos(a)), round(CZ + PILLAR_R * math.sin(a))
        pillar(t, x, z, heights[k], tops[k], rng)
        ox, oz = (1 if x > CX else -1, 0) if abs(x - CX) >= abs(z - CZ) else (0, 1 if z > CZ else -1)
        words = next(carvings, None) if heights[k] >= 4 else None
        if words:
            t.sign(x + ox, W + 2, z + oz, words, facing=DIR[(ox, oz)], wood='pale_oak')
        if heights[k] < 4:      # the fallen top lies outward on the floor
            for i, b in enumerate(('chiseled_deepslate', 'deepslate_tiles', 'cracked_deepslate_tiles')):
                fx, fz = x + ox * (i + 2) + (oz if i == 2 else 0), z + oz * (i + 2) + (ox if i == 2 else 0)
                if t.get(fx, W, fz) == 'air' and (fx, fz) not in paths: t.set(fx, W, fz, b)
            t.set(x - oz, W, z + ox, 'deepslate_tile_slab[type=bottom,waterlogged=false]') \
                if t.get(x - oz, W, z + ox) == 'air' else None
        elif t.get(x - oz + ox, W, z + ox + oz) == 'air':
            t.set(x - oz + ox, W, z + ox + oz, 'white_candle[candles=2,lit=false,waterlogged=false]')
    t.anchor(CX, FB, CZ - 5, floor='polished_deepslate')


FACING = {(1, 0, 0): 'east', (-1, 0, 0): 'west', (0, 1, 0): 'up', (0, -1, 0): 'down', (0, 0, 1): 'south',
          (0, 0, -1): 'north'}
LICHEN_OFF = 'down=false,east=false,north=false,south=false,up=false,west=false,waterlogged=false'


def lichen(face):
    """Glow lichen covering one face of its cell ('up' = on the roof above it, 'east' = on the wall east...)."""
    return 'glow_lichen[' + LICHEN_OFF.replace(f'{face}=false', f'{face}=true') + ']'


def crystals(t, keep_clear, rng, budding=0.75, plain=0.05):
    """Clusters and buds growing out of budding amethyst (and now and then plain amethyst) into the open."""
    for (x, y, z), (name, _) in sorted(t.blocks.items()):
        if name == 'minecraft:budding_amethyst': p = budding
        elif name == 'minecraft:amethyst_block': p = plain
        else: continue
        if rng.random() > p: continue
        opts = [d for d in FACING if t.get(x + d[0], y + d[1], z + d[2]) == 'air'
                and (x + d[0], y + d[1], z + d[2]) not in keep_clear]
        if not opts: continue
        d = rng.choice(opts)
        r = rng.random()
        kind = ('amethyst_cluster' if r < 0.45 else 'large_amethyst_bud' if r < 0.7 else
                'medium_amethyst_bud' if r < 0.88 else 'small_amethyst_bud')
        t.set(x + d[0], y + d[1], z + d[2], f'{kind}[facing={FACING[d]},waterlogged=false]')


def roof_and_walls(t, cav, water, keep_clear, rng, lichen_p=0.045):
    """Stalactites under dripstone (long ones over the pool), stalagmites under some, glow lichen about."""
    pool_cols = {(x, z) for (x, y, z) in water}
    for (x, c, z) in sorted(cav.ceiling_cells()):
        if t.get(x, c, z) != 'air': continue
        above, room = t.name_at(x, c + 1, z), c - cav.floor[(x, z)]
        over_pool = (x, z) in pool_cols
        if (above == 'minecraft:dripstone_block' and room > 4 and rng.random() < 0.55) or \
                (over_pool and above is not None and room > 4 and rng.random() < 0.18):
            hang(t, x, c, z, rng.randint(1, min(6 if over_pool else 4, room - 3)), 'drip')
            f = cav.floor[(x, z)]
            if not over_pool and (x, f + 1, z) not in keep_clear and t.name_at(x, f, z) in SOFT \
                    and rng.random() < 0.4:
                stalagmite(t, x, f + 1, z, rng.randint(1, 3))
        elif above is not None and rng.random() < lichen_p:
            t.set(x, c, z, lichen('up'))
    for (x, y, z) in sorted(cav.cells()):
        if t.get(x, y, z) != 'air' or (x, y, z) in keep_clear: continue
        for (dx, dy, dz), face in FACING.items():
            if dy: continue
            n = t.name_at(x + dx, y, z + dz)
            if n in SOFT and n != 'minecraft:budding_amethyst' and rng.random() < lichen_p / 3:
                t.set(x, y, z, lichen(face))
                break
        else:
            f = cav.floor[(x, z)]
            if y == f + 1 and f > FB and t.name_at(x, f, z) in SOFT and rng.random() < lichen_p:
                t.set(x, y, z, lichen('down'))


def standing_carving(t, cav, cells, lines, facing, keep_clear):
    """A pale standing sign on the first free floor cell among `cells`."""
    for (x, z) in cells:
        if (x, z) not in cav.floor: continue
        f = cav.floor[(x, z)]
        if t.get(x, f + 1, z) == 'air' and t.get(x, f + 2, z) == 'air' and (x, f + 1, z) not in keep_clear \
                and t.name_at(x, f, z) not in (None, 'minecraft:water'):
            t.sign(x, f + 1, z, lines, facing=facing, wood='pale_oak', wall=False)
            return True
    return False


def glimmering():
    t = Template('grotto/glimmering', (SX, SY, SZ), seed='grotto/glimmering')
    rng = t.rng
    cav, water, paths, vein, mix = shape(t)
    shrine(t, cav, paths)
    # keep the paths and the platform walkable: nothing grows into their walking cells
    keep_clear = {(x, cav.floor[(x, z)] + i, z) for (x, z) in paths for i in (1, 2)}
    keep_clear |= {(x, FB + i, z) for (x, z) in cav.floor if math.hypot(x - CX, z - CZ) <= 8.6 for i in (1, 2, 3)}
    cav.lining(geode(vein, mix, rng), depth=3)
    crystals(t, keep_clear, rng)
    roof_and_walls(t, cav, water, keep_clear, rng)
    # carvings by the pool and inside the north mouth
    px, pz = POOL[0], POOL[1]
    rim = sorted(((x, z) for (x, z), f in cav.floor.items() if f == FB and (x, FB, z) not in water
                  and math.hypot(x - CX, z - CZ) > 8.8 and any((x + a, FB, z + b) in water for a, b in DIR)),
                 key=lambda c: math.hypot(c[0] - (px + 3.5), c[1] - (pz - 3.5)))
    standing_carving(t, cav, rim, POOL_CARVING, 'east', keep_clear)
    north = path4(ROUTES[1])
    beside = [s for i in range(CORRIDOR, CORRIDOR + 5) for s in side_of(north, i) if s not in paths]
    standing_carving(t, cav, beside, MOUTH_CARVING, 'north', keep_clear)
    for (fx, fz), orient, fy in MOUTHS:
        t.jigsaw(fx, fy + 1, fz, orient, 'grotto/mouth', target='grotto/tunnel_in', pool='grotto/tunnels')
    seal_water(t, water, lambda x, y, z: 'polished_tuff' if (x + z) % 4 == 0 else 'polished_diorite')
    underpin(t)
    t.notes['shrine'] = (CX, W + 1, CZ)
    return t


# -- the ways in: natural passages, crystal near the cavern end -----------------------------------------

def tunnel_lining(rock, rng, crystal_end):
    """Deepslate and tuff with basalt seams and dripstone; calcite and amethyst toward the cavern (x small)."""
    def pick(x, y, z, d, kind):
        v = rock[x, y, z]
        near = x < crystal_end
        if d >= 2: return ('calcite' if d == 2 else 'smooth_basalt') if near else 'deepslate'
        if near and v > 0.32: return 'budding_amethyst' if rng.random() < 0.3 else 'amethyst_block'
        if near and v > 0.0: return 'calcite'
        if kind == 'ceiling' and v < -0.35: return 'dripstone_block'
        if abs(v) < 0.05: return 'smooth_basalt'
        if v < -0.45: return 'tuff'
        return 'deepslate'
    return pick


def tunnel_piece(name, size, points, rise_at, exit_orient, crystal_end=6, rubble=None):
    """A natural passage three wide and four or five high along `points` (entry at x = 0, floor y 1), its old
    tiled path half gone. With rise_at, the floor steps up one there (tile stairs)."""
    t = Template(name, size, seed=name)
    rng = t.rng
    cav = Cavern(t)
    route = path4(points)
    tiles = set()
    for i, c in enumerate(route):
        f = 1 + (1 if rise_at is not None and i >= rise_at else 0)
        for j, (x, z) in enumerate([c] + list(side_of(route, i))):
            if not (0 <= x < size[0] and 0 <= z < size[2]): continue
            h = (4 if j == 0 else 3) + (1 if rng.random() < 0.4 else 0)
            cav.add_column(x, z, f, f + h)
            cav.floor[(x, z)] = f
            if j < 2: tiles.add((x, z))
    cav.carve()
    rock = noise(size, sum(map(ord, name)) * 7, 4)
    faces = {c for i in (0, len(route) - 1) for c in [route[i]] + list(side_of(route, i))}
    for (x, z), f in sorted(cav.floor.items()):
        if (x, z) in faces or (x, z) in tiles and rng.random() < 0.55:
            t.set(x, f, z, worn_tile(rng))
            t.set(x, f - 1, z, 'cobbled_deepslate')
        else:
            top = ('calcite' if x < crystal_end and rng.random() < 0.6 else
                   'tuff' if rng.random() < 0.6 else 'smooth_basalt')
            t.set(x, f, z, top)
            t.set(x, f - 1, z, sub_floor('minecraft:' + top))
    stairs_on_steps(t, cav, set(cav.floor), 'deepslate_tile_stairs')
    if rubble:
        for (x, y, z), b in rubble.items(): t.set(x, y, z, b)
    keep_clear = {(x, cav.floor[(x, z)] + i, z) for (x, z) in route if (x, z) in cav.floor for i in (1, 2)}
    cav.lining(tunnel_lining(rock, rng, crystal_end), depth=2)
    crystals(t, keep_clear, rng, budding=0.6, plain=0.03)
    roof_and_walls(t, cav, set(), keep_clear, rng, lichen_p=0.05)
    (x0, z0), (x1, z1) = route[0], route[-1]
    t.jigsaw(x0, cav.floor[(x0, z0)] + 1, z0, 'west_up', 'grotto/tunnel_in')
    if exit_orient:
        t.jigsaw(x1, cav.floor[(x1, z1)] + 1, z1, exit_orient, 'grotto/tunnel_out', target='grotto/tunnel_in',
                 pool='grotto/tunnels')
    underpin(t)
    return t


def passage():
    return tunnel_piece('grotto/passage', (16, 9, 9), [(0, 4), (4, 4), (6, 3), (9, 3), (11, 5), (15, 5)], 10,
                        'east_up')


def turn():
    return tunnel_piece('grotto/turn', (12, 9, 12), [(0, 5), (4, 5), (6, 6), (7, 8), (7, 11)], None, 'south_up')


def cap():
    """The way in ends in an old collapse; somebody left a candle on it."""
    rubble = {(7, 2, 3): 'cobbled_deepslate_slab[type=bottom,waterlogged=false]',
              (7, 2, 2): 'cobbled_deepslate', (7, 2, 4): 'tuff', (8, 2, 2): 'cobbled_deepslate',
              (8, 2, 3): 'cobbled_deepslate', (8, 2, 4): 'cobbled_deepslate', (8, 3, 3): 'cobbled_deepslate',
              (8, 3, 2): 'cobbled_deepslate_slab[type=bottom,waterlogged=false]', (8, 3, 4): 'gravel',
              (8, 4, 3): 'tuff', (7, 3, 2): 'candle[candles=1,lit=false,waterlogged=false]'}
    return tunnel_piece('grotto/cap', (10, 9, 8), [(0, 4), (4, 4), (6, 3), (8, 3)], None, None, rubble=rubble)


def pieces():
    return [glimmering(), passage(), turn(), cap()]
