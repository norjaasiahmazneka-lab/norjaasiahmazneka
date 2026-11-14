#!/usr/bin/env python3
"""Face tracking: turn any video (e.g. landscape 16:9) into a 9:16 reel that follows the speaker's face.
The crop moves smoothly (no shaking). Keeps the original sound.
Usage: python3 facetrack.py in.mp4 out.mp4 [--smooth 0.08] [--every 3]"""
import argparse, subprocess, cv2, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--smooth", type=float, default=0.08, help="lower = slower, calmer camera (0.02-0.3)")
ap.add_argument("--every", type=int, default=3, help="look for the face every N frames (speed)")
a = ap.parse_args()

def frames():  # yields frames already rotated like the phone showed them
    cap = cv2.VideoCapture(a.inp)
    while True:
        ok, fr = cap.read()
        if not ok: break
        yield fr
    cap.release()

cap = cv2.VideoCapture(a.inp); fps = cap.get(cv2.CAP_PROP_FPS) or 30; cap.release()
first_fr = next(frames(), None)
if first_fr is None: raise SystemExit("could not read the video")
H, W = first_fr.shape[:2]   # real size after rotation (CAP_PROP_FRAME_WIDTH can ignore phone rotation)
cw = min(W, int(H * 9 / 16)) // 2 * 2; ch = min(H, int(cw * 16 / 9)) // 2 * 2   # 9:16 crop size
face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# pass 1: where is the face (centre x,y) on sampled frames
xs, tx, ty, first = [], W / 2, H / 2, None
for i, fr in enumerate(frames()):
    if i % a.every == 0:
        g = cv2.cvtColor(cv2.resize(fr, (W // 2, H // 2)), cv2.COLOR_BGR2GRAY)
        f = face.detectMultiScale(g, 1.1, 6, minSize=(40, 40))
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])   # biggest face = speaker
            tx, ty = (x + w / 2) * 2, (y + h / 2) * 2
            if first is None: first = len(xs)
    xs.append((tx, ty))

# smooth the camera path both ways so it glides instead of jumping
p = np.array(xs, float)
if first: p[:first] = p[first]          # start on the face, not the middle
if first is None: print("no face found: keeping the centre")
for k in range(1, len(p)): p[k] = p[k - 1] + a.smooth * (p[k] - p[k - 1])             # forward
for k in range(len(p) - 2, -1, -1): p[k] = p[k + 1] + a.smooth * (p[k] - p[k + 1])    # backward
p[:, 0] = np.clip(p[:, 0] - cw / 2, 0, W - cw); p[:, 1] = np.clip(p[:, 1] - ch * 0.4, 0, H - ch)

# pass 2: crop each frame, scale to 1080x1920, add the original audio back
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
    "-s", "1080x1920", "-r", str(fps), "-i", "-", "-i", a.inp, "-map", "0:v", "-map", "1:a?",
    "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "-shortest", a.out], stdin=subprocess.PIPE)
k = 0
for fr in frames():
    x, y = p[min(k, len(p) - 1)].astype(int)
    enc.stdin.write(cv2.resize(fr[y:y + ch, x:x + cw], (1080, 1920), interpolation=cv2.INTER_AREA).tobytes()); k += 1
enc.stdin.close()
if enc.wait(): raise SystemExit("ffmpeg failed while saving the reel")
print(f"{k} frames, crop {cw}x{ch} following the face -> {a.out}")
