"""
zh.py - the Chinese half of hookscore.py, beats.py and swipe.py.

Chinese has no spaces, so "split into words" finds nothing and every Chinese
hook used to score as zero words long. Here one Han character is one unit:
a character is one syllable, so units divided by a speaking rate gives
seconds, the same job words / wpm does for English.

Two spoken varieties are told apart, because they run at different speeds
and use different words: Mandarin as spoken in Taiwan ("zh") and Cantonese as
spoken in Hong Kong ("yue"). Cantonese is detected from characters that only
written Cantonese uses (嘅, 咗, 喺, 唔...). Traditional and Simplified Mandarin
share one lexicon below: entries list both forms where they differ.

The word lists are heuristics in the same spirit as the English ones in
hookscore.py: they catch greetings, preambles and lines with nothing concrete
in them. They are not a view predictor.
"""

import re

HAN = "㐀-䶿一-鿿豈-﫿\U00020000-\U0003134f"
HAN_RE = re.compile(f"[{HAN}]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]+")

# Characters written Cantonese uses and written Mandarin does not. Two are
# needed: one can be a loan (Taiwan writes 就這樣囉), two rarely is.
# 囉 and 啦 are left out because Taiwan Mandarin uses them too.
CANTONESE_RE = re.compile("[嘅咗喺唔冇啲哋嘢佢咁噉嚟乜㗎喎啫嗰咩睇攞嘥諗揾搵畀俾冚嚿]")

# Syllables per second, pauses included. Read-aloud studies measure Mandarin
# at 5.2-5.9 and Cantonese at 5.6 with pauses removed (Pellegrino et al. 2011;
# Coupe et al. 2019); conversation and newsreading with pauses run 3.8-4.8.
# Cantonese is the Mandarin figure times the measured Cantonese/Mandarin
# ratio, 0.95. Sources: docs/asia/chinese.md, section 1.
# ponytail: one rate per variety; a creator who has timed themselves should
# pass --wpm to beats.py (it means syllables per minute for Chinese).
RATE = {"zh": 4.5, "yue": 4.3}

# Hook length in characters. An English word is about 1.5 Mandarin or 1.7
# Cantonese characters, so the English 5-12 words becomes 8-18 and 9-20.
HOOK_CHARS = {"zh": (8, 18), "yue": (9, 20)}
PER_CHAR = {"zh": 1.5, "yue": 1.7}

# A Latin word or a figure counts as one unit, a Han character as one unit.
UNIT_RE = re.compile(f"[{HAN}]|(?:NT|HK|US|S)?[$＄]?[0-9０-９][0-9０-９,.]*%?|[A-Za-z][A-Za-z'’-]*")


def is_cjk(text):
    """Mainly Chinese: at least two Han characters, and more Han characters
    than Latin words. A character and a word are each about one unit of
    meaning, but a Chinese word averages 1.6 characters, so Chinese has to
    outnumber the Latin words two to one: "你嘅 IG bio 寫錯咗" is Chinese,
    "Our 黑糖珍珠鮮奶 is back, limited run" is English with a product name.
    The same function is copied in ig-human/detect.py and ig-caption/caption.py
    so those skills run on their own; tests/check_asia.py keeps them equal."""
    han = len(HAN_RE.findall(text))
    return han >= 2 and han > 2 * len(LATIN_WORD_RE.findall(text))


def variety(text):
    """'yue' for written Cantonese, 'zh' for written Mandarin: two markers,
    or one for every 50 characters (a short hook has room for only one)."""
    markers = len(CANTONESE_RE.findall(text))
    return "yue" if markers >= 2 or (markers and markers * 50 >= len(HAN_RE.findall(text))) else "zh"


def units(text):
    return UNIT_RE.findall(re.sub(r"(?<=\d),(?=\d)", "", text))


def units_before(text, index):
    return len(units(text[:index]))


# ---------------------------------------------------------------- concrete markers
_NUM = "零〇兩二三四五六七八九十百千萬万億亿半幾几"
_LEAD = "零〇兩二三四五六七八九十百千萬万億亿半"     # 幾 alone is "several", not a number
_UNIT = ("萬|万|千|百|億|亿|元|塊|块|蚊|個|个|次|天|日|週|周|星期|個月|个月|月|年|小時|小时|"
         "分鐘|分钟|秒|倍|成|折|人|位|條|条|片|間|间|家|克|公斤|斤|件|單|单|張|张|支|杯|"
         "碗|份|套|堂|班|晚|歲|岁|號|号|%|％")
_UNIT = "|".join(sorted(_UNIT.split("|"), key=len, reverse=True))   # 個月 before 個
NUMBER_RE = re.compile(
    r"(?:NT|HK|US|S|RM)?[$＄¥￥]\s?[0-9０-９][0-9０-９,，]*(?:\.[0-9]+)?"     # money with a sign
    rf"|[0-9０-９][0-9０-９,，]*(?:\.[0-9]+)?\s?[十百千萬万億亿]*(?:{_UNIT}|k\b|K\b)?"  # a figure: 3千萬元
    rf"|百分之[{_NUM}一]+"                                                       # 百分之三十
    rf"|(?<![{_NUM}一])(?!千[萬万](?![{_NUM}一元塊块蚊人]))[{_LEAD}][{_NUM}一]*(?:{_UNIT})"  # 三萬元, 兩個月; not 千萬別
    r"|一(?:萬|万|千|百|億|亿|成|倍|折|半)"                                      # 一萬, 一成 (bare 一 is filler)
)
# Brand and product names inside Chinese are usually Latin script: Canva, IG.
NAME_RE = re.compile(
    r"(?<![A-Za-z$])(?!(?:OK|IG|DM|PM|CF|KOL|FB|YT|LOL|OMG|WOW|BTW|CEO|HK|NT|TW|US|AI|DIY|SOP)(?![A-Za-z]))"
    r"(?:[A-Z][a-z][A-Za-z0-9]*|[A-Z]{3,})")
# Places people can check are concrete too: Hong Kong districts and areas,
# Taiwan cities and Taipei districts, and MTR / MRT exits (A2出口).
PLACE_RE = re.compile(
    # Names that are also ordinary words (三重 triple, 淡水 freshwater, 太子
    # prince, 中和 neutralise) are left out on purpose.
    "中環|上環|灣仔|銅鑼灣|北角|鰂魚涌|西環|堅尼地城|香港仔|赤柱|尖沙咀|佐敦|油麻地|旺角|"
    "深水埗|長沙灣|荔枝角|美孚|九龍城|土瓜灣|紅磡|黃大仙|鑽石山|觀塘|牛頭角|九龍灣|將軍澳|西貢|"
    "沙田|大圍|大埔|粉嶺|上水|元朗|天水圍|屯門|荃灣|葵涌|青衣|東涌|長洲|啟德|"
    "台北|臺北|新北|桃園|新竹|台中|臺中|台南|臺南|高雄|基隆|宜蘭|花蓮|台東|臺東|屏東|嘉義|彰化|"
    "南投|雲林|苗栗|澎湖|金門|信義區|大安區|中山區|松山區|內湖|士林|北投|萬華|西門町|"
    "新莊|天母|"
    r"[A-Z]\d{1,2}\s?出口")
PRICE_RE = re.compile(rf"[$＄¥￥]\s?[0-9０-９]|[0-9０-９{_NUM}一]\s?(?:元|塊|块|蚊|萬元|万元)")

# ---------------------------------------------------------------- stakes
# Cost, loss, negation, reversal. Matched as substrings, so short words that
# hide inside common compounds carry a guard (別 is not 特別, 輸 is not 輸入).
STAKES_RE = re.compile(
    "不要|千萬|千万|沒有|沒人|没有|没人|不是|(?<![不沒没])錯|(?<![不沒没])错|失敗|失败|虧|亏|賠|赔|蝕|浪費|浪费|後悔|后悔|"
    "被騙|被骗|騙|骗|結果|结果|竟然|居然|但是|卻|却|只有|免費|免费|損失|损失|風險|风险|"
    "危險|危险|警告|禁止|違法|违法|秘密|真相|最差|最慘|最惨|討厭|讨厌|停止|刪掉|删掉|取消|"
    "被炒|失業|失业|倒閉|倒闭|執笠|唔好|冇|唔係|白做|白費|白费|流失|漲價|涨价|加價|加价|"
    "太貴|太贵|罰|罚|扣錢|扣钱|欠|搞砸|翻車|翻车|踩雷|踩坑|中伏|伏|"
    # contrast and limits, the Chinese for "only", "before", "but", "instead"
    "以前|從前|从前|直到|原來|原来|而是|但|只有|淨係|"
    "(?<![一兩两三四五六七八九十幾几])只(?!是)|"
    # more loss and reversal words, Traditional and Simplified
    "血虧|血亏|白花錢|白花钱|冤枉錢|冤枉钱|上當|上当|吃虧|吃亏|錯過|错过|代價|代价|後果|后果|"
    "毀了|毁了|崩潰|崩溃|破產|破产|罰款|罚款|違規|违规|智商稅|智商税|封號|封号|一場空|一场空|"
    "沒想到|没想到|才發現|才发现|陷阱|避坑|割韭菜|限流|"
    # Cantonese only (Wiktionary dialect labels)
    "蝕底|執輸|搵笨|被人呃|呃人|呃錢|呃like|嘥|走數|甩轆|爆煲|千祈|"
    "(?<![特分區区告識识性類类級级派個个])[別别](?![人的墅具])|(?<![運运])[輸输](?![入出送])"
)

# ---------------------------------------------------------------- openers and address
WEAK_OPENERS = (
    "大家好", "哈囉", "哈啰", "哈佬", "嗨", "欸", "誒", "那個", "那个", "嗯", "今天", "今日",
    "其實", "其实", "就是", "所以", "首先", "我想", "我要跟", "你知道嗎", "你知道吗",
    "你知不知道", "你知唔知", "你有沒有", "你有没有", "你有冇", "有沒有人", "有没有人",
    "這支影片", "这支视频", "呢條片", "在這", "在这", "歡迎", "欢迎", "各位", "大家",
)
# Chinese drops the subject: 不用買整條 and 唔使排隊 talk to the viewer as
# directly as an imperative does.
IMPERATIVE_RE = re.compile(
    "^\\s*(?:[別别](?![人的])|不要|千萬別|千万别|唔好|不用|不必|唔使|唔洗|免|停止|試試|试试|試下|"
    "記住|记住|收藏|立刻|馬上|马上|快(?![樂乐])|偷|抄|刪|删|用(?![戶户家心品料])|看(?![到來来起法似])|"
    "睇|寫|写|傳|传|拿|開始|开始|檢查|检查|去(?![年過过])|先(?![生前後后]))")
VIEWER_RE = re.compile("你|妳|您")
QUESTION_RE = re.compile("[？?]")
CROWD_RE = re.compile("大家|各位")
FIRST_RE = re.compile("我|咱")

HASHTAG_RE = re.compile(r"#[^\s#]+")
DEALBREAKERS = [
    (re.compile("^\\s*(?:先|請|请)?(?:別|别|不要|唔好)(?:再)?(?:滑|划|碌|滾|滚)|^\\s*停一停"),
     "Opens with \"stop scrolling\" (先別滑走 / 唔好碌走). Asking for attention proves you have not earned it."),
    (re.compile("(?:今天|今日)(?:這支|这支|這部|这部|這集|这集|呢條|呢条|呢集)?(?:的)?(?:影片|片|視頻|视频|reel|Reel)"
                "|(?:這支|这支|呢條|呢条)(?:影片|片|視頻|视频)(?:要|會|会|將|将)|(?:這集|这集|呢集)(?:要|會|会|將|将)"
                "|(?:跟|同|和)(?:大家|你們|你们|你哋)分享|我(?:來|来)教你|話你知"),
     "Video preamble (今天這支影片 / 跟大家分享). Delete it and open on the payoff."),
    (re.compile("^\\s*(?:哈囉|哈啰|哈佬|嗨|大家好|各位好|[Hh]ello|[Hh]i\\b)"),
     "Greeting. Nobody came to the feed to be greeted."),
    (HASHTAG_RE,
     "Hashtag in the hook. Hashtags belong at the bottom of the caption, if anywhere."),
]

# ---------------------------------------------------------------- loops (beats.py)
_COMMON_BIGRAMS = {
    "一個", "一个", "我們", "我们", "你們", "你们", "這個", "这个", "那個", "那个", "什麼", "什么",
    "就是", "可以", "沒有", "没有", "不是", "因為", "因为", "所以", "現在", "现在", "今天",
    "一天", "我哋", "你哋", "佢哋", "係咪", "唔係", "嘅嘢", "一樣", "一样",
}


_FUNCTION = set("的了是在我你他她它們们這这那就都也還还很不沒没有和跟與与個个一嗎吗呢吧啊喔啦嘅咗喺唔係佢哋")


def bigrams(text):
    """Character pairs that can carry a loop: no function characters."""
    han = "".join(HAN_RE.findall(text))
    pairs = {han[i:i + 2] for i in range(len(han) - 1)} - _COMMON_BIGRAMS
    return {p for p in pairs if not (set(p) & _FUNCTION)}
