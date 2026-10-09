# Chishti Bro Neon Racer - High Level PC Edition

## GitHub structure

```text
repository/
├── neon_racer.py
└── .github/
    └── workflows/
        └── build-exe.yml
```

## Local install

```bash
py -m pip install pygame pyttsx3
```

## Run

```bash
py neon_racer.py
```

## Controls

A / LEFT = move left
D / RIGHT = move right
SPACE = boost
SHIFT = extra boost
P = pause
R = restart after crash
F11 = fullscreen
ESC = quit

## Voice

Voice announcements use pyttsx3. If pyttsx3 is unavailable, the game remains playable.

## GitHub

Go to Actions -> Build Chishti Bro Neon Racer -> Run workflow.

The workflow builds a Windows EXE and uploads both the EXE package and ZIP artifact.
