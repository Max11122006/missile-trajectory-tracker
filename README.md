# Missile Trajectory Tracker

A physics-based missile tracking and trajectory animation system built with **Python + Pygame**. Simulates guided missiles following target coordinates with real-time trajectory visualization, ballistic calculations, and interactive targeting controls.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Guided missile physics** – thrust, gravity, aerodynamic drag, and proportional-navigation guidance
- **Real-time trajectory rendering** – fading trail lines showing the full flight path
- **Particle effects** – smoke trails during thrust and explosions on impact
- **Interactive targeting** – click anywhere to place/move the target crosshair
- **HUD telemetry** – live speed, altitude, distance-to-target, fuel, and flight time
- **Fuel system** – missile flies guided while fuel lasts, then follows a ballistic arc

## Controls

| Key | Action |
|-----|--------|
| **Left Click** | Set / move target |
| **Space** | Launch missile |
| **R** | Reset simulation |
| **ESC / Q** | Quit |

## Getting Started

### Prerequisites

- Python 3.10+
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
├── main.py          # Entry point – game loop & event handling
├── missile.py       # Missile physics, guidance, and state
├── target.py        # Target placement and state
├── particles.py     # Particle system (smoke trails & explosions)
├── renderer.py      # All Pygame drawing / HUD rendering
├── config.py        # Constants (physics, display, colours)
├── requirements.txt
├── LICENSE
└── README.md
```

## Physics Model

The missile simulation uses:

- **Thrust** – constant forward acceleration along the missile heading while fuel remains
- **Gravity** – downward acceleration (150 px/s²)
- **Air drag** – quadratic drag opposing velocity
- **Guidance** – rate-limited steering toward the target (proportional navigation)
- **Ballistic phase** – once fuel is depleted, the missile follows a purely ballistic trajectory

## License

[MIT](LICENSE)
