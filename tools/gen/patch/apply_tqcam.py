"""대회 쿼터뷰 클로즈업 (1007) — 몇 번을 돌려도 같은 결과. apply_tq.py 다음에 돌린다.

    python3 apply_tqcam.py <game.html>

스타일리시 전투 줌인 때 —
· 카메라가 바닥 문장(맵 마크 · 지역 대회 판은 경기장 바닥 가운데)을 전투판 가운데로 옮긴다
· 유닛은 문장 둘레에 선다 — 왼쪽 · 오른쪽 무리의 순서는 예전 클로즈업 그대로, 가장 안쪽 유닛이 월계수 끝에 서고 발밑은 문장 가운데보다 조금 아래
· 유닛을 따로 키우던 배율(1.3)을 카메라 배율에 합쳐(1.2 × 1.3) 지도와 유닛이 똑같이 커진다 — 유닛 크기는 예전 클로즈업과 같다
· 클로즈업 위아래 경계선을 안쪽으로 (흐린 띠 — 위 24 → 27% · 아래 14 → 26%)
일반 필드 전투의 클로즈업은 그대로."""
import sys

MARK = "const TQ_MARK = "

FN_AT = "function tournamentLayoutApply(fk){\n"
FN = '''/* 1007 — 대회 쿼터뷰 클로즈업. 바닥 문장(맵 마크)을 전투판 가운데로 옮기고, 지도 · 유닛을 같은 배율로 키운다 (camTurn).
   TQ_MARK — 지도 그림(iw × ih) 안의 문장 가운데 픽셀 (지역 대회 판은 문장이 없어 경기장 바닥 가운데).
   TQ_ZOOM — 예전 클로즈업에서 유닛이 커지던 만큼(유닛 1.3 × 카메라 1.2). 이제 카메라 하나로 키워 지도도 같이 커진다.
   TQ_FEET — 화면에서 문장 가운데부터 유닛 기준점까지(%) — 그림 발밑은 기준점보다 11% 쯤 아래라 발밑은 문장 가운데보다 조금 아래.
   TQ_GAP · TQ_STEP · TQ_OUT — 화면에서 문장 가운데부터 가장 안쪽 유닛 · 유닛 사이 · 가장 바깥 한도(%). 안쪽 유닛은 월계수 끝에 선다 */
const TQ_MARK = {citytournament:{x:767, y:462, iw:1536, ih:1024}, areatournament:{x:784, y:430, iw:1536, ih:1024}};
const TQ_ZOOM = 1.3 * 1.2, TQ_FEET = -5, TQ_GAP = 19.5, TQ_STEP = 10, TQ_OUT = 40;
function tqCloseup(stage){
  const M = stage && stage.isConnected && stage._tqMark; if(!M) return null;
  const sw = stage.clientWidth, sh = stage.clientHeight; if(!sw || !sh) return null;
  const z = TQ_ZOOM, tx = -z * (M.x - sw/2), ty = -z * (M.y - sh/2);      // 문장이 전투판 가운데로 (카메라 가운데 = 전투판 가운데)
  return {z, pre: `translate(${tx.toFixed(1)}px, ${ty.toFixed(1)}px) `, mx: M.x / sw * 100, my: M.y / sh * 100};
}
/* 예전 클로즈업 자리(stylishFormation · 판 %) → 문장 둘레 자리. 가운데를 기준으로 왼쪽 · 오른쪽 무리로 나눠
   가운데에 가까운 순서를 그대로 지키고, 화면에서 TQ_GAP 부터 TQ_STEP 간격으로 바깥으로 세운다 (많으면 TQ_OUT 안으로 좁힌다).
   가운데(50)에 놓인 유닛은 행동하는 쪽의 반대편. 세로는 모두 문장 가운데 + TQ_FEET */
function tqFormation(T, list, actor){
  if(!T) return list;
  const ax = (list.find(p=> p.uid === actor) || list[0] || {x:0}).x;
  const sideOf = p=> p.x > 50 ? 1 : p.x < 50 ? -1 : (ax > 50 ? -1 : 1);
  const out = [];
  [-1, 1].forEach(s=>{
    const g = list.filter(p=> sideOf(p) === s).sort((a,b)=> Math.abs(a.x - 50) - Math.abs(b.x - 50));
    const step = g.length > 1 ? Math.min(TQ_STEP, (TQ_OUT - TQ_GAP) / (g.length - 1)) : 0;
    g.forEach((p,i)=> out.push({uid: p.uid, scale: 1, x: T.mx + s * (TQ_GAP + step * i) / T.z, y: T.my + TQ_FEET / T.z}));
  });
  return out;
}
'''

MK_AT = " if(!stage.querySelector('.tq-frame'))"
MK = (" {const mk=TQ_MARK[fk];if(mk)stage._tqMark={x:L.map.x-F.x+mk.x*L.map.w/mk.iw,y:L.map.y-F.y+mk.y*L.map.h/mk.ih};}"
      "   // 1007 — 바닥 문장 자리 (판 px) · 클로즈업 가운데\n")

EDITS = [
    ("    const sw = stage.clientWidth, sh = stage.clientHeight, CS = 1.2;\n",
     "    const sw = stage.clientWidth, sh = stage.clientHeight, TQ = tqCloseup(stage), CS = TQ ? TQ.z : 1.2, CP = TQ ? TQ.pre : \"\";"
     "   // 1007 — 대회 쿼터뷰: 바닥 문장을 가운데로 · 지도와 유닛을 같은 배율로\n"),
    ("    stylishFormation(a, allies, enemies, side, F.fx && F.fx.skillId).forEach(p=>place(uEl(p.uid),p.x,p.y,p.scale));\n",
     "    tqFormation(TQ, stylishFormation(a, allies, enemies, side, F.fx && F.fx.skillId), a).forEach(p=>place(uEl(p.uid),p.x,p.y,p.scale));\n"),
    ('    stage.style.setProperty("--cam", `scale(${CS})`);\n',
     '    stage.style.setProperty("--cam", `${CP}scale(${CS})`);\n'),
    ('    stage.style.setProperty("--cam", `scale(${CS}) translateX(${Math.round(dir*.03*sw)}px)${attack ? ` rotate(${dir*3}deg)` : ""}`);\n',
     '    stage.style.setProperty("--cam", `${CP}scale(${CS}) translateX(${Math.round(dir*.03*sw*1.2/CS)}px)${attack ? ` rotate(${dir*3}deg)` : ""}`);'
     '   // 흐르는 폭은 화면에서 예전과 같게\n'),
]


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:90]))
    return src.replace(old, new)


BAND_AT = ".cam-fx .cs.b{bottom:calc(var(--band-b) - 17px)}\n"
BAND = (".tournament-quarter .cam-fx{--band-t:27%;--band-b:26%}"
        "   /* 1007 — 대회 쿼터뷰 클로즈업 경계선을 안쪽으로 — 위(24 → 27%)는 조금, 아래(14 → 26%)는 더 · 유닛이 문장 둘레(가운데)에 서므로 */\n")


def apply(src):
    if MARK not in src:
        src = sub1(src, FN_AT, FN + FN_AT)
        src = sub1(src, MK_AT, MK + MK_AT)
        for old, new in EDITS:
            src = sub1(src, old, new)
    if BAND not in src:
        src = sub1(src, BAND_AT, BAND_AT + BAND)
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
