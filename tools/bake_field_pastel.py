"""전투 배경에 파스텔 필터(ILLUS_FILTER_SPEC §4.1)를 입혀 assets/field_pastel/ 로 굽는다.
    python tools/bake_field_pastel.py
어두운 실내 필드는 명세 권장대로 lift 를 낮춘다(회색으로 뜨지 않게)."""
import os, sys, glob, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from illus_filters import preset_pastel
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DARK = {"dummy": .13, "gargoyle": .13, "guardian": .13, "wraith": .14, "demonking": .12}
os.makedirs(os.path.join(ROOT, "assets/field_pastel"), exist_ok=True)
for f in sorted(glob.glob(os.path.join(ROOT, "assets/field_img/*.webp"))):
    k = os.path.splitext(os.path.basename(f))[0]
    rgba = np.array(Image.open(f).convert("RGBA"))
    kw = {"lift": DARK[k]} if k in DARK else {}
    out = preset_pastel(rgba, **kw)
    Image.fromarray(out[..., :3], "RGB").save(os.path.join(ROOT, "assets/field_pastel", k + ".webp"), quality=86, method=6)
    print(k, kw)
