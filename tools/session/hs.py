#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용사 학원 — 클라우드 작업 공간 도우미 (1009 · 새 세션의 Claude 가 쓴다)

PC(D:\\heroschool)에서 받은(stage) 파일은 /mnt/user-data/uploads/heroschool/<경로> 에 PC 와 같은 모양으로 쌓인다.
그 사본으로 작업 폴더를 만들고 → 고치고 → 빌드 → 바뀐 파일만 골라 PC 에 쓸 목록(device_commit_files 입력)을 만든다.

  python3 hs.py list core patch          받을 파일 목록 — device_stage_files 의 paths 로 그대로 (50개씩) · 묶음: core patch counsel test placer rbook roster schedkit i18n
  python3 hs.py init                     지금까지 받은 파일 → 작업 폴더 ~/hs/work + PC 원본 ~/hs/base (+ 블록 지문)
  python3 hs.py sync                     나중에 더 받은 파일 반영 — PC 쪽이 바뀌었으면 3-way 병합
  python3 hs.py status                   PC 원본과 달라진 파일
  python3 hs.py diff [경로…]              바뀐 줄 (CRLF 무시 · 긴 줄은 자름)
  python3 hs.py apply cslwin [인자…]      작업 폴더에서 tools/gen/patch/apply_cslwin.py game.html [인자…]
  python3 hs.py build                    wrap.py → wrap_site.py (TZ=Asia/Seoul)
  python3 hs.py shot [옵션]               heroschool.html 을 띄워 스크린샷 · 오류 (http(s) 는 모두 막는다 — firebase 쓰기 불가)
  python3 hs.py i18n [--years 3]         영어판 시험 — 한국어가 변환 전과 같은지 · 영어 시험 단어가 보이는지 (tools/i18n/check_i18n.py · 빌드 뒤에)
  python3 hs.py layout [--only plan,…]    영어판 화면 점검 — 넘치거나 잘린 칸 (tools/i18n/check_layout.py · 빌드 뒤에 · 스크린샷 shots/layout)
  python3 hs.py mtimes game.html=1791…   PC mtime 기록 (stage 결과의 mtimeMs) — pack 이 expectedMtimeMs 로 쓴다
  python3 hs.py pack 이름                 바뀐 파일 → /mnt/user-data/outputs/이름_시각/ + 커밋 목록 (1차 · 2차)
  python3 hs.py done [경로=mtime…]        커밋이 끝났다 — 보낸 내용을 새 원본으로 (새 mtime 을 주면 기록, 안 주면 지운다)
  python3 hs.py verify [경로=mtime…]      다시 받은(stage) PC 파일과 보낸 것을 비교(그림은 픽셀)한 뒤 done 과 같이
  python3 hs.py resolve 경로              sync 충돌을 손으로 고친 뒤 '해결됨' 표시

mtime 은 경로=숫자 (경로는 저장소 기준 game.html · site/index.html 또는 PC 경로) 로 주거나,
stage / list 결과 JSON 을 파일(또는 - 로 표준 입력)로 줘도 된다 (list 결과는 --dir 'D:\\heroschool\\site' 와 같이).
블록 지문(tools/gen/patch/blocks.sha.json)은 커밋하지 않는다 — init · sync 가 PC 것을 작업 폴더에 넣고(블록 지킴이가 읽는다),
작업 폴더에 이미 있으면 그대로 둔다 (이 세션의 apply 가 적은 지문을 지킨다).
환경 변수: HS_HOME(기본 ~/hs) · HS_DEVICE_ROOT(기본 D:\\heroschool) · HS_UPLOADS · HS_OUTPUTS
직접 쓰는 테스트 스크립트에서:  sys.path.insert(0, 이 폴더); import hs; b, pg, errs = await hs.open_game(p)
"""
import difflib, hashlib, json, os, re, shutil, subprocess, sys, time, urllib.parse

DEVICE_ROOT = os.environ.get("HS_DEVICE_ROOT", "D:\\heroschool").rstrip("\\")
UPLOADS = os.environ.get("HS_UPLOADS", "/mnt/user-data/uploads/heroschool")
OUTPUTS = os.environ.get("HS_OUTPUTS", "/mnt/user-data/outputs")
HOME = os.path.abspath(os.path.expanduser(os.environ.get("HS_HOME", "~/hs")))
WORK, BASE = os.path.join(HOME, "work"), os.path.join(HOME, "base")
THEIRS = os.path.join(HOME, "theirs")                   # sync 충돌 때 PC 쪽 사본
MT, LAST, CONF = (os.path.join(HOME, n) for n in ("mtimes.json", "last_pack.json", "conflicts.json"))
SHOTS = os.path.join(HOME, "shots")

FP = "tools/gen/patch/blocks.sha.json"     # 블록 지문 — 커밋하지 않는다(SKIP). 작업 폴더에는 put_fp 가 따로 넣는다
SKIP = re.compile(r"(^|/)(__pycache__|\.git)(/|$)|\.pyc$|\.merge$|\.orig$|^" + re.escape(FP) + "$")
IMG = (".png", ".webp", ".jpg", ".jpeg", ".gif")
AUD = (".mp3", ".ogg", ".wav")
TEXT = (".html", ".js", ".css", ".py", ".json", ".md", ".txt", ".csv", ".cjs", ".mjs", ".lua", ".svg")
MAX_FILE = 20 * 1024 * 1024          # 사용자 규칙 — 파일 하나 20MB 까지
MAX_CALL_FILES, MAX_CALL_BYTES = 50, 95 * 1024 * 1024

# ── 받을 파일 묶음 (1008 기준 PC 목록 — 바뀌었으면 device_list_dir 로 확인) ──────────────────────
JOBS = ["archer", "bard", "darkpriest", "druid", "enchanter", "forcemage", "gunner", "monk", "ninja", "paladin",
        "priest", "rogue", "spellsword", "sword", "timemage", "wizard"]
PROPS = ["blotter", "book_pair", "book_stack", "candle", "candlestick", "coin_stack", "coin", "cookie_plate", "envelope",
         "globe", "hourglass_up", "ink_bottle", "inkwell_quill", "inkwell", "lamp", "open_book", "paper_stack",
         "paperweight", "pen", "plant", "pocket_watch", "pouch", "rolled_map", "spectacles", "teacup", "teapot", "vase_flowers"]
PATCH = ["apply_acadfit.py", "apply_crit.py", "apply_cslpers.py", "apply_cslwin.py", "apply_defy.py", "apply_desk.py",
         "apply_exped3.py", "apply_fdecline.py", "apply_job.py", "apply_lgfield.py", "apply_optsel.py", "apply_rookiefield.py",
         "apply_roster.py", "apply_sched.py", "apply_skgrade.py", "apply_tq.py", "apply_tqalign.py", "apply_tqcam.py", "apply_tqcenter.py",
         "apply_tqfield.py", "apply_tqgrow.py", "apply_tqmaps.py", "apply_tqui.py", "apply_tune.py", "apply_webp.py",
         "blockguard.py", "blocks.sha.json", "cslwin_block.css", "cslwin_block.js", "desk_art.py", "desk_layout.json",
         "mdesk_block.css", "mdesk_block.js", "roster_block.css", "roster_block.js",
         "apply_optx.py", "optx_block.js", "optx_fonts.css", "optx_fonts.py",
         "sched_art.py", "sched_block.css", "sched_block.js", "sched_layout.json"]
CW = "mockups/counsel-window/"
SR = "mockups/student-roster/"
SKILL_ICONS = {   # assets/skill-icons/<직업>/<이름>.webp — 직업마다 다섯 (일반 공격 · 스킬 둘 · 필살기 · 패시브)
    "archer": ["aimed-shot", "hawk-eye", "meteor", "pierce", "sniper"], "bard": ["dissonance", "harmony", "march", "pluck", "victory"],
    "darkpriest": ["curse", "drain", "pact-clean", "supper", "touch"], "druid": ["beast-form", "nature-recovery", "nature-wrath", "regen-seed", "thorn-whip"],
    "enchanter": ["all-rune", "magic-seal", "permanent-rune", "rune-shot", "weapon-rune"], "forcemage": ["body", "overcharge", "shatter-foot", "strike", "unseal"],
    "gunner": ["encore", "finale", "greeting", "knock", "waltz"], "monk": ["chi-wave", "circulation", "combo", "hundred-fists", "training"],
    "ninja": ["fuma", "kunai", "swamp", "water-dragon", "water-mirage"], "paladin": ["guardian-vow", "healing-light", "holy-strike", "protective-oath", "sanctuary"],
    "priest": ["blessing", "greater-heal", "holy-wave", "prayer", "revival"], "rogue": ["ambush", "assassinate", "poison", "shadow-step", "weakness"],
    "spellsword": ["arcane-slash", "awakening", "echo", "thousand-blades", "triple"], "sword": ["counter", "earth-cleaver", "iron-wall", "slash", "taunt"],
    "timemage": ["delay", "foresight", "haste", "time-shard", "time-stop"], "wizard": ["arcane-bolt", "fire-burst", "frost-field", "gravity", "resonance"],
}
PROFILES = {
    # 빌드에 늘 필요한 것 + 이 도우미 (빌드 결과물도 받는다 — 바뀐 그림 판정 · 커밋 mtime)
    "core": ["game.html", "heroschool.html", "site/index.html", "site/version.json", "wrap.py", "wrap_site.py",
             "split_assets.py", "build_boot.py", "build_guard.py", "build_strip.py",
             "tools/session/HANDOFF.md", "tools/session/hs.py"]
            + ["tools/i18n/" + f for f in ("i18n_build.py", "i18n_runtime.js", "config.json", "en.json", "check_i18n.py", "check_layout.py", "check_save.py", "todo_en.py",
                                           "en_layout.css", "en_layout_rbook.css")]
            + ["tools/i18n/en/%s.json" % n for n in ("battle", "core", "data", "dialogue", "log", "names", "opening", "story", "tut", "ui")],   # 영어판 (1010) — 빌드가 읽는다 · en/ 는 2단계(화면) · 3단계(data · names) · 4단계(dialogue · story · opening) 표
    # tools/gen/patch 의 apply 스크립트 · 블록 · 배치 (desk_out 그림은 빼고 — apply_desk 로 다시 구울 때만 따로)
    "patch": ["tools/gen/README.md"] + ["tools/gen/patch/" + f for f in PATCH],
    # 학생 도트 · 전투 이펙트가 그려지게 (게임 테스트용 — 다른 그림은 없어도 돈다)
    "test": ["assets/spr_img.webp.js", "assets/fx_img.webp.js"] + ["assets/spr_x_img/%s.png.js" % j for j in JOBS]
            + ["assets/spr_x_img/demonking.webp.js"],
    # apply_cslwin 이 읽는 상담창 그림 · 배치
    "counsel": [CW + "README.md", CW + "src/compose_desk.py"]
               + [CW + "art/" + f for f in ("bg.webp", "desk.png", "desk_plain.png", "desk_layout.json", "props.json")]
               + [CW + "art/props/%s.png" % n for n in PROPS],
    # 상담 목업 · 책상 배치판을 다시 만들 때 (core · counsel 과 같이 — game.html 의 글꼴 · 대사 표를 읽는다)
    "placer": [CW + "counsel_desk_placer.html", CW + "counsel_mockup.html", CW + "art/desk_props.png"]
              + [CW + "src/" + f for f in ("bg_make.py", "build_mockup.py", "build_placer.py", "desk_persp.py", "mockup_tpl.html",
                                           "placer_tpl.html", "props_counsel.py", "props_render.py", "spr_strip.py")]
              + [CW + "art/spr_%s.png" % j for j in JOBS]
              + ["assets/student-portraits-v2/%s-512.png" % j for j in JOBS],      # 목업의 학생 얼굴 (build_mockup)
    # apply_roster 가 읽는 학생 명부 책 (1009) — 목업 원본의 CSS · HTML(roster_tpl.html) · 책 그림 · 배치. patch 와 같이
    "rbook": [SR + f for f in ("src/roster_tpl.html", "art/book.png", "art/ribbon.png", "art/roster_layout.json")],
    # apply_sched 가 두루마리 그림을 굽는 재료 (1010 · patch 와 같이) — kit 모듈 · 소품 시트 · 글꼴. 지금 배치(sched_layout.json)의 소품만 —
    # 배치에 다른 소품을 넣었으면 tools/gen/kit/out3/props/<이름>.png 도 받는다. 그림은 바이트 단위로 같게 나온다 (?v= 그대로)
    "schedkit": ["tools/gen/kit/" + f for f in ("compose3.py", "desk_top.py", "props3d.py", "px3d.py", "scene2d.py", "schedule_mock.py",
                                                "schedule_mock2.py", "cache/rollers_24_582_14_451.png", "cache/rollers_24_582_14_451.png.json",
                                                "out3/desk_bg.png", "out3/frame_1x.png", "out3/props.json")]
                + ["tools/gen/kit/out3/props/%s.png" % n for n in ("inkwell", "knob_bottom", "paperweight", "quill", "runner")]
                + ["tools/gen/fonts/" + f for f in ("Galmuri7.woff", "Galmuri9.woff", "Galmuri11.woff", "Galmuri11-Bold.woff", "Galmuri14.woff",
                                                     "mulmaru.woff2", "mulmaru_mono.woff2")],
    # 학생 명부 목업 · 배치판 (1009 · core 와 같이) — 결과물(목업 · 배치판 HTML)도 받는다: 다시 구운 것을 덮어쓸 때 mtime 으로 지킨다
    "roster": [SR + f for f in ("README.md", "roster_mockup.html", "roster_placer.html", "art/book.png", "art/ribbon.png", "art/desk_bg.png",
                                "art/sample_roster.json", "art/roster_layout.json")]
              + [SR + "src/" + f for f in ("book_art.py", "build_mockup.py", "build_placer.py", "roster_build.py", "sample_roster.py",
                                           "roster_tpl.html", "placer_tpl.html")]
              + ["assets/mdesk_art/%s.webp" % k for k in ("base", "items", "props", "vig")]
              + ["assets/student-portraits-v2/%s-512.png" % j for j in JOBS]
              + ["assets/skill-icons/frame-%s.webp" % g for g in ("D", "C", "B", "A", "S", "EX")]
              + ["assets/skill-icons/%s/%s.webp" % (j, n) for j in JOBS for n in SKILL_ICONS[j]],
    # 영어판 글 목록을 다시 뽑을 때 (1010 · core 와 같이) — extract_ko.cjs 는 acorn 이 필요하다 (저장소 밖에서 npm i acorn acorn-walk)
    # 영어 공유 미리보기(og_en.py → site/og-en.png · en/index.html)를 다시 만들 때도 (5단계)
    "i18n": ["tools/i18n/README.md", "tools/i18n/extract_ko.cjs", "tools/i18n/classify_ko.py",
             "tools/i18n/og_en.py", "site/og-en.png", "en/index.html"],
}


# ── 도움 함수 ────────────────────────────────────────────────────────────────
def die(msg):
    print("멈춤 —", msg)
    sys.exit(1)


def dev_of(rel):
    return DEVICE_ROOT + "\\" + rel.replace("/", "\\")


def rel_of(path):
    """PC 경로(D:\\heroschool\\…) 또는 저장소 기준 경로 → 저장소 기준 경로(a/b.c)"""
    p = path.strip().strip('"').replace("/", "\\")
    if p.lower().startswith(DEVICE_ROOT.lower() + "\\"):
        p = p[len(DEVICE_ROOT) + 1:]
    elif re.match(r"^[A-Za-z]:\\", p):
        die("PC 경로가 %s 아래가 아니다: %s" % (DEVICE_ROOT, path))
    return p.replace("\\", "/").lstrip("/")


def jload(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def jsave(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)


def parse_mtimes(args):
    """경로=mtime · stage/list 결과 JSON 파일(- 는 표준 입력) → {경로: mtime}. list 결과는 --dir 로 그 폴더를 알려 준다"""
    out, dec, d = {}, json.JSONDecoder(), None
    it = iter(args)
    for a in it:
        if a == "--dir":
            d = next(it, None)
            continue
        if "=" in a and not a.lower().endswith(".json"):
            k, v = a.rsplit("=", 1)
            out[rel_of(k)] = int(float(v))
            continue
        text = sys.stdin.read() if a == "-" else open(a, encoding="utf-8").read()
        i = 0
        while True:
            while i < len(text) and text[i] in " \t\r\n,":
                i += 1
            if i >= len(text):
                break
            obj, i = dec.raw_decode(text, i)
            if isinstance(obj, dict) and "entries" in obj:            # device_list_dir 결과
                if not d:
                    die("list 결과에는 --dir 'D:\\heroschool\\…' 가 필요하다")
                pre = rel_of(d)
                for e in obj["entries"]:
                    if e.get("type") == "file" and "mtimeMs" in e:
                        out[(pre + "/" if pre else "") + e["name"].replace("\\", "/")] = int(e["mtimeMs"])
            else:                                                       # device_stage_files 결과
                for e in (obj.get("staged", []) if isinstance(obj, dict) else obj):
                    if isinstance(e, dict) and e.get("devicePath") and e.get("ok", True) and "mtimeMs" in e:
                        out[rel_of(e["devicePath"])] = int(e["mtimeMs"])
    return out


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)


def sha(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def pixels_same(a, b):
    try:
        from PIL import Image
        with Image.open(a) as x, Image.open(b) as y:
            return x.size == y.size and x.convert("RGBA").tobytes() == y.convert("RGBA").tobytes()
    except Exception:
        return False


def same(a, b):
    """같은 내용인가 — 그림은 픽셀이 같으면 같다 (PC 가 C2PA 정보를 붙여도)"""
    if not (os.path.exists(a) and os.path.exists(b)):
        return False
    if os.path.getsize(a) == os.path.getsize(b) and sha(a) == sha(b):
        return True
    return a.lower().endswith(IMG) and pixels_same(a, b)


def walk(top):
    for root, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), top).replace(os.sep, "/")
            if not SKIP.search(rel):
                yield rel


def settle(top, t=30):
    """막 받은 파일이 다 내려올 때까지 (크기가 1초 동안 그대로면)"""
    def sizes():
        return {r: os.path.getsize(os.path.join(top, r)) for r in walk(top)} if os.path.isdir(top) else {}
    a, end = sizes(), time.time() + t
    while time.time() < end:
        time.sleep(1)
        b = sizes()
        if a == b:
            return b
        a = b
    return a


def run(cmd, env=None):
    print("$", " ".join(cmd))
    r = subprocess.run(cmd, cwd=WORK, env=env)
    if r.returncode:
        die("실패 (%d): %s" % (r.returncode, " ".join(cmd)))


# ── 받기 · 맞추기 ─────────────────────────────────────────────────────────────
def ingest(rels=None):
    """받은 사본(UPLOADS) → 원본(BASE) · 작업(WORK). PC 쪽이 바뀐 파일은 작업 폴더로 넘기거나 병합한다"""
    have = settle(UPLOADS)
    asked = False
    if rels:
        rels = [rel_of(r) for r in rels]
        asked = FP in rels
        rels = [r for r in rels if r != FP]                 # 블록 지문은 끝의 put_fp 가 따로
        miss = [r for r in rels if r not in have]
        if miss:
            die("받은 사본에 없다: " + ", ".join(miss))
    else:
        rels = sorted(have)
    mt, conf = jload(MT, {}), jload(CONF, {})
    st = {k: [] for k in ("new", "same", "updated", "merged", "conflict")}
    for rel in rels:
        src, b, w = os.path.join(UPLOADS, rel), os.path.join(BASE, rel), os.path.join(WORK, rel)
        if not os.path.exists(b):
            copy(src, b)
            if os.path.exists(w) and not same(w, src):
                st["conflict"].append(rel + " (작업 폴더에 먼저 만든 같은 이름 파일 — 둘을 견주어 고친 뒤 resolve)")
                conf[rel] = None
                copy(src, os.path.join(THEIRS, rel))
            else:
                copy(src, w)
                st["new"].append(rel)
            continue
        if same(src, b):
            st["same"].append(rel)
            continue
        mt.pop(rel, None)                       # PC 쪽이 바뀌었다 — 그 mtime 은 새로 받아야 한다
        if not os.path.exists(w) or same(w, b):
            copy(src, b); copy(src, w)
            st["updated"].append(rel)
        elif same(w, src):
            copy(src, b)
            st["same"].append(rel)
        else:                                   # 둘 다 바뀌었다 — 다른 세션이 PC 에서 고친 것과 이쪽 수정을 합친다
            keep = os.path.join(THEIRS, rel)
            copy(src, keep)
            if rel.lower().endswith(TEXT):
                r = subprocess.run(["git", "merge-file", "-p", "-L", "work", "-L", "base", "-L", "pc", w, b, keep],
                                   capture_output=True)
                if r.returncode == 0:
                    with open(w, "wb") as f:
                        f.write(r.stdout)
                    copy(keep, b)
                    st["merged"].append(rel)
                    continue
                with open(w + ".merge", "wb") as f:
                    f.write(r.stdout)
                st["conflict"].append(rel + " (충돌 %s곳 — %s.merge 를 보고 작업 파일을 고친 뒤 resolve)" % (r.returncode, rel))
            else:
                st["conflict"].append(rel + " (그림 · 바이너리 — 어느 쪽을 쓸지 정해 작업 파일에 둔 뒤 resolve)")
            conf[rel] = None
    jsave(MT, mt)
    jsave(CONF, conf)
    for k, label in (("new", "새로 받음"), ("updated", "PC 쪽이 바뀌어 작업 폴더도 갱신"), ("merged", "PC 수정과 병합됨"),
                     ("same", "그대로"), ("conflict", "충돌")):
        v = st[k]
        if v:
            if len(v) > 12 and k in ("new", "same"):
                print("%s %d개" % (label, len(v)))
            else:
                print("%s %d개:\n  " % (label, len(v)) + "\n  ".join(v))
    if st["updated"] or st["merged"]:
        print("※ PC 쪽이 바뀐 파일은 mtime 을 지웠다 — 커밋 전에 그 stage 결과의 mtimeMs 를 hs.py mtimes 로")
    if st["conflict"]:
        print("※ 충돌을 먼저 처리한다 (해결 전에는 pack 이 멈춘다)")
    put_fp(asked)


def put_fp(asked=False):
    """블록 지문(FP)은 SKIP 이라 ingest 가 건너뛴다 — 블록 지킴이가 읽도록 PC 것을 작업 폴더에 넣는다 (1009).
    작업 폴더에 이미 있으면 그대로 둔다 — 이 세션의 apply 가 적은 지문을 PC 의 옛 지문으로 덮으면 다음 apply 가 괜히 멈춘다.
    지문이 없거나 깨져 있으면 블록 지킴이는 아무 말 없이 통과시키므로, patch 를 받았는데 못 넣었으면 알린다."""
    src, w = os.path.join(UPLOADS, FP), os.path.join(WORK, FP)
    if os.path.exists(w):
        if asked:
            print("블록 지문: 작업 폴더에 이미 있어 그대로 둠 — PC 것으로 바꾸려면 작업 폴더의 것을 지우고 다시 sync")
        return
    want = os.path.isdir(os.path.dirname(w))            # patch 를 받았다 — 지문이 있어야 한다
    missing = True
    for i in range(4 if want else 1):                   # 받은 파일은 1초쯤 늦게 나타난다 · 반쯤 내려온 파일은 넣지 않는다
        if i:
            time.sleep(1)
        try:
            with open(src, encoding="utf-8") as f:
                d = json.load(f)
            if not isinstance(d, dict):
                raise ValueError("블록 이름 → 지문 표가 아니다")
            copy(src, w)
            print("블록 지문: PC 의 %s 를 작업 폴더에 넣음 (블록 %d개 · 커밋하지 않는다)" % (FP, len(d)))
            return
        except FileNotFoundError:
            missing = True
        except ValueError:
            missing = False
    if missing and want:
        print("※ 블록 지문(%s)을 받지 않았다 — 블록 지킴이가 첫 apply 를 그냥 통과시킨다 (patch 묶음에 들어 있다)" % FP)
    elif not missing:
        print("※ 블록 지문(%s)이 JSON 으로 읽히지 않아 넣지 않았다 — 블록 지킴이가 첫 apply 를 그냥 통과시킨다" % FP)


def cmd_list(names):
    names = names or ["core"]
    rels = []
    for n in names:
        if n not in PROFILES:
            die("묶음 이름: " + " · ".join(PROFILES))
        rels += [r for r in PROFILES[n] if r not in rels]
    print("# %s — %d개. device_stage_files 의 paths 에 한 줄씩 그대로"
          " (없는 파일이 하나라도 있으면 그 호출 전체가 실패한다 — 그 경로만 빼고 다시)" % (" + ".join(names), len(rels)))
    for i in range(0, len(rels), MAX_CALL_FILES):
        print(json.dumps([dev_of(r) for r in rels[i:i + MAX_CALL_FILES]], ensure_ascii=False))


def cmd_init(args):
    if os.path.exists(WORK) and "--reset" not in args:
        die("작업 폴더가 이미 있다 (%s) — 더 받은 파일은 sync, 처음부터 다시는 init --reset" % WORK)
    for p in (WORK, BASE, THEIRS):
        shutil.rmtree(p, ignore_errors=True)
    for p in (MT, LAST, CONF):
        if os.path.exists(p):
            os.remove(p)
    os.makedirs(WORK, exist_ok=True)
    ingest()
    print("작업 폴더:", WORK)


def cmd_mtimes(args):
    new = parse_mtimes(args)
    if not new:
        die("기록할 mtime 이 없다 (경로=숫자 또는 stage 결과 JSON)")
    mt = jload(MT, {})
    mt.update(new)
    jsave(MT, mt)
    print("mtime %d개 기록:" % len(new), ", ".join(sorted(new)[:12]) + (" …" if len(new) > 12 else ""))


def cmd_resolve(rels):
    conf = jload(CONF, {})
    for r in rels:
        rel = rel_of(r)
        if rel not in conf:
            die("충돌 목록에 없다: " + rel)
        copy(os.path.join(THEIRS, rel), os.path.join(BASE, rel))
        conf.pop(rel)
        m = os.path.join(WORK, rel + ".merge")
        if os.path.exists(m):
            os.remove(m)
        print("해결됨:", rel, "— 원본은 PC 최신본, 작업 파일은 지금 그대로 (mtime 은 그 stage 결과로 hs.py mtimes)")
    jsave(CONF, conf)


# ── 바뀐 파일 ────────────────────────────────────────────────────────────────
_vcache = {}


def _asset_v(tree, rel):
    """heroschool.html 이 이 그림을 어떤 ?v= 로 부르는가 (파일이 없으면 '?', 부르지 않으면 None)"""
    path = os.path.join(tree, "heroschool.html")
    if path not in _vcache:
        _vcache[path] = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    s = _vcache[path]
    if s is None:
        return "?"
    m = re.search(re.escape(rel) + r"\?v=([0-9A-Za-z_-]+)", s)
    return m.group(1) if m else None


def changed():
    """([(종류, 경로)], 같은 그림 수) — M 바뀜(PC 에 있음) / A 새 파일 / D 빌드가 새로 뺀 그림(PC 의 것과 ?v= 가 다름)"""
    _vcache.clear()
    out, same_assets = [], 0
    for rel in sorted(walk(WORK)):
        w, b = os.path.join(WORK, rel), os.path.join(BASE, rel)
        if os.path.exists(b):
            if not same(w, b):
                out.append(("M", rel))
        elif rel.startswith("assets/"):
            vn, vo = _asset_v(WORK, rel), _asset_v(BASE, rel)
            if vn is None:
                continue                                  # 빌드가 부르지 않는 그림 — 올리지 않는다
            if vo not in ("?", None) and vo == vn:
                same_assets += 1                          # PC 의 heroschool.html 도 같은 ?v= → PC 에 같은 그림이 있다
                continue
            out.append(("D", rel))
        else:
            out.append(("A", rel))
    return out, same_assets


def eol_warn(rel):
    b, w = os.path.join(BASE, rel), os.path.join(WORK, rel)
    if not (rel.lower().endswith(TEXT) and os.path.exists(b)):
        return None
    bb, wb = open(b, "rb").read(), open(w, "rb").read()
    crlf = bb.count(b"\r\n") > bb.count(b"\n") // 2
    if crlf and wb.count(b"\n") != wb.count(b"\r\n"):
        return "줄바꿈 섞임 — 원래 CRLF 인데 LF 줄이 %d개" % (wb.count(b"\n") - wb.count(b"\r\n"))
    if not crlf and wb.count(b"\r\n"):
        return "줄바꿈 섞임 — 원래 LF 인데 CRLF 줄이 %d개" % wb.count(b"\r\n")
    return None


def cmd_status(_):
    if not os.path.exists(WORK):
        die("작업 폴더가 없다 — 먼저 init")
    ch, sa = changed()
    conf, mt = jload(CONF, {}), jload(MT, {})
    print("작업 폴더 %s · 바뀐 파일 %d개%s" % (WORK, len(ch), (" · 빌드가 뺀 그림 중 PC 와 같은 것 %d개(올리지 않음)" % sa) if sa else ""))
    for k, rel in ch:
        tag = {"M": "바뀜", "A": "새 파일", "D": "그림(빌드)"}[k]
        warn = eol_warn(rel) if k == "M" else None
        need = "  (mtime 없음)" if k == "M" and rel not in mt else ""
        print("  %s  %s%s%s" % (tag, rel, need, ("   ⚠ " + warn) if warn else ""))
    if conf:
        print("충돌 해결 전:", ", ".join(conf))


def cmd_diff(args):
    allv = "--all" in args
    rels = [rel_of(a) for a in args if a != "--all"] or [r for k, r in changed()[0] if k == "M"]
    budget = 10 ** 9 if allv else 400
    for rel in rels:
        b, w = os.path.join(BASE, rel), os.path.join(WORK, rel)
        if not rel.lower().endswith(TEXT):
            print("##", rel, "(텍스트가 아니라 생략)")
            continue
        a = open(b, encoding="utf-8", errors="replace").read().replace("\r\n", "\n").split("\n") if os.path.exists(b) else []
        c = open(w, encoding="utf-8", errors="replace").read().replace("\r\n", "\n").split("\n")
        print("##", rel)
        for line in difflib.unified_diff(a, c, "pc", "work", n=0, lineterm=""):
            if line.startswith(("---", "+++")):
                continue
            print(line[:220] + (" …(%d자)" % len(line) if len(line) > 220 else ""))
            budget -= 1
            if budget <= 0:
                print("… (더 보려면 --all)")
                return


# ── 빌드 ────────────────────────────────────────────────────────────────────
def cmd_apply(args):
    if not args:
        die("apply 이름 [인자…]  (예: apply cslwin)")
    script = "tools/gen/patch/apply_%s.py" % args[0]
    if not os.path.exists(os.path.join(WORK, script)):
        die("없다: %s — patch 묶음을 받았는지 (hs.py list patch · apply roster 는 rbook 도)" % script)
    run([sys.executable, script, "game.html"] + args[1:])


def cmd_build(_):
    env = dict(os.environ, TZ="Asia/Seoul")
    run([sys.executable, "wrap.py"], env)
    run([sys.executable, "wrap_site.py"], env)
    # 1009 — 리눅스의 wrap 은 LF 로 쓴다. PC(윈도우)에서 구운 것은 CRLF 라 PC 원본과 줄바꿈을 맞춘다 (.gitattributes text=auto 라 git 내용은 같다)
    for rel in ("heroschool.html", "site/index.html"):
        b, w = os.path.join(BASE, rel), os.path.join(WORK, rel)
        if os.path.exists(b) and os.path.exists(w):
            bb, wb = open(b, "rb").read(), open(w, "rb").read()
            if bb.count(b"\r\n") > bb.count(b"\n") // 2 and b"\r\n" not in wb:
                open(w, "wb").write(wb.replace(b"\n", b"\r\n"))
                print("줄바꿈 CRLF 로 (PC 와 같게):", rel)
    v = jload(os.path.join(WORK, "site", "version.json"), {})
    print("빌드", v.get("build"))


# ── 테스트 (Playwright · 크로미움은 미리 깔려 있다) ──────────────────────────────
class Errs(list):
    """콘솔 · 페이지 오류 + .missing (작업 폴더에 없어서 못 읽은 파일 — 저장소 기준 경로)"""
    def __init__(self):
        super().__init__()
        self.missing = set()


async def open_game(p, w=1280, h=800, page="heroschool.html", dsf=1, title=False):
    """게임을 띄워 시작 화면을 닫고 홈으로 (title=True 면 시작 화면 그대로). 반환: (browser, page, errs)"""
    b = await p.chromium.launch()
    c = await b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dsf, locale="ko-KR")   # 한국어 브라우저 — 영어판 공개 뒤에도 ?lang=en 을 붙여야 영어
    await c.route(re.compile(r"^https?://"), lambda r: r.abort())      # 바깥 주소는 전부 막는다 (firebase · 글꼴)
    pg = await c.new_page()
    errs = Errs()

    def failed(r):
        if r.url.startswith("file://"):
            path = urllib.parse.unquote(r.url[7:].split("?")[0])
            if path.startswith(WORK + "/"):
                errs.missing.add(path[len(WORK) + 1:])
    pg.on("requestfailed", failed)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)[:300]))
    pg.on("console", lambda m: errs.append("console: " + m.text[:300]) if m.type == "error" else None)
    await pg.goto("file://" + os.path.join(WORK, page), wait_until="commit")
    await pg.wait_for_function("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0"
                               " && !document.getElementById('bootLoader')", polling=250, timeout=40000)
    if not title:
        await pg.evaluate("() => { try { audOver(null); } catch(e) {} closeModal(); UI.view = 'home'; render(); }")
    await pg.wait_for_timeout(300)
    return b, pg, errs


def real_errors(errs):
    """그림 파일이 없어서 나는 오류(작업 폴더에 assets 를 다 받지 않았으니 당연)는 뺀다"""
    return [e for e in errs if "Failed to load resource" not in e and "ERR_FILE_NOT_FOUND" not in e and "ERR_FAILED" not in e]


def cmd_shot(args):
    import argparse, asyncio
    ap = argparse.ArgumentParser(prog="hs.py shot")
    ap.add_argument("--page", default="heroschool.html")
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=800)
    ap.add_argument("--phone", action="store_true", help="390×844 · 2배")
    ap.add_argument("--title", action="store_true", help="시작 화면을 닫지 않는다")
    ap.add_argument("--js", action="append", default=[], help="띄운 뒤 돌릴 코드 (함수 본문 · return 값을 찍는다)")
    ap.add_argument("--click", action="append", default=[], help="누를 선택자 (차례대로)")
    ap.add_argument("--wait", type=int, default=700, help="마지막 동작 뒤 기다릴 ms")
    ap.add_argument("--sel", help="이 요소만 찍는다")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--out", default="shot.png")
    ap.add_argument("--missing", action="store_true", help="이 화면이 못 읽은 그림을 받을 목록(PC 경로)으로")
    o = ap.parse_args(args)
    if o.phone:
        o.w, o.h = 390, 844
    from playwright.async_api import async_playwright

    async def main():
        async with async_playwright() as p:
            t = time.time()
            b, pg, errs = await open_game(p, o.w, o.h, o.page, 2 if o.phone else 1, o.title)
            print("띄움 %.1f초 · 빌드 %s · 화면 %s" % (time.time() - t, await pg.evaluate("() => typeof BUILD !== 'undefined' ? BUILD : '?'"),
                                               await pg.evaluate("() => UI.view")))
            for js in o.js:
                r = await pg.evaluate("async () => { %s }" % js)
                if r is not None:
                    print("js →", json.dumps(r, ensure_ascii=False)[:2000])
            for sel in o.click:
                await pg.click(sel)
                await pg.wait_for_timeout(300)
            await pg.wait_for_timeout(o.wait)
            os.makedirs(SHOTS, exist_ok=True)
            out = os.path.join(SHOTS, o.out)
            el = await pg.query_selector(o.sel) if o.sel else None
            if o.sel and not el:
                print("선택자를 못 찾아 화면 전체를 찍는다:", o.sel)
            await (el.screenshot(path=out) if el else pg.screenshot(path=out, full_page=o.full))
            real = real_errors(errs)
            print("스크린샷:", out)
            print("오류 %d개%s  (그림 파일 없음 %d개는 뺌)" % (len(real), (":\n  " + "\n  ".join(real[:12])) if real else "", len(errs) - len(real)))
            if errs.missing:
                by = {}
                for r in errs.missing:
                    by[os.path.dirname(r)] = by.get(os.path.dirname(r), 0) + 1
                print("작업 폴더에 없어 못 그린 파일 %d개 — " % len(errs.missing)
                      + " · ".join("%s %d" % (d, n) for d, n in sorted(by.items(), key=lambda x: -x[1])[:12])
                      + ("" if o.missing else "  (받을 목록은 --missing)"))
                if o.missing:
                    m = sorted(errs.missing)
                    for i in range(0, len(m), MAX_CALL_FILES):
                        print(json.dumps([dev_of(r) for r in m[i:i + MAX_CALL_FILES]], ensure_ascii=False))
            await b.close()
    asyncio.run(main())


def cmd_i18n(args):
    """영어판 시험 (1010) — 빌드한 뒤에 돌린다. 실패하면 멈춘다"""
    if not os.path.exists(os.path.join(WORK, "tools", "i18n", "check_i18n.py")):
        die("없다: tools/i18n/check_i18n.py — core 묶음을 다시 받는다 (hs.py list core)")
    run([sys.executable, "tools/i18n/check_i18n.py", "--shots", os.path.join(SHOTS, "i18n")] + args)
    print("영어 스크린샷:", os.path.join(SHOTS, "i18n"))


def cmd_layout(args):
    """영어판 화면 점검 (1010 · 2단계) — 영어에서 넘치거나 잘린 칸 (크기 1440×900 · 900×1000 · 390×844, 한국어에도 있는 것은 뺀다)"""
    if not os.path.exists(os.path.join(WORK, "tools", "i18n", "check_layout.py")):
        die("없다: tools/i18n/check_layout.py — core 묶음을 다시 받는다 (hs.py list core)")
    out = os.path.join(SHOTS, "layout")
    p = subprocess.run([sys.executable, "tools/i18n/check_layout.py", "--shots", out] + args, cwd=WORK)
    print("영어 화면 스크린샷:", out)
    if p.returncode:
        print("(넘치거나 잘린 칸이 있다 — 위 목록)")


# ── PC 로 보내기 ─────────────────────────────────────────────────────────────
def chunks(items):
    out, cur, size = [], [], 0
    for it in items:
        s = os.path.getsize(it["_src"])
        if cur and (len(cur) >= MAX_CALL_FILES or size + s > MAX_CALL_BYTES):
            out.append(cur)
            cur, size = [], 0
        cur.append(it)
        size += s
    return out + ([cur] if cur else [])


def cmd_pack(args):
    dry, nowait = "--dry" in args, "--nowait" in args
    args = [a for a in args if not a.startswith("--")]
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", args[0] if args else "pack")
    ch, sa = changed()
    if not ch:
        print("바뀐 파일 없음")
        return
    conf, mt = jload(CONF, {}), jload(MT, {})
    bad = [r for k, r in ch if r in conf]
    if bad:
        die("sync 충돌이 해결되지 않았다: " + ", ".join(bad))
    need = [r for k, r in ch if k == "M" and r not in mt]
    if need:
        print("PC mtime 을 모르는 파일 %d개 — 이 파일들을 받았던 stage 결과(또는 지금 device_list_dir)의 mtimeMs 로:" % len(need))
        print("  python3 hs.py mtimes " + " ".join("%s=<mtimeMs>" % r for r in need))
        print("  (stage 이후 다른 세션이 PC 에서 고쳤을 수 있으면 다시 받아 sync 부터 — 지금 목록의 mtime 을 쓰면 그 수정을 덮는다)")
        sys.exit(1)
    for k, rel in ch:
        size = os.path.getsize(os.path.join(WORK, rel))
        if size > MAX_FILE:
            die("20MB 넘는 파일: %s (%.1fMB)" % (rel, size / 1e6))
    out = os.path.join(OUTPUTS, "%s_%s" % (name, time.strftime("%m%d-%H%M%S")))
    g1, g2 = [], []
    for k, rel in ch:
        it = {"devicePath": dev_of(rel), "stagedPath": os.path.join(out, rel), "_src": os.path.join(WORK, rel), "_rel": rel, "_k": k}
        if k == "M":
            it["expectedMtimeMs"] = mt[rel]
            g1.append(it)
        else:
            g2.append(it)
    if not dry:
        for it in g1 + g2:
            copy(it["_src"], it["stagedPath"])
    jsave(LAST, {"out": out, "dry": dry, "time": time.time(),
                 "files": {it["_rel"]: {"stagedPath": it["stagedPath"], "sha1": sha(it["_src"])} for it in g1 + g2}})

    def show(group, title):
        cs = chunks(group)
        for i, c in enumerate(cs):
            print("\n## %s%s — %d개" % (title, (" (%d/%d)" % (i + 1, len(cs))) if len(cs) > 1 else "", len(c)))
            print("[" + ",\n ".join(json.dumps({k: v for k, v in it.items() if not k.startswith("_")}, ensure_ascii=False) for it in c) + "]")

    print("보낼 폴더:", out, "(시험 — 복사하지 않음)" if dry else "")
    if sa:
        print("빌드가 뺀 그림 중 PC 와 같은 것 %d개는 뺐다 (heroschool.html 의 ?v= 가 같다)" % sa)
    if g1:
        show(g1, "1차 커밋 — 이미 PC 에 있는 파일 (expectedMtimeMs 로 지킨다 · force 금지)")
    if g2:
        show(g2, "2차 커밋 — 1차가 모두 written 일 때만 (새 파일 · 빌드가 새로 뺀 그림)")
        news = [it["_rel"] for it in g2 if it["_k"] == "A"]
        if news:
            print("※ 새 파일 %d개 — PC 에 같은 이름이 없는지 모르면 device_list_dir 로 먼저 본다: %s" % (len(news), ", ".join(news[:8])))
    print("\n## 커밋 뒤 — 확인까지 하려면 아래를 다시 받아(device_stage_files) hs.py verify 경로=mtime…, 아니면 hs.py done 경로=mtime…")
    allp = [dev_of(it["_rel"]) for it in g1 + g2]
    for i in range(0, len(allp), MAX_CALL_FILES):
        print(json.dumps(allp[i:i + MAX_CALL_FILES], ensure_ascii=False))
    if not dry and not nowait:
        time.sleep(8)                     # outputs 폴더가 동기화될 시간 — 바로 커밋하면 옛 내용이 갈 때가 있었다
        print("\n(8초 기다렸다 — 이제 커밋)")


def finish(args, check):
    last = jload(LAST, None)
    if not last or last.get("dry"):
        die("커밋한 pack 기록이 없다")
    files, mt, new = last["files"], jload(MT, {}), parse_mtimes(args)
    ok, bad, skip = [], [], []
    if check:
        settle(UPLOADS, 15)
    for rel, info in files.items():
        sent = info["stagedPath"] if os.path.exists(info["stagedPath"]) else os.path.join(WORK, rel)
        got = os.path.join(UPLOADS, rel)
        if check:
            if not os.path.exists(got) or os.path.getmtime(got) < last["time"]:
                skip.append(rel + " (커밋 뒤 다시 받지 않았다)")
            elif os.path.getsize(got) == os.path.getsize(sent) and sha(got) == info["sha1"]:
                ok.append(rel)
            elif rel.lower().endswith(IMG) and pixels_same(got, sent):
                ok.append(rel + " (픽셀 같음 · C2PA)")
            elif rel.lower().endswith(AUD):
                skip.append(rel + " (소리 — C2PA 로 바이트가 달라 비교 생략)")
            else:
                bad.append(rel)
                continue
        copy(sent, os.path.join(BASE, rel))                  # 보낸 내용이 이제 PC 원본
        if rel in new:
            mt[rel] = new[rel]
        else:
            mt.pop(rel, None)
    jsave(MT, mt)
    os.remove(LAST)
    if check:
        print("같음 %d개" % len(ok) + (":\n  " + "\n  ".join(ok) if len(ok) <= 15 else ""))
        if skip:
            print("확인 못 함 %d개:\n  " % len(skip) + "\n  ".join(skip))
        if bad:
            print("⚠ 다름 %d개 — PC 에 쓴 내용이 보낸 것과 다르다 (원본은 그대로 둠):\n  " % len(bad) + "\n  ".join(bad))
    nomt = [r for r in files if r not in new]
    print("커밋 반영 %d개 · 새 mtime %d개%s" % (len(files) - len(bad), len([r for r in files if r in new]),
                                         (" · mtime 없음(다음 커밋 전에 hs.py mtimes): " + ", ".join(nomt[:8])) if nomt else ""))


CMDS = {"list": cmd_list, "init": cmd_init, "sync": lambda a: ingest(a or None), "resolve": cmd_resolve,
        "mtimes": cmd_mtimes, "status": cmd_status, "diff": cmd_diff, "apply": cmd_apply, "build": cmd_build,
        "shot": cmd_shot, "i18n": cmd_i18n, "layout": cmd_layout, "pack": cmd_pack, "done": lambda a: finish(a, False), "verify": lambda a: finish(a, True)}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
