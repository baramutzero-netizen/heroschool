// 영어판 준비 (1010) — game.html 에서 화면에 나오는 한국어 글을 전부 뽑는다.
//   인라인 스크립트(JS 문자열 · 템플릿) · 스크립트 밖 HTML(글 · title/aria-label 등 속성) · CSS content.
//   주석은 세기만 한다. 개발용 블록(CHRONICLE_JS · AVATAR_LAB — 배포 빌드에서 빠짐)은 dev 표시.
//
//   준비 (한 번): 저장소 밖 임시 폴더에서  npm i acorn@8.14.0 acorn-walk@8.3.4
//   실행:  NODE_PATH=<그 폴더>/node_modules node tools/i18n/extract_ko.cjs game.html ko.json
//   다음:  python3 tools/i18n/classify_ko.py ko.json ko_strings.csv   (갈래 · 분량 요약 + CSV)
//
//   한 항목 = {src, line, kind(str|tpl|regex|html|attr|css), role(text|key|cmp|case|member|find|regex),
//              top(맨 위 선언), func, callee(가장 가까운 호출), path(속성 경로), inTpl, dev, text, exprs, h(한글 글자 수)}
//   템플릿의 text 는 자리표 {0} {1} … 로 — exprs 가 그 자리의 식.
'use strict';
const fs = require('fs');
const acorn = require('acorn');
const walk = require('acorn-walk');

const [, , inPath, outPath] = process.argv;
if (!inPath || !outPath) { console.error('usage: node extract_ko.cjs game.html out.json'); process.exit(2); }
const src = fs.readFileSync(inPath, 'utf8');
const HANG = /[가-힣ㄱ-ㆎ]/;
const hcount = s => (s.match(/[가-힣]/g) || []).length;
const lineStarts = [0]; for (let i = 0; i < src.length; i++) if (src.charCodeAt(i) === 10) lineStarts.push(i + 1);
const lineOf = off => { let lo = 0, hi = lineStarts.length - 1; while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (lineStarts[mid] <= off) lo = mid; else hi = mid - 1; } return lo + 1; };
// 개발용 블록 (build_strip.py 가 배포 빌드에서 걷어내는 곳)
const devRanges = [];
for (const [a, b] of [['/* CHRONICLE_JS_START */', '/* CHRONICLE_JS_END */'], ['/* AVATAR_LAB_START */', '/* AVATAR_LAB_END */']]) {
  const i = src.indexOf(a), j = i < 0 ? -1 : src.indexOf(b, i);
  if (i >= 0 && j >= 0) devRanges.push([i, j + b.length]);
}
const isDev = off => devRanges.some(([a, b]) => a <= off && off < b);

const out = []; let commentHangul = 0, commentCount = 0;
const regions = [];
const push = (o, abs) => out.push(Object.assign({inTpl: false, dev: isDev(abs), exprs: null, h: hcount(o.text), line: lineOf(abs)}, o));

// ── JS ──
const sre = /<script\b([^>]*)>([\s\S]*?)<\/script>/g; let m;
while ((m = sre.exec(src))) {
  const bodyStart = m.index + m[0].indexOf('>') + 1;
  regions.push([m.index, m.index + m[0].length]);
  if (/\bsrc\s*=/.test(m[1]) || !HANG.test(m[2])) continue;
  const code = m[2], comments = [];
  let ast;
  try {
    ast = acorn.parse(code, {ecmaVersion: 'latest', sourceType: 'script', allowReturnOutsideFunction: true, allowAwaitOutsideFunction: true, allowHashBang: true, onComment: comments});
  } catch (e) { console.error('parse error at line', lineOf(bodyStart + (e.pos || 0)), e.message); process.exit(1); }
  for (const c of comments) { const h = hcount(c.value); if (h) { commentHangul += h; commentCount++; } }
  const S = n => code.slice(n.start, n.end);
  const fnName = (fn, p) => {
    if (fn.id && fn.id.name) return fn.id.name;
    if (p && p.type === 'VariableDeclarator' && p.id.type === 'Identifier') return p.id.name;
    if (p && p.type === 'Property' && !p.computed) return p.key.name || p.key.value;
    if (p && p.type === 'AssignmentExpression') return S(p.left).slice(0, 60);
    if (p && p.type === 'MethodDefinition') return p.key.name;
    return '(anon)';
  };
  walk.fullAncestor(ast, (node, _st, anc) => {
    let kind = null, text = null, exprs = null;
    if (node.type === 'Literal' && typeof node.value === 'string' && HANG.test(node.value)) { kind = 'str'; text = node.value; }
    else if (node.type === 'Literal' && node.regex && HANG.test(node.regex.pattern)) { kind = 'regex'; text = node.regex.pattern; }
    else if (node.type === 'TemplateLiteral' && node.quasis.some(q => HANG.test(q.value.cooked || q.value.raw))) {
      kind = 'tpl'; exprs = node.expressions.map(S);
      text = node.quasis.map((q, i) => (q.value.cooked ?? q.value.raw) + (i < node.expressions.length ? `{${i}}` : '')).join('');
    }
    if (!kind) return;
    const parent = anc[anc.length - 2];
    let role = 'text';
    if (kind === 'regex') role = 'regex';
    else if (parent && parent.type === 'Property' && parent.key === node && !parent.computed) role = 'key';
    else if (parent && parent.type === 'BinaryExpression' && /^[!=]==?$/.test(parent.operator)) role = 'cmp';
    else if (parent && parent.type === 'SwitchCase' && parent.test === node) role = 'case';
    else if (parent && parent.type === 'MemberExpression' && parent.property === node && parent.computed) role = 'member';
    else if (parent && parent.type === 'CallExpression' && parent.callee.type === 'MemberExpression' && /^(includes|indexOf|startsWith|endsWith|test|match|split|replace|replaceAll|lastIndexOf|search)$/.test(parent.callee.property.name || '')) role = 'find';
    else if (parent && parent.type === 'NewExpression' && S(parent.callee) === 'RegExp') role = 'regex';
    let top = '', func = '', callee = '', path = [], inTpl = false;
    const prog = anc[1];
    if (prog) {
      if (prog.type === 'VariableDeclaration') { const d = prog.declarations.find(d => d.start <= node.start && node.end <= d.end); top = d && d.id.type === 'Identifier' ? d.id.name : (d ? S(d.id).slice(0, 40) : ''); }
      else if (prog.type === 'FunctionDeclaration') top = prog.id.name + '()';
      else if (prog.type === 'ExpressionStatement') { const e = prog.expression; top = e.type === 'AssignmentExpression' ? S(e.left).slice(0, 40) : (e.type === 'CallExpression' ? S(e.callee).slice(0, 40).replace(/\s+/g, ' ') + '(…)' : e.type); }
      else top = prog.type;
    }
    for (let i = anc.length - 2; i >= 0; i--) {
      const a = anc[i], p = anc[i - 1];
      if (!func && /Function/.test(a.type)) func = fnName(a, p);
      if (!callee && !func && a.type === 'CallExpression' && a.arguments.some(x => x.start <= node.start && node.end <= x.end)) callee = S(a.callee).slice(0, 50);
      if (!func && a.type === 'TemplateLiteral' && a !== node) inTpl = true;
      if (!func && a.type === 'Property' && a.value && a.value.start <= node.start && node.end <= a.value.end && !a.computed) path.unshift(a.key.name ?? a.key.value);
      if (!func && a.type === 'ArrayExpression') { const k = a.elements.findIndex(x => x && x.start <= node.start && node.end <= x.end); if (k >= 0) path.unshift(k); }
    }
    push({src: 'js', kind, role, top, func, callee, path: path.join('.'), inTpl, text, exprs}, bodyStart + node.start);
  });
}
// ── CSS content ──
const cre = /<style\b[^>]*>([\s\S]*?)<\/style>/g;
while ((m = cre.exec(src))) {
  regions.push([m.index, m.index + m[0].length]);
  const body = m[1], b0 = m.index + m[0].indexOf('>') + 1;
  const noCom = body.replace(/\/\*[\s\S]*?\*\//g, mm => { const h = hcount(mm); if (h) { commentHangul += h; commentCount++; } return ' '.repeat(mm.length); });
  const q = /content\s*:\s*(["'])((?:\\.|(?!\1).)*)\1/g; let k;
  while ((k = q.exec(noCom))) if (HANG.test(k[2])) push({src: 'css', kind: 'css', role: 'text', top: 'CSS', func: '', callee: '', path: '', text: k[2]}, b0 + k.index);
}
// ── HTML 마크업 (스크립트 · 스타일 밖) ──
regions.sort((a, b) => a[0] - b[0]);
let pos = 0; const html = [];
for (const [a, b] of regions) { if (a > pos) html.push([pos, src.slice(pos, a)]); pos = Math.max(pos, b); }
html.push([pos, src.slice(pos)]);
for (const [off, chunk] of html) {
  const noCom = chunk.replace(/<!--[\s\S]*?-->/g, mm => ' '.repeat(mm.length));
  const tag = /<[^>]+>/g; let last = 0, t;
  const pushText = (s, o) => { const v = s.replace(/\s+/g, ' ').trim(); if (HANG.test(v)) push({src: 'html', kind: 'html', role: 'text', top: 'HTML', func: '', callee: '', path: '', text: v}, off + o); };
  while ((t = tag.exec(noCom))) {
    pushText(noCom.slice(last, t.index), last);
    const at = /\s(title|aria-label|placeholder|alt|value|content)\s*=\s*"([^"]*)"/g; let a;
    while ((a = at.exec(t[0]))) if (HANG.test(a[2])) push({src: 'html', kind: 'attr', role: 'text', top: 'HTML', func: '', callee: '', path: a[1], text: a[2]}, off + t.index);
    last = t.index + t[0].length;
  }
  pushText(noCom.slice(last), last);
}
fs.writeFileSync(outPath, JSON.stringify({entries: out, commentHangul, commentCount}));
console.log('entries', out.length, '· comment hangul', commentHangul, 'in', commentCount, 'comments');
