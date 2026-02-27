"""Global configuration and constants for the missile trajectory tracker."""

import math

# ── Display ──────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "Missile Trajectory Tracker"

# ── Graph area (the plotting region inside the window) ───────────────────────
GRAPH_LEFT = 80           # left margin for Y-axis labels
GRAPH_TOP = 50            # top margin for title
GRAPH_RIGHT = SCREEN_WIDTH - 260   # right margin (telemetry panel)
GRAPH_BOTTOM = SCREEN_HEIGHT - 60  # bottom margin for X-axis labels
GRAPH_W = GRAPH_RIGHT - GRAPH_LEFT
GRAPH_H = GRAPH_BOTTOM - GRAPH_TOP

# ── World coordinate range (metres) ─────────────────────────────────────────
WORLD_X_MIN = 0.0
WORLD_X_MAX = 5000.0     # metres
WORLD_Y_MIN = 0.0
WORLD_Y_MAX = 3000.0     # metres (altitude)

# ── Grid ─────────────────────────────────────────────────────────────────────
GRID_X_STEP = 500        # metres between vertical grid lines
GRID_Y_STEP = 500        # metres between horizontal grid lines

# ── Colours (professional / muted palette) ───────────────────────────────────
BG = (18, 18, 24)
GRAPH_BG = (12, 12, 18)
GRID_COLOUR = (38, 38, 50)
GRID_COLOUR_MAJOR = (50, 50, 65)
AXIS_COLOUR = (120, 120, 140)
LABEL_COLOUR = (160, 160, 175)
TITLE_COLOUR = (200, 200, 215)
PANEL_BG = (22, 22, 30)
PANEL_BORDER = (50, 50, 65)

MISSILE_COLOUR = (230, 60, 60)       # red dot
MISSILE_TRAIL = (230, 60, 60)        # trajectory line
MISSILE_TRAIL_FADE = (80, 30, 30)    # faded old portion
TARGET_COLOUR = (60, 130, 255)       # blue dot
TARGET_RING = (60, 130, 255)
ORIGIN_COLOUR = (100, 200, 120)      # launch origin marker
VELOCITY_VEC = (255, 200, 80)        # velocity vector colour
IMPACT_COLOUR = (255, 180, 60)       # impact marker

TEXT_VALUE = (220, 220, 235)
TEXT_LABEL = (130, 130, 150)
TEXT_ACCENT = (80, 180, 255)
TEXT_WARN = (255, 100, 80)
TEXT_OK = (80, 220, 130)

# ── Physics ──────────────────────────────────────────────────────────────────
GRAVITY = 9.81            # m/s² (real-world)
AIR_DRAG = 0.0003         # drag coefficient

# ── Missile defaults ─────────────────────────────────────────────────────────
MISSILE_THRUST = 120.0    # m/s²
MISSILE_TURN_RATE = 2.0   # radians/s
MISSILE_MAX_SPEED = 800.0 # m/s
MISSILE_MIN_SPEED = 30.0
MISSILE_FUEL_TIME = 8.0   # seconds of thrust

# ── Launcher ─────────────────────────────────────────────────────────────────
LAUNCH_X = 200.0          # metres from origin
LAUNCH_Y = 0.0            # metres altitude (ground level)
LAUNCH_ANGLE = math.radians(55)   # 55° above horizontal
LAUNCH_SPEED = 180.0      # m/s initial

# ── Target ───────────────────────────────────────────────────────────────────
TARGET_RADIUS = 6         # screen pixels
DEFAULT_TARGET_X = 3800.0 # metres
DEFAULT_TARGET_Y = 200.0  # metres altitude

# ── Trail ────────────────────────────────────────────────────────────────────
TRAIL_DOT_INTERVAL = 0.05 # seconds between recorded trail points

# ── HUD / Telemetry panel ───────────────────────────────────────────────────
FONT_TITLE = 20
FONT_LABEL = 13
FONT_VALUE = 14
FONT_AXIS = 11
PANEL_X = GRAPH_RIGHT + 20
PANEL_Y = GRAPH_TOP
PANEL_W = SCREEN_WIDTH - PANEL_X - 16
PANEL_H = GRAPH_BOTTOM - GRAPH_TOP

# ── Ground ───────────────────────────────────────────────────────────────────
GROUND_Y = 0.0  # ground is at altitude 0 in world coords
