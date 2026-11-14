#!/usr/bin/env python3
"""Transcribe a video/audio file -> .srt (captions) + _words.json (word timings).
Usage: python3 transcribe.py VIDEO [--lang en|ms] [--model small|medium] [--prompt "names, terms"]"""
import argparse, json, os
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--lang", default="en", help="language actually spoken: en or ms")
ap.add_argument("--model", default="small", help="small = fast; medium = better for Malay")
ap.add_argument("--prompt", default=None, help="spelling hints: names, brands, terms")
ap.add_argument("--maxwords", type=int, default=4, help="max words per caption line")
a = ap.parse_args()

model = WhisperModel(a.model, device="cpu", compute_type="int8")
segs, info = model.transcribe(a.video, language=a.lang, word_timestamps=True,
                              vad_filter=True, initial_prompt=a.prompt)
words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
         for s in segs for w in (s.words or []) if w.word.strip()]

def ts(t):  # round once to whole ms, then split (avoids 1.9996 -> 00:00:01,000)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# group words into short caption chunks (break on punctuation, pauses, or maxwords)
cues, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    gap = words[i + 1]["s"] - w["e"] if i + 1 < len(words) else 9
    if len(cur) >= a.maxwords or w["w"][-1:] in ".,?!" or gap > 0.4:
        cues.append(cur); cur = []
if cur: cues.append(cur)

base = os.path.splitext(a.video)[0]
with open(base + ".srt", "w", encoding="utf-8") as f:
    for n, c in enumerate(cues, 1):
        nxt = cues[n][0]["s"] if n < len(cues) else 1e9
        end = min(max(c[-1]["e"], c[0]["s"] + 0.8), nxt)  # hold short lines ~0.8 s, never overlap
        f.write(f"{n}\n{ts(c[0]['s'])} --> {ts(end)}\n{' '.join(x['w'] for x in c)}\n\n")
with open(base + "_words.json", "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False, indent=0)
print(f"{len(words)} words, {len(cues)} captions -> {base}.srt")
if not words: print("no speech found (check --lang, or the video has no talking)")
