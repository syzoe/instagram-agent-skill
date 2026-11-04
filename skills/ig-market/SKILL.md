---
name: ig-market
description: >-
  Use when the Instagram account's audience is in Taiwan or Hong Kong, or
  when a Reel script, caption, carousel, story, comment, reply or DM is
  written in Chinese - before any other ig- skill writes for that account.
  Also use when the user asks for 台灣, 香港, 繁體, 廣東話 or Cantonese
  Instagram content.
---

# ig-market

The rest of this pack was written for an English-speaking, US audience. This
skill holds what changes for Taiwan and Hong Kong. Load it first, then run the
skill you came for. Its numbers replace that skill's US defaults.

## 1. Settle the market, once per account

Read `~/.claude/instagram/voice.md`. If its `## Market` section is filled in,
use it. If not, ask these in one message and write the answers into it:

- **Market:** Taiwan or Hong Kong
- **Caption language:** Taiwan is 台灣正體. Hong Kong creators write
  standard written Chinese, Cantonese, or either mixed with English: ask
  which, and use their own past captions if they have them
- **Spoken language for Reels:** Taiwan is Mandarin. Hong Kong is Cantonese
- **How people buy:** online, a shop they walk into, or a booking (LINE in
  Taiwan, WhatsApp in Hong Kong)
- **Regulated category:** food, health food, supplements, cosmetics and
  skincare, medical or aesthetic treatment, alcohol, finance, or none

## 2. Read the files

| Market | Read |
|---|---|
| Taiwan | `taiwan.md` and `chinese.md` in this folder |
| Hong Kong | `hong-kong.md` and `chinese.md` in this folder |
| Chinese copy for Singapore, Malaysia or mainland China | `chinese.md` only. There is no market file yet: say so to the user, and do not borrow Taiwan or Hong Kong rules for them |
| Any market in English | Not this skill. The pack's defaults apply |

## 3. What changes in every skill

| Thing | Pack default (US) | Taiwan / Hong Kong |
|---|---|---|
| Hook length | 5-12 words | 8-18 characters (Cantonese 9-20), as `hookscore.py` scores it. `beats.py` also wants the first beat said inside 3 seconds, about 13 characters, so aim for the short end |
| On-screen card | 6 words | 10 characters |
| Caption cut | ~125 characters | ~40 characters, unverified: hook in the first 30 |
| Vocabulary | US English | the market file's table. Never mix the two markets |
| The ask | comment, save, follow, DM | the same, plus LINE or WhatsApp bookings and "come to the shop" for a business people visit |
| Posting time | "early evening local" | the market file's evidence, labelled as such |
| Calendar | none | the market file's dates |
| Claims | none | the market file's rules, before any results claim: a hook, a "proof" post in a weekly plan, a before-and-after, a testimonial |
| Sponsored posts | none | the market file's disclosure rule |

## 4. The tools

All five Python tools detect Chinese on their own and switch to characters,
Chinese numbers, Chinese stakes words and Chinese machine tells. Cantonese is
detected from its characters (嘅, 咗, 喺, 唔) and timed at its own rate. No
flags are needed. Two limits: `swipe.py` labels hook formulas in English only,
and the Chinese caption cut is an estimate.

## 5. Rules that hold in both markets

- **Claims in a regulated category:** check the market file's table before
  writing any effect, result or before-and-after. If the claim is on the
  banned list, write the experience instead ("用了兩週，我自己覺得…") and tell
  the user which rule it hit. Do not decide for them that a risky claim is
  fine.
- **Proof stays real.** A number in a hook must come from voice.md or the
  user. Never invent a customer count, a sales figure or a testimonial.
- **Write, do not translate.** Write the line a local creator would say, then
  check it with the tools. A translated English hook reads as an ad.
