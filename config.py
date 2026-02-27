"""Configuration for the ground-to-air interceptor trajectory tracker."""

import math

# ── Display ──────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 850
FPS = 60
TITLE = "Ground-to-Air Intercept Trajectory Tracker"

# ── Colours (light, professional) ────────────────────────────────────────────
BG = (245, 245, 248)
GRAPH_BG = (252, 252, 255)
GRID_COLOUR = (218, 218, 228)
GRID_COLOUR_MAJOR = (195, 195, 210)
AXIS_X_COLOUR = (190, 50, 50)
AXIS_Y_COLOUR = (40, 140, 40)
AXIS_Z_COLOUR = (50, 80, 190)
AXIS_LABEL = (90, 90, 105)

MISSILE_COLOUR = (210, 45, 45)
MISSILE_TRAIL = (210, 60, 60)
MISSILE_TRAIL_FADE = (230, 170, 170)
PREDICTED_COLOUR = (170, 170, 185)

AIRCRAFT_COLOUR = (30, 100, 220)
AIRCRAFT_TRAIL = (80, 140, 230)
AIRCRAFT_TRAIL_FADE = (185, 205, 235)

ORIGIN_COLOUR = (60, 160, 80)
INTERCEPT_COLOUR = (220, 140, 30)

# panel / text
PANEL_BG = (250, 250, 253)
PANEL_BORDER = (200, 200, 215)
TEXT_VALUE = (30, 30, 40)
TEXT_LABEL = (100, 100, 115)
TEXT_ACCENT = (30, 90, 200)
TEXT_OK = (30, 160, 70)
TEXT_WARN = (210, 60, 40)
TITLE_COLOUR = (40, 40, 55)
SHADOW_COLOUR = (200, 200, 210)

# ── 3-D World (metres) ──────────────────────────────────────────────────────
WORLD_X_MAX = 8000.0
WORLD_Y_MAX = 4000.0
WORLD_Z_MAX = 5000.0

GRID_STEP = 1000
GRID_EXTENT_X = 8000
GRID_EXTENT_Y = 4000

# ── Camera ───────────────────────────────────────────────────────────────────
CAM_DISTANCE = 12000.0
CAM_AZIMUTH = math.radians(-45)
CAM_ELEVATION = math.radians(22)
CAM_TARGET = (3500.0, 0.0, 1200.0)
CAM_ROTATE_SPEED = 0.005
CAM_ZOOM_SPEED = 300.0
CAM_MIN_DIST = 4000.0
CAM_MAX_DIST = 30000.0
FOV_FACTOR = 1100.0

# ── Physics ──────────────────────────────────────────────────────────────────
GRAVITY = 9.81
DRAG_MISSILE = 0.00008

# ── Interceptor missile ─────────────────────────────────────────────────────
LAUNCH_POS = (0.0, 0.0, 0.0)
MISSILE_ACCEL = 80.0        # m/s² thrust
MISSILE_MAX_SPEED = 900.0   # m/s
MISSILE_TURN_RATE = 2.5     # rad/s  – max angular steering rate
MISSILE_NAV_GAIN = 4.0      # proportional navigation constant (N)
HIT_RADIUS = 60.0           # metres

# ── Aircraft (target) ───────────────────────────────────────────────────────
AIRCRAFT_SPEED = 250.0           # m/s
AIRCRAFT_ALTITUDE = 2500.0       # m  – cruise altitude
AIRCRAFT_START = (7000.0, -3000.0, 2500.0)
AIRCRAFT_HEADING = math.radians(160)   # heading (into the area)
AIRCRAFT_TURN_RATE = 0.45        # rad/s – aggressive manoeuvring
AIRCRAFT_CLIMB_RATE = 0.30       # rad/s – climb/dive agility
AIRCRAFT_MANOEUVRE_PERIOD = 4.0  # seconds between direction changes
AIRCRAFT_MIN_ALT = 300.0        # floor altitude (m)
AIRCRAFT_MAX_ALT = 4500.0       # ceiling altitude (m)

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_TITLE = 20
FONT_LABEL = 13
FONT_VALUE = 14
FONT_AXIS = 11

# ── Panel ────────────────────────────────────────────────────────────────────
PANEL_X = SCREEN_WIDTH - 290
PANEL_Y = 12
PANEL_W = 274
PANEL_H = SCREEN_HEIGHT - 24
