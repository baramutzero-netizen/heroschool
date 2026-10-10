/* ── 오프닝 글 (1010) ──────────────────────────────────────────────────────────────
   예전 APNG 아홉 장(글 · 시공 균열 · '아, 이건 위험...' · 날짜 둘 · 타자기 제목 · 아버지 대사 셋)을 캔버스 글자로 그린다.
   효과와 때(ms)는 그 APNG 를 50ms 장마다 재서 옮긴 값 — 글자가 흐림에서 선명해지기 · 흐림 없이 서서히 · 타자기처럼 한 번에,
   지지직(청록 잔상 · 밀린 띠 · 검은 줄) · 글자마다 깜빡이다 꺼지기 · 꺼질 듯 깜빡이기 · 연이 통째로 흐려지기.
   글꼴은 나눔명조 ExtraBold(OpTxSerif) · 고운돋움(OpTxSans) — 오프닝 글자만 남긴 조각(CSS @font-face).
   OPTX.make(장면, 클래스) → 그릴 준비가 된 canvas. 붙이는 순간부터 돌고, 떼면 멈춘다. 크기는 예전 APNG(1280×720)와 같은 클래스 그대로. */
const OPTX = (()=>{
  const W = 1280, H = 720, REVEAL = 420, BLUR0 = 11, MAXW = 1920;
  const SERIF = ["OpTxSerif", 800, 46, 4.1, 0.5];            // [글꼴, 굵기, 크기(1280 기준), 자간, 굵게 덧칠(px)]
  const SANS = ["OpTxSans", 400, 46, 2.7, 0.55];
  const SERIF_EN = ["OpTxSerifEn", 800, 46, 1, 0.45];      // 영어판 (1010) — EB Garamond ExtraBold · 고운돋움의 라틴 글자
  const SANS_EN = ["OpTxSans", 400, 46, 1.2, 0.55];
  const LOOK = {
    cream: {fill:"rgb(245,240,230)", rgb:[245,240,230], glow:"rgba(255,248,236,0.55)", glowBlur:6, halo:"rgba(105,125,190,0.42)", haloBlur:22},
    red:   {fill:"rgb(255,0,0)", rgb:[255,0,0], glow:"rgba(205,10,20,0.62)", glowBlur:8, halo:"rgba(100,115,190,0.38)", haloBlur:22},
    ink:   {fill:"rgb(0,0,0)", rgb:[0,0,0], glow:"rgba(18,24,36,0.6)", glowBlur:7, halo:"rgba(45,60,95,0.58)", haloBlur:22},
    dad:   {fill:"rgb(243,238,228)", rgb:[243,238,228], glow:"rgba(255,255,255,0.45)", glowBlur:6, halo:"rgba(150,150,150,0.42)", haloBlur:20},
    metal: {grad:[[0,"#f8f9fa"],[0.52,"#d8dfe7"],[1,"#919dab"]], rgb:[215,222,230], outline:"#27303b", olw:3, join:"miter", shadow:"rgba(30,44,66,0.62)", shadowBlur:9, shadowY:6},
    metalSub: {grad:[[0,"#eef0f3"],[1,"#9aa3ae"]], rgb:[200,206,214], outline:"#3a4450", olw:0.9, join:"miter", shadow:"rgba(30,44,66,0.45)", shadowBlur:4, shadowY:2}
  };
  const STRETCH = {OpTxSerif: {"—": [1.17, 0.72]}};     // 예전 APNG 의 줄표(—)는 글꼴보다 17% 길고 조금 얇았다
  /* '아, 이건 위험...' 이 꺼질 듯 깜빡이는 장 — 3.70초부터 50ms 마다. B 밝음(청록 잔상) · D 어두움 · 숫자는 밝기(%) · s 는 밀린 띠 */
  const MAL_DANGER = "B100 B100 B100 B100 B100 B100 B100 B100 B100 D23 B100 D23s B100s B100 B100s B100s B100 B100 B100s D23 B100 B100s B100s B100 D23 B99 D21 B99 D21 B99s D21 D21 B98 D20s B98s D19 B97s B97s B96s B96s B95s D16 D16s D16s D16s D14 D14 D14 D12s D12 B72s D10 D9 D7 D7 D5 D4 D23s D16s";
  /* 장면 — st: 연. t 글 · y 줄 가운데 높이 · ln 줄마다 [첫 글자, 끝 글자] 나오는 때(그 사이는 글자 무게대로) · at 글자마다 나오는 때(띄어쓰기 빼고)
     fade 연이 흐려지는 때 · out 글자마다 깜빡이다 꺼지는 때 · mal 꺼질 듯 깜빡이기 · cut 한 번에 꺼짐 · rule 제목 밑 가로줄 · tail 끝의 빈 시간 */
  const SC = {
    intro: {ms:29250, tail:300, look:"cream", font:SERIF, st:[
      {t:["왕국력 236년—", "마왕군의 총공세가 시작됐다."], y:[318, 402], ln:[[110, 760], [1710, 2810]], fade:[4880, 5480]},
      {t:["오랜 세월 평화에 젖어 있던 왕국군은", "속수무책으로 무너졌고", "왕국은 유례없는 위기를 맞았다."], y:[274, 361, 448], ln:[[5760, 7360], [7960, 8760], [9360, 10660]], fade:[12720, 13300]},
      {t:["하지만 그런 왕국에게도 희망은 있었으니,", "역사상 전무후무하게 모든 직업을 마스터한", "인류 최강의 영웅, 당신이다."], y:[274, 361, 448], ln:[[13610, 15310], [16110, 17860], [18410, 19860]], fade:[21880, 22450]},
      {t:["당신은 동료들과 마왕을 저지하기 위해", "위험을 무릅쓰고 적진으로 향했다."], y:[318, 402], ln:[[22760, 24360], [24910, 26310]], fade:[28370, 28950]}]},
    rift: {ms:19300, tail:300, look:"red", font:SANS,
      glitch:[1700, 1750, 1800, 3400, 3450, 3500, 5150, 5200, 6800, 6850, 6900, 10250, 10300, 11900, 11950, 12000, 13600, 13650, 13700, 15300, 15350, 15400, 17000, 17050, 17100], st:[
      {t:["눈앞에서 시공이 휘몰아치며 흔들린다", "그리고 주변의 모든 걸 게걸스럽게 빨아들이기 시작한다."], y:[318, 400], ln:[[110, 1610], [2060, 4410]], out:[[6360, 6960], [7010, 7910]], flash:8500, end:8700},
      {t:["마왕은 웃으며 시공의 저편으로 빨려 들어간다...", "나와 함께 싸웠던 동료들도 손쓸 틈 없이 삼켜진다."], y:[318, 400], ln:[[9010, 11710], [12360, 14560]], out:[[16510, 17360], [17410, 18210]], flash:18800, end:19300}]},
    danger: {ms:7000, tail:350, look:"red", font:["OpTxSans", 400, 50, 2.1, 0.55], glitch:[1700, 1750, 1800, 3400, 3450, 3500], st:[
      {t:["아, 이건 위험..."], y:[359.5], at:[[110, 160, 460, 560, 710, 810, 810, 1260, 1610]], mal:{t0:3700, tab:MAL_DANGER}}]},
    date: {ms:4700, tail:300, look:"ink", font:SERIF, light:true, st:[
      {t:["—왕국력 230년, 가을"], y:[359.5], at:[[110, 460, 510, 610, 760, 860, 960, 1010, 1060, 1410, 1460]], fade:[3750, 4380]}]},
    typer: {ms:5950, tail:300, light:true, reveal:"pop", ghost:[108, 150, 177], ghost2:[196, 92, 132], glitch:[100, 1700, 1750, 1800, 3400, 3450, 3500], st:[
      {t:["용사 학원 키우기", "학원이 망했다"], y:[299.5, 423.5], fonts:[["OpTxSans", 400, 108, 32.5, 4], ["OpTxSans", 400, 34, 6.5, 0.3]], looks:["metal", "metalSub"],
       at:[[2700, 2250, 1850, 1400, 1000, 550, 100], [2750, 2700, 2650, 2600, 2550, 2500]], cut:[4750, 4800], rule:{y:381.5, x0:72, x1:1207, grow:[100, 950], shrink:[4800, 5650]}}]},
    dontsay: {ms:5050, tail:300, look:"dad", font:["OpTxSans", 400, 55, 4, 0.8], reveal:"fade", st:[
      {t:["그런 말 하지마."], y:[359.5], at:[[110, 310, 610, 910, 1110, 1310, 1560]], fade:[4050, 4750]}]},
    dream: {ms:5050, tail:300, look:"dad", font:["OpTxSans", 400, 55, 4, 0.8], reveal:"fade", st:[
      {t:["내 꿈은..."], y:[359.5], at:[[110, 560, 910, 1260, 1360, 1510]], fade:[4000, 4720]}]},
    hero: {ms:5100, tail:300, look:"dad", font:["OpTxSans", 400, 47, 5.1, 0.8], reveal:"fade", st:[
      {t:["자랑스러운 아빠 같은 영웅이 되고 싶은 거니까......"], y:[360],
       at:[[110, 160, 210, 310, 360, 460, 510, 610, 660, 760, 810, 860, 960, 1010, 1110, 1160, 1260, 1360, 1410, 1460, 1510, 1510, 1560, 1560, 1560]], fade:[4080, 4790]}]},
    winter: {ms:7400, tail:300, look:"cream", font:SERIF, st:[
      {t:["—왕국력 230년, 겨울", "아버지가 돌아가셨다."], y:[315.5, 403.5],
       at:[[110, 460, 510, 610, 760, 860, 960, 1010, 1060, 1410, 1460], [3360, 3460, 3510, 3610, 3760, 3860, 3960, 4010, 4110, 4160]], fade:[6470, 7100]}]}
  };
  /* 영어판 (1010) — 장면 · 연 · 효과 · 때는 SC 그대로 두고 글 · 줄 · 글꼴만 바꾼다. at 는 조각마다 고르게 나눈 값
     (타자기 제목은 소리 OP_TYPE_AT 와 맞게 오른쪽부터 음절 조각 일곱 · 부제 여섯) */
  const SC_EN = {
    intro: {ms:29250, tail:300, look:"cream", font:SERIF_EN, st:[
      {t:["Kingdom Year 236—", "The Demon Army began its all-out assault."], y:[318, 402], ln:[[110, 760], [1710, 2810]], fade:[4880, 5480]},
      {t:["The royal army, long steeped in peace,", "crumbled helplessly,", "and the kingdom faced an unprecedented crisis."], y:[274, 361, 448], ln:[[5760, 7360], [7960, 8760], [9360, 10660]], fade:[12720, 13300]},
      {t:["But even this kingdom had one hope:", "the first and only in history to master every class,", "humanity’s mightiest hero—you."], y:[274, 361, 448], ln:[[13610, 15310], [16110, 17860], [18410, 19860]], fade:[21880, 22450]},
      {t:["To stop the Demon King, you and your companions", "braved the danger and marched into enemy territory."], y:[318, 402], ln:[[22760, 24360], [24910, 26310]], fade:[28370, 28950]}]},
    rift: {ms:19300, tail:300, look:"red", font:SANS_EN,
      glitch:[1700, 1750, 1800, 3400, 3450, 3500, 5150, 5200, 6800, 6850, 6900, 10250, 10300, 11900, 11950, 12000, 13600, 13650, 13700, 15300, 15350, 15400, 17000, 17050, 17100], st:[
      {t:["Before my eyes, space and time swirl and shudder,", "then begin greedily devouring everything around them."], y:[318, 400], ln:[[110, 1610], [2060, 4410]], out:[[6360, 6960], [7010, 7910]], flash:8500, end:8700},
      {t:["Laughing, the Demon King is pulled into the rift...", "and my companions are swallowed before I can move."], y:[318, 400], ln:[[9010, 11710], [12360, 14560]], out:[[16510, 17360], [17410, 18210]], flash:18800, end:19300}]},
    danger: {ms:7000, tail:350, look:"red", font:["OpTxSans", 400, 50, 1.2, 0.55], glitch:[1700, 1750, 1800, 3400, 3450, 3500], st:[
      {t:["Ah, this is dangerous..."], y:[359.5], at:[[110, 135, 160, 460, 480, 500, 520, 560, 590, 710, 722, 734, 746, 758, 770, 782, 794, 806, 810, 1260, 1610]], mal:{t0:3700, tab:MAL_DANGER}}]},
    date: {ms:4700, tail:300, look:"ink", font:SERIF_EN, light:true, st:[
      {t:["—Kingdom Year 230, Fall"], y:[359.5], at:[[110, 460, 485, 510, 535, 560, 585, 610, 660, 685, 710, 735, 760, 860, 960, 1060, 1410, 1440, 1470, 1500]], fade:[3750, 4380]}]},
    typer: {ms:5950, tail:300, light:true, reveal:"pop", ghost:[108, 150, 177], ghost2:[196, 92, 132], glitch:[100, 1700, 1750, 1800, 3400, 3450, 3500], st:[
      {t:["My Hero’s Academy", "The Academy Went Under"], y:[299.5, 423.5], fonts:[["OpTxSans", 400, 100, 10, 4], ["OpTxSans", 400, 34, 3, 0.3]], looks:["metal", "metalSub"],
       at:[[2700, 2700, 2250, 2250, 1850, 1850, 1850, 1850, 1400, 1000, 1000, 550, 550, 100, 100], [2750, 2750, 2750, 2700, 2700, 2700, 2650, 2650, 2650, 2650, 2600, 2600, 2600, 2600, 2550, 2550, 2500, 2500, 2500]], cut:[4750, 4800], rule:{y:381.5, x0:72, x1:1207, grow:[100, 950], shrink:[4800, 5650]}}]},
    dontsay: {ms:5050, tail:300, look:"dad", font:["OpTxSans", 400, 55, 1.6, 0.8], reveal:"fade", st:[
      {t:["Don’t say that."], y:[359.5], at:[[110, 160, 210, 260, 310, 610, 660, 710, 910, 1043, 1177, 1310, 1560]], fade:[4050, 4750]}]},
    dream: {ms:5050, tail:300, look:"dad", font:["OpTxSans", 400, 55, 1.6, 0.8], reveal:"fade", st:[
      {t:["My dream is..."], y:[359.5], at:[[110, 160, 560, 590, 620, 650, 680, 910, 960, 1260, 1360, 1510]], fade:[4000, 4720]}]},
    hero: {ms:5100, tail:300, look:"dad", font:["OpTxSans", 400, 46, 1.4, 0.8], reveal:"fade", st:[
      {t:["to be a hero just like the dad I’m so proud of..."], y:[360],
       at:[[110, 149, 188, 227, 266, 306, 345, 384, 423, 462, 501, 540, 579, 619, 658, 697, 736, 775, 814, 853, 892, 931, 971, 1010, 1049, 1088, 1127, 1166, 1205, 1244, 1284, 1323, 1362, 1401, 1440, 1510, 1560, 1560]], fade:[4080, 4790]}]},
    winter: {ms:7400, tail:300, look:"cream", font:SERIF_EN, st:[
      {t:["—Kingdom Year 230, Winter", "My father passed away."], y:[315.5, 403.5],
       at:[[110, 460, 485, 510, 535, 560, 585, 610, 660, 685, 710, 735, 760, 860, 960, 1060, 1410, 1435, 1460, 1485, 1510, 1535], [3360, 3400, 3460, 3496, 3532, 3568, 3604, 3640, 3760, 3796, 3832, 3868, 3904, 3940, 3990, 4030, 4070, 4110, 4160]], fade:[6470, 7100]}]}
  };
  const SCX = (typeof I18N !== "undefined" && I18N.lang === "en") ? SC_EN : SC;
  const meas = document.createElement("canvas").getContext("2d");
  const FILTER_OK = (()=>{ try{ const c = document.createElement("canvas").getContext("2d"); if(!("filter" in c)) return false; c.filter = "blur(2px)"; return c.filter === "blur(2px)"; }catch(e){ return false; } })();
  const isSpace = c=> c === " " || c === "　";
  const hash = (a, b)=>{ let h = (Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  const rng = seed=>{ let s = seed >>> 0 || 1; return ()=>{ s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; }; };
  const fontStr = (f, px)=> `${f[1]} ${px}px ${f[0]}`;
  const dpr = ()=> Math.min(window.devicePixelRatio || 1, 2);
  const parseMal = str=> str.trim().split(/\s+/).map(k=> ({b:k[0] === "B", a:parseInt(k.slice(1), 10) / 100, s:k.endsWith("s")}));
  /* 글자 사이 간격의 무게 — 보통 1 · 띄어쓰기 건너 1.9 · 쉼표 뒤 띄어쓰기 3.6 · 줄표 뒤 4.2 · 문장부호 0.6 · 말줄임 점 4.4 */
  function weights(chars){
    const w = []; let prev = null, gap = false;
    for(const c of chars){
      if(isSpace(c)){ w.push(null); gap = true; continue; }
      let k;
      if(prev === null) k = 0;
      else if(c === "." && prev === ".") k = 4.4;
      else if(c === "…") k = prev === "…" ? 4.4 : 2.6;
      else if(gap && /[,，、]/.test(prev)) k = 3.6;
      else if(/[—―]/.test(prev) && !/[—―]/.test(c)) k = 4.2;
      else if(gap) k = 1.9;
      else if(/[.,!?:;—–、。，！？]/.test(c)) k = 0.6;
      else k = 1;
      w.push(k); prev = c; gap = false;
    }
    return w;
  }
  function spread(w, t0, t1){ let acc = 0; const cum = w.map(k=> k === null ? null : (acc += k)), tot = acc || 1; return cum.map(v=> v === null ? null : t0 + (t1 - t0) * v / tot); }
  function layout(s, f){
    meas.font = fontStr(f, f[2]);
    const st = STRETCH[f[0]] || {}, chars = Array.from(s), xs = [], sx = [];
    let pre = "", gaps = 0, extra = 0;
    for(let i = 0; i < chars.length; i++){
      if(i > 0 && !(chars[i - 1] === chars[i] && /[—―…]/.test(chars[i]))) gaps++;
      xs.push(meas.measureText(pre).width + gaps * f[3] + extra);
      const k = st[chars[i]] ? st[chars[i]][0] : 1; sx.push(st[chars[i]] || null);
      if(k !== 1){ const m = meas.measureText(chars[i]); extra += (m.actualBoundingBoxLeft + m.actualBoundingBoxRight) * (k - 1); }
      pre += chars[i];
    }
    const m = meas.measureText(s);
    return {chars, xs, sx, w:m.width + gaps * f[3] + extra, asc:m.actualBoundingBoxAscent, desc:m.actualBoundingBoxDescent};
  }
  /* 장면 하나를 글자 단위로 펼친다 */
  function build(sc){
    return sc.st.map((sp, si)=>{
      const lines = sp.t.map((s, li)=>{
        const f = ((sp.fonts && sp.fonts[li]) || sc.font).slice(), look = LOOK[(sp.looks && sp.looks[li]) || sc.look];
        const lay = layout(s, f), yc = sp.y[li], base = yc + (lay.asc - lay.desc) / 2, x0 = W / 2 - lay.w / 2;
        let starts;
        if(sp.at){ let k = 0; starts = lay.chars.map(c=> isSpace(c) ? null : sp.at[li][k++]); }
        else starts = spread(weights(lay.chars), sp.ln[li][0], sp.ln[li][1]);
        const dims = sp.out ? spread(lay.chars.map((c, i)=> isSpace(c) ? null : (i === 0 ? 0 : 1)), sp.out[li][0], sp.out[li][1]) : null;
        const glyphs = [];
        lay.chars.forEach((c, i)=>{
          if(isSpace(c)) return;
          const seed = si * 1000 + li * 100 + i, g = {c, x:x0 + lay.xs[i], sx:lay.sx[i], start:starts[i], seed, sp:null};
          if(dims){ g.dim = dims[i]; g.gone = dims[i] + 520 + 280 * hash(seed, 7); }
          glyphs.push(g);
        });
        return {yc, base, x0, w:lay.w, top:lay.asc, bot:lay.desc, font:f, look, reveal:sc.reveal || "blur", glyphs};
      });
      return {sp, lines, t0:Math.min(...lines.flatMap(l=> l.glyphs.map(g=> g.start))), mal:sp.mal ? parseMal(sp.mal.tab) : null};
    });
  }
  /* 글자 한 장 — 바깥 그늘(halo) · 가까운 빛(glow) · 본 글자 / 은빛 제목은 그라데이션 · 테두리 · 그림자 */
  function sprite(g, ln, scale){
    const f = ln.font, look = ln.look, px = f[2], font = fontStr(f, px), emb = f[4] || 0;
    const pad = 30, k = g.sx ? g.sx[0] : 1, ky = g.sx ? g.sx[1] : 1;
    meas.font = font;
    const m = meas.measureText(g.c);
    const asc = m.fontBoundingBoxAscent || px * 0.95, desc = m.fontBoundingBoxDescent || px * 0.3;
    const left = Math.max(0, m.actualBoundingBoxLeft || 0), right = Math.max(m.width, m.actualBoundingBoxRight || 0);
    const w = (left + right) * k + pad * 2, h = asc + desc + pad * 2;
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.ceil(w * scale)); c.height = Math.max(1, Math.ceil(h * scale));
    const x = c.getContext("2d");
    x.setTransform(scale, 0, 0, scale, 0, 0); x.translate(pad, 0); x.scale(k, 1);
    x.font = font; x.textBaseline = "alphabetic"; x.lineJoin = "round";
    const tx = left, ty = pad + asc;
    if(ky !== 1){ const cy = ty + ((m.actualBoundingBoxDescent || 0) - (m.actualBoundingBoxAscent || 0)) / 2; x.translate(0, cy); x.scale(1, ky); x.translate(0, -cy); }
    if(look.join){ x.lineJoin = look.join; x.miterLimit = 2.5; }
    if(look.grad){
      const grd = x.createLinearGradient(0, ty - ln.top, 0, ty + ln.bot);
      for(const [p, col] of look.grad) grd.addColorStop(p, col);
      x.shadowColor = look.shadow; x.shadowBlur = look.shadowBlur * scale; x.shadowOffsetY = look.shadowY * scale;
      x.strokeStyle = look.outline; x.fillStyle = look.outline; x.lineWidth = 2 * (emb + look.olw);
      x.strokeText(g.c, tx, ty); x.fillText(g.c, tx, ty);
      x.shadowColor = "transparent"; x.shadowBlur = 0; x.shadowOffsetY = 0;
      x.strokeStyle = grd; x.fillStyle = grd;
      if(emb > 0){ x.lineWidth = 2 * emb; x.strokeText(g.c, tx, ty); }
      x.fillText(g.c, tx, ty);
    } else {
      x.fillStyle = look.fill; x.strokeStyle = look.fill;
      x.shadowColor = look.halo; x.shadowBlur = look.haloBlur * scale; x.fillText(g.c, tx, ty);
      x.shadowColor = look.glow; x.shadowBlur = look.glowBlur * scale; x.fillText(g.c, tx, ty);
      x.shadowColor = "transparent"; x.shadowBlur = 0;
      if(emb > 0){ x.lineWidth = emb * 2; x.strokeText(g.c, tx, ty); }
      x.fillText(g.c, tx, ty);
    }
    return {c, ox:pad + left * k, oy:pad + asc, w, h};
  }
  function size(I, cssW){
    const cw = Math.max(320, Math.min(MAXW, Math.round(cssW * dpr()))), ch = Math.round(cw * H / W);
    if(I.cv.width === cw && I.S[0].lines[0].glyphs[0].sp) return;
    I.cv.width = I.lc.width = I.tc.width = cw; I.cv.height = I.lc.height = I.tc.height = ch;
    I.scale = cw / W;
    for(const st of I.S) for(const ln of st.lines) for(const g of ln.glyphs) g.sp = sprite(g, ln, I.scale);
  }
  function blit(I, g, ln, a, b){
    const L = I.L, sp = g.sp, dx = g.x - sp.ox, dy = ln.base - sp.oy, s = I.scale;
    if(b < 0.35){ L.globalAlpha = a; L.drawImage(sp.c, dx, dy, sp.w, sp.h); return; }
    if(FILTER_OK){ L.globalAlpha = a; L.filter = `blur(${(b * s).toFixed(2)}px)`; L.drawImage(sp.c, dx, dy, sp.w, sp.h); L.filter = "none"; return; }
    const OFF = 30000, rgb = ln.look.rgb;          // filter 가 없는 브라우저 — 그림자만 남겨 흐리게
    L.save(); L.setTransform(1, 0, 0, 1, 0, 0);
    L.globalAlpha = 1; L.shadowColor = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a})`; L.shadowBlur = b * 2 * s; L.shadowOffsetX = OFF;
    L.drawImage(sp.c, dx * s - OFF, dy * s, sp.c.width, sp.c.height);
    L.restore();
  }
  /* 제목 밑 가로줄 — 왼쪽에서 그어지고, 글자가 꺼진 뒤 왼쪽부터 걷힌다 (합성 뒤 본 캔버스에 — 지지직이 묻지 않게) */
  function rule(I, r, t){
    if(!r || t < r.grow[0]) return;
    const span = r.x1 - r.x0, pg = Math.min(1, (t - r.grow[0]) / (r.grow[1] - r.grow[0]));
    const x1 = r.x0 + span * (1 - Math.pow(1 - pg, 2.8));
    const x0 = t >= r.shrink[0] ? r.x0 + span * Math.pow(Math.min(1, (t - r.shrink[0]) / (r.shrink[1] - r.shrink[0])), 2.65) : r.x0;
    if(x1 - x0 < 0.5) return;
    const M = I.M; M.setTransform(I.scale, 0, 0, I.scale, 0, 0); M.globalAlpha = 1; M.fillStyle = "rgb(252,253,254)"; M.fillRect(x0, r.y - 0.9, x1 - x0, 1.8); M.setTransform(1, 0, 0, 1, 0, 0);
  }
  function draw(I, t){
    const {cv, L, M, sc} = I, cw = cv.width, ch = cv.height;
    L.setTransform(1, 0, 0, 1, 0, 0); L.globalAlpha = 1; L.clearRect(0, 0, cw, ch);
    L.setTransform(I.scale, 0, 0, I.scale, 0, 0);
    const bands = [], tick = Math.floor(t / 50); let mal = null;
    for(const st of I.S){
      const sp = st.sp;
      if(t < st.t0) continue;
      let mul = 1;
      if(sp.fade){ if(t >= sp.fade[1]) continue; if(t > sp.fade[0]) mul = 1 - Math.pow((t - sp.fade[0]) / (sp.fade[1] - sp.fade[0]), 2.2); }
      if(sp.cut){ if(t >= sp.cut[1]) continue; if(t > sp.cut[0]) mul *= 1 - (t - sp.cut[0]) / (sp.cut[1] - sp.cut[0]); }
      if(sp.end && t >= sp.end) continue;
      if(st.mal && t >= sp.mal.t0){ const k = Math.floor((t - sp.mal.t0) / 50); if(k >= st.mal.length) continue; mal = st.mal[k]; mul *= mal.a; }
      const flash = sp.flash && t >= sp.flash && t < sp.flash + 50;
      for(const ln of st.lines){
        let any = false, vx0 = 1e9, vx1 = -1e9;
        for(const g of ln.glyphs){
          const tau = t - g.start; let a, b = 0;
          if(ln.reveal === "pop"){ if(tau < 0) continue; a = 1; }
          else { if(tau <= 0) continue; const p = Math.min(1, tau / REVEAL), q = (1 - p) * (1 - p); a = 1 - q; if(ln.reveal === "blur") b = BLUR0 * q; }
          if(g.dim != null && t >= g.dim){
            if(t >= g.gone) continue;
            const k = (t - g.dim) / (g.gone - g.dim);
            a *= Math.max(0, 1 - 1.4 * (t - g.dim) / 1000);
            if(t - g.dim > 120 && hash(g.seed, tick) < 0.12 + 0.6 * Math.pow(k, 1.6)) a = 0.02;
            if(flash) a = Math.min(1, a * 2.1);
          }
          a *= mul;
          if(a <= 0.004) continue;
          if(mal && !mal.b) b = Math.max(b, 1.6);
          blit(I, g, ln, a, b); any = true;
          vx0 = Math.min(vx0, g.x - 2); vx1 = Math.max(vx1, g.x + g.sp.w - 58);
        }
        if(any){ const hh = (ln.top + ln.bot) / 2 + 2; bands.push({x0:vx0, x1:vx1, y0:ln.yc - hh, y1:ln.yc + hh}); }
      }
    }
    L.globalAlpha = 1;
    M.setTransform(1, 0, 0, 1, 0, 0); M.globalAlpha = 1; M.clearRect(0, 0, cw, ch);
    const gt = tick * 50, gl = I.glitch;
    if(gl.has(gt) && bands.length){
      const idx = (gl.has(gt - 50) ? 1 : 0) + (gl.has(gt - 100) ? 1 : 0), R = rng(gt * 2654435761);
      glitch(I, R, bands, true, idx === 0 ? 1 + Math.floor(R() * 2) : 2 + Math.floor(R() * 3), idx > 0);
    } else if(mal && (mal.b || mal.s) && bands.length){
      const R = rng(gt * 2654435761);
      glitch(I, R, bands, mal.b, mal.s ? 2 + Math.floor(R() * 2) : 0, mal.s);
    } else M.drawImage(I.lc, 0, 0);
    for(const st of I.S) rule(I, st.sp.rule, t);
  }
  /* 지지직 — 청록 잔상(밝은 바탕의 제목은 반대쪽에 분홍도) · 가로로 밀린 띠 · 검은 줄 · 옆으로 번진 선 */
  function glitch(I, R, bands, ghost, n, smear){
    const {M, TN, sc} = I, s = I.scale, cw = I.cv.width, ch = I.cv.height, gc = sc.ghost || [95, 178, 218];
    const tint = col=>{ TN.globalCompositeOperation = "source-in"; TN.fillStyle = `rgb(${col[0]},${col[1]},${col[2]})`; TN.fillRect(0, 0, cw, ch); TN.globalCompositeOperation = "source-over"; };
    TN.setTransform(1, 0, 0, 1, 0, 0); TN.globalCompositeOperation = "source-over"; TN.clearRect(0, 0, cw, ch);
    TN.drawImage(I.lc, 0, 0); tint(gc);
    if(ghost){
      M.globalAlpha = 0.85; if(FILTER_OK) M.filter = `blur(${(2.6 * s).toFixed(2)}px)`;
      M.drawImage(I.tc, 3 * s, 2 * s); M.filter = "none"; M.globalAlpha = 1;
      if(sc.ghost2){
        tint(sc.ghost2);
        M.globalAlpha = 0.55; if(FILTER_OK) M.filter = `blur(${(2.2 * s).toFixed(2)}px)`;
        M.drawImage(I.tc, -3 * s, -1 * s); M.filter = "none"; M.globalAlpha = 1;
        tint(gc);
      }
    }
    M.drawImage(I.lc, 0, 0);
    for(let k = 0; k < n; k++){
      const b = bands[Math.floor(R() * bands.length)];
      const y = (b.y0 + R() * (b.y1 - b.y0)) * s, h = (2 + R() * 6) * s, dx = (R() < 0.5 ? -1 : 1) * (5 + R() * 20) * s;
      M.save(); M.beginPath(); M.rect(0, y, cw, h); M.clip(); M.clearRect(0, y, cw, h);
      if(ghost){ M.globalAlpha = 0.8; M.drawImage(I.tc, dx + 4 * s, 2 * s); M.globalAlpha = 1; }
      M.drawImage(I.lc, dx, 0);
      M.restore();
      M.fillStyle = sc.light ? "rgba(38,48,62,0.3)" : "rgba(0,0,0,0.9)";
      M.fillRect((b.x0 - 10) * s, R() < 0.5 ? y : y + h, (b.x1 - b.x0 + 20) * s, Math.max(1, 1.2 * s));
    }
    if(smear && !sc.light){
      const ns = 1 + Math.floor(R() * 2);
      for(let k = 0; k < ns; k++){
        const b = bands[Math.floor(R() * bands.length)];
        const y = (b.y0 + 6 + R() * Math.max(1, b.y1 - b.y0 - 12)) * s, len = (40 + R() * 110) * s, bw = (b.x1 - b.x0) * s;
        M.globalAlpha = 0.5; M.drawImage(I.lc, b.x0 * s, y, bw, 1.5 * s, b.x0 * s - len, y, bw + len, 1.5 * s); M.globalAlpha = 1;
      }
    }
  }
  /* 글꼴 — 오프닝을 시작할 때 미리 */
  let fontP = null;
  function fonts(){
    if(fontP) return fontP;
    const all = Object.values(SCX).flatMap(sc=> sc.st.flatMap(sp=> sp.t)).join("");
    const load = (document.fonts && document.fonts.load)
      ? Promise.all([SCX === SC_EN ? "800 46px OpTxSerifEn" : "800 46px OpTxSerif", "400 46px OpTxSans"].map(f=> document.fonts.load(f, all))).catch(()=>{})
      : Promise.resolve();
    fontP = Promise.race([load, new Promise(r=> setTimeout(r, 2500))]);
    return fontP;
  }
  /* 예전 APNG 와 같은 클래스의 화면 폭 — 붙이기 전에 미리 그 크기로 글자를 굽는다 */
  function guessW(cls){
    const vw = innerWidth, vh = innerHeight;
    return /op-rift|op-date/.test(cls || "") ? Math.min(vw, 1.78 * vh, 1600) : Math.min(1.1835 * vw, 3.18 * vh, 1600);
  }
  function free(I){
    cancelAnimationFrame(I.raf); I.raf = 0; I.done = true;
    for(const st of I.S) for(const ln of st.lines) for(const g of ln.glyphs) g.sp = null;
    I.lc.width = I.lc.height = I.tc.width = I.tc.height = 0;
  }
  function make(key, cls){
    const sc = SCX[key];
    if(!sc) return Promise.resolve(null);
    return fonts().then(()=>{
      const cv = document.createElement("canvas");
      cv.width = W; cv.height = H; cv.setAttribute("aria-hidden", "true"); cv.draggable = false;
      if(cls) cv.className = cls;
      const I = {sc, cv, M:cv.getContext("2d"), lc:document.createElement("canvas"), tc:document.createElement("canvas"), scale:1, t0:0, on:false, made:performance.now(), raf:0, frozen:null,
        glitch:new Set(sc.glitch || []), S:build(sc)};
      I.L = I.lc.getContext("2d"); I.TN = I.tc.getContext("2d");
      size(I, guessW(cls));
      const step = now=>{
        if(I.done) return;
        if(!cv.isConnected){
          if(I.on || now - I.made > 10000){ free(I); return; }      // 붙였다 뗐거나, 끝내 붙지 않았으면 멈춘다
          I.raf = requestAnimationFrame(step); return;
        }
        if(!I.on){ I.on = true; I.t0 = now; }
        const t = I.frozen != null ? I.frozen : now - I.t0;
        const cssW = cv.clientWidth;
        if(cssW && Math.abs(Math.min(MAXW, Math.round(cssW * dpr())) - cv.width) > 24) size(I, cssW);   // 창 크기가 바뀌었다
        draw(I, Math.min(t, sc.ms));
        I.raf = requestAnimationFrame(step);
      };
      I.raf = requestAnimationFrame(step);
      cv._optx = I;
      return cv;
    });
  }
  return {make, prep:fonts, ms:k=> SCX[k] && SCX[k].ms, tail:k=> SCX[k] && SCX[k].tail,
    seek:(cv, t)=>{ const I = cv && cv._optx; if(!I || I.done) return false; I.frozen = t; if(cv.isConnected && cv.clientWidth) size(I, cv.clientWidth); draw(I, Math.min(t, I.sc.ms)); return true; }};   // 시험용 — 특정 때에 멈춰 그리기
})();
