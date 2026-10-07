"""고른 칸(.opt.sel) 강조선 (1007) — 몇 번을 돌려도 같은 결과.

    python3 apply_optsel.py <game.html>

도트 마감(html[data-ui-finish="pixel"])의 button · .opt 테두리 규칙이 .opt.sel 을 덮어서
원정 파견 팝업의 원정지 · 팀이 고른 것과 안 고른 것이 똑같이 보였다 (리그 출전 칸 · 바꿀 유물 칸도 같은 규칙).
고른 칸에 진한 테두리 + 바깥 금빛 선을 두른다. 민트 팔레트는 초록빛 선."""
import sys

MARK = "/* 1007 — 고른 칸(.opt.sel) 강조선"
ANCHOR = 'html[data-ui-finish="pixel"] [aria-pressed="true"] {outline:2px solid #bc8a3a;outline-offset:2px}\n'
CSS = '''/* 1007 — 고른 칸(.opt.sel) 강조선. 도트 마감의 button · .opt 테두리 규칙이 .opt.sel 을 덮어서 원정 파견의 원정지 · 팀
   (리그 출전 칸 · 바꿀 유물 칸도)이 고른 것과 안 고른 것이 똑같이 보였다 — 진한 테두리 + 한 칸 띄운 바깥 금빛 선 */
html[data-ui-finish="pixel"] body :is(#modalRoot,#view) .opt.sel {
  --sel-ring:#c8902e;--sel-gap:#f6e7c4;
  border-color:#3a2716!important;background-color:#f1d48c40!important;
  box-shadow:inset 2px 2px #fff0c980,inset -2px -2px #60422140,0 2px #30271e,0 0 0 2px var(--sel-gap),0 0 0 4px var(--sel-ring)!important;
}
html[data-ui-finish="pixel"][data-ui-palette="mint"] body :is(#modalRoot,#view) .opt.sel {--sel-ring:#34826a;--sel-gap:#f0fff6;border-color:#226754!important;background-color:#26745c20!important}
'''


def apply(src):
    if MARK in src:
        return src
    n = src.count(ANCHOR)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, ANCHOR[:80]))
    return src.replace(ANCHOR, ANCHOR + CSS)


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
