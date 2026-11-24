---
name: easy-video-editing
description: Simple video editing for non-technical users - transcribe speech (English/Malay), add captions or pop-up captions, make a vertical 9:16 reel that follows the face, cut silent pauses, trim, join clips, add background music, speed up, shrink for WhatsApp, make a cover photo. Use when the person uploads a video or asks for any of these edits.
---

# Easy Video Editing

Talk to the person in simple words. Don't show commands unless they ask.

## 1. Install (once per session)

```bash
bash .claude/skills/easy-video-editing/scripts/install.sh
```
Run from the repository root. Copies the 4 scripts to `~/easy-edit/`. Safe to run again.

If it prints `SPEECH MODEL BLOCKED`, say: "Writing down speech needs the Hugging Face websites allowed in the cloud settings. Everything else works." (See the `video-cloud-setup` skill.)

## 2. Files

- Uploads in Claude Code land in `~/.claude/uploads/<session-id>/` (in claude.ai chat: `/mnt/user-data/uploads/`). Find them with `ls -t ~/.claude/uploads/*/ /mnt/user-data/uploads/ 2>/dev/null`.
- Work on a copy. Never change the original.
- Save results in an `output/` folder inside the working directory so the person can open them. Name them clearly (`reel-captions.mp4`).
- Videos are large: don't commit them to git unless asked.

## 3. Check your own work after every edit

```bash
ffmpeg -v error -y -i out.mp4 -vf "fps=1/3,scale=270:-1,tile=6x1" -frames:v 1 sheet.jpg   # look at it
ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 out.mp4
```
Reels: 1080x1920, H.264 + AAC, `-pix_fmt yuv420p`, `-movflags +faststart`.

## 4. Recipes

**Transcribe / captions file**
```bash
python3 ~/easy-edit/transcribe.py in.mp4 --lang en
python3 ~/easy-edit/transcribe.py in.mp4 --lang ms --model medium --prompt "names, brand words"   # Malay
```
Makes `in.srt` + `in_words.json`. Show the text; fix wrong names in the .srt by hand.

**Pop-up captions burned in** (video must be 1080x1920 - run facetrack or the blur recipe first)
```bash
python3 ~/easy-edit/popcaps.py in.srt caps.ass --accent "FREE,WEIGHT"
ffmpeg -i in.mp4 -vf "ass=caps.ass" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart out.mp4
```

**Handwriting captions** (upright, neat, natural - like a handwritten card: dark text on a cream box, accent words pink-red, normal capitals)
```bash
python3 ~/easy-edit/popcaps.py in.srt caps.ass --look hand --accent "wanita,berat,badan"
ffmpeg -i in.mp4 -vf "ass=caps.ass" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart out.mp4
```
Font is Mali Bold (installed by install.sh). Bigger/smaller: `--size 110`. All capitals: `--upper yes`.

**No speech in the video?** (walking, b-roll) Whisper may invent words like "Terima kasih kerana menonton". Check with `volumedetect` and the contact sheet; if nobody talks, write the .srt by hand from the person's own text, split into 2-3 short lines across the video.

**Plain captions burned in**
```bash
ffmpeg -i in.mp4 -vf "subtitles=in.srt:force_style='FontName=Montserrat,FontSize=14,Bold=1,Outline=2,MarginV=60'" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart out.mp4
```

**Vertical reel that follows the face** (~3 s of work per 1 s of video)
```bash
python3 ~/easy-edit/facetrack.py in.mp4 out.mp4      # calmer: --smooth 0.04, faster: --every 5
```
Follows the biggest face. No face found -> keeps the centre.

**Cut pauses**
```bash
python3 ~/easy-edit/cutpauses.py in.mp4 out.mp4 --min 0.35
```

**Trim** (keep 0:05 to 0:20)
```bash
ffmpeg -ss 00:00:05 -to 00:00:20 -i in.mp4 -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -movflags +faststart out.mp4
```

**Join clips** (re-encodes, so clips from different phones still join)
```bash
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart out.mp4
```
More clips: add inputs and `[v2][2:a]`, set `n=`. A clip with no sound needs a silent track (`-f lavfi -t DUR -i anullsrc=r=48000:cl=stereo`).

**9:16 with blurred background**
```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart out.mp4
```

**Music under the voice** (music ~15%, loops if short, fades out at the end)
```bash
ffmpeg -i in.mp4 -stream_loop -1 -i music.mp3 -filter_complex "[1:a]volume=0.15,afade=t=out:st=DUR-2:d=2[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -movflags +faststart out.mp4
```
Replace `DUR-2` with the number (video length from ffprobe minus 2). `normalize=0` keeps the voice at full volume. Only music the person owns or is royalty-free. Never put song lyrics on screen.

**Slow down** (0.65 = 35% slower, looks natural; 0.5 = 50%, dramatic slow-motion; 60 fps phone video stays smooth)
```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/0.65,fps=30[v];[0:a]atempo=0.65[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart out.mp4
```
Slow down first, then make captions, so caption times match.

**Speed up 1.2x**
```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/1.2[v];[0:a]atempo=1.2[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart out.mp4
```

**Smaller for WhatsApp** (longest side 1280, never upscales landscape)
```bash
ffmpeg -i in.mp4 -vf "scale=1280:1280:force_original_aspect_ratio=decrease:force_divisible_by=2" -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart small.mp4
```

**Cover photo**
```bash
ffmpeg -ss 00:00:03 -i in.mp4 -frames:v 1 -q:v 2 cover.jpg
```

## Rules
- Simple words. Captions in the lower middle (clear of TikTok/Instagram buttons).
- If something fails, say what failed in one line and try the next simplest way.
- Remind them: always watch the video before posting.
