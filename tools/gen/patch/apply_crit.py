"""전투 치명타 숫자를 조금 위에서 떠오르게 (1006) — 몇 번을 돌려도 같은 결과.

    python3 apply_crit.py <game.html>

· .pop.crit 에 margin-top — 큰 숫자가 보통 숫자 자리(머리 위)에 오고, CRITICAL!! 은 그 위로
  (CRITICAL!! 한 줄 25px + 숫자 크기 차이의 반. 48px 이면 39px 올라간다 · 폰은 숫자가 13px 라 21.5px)
· 무대 맨 윗줄 학생은 숫자가 무대 위로 잘리지 않게 덜 올린다 — popCritFit (그린 뒤 · 스타일리시 연출의 camPop 뒤)"""
import sys

MARK = "popCritFit"


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:80]))
    return src.replace(old, new)


def apply(src):
    if MARK in src:
        return src
    old = ".pop.crit  {color:#F2B200; font-size:48px}   /* 치명타 — 짙은 노랑 · 48px (0930) */"
    new = (".pop.crit  {color:#F2B200; font-size:48px; margin-top:calc(-15px - .5em)}   /* 치명타 — 짙은 노랑 · 48px (0930)"
           " · 조금 위에서 떠오른다 (1006 — 큰 숫자가 보통 숫자 자리에, CRITICAL!! 은 그 위로. 맨 윗줄은 popCritFit 이 덜 올린다) */")
    src = sub1(src, old, new)
    old = "function openBattle(res, opt, onDone){\n"
    new = ("/* 치명타 숫자 (1006) — CSS(.pop.crit margin-top)가 조금 위로 올린다. 무대 맨 윗줄 학생은 숫자가 무대 위로 잘리지 않게 덜 올린다\n"
           "   (떠오르는 동안 14px 더 올라가고 처음엔 1.18배로 커진다 — 그만큼 남긴다) */\n"
           "function popCritFit(root){\n"
           "  const stage = root && root.querySelector(\".bf-stage\");\n"
           "  const ps = stage ? stage.querySelectorAll(\".pop.crit\") : [];\n"
           "  if(!ps.length) return;\n"
           "  const top = stage.getBoundingClientRect().top;\n"
           "  ps.forEach(p=>{\n"
           "    const w = p.parentElement, u = w && w.parentElement;\n"
           "    if(!u || !u.offsetHeight) return;\n"
           "    const k = u.getBoundingClientRect().height / u.offsetHeight || 1;                  // 학생 크기 · 화면 배율 · 카메라\n"
           "    const up = -parseFloat(getComputedStyle(p).marginTop) || 0;                       // CSS 가 올린 만큼 (학생 안 px)\n"
           "    const room = (w.getBoundingClientRect().top - top) / k + (parseFloat(p.style.top) || 0) - 20;\n"
           "    if(up > room) p.style.marginTop = -Math.max(0, room) + \"px\";\n"
           "  });\n"
           "}\n"
           "function openBattle(res, opt, onDone){\n")
    src = sub1(src, old, new)
    old = "    modalLockSync();\n    alignDemonField();\n    const bs = $(\"#btscroll\");"
    new = ("    modalLockSync();\n    alignDemonField();\n"
           "    popCritFit($(\"#modalRoot\"));                                          // 치명타 숫자 — 맨 윗줄은 덜 올린다 (1006)\n"
           "    const bs = $(\"#btscroll\");")
    src = sub1(src, old, new)
    old = "    }).join(\"\")}</div>`);\n  };\n  const camBars = (F)=>{"
    new = ("    }).join(\"\")}</div>`);\n"
           "    popCritFit($(\"#modalRoot\"));\n"
           "  };\n  const camBars = (F)=>{")
    src = sub1(src, old, new)
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
