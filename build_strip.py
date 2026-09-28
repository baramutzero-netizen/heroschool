"""배포 빌드에서 테스트 기능을 뺀다 (0927) — wrap.py · wrap_site.py 가 함께 쓴다.

game.html(개발본)에는 그대로 남기고, heroschool.html · site/index.html 에서만 걷어낸다.
· 진행 페이지 테스트 모드 (양피지 책) — CHRONICLE_CSS / CHRONICLE_JS 블록 전체(책 그림 · 장식 · 손글씨 글꼴 포함)와
  설정의 켜기 칸. 게임이 부르는 viewPlan · bindChronicle · chronicleAdvance 는 원래 화면으로 가는 껍데기만 남긴다.
· 애니메이션 테스트 — AVATAR_LAB 블록 전체와 설정의 열기 칸.
"""
import re

CHRON_JS_STUB = ("/* CHRONICLE_JS_START */\n"
                 "/* 배포 빌드 — 진행 페이지 테스트 모드는 빠져 있다 (build_strip.py) */\n"
                 "function viewPlan(){ return viewPlanClassic(); }\n"
                 "function bindChronicle(){}\n"
                 "function chronicleAdvance(button){ runWithReport(); }\n"
                 "/* CHRONICLE_JS_END */\n")
AVATAR_STUB = ("/* AVATAR_LAB_START */\n"
               "/* 배포 빌드 — 애니메이션 테스트는 빠져 있다 (build_strip.py) */\n"
               "function openAvatarLab(){}\n"
               "/* AVATAR_LAB_END */")


def _cut(src, start, end, repl, name):
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end) + (r"\r?\n" if end.endswith("*/") and name == "chron-js" else ""), re.S)
    new, n = pat.subn(lambda _: repl, src, count=1)
    if n != 1:
        raise RuntimeError(f"build_strip: {name} 블록을 찾지 못했다")
    return new


def _cut_panel(src, title, name):
    pat = re.compile(r'<section class="panel"><div class="optrow"><div class="optlab"><b>' + re.escape(title) + r'</b>.*?</section>', re.S)
    new, n = pat.subn("", src, count=1)
    if n != 1:
        raise RuntimeError(f"build_strip: 설정의 {name} 칸을 찾지 못했다")
    return new


def strip_dev(src):
    before = len(src)
    src = _cut(src, "/* CHRONICLE_CSS_START */", "/* CHRONICLE_CSS_END */", "", "chron-css")
    src = _cut(src, "/* CHRONICLE_JS_START */", "/* CHRONICLE_JS_END */", CHRON_JS_STUB, "chron-js")
    src = _cut(src, "/* AVATAR_LAB_START */", "/* AVATAR_LAB_END */", AVATAR_STUB, "avatar")
    src = _cut_panel(src, "진행 페이지 테스트 모드", "진행 페이지 테스트 모드")
    src = _cut_panel(src, "애니메이션 테스트", "애니메이션 테스트")
    print(f"build_strip: 테스트 기능 제외 -{(before-len(src))/1e6:.2f}MB")
    return src
