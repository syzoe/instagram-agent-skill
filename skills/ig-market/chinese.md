# Chinese on Instagram: the mechanics

What changes when the copy is Chinese, for any market. The sourced research,
with every figure and its study, is in `docs/asia/chinese.md` in the repo.

## Length

| Thing | English default in the pack | Mandarin (Taiwan) | Cantonese (Hong Kong) |
|---|---|---|---|
| Speaking rate | 165 words/min | 4.5 characters/s | 4.3 characters/s |
| Hook (`hookscore.py`) | 5-12 words | 8-18 characters | 9-20 characters |
| First beat (`beats.py`) | inside 3 seconds | about 13 characters | about 13 characters |
| On-screen card | 6 words or fewer | 10 characters or fewer | 10 characters or fewer |
| Carousel slide | headline 3-7 words, 25 words under it | headline 5-10 characters, 40 under it | same |
| Caption before 更多 | about 125 characters | about 40 characters (UNVERIFIED) | same |

One Han character is one syllable. Digits, Latin words and currency break
that: `2026` is said as four or six syllables, `NT$500` as three to six. When
a line has many of them, say it out loud before trusting the timing.

The caption cut for Chinese has no published figure. It is an estimate from
two feed lines of about 20 characters. Until it has been checked on a phone,
put the hook in the first 30 characters. `caption.py --truncate N` counts
Chinese characters for a Chinese caption.

## Typography

- Full-width punctuation inside Chinese: ，。！？：；（）. A half-width `,` or
  `.` between two Chinese characters reads as pasted or converted text.
- Quotes: Taiwan and Hong Kong use 「」 (outer) and 『』 (inner). Mainland
  Simplified uses “”. “” in a Traditional caption is a mild machine tell.
- Dash: —— (or ──) is correct Chinese punctuation. Do not delete it the way
  the English em dash gets deleted. A single — inside Chinese is wrong. More
  than one dash pair per caption, alongside other tells, reads as generated.
- Ellipsis: …… (two characters, six dots) is standard. `...` is fine on a
  phone. Neither is a machine tell.
- A space between Chinese and Latin text (`用 Canva 做`) is a style choice.
  Pick one and keep it the whole way through.
- Markdown (`**bold**`, `# heading`) never renders in a caption. If it is
  there, it was pasted from a chatbot.

## Script

- Never mix Traditional and Simplified in one piece. Taiwan and Hong Kong
  read Traditional. Converting Simplified with a character table is not
  enough: the vocabulary is different too (see the market file).
- Taiwan Traditional and Hong Kong Traditional are not the same either:
  different words (影片 vs 片, 品質 vs 質素, 貼文 vs 帖子). Most
  Traditional-Chinese training text is Taiwanese, so Hong Kong drafts drift
  toward Taiwan words. Write for one market per piece.
- Spoken Cantonese is written with its own characters (嘅, 咗, 喺, 唔, 冇,
  啲, 哋, 嘢). A Cantonese voiceover script must be written in them, or it
  will be read aloud as Mandarin-shaped Cantonese.

## Machine tells in Chinese

`slop.json` in ig-human has a `zh` block: about 100 stock phrases and 11
structures (不是A，而是B; 不僅A，更是B; 在這個…的時代; 首先…其次…最後; emoji-bullet
lists). One hit proves nothing. A cluster does. The structures are flagged,
not rewritten: rewrite them yourself.

What humans do that models do not: sentence-final particles (啊, 吧, 呢, 喔,
啦 in Taiwan; 啦, 喎, 囉, 㗎, 呀 in Hong Kong), first and second person, a
number or a name in most sentences, sentences of very different lengths.

## Hook formulas

The 26 formulas in `ig-reel/hooks.json` transfer: they are shapes, not
sentences. Write the Chinese line a local creator would say, then score it.
Do not translate the English example. `swipe.py` labels formulas with English
patterns only, so label Chinese hooks by hand against `hooks.json`.

Chinese openers that waste the first second. `hookscore.py` flags these as
dealbreakers: 大家好 / 哈囉, 今天這支影片, 跟大家分享, 先別滑走 / 唔好碌走.
It scores these lower as weak openers: 你知道嗎 / 你知唔知, 其實, 今天.

Chinese drops the subject. A question (喺深水埗返工？) or a 不用 / 唔使 line
already talks to the viewer, and the scorer counts it that way.
