"""오프닝 글 (1010) — 예전 APNG 아홉 장을 캔버스 글자(OPTX)로. 몇 번을 돌려도 같은 결과 (블록은 통째로 갈아 끼운다).

    python tools/gen/patch/apply_optx.py game.html      (저장소 맨 위에서)

· 코드 — optx_block.js 를 /* OPTX 시작 */ ~ /* OPTX 끝 */ 에 (function opReduced 바로 앞). 장면 9개의 글 · 효과 · 때(ms)가 다 이 파일에 있다
· 글꼴 — optx_fonts.css (나눔명조 ExtraBold OpTxSerif · 고운돋움 OpTxSans 조각 · data: woff2) 를 /* OPTX-FONTS 시작 … 끝 */ 에 (오프닝 CSS 바로 앞)
  오프닝 글을 바꾸면 optx_fonts.py 로 조각을 다시 만든다 (글자가 빠지면 대신 글꼴로 그려진다)
· 처음 한 번 고친 곳 (다시 돌려도 그대로) — OPENING 의 글 APNG 주소를 빼고 {ms, tail} 만 · openingPlay 의 APNG 미리 받기 → OPTX.prep()
  · apngImg(…) 다섯 곳 → OPTX.make(장면, 예전과 같은 클래스) · 오프닝 머리말
· 블록 지킴이(blockguard)에는 넣지 않았다 — game.html 쪽 OPTX 를 직접 고쳐도 다음 apply 가 블록 파일로 덮는다
"""
import os, sys, re
G = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
raw = open(G, "rb").read().decode("utf-8")
assert "\r\n" in raw
s = raw.replace("\r\n", "\n")
css = open(HERE + "optx_fonts.css", encoding="utf-8").read().strip()
js = open(HERE + "optx_block.js", encoding="utf-8").read().strip()
def once(old, new, cnt=1):
    global s
    n = s.count(old)
    if n != cnt: raise SystemExit(f"찾기 {n}번 (기대 {cnt}): {old[:70]!r}")
    s = s.replace(old, new)
# 1. 글꼴 (CSS) — 오프닝 CSS 바로 앞. 다시 돌리면 바꿔 끼운다
FB, FE = "/* OPTX-FONTS 시작 — 오프닝 글 글꼴 조각 (1010) */", "/* OPTX-FONTS 끝 */"
if FB in s:
    s = re.sub(re.escape(FB) + r".*?" + re.escape(FE), lambda m: FB + "\n" + css + "\n" + FE, s, flags=re.S)
else:
    once("/* 새 시나리오 오프닝 (1003) — 검은 화면 · 글(APNG) · 붉은빛 · 핏방울 · 대화 · 흰빛 */",
         FB + "\n" + css + "\n" + FE + "\n/* 새 시나리오 오프닝 (1003) — 검은 화면 · 글(캔버스 · 1010 전엔 APNG) · 붉은빛 · 핏방울 · 대화 · 흰빛 */")
# 2. 그리는 코드 — opReduced 바로 앞
JB, JE = "/* OPTX 시작 */", "/* OPTX 끝 */"
if JB in s:
    s = re.sub(re.escape(JB) + r".*?" + re.escape(JE), lambda m: JB + "\n" + js + "\n" + JE, s, flags=re.S)
else:
    once("function opReduced(){", JB + "\n" + js + "\n" + JE + "\nfunction opReduced(){")
# 3. OPENING — 글 APNG 주소를 빼고 길이 · 끝의 빈 시간만
if 'intro: {src:"assets/opening/intro.png' in s:
    rep = [
        (r'  intro: \{src:"assets/opening/intro\.png\?v=[0-9a-f]+", ms:29250\},[^\n]*', '  intro: {ms:29250, tail:300},                 // 글 — 캔버스 글자(OPTX · 1010 전엔 APNG) · 1004 사용자 새 글(‘왕국력 236년—’ … ‘모든 직업을 마스터한 인류 최강의 영웅’)'),
        (r'  rift: \{src:"assets/opening/rift\.png\?v=[0-9a-f]+", ms:19300\},[^\n]*', '  rift: {ms:19300, tail:300},                  // 시공이 휘몰아치는 글 (끝의 0.3초는 비어 있다)'),
        (r'  danger: \{src:"assets/opening/danger\.png\?v=[0-9a-f]+", ms:7000\},[^\n]*', "  danger: {ms:7000, tail:350},                 // '아, 이건 위험...' — rift 바로 뒤"),
        (r'  date: \{src:"assets/opening/date\.png\?v=[0-9a-f]+", ms:4700\},[^\n]*', "  date: {ms:4700, tail:300},                   // '—왕국력 230년, 가을' — 빛이 다 덮이고 시간 리와인드 소리가 끝난 뒤"),
        (r'  typer: \{src:"assets/opening/title-type\.png\?v=[0-9a-f]+", ms:5950\},[^\n]*', "  typer: {ms:5950, tail:300},                  // '용사 학원 키우기 / 학원이 망했다' 타자기 — 위 글이 사라지고 0.5초 뒤, 끝나면 아버지의 마지막 (1004 · 1005)"),
        (r'  dontsay: \{src:"assets/opening/dad-dontsay\.png\?v=[0-9a-f]+", ms:5050\},[^\n]*', "  dontsay: {ms:5050, tail:300},                // '그런 말 하지마.'"),
        (r'  dream: \{src:"assets/opening/dad-dream\.png\?v=[0-9a-f]+", ms:5050\},[^\n]*', "  dream: {ms:5050, tail:300},                  // '내 꿈은...'"),
        (r'  hero: \{src:"assets/opening/dad-hero\.png\?v=[0-9a-f]+", ms:5100\},[^\n]*', "  hero: {ms:5100, tail:300},                   // '자랑스러운 아빠 같은 영웅이 되고 싶은 거니까......'"),
        (r'  winter: \{src:"assets/opening/date-winter\.png\?v=[0-9a-f]+", ms:7400\}[^\n]*', "  winter: {ms:7400, tail:300}                   // '—왕국력 230년, 겨울 / 아버지가 돌아가셨다.'"),
    ]
    for pat, new in rep:
        n = len(re.findall(pat, s))
        if n != 1: raise SystemExit(f"OPENING {pat[:30]} {n}번")
        s = re.sub(pat, lambda m: new, s)
    once("  /* 아버지의 마지막 (1005) — 그림 둘(사용자 원본 1536x1024 PNG → WebP q78) · 한 번 도는 APNG 넷(사용자 원본 그대로 · 1280x720 · 끝 장은 비어 있다) */",
         "  /* 아버지의 마지막 (1005) — 그림 둘(사용자 원본 1536x1024 PNG → WebP q78) · 글 넷은 캔버스 글자 (OPTX · 1010 전엔 APNG) */")
# 4. 미리 받기 → 글꼴만
once('  apngBlob("opening", OPENING.intro); apngBlob("rift", OPENING.rift); apngBlob("danger", OPENING.danger); apngBlob("date", OPENING.date); apngBlob("typer", OPENING.typer);\n  ["dontsay","dream","hero","winter"].forEach(k=> apngBlob("dad_" + k, OPENING[k]));   // 아버지의 마지막 APNG 넷 (1005)\n',
     '  OPTX.prep();                        // 오프닝 글 글꼴 (1010 — 예전엔 APNG 아홉 장을 미리 받았다)\n') if 'apngBlob("opening", OPENING.intro)' in s else None
# 5. APNG 대신 캔버스
for old, new in [
    ('const img = await apngImg("opening", OPENING.intro, 9000);', 'const img = await OPTX.make("intro", "op-intro");'),
    ('const img = await apngImg("rift", OPENING.rift, 9000);', 'const img = await OPTX.make("rift", "op-intro op-rift");'),
    ('const im2 = await apngImg("danger", OPENING.danger, 4000);', 'const im2 = await OPTX.make("danger", "op-intro op-rift");'),
    ('const im = await apngImg(k, B, 3000);', 'const im = await OPTX.make(k, "op-date");'),
    ('const im = await apngImg("dad_" + k, B, 4000);', 'const im = await OPTX.make(k, "op-intro op-rift");'),
]:
    if old in s: once(old, new)
    else: assert new in s, new
# 6. 머리말
for old, new in [
    ("검은 화면에 글(APNG, 약 24초)", "검은 화면에 글(캔버스 글자 · 약 29초 · 1010 전엔 APNG)"),
    ("→ 시공이 휘몰아치는 글(APNG)\n   → '아, 이건 위험...'(APNG)", "→ 시공이 휘몰아치는 글\n   → '아, 이건 위험...'"),
    ("'—왕국력 230년, 가을'(APNG) → 글이 사라지고 0.5초 → 타자기 '용사 학원 키우기'(APNG · 글자마다 타자 소리) (1004)", "'—왕국력 230년, 가을' → 글이 사라지고 0.5초 → 타자기 '용사 학원 키우기'(글자마다 타자 소리) (1004)"),
    ("→ 대화와 APNG 셋이 번갈아 → '—왕국력 230년, 겨울'(APNG) →", "→ 대화와 글 셋이 번갈아 → '—왕국력 230년, 겨울' →"),
]:
    if old in s: once(old, new)
if "글은 모두 캔버스 글자(OPTX" not in s:
    once("   학원 이름은 프롤로그 끝에서 정하고, 정하면 빛이 걷히며 게임 화면.\n",
         "   학원 이름은 프롤로그 끝에서 정하고, 정하면 빛이 걷히며 게임 화면.\n   글은 모두 캔버스 글자(OPTX · 1010) — 예전 APNG 아홉 장(12.3MB)을 50ms 장마다 재서 효과 · 때를 옮겼다. 글꼴 조각 50KB.\n")
open(G, "wb").write(s.replace("\n", "\r\n").encode("utf-8"))
print("ok")
