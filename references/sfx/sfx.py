"""Synthesize small, soft SFX set for the giraffe film (44.1 kHz mono 16-bit WAV)."""
import os
import wave

import numpy as np

SR = 44100
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def env(n, attack=0.005, decay=0.9):
    t = np.linspace(0, 1, n)
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    return a * np.exp(-decay / max(t, 1e-6) * 0.0 + -decay * t * 6)


def adsr(n, a=0.005, d=0.35):
    t = np.linspace(0, 1, n)
    atk = np.clip(t / a, 0, 1)
    return atk * np.exp(-t / d)


def sweep(f0, f1, dur, curve=1.0):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    f = f0 + (f1 - f0) * (t / dur) ** curve
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase)


def noise(dur):
    return rng.standard_normal(int(SR * dur))


def norm(x, peak=0.7):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def save(name, x):
    os.makedirs(OUT, exist_ok=True)
    x = norm(x)
    data = (x * 32767).astype("<i2").tobytes()
    with wave.open(os.path.join(OUT, name), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(data)
    print(f"{name:14} {len(x) / SR:5.2f}s")


# pop: quick blip dropping in pitch
d = 0.14
save("pop.wav", sweep(1100, 420, d, 0.6) * adsr(int(SR * d), 0.004, 0.20))

# boing: playful wobble for the stretch
d = 0.55
n = int(SR * d)
t = np.linspace(0, d, n, endpoint=False)
f = 300 + 260 * np.sin(2 * np.pi * 5.5 * t) * np.exp(-t * 4) + 220 * (t / d)
boing = np.sin(2 * np.pi * np.cumsum(f) / SR) * adsr(n, 0.006, 0.16)
save("boing.wav", boing)

# whoosh: noise shaped by a moving band
d = 0.5
n = int(SR * d)
t = np.linspace(0, d, n, endpoint=False)
nz = noise(d) * (0.25 + 0.75 * np.sin(np.pi * t / d) ** 2)
band = np.sin(2 * np.pi * (600 + 2400 * (t / d) ** 1.6) * t)
save("whoosh.wav", nz * 0.55 + nz * band * 0.45)

# chime: two soft bells
d = 1.5
t = np.linspace(0, d, int(SR * d), endpoint=False)
ch = (np.sin(2 * np.pi * 880 * t) * 0.6 + np.sin(2 * np.pi * 1320 * t) * 0.35) * np.exp(-t * 2.6)
ch += np.sin(2 * np.pi * 1760 * t) * 0.15 * np.exp(-t * 4.2)
save("chime.wav", ch)

# stamp: low thud with a short noise crack
d = 0.4
n = int(SR * d)
t = np.linspace(0, d, n, endpoint=False)
low = np.sin(2 * np.pi * (110 - 55 * t / d) * t) * np.exp(-t * 11)
crack = noise(d) * np.exp(-t * 45) * 0.45
save("stamp.wav", low + crack)

# sparkle: quick rising arpeggio
d = 0.8
n = int(SR * d)
x = np.zeros(n)
for i, f in enumerate([1318, 1568, 1976, 2637]):
    s = int(SR * i * 0.09)
    seg = np.arange(n - s)
    tt = seg / SR
    x[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * 0.5
save("sparkle.wav", x)

# big-reveal: soft riser for the recap
d = 1.2
x = sweep(220, 880, d, 1.4) * np.linspace(0, 1, int(SR * d)) ** 1.5
save("riser-soft.wav", x)
