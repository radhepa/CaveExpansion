"""A tiny worked example of a design module (not built into the mod): one room with an anchor, a tunnel that
chains, and a cap. Copy its shape, not its looks. See DESIGN.md, "Design module contract"."""
from kit import Template

KEY = 'example'
NAME = 'Example Delve'
FEATURES = ['a lit room with a resident', 'tunnels that end in rubble']
STRUCTURE = {'start_pool': 'example/start', 'size': 3, 'horizontal': 48, 'vertical': 16,
             'min_y': 0, 'max_y': 30, 'cover': 10, 'inhabited': True, 'weight': 1}
POOLS = {
    'example/start': {'elements': [('example/room', 1)]},
    'example/tunnels': {'elements': [('example/tunnel', 3), ('example/cap', 1)], 'fallback': 'example/caps'},
    'example/caps': {'elements': [('example/cap', 1)]},
}


def room():
    t = Template('example/room', (11, 6, 11))
    t.fill((0, 0, 0), (10, 0, 10), 'stone_bricks')            # floor (built: always placed)
    t.carve((1, 1, 1), (9, 4, 9))                              # the room's air
    t.shell((1, 1, 1), (9, 4, 9), 'tuff')                      # rock lining (soft: only where the world is solid)
    t.anchor(5, 0, 5, floor='chiseled_stone_bricks')           # where the delve stands
    for x, z in ((2, 2), (8, 2), (2, 8), (8, 8)):
        t.set(x, 4, z, 'lantern[hanging=true]')
    t.resident(5, 1, 7, 'miner', facing='north')
    t.chest(1 + 1, 1, 1 + 1, 'south', 'camp/supplies')
    # a doorway east: jigsaw in the outer face (x = 10), at walking height, pointing out
    t.carve((10, 1, 4), (10, 3, 6))
    t.jigsaw(10, 1, 5, 'east_up', 'example/door', target='example/tunnel_in', pool='example/tunnels')
    return t


def tunnel():
    t = Template('example/tunnel', (8, 5, 3))
    t.fill((0, 0, 0), (7, 0, 2), 'cobblestone')
    t.carve((0, 1, 0), (7, 3, 2))
    t.jigsaw(0, 1, 1, 'west_up', 'example/tunnel_in')          # joins the door (or the last tunnel)
    t.jigsaw(7, 1, 1, 'east_up', 'example/tunnel_out', target='example/tunnel_in', pool='example/tunnels')
    t.set(3, 3, 1, 'lantern[hanging=true]')
    return t


def cap():
    t = Template('example/cap', (3, 5, 3))
    t.fill((0, 0, 0), (2, 0, 2), 'cobblestone')
    t.carve((0, 1, 0), (1, 3, 2))
    t.fill((2, 1, 0), (2, 2, 2), 'gravel')                       # rubble (soft)
    t.jigsaw(0, 1, 1, 'west_up', 'example/tunnel_in')
    return t


def pieces():
    return [room(), tunnel(), cap()]
