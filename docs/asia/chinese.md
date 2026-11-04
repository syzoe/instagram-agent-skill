# Chinese text mechanics for the Instagram skill tools

Scope: what the hook scorer, beat-sheet timer, caption linter and AI-text detector need so that
Chinese (Taiwan Mandarin, Hong Kong Cantonese, Simplified) is not counted as zero words.
All web sources retrieved 2026-11-03. Source IDs `[Sn]` are listed at the end.
Labels: **UNVERIFIED** = claim found but not confirmed at the source; **INFERENCE** = my reasoning
or design choice, no source; **LOCAL** = computed or tested here on 2026-11-03.

## 1. Speaking rate

### Measurements found

| Study | Variety | Task | Rate | Pauses | Src |
|---|---|---|---|---|---|
| Pellegrino, Coupé & Marsico 2011 | Mandarin (region not given) | read texts, "normal" rate | **5.18 ± 0.15 syl/s** (English 6.19, Japanese 7.84, Spanish 7.82) | pauses > 150 ms removed | [S1] |
| Coupé, Oh, Dediu & Pellegrino 2019 | Mandarin (Beijing given as example) | read 15 texts, 10 speakers | **5.86 syl/s** (speakers 5.16–6.65) | pauses > 150 ms removed | [S2] LOCAL |
| same | Cantonese | same | **5.57 syl/s** (speakers 5.14–5.88) | same | [S2] LOCAL |
| same | English (reference) | same | 6.38 syl/s | same | [S2] LOCAL |
| Yuan, Liberman & Cieri 2006 | Mandarin (HKUST/Fisher, strangers) | telephone conversation | **228 ± 2.85 chars/min = 3.8 chars/s** | whole conversation ÷ elapsed time | [S3] |
| same | Mandarin (CallHome/CallFriend, friends/family) | telephone conversation | **247 ± 10.2 chars/min = 4.1 chars/s** | same | [S3] |
| same | English (reference) | telephone conversation | 193–214 words/min | same | [S3] |
| Mok, Fung & Li 2014 | HK Cantonese, 8 TV news anchors | news reading | **mean 5.72 syl/s** (5.19–6.19) | per intonational phrase | [S4] LOCAL mean |
| same | HK Cantonese, 8 students | same news, rehearsed | **mean 4.77 syl/s** (4.53–4.97) | same | [S4] LOCAL mean |
| Chiang et al. 2009 (NCTU, Taiwan) | Mandarin, 1 professional announcer | read corpus at 4 rates | normal **3.82**, fast **4.40**, slow 2.45 syl/s | UNVERIFIED (abstract only) | [S5] |
| Tseng & Lee (Academia Sinica, Taipei) | Mandarin, female radio announcer | faster reading | 199.75 ms/syl ≈ **5.0 syl/s**; slower male reader 304.7 ms ≈ 3.3 | not stated | [S6] |
| Chan & Lee 2005 (CityU HK) | "Chinese" (variety not in abstract) | newscaster rate, listening test | **4.3 chars/s** (231 ms/char) = max preference, 99% correct | not stated | [S7] |
| The News Lens (secondary) | Taiwan adults | "continuous speech" | 4.4 chars/s; 5.3 = very fast | not stated | [S8] UNVERIFIED |

- Coupé values: recomputed from the paper's open data (`InfoRateData.csv`, syllables ÷ duration,
  mean of speaker means); they reproduce its quoted 8.0 Japanese, 7.7 Spanish, 5.3 Vietnamese. LOCAL, [S2].
- **Short-video / fast voiceover: no measured data found** for Mandarin or Cantonese (searched
  Chinese and English; only creator tips with no source). UNVERIFIED.
- No conversational corpus figure specific to **Taiwan** Mandarin or **HK** Cantonese was found.
  The Yuan 2006 conversation data are mainland telephone speech.

### One character = one syllable?
Confirmed for Han characters: Chinese studies count one syllable per character [S1][S2]. Qualify:
- Erhua: 兒 merges into the preceding syllable (花兒 *huār*); "extremely rare or absent" in Taiwan
  Mandarin [S9]. Ignore for TW/HK; Simplified mainland scripts may lose ~1 syllable per 兒.
- Cantonese 咩 is a written contraction of 乜嘢 [S17]: still 1 char = 1 syllable in writing.
- Non-Han tokens are where the rule breaks (INFERENCE): expand before timing.
  `3` → 三 (1); `2026` → 二零二六 (4) or 兩千零二十六 (6); `30%` → 百分之三十 (5);
  `NT$500` → 五百塊 (3) or 新台幣五百元 (6); `AI` → 2; English words ≈ vowel groups (1–3).
- Punctuation = 0 syllables (but a pause).

### Recommended defaults for the timer

| Language | Default | Fast preset | Reasoning |
|---|---|---|---|
| Taiwan Mandarin | **4.5 Han chars/s** (270/min) | 5.5 | Sits between conversation with pauses (3.8–4.1, [S3]) and pause-free reading (5.2–5.9, [S1][S2]); close to the newscaster optimum 4.3 [S7] and Taiwan figure 4.4 [S8]. A rehearsed Reel line is faster than chat but still has comma pauses. INFERENCE. |
| HK Cantonese | **4.3 Han chars/s** (258/min) | 5.2 | Mandarin default × Coupé YUE/CMN ratio 5.57/5.86 = 0.95 [S2]. HK anchors read at 5.7 [S4], so the fast preset is reachable. INFERENCE. |

- These rates exclude sentence breaks. If the English timer adds a pause per sentence, add the
  same per 。！？ (INFERENCE).
- Cantonese scripts need ~12% more characters for the same content (see §2), so the timer already
  gives Cantonese lines more time. The 4.3 covers the slower syllable rate; do not lower it again.

## 2. Length equivalence

### English words → Chinese characters

| Evidence | Ratio | Src |
|---|---|---|
| Commercial translator estimate | 1.4–1.8 Han chars per English word | [S10] (Babcock, 2003-03-06) |
| Pellegrino appendix text P8 (63 English words ↔ 79 Mandarin chars, casual narrative) | 1.25 | [S1] LOCAL count |
| Coupé 15 parallel texts, syllables vs English | Mandarin 0.88×, Cantonese 0.99× English syllables | [S2] LOCAL |

Rule (INFERENCE): **Mandarin Han chars ≈ 1.5 × English words; Cantonese ≈ 1.7 ×** (1.5 × 0.99/0.88).
- Hook target **5–12 English words → 8–18 Han chars (Mandarin), 9–20 (Cantonese)**.
- Cross-check by time: 8–18 chars at 4.5/s = 1.8–4.0 s; 5–12 English words at 193–214 wpm
  [S3] = 1.4–3.8 s. Consistent.
- "Payload by word N" → "payload by Han char 1.5 × N" (1.7 × N for Cantonese). INFERENCE.
- Count each Latin word, @handle or digit group inside Chinese as 1 unit, not per letter. INFERENCE.

### Caption cut before 「更多」 / "... more"
**UNVERIFIED — no Chinese-specific evidence exists.** Searched Meta help, Chinese marketing blogs
and English creator tests: none states or screenshots how many Chinese characters show.
- The 125-character figure itself is third-party; it traces to Meta's *ad* guidance (125 chars,
  "one to three lines") as quoted by Jon Loomer [S11] (page 403 here, so UNVERIFIED).
- Estimate reasoning (INFERENCE): the feed cut is by rendered lines (about two, username first),
  not by character count. Han glyphs are East Asian Width "W" [S12], roughly double an average Latin
  letter. 125 Latin columns ≈ 62 Han; two phone lines of ~23 Han minus the username ≈ **40 Han**.
- Linter rule: measure **display columns** with stdlib `unicodedata.east_asian_width`
  (`W`/`F` → 2, else 1). Warn when the first line's payload ends after **80 columns (~40 Han)**;
  treat 30–55 Han as the plausible range. LOCAL test: 中 。「 😀 → W; １ ， → F; — … → A (ambiguous; count 1).
- Proof is hers, not ours: post one caption made of numbered blocks (`一二三四五六七八九十①…`)
  from a test account, screenshot on two phone sizes, read the last visible block. Until then the
  40 figure stays an estimate.

## 3. Numbers and specificity (regex forms)

Python stdlib only. Do **not** use `\d` (also matches Arabic-Indic ٣, LOCAL) and do not split on
`\w` (`我有3萬元和AI工具` is one `\w+` run, LOCAL). `unicodedata.numeric()` parses single Han
numerals incl. 兩 廿 卅 卌 壹 貳 參 (LOCAL); it raises on 半 and 幾.

| Form | Examples | Regex fragment (Python `re`) | Src |
|---|---|---|---|
| ASCII + full-width digits | 30, ３０, 1.5, 3,000 | `[0-9０-９]+(?:[.,，．][0-9０-９]+)*` | FF10–FF19 [S35]; `int('３０')==30` LOCAL |
| Han numerals | 三, 十五, 兩, 〇 | `[〇零一二三四五六七八九十百千萬万億亿兩两]+` | [S14] |
| Financial numerals | 壹佰, 參拾 | `[壹貳贰參叁肆伍陸陆柒捌玖拾佰仟]+` | [S14] |
| Cantonese tens | 廿幾, 卅 | `[廿卅卌][一二三四五六七八九幾几]?` | [S14] |
| Mixed / approximate | 3萬, 1.5億, 十幾, 幾十, 二十多, 百餘 | `NUM(?:[十百千萬万億亿])?(?:幾|几|多|餘|余|來|来)?` and `(?:幾|几)[十百千萬万]` | INFERENCE |
| Half | 半年, 一半, 半價 | `一?半(?=[年天日月小個个價价])` | [S14] (半 needs a measure word) |
| Percent | 30%, ３０％, 百分之三十 | `NUM\s*[%％]`, `百分之[〇零一二三四五六七八九十百]+` | INFERENCE |
| Tenths / discounts | 三成 (30%), 八折, 85折 | `NUM成`, `NUM折` | INFERENCE |
| Money prefix | NT$, HK$, US$, $, ＄, ¥, ￥, RMB, TWD | `(?:NT|HK|US)?\$|＄|[¥￥]|RMB|TWD|HKD|CNY` + NUM | NT$/TWD [S16]; rest INFERENCE |
| Money suffix | 500元, 五百塊, 十蚊, 5毫, 3萬元 | `NUM\s*(?:萬元|万元|元|圓|塊|块|蚊|毫|角|毛)` | [S15][S16] (蚊/毫 = Cantonese) |
| Currency names | 港幣/港元, 新台幣/新臺幣/台幣, 人民幣/人民币, 美金/美元 | literal alternation | [S15][S16] |
| Time / duration | 3天, 兩個月, 半年, 7日, 3個鐘 | `NUM\s*(?:個|个)?\s*(?:秒|分鐘|分钟|小時|小时|鐘頭|钟头|鐘|钟|天|日|週|周|星期|禮拜|礼拜|月|年)` | INFERENCE (鐘 = hour, Cantonese) |
| Counts with classifiers | 3個方法, 5招, 7步 | `NUM\s*(?:個|个|招|步|點|点|種|种|次|件|款|位|本|篇)` | INFERENCE |
| Latin names inside Chinese | iPhone, Canva, ChatGPT, ＡＩ | `[A-Za-zＡ-Ｚａ-ｚ][A-Za-z0-9Ａ-Ｚａ-ｚ０-９&+.'’-]*` | INFERENCE |
| Quoted titles / names | 《原子習慣》, 「蝦皮」 | `《[^》]{1,30}》`, `「[^」]{1,20}」` | INFERENCE |

`NUM` = digit or Han-numeral group above. Noise guard (INFERENCE): 一 is mostly not a number
(一起, 一定, 一樣); count a Han numeral only when followed by a unit/classifier, or 2+ numerals.
Han-script brand names (蝦皮, 全聯) cannot be caught without a list. UNVERIFIED for coverage.

## 4. Stakes and address words

**Address** (哋 per [S17]; other forms and usage notes INFERENCE):

| Person | Traditional | Simplified | Cantonese | Note |
|---|---|---|---|---|
| 2nd sg | 你, 妳, 您 | 你, 您 | 你 | 妳 = female "you", mainly Taiwan; OpenCC does not fold it, so it can appear in Simplified [S19] |
| 2nd pl | 你們, 妳們, 您們, 大家, 各位 | 你们, 大家, 各位 | 你哋, 大家 | 哋 = Cantonese plural marker [S17] |
| 1st sg | 我, 本人 | 我 | 我 | |
| 1st pl | 我們, 咱們 | 我们, 咱们 | 我哋 | 咱 is rare in TW/HK (INFERENCE) |

**Stakes words** (cost, loss, risk, reversal). Traditional and Simplified forms generated and
round-trip checked against OpenCC tables (LOCAL, [S19]); Cantonese labels from Wiktionary [S18].
Which words carry stakes in a hook is INFERENCE.

| # | 繁 (Traditional-only form) | 簡 (Simplified-only form) | Note |
|---|---|---|---|
| 1–7 | 虧, 虧錢, 血虧, 虧大了, 賠, 賠錢, 輸 | 亏, 亏钱, 血亏, 亏大了, 赔, 赔钱, 输 | loss; 輸 alone is noisy |
| 8–13 | 浪費, 白花錢, 冤枉錢, 後悔, 後悔莫及, 失敗 | 浪费, 白花钱, 冤枉钱, 后悔, 后悔莫及, 失败 | waste, regret |
| 14–18 | 被騙, 上當, 吃虧, 錯, 錯過 | 被骗, 上当, 吃亏, 错, 错过 | OpenCC base gives 喫虧; TW/HK write 吃虧 |
| 19–25 | 千萬不要, 千萬別, 別再, 損失, 代價, 風險, 危險 | 千万不要, 千万别, 别再, 损失, 代价, 风险, 危险 | warning, risk |
| 26–33 | 後果, 慘, 毀了, 崩潰, 破產, 倒閉, 罰款, 違規 | 后果, 惨, 毁了, 崩溃, 破产, 倒闭, 罚款, 违规 | damage |
| 34–37 | 翻車, 智商稅, 封號, 一場空 | 翻车, 智商税, 封号, 一场空 | first three mainland slang (INFERENCE) |
| 38–43 | 結果, 沒想到, 原來, 才發現, 卻, 其實 | 结果, 没想到, 原来, 才发现, 却, 其实 | reversal; 其實 repeated is also an AI tell (§5) |

Same characters in both scripts: 竟然, 居然, 真相, 陷阱, 白做, 踩雷 (TW-leaning), 踩坑, 避坑,
割韭菜, 限流 (mainland-leaning). Regional leanings are INFERENCE.

**Cantonese-only** (Wiktionary dialect label in brackets, [S18]):
蝕 / 蝕錢 (lose money; Cantonese, also Hakka/Min) · 蝕底 (suffer a loss) · 執輸 (miss out) ·
搵笨 (con) · 呃 / 被人呃 (cheat) · 中伏 (HK Cantonese slang: be fooled) · 嘥 / 嘥錢 / 嘥時間 (waste) ·
衰 / 衰咗 (bad, failed; 衰 alone is also standard "decline", noisy) · 走數 (renege on payment) ·
甩轆 (screw up) · 爆煲 (blow up) · 千祈 (never/by all means; also some Mandarin dialects) ·
唔好 (don't). That is 13 Cantonese + 43 T/S + 10 shared = 66 entries.

Regex notes (INFERENCE): build one alternation from both script forms, longest first
(`後悔莫及` before `後悔`); score single-character entries (錯 輸 卻 慘 衰 呃 蝕) only inside the
first ~20 Han chars of a hook, where they rarely appear by accident.

## 5. Chinese AI-writing tells

Sources agree a hit is a signal, not proof: zh Wikipedia says the dash is unreliable alone and
"中文模型是否具備相同規律尚乏實證" [S20]; Humanizer-zh says single words, punctuation, triplets or
four-character words are not reasons to edit by themselves [S21]. Score clusters, not single hits.
HK column: written-Chinese forms are shared with TW; the Cantonese renderings are INFERENCE.
Replacement "→ del" = delete; "→ fact" = say the concrete thing instead.

| # | 繁體（台灣） | 繁體（香港） | 簡體 | Replace | Src |
|---|---|---|---|---|---|
| 1 | 不是A，而是B | 唔係A，而係B / 不是A，而是B | 不是A，而是B | state B | [S20][S21] |
| 2 | 並非A，而是B | 並非A，而是B | 并非A，而是B | state B | [S21] |
| 3 | 不僅是A，更是B | 唔止係A，仲係B | 不仅是A，更是B | → fact | [S21] |
| 4 | 這不只是…，更是… | 呢個唔只係…，仲係… | 这不只是…，更是… | → fact | [S21] |
| 5 | 在這個…的時代 | 喺呢個…嘅時代 | 在这个…的时代 | → del | [S21] (#30) |
| 6 | 隨著…的發展 | 隨住…嘅發展 | 随着…的发展 | → del or dated fact | [S21][S22] |
| 7 | 讓我們一起 | 等我哋一齊 | 让我们一起 | → del / 你可以 | [S23] |
| 8 | 讓我們深入看看 | 等我哋深入睇下 | 让我们深入看看 | → del | [S21] |
| 9 | 以下是你需要知道的 | 以下係你要知嘅 | 以下是你需要知道的 | → del | [S21] |
| 10 | 首先…其次…最後 | 首先…其次…最後 | 首先…其次…最后 | numbers or nothing | [S23][S24] |
| 11 | 總而言之 | 總括嚟講 | 总而言之 | → del | [S21] |
| 12 | 綜上所述 | 綜上所述 | 综上所述 | → del | [S23] |
| 13 | 總的來說 / 總之 | 總之 | 总的来说 / 总之 | → del | [S24] |
| 14 | 值得注意的是 | 值得注意嘅係 | 值得注意的是 | → del | [S23][S24] |
| 15 | 值得一提的是 | 值得一提嘅係 | 值得一提的是 | → del | INFERENCE (sibling of 14) |
| 16 | 需要指出的是 | 要指出嘅係 | 需要指出的是 | → del | [S23] |
| 17 | 由此可見 | 由此可見 | 由此可见 | → del | [S24] |
| 18 | 不難看出 | 唔難睇出 | 不难看出 | → del | [S24] |
| 19 | 具有重要意義 | 具有重要意義 | 具有重要意义 | → what changes | [S24] |
| 20 | 至關重要 / 意義重大 | 至關重要 | 至关重要 / 意义重大 | 很重要 / → del | [S20][S21] |
| 21 | 標誌著（新時代） | 標誌住 | 标志着 | → del | [S20][S21] |
| 22 | 奠定基礎 | 奠定基礎 | 奠定基础 | → fact | [S20] |
| 23 | 不斷變化的格局 | 不斷變化嘅格局 | 不断变化的格局 | → del | [S20] |
| 24 | 不可磨滅 | 不可磨滅 | 不可磨灭 | → del | [S20] |
| 25 | 根植於 | 植根於 | 根植于 | 來自 | [S20] |
| 26 | 見證 | 見證 | 见证 | 看到 | [S20] |
| 27 | 穩穩地接住（你） | 穩穩陣陣接住 | 稳稳地接住 | → del | [S20] |
| 28 | 彰顯了… / 充分彰顯 | 彰顯咗 | 彰显了 / 充分彰显 | → del tail | [S21] (#15) |
| 29 | 為什麼？因為… | 點解？因為… | 为什么？因为… | state the reason | [S20] example |
| 30 | 你可能會問… | 你可能會問… | 你可能会问… | → del | [S21] (#5) |
| 31 | 創新、突破和全新的可能 (empty triplet) | 同左 | 创新、突破和全新的可能 | keep only concrete items | [S20][S21] |
| 32 | 穩定高效、安全可靠、簡單易用 | 同左 | 稳定高效、安全可靠、简单易用 | plain clause | [S21] (#29) |
| 33 | 進行優化 / 進行討論 | 進行優化 | 进行优化 / 进行讨论 | 優化 / 討論 | [S21] (#27) |
| 34 | 好問題！… 希望這對你有幫助！ | 好問題！… 希望幫到你！ | 好问题！… 希望这对你有帮助！ | → del | [S21] (#22) |
| 35 | 讓我們拭目以待 / 期待更多可能 | 拭目以待 | 让我们拭目以待 / 期待更多可能 | → del | [S21] (#31) |
| 36 | 其實…其實… (repeated) | 其實…其實… | 其实…其实… | keep one | INFERENCE |
| 37 | 真正的… / 本質上 | 真正嘅… / 本質上 | 真正的… / 本质上 | → del | INFERENCE |
| 38 | 賦能 | 賦能 | 赋能 | 幫…做到X | [S21][S25] |
| 39 | 助力 | 助力 | 助力 | 幫 / 讓 | INFERENCE |
| 40 | 打造 | 打造 | 打造 | 做 / 建 | INFERENCE |
| 41 | 解鎖（新技能） | 解鎖 | 解锁 | 學會 | INFERENCE |
| 42 | 全方位 | 全方位 | 全方位 | → del or list | INFERENCE |
| 43 | 一站式 | 一站式 | 一站式 | 一個地方搞定 | INFERENCE |
| 44 | 無縫 | 無縫 | 无缝 | → del | [S21] |
| 45 | 顛覆 | 顛覆 | 颠覆 | 改變 | INFERENCE |
| 46 | 重新定義 | 重新定義 | 重新定义 | → what changed | INFERENCE |
| 47 | 深度解析 / 深入探討 | 深入探討 | 深度解析 / 深入探讨 | 講清楚 | [S21] |
| 48 | 探索 | 探索 | 探索 | 看 / 試 | INFERENCE |
| 49 | 你的…旅程 | 你嘅…旅程 | 你的…旅程 | → del | INFERENCE |
| 50 | 乾貨 | 乾貨 | 干货 | → del | INFERENCE |
| 51 | 抓手 | 抓手 | 抓手 | 方法 | INFERENCE |
| 52 | 閉環 | 閉環 | 闭环 | 做完 | [S21][S25] |
| 53 | 顆粒度 / 對齊 | 顆粒度 / 對齊 | 颗粒度 / 对齐 | 細節 / 確認 | [S25] |
| 54 | 底層邏輯 | 底層邏輯 | 底层逻辑 | 原因 | [S25] |
| 55 | 打通 / 鏈路 | 打通 / 鏈路 | 打通 / 链路 | 連起來 / 流程 | [S25] |
| 56 | 痛點 | 痛點 | 痛点 | 麻煩 | INFERENCE |
| 57 | 生態（打造生態） | 生態 | 生态 | → del | INFERENCE |
| 58 | 家人們 | 家人們 | 家人们 | 你 / → del | [S26] |
| 59 | 寶子們 | 寶子們 | 宝子们 | → del | [S27] |
| 60 | 姐妹們 | 姊妹們 / 啲姊妹 | 姐妹们 / 集美们 | 你 | INFERENCE |
| 61 | 建議收藏 / 快筆記起來 | 記得 save 低 | 建议收藏 / 码住 | say why to save | INFERENCE |
| 62 | 一定要看到最後 | 一定要睇到最尾 | 一定要看到最后 | move payload up | INFERENCE |
| 63 | 按讚收藏 / 留言+1 | 俾個 like / 留言 | 点赞收藏 / 评论区扣1 | one specific ask | [S28] |
| 64 | 乾貨滿滿 | 乾貨滿滿 | 干货满满 | → del | INFERENCE |
| 65 | 誰懂啊 / 絕絕子 | 邊個明白 | 谁懂啊 / 绝绝子 / yyds | → del | INFERENCE |
| 66 | 句末～ + 驚嘆號 + 貼圖疊用 | 同左 | 句末～ + 感叹号 + 表情包 | one or none | [S27] |

Structural tells beyond words:
- **Uniform sentence length**: "其句子长度往往过于均衡" [S24]. For burstiness, split on
  `[。！？!?；;…\n]`, measure Han chars per sentence (INFERENCE).
- **Three-part templates** 三段式/四段式 and stock connectives 首先、其次、總之 [S24].
- **Overused set phrases in fiction-style copy**: 淬了毒, 不容置喙, 眼神里有XX，但更多的是XX [S29];
  that author warns that banning common words (虽然, 显然, 果然) overcorrects [S29].

## 6. Typography tells

| Mark | Normal use | Tool rule | Src |
|---|---|---|---|
| Full-width vs half-width punctuation | Chinese text uses full-width ，。！？：；（） with no spaces around them | Flag half-width `, . ? ! : ;` between two Han chars, and a space after ，or 。 | [S32] |
| Dash —— | Standard: 2 em wide. clreq recommends U+2E3A ⸺; two U+2014 "often used". Taiwan MOE handbook text uses `──` (U+2500 ×2, LOCAL code-point check) | **Do not ban.** Accept ——, ──, ⸺. Flag a single `—`, `–` or `--` inside Chinese as non-standard. For overuse, count dash pairs per 100 Han chars and add weight only above ~1/100 or 2 per caption, and only alongside other tells | [S30][S31][S20] (dash alone unreliable) |
| Quotes | TW and HK: 「」 outer, 『』 inner; mainland: “” outer, ‘’ inner | “” or straight `"` in Traditional text = mild tell (Simplified-trained default or converted text). Never flag 「」 | [S31][S34][S21] (#21) |
| Space between Han and Latin (盤古之白) | Both styles are valid: copywriting guide wants a space ("中英文之間需要增加空格"); clreq allows up to 1/4 em typographic gap | Do not score presence or absence; flag inconsistency within one text. Name comes from pangu.js README (tongue-in-cheek) | [S32][S30][S33] |
| Ellipsis | …… = two U+2026, six dots, two Han widths (MOE "占行中二格"; clreq) | Flag `...`, single `…`, `。。。` as typography only, not as an AI tell | [S31][S30] |
| Emoji bullets ✅🔥🚀👉✨📌 | Human marketers use them too | Count lines starting with an emoji; 3+ consecutive = tell. zh Wikipedia: AI "很喜歡使用表情符號…尤其常用於列表前面的標記" (citing Washington Post 2025-11-13) | [S20][S21] (#20) |
| Bold `**…**`, `#` headings in a caption | Instagram renders neither (INFERENCE) | Any Markdown in a caption = strong tell (pasted chatbot output) | [S20][S21] (#19) |

## 7. Script detection

**Unicode ranges** (Unicode 18.0 Blocks.txt [S35]; Python 3.14.6 stdlib is Unicode 16.0, LOCAL —
use explicit ranges, since stdlib `re` has no `\p{Han}`):

| Class | Ranges |
|---|---|
| Han ideographs | 4E00–9FFF; 3400–4DBF (Ext A, holds Cantonese 㗎); 20000–2A6DF (Ext B); 2A700–2EE5F (Ext C–F, I); 30000–3347F (Ext G, H, J); F900–FAFF, 2F800–2FA1F (compatibility) |
| CJK punctuation | 3000–303F; FE10–FE1F (vertical); FE30–FE4F (compatibility forms) |
| Full-width forms | FF01–FF60, FFE0–FFE6 (skip FF61–FFDC: half-width kana/Hangul) |
| Bopomofo | 3100–312F, 31A0–31BF (Taiwan 注音 in casual posts, e.g. ㄉ = 的; INFERENCE) |
| Japanese guard | Kana 3040–30FF: if kana ≥ 10% of Han, treat as Japanese (INFERENCE) |

"Mainly CJK" (INFERENCE): Han ÷ (Han + Latin letters) ≥ 0.5, ignoring digits, spaces, emoji
and punctuation. Then use Han-char counts everywhere the English tools use words.

**Traditional vs Simplified**: count hits from the pairs below. Every pair was checked against
OpenCC STCharacters/TSCharacters (LOCAL, [S19]): no simplified form is a valid Traditional
character and no Traditional form is a valid Simplified one.

```
这這 们們 说說/説 会會 为為/爲 时時 来來 对對 还還 没沒 过過 吗嗎 与與 点點 东東 车車
门門 问問 间間 长長 开開 关關 见見 现現 经經 实實 头頭 学學 国國 动動 样樣 让讓 话話
进進 将將 业業 网網 钱錢 买買 卖賣 爱愛 觉覺 应應 该該 题題 认認 识識 写寫 听聽 讲講
帮幫 带帶 给給 边邊 两兩 亿億 块塊 视視 频頻 产產 质質 费費 贵貴 单單 员員 个個
```
(66 pairs.) Accept both 為/爲 and 說/説: OpenCC's base Traditional uses 爲, and its HK
variant table gives 説 [S19]. **Exclude** 后 里 万 云 干 种 价 广 么: each simplified form is also a
valid Traditional character [S19]. Decision (INFERENCE): T = Traditional hits, S = Simplified
hits; need T + S ≥ 3, else "unknown"; T/(T+S) ≥ 0.8 → Traditional, ≤ 0.2 → Simplified, between →
"mixed" (often a bad conversion, itself worth flagging).

**TW vs HK hints** (weak; many HK users type TW forms, INFERENCE): 裡 (TW) vs 裏 (HK); 著 (TW)
vs 着 (HK, also Simplified); 說 (TW) vs 説 (HK); 啟 (TW) vs 啓 (HK) [S19]. Rely on Cantonese markers.

**Spoken HK Cantonese markers** (all listed in [S17] as Cantonese written forms):

嘅 U+5605 (的) · 咗 5497 (了) · 喺 55BA (在) · 唔 5514 (不) · 冇 5187 (沒有) · 啲 5572 (些) ·
哋 54CB (們) · 嘢 5622 (東西) · 佢 4F62 (他) · 咁 5481 (這麼) · 噉 5649 (這樣) · 嚟 569F (來) ·
乜 4E5C (什麼) · 㗎 35CE (的啊) · 喎 558E (哦) · 囉 56C9 (particle) · 啫 556B (而已) · 嗰 55F0 (那) ·
睇 7747 (看) · 畀 7540 (給) · 俾 4FFE (被) · 咩 54A9 (嗎) · 攞 651E (拿) · 搵 6435 (找) · 諗 8AD7 (想) · 瞓 7793 (睡)

Rule (INFERENCE): ≥ 2 distinct markers, or ≥ 1 marker per 50 Han chars → spoken HK Cantonese.
Strongest: 嘅 咗 喺 唔 冇 啲 哋 嘢 嚟 㗎. Weak (also in Mandarin text): 咁 乜 俾 搵. Never use 係 or 呢
(係 appears in Traditional Mandarin 關係; 呢 is a Mandarin particle).

## Not verified

- Short-video voiceover rate for Mandarin or Cantonese: no data. The 4.5 / 4.3 defaults are INFERENCE.
- Taiwan-specific conversational rate: only a secondary article (4.4 chars/s, [S8], page blocked).
- Chiang 2009 and Tseng & Lee: whether pauses are inside the rate; Tseng & Lee publication year.
- Chinese characters visible before 「更多」 on Instagram: no evidence at all; 40 is an estimate.
- Meta's own wording on 125 characters (seen only via a blocked third-party page).
- Regional leanings of slang (踩雷 TW, 割韭菜 mainland) and all HK Cantonese renderings in §5.

## Sources

- [S1] Pellegrino, Coupé, Marsico, "A cross-language perspective on speech information rate", *Language* 87(3), 2011 (accepted May 2011). https://www.livinglanguage.com/fulltext/pellegrino/Pellegrino_to%20appear_Language.pdf
- [S2] Coupé, Oh, Dediu, Pellegrino, "Different languages, similar encoding efficiency", *Science Advances* 5(9), 2019-09-04. https://pmc.ncbi.nlm.nih.gov/articles/PMC6984970 · data: https://github.com/keruiduo/SupplMatInfoRate (InfoRateData.csv, CC-BY 4.0)
- [S3] Yuan, Liberman, Cieri, "Towards an integrated understanding of speaking rate in conversation", Interspeech 2006. https://www.ldc.upenn.edu/sites/default/files/interspeech2006-towards-integrated-understanding.pdf
- [S4] Mok, Fung, Li, "A preliminary study on the prosody of broadcast news in Hong Kong Cantonese", Speech Prosody 2014. https://www.cuhk.edu.hk/lin/people/peggy/MokFungLi_SP2014.pdf
- [S5] Chiang et al., Oriental COCOSDA 2009, NYCU repository record. https://ir.lib.nycu.edu.tw/handle/11536/80823
- [S6] Tseng & Lee, "Speech Rate and Prosody Units: Evidence of Interaction from Mandarin Chinese", Academia Sinica (year not printed). https://www.ling.sinica.edu.tw/upload/researcher_manager_result/3f63f7d1287b996a95d7c6b46e9f7f26.pdf
- [S7] Chan & Lee, "Intelligibility and preferred rate of Chinese speaking", *Int. J. Industrial Ergonomics* 35(3), March 2005. https://scholars.cityu.edu.hk/en/publications/intelligibility-and-preferred-rate-of-chinese-speaking/
- [S8] The News Lens, article 260113 (date unknown; HTTP 403; search snippet only). https://www.thenewslens.com/article/260113
- [S9] Wikipedia, "Erhua". https://en.wikipedia.org/wiki/Erhua
- [S10] Jon Babcock, Unicode mailing list, 2003-03-06. https://www.unicode.org/mail-arch/unicode-ml/y2003-m03/0104.html
- [S11] Jon Loomer, "Recommended Ad Copy Length" (HTTP 403; search snippet only). https://www.jonloomer.com/qvt/recommended-ad-copy-length/
- [S12] Unicode UAX #11 East Asian Width. https://www.unicode.org/reports/tr11/
- [S13] Unicode Halfwidth and Fullwidth Forms block, see [S35].
- [S14] Wikipedia, "Chinese numerals". https://en.wikipedia.org/wiki/Chinese_numerals
- [S15] Wikipedia, "Hong Kong dollar" (蚊, 毫, 港元/港幣). https://en.wikipedia.org/wiki/Hong_Kong_dollar
- [S16] Wikipedia, "New Taiwan dollar" (NT$, 元/圓, 塊, 角/毛). https://en.wikipedia.org/wiki/New_Taiwan_dollar
- [S17] Wikipedia, "Written Cantonese". https://en.wikipedia.org/wiki/Written_Cantonese
- [S18] Wiktionary entries (raw wikitext `{{lb|zh|Cantonese}}` labels), e.g. https://en.wiktionary.org/wiki/中伏
- [S19] OpenCC dictionaries STCharacters, TSCharacters, HKVariants, TWVariants (STCharacters last changed 2026-07-17). https://github.com/BYVoid/OpenCC/tree/master/data/dictionary
- [S20] 中文維基百科「Wikipedia:AI生成文的特徵」(last edited 2026-10-30; cites 朱宥勳「對「AI腔」厭煩了嗎？」https://www.youtube.com/watch?v=9uuX6cb81C8). https://zh.wikipedia.org/wiki/Wikipedia:AI生成文的特徵
- [S21] op7418/Humanizer-zh, SKILL.md, 31 patterns (last commit 2026-09-23). https://github.com/op7418/Humanizer-zh
- [S22] kevintsai1202/Humanizer-zh-TW (Traditional version of S21). https://github.com/kevintsai1202/Humanizer-zh-TW
- [S23] 陌晨《3招秒去AI味！讓文章像人寫的》人人都是产品经理, 2025-07-22. https://www.woshipm.com/?p=6244919
- [S24] 简圣宇《智能写作的"AI味"问题》中国社会科学网, 2026-07-03. https://www.cssn.cn/skgz/bwyc/202607/t20260703_6057355.shtml
- [S25] 半月谈 via 中新网《"对齐颗粒度"？"黑话"太多干扰职场生态》, 2024-02-05. https://www.chinanews.com.cn/gn/2024/02-05/10159178.shtml
- [S26] 储泽祥《网络称呼语的前世今生》光明日报 2025-05-11, via 爱思想. https://www.aisixiang.com/data/162538.html
- [S27] 《网络社交语言应繁简相宜》光明日报 via 环球网, 2025-03-12. https://lx.huanqiu.com/article/4LpR2bCpang
- [S28] Meta, "News Feed FYI: Fighting Engagement Bait on Facebook", 2017-12-18 (updated 2019-11-07). https://about.fb.com/news/2017/12/news-feed-fyi-fighting-engagement-bait-on-facebook/
- [S29] 不知《「AI味」的本质是什么？你可能搞错了！》人人都是产品经理, 2026-01-04. https://www.woshipm.com/ai/6316640.html
- [S30] W3C, Requirements for Chinese Text Layout (clreq), Group Note Draft dated 2026-11-04. https://www.w3.org/TR/clreq/
- [S31] 教育部《重訂標點符號手冊》修訂版 (Taiwan). https://language.moe.gov.tw/001/Upload/FILES/SITE_CONTENT/M0001/HAU/Revised_Handbook_of_Punctuation.pdf
- [S32] sparanoid, 中文文案排版指北. https://github.com/sparanoid/chinese-copywriting-guidelines
- [S33] vinta/pangu.js README. https://github.com/vinta/pangu.js
- [S34] 中文維基百科「引號」. https://zh.wikipedia.org/zh-hk/引號
- [S35] Unicode Blocks.txt 18.0.0. https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt
