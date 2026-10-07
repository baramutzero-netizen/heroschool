"""대회 쿼터뷰 화면 정리 (1007) — 몇 번을 돌려도 같은 결과. apply_tq.py → apply_tqcam.py → apply_tqmaps.py 다음에 돌린다.

    python3 apply_tqui.py <game.html>

· 경기 이름 — BATTLE START 가 도는 동안만 보인다. 물마루 · 흰 글자 · 검은 테두리, 글자가 나타나고 사라지는 때를 배너에 맞춘다
· 범례(체력 · 행동 · 필살기) — 숨김
· 진영 칸 — 진형(배치) 정보를 빼고 이름만. 버튼 박스와 같은 나무판(controls.png)을 9칸으로 늘여 깐다 (모서리는 버튼 박스와 같은 배율)
· 자리 · 크기 — BATTLE_TUNE.quarter (편집기 좌표 px). 필드 배치 실험실(tools/field_lab.html)에서 끌어 옮기고 크기를 바꾼다
가로 화면의 쿼터뷰에서만 (세로 화면 · 계절 필드는 그대로)."""
import sys

# BATTLE_TUNE 에 넣을 기본값 — 경기 이름은 BATTLE START 글자 바로 아래 · 진영 칸은 예전 자리 · 크기(TOURNAMENT_LAYOUT info2 · info3)
QUARTER = ('  quarter:{   /* 1007 — 대회 쿼터뷰(가로) 경기 이름 · 진영 칸 — 편집기 좌표 px. title 은 글 가운데 x · y 와 글자 크기 · enemy / ally 는 칸 x · y · w · h 와 이름 글자 크기 */\n'
           '    title:{"x":899,"y":622,"size":24},\n'
           '    enemy:{"x":1292,"y":194,"w":237,"h":99,"size":20},\n'
           '    ally:{"x":326,"y":807,"w":189,"h":99,"size":20}\n'
           '  }\n')

CSS = r"""
/* 1007 — 대회 쿼터뷰 화면 정리 (apply_tqui) — 범례 숨김 · 진영 칸은 이름만 + 버튼 박스 나무판 · 경기 이름은 BATTLE START 동안만 */
.tournament-quarter .bf-legend{display:none!important}
.tournament-quarter .bf-school .fmtag{display:none!important}
.tournament-quarter .bf-school{background:none!important;border:0!important;border-radius:0!important;padding:0 14px!important;gap:0!important;max-width:none!important;justify-content:center!important;align-items:center!important;text-align:center!important;overflow:visible!important}
.tournament-quarter .bf-school::before{content:"";position:absolute;z-index:-1;pointer-events:none;box-sizing:border-box;
  top:calc(var(--tq-ot,19px) * -1);right:calc(var(--tq-or,12px) * -1);bottom:calc(var(--tq-ob,22px) * -1);left:calc(var(--tq-ol,12px) * -1);
  border:1px solid transparent;border-image-source:url(assets/battle-fields/quarter/controls.png);border-image-slice:290 320 292 320 fill;border-image-width:var(--tq-bw,50px 43px 51px 43px);border-image-repeat:stretch}
.tournament-quarter .bf-school>b{font-size:var(--tq-fs,18px)!important;line-height:1.25!important;max-width:100%;color:#ffe9b5!important;word-break:keep-all;overflow-wrap:anywhere;
  text-shadow:1px 0 0 #2a1506,-1px 0 0 #2a1506,0 1px 0 #2a1506,0 -1px 0 #2a1506,1px 1px 0 #2a1506,-1px 1px 0 #2a1506,1px -1px 0 #2a1506,-1px -1px 0 #2a1506,0 2px 3px #000b!important}
.tq-title{position:absolute;transform:translate(-50%,-50%);margin:0!important;padding:0!important;background:none!important;border:0!important;border-radius:0!important;box-shadow:none!important;
  font-family:"Mulmaru",sans-serif!important;font-weight:400!important;line-height:1.25!important;letter-spacing:0!important;color:#fff!important;text-align:center;white-space:normal;word-break:keep-all;
  opacity:0;pointer-events:none;filter:drop-shadow(0 3px 2px #0009)}
.tq-title::before{content:attr(data-text);position:absolute;inset:0;z-index:-1;color:#000;-webkit-text-stroke:calc(var(--tq-o,2px) * 2) #000;pointer-events:none}
html.tq-lab .tq-title{opacity:1}
html.tq-ban .tq-title{animation:tqTitleBan 1500ms linear both}
/* BATTLE START 글자의 진하기를 그림(battle_start.png) 장면마다 재서 옮겼다 — 167ms 부터 나타나 625ms 에 다 보이고, 1292ms 부터 흐려져 1500ms 에 사라진다 */
@keyframes tqTitleBan{0%,11.1%{opacity:0}16.7%{opacity:.09}22.2%{opacity:.36}27.8%{opacity:.7}33.3%{opacity:.92}38.9%{opacity:.99}41.7%,86.1%{opacity:1}88.9%{opacity:.97}91.7%{opacity:.88}94.4%{opacity:.7}97.2%{opacity:.42}100%{opacity:0}}
"""

CSS_AT = ".tournament-quarter .bf-school{box-shadow:none!important;text-shadow:none!important}</style>"

HELPERS = r"""/* 1007 — 대회 쿼터뷰 경기 이름 · 진영 칸 (apply_tqui). 자리 · 크기는 BATTLE_TUNE.quarter — 편집기 좌표 px (TOURNAMENT_LAYOUT 과 같은 판).
   필드 배치 실험실(tools/field_lab.html)에서 끌어 옮기거나 크기를 바꾼다 (실험실 값이 기본값 위에 얹힌다).
   title — 글 가운데 x · y 와 글자 크기 · enemy / ally — 칸(나무판 안쪽) x · y · w · h 와 이름 글자 크기 */
const TQ_SKIN = {w:1960, h:802, t:290, r:320, b:292, l:320};   // controls.png 크기와 9칸 자르는 선 (CSS border-image-slice 와 같게)
function tqTune(){
  const d = BATTLE_TUNE.quarter || {}, t = bfTune().quarter || {}, o = {};
  ["title","enemy","ally"].forEach(k=> o[k] = Object.assign({}, d[k], t[k]));
  return o;
}
function tqPlace(el, k, v){
  if(!el || !v) return;
  const F = TOURNAMENT_LAYOUT.field, set = (p, x)=> el.style.setProperty(p, x, "important");
  set("left", (v.x - F.x) + "px"); set("top", (v.y - F.y) + "px");
  if(k === "title"){ set("font-size", v.size + "px"); set("--tq-o", Math.max(2, Math.round(v.size / 12)) + "px"); set("max-width", (F.w - 40) + "px"); }
  else { set("width", v.w + "px"); set("height", v.h + "px"); set("--tq-fs", v.size + "px"); }
}
/* 경기 이름은 BATTLE START 가 도는 동안만 (CSS tqTitleBan — 글자가 나타나고 사라지는 때에 맞춘 1500ms).
   전투 화면은 다시 그려질 때마다 제목도 새로 생기므로, 배너가 시작된 때를 기억해 두고 새 제목은 그만큼 앞당겨 튼다 */
var TQ_BAN_T0 = 0;
function tqTitleBan(on){
  TQ_BAN_T0 = on ? performance.now() : 0;
  document.documentElement.classList.toggle("tq-ban", !!on);
  document.querySelectorAll("#modalRoot .tq-title").forEach(tqTitleSync);
}
function tqTitleSync(t){ t.style.animationDelay = TQ_BAN_T0 ? -Math.round(performance.now() - TQ_BAN_T0) + "ms" : ""; }
"""
HELPERS_AT = "function tournamentLayoutApply(fk){\n"

EDITS = [
    # 경기 이름 — 예전 제목 칸(info0) 대신 BATTLE_TUNE.quarter.title
    (" const head=modal.querySelector('.panel-h');let title=null;if(head){title=head.querySelector('h2');title.classList.add('tq-title');stage.append(title);place(title,L.info0,F);head.remove();\n"
     "  /* 1007 — 제목 칸은 글 길이만큼 가로로 늘어난다 (상대 진영 칸 앞까지 · 그보다 길면 두 줄) */\n"
     "  set(title,'width','max-content');set(title,'height','auto');set(title,'min-height',L.info0.h+'px');set(title,'max-width',Math.max(L.info0.w,L.info2.x-L.info0.x-16)+'px');set(title,'white-space','normal');set(title,'word-break','keep-all');}\n",
     " const Q=tqTune(),head=modal.querySelector('.panel-h');let title=null;if(head){title=head.querySelector('h2');title.classList.add('tq-title');title.removeAttribute('style');title.dataset.tq='title';title.dataset.text=title.textContent;stage.append(title);head.remove();\n"
     "  /* 1007 — 경기 이름: BATTLE START 가 도는 동안만 보인다 (물마루 · 검은 테두리 · CSS .tq-title). 자리 · 크기는 BATTLE_TUNE.quarter.title (글 가운데) */\n"
     "  set(title,'position','absolute');set(title,'width','max-content');set(title,'height','auto');set(title,'right','auto');set(title,'bottom','auto');tqPlace(title,'title',Q.title);tqTitleSync(title);}\n"),
    # 범례 · 진영 칸
    (" place(stage.querySelector('.bf-legend'),L.info1,F);const schools=stage.querySelectorAll('.bf-school');schools.forEach((e,i)=>place(e,L['info'+(i+2)],F));\n"
     " {const lg=stage.querySelector('.bf-legend');if(title&&lg){const b=title.offsetTop+title.offsetHeight+6;if(b>lg.offsetTop)set(lg,'top',b+'px');}}   // 1007 — 제목이 두 줄이면 범례는 그 아래로\n",
     " /* 1007 — 범례는 숨김 · 진영 칸은 진형(배치) 정보 없이 이름만 (CSS). 칸 뒤에 버튼 박스와 같은 나무판을 9칸으로 늘여 깐다 (.bf-school::before) —\n"
     "    모서리 배율 · 칸 밖으로 나오는 만큼은 버튼 박스(controls → controlSkin)와 같게. 자리 · 크기는 BATTLE_TUNE.quarter.enemy · ally */\n"
     " {const C=L.controls,K=L.controlSkin,sx=K.w/TQ_SKIN.w,sy=K.h/TQ_SKIN.h,px=v=>(+v).toFixed(1)+'px';\n"
     "  set(stage,'--tq-bw',[TQ_SKIN.t*sy,TQ_SKIN.r*sx,TQ_SKIN.b*sy,TQ_SKIN.l*sx].map(px).join(' '));\n"
     "  set(stage,'--tq-ot',px(C.y-K.y));set(stage,'--tq-or',px(K.x+K.w-C.x-C.w));set(stage,'--tq-ob',px(K.y+K.h-C.y-C.h));set(stage,'--tq-ol',px(C.x-K.x));\n"
     "  [['enemy','.bf-school.enemy'],['ally','.bf-school.ally']].forEach(([k,q])=>{const e=stage.querySelector(q);if(!e)return;e.dataset.tq=k;place(e,Q[k],F);tqPlace(e,k,Q[k]);});}\n"),
    # BATTLE START 배너와 같이
    ("        el.appendChild(img); document.body.appendChild(el); bannerPlace(el);\n",
     "        el.appendChild(img); document.body.appendChild(el); bannerPlace(el);\n"
     "        if(k === \"start\") tqTitleBan(true);                                // 1007 — 대회 쿼터뷰 경기 이름도 같이 나타났다 사라진다\n"),
    ("function battleBannerClear(){\n  BANNER_SEQ++;\n",
     "function battleBannerClear(){\n  BANNER_SEQ++;\n  tqTitleBan(false);\n"),
    # 필드 배치 실험실 — 쿼터뷰 필드 목록 · 요소 고르기 · 끌기 · BATTLE START 틀어 보기
    ("    orient: bfOrient(), pastel: PREF.fieldPastel !== false};\n",
     "    orient: bfOrient(), pastel: PREF.fieldPastel !== false,\n"
     "    quarter: Object.keys(FIELD_GROUND).filter(k=> tqMapKey(k))};      // 1007 — 가로 화면에서 쿼터뷰로 보이는 필드\n"),
    ("  document.querySelectorAll(\".bf-stage [data-slot]\").forEach(el=> el.classList.toggle(\"lab-sel\", el.dataset.slot === FIELD_LAB.sel));\n",
     "  document.querySelectorAll(\".bf-stage [data-slot]\").forEach(el=> el.classList.toggle(\"lab-sel\", el.dataset.slot === FIELD_LAB.sel));\n"
     "  labTqDecorate();\n"),
    ("    const u = ev.target.closest(\".bf-unit[data-slot]\");\n    if(!u || u.dataset.slot === \"boss\") return;\n",
     "    const q = ev.target.closest(\"[data-tq]\");\n    if(q){ labTqDrag(ev, q, stage); return; }                           // 1007 — 쿼터뷰 경기 이름 · 진영 칸\n"
     "    const u = ev.target.closest(\".bf-unit[data-slot]\");\n    if(!u || u.dataset.slot === \"boss\") return;\n"),
    ("    FIELD_LAB.sel = k; labDecorate(); labPost({type:\"pick\", slot:k});\n",
     "    FIELD_LAB.sel = k; FIELD_LAB.tqSel = null; labDecorate(); labPost({type:\"pick\", slot:k});\n"),
    ("    if(d.lab !== \"field\" || d.type !== \"set\") return;\n",
     "    if(d.lab === \"field\" && d.type === \"banner\"){ battleBanner(\"start\", 4000); return; }   // 1007 — BATTLE START 틀어 보기 (경기 이름이 같이 뜬다)\n"
     "    if(d.lab !== \"field\" || d.type !== \"set\") return;\n"),
    ("    if(d.sel !== undefined) L.sel = d.sel;\n",
     "    if(d.sel !== undefined) L.sel = d.sel;\n    if(d.tqSel !== undefined) L.tqSel = d.tqSel;\n"),
]

LAB_FN = r"""/* 1007 — 실험실: 쿼터뷰 경기 이름 · 진영 칸. 늘 보이게 하고(경기 이름도), 고른 요소에 점선 · 오른쪽 아래 노란 손잡이.
   끌면 옮기고, 손잡이를 끌면 크기(진영 칸은 너비 · 높이, 경기 이름은 글자 크기)를 바꾼다 — 바깥 창에 tqpick · tqmove · tqmoveend */
function labTqDecorate(){
  document.documentElement.classList.add("tq-lab");
  let st = document.getElementById("labTqStyle");
  if(!st){ st = document.createElement("style"); st.id = "labTqStyle";
    st.textContent = `.tournament-quarter [data-tq]{pointer-events:auto!important;cursor:move}
      .tournament-quarter [data-tq].lab-tq{outline:2px dashed #ffd84a!important;outline-offset:4px}
      .tq-rs{position:absolute;right:-10px;bottom:-10px;width:14px;height:14px;background:#ffd84a;border:2px solid #1a1206;border-radius:3px;cursor:nwse-resize;z-index:5}`;
    document.head.appendChild(st); }
  document.querySelectorAll(".tournament-quarter [data-tq]").forEach(el=>{
    const on = el.dataset.tq === FIELD_LAB.tqSel;
    el.classList.toggle("lab-tq", on);
    let h = el.querySelector(":scope > .tq-rs");
    if(on && !h){ h = document.createElement("i"); h.className = "tq-rs"; el.appendChild(h); }
    if(!on && h) h.remove();
  });
}
function labTqDrag(ev, el, stage){
  ev.preventDefault();
  const k = el.dataset.tq, rs = !!ev.target.closest(".tq-rs");
  FIELD_LAB.tqSel = k; labTqDecorate(); labPost({type:"tqpick", el:k});
  const v0 = tqTune()[k], R = stage.getBoundingClientRect(), sc = (R.width / stage.offsetWidth) || 1, px = ev.clientX, py = ev.clientY;
  let v = null;
  const mv = e=>{
    const dx = (e.clientX - px) / sc, dy = (e.clientY - py) / sc;
    if(!v && Math.abs(dx) + Math.abs(dy) < 3) return;
    v = Object.assign({}, v0);
    if(!rs){ v.x = Math.round(v0.x + dx); v.y = Math.round(v0.y + dy); }
    else if(k === "title") v.size = Math.max(8, Math.round(v0.size + (dx + dy) / 4));
    else { v.w = Math.max(40, Math.round(v0.w + dx)); v.h = Math.max(24, Math.round(v0.h + dy)); }
    tqPlace(el, k, v);
    labPost({type:"tqmove", el:k, v});
  };
  const up = ()=>{ removeEventListener("pointermove", mv); removeEventListener("pointerup", up);
    if(v){ FIELD_LAB.tune.quarter = Object.assign({}, FIELD_LAB.tune.quarter, {[k]: v}); labPost({type:"tqmoveend", el:k, v}); } };
  addEventListener("pointermove", mv); addEventListener("pointerup", up);
}
"""
LAB_FN_AT = "function fieldLabBoot(){\n"


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:100]))
    return src.replace(old, new)


def apply(src):
    if "function tqTune(){" in src:
        return src
    # BATTLE_TUNE 끝에 quarter 묶음
    a = src.index("const BATTLE_TUNE = {")
    b = src.index("\n};\n", a)
    if "\n  quarter:{" in src[a:b]:
        raise RuntimeError("BATTLE_TUNE 에 quarter 가 이미 있다")
    if not src[a:b].endswith("\n  }"):
        raise RuntimeError("BATTLE_TUNE 끝 모양이 다르다")
    src = src[:b] + ",\n" + QUARTER.rstrip("\n") + src[b:]
    src = sub1(src, CSS_AT, CSS_AT.replace("</style>", "") + CSS.rstrip("\n") + "\n</style>")
    src = sub1(src, HELPERS_AT, HELPERS + HELPERS_AT)
    for old, new in EDITS:
        src = sub1(src, old, new)
    src = sub1(src, LAB_FN_AT, LAB_FN + LAB_FN_AT)
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
