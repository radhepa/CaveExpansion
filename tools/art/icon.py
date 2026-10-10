"""The Cave Expansion mod icon: the Old Delvers' mark, a glowing lantern above two crossed pickaxes,
on deepslate tiles framed in polished blackstone with a gold inlay, with a few ore flecks in the stone.

Painted at 32x32 from palette-locked rasters (pixel.RAMPS), upscaled 4x with nearest-neighbour.

    python tools/art/icon.py                  # writes src/main/resources/assets/caveexpansion/icon.png
    python tools/art/icon.py --check          # verifies the written icon matches this script
    python tools/art/icon.py --preview out.png  # the icon at 128, 64 and 32 px on light and dark grounds
"""
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixel  # noqa: E402
from pixel import RAMPS as R, raster, stamp, locked  # noqa: E402

DEST = pixel.PROJECT / 'src/main/resources/assets/caveexpansion/icon.png'
SIZE, SCALE = 32, 4

# Deepslate tiles, 16x8, repeated: a mortar, b-e brick tones (dark to light).
TILES = """
dddeddda dddddeda
dccccbca dcccbcca
dcbcccba dccbccba
aaaaaaaa aaaaaaaa
ddda dddddeda dddd
cbca dccccbca dccc
ccba dcbcccba dcbc
aaaa aaaaaaaa aaaa
"""
STONE = {'a': R['deepslate'][0], 'b': R['deepslate'][1], 'c': R['deepslate'][2], 'd': R['deepslate'][3], 'e': R['deepslate'][4]}
# The lantern's light on the stone: the same tones, warmed in steps (the outer step dithered).
LIT = {'a': R['bark'][0], 'b': R['bark'][1], 'c': R['bark'][2], 'd': R['flame'][0], 'e': R['flame'][1]}
WARM = {'a': R['bark'][0], 'b': R['bark'][1], 'c': R['bark'][2], 'd': R['bark'][3], 'e': R['spruce'][1]}

PICK = """
....................
....................
....sTTTTT..........
.....SSttTTT........
........SSttTT......
..........SStTT.....
............htT.....
...........hdStT....
..........hd.StT....
.........hd...STT...
........hd....StT...
.......hd......tT...
......hd.......ST...
.....hd........ST...
....hd..........s...
...hd...............
..hd................
.hd.................
Hd..................
....................
"""
PICK_COLORS = {'s': R['steel'][0], 'S': R['steel'][2], 't': R['steel'][3], 'T': R['steel'][4],
               'h': R['oak'][5], 'H': R['oak'][6], 'd': R['oak'][1]}

LANTERN = """
.....oo.....
....oJIo....
....o..o....
...ooJJoo...
..oJJJJJIo..
.oJJJJJJJIo.
.oJmMnnMmIo.
.oJMnNNnMIo.
.oJMnNNnMIo.
.oJmMnnMmIo.
.oJLmMMmLIo.
.oIIIIIIIio.
..oiiiiiio..
...oooooo...
"""
LANTERN_COLORS = {'o': R['blackstone'][0], 'J': R['iron'][3], 'I': R['iron'][1], 'i': R['iron'][0],
                  'N': R['flame'][6], 'n': R['flame'][5], 'M': R['flame'][4], 'm': R['flame'][3],
                  'L': R['flame'][2], 'l': R['flame'][0]}

# Ore flecks in the stone: (x, y, pattern rows) with g=gold, c=copper, i=raw iron; lit pixel first.
FLECKS = [
    (4, 4, ['gG', '.G']), (25, 3, ['cC']), (27, 13, ['i', 'I']), (3, 15, ['C', 'cC']),
    (6, 26, ['gG']), (25, 27, ['iI', '.I']), (14, 28, ['c']),
]
FLECK_COLORS = {'g': R['gold'][5], 'G': R['gold'][2], 'c': R['copper'][4], 'C': R['copper'][1],
                'i': R['raw_iron'][5], 'I': R['raw_iron'][3]}
LANTERN_AT = (10, 3)
GLOW = (16, 11.5)  # centre of the lantern glass (pixel corners)
PICKS_Y = 11      # the right-hand pick's sprite sits at (12, PICKS_Y), its mirror at (0, PICKS_Y)


def rows(pattern):
    return [r.replace(' ', '') for r in pattern.strip('\n').splitlines()]


def background():
    """Deepslate tiles warmed by the lantern, framed in blackstone with a gold inlay."""
    tile = rows(TILES)
    image = Image.new('RGBA', (SIZE, SIZE))
    for y in range(SIZE):
        for x in range(SIZE):
            tone = tile[y % 8][x % 16]
            d = ((x + .5 - GLOW[0]) ** 2 + (y + .5 - GLOW[1]) ** 2) ** .5
            if d < 8:
                ramp = LIT
            elif d < 10 or (d < 12.5 and (x + y) % 2 == 0):
                ramp = WARM
            else:
                ramp = STONE
            image.putpixel((x, y), pixel.rgb(ramp[tone]))
    last = SIZE - 1
    for i in range(SIZE):
        for x, y in ((i, 0), (0, i), (i, last), (last, i)):
            image.putpixel((x, y), pixel.rgb(R['blackstone'][1]))
    for i in range(1, last):
        image.putpixel((i, 1), pixel.rgb(R['gold'][1]))
        image.putpixel((1, i), pixel.rgb(R['gold'][1]))
        image.putpixel((i, last - 1), pixel.rgb(R['gold'][0]))
        image.putpixel((last - 1, i), pixel.rgb(R['gold'][0]))
    for x, y in ((1, 1), (last - 1, 1), (1, last - 1), (last - 1, last - 1)):
        image.putpixel((x, y), pixel.rgb(R['gold'][4]))
    return image


def icon():
    image = background()
    for x, y, pattern in FLECKS:
        stamp(image, '\n'.join(pattern), FLECK_COLORS, x, y)
    mirrored = '\n'.join(r[::-1] for r in rows(PICK))
    stamp(image, mirrored, PICK_COLORS, 0, PICKS_Y)
    stamp(image, PICK, PICK_COLORS, 12, PICKS_Y)
    stamp(image, LANTERN, LANTERN_COLORS, *LANTERN_AT)
    return locked(image, 'icon')


def big(image, scale=SCALE):
    return image.resize((image.width * scale, image.height * scale), Image.NEAREST)


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    return buffer.getvalue()


def preview(dest):
    """The icon at 128, 64 and 32 px (as Mod Menu shows it) on light and dark grounds."""
    full = big(icon())
    sheet = Image.new('RGBA', (2 * (128 + 64 + 32 + 40) + 20, 148), '#D8DEE4')
    sheet.paste(Image.new('RGBA', (sheet.width // 2, 148), '#1E2228'), (sheet.width // 2, 0))
    for n in range(2):
        x = 10 + n * (sheet.width // 2)
        for size in (128, 64, 32):
            sheet.alpha_composite(full.resize((size, size), Image.LANCZOS if size < 128 else Image.NEAREST), (x, 10))
            x += size + 20
    sheet.convert('RGB').save(dest)
    print('preview', dest)


if __name__ == '__main__':
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
    elif '--check' in sys.argv:
        ok = DEST.exists() and DEST.read_bytes() == png(big(icon()))
        print('Icon is up to date.' if ok else 'Icon is out of date (rerun tools/art/icon.py).')
        sys.exit(0 if ok else 1)
    else:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        DEST.write_bytes(png(big(icon())))
        print('wrote', DEST.relative_to(pixel.PROJECT).as_posix())
