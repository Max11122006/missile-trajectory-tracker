"""Global configuration and constants for the missile trajectory tracker."""

import math

# ── Display ──────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Missile Trajectory Tracker"

# ── Colours ──────────────────────────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
DARK_GREY = (40, 40, 40)
RED = (220, 50, 50)
ORANGE = (255, 160, 40)
YELLOW = (255, 230, 60)
GREEN = (50, 200, 80)
CYAN = (80, 220, 255)
BLUE = (60, 120, 255)
DARK_BLUE = (15, 15, 40)
LIGHT_BLUE = (140, 180, 255)

# ── Physics ──────────────────────────────────────────────────────────────────
GRAVITY = 150.0          # pixels/s²  (downward)
AIR_DRAG = 0.02          # drag coefficient

# ── Missile defaults ─────────────────────────────────────────────────────────
MISSILE_THRUST = 420.0   # pixels/s²
MISSILE_TURN_RATE = 3.0  # radians/s  – how fast it can steer
MISSILE_MAX_SPEED = 600.0
MISSILE_MIN_SPEED = 80.0
MISSILE_LENGTH = 22
MISSILE_WIDTH = 5
MISSILE_FUEL_TIME = 6.0  # seconds of thrust

# ── Launcher ─────────────────────────────────────────────────────────────────
LAUNCHER_POS = (100, SCREEN_HEIGHT - 60)   # bottom‑left
LAUNCH_ANGLE = -math.pi / 4               # 45° upward (negative = up in screen coords)
LAUNCH_SPEED = 300.0

# ── Particles ────────────────────────────────────────────────────────────────
TRAIL_RATE = 80           # particles per second
TRAIL_LIFETIME = 1.2      # seconds
TRAIL_SIZE = 3
EXPLOSION_PARTICLES = 120
EXPLOSION_SPEED = 250.0
EXPLOSION_LIFETIME = 0.9

# ── Target ───────────────────────────────────────────────────────────────────
TARGET_RADIUS = 14
TARGET_RING_RADIUS = 22

# ── HUD ──────────────────────────────────────────────────────────────────────
HUD_FONT_SIZE = 16
HUD_PADDING = 12

# ── Ground ───────────────────────────────────────────────────────────────────
GROUND_Y = SCREEN_HEIGHT - 40
