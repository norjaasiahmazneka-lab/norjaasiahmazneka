#!/usr/bin/env python3
"""Turn an .srt into pop-up captions (.ass) for a 1080x1920 reel: each line pops in, white text,
black outline, sits in the lower-middle (clear of the TikTok/IG buttons). Words listed in
--accent go yellow. --look hand = handwriting style (Mali font, cream card, pink accent words).  Usage: python3 popcaps.py in.srt out.ass [--accent "PLAN,500"] [--y 1340]"""
import argparse, re
ap = argparse.ArgumentParser()
ap.add_argument("srt"); ap.add_argument("ass")
ap.add_argument("--accent", default=""); ap.add_argument("--y", type=int, default=1340)
ap.add_argument("--font", default=None); ap.add_argument("--size", type=int, default=None)
ap.add_argument("--look", default="pop", choices=["pop", "hand"],
                help="pop = white bold text, black outline; hand = handwriting (Mali), dark text on a cream card, pink accent")
ap.add_argument("--upper", default=None, choices=["yes", "no"], help="CAPITALS (default: yes for pop, no for hand)")
a = ap.parse_args()
HAND = a.look == "hand"
font = a.font or ("Mali" if HAND else "Montserrat"); size = a.size or (100 if HAND else 78)
upper = (a.upper or ("no" if HAND else "yes")) == "yes"
# colours are &HAABBGGRR. hand: dark brown text #2A1A1A on a cream box #FAEEE2, accent pink-red #D23C55
TXT, ACC = ("&H001A1A2A", "&H553CD2") if HAND else ("&H00FFFFFF", "&H00D2FF")
STYLE = (f"Pop,{font},{size},{TXT},{TXT},&H10E2EEFA,&H00000000,-1,0,0,0,100,100,0,0,3,18,0,5,80,80,0,1" if HAND
         else f"Pop,{font},{size},{TXT},{TXT},&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,5,80,80,0,1")
acc = {w.strip().upper() for w in a.accent.split(",") if w.strip()}
def t2ass(t):  # 00:00:01,520 -> 0:00:01.52
    h, m, s = t.replace(",", ".").split(":"); return f"{int(h)}:{m}:{float(s):05.2f}"
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: {STYLE}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
out = [head]
for blk in re.split(r"\n\s*\n", open(a.srt, encoding="utf-8-sig").read().strip()):
    L = blk.splitlines()
    if len(L) < 3 or "-->" not in L[1]: continue
    s, e = [x.strip() for x in L[1].split("-->")]
    words = " ".join(L[2:])
    words = (words.upper() if upper else words).replace("{", "(").replace("}", ")").replace("\\", "/").split()
    txt = " ".join("{\\c" + ACC + "&}" + w + "{\\c" + TXT[:2] + TXT[4:] + "&}" if re.sub(r"\W", "", w).upper() in acc else w for w in words)
    pop = "{\\an5\\pos(540,%d)\\fscx70\\fscy70\\t(0,90,\\fscx108\\fscy108)\\t(90,160,\\fscx100\\fscy100)}" % a.y
    out.append(f"Dialogue: 0,{t2ass(s)},{t2ass(e)},Pop,,0,0,0,,{pop}{txt}\n")
open(a.ass, "w", encoding="utf-8").write("".join(out)); print("wrote", a.ass)
