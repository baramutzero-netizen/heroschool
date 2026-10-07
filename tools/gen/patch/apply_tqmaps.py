"""쿼터뷰 지도 11장을 필드마다 잇는다 (1007) — 몇 번을 돌려도 같은 결과. apply_tq.py · apply_tqcam.py 다음에 돌린다.

    python3 apply_tqmaps.py <game.html> [지도 폴더 — 주면 그림 내용으로 ?v= 를 새로 매긴다]

assets/battle-fields/quarter/ 의 지도 (모두 1536×1024 · 시내 대회와 같은 구도라 같은 자리에 놓는다)
  · 학원 연습장 원정 · 친선전(필드 dummy) — 지금 계절: spring · academy(여름) · fall · winter
  · 안개 낀 옛 성터 wraith · 무너진 종탑 gargoyle · 소금 바다의 균열 brine · 용사의 무덤 guardian
  · 시내 대회 city · 광역 대회 · 예선 리그 regional · 본선 · 5인 리그 final · 마왕 대항전 guardian
가로 화면에서만 쿼터뷰 (세로는 예전 필드 그림)."""
import hashlib, os, re, sys

MARK = "const TQ_MAPS = "

SRC = {"city": "city", "regional": "regional", "final": "final",
       "academy-spring": "spring", "academy-summer": "academy", "academy-fall": "fall", "academy-winter": "winter",
       "wraith": "wraith", "gargoyle": "gargoyle", "brine": "brine", "guardian": "guardian"}
# 클로즈업 가운데 — 지도 그림 픽셀 (바닥 문장 가운데 · 문장이 없으면 경기장 바닥 가운데)
MXY = {"city": (767, 463), "regional": (767, 469), "final": (767, 470),
       "academy-spring": (766, 454), "academy-summer": (766, 454), "academy-fall": (766, 454), "academy-winter": (766, 454),
       "wraith": (775, 505), "gargoyle": (790, 500), "brine": (780, 520), "guardian": (770, 500)}
VER = {"city": "249afb2b", "regional": "336705d6", "final": "ff1b06b7", "academy-spring": "03189471", "academy-summer": "15dd1f77",
       "academy-fall": "a7315cce", "academy-winter": "7cc2fab8", "wraith": "6bbc9907", "gargoyle": "bf0125cc", "brine": "830ae6e2", "guardian": "5d5101e1"}


def table_only(ver):
    rows = ",\n  ".join(f'"{k}":{{src:"{SRC[k]}.png?v={ver[k]}", mx:{MXY[k][0]}, my:{MXY[k][1]}}}' for k in SRC)
    return f"const TQ_MAPS = {{\n  {rows}\n}};\n"


def block(ver):
    return ("/* 1007 — 쿼터뷰 지도 (assets/battle-fields/quarter · 모두 1536×1024 · 시내 대회와 같은 구도라 TOURNAMENT_LAYOUT.map 자리에 놓는다).\n"
            "   mx · my — 지도 그림 안 클로즈업 가운데: 바닥 문장 가운데 · 문장이 없는 원정지(성터 · 종탑 · 균열)는 경기장 바닥 가운데.\n"
            "   map — 따로 둘 자리가 있을 때만 {x,y,w,h} (편집기 좌표). TOURNAMENT_REGIONAL_MAP 은 예전 광역 그림 자리라 쓰지 않는다 */\n"
            + table_only(ver) +
            "/* 필드 → 쿼터뷰 지도. 학원 연습장(dummy — 연습장 원정 · 친선전)은 지금 계절 · 예선 리그는 광역 대회 필드 · 마왕 대항전은 용사의 무덤.\n"
            "   계절 필드(봄 신인전 등)는 쿼터뷰가 아니다 */\n"
            "function tqMapKey(fk){\n"
            "  const k = fk===\"citytournament\" ? \"city\" : fk===\"areatournament\" ? \"regional\" : fk===\"demonking\" ? \"guardian\"\n"
            "          : fk===\"dummy\" ? \"academy-\" + ((typeof S!==\"undefined\" && S && PHASES[S.phase]) ? S.phase : \"spring\") : fk;\n"
            "  return TQ_MAPS[k] ? k : null;\n"
            "}\n")


TQ_MARK_LINE = re.compile(r"^const TQ_MARK = \{.*\};\n", re.M)

EDITS = [
    (" if(!['citytournament','areatournament'].includes(fk)||bfOrient()!=='landscape')return;\n",
     " const qk=tqMapKey(fk);if(!qk||bfOrient()!=='landscape')return;   // 1007 — 쿼터뷰 지도가 있는 필드면 모두 (TQ_MAPS)\n"),
    (" const L=fk==='areatournament'?{...TOURNAMENT_LAYOUT,map:TOURNAMENT_REGIONAL_MAP}:TOURNAMENT_LAYOUT,F=L.field;\n",
     " const L=TQ_MAPS[qk].map?{...TOURNAMENT_LAYOUT,map:TQ_MAPS[qk].map}:TOURNAMENT_LAYOUT,F=L.field;\n"),
    ("im.src=fk==='citytournament'?'assets/battle-fields/quarter/city.png':'assets/battle-fields/quarter/regional.png';",
     "im.src='assets/battle-fields/quarter/'+TQ_MAPS[qk].src;"),
    (" {const mk=TQ_MARK[fk];if(mk)stage._tqMark={x:L.map.x-F.x+mk.x*L.map.w/mk.iw,y:L.map.y-F.y+mk.y*L.map.h/mk.ih};}",
     " {const mk=TQ_MAPS[qk];stage._tqMark={x:L.map.x-F.x+mk.mx*L.map.w/1536,y:L.map.y-F.y+mk.my*L.map.h/1024};}"),
]


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:90]))
    return src.replace(old, new)


TABLE_RE = re.compile(r"const TQ_MAPS = \{\n.*?\n\};\n", re.S)


def apply(src, ver=VER):
    if MARK in src:                                            # 이미 넣었으면 표만 새로 (그림이 바뀌었을 때 ?v=)
        return TABLE_RE.sub(lambda m: table_only(ver), src, count=1)
    if len(TQ_MARK_LINE.findall(src)) != 1:
        raise RuntimeError("TQ_MARK 줄을 못 찾았다 — apply_tqcam.py 를 먼저 돌린다")
    src = TQ_MARK_LINE.sub(lambda m: block(ver), src, count=1)
    src = src.replace("   TQ_MARK — 지도 그림(iw × ih) 안의 문장 가운데 픽셀 (지역 대회 판은 문장이 없어 경기장 바닥 가운데).\n",
                      "   클로즈업 가운데는 TQ_MAPS 의 mx · my (아래).\n", 1)
    for old, new in EDITS:
        src = sub1(src, old, new)
    return src

if __name__ == "__main__":
    path = sys.argv[1]
    ver = dict(VER)
    if len(sys.argv) > 2:
        for k, f in SRC.items():
            ver[k] = hashlib.sha1(open(os.path.join(sys.argv[2], f + ".png"), "rb").read()).hexdigest()[:8]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"), ver)
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
