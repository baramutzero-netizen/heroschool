"""Pack validated standalone frames. Never infer cell boundaries from a sheet."""
from pathlib import Path
import base64, io, json, math, re
import numpy as np
from PIL import Image
import pack

HERE = Path(__file__).resolve().parent
MOTIONS = ['idle', 'attack', 'hit', 'down', 'win']
CELL, GUTTER, COLS = 256, 2, 24

def main():
    manifest = json.loads((HERE/'frames-v3/manifest.json').read_text(encoding='utf8'))
    assert manifest['canvas'] == [CELL, CELL]
    assert manifest['pivot'] == [128, 170]
    images, metadata, counts, palettes = [], {}, {}, {}
    def append(im):
        n = len(images)
        images.append(im)
        return [(n % COLS)*(CELL+2*GUTTER)+GUTTER,
                (n // COLS)*(CELL+2*GUTTER)+GUTTER, CELL, CELL]
    for job, info in sorted(manifest['jobs'].items()):
        frames = info['frames']
        counts[job] = info['counts']
        metadata[job] = [[] for _ in MOTIONS]
        sheet = Image.new('RGBA', (6*CELL, 5*CELL))
        bodies, effects = [], []
        for f in frames:
            assert f['pivot'] == manifest['pivot'], (job, f['file'], 'pivot')
            pair = []
            for key in ['file', 'effect']:
                im = Image.open(HERE/'frames-v3'/f[key]).convert('RGBA')
                assert im.size == (CELL, CELL), f[key]
                assert set(np.unique(np.asarray(im)[:,:,3])) <= {0,255}, f[key]
                bbox = im.getbbox()
                if bbox:
                    assert min(bbox[:2]) >= 16 and max(bbox[2:]) <= 240, (f[key], bbox)
                pair.append(im)
            body, effect = pair
            assert body.getbbox() or effect.getbbox(), ('Empty frame', f['file'])
            bodies.append(body); effects.append(effect)
            sheet.paste(body, (f['frame']*CELL, MOTIONS.index(f['motion'])*CELL))
        # One shared palette per character, not independent frame palettes.
        alpha = sheet.getchannel('A')
        rgb = Image.new('RGB', sheet.size); rgb.paste(sheet, mask=alpha)
        sheet = rgb.quantize(colors=96, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE).convert('RGBA')
        sheet.putalpha(alpha)
        ban = pack.skin_colors(sheet, CELL) | pack.head_only(sheet, CELL)
        palettes[job] = pack.cloth_colors(sheet, CELL, ban)[0]
        for f, effect in zip(frames, effects):
            row, col = MOTIONS.index(f['motion']), f['frame']
            body = sheet.crop((col*CELL,row*CELL,(col+1)*CELL,(row+1)*CELL))
            entry = {'rect':append(body), 'duration':f['duration']}
            if effect.getbbox(): entry['fx'] = append(effect)
            assert col == len(metadata[job][row]), ('Noncontiguous frames', job, row)
            metadata[job][row].append(entry)
        assert list(map(len, metadata[job])) == counts[job]
        print(job, counts[job], 'validated')
    stride = CELL+2*GUTTER
    atlas = Image.new('RGBA', (COLS*stride, math.ceil(len(images)/COLS)*stride))
    for n, im in enumerate(images):
        atlas.paste(im, ((n%COLS)*stride+GUTTER,(n//COLS)*stride+GUTTER))
    buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, method=6, exact=True)
    dump = lambda obj: json.dumps(obj, separators=(',',':'))
    js = f'const SPR_CELL=256,SPR_COLS=6,SPR_META={dump(metadata)};\n'
    js += f'const SPR_JOB={dump(counts)};\nconst SPR_HAIR={dump(palettes)};\n'
    js += 'const SPR_IMG="data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()+'";\n'
    js += pack.pack_fx()
    (HERE/'sprites.js').write_text(js, encoding='utf8')
    game = HERE.parent/'game.html'
    text = game.read_text(encoding='utf8')
    for line in js.strip().splitlines():
        name = re.match(r'const ([A-Za-z_]\w*)',line)[1]
        text, n = re.subn(r'^const '+name+r'[=,].*$', lambda _:line, text, count=1, flags=re.M)
        assert n == 1, ('Missing runtime constant',name)
    game.write_text(text,encoding='utf8')
    atlas.save(HERE/'atlas.png')
    print(f'{len(images)} cells / {atlas.size} / {len(buf.getvalue())//1024} KB; game.html updated')

if __name__ == '__main__': main()
