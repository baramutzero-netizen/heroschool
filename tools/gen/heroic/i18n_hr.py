"""스타일리시 전투 체크포인트 (1015) — 새 글의 영어 · 일본어 표 넣기 (tools/i18n/en · ja 의 battle.json · ui.json)

    python3 tools/gen/heroic/i18n_hr.py        # 저장소 맨 위에서 · 몇 번 돌려도 같다 (있는 키는 값만 갈아 끼운다)

대사(정신력 시험 — 기상 36 · 동료 반응 27 · 기절 18 · 기절 동료 반응 27)의 영어는 mockups/heroic-resolve/src/lines.json 그대로,
일본어는 여기 JA (ja/GUIDE.md — 성격별 말투 · 성별 없는 말 · 허세의 ‘ ’ 혼잣말 · 1인칭은 되도록 빼고 私).
"""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
I18N = os.path.join(ROOT, "tools", "i18n")
L = json.load(open(os.path.join(ROOT, "mockups", "heroic-resolve", "src", "lines.json"), encoding="utf-8"))
P9 = ["intro", "hot", "stone", "dilig", "tsun", "lively", "boast", "plain", "genius"]

JA_TYPES = {"will": "不屈の意志", "faith": "揺るがぬ信念", "clarity": "澄みわたる心", "courage": "湧き上がる勇気"}
JA_HERO = {
  "will": {"intro": "こ、怖くても…ここで引き下がったりしません…！", "hot": "この程度で消える炎じゃない！！もう一度いく！！",
           "stone": "…まだ立っている。ならば、続ける。", "dilig": "任された務めは…最後までやり遂げます！",
           "tsun": "ふん…この程度で倒れると思った？", "lively": "えへへ…まだ終わってないですよ～！",
           "boast": "‘くっくっ…英雄の真価は倒れてからだ’", "plain": "まだだ…！まだやれる！", "genius": "計算違いですね。私はまだ倒れませんよ。"},
  "faith": {"intro": "み、みんなを守ります…今度は、私が…！", "hot": "後ろには仲間がいる！！絶対にどかない！！",
            "stone": "守るものがある。だから、退かない。", "dilig": "皆を守るのが私の役目です。持ちこたえてみせます！",
            "tsun": "…勘違いしないで。あなたたちのために踏ん張ってるんじゃないから。", "lively": "みんなで笑って帰るんです！だから負けません！",
            "boast": "‘この私が倒れれば、誰がこの者たちを守るのだ’", "plain": "ここで踏ん張らなきゃ。踏ん張ってみせる。", "genius": "ここで持ちこたえるのが最善です。確信しています。"},
  "clarity": {"intro": "あ、あれ…不思議と…全部見えます…", "hot": "見える！！頭がすっきり晴れわたった！！",
              "stone": "…雑音が消えた。すべて見える。", "dilig": "落ち着いて…一つずつ。もう全部見えます。",
              "tsun": "…ふん。やっとまともに見えてきた。", "lively": "うわあ…世界がキラキラして見えます！",
              "boast": "‘くっくっ…この目には運命の糸がすべて見える’", "plain": "あれ？頭がすっきりした。もう見える。", "genius": "ああ、見えましたね。もう終わっていますよ。"},
  "courage": {"intro": "勇気…出してみます。あと一歩だけ…！", "hot": "体が軽い！！このまま最後まで突っ走る！！",
              "stone": "体が軽い。今、終わらせる。", "dilig": "力が湧いてきます…！もう少しだけ走ってみます！",
              "tsun": "べ、別に元気が出たからってわけじゃないから！", "lively": "うわあ、力がどんどん湧いてきます！いこういこう～！",
              "boast": "‘くっくっ…風さえもこの私には追いつけまい’", "plain": "よし、力が出てきた！もう一回いこう！", "genius": "体が軽いですね。さて、ついて来られますか？"},
}
JA_REACT = {
  "intro": ["{n}…よ、よかった…！", "わ、私も…がんばります…！", "……かっこいいです、{n}。"],
  "hot": ["そうだ、それだ{n}！！", "うおおっ、負けてられない！！", "燃えてきたあああ！！"],
  "stone": ["…流れが変わった。", "{n}、背中は任せろ。", "今だ。押し切る。"],
  "dilig": ["{n}、すごいです！最後まで一緒に戦います！", "みなさん、あと少しがんばりましょう！", "隙は私が埋めます！"],
  "tsun": ["…ふん、心配なんかしてないから。", "お、遅い…でも、よかった。", "{n}のくせに…かっこつけちゃって。"],
  "lively": ["わあ！{n}、最高！", "えへへ、今度はこっちの番だよ～！", "いい感じ～！いこういこう！"],
  "boast": ["‘くっくっ…さすがはこの私が認めた仲間だ’", "‘よかろう、この私も本気を見せてやろう’", "‘英雄の覚醒か…悪くない’"],
  "plain": ["{n}、大丈夫なんだね？よかった！", "私たちもがんばろう！", "よし、まだやれる！"],
  "genius": ["やっぱり、そうなると思っていました。", "{n}、いいですね。私が続きます。", "これで計算が合いますね。"],
}
JA_FAINT = {
  "intro": ["ご、ごめんなさい…もう…", "……すみません…"],
  "hot": ["くっ…ここまでか…！", "まだ…炎は…消えてないのに…"],
  "stone": ["…限界、か。", "…後は、頼む。"],
  "dilig": ["最後まで…やり遂げたかったのに…", "みなさん…申し訳ありません…"],
  "tsun": ["ふん…ちょ、ちょっと休むだけなんだから…", "み、見ないで…こんな姿…"],
  "lively": ["えへへ…ちょっとだけ…休みます…", "あれ…目の前が…ぐるぐる…"],
  "boast": ["‘くっ…今日のところは…このくらいにしておこう…’", "‘英雄にも…休息は…必要なもの…’"],
  "plain": ["ごめん…みんな、頼んだ…", "うっ…もう、もたない…"],
  "genius": ["…これは、予想外でしたね…", "…計算が…狂っ…"],
}
JA_REACT_FAINT = {
  "intro": ["{n}…！だ、大丈夫ですよね…？", "ど、どうしよう…わ、私が持ちこたえます…！", "{n}の分まで…わ、私もやってみます…！"],
  "hot": ["{n}！！その分まで戦ってみせる！！", "この借りは十倍にして返す！！", "ゆっくり休め、{n}！！すぐに終わらせる！！"],
  "stone": ["…{n}、休んでいろ。後は引き受ける。", "…空いた穴は埋める。", "揺らぐな。まだ終わっていない。"],
  "dilig": ["{n}！その分まで私がやり遂げます！", "みなさん落ち着いて！隊列を立て直しましょう！", "{n}、休んでいてください。必ず勝ちます！"],
  "tsun": ["ふん…だから無理するなって言ったのに。", "{n}の分までやってあげる…こ、今回だけだから。", "…心配なんかしてない。早く起きて。"],
  "lively": ["{n}～！起きたら一緒においしいもの食べよう！", "大丈夫、大丈夫！私たちがいるよ～！", "うわっ、{n}！ちょっと待っててね～！"],
  "boast": ["‘くっくっ…{n}の分まで、この私が背負おう’", "‘この私の仲間に手を出した報い、受けてもらおう’", "‘眠るがいい、{n}…目覚めた時には終わっているだろう’"],
  "plain": ["{n}！大丈夫？！", "まずい…でも、踏ん張らなきゃ！", "{n}の分までがんばろう！"],
  "genius": ["変数が増えましたね。計算し直します。", "{n}、休んでください。残りは私が埋め合わせます。", "…予想より早いですね。それでも勝算はあります。"],
}


def battle_rows(lang):
    rows = [("_HR_TYPES", "")]
    for t in L["types"]:
        rows.append((t["ko"], t["en"] if lang == "en" else JA_TYPES[t["k"]]))
    rows += [("_HR_TEST_TXT", ""), ("{0}의 정신력이 시험받고 있습니다…", "{0}'s spirit is being tested…" if lang == "en" else "{0}の精神力が試されています…"),
             ("_HR_FAINT_TXT", ""), ("{0}, 의식을 잃었다", "{0} lost consciousness" if lang == "en" else "{0}、意識を失った"),
             ("_HR_LINES", "")]
    for t in L["types"]:
        for p in P9:
            ko = L["hero"][t["k"]][p]["ko"]
            rows.append((ko, L["hero"][t["k"]][p]["en"] if lang == "en" else JA_HERO[t["k"]][p]))
    for tab, ja in (("react", JA_REACT), ("faint", JA_FAINT), ("reactFaint", JA_REACT_FAINT)):
        for p in P9:
            for i, x in enumerate(L[tab][p]):
                rows.append((x["ko"], x["en"] if lang == "en" else ja[p][i]))
    return rows


def ui_rows(lang):
    en = lang == "en"
    return [("_SKPICK_OPTS", ""), ("모든 학생", "All" if en else "すべての生徒"), ("자신의 학생만", "Mine only" if en else "自分の生徒のみ"),
            ("상대의 학생만", "Opponents only" if en else "相手の生徒のみ"), ("표시 안 함", "Off" if en else "表示しない"),
            ("_viewOpt() — 기술 선택 연출 (1015)", ""), ("기술 선택 연출", "Skill Pick Scene" if en else "技の選択演出"),
            ("넓은 화면의 스타일리시 전투에서 차례가 온 학생의 머리 위에 기술 상자가 떠서 스킬이 뜨고 골라지는 모습을 보여 준다. 2배속 이상은 짧게. 몬스터와 필살기는 바로 줌인한다.",
             "In stylish battles on wide screens, skill boxes pop up over the acting student to show skills appearing and being picked. Shorter at 2× and above. Monsters and ultimates zoom in right away."
             if en else "広い画面のスタイリッシュ戦闘で、手番の来た生徒の頭上に技の箱が浮かび、スキルが出て選ばれる様子を見せる。2倍速以上は短くなる。モンスターと必殺技はすぐにズームインする。")]


def put(path, rows, indent):
    d = json.load(open(path, encoding="utf-8"))
    for k, v in rows:
        if k in d and d[k] != v and not k.startswith("_"):
            print("  값 바뀜", path.split("tools/")[1], k[:30])
        d[k] = v
    open(path, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=indent) + "\n")


def main():
    for lang, ind in (("en", 1), ("ja", 2)):
        b, u = battle_rows(lang), ui_rows(lang)
        put(os.path.join(I18N, lang, "battle.json"), b, ind)
        put(os.path.join(I18N, lang, "ui.json"), u, ind)
        print(lang, "battle", len([r for r in b if not r[0].startswith("_")]), "· ui", len([r for r in u if not r[0].startswith("_")]))


if __name__ == "__main__":
    main()
