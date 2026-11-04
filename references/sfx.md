# Sound effects for a 2D Animation HyperFrames project

Reference for the `2d-animation-hyperframes` skill. `SKILL.md` says *where* SFX go ("in pauses, at
levels that do not mask speech") — this file covers *how* to obtain or make them and how to place
them in the composition.

## Two routes, same output

### Route A — retrieve (default, no synthesis)

`media-use` never generates audio. It resolves each named cue from Openverse (CC0/CC BY only) and
falls back to a bundled 21-file library. Its index is copied into this folder as
`sfx/media-use-sfx-manifest.json` (originally `audio/assets/sfx/manifest.json` inside the `media-use` skill):

```
chime, click, click-soft, error, glitch-1..3, impact-bass-1..2, key-press,
notification, ping, pop, riser, sparkle, typing, whoosh, whoosh-short, whoosh-cinematic
```

Use this when the effect is a named, generic sound. Offline, the manifest gives durations up front
(`riser` = 10.03 s), so cues can be timed without listening.

### Route B — synthesize with Python (custom / consistent set)

Use when the film needs a small, coherent family of soft effects that no stock library matches, or
when the project must stay offline / licence-free. Every generated file is CC0 by construction.

Minimal recipe: `numpy` for the waveform, stdlib `wave` for the container. 44.1 kHz, mono, 16-bit.

```python
import wave
import numpy as np

SR = 44100

def save(name, x, peak=0.7):
    x = x / (np.max(np.abs(x)) or 1) * peak
    with wave.open(name, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((x * 32767).astype("<i2").tobytes())

def sweep(f0, f1, dur, curve=1.0):          # pitch glide
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    f = f0 + (f1 - f0) * (t / dur) ** curve
    return np.sin(2 * np.pi * np.cumsum(f) / SR)

def decay(n, k=8.0):                        # simple exponential envelope
    t = np.linspace(0, 1, n)
    return np.clip(t / 0.005, 0, 1) * np.exp(-t * k)
```

Building blocks that cover most 2D explainer needs:

| Effect | Recipe | Length |
| --- | --- | --- |
| `pop` | sine sweep 1100 → 420 Hz, fast decay | 0.10–0.15 s |
| `boing` | sine with decaying pitch wobble (~5 Hz) | 0.4–0.6 s |
| `whoosh` | white noise × sin² envelope, band sweep 600 → 3000 Hz | 0.4–0.5 s |
| `chime` | 880 + 1320 Hz (plus 1760 Hz at 15 %) with exp decay | 1.2–1.5 s |
| `stamp` | 110 → 55 Hz thud + 45 Hz-decay noise crack | 0.3–0.4 s |
| `sparkle` | 4-note arpeggio 1318/1568/1976/2637 Hz, 90 ms apart | 0.7–0.9 s |
| `riser-soft` | rising sweep 220 → 880 Hz, amplitude ramp | 1.0–1.5 s |

Rules for synthesis:

- Seed any noise: `np.random.default_rng(7)` — regenerate identical files on every run.
- Normalise peak to 0.7 so every effect sits at the same loudness before `data-volume` scaling.
- Keep it under ~1.5 s except deliberate risers; short accents read as "UI", long ones mask speech.
- Save as `.wav` — no encoder dependency, exact duration known from the sample count.

## Wiring cues into HyperFrames

SFX are ordinary timed `<audio>` clips on the root composition. `data-start` is absolute seconds on
the root timeline; `data-duration` is the file length (a longer value is cut, a longer file is
trimmed).

```html
<audio id="sfx-pop-01" class="clip" src="assets/sfx/pop.wav"
       data-start="0.35" data-duration="0.14" data-track-index="3" data-volume="0.32"></audio>
```

In this kit the files sit in `references/sfx/`; copy them to the project's `assets/sfx/` so the paths
above resolve (`cp references/sfx/*.wav <project>/assets/sfx/`). `sfx/example-cues.html` uses the
project paths.

Non-negotiables, all enforced by `npm run check`:

1. Every `<audio>` needs a unique `id` (`media_missing_id`).
2. Keep `data-start + data-duration <= root data-duration` (`clip_ends_past_root_duration`).
3. Two audible clips on the same `data-track-index` must not overlap (`duplicate_audio_track`) —
   give simultaneous cues different indices.
4. `data-volume` around 0.22–0.38. Narration is 1.0; SFX must sit under it.

## Placement map used in `kenapa-jerapah-punya-leher-panjang`

| Time | Cue | Visual trigger |
| --- | --- | --- |
| 0.35 | pop | giraffe entrance |
| 3.58 | boing | whole-body stretch on "panjang sekali" |
| 5.52 | pop | question mark appears |
| 8.20 | whoosh | cut into the noodle gag |
| 11.18 | boing | neck stretch on "memanjang?" |
| 13.48 | stamp | red "BUKAN!" slam |
| 15.40 | chime | food leaves appear |
| 20.20 | whoosh | cut to the savanna explanation |
| 22.30 | sparkle | high leaves highlighted |
| 30.60 | chime | height measure line draws |
| 40.46 | pop | first vertebra pops in |
| 43.22 | stamp | "Hah?!" close-up |
| 45.30 | pop | bone-length bars |
| 47.44 | sparkle | "×7" stamp |
| 48.20 | riser-soft | build into the recap |
| 49.40 | sparkle | recap sparkles |
| 52.90 | whoosh | cut to the closing question |
| 57.40 | chime | "Terima kasih" end card |

Pattern: one accent per visual hit, never on every caption; transitions get whoosh, reveals get
pop/sparkle/chime, punchlines get stamp. Silence between cues is what makes them land.

## Files in `references/sfx/`

| File | Use |
| --- | --- |
| `sfx.py` | Working generator (`numpy` + `wave`). Run it to regenerate every effect identically |
| `*.wav` | The seven effects it produced — ready to drop into a project's `assets/sfx/` |
| `example-cues.html` | All 18 `<audio>` cue lines exactly as wired in the finished film |
| `media-use-sfx-manifest.json` | Copy of the stock-library manifest: names + durations + placement hints for the retrieve route |

Regenerate: `python sfx.py` — `OUT` at the top of the script writes next to it; point it at
`<project>/assets/sfx/` to write straight into a project. Or just copy the `.wav` files across.

## Checklist

- [ ] Cues generated or resolved into the project's `assets/sfx/`, all at consistent peak level
- [ ] Each cue has a matching visual hit within ±0.1 s
- [ ] No cue during a narration onset, none overlapping the music bed
- [ ] `npm run check` → 0 errors, no `clip_ends_past_root_duration` / `duplicate_audio_track`
- [ ] Rendered mix listened to: speech still clearly on top
