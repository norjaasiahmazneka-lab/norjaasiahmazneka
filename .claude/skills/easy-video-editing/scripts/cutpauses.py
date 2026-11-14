#!/usr/bin/env python3
"""Jump-cut a talking-head clip: removes pauses longer than --min seconds.
Works on noisy audio too (uses the loudness floor, not a fixed dB like silencedetect).
Usage: python3 cutpauses.py in.mp4 out.mp4 [--min 0.35] [--pad 0.08]"""
import argparse, subprocess, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--min", type=float, default=0.35, help="shortest pause to cut (s)")
ap.add_argument("--pad", type=float, default=0.08, help="breathing room kept around speech (s)")
a = ap.parse_args()
R = 16000
pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.inp, "-vn", "-ac", "1", "-ar", str(R), "-f", "s16le", "-"],
                     capture_output=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
h = int(R * 0.02); n = len(x) // h
if n < 10: raise SystemExit("this video has no sound, so there are no pauses to find")
db = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
floor, speech = np.percentile(db, 10), np.percentile(db, 90)
quiet = db < floor + 0.35 * (speech - floor)
keep, i, dur = [], 0, n * 0.02
start = 0.0
while i < n:
    if quiet[i]:
        j = i
        while j < n and quiet[j]: j += 1
        if (j - i) * 0.02 >= a.min:
            keep.append((start, i * 0.02 + a.pad)); start = j * 0.02 - a.pad
        i = j
    else: i += 1
keep.append((start, dur))
keep = [(max(0, s), e) for s, e in keep if e - s > 0.15]
sel = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in keep)
# asetnsamples: cut audio in tiny 256-sample blocks so sound stays in sync with the picture after many cuts
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.inp,
    "-vf", f"select='{sel}',setpts=N/FRAME_RATE/TB",
    "-af", f"asetnsamples=n=256:p=0,aselect='{sel}',asetpts=N/SR/TB",
    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", a.out], check=True)
kept = sum(e - s for s, e in keep)
print(f"kept {len(keep)} pieces, {kept:.1f}s of {dur:.1f}s -> {a.out}")
