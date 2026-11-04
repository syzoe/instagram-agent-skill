#!/usr/bin/env python3
"""
check_asia.py - one runnable check for the Chinese (Taiwan / Hong Kong) support
in the five Python tools, plus a guard that English output has not moved.

    python3 -I tests/check_asia.py

English: every tool is run on tests/fixtures/en_* and its JSON must equal the
copy in tests/golden/, which was captured from the tools before any Chinese
support was added. If you change English behaviour on purpose, regenerate the
golden files and say so in the commit.

Chinese: the assertions encode what the tools should notice in a Chinese line,
not exact scores, so the thresholds are loose on purpose.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "skills")
FIX = os.path.join(ROOT, "tests", "fixtures")
GOLD = os.path.join(ROOT, "tests", "golden")

failures = []


def tool(rel, *args, stdin=None):
    cmd = [sys.executable, "-I", os.path.join(S, rel), *args]
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, cwd=ROOT)
    return p.stdout


def js(rel, *args, stdin=None):
    out = tool(rel, *args, "--json", stdin=stdin)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"_raw": out}


def check(name, cond, detail=""):
    print(("ok    " if cond else "FAIL  ") + name + (f"   [{detail}]" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def tmp(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


# ---------------------------------------------------------------- English is unchanged
def rel_fix(name):
    return os.path.relpath(os.path.join(FIX, name), ROOT)


golden = {
    "hookscore": js("ig-reel/hookscore.py", rel_fix("en_hooks.txt")),
    "beats": js("ig-reel/beats.py", rel_fix("en_script.txt"), "--target", "20"),
    "caption": js("ig-caption/caption.py", rel_fix("en_caption.txt"), "--keywords", "contract,freelance"),
    "detect": js("ig-human/detect.py", rel_fix("en_slop.txt")),
    "humanize": js("ig-human/humanize.py", rel_fix("en_slop.txt")),
}
for name, got in golden.items():
    want = json.load(open(os.path.join(GOLD, name + ".json"), encoding="utf-8"))
    check(f"english unchanged: {name}", got == want)


# ---------------------------------------------------------------- hookscore
def hook(text):
    return js("ig-reel/hookscore.py", "--hook", text)


h1 = hook("我花了三萬元請代理商，結果一個客人都沒有")
c = h1.get("checks", {})
check("hook zh: length counts characters", "0 words" not in c.get("LENGTH", {}).get("detail", "0 words"),
      c.get("LENGTH", {}).get("detail"))
check("hook zh: a 20-character line is a sayable length", c.get("LENGTH", {}).get("score", 0) >= 60,
      c.get("LENGTH"))
check("hook zh: 三萬元 counts as concrete", c.get("SPECIFICITY", {}).get("score", 0) >= 75, c.get("SPECIFICITY"))
check("hook zh: 結果/沒有 carry stakes", c.get("STAKES", {}).get("score", 0) >= 70, c.get("STAKES"))
check("hook zh: 我 is first person", c.get("ADDRESS", {}).get("score") == 70, c.get("ADDRESS"))

h2 = hook("哈囉大家好，今天這支影片要跟大家分享我的早晨習慣")
check("hook zh: greeting + video preamble are dealbreakers", len(h2.get("flags", [])) >= 2, h2.get("flags"))
check("hook zh: greeting hook is WEAK", h2.get("verdict") == "WEAK", h2.get("verdict"))
check("hook zh: real hook beats greeting hook", h1.get("score", 0) > h2.get("score", 100) + 20,
      (h1.get("score"), h2.get("score")))

h3 = hook("你的網站每天都在流失四成客人")
check("hook zh: 你 speaks to the viewer", h3.get("checks", {}).get("ADDRESS", {}).get("score") == 100,
      h3.get("checks", {}).get("ADDRESS"))
check("hook zh: 四成 counts as concrete", h3.get("checks", {}).get("SPECIFICITY", {}).get("score", 0) >= 75,
      h3.get("checks", {}).get("SPECIFICITY"))

h4 = hook("你知唔知間鋪一個月蝕咗三萬蚊？")
c4 = h4.get("checks", {})
check("hook yue: 你 speaks to the viewer", c4.get("ADDRESS", {}).get("score") == 100, c4.get("ADDRESS"))
check("hook yue: 三萬蚊 counts as concrete", c4.get("SPECIFICITY", {}).get("score", 0) >= 75, c4.get("SPECIFICITY"))
check("hook yue: 蝕 carries stakes", c4.get("STAKES", {}).get("score", 0) >= 70, c4.get("STAKES"))

h5 = hook("三個方法讓營業額翻倍 #創業")
check("hook zh: Chinese hashtag in the hook is flagged", any("ashtag" in f for f in h5.get("flags", [])),
      h5.get("flags"))

h6 = hook("先別滑走！這個方法讓你省下一半時間")
check("hook zh: 先別滑走 is the stop-scrolling dealbreaker", any("scroll" in f for f in h6.get("flags", [])),
      h6.get("flags"))

spaced = hook("我們店裡賣最好的，是一片 35 元的蔓越莓吐司。").get("score")
tight = hook("我們店裡賣最好的，是一片35元的蔓越莓吐司。").get("score")
check("hook zh: a space around a number does not change the score", spaced == tight, (spaced, tight))
check("hook zh: 以前…只 carries stakes",
      hook("這條吐司以前一天只賣3條").get("checks", {}).get("STAKES", {}).get("score", 0) >= 70)


# ---------------------------------------------------------------- beats
zh_script = """一條蔓越莓麵包，以前一天只賣三條。
我們把它切成五十克的試吃片，一片三十五元。
客人吃完一片，就回來買一整條。
現在一天賣四十條，變成店裡賣最好的麵包。
下次來店裡，先拿一片蔓越莓試試看。
"""
b = js("ig-reel/beats.py", tmp(zh_script), "--target", "20")
chars = sum(1 for ch in zh_script if "一" <= ch <= "鿿")
check("beats zh: counts characters", b.get("total_words", 0) >= chars * 0.9, (b.get("total_words"), chars))
check("beats zh: timing is a Mandarin rate", chars / 6.5 <= b.get("total_seconds", 0) <= chars / 3.5,
      b.get("total_seconds"))
check("beats zh: reports the language", b.get("lang") == "zh", b.get("lang"))
check("beats zh: 三條 in beat 1 counts as concrete",
      (b.get("beats") or [{}])[0].get("concrete", 0) >= 1, (b.get("beats") or [{}])[0])
check("beats zh: loop on 蔓越莓 is found", any("Loops" in n for n in b.get("notes", [])), b.get("notes"))

yue_script = """呢間鋪頭以前一個月蝕三萬蚊。
老闆做咗一樣嘢，就係將價錢寫喺門口。
而家每個月賺返兩萬幾。
你間鋪有冇寫價錢喺門口？
"""
y = js("ig-reel/beats.py", tmp(yue_script))
check("beats yue: Cantonese is detected", y.get("lang") == "yue", y.get("lang"))

long_line = "我們試了很多方法。" * 6
lb = js("ig-reel/beats.py", tmp(long_line))
check("beats zh: a long paragraph splits at 。", len(lb.get("beats", [])) >= 2, len(lb.get("beats", [])))


# ---------------------------------------------------------------- caption
zh_caption = """一片三十五元的蔓越莓試吃片，讓一條麵包從一天三條賣到四十條。

我們把麵包切成五十克，放在櫃台旁邊。客人吃完一片，多半會回來買一整條。

留言「試吃」，我們私訊你下週的試吃時間。

#台北美食 #麵包店 #大安區
"""
cap = js("ig-caption/caption.py", tmp(zh_caption), "--keywords", "蔓越莓,試吃")
check("caption zh: Chinese hashtags are counted", len(cap.get("hashtags", [])) == 3, cap.get("hashtags"))
check("caption zh: 留言 + 私訊 is found as an ask", len(cap.get("asks", [])) >= 1, cap.get("asks"))
vis = cap.get("visible", "")
check("caption zh: the visible window is measured by width, not characters",
      30 <= len(vis) <= 70, (len(vis), vis))
check("caption zh: Chinese keywords are found", any("2/2" in json.dumps(x, ensure_ascii=False)
                                                     for x in (cap.get("checks") or [])), cap.get("checks"))

too_many = zh_caption.replace("#大安區", "#大安區 #烘焙 #試吃 #台北 #甜點")
cap2 = js("ig-caption/caption.py", tmp(too_many))
check("caption zh: seven Chinese hashtags fail the cap",
      any(x.get("status") == "FAIL" and "HASHTAG" in x.get("check", "") for x in (cap2.get("checks") or [])),
      cap2.get("checks"))


# ---------------------------------------------------------------- detect / humanize
zh_slop = ("在這個快速變化的時代，保養不僅僅是一種習慣，更是一種對自己的承諾——讓我們一起探索肌膚的無限可能！"
           "我們致力於為您打造全方位的保養旅程。我們的產品不是單純的面膜，而是一場肌膚的革命。"
           "值得一提的是，我們採用一站式的解決方案，為您賦能，助力您解鎖更好的自己。"
           "總而言之，選擇我們，就是選擇無縫接軌的美麗人生。立即行動，開啟您的蛻變之旅吧！\n")
zh_human = ("上個月我們做了一個實驗：請二十個客人連續兩週，每晚敷一片我們的玻尿酸面膜。"
            "第十天，有六個人回來說臉頰乾的地方不脫皮了，兩個人說沒感覺。"
            "老實說，沒感覺的那兩位本來就是油肌。"
            "所以如果你是乾肌，這片才適合你；油肌的話先別買，我們下個月會出清爽版。"
            "想試的話留言「乾肌」，我私訊你試用包的領取方式。\n")
d_slop = js("ig-human/detect.py", tmp(zh_slop))
d_human = js("ig-human/detect.py", tmp(zh_human))
ds = d_slop.get("checks", {})
check("detect zh: stock phrases are found", ds.get("SLOP DENSITY", {}).get("score", 100) <= 30, ds.get("SLOP DENSITY"))
check("detect zh: 不僅…更… / 不是…而是… structures are found",
      "zh-not-a-but-b" in ds.get("VOICE", {}).get("detail", "") and "zh-not-only" in ds.get("VOICE", {}).get("detail", ""),
      ds.get("VOICE"))
check("detect zh: the slop caption is not PASS", d_slop.get("verdict") != "PASS", d_slop.get("verdict"))
check("detect zh: the specific caption scores 20+ higher than the slop one",
      d_human.get("human_score", 0) >= d_slop.get("human_score", 100) + 20, (d_human.get("human_score"), d_slop.get("human_score")))
check("detect zh: numbers in the specific caption are counted",
      d_human.get("checks", {}).get("SPECIFICITY", {}).get("score", 0) >= 55, d_human.get("checks", {}).get("SPECIFICITY"))

hz = js("ig-human/humanize.py", tmp(zh_slop))
out = hz.get("text", "")
check("humanize zh: 在這個快速變化的時代 is removed", "在這個快速變化的時代" not in out, out[:60])
check("humanize zh: full-width punctuation is kept", "，" in out and "。" in out, out[:60])
import re as _re
check("humanize zh: no half-width comma lands between Chinese characters", not _re.search(r"[\u4e00-\u9fff], ?[\u4e00-\u9fff]", out), out[:60])
hq = js("ig-human/humanize.py", tmp("她說「真的有用」，我回她：「那就好……」\n"))
qt = hq.get("text", "")
check("humanize zh: 「」 and …… are left alone", qt.strip() == "她說「真的有用」，我回她：「那就好……」", qt)

fp_clean = js("ig-human/detect.py", tmp("她說「這個真的有用」，我回她：「那就好」。\n")).get("checks", {}).get("FINGERPRINT", {}).get("score")
fp_mixed = js("ig-human/detect.py", tmp("她說“這個真的有用”,我回她:“那就好”。\n")).get("checks", {}).get("FINGERPRINT", {}).get("score")
check("detect zh: “” and half-width commas in Traditional text are a mild tell", fp_mixed < fp_clean, (fp_mixed, fp_clean))
fp_hans = js("ig-human/detect.py", tmp("她说“这个真的有用”，我回她：“那就好”。\n")).get("checks", {}).get("FINGERPRINT", {}).get("score")
check("detect zh: “” in Simplified text is not a tell", fp_hans == 100, fp_hans)


# ---------------------------------------------------------------- swipe
tsv = "account\tfollowers\tmedian\tviews\thook\n@bakery\t8000\t2000\t30000\t我花了三萬元請代理商，結果一個客人都沒有\n"
sw = js("ig-viral/swipe.py", tmp(tsv))
rows = sw.get("rows") or sw.get("reels") or []
check("swipe zh: hook length is counted for Chinese hooks",
      bool(rows) and rows[0].get("words", 0) > 0, (sw.keys() if isinstance(sw, dict) else sw, rows[:1]))


# ---------------------------------------------------------------- review round 1
# Mixed Chinese-English is still Chinese: one English word must not outweigh it.
mx = hook("你嘅 IG bio 寫錯咗，難怪冇人 follow 你")
check("mixed: Cantonese with English words is scored as Chinese",
      "characters" in mx.get("checks", {}).get("LENGTH", {}).get("detail", ""), mx.get("checks", {}).get("LENGTH"))
hm = js("ig-human/humanize.py", tmp("新店開張——“免費試飲”三天 #coffee #hongkong\n"))
check("mixed: a Chinese caption with English hashtags keeps its Chinese typography",
      "——" in hm.get("text", "") and ", \"" not in hm.get("text", ""), hm.get("text"))

# The three copies of the Chinese check must agree.
sys.path.insert(0, os.path.join(S, "ig-reel")); sys.path.insert(0, os.path.join(S, "ig-human"))
sys.path.insert(0, os.path.join(S, "ig-caption"))
import zh as _zh, detect as _detect, caption as _caption  # noqa: E402
samples = ["I love 台北", "I love 台北 so much", "你嘅 IG bio 寫錯咗", "新店開張 #coffee #hongkong #newopening",
           "台北", "a", "", "🔥🔥", "Canva 教學：三步做好封面", "Our 黑糖珍珠鮮奶 is back — limited run!",
           "Try our 珍珠奶茶 today"]
check("English lines with a Chinese product name are English",
      not _zh.is_cjk("Our 黑糖珍珠鮮奶 is back — limited run!") and not _zh.is_cjk("Try our 珍珠奶茶 today"))
check("is_cjk agrees across zh.py, detect.py and caption.py",
      all(_zh.is_cjk(t) == _detect.is_cjk(t) == _caption.is_cjk(t) for t in samples),
      [(t, _zh.is_cjk(t), _detect.is_cjk(t), _caption.is_cjk(t)) for t in samples])

# Ordinary words survive the humanizer; risky slop is flagged, not rewritten.
for text, keep in [("感謝我的家人們一路支持。", "家人們"), ("用 Face ID 解鎖手機。", "解鎖"),
                   ("這趟台南之旅吃了五家店。", "之旅"), ("我們致力於做好每一條麵包。", "致力於")]:
    out_ = js("ig-human/humanize.py", tmp(text + "\n")).get("text", "")
    check(f"humanize zh: '{keep}' in an ordinary sentence is kept", keep in out_, out_)
fl = js("ig-human/humanize.py", tmp(zh_slop))
check("humanize zh: 致力於 and 打造 are flagged for a rewrite",
      any("致力於" in json.dumps(x, ensure_ascii=False) for x in fl.get("report", {}).get("structures", [])), fl.get("report", {}).get("structures"))

# One correct —— in a short human caption is not a tell.
short = "週末兩天限定——蔓越莓吐司一片35元，賣完就收。\n"
fp1 = js("ig-human/detect.py", tmp(short)).get("checks", {}).get("FINGERPRINT", {}).get("score")
check("detect zh: one —— in a short caption does not cost fingerprint points", fp1 == 100, fp1)
bl = js("ig-human/humanize.py", tmp("三款新品：\n— 蔓越莓吐司\n— 鹽可頌\n— 肉桂捲\n")).get("text", "")
check("humanize zh: a dash used as a list bullet is left alone", bl.count("\n") >= 3 and "，蔓越莓" not in bl, bl)

# Every structure regex in the lexicon compiles, English and Chinese.
lex = json.load(open(os.path.join(S, "ig-human", "slop.json"), encoding="utf-8"))
bad = []
import re as _re2
for st in lex["structures"] + lex["zh"]["structures"]:
    try:
        _re2.compile(st["regex"], _re2.MULTILINE)
    except _re2.error as e:
        bad.append((st["id"], str(e)))
check("every structure regex in slop.json compiles", not bad, bad)
mdx = js("ig-human/detect.py", tmp("**三個重點**\n我們上週賣了四十條吐司，比上個月多了一倍，客人說試吃片很方便，下次還想再來買一條帶回家給家人吃，我們也打算在週末多做二十條。\n"))
check("detect zh: Markdown in a Chinese caption is flagged",
      "zh-markdown" in mdx.get("checks", {}).get("VOICE", {}).get("detail", ""), mdx.get("checks", {}).get("VOICE"))

# English behaviour matches main on inputs the fixtures do not cover:
# accented hashtags, generic tags, emoji, em dashes, curly quotes.
MAIN = tempfile.mkdtemp()
subprocess.run(f"git archive main skills | tar -x -C {MAIN}", shell=True, cwd=ROOT, check=True)
extra_en = {
    "ig-caption/caption.py": "Café opening this week 🎉 first 50 coffees free — today only.\n\n#café #été #hk #ig #tw #coffee\n",
    "ig-reel/hookscore.py": "I lost $18,000 — and my best client — in one week 😬\n",
    "ig-human/detect.py": ("Our café’s new menu is “honestly” the best — it’s a game-changer. "
                           "We tried 12 recipes over 3 weeks. Résumé-worthy? Maybe. Naïve? Never. "
                           "Come by Saturday and try the crème brûlée for $6.\n"),
    "ig-human/humanize.py": "It’s not just coffee — it’s a “ritual”… Delve into our seamless café experience.\n",
}
for rel, text in extra_en.items():
    f = tmp(text)
    new = tool(rel, f, "--json")
    old = subprocess.run([sys.executable, "-I", os.path.join(MAIN, "skills", rel), f, "--json"],
                         capture_output=True, text=True).stdout
    check(f"english matches main on extra input: {rel.split('/')[1]}", json.loads(new) == json.loads(old),
          (new[:200], old[:200]))

# Cantonese needs two markers; Taiwan's 囉 is not one.
tw = js("ig-reel/beats.py", tmp("就這樣囉，我們明天見。\n今天先做到這裡。\n"))
check("beats: Taiwan 就這樣囉 is timed as Mandarin", tw.get("lang") == "zh", tw.get("lang"))

# Particles do not decide the VOICE score, and 嘅/咗 are not particles.
written = ("我們的旺角分店下週一開張，首三天所有美甲服務八折，價錢由三百八十元起。"
           "預約請WhatsApp我們，名額每天二十個，額滿即止。開張當天首十位客人另送護手霜一支。\n")
canto = ("我哋嘅旺角分店下星期一開張，首三日所有美甲服務八折，價錢由三百八十蚊起。"
         "預約就WhatsApp我哋，名額每日二十個，額滿即止。開張當日首十位客人仲送支護手霜。\n")
vw = js("ig-human/detect.py", tmp(written)).get("checks", {}).get("VOICE", {}).get("score", 0)
vc = js("ig-human/detect.py", tmp(canto)).get("checks", {}).get("VOICE", {}).get("score", 0)
check("detect zh: written Chinese and Cantonese of the same caption score within 10 on VOICE",
      abs(vw - vc) <= 10, (vw, vc))

# Things that are not concrete are not counted as concrete.
c1 = hook("千萬別再用這個方法洗臉").get("checks", {}).get("SPECIFICITY", {})
check("hook zh: 千萬 (by all means) is not a number", c1.get("score") == 15, c1)
c2 = hook("幾個方法讓你的貼文更好看").get("checks", {}).get("SPECIFICITY", {})
check("hook zh: 幾個 (several) is not a number", c2.get("score") == 15, c2)
c3 = hook("OK，這是我們的新菜單").get("checks", {}).get("SPECIFICITY", {})
check("hook zh: OK is not a name", c3.get("score") == 15, c3)
c4 = hook("美甲HK$380起，五款新年款").get("checks", {}).get("SPECIFICITY", {})
check("hook zh: HK$380 is one marker, not two", "HK," not in c4.get("detail", "") and "HK$380" in c4.get("detail", ""), c4)
c5 = hook("深水埗呢間茶餐廳午餐減咗十蚊").get("checks", {}).get("SPECIFICITY", {})
check("hook yue: a district (深水埗) counts as concrete", "深水埗" in c5.get("detail", ""), c5)

# Chinese drops the subject: a question or a 不用 line still talks to the viewer.
a1 = hook("不用買整條，先花35元吃一片").get("checks", {}).get("ADDRESS", {}).get("score", 0)
a2 = hook("喺深水埗返工？呢個午餐減咗十蚊").get("checks", {}).get("ADDRESS", {}).get("score", 0)
check("hook zh: a 不用 line addresses the viewer", a1 >= 85, a1)
check("hook yue: a question addresses the viewer", a2 >= 85, a2)
a3 = hook("去年我們只賣三條").get("checks", {}).get("ADDRESS", {}).get("detail", "")
a4 = hook("別人的店都在排隊").get("checks", {}).get("ADDRESS", {}).get("detail", "")
check("hook zh: 去年 and 別人 are not imperatives", "imperative" not in a3 and "imperative" not in a4, (a3, a4))

# Stakes: 不錯 is not a loss, Simplified warnings count.
s1 = hook("這家店的吐司不錯").get("checks", {}).get("STAKES", {})
check("hook zh: 不錯 is not a stakes word", "錯" not in s1.get("detail", ""), s1)
sp = hook("千万别再用这个方法洗脸").get("checks", {}).get("STAKES", {}).get("score", 0)
st_ = hook("千萬別再用這個方法洗臉").get("checks", {}).get("STAKES", {}).get("score", 0)
check("hook zh: Simplified 千万别 scores like Traditional 千萬別", sp == st_, (sp, st_))

# 這部片 in a normal sentence is not a preamble; 今天這支影片 is.
pf = hook("這部片我看了三次，結局還是哭").get("flags", [])
check("hook zh: 這部片 in a sentence is not a video preamble", not any("preamble" in f for f in pf), pf)

# Comma-chained scripts split into beats; function bigrams are not a loop.
chain = "我們以前一天只賣三條吐司，後來把它切成五十克的試吃片，一片三十五元放在櫃台，客人吃完就回來買一整條，現在一天賣四十條\n"
cb = js("ig-reel/beats.py", tmp(chain))
check("beats zh: a comma-chained line splits into beats", len(cb.get("beats", [])) >= 3, len(cb.get("beats", [])))
nl = js("ig-reel/beats.py", tmp("這是我開店的第三年。\n客人越來越少。\n這是我最後一次試。\n"))
check("beats zh: 這是 / 是我 are not a loop", not any("Loops" in n for n in nl.get("notes", [])), nl.get("notes"))

# Nested lexicon entries are counted once.
nest = js("ig-human/detect.py", tmp("我們的一站式的服務。\n")).get("checks", {}).get("SLOP DENSITY", {}).get("detail", "")
check("detect zh: 一站式的 counts once, not twice", nest.startswith("1 stock"), nest)

# humanize and detect agree on sentence-length variation.
vt = ("我們試了三種切法。第一種太厚，客人吃不完。第二種太薄，一拿就碎了，最後丟掉一半。"
      "第三種五十克剛好。現在每天切八十片，中午前就賣完。\n")
hv = [x["name"] for x in js("ig-human/humanize.py", tmp(vt)).get("report", {}).get("structures", []) if "variation" in x["name"]]
dv = js("ig-human/detect.py", tmp(vt)).get("checks", {}).get("BURSTINESS", {}).get("detail", "")
import re as _re3
hvn = _re3.findall(r"variation ([0-9.]+)", " ".join(hv)); dvn = _re3.findall(r"variation ([0-9.]+)", dv)
check("humanize and detect measure the same sentence variation", (not hvn) or (hvn == dvn), (hv, dv))

# Traditional text gets 「」, Simplified keeps “”.
qq = js("ig-human/humanize.py", tmp("她說“這個真的有用”，我也這麼覺得。\n")).get("text", "")
check("humanize zh: “” in Traditional text becomes 「」", "「這個真的有用」" in qq, qq)
qs = js("ig-human/humanize.py", tmp("她说“这个真的有用”，我也这么觉得。\n")).get("text", "")
check("humanize zh: “” in Simplified text is kept", "“这个真的有用”" in qs, qs)

# Asks: LINE and 睇bio count; the visible window and digits.
la = js("ig-caption/caption.py", tmp("一片三十五元的試吃，週末限定。\n\n加 LINE 好友領券，下次來店折十元。\n"))
check("caption zh: 加 LINE 好友 is an ask", len(la.get("asks", [])) == 1, la.get("asks"))
lb = js("ig-caption/caption.py", tmp("新年美甲五款，三百八十蚊起。\n\n詳情睇bio。\n"))
check("caption zh: 詳情睇bio is an ask", len(lb.get("asks", [])) == 1, lb.get("asks"))
d380 = js("ig-caption/caption.py", tmp("新年美甲五款，HK$380起，旺角店。\n"))
hc = [x for x in d380.get("checks", []) if x.get("check") == "HOOK IS CONCRETE"]
check("caption zh: 380 is one number, not three", hc and hc[0]["detail"].startswith(("1 ", "2 ")), hc)
t40 = js("ig-caption/caption.py", tmp(zh_caption), "--truncate", "30")
check("caption zh: --truncate counts Chinese characters", len(t40.get("visible", "")) == 30, len(t40.get("visible", "")))


# ---------------------------------------------------------------- review round 2
# English matches main in text mode too, and with flags the fixtures skip.
en_runs = [
    ("ig-reel/beats.py", "I lost $18,000 on one contract.\nNow I send one page in 24 hours.\nComment CONTRACT.\n", ["--wpm", "150"]),
    ("ig-reel/hookscore.py", "Try our 珍珠奶茶 today, only $5\n", []),
    ("ig-human/humanize.py", "Our 黑糖珍珠鮮奶 is back — limited run! I’m obsessed, it’s “so good”.\n", []),
    ("ig-human/detect.py", "Our 黑糖珍珠鮮奶 is back — limited run! I’m obsessed, it’s “so good”. We sold 300 cups in 2 days at the Mong Kok shop, and the line went round the block twice on Saturday.\n", []),
    ("ig-caption/caption.py", "Café drop 🎉🔥 first 50 free — today only ✨\n\n#café #coffee\n", []),
]
for rel, text, flags in en_runs:
    f = tmp(text)
    for mode in ([], ["--json"]):
        new = subprocess.run([sys.executable, "-I", os.path.join(S, rel), f, *flags, *mode], capture_output=True, text=True)
        old = subprocess.run([sys.executable, "-I", os.path.join(MAIN, "skills", rel), f, *flags, *mode], capture_output=True, text=True)
        check(f"english byte-identical to main: {rel.split('/')[1]} {' '.join(flags + mode)}",
              (new.stdout, new.stderr) == (old.stdout, old.stderr), (new.stdout[:160], old.stdout[:160]))

# The tools agree on what counts as concrete in Chinese.
tricky = "千萬別再用這個方法！幾個步驟就好，OK 嗎？"
cap_t = js("ig-caption/caption.py", tmp(tricky + "\n"))
hc_t = [x for x in cap_t.get("checks", []) if x.get("check") == "HOOK IS CONCRETE"]
check("caption zh: 千萬 / 幾個 / OK are not concrete", hc_t and hc_t[0]["status"] == "WARN", hc_t)

# Ordinary words do not count as machine phrasing in detect either.
travel = ("這趟台南之旅，我和家人們一共吃了七家店。第一天在國華街排了四十分鐘的牛肉湯，"
          "第二天早上六點去吃虱目魚粥。整趟旅程花了八千二百元，比去年的高雄行便宜一千多。"
          "下次想帶爸媽去安平，聽說老街的蝦捲要早點去才買得到。\n")
dt = js("ig-human/detect.py", tmp(travel))
check("detect zh: 之旅 / 旅程 / 家人們 in a real travel caption do not count as stock phrases",
      dt.get("checks", {}).get("SLOP DENSITY", {}).get("score", 0) >= 80,
      (dt.get("verdict"), dt.get("checks", {}).get("SLOP DENSITY")))
check("humanize zh: 天衣無縫 is kept", "天衣無縫" in js("ig-human/humanize.py", tmp("這次合作天衣無縫。\n")).get("text", ""))

# Short Cantonese hooks are Cantonese.
for line in ["你知唔知間鋪一個月蝕三萬蚊", "唔好再買呢隻面霜"]:
    check(f"beats yue: short hook '{line}' is Cantonese",
          js("ig-reel/beats.py", tmp(line + "\n")).get("lang") == "yue")

# Cantonese hook window follows the research: longer than Mandarin.
yl = hook("唔好再買呢隻面霜，我用咗三個月真係冇分別").get("checks", {}).get("LENGTH", {}).get("detail", "")
ml = hook("別再買這款面霜，我用了三個月真的沒差").get("checks", {}).get("LENGTH", {}).get("detail", "")
check("hook: Cantonese window is 9-20, Mandarin 8-18", "want 9-20" in yl and "want 8-18" in ml, (yl, ml))

# Filler 呃 and 用戶 / 看來 / 先生 are not stakes or imperatives.
check("hook zh: 呃 (uh) is not a stakes word",
      "呃" not in hook("呃，我們今天來聊聊麵包").get("checks", {}).get("STAKES", {}).get("detail", ""))
for line in ["用戶都說這款最好用", "看來大家都喜歡吐司", "先生們請看這邊"]:
    check(f"hook zh: '{line[:2]}' is not an imperative",
          "imperative" not in hook(line).get("checks", {}).get("ADDRESS", {}).get("detail", ""))

# One pair of “” in a short Traditional caption is a mild tell, not a zero.
fq = js("ig-human/detect.py", tmp("她說“這個真的有用”，我回她：那就好。\n")).get("checks", {}).get("FINGERPRINT", {}).get("score", 0)
check("detect zh: one “” pair in a short caption is a mild tell", 50 <= fq < 100, fq)

# Place names and names: no 三重 / 淡水 as words, no OMG.
p1 = hook("這個方法讓效果三重加倍").get("checks", {}).get("SPECIFICITY", {}).get("detail", "")
p2 = hook("OMG 這家店太好吃").get("checks", {}).get("SPECIFICITY", {}).get("detail", "")
check("hook zh: 三重 (triple) is not a place, OMG is not a name", "三重" not in p1 and "OMG" not in p2, (p1, p2))

# A sentence about a stock is not a video preamble; 這集要講 is.
check("hook zh: 這支會漲到三百元嗎 is not a preamble",
      not any("preamble" in f for f in hook("這支會漲到三百元嗎").get("flags", [])))
check("hook zh: 這集要講 is a preamble",
      any("preamble" in f for f in hook("這集要講我開店三年學到的事").get("flags", [])))


print(f"\n{len(failures)} failed" if failures else "\nall passed")
sys.exit(1 if failures else 0)
