"""Write everything the Cave Expansion structures need in the data pack: the block templates of every design
in designs/, their jigsaw pools, the processor lists, one structure per delve, the structure set (its own
placement keeps clear of villages, homesteads, the Plata Clan's hideouts and vanilla's big underground
structures), biome and structure tags, loot tables, the miner's trades and a catalog the game tests read.

  python tools/delves/build.py            build (templates are validated against vanilla's blockstates)
  python tools/delves/build.py --render   also render every piece to tools/delves/out/
  python tools/delves/build.py --check    only validate (writes nothing)
  python tools/delves/build.py --check --only=camp,seam   validate just those designs
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from kit import ANCHOR, LOOT, NATURAL, NS, RES, ROLES, write_json  # noqa: E402
import designs  # noqa: E402

DATA = os.path.join(RES, 'data', NS)
ITEMS = set(open(os.path.join(HERE, '.cache', 'items.txt'), encoding='utf-8').read().split())

# Every overworld biome but the Deep Dark (the ancient cities' country). Underground the biome is the cave
# biome where the delve stands (lush caves, dripstone caves...) or the land above, extended down.
BIOMES = ['bamboo_jungle', 'badlands', 'beach', 'birch_forest', 'cherry_grove', 'cold_ocean', 'dappled_forest',
          'dark_forest', 'deep_cold_ocean', 'deep_frozen_ocean', 'deep_lukewarm_ocean', 'deep_ocean', 'desert',
          'dripstone_caves', 'eroded_badlands', 'flower_forest', 'forest', 'frozen_ocean', 'frozen_peaks', 'frozen_river',
          'grove', 'ice_spikes', 'jagged_peaks', 'jungle', 'lukewarm_ocean', 'lush_caves', 'mangrove_swamp', 'meadow',
          'mushroom_fields', 'ocean', 'old_growth_birch_forest', 'old_growth_pine_taiga', 'old_growth_spruce_taiga',
          'pale_garden', 'plains', 'river', 'savanna', 'savanna_plateau', 'snowy_beach', 'snowy_plains', 'snowy_slopes',
          'snowy_taiga', 'sparse_jungle', 'stony_peaks', 'stony_shore', 'sulfur_caves', 'sunflower_plains', 'swamp',
          'taiga', 'warm_ocean', 'windswept_forest', 'windswept_gravelly_hills', 'windswept_hills', 'windswept_savanna',
          'wooded_badlands']

# The one structure set every delve belongs to: about one delve in each 30 x 30 chunk cell (480 blocks
# square), rarer or commoner with "rarity" in config/caveexpansion.json. Each set listed in AVOID is kept
# that many chunks away; a set from a mod that isn't installed is skipped.
SPACING, SEPARATION, SALT = 30, 12, 1046207133
AVOID = [('minecraft:villages', 4), ('villagefriends:homesteads', 2), ('plataclan:dens', 3), ('plataclan:warrens', 5),
         ('minecraft:trial_chambers', 4), ('minecraft:ancient_cities', 4), ('minecraft:strongholds', 3),
         ('minecraft:ocean_monuments', 2)]

ALL_SPAWNS = ('monster', 'creature', 'ambient', 'axolotls', 'underground_water_creature', 'water_creature',
              'water_ambient', 'misc')
NO_MONSTERS = {'monster': {'bounding_box': 'piece', 'spawns': []}}


# -- templates, pools, structures -----------------------------------------------------------------

def element(location, processors):
    if location == 'empty':
        return {'element_type': 'minecraft:empty_pool_element'}
    return {'element_type': 'minecraft:single_pool_element', 'location': f'{NS}:{location}',
            'processors': f'{NS}:{processors}', 'projection': 'rigid'}


def check_design(mod, catalog):
    """Pools, jigsaw names and anchors must line up, or the game quietly builds half a delve."""
    key = mod.KEY
    names = {t: info for t, info in catalog.items() if t.startswith(key + '/')}
    s = mod.STRUCTURE
    assert s['start_pool'] in mod.POOLS, f'{key}: start pool {s["start_pool"]} missing'
    for pool, spec in mod.POOLS.items():
        assert pool.startswith(key + '/'), f'{key}: pool {pool} must start with "{key}/"'
        for loc, weight in spec['elements']:
            assert loc == 'empty' or loc in names, f'{key}: pool {pool} lists unknown template {loc}'
            assert isinstance(weight, int) and weight > 0
        fb = spec.get('fallback')
        assert fb is None or fb in mod.POOLS, f'{key}: fallback {fb} missing'
    for loc, _ in mod.POOLS[s['start_pool']]['elements']:
        anchors = [j for j in names[loc]['jigsaws'] if j['name'] == ANCHOR]
        assert len(anchors) == 1, f'{key}: start piece {loc} needs exactly one anchor (has {len(anchors)})'
    provided = {}
    for t, info in names.items():
        for j in info['jigsaws']: provided.setdefault(j['name'], set()).add(t)
    for t, info in names.items():
        for j in info['jigsaws']:
            if j['name'] == ANCHOR or j['pool'] == 'minecraft:empty': continue
            pool = j['pool'].split(':', 1)[1]
            assert pool in mod.POOLS, f'{key}: {t} jigsaw {j["name"]} points at unknown pool {pool}'
            members = {loc for loc, _ in mod.POOLS[pool]['elements'] if loc != 'empty'}
            fb = mod.POOLS[pool].get('fallback')
            if fb: members |= {loc for loc, _ in mod.POOLS[fb]['elements'] if loc != 'empty'}
            assert any(j['target'] in {k['name'] for k in names[m]['jigsaws']} for m in members), \
                f'{key}: {t} jigsaw targets {j["target"]} but nothing in pool {pool} has a jigsaw by that name'
    for t, info in names.items():
        for table in info['notes'].get('loot', []):
            assert table.split('chests/', 1)[1] in LOOT
    assert s['min_y'] < s['max_y'] and s['min_y'] >= -56 and s['max_y'] <= 60, f'{key}: depth {s["min_y"]}..{s["max_y"]}'
    if s.get('require'):
        assert s['require'] in names, f'{key}: required piece {s["require"]} missing'


def structures(mods):
    write_json(f'data/{NS}/tags/worldgen/biome/has_delve.json', {'values': ['minecraft:' + b for b in BIOMES]})
    natural = {'processor_type': f'{NS}:natural', 'blocks': NATURAL}
    for mod in mods:
        s = mod.STRUCTURE
        write_json(f'data/{NS}/worldgen/processor_list/{mod.KEY}.json',
                   {'processors': [natural] + list(s.get('processors', []))})
        for pool, spec in mod.POOLS.items():
            write_json(f'data/{NS}/worldgen/template_pool/{pool}.json', {
                'fallback': f'{NS}:{spec["fallback"]}' if spec.get('fallback') else 'minecraft:empty',
                'elements': [{'weight': w, 'element': element(loc, mod.KEY)} for loc, w in spec['elements']]})
        structure = {
            'type': f'{NS}:delve', 'biomes': f'#{NS}:has_delve', 'step': 'underground_structures',
            'terrain_adaptation': 'none', 'spawn_overrides': NO_MONSTERS if s.get('inhabited') else {},
            'start_pool': f'{NS}:{s["start_pool"]}', 'size': s['size'],
            'max_distance_from_center': {'horizontal': s['horizontal'], 'vertical': s['vertical']},
            'depth': {'min_y': s['min_y'], 'max_y': s['max_y']}, 'cover': s.get('cover', 10),
            'seek_caves': s.get('seek_caves', True), 'clearance': s.get('clearance', 10)}
        if s.get('require'): structure['require'] = f'{NS}:{s["require"]}'
        if s.get('chance', 1) < 1: structure['chance'] = s['chance']
        write_json(f'data/{NS}/worldgen/structure/{mod.KEY}.json', structure)
    write_json(f'data/{NS}/worldgen/structure_set/delves.json', {
        'structures': [{'structure': f'{NS}:{m.KEY}', 'weight': m.STRUCTURE.get('weight', 1)} for m in mods],
        'placement': {'type': f'{NS}:spread', 'spacing': SPACING, 'separation': SEPARATION, 'salt': SALT,
                      'avoid': [{'set': s, 'chunks': c} for s, c in AVOID]}})
    write_json(f'data/{NS}/tags/worldgen/structure/delves.json', {'values': [f'{NS}:{m.KEY}' for m in mods]})
    write_json(f'data/{NS}/tags/worldgen/structure/inhabited.json',
               {'values': [f'{NS}:{m.KEY}' for m in mods if m.STRUCTURE.get('inhabited')]})
    # What a camp foreman's survey map can point you to: any delve but another camp.
    write_json(f'data/{NS}/tags/worldgen/structure/on_survey_maps.json',
               {'values': [f'{NS}:{m.KEY}' for m in mods if m.KEY != 'camp']})


# -- loot ------------------------------------------------------------------------------------------

def item(name, weight=1, lo=1, hi=1, extra=None):
    full = name if ':' in name else 'minecraft:' + name
    if full.startswith('minecraft:'): assert full.split(':')[1] in ITEMS, f'unknown item {full}'
    e = {'type': 'minecraft:item', 'name': full, 'weight': weight}
    mods = []
    if (lo, hi) != (1, 1):
        mods.append({'type': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}})
    mods += extra or []
    if mods: e['modifier'] = mods if len(mods) > 1 else mods[0]
    return e


def empty(weight):
    return {'type': 'minecraft:empty', 'weight': weight}


def rolls(lo, hi):
    return lo if lo == hi else {'type': 'minecraft:uniform', 'min': lo, 'max': hi}


def enchanted(lo, hi):
    return [{'type': 'minecraft:enchant_with_levels', 'levels': {'type': 'minecraft:uniform', 'min': lo, 'max': hi},
             'options': '#minecraft:on_random_loot'}]


RANDOM_ENCHANT = [{'type': 'minecraft:enchant_randomly', 'options': '#minecraft:on_random_loot'}]
WORN = [{'type': 'minecraft:set_damage', 'damage': {'type': 'minecraft:uniform', 'min': 0.25, 'max': 0.7}}]


def survey_map(weight):
    """A map to the nearest delve that isn't a camp."""
    return item('map', weight, extra=[
        {'type': 'minecraft:exploration_map', 'destination': f'#{NS}:on_survey_maps', 'decoration': 'minecraft:target_x',
         'zoom': 2, 'search_radius': 60, 'skip_existing_chunks': True},
        {'type': 'minecraft:set_name', 'target': 'item_name', 'name': {'translate': f'item.{NS}.survey_map'}},
        {'type': 'minecraft:filtered', 'item_filter': {'predicates': {'minecraft:map_id': {}}},
         'on_fail': {'type': 'minecraft:discard'}}])


TRIMS = ['coast', 'dune', 'eye', 'host', 'raiser', 'rib', 'sentry', 'shaper', 'silence', 'snout', 'spire', 'tide', 'vex',
         'ward', 'wayfinder', 'wild', 'flow', 'bolt']


def loot():
    chests = {
        # Delvers' Camp: working stores, nothing grand.
        'camp/supplies': [
            {'rolls': rolls(4, 7), 'entries': [
                item('bread', 10, 1, 4), item('baked_potato', 8, 2, 5), item('cooked_mutton', 5, 1, 3),
                item('torch', 10, 4, 12), item('coal', 10, 3, 10), item('rail', 5, 4, 10), item('ladder', 4, 3, 8),
                item('stick', 4, 2, 6), item('iron_nugget', 6, 3, 9), item('lantern', 2, 1, 2), item('copper_torch', 3, 2, 6),
                item('milk_bucket', 1)]}],
        'camp/foreman': [
            {'rolls': rolls(3, 5), 'entries': [
                item('emerald', 10, 2, 6), item('iron_ingot', 8, 2, 5), item('gold_ingot', 4, 1, 3), item('raw_iron', 6, 2, 6),
                item('redstone', 4, 3, 9), item('lapis_lazuli', 4, 3, 9), item('compass', 2), item('clock', 1)]},
            {'rolls': 1, 'entries': [empty(4), survey_map(5), item('iron_pickaxe', 2, extra=RANDOM_ENCHANT)]}],
        'camp/ore_cart': [
            {'rolls': rolls(4, 8), 'entries': [
                item('raw_iron', 10, 2, 7), item('raw_copper', 10, 3, 10), item('coal', 10, 4, 12), item('raw_gold', 4, 1, 4),
                item('redstone', 5, 2, 8), item('lapis_lazuli', 4, 2, 7), item('flint', 3, 1, 4), item('diamond', 1)]}],
        # The Buried Seam: what the lost shift left behind.
        'seam/cart': [
            {'rolls': rolls(3, 7), 'entries': [
                item('raw_iron', 10, 2, 8), item('raw_gold', 6, 2, 5), item('coal', 8, 4, 12), item('raw_copper', 8, 4, 10),
                item('redstone', 5, 3, 9), item('lapis_lazuli', 5, 3, 9), item('emerald', 2, 1, 3), item('diamond', 2, 1, 2)]}],
        'seam/shack': [
            {'rolls': rolls(3, 6), 'entries': [
                item('emerald', 8, 2, 5), item('gold_nugget', 8, 4, 12), item('iron_ingot', 8, 2, 6), item('candle', 4, 1, 3),
                item('bone', 6, 1, 4), item('paper', 4, 1, 4), item('bread', 4, 1, 2), item('name_tag', 1)]},
            {'rolls': 1, 'entries': [empty(2), item('iron_pickaxe', 3, extra=RANDOM_ENCHANT + WORN),
                                     item('golden_pickaxe', 1, extra=enchanted(10, 25)), survey_map(2)]}],
        'seam/rich': [
            {'rolls': rolls(4, 7), 'entries': [
                item('raw_gold', 10, 3, 8), item('raw_iron', 8, 4, 10), item('diamond', 4, 1, 3), item('emerald', 4, 2, 5),
                item('lapis_lazuli', 6, 4, 12), item('redstone', 6, 4, 12), item('gold_ingot', 5, 2, 5)]},
            {'rolls': 1, 'entries': [empty(3), item('raw_gold_block', 2), item('diamond_pickaxe', 1, extra=WORN)]}],
        # Deepwatch Post: a garrison's kit and the one thing it guards.
        'post/armory': [
            {'rolls': rolls(3, 6), 'entries': [
                item('arrow', 10, 6, 16), item('iron_ingot', 6, 1, 4), item('shield', 3), item('iron_helmet', 2),
                item('iron_chestplate', 1), item('chainmail_leggings', 2), item('chainmail_boots', 2), item('crossbow', 2),
                item('iron_sword', 2), item('string', 4, 2, 5), item('flint', 4, 2, 5), item('feather', 4, 2, 6)]},
            {'rolls': 1, 'entries': [empty(5), item('bow', 2, extra=enchanted(5, 20)), item('iron_sword', 2, extra=enchanted(5, 20))]}],
        'post/barracks': [
            {'rolls': rolls(3, 6), 'entries': [
                item('bread', 10, 2, 5), item('cooked_beef', 6, 1, 4), item('apple', 6, 1, 3), item('torch', 6, 3, 8),
                item('leather', 4, 1, 3), item('paper', 3, 1, 3), item('emerald', 4, 1, 3), item('candle', 2, 1, 2)]},
            {'rolls': 1, 'entries': [empty(6), item('potion', 2, extra=[{'type': 'minecraft:set_potion', 'id': 'minecraft:healing'}]),
                                     item('splash_potion', 1, extra=[{'type': 'minecraft:set_potion', 'id': 'minecraft:healing'}])]}],
        'post/captain': [
            {'rolls': rolls(3, 5), 'entries': [
                item('emerald', 10, 3, 8), item('gold_ingot', 6, 1, 4), item('iron_ingot', 6, 2, 5), item('book', 4),
                item('compass', 3), item('spyglass', 2), item('golden_carrot', 4, 2, 5), item('experience_bottle', 4, 1, 4)]},
            {'rolls': 1, 'entries': [empty(3), item('golden_apple', 3), survey_map(4), item('book', 2, extra=enchanted(15, 30))]}],
        'post/deepgate': [
            {'rolls': rolls(4, 7), 'entries': [
                item('emerald', 8, 4, 10), item('gold_ingot', 8, 3, 7), item('diamond', 5, 1, 3), item('golden_apple', 3),
                item('experience_bottle', 6, 3, 8), item('iron_block', 2), item('book', 4, extra=enchanted(20, 39))]},
            {'rolls': 1, 'entries': [empty(2), item('diamond_sword', 1, extra=enchanted(15, 30)),
                                     item('diamond_chestplate', 1, extra=enchanted(15, 30)),
                                     item('enchanted_golden_apple', 1)]}],
        # Hermit's Hollow: mushrooms, brews and an old delver's keepsakes.
        'hermit/pantry': [
            {'rolls': rolls(3, 6), 'entries': [
                item('mushroom_stew', 8), item('brown_mushroom', 8, 2, 6), item('red_mushroom', 8, 2, 6),
                item('glow_berries', 8, 2, 8), item('bread', 4, 1, 3), item('baked_potato', 4, 1, 4), item('honey_bottle', 2),
                item('suspicious_stew', 2, extra=[{'type': 'minecraft:set_stew_effect', 'effects': [
                    {'type': 'minecraft:night_vision', 'duration': 200}]}])]}],
        'hermit/shelf': [
            {'rolls': rolls(2, 4), 'entries': [
                item('amethyst_shard', 8, 2, 6), item('glow_ink_sac', 5, 1, 3), item('book', 4), item('emerald', 5, 1, 4),
                item('fermented_spider_eye', 3, 1, 2), item('glistering_melon_slice', 2, 1, 2), item('ender_pearl', 2),
                item('potion', 3, extra=[{'type': 'minecraft:set_potion', 'id': 'minecraft:long_night_vision'}])]},
            {'rolls': 1, 'entries': [empty(4), item('iron_pickaxe', 2, extra=enchanted(10, 25) + WORN), item('lodestone', 1)]}],
        # The Glimmering: the grotto's shrine.
        'grotto/shrine': [
            {'rolls': rolls(4, 7), 'entries': [
                item('amethyst_shard', 10, 4, 12), item('diamond', 5, 1, 3), item('emerald', 6, 2, 6),
                item('gold_ingot', 5, 2, 5), item('glow_ink_sac', 4, 1, 4), item('spyglass', 2), item('experience_bottle', 4, 2, 6)]},
            {'rolls': 1, 'entries': [empty(2), item('music_disc_5', 1), item('book', 3, extra=enchanted(20, 39)),
                                     item('amethyst_block', 2, 2, 4), item('echo_shard', 1)]}],
        'grotto/pot': [
            {'rolls': rolls(1, 3), 'entries': [
                item('amethyst_shard', 10, 1, 4), item('emerald', 4, 1, 2), item('glow_berries', 6, 1, 4),
                item('gold_nugget', 6, 2, 8), item('diamond', 1)]}],
        # The Drowned Cistern.
        'cistern/vault': [
            {'rolls': rolls(4, 7), 'entries': [
                item('gold_ingot', 10, 2, 6), item('emerald', 8, 2, 6), item('nautilus_shell', 4, 1, 2), item('prismarine_shard', 4, 2, 6),
                item('diamond', 4, 1, 2), item('golden_apple', 2), item('experience_bottle', 4, 2, 5), item('gold_block', 1)]},
            {'rolls': 1, 'entries': [empty(4), item('trident', 1, extra=WORN), item('heart_of_the_sea', 1),
                                     item('book', 3, extra=[{'type': 'minecraft:enchant_randomly', 'options': [
                                         'minecraft:depth_strider', 'minecraft:aqua_affinity', 'minecraft:respiration',
                                         'minecraft:frost_walker', 'minecraft:impaling', 'minecraft:loyalty']}])]}],
        'cistern/ledge': [
            {'rolls': rolls(2, 5), 'entries': [
                item('gold_nugget', 8, 3, 9), item('iron_nugget', 8, 3, 9), item('bucket', 3), item('kelp', 4, 2, 6),
                item('ink_sac', 4, 1, 3), item('emerald', 3, 1, 2), item('fishing_rod', 2, extra=WORN)]}],
        # The Ossuary.
        'ossuary/sarcophagus': [
            {'rolls': rolls(2, 5), 'entries': [
                item('bone', 10, 2, 6), item('gold_nugget', 8, 3, 10), item('gold_ingot', 5, 1, 3), item('emerald', 4, 1, 3),
                item('candle', 4, 1, 3), item('rotten_flesh', 4, 1, 3), item('golden_helmet', 2, extra=enchanted(5, 20))]},
            {'rolls': 1, 'entries': [empty(5), item('book', 3, extra=enchanted(15, 35)), item('golden_apple', 2),
                                     item('skeleton_skull', 1)]}],
        'ossuary/reliquary': [
            {'rolls': rolls(4, 7), 'entries': [
                item('gold_ingot', 10, 3, 8), item('emerald', 8, 3, 8), item('diamond', 5, 1, 3), item('golden_apple', 4),
                item('experience_bottle', 6, 3, 8), item('book', 5, extra=enchanted(25, 39)), item('totem_of_undying', 1)]},
            {'rolls': 1, 'entries': [empty(3)] + [item(f'{t}_armor_trim_smithing_template', 1) for t in ('rib', 'silence', 'ward', 'eye')]},
            {'rolls': 1, 'entries': [empty(6), item('enchanted_golden_apple', 1)]}],
        # The Sunken Forge.
        'forge/supplies': [
            {'rolls': rolls(4, 7), 'entries': [
                item('iron_ingot', 10, 3, 8), item('gold_ingot', 6, 2, 5), item('coal_block', 4, 1, 3), item('coal', 8, 4, 12),
                item('iron_nugget', 8, 6, 18), item('copper_ingot', 6, 3, 9), item('flint', 3, 2, 5), item('iron_chain', 3, 1, 4),
                item('lava_bucket', 1)]}],
        'forge/vault': [
            {'rolls': rolls(5, 8), 'entries': [
                item('diamond', 8, 2, 5), item('gold_block', 3), item('iron_block', 4, 1, 2), item('gold_ingot', 6, 3, 8),
                item('emerald', 6, 3, 8), item('netherite_scrap', 2, 1, 2), item('experience_bottle', 5, 4, 10)]},
            {'rolls': 1, 'entries': [empty(4), item('netherite_upgrade_smithing_template', 2)]},
            {'rolls': 1, 'entries': [empty(2)] + [item(f'{t}_armor_trim_smithing_template', 1) for t in ('snout', 'rib', 'spire', 'wayfinder', 'shaper')]},
            {'rolls': 1, 'entries': [item('diamond_pickaxe', 3, extra=enchanted(20, 39)), item('diamond_axe', 2, extra=enchanted(20, 39)),
                                     item('diamond_sword', 2, extra=enchanted(20, 39)), item('iron_pickaxe', 3, extra=enchanted(25, 39))]}],
    }
    assert set(chests) == LOOT, f'loot tables and kit.LOOT differ: {set(chests) ^ LOOT}'
    for name, pools_ in chests.items():
        write_json(f'data/{NS}/loot_table/chests/{name}.json', {'type': 'minecraft:chest', 'pools': pools_,
                                                                'random_sequence': f'{NS}:chests/{name}'})


# -- the miner's trades ---------------------------------------------------------------------------

# level -> [(name, wants, gives, max_uses, xp)]; items as (id, count). Wants may carry a second item.
TRADES = {
    1: [('coal', [('coal', 15)], ('emerald', 1), 16, 2),
        ('raw_copper', [('raw_copper', 12)], ('emerald', 1), 16, 2),
        ('torches', [('emerald', 1)], ('torch', 16), 16, 1),
        ('ladders', [('emerald', 1)], ('ladder', 8), 12, 1)],
    2: [('raw_iron', [('raw_iron', 6)], ('emerald', 1), 16, 10),
        ('copper_torches', [('emerald', 1)], ('copper_torch', 12), 12, 5),
        ('lanterns', [('emerald', 2)], ('lantern', 3), 12, 5),
        ('rails', [('emerald', 3)], ('rail', 16), 12, 5)],
    3: [('raw_gold', [('raw_gold', 4)], ('emerald', 1), 12, 20),
        ('redstone', [('redstone', 12)], ('emerald', 1), 12, 20),
        ('copper_helmet', [('emerald', 4)], ('copper_helmet', 1), 4, 10),
        ('tnt', [('emerald', 4), ('gunpowder', 2)], ('tnt', 2), 6, 10)],
    4: [('lapis', [('lapis_lazuli', 10)], ('emerald', 1), 12, 30),
        ('iron_pickaxe', [('emerald', 6)], ('iron_pickaxe', 1), 3, 15),
        ('survey_map', [('emerald', 10), ('compass', 1)], ('map', 1), 4, 15)],
    5: [('diamond', [('diamond', 1)], ('emerald', 6), 8, 30),
        ('diamond_pickaxe', [('emerald', 18), ('diamond', 1)], ('diamond_pickaxe', 1), 3, 30)],
}
OFFERS = {1: 2, 2: 2, 3: 2, 4: 2, 5: 1}


def trades():
    tags = {}
    for level, offers in TRADES.items():
        for name, wants, gives, uses, xp in offers:
            for i, _ in wants + [gives]:
                assert i in ITEMS, f'unknown trade item {i}'
            body = {'wants': {'id': 'minecraft:' + wants[0][0], 'count': wants[0][1]},
                    'gives': {'id': 'minecraft:' + gives[0], 'count': gives[1]},
                    'max_uses': uses, 'xp': xp, 'reputation_discount': 0.05}
            if len(wants) > 1: body['additional_wants'] = {'id': 'minecraft:' + wants[1][0], 'count': wants[1][1]}
            if name == 'iron_pickaxe':
                body['given_item_modifier'] = RANDOM_ENCHANT
            if name == 'diamond_pickaxe':
                body['given_item_modifier'] = enchanted(15, 25)
            if name == 'survey_map':
                body['given_item_modifier'] = survey_map(1)['modifier']
            write_json(f'data/{NS}/villager_trade/miner/{name}.json', body)
            tags.setdefault(level, []).append(f'{NS}:miner/{name}')
    for level, values in tags.items():
        write_json(f'data/{NS}/tags/villager_trade/miner/level_{level}.json', {'values': sorted(values)})
        write_json(f'data/{NS}/trade_set/miner/level_{level}.json', {
            'trades': f'#{NS}:miner/level_{level}', 'amount': OFFERS[level],
            'random_sequence': f'{NS}:trade_set/miner/level_{level}'})


# -- catalog for the game tests --------------------------------------------------------------------

def catalog_file(mods, catalog):
    out = {}
    for mod in mods:
        pieces = {t: info for t, info in catalog.items() if t.startswith(mod.KEY + '/')}
        residents, loot, haunts, books, spawners = [], [], [], [], []
        for info in pieces.values():
            n = info['notes']
            residents += n.get('residents', []); loot += n.get('loot', []); haunts += n.get('haunts', [])
            books += n.get('books', []); spawners += n.get('spawners', [])
        start = [loc for loc, _ in mod.POOLS[mod.STRUCTURE['start_pool']]['elements']]
        out[mod.KEY] = {'name': mod.NAME, 'structure': f'{NS}:{mod.KEY}', 'inhabited': bool(mod.STRUCTURE.get('inhabited')),
                        'depth': [mod.STRUCTURE['min_y'], mod.STRUCTURE['max_y']], 'start': start,
                        'start_residents': sorted(sum((catalog[s]['notes'].get('residents', []) for s in start), [])),
                        'residents': sorted(set(residents)), 'loot': sorted(set(loot)), 'haunts': sorted(set(haunts)),
                        'books': books, 'spawners': sorted(set(spawners)), 'pieces': sorted(pieces),
                        'features': getattr(mod, 'FEATURES', [])}
        for role in out[mod.KEY]['residents']: assert role in ROLES
    write_json(f'data/{NS}/{NS}/catalog.json', out)


def main():
    check_only = '--check' in sys.argv
    only = None
    for a in sys.argv:
        if a.startswith('--only='): only = a.split('=', 1)[1].split(',')
    mods = designs.modules(only)
    assert mods, 'no designs yet'
    catalog = {}
    if not check_only:
        shutil.rmtree(os.path.join(DATA, 'structure'), ignore_errors=True)
        shutil.rmtree(os.path.join(DATA, 'worldgen'), ignore_errors=True)
    for mod in mods:
        for t in mod.pieces():
            assert t.name.startswith(mod.KEY + '/'), f'{t.name}: pieces of {mod.KEY} are named "{mod.KEY}/..."'
            assert t.name not in catalog, f'duplicate piece {t.name}'
            if check_only:
                t.validate()
                catalog[t.name] = {'jigsaws': [{**j, 'pos': list(j['pos'])} for j in t.jigsaws], 'notes': t.notes,
                                   'size': list(t.size), 'blocks': len(t.blocks)}
            else:
                catalog[t.name] = t.save()
        check_design(mod, catalog)
    if check_only:
        print(f'ok: {len(catalog)} pieces in {len(mods)} designs')
        return
    structures(mods)
    loot()
    trades()
    catalog_file(mods, catalog)
    for mod in mods:
        pieces = [t for t in catalog if t.startswith(mod.KEY + '/')]
        blocks = sum(catalog[t]['blocks'] for t in pieces)
        print(f'  {mod.KEY:8} {mod.NAME:22} {len(pieces):2} pieces {blocks:6} blocks  y {mod.STRUCTURE["min_y"]}..{mod.STRUCTURE["max_y"]}')
    print(f'{len(catalog)} templates, {len(mods)} structures, 1 structure set')
    if '--render' in sys.argv:
        os.system(f'"{sys.executable}" "{os.path.join(HERE, "preview.py")}"')


if __name__ == '__main__':
    main()
