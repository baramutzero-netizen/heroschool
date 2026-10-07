"""학원 이름이 두 줄을 넘으면 글자를 줄인다 (1007) — 몇 번을 돌려도 같은 결과.

    python3 apply_acadfit.py <game.html>

가로 화면 사이드의 학원 이름이 3줄 이상이 되면 사이드가 길어져 스케줄의 잉크 단지 · 깃펜을 가린다.
두 줄에 들어가는 가장 큰 크기까지 비례로 줄인다 (도트 폰트도 같은 방식)."""
import sys

MARK = "function acadNameFit("
OLD = "  if(px){ set(12); return; }\n"


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:80]))
    return src.replace(old, new)


FN = '''/* 학원 이름 (1007) — 두 줄을 넘으면 두 줄에 들어가는 크기까지 글자를 비례로 줄인다
   (가로 화면 사이드가 길어져 스케줄의 잉크 단지 · 깃펜을 가리지 않게). 도트 폰트도 같은 방식 — 12 · 24px 사이 크기는 조금 흐리게 보인다.
   이름 · 글꼴 · 칸 폭이 그대로면 다시 재지 않는다 */
const ACAD_FIT = {key:"", t:0};
function acadNameFit(){
  const el = $("#acadName"); if(!el) return;
  const px = document.documentElement.dataset.font === "pixel", key = el.textContent + "|" + px + "|" + el.clientWidth;
  if(key === ACAD_FIT.key) return;
  el.style.removeProperty("font-size"); el.style.removeProperty("line-height");
  if(!el.clientWidth){ ACAD_FIT.key = ""; return; }                  // 숨겨진 화면 — 보일 때 다시
  ACAD_FIT.key = key;
  const cs = getComputedStyle(el), f0 = parseFloat(cs.fontSize), r = (parseFloat(cs.lineHeight) || f0 * 1.25) / f0;
  const fits = (f)=> el.scrollHeight <= f * r * 2 + 2;
  if(fits(f0)) return;
  const set = (f)=>{ el.style.setProperty("font-size", f + "px", "important"); el.style.setProperty("line-height", (f * r) + "px", "important"); };
  let lo = 10, hi = f0;                                              // 두 줄에 드는 가장 큰 크기 (반 px 단위)
  for(let i = 0; i < 9 && hi - lo > .25; i++){ const m = (lo + hi) / 2; set(m); if(fits(m)) lo = m; else hi = m; }
  set(Math.floor(lo * 2) / 2);
}
if(document.fonts && document.fonts.ready) document.fonts.ready.then(()=>{ ACAD_FIT.key = ""; acadNameFit(); });   // 글꼴을 다 받은 뒤 다시 잰다
addEventListener("resize", ()=>{ clearTimeout(ACAD_FIT.t); ACAD_FIT.t = setTimeout(()=>{ ACAD_FIT.key = ""; acadNameFit(); }, 150); });
'''


def apply(src):
    if MARK in src:
        return src.replace(OLD, "")                                   # 앞판(도트 폰트는 12px) → 비례
    src = sub1(src, '  $("#acadName").textContent = S.acadName;\n',
               '  $("#acadName").textContent = S.acadName; acadNameFit();   // 1007 — 두 줄을 넘으면 글자를 줄인다\n')
    src = sub1(src, 'function renderMission(){\n', FN + 'function renderMission(){\n')
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
