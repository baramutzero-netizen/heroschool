"""새 스킬 아이콘 · 등급 테두리 · 안쪽 바탕을 게임에 넣는다 (1015) — 몇 번을 돌려도 같은 결과.

    python3 tools/gen/patch/apply_skicon.py game.html

사용자: '새로운 스킬 아이콘들하고 테두리를 tools/newskillicon 폴더에 넣어두고 … 테두리는 등급에 맞춰서 색 변조해서 쓰고' ·
'옅은 등급색인데 살짝 그라데이션하고 글로스를 줘볼수있을까?' · '둥근 광택으로 게임에 적용' (목업 mockups/new-skill-icon — 고른 바탕은 둥근 광택 arc).

읽는 것 (game.html 옆 저장소):
  tools/newskillicon/icons/<폴더>/<이름>-96.png — 기술 80장 (직업마다 기본기 · 스킬 1 · 스킬 2 · 필살기 · 패시브 — 아래 ICONS)
  tools/newskillicon/frame/square-frame-96.png — 공용 테두리 (네 색만 등급 색으로 바꾼다 — FRAME_PAL)
쓰는 것 (무손실 WebP · 96 × 96 · 내용이 같으면 건드리지 않는다):
  assets/skill-icons/<직업>/<이름>.webp — 지금 SKILL_ICON_ART · SKILL_ICON_PASSIVE 가 가리키는 자리에 그대로 덮어쓴다
      (파일 이름은 예전 것 그대로 — 남는 파일이 없다. 새 묶음 이름과 다른 것은 아래 ICONS 옆 설명 · mockups/new-skill-icon/README.md 표)
  assets/skill-icons/frame-<등급>.webp — 등급 테두리 · assets/skill-icons/bg-<등급>.webp — 안쪽 바탕 (BG_STYLE · 처음 둥근 광택)
  assets/skill-icons/manifest.json — 자리 · 기술 이름 · 원본 · 크기 · 캐시 해시 (같은 폴더 README.md 는 손으로 쓴 설명)
game.html: SKILL_ICON_ART · SKILL_ICON_PASSIVE · SKILL_ICON_FRAME · SKILL_ICON_BG 네 줄의 ?v= (sha256 앞 10자리) —
  SKILL_ICON_BG 줄이 없으면 SKILL_ICON_FRAME 다음에 넣는다.
칸 그리기(바탕 · 그림 · 테두리 셋을 칸 가득 겹친다 · 테두리가 맨 위)는 game.html 코드 — skillIconHtml · 스타일리시 기술 선택 상자(camPick 의 icon) ·
학생 명부 책(roster_block.js — apply_roster). 크기별 그리기: 그림은 48 이하 부드럽게(auto) · 강화 창 80 은 픽셀 그대로 · 바탕 · 테두리는 늘 픽셀 그대로.
Pillow(libwebp)로 굽는다 — 버전이 다르면 바이트가 조금 달라질 수 있다 (그림은 같다)."""
import hashlib, io, json, os, re, sys
from PIL import Image

GRADES = ["D", "C", "B", "A", "S", "EX"]
# 게임 직업 키 → 아이콘 묶음 폴더 (소드맨만 이름이 다르다)
JOB_CLASS = {"archer": "archer", "bard": "bard", "darkpriest": "darkpriest", "druid": "druid", "enchanter": "enchanter",
             "forcemage": "forcemage", "gunner": "gunner", "monk": "monk", "ninja": "ninja", "paladin": "paladin", "priest": "priest",
             "rogue": "rogue", "spellsword": "spellsword", "sword": "swordsman", "timemage": "timemage", "wizard": "wizard"}
PREFIX = {"archer": "ar", "bard": "bd", "darkpriest": "dp", "druid": "dr", "enchanter": "en", "forcemage": "fm", "gunner": "gn",
          "monk": "mo", "ninja": "nj", "paladin": "pa", "priest": "pr", "rogue": "ro", "spellsword": "ss", "sword": "sw",
          "timemage": "tm", "wizard": "wz"}
SLOTS = ["_b", "_1", "_2", "_u", None]          # 기본기 · 스킬 1 · 스킬 2 · 필살기 · 패시브(SKILL_ICON_PASSIVE — 직업 키)
# 직업마다 [기본기, 스킬 1, 스킬 2, 필살기, 패시브] — 묶음의 icons/<폴더>/<이름>-96.png
# (게임 파일 이름이 다른 것 — 몽크 combo · chi-wave · circulation · hundred-fists · training / 아처 pierce · hawk-eye · meteor · sniper /
#  로그 assassinate / 타임 매지션 time-shard / 마법사 fire-burst · frost-field · gravity · resonance / 드루이드 regen-seed · nature-wrath · nature-recovery /
#  배틀메이지 strike · shatter-foot · overcharge · unseal · body / 암흑 사제 touch · drain · supper · pact-clean / 마법검사 triple)
ICONS = {
    "archer":     ["aimed-shot", "piercing-arrow", "hawks-eye", "meteor-arrow", "sniper-stance"],
    "bard":       ["pluck", "march", "dissonance", "victory", "harmony"],
    "darkpriest": ["dark-touch", "blood-rite", "curse", "dark-communion", "dark-pact"],
    "druid":      ["thorn-whip", "regeneration-seed", "beast-form", "natures-wrath", "natural-recovery"],
    "enchanter":  ["rune-shot", "weapon-rune", "magic-seal", "all-rune", "permanent-rune"],
    "forcemage":  ["mana-strike", "shattering-strike", "mana-overcharge", "unsealing", "mana-body"],
    "gunner":     ["greeting", "waltz", "knock", "finale", "encore"],
    "monk":       ["double-strike", "qi-wave", "inner-circulation", "white-hot-fist", "martial-focus"],
    "ninja":      ["kunai", "swamp", "water-dragon", "fuma", "water-mirage"],
    "paladin":    ["holy-strike", "protective-oath", "healing-light", "sanctuary", "guardian-vow"],
    "priest":     ["holy-wave", "greater-heal", "blessing", "revival", "prayer"],
    "rogue":      ["ambush", "poison", "shadow-step", "assassination", "weakness"],
    "spellsword": ["arcane-slash", "triple-v2", "awakening", "thousand-blades", "echo"],
    "sword":      ["slash", "taunt", "iron-wall", "earth-cleaver", "counter"],
    "timemage":   ["time-fragment", "haste", "delay", "time-stop", "foresight"],
    "wizard":     ["arcane-bolt", "flame-explosion", "frost-barrier", "gravity-reversal", "elemental-resonance"],
}

# ── 등급 테두리 — 공용 금색 테두리의 네 색(외곽선 · 어두운 면(아래 · 오른쪽) · 가운데 · 밝은 면(위 · 왼쪽 · 안쪽 모서리 점))을 등급 색으로.
#    색 차례는 예전 게임 테두리와 같다: D 회색 · C 초록 · B 파랑 · A 보라 · S 금(원래 색) · EX 분홍
FRAME_SRC = {(48, 32, 26): 0, (112, 72, 37): 1, (188, 139, 65): 2, (239, 199, 115): 3}
FRAME_PAL = {
    "D":  [(40, 40, 46), (92, 94, 100), (150, 152, 158), (212, 214, 218)],
    "C":  [(26, 48, 30), (50, 104, 58), (98, 164, 90), (178, 226, 144)],
    "B":  [(20, 36, 64), (40, 86, 142), (82, 144, 208), (166, 212, 248)],
    "A":  [(42, 24, 66), (90, 56, 146), (150, 104, 216), (216, 182, 252)],
    "S":  [(48, 32, 26), (112, 72, 37), (188, 139, 65), (239, 199, 115)],
    "EX": [(66, 14, 42), (152, 34, 98), (232, 84, 154), (255, 186, 222)],
}

# ── 안쪽 바탕 — 96 × 96 도트 (테두리와 같은 칸 · 바깥 3px 는 테두리가 덮는다) · 그림 '아래'에 깐다. 빛은 테두리처럼 왼쪽 위에서.
#    tint 옅은 등급색 한 색 · grad 그라데이션 · arc 그라데이션 + 둥근 광택(위쪽 반달 · 아래 끝이 또렷한 곡선 · 왼쪽 위 반짝임) ·
#    diag 그라데이션 + 비스듬한 광택(왼쪽 위 삼각 · 가는 줄 하나) — 목업에서 견준 넷. 게임은 BG_STYLE 하나만 쓴다.
BG_STYLE = "arc"
TINT = {"D": (227, 223, 215), "C": (226, 236, 201), "B": (221, 234, 239), "A": (236, 221, 242), "S": (247, 231, 186), "EX": (244, 220, 228)}   # 예전 테두리(64 × 64)의 가운데 색
GRAD_TOP, GRAD_BOT = .35, .38          # 위: 옅은 등급색 + 흰색 35% · 아래: 옅은 등급색 + 테두리 가운데 색 38% · 방향 0.85 × 세로 + 0.15 × 가로
GLOSS_ARC = dict(a0=.72, a1=.30, cx=48, cy=-16, rx=70, ry=62)      # 흰색 72%(맨 위) → 30%(곡선 끝) · 타원 (48, -16) 반지름 70 × 62
GLOSS_DIAG = dict(a0=.62, a1=.28, w=34)                            # x + y < 76 삼각 (흰색 62% → 28%) · x + y 82 ~ 87 가는 줄 35%
GLINT = [(7, 6), (8, 6), (9, 6), (10, 6), (6, 7), (7, 7), (6, 8), (6, 9), (6, 10)]   # 둥근 광택의 왼쪽 위 반짝임 (흰 점)
NAMES = ("SKILL_ICON_ART", "SKILL_ICON_PASSIVE", "SKILL_ICON_FRAME", "SKILL_ICON_BG")


def _mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def frame_of(root, g):
    out = Image.open(os.path.join(root, "tools", "newskillicon", "frame", "square-frame-96.png")).convert("RGBA")
    px, pal = out.load(), FRAME_PAL[g]
    for y in range(out.height):
        for x in range(out.width):
            r, gg, b, a = px[x, y]
            if a == 0: continue
            k = FRAME_SRC.get((r, gg, b))
            if k is None: raise RuntimeError("공용 테두리에 모르는 색 %r (%d, %d) — FRAME_SRC 를 고친다" % ((r, gg, b), x, y))
            px[x, y] = pal[k] + (a,)
    return out


def bg_of(g, style=BG_STYLE):
    t0 = TINT[g]
    im = Image.new("RGBA", (96, 96), t0 + (255,))
    if style == "tint":
        return im
    px = im.load()
    top, bot = _mix(t0, (255, 255, 255), GRAD_TOP), _mix(t0, FRAME_PAL[g][2], GRAD_BOT)
    for y in range(96):
        for x in range(96):
            t = max(0.0, min(1.0, (.85 * y + .15 * x - 3) / 89))
            px[x, y] = _mix(top, bot, t) + (255,)
    if style == "arc":
        P = GLOSS_ARC
        for y in range(96):
            for x in range(96):
                dx = (x - P["cx"]) / P["rx"]
                if dx * dx + ((y - P["cy"]) / P["ry"]) ** 2 >= 1: continue
                yb = P["cy"] + P["ry"] * (1 - dx * dx) ** .5                 # 이 줄에서 광택이 끝나는 y
                k = max(0.0, min(1.0, (y - 3) / max(1.0, yb - 3)))
                px[x, y] = _mix(px[x, y][:3], (255, 255, 255), P["a0"] + (P["a1"] - P["a0"]) * k) + (255,)
        for x, y in GLINT:
            px[x, y] = (255, 255, 255, 255)
    elif style == "diag":
        P = GLOSS_DIAG
        for y in range(96):
            for x in range(96):
                d = x + y
                if d < 2 * P["w"] + 8:
                    px[x, y] = _mix(px[x, y][:3], (255, 255, 255), P["a0"] + (P["a1"] - P["a0"]) * d / (2 * P["w"] + 8)) + (255,)
                elif 2 * P["w"] + 14 <= d < 2 * P["w"] + 20:
                    px[x, y] = _mix(px[x, y][:3], (255, 255, 255), .35) + (255,)
    elif style != "grad":
        raise RuntimeError("BG_STYLE 는 tint · grad · arc · diag 중 하나")
    return im


def webp_lossless(im):
    b = io.BytesIO()
    im.save(b, "WEBP", lossless=True, quality=100, method=6)
    return b.getvalue()


def ver(data):
    return hashlib.sha256(data).hexdigest()[:10]


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and open(path, "rb").read() == data:
        return False
    open(path, "wb").write(data)
    return True


def line_re(name):
    return re.compile(r'^const %s = (\{.*\});$' % name, re.M)


def apply(src, root, log=print):
    maps = {}
    for name in NAMES:
        m = line_re(name).search(src)
        maps[name] = json.loads(m.group(1)) if m else None
    for name in NAMES[:3]:
        if maps[name] is None: raise RuntimeError("game.html 에 %s 줄이 없다" % name)
    # 그릴 것: 자리(저장소 기준 경로) → 그림
    plan, changed = {}, 0
    for job, names in ICONS.items():
        for i, nm in enumerate(names):
            key, table = (PREFIX[job] + SLOTS[i], "SKILL_ICON_ART") if SLOTS[i] else (job, "SKILL_ICON_PASSIVE")
            if key not in maps[table]: raise RuntimeError("%s 에 %s 가 없다" % (table, key))
            rel = maps[table][key].split("?")[0]
            p = os.path.join(root, "tools", "newskillicon", "icons", JOB_CLASS[job], nm + "-96.png")
            im = Image.open(p); im.load()
            if im.size != (96, 96): raise RuntimeError("96 × 96 이 아니다: " + p)
            plan[(table, key)] = (rel, im.convert("RGBA"))
    for table in ("SKILL_ICON_ART", "SKILL_ICON_PASSIVE"):
        extra = [k for k in maps[table] if (table, k) not in plan]
        if extra: raise RuntimeError("%s 에 새 아이콘이 없는 칸 %s — ICONS 에 더한다" % (table, extra))
    for g in GRADES:
        plan[("SKILL_ICON_FRAME", g)] = ("assets/skill-icons/frame-%s.webp" % g, frame_of(root, g))
        plan[("SKILL_ICON_BG", g)] = ("assets/skill-icons/bg-%s.webp" % g, bg_of(g))
    out = {name: {} for name in NAMES}
    for name in NAMES[:3]:                       # 지금 줄의 차례 그대로
        for k in maps[name]:
            out[name][k] = None
    # 기술 이름 (manifest — game.html 의 JOBS · PASSIVES 에서 · 못 찾으면 빈칸)
    nm_sk = dict(re.findall(r'\{id:"(\w+)",[^{}]*?name:"([^"]+)"', src))
    i = src.find("const PASSIVES = {")
    nm_ps = dict(re.findall(r'^\s*(\w+):\s*\{n:"([^"]+)"', src[i:src.find("\n};", i)], re.M)) if i >= 0 else {}
    man = {"source": "tools/newskillicon", "quality": "lossless", "dimensions": "96x96", "bg": BG_STYLE,
           "skills": {}, "passives": {}, "frames": {}, "bgs": {}}
    sect = {"SKILL_ICON_ART": "skills", "SKILL_ICON_PASSIVE": "passives", "SKILL_ICON_FRAME": "frames", "SKILL_ICON_BG": "bgs"}
    for (table, key), (rel, im) in plan.items():
        data = webp_lossless(im)
        changed += write(os.path.join(root, rel), data)
        out[table][key] = "%s?v=%s" % (rel, ver(data))
        e = {"path": rel[len("assets/skill-icons/"):]}
        if table == "SKILL_ICON_ART": e["name"] = nm_sk.get(key, "")
        if table == "SKILL_ICON_PASSIVE": e["name"] = nm_ps.get(key, "")
        e.update({"bytes": len(data), "sha": ver(data)})
        man[sect[table]][key] = e
    for job, names in ICONS.items():                 # 원본 그림 (묶음 안 경로)
        for i, nm in enumerate(names):
            k = PREFIX[job] + SLOTS[i] if SLOTS[i] else job
            man["skills" if SLOTS[i] else "passives"][k]["src"] = "icons/%s/%s-96.png" % (JOB_CLASS[job], nm)
    changed += write(os.path.join(root, "assets", "skill-icons", "manifest.json"), (json.dumps(man, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    for name in NAMES:
        line = "const %s = %s;" % (name, json.dumps(out[name], ensure_ascii=False))
        m = line_re(name).search(src)
        if m:
            src = src[:m.start()] + line + src[m.end():]
        else:                                    # SKILL_ICON_BG — 테두리 줄 다음에
            f = line_re("SKILL_ICON_FRAME").search(src)
            src = src[:f.end()] + "\n" + line + src[f.end():]
    log("apply_skicon: 그림 %d장 (아이콘 80 · 테두리 6 · 바탕 6) + manifest.json — 새로 쓰거나 바뀐 파일 %d · 바탕 %s" % (len(plan), changed, BG_STYLE))
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"), os.path.dirname(os.path.abspath(path)))
    if crlf:
        src = src.replace("\n", "\r\n")
    if src != raw:
        open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
