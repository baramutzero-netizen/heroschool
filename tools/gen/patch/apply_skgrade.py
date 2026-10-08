"""스킬 등급표 (1008) — 스킬 수치를 등급 · 레벨로 정한다. 몇 번을 돌려도 같은 결과.
apply_exped3 뒤에 돌린다 (원정 잡몹 배율 MOB_K 를 이 스크립트가 다시 쓴다).

    python3 apply_skgrade.py <game.html>

· 등급 6단계 — D · C · B · A · S · EX (S 를 새로 넣었다. 예전 5단계의 EX 는 그대로 EX)
· 수치는 등급 · 레벨만 보고 정한다 — 같은 등급 · 레벨이면 누가 가진 스킬이든 같은 수치 (학생 · 졸업생 · 리그 · 적 · 마왕)
    효과량    (레벨−1) × D 12 · C 16 · B 20 · A 25 · S 30 · EX 40 %          (SK_POW_LV)
    출현 확률 (레벨−1) × D 7 · C 10 · B 13 · A 16 · S 19 · EX 25 % — 스킬 1 · 2 만 (SK_PROC_LV)
    지속 시간 B Lv.5 +1 · A Lv.3 +1 · S Lv.3 +1 / Lv.5 +2 · EX Lv.3 +2 / Lv.5 +3 — 지속형 스킬만, noDur 제외 (SK_DUR_LV)
· 강화 한 번 = 레벨 +1, 진화 강화 등급 +1 · 각성 강화 등급 +2 (확률은 그대로). 등급이 오르면 지난 레벨 몫도 새 등급으로 다시 계산
  — 3지선다는 이제 "어느 스킬 · 어떤 강화" 만 고른다 (효과량 · 출현 · 지속 중 하나를 고르던 것은 없앴다).
  EX 위로는 등급이 없어서, 제안을 만들 때 실제로 오르는 칸으로 깎는다 (EX 의 진화 · 각성 → 단순, S 의 각성 → 진화)
· 적도 같은 표 — autoSkMod 는 강화 횟수 · 등급만 정하고(난수 쓰는 순서는 예전과 같다), 마왕은 Lv.5 EX
· 옛 기록 — 저장(S.skgV < 2)은 boot 에서 EX(4) → EX(5) 로 한 번 옮긴다 (학생 · 졸업생 · 보관고 · 마왕전 명단 등 skMod · sm · mod 전부).
  리그 기록은 팀 · 마왕전 기록의 v 가 2 보다 작으면 받을 때 옮긴다 (서버는 고치지 않는다). 보낼 때는 등급 · 강화 횟수만 (v 2)
  받는 쪽도 등급 · 강화 횟수만 믿는다 — 예전처럼 남이 올린 효과량 숫자를 그대로 쓰지 않는다
· 전투 수치가 바뀌므로 RULES_VER 7
· 보관고 처분 가격 — S 1250 G (A 950 과 EX 1600 사이) · 졸업 선물은 강화 횟수 → 등급 순으로 고른다
· 원정 — 마물도 등급표를 따라 세져서 잡몹 배율을 조금 낮춘다 (MOB_K_SKG, 시뮬레이션 값)"""
import re, sys

MARK = "const SK_POW_LV  = ["

# 원정 잡몹 배율 — 마물 스킬이 등급표로 세진 만큼 (시뮬레이션: tools/gen/sim/exped_sim.py · sk "auto")
MOB_K_SKG = {"d2": 1.02, "d3": .94, "d4": 1.67, "d5": 1.01}   # 성터 1.03 · 종탑 .95 · 균열 1.7 · 무덤 1.05 에서 (연습장 1.9 그대로)
# 맞춘 법: 학생 스킬은 새 등급표 + 임의 강화 방식, 마물 스킬만 예전(효과량 +12%/강화) 인 판의 완주율(권장 +0 · +2 · +4, n 8000)에
#          마물 스킬도 등급표로 바꾼 판이 같아지는 배율 — 바꾸기 전 d5 +0 64.7% → 조정 뒤 67.8% (목표 67.9%)


def sub1(src, old, new, n=1):
    c = src.count(old)
    if c != n:
        raise RuntimeError("자리를 못 찾았다 (%d/%d): %s" % (c, n, old[:120]))
    return src.replace(old, new)


CORE_OLD = """/* ---------- 스킬 성장 ---------- */
const SK_GRADE = ["D","C","B","A","EX"];   // 스킬 등급 — 표시용, 최고는 EX
const SK_UP  = {pow:.12, proc:.15, dur:0};    // 단순 — 지속 시간은 제안되지 않는다
const SK_EVO = {pow:.24, proc:.30, dur:1};    // 진화 — 등급 +1
const SK_AWK = {pow:.48, proc:.50, dur:2};    // 각성 — 등급 +2
const SK_TIER   = [SK_UP, SK_EVO, SK_AWK];
const SK_TIER_N = ["단순 강화","진화 강화","각성 강화"];
const SK_TIER_C = ["var(--text)","var(--brass)","var(--ex)"];
const SK_LV_MAX = 5;                          // 스킬 최대 레벨 — 강화는 4회까지
"""
CORE_NEW = """/* ---------- 스킬 성장 ----------
   1008 — 수치는 등급 · 레벨로 정해진다. 같은 등급 · 레벨이면 누가 가진 스킬이든 같은 수치 (학생 · 졸업생 · 리그 · 적 · 마왕).
   강화 한 번 = 레벨 +1, 진화 강화는 등급 +1 · 각성 강화는 등급 +2. 등급이 오르면 지난 레벨 몫도 새 등급으로 다시 계산된다.
   등급은 6단계 — S 를 새로 넣었다 (예전 5단계의 EX 는 그대로 EX: 저장 · 리그 기록은 skModOld2New 로 옮긴다) */
const SK_GRADE = ["D","C","B","A","S","EX"];
const SK_G_MAX = SK_GRADE.length - 1;                 // 5 = EX
const SK_POW_LV  = [.12, .16, .20, .25, .30, .40];   // 레벨당 효과량 — Lv.n 이면 (n−1)배 (D Lv.5 +48% … EX Lv.5 +160%)
const SK_PROC_LV = [.07, .10, .13, .16, .19, .25];   // 레벨당 출현 확률 — 스킬(1 · 2)만 (D Lv.5 +28% … EX Lv.5 +100%)
/* 지속 시간 — 지속 시간이 있는 스킬만 (도발처럼 noDur 이면 빼고) · [등급][레벨−1]
   새로 키우면 EX 는 강화 3번째(Lv.4)부터 나온다 — Lv.3 EX 는 예전 기록(각성 2번)에서만 나온다 */
const SK_DUR_LV = [
  [0,0,0,0,0],   // D
  [0,0,0,0,0],   // C
  [0,0,0,0,1],   // B  — Lv.5 +1
  [0,0,1,1,1],   // A  — Lv.3 부터 +1
  [0,0,1,1,2],   // S  — Lv.3 +1 · Lv.5 +2
  [0,0,2,2,3]];  // EX — Lv.3 +2 · Lv.5 +3
const SK_TIER_N = ["단순 강화","진화 강화","각성 강화"];
const SK_TIER_C = ["var(--text)","var(--brass)","var(--ex)"];
const SK_LV_MAX = 5;                          // 스킬 최대 레벨 — 강화는 4회까지
"""

EDITS = [
    (CORE_OLD, CORE_NEW),
    ("  return o.skMod[id] || (o.skMod[id] = {pow:0, proc:0, dur:0, grade:0, up:0});\n",
     "  return o.skMod[id] || (o.skMod[id] = {grade:0, up:0});\n"),
    ("    const m = modOf(st, pick(open));\n    m.pow += .12; m.up++;\n    if(RNG() < .16) m.grade = Math.min(4, m.grade+1);\n",
     "    const m = modOf(st, pick(open));\n"
     "    m.up++;                                                   // 수치는 등급표에서 (1008 — 예전엔 강화마다 효과량 +12% 만)\n"
     "    if(RNG() < .16) m.grade = Math.min(SK_G_MAX, m.grade+1);\n"),
    ("""function skGrade(o, id){ return SK_GRADE[clamp(((o.skMod&&o.skMod[id])||{}).grade||0, 0, 4)]; }
function skLevel(o, id){ return 1 + (((o.skMod&&o.skMod[id])||{}).up||0); }
function skPow(o, sk){ return sk.power * (1 + (modOf(o,sk.id).pow||0)); }
function skDur(o, sk){ return (sk.dur||0) + (modOf(o,sk.id).dur||0); }
function skProc(o, sk, genius){
  return clamp(sk.proc * (1 + (modOf(o,sk.id).proc||0)) * (1 + MR("proc", genius)), 0, .85);
}
""", """function skG(o, id){ return clamp(((((o && o.skMod) || {})[id]) || {}).grade|0, 0, SK_G_MAX); }
function skUp(o, id){ return clamp(((((o && o.skMod) || {})[id]) || {}).up|0, 0, SK_LV_MAX-1); }   // 강화 횟수 = 레벨 − 1
function skGrade(o, id){ return SK_GRADE[skG(o, id)]; }
function skLevel(o, id){ return 1 + skUp(o, id); }
/* 등급 g · 강화 횟수 up 의 수치 — sk 는 스킬 정의 (패시브는 null: 효과량만) */
function skVal(g, up, sk){
  g = clamp(g|0, 0, SK_G_MAX); up = clamp(up|0, 0, SK_LV_MAX-1);
  return {pow: up * SK_POW_LV[g],
          proc: (sk && !sk.kind) ? up * SK_PROC_LV[g] : 0,
          dur: (sk && (sk.dur||0) > 0 && !sk.noDur) ? SK_DUR_LV[g][up] : 0};
}
function skValOf(o, sk){ return skVal(skG(o, sk.id), skUp(o, sk.id), sk); }
function skModVal(m, sk){ return skVal(m && m.grade, m && m.up, sk); }   // 기록 하나(보관고 mod 등)
function skPow(o, sk){ return sk.power * (1 + skValOf(o, sk).pow); }
function skDur(o, sk){ return (sk.dur||0) + skValOf(o, sk).dur; }
function skProc(o, sk, genius){
  return clamp(sk.proc * (1 + skValOf(o, sk).proc) * (1 + MR("proc", genius)), 0, .85);
}
function passiveK(o){ return 1 + skVal(skG(o, "passive"), skUp(o, "passive"), null).pow; }
/* 예전 5단계(D·C·B·A·EX) 기록 → 6단계: EX(4) 를 EX(5) 로. 옛 기록에는 S 가 없다 */
const SKG_VER  = 2;   // 저장 판번호 (S.skgV)
const SKG_PACK = 2;   // 리그 기록 판번호 (팀 · 마왕전 기록의 v) — 2 부터 새 등급
function skModOld2New(sm){
  if(sm && typeof sm === "object") Object.keys(sm).forEach(id=>{ const m = sm[id]; if(m && typeof m === "object" && (m.grade|0) >= 4) m.grade = SK_G_MAX; });
  return sm;
}
/* 저장 안의 스킬 기록 전부 — skMod(학생 · 졸업생 · 적 명단) · sm(리그 · 마왕전 명단) · mod(보관고 · 졸업 선물) */
function skgMigrate(o, depth){
  if(!o || typeof o !== "object" || depth > 14) return;
  if(Array.isArray(o)){ o.forEach(x=> skgMigrate(x, depth+1)); return; }
  Object.keys(o).forEach(k=>{
    const v = o[k];
    if(!v || typeof v !== "object") return;
    if(k === "skMod" || k === "sm") skModOld2New(v);
    else if(k === "mod" && !Array.isArray(v) && typeof v.up === "number"){ if((v.grade|0) >= 4) v.grade = SK_G_MAX; }
    else skgMigrate(v, depth+1);
  });
}
/* 리그로 보내는 스킬 기록 — 등급 · 강화 횟수만 (수치는 받는 쪽이 등급표로 계산한다) */
function skModPack(sm){
  const out = {};
  Object.keys(sm||{}).forEach(id=>{ const m = sm[id];
    if(m && typeof m === "object") out[id] = {grade:clamp(m.grade|0, 0, SK_G_MAX), up:clamp(m.up|0, 0, SK_LV_MAX-1)}; });
  return out;
}
/* 받는 쪽 — 남이 올린 값이라 등급 · 강화 횟수만 믿는다. 예전 판(old) 기록은 EX(4) → EX(5) */
function skModSane(sm, old){
  const out = {};
  if(!sm || typeof sm !== "object" || Array.isArray(sm)) return out;
  Object.keys(sm).slice(0, 8).forEach(id=>{
    const m = sm[id]; if(!m || typeof m !== "object") return;
    let g = clamp(m.grade|0, 0, SK_G_MAX);
    if(old && g >= 4) g = SK_G_MAX;
    out[String(id).slice(0, 24)] = {grade:g, up:clamp(m.up|0, 0, SK_LV_MAX-1)};
  });
  return out;
}
"""),
    ("  const k = 1 + (((o.skMod&&o.skMod.passive)||{}).pow||0);\n", "  const k = passiveK(o);\n"),
    # 졸업 기록 · 선물
    ("      ment:Object.assign({}, st.ment), skMod:JSON.parse(JSON.stringify(st.skMod||{})),\n",
     "      ment:Object.assign({}, st.ment), skMod:skModPack(st.skMod),\n"),
    ("    abil.sort((a,b)=> (b.m.up||0)-(a.m.up||0) || RNG()-.5);\n",
     "    abil.sort((a,b)=> (b.m.up|0)-(a.m.up|0) || (b.m.grade|0)-(a.m.grade|0) || RNG()-.5);   // 강화 횟수 → 등급 순 (1008)\n"),
    ("      skillId: bestA.id, mod: Object.assign({}, bestA.m), from: dn(st), year: S.year});\n",
     "      skillId: bestA.id, mod: {grade:bestA.m.grade|0, up:bestA.m.up|0}, from: dn(st), year: S.year});\n"),
    # 학생 상세 — 패시브 배율
    ("        const g = skGrade(s,\"passive\"), k = 1+((s.skMod&&s.skMod.passive||{}).pow||0);\n",
     "        const g = skGrade(s,\"passive\"), k = passiveK(s);\n"),
    # 리그 — 보내기 · 받기
    ("          sm:g.skMod||{},\n", "          sm:skModPack(g.skMod),\n"),
    ("          t:gs.map(leaguePackUnit), ts:Date.now(), v:1,\n", "          t:gs.map(leaguePackUnit), ts:Date.now(), v:SKG_PACK,\n"),
    ("function leagueSaneUnit(u, tid, ui){\n", "function leagueSaneUnit(u, tid, ui, old){\n"),
    ("            ment:m, skMod:(u.sm && typeof u.sm===\"object\")? u.sm : {},\n",
     "            ment:m, skMod:skModSane(u.sm, old),   // 1008 — 등급 · 강화 횟수만 (예전 판 기록은 EX 4 → 5)\n"),
    ("    return {acad:L5_NPC_ACAD[i % L5_NPC_ACAD.length], form, t:t.concat(left).slice(0, L5_TEAM), ts:0, v:1, mi:8,\n",
     "    return {acad:L5_NPC_ACAD[i % L5_NPC_ACAD.length], form, t:t.concat(left).slice(0, L5_TEAM), ts:0, v:SKG_PACK, mi:8,\n"),
    ("function demonSaneUnit(u, tid, i){ return (u && JOBS[u.j] && !JOBS[u.j].mon) ? leagueSaneUnit(u, tid, i) : null; }\n",
     "function demonSaneUnit(u, tid, i, old){ return (u && JOBS[u.j] && !JOBS[u.j].mon) ? leagueSaneUnit(u, tid, i, old) : null; }\n"),
    ("  const units = (Array.isArray(d.t) ? d.t : []).slice(0,5).map((u,i)=> demonSaneUnit(u, tid+\"_dm\", i)).filter(Boolean);\n",
     "  const units = (Array.isArray(d.t) ? d.t : []).slice(0,5).map((u,i)=> demonSaneUnit(u, tid+\"_dm\", i, (d.v|0) < SKG_PACK)).filter(Boolean);\n"),
    ("          best:D.best|0, t:D.comp.slice(0,5), ts:D.bestAt||Date.now(), n:D.n|0};\n",
     "          best:D.best|0, t:D.comp.slice(0,5), ts:D.bestAt||Date.now(), n:D.n|0, v:SKG_PACK};\n"),
    # 마왕
    ("const DEMON_SK = {pow:1.44, proc:0, dur:0, grade:4, up:4};   // Lv.5 · EX — 진화 강화 2회 + 각성 강화 2회 (효과량)\n",
     "const DEMON_SK = {grade:5, up:4};   // Lv.5 · EX — 등급표 그대로 (1008 — 효과량 +160% · 스킬 출현 +100% · 지속 +3턴. 예전엔 효과량 +144% 만)\n"),
    # 보관고 · 전수
    ("  const g = SK_GRADE[clamp(gradeIdx,0,4)];\n", "  const g = SK_GRADE[clamp(gradeIdx,0,SK_G_MAX)];\n"),
    ("  const newG = clamp((e.mod && e.mod.grade)||0, 0, 4), newUp = (e.mod && e.mod.up)||0;\n",
     "  const newG = clamp((e.mod && e.mod.grade)|0, 0, SK_G_MAX), newUp = clamp((e.mod && e.mod.up)|0, 0, SK_LV_MAX-1);\n"),
    ("    const cg = skGrade(st,\"passive\"), ck = 1+((st.skMod&&st.skMod.passive||{}).pow||0);\n    const nk = 1+((e.mod&&e.mod.pow)||0);\n",
     "    const cg = skGrade(st,\"passive\"), ck = passiveK(st);\n    const nk = 1 + skModVal(e.mod, null).pow;\n"),
    ("""function skillModText(m){
  const t=[];
  if(m.pow) t.push(`효과량 +${Math.round(m.pow*100)}%`);
  if(m.proc) t.push(`출현 +${Math.round(m.proc*100)}%`);
  if(m.dur) t.push(`지속 +${m.dur}턴`);
  return t.length? t.join(" · ") : "강화 없음";
}
""", """/* 보관고 기록 하나의 수치 — 등급 · 레벨로 (1008) */
function skillModText(e){
  const sk = (e && e.cat !== "passive") ? ((JOBS[e.job]||{}).skills||[]).find(x=> x.id === e.skillId) : null;
  const v = skModVal(e && e.mod, sk), t = [];
  if(v.pow) t.push(`효과량 +${Math.round(v.pow*100)}%`);
  if(v.proc) t.push(`출현 +${Math.round(v.proc*100)}%`);
  if(v.dur) t.push(`지속 +${v.dur}턴`);
  return t.length? t.join(" · ") : "강화 없음";
}
"""),
    ("  const g  = x => clamp((x.e.mod&&x.e.mod.grade)||0, 0, 4);\n  const lv = x => 1 + ((x.e.mod&&x.e.mod.up)||0);\n",
     "  const g  = x => clamp((x.e.mod&&x.e.mod.grade)|0, 0, SK_G_MAX);\n  const lv = x => 1 + clamp((x.e.mod&&x.e.mod.up)|0, 0, SK_LV_MAX-1);\n"),
    ("      const g = SK_GRADE[clamp(e.mod.grade||0,0,4)];\n", "      const g = SK_GRADE[clamp(e.mod.grade|0,0,SK_G_MAX)];\n"),
    ("(${SK_GRADE[clamp((e.mod.grade||0),0,4)]}급 · Lv.${1+(e.mod.up||0)})",
     "(${SK_GRADE[clamp(e.mod.grade|0,0,SK_G_MAX)]}급 · Lv.${1+clamp(e.mod.up|0,0,SK_LV_MAX-1)})"),
    ("""function skillPrice(e){
  const g = clamp((e.mod && e.mod.grade)||0, 0, 4);
  const up = (e.mod && e.mod.up)||0;
  return Math.round(([200,340,560,950,1600][g]) * (1 + up*0.30));
}
""", """function skillPrice(e){
  const g = clamp((e.mod && e.mod.grade)|0, 0, SK_G_MAX);
  const up = clamp((e.mod && e.mod.up)|0, 0, SK_LV_MAX-1);
  return Math.round(([200,340,560,950,1250,1600][g]) * (1 + up*0.30));   // 1008 — S 1250 을 A 와 EX 사이에
}
"""),
    # 판번호
    ("const RULES_VER = 6;   // 6 (1003): ",
     "const RULES_VER = 7;   // 7 (1008): 스킬 수치를 등급 · 레벨 표로 (등급 6단계 D·C·B·A·S·EX — 효과량 · 출현 확률 · 지속 시간, 적 · 마왕도 같은 표) · 6 (1003): "),
    # 새 게임 · 옛 저장
    ("facil:{expand:0,gym:0,hall:0,chapel:0,infirm:0,library:0,arena:0,counsel:0}, facilV:FACIL_VER, shopUnlock:0,",
     "facil:{expand:0,gym:0,hall:0,chapel:0,infirm:0,library:0,arena:0,counsel:0}, facilV:FACIL_VER, skgV:SKG_VER, shopUnlock:0,"),
    ("    S.potV = POT_VER;\n  }\n",
     "    S.potV = POT_VER;\n  }\n"
     "  /* 스킬 등급 6단계 (1008) — 예전 EX(4) 를 EX(5) 로 (학생 · 신입 예정자 · 졸업생 · 보관고 · 마왕전 · 리그 명단 모두) */\n"
     "  if((S.skgV|0) < SKG_VER){\n"
     "    skgMigrate(S, 0);\n"
     "    S.skgV = SKG_VER;\n"
     "  }\n"),
    # CSS — 강화 창의 등급표
    (".dmsk-t{color:var(--ex);font-size:12px}.dmsk-d{color:var(--muted);font-size:12.5px}\n",
     ".dmsk-t{color:var(--ex);font-size:12px}.dmsk-d{color:var(--muted);font-size:12.5px}\n"
     "/* 스킬 강화 창 — 등급표 (1008) */\n"
     ".skgd{margin-top:8px;font-size:12px;color:var(--muted)}\n"
     ".skgd summary{cursor:pointer;color:var(--text);font-size:12.5px}\n"
     ".skgd table{border-collapse:collapse;margin-top:6px;width:100%;max-width:440px}\n"
     ".skgd th,.skgd td{padding:3px 4px;text-align:center;border-bottom:1px solid var(--line-soft);font-variant-numeric:tabular-nums;font-weight:400}\n"
     ".skgd th{font-weight:700}.skgd td:first-child{text-align:left;white-space:nowrap}\n"
     ".skgd .skgd-dur{margin-top:5px;line-height:1.5}\n"
     ".skopt-v{font-size:12.5px;color:var(--text)}.skopt-v b{color:var(--ok);font-weight:700}\n"),
]

# 여러 곳 — 몇 군데인지 정해 두고 바꾼다
MULTI = [
    ("clamp(g,0,4)", "clamp(g,0,SK_G_MAX)", 6),                           # 전수 미리보기 — 패시브 칸
    ("SK_GRADE[4]", "SK_GRADE[SK_G_MAX]", 2),                             # 마왕 스킬 표시 (Lv.5 EX)
    ("skillModText(e.mod)", "skillModText(e)", 2),                        # 보관고 · 전수
    ("const units = t.map((u, ui)=> leagueSaneUnit(u, tid, ui));",       # 3인 · 5인 리그 팀 기록
     "const units = t.map((u, ui)=> leagueSaneUnit(u, tid, ui, (e.v|0) < SKG_PACK));", 2),
    ("<span class=\"price\">Lv.${1+(e.mod.up||0)}</span>",                # 보관고 목록
     "<span class=\"price\">Lv.${1+clamp(e.mod.up|0,0,SK_LV_MAX-1)}</span>", 1),
]

SKUP_START = "/* ============================================================\n   스킬 강화 — 레벨 2당 1포인트, 3지선다\n"
SKUP_END = "let SPR_BTSCROLL = 0;"
SKUP_FUNCS = ['evoChance', 'evoRoll', 'optId', 'skMaxed', 'skUpPool', 'genSkillOptions', 'evLv', 'skillOptText', 'applySkillUp',
              'autoSpendSp', 'hydrateOpt', 'spReady', 'spTotal', 'autoSkillUpAll', 'autoSkillUpConfirm', 'skillUpModal']
SKUP_NEW = r'''/* ============================================================
   스킬 강화 — 레벨 2당 1포인트, 3지선다
   1008 — 수치는 등급 · 레벨로 정해진다 (SK_POW_LV · SK_PROC_LV · SK_DUR_LV). 제안은 "어느 스킬 · 어떤 강화" 만 고른다:
   강화하면 레벨 +1, 진화 강화는 등급 +1 · 각성 강화는 등급 +2 (EX 위로는 없다 — 실제로 오르는 칸으로 깎는다)
   ============================================================ */
function evoChance(st){
  /* 천재성과 잠재력의 평균만 본다 */
  const m = ((st.ment.genius||0) + (st.ment.pot||0)) / 2;
  return clamp(.10 + m/100*.5, .10, .62);
}
/* 0 단순 · 1 진화 · 2 각성 — 진화에 성공하면 같은 확률로 한 번 더 굴린다 */
function evoRoll(st){
  const p = evoChance(st);
  if(RNG() >= p) return 0;
  return RNG() < p ? 2 : 1;
}
function optId(t){ return t.kind==="passive" ? "passive" : t.sk.id; }
function skMaxed(st, t){ return skLevel(st, optId(t)) >= SK_LV_MAX; }
/* 아직 더 올릴 수 있는 강화 대상 */
function skUpPool(st){
  const list = skillsOf(st).map(sk=>({kind:"skill", sk}));
  const P = passiveOf(passiveJobOf(st));
  if(P) list.push({kind:"passive", name:P.n, id:"passive", desc:P.d});
  return list.filter(t=> !skMaxed(st, t));
}
/* 실제로 오르는 등급 칸 — EX 에서 뜬 진화 · 각성은 단순 강화, S 에서 뜬 각성은 진화 강화가 된다 */
function evCap(st, id, ev){ return Math.max(0, Math.min(ev|0, SK_G_MAX - skG(st, id))); }
function genSkillOptions(st){
  const pool = shuffle(skUpPool(st));
  if(!pool.length) return [];
  const out = [];
  for(let i=0;i<3;i++){
    const t = pool[i % pool.length];
    out.push({t, ev: evCap(st, optId(t), evoRoll(st))});
  }
  return out;
}
function evLv(o){ return o.ev != null ? clamp(o.ev|0,0,2) : (o.evo?1:0); }
/* 강화 전 · 후 — 레벨 · 등급 · 수치 */
function skUpDiff(st, o){
  const id = optId(o.t), sk = o.t.kind==="passive" ? null : o.t.sk;
  const g0 = skG(st, id), u0 = skUp(st, id), ev = evCap(st, id, evLv(o));
  const g1 = Math.min(SK_G_MAX, g0 + ev), u1 = Math.min(SK_LV_MAX-1, u0 + 1);
  return {id, sk, ev, g0, g1, lv0:u0+1, lv1:u1+1, a:skVal(g0, u0, sk), b:skVal(g1, u1, sk)};
}
function skUpLines(d){
  const pc = v=> Math.round(v*100);
  const out = [`효과량 +${pc(d.a.pow)}% → <b>+${pc(d.b.pow)}%</b>`];
  if(d.sk && !d.sk.kind) out.push(`출현 확률 +${pc(d.a.proc)}% → <b>+${pc(d.b.proc)}%</b>`);
  if(d.b.dur !== d.a.dur) out.push(`지속 시간 +${d.a.dur} → <b>+${d.b.dur}턴</b>`);
  return out;
}
/* 지금 수치 한 줄 — 기록 · 임의 강화 결과용 */
function skillOptText(st, o){
  const id = optId(o.t), sk = o.t.kind==="passive" ? null : o.t.sk;
  const v = skVal(skG(st, id), skUp(st, id), sk), t = [`효과량 +${Math.round(v.pow*100)}%`];
  if(sk && !sk.kind) t.push(`출현 +${Math.round(v.proc*100)}%`);
  if(v.dur) t.push(`지속 +${v.dur}턴`);
  return t.join(" · ");
}
/* 등급표 — 강화 창에서 펼쳐 본다 */
function skGradeTable(){
  const head = SK_GRADE.map(g=>`<th style="color:${GRADE_COLOR[g]}">${g}</th>`).join("");
  const row = (n, arr)=> `<tr><td>${n}</td>${arr.map(v=>`<td>${Math.round(v*100)}%</td>`).join("")}</tr>`;
  const dur = SK_GRADE.map((g, gi)=>{
    const L = SK_DUR_LV[gi], at = [];
    L.forEach((v, i)=>{ if(v && v !== (i ? L[i-1] : 0)) at.push(`Lv.${i+1} +${v}`); });
    return at.length ? `<span style="white-space:nowrap"><b style="color:${GRADE_COLOR[g]}">${g}</b> ${at.join(" / ")}</span>` : "";
  }).filter(Boolean).join(" · ");
  return `<details class="skgd"><summary>등급표 — 레벨이 오를 때마다 붙는 수치</summary>
    <table><tr><th></th>${head}</tr>${row("효과량", SK_POW_LV)}${row("출현 확률", SK_PROC_LV)}</table>
    <div class="skgd-dur">출현 확률은 스킬(1 · 2)만 · 지속 시간(지속형 스킬) — ${dur}턴<br>
      Lv.n 의 수치는 표의 값 × (n−1) — 등급이 오르면 지난 레벨 몫도 새 등급으로 다시 계산된다.</div></details>`;
}
function applySkillUp(st, o, silent){
  const id = optId(o.t);
  if(skLevel(st, id) >= SK_LV_MAX) return false;
  const ev = evCap(st, id, evLv(o));
  const m = modOf(st, id);
  m.up = (m.up|0) + 1;
  if(ev > 0) m.grade = Math.min(SK_G_MAX, (m.grade|0) + ev);
  st.sp = Math.max(0, (st.sp||0)-1);
  if(!silent){
    const nm = o.t.kind==="passive" ? o.t.name : o.t.sk.name;
    logE(`<b>${dnH(st)}</b> — ${SK_TIER_N[ev]} · ${nm} Lv.${skLevel(st,id)} ${SK_GRADE[skG(st,id)]} · ${skillOptText(st,o)}${
      skLevel(st,id)>=SK_LV_MAX? " · <b>MAX</b>":""}`, ev? "big":"good");
  }
  return true;
}
/* 개교 시점의 상급생 — 쌓인 포인트를 임의로 소비한 상태로 시작 */
function autoSpendSp(st){
  let guard = 0;
  while((st.sp||0) > 0 && guard++ < 60){
    const pool = skUpPool(st);
    if(!pool.length) break;
    applySkillUp(st, {t: pick(pool), ev: evoRoll(st)}, true);
  }
  st.skOpts = null;
}
function hydrateOpt(st, o){
  if(o.id==="passive"){
    const P = passiveOf(passiveJobOf(st));
    return {t:{kind:"passive", name: P? P.n : "패시브", id:"passive"}, ev:evLv(o)};
  }
  const sk = skillsOf(st).find(x=>x.id===o.id) || skillsOf(st)[0];
  return {t:{kind:"skill", sk}, ev:evLv(o)};
}
function spReady(){ return S.students.filter(s=>(s.sp||0)>0); }
function spTotal(){ return spReady().reduce((a,s)=>a+(s.sp||0),0); }
/* 포인트를 다 쓴다 — 매번 세 제안 중 실제로 오르는 등급이 가장 높은 것 (동률이면 무작위). 임의 강화 · 시뮬레이션이 같이 쓴다 */
function skAutoSpend(st){
  const got = [];
  let guard = 0;
  while((st.sp||0) > 0 && guard++ < 60){
    if(!st.skOpts || !st.skOpts.length){
      const gen = genSkillOptions(st);
      if(!gen.length) break;                 // 더 올릴 스킬이 없다
      st.skOpts = gen.map(o=>({ id: optId(o.t), ev:o.ev }));
    }
    const eff = x=> evCap(st, x.id, evLv(x));
    const mx = Math.max.apply(null, st.skOpts.map(eff));
    const o = hydrateOpt(st, pick(st.skOpts.filter(x=> eff(x)===mx)));
    const id = optId(o.t), ev = evCap(st, id, evLv(o));
    if(!applySkillUp(st, o, true)){ st.skOpts = null; continue; }
    st.skOpts = null;
    got.push({nm: o.t.kind==="passive"? o.t.name : o.t.sk.name, txt: skillOptText(st, o), ev,
      lv: skLevel(st,id), g: skGrade(st,id)});
  }
  return got;
}
function autoSkillUpAll(){
  const targets = spReady();
  if(!targets.length){ toast("강화 포인트가 남은 학생이 없다."); return; }
  const rows = targets.map(st=> ({name:dn(st), job:JOBS[st.job].name, got: skAutoSpend(st)}));
  const evoN = rows.reduce((a,r)=> a + r.got.filter(g=>g.ev===1).length, 0);
  const awkN = rows.reduce((a,r)=> a + r.got.filter(g=>g.ev===2).length, 0);
  const upN  = rows.reduce((a,r)=> a + r.got.length, 0);
  logE(`임의 강화 — <b>${rows.length}명</b>이 강화 포인트 ${upN}점을 소비했다${evoN? ` · <b style="color:var(--brass)">진화 ${evoN}건</b>`:""}${awkN? ` · <b style="color:var(--ex)">각성 ${awkN}건</b>`:""}`, (evoN||awkN)?"big":"good");
  save(); render();
  showModal(`<div class="cerhead"><div class="eyebrow">임의 강화 결과</div>
      <h2 style="font-size:22px;margin-top:2px">${rows.length}명 · 강화 ${upN}회</h2>
      <p style="color:var(--muted);font-size:13px;margin-top:6px">각 학생의 제안 세 가지 중 <b style="color:var(--text)">가장 높은 강화 등급</b>을 골랐다 (동률이면 무작위).${evoN? ` <b style="color:var(--brass)">진화 강화 ${evoN}건</b>.`:""}${awkN? ` <b style="color:var(--ex)">각성 강화 ${awkN}건</b>.`:""}</p></div>
    <div class="grid2" style="margin-top:12px">
      ${rows.map(r=>`<div class="opt" style="cursor:default">
        <div class="on">${esc(r.name)} <span class="tag">${esc(r.job)}</span><span class="price">${r.got.length}회</span></div>
        ${r.got.map(g=>`<div class="od" style="color:${g.ev? SK_TIER_C[g.ev] : "var(--muted)"}">${g.ev? (g.ev===2?"각성 · ":"진화 · ") : ""}${esc(g.nm)} ${esc(g.txt)} <span style="color:var(--dim)">Lv.${g.lv}${g.lv>=SK_LV_MAX?" MAX":""} · ${g.g}</span></div>`).join("")}
      </div>`).join("")}
    </div>
    <div class="btnrow" style="margin-top:14px"><button class="btn primary" data-close>확인</button></div>`, null, true);
}
function autoSkillUpConfirm(){
  const targets = spReady();
  if(!targets.length){ toast("강화 포인트가 남은 학생이 없다."); return; }
  showModal(`<h2 style="font-size:17px;margin-bottom:8px">스킬 임의 강화</h2>
    <p style="color:var(--muted);font-size:13px;margin-bottom:10px">강화 포인트가 남은 <b style="color:var(--text)">${targets.length}명</b>이 포인트 <b style="color:var(--brass)">${spTotal()}점</b>을 전부 소비한다.
      각자에게 주어진 세 가지 제안 중 <b>가장 높은 강화 등급</b>이 선택되며(동률이면 무작위), 어느 스킬을 올릴지 직접 고를 기회는 사라진다.</p>
    <div class="scroll-x" style="max-height:220px;overflow-y:auto;margin-bottom:12px"><table class="tb"><thead><tr><th>학생</th><th>직업</th><th>포인트</th></tr></thead><tbody>
      ${targets.map(s=>`<tr><td>${dnH(s)}</td><td>${JOBS[s.job].name}</td><td class="num">${s.sp}</td></tr>`).join("")}
    </tbody></table></div>
    <div class="btnrow"><button class="btn" data-close>취소</button><button class="btn primary" id="spGo">임의로 강화</button></div>`, ()=>{
    $("#spGo").onclick = ()=>{ closeModal(); autoSkillUpAll(); };
  }, true);
}
function skillUpModal(sid){
  const st = S.students.find(x=>x.id===sid);
  if(!st || !(st.sp>0)) return;
  if(!st.skOpts || !st.skOpts.length){
    const gen = genSkillOptions(st);
    if(!gen.length){ toast("모든 스킬이 최대 레벨이다."); return; }
    st.skOpts = gen.map(o=>({ id: optId(o.t), ev:o.ev }));
    save();
  }
  const opts = st.skOpts.map(o=> hydrateOpt(st, o));
  const p = evoChance(st);
  showModal(`<div class="cerhead"><div class="eyebrow">스킬 강화 · 남은 포인트 ${st.sp}</div>
      <h2 style="font-size:22px;margin-top:2px">${dnH(st)}</h2>
      <p style="color:var(--muted);font-size:13px;margin-top:6px">세 가지 제안 중 하나를 고른다. 한 번 확인한 제안은 고정되며, 나중에 다시 열어도 같은 세 가지가 나온다.
        강화하면 레벨이 하나 오르고, <b style="color:var(--brass)">진화 강화</b>는 등급이 한 단계, <b style="color:var(--ex)">각성 강화</b>는 두 단계 오른다 (D · C · B · A · S · EX).
        수치는 등급과 레벨로 정해져서, 등급이 오르면 지난 레벨 몫까지 새 등급으로 다시 계산된다.
        천재성과 잠재력이 높을수록 진화 · 각성이 자주 나타난다 (진화 이상 ${Math.round(p*100)}% · 각성 ${Math.round(p*p*100)}%). 스킬은 Lv.${SK_LV_MAX}에서 멈춘다.</p>
      ${skGradeTable()}</div>
    <div class="grid2" style="margin-top:12px">
      ${opts.map((o,i)=>{
        const d = skUpDiff(st, o);
        const nm = o.t.kind==="passive"? o.t.name : o.t.sk.name;
        const cat = o.t.kind==="passive"? "패시브" : (o.t.sk.kind==="basic"?"일반 공격":o.t.sk.kind==="ult"?"필살기":"스킬");
        const g = SK_GRADE[d.g0], ng = SK_GRADE[d.g1];
        return `<button class="opt" data-skopt="${i}" style="border-color:${d.ev? SK_TIER_C[d.ev] : "var(--line-soft)"}">
          <div class="on" style="color:${SK_TIER_C[d.ev]}">${esc(nm)}
            <span class="tag">${cat}</span>
            <span class="price">${SK_TIER_N[d.ev]}</span></div>
          <div class="od">Lv.${d.lv0} → ${d.lv1}${d.lv1>=SK_LV_MAX?" <b>MAX</b>":""} · 등급 <b style="color:${GRADE_COLOR[g]}">${g}</b>${d.ev? ` → <b style="color:${GRADE_COLOR[ng]}">${ng}</b>`:""}</div>
          ${skUpLines(d).map(x=>`<div class="od skopt-v">${x}</div>`).join("")}
        </button>`;
      }).join("")}
    </div>
    <div class="btnrow" style="margin-top:14px"><button class="btn ghost" data-close>나중에 고른다</button></div>`, ()=>{
    $("#modalRoot").querySelectorAll("[data-skopt]").forEach(b=> b.onclick=()=>{
      applySkillUp(st, opts[+b.dataset.skopt]);
      st.skOpts = null;
      save(); closeModal(); render();
      if(st.sp>0) skillUpModal(sid);
    });
  }, true);
}
'''

PFB_NOTE_OLD = "   자리 순서 = 전열 1·2·3, 후열 1·3 (허나래 / 성단 / 한현서 / 송찬율 / 전하랑) */\nconst PORTAL_FINAL_BOSS = ["
PFB_NOTE_NEW = ("   자리 순서 = 전열 1·2·3, 후열 1·3 (허나래 / 성단 / 한현서 / 송찬율 / 전하랑)\n"
                "   스킬 기록은 등급 · 강화 횟수만 쓴다 (1008 — 6단계 등급: 예전 EX 4 → 5. 강화 횟수가 4 를 넘는 칸은 Lv.5 로 읽는다) */\n"
                "const PORTAL_FINAL_BOSS = [")

MOB_RE = re.compile(r"const MOB_K = \{[^}]*\};\n")


def mob_apply(src):
    if not MOB_K_SKG:
        return src
    m = MOB_RE.search(src)
    if not m:
        raise RuntimeError("MOB_K 를 못 찾았다")
    cur = dict(re.findall(r"(d\d):([\d.]+)", m.group(0)))
    cur = {k: float(v) for k, v in cur.items()}
    cur.update(MOB_K_SKG)
    fmt = lambda v: ("%g" % v).replace("0.", ".", 1) if v < 1 else "%g" % v
    line = "const MOB_K = {%s};\n" % ", ".join("%s:%s" % (k, fmt(cur[k])) for k in sorted(cur))
    note = ("/* 1008 스킬 등급표 — 마물 스킬도 등급표(출현 확률 · 지속 시간 포함)를 따라 세진 만큼 잡몹 배율을 낮췄다: %s\n"
            "   (역할을 갖춘 B급 3인 · 학생 스킬은 임의 강화 방식, 권장 레벨 +0 · +2 · +4 완주율이 마물 스킬을 바꾸기 전과 같도록 — apply_skgrade) */\n"
            % " · ".join("%s %s" % (k, fmt(v)) for k, v in sorted(MOB_K_SKG.items())))
    body = src[:m.start()]
    k = body.rfind("/* 1008 스킬 등급표 — 마물 스킬도")
    if k >= 0 and body[k:].count("*/") == 1:          # 다시 돌릴 때 — 예전 메모를 지운다
        src = src[:k] + src[m.start():]
        m = MOB_RE.search(src)
    return src[:m.start()] + note + line + src[m.end():]


def apply(src):
    if MARK not in src:
        for old, new in EDITS:
            src = sub1(src, old, new)
        for old, new, n in MULTI:
            src = sub1(src, old, new, n)
        i = src.index(SKUP_START); j = src.index(SKUP_END)
        blk = src[i:j]
        fns = re.findall(r"^function (\w+)", blk, re.M)
        if fns != SKUP_FUNCS:
            raise RuntimeError("스킬 강화 덩어리가 예상과 다르다: %s" % fns)
        src = src[:i] + SKUP_NEW + src[j:]
        # 이계 결승 1군 — 예전 등급(EX 4) 기록
        src = sub1(src, PFB_NOTE_OLD, PFB_NOTE_NEW)
        a = src.index("const PORTAL_FINAL_BOSS = ["); b = src.index("\n", a)
        line = src[a:b]
        if line.count('"grade":4,"up"') != 12:
            raise RuntimeError("이계 결승 1군 기록이 예상과 다르다")
        src = src[:a] + line.replace('"grade":4,"up"', '"grade":5,"up"') + src[b:]
    src = mob_apply(src)
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    if src != raw:
        open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
