#!/usr/bin/env python3
"""
caption.py - lint an Instagram caption and show exactly what the feed shows
before the "... more".

Instagram gives a caption about 125 characters in the feed and hides the rest
behind a tap. Almost every caption that fails, fails there: the hook is in
sentence three, or the first line is a greeting, or the whole thing opens on a
hashtag. This prints the visible window as a box so you can read it the way a
scrolling stranger does, then checks the eight things that are worth checking.

The 125-character cut is an approximation. The real number moves with the
device, the font size and where your line breaks fall, which is exactly why
you want a margin rather than a caption engineered to end at 125. Change it
with --truncate if you want to test a tighter one.

Usage
  python3 caption.py caption.txt
  python3 caption.py caption.txt --keywords "proposal software,client contract"
  pbpaste | python3 caption.py -
  python3 caption.py caption.txt --json
"""

import argparse
import json
import re
import sys
import textwrap
import unicodedata

LIMIT = 2200             # Instagram's hard caption limit.
TRUNCATE = 125           # Roughly where the feed cuts to "... more".
ZH_TRUNCATE = 40         # Chinese characters (each takes the width of two Latin ones).
                         # UNVERIFIED: no published figure exists. Estimate from
                         # two feed lines of ~20 characters; check it by posting a
                         # numbered test caption and reading where 更多 lands.
HASHTAG_LIMIT = 5        # Instagram's cap per post or reel since 18 Dec 2025,
                         # down from 30. Announced by the @Creators account:
                         # "using fewer (up to 5) more targeted hashtags,
                         # rather than many generic ones, can improve both your
                         # content's performance and people's experience".

HASHTAG_RE = re.compile(r"(?:^|\s)(#[A-Za-z0-9_]+)")
ZH_HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")   # Chinese captions: #台北美食 is one tag
MENTION_RE = re.compile(r"(?:^|\s)(@[A-Za-z0-9_.]+)")
LINK_RE = re.compile(r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|co|io|net|org|ai|app)/\S*",
                     re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")
CONCRETE_RE = re.compile(r"\$\s?\d|\b\d[\d,.]*\b|(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE)

ASKS = [
    (re.compile(r"(?i)\bcomment (?:the word |\")?[A-Z0-9]{2,}\b"), "comment a keyword"),
    (re.compile(r"(?i)\b(?:dm|message) me\b"), "DM me"),
    (re.compile(r"(?i)\bsave (?:this|it)\b"), "save this"),
    (re.compile(r"(?i)\bshare (?:this|it)\b"), "share this"),
    (re.compile(r"(?i)\bfollow (?:me|for)\b"), "follow"),
    (re.compile(r"(?i)\blink in (?:my )?bio\b"), "link in bio"),
    (re.compile(r"(?i)\b(?:swipe|tap) (?:through|left|right|for|to)\b"), "swipe or tap"),
    (re.compile(r"(?i)\btell me\b|\bwhat would you\b|\bwhich one\b"), "answer a question"),
]

FILLER_TAGS = {"#viral", "#fyp", "#explore", "#explorepage", "#foryou", "#foryoupage",
               "#trending", "#instagood", "#love", "#follow", "#like4like", "#reels",
               "#reelsinstagram", "#viralreels", "#instadaily"}
# Chinese tags that say nothing about the topic (Chinese captions only).
ZH_FILLER_TAGS = {"#日常", "#生活", "#分享", "#推薦", "#推荐", "#熱門", "#热门", "#爆紅", "#爆红",
                  "#好物分享", "#ig", "#igdaily", "#tw", "#hk"}

# Chinese captions. Kept in this file, not imported, so ig-caption still runs
# when it is copied on its own.
HAN_RE = re.compile("[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
ZH_CONCRETE_RE = re.compile(
    r"(?:HK|NT|US|S)?[$＄]?\s?[0-9０-９][0-9０-９,，.]*"
    r"|[兩两二三四五六七八九十百千萬万億亿半幾几][兩两二三四五六七八九十百千萬万億亿一]*"
    r"(?:萬|万|千|百|億|亿|元|塊|块|蚊|個|个|天|日|週|周|個月|月|年|小時|分鐘|倍|成|折|人|條|条|片|間|家|克|件|%)"
    r"|(?<![A-Za-z])[A-Z][A-Za-z0-9]+")
ZH_ASKS = [
    (re.compile(r"留言\s*(?:「[^」]{1,12}」|“[^”]{1,12}”|\+1|[A-Za-z0-9]{2,})"), "comment a keyword"),
    (re.compile(r"(?:私訊|私信|[Pp][Mm]|[Ii]nbox|DM|dm)\s*(?:我|小盒子)"), "DM me"),
    (re.compile(r"[Ww]hats[Aa]pp|WA我"), "message on WhatsApp"),
    (re.compile(r"收藏|先存|存起來|存起来|儲起|save低"), "save this"),
    (re.compile(r"分享給|分享给|轉發|转发|標記|标记|[Tt]ag\s*(?:你|一個|一个|朋友)"), "share this"),
    (re.compile(r"追蹤|關注|关注|[Ff]ollow\s*我"), "follow"),
    (re.compile(r"(?:連結|链接|[Ll]ink)\s*(?:在|喺)?\s*(?:個人|个人)?(?:簡介|简介|主頁|主页|[Bb]io)|[Bb]io\s*(?:有|link)|撳\s*bio|睇\s*[Bb]io"),
     "link in bio"),
    (re.compile(r"加\s*(?:入)?\s*LINE|加\s*[Ll]ine"), "add on LINE"),
    (re.compile(r"(?:往|向)?[左右]滑|滑到最後|滑到最后|碌到最尾"), "swipe or tap"),
    (re.compile(r"告訴我|告诉我|話我知|你會選|你会选|你揀|邊一個|哪一個|哪一个|你覺得呢|你觉得呢|你點睇"),
     "answer a question"),
]


def is_cjk(text):
    """Same rule as ig-reel/zh.py: two or more Han characters, and more than
    twice as many as Latin words. Copied so ig-caption runs on its own."""
    han = len(HAN_RE.findall(text))
    return han >= 2 and han > 2 * len(re.findall(r"[A-Za-z]+", text))


# With the rest of the pack installed, Chinese numbers, names and places come
# from ig-reel/zh.py so all the tools agree; on its own, the regex above.
try:
    import os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "ig-reel"))
    import zh as _zh
    ZH_CONCRETE_RE = re.compile("|".join(f"(?:{r.pattern})" for r in (_zh.NUMBER_RE, _zh.NAME_RE, _zh.PLACE_RE)))
except Exception:
    pass


def width(text):
    """Display width: a Chinese character takes the room of two Latin ones."""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def wrap_width(raw, limit):
    lines, cur = [], ""
    for ch in raw:
        if width(cur + ch) > limit:
            lines.append(cur)
            cur = ""
        cur += ch
    return lines + [cur]


def visible_window(text, cut, cjk=False):
    """What the feed shows. Instagram cuts mid-word, so this does too.
    Chinese is cut by width: the feed has room for about half as many Han
    characters as Latin ones."""
    flat = text.strip()
    if not cjk:
        return flat if len(flat) <= cut else flat[:cut]
    out = ""
    for ch in flat:
        if width(out + ch) > cut * 2:       # cut is in Chinese characters
            break
        out += ch
    return out


def render_box(window, truncated, out=sys.stdout, box=52):
    print("\n  WHAT THE FEED SHOWS", file=out)
    print("  +" + "-" * (box + 2) + "+", file=out)
    lines = []
    for raw in window.split("\n"):
        if is_cjk(raw):
            lines.extend(wrap_width(raw, box))
        else:
            lines.extend(textwrap.wrap(raw, box) or [""])
    for line in lines[:8]:
        if is_cjk(line):
            print(f"  | {line}{' ' * max(0, box - width(line))} |", file=out)
        else:
            print(f"  | {line:<{box}} |", file=out)
    tail = "... more" if truncated else "(whole caption fits)"
    print("  +" + "-" * (box + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)


def analyse(text, cut=None, keywords=None):
    text = text.rstrip()
    stripped = text.strip()
    chars = len(stripped)
    lines = [l for l in stripped.split("\n")]
    first_line = lines[0].strip() if lines else ""
    cjk = is_cjk(stripped)
    tags = (ZH_HASHTAG_RE if cjk else HASHTAG_RE).findall(stripped)
    mentions = MENTION_RE.findall(stripped)
    links = LINK_RE.findall(stripped)
    emoji = EMOJI_RE.findall(stripped)
    if cut is None:
        cut = ZH_TRUNCATE if cjk else TRUNCATE
    window = visible_window(stripped, cut, cjk)
    truncated = (width(stripped) > cut * 2) if cjk else chars > cut
    asks = [name for pattern, name in ASKS if pattern.search(stripped)]
    if cjk:
        asks += [name for pattern, name in ZH_ASKS if pattern.search(stripped) and name not in asks]
    filler = [t for t in tags if t.lower() in (FILLER_TAGS | ZH_FILLER_TAGS if cjk else FILLER_TAGS)]
    keywords = [k.strip() for k in (keywords or []) if k.strip()]

    checks = []

    def add(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    add("LENGTH", "FAIL" if chars > LIMIT else "PASS",
        f"{chars} / {LIMIT} characters" + (f", {chars - LIMIT} over the limit"
                                           if chars > LIMIT else ""))

    if not first_line:
        add("FIRST LINE", "FAIL", "the caption opens on a blank line")
    elif first_line.startswith("#") or first_line.startswith("@"):
        add("FIRST LINE", "FAIL",
            "opens on a hashtag or a mention, which is the one position worth a sentence")
    elif (width(first_line) > cut * 2) if cjk else len(first_line) > cut:
        add("FIRST LINE", "WARN",
            f"{len(first_line)} characters, so it gets cut at {len(window)} mid-thought. "
            "Fine if the cut is a cliffhanger, bad if it is a subordinate clause")
    else:
        add("FIRST LINE", "PASS", f"{len(first_line)} characters, lands whole")

    concrete = ZH_CONCRETE_RE if cjk else CONCRETE_RE
    add("HOOK IS CONCRETE", "PASS" if concrete.search(window) else "WARN",
        f"{len(concrete.findall(window))} number(s) or name(s) in the visible window"
        + ("" if concrete.search(window) else " - nothing checkable before the tap"))

    if len(tags) > HASHTAG_LIMIT:
        add("HASHTAGS", "FAIL", f"{len(tags)} tags, over Instagram's cap of {HASHTAG_LIMIT}. "
                                "Tags past the fifth do not count and the block reads as old")
    elif len(tags) == HASHTAG_LIMIT and filler:
        add("HASHTAGS", "WARN", f"{len(tags)} tags, at the cap, and "
                                f"{len(filler)} of them generic. Spend the five on topics")
    elif filler:
        add("HASHTAGS", "WARN", f"{len(tags)} tags, {len(filler)} of them generic "
                                f"({', '.join(filler[:3])}). Those describe nothing")
    else:
        add("HASHTAGS", "PASS", f"{len(tags)} tag(s)" + (f": {' '.join(tags)}" if tags else ""))

    if not tags:
        add("TAG PLACEMENT", "PASS", "no tags to place")
    elif any(re.search(r"(?:^|\s)" + re.escape(t) + r"\b", window) for t in tags):
        add("TAG PLACEMENT", "WARN", "a hashtag is inside the visible window, "
                                     "spending feed space on a label")
    else:
        add("TAG PLACEMENT", "PASS", "tags are below the fold")

    add("LINKS", "WARN" if links else "PASS",
        f"{len(links)} link(s) in the caption, and captions are not clickable. "
        f"Move it to the bio or the DM" if links else "no dead links in the body")

    if len(asks) == 1:
        add("ONE ASK", "PASS", f"one call to action: {asks[0]}")
    elif not asks:
        add("ONE ASK", "WARN", "no call to action. Decide what this post is for")
    else:
        add("ONE ASK", "WARN", f"{len(asks)} asks ({', '.join(asks)}). "
                               "Two asks is the same as none")

    density = len(emoji) * 100 / max(width(stripped) if cjk else chars, 1)
    add("EMOJI", "WARN" if density > 4 else "PASS",
        f"{len(emoji)} emoji, {density:.1f} per 100 characters"
        + (" - reads as decoration" if density > 4 else ""))

    if keywords:
        low = stripped.lower()
        found = [k for k in keywords if k.lower() in low]
        missing = [k for k in keywords if k.lower() not in low]
        in_window = [k for k in found if k.lower() in window.lower()]
        status = "PASS" if not missing else ("WARN" if found else "FAIL")
        add("SEARCH TERMS", status,
            f"{len(found)}/{len(keywords)} present"
            + (f", {len(in_window)} in the visible window" if found else "")
            + (f". Missing: {', '.join(missing)}" if missing else ""))

    fails = sum(1 for c in checks if c["status"] == "FAIL")
    warns = sum(1 for c in checks if c["status"] == "WARN")
    verdict = "FIX" if fails else ("REVIEW" if warns else "READY")

    return {
        "characters": chars, "limit": LIMIT, "truncate_at": cut,
        "visible": window, "truncated": truncated,
        "first_line_chars": len(first_line),
        "hashtags": tags, "mentions": mentions, "links": links,
        "emoji": len(emoji), "asks": asks,
        "checks": checks, "verdict": verdict,
    }


def render(a, out=sys.stdout):
    head = (f"CAPTION LINT  ·  {a['characters']} / {a['limit']} chars  ·  "
            f"{len(a['hashtags'])} hashtags  ·  {len(a['asks'])} ask(s)")
    print("\n" + head, file=out)
    print("=" * max(len(head), 62), file=out)
    render_box(a["visible"], a["truncated"], out=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {c['status']:<5} {c['check']:<17} {c['detail']}", file=out)
    print("-" * max(len(head), 62), file=out)
    print(f"  VERDICT  {a['verdict']}\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Lint an Instagram caption.")
    ap.add_argument("input", nargs="?", default="-", help="caption file, or - for stdin")
    ap.add_argument("--truncate", type=int, default=None,
                    help=f"characters shown before '... more' (default {TRUNCATE}; "
                         f"{ZH_TRUNCATE} for a Chinese caption)")
    ap.add_argument("--keywords", default="", help="comma-separated terms you want to be found for")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, cut=args.truncate, keywords=args.keywords.split(","))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0 if a["verdict"] == "READY" else 1)


if __name__ == "__main__":
    main()
