#!/usr/bin/env python3
"""
detect.py - a five-check panel that scores how machine-written a draft looks.

What this is:  five local heuristics modelled on the signals public AI
detectors actually measure - sentence-length variation, concreteness, stock
vocabulary, typographic fingerprint, and voice. Every score is computed on
your machine from the text alone. Nothing is uploaded.

What this is NOT:  GPTZero, Originality, Copyleaks, Winston or Turnitin.
It does not call their APIs and it cannot promise their verdict. It catches
the things they all key on, which is why fixing them tends to move their
numbers too - but the only honest claim is the one on this line.

Each check returns a HUMAN score from 0 to 100. Higher is better.

Usage
  python3 detect.py draft.txt
  pbpaste | python3 detect.py -
  python3 detect.py draft.txt --json
  python3 detect.py before.txt after.txt      # compare two drafts
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-z']+")
CONTRACTIONS = re.compile(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE)
PRONOUNS = re.compile(r"\b(i|me|my|mine|we|us|our|you|your)\b", re.IGNORECASE)
NUMBERS = re.compile(r"\b\d[\d,.]*%?\b|\$\d")
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE)

# Chinese. Kept in this file so ig-human runs when copied on its own. One Han
# character is one unit; a Chinese word averages 1.6 characters, so densities
# measured per 100 words in English are taken per 160 characters here.
HAN = "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
HAN_RE = re.compile(f"[{HAN}]")
ZH_UNIT_RE = re.compile(f"[{HAN}]|[A-Za-z0-9][A-Za-z0-9'.,%$]*")
ZH_SENT_RE = re.compile(r"[^。！？!?\n]+[。！？!?]*")
ZH_NUMBERS = re.compile(
    r"[0-9０-９][0-9０-９,，.]*\s?[%％]?"
    r"|[兩两二三四五六七八九十百千萬万億亿半幾几][兩两二三四五六七八九十百千萬万億亿一]*"
    r"(?:萬|万|千|百|億|亿|元|塊|块|蚊|個|个|位|天|日|週|周|個月|月|年|小時|分鐘|倍|成|折|人|條|条|片|間|家|克|件|次|%)"
    r"|一(?:萬|万|千|百|億|亿|成|倍|折|半)")
ZH_NAMES = re.compile(r"(?<![A-Za-z])[A-Z][A-Za-z0-9]+")
# Sentence-final particles mark spoken Chinese, but written Chinese is the
# normal register for Hong Kong brand captions and Taiwan announcements, so
# their absence is not a machine tell. They are reported, not scored.
ZH_PARTICLES = re.compile("[啊吧呢喔哦欸誒啦嘛耶囉啰齁唷喎㗎呀咩啫喇吖咋]")
ZH_PRONOUNS = re.compile("我|你|妳|您|咱|佢")
ZH_PER = 1.6
# High-frequency characters whose Traditional form is not valid Simplified.
TRAD_RE = re.compile("[這們說會為時來對還個麼國過種樣點問題電發開關經應頭實學氣當進給讓]")


def is_cjk(text):
    """Same rule as ig-reel/zh.py: two or more Han characters, and more of
    twice as many as Latin words. Copied so ig-human runs on its own."""
    han = len(HAN_RE.findall(text))
    return han >= 2 and han > 2 * len(re.findall(r"[A-Za-z]+", text))


# With the rest of the pack installed, Chinese numbers and names come from
# ig-reel/zh.py so all the tools agree; on its own, the regexes above.
try:
    sys.path.insert(0, os.path.join(HERE, "..", "ig-reel"))
    import zh as _zh
    ZH_NUMBERS, ZH_NAMES = _zh.NUMBER_RE, _zh.NAME_RE
except Exception:
    pass


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Map value onto 0-100 where `human` -> 100 and `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


CJK = False   # set by run() from the text it is given


def sentences(text):
    if CJK:
        return [s.strip() for s in ZH_SENT_RE.findall(text) if len(ZH_UNIT_RE.findall(s)) > 4]
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def length(sentence):
    return len(ZH_UNIT_RE.findall(sentence)) if CJK else len(sentence.split())


def words(text):
    return ZH_UNIT_RE.findall(text) if CJK else WORD_RE.findall(text)


def per100(n, w):
    """Hits per 100 words, or per 160 Chinese characters."""
    return n * 100 / len(w) * (ZH_PER if CJK else 1)


def min_words():
    return 40 if CJK else 25


def check_burstiness(text):
    """Humans vary sentence length hard. Models write even."""
    lens = [length(s) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, "too short to judge"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, f"variation {cv:.2f} across {len(lens)} sentences (want 0.55+)"


def check_specificity(text):
    """Numbers, names and concrete nouns. Slop is abstract."""
    w = words(text)
    if len(w) < min_words():
        return 50.0, "too short to judge"
    if CJK:
        hits = (len([m for m in ZH_NUMBERS.finditer(text) if m.group(0).strip()])
                + len(set(ZH_NAMES.findall(text))))
    else:
        hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = per100(hits, w)
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} concrete markers, {density:.1f} per 100 words (want 4+)"


def check_slop(text, lex):
    """Stock vocabulary density against the lexicon."""
    w = words(text)
    if not w:
        return 50.0, "empty"
    hits, found = 0, []
    entries = lex.get("zh", {}).get("phrases", []) if CJK else lex["words"] + lex["phrases"]
    if CJK:   # longest first, and a match is used up so 全方位的 is not also 全方位.
        # Flag-only entries (旅程, 家人們) are ordinary words elsewhere: not counted.
        entries = sorted((e for e in entries if e["replace"] is not None),
                         key=lambda e: len(e["find"]), reverse=True)
        work = text
    for entry in entries:
        if CJK:   # no word boundaries in Chinese: plain substring
            n = work.count(entry["find"])
            work = work.replace(entry["find"], "\x00")
        else:
            pattern = re.compile(r"\b" + re.escape(entry["find"]).replace(r"\ ", r"\s+") + r"\b",
                                 re.IGNORECASE)
            n = len(pattern.findall(text))
        if n:
            hits += n
            found.append(entry["find"])
    density = per100(hits, w)
    score = scale(density, human=0.0, machine=4.0)
    detail = f"{hits} stock terms, {density:.1f} per 100 words"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Characters a phone keyboard does not produce."""
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "   ")
    if CJK:
        # ——, …… and “” are correct Chinese typography. What a phone keyboard
        # rarely produces is a run of dashes: count each —— once, at half
        # weight, and leave the quotes and ellipses alone.
        # A dash pair (—— or ──) is correct Chinese punctuation: only pairs
        # past two per caption, or one per 100 characters, count.
        pairs = text.count("——") + text.count("──")
        allowance = max(2, len(HAN_RE.findall(text)) // 100)
        em = max(0, pairs - allowance) * 0.5 + (text.count("—") - text.count("——") * 2)
        # Taiwan and Hong Kong quote with 「」; “” in Traditional text is the
        # Simplified-trained default. Half-width , . ? ! between two Han
        # characters is converted or pasted text. Both are mild tells.
        curly = sum(text.count(c) for c in "“”") * 0.5 if TRAD_RE.search(text) else 0
        curly += len(re.findall(f"[{HAN}][,.?!:;][{HAN}]", text))
        ellip = 0
        total = invisible * 4 + em * 2 + curly + nbsp
        # Chinese packs more into a character: judge per 1,000 characters of
        # at least a 200-character caption, so one mark in a short one is mild.
        per1k = total * 1000 / max(len(text), 200)
        detail = (f"{invisible} invisible, {em:g} em dash, {curly:g} curly quote, "
                  f"0 ellipsis, {nbsp} hard space")
        return scale(per1k, human=0.0, machine=12.0), detail
    total = invisible * 4 + em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisible, {em:g} em dash, {curly:g} curly quote, "
              f"{ellip} ellipsis, {nbsp} hard space")
    return score, detail


def check_voice(text, lex):
    """Contractions, person, and the shapes models default to."""
    w = words(text)
    if len(w) < min_words():
        return 50.0, "too short to judge"
    if CJK:
        contractions = per100(len(ZH_PARTICLES.findall(text)), w)   # reported only
        person = per100(len(ZH_PRONOUNS.findall(text)), w)
    else:
        contractions = per100(len(CONTRACTIONS.findall(text)), w)
        person = per100(len(PRONOUNS.findall(text)), w)
    tells = 0
    names = []
    for s in (lex.get("zh", {}).get("structures", []) if CJK else lex["structures"]):
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [length(b) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    if CJK:
        score = (scale(person, human=8.0, machine=1.0) * 0.5
                 + clamp(100 - tells * 22) * 0.5)
    else:
        score = (scale(contractions, human=3.0, machine=0.0) * 0.35
                 + scale(person, human=8.0, machine=1.0) * 0.35
                 + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("uniform-bullets")
    detail = (f"{contractions:.1f} {'particles' if CJK else 'contractions'}, {person:.1f} personal pronouns "
              f"per 100 words, {tells} structural tell(s)")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]


def run(text, lex):
    global CJK
    CJK = is_cjk(text)
    results = {}
    results["BURSTINESS"] = check_burstiness(text)
    results["SPECIFICITY"] = check_specificity(text)
    results["SLOP DENSITY"] = check_slop(text, lex)
    results["FINGERPRINT"] = check_fingerprint(text)
    results["VOICE"] = check_voice(text, lex)
    scores = [results[c][0] for c in CHECKS]
    # The weakest check drags the verdict: a detector only needs one signal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "PASS" if overall >= 70 and min(scores) >= 55 else (
        "REVIEW" if overall >= 50 else "FLAGGED")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "AI DETECTION PANEL" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'HUMAN SCORE':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "PASS":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Weakest signal: {weakest}. Fix that first.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Score how machine-written a draft looks.")
    ap.add_argument("input", nargs="?", default="-", help="file, or - for stdin")
    ap.add_argument("compare", nargs="?", help="second file, to show before/after")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=LEX)
    args = ap.parse_args()

    lex = json.load(open(args.lexicon, encoding="utf-8"))
    read = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex)
        payload.append({
            "source": name,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2,
                         ensure_ascii=not any(is_cjk(t) for _, t in targets)))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex)
        render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(f"  {a['human_score']:.1f} {a['verdict']}  ->  "
              f"{b['human_score']:.1f} {b['verdict']}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
