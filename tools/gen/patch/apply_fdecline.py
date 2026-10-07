"""친선전 '전부 거절' — 한 번 더 묻는다 (1007). 몇 번을 돌려도 같은 결과.

    python3 apply_fdecline.py <game.html>

친선전 요청 팝업은 그대로 두고 그 위에 작은 확인 창을 겹쳐 띄운다 (튜토리얼 겹침 창과 같은 방식).
취소하면 고르던 배치 그대로 돌아가고, 전부 거절을 누르면 예전과 똑같이 거절 처리한다."""
import sys

MARK = "function friendlyDeclineAsk("

FN = '''/* 친선전 전부 거절 — 한 번 더 묻는다 (1007). 친선전 팝업은 그대로 두고 그 위에 겹쳐 띄운다 — 취소하면 고르던 그대로 */
function friendlyDeclineAsk(onYes){
  const root = $("#modalRoot");
  if(!root || !root.firstChild){ onYes(); return; }
  if(root.querySelector(".fdecl")) return;                       // 이미 묻는 중
  const box = document.createElement("div");
  box.className = "overlay tutover fdecl";
  box.innerHTML = `<div class="modal" style="width:min(560px,100%)">
      <h2 style="font-size:18px;margin-bottom:14px;word-break:keep-all">이번 계절에 친선전을 진행하지 않겠습니까?</h2>
      <div class="btnrow"><button class="btn primary" data-fdno>취소</button>
        <button class="btn" data-fdyes style="border-color:var(--bad);color:var(--bad)">전부 거절</button></div>
    </div>`;
  root.appendChild(box);
  const no = box.querySelector("[data-fdno]");
  no.onclick = ()=> box.remove();
  box.querySelector("[data-fdyes]").onclick = ()=>{ box.remove(); onYes(); };
  no.focus();                                                    // 키보드 — Enter 를 한 번 더 눌러도 거절되지 않게
}
'''

OLD = '''      $("#fDecline").onclick = ()=>{ F.slots=[null,null,null]; UI.fsel=null; F.answered=true;
        logE(`친선전 — 세 학원의 요청을 모두 거절했다.`,"");
        save(); closeModal(); showCeremony(); };
'''
NEW = '''      $("#fDecline").onclick = ()=> friendlyDeclineAsk(()=>{ F.slots=[null,null,null]; UI.fsel=null; F.answered=true;   // 1007 — 한 번 더 묻는다
        logE(`친선전 — 세 학원의 요청을 모두 거절했다.`,"");
        save(); closeModal(); showCeremony(); });
'''


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:80]))
    return src.replace(old, new)


def apply(src):
    if MARK in src:
        return src
    src = sub1(src, OLD, NEW)
    src = sub1(src, "function showCeremony(){\n", FN + "function showCeremony(){\n")
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
