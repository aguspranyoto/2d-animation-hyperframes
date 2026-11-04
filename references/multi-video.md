# Make the HyperFrames project reusable for many videos

Reference for the `2d-animation-hyperframes` skill. One workspace holds many videos: sources live in
`inputs/<slug>/`, and each video gets its own generated HyperFrames project under `videos/<slug>/`.

## Workspace layout

```
video-generator/                       # the workspace, not a HyperFrames project
├── inputs/<slug>/                     # source of truth: vo.mp3 + script.txt
├── videos/<slug>/                     # generated HyperFrames project (one per video)
│   ├── index.html                     # root composition: audio + bg + scene hosts
│   ├── compositions/                  # bg.html (shared look) + sNN.html scenes
│   └── assets/audio/                  # vo.mp3, script.txt, script.json, blocks.json, video.json
├── templates/                         # what the generator copies
│   ├── index.html                     # root skeleton with __SLUG__ / __DURATION__
│   ├── bg.html                        # savanna background, duration substituted
│   ├── package.json, hyperframes.json, CLAUDE.md, AGENTS.md
├── tools/
│   ├── new-video.py                   # generator
│   ├── transcribe.py                  # faster-whisper → word timings
│   └── blocks.py                      # aligns [emotion] blocks to those timings
└── references/visual-style/overall/   # approved style refs, shared by every video
```

Rules:

- **One HyperFrames project per video.** Never mount two videos' scenes in one project; they would
  share ids, the root duration, and the render.
- `inputs/<slug>/` is never edited by tooling. The generator only reads it.
- Shared visual references live at the workspace root, not per video. Pass the explicit path to the
  style step; do not copy 50 MB of images per video.

## Generator

```bash
python tools/new-video.py <slug>          # full: scaffold + transcribe + block map
python tools/new-video.py <slug> --force  # rebuild an existing videos/<slug>
python tools/new-video.py <slug> --no-transcribe   # scaffold only
```

Requires: `ffprobe` on PATH, and a Python with `faster-whisper` for transcription. That interpreter
is taken from `HF_PYTHON` (default `D:\hf-tools\venv\Scripts\python.exe`); set the env var on any
other machine:

```bash
HF_PYTHON=/path/to/venv/bin/python python tools/new-video.py <slug>
```

What it produces in `videos/<slug>/`:

| Output | Purpose |
| --- | --- |
| `index.html` | root composition: `vo.mp3`, `bg` host, root duration = audio duration |
| `compositions/bg.html` | the shared savanna background, parallax timeline stretched to the length |
| `assets/audio/script.json` | word-level timings |
| `assets/audio/blocks.json` | `[emotion]` blocks aligned to audio, with absolute start/end |
| `assets/audio/video.json` | slug, duration, block list — the machine-readable scene plan |
| `package.json`, `hyperframes.json`, `meta.json`, `CLAUDE.md`, `AGENTS.md` | project plumbing |

It then prints the scene plan:

```
duration: 58.75s   blocks: 12
  s01    0.00 ->   2.10  (local  0.00, dur  2.10)  [excited] Adik-adik, pernah nggak...
  s02    2.94 ->   8.06  (local  2.94, dur  5.12)  [curious] Wah, lehernya panjang sekali...
```

`local` is the block's offset inside its own scene file; caption `data-start` values are local to
the composition, so use that column, not the absolute one.

## After generating

1. `cd videos/<slug> && npx hyperframes preview --background`
2. Author `compositions/sNN.html`, one per beat group, following the animation skill:
   - scene root is `#root`, styles and script inside `<template>`
   - timeline key equals the host id and the file's `data-composition-id`
   - use `fromTo`, never `from` (seeking back drifts with `from`)
   - captions: `class="clip"` with local `data-start` / `data-duration`; animate a child `span`
3. Add a host in `index.html` for each scene:
   `data-start` = block start, `data-duration` = next block start − this start (last one ends at the
   video duration). Hosts should tile the timeline with no gaps.
4. `npm run check` → 0 errors, then look at frames with `npx hyperframes snapshot --at ...`.
5. `npm run render` when approved.

Optional: SFX cues go on the root as timed `<audio>` clips — see `sfx.md`.

## What is reusable, what is not

| Reusable | Per video |
| --- | --- |
| Workspace layout, generator, transcription + block alignment | Narration, voiceover |
| `templates/bg.html`, palette, caption styling, SFX bank | Scene art and animation |
| Root skeleton, lint contract, render settings | Block → scene grouping, cue timing |
| Style references at `references/visual-style/overall/` | Which beats get which visual gag |

Scene authoring stays creative work. The generator removes the mechanical part (scaffold, timing,
alignment, duration bookkeeping), not the direction.

## Checklist for a new video

- [ ] `inputs/<slug>/` contains `vo.mp3` and `script.txt` with `[emotion]` tags
- [ ] `python tools/new-video.py <slug>` prints a block for every tagged block
- [ ] `videos/<slug>/assets/audio/video.json` duration matches the MP3
- [ ] every block has a scene host; hosts tile `0 → duration` with no gaps or overlaps
- [ ] `npm run check` reports 0 errors
- [ ] the previous video still previews from its own folder (no shared ids, no shared assets)
