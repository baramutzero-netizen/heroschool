"""이국의 부채 그림 v2 (1013) — 도트 그림 SVG 를 만든다 (스킬 강화 창의 이국의 부채 단추 · 휘두르는 부채가 같이 쓴다).
사용자가 준 참고 그림(은빛 주름 · 두꺼운 흰 테두리 · 붉은 손잡이 · 흰 마개)을 따라 — 주름 M 개(밝은 면 · 그늘 면 · 골 선) + 뾰족한 주름 끝,
감은 줄 손잡이 · 흰 마개를 그리고 부채 선(회청) → 흰 테두리 2칸 → 바깥 어두운 선(모두 4방향 — 계단 모서리). 그림자는 게임 CSS(drop-shadow).

    python3 tools/gen/patch/skup_fan.py assets/skill-upgrade/fan-v2.svg [미리보기.png] [기울기 도]

모양 · 색은 아래 숫자 · C 표에서. 그림 크기(viewBox)가 바뀌면 game.html 의 SK_CHOICE_FIT.fan(단추 폭에 대한 그림 너비 · 높이)도 같은 비율로."""
import math, sys
TILT = float(sys.argv[3]) if len(sys.argv) > 3 else 0       # + 시계 방향 (1013 은 0 — 똑바로)
W, H = 64, 64
PX, PY = 32, 37.5           # 사북 (돌리기 축)
TOP, RMAX, A, M, Z = 22.5, 29.5, 57, 7, .22
HL = 11                     # 손잡이 길이
C = {"o": "#55647d", "w": "#ffffff", "e": "#252a37",
     "l": "#f7fafd", "m": "#c4d1df", "d": "#9dadc2", "k": "#687893", "h": "#ffffff",
     "r": "#d4323a", "R": "#a11e25", "q": "#66111a", "s": "#f6c9cb", "c": "#ffffff", "C": "#b9c3cf"}
ct, st = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
def shade(cx, cy):
    # 그림 좌표 → 돌리기 전 좌표 (사북 축으로 -TILT)
    ox, oy = cx - PX, cy - PY
    ux, uy = ox * ct + oy * st, -ox * st + oy * ct      # 화면(y 아래) 기준 회전의 역
    # 손잡이 · 마개
    if -1.5 <= ux < 1.5 and -1 <= uy < HL:
        if ux < -.5: return "R"
        if (math.floor(ux) + math.floor(uy)) % 3 == 0: return "q"
        if 0.5 <= ux and 1 <= uy < 2: return "s"
        return "r"
    if -2.5 <= ux < 2.5 and HL <= uy < HL + 2:
        return "C" if (uy >= HL + 1 or ux < -1.5) else "c"
    dx, dy = ux, -uy
    r = math.hypot(dx, dy)
    if dy < -.8 or r < .1: return None
    th = math.degrees(math.atan2(dx, dy))
    if abs(th) > A: return None
    u = (th + A) / (2 * A) * M; k = min(M - 1, int(u)); f = u - k
    t = 1 - abs(2 * f - 1)
    base = min(TOP / max(.2, math.cos(math.radians(th))), RMAX)
    edge = base * (1 - Z * (1 - t))
    if r > edge: return None
    fold = min(abs(r * math.sin(math.radians(th - (-A + 2 * A * j / M)))) for j in range(M + 1))
    if fold < .55 and 5 < r < edge - .7: return "k"
    if r > edge - 1.2 or r < 6.5: return "d"
    if f < .5:
        return "h" if (f < .2 and 9 < r < edge - 3.5) else "l"
    return "m"
g = [[shade(x + .5, y + .5) for x in range(W)] for y in range(H)]
fill = {(x, y) for y in range(H) for x in range(W) if g[y][x]}
def ring(src):
    out = set()
    for (x, y) in src:
        for ddx, ddy in ((1,0),(-1,0),(0,1),(0,-1)):
            p = (x + ddx, y + ddy)
            if p not in src and 0 <= p[0] < W and 0 <= p[1] < H: out.add(p)
    return out
acc = set(fill)
for col in ("o", "w", "w", "e"):
    rg = ring(acc)
    for (x, y) in rg: g[y][x] = col
    acc |= rg
used = [(x, y) for y in range(H) for x in range(W) if g[y][x]]
x0 = min(p[0] for p in used); x1 = max(p[0] for p in used); y0 = min(p[1] for p in used); y1 = max(p[1] for p in used)
vw, vh = x1 - x0 + 1, y1 - y0 + 1
paths = {}
for y in range(y0, y1 + 1):
    x = x0
    while x <= x1:
        c = g[y][x]
        if not c: x += 1; continue
        s0 = x
        while x <= x1 and g[y][x] == c: x += 1
        paths.setdefault(c, []).append("M%d %dh%dv1h-%dz" % (s0 - x0, y - y0, x - s0, x - s0))
order = ["e", "w", "o", "d", "m", "l", "h", "k", "R", "r", "q", "s", "C", "c"]
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" shape-rendering="crispEdges">' % (vw, vh)
       + "".join('<path fill="%s" d="%s"/>' % (C[c], "".join(paths[c])) for c in order if c in paths) + "</svg>")
open(sys.argv[1], "w").write(svg)
print("size", vw, vh, "svg", len(svg))
if len(sys.argv) > 2 and sys.argv[2] != "-":
    from PIL import Image
    im = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = g[y][x]
            if c:
                hx = C[c].lstrip("#"); im.putpixel((x - x0, y - y0), tuple(int(hx[i:i+2], 16) for i in (0, 2, 4)) + (255,))
    big = im.resize((vw * 4, vh * 4), Image.NEAREST)
    bg = Image.new("RGBA", big.size, (225, 237, 255, 255)); bg.alpha_composite(big); bg.save(sys.argv[2])
