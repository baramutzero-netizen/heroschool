from pathlib import Path
root = Path(__file__).resolve().parents[3]
p = root / 'game.html'
s = p.read_text(encoding='utf-8')
start, end = '/* STYLISH_SKILL_FX_BEGIN */', '/* STYLISH_SKILL_FX_END */'
a, b = s.index(start), s.index(end)
runtime = Path(__file__).with_name('runtime.js').read_text(encoding='utf-8')
p.write_text(s[:a] + start + '\n' + runtime + '\n' + s[b:], encoding='utf-8')
