"""대회 쿼터뷰 판 손보기 (1007) — 몇 번을 돌려도 같은 결과.

    python3 apply_tq.py <game.html>

① 제목 칸 — 배치값(전투 제목 · 72×53)이 '전투' 두 글자 크기라 실제 제목이 세로로 길게 늘어졌다.
   글 길이만큼 가로로 늘어나게 한다 (상대 진영 칸 앞까지 · 그보다 길면 두 줄, 범례는 그 아래로).
② 스타일리시 연출 줌 — 카메라(.bf-cam)만 커지고 지도는 그대로였다. 지도 그림이 매 프레임 카메라의 지금 변형을
   그대로 따라가게 한다 (가운데 = 전투판 가운데). CSS 전환을 따로 걸면 큰 지도 그림의 전환이 늦게 시작해
   유닛과 바닥이 어긋나서 프레임마다 옮겨 적는 쪽을 택했다. 액자 · 제목 · 진영 칸 · 단추 판은 그대로."""
import sys

MARK = "1007 — 제목 칸은 글 길이만큼"

TITLE_OLD = (" const head=modal.querySelector('.panel-h');if(head){const title=head.querySelector('h2');title.classList.add('tq-title');"
             "stage.append(title);place(title,L.info0,F);head.remove();}\n")
TITLE_NEW = (" const head=modal.querySelector('.panel-h');let title=null;if(head){title=head.querySelector('h2');title.classList.add('tq-title');"
             "stage.append(title);place(title,L.info0,F);head.remove();\n"
             "  /* 1007 — 제목 칸은 글 길이만큼 가로로 늘어난다 (상대 진영 칸 앞까지 · 그보다 길면 두 줄) */\n"
             "  set(title,'width','max-content');set(title,'height','auto');set(title,'min-height',L.info0.h+'px');"
             "set(title,'max-width',Math.max(L.info0.w,L.info2.x-L.info0.x-16)+'px');set(title,'white-space','normal');set(title,'word-break','keep-all');}\n")

MAP_OLD = "bg.append(im);stage.prepend(bg);place(im,L.map,F);}"
MAP_NEW = ("bg.append(im);stage.prepend(bg);place(im,L.map,F);"
           "set(im,'transform-origin',(F.w/2-(L.map.x-F.x))+'px '+(F.h/2-(L.map.y-F.y))+'px');}"
           "   // 1007 — 줌 가운데 = 전투판 가운데 (카메라와 같은 점) · tqCamSync")

LEG_OLD = " place(stage.querySelector('.bf-legend'),L.info1,F);const schools=stage.querySelectorAll('.bf-school');schools.forEach((e,i)=>place(e,L['info'+(i+2)],F));\n"
LEG_NEW = LEG_OLD + (" {const lg=stage.querySelector('.bf-legend');if(title&&lg){const b=title.offsetTop+title.offsetHeight+6;if(b>lg.offsetTop)set(lg,'top',b+'px');}}"
                     "   // 1007 — 제목이 두 줄이면 범례는 그 아래로\n")

SYNC_AT = "function tournamentLayoutApply(fk){\n"
SYNC_FN = '''/* 1007 — 대회 쿼터뷰 지도도 스타일리시 연출 카메라(.bf-cam)를 따라 줌인 · 줌아웃한다.
   지도에 CSS 전환을 따로 걸면 큰 그림(합성 층)의 전환이 늦게 시작해 유닛과 바닥이 어긋났다 — sprTick 이 매 프레임
   카메라의 지금 변형을 지도 그림에 옮겨 적는다 (가운데는 tournamentLayoutApply 가 전투판 가운데로 맞춰 둔다) */
function tqCamSync(){
  const st = tournamentFinishStage; if(!st || !st.isConnected) return;
  const im = st._tqMap || (st._tqMap = st.querySelector('.tq-map img')), cam = st._tqCam || (st._tqCam = st.querySelector('.bf-cam'));
  if(!im || !cam) return;
  const t = getComputedStyle(cam).transform;
  if(t !== im._tqT){ im._tqT = t; im.style.setProperty('transform', t, 'important'); }
}
'''
TICK_OLD = "  tournamentCharacterTick(now);\n}\n"
TICK_NEW = "  tournamentCharacterTick(now);\n  tqCamSync();   // 1007 — 대회 쿼터뷰 지도도 카메라를 따라 줌\n}\n"


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:90]))
    return src.replace(old, new)


def apply(src):
    if MARK in src:
        return src
    src = sub1(src, TITLE_OLD, TITLE_NEW)
    src = sub1(src, MAP_OLD, MAP_NEW)
    src = sub1(src, LEG_OLD, LEG_NEW)
    src = sub1(src, SYNC_AT, SYNC_FN + SYNC_AT)
    return sub1(src, TICK_OLD, TICK_NEW)


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
