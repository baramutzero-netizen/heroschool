"""PNG → WebP (1008) — 게임이 받는 PNG 가운데 정한 묶음만 WebP 로 바꾸고 game.html 의 경로를 고친다. 몇 번을 돌려도 같은 결과.
다른 apply 스크립트를 다 돌린 뒤, wrap.py 앞에 돌린다.

    python3 apply_webp.py <game.html>

game.html 옆 assets/ 의 PNG 를 읽어 같은 자리에 같은 이름의 .webp 를 만들고(내용이 같으면 건드리지 않는다),
game.html 안의 "assets/…png(?v=…)" 를 "assets/…webp?v=<내용 해시>" 로 바꾼다. 원래 PNG 는 지우지 않는다.

· 무손실 (보이는 픽셀 그대로): LOSSLESS_DIRS 폴더의 그림 — 이야기 그림 · 스킬 이펙트 · UI 리소 · 마을 지도 · 시작 화면 목판 ·
  메뉴 아이콘 · NPC 도트 · 몬스터 도트 · 스케줄 그림 · 책상 그림
· q90 (손실 · 투명도는 그대로): 쿼터뷰 나무 테두리 · 버튼 박스 · 몬스터 큰 그림(mon_img/*-warm-pixel) (Q90 — 글롭 무늬 · 무손실보다 먼저)
  q90 쪽은 이미 WebP 로 바꾼 경로(…webp?v=)도 옆에 PNG 가 있으면 다시 굽는다 — 무손실로 넣었던 몬스터 그림도 이렇게 q90 이 된다
· 효과 아틀라스 — 캔버스에서 픽셀을 읽는 그림이라 JS 로 감싼다: assets/fx_img.png.js → assets/fx_img.webp.js · HS_A["fx_img.webp"] (무손실)
· 스케줄 · 책상 그림은 생성 스크립트(apply_sched · apply_desk)도 이제 같은 방식(webp_lossless)으로 WebP 를 넣는다
· 빼는 것: 직업 스프라이트 · 쿼터뷰 지도 · 움직이는 PNG(오프닝 · 전투 배너 — 여기 폴더에 있어도 건너뛴다) · 얼굴 그림(학생 · 오프닝)
Pillow(libwebp)로 굽는다 — 버전이 다르면 바이트가 조금 달라질 수 있다 (그림은 같다)."""
import base64, fnmatch, hashlib, io, os, re, struct, sys
from PIL import Image

LOSSLESS_DIRS = ["story_art", "skill-fx", "ui-riso", "town", "title-art", "menu_sc", "npc_px", "mon_img", "sched_art", "mdesk_art"]
Q90 = ["battle-fields/quarter/frame.png", "battle-fields/quarter/controls.png",
       "mon_img/*-warm-pixel.png"]   # 1008 — 몬스터 큰 그림 (1774×887 · 1254×1254 — 화면에는 512×256 · 256×256 으로 줄여 그린다)


def is_q90(rel):
    return any(fnmatch.fnmatchcase(rel, p) for p in Q90)


def webp_lossless(png_bytes):
    """무손실 — 보이는 픽셀은 원본과 똑같다. 완전히 투명한 픽셀(알파 0)의 숨은 색만 정리한다 — 화면에는 안 보이고,
    그대로 두면(exact) 스킬 이펙트 · 마을 테두리처럼 투명한 곳이 넓은 그림은 2배 가까이 커진다"""
    im = Image.open(io.BytesIO(png_bytes)); im.load()
    b = io.BytesIO(); im.save(b, "WEBP", lossless=True, quality=100, method=6)
    return b.getvalue()


def webp_q90(png_bytes):
    """손실 q90 — 투명도(알파)는 무손실"""
    im = Image.open(io.BytesIO(png_bytes)); im.load()
    if im.mode not in ("RGB", "RGBA"): im = im.convert("RGBA")
    b = io.BytesIO(); im.save(b, "WEBP", quality=90, method=6, alpha_quality=100)
    return b.getvalue()


def is_apng(b):
    p = 8
    while p + 8 <= len(b):
        n, t = struct.unpack(">I", b[p:p+4])[0], b[p+4:p+8]
        if t == b"acTL": return True
        if t in (b"IDAT", b"IEND"): return False
        p += 12 + n
    return False


def ver(b):
    return hashlib.sha1(b).hexdigest()[:8]


def write(path, data):
    if os.path.exists(path) and open(path, "rb").read() == data:
        return False
    open(path, "wb").write(data); return True


def apply(src, root, log=print):
    A = os.path.join(root, "assets")
    dirs = "|".join(re.escape(d) for d in LOSSLESS_DIRS)
    refs = set(re.findall(r'assets/((?:' + dirs + r')/[A-Za-z0-9_\-./]+?)\.png(?![A-Za-z0-9_.])', src))
    jobs = [(r + ".png", webp_lossless) for r in sorted(refs) if not is_q90(r + ".png")]
    # q90 — PNG 경로든 이미 바꾼 WebP 경로든 (옆에 PNG 가 있으면) 다시 굽는다. 무늬가 좁아서 원래부터 WebP 인 그림은 걸리지 않는다
    qrefs = set()
    for r, ext in re.findall(r'assets/([A-Za-z0-9_\-./]+?)\.(png|webp)(?![A-Za-z0-9_.])', src):
        if is_q90(r + ".png") and (ext == "png" or os.path.exists(os.path.join(A, r + ".png"))):
            qrefs.add(r)
    jobs += [(r + ".png", webp_q90) for r in sorted(qrefs)]
    made = changed = 0
    for rel, enc in jobs:
        png = os.path.join(A, rel)
        if not os.path.exists(png):
            raise RuntimeError("PNG 가 없다: assets/" + rel)
        raw = open(png, "rb").read()
        if is_apng(raw):
            log("  건너뜀 (움직이는 PNG): assets/" + rel); continue
        data = enc(raw)
        out = rel[:-4] + ".webp"
        changed += write(os.path.join(A, out), data); made += 1
        ext = r'\.(?:png|webp)' if enc is webp_q90 else r'\.png'   # 무손실은 PNG 경로만 (원래부터 있던 같은 이름 WebP 는 건드리지 않는다)
        src = re.sub(r'assets/' + re.escape(rel[:-4]) + ext + r'(?:\?v=[A-Za-z0-9]+)?(?![A-Za-z0-9_.])', 'assets/' + out + '?v=' + ver(data), src)
    # 효과 아틀라스 (JS 안 PNG — 캔버스에서 픽셀을 읽는다)
    fxp = os.path.join(A, "fx_img.png.js")
    if 'HS_A["fx_img.png"]' in src and os.path.exists(fxp):
        m = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', open(fxp, encoding="utf-8").read())
        data = webp_lossless(base64.b64decode(m.group(1)))
        js = ('HS_A["fx_img.webp"]="data:image/webp;base64,%s";\n' % base64.b64encode(data).decode()).encode()
        changed += write(os.path.join(A, "fx_img.webp.js"), js); made += 1
        src = src.replace('HS_A["fx_img.png"]', 'HS_A["fx_img.webp"]')
        src = re.sub(r'<script src="assets/fx_img\.png\.js\?v=[A-Za-z0-9]+"></script>',
                     '<script src="assets/fx_img.webp.js?v=%s"></script>' % ver(js), src)
    log(f"apply_webp: WebP {made}개 (새로 쓰거나 바뀐 파일 {changed}개)")
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"), os.path.dirname(os.path.abspath(path)))
    if crlf:
        src = src.replace("\n", "\r\n")
    if src != raw:
        open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
