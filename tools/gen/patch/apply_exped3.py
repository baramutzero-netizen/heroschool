"""원정을 모두 3구간으로 (1008) — 몇 번을 돌려도 같은 결과.

    python3 apply_exped3.py <game.html>

· DUNGEONS 의 secs 를 모두 3 으로 · 예전 구간 수는 depth(원정지 깊이)로 남긴다 (연습장 3 · 성터 4 · 종탑 5 · 균열 6 · 무덤 7)
· 난이도 — 구간마다 마물 레벨이 깊이만큼 가파르게 오른다 (마지막 보스 방은 예전과 같은 레벨 · dgSecLv).
  잡몹 배율(MOB_K)은 예전 완주율이 그대로 나오도록 시뮬레이션으로 다시 맞췄다 (구간 하나하나는 더 어렵다 · 균열만 종탑과 무덤 사이로 낮춤) —
  tools/gen/sim/exped_sim.py 로 바꾸기 전 · 뒤 빌드를 같은 설정(역할 팀 · 쐐기진 · 권장 레벨 +0/2/4/6 · 1500번)으로 돌려 비교
· 지구력 한계 · 의식 리타이어는 깊이 기준 그대로 — 예전에 몇 구간까지 버티던 팀은 그만큼에 해당하는 구간까지,
  리타이어 확률은 그 구간이 대신하는 예전 구간들의 확률을 겹쳐 굴린다
· 보상 — 완주 합계가 예전과 같도록 구간당 값을 키운다: 경험치(dgExpK — 구간마다 오르는 몫까지 맞춘다) ·
  자금 · 유물 확률 · 진로 평가 · 학생 명성 (dgK = 깊이 ÷ 3). 업보 · 컨디션 소모도 같은 배율 — 완주 합계가 예전과 같다
· 그뉵이용(5%) · 완주 명성 · 이계의 지도 배율은 그대로"""
import re, sys

# 시뮬레이션으로 다시 맞춘 잡몹 배율 (아래 MOB_NOTE 참고). 연습장(d1)은 원래 3구간이라 그대로
NEW_MOB_K = {"d1": 1.9, "d2": 1.03, "d3": .95, "d4": 1.7, "d5": 1.05}
MOB_NOTE = ("/* 원정지별 잡몹 배율 — 시뮬레이션으로 맞춘다.\n"
            "   1008 — 원정을 3구간으로 줄이며 다시 맞췄다: 역할을 갖춘 B급 3인(탱커 · 딜러 · 힐/지원, 쐐기진, 그 무렵 멘탈리티 DG_MENT, 유물 없음)이\n"
            "   권장 레벨 +0 · +2 · +4 · +6 일 때 완주율이 예전 길이(구간 4~7개)와 같도록 (성터 .97→1.03 · 종탑 .85→.95 · 무덤 .83→1.05).\n"
            "   균열은 예전부터 잡몹이 유난히 세서(권장 +2 팀 대비 체력 1.04배 · 공격 1.48배 — 무덤 잡몹은 0.63배 · 1.15배) 무덤보다도 완주가 낮았다 (권장 +2 에서 35%).\n"
            "   예전 완주율에 맞추면 2.0 이지만, 종탑과 무덤 사이에 오도록 1.7 로 낮췄다 (권장 +0 · +2 · +4 · +6 완주 약 34 · 66 · 82 · 85%).\n"
            "   연습장은 원래 3구간이라 그대로. (예전 메모 — B급 3인 기준 완주 95 / 90 / 85 / 80 / 75% 로 맞췄었다) */\n")

HELPERS = """/* 원정지 깊이 (1008) — 원정은 모두 3구간이고, depth 는 예전 구간 수(원정지 깊이)다.
   구간마다 마물 레벨이 깊이만큼 가파르게 오르고(마지막 보스 방은 예전과 같은 레벨), 지구력 한계 · 의식 리타이어도 깊이 기준.
   구간당 보상 · 업보 · 컨디션 소모는 완주 합계가 예전과 같도록 키운다 */
function dgDepth(dg){ return (dg && (dg.depth || dg.secs)) || 1; }
/* 구간당 보상 · 비용 배율 — 깊이 ÷ 구간 수 (자금 · 유물 확률 · 진로 평가 · 학생 명성 · 업보 · 컨디션 소모) */
function dgK(dg){ return dgDepth(dg) / Math.max(1, dg.secs); }
/* 경험치는 구간마다 (1 + 0.14 × 구간) 으로 오른다 — 그 몫까지 맞춰 완주 합계가 예전과 같게 */
const EXPED_EXP_RAMP = .14;
function expRampSum(n){ return n + EXPED_EXP_RAMP*n*(n+1)/2; }
function dgExpK(dg){ return expRampSum(dgDepth(dg)) / expRampSum(Math.max(1, dg.secs)); }
/* 구간 → 예전 구간 자리 (1 ~ 깊이). 마물 레벨 · 지구력 한계 · 의식 리타이어가 이 자리를 따른다 */
function dgSecPos(dg, sec){ const n = Math.max(1, dg.secs); return n <= 1 ? dgDepth(dg) : 1 + Math.round((sec-1)*(dgDepth(dg)-1)/(n-1)); }
function dgSecLv(dg, sec){ return dg.lv + dgSecPos(dg, sec) - 1; }
/* 유물 — 구간 승리마다 이 확률 */
function dgRelicP(dg){ return clamp((dg.relicP||.2) * dgK(dg), 0, 1); }
"""

RETIRE = """/* 지구력 한계 — 예전 깊이로 몇 구간까지 버티는지(3 + 지구력/12) 재고, 그 자리까지 닿는 구간 수로 바꾼다 (1008) */
function expedMaxSec(dg, avgStam){
  const cap = Math.round(3 + avgStam/12);
  let n = 1;
  for(let s = 2; s <= dg.secs; s++) if(dgSecPos(dg, s) <= cap) n = s;
  return n;
}
/* 의식 리타이어 — 이 구간이 대신하는 예전 구간들의 확률을 겹쳐 굴린다 (1008 — 깊이 기준이라 의지의 몫은 예전과 같다) */
function expedRetireP(dg, sec, will){
  const one = i=> clamp((.02 + i*.015) * (1 - will/120), 0, .35);
  let keep = 1;
  for(let i = dgSecPos(dg, sec); i < dgSecPos(dg, sec+1); i++) keep *= 1 - one(i);
  return 1 - keep;
}
"""


def mob_line():
    return "const MOB_K = {%s};\n" % ", ".join("%s:%s" % (k, ("%g" % v).replace("0.", ".", 1) if v < 1 else "%g" % v) for k, v in NEW_MOB_K.items())


EDITS = [
    # 던전 표 머리 — 설명
    ("const DUNGEONS = [\n",
     "/* 1008 — 원정은 모두 3구간. depth 는 예전 구간 수(원정지 깊이) — 아래 dgDepth 참고 */\nconst DUNGEONS = [\n"),
    # 그뉵이용 · 조우 레벨 — 깊이만큼 가파르게
    ('  const arr = [genMonsterOne(dg, "mon_muscle", dg.lv + (sec-1), MUSCLE_K[dg.id]!=null ? MUSCLE_K[dg.id] : 1)];\n',
     '  const arr = [genMonsterOne(dg, "mon_muscle", dgSecLv(dg, sec), MUSCLE_K[dg.id]!=null ? MUSCLE_K[dg.id] : 1)];\n'),
    ("  const lv = dg.lv + (sec-1);\n",
     "  const lv = dgSecLv(dg, sec);                                        // 1008 — 깊이만큼 가파르게 (마지막 구간은 예전 보스 레벨)\n"),
    # 원정 — 지구력 한계 · 경험치 · 리타이어
    ("    maxSec: clamp(Math.round(3 + avgStam/12), 1, dg.secs), sec:1, hpLeft:{},\n",
     "    maxSec: expedMaxSec(dg, avgStam), sec:1, hpLeft:{},\n"),
    ("  res.exp += E.dg.exp*(1+E.sec*.14)*EXPED_EXP_MUL * (muscle? MUSCLE_RWD : 1);\n",
     "  res.exp += E.dg.exp*(1+E.sec*EXPED_EXP_RAMP)*EXPED_EXP_MUL*dgExpK(E.dg) * (muscle? MUSCLE_RWD : 1);\n"),
    ("  const retire = clamp((.02 + E.sec*.015) * (1 - E.avgWill/120), 0, .35);\n",
     "  const retire = expedRetireP(E.dg, E.sec, E.avgWill);\n"),
    # 보상 · 비용
    ("    const per = clamp(dg.relicP||.2, 0, 1);\n",
     "    const per = dgRelicP(dg);\n"),
    ("      const g = ((cap-cur)*.13*(res.reached/dg.secs) + res.reached*.25) * EXPED_RWD_MUL;\n",
     "      const g = ((cap-cur)*.13*(res.reached/dg.secs) + res.reached*.25*dgK(dg)) * EXPED_RWD_MUL;\n"),
    ("      setCond(s, s.cond - EXPED_COND*Math.max(1, res.secs.length)); s.fame += Math.round(res.reached*2*EXPED_RWD_MUL); });\n",
     "      setCond(s, s.cond - EXPED_COND*dgK(dg)*Math.max(1, res.secs.length)); s.fame += Math.round(res.reached*2*EXPED_RWD_MUL*dgK(dg)); });\n"),
    ("    res.karma = (dg.karma||0) * res.secs.length * EXPED_RWD_MUL;\n",
     "    res.karma = (dg.karma||0) * res.secs.length * EXPED_RWD_MUL * dgK(dg);\n"),
    # 화면 수치
    ("function dgExp(d){ return Math.round(d.exp * EXPED_EXP_MUL); }\n",
     "function dgExp(d){ return Math.round(d.exp * EXPED_EXP_MUL * dgExpK(d)); }\n"),
    ("function dgKarma(d){ return (d.karma||0) * EXPED_RWD_MUL; }\n",
     "function dgKarma(d){ return Math.round((d.karma||0) * EXPED_RWD_MUL * dgK(d) * 10) / 10; }   // 구간당 (화면용 · 소수 한 자리)\n"),
    ("function dgGold(d){ return (EXPED_GOLD + d.tier*EXPED_GOLD_TIER) * (d.goldMul!=null ? d.goldMul : 1); }",
     "function dgGold(d){ return (EXPED_GOLD + d.tier*EXPED_GOLD_TIER) * (d.goldMul!=null ? d.goldMul : 1) * dgK(d); }"),
    (" · 유물 ${Math.round(d.relicP*100)}%${dgKarma(d)? ` · 업보 ${dgKarma(d).toFixed(1)}`:\"\"}</div>\n",
     " · 유물 ${Math.round(dgRelicP(d)*100)}%${dgKarma(d)? ` · 업보 ${dgKarma(d).toFixed(1)}`:\"\"}</div>\n"),
    ("          <div class=\"od\">유물 — 구간 승리마다 ${Math.round(d.relicP*100)}%</div>\n",
     "          <div class=\"od\">유물 — 구간 승리마다 ${Math.round(dgRelicP(d)*100)}%</div>\n"),
]

MARK = "function dgSecLv(dg, sec){"


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:100]))
    return src.replace(old, new)


def apply(src):
    if MARK not in src:
        for old, new in EDITS:
            src = sub1(src, old, new)
        # 던전 표 — secs 를 3 으로, 예전 값은 depth 로
        i = src.index("const DUNGEONS = [\n"); j = src.index("\n];\n", i)
        block = src[i:j]
        nb, n = re.subn(r"secs:(\d), ", lambda m: "secs:3, depth:%s, " % m.group(1), block)
        if n != 5:
            raise RuntimeError("던전 표 secs 가 다섯 곳이 아니다 (%d)" % n)
        src = src[:i] + nb + src[j:]
        # 도우미 — 던전 표 바로 뒤 · 지구력/리타이어 — 원정 단계 함수 앞
        k = src.index("\n];\n", src.index("const DUNGEONS = [\n")) + 4
        src = src[:k] + "\n" + HELPERS + src[k:]
        src = sub1(src, "function expedInit(dg, team, TM){\n", RETIRE + "function expedInit(dg, team, TM){\n")
    # 잡몹 배율 — 시뮬레이션 값 (다시 돌리면 이 값으로 맞춘다)
    src = re.sub(r"/\* 원정지별 잡몹 배율 — [\s\S]*?\*/\nconst MOB_K = \{[^}]*\};\n", lambda m: MOB_NOTE + mob_line(), src, count=1)
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
