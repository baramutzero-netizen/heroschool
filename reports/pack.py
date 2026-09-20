"""Embed report runtime and room assets for both self-contained HTML builds."""
from pathlib import Path
import base64, json, re
ROOT = Path(__file__).resolve().parent.parent
src = ROOT / 'game.html'
text = src.read_text(encoding='utf-8')
def block(text, start, end, content, anchor):
    value = start + '\n' + content + '\n' + end
    if start in text:
        return re.sub(re.escape(start)+r'.*?'+re.escape(end), lambda _: value, text, count=1, flags=re.S)
    return text.replace(anchor, value+'\n'+anchor, 1)
rooms = {p.stem:'data:image/webp;base64,'+base64.b64encode(p.read_bytes()).decode() for p in (ROOT/'reports/rooms').glob('*.webp')}
assert set(rooms) == {'library','gym','hall','chapel','infirm','arena','beach'}, 'Missing report room asset'
text = block(text, '/* REPORT_SCENE_STYLE_START */', '/* REPORT_SCENE_STYLE_END */',
    (ROOT/'reports/style.css').read_text(encoding='utf-8'), '/* ---------- 주간 일지 ---------- */')
text = block(text, '/* REPORT_SCENE_RUNTIME_START */', '/* REPORT_SCENE_RUNTIME_END */',
    'const REPORT_ROOMS = '+json.dumps(rooms)+';\nconst REPORT_STATUP = '+json.dumps('data:audio/mpeg;base64,'+base64.b64encode((ROOT/'bgm/statup.mp3').read_bytes()).decode())+';\nconst REPORT_RECOVERY = '+json.dumps('data:audio/mpeg;base64,'+base64.b64encode((ROOT/'bgm/recovery.mp3').read_bytes()).decode())+';\n'+(ROOT/'reports/runtime.js').read_text(encoding='utf-8'), 'function showReport(r){')
src.write_text(text, encoding='utf-8')
print('Embedded report scenes and', len(rooms), 'rooms')
