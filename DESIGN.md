# Cave Expansion: design

Cave Expansion is an add-on for the Village Friends modpack (Minecraft 26.3, Fabric). It revamps the underground
with **eight rare places** you stumble on while caving or strip-mining. Three are lived in (Village Friends
residents: miners, the Deepwatch garrison, a hermit); five are abandoned, with guardians, lore and loot.

It needs Village Friends (it uses its residents, conversation window and guards); Village Friends never needs it.
It must play well with everything else in the pack: the Plata Clan (whose dens and warrens are also
underground), the RPG add-on, Not-So-Vanilla Mobs, Turning Seasons, End Friends and Nether Friends.

## The eight delves

| key | name | depth (floor y) | lived in? | the hook |
|---|---|---|---|---|
| `camp` | Delvers' Camp | -4 .. 36 | 3 miners + a foreman | a working mine camp: bunks, forge, ore carts, rich working faces; miners trade and tell you where other delves are |
| `seam` | The Buried Seam | -12 .. 32 | no | a Guild mine lost to a cave-in; rubble, a derailed ore cart, the foreman's last log, and the rich seam that got them killed; restless miners rise |
| `post` | Deepwatch Post | -20 .. 8 | 2 knights, 2 archers, a captain | a fortified checkpoint across a cave road; the garrison fights cave monsters; behind it the sealed Deepgate and what it guards |
| `cistern` | The Drowned Cistern | -24 .. 16 | no | a pillared, half-flooded reservoir of the Old Delvers; swim down to the sunken vault; the drowned wake |
| `hermit` | Hermit's Hollow | 12 .. 44 | an old hermit | a cosy mushroom-grove home in a mossy cave: giant mushrooms, glow berries, a pond, brews |
| `grotto` | The Glimmering | -44 .. -8 | no | a vast amethyst-and-calcite cavern with a still pool and an ancient crystal shrine |
| `ossuary` | The Ossuary | -52 .. -16 | no | the Old Delvers' catacombs: bone niches, sarcophagi, candles; a crypt keeper and its skeletons |
| `forge` | The Sunken Forge | -50 .. -28 | no | an ancient forge-hall over a lava lake: anvils, blast furnaces, lava channels; the masterwork vault (netherite template) |

### Lore (shared by every design, dialogue and book)
- **The Old Delvers**: a vanished people of master miners and smiths who lived deep below, long before the
  villages. Their works are the Sunken Forge, the Drowned Cistern (their waterworks), the Ossuary (their dead)
  and the Glimmering (their holy place). Their stone is deepslate tile and polished blackstone with gold inlay;
  their mark is a **lantern** (a lantern over crossed picks). Nobody knows why they left or died.
- **The Delvers' Guild**: today's miners, from the villages above, who work camps underground for months at a
  time ("a shift" is a season). Their camps are timbered (spruce and oak), lit by lanterns, on rails.
  Guild sayings: "Mind the roof", "Light behind you, light ahead", "Stone gives, stone takes".
- **The Deepwatch**: an old order of guards (Village Friends knights and archers) posted at the ways down,
  keeping cave monsters from rising and keeping fools from going too deep. Banner: black field, a white
  lantern-like charge (vanilla patterns). Each post keeps a Watch Log.
- **The Buried Seam**: a Guild camp that dug too greedily under a bad roof; the cave-in buried a whole shift.
  The miners who never came out are the restless miners.
- **The hermit**: a former Guild miner who stayed below decades ago and now grows mushrooms and brews.
- **The Plata Clan** (when installed): miners have seen silver husks in the stone near the surface and tell
  stories of "silver folk". Our delves never stand near a Plata den or warren (see Placement).

## Rarity and placement
- One structure set, `caveexpansion:delves`: one delve per 30 x 30 chunk cell (about one in every 480 x 480
  blocks), separation 12; which of the eight is weighted (camp 3, seam 3, the others 2, forge 1).
- `config/caveexpansion.json` `"rarity"`: multiplies the spacing (2.0 = half as many per side, 0.5 = more).
- The placement (`caveexpansion:spread`) keeps clear of: villages 4 chunks, Village Friends homesteads 2,
  Plata dens 3, Plata warrens 5, trial chambers 4, ancient cities 4, strongholds 3, ocean monuments 2. A set
  from a mod that isn't installed is skipped.
- `caveexpansion:delve` (the structure type) picks the delve's height inside its depth range so that it **touches
  a cave** (it samples the noise caves around it) and has no water or lava in its core, then checks that every
  piece keeps at least `cover` blocks of ground above it (an exposed branch is dropped; an exposed core means no
  delve here). Never in the Deep Dark.
- Lived-in delves stop monsters spawning inside their pieces (and are lit anyway).

## What's in the code
- `caveexpansion:delve` structure type, `caveexpansion:spread` placement, `caveexpansion:natural` processor.
- Blocks: `prospecting_table` (the miner's workstation), `haunt` (invisible guardian marker).
- Profession `caveexpansion:miner` (trades in `data/caveexpansion/villager_trade/miner`).
- Residents: Village Friends residents with the homestead "dweller" attachment (roles `caveexpansion_miner`,
  `_foreman`, `_warden`, `_captain`, `_hermit`): no village, own day, tethered to their delve, own dialogue,
  rumours about other delves, gear (copper helmet and pick for miners).
- Haunts: `restless_miner` (Not-So-Vanilla Mobs Lost Miners when installed, else zombies in miners' gear),
  `drowned`, `crypt_keeper` (NSV Gravewarden when installed, else an armoured skeleton) + skeletons,
  `cinder` (NSV Soulpyres when installed, else magma cubes).

---

## Design module contract (for whoever builds a delve)

Each delve is one Python module, `tools/delves/designs/<key>.py`, built with `tools/delves/kit.py`. Run from
the repo root:

```
python tools/delves/build.py --check        # validates every design (blocks, properties, pools, jigsaws)
python tools/delves/preview.py <key>         # isometric cutaways to tools/delves/out/<key>_<piece>.png
python tools/delves/preview.py <key> --full  # the whole piece, uncut
```

Look at your previews (open the PNGs) and fix what looks wrong. `designs/_example.py` is a tiny worked example.

### The module
```python
KEY = 'camp'                          # the structure id: caveexpansion:camp
NAME = "Delvers' Camp"
FEATURES = ['...']                    # one line per notable thing (for the docs and the showcase)
STRUCTURE = {
    'start_pool': 'camp/start',       # pool of start pieces (each has exactly one anchor)
    'size': 5,                        # jigsaw depth (how many links out from the start)
    'horizontal': 64, 'vertical': 24, # max distance of any piece from the start (blocks)
    'min_y': -4, 'max_y': 36,         # where the anchor floor block may be (use the table above)
    'cover': 10,                      # ground needed above every piece
    'inhabited': True,                # no monster spawns inside the pieces
    'weight': 3,                      # share of the structure set (use the table above)
    'require': None,                  # optional 'camp/xyz': a piece the delve can't exist without
    'clearance': 10,                  # height above the floor checked for water/lava at the core
    'processors': [],                 # optional extra vanilla processors (e.g. minecraft:block_rot on planks)
    'chance': 1.0,                    # optional: share of offered spots it takes (the forge uses 0.45 to stay rarest)
}
POOLS = {                             # pool -> elements [(piece, weight)], optional fallback pool
    'camp/start': {'elements': [('camp/hall', 1)]},
    'camp/tunnels': {'elements': [('camp/drift', 3), ('camp/bend', 2), ('empty', 1)], 'fallback': 'camp/caps'},
    'camp/caps': {'elements': [('camp/cap', 1)]},
}
def pieces(): return [...]            # every Template; names are '<key>/<piece>'
```
`'empty'` in a pool is vanilla's empty element (the branch simply stops).

### Building pieces (kit.Template)
- Coordinates are template-local: x east, y up, z south, all from 0. `Template(name, (sx, sy, sz))`.
- `set`, `fill(a, b, block)`, `walls`, `carve(a, b)` (air), `shell(a, b, natural_block, thickness)` (lines the
  rock around a box), `get`. Block specs are vanilla ids with properties: `'spruce_stairs[facing=east,half=top]'`.
  Every block and property is checked against vanilla 26.3.
- **Unset cells are structure void**: the world's own block stays (living rock, or a cave's air). So you only
  set what you build and the air you carve.
- **Built blocks** (bricks, planks, logs, polished/cobbled stone, tiles, glass, lanterns...) always appear.
- **`'air'` always carves**: rooms and tunnels are always open, even through rock.
- **NATURAL blocks are soft** (`kit.NATURAL`: stone, deepslate, tuff, andesite/diorite/granite, calcite,
  amethyst, basalt, dripstone, moss, dirt, gravel, clay, mud, magma, obsidian, blackstone, every ore, raw ore
  blocks): in the world they only replace solid ground; where a cave is open they are skipped. Use them to
  line rock walls, set ore seams and make natural-looking surfaces. **Never** use them for a floor, wall,
  pillar or step that must be there: use a built block (cobblestone, cobbled deepslate, stone bricks, mossy
  cobblestone, polished/tiles...). Rubble piles should be cobblestone / cobbled deepslate / gravel *on a
  built floor*, accepting that gravel can be skipped.
- Floors under rooms: built blocks. A room may end up partly open to a cave; that's the point (you find it
  from the cave). Don't build sealed boxes with no way in: every delve needs at least one tunnel or opening
  that reaches its outer edge so cave explorers find a way in, and strip-miners break into a room or tunnel.
- Jigsaws: `jigsaw(x, y, z, '<facing>_up', name, target=..., pool=..., final='air')` in the outer face of the
  piece pointing out. A parent's `target` must equal the child jigsaw's `name`. Put horizontal jigsaws at walking
  height (floor + 1) in the middle of the opening. Use names prefixed with your key (`camp/door`). Vertical
  links use `up_<facing>` / `down_<facing>`.
- **Anchor**: every start piece has exactly one `anchor(x, y, z, floor=...)`: a floor block near the middle of
  the main room; the game puts the chosen height there (people walk at y + 1).
- Things that **must** exist (residents, the lore book, the main loot, signature features) go in the start
  piece or a `require`d piece: other pieces can be dropped if they would break the surface.
- Containers: `chest(x, y, z, facing, 'camp/supplies')`, `barrel(...)`, `pot(x, y, z, facing, loot=None,
  sherds=None)`. Only the loot tables in `kit.LOOT` exist (one design's tables are listed with it below).
- `lectern(x, y, z, facing, title, author, pages)`: the place's own book. Title <= 32 chars, pages short
  (~14 lines of ~19 characters; <= 700 chars), plain text, in the voice of the place. 3 to 6 pages.
- `sign(x, y, z, lines, facing, wood='spruce', wall=True)`; `banner(x, y, z, facing, color, [(pattern, color)])`
  with vanilla patterns (border, cross, stripe_center, circle, flower, curly_border, bricks, gradient...).
- `item_frame(x, y, z, facing, 'iron_pickaxe')` (hangs on the block behind it), `minecart(x, y, z, loot=None)`
  on a rail.
- `spawner(x, y, z, 'minecraft:skeleton')` (vanilla mobs only).
- `haunt(x, y, z, kind)`: invisible marker; the first time a player comes within 14 blocks the guardians rise
  there and it vanishes. Leave two blocks of air above it. Kinds: `restless_miner`, `drowned`, `crypt_keeper`,
  `cinder`.
- `resident(x, y, z, role, facing)`: a villager standing at (x, y, z) (feet; the block below must be solid).
  Roles: `miner`, `foreman`, `warden_knight`, `warden_archer`, `captain`, `hermit`. Give each a bed somewhere in
  the delve (vanilla beds, `red_bed[facing=..,part=foot|head]`), lived-in delves only.
- Job sites: miners need `caveexpansion:prospecting_table[facing=..]` (one per miner + foreman); wardens need
  `villagefriends:training_dummy[facing=..]` (knights) and `villagefriends:archery_target[facing=..]` (archers);
  the hermit needs a `brewing_stand`. Without one they lose the job.
- **Light**: lived-in delves must be lit (lanterns, torches): `kit.dark_spots(t)` lists walkable cells under
  light 8 and should be (nearly) empty for every lived-in piece. Abandoned delves are dim on purpose (a few
  candles, soul lanterns, glow lichen, lava), which is what lets their monsters spawn.
- Notes: the kit records residents, loot, haunts, books and spawners in `t.notes` for the tests. Add your own
  facts to `t.notes` if they help (e.g. `t.notes['deepgate'] = (x, y, z)`).
- Water and lava: you may place them (the cistern's flood, the forge's lava). Keep fluids inside built basins
  or carved hollows so they don't spill into the rock's caves in odd ways; source blocks only.
- Sizes: a start piece up to about 32 x 20 x 32; a whole delve within 64 blocks of its start horizontally.
  Under ~40,000 set blocks per delve. Rotations are random, so nothing may depend on a compass direction.
- Style: Minecraft-vanilla blocks only, medieval-fantasy, no modern things. Make it feel like a *place*:
  furniture, clutter, wear (mossy/cracked variants, cobwebs where abandoned), small stories (a half-eaten
  meal, a tally scratched on a sign, a toppled cart). Avoid giant empty boxes and perfect symmetry.

### Per-delve brief
Loot tables available (kit.LOOT): `camp/supplies|foreman|ore_cart`, `seam/cart|shack|rich`,
`post/armory|barracks|captain|deepgate`, `hermit/pantry|shelf`, `grotto/shrine|pot`, `cistern/vault|ledge`,
`ossuary/sarcophagus|reliquary`, `forge/supplies|vault`.

**camp: Delvers' Camp** (inhabited, weight 3, -4..36, cover 10). A timbered hall carved in rock (bunks for
4, a mess table, a cookfire or furnace, a small forge corner: blast furnace, anvil, grindstone; ore bins of
raw-ore blocks; 4 prospecting tables; foreman's corner with a lectern "Ore Ledger" and the foreman chest).
Rail drifts lead out (2 to 4 branches through the jigsaw), timber-propped (log posts and plank beams every
3-4 blocks), with working faces where the walls are thick with ores (soft ore blocks: coal, iron, copper,
some gold, redstone, lapis; deepslate variants if you want), a chest minecart (`camp/ore_cart`) on the rails,
a ladder/scaffolding shaft going up some way and ending in rock ("the way up we use", capped). Residents in
the start piece: 3 `miner` + 1 `foreman`. Lit everywhere.

**seam: The Buried Seam** (abandoned, weight 3, -12..32). The same Guild style, wrecked: broken props
(missing posts, sagging beams, fallen logs), rubble mounds (cobblestone, gravel, tuff on built floors),
rails with gaps, a derailed chest minecart (`seam/cart`), cobwebs, skeleton remains (bone blocks, a skull),
candles burned down, the foreman's shack (lectern "The Last Shift", the foreman's log, and `seam/shack`), a
cave-spider spawner in a side drift, a `restless_miner` haunt (one or two), and the **rich seam**: a chamber
behind a rubble wall whose walls are crowded with ores incl. a few diamond ores and raw gold blocks, with a
`seam/rich` chest. Dim.

**post: Deepwatch Post** (inhabited, weight 2, -20..8, size up to ~31 x 16 x 25). A fortified barbican
across a cave road (stone/deepslate bricks): a gatehouse with a decorative portcullis (iron bars) over the road,
crenellated walls, two archer towers with arrow slits, barracks (5 beds), armory (`post/armory`, training
dummies + archery targets: 2 dummies, 2 targets), a mess, the captain's room (lectern "Deepwatch Log",
`post/captain`), braziers (campfires), Deepwatch banners. The road runs through the gate both ways (jigsaw
roads/tunnels out of both ends so explorers arrive along it). Behind the post: **the Deepgate**, a heavy
iron door (closed, with a lever beside it) to a stair down to a sealed chamber with `post/deepgate` loot.
Residents in the start piece: 2 `warden_knight`, 2 `warden_archer`, 1 `captain`. Lit.

**cistern: The Drowned Cistern** (abandoned, weight 2, -24..16). An Old Delver reservoir: a vaulted hall of
stone bricks/deepslate tiles, rows of pillars with arches, walkways along the walls, the floor flooded
(water source blocks, 4 to 8 deep), a sunken vault at the bottom (a grate of iron bars or a door, a
`cistern/vault` chest), stairs down from the walkway into the water, a sluice/valve room, a lectern
"Waterwarden's Ledger", `cistern/ledge` barrels on the walkways, a `drowned` haunt. Dim (some sea lanterns
underwater, a few candles). Water stays inside built walls.

**hermit: Hermit's Hollow** (inhabited, weight 2, 12..44). A natural-looking mossy cave (moss, rooted dirt,
dirt, clay lining; soft) with a giant red and a giant brown mushroom (mushroom stem + caps), mycelium/podzol
patches on a built floor, glow berries (cave_vines with berries), a small pond (water in a basin) with lily
pads, and the hermit's hut (spruce + mushroom stem): bed, brewing stand, cauldron, shelves, pantry barrel
(`hermit/pantry`), a chest `hermit/shelf`, candles, a lectern "Notes on the Deep". One way in is a winding
crawl/tunnel. Resident: 1 `hermit`. Lit (lanterns, shroomlight, glow berries).

**grotto: The Glimmering** (abandoned, weight 2, -44..-8). A big natural cavern (~28-36 across, ~16-20 high),
irregular, lined with calcite, amethyst blocks, budding amethyst and clusters, smooth basalt veins, dripstone,
glow lichen; a still pool with a few glowing blocks under the water; and the Old Delvers' crystal shrine in the
middle: a ring of deepslate-tile pillars with candles and amethyst, a dais, the `grotto/shrine` chest and a few
`grotto/pot` decorated pots. Carvings as signs. Paths in from two or more sides (jigsaw tunnels). Beautiful
first: the reward is finding it. No haunt.

**ossuary: The Ossuary** (abandoned, weight 2, -52..-16). Catacombs: a cross-shaped vaulted central crypt
(deepslate tiles/bricks, polished blackstone, bone blocks, skulls in niches, candles), side corridors (jigsaw)
lined with niches, sarcophagi (polished deepslate, `ossuary/sarcophagus` chests inside), two side crypts with a
`minecraft:skeleton` spawner each, the reliquary behind the central altar (`ossuary/reliquary`), a lectern
"Names of the Honoured Dead", and a `crypt_keeper` haunt in the central crypt. Soul lanterns, dim.

**forge: The Sunken Forge** (abandoned, weight 1, -50..-28). A great Old Delver forge-hall (polished
blackstone bricks, deepslate tiles, gilded blackstone, gold-block trim, iron chains, cauldrons) over a lava
lake: lava channels in the floor bridged by stone, a colossal anvil (anvils + iron blocks), banks of blast
furnaces and smokers, a bellows (built), forge supplies (`forge/supplies`), a lectern "The Smith's Rule", and
the **masterwork vault** reached across the lava (a narrow bridge or stepping stones) with `forge/vault`. A
`cinder` haunt in the hall. Lit by the lava itself, dim elsewhere. Lava stays in built basins.

---

## Residents
- Settled the first time they load (`Residents.settle`): Village Friends dweller attachment with our role,
  a name ("Brannoc of Copperdeep Camp"), the place's name, the profession and level, gear, and the delve's
  middle (they stay within 20 blocks of it).
- Their day (mixins into Village Friends' homestead hooks): no tavern, bell or market; work at their stations,
  eat and sleep in the delve; the garrison keeps a night watch.
- Talk: Village Friends' own window; every line comes from `data/caveexpansion/talk/lines.json` (compiled from
  `tools/talk/lines/*.txt`). Rumours name the nearest other delve, its direction and roughly how far.
- Miner trades (levels 1-5): coal/copper/iron/gold/redstone/lapis/diamond for emeralds; torches, ladders,
  lanterns, rails, TNT, a copper helmet, pickaxes, and a **survey map** to the nearest other delve.

## Testing
- `python tools/delves/build.py` (validates and writes data); `python tools/talk/talk.py` (dialogue).
- Unit tests: survey choice, rarity, talk bank.
- Client game test `DelvesClientTest`: locates every delve on a fixed seed, checks pieces, residents, loot,
  haunts, Plata distance; screenshots. Also run inside the whole modpack (`-PcompatMods=<instance mods>`).
