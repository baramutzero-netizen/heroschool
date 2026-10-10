/* I18N 시작 — 영어판 번역 함수 (1010 · tools/i18n/i18n_runtime.js — 빌드 때 i18n_build.py 가 여기에 넣는다. game.html 원본에는 없다)
   _T("한국어"[, 문맥]) · _L`…${x}…` · _LC.문맥`…` — 한국어면 받은 글을 그대로 돌려주고, 영어면 영어 표(I18N_EN)에서 찾는다. 없으면 한국어 그대로.
   문맥 = 그 글이 든 맨 위 선언 이름 — 영어 표에 "문맥|한국어" 키가 있을 때만 빌드가 붙인다 (같은 한국어를 곳마다 달리 옮길 때).
   HS_LANG 은 <head> 맨 앞의 작은 스크립트가 정한다 (?lang=en|ko · 공개 뒤에는 설정 · 브라우저 언어). */
var I18N_EN = /*@@EN@@*/{};
var I18N_CSS = /*@@CSS@@*/"", I18N_RBCSS = /*@@RBCSS@@*/"";   /* 영어 화면 고침 — en_layout.css · en_layout_rbook.css (영어일 때만 붙인다) */
var I18N = (function(){
  var lang = (typeof HS_LANG === "string" && HS_LANG === "en") ? "en" : "ko";
  var PH = /\{(\d+)(?:\|([^|{}]*)\|([^|{}]*))?\}/g;
  function compile(s){                       // "{0|student|students} 오른다 {1}" → ["", {i:0, one, many}, " …", {i:1}, ""]
    var parts = [], last = 0, m; PH.lastIndex = 0;
    while((m = PH.exec(s))){
      parts.push(s.slice(last, m.index));
      parts.push(m[2] === undefined ? {i: +m[1]} : {i: +m[1], one: m[2], many: m[3]});
      last = PH.lastIndex;
    }
    parts.push(s.slice(last));
    return parts;
  }
  return {lang: lang, en: lang === "en" ? I18N_EN : null, pub: typeof HS_LANG_PUBLIC !== "undefined" && !!HS_LANG_PUBLIC,
          compile: compile, cache: new WeakMap(), tcache: new Map()};
})();
/* 키 모양 — 줄바꿈이 낀 빈칸은 한 칸, 글 안 태그의 속성은 뺀다 (<b style=…> → <b>). i18n_build.py 의 norm_key 와 같은 규칙.
   영어 값의 <b> 들은 원문의 <b …> 를 차례로 되돌려 받는다 (<b#2> = 원문의 두 번째 b). */
var I18N_NL = /[ \t]*\n[ \t\n]*/g, I18N_TAG = /<([A-Za-z][A-Za-z0-9-]*)\s[^<>]*>/g, I18N_ANY = /<([A-Za-z][A-Za-z0-9-]*)(\s[^<>]*)?>/g,
    I18N_VTAG = /<([A-Za-z][A-Za-z0-9-]*)(?:#(\d+))?>/g;
function i18nKey(k){
  if(k.indexOf("\n") >= 0) k = k.replace(I18N_NL, " ");
  if(k.indexOf("<") >= 0) k = k.replace(I18N_TAG, "<$1>");
  return k;
}
function i18nFind(ctx, k0){                  // 원문(자리표 {n} 포함) → 영어 값 (태그 속성 되돌림) · 없으면 undefined
  var k = i18nKey(k0), en = I18N.en, v;
  if(ctx !== null && ctx !== undefined) v = en[ctx + "|" + k];
  if(v === undefined) v = en[k];
  if(v === undefined || k0.indexOf("<") < 0) return v;
  var list = {}, m; I18N_ANY.lastIndex = 0;
  while((m = I18N_ANY.exec(k0))){ var nm = m[1].toLowerCase(); (list[nm] = list[nm] || []).push(m[0]); }
  var cnt = {};
  return v.replace(I18N_VTAG, function(all, n, idx){
    var L = list[n.toLowerCase()];
    if(!L) return idx ? "<" + n + ">" : all;
    var i = idx ? (+idx - 1) : ((cnt[n] = (cnt[n] || 0) + 1) - 1);
    return L[i] !== undefined ? L[i] : (idx ? "<" + n + ">" : all);
  });
}
function _T(s, c){
  if(I18N.en === null) return s;
  var key = c === undefined ? s : c + "|" + s, v = I18N.tcache.get(key);
  if(v === undefined){ v = i18nFind(c, s); if(v === undefined) v = s; I18N.tcache.set(key, v); }
  return v;
}
function _Lx(ctx, strs, args){
  var n = args.length, i, out;
  if(I18N.en !== null){
    var c = I18N.cache.get(strs);
    if(c === undefined){
      var key = strs[0];
      for(i = 1; i < strs.length; i++) key += "{" + (i - 1) + "}" + strs[i];
      var v = i18nFind(ctx, key);
      c = v === undefined ? null : I18N.compile(v);
      I18N.cache.set(strs, c);
    }
    if(c !== null){
      out = "";
      for(i = 0; i < c.length; i++){
        var p = c[i];
        if(typeof p === "string"){ out += p; continue; }
        var val = args[p.i + 1];
        out += p.one !== undefined ? (Number(val) === 1 ? p.one : p.many) : String(val);
      }
      return out;
    }
  }
  out = strs[0];
  for(i = 1; i < n; i++) out += String(args[i]) + strs[i];
  return out;
}
function _L(strs){ return _Lx(null, strs, arguments); }
function _Lt(ctx){ return function(strs){ return _Lx(ctx, strs, arguments); }; }
var _LC = /*@@CTX@@*/{};
/* 세이브 · 서버의 데이터 글 (1010 · 3단계) — 학생 이름 · 이명 · 유물 · 학원 이름 · 진로 · 스킬 이름처럼 세이브와 서버에 글 그대로 남는 것.
   I18N.toCur(x) — 지금 언어로 (세이브를 불러올 때 · 서버에서 받은 남의 학원).  I18N.toKo(x) — 한국어 원문으로 (서버로 보낼 때 · 한국어판이면 그대로).
   x 는 글 · 배열 · 객체 (객체 · 배열은 고친 사본 · 맨 위 log(일지)는 그대로). 영어 표의 글 하나와 통째로 같은 글과 정해진 모양만 바꾼다 —
   “이명” 이름 · ○○ 용사 학원 · ○○ 학원 · 유물(형용사 명사) · 한국식 성+이름. 문장(일지 등)은 쓰인 언어 그대로. game.html 은 koData · curData 로 부른다 */
(function(){
  var NAME_CTX = {NAME_POOL: 1, L5_NPC_ACAD: 1, MON: 1, EPI_CROWD: 1};     // 통째로 바꾸는 이름 (문맥 키) — 같은 글이면 전역 값보다 먼저
  /* 영어 하나에 한국어가 여럿인 것 중 세이브 · 서버에 남는 것 — 되돌릴 한국어 (유물 옵션 · 스킬 · 이름 없는 학생) */
  var KO_PREF = {"DEF": "방어력", "Slash": "베기", "Unknown": "무명", "EXP": "경험치"};
  var M = null, HAN = /[가-힣]/, LAT2 = /[A-Za-z][\s\S]*[A-Za-z]/, PH = /\{\d/;
  function maps(){
    if(M) return M;
    M = {f: {}, r: {}, amb: {}, sur: {}, giv: {}, acad: {}, adj: {}, noun: {}, rsur: {}, rgiv: {}, racad: {}, radj: {}, rnoun: {}};
    var k, v, b, c, ko, part = {SUR: "sur", GIV: "giv", ACAD: "acad", RELIC_ADJ: "adj", RELIC_NOUN: "noun"};
    for(k in I18N_EN){
      v = I18N_EN[k];
      if(typeof v !== "string" || !v || v === "∅" || k.charAt(0) === "_") continue;
      b = k.indexOf("|");
      if(b < 0){
        if(PH.test(k) || k.indexOf("<") >= 0) continue;
        M.f[k] = v; if(M.r[v] !== undefined && M.r[v] !== k) M.amb[v] = 1; else M.r[v] = k;
        continue;
      }
      c = k.slice(0, b); ko = k.slice(b + 1);
      if(part[c]){ M[part[c]][ko] = v; M["r" + part[c]][v] = ko; }
    }
    for(k in I18N_EN){
      b = k.indexOf("|"); if(b < 0 || !NAME_CTX[k.slice(0, b)]) continue;
      ko = k.slice(b + 1); v = I18N_EN[k];
      M.f[ko] = v; M.r[v] = ko; delete M.amb[v];
    }
    for(k in KO_PREF) if(M.f[KO_PREF[k]] === k){ M.r[k] = KO_PREF[k]; delete M.amb[k]; }
    var sfx = function(ko, dflt){ var e = I18N_EN[ko]; return (typeof e === "string" && e) ? e : dflt; };
    M.heroA = sfx(" 용사 학원", " Hero Academy"); M.acadA = sfx(" 학원", " Academy");   // ' 용사 학원' · ' 학원'
    return M;
  }
  function en1(s){                                  // 한국어 → 영어 (영어판)
    if(!HAN.test(s)) return s;
    var m = maps(), x, a, b;
    if(m.f[s] !== undefined) return m.f[s];
    if((x = /^“([^”]+)”\s+(.+)$/.exec(s))){ a = en1(x[1]); b = en1(x[2]); return (a === x[1] && b === x[2]) ? s : b + " “" + a + "”"; }
    if((x = /^(.+?) 용사 학원$/.exec(s)) && m.acad[x[1]]) return m.acad[x[1]] + m.heroA;
    if((x = /^(.+?) 학원$/.exec(s)) && m.acad[x[1]]) return m.acad[x[1]] + m.acadA;
    if((x = /^(\S+) (\S+)$/.exec(s)) && m.adj[x[1]] && m.noun[x[2]]) return m.adj[x[1]] + " " + m.noun[x[2]];
    if(s.length >= 2 && m.sur[s.charAt(0)] && m.giv[s.slice(1)]) return m.sur[s.charAt(0)] + " " + m.giv[s.slice(1)];
    return s;
  }
  function ko1(s){                                  // 영어 → 한국어 (서버로 보낼 때 · 영어로 쌓은 세이브를 한국어판에서)
    if(HAN.test(s) || !LAT2.test(s)) return s;
    var m = maps(), x, a, b, hs = m.heroA.replace(/^\s+/, ""), as = m.acadA.replace(/^\s+/, "");
    if(m.r[s] !== undefined && !m.amb[s]) return m.r[s];
    if((x = /^(.+?)\s+“([^”]+)”$/.exec(s))){ a = ko1(x[2]); b = ko1(x[1]); return (a === x[2] && b === x[1]) ? s : "“" + a + "” " + b; }
    if(s.slice(-hs.length - 1) === " " + hs && (a = m.racad[s.slice(0, -hs.length - 1)])) return a + " 용사 학원";
    if(s.slice(-as.length - 1) === " " + as && (a = m.racad[s.slice(0, -as.length - 1)])) return a + " 학원";
    if((x = /^(\S+) (\S+)$/.exec(s))){
      if(m.radj[x[1]] && m.rnoun[x[2]]) return m.radj[x[1]] + " " + m.rnoun[x[2]];
      if(m.rsur[x[1]] && m.rgiv[x[2]]) return m.rsur[x[1]] + m.rgiv[x[2]];
    }
    return s;
  }
  function deep(x, f, d){
    if(typeof x === "string") return f(x);
    if(!x || typeof x !== "object" || d > 40) return x;
    if(Array.isArray(x)){ var a = new Array(x.length); for(var i = 0; i < x.length; i++) a[i] = deep(x[i], f, d + 1); return a; }
    var o = {}; for(var k in x) if(Object.prototype.hasOwnProperty.call(x, k)) o[k] = (d === 0 && k === "log") ? x[k] : deep(x[k], f, d + 1);
    return o;
  }
  I18N.toCur = function(x){ try{ return deep(x, I18N.lang === "en" ? en1 : ko1, 0); }catch(e){ return x; } };
  I18N.toKo = function(x){ if(I18N.lang !== "en") return x; try{ return deep(x, ko1, 0); }catch(e){ return x; } };
})();
/* 지난 한국어 글을 영어로 (1010 · 5단계) — 세이브에 글로 남은 일지 · 상담 기록처럼 한국어판에서 쓴 글을 영어판에서 보여 줄 때.
   I18N.line(s) — 한국어 글(HTML 가능)을 영어 표에 거꾸로 맞춰 본다: 표의 글과 통째로 같거나, 문장 틀의 글자 부분이 모두 맞고
   자리({n})에 든 것도 모두 옮길 수 있을 때(숫자 · 이름 · 표의 글 · 안쪽 문장 틀 · '가 · 나' 목록)만 영어로. 하나라도 못 옮기면
   원래 글 그대로 (틀린 영어보다 한국어가 낫다). 화면에 그릴 때만 바꾸고 세이브는 그대로다.
   영어 값에서 쓰지 않는 자리(조사 등)는 짧은 글만 받는다. game.html 은 curLog 로 부른다 (한국어판 · I18N 이 없으면 그대로) */
(function(){
  var HAN = /[가-힣]/, NLS = /[ \t]*\n[ \t\n]*/g, RE_ESC = /[.*+?^${}()|[\]\\]/g, TAG = /<(\/?)([A-Za-z][A-Za-z0-9-]*)>/g;
  var BOUND = /^(?: ·| \(| —| <| \/|<|\(|·|\.|,|:)/, SEP = /( · |, | \/ )/, MAXD = 6;
  var JOSA = /^(?:\(으\)로|\(이\)|으로|이라는|라는|이란|란|에게|이|가|은|는|을|를|과|와|로|의)(?=[^가-힣]|$)/;   // 붙은 두 자리 사이 — 이름 뒤 조사
  var EPI = /^(<span\b[^<>]*\bclass="epi"[^<>]*>)“([^”]+)”<\/span>\s+([가-힣]+)([^가-힣]*)$/;   // “이명” 이름(뒤 기호) → Name “Epithet”
  var WRAP = /^(<([A-Za-z][A-Za-z0-9-]*)(?:\s[^<>]*)?>)([\s\S]*?)(<\/\2>)$/;
  var CORE = /^([^가-힣“]*)([“가-힣](?:[\s\S]*[가-힣”])?)([^가-힣”]*)$/;
  var T = null, EX = null, IDX = null, memo = new Map(), fail = new Map(), busy = new Set();
  function litSrc(l){                               // 틀의 글자 부분 → 정규식 (원문 태그의 속성은 무엇이든)
    var out = "", last = 0, m; TAG.lastIndex = 0;
    while((m = TAG.exec(l))){
      out += l.slice(last, m.index).replace(RE_ESC, "\\$&") + (m[1] ? "</" + m[2] + "\\s*>" : "<" + m[2] + "(?:[\\s/][^<>]*)?>");
      last = TAG.lastIndex;
    }
    return out + l.slice(last).replace(RE_ESC, "\\$&");
  }
  function build(){
    T = []; EX = {}; IDX = {};
    var en = I18N.en, seen = {}, list = [], k, b, ko;
    for(k in en) if(k.indexOf("|") < 0) list.push([k, k]);
    for(k in en){ b = k.indexOf("|"); if(b > 0){ ko = k.slice(b + 1); if(!(ko in en)){ list.push([k, ko]); if(EX[ko] === undefined) EX[ko] = en[k]; } } }
    list.forEach(function(x){
      var key = x[1], v = en[x[0]];
      if(typeof v !== "string" || !v || x[0].charAt(0) === "_" || key.indexOf("{") < 0 || !HAN.test(key) || seen[key]) return;
      seen[key] = 1;
      var lits = [], phs = [], last = 0, m, re = /\{(\d+)\}/g;
      while((m = re.exec(key))){ lits.push(key.slice(last, m.index)); phs.push(+m[1]); last = re.lastIndex; }
      lits.push(key.slice(last));
      var probe = "", len = 0, used = {};
      lits.forEach(function(l){ len += l.length; l.split(/<[^<>]*>/).forEach(function(y){ y = y.trim(); if(y.length > probe.length) probe = y; }); });
      if(!probe) return;
      (v.match(/\{\d+/g) || []).forEach(function(z){ used[+z.slice(1)] = 1; });
      T.push({v: v === "∅" ? "" : v, lits: lits, phs: phs, n: lits.length - 1, probe: probe, len: len, used: used, re: null});
    });
    T.sort(function(a, c){ return c.len - a.len; });                 // 글자 부분이 긴(덜 흔한) 틀부터
    T.forEach(function(t, i){ var g = t.probe.slice(0, 2); (IDX[g] = IDX[g] || []).push(i); });   // 찾기 — 앞 두 글자(한 글자면 그 글자)로
  }
  function cands(s){                                // 이 글 안에 찾기 글이 든 틀 (차례대로)
    var got = {}, out = [], i, g, L, j;
    for(i = 0; i < s.length; i++){
      for(j = 1; j <= 2; j++){
        g = s.substr(i, j); if(g.length !== j || got[g]) continue; got[g] = 1;
        if((L = IDX[g])) for(var q = 0; q < L.length; q++) if(s.indexOf(T[L[q]].probe) >= 0) out.push(L[q]);
      }
    }
    return out.sort(function(a, c){ return a - c; });
  }
  function prep(t){ t.re = t.lits.map(function(l){ var src = litSrc(l); return {first: new RegExp("^" + src), any: new RegExp(src, "g"), last: new RegExp("(?:" + src + ")$")}; }); }
  function tagsOf(s, out){ var m, re = /<([A-Za-z][A-Za-z0-9-]*)(\s[^<>]*)?\/?>/g; while((m = re.exec(s))) out.push(m); }
  function putTags(v, ms){                          // 영어 값의 <b> · <b#2> 에 원문 태그(속성째)를 차례로 — i18nFind 와 같은 규칙
    if(v.indexOf("<") < 0 || !ms.length) return v;
    var list = {}, cnt = {};
    ms.forEach(function(m){ var n = m[1].toLowerCase(); (list[n] = list[n] || []).push(m[0]); });
    return v.replace(I18N_VTAG, function(all, n, idx){
      var L = list[n.toLowerCase()]; if(!L) return idx ? "<" + n + ">" : all;
      var i = idx ? (+idx - 1) : ((cnt[n] = (cnt[n] || 0) + 1) - 1);
      return L[i] !== undefined ? L[i] : (idx ? "<" + n + ">" : all);
    });
  }
  function balanced(a){                             // 태그가 반쪽으로 잘리지 않았고 여닫음이 맞는 글만 자리에 받는다
    if(/<[^>]*$/.test(a) || /^[^<]*>/.test(a)) return false;
    var st = [], m, re = /<(\/?)([A-Za-z][A-Za-z0-9-]*)[^<>]*?(\/?)>/g;
    while((m = re.exec(a))){
      var n = m[2].toLowerCase(); if(m[3] || n === "br" || n === "img" || n === "hr" || n === "wbr") continue;
      if(!m[1]) st.push(n); else if(st.pop() !== n) return false;
    }
    return !st.length;
  }
  function num(x){ return Number(String(x).replace(/<[^<>]*>/g, "").replace(/,/g, "").trim()); }
  function exact(c){
    var v = i18nFind(null, c);
    if(v === undefined){ var e = EX[i18nKey(c)]; if(typeof e === "string" && e){ var ms = []; tagsOf(c, ms); v = putTags(e, ms); } }
    if(typeof v !== "string" || !v) return undefined;
    v = v === "∅" ? "" : v;
    return HAN.test(v) || /\{\d/.test(v) ? undefined : v;
  }
  function named(c){ var r; try{ r = I18N.toCur(c); }catch(e){ return undefined; } return (typeof r === "string" && r !== c && !HAN.test(r)) ? r : undefined; }
  function word(c){ var r = exact(c); if(r === undefined) r = named(c); return r === undefined ? null : r; }
  function arg(t, ph, a, d){
    if(!balanced(a)) return null;
    if(!t.used[ph]) return (a.length <= 3 || !HAN.test(a)) ? "" : null;   // 영어에서 쓰지 않는 자리 (조사 등)
    if(!HAN.test(a)) return a;
    return d < MAXD ? tr(a, d + 1) : null;
  }
  function cand(t, i, s, pos){                      // lits[i] 가 놓일 수 있는 곳 [시작, 길이] — 빈 글(붙은 두 자리)이면 ' · ' · ' (' · 태그 · 문장부호 앞과 조사 앞마다
    var out = [], m, g, p;
    if(t.lits[i] === ""){
      out.push([pos, 0]);
      for(p = pos + 1; p <= s.length && out.length < 64; p++)
        if(p === s.length || BOUND.test(s.slice(p, p + 3)) || (HAN.test(s.charAt(p - 1)) && JOSA.test(s.slice(p, p + 4)))) out.push([p, 0]);
      return out;
    }
    g = t.re[i].any; g.lastIndex = pos;
    while(out.length < 64 && (m = g.exec(s))){ out.push([m.index, m[0].length]); g.lastIndex = m.index + 1; }
    return out;
  }
  function solve(t, s, k, pos, d, M, bud){          // 자리 k 가 pos 에서 시작 — 뒤의 자리까지 {args, lits} 또는 null (자리 · 위치마다 한 번)
    var mk = k + ":" + pos;
    if(M.has(mk)) return M.get(mk);
    M.set(mk, null);
    var res = null, a, i;
    if(++bud.n <= 600){
      if(k + 1 === t.n){
        var rest = s.slice(pos), ml = t.re[t.n].last.exec(rest);
        if(ml && (a = arg(t, t.phs[k], rest.slice(0, ml.index), d)) !== null) res = {args: [a], lits: [ml[0]]};
      } else {
        var cs = cand(t, k + 1, s, pos);
        for(i = 0; i < cs.length && !res; i++){
          if((a = arg(t, t.phs[k], s.slice(pos, cs[i][0]), d)) === null) continue;
          var sub = solve(t, s, k + 1, cs[i][0] + cs[i][1], d, M, bud);
          if(sub) res = {args: [a].concat(sub.args), lits: [s.substr(cs[i][0], cs[i][1])].concat(sub.lits)};
        }
      }
    }
    M.set(mk, res);
    return res;
  }
  function finish(t, lits, args){
    var ms = [], val = {}, i, out = "";
    lits.forEach(function(x){ tagsOf(x, ms); });
    for(i = 0; i < t.phs.length; i++) val[t.phs[i]] = args[i];
    var parts = I18N.compile(putTags(t.v, ms));
    for(i = 0; i < parts.length; i++){
      var p = parts[i];
      if(typeof p === "string"){ out += p; continue; }
      if(val[p.i] === undefined) return null;
      out += p.one !== undefined ? (num(val[p.i]) === 1 ? p.one : p.many) : val[p.i];
    }
    return HAN.test(out) ? null : out;
  }
  function tmpl(s, d){
    var cs = cands(s);
    for(var j = 0; j < cs.length; j++){
      var t = T[cs[j]];
      if(!t.re) prep(t);
      var m0 = t.re[0].first.exec(s);
      if(!m0 || !t.re[t.n].last.test(s)) continue;
      var r = solve(t, s, 0, m0[0].length, d, new Map(), {n: 0}), out;
      if(r && (out = finish(t, [m0[0]].concat(r.lits), r.args)) !== null) return out;
    }
    return null;
  }
  function list(s, d){                              // 자리에 든 '가 · 나 · 다' · '가, 나' — 하나씩 옮긴다
    if(!SEP.test(s)) return null;
    var parts = s.split(SEP), out = "", r, i;
    for(i = 0; i < parts.length; i++){
      if(i % 2){ out += parts[i]; continue; }
      if((r = tr(parts[i], d + 1)) === null) return null;
      out += r;
    }
    return out;
  }
  function pair(s, d){                              // 자리에 든 '왕국력 233년 시내 대회' — 빈칸 한 곳에서 갈라 두 쪽이 다 옮겨지면 (영어도 같은 차례)
    var sp = [], i, a, b;
    for(i = 0; i < s.length; i++) if(s.charAt(i) === " ") sp.push(i);
    if(!sp.length || sp.length > 5) return null;
    for(i = sp.length - 1; i >= 0; i--){
      if((b = tr(s.slice(sp[i]), d + 1)) === null || (a = tr(s.slice(0, sp[i]), d + 1)) === null) continue;   // 오른쪽은 빈칸째 (' 등' 같은 키)
      return a + b;
    }
    return null;
  }
  function core(s){                                 // 자리에 든 '이름(C)' · '이름 Lv.11' · '이름 +8' — 한글 부분만 옮기고 앞뒤 기호 · 숫자는 그대로
    var m = CORE.exec(s), r;
    if(!m || (!m[1] && !m[3]) || (r = word(m[2])) === null) return null;
    return m[1] + r + m[3];
  }
  function tr1(s, d){
    var a = /^\s*/.exec(s)[0], z = /\s*$/.exec(s)[0], c = s.slice(a.length, s.length - z.length), r, w, x, y;
    if(!c) return s;
    if((a || z) && (r = exact(s)) !== undefined) return r;                       // 앞뒤 빈칸까지 키인 글 (' 등' 등)
    if(c.indexOf("‘마스터’") >= 0){                                              // 1년차 암흑 사제의 ‘마스터’ (masterQ) — 따옴표를 떼고 맞춘 뒤 영어도 ‘Master’
      if((r = tr(c.replace(/‘마스터’/g, "마스터"), d)) !== null) return a + r.replace(/‘?\bMaster\b’?/g, "‘Master’") + z;
    }
    if((r = exact(c)) !== undefined || (r = named(c)) !== undefined) return a + r + z;
    if((w = EPI.exec(c)) && (x = word(w[2])) !== null && (y = word(w[3])) !== null) return a + y + " " + w[1] + "“" + x + "”</span>" + w[4] + z;
    if(d < MAXD && (w = WRAP.exec(c)) && w[3].indexOf("<" + w[2]) < 0 && (r = tr(w[3], d + 1)) !== null) return a + w[1] + r + w[4] + z;
    if(d > 0 && d < MAXD && (w = /^\(([^()]*)\)$/.exec(c)) && (r = tr(w[1], d + 1)) !== null) return a + "(" + r + ")" + z;   // 자리에 든 (…)
    if((r = tmpl(c, d)) !== null) return a + r + z;
    if(d > 0 && d < MAXD){
      if((r = list(c, d)) !== null || (r = core(c)) !== null || (d <= 3 && !SEP.test(c) && (r = pair(c, d)) !== null)) return a + r + z;
    }
    return null;
  }
  function tr(s, d){
    if(!HAN.test(s)) return s;
    var r = memo.get(s), f;
    if(r !== undefined) return r;
    if((f = fail.get(s)) !== undefined && f <= d) return null;   // 이 깊이(또는 더 얕은 곳)에서 이미 못 옮긴 글
    if(busy.has(s)) return null;                    // 자기 자신을 다시 부르면 실패로
    busy.add(s);
    try{ r = tr1(s, d); }finally{ busy.delete(s); }
    if(r === null) fail.set(s, d); else memo.set(s, r);
    return r;
  }
  I18N.line = function(s){
    if(I18N.en === null || typeof s !== "string" || !HAN.test(s)) return s;
    try{
      if(!T) build();
      var r = tr(s.indexOf("\n") >= 0 ? s.replace(NLS, " ") : s, 0);
      return r === null ? s : r;
    }catch(e){ return s; }
  };
})();
/* 스크립트 밖 HTML(상단 바 이름 · title 등)은 처음 한 번 바꾼다 — 이후 화면은 _T · _L 로 그려진다 */
I18N.dom = function(root){
  if(I18N.en === null || !root) return;
  var H = /[가-힣]/, A = ["title", "aria-label", "placeholder", "alt"], en = I18N.en;
  var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {acceptNode: function(t){
    var p = t.parentNode && t.parentNode.nodeName; return (p === "SCRIPT" || p === "STYLE") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }});
  var t;
  while((t = w.nextNode())){
    var v = t.nodeValue; if(!H.test(v)) continue;
    var k = v.trim(); if(en[k] !== undefined) t.nodeValue = v.replace(k, function(){ return en[k]; });
  }
  var els = root.querySelectorAll("[title],[aria-label],[placeholder],[alt]");
  for(var i = 0; i < els.length; i++) for(var j = 0; j < A.length; j++){
    var a = els[i].getAttribute(A[j]); if(a && H.test(a) && en[a] !== undefined) els[i].setAttribute(A[j], en[a]);
  }
};
if(I18N.en !== null){
  try{ I18N.dom(document.documentElement); if(I18N.en[document.title] !== undefined) document.title = I18N.en[document.title]; }catch(e){}
  /* 영어에서는 한국어 조사(이/가 · 은/는 · 을/를 · 과/와 · 으로/로)를 붙이지 않는다 — 함수 선언은 미리 올라가 있으므로 여기서 바꿔 끼운다
     (iga · eunn · gwa · eulr 은 jo 를 부른다). 문장 틀의 조사 자리는 영어 표에서 그 {n} 을 안 쓰면 된다 */
  try{ jo = function(){ return ""; }; ro = function(){ return ""; }; }catch(e){}
  /* 영어 글이 길어 넘치는 칸 — CSS 를 덧붙인다 (게임 쪽 CSS 는 그대로). 학생 명부 책은 그림자 DOM 이라 따로 넣는다 */
  try{
    if(I18N_CSS){ var st = document.createElement("style"); st.id = "i18nCss"; st.textContent = I18N_CSS; (document.head || document.documentElement).appendChild(st); }
    if(I18N_RBCSS && Element.prototype.attachShadow){
      var aS = Element.prototype.attachShadow;
      Element.prototype.attachShadow = function(o){
        var r = aS.call(this, o);
        if(this.id === "rbHost") setTimeout(function(){
          if(!r.getElementById("i18nCss")){ var s2 = document.createElement("style"); s2.id = "i18nCss"; s2.textContent = I18N_RBCSS; r.appendChild(s2); }
        }, 0);
        return r;
      };
    }
  }catch(e){}
}
/* I18N 끝 */
