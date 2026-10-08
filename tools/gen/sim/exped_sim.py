"""원정 시뮬레이션 (1008) — 잡몹 배율(MOB_K) · 그뉵이용 배율을 다시 맞출 때 쓴다. 저장소 맨 위에서:

    python tools/gen/sim/exped_sim.py heroschool.html '[{"id":"d5","n":1000,"comp":"role","form":1,"lvAdd":2}]'
    python tools/gen/sim/exped_sim.py heroschool.html '[{"id":"d5","n":1000,"comp":"role","form":1,"lvAdd":2,"mobK":1.1}]'   # 배율을 바꿔 보기
    python tools/gen/sim/exped_sim.py heroschool.html '[{"id":"d5","n":1000,"duel":1,"kind":"boss","lvAdd":2}]'           # 한 판 승률
    python tools/gen/sim/exped_sim.py heroschool.html '[{"id":"d5","n":1000,"comp":"role","form":1,"lvAdd":2,"sk":"auto"}]'   # 학생 스킬을 임의 강화 방식으로

설정마다 결과 한 줄(JSON): full(완주 수) · reached(도달 비율 합) · exp · gold · relics · karma · cond(학생당 컨디션 소모) ·
fame · eval · wipe / retire / stam(전멸 · 리타이어 · 지구력 철수 수) · secWin / secTry(구간별 승 / 시도) — n 으로 나누면 한 번 평균.
1008 에 3구간으로 바꿀 때: 바꾸기 전 빌드와 뒤 빌드를 같은 설정(comp role · form · lvAdd 0/2/4/6 · n 1500)으로 돌려
완주율이 같아지는 mobK 를 골랐다. 스킬 등급표(1008, apply_skgrade)로 마물 스킬이 세졌을 때는 sk "auto"(실제 학생처럼 강화)로
마물 스킬을 바꾸기 전 · 뒤를 견줘 성터 · 종탑 · 균열 · 무덤 배율을 조금씩 낮췄다. 필요한 것: pip install playwright · playwright install chromium
Firebase 주소는 막는다 (게임 서버에 아무것도 쓰지 않는다). 그림 · 소리도 받지 않는다."""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

SIM = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exped_sim.js"), encoding="utf-8").read()


async def main():
    page, cfgs = os.path.abspath(sys.argv[1]), json.loads(sys.argv[2])
    async with async_playwright() as p:
        b = await p.chromium.launch()
        c = await b.new_context(viewport={"width": 1280, "height": 800})
        await c.route("**/*firebasedatabase.app/**", lambda r: r.abort())
        await c.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        await c.route("**/*.{png,webp,jpg,gif,mp3,ogg}", lambda r: r.abort())
        pg = await c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.goto("file:///" + page.replace("\\", "/").lstrip("/"))
        for _ in range(300):
            if await pg.evaluate("() => typeof S !== 'undefined' && !!S && !!S.students"): break
            await pg.wait_for_timeout(100)
        await pg.evaluate("() => { " + SIM + "\n return 0; }")
        print(json.dumps({"info": await pg.evaluate("() => __simSetup()")}, ensure_ascii=False), flush=True)
        for cfg in cfgs:
            r = await pg.evaluate("(c) => c.duel ? __duel(c) : __sim(c)", cfg)
            r["cfg"] = cfg
            print(json.dumps(r, ensure_ascii=False), flush=True)
        if errs: print(json.dumps({"errors": errs[:5]}, ensure_ascii=False), flush=True)
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
