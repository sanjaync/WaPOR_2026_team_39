# Making the 60 second video

Everything visual is already done. `pitch_visuals_silent.mp4` is a finished
59 second 1080p track with no sound.

## The one command

Open Terminal, paste this, press enter:

```
bash ~/Desktop/Wapor_2026_hackathon/SUBMIT/01_pitch_video/make_video.sh
```

It writes `FINAL_pitch_video.mp4` into this folder.

If it stops and says ffmpeg is missing, install it once with `brew install ffmpeg`
and run the command again.

## If you would rather use your own voice

A human voice usually lands better with a jury than a synthetic one. Open
`OPEN_ME_teleprompter.html`, press space, and read along while you record. Save
the recording as `my_voice.m4a` in this folder, then run:

```
cd ~/Desktop/Wapor_2026_hackathon/SUBMIT/01_pitch_video
ffmpeg -i pitch_visuals_silent.mp4 -i my_voice.m4a -c:v copy -c:a aac -shortest FINAL_pitch_video.mp4
```

## What is on screen, and when

| Time | Picture | Line |
|---|---|---|
| 0:00 | the tool, beneficial fraction map | We thought Egypt's rice paddies wasted the most water. They waste the least. And that one measurement changes where a national budget should go. |
| 0:09 | driest countries chart, Egypt ringed | No country with over five million people has less freshwater of its own. |
| 0:14 | water stress bubbles, Egypt ringed | And the driest countries are the farming ones. |
| 0:18 | the mandate | Its Ministry of Water Resources and Irrigation spends a budget every year modernising farms, and has to justify every pound of it. |
| 0:26 | the challenge | But nothing tells it where. So the money spreads by cultivated area. |
| 0:31 | the alignment | The ministry already runs a WaPOR tool that shows where water productivity is low. It does not say where to spend. We add that step. |
| 0:40 | the tool, budget slider moving | WaPOR separates water that grew a crop from water that simply evaporated. We rank every governorate by how much is recoverable, and what it costs. Same budget, a quarter more water. |
| 0:53 | how it gets checked | And next season, the same satellite shows whether the money worked. |

## Do not put these in the pitch

Team names, countries or team number. The subtheme you selected. Next steps or
future work. Heavy technical detail. All four are excluded by the submission
rules, and the video above already avoids them.
