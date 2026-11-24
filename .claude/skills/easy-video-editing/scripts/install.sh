#!/usr/bin/env bash
# Installs the video tools. Safe to run again; finishes in seconds if already installed.
set -e
PIP="pip install --break-system-packages -q"
command -v ffmpeg >/dev/null || { apt-get update -q && apt-get install -y -q ffmpeg; }
# fonts-montserrat needs a fresh package list, or it silently fails
fc-list | grep -qi montserrat || { apt-get update -q >/dev/null 2>&1; apt-get install -y -q fonts-montserrat >/dev/null 2>&1 || echo "Montserrat font skipped"; }
# faster-whisper = speech to text. av<19: newer PyAV breaks faster-whisper.  opencv<5: keeps the face detector file.
$PIP faster-whisper "av<19" "opencv-contrib-python-headless<5" numpy
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')" >/dev/null 2>&1 \
  && echo "Speech model ready" \
  || echo "SPEECH MODEL BLOCKED: allow the Hugging Face domains in the cloud environment"
# handwriting font (Mali) for --look hand, from npm (no extra websites needed)
if ! fc-list | grep -qi "Mali:style=Bold"; then
  T=$(mktemp -d); pip install --break-system-packages -q fonttools brotli >/dev/null 2>&1
  ( cd "$T" && npm pack -q @fontsource/mali >/dev/null 2>&1 && tar xzf fontsource-mali-*.tgz ) || true
  mkdir -p ~/.fonts
  for w in 400 700; do f="$T/package/files/mali-latin-$w-normal.woff2"
    [ -f "$f" ] && python3 -c "import sys;from fontTools.ttLib import TTFont;t=TTFont(sys.argv[1]);t.flavor=None;t.save(sys.argv[2])" "$f" ~/.fonts/Mali-$w.ttf; done
  fc-cache -f >/dev/null 2>&1; rm -rf "$T"
  fc-list | grep -qi mali && echo "Handwriting font ready" || echo "Handwriting font skipped"
fi
mkdir -p ~/easy-edit && cp "$(dirname "$0")"/*.py ~/easy-edit/
echo "Tools ready: $(ffmpeg -version | head -1 | cut -d' ' -f1-3)"
