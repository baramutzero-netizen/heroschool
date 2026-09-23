from pathlib import Path
from PIL import Image
import base64,io,re,json
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
im=Image.open(out/'book-source.png').convert('RGB');im.thumbnail((1800,1100));bio=io.BytesIO();im.save(bio,'WEBP',quality=88);(out/'book.webp').write_bytes(bio.getvalue());art='data:image/webp;base64,'+base64.b64encode(bio.getvalue()).decode()
p=root/'game.html';s=p.read_text(encoding='utf-8')
if 'function viewPlanClassic(){' not in s:s=s.replace('function viewPlan(){','function viewPlanClassic(){',1)
s=s.replace('const PREF = {bspeed: 280, reportSpeed: 2};','const PREF = {bspeed: 280, reportSpeed: 2, chronicleTest: false};')
anchor='if(j && [1,2,6].includes(j.reportSpeed)) PREF.reportSpeed = j.reportSpeed;'
if 'PREF.chronicleTest = j.chronicleTest' not in s:s=s.replace(anchor,anchor+'\n  if(j && typeof j.chronicleTest === "boolean") PREF.chronicleTest = j.chronicleTest;')
fonts='\n'.join("@font-face{font-family:'"+family+"';src:url(data:font/woff2;base64,"+base64.b64encode((out/'fonts'/filename).read_bytes()).decode()+") format('woff2');font-weight:400;font-display:swap;}" for family,filename in [('ChroniclePen','NanumPenScript.woff2'),('ChronicleBrush','NanumBrushScript.woff2')])
css='/* CHRONICLE_CSS_START */\n'+fonts+'\n'+(out/'style.css').read_text(encoding='utf-8')+'\n'+(out/'ornaments.css').read_text(encoding='utf-8')+'\n/* CHRONICLE_CSS_END */'
if '/* CHRONICLE_CSS_START */' in s:s=re.sub(r'/\* CHRONICLE_CSS_START \*/.*?/\* CHRONICLE_CSS_END \*/',lambda _:css,s,flags=re.S)
else:s=s.replace('</style>',css+'\n</style>',1)
assets={f.stem:'data:image/webp;base64,'+base64.b64encode(f.read_bytes()).decode() for f in (out/'ornaments').glob('*.webp')}
js='/* CHRONICLE_JS_START */\nconst CHRONICLE_BOOK="'+art+'";\n'+'const CHRONICLE_ART='+json.dumps(assets,separators=(',',':'))+';\n'+(out/'runtime.js').read_text(encoding='utf-8')+'\n/* CHRONICLE_JS_END */\n'
if '/* CHRONICLE_JS_START */' in s:s=re.sub(r'/\* CHRONICLE_JS_START \*/.*?/\* CHRONICLE_JS_END \*/\n',lambda _:js,s,flags=re.S)
else:s=s.replace('function viewPlanClassic(){',js+'function viewPlanClassic(){',1)
if 'id="chronicleToggle"' not in s:s=s.replace('function viewOpt(){\n  const a = optFxA();','function viewOpt(){\n  const a = optFxA();').replace('return errPanel() + xferPanel() + `<section class="panel">','return errPanel() + xferPanel() + `<section class="panel"><div class="optrow"><div class="optlab"><b>진행 페이지 테스트 모드</b><span>양피지 책으로 일정과 학생 집중 훈련을 기록합니다. 기본은 꺼짐이며 다른 페이지는 유지됩니다.</span></div><label><input type="checkbox" id="chronicleToggle" ${PREF.chronicleTest?"checked":""}> 사용</label></div></section><section class="panel">',1)
s=s.replace('  bindView();','  bindView();\n  bindChronicle();') if '  bindChronicle();' not in s else s
s=s.replace('const bw = $("#btnWeek"); if(bw) bw.onclick=()=> runWithReport();','const bw = $("#btnWeek"); if(bw) bw.onclick=()=> chronicleAdvance(bw);')
# Plan slots must not invoke team-selection rendering before the card click handler.
s=s.replace('v.querySelectorAll("[data-slot]").forEach(b=> b.onclick=()=>{\n    UI.slot', 'v.querySelectorAll("[data-slot]").forEach(b=> b.onclick=()=>{\n    if(UI.view==="plan") return;\n    UI.slot')
p.write_text(s,encoding='utf-8');print('Chronicle embedded')
