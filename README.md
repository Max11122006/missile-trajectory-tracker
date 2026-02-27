# Missile Trajectory Tracker

A **ground-to-air intercept** simulation rendered in a **3-D graph space** using **Python + Pygame**. A guided interceptor missile tracks and attempts to intercept a manoeuvring aircraft using **proportional navigation** guidance.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **3-D graph space** – X (range), Y (lateral), Z (altitude) axes with grid and labels
- **Moving aircraft target** – flies through the airspace with random heading and altitude changes
- **Guided interceptor** – proportional navigation (PN) steers the missile toward the aircraft
- **Orbiting camera** – click-drag to rotate, scroll to zoom
- **Trail rendering** – fading 3-D paths for both aircraft and missile with ground shadows
- **Closing line** – dashed line between missile and target during pursuit
- **Telemetry panel** – live aircraft & missile telemetry, intercept status, camera info
- **Light mode** – clean, professional light colour palette

## Controls

| Key | Action |
|-----|--------|
| **Space** | Launch interceptor |
| **R** | Reset simulation |
| **Left Drag** | Orbit camera |
| **Scroll** | Zoom in / out |
| **ESC** | Quit |

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/Max11122006/missile-trajectory-tracker.git
cd missile-trajectory-tracker
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

## Project Structure

```
missile-trajectory-tracker/
├── main.py          # Entry point – simulation loop & input handling
├── missile.py       # Guided interceptor – proportional navigation
├── aircraft.py      # Moving aircraft target with manoeuvres
├── camera.py        # Orbiting camera & perspective projection
├── renderer.py      # 3-D graph rendering – axes, grid, trails, panel
├── config.py        # Constants (physics, display, colours, camera)
├── requirements.txt
├── LICENSE
└── README.md
```

## Physics Model

Ground-to-air intercept in 3-D space:

- **Aircraft** – constant-speed target with periodic heading and altitude manoeuvres
- **Interceptor** – thrust-accelerated missile with gravity and quadratic drag
- **Proportional navigation** – guidance law steers via line-of-sight rate × closing velocity
- **Hit detection** – intercept when missile comes within 60 m of the aircraft
- **3-D coordinates** – X (forward range), Y (lateral), Z (altitude) in metres

## License

[MIT](LICENSE)
