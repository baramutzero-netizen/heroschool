"""영어판 준비 (1010) — extract_ko.cjs 가 뽑은 글에 갈래를 붙이고 분량을 요약한 뒤 CSV 로 쓴다.

    python3 tools/i18n/classify_ko.py ko.json ko_strings.csv

갈래는 '맨 위 선언 이름 · 가장 가까운 호출'로 정한다 (아래 표). 새 데이터 표가 생기면 이름을 알맞은 묶음에 더한다.
영어 단어 수는 한글 1자 ≈ 0.55단어로 어림한다 (게임 문장 몇 개를 옮겨 본 비율 0.5~0.7 의 가운데쯤).
"""
import collections, csv, json, re, sys

OPENING = {'OPTX', 'PROLOGUE', 'opLines()', 'opFatherLines()', 'opSay()', 'opFather()', 'openingPlay()', 'newScenarioStart()', 'showPrologue()'}
TUT = {'tutGuideData()', 'tutGuideVisual()', 'tutGuideHTML()', 'cardLegendHtml()', 'tutOnePage()', 'tutOverPage()', 'tutSchedBtn()', 'showTutorial()',
       'viewCodex()', 'codexJobs()', 'skGradeTable()', 'secretConds()', 'secretCondHtml()'}
NAMES = {'NAME_POOL', 'ACAD', 'EPI_TITLES', 'L5_NPC_ACAD', 'RELIC_ADJ', 'RELIC_NOUN', 'acadNames()', 'rivalAcademy()', 'EPI_CROWD', 'DEMON_NAME',
         'SPR_HUE_NAME', 'SPR_TONE_NAME', 'makeRivals()', 'makeBrothers()', 'SUR', 'GIV', 'MON'}
DIALOGUE = {'COUNSEL', 'TRUST_LINES_P', 'TRUST_LINES', 'CAREER_REASON', 'GREET_LINES', 'UNIQ_GREET', 'DEFY_LINES', 'DEFY_REPLY', 'DEFY_REACT', 'DEFY_ASK',
            'CSL_REACT', 'CSL_ENTER', 'CSL_DEFY_ENTER', 'SPEECH_MOTIVE', 'SPEECH_EXPECT', 'SPEECH_RELIEF', 'SPEECH_TYPE', 'TRUST_FAREWELL', 'CHAT_BAD',
            'BRO_SCENE', 'RIVAL_SCENE', 'RIVAL_INTRO', 'shopKeeperInfo()', 'TOWN_NPCS', 'lockerSpeak()', 'ENROLL_NOTE', 'answerCounsel()', 'answerDefy()',
            'cslwTalk()', 'cslwAsk()', 'cslwResult()'}
STORY = {'JOB_EV', 'EPI_DEEDS', 'VALENTINE_MSG', 'SPARKLER_MSG', 'GUILD_PAGES', 'CAMP_INSIGHT', 'TOWN_EV_RWD', 'TOWN_EV', 'PORTAL_LETTER', 'SHOP_OPEN_TEXT',
         'townEvBank()', 'townEvSeason()', 'townEvBanner()', 'townEvPage()', 'epiScene()'}
BATTLE = {'runBattle()', 'battleCallout()', 'openBattle()', 'battleStatusIcon()', 'fxAText()', 'targetLabel()', 'expedBattle()', 'demonBattle()', 'BATTLE', 'monLabel()'}
DEV_TOPS = {'fieldLabRender()', 'fieldLabBoot()', 'openAvatarLab()', 'AVATAR_LAB_HTML'}
LOGS = {'logE', 'dlog', 'toast'}
CAT_KO = {'dialogue': '대사 · 상담', 'ui': '화면 UI', 'data': '게임 데이터', 'story': '이야기 · 행사 이벤트', 'log': '일지 · 알림', 'tut': '안내 · 도감',
          'names': '이름 짓기', 'opening': '오프닝 · 프롤로그', 'battle': '전투 화면', 'dev': '개발용 (빌드에서 빠짐)', 'logic': '로직 (비교 · 정규식)'}
ORDER = list(CAT_KO)
KIND = {'str': '글', 'tpl': '문장 틀', 'html': 'HTML', 'attr': 'HTML 속성', 'css': 'CSS', 'regex': '정규식'}
WORDS_PER_SYLLABLE = 0.55


def cat(e):
    if e.get('dev') or e['top'] in DEV_TOPS: return 'dev'
    if e['role'] != 'text': return 'logic'
    t = e['top']
    if t in OPENING: return 'opening'
    if e['callee'] in LOGS: return 'log'
    if t in TUT or t.startswith('tut'): return 'tut'
    if t in NAMES: return 'names'
    if t in DIALOGUE: return 'dialogue'
    if t in STORY or t.endswith('Ceremony()'): return 'story'
    if t in BATTLE: return 'battle'
    if re.fullmatch(r'[A-Z][A-Z0-9_]+', t) or t == 'Object.assign(…)': return 'data'
    return 'ui'


def main(src, out_csv):
    d = json.load(open(src, encoding='utf-8')); E = d['entries']
    for e in E: e['cat'] = cat(e)
    S = collections.defaultdict(lambda: [0, 0, set()])
    for e in E:
        s = S[e['cat']]; s[0] += 1; s[1] += e['h']; s[2].add(e['text'])
    tot = sum(s[1] for k, s in S.items() if k not in ('dev', 'logic'))
    print(f"{'갈래':16s} {'곳':>6s} {'고유':>6s} {'한글':>8s} {'%':>4s} {'영어 단어':>9s}")
    for k in sorted(S, key=lambda k: -S[k][1]):
        n, h, u = S[k]
        share = f"{h / tot * 100:4.0f}" if k not in ('dev', 'logic') else '   -'
        print(f"{CAT_KO[k]:16s} {n:6d} {len(u):6d} {h:8d} {share} {round(h * WORDS_PER_SYLLABLE):9d}")
    tpl = [e for e in E if e['kind'] == 'tpl' and e['cat'] not in ('dev', 'logic')]
    part = sum(1 for e in tpl if any(re.search(r'\b(jo|iga|eunn|eulr|gwa|ro)\(', x) for x in (e['exprs'] or [])))
    counter = sum(1 for e in tpl if re.search(r'\{\d+\}(명|주|회|개|년|번|장|승|패|일|칸|팀|살|점|위|학년|구간|계절|주차|시즌)', e['text']))
    print(f"번역할 한글 {tot:,}자 · 영어 약 {round(tot * WORDS_PER_SYLLABLE):,}단어 · 문장 틀 {len(tpl)} (조사 함수 {part} · 숫자+단위 {counter}) · 주석 한글 {d['commentHangul']:,}자")
    rows = sorted(E, key=lambda e: (ORDER.index(e['cat']), e['line']))
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['번호', 'game.html 줄', '갈래', '종류', '위치', '경로', '한글 글자', '한국어', '자리표 {0}{1}… 에 들어가는 식'])
        for i, e in enumerate(rows, 1):
            top = 'ROSTERBK 블록 (학생 명부 책)' if e['top'].startswith('() => {') else e['top']
            w.writerow([i, e['line'], CAT_KO[e['cat']], KIND.get(e['kind'], e['kind']), top, e['path'], e['h'], e['text'], ' ¦ '.join(e['exprs'] or [])])
    print('CSV', out_csv, len(rows), '줄')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
