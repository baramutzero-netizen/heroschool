"""game.html 에 두루마리 스케줄(1006)을 넣는다 — 몇 번을 돌려도 같은 결과 (이전 블록은 지우고 다시 넣는다).

    python3 apply_sched.py <game.html> <배치 JSON> [--force]

넣는 것: CSS(본 스타일시트 끝) · JS 블록(viewPlanClassic 앞) · render 의 스케줄 분기 · bindView 연결 · PREF(schedScroll · sign) · 설정 칸 ·
임의 감추기 · 소리(SFX 셋 · slotPut / 자동 배치 뒤 slotSfx — 소리 파일은 bgm/sched_*.ogg 를 따로 둔다).
그림은 data: 로 넣고, wrap.py / wrap_site.py 가 돌 때 split_assets 가 assets/sched_art/ 로 뺀다.
1008 — 그림은 무손실 WebP 로 넣는다 (apply_webp.webp_lossless — 픽셀은 PNG 와 똑같다)."""
import base64, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, HERE)
import sched_art
import apply_job                                              # 의뢰 바꾸기 (1006) — 이번 주 의뢰를 미리 · 의뢰처별 등급
from apply_webp import webp_lossless                         # 1008 — 그림은 무손실 WebP


def prefix_css(css, pre="html body "):
    """규칙마다 앞에 pre 를 붙인다 (@media 안쪽도). 무대 안 규칙은 .skwrap .skfit .skstage 까지 — 게임의 도트 테마 단추 규칙
    (html[data-ui-finish=pixel] :is(button…) — :is 안의 input:not()×3 때문에 (0,4,2))과 같거나 세고, 스타일시트 끝에 두어 같으면 이긴다"""
    out, i, n = [], 0, len(css)
    def rules(block):
        res = []
        for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', block):
            sel, body = m.group(1), m.group(2)
            lead = sel[:len(sel) - len(sel.lstrip())]
            sels = [s.strip() for s in sel.split(',')]
            res.append(lead + ",".join(s if s.startswith(('from', 'to')) or re.match(r'^[0-9.,% ]+$', s) else (pre if s.startswith(('.skwrap', '.skfit', '.skstage')) else pre + '.skwrap .skfit .skstage ') + s for s in sels) + "{" + body + "}")
        return "".join(res)
    while i < n:
        if css.startswith('/*', i):
            j = css.index('*/', i) + 2; out.append(css[i:j]); i = j; continue
        if css[i] in ' \n\t':
            out.append(css[i]); i += 1; continue
        if css.startswith('@keyframes', i):
            j = css.index('{', i); depth = 0; k = j
            while True:
                if css[k] == '{': depth += 1
                elif css[k] == '}':
                    depth -= 1
                    if depth == 0: break
                k += 1
            out.append(css[i:k + 1]); i = k + 1; continue
        if css.startswith('@media', i):
            j = css.index('{', i); depth = 0; k = j
            while True:
                if css[k] == '{': depth += 1
                elif css[k] == '}':
                    depth -= 1
                    if depth == 0: break
                k += 1
            out.append(css[i:j + 1] + rules(css[j + 1:k]) + "}"); i = k + 1; continue
        j = css.index('}', i) + 1
        out.append(rules(css[i:j])); i = j
    return "".join(out)


def sub1(src, old, new, done_mark):
    if done_mark in src: return src
    if old not in src: raise RuntimeError("자리를 못 찾았다: " + old[:80])
    return src.replace(old, new, 1)


def apply(src, layout_path):
    art, geo = sched_art.build(layout_path)
    uri = {k: "data:image/webp;base64," + base64.b64encode(webp_lossless(v)).decode() for k, v in art.items()}   # 1008 — 무손실 WebP
    css = prefix_css(open(HERE + "sched_block.css", encoding="utf-8").read())
    js = open(HERE + "sched_block.js", encoding="utf-8").read()
    js = js.replace("/*SCHED_ART*/{}", json.dumps(uri, separators=(",", ":")), 1)
    js = js.replace("/*SCHED_GEO*/{}", json.dumps(geo, ensure_ascii=False, separators=(",", ":")), 1)
    # 이전 블록 지우기
    src = re.sub(r'/\* SCHED_SCROLL_CSS_START.*?/\* SCHED_SCROLL_CSS_END \*/\n?', '', src, flags=re.S)
    src = re.sub(r'/\* SCHED_SCROLL_START.*?/\* SCHED_SCROLL_END \*/\n?', '', src, flags=re.S)
    # CSS — 본 스타일시트(첫 </style>) 끝
    i = src.index('</style>')
    src = src[:i] + css.rstrip('\n') + '\n' + src[i:]
    # JS — 예전 스케줄 화면 함수 바로 앞
    j = src.index('function viewPlanClassic(){')
    src = src[:j] + js.rstrip('\n') + '\n' + src[j:]
    # render — 가로 화면이면 두루마리
    src = sub1(src, 'else if(UI.view==="plan") v.innerHTML = viewPlan();',
               'else if(UI.view==="plan") v.innerHTML = schedScrollOn() ? viewPlanScroll() : viewPlan();   // 두루마리 스케줄 (1006)',
               'schedScrollOn() ? viewPlanScroll()')
    # bindView — 원래 단추 · 카드 연결 뒤에 (결재 단추를 서명으로 감싼다)
    old = 'const br = $("#btnRest"); if(br) br.onclick=()=> runWeeks(halfLeft());'
    src = sub1(src, old, old + '\n  if(UI.view==="plan" && document.querySelector("#view .skstage")) bindSchedScroll(v);   // 두루마리 스케줄 — 깃펜 · 서명 · 카드 끌기 (1006)',
               'bindSchedScroll(v);')
    # PREF — 기본 켬 · 저장된 서명
    src = sub1(src, 'bfGrid: false, battleCam: "stylish"};', 'bfGrid: false, battleCam: "stylish", schedScroll: true};', 'schedScroll: true};')
    old = '  if(j && typeof j.bfGrid === "boolean") PREF.bfGrid = j.bfGrid;'
    src = sub1(src, old, old + '\n  if(j && typeof j.schedScroll === "boolean") PREF.schedScroll = j.schedScroll;   // 두루마리 스케줄 (1006)'
               + '\n  if(j && j.sign && Array.isArray(j.sign.s) && j.sign.s.length) PREF.sign = j.sign;          // 결재 서명 — 이 브라우저에 남는다 (1006)',
               'PREF.schedScroll = j.schedScroll;')
    # 설정 — 두루마리 스케줄 켜고 끄기 · 저장된 서명 지우기
    old = '  return conceptPanel + (OPT_PIXEL_FONT ? pxPanel : "") + lvPanel + '
    new = ('  const skPanel = `<section class="panel"><div class="optrow"><div class="optlab"><b>두루마리 스케줄</b><span>가로 화면의 스케줄을 책상 위 두루마리로 보여 준다. '
           '결재는 깃펜을 잉크 단지에 찍어 서명한다. 끄면 예전 스케줄 화면.</span></div><label style="display:flex;align-items:center;gap:6px;cursor:pointer">'
           '<input type="checkbox" id="optSchedScroll" ${PREF.schedScroll!==false?"checked":""}> 켜기</label></div>${PREF.sign? `<div class="optrow" style="margin-top:8px">'
           '<div class="optlab"><b>저장된 서명</b><span>결재 때 쓰는 서명. 지우면 다음 결재 때 새로 그린다 — 서명줄에 새로 그어도 바뀐다.</span></div>'
           '<button class="btn sm" id="optSignClear">서명 지우기</button></div>` : ""}</section>`;   // 두루마리 스케줄 (1006)\n'
           '  return conceptPanel + (OPT_PIXEL_FONT ? pxPanel : "") + skPanel + lvPanel + ')
    src = sub1(src, old, new, 'const skPanel =')
    old = '  { const lp = $("#optLvPop");'
    new = ('  { const sc = $("#optSchedScroll"); if(sc) sc.onchange = ()=>{ PREF.schedScroll = sc.checked; prefSave(); toast(sc.checked? "스케줄을 두루마리로 보여 준다 (가로 화면)." : "예전 스케줄 화면으로 돌아갔다."); }; }   // 1006\n'
           '  { const sg = $("#optSignClear"); if(sg) sg.onclick = ()=>{ delete PREF.sign; prefSave(); render(); toast("저장된 서명을 지웠다 — 다음 결재 때 새로 서명한다."); }; }\n' + old)
    src = sub1(src, old, new, 'const sc = $("#optSchedScroll")')
    # 임의(auto) 감추기 (1006) — 규칙은 그대로 두고 고르는 칸 · 스케줄 화면에서만 뺀다. 임의인 학생은 이번 주에 할 일로 보인다
    old = 'function actTag(s){\n  const k = actUnlocked() ? actOf(s) : (isRestFocus(s) ? "rest" : "");'
    new = ('/* 임의(auto)는 고르는 칸에서 감췄다 (1006) — 규칙은 그대로라 새 학생은 여전히 임의로 시작한다.\n'
           '   화면에는 임의 대신 이번 주에 할 일(부상이거나 컨디션 69 이하면 휴식, 아니면 훈련)로 보여 주고, 고르는 칸은 훈련 · 휴식 · 의뢰만 */\n'
           'function actShown(st){ const k = actOf(st); return k !== "auto" ? k : (isInjured(st) || (st && st.cond < AUTO_REST_BELOW)) ? "rest" : "train"; }\n'
           'function actPickKeys(){ return ["train", "rest", "job"].filter(k=> k!=="job" || jobOpen()); }\n'
           'function actTag(s){\n  const k = actUnlocked() ? actShown(s) : (isRestFocus(s) ? "rest" : "");')
    src = sub1(src, old, new, 'function actShown(st)')
    old = '${actKeys().map(k=>`<option value="${k}" ${actOf(s)===k?"selected":""}>${ACT[k].n} — '
    src = sub1(src, old, '${actPickKeys().map(k=>`<option value="${k}" ${actShown(s)===k?"selected":""}>${ACT[k].n} — ', 'actPickKeys().map(k=>`<option')
    old = '<div style="font-size:11.5px;color:var(--dim);margin-top:4px">${actOf(s)==="train"? `오늘 기준'
    src = sub1(src, old, '<div style="font-size:11.5px;color:var(--dim);margin-top:4px">${actShown(s)==="train"? `오늘 기준', 'margin-top:4px">${actShown(s)==="train"?')
    old = '            : actOf(s)==="job"? `그 주의 의뢰를 오후에 수행한다.'
    src = sub1(src, old, '            : actShown(s)==="job"? `그 주의 의뢰를 오후에 수행한다.', ': actShown(s)==="job"?')   # apply_job 이 뒤를 바꿔도 남는 표시
    old = '<span class="btnpair"><button class="btn sm" id="btnFocusClear">전원 임의</button><button class="btn sm" id="btnActTrain">전원 훈련</button>'
    src = sub1(src, old, '<span class="btnpair"><button class="btn sm" id="btnActTrain">전원 훈련</button>', '<span class="btnpair"><button class="btn sm" id="btnActTrain">전원 훈련</button>')
    old = '<button class="btn primary" id="rwFix">임의로 바꾸고 진행</button>'
    src = sub1(src, old, '<button class="btn primary" id="rwFix">훈련으로 바꾸고 진행</button>', 'id="rwFix">훈련으로 바꾸고 진행')
    old = '      n.forEach(s=> s.focus = "auto");\n      logE(`휴식 해제 — ${n.map(x=>dnH(x)).join(", ")}을(를) 임의로 돌렸다 (컨디션 회복 완료)`, "good");'
    new = '      n.forEach(s=> s.focus = "train");   // 임의를 감춰서 훈련으로 (1006)\n      logE(`휴식 해제 — ${n.map(x=>dnH(x)).join(", ")}을(를) 훈련으로 돌렸다 (컨디션 회복 완료)`, "good");'
    src = sub1(src, old, new, '을(를) 훈련으로 돌렸다')
    # 소리 (1006) — 효과음 목록에 셋 · 일과를 놓을 때(slotPut · 자동 배치) 놓는 소리와 새 체인 소리 (slotSfx 는 두루마리 블록에)
    old = '  op_hand:  {f:"opening_hand.ogg"}\n};'
    new = ('  op_hand:  {f:"opening_hand.ogg"},\n'
           '  /* 스케줄 (1006) — 일과를 요일에 놓을 때 · 같은 색이 이어져 체인이 생길 때 · 서명하는 동안(펜이 움직일 때만 되풀이). 원본 mp3 도 bgm/ 에.\n'
           '     sched_sign.ogg 는 원본(7.4초)의 긴 무음을 줄이고 끝과 처음을 0.08초 겹쳐 이음매 없는 고리로 만든 것 (6.74초) */\n'
           '  sk_place:{f:"sched_place.ogg"},\n'
           '  sk_chain:{f:"sched_chain.ogg"},\n'
           '  sk_sign: {f:"sched_sign.ogg"}\n};')
    src = sub1(src, old, new, 'sk_place:{f:"sched_place.ogg"}')
    old = 'function slotPut(u, day){\n  if(day<0 || day>=WEEK_DAYS) return;'
    new = ('function slotPut(u, day){                        // 소리 (1006) — 놓기 · 새 체인 (slotSfx)\n'
           '  const pre = (S.slots||[]).slice();\n'
           '  slotPut0(u, day);\n'
           '  if(typeof slotSfx === "function") slotSfx(pre);\n'
           '}\n'
           'function slotPut0(u, day){\n  if(day<0 || day>=WEEK_DAYS) return;')
    src = sub1(src, old, new, 'function slotPut0(u, day){')
    old = 'const bAuto = $("#btnAuto"); if(bAuto) bAuto.onclick = ()=>{ autoFillSlots(); save(); render(); };'
    new = 'const bAuto = $("#btnAuto"); if(bAuto) bAuto.onclick = ()=>{ const pre = (S.slots||[]).slice(); autoFillSlots(); if(typeof slotSfx === "function") slotSfx(pre); save(); render(); };   // 소리 (1006)'
    src = sub1(src, old, new, 'autoFillSlots(); if(typeof slotSfx')
    # 반짝이는 소리 (1006) — 깃펜 · 잉크 단지가 빛나기 시작할 때. 다른 효과음보다 60% 작게(v .4)
    old = '  sk_sign: {f:"sched_sign.ogg"}\n};'
    new = ('  sk_sign: {f:"sched_sign.ogg"},\n'
           '  sk_glow: {f:"sched_glow.ogg", v:.4}   // 깃펜 · 잉크 단지가 빛나기 시작할 때 (13.8초 · 빛나는 동안 한 번) — 다른 효과음보다 60% 작게\n};')
    src = sub1(src, old, new, 'sk_glow: {f:"sched_glow.ogg"')
    # 두루마리 스케줄이 아닌 화면으로 가면 반짝이는 소리를 끈다
    # (1006 앞판 — 소리만 끄던 줄은 skLeave 로 바꾼다)
    src = src.replace('bindSchedScroll(v); else if(typeof skGlowSnd === "function") skGlowSnd(false);', 'bindSchedScroll(v); else if(typeof skLeave === "function") skLeave();')
    old = 'if(UI.view==="plan" && document.querySelector("#view .skstage")) bindSchedScroll(v);'
    new = 'if(UI.view==="plan" && document.querySelector("#view .skstage")) bindSchedScroll(v); else if(typeof skLeave === "function") skLeave();'
    src = sub1(src, old, new, 'else if(typeof skLeave === "function") skLeave();')
    src = apply_job.apply(src)
    return src, geo


BLOCKS = [("sched_js", "/* SCHED_SCROLL_START", "/* SCHED_SCROLL_END */"), ("sched_css", "/* SCHED_SCROLL_CSS_START", "/* SCHED_SCROLL_CSS_END */")]

if __name__ == "__main__":
    import blockguard                                          # game.html 에서 블록 안을 직접 고친 게 있으면 멈춘다 (--force 로 덮어쓴다)
    force = "--force" in sys.argv
    path, lay = [a for a in sys.argv[1:] if a != "--force"][:2]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    blockguard.check(raw.replace("\r\n", "\n"), BLOCKS, force)
    src, geo = apply(raw.replace("\r\n", "\n"), lay)
    blockguard.record(src, BLOCKS)
    if crlf: src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars · crlf" if crlf else "")
