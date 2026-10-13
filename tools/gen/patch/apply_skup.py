"""스킬 강화 창 배치를 game.html 에 넣는다 (1013) — 몇 번을 돌려도 같은 결과.

    python3 tools/gen/patch/apply_skup.py game.html [tools/gen/patch/skup_layout.json]

배치 JSON 은 tools/skill_upgrade_lab.html 의 'JSON 저장'(skup_layout.json) 그대로 — {v:1, pc:{…}, mobile:{…}}.
game.html 의 `const SK_CHOICE_LAYOUT = /*SKUP_LAYOUT*/{…};` 한 줄만 바꾼다 (SKUP_LAYOUT 블록 · 스킬 강화 창 코드는 그대로).
표시 테두리(outline — {c 색, w 두께 0~3 그림 칸}) · 배경(bg — 두 화면 같이 · end 완료 화면 solid · grade · same · endSat 채도 남김 %): {on, a · b 띠 색, ink 글자 색 (#rrggbb), inkA 글자 진하기 0~1, w 띠 폭, tilt 기울기(도), speed 초당 px, gap 글 사이, size 12·24·36·48} — 없으면 기본값.
휘두르는 부채(1014) — swing 상자가 맞는 자리(+ r 맞을 때 각도 · 도) · swingFrom {x, y, r} 시작 자리(맞는 자리에서 옮긴 px · 각도) — 화면마다.
fan {flip 휘두를 때 좌우 뒤집기, c 테두리 색, w 두께 0~3 그림 칸} — 두 화면 같이. 없으면 기본값 (예전 JSON 도 받는다).
넓은 화면 창(pc.scene)의 fitH — 게임이 보는 세로가 이 값 이하면 창 전체를 높이 비율로 줄인다 (0 = 안 줄임 · 없으면 900).
학생 머리 옆 표시 셋(marks — thinking 전구 · before 긴장 · hit 충격 · 두 화면 같이)은 {s 크기, d 모든 직업 옮김 [x, y], at {직업 그림: [x, y]}} — 학생 그림 192 칸.
표시가 없는 예전 JSON 도 받는다 (기본값으로 채운다).
요소 이름 · 값 모양을 확인하고, 모르는 이름이나 숫자가 아닌 값이 있으면 멈춘다. 바꾼 뒤 hs.py build (또는 wrap.py · wrap_site.py)."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = {
    "pc": ["scene", "heading", "points", "slot1", "slot2", "slot3", "hero", "swing", "swingFrom", "reroll", "footer", "later", "rules",
           "sLabel", "sTitle", "sHero", "sInfo", "sDone"],
    "mobile": ["scene", "sceneEnd", "heading", "points", "slot1", "slot2", "slot3", "hero", "swing", "swingFrom", "reroll", "footer", "later", "rules",
               "sLabel", "sTitle", "sHero", "sInfo", "sDone"],
}
SWING_FROM = {"pc": {"x": 24, "y": -40, "r": 35}, "mobile": {"x": 12, "y": -20, "r": 35}}   # 게임 skChoiceSwingDef 와 같게
HIT_R = -60                                                                                   # 게임 SK_CHOICE_HIT_R 과 같게
FAN_DEF = {"flip": True, "c": "#3d2b1f", "w": 1}                                             # 게임 skChoiceFanDef 와 같게
BAND = {"heading", "footer", "sceneEnd"}
MARKS = ("before", "hit", "thinking")
MARK_S = {"before": 32, "hit": 32, "thinking": 28}      # 기본 너비 (그림 칸) — thinking 은 전구 28×27
ART_KEY = re.compile(r"^[a-z0-9][a-z0-9_-]{0,40}$")
LINE = re.compile(r"^const SK_CHOICE_LAYOUT = /\*SKUP_LAYOUT\*/.*$", re.M)


def num(v, what, nullable=False):
    if v is None and nullable:
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or abs(v) > 5000:
        raise SystemExit("apply_skup: 숫자가 아니다 — %s = %r" % (what, v))
    return round(float(v), 1) if float(v) != int(v) else int(v)


def pair(v, what, lo, hi):
    if not isinstance(v, (list, tuple)) or len(v) != 2:
        raise SystemExit("apply_skup: [x, y] 가 아니다 — %s = %r" % (what, v))
    out = [num(v[0], what + "[0]"), num(v[1], what + "[1]")]
    if not all(lo <= x <= hi for x in out):
        raise SystemExit("apply_skup: 범위 밖 — %s = %r" % (what, v))
    return out


def clean_marks(m):
    """학생 머리 옆 표시 — 없으면 기본값 (크기 32 · 옮김 없음)"""
    if m is None:
        m = {}
    if not isinstance(m, dict) or set(m) - set(MARKS):
        raise SystemExit("apply_skup: marks 는 before · hit · thinking 만 — %r" % (sorted(m) if isinstance(m, dict) else m))
    out = {}
    for k in MARKS:
        b = m.get(k) or {}
        if not isinstance(b, dict) or set(b) - {"s", "d", "at"}:
            raise SystemExit("apply_skup: marks.%s 는 s · d · at 만 — %r" % (k, b))
        s = num(b.get("s", MARK_S[k]), "marks.%s.s" % k)
        if not 4 <= s <= 192:
            raise SystemExit("apply_skup: marks.%s.s 크기가 이상하다 — %r" % (k, s))
        at = b.get("at") or {}
        if not isinstance(at, dict):
            raise SystemExit("apply_skup: marks.%s.at 이 이상하다 — %r" % (k, at))
        for a in at:
            if not ART_KEY.match(a):
                raise SystemExit("apply_skup: marks.%s.at 의 직업 그림 이름이 이상하다 — %r" % (k, a))
        out[k] = {"s": s, "d": pair(b.get("d", [0, 0]), "marks.%s.d" % k, -192, 192),
                  "at": {a: pair(at[a], "marks.%s.at.%s" % (k, a), -192, 384) for a in sorted(at)}}
    return out


BG_DEF = {"on": True, "a": "#c2e5ff", "b": "#c6faf6", "ink": "#283231", "inkA": 0.35, "w": 64, "tilt": 20, "speed": 30, "gap": 160, "size": 24,
          "end": "solid", "endSat": 50}
BG_NUM = {"inkA": (0, 1), "w": (16, 400), "tilt": (-60, 60), "speed": (0, 400), "gap": (0, 2000), "endSat": (0, 100)}
OL_DEF = {"c": "#3d2b1f", "w": 1}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def clean_bg(b):
    """배경 벨트 — 없으면 기본값 · 모르는 칸 · 이상한 값이면 멈춘다"""
    if b is None:
        b = {}
    if not isinstance(b, dict) or set(b) - set(BG_DEF):
        raise SystemExit("apply_skup: bg 는 %s 만 — %r" % (", ".join(BG_DEF), sorted(b) if isinstance(b, dict) else b))
    out = dict(BG_DEF)
    if "on" in b:
        if not isinstance(b["on"], bool):
            raise SystemExit("apply_skup: bg.on 은 true · false — %r" % b["on"])
        out["on"] = b["on"]
    for c in ("a", "b", "ink"):
        if c in b:
            if not isinstance(b[c], str) or not HEX.match(b[c]):
                raise SystemExit("apply_skup: bg.%s 색이 #rrggbb 가 아니다 — %r" % (c, b[c]))
            out[c] = b[c].lower()
    for c, (lo, hi) in BG_NUM.items():
        if c in b:
            v = num(b[c], "bg." + c)
            if c == "inkA":                                  # 진하기는 0.05 단위까지 (num 은 소수 한 자리)
                v = round(float(b[c]), 2)
            if not lo <= v <= hi:
                raise SystemExit("apply_skup: bg.%s 범위(%s~%s) 밖 — %r" % (c, lo, hi, v))
            out[c] = v
    if "size" in b:
        if b["size"] not in (12, 24, 36, 48):
            raise SystemExit("apply_skup: bg.size 는 12 · 24 · 36 · 48 — %r" % b["size"])
        out["size"] = b["size"]
    if "end" in b:
        if b["end"] not in ("solid", "grade", "same"):
            raise SystemExit("apply_skup: bg.end 는 solid · grade · same — %r" % b["end"])
        out["end"] = b["end"]
    return out


def clean_outline(o):
    """표시 셋 테두리 — {c 색, w 두께 0~3 (그림 칸)} · 없으면 기본값"""
    if o is None:
        o = {}
    if not isinstance(o, dict) or set(o) - {"c", "w"}:
        raise SystemExit("apply_skup: outline 은 c · w 만 — %r" % o)
    out = dict(OL_DEF)
    if "c" in o:
        if not isinstance(o["c"], str) or not HEX.match(o["c"]):
            raise SystemExit("apply_skup: outline.c 색이 #rrggbb 가 아니다 — %r" % o["c"])
        out["c"] = o["c"].lower()
    if "w" in o:
        if o["w"] not in (0, 1, 2, 3):
            raise SystemExit("apply_skup: outline.w 는 0 ~ 3 — %r" % o["w"])
        out["w"] = o["w"]
    return out


def angle(v, what):
    a = num(v, what)
    if not -360 <= a <= 360:
        raise SystemExit("apply_skup: %s 각도는 -360 ~ 360 — %r" % (what, a))
    return a


def clean_swing_from(b, mode):
    """휘두르기 시작 자리 — {x, y 맞는 자리에서 옮긴 px, r 각도} · 없으면 기본값"""
    if b is None:
        return dict(SWING_FROM[mode])
    if not isinstance(b, dict) or set(b) - {"x", "y", "r"}:
        raise SystemExit("apply_skup: %s.swingFrom 은 x · y · r 만 — %r" % (mode, b))
    out = dict(SWING_FROM[mode])
    for c in ("x", "y"):
        if c in b:
            v = num(b[c], "%s.swingFrom.%s" % (mode, c))
            if not -1000 <= v <= 1000:
                raise SystemExit("apply_skup: %s.swingFrom.%s 범위(-1000~1000) 밖 — %r" % (mode, c, v))
            out[c] = v
    if "r" in b:
        out["r"] = angle(b["r"], "%s.swingFrom.r" % mode)
    return out


def clean_fan(o):
    """부채 둘 테두리 · 휘두를 때 좌우 뒤집기 — 없으면 기본값"""
    if o is None:
        o = {}
    if not isinstance(o, dict) or set(o) - set(FAN_DEF):
        raise SystemExit("apply_skup: fan 은 flip · c · w 만 — %r" % o)
    out = dict(FAN_DEF)
    if "flip" in o:
        if not isinstance(o["flip"], bool):
            raise SystemExit("apply_skup: fan.flip 은 true · false — %r" % o["flip"])
        out["flip"] = o["flip"]
    if "c" in o:
        if not isinstance(o["c"], str) or not HEX.match(o["c"]):
            raise SystemExit("apply_skup: fan.c 색이 #rrggbb 가 아니다 — %r" % o["c"])
        out["c"] = o["c"].lower()
    if "w" in o:
        if o["w"] not in (0, 1, 2, 3):
            raise SystemExit("apply_skup: fan.w 는 0 ~ 3 — %r" % o["w"])
        out["w"] = o["w"]
    return out


def clean(layout):
    """확인하고 쓸 값만 남긴다 (모르는 요소 · 칸은 멈춘다)"""
    if not isinstance(layout, dict) or layout.get("v") != 1:
        raise SystemExit("apply_skup: v:1 인 배치 JSON 이 아니다")
    out = {"v": 1}
    for mode, keys in KEYS.items():
        src = layout.get(mode)
        if not isinstance(src, dict):
            raise SystemExit("apply_skup: %s 가 없다" % mode)
        extra = set(src) - set(keys)
        if extra:
            raise SystemExit("apply_skup: %s 에 모르는 요소 %s" % (mode, sorted(extra)))
        m = {}
        for k in keys:
            b = src.get(k)
            if k == "swingFrom":
                m[k] = clean_swing_from(b, mode)
                continue
            if not isinstance(b, dict):
                raise SystemExit("apply_skup: %s.%s 가 없다" % (mode, k))
            w = "%s.%s" % (mode, k)
            if k in BAND:
                m[k] = {"h": num(b.get("h"), w + ".h")}
            elif k == "scene":
                if mode == "mobile":
                    m[k] = {"h": num(b.get("h"), w + ".h")}
                else:
                    fit = num(b.get("fitH", 900), w + ".fitH")      # 세로가 이 값 이하면 창 전체를 높이 비율로 줄인다 (0 = 안 줄임 · 없으면 900)
                    if not 0 <= fit <= 4000:
                        raise SystemExit("apply_skup: %s.fitH 가 이상하다 — %r" % (w, fit))
                    m[k] = {"x": num(b.get("x", 0), w + ".x"), "y": num(b.get("y", 0), w + ".y"), "w": num(b.get("w"), w + ".w"), "h": num(b.get("h"), w + ".h"),
                            "fitH": fit}
            else:
                if b.get("ax") not in ("l", "c", "r") or b.get("ay") not in ("t", "b"):
                    raise SystemExit("apply_skup: %s 의 기준(ax · ay)이 이상하다 — %r %r" % (w, b.get("ax"), b.get("ay")))
                v = {"ax": b["ax"], "ay": b["ay"], "x": num(b.get("x"), w + ".x"), "y": num(b.get("y"), w + ".y"),
                     "w": num(b.get("w"), w + ".w", True), "h": num(b.get("h"), w + ".h", True)}
                if b["ax"] == "c" and v["w"] is None:
                    raise SystemExit("apply_skup: %s 는 가운데 기준인데 너비(w)가 없다" % w)
                if b.get("mw") is not None:
                    v["mw"] = num(b["mw"], w + ".mw")
                if k.startswith("slot"):
                    v["tail"] = b.get("tail") if b.get("tail") in ("l", "c", "r") else {"slot1": "r", "slot2": "c", "slot3": "l"}[k]
                if k == "swing":
                    v["r"] = angle(b.get("r", HIT_R), w + ".r")
                m[k] = v
        out[mode] = m
    out["marks"] = clean_marks(layout.get("marks"))
    out["bg"] = clean_bg(layout.get("bg"))
    out["outline"] = clean_outline(layout.get("outline"))
    out["fan"] = clean_fan(layout.get("fan"))
    return out


def apply(src, layout):
    line = "const SK_CHOICE_LAYOUT = /*SKUP_LAYOUT*/" + json.dumps(clean(layout), ensure_ascii=False, separators=(",", ":")) + ";"
    new, n = LINE.subn(lambda _: line, src, count=1)
    if n != 1:
        raise SystemExit("apply_skup: game.html 에 SK_CHOICE_LAYOUT 줄이 없다 (SKUP_LAYOUT 블록)")
    return new


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    lay = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "skup_layout.json")
    raw = open(path, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    src = raw.replace("\r\n", "\n")
    out = apply(src, json.load(open(lay, encoding="utf-8")))
    if out == src:
        print("apply_skup: 그대로 (같은 배치)")
        return
    open(path, "wb").write((out.replace("\n", "\r\n") if crlf else out).encode("utf-8"))
    print("apply_skup: 배치를 넣었다 —", os.path.basename(lay), "→", path, "crlf" if crlf else "lf")


if __name__ == "__main__":
    main()
