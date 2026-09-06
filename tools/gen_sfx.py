#!/usr/bin/env python3
"""Synthesises every sound effect of the game as 16-bit WAV files.

Pure Python (no numpy): a tiny synth with oscillators, envelopes, pitch
sweeps, a one-pole low-pass, echo and a bit-crusher, tuned for a chunky
synthwave-arcade flavour. Re-run after tweaking:  python3 tools/gen_sfx.py
"""
import math
import os
import random
import struct
import wave

RATE = 32000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "audio", "sfx")
random.seed(7)


def sine(t, f):
    return math.sin(2.0 * math.pi * f * t)


def square(t, f, duty=0.5):
    return 1.0 if (f * t) % 1.0 < duty else -1.0


def saw(t, f):
    return 2.0 * ((f * t) % 1.0) - 1.0


def tri(t, f):
    return 4.0 * abs(((f * t) % 1.0) - 0.5) - 1.0


def noise(_t=None, _f=None):
    return random.uniform(-1.0, 1.0)


def env(t, a, d, s, r, length):
    """ADSR in seconds; `length` is the note length before release."""
    if t < a:
        return t / a if a > 0 else 1.0
    if t < a + d:
        return 1.0 - (1.0 - s) * (t - a) / d if d > 0 else s
    if t < length:
        return s
    tail = t - length
    return max(0.0, s * (1.0 - tail / r)) if r > 0 else 0.0


def render(seconds, fn):
    n = int(seconds * RATE)
    return [fn(i / RATE) for i in range(n)]


def lowpass(samples, cutoff):
    out = []
    y = 0.0
    a = 1.0 - math.exp(-2.0 * math.pi * cutoff / RATE)
    for x in samples:
        y += a * (x - y)
        out.append(y)
    return out


def highpass(samples, cutoff):
    lp = lowpass(samples, cutoff)
    return [x - l for x, l in zip(samples, lp)]


def echo(samples, delay, gain, taps=3):
    out = list(samples) + [0.0] * int(delay * RATE * taps)
    d = int(delay * RATE)
    for k in range(1, taps + 1):
        g = gain ** k
        for i in range(len(samples)):
            j = i + d * k
            if j < len(out):
                out[j] += samples[i] * g
    return out


def crush(samples, bits=6, hold=3):
    q = float(2 ** (bits - 1))
    out = []
    last = 0.0
    for i, x in enumerate(samples):
        if i % hold == 0:
            last = math.floor(x * q) / q
        out.append(last)
    return out


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, x in enumerate(t):
            out[i] += x
    return out


def normalize(samples, peak=0.85):
    m = max(1e-6, max(abs(x) for x in samples))
    return [x / m * peak for x in samples]


def write(name, samples):
    samples = normalize(samples)
    # short fade in/out against clicks
    f = int(RATE * 0.004)
    for i in range(min(f, len(samples))):
        samples[i] *= i / f
        samples[-1 - i] *= i / f
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples))
    print("wrote", os.path.relpath(path, os.path.join(OUT, "..", "..", "..")), "%.2fs" % (len(samples) / RATE))


def sweep(f0, f1, seconds, osc=sine, curve=1.0):
    """Oscillator whose pitch glides from f0 to f1 (phase-continuous)."""
    n = int(seconds * RATE)
    out = []
    phase = 0.0
    for i in range(n):
        u = (i / n) ** curve
        f = f0 + (f1 - f0) * u
        phase += f / RATE
        out.append(osc(phase, 1.0))
    return out


def note_arp(freqs, step, osc=square, decay=0.35, gap=0.0):
    out = []
    for f in freqs:
        n = int(step * RATE)
        seg = [osc(i / RATE, f) * math.exp(-(i / RATE) / decay) for i in range(n)]
        out += seg + [0.0] * int(gap * RATE)
    return out


NOTE = lambda n: 440.0 * 2 ** ((n - 69) / 12.0)   # MIDI note number to Hz

# ---------------------------------------------------------------- sounds --
# coin: bright two-note ping with a sparkle tail
coin = mix(
    [x * env(t / RATE, 0.002, 0.08, 0.3, 0.12, 0.06) for t, x in enumerate(note_arp([NOTE(88), NOTE(95)], 0.07, square, 0.12))],
    [0.35 * sine(i / RATE, NOTE(100)) * math.exp(-(i / RATE) * 14.0) for i in range(int(0.3 * RATE))],
)
write("coin", echo(coin, 0.09, 0.25, 2))

# jump: quick rising chirp
jump = [x * env(i / RATE, 0.005, 0.05, 0.6, 0.06, 0.09) for i, x in enumerate(sweep(320.0, 980.0, 0.15, square, 0.7))]
write("jump", lowpass(jump, 3200))

# land: soft thud with a low knock
land = mix(
    lowpass([noise() * math.exp(-(i / RATE) * 45.0) for i in range(int(0.12 * RATE))], 900),
    [0.8 * sine(i / RATE, 75.0) * math.exp(-(i / RATE) * 28.0) for i in range(int(0.12 * RATE))],
)
write("land", land)

# step: a tiny tick for the run cycle (played with pitch variation)
step = lowpass([noise() * math.exp(-(i / RATE) * 160.0) for i in range(int(0.04 * RATE))], 1800)
write("step", mix(step, [0.5 * sine(i / RATE, 140.0) * math.exp(-(i / RATE) * 80.0) for i in range(int(0.04 * RATE))]))

# hit: shield takes a blow; zap down + crunch
hit = mix(
    [x * env(i / RATE, 0.002, 0.1, 0.3, 0.1, 0.12) for i, x in enumerate(sweep(900.0, 160.0, 0.22, saw, 1.4))],
    lowpass([0.6 * noise() * math.exp(-(i / RATE) * 22.0) for i in range(int(0.22 * RATE))], 2500),
)
write("hit", crush(hit, 7, 2))

# death: descending detuned arpeggio, bit-crushed, with echo
death = note_arp([NOTE(76), NOTE(72), NOTE(69), NOTE(64), NOTE(57)], 0.13, saw, 0.4)
death = mix(death, [0.5 * x for x in note_arp([NOTE(76.2), NOTE(72.2), NOTE(69.2), NOTE(64.2), NOTE(57.2)], 0.13, square, 0.4)])
write("death", echo(crush(lowpass(death, 3000), 6, 3), 0.16, 0.35, 3))

# explosion: noise burst that darkens, over a sub boom
boom_n = int(1.1 * RATE)
exp_noise = [noise() * math.exp(-(i / RATE) * 4.5) for i in range(boom_n)]
darkening = []
y = 0.0
for i, x in enumerate(exp_noise):
    cutoff = 6000.0 * math.exp(-(i / RATE) * 5.0) + 120.0
    a = 1.0 - math.exp(-2.0 * math.pi * cutoff / RATE)
    y += a * (x - y)
    darkening.append(y)
sub = [1.2 * x * math.exp(-(i / RATE) * 3.5) for i, x in enumerate(sweep(110.0, 38.0, 1.1, sine, 0.5))]
write("explosion", echo(mix(darkening, sub), 0.12, 0.3, 2))

# metal_bounce: inharmonic ping for bombs hitting the floor
partials = [(1.0, 1.0), (2.76, 0.5), (5.40, 0.25), (8.93, 0.12)]
bounce = [sum(a * sine(i / RATE, 520.0 * r) * math.exp(-(i / RATE) * (9.0 + 6.0 * r)) for r, a in partials) for i in range(int(0.35 * RATE))]
write("metal_bounce", bounce)

# shield pickups: rising chime (battery) and a bigger chord (core)
battery = note_arp([NOTE(79), NOTE(83), NOTE(86)], 0.09, tri, 0.25)
write("shield_battery_up", echo(battery, 0.1, 0.3, 2))
core = mix(
    note_arp([NOTE(72), NOTE(76), NOTE(79), NOTE(84)], 0.1, square, 0.5),
    [0.6 * x for x in note_arp([NOTE(60), NOTE(64), NOTE(67), NOTE(72)], 0.1, saw, 0.5)],
)
write("shield_core_up", echo(lowpass(core, 4000), 0.13, 0.35, 3))

# magnet: humming sweep that locks in
magnet = [x * env(i / RATE, 0.02, 0.1, 0.7, 0.15, 0.3) for i, x in enumerate(sweep(180.0, 520.0, 0.45, saw, 0.6))]
magnet = mix(magnet, [0.5 * x for x in sweep(181.5, 523.0, 0.45, square, 0.6)])
write("magnet_up", lowpass(magnet, 2200))

# doubler: sparkling upward arpeggio
doubler = note_arp([NOTE(84), NOTE(88), NOTE(91), NOTE(96), NOTE(100)], 0.06, sine, 0.3)
write("doubler_up", echo(mix(doubler, [0.4 * x for x in note_arp([NOTE(96), NOTE(100), NOTE(103), NOTE(108), NOTE(112)], 0.06, tri, 0.3)]), 0.08, 0.35, 3))

# crate: wooden crack then a coin shower
crack = lowpass([noise() * math.exp(-(i / RATE) * 60.0) for i in range(int(0.1 * RATE))], 1500)
shower = note_arp([NOTE(91), NOTE(95), NOTE(98), NOTE(103), NOTE(95), NOTE(103)], 0.05, square, 0.08, 0.01)
write("crate_open", mix(crack, [0.0] * int(0.06 * RATE) + [0.7 * x for x in shower]))

# start: power-on stab
start = mix(
    [x * env(i / RATE, 0.01, 0.15, 0.6, 0.25, 0.3) for i, x in enumerate(sweep(110.0, 220.0, 0.55, saw, 0.4))],
    [0.7 * x * env(i / RATE, 0.05, 0.15, 0.6, 0.25, 0.3) for i, x in enumerate(sweep(220.0, 440.0, 0.55, square, 0.4))],
    [0.5 * sine(i / RATE, NOTE(88)) * env(i / RATE, 0.15, 0.1, 0.5, 0.2, 0.35) for i in range(int(0.55 * RATE))],
)
write("start", echo(lowpass(start, 3500), 0.14, 0.3, 2))

# click: UI tick
click = [square(i / RATE, 1400.0) * math.exp(-(i / RATE) * 120.0) for i in range(int(0.05 * RATE))]
write("click", lowpass(click, 5000))

# bumper: springy boing (pitch dips then bounces back)
n = int(0.32 * RATE)
boing = []
phase = 0.0
for i in range(n):
    t = i / RATE
    f = 380.0 + 260.0 * math.exp(-t * 9.0) * math.cos(t * 55.0)
    phase += f / RATE
    boing.append((0.7 * square(phase, 1.0, 0.3) + 0.5 * sine(phase, 1.0)) * math.exp(-t * 8.0))
write("bumper", lowpass(boing, 4000))

# slot reels: ratchet clicks speeding up, then a jackpot arpeggio
spin = []
t = 0.0
gap = 0.14
while t < 1.25:
    tick = [tri(i / RATE, 900.0) * math.exp(-(i / RATE) * 200.0) for i in range(int(0.02 * RATE))]
    spin += tick + [0.0] * int(max(0.02, gap) * RATE)
    t += 0.02 + gap
    gap *= 0.92
write("slot_spin", lowpass(spin, 5000))
jackpot = note_arp([NOTE(72), NOTE(76), NOTE(79), NOTE(84), NOTE(79), NOTE(84), NOTE(88), NOTE(91)], 0.08, square, 0.3)
write("slot_win", echo(mix(jackpot, [0.4 * x for x in note_arp([NOTE(60), NOTE(64), NOTE(67), NOTE(72), NOTE(67), NOTE(72), NOTE(76), NOTE(79)], 0.08, saw, 0.3)]), 0.12, 0.35, 3))

# plasma shot: laser pew
pew = [x * env(i / RATE, 0.002, 0.06, 0.4, 0.08, 0.1) for i, x in enumerate(sweep(1600.0, 260.0, 0.2, square, 1.6))]
write("plasma", lowpass(pew, 5000))

# laser ring: short buzz when the beam switches on
buzz = mix(
    [x * env(i / RATE, 0.01, 0.05, 0.7, 0.1, 0.18) for i, x in enumerate(sweep(60.0, 90.0, 0.3, saw, 1.0))],
    [0.5 * square(i / RATE, 2400.0) * env(i / RATE, 0.01, 0.05, 0.4, 0.1, 0.18) for i in range(int(0.3 * RATE))],
)
write("laser_on", lowpass(buzz, 3000))

# fire: crackling whoosh
fire = highpass(lowpass([noise() * env(i / RATE, 0.05, 0.1, 0.8, 0.2, 0.35) for i in range(int(0.6 * RATE))], 2600), 300)
write("fire", fire)

# vault crack: heavy metal clang
clang = [sum(a * sine(i / RATE, 180.0 * r) * math.exp(-(i / RATE) * (3.0 + 2.5 * r)) for r, a in partials) for i in range(int(0.9 * RATE))]
write("vault_crack", echo(mix(clang, lowpass([0.8 * noise() * math.exp(-(i / RATE) * 30.0) for i in range(int(0.9 * RATE))], 1200)), 0.18, 0.3, 2))

# door: whoosh and a rising tone for the skybridge lobby
door = mix(
    lowpass([noise() * env(i / RATE, 0.15, 0.1, 0.6, 0.3, 0.35) for i in range(int(0.7 * RATE))], 1600),
    [0.6 * x * env(i / RATE, 0.1, 0.1, 0.7, 0.2, 0.45) for i, x in enumerate(sweep(220.0, 660.0, 0.7, tri, 0.8))],
)
write("door", echo(door, 0.15, 0.3, 2))

# steel hit: bomb blast dents a steel cell
dent = [sum(a * sine(i / RATE, 330.0 * r) * math.exp(-(i / RATE) * (12.0 + 8.0 * r)) for r, a in partials) for i in range(int(0.25 * RATE))]
write("steel_hit", dent)

# bat screech and heart grab
screech = [x * env(i / RATE, 0.02, 0.1, 0.6, 0.15, 0.3) for i, x in enumerate(sweep(1900.0, 1100.0, 0.45, saw, 1.0))]
screech = mix(screech, [0.5 * x for x in sweep(1930.0, 1130.0, 0.45, square, 1.0)])
write("bat", crush(lowpass(screech, 5000), 6, 2))
heart = note_arp([NOTE(67), NOTE(74), NOTE(79), NOTE(86)], 0.12, sine, 0.5)
write("heart", echo(mix(heart, [0.5 * x for x in note_arp([NOTE(55), NOTE(62), NOTE(67), NOTE(74)], 0.12, tri, 0.5)]), 0.2, 0.4, 3))

# menu open/close swoosh
swoosh = highpass(lowpass([noise() * env(i / RATE, 0.02, 0.05, 0.5, 0.1, 0.12) for i in range(int(0.25 * RATE))], 3000), 600)
write("swoosh", swoosh)
