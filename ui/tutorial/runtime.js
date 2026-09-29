/* Responsive tutorial artwork: text stays live; examples use current game data.
   Read-only: never consumes RNG or changes students/cards. */
function tutGuideData(k){
  const chain=Math.round(CHAIN_STEP*100), max=Math.round(CHAIN_STEP*CHAIN_MAX*100);
  const bonus=Math.round((RIVAL_FOCUS_MUL-1)*100);
  const data={
    1:{title:"월요일부터, 한 주를 채워요",tag:"진행 · 주간 스케줄",job:"timemage",lead:"일과 카드를 다섯 요일에 배치한 뒤 한 주를 진행하세요.",visual:"schedule",steps:[["카드를 눌러 배치", "폰에서는 카드를 누르면 첫 빈 요일에 들어갑니다. 원하는 요일로 끌어 놓아도 됩니다."],["컨디션과 비용 확인", "다섯 칸을 채우고 진행 버튼에 표시된 비용을 확인하세요. 놓은 카드를 누르면 다시 뺄 수 있어요."]],tip:`같은 색이 이어지면 +${chain}%씩, 최대 +${max}%. 원정 카드는 체인이 이어지지 않아요.`},
    2:{title:"오후에는 무엇을 할까요?",tag:"진행 · 개인 행동",job:"priest",lead:"개인 행동은 임의·훈련·휴식·의뢰 중에서 고릅니다.",visual:"actions",steps:[["훈련은 약점을 보완해요", "그날 가장 약한 멘탈리티를 집중 훈련합니다. 진행 화면이나 학생 화면에서 개인 행동을 바꿀 수 있어요."],["지쳤다면 휴식", "휴식으로 지정한 학생은 학원 스케줄에 참여하지 않고 쉽니다. 의뢰는 열린 뒤에 선택할 수 있고, 여름에는 할 수 없어요."]],tip:"컨디션이 낮아질수록 효율이 떨어집니다. 진행 전에 학생의 컨디션을 살펴보세요."},
    3:{title:"여섯 능력이 용사를 만들어요",tag:"학생 · 멘탈리티",job:"paladin",lead:"훈련으로 키운 멘탈리티는 전투와 성장에 영향을 줍니다.",visual:"mental",steps:[["학생에게 부족한 능력 확인", "학생 화면에서 멘탈리티를 보고 훈련을 계획하세요. 개인 행동을 훈련으로 두면 약점을 보완합니다."]],tip:"잠재력은 입학 등급으로 정해지는 성장 폭과 한계입니다. 여섯 훈련 능력과 구분해 주세요."},
    4:{title:"가을 대회를 향해 한 걸음씩",tag:"대회 · 장기 목표",job:"sword",lead:"학생들을 키우고 팀을 갖춰 학원제 본선 우승에 도전하세요.",visual:"tournament",steps:[["팀 편성부터 준비", "출전 학생과 진형을 확인하고, 컨디션과 유물을 챙겨 주세요."],["대회 성적으로 다음 무대에", "시내 대회부터 차근차근 도전합니다. 다음 대회 초대 조건은 게임의 안내에서 확인하세요."]],tip:"실적뿐 아니라 자금도 관리해야 합니다. 유지비와 빚을 함께 챙기세요."},
    5:{title:"라이벌과 함께 훈련해요",tag:"학생 · 라이벌",job:"timemage",lead:"서로 의식하는 두 학생은 함께 훈련하며 더 빠르게 성장합니다.",visual:"rival",steps:[["두 학생 모두 ‘훈련’으로", "개인 행동에서 라이벌 두 명을 모두 훈련으로 지정하세요. 두 사람이 함께 보완할 약한 분야를 고릅니다."],["같은 분야에서 성장 보너스", `둘이 같은 분야를 개인 훈련하면 해당 멘탈리티 성장이 ${bonus}% 증가합니다.`]],tip:"한쪽이 휴식이나 의뢰를 하면 함께 훈련하는 조건이 달라집니다. 두 학생의 행동을 함께 확인하세요."},
    6:{title:"원정에서 얻고, 장착해요",tag:"원정 · 유물",job:"spellsword",lead:"원정 파견 카드를 쓰면 원정지와 팀을 골라 자동 전투를 진행합니다.",visual:"expedition",steps:[["원정지와 팀 선택", "난이도와 팀 상태를 보고 출발하세요. 결과로 건너뛰기를 눌러 전투 결과를 바로 볼 수도 있어요."],["얻은 유물은 장착까지", "원정 보상으로 얻은 유물은 유물 · 스킬 화면에서 확인하고 학생에게 장착하세요."]],tip:"원정에서는 자금·유물·진로 평가와 함께 업보도 얻습니다. 반복 파견 전에 학생의 상태를 확인하세요."},
    7:{title:"친선전, 상대와 날짜를 골라요",tag:"봄 · 친선전",job:"darkpriest",lead:"요청한 학원 중 대결할 상대를 고르고 봄 하반기 일정에 배치합니다.",visual:"friendly",steps:[["상대와 명성 변화 확인", "상대 전력과 승패에 따른 명성 변화를 살펴보고 요청을 수락하세요."],["빈 일정에 배치하고 회신", "학원을 고른 뒤 날짜에 놓습니다. 끌어서 배치하거나 눌러서 고를 수 있어요."]],tip:"모든 요청을 받을 필요는 없습니다. 일정을 비워 두거나 요청을 거절해도 괜찮아요."},
    8:{title:"전투 전, 학생들에게 한마디",tag:"전투 준비 · 라커룸",job:"darkpriest",lead:"우리 팀과 상대의 전력, 학생들의 성격을 보고 말을 고릅니다.",visual:"speech",steps:[["한마디만 선택", "상황에 맞는 말을 고르면 학생의 기분과 신뢰에 도움이 됩니다."],["모두에게 같은 반응은 아니에요", "동기부여는 특히 성격을 살펴보세요. 맞지 않는 말은 기분을 떨어뜨릴 수도 있습니다."]],tip:"예시 수치가 항상 보장되는 보상은 아닙니다. 현재 학생들의 반응을 확인하세요."},
    9:{title:"졸업 뒤에도, 함께하는 리그",tag:"졸업생 리그 · 리그 등록",job:"paladin",lead:"졸업생이 생기면 더 넓은 무대에서 다른 학원과 모의 대전을 펼칠 수 있어요.",visual:"league",steps:[["졸업생으로 팀 구성", "리그 등록에서 출전할 졸업생과 진형을 확인하고 등록합니다."],["리그와 SP 상점 이용", "리그를 진행하며 SP를 얻고 SP 상점에서 사용하세요. 폰에서는 더보기 메뉴에서 찾을 수 있어요."]],tip:"리그는 온라인 기능입니다. 등록·시즌 정산 조건과 결과는 해당 화면에서 확인하세요."},
    10:{title:"부지를 넓히고 시설을 들여요",tag:"시설 · 상점 → 학원 증축",job:"enchanter",lead:"명성에 따른 인가와 학원 증축은 별개의 단계입니다.",visual:"expand",steps:[["첫 증축은 시내 대회 참가 뒤", "현재 규칙에서는 첫 시내 대회를 치른 뒤 시설 · 상점과 첫 증축이 열립니다."],["이후에는 인가와 자금 확인", "증축 단계마다 필요한 학원 등급과 비용이 다릅니다. 조건을 채우고 증축하면 추가 시설·물품이 열려요."]],tip:"인가를 받았다고 모든 시설이 바로 열리지는 않습니다. 각 시설에 표시된 증축 조건을 확인하세요."},
    11:{title:"3학년의 겨울은 진로 준비",tag:"겨울 · 졸업 준비",job:"forcemage",lead:"3학년은 겨울 동안 졸업 이후의 진로를 준비합니다.",visual:"winter",steps:[["겨울 스케줄에서 빠져요", "3학년 학생들이 훈련에 보이지 않아도 오류가 아닙니다. 남은 재학생 중심으로 일정을 준비하세요."],["겨울이 끝나면 졸업식", "그동안 쌓아 온 성장과 기록으로 진로 발표와 졸업을 맞이합니다."]],tip:"학생들의 마지막 가을을 미리 준비해 주세요. 겨울에는 신입생을 맞을 다음 해도 계획할 수 있어요."},
    12:{title:"카드의 작은 표식을 확인해요",tag:"진행 · 카드 표식",job:"timemage",lead:"같은 훈련 카드라도 표식에 따라 사용하는 날의 효과가 달라집니다.",visual:"marks",steps:[["사용하는 날에 적용", "표식은 카드를 들고 있는 동안이 아니라, 해당 요일에 사용했을 때 적용됩니다."]],tip:"카드 왼쪽 위 남은 기간도 확인하세요. 이번 주까지인 카드는 사용하지 않으면 주가 끝날 때 사라집니다."}
  };return data[k]||data[1];
}
function tutSampleCard(t="basic",mark){
  const c={t,u:-100,w:S.weekSeq||0};if(mark)c.m=mark;
  return cardHtml(c).replace('draggable="true"','draggable="false"').replace(/data-card="[^"]*"/g,'data-tutorial-example="card"');
}
function tutGuideVisual(kind){
  const row=(title,body,icon="✦")=>`<div class="tg-row"><span class="tg-symbol" aria-hidden="true">${icon}</span><div><strong>${esc(title)}</strong><p>${esc(body)}</p></div></div>`;
  const route=items=>`<ol class="tg-route">${items.map((x,i)=>`<li><span>${i+1}</span><div><strong>${esc(x[0])}</strong><p>${esc(x[1])}</p></div></li>`).join("")}</ol>`;
  switch(kind){
    case "schedule":return `<div class="tg-caption">배치 예시 · 카드를 누르면 첫 빈칸으로</div><div class="tg-card-demo">${tutSampleCard()}<span class="tg-arrow" aria-hidden="true">→</span><div class="tg-destination"><b>월요일</b><span>기초 체력</span><small>첫 번째 일과</small></div></div><div class="tg-week">${DAY_N.map((d,i)=>`<span>${d}<b>${i?`+${Math.round(Math.min(i,CHAIN_MAX)*CHAIN_STEP*100)}%`:"시작"}</b></span>`).join("")}</div><p class="tg-caption">같은 색을 다섯 날 이어 놓은 예시</p>`;
    case "actions":return ACT_KEYS.map(k=>row(ACT[k].n,ACT[k].d,{auto:"?",train:"↑",rest:"☾",job:"G"}[k])).join("");
    case "mental":return MENTAL.filter(x=>!x.fixed).map((x,i)=>row(x.n,x.d,String(i+1).padStart(2,"0"))).join("");
    case "tournament":return route([["시내 대회","첫 출전과 실적"],["광역 대회","여러 팀의 준비"],["학원제 예선 · 본선","더 큰 무대에 도전"]]);
    case "rival":return `<div class="tg-pair">${faceHTML("sword","라이벌 학생 예시") }<span>↔</span>${faceHTML("paladin","라이벌 학생 예시")}</div><div class="tg-choice-pair"><span>학생 A · 훈련</span><span>학생 B · 훈련</span></div><div class="tg-big-number">+${Math.round((RIVAL_FOCUS_MUL-1)*100)}%<small>같은 분야의 개인 훈련 성장</small></div>`;
    case "expedition":return route([["원정 파견 카드","요일에 배치"],["원정지 · 팀 선택","난이도와 컨디션 확인"],["자동 전투 · 보상","결과와 획득 유물 확인"],["유물 · 스킬","학생에게 장착"]]);
    case "friendly":return route([["요청 학원 선택","전력과 명성 변화 확인"],["봄 하반기 일정 배치","빈 날짜에 놓기"],["회신","참가할 일정 확정"]]);
    case "speech":return Object.values(SPEECH_TYPE).map(x=>row(x.n,x.d,"“")).join("");
    case "league":return route([["졸업생","졸업한 학생 확인"],["리그 등록","출전 팀과 진형 선택"],["졸업생 리그","다른 학원과 대전"],["SP 상점","모은 SP 사용"]]);
    case "expand":return route([["시내 대회 참가","시설 · 상점 개방"],["학원 증축","필요 인가 · 비용 확인"],["시설 · 물품 해금","열린 시설을 구매·강화"]]);
    case "winter":return `<div class="tg-season"><span>가을</span><b>→</b><span>겨울</span><b>→</b><span>졸업</span></div>${row("3학년","진로 준비로 스케줄 불참","❄")}${row("남은 재학생","계속 훈련하고 다음 해 준비","↑")}`;
    case "marks":return `<div class="tg-card-demo tg-mark-card">${tutSampleCard("tact","dbl")}<div><strong>모서리 표식</strong><p>카드의 훈련 이름과 함께 확인해요.</p></div></div>`+Object.values(CARD_MARK).map(m=>row(m.n,m.d,m.i)).join("");
  }return "";
}
function tutGuideHTML(k){
  const d=tutGuideData(k);
  return `<article class="tg-guide" data-guide="${esc(String(k))}" aria-label="${esc(d.title)}"><header class="tg-head"><div><span class="tg-kicker">용사 학원 · 운영 안내 ${String(k).padStart(2,"0")}</span><h2>${esc(d.title)}</h2><p class="tg-location">${esc(d.tag)}</p></div><span class="tg-host">${faceHTML(d.job,"")}</span></header><p class="tg-lead">${esc(d.lead)}</p><div class="tg-columns"><section class="tg-visual" aria-label="기능 설명 그림">${tutGuideVisual(d.visual)}</section><section class="tg-instructions" aria-label="사용 방법">${d.steps.map((step,i)=>`<div class="tg-step"><span>${i+1}</span><div><h3>${esc(step[0])}</h3><p>${esc(step[1])}</p></div></div>`).join("")}<aside class="tg-tip"><b>기억해 주세요</b><p>${esc(d.tip)}</p></aside></section></div><footer class="tg-foot">마스터 노트의 튜토리얼 단추에서 다시 볼 수 있어요.</footer></article>`;
}
