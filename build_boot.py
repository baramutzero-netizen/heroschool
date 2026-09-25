"""첫 접속 로딩 화면 (0925) — wrap.py · wrap_site.py 가 함께 쓴다.

파일 하나가 18MB 가 넘어서 처음 접속하면 다 받을 때까지 몇 초에서 십수 초가 걸린다.
· 로딩 화면을 <body> 바로 뒤에 넣는다 — 앞쪽 몇 KB 만 받아도 바로 그려진다.
· head 에 박혀 있던 글꼴(@font-face data:) 은 파일 맨 뒤로 옮긴다 — head 의 CSS 를 다 받아야
  첫 화면이 그려지는데, 글꼴 두 개가 1.6MB 라서 그동안 빈 화면이었다.
로딩 화면은 게임의 boot() 가 시작할 때 걷어낸다.
"""
import re

LOADER = '''<div id="bootLoader" role="status" aria-live="polite">
<style>
#bootLoader{position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px;
  background:var(--bg,#EBE9EF);color:var(--text,#191A24);font-family:system-ui,-apple-system,"Malgun Gothic","Apple SD Gothic Neo",sans-serif;
  text-align:center;transition:opacity .25s ease}
#bootLoader.done{opacity:0;pointer-events:none}
#bootLoader .bl-in{max-width:360px;width:100%}
#bootLoader svg{width:56px;height:56px;margin-bottom:14px}
#bootLoader .bl-t{font-size:28px;font-weight:700;letter-spacing:-.02em;margin:0}
#bootLoader .bl-s{color:var(--brass,#8A6A15);font-size:14px;font-weight:600;letter-spacing:.14em;margin:6px 0 0}
#bootLoader .bl-bar{position:relative;height:4px;border-radius:2px;background:var(--line-soft,#DEDCE8);overflow:hidden;margin:26px auto 12px;max-width:240px}
#bootLoader .bl-bar i{position:absolute;top:0;bottom:0;left:-40%;width:40%;border-radius:2px;background:var(--brass-b,#B98E23);animation:blRun 1.3s ease-in-out infinite}
#bootLoader .bl-m{color:var(--muted,#5B5D72);font-size:13px;margin:0}
@keyframes blRun{0%{left:-40%}100%{left:100%}}
@media (prefers-reduced-motion:reduce){#bootLoader .bl-bar i{animation-duration:3s}}
</style>
<div class="bl-in">
<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 2 L35 7 V20 C35 29 28 35 20 38 C12 35 5 29 5 20 V7 Z" fill="none" stroke="var(--brass,#8A6A15)" stroke-width="1.4"/><path d="M20 10 V30 M14 15 L20 12 L26 15 M13 21 H27" fill="none" stroke="var(--brass,#8A6A15)" stroke-width="1.2"/></svg>
<p class="bl-t">용사 학원 키우기</p>
<p class="bl-s">학원이 망했다</p>
<div class="bl-bar"><i></i></div>
<p class="bl-m">불러오는 중…</p>
</div>
</div>
'''

FONT_RE = re.compile(r"@font-face\{[^{}]*?url\(data:font/[^)]*\)[^{}]*\}")


def boot_split(head, body):
    """head 에서 data: 글꼴을 빼고, body 앞에 로딩 화면을 붙인다. 반환: (head, body, tail)"""
    fonts = FONT_RE.findall(head)
    head = FONT_RE.sub("", head)
    tail = ('<style id="lateFonts">\n' + "\n".join(fonts) + "\n</style>") if fonts else ""
    return head, LOADER + body, tail
