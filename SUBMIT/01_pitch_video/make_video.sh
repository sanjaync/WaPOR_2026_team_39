#!/bin/bash
# =============================================================================
#  Builds the finished 1 minute pitch video.
#
#  RUN THIS, and nothing else:
#      bash ~/Desktop/Wapor_2026_hackathon/make_video.sh
#
#  It generates the narration with Microsoft Edge neural text to speech, places
#  each line at the exact second its visual appears, and lays it over the silent
#  video. Output: FINAL_pitch_video.mp4 on your Desktop folder.
#
#  If you would rather use your own voice, see USING YOUR OWN VOICE at the end.
# =============================================================================
set -e
cd "$(dirname "$0")"

VOICE="en-GB-SoniaNeural"     # try en-US-AriaNeural or en-GB-RyanNeural for a change
SILENT="pitch_visuals_silent.mp4"
OUT="FINAL_pitch_video.mp4"

echo ""
echo "  Same Budget, More Water — building the pitch video"
echo "  ==============================================="

# ---------- 1. checks ---------------------------------------------------------
if [ ! -f "$SILENT" ]; then
  echo "  ✗ $SILENT is not in this folder. Put it here and run again."; exit 1
fi

PY=""
for c in python3 python; do command -v $c >/dev/null 2>&1 && PY=$c && break; done
if [ -z "$PY" ]; then
  echo "  ✗ No Python found. Install it from python.org, then run this again."; exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "  ✗ ffmpeg not found."
  echo "    Install it with:   brew install ffmpeg"
  echo "    (If you do not have brew: https://brew.sh )"; exit 1
fi

echo "  ✓ python and ffmpeg found"

# ---------- 2. text to speech engine -----------------------------------------
if ! $PY -c "import edge_tts" >/dev/null 2>&1; then
  echo "  · installing the speech engine, one moment ..."
  $PY -m pip install --quiet --user edge-tts || $PY -m pip install --quiet --break-system-packages edge-tts
fi
echo "  ✓ speech engine ready"

# ---------- 3. the script -----------------------------------------------------
# Each line is placed at a fixed second so it lands with its picture.
# Written to Edge TTS rules: no hyphens, no symbols, no markdown, plain text.
mkdir -p .vo && rm -f .vo/*.mp3

$PY - <<'PYEOF'
import asyncio, edge_tts, os
VOICE = os.environ.get("VOICE", "en-GB-SoniaNeural")
LINES = [
 ("01", "We thought Egypt's rice paddies wasted the most water. They waste the least. And that one measurement changes where a national budget should go."),
 ("02", "No country with over five million people has less freshwater of its own."),
 ("03", "And the driest countries are the farming ones."),
 ("04", "Its Ministry of Water Resources and Irrigation spends a budget every year modernising farms, and has to justify every pound of it."),
 ("05", "But nothing tells it where. So the money spreads by cultivated area."),
 ("06", "The ministry already runs a Wapor tool that shows where water productivity is low. It does not say where to spend. We add that step."),
 ("07", "Wapor separates water that grew a crop from water that simply evaporated. We rank every governorate by how much is recoverable, and what it costs. Same budget, a quarter more water."),
 ("08", "And next season, the same satellite shows whether the money worked."),
]
async def main():
    for tag, text in LINES:
        await edge_tts.Communicate(text, VOICE, rate="-4%").save(f".vo/{tag}.mp3")
        print(f"     line {tag} done")
asyncio.run(main())
PYEOF
echo "  ✓ narration generated"

# ---------- 4. place each line at its cue -------------------------------------
# cue times in milliseconds, matched to the picture cuts
CUES=(400 9300 14200 18300 26300 31300 40500 53400)
IN=""; FILTER=""; MIX=""
for i in "${!CUES[@]}"; do
  n=$(printf "%02d" $((i+1)))
  IN="$IN -i .vo/$n.mp3"
  FILTER="$FILTER[$i:a]adelay=${CUES[$i]}|${CUES[$i]}[a$i];"
  MIX="$MIX[a$i]"
done
ffmpeg -v error -y $IN -filter_complex "${FILTER}${MIX}amix=inputs=${#CUES[@]}:normalize=0[out]" \
  -map "[out]" -ar 48000 .vo/voice.wav
echo "  ✓ narration timed to the picture"

# ---------- 5. mux ------------------------------------------------------------
# -apad pads the narration with silence so the closing shot is not cut short;
# -shortest then trims to the video length rather than the audio length.
ffmpeg -v error -y -i "$SILENT" -i .vo/voice.wav \
  -c:v copy -c:a aac -b:a 192k -af apad -shortest "$OUT"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | cut -d. -f1)
echo ""
echo "  ✓ DONE  ->  $(pwd)/$OUT   (${DUR} seconds)"
echo ""
echo "  Watch it before you submit. If a line runs over its picture, open this"
echo "  file and change rate=\"-4%\" to rate=\"-8%\" to slow the voice down."
echo ""

# =============================================================================
#  USING YOUR OWN VOICE INSTEAD
#  Record yourself reading the script while watching the silent video, save it
#  as my_voice.m4a in this folder, then run:
#
#    ffmpeg -i pitch_visuals_silent.mp4 -i my_voice.m4a -c:v copy -c:a aac \
#           -shortest FINAL_pitch_video.mp4
# =============================================================================
