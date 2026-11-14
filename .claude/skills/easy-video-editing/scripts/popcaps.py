#!/usr/bin/env python3
"""Turn an .srt into pop-up captions (.ass) for a 1080x1920 reel: each line pops in, white text,
black outline, sits in the lower-middle (clear of the TikTok/IG buttons). Words listed in
--accent go yellow.  Usage: python3 popcaps.py in.srt out.ass [--accent "PLAN,500"] [--y 1340]"""
import argparse, re
ap = argparse.ArgumentParser()
ap.add_argument("srt"); ap.add_argument("ass")
ap.add_argument("--accent", default=""); ap.add_argument("--y", type=int, default=1340)
ap.add_argument("--font", default="Montserrat"); ap.add_argument("--size", type=int, default=78)
a = ap.parse_args()
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
Style: Pop,{a.font},{a.size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
out = [head]
for blk in re.split(r"\n\s*\n", open(a.srt, encoding="utf-8-sig").read().strip()):
    L = blk.splitlines()
    if len(L) < 3 or "-->" not in L[1]: continue
    s, e = [x.strip() for x in L[1].split("-->")]
    words = " ".join(L[2:]).upper().replace("{", "(").replace("}", ")").replace("\\", "/").split()
    txt = " ".join("{\\c&H00D2FF&}" + w + "{\\c&HFFFFFF&}" if re.sub(r"\W", "", w) in acc else w for w in words)
    pop = "{\\an5\\pos(540,%d)\\fscx70\\fscy70\\t(0,90,\\fscx108\\fscy108)\\t(90,160,\\fscx100\\fscy100)}" % a.y
    out.append(f"Dialogue: 0,{t2ass(s)},{t2ass(e)},Pop,,0,0,0,,{pop}{txt}\n")
open(a.ass, "w", encoding="utf-8").write("".join(out)); print("wrote", a.ass)
