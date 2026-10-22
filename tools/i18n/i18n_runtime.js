/* I18N 시작 — 영어판 번역 함수 (1010 · tools/i18n/i18n_runtime.js — 빌드 때 i18n_build.py 가 여기에 넣는다. game.html 원본에는 없다)
   _T("한국어"[, 문맥]) · _L`…${x}…` · _LC.문맥`…` — 한국어면 받은 글을 그대로 돌려주고, 영어면 영어 표(I18N_EN)에서 찾는다. 없으면 한국어 그대로.
   문맥 = 그 글이 든 맨 위 선언 이름 — 영어 표에 "문맥|한국어" 키가 있을 때만 빌드가 붙인다 (같은 한국어를 곳마다 달리 옮길 때).
   HS_LANG 은 <head> 맨 앞의 작은 스크립트가 정한다 (?lang=en|ko|ja · 공개 뒤에는 설정 · 브라우저 언어 · 일본어는 config.json "ja" 로 공개 — 1014).
   1014 일본어판 — I18N.tab 이 지금 언어의 표 (영어 I18N_EN · 일본어 I18N_JA — 비어 있으면 null 이라 한국어 그대로). 이름 모양 바꾸기(toCur) ·
   지난 일지 옮기기(line) · 조사 비우기도 일본어 표로. en_layout.css 는 영어만 · 일본어는 글꼴 · 줄바꿈 CSS(I18N_JACSS)를 붙인다.
   1022 중국어 간체판 — HS_LANG "zh-Hans" · 표 I18N_ZHS (비어 있으면 한국어 그대로) · 이름 모양은 일본어처럼 「二つ名」名字 · 白银勇者学院 · 붙인 유물 이름 ·
   한국식 성+이름은 빈칸 없이(金道允) · 대사 따옴표는 한국어처럼 “ ” · 글꼴 · 줄바꿈 CSS(I18N_ZHSCSS).
   1022 중국어 번체판(대만) — HS_LANG "zh-Hant" · 표 I18N_ZHT · 이름 모양은 간체와 같다(「不屈之壁」高文 · 白銀勇者學院) · 대사 따옴표는 「」 ·
   1년차 암흑 사제의 마스터는 『大師』 · 글꼴 · 줄바꿈 CSS(I18N_ZHTCSS). */
var I18N_EN = /*@@EN@@*/{};
var I18N_JA = /*@@JA@@*/{};
var I18N_ZHS = /*@@ZHS@@*/{};
var I18N_ZHT = /*@@ZHT@@*/{};
var I18N_CSS = /*@@CSS@@*/"", I18N_RBCSS = /*@@RBCSS@@*/"";   /* 영어 화면 고침 — en_layout.css · en_layout_rbook.css (영어일 때만 붙인다) */
var I18N_JACSS = /*@@JACSS@@*/"", I18N_JARBCSS = /*@@JARBCSS@@*/"";   /* 일본어 화면 — 줄바꿈 · 도트 폰트를 껐을 때의 글꼴 (빌드가 게임 CSS 에서 만든다 + ja_layout.css · 일본어일 때만) */
var I18N_ZHSCSS = /*@@ZHSCSS@@*/"", I18N_ZHSRBCSS = /*@@ZHSRBCSS@@*/"";   /* 중국어 간체 화면 (1022) — 일본어와 같은 줄바꿈 · 도트 폰트를 껐을 때는 기기 글꼴 (+ zh-Hans_layout.css) */
var I18N_ZHTCSS = /*@@ZHTCSS@@*/"", I18N_ZHTRBCSS = /*@@ZHTRBCSS@@*/"";   /* 중국어 번체 화면 (1022 · 대만) — 간체와 같다 (+ zh-Hant_layout.css) */
var I18N = (function(){
  var lang = (typeof HS_LANG === "string" && (HS_LANG === "en" || HS_LANG === "ja" || HS_LANG === "zh-Hans" || HS_LANG === "zh-Hant")) ? HS_LANG : "ko";
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
  var tab = lang === "en" ? I18N_EN : (lang === "ja" && Object.keys(I18N_JA).length) ? I18N_JA : (lang === "zh-Hans" && Object.keys(I18N_ZHS).length) ? I18N_ZHS
          : (lang === "zh-Hant" && Object.keys(I18N_ZHT).length) ? I18N_ZHT : null;
  var pub = typeof HS_LANG_PUBLIC !== "undefined" && !!HS_LANG_PUBLIC;
  return {lang: lang, tab: tab, pub: pub, pubJa: pub && typeof HS_LANG_JA !== "undefined" && !!HS_LANG_JA,   // pubJa — 일본어 공개 (config.json "ja")
          pubZh: pub && typeof HS_LANG_ZH !== "undefined" && !!HS_LANG_ZH,                                  // pubZh — 중국어 간체 공개 (config.json "zh-Hans" · 1022)
          pubZhT: pub && typeof HS_LANG_ZHT !== "undefined" && !!HS_LANG_ZHT,                               // pubZhT — 중국어 번체 공개 (config.json "zh-Hant" · 1022)
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
function i18nFind(ctx, k0){                  // 원문(자리표 {n} 포함) → 지금 언어의 값 (태그 속성 되돌림) · 없으면 undefined
  var k = i18nKey(k0), en = I18N.tab, v;
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
  if(I18N.tab === null) return s;
  var key = c === undefined ? s : c + "|" + s, v = I18N.tcache.get(key);
  if(v === undefined){ v = i18nFind(c, s); if(v === undefined) v = s; I18N.tcache.set(key, v); }
  return v;
}
function _Lx(ctx, strs, args){
  var n = args.length, i, out;
  if(I18N.tab !== null){
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
/* 세이브 · 서버의 데이터 글 (1010 · 3단계 · 1014 일본어) — 학생 이름 · 이명 · 유물 · 학원 이름 · 진로 · 스킬 이름처럼 세이브와 서버에 글 그대로 남는 것.
   I18N.toCur(x) — 지금 언어로 (세이브를 불러올 때 · 서버에서 받은 남의 학원).  I18N.toKo(x) — 한국어 원문으로 (서버로 보낼 때 · 한국어판이면 그대로).
   x 는 글 · 배열 · 객체 (객체 · 배열은 고친 사본 · 맨 위 log(일지)는 그대로). 표의 글 하나와 통째로 같은 글과 정해진 모양만 바꾼다 —
   “이명” 이름 · ○○ 용사 학원 · ○○ 학원 · 유물(형용사 명사) · 한국식 성+이름. 문장(일지 등)은 쓰인 언어 그대로. game.html 은 koData · curData 로 부른다.
   어느 언어로 쌓인 글이든(영어 · 일본어) 먼저 한국어로 되돌린 뒤 지금 언어로 — 영어로 하다 일본어판으로 바꿔도 이름이 따라온다.
   모양: 영어 Name “Epithet” · Argent Hero Academy · Worn Ring · Kim Doyoon / 일본어 「不屈の城壁」ガウェイン · 白銀勇者学園 · 古びた指輪 · キム・ドユン /
   중국어 간체(1022) 「不屈之壁」高文 · 白银勇者学院 · 破旧的戒指 · 金道允 / 번체(대만) 「不屈之壁」高文 · 白銀勇者學院 · 破舊戒指 · 金道允 */
(function(){
  var NAME_CTX = {NAME_POOL: 1, L5_NPC_ACAD: 1, MON: 1, EPI_CROWD: 1};     // 통째로 바꾸는 이름 (문맥 키) — 같은 글이면 전역 값보다 먼저
  /* 값 하나에 한국어가 여럿인 것 중 세이브 · 서버에 남는 것 — 되돌릴 한국어 (유물 옵션 · 스킬 · 이름 없는 학생) */
  /* 1018 — "Sanctuary" = 성역 선포(팔라딘 필살기 — 졸업생 재능 · 스킬로 세이브에 남는다) · 성역(전투 버프 이름 — 남지 않는다). check_save 왕복 */
  var KO_PREF = {en: {"DEF": "방어력", "Slash": "베기", "Unknown": "무명", "EXP": "경험치", "Sanctuary": "성역 선포"},
                 ja: {"斬撃": "베기", "経験値": "경험치"},
                 "zh-Hans": {"斩击": "베기", "经验值": "경험치"}, "zh-Hant": {"斬擊": "베기", "經驗值": "경험치"}};
  var MS = {}, HAN = /[가-힣]/, LAT2 = /[A-Za-z][\s\S]*[A-Za-z]/, JPC = /[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]/, PH = /\{\d/;
  var KANA = /[\u3040-\u30ff]/, ZHC = /[\u3400-\u9fff\uf900-\ufaff]/;     // 가나가 있으면 일본어 · 한자만이면 일본어 · 중국어 둘 다 맞춰 본다 (1022)
  function maps(L){
    if(MS[L]) return MS[L];
    var T = L === "en" ? I18N_EN : L === "ja" ? I18N_JA : L === "zh-Hant" ? I18N_ZHT : I18N_ZHS;
    var M = {f: {}, r: {}, amb: {}, sur: {}, giv: {}, acad: {}, adj: {}, noun: {}, rsur: {}, rgiv: {}, racad: {}, radj: {}, rnoun: {}};
    var k, v, b, c, ko, part = {SUR: "sur", GIV: "giv", ACAD: "acad", RELIC_ADJ: "adj", RELIC_NOUN: "noun"};
    for(k in T){
      v = T[k];
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
    for(k in T){
      b = k.indexOf("|"); if(b < 0 || !NAME_CTX[k.slice(0, b)]) continue;
      ko = k.slice(b + 1); v = T[k];
      M.f[ko] = v; M.r[v] = ko; delete M.amb[v];
    }
    var pref = KO_PREF[L] || {};
    for(k in pref) if(M.f[pref[k]] === k){ M.r[k] = pref[k]; delete M.amb[k]; }
    var sfx = function(ko, dflt){ var e = T[ko]; return (typeof e === "string" && e) ? e : dflt; };
    if(L === "ja"){
      M.heroA = sfx(" 용사 학원", "勇者学園"); M.acadA = sfx(" 학원", "学園");
      M.epi = function(a, n){ return "「" + a + "」" + n; }; M.rsep = ""; M.nsep = "・";
    } else if(L === "zh-Hans" || L === "zh-Hant"){                    // 1022 — 「不屈之壁」高文 · 白银勇者学院 · 破旧戒指 · 金道允 (번체도 같은 모양)
      M.heroA = sfx(" 용사 학원", L === "zh-Hant" ? "勇者學院" : "勇者学院"); M.acadA = sfx(" 학원", L === "zh-Hant" ? "學院" : "学院");
      M.epi = function(a, n){ return "「" + a + "」" + n; }; M.rsep = ""; M.nsep = "";
    } else {
      M.heroA = sfx(" 용사 학원", " Hero Academy"); M.acadA = sfx(" 학원", " Academy");   // ' 용사 학원' · ' 학원'
      M.epi = function(a, n){ return n + " “" + a + "”"; }; M.rsep = " "; M.nsep = " ";
    }
    return (MS[L] = M);
  }
  function cur1(L, s){                              // 한국어 → L (영어 · 일본어 · 중국어)
    if(!HAN.test(s)) return s;
    var m = maps(L), x, a, b;
    if(m.f[s] !== undefined) return m.f[s];
    if((x = /^“([^”]+)”\s+(.+)$/.exec(s))){ a = cur1(L, x[1]); b = cur1(L, x[2]); return (a === x[1] && b === x[2]) ? s : m.epi(a, b); }
    if((x = /^(.+?) 용사 학원$/.exec(s)) && m.acad[x[1]]) return m.acad[x[1]] + m.heroA;
    if((x = /^(.+?) 학원$/.exec(s)) && m.acad[x[1]]) return m.acad[x[1]] + m.acadA;
    if((x = /^(\S+) (\S+)$/.exec(s)) && m.adj[x[1]] && m.noun[x[2]]) return m.adj[x[1]] + m.rsep + m.noun[x[2]];
    if(s.length >= 2 && m.sur[s.charAt(0)] && m.giv[s.slice(1)]) return m.sur[s.charAt(0)] + m.nsep + m.giv[s.slice(1)];
    return s;
  }
  function koEn(s){                                 // 영어 → 한국어 (서버로 보낼 때 · 영어로 쌓은 세이브를 다른 언어판에서)
    if(HAN.test(s) || !LAT2.test(s)) return s;
    var m = maps("en"), x, a, b, hs = m.heroA.replace(/^\s+/, ""), as = m.acadA.replace(/^\s+/, "");
    if(m.r[s] !== undefined && !m.amb[s]) return m.r[s];
    if((x = /^(.+?)\s+“([^”]+)”$/.exec(s))){ a = koEn(x[2]); b = koEn(x[1]); return (a === x[2] && b === x[1]) ? s : "“" + a + "” " + b; }
    if(s.slice(-hs.length - 1) === " " + hs && (a = m.racad[s.slice(0, -hs.length - 1)])) return a + " 용사 학원";
    if(s.slice(-as.length - 1) === " " + as && (a = m.racad[s.slice(0, -as.length - 1)])) return a + " 학원";
    if((x = /^(\S+) (\S+)$/.exec(s))){
      if(m.radj[x[1]] && m.rnoun[x[2]]) return m.radj[x[1]] + " " + m.rnoun[x[2]];
      if(m.rsur[x[1]] && m.rgiv[x[2]]) return m.rsur[x[1]] + m.rgiv[x[2]];
    }
    return s;
  }
  function koJa(s){                                 // 일본어 → 한국어 (1014)
    if(HAN.test(s) || !JPC.test(s)) return s;
    var m = maps("ja"), x, a, b, i, H = m.heroA, A = m.acadA;
    if(m.r[s] !== undefined && !m.amb[s]) return m.r[s];
    if((x = /^「([^」]+)」\s*([\s\S]+)$/.exec(s))){ a = koJa(x[1]); b = koJa(x[2]); return (a === x[1] && b === x[2]) ? s : "“" + a + "” " + b; }
    if(H && s.length > H.length && s.slice(-H.length) === H && (a = m.racad[s.slice(0, -H.length)])) return a + " 용사 학원";
    if(A && s.length > A.length && s.slice(-A.length) === A && (a = m.racad[s.slice(0, -A.length)])) return a + " 학원";
    for(a in m.radj) if(s.length > a.length && s.slice(0, a.length) === a && (b = m.rnoun[s.slice(a.length)])) return m.radj[a] + " " + b;
    if((i = s.indexOf("・")) > 0 && (a = m.rsur[s.slice(0, i)]) && (b = m.rgiv[s.slice(i + 1)])) return a + b;
    return s;
  }
  function koZh(s, L){                              // 중국어 → 한국어 (1022 · L = zh-Hans 간체 · zh-Hant 번체) — 성+이름은 빈칸 없이 붙어 있어 성 한두 글자로 갈라 본다
    if(HAN.test(s) || !ZHC.test(s) || KANA.test(s)) return s;
    L = L || "zh-Hans";
    var m = maps(L), x, a, b, i, H = m.heroA, A = m.acadA;
    if(m.r[s] !== undefined && !m.amb[s]) return m.r[s];
    if((x = /^「([^」]+)」\s*([\s\S]+)$/.exec(s))){ a = koZh(x[1], L); b = koZh(x[2], L); return (a === x[1] && b === x[2]) ? s : "“" + a + "” " + b; }
    if(H && s.length > H.length && s.slice(-H.length) === H && (a = m.racad[s.slice(0, -H.length)])) return a + " 용사 학원";
    if(A && s.length > A.length && s.slice(-A.length) === A && (a = m.racad[s.slice(0, -A.length)])) return a + " 학원";
    for(a in m.radj) if(s.length > a.length && s.slice(0, a.length) === a && (b = m.rnoun[s.slice(a.length)])) return m.radj[a] + " " + b;
    for(i = 1; i <= 2 && i < s.length; i++) if((a = m.rsur[s.slice(0, i)]) && (b = m.rgiv[s.slice(i)])) return a + b;
    return s;
  }
  function anyKo(s){
    if(HAN.test(s)) return s;
    if(KANA.test(s)) return koJa(s);
    if(ZHC.test(s)){                                // 한자만 — 지금 언어를 먼저 맞춰 본다 (일본어 · 간체 · 번체 표의 글은 서로 겹치지 않는다 — 겹쳐도 같은 한국어)
      var order = I18N.lang === "zh-Hant" ? ["zh-Hant", "zh-Hans", "ja"] : I18N.lang === "zh-Hans" ? ["zh-Hans", "zh-Hant", "ja"] : ["ja", "zh-Hans", "zh-Hant"], r, best = null;
      for(var oi = 0; oi < order.length; oi++){   // 다 옮겨진 것을 먼저 — 간체 · 번체에 같은 글자인 이명(不屈之壁)만 맞고 이름(雷诺 · 雷諾)은 다른 표에 있을 수 있다
        r = order[oi] === "ja" ? koJa(s) : koZh(s, order[oi]);
        if(r !== s){ if(!ZHC.test(r) && !KANA.test(r)) return r; if(best === null) best = r; }
      }
      return best !== null ? best : s;
    }
    return LAT2.test(s) ? koEn(s) : s;
  }
  function deep(x, f, d){
    if(typeof x === "string") return f(x);
    if(!x || typeof x !== "object" || d > 40) return x;
    if(Array.isArray(x)){ var a = new Array(x.length); for(var i = 0; i < x.length; i++) a[i] = deep(x[i], f, d + 1); return a; }
    var o = {}; for(var k in x) if(Object.prototype.hasOwnProperty.call(x, k)) o[k] = (d === 0 && k === "log") ? x[k] : deep(x[k], f, d + 1);
    return o;
  }
  I18N.toCur = function(x){
    var L = I18N.lang;
    if((L === "ja" || L === "zh-Hans" || L === "zh-Hant") && I18N.tab === null) L = "ko";            // 일본어 · 중국어 표가 빈 빌드 — 한국어처럼
    try{ return deep(x, L === "ko" ? anyKo : function(s){ return cur1(L, anyKo(s)); }, 0); }catch(e){ return x; }
  };
  I18N.toKo = function(x){ if(I18N.lang === "ko") return x; try{ return deep(x, anyKo, 0); }catch(e){ return x; } };
})();
/* 지난 한국어 글을 영어로 (1010 · 5단계 · 1014 일본어도) — 세이브에 글로 남은 일지 · 상담 기록처럼 한국어판에서 쓴 글을 영어판 · 일본어판에서 보여 줄 때.
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
    var en = I18N.tab, seen = {}, list = [], k, b, ko;
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
    if(c.indexOf("‘마스터’") >= 0){                                              // 1년차 암흑 사제의 ‘마스터’ (masterQ) — 따옴표를 떼고 맞춘 뒤 영어도 ‘Master’ · 일본어는 『マスター』
      if((r = tr(c.replace(/‘마스터’/g, "마스터"), d)) !== null)
        return a + (I18N.lang === "ja" ? r.replace(/[『‘]?マスター[』’]?/g, "『マスター』") : I18N.lang === "zh-Hans" ? r.replace(/‘?大师’?/g, "‘大师’")
                    : I18N.lang === "zh-Hant" ? r.replace(/[『‘]?大師[』’]?/g, "『大師』")
                    : r.replace(/‘?\bMaster\b’?/g, "‘Master’")) + z;
    }
    if((r = exact(c)) !== undefined || (r = named(c)) !== undefined) return a + r + z;
    if((w = EPI.exec(c)) && (x = word(w[2])) !== null && (y = word(w[3])) !== null)
      return (I18N.lang === "ja" || I18N.lang === "zh-Hans" || I18N.lang === "zh-Hant") ? a + w[1] + "「" + x + "」</span>" + y + w[4] + z : a + y + " " + w[1] + "“" + x + "”</span>" + w[4] + z;   // 일본어 · 중국어는 「二つ名」名前
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
    if(I18N.tab === null || typeof s !== "string" || !HAN.test(s)) return s;   // 영어 · 일본어 · 중국어 (1014 · 1022 — 표 · 이름 모양이 그 언어)
    try{
      if(!T) build();
      var r = tr(s.indexOf("\n") >= 0 ? s.replace(NLS, " ") : s, 0);
      return r === null ? s : r;
    }catch(e){ return s; }
  };
})();
/* 스크립트 밖 HTML(상단 바 이름 · title 등)은 처음 한 번 바꾼다 — 이후 화면은 _T · _L 로 그려진다 */
I18N.dom = function(root){
  if(I18N.tab === null || !root) return;
  var H = /[가-힣]/, A = ["title", "aria-label", "placeholder", "alt"], en = I18N.tab;
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
/* 학생 명부 책(그림자 DOM)에 언어별 CSS 를 넣는다 — 책을 열 때 attachShadow 뒤에 */
I18N.shadowCss = function(css){
  if(!css || !Element.prototype.attachShadow) return;
  var aS = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function(o){
    var r = aS.call(this, o);
    if(this.id === "rbHost") setTimeout(function(){
      if(!r.getElementById("i18nCss")){ var s2 = document.createElement("style"); s2.id = "i18nCss"; s2.textContent = css; r.appendChild(s2); }
    }, 0);
    return r;
  };
};
I18N.addCss = function(id, css){
  if(!css) return;
  var st = document.createElement("style"); st.id = id; st.textContent = css; (document.head || document.documentElement).appendChild(st);
};
if(I18N.tab !== null){
  try{ I18N.dom(document.documentElement); if(I18N.tab[document.title] !== undefined) document.title = I18N.tab[document.title]; }catch(e){}
}
if(I18N.lang === "en"){
  /* 영어에서는 한국어 조사(이/가 · 은/는 · 을/를 · 과/와 · 으로/로)를 붙이지 않는다 — 함수 선언은 미리 올라가 있으므로 여기서 바꿔 끼운다
     (iga · eunn · gwa · eulr 은 jo 를 부른다). 문장 틀의 조사 자리는 영어 표에서 그 {n} 을 안 쓰면 된다 */
  try{ jo = function(){ return ""; }; ro = function(){ return ""; }; }catch(e){}
  /* 영어 글이 길어 넘치는 칸 — CSS 를 덧붙인다 (게임 쪽 CSS 는 그대로). 학생 명부 책은 그림자 DOM 이라 따로 넣는다 */
  try{ I18N.addCss("i18nCss", I18N_CSS); I18N.shadowCss(I18N_RBCSS); }catch(e){}
}
if(I18N.lang === "ja"){
  /* 일본어 (1014) — 줄바꿈(keep-all → normal) · 도트 폰트를 껐을 때의 글꼴. 글꼴 조각(@font-face)은 빌드 맨 끝 스크립트가 붙인다 (I18N_TAIL).
     한국어 조사는 영어처럼 비운다 (일본어 표가 있을 때 — 일본어 조사는 표의 값에 직접 쓴다) */
  if(I18N.tab !== null){ try{ jo = function(){ return ""; }; ro = function(){ return ""; }; }catch(e){} }
  try{ I18N.addCss("i18nJaCss", I18N_JACSS); I18N.shadowCss(I18N_JARBCSS); }catch(e){}
}
if(I18N.lang === "zh-Hans"){
  /* 중국어 간체 (1022) — 일본어와 같다: 줄바꿈 · 도트 폰트를 껐을 때의 글꼴(기기 글꼴) · 글꼴 조각은 빌드 맨 끝 스크립트(I18N_TAIL) · 조사는 비운다 (표가 있을 때) */
  if(I18N.tab !== null){ try{ jo = function(){ return ""; }; ro = function(){ return ""; }; }catch(e){} }
  try{ I18N.addCss("i18nZhCss", I18N_ZHSCSS); I18N.shadowCss(I18N_ZHSRBCSS); }catch(e){}
}
if(I18N.lang === "zh-Hant"){
  /* 중국어 번체 (1022 · 대만) — 간체와 같다 */
  if(I18N.tab !== null){ try{ jo = function(){ return ""; }; ro = function(){ return ""; }; }catch(e){} }
  try{ I18N.addCss("i18nZhtCss", I18N_ZHTCSS); I18N.shadowCss(I18N_ZHTRBCSS); }catch(e){}
}
/* I18N 끝 */
