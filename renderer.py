"""3-D graph renderer – light-mode, ground-to-air intercept visualisation."""

from __future__ import annotations

import math
import pygame
import config as cfg
from camera import Camera
from missile import Missile
from aircraft import Aircraft


# ═══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _in_view(sx: int, sy: int) -> bool:
    return 0 <= sx < cfg.PANEL_X and 0 <= sy < cfg.SCREEN_HEIGHT


def _line3d(surface, cam, p1, p2, colour, width=1):
    a = cam.project(*p1)
    b = cam.project(*p2)
    if a and b and _in_view(a[0], a[1]) and _in_view(b[0], b[1]):
        pygame.draw.line(surface, colour, (a[0], a[1]), (b[0], b[1]), width)


def _dot3d(surface, cam, pos, colour, radius=4):
    p = cam.project(*pos)
    if p and _in_view(p[0], p[1]):
        pygame.draw.circle(surface, colour, (p[0], p[1]), radius)
        return (p[0], p[1])
    return None


def _label3d(surface, cam, font, pos, text, colour):
    p = cam.project(*pos)
    if p and _in_view(p[0], p[1]):
        r = font.render(text, True, colour)
        surface.blit(r, (p[0] - r.get_width() // 2, p[1] - r.get_height() // 2))


# ═══════════════════════════════════════════════════════════════════════════════
#  Background
# ═══════════════════════════════════════════════════════════════════════════════

def draw_background(surface):
    surface.fill(cfg.BG)


# ═══════════════════════════════════════════════════════════════════════════════
#  Grid + Axes
# ═══════════════════════════════════════════════════════════════════════════════

def draw_grid(surface, cam):
    step = cfg.GRID_STEP
    xm, ym = cfg.GRID_EXTENT_X, cfg.GRID_EXTENT_Y

    x = 0
    while x <= xm:
        c = cfg.GRID_COLOUR_MAJOR if x % (step * 2) == 0 else cfg.GRID_COLOUR
        _line3d(surface, cam, (x, -ym, 0), (x, ym, 0), c)
        x += step

    y = -ym
    while y <= ym:
        c = cfg.GRID_COLOUR_MAJOR if abs(y) % (step * 2) == 0 else cfg.GRID_COLOUR
        _line3d(surface, cam, (0, y, 0), (xm, y, 0), c)
        y += step


def draw_axes(surface, cam, font):
    xl, yl, zl = cfg.WORLD_X_MAX, cfg.WORLD_Y_MAX, cfg.WORLD_Z_MAX

    _line3d(surface, cam, (0,0,0), (xl,0,0), cfg.AXIS_X_COLOUR, 2)
    _line3d(surface, cam, (0,-yl,0), (0,yl,0), cfg.AXIS_Y_COLOUR, 2)
    _line3d(surface, cam, (0,0,0), (0,0,zl), cfg.AXIS_Z_COLOUR, 2)

    _label3d(surface, cam, font, (xl+200, 0, 0), "X  Range (m)", cfg.AXIS_X_COLOUR)
    _label3d(surface, cam, font, (0, yl+200, 0), "Y  Lateral (m)", cfg.AXIS_Y_COLOUR)
    _label3d(surface, cam, font, (0, 0, zl+200), "Z  Altitude (m)", cfg.AXIS_Z_COLOUR)

    step = cfg.GRID_STEP
    x = step
    while x <= xl:
        _line3d(surface, cam, (x,0,0), (x,0,-50), cfg.AXIS_X_COLOUR)
        if x % (step * 2) == 0:
            _label3d(surface, cam, font, (x, 0, -120), str(int(x)), cfg.AXIS_LABEL)
        x += step

    z = step
    while z <= zl:
        _line3d(surface, cam, (0,0,z), (-50,0,z), cfg.AXIS_Z_COLOUR)
        if z % (step * 2) == 0:
            _label3d(surface, cam, font, (-180, 0, z), str(int(z)), cfg.AXIS_LABEL)
        z += step

    y = -yl
    while y <= yl:
        if y != 0:
            _line3d(surface, cam, (0,y,0), (0,y,-50), cfg.AXIS_Y_COLOUR)
            if abs(y) % (step * 2) == 0:
                _label3d(surface, cam, font, (0, y, -120), str(int(y)), cfg.AXIS_LABEL)
        y += step


# ═══════════════════════════════════════════════════════════════════════════════
#  Launch origin
# ═══════════════════════════════════════════════════════════════════════════════

def draw_origin(surface, cam):
    _dot3d(surface, cam, cfg.LAUNCH_POS, cfg.ORIGIN_COLOUR, 5)


# ═══════════════════════════════════════════════════════════════════════════════
#  Aircraft (target)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_aircraft(surface, cam, ac: Aircraft, font):
    if not ac.alive:
        return
    tx, ty, tz = ac.pos

    # ground shadow + drop-line
    sc = (cfg.SHADOW_COLOUR[0], cfg.SHADOW_COLOUR[1], cfg.SHADOW_COLOUR[2])
    _dot3d(surface, cam, (tx, ty, 0), sc, 3)
    _line3d(surface, cam, (tx, ty, 0), (tx, ty, tz), sc, 1)

    # aircraft dot
    p = cam.project(tx, ty, tz)
    if p and _in_view(p[0], p[1]):
        pygame.draw.circle(surface, cfg.AIRCRAFT_COLOUR, (p[0], p[1]), 7)
        pygame.draw.circle(surface, cfg.AIRCRAFT_COLOUR, (p[0], p[1]), 11, 1)
        label = font.render(f"AIRCRAFT ({tx:.0f}, {ty:.0f}, {tz:.0f})", True, cfg.AIRCRAFT_COLOUR)
        surface.blit(label, (p[0] + 14, p[1] - 6))

    # velocity vector
    sc2 = 1.5
    _line3d(surface, cam, (tx, ty, tz),
            (tx + ac.vx*sc2, ty + ac.vy*sc2, tz + ac.vz*sc2),
            cfg.AIRCRAFT_COLOUR, 1)


def draw_aircraft_trail(surface, cam, history):
    n = len(history)
    if n < 2:
        return
    step = max(1, n // 600)
    for i in range(step, n, step):
        t = i / n
        r = int(cfg.AIRCRAFT_TRAIL_FADE[0] + (cfg.AIRCRAFT_TRAIL[0] - cfg.AIRCRAFT_TRAIL_FADE[0]) * t)
        g = int(cfg.AIRCRAFT_TRAIL_FADE[1] + (cfg.AIRCRAFT_TRAIL[1] - cfg.AIRCRAFT_TRAIL_FADE[1]) * t)
        b = int(cfg.AIRCRAFT_TRAIL_FADE[2] + (cfg.AIRCRAFT_TRAIL[2] - cfg.AIRCRAFT_TRAIL_FADE[2]) * t)
        _line3d(surface, cam, history[i - step], history[i], (r, g, b), 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  Missile (interceptor)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_missile(surface, cam, m: Missile):
    if not m.alive:
        return
    p = cam.project(m.x, m.y, m.z)
    if not p or not _in_view(p[0], p[1]):
        return

    # ground shadow + drop-line
    sc = (cfg.SHADOW_COLOUR[0], cfg.SHADOW_COLOUR[1], cfg.SHADOW_COLOUR[2])
    _dot3d(surface, cam, (m.x, m.y, 0), sc, 2)
    _line3d(surface, cam, (m.x, m.y, 0), (m.x, m.y, m.z), sc, 1)

    # missile dot
    pygame.draw.circle(surface, cfg.MISSILE_COLOUR, (p[0], p[1]), 5)

    # velocity vector
    sc2 = 0.6
    tip = cam.project(m.x + m.vx*sc2, m.y + m.vy*sc2, m.z + m.vz*sc2)
    if tip and _in_view(tip[0], tip[1]):
        pygame.draw.line(surface, cfg.MISSILE_COLOUR, (p[0], p[1]), (tip[0], tip[1]), 1)


def draw_missile_trail(surface, cam, history):
    n = len(history)
    if n < 2:
        return
    step = max(1, n // 600)
    for i in range(step, n, step):
        t = i / n
        r = int(cfg.MISSILE_TRAIL_FADE[0] + (cfg.MISSILE_TRAIL[0] - cfg.MISSILE_TRAIL_FADE[0]) * t)
        g = int(cfg.MISSILE_TRAIL_FADE[1] + (cfg.MISSILE_TRAIL[1] - cfg.MISSILE_TRAIL_FADE[1]) * t)
        b = int(cfg.MISSILE_TRAIL_FADE[2] + (cfg.MISSILE_TRAIL[2] - cfg.MISSILE_TRAIL_FADE[2]) * t)
        _line3d(surface, cam, history[i - step], history[i], (r, g, b),
                2 if t > 0.85 else 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  Intercept / impact marker
# ═══════════════════════════════════════════════════════════════════════════════

def draw_intercept(surface, cam, m: Missile, font):
    if m.alive:
        return
    p = cam.project(m.x, m.y, m.z)
    if not p or not _in_view(p[0], p[1]):
        return
    sz = 9
    c = cfg.TEXT_OK if m.reached_target else cfg.INTERCEPT_COLOUR
    pygame.draw.line(surface, c, (p[0]-sz, p[1]-sz), (p[0]+sz, p[1]+sz), 2)
    pygame.draw.line(surface, c, (p[0]-sz, p[1]+sz), (p[0]+sz, p[1]-sz), 2)
    status = "INTERCEPT" if m.reached_target else "MISS"
    label = font.render(f"{status} ({m.x:.0f}, {m.y:.0f}, {m.z:.0f})", True, c)
    surface.blit(label, (p[0] + 14, p[1] - 6))


# ═══════════════════════════════════════════════════════════════════════════════
#  Closing line (missile → target)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_closing_line(surface, cam, m: Missile, ac: Aircraft):
    """Thin dashed line between missile and aircraft."""
    if not m.alive or not ac.alive:
        return
    a = cam.project(m.x, m.y, m.z)
    b = cam.project(ac.x, ac.y, ac.z)
    if a and b and _in_view(a[0], a[1]) and _in_view(b[0], b[1]):
        # draw dashed
        dx = b[0] - a[0]; dy = b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 2:
            return
        segments = max(1, int(length / 10))
        for i in range(0, segments, 2):
            t1 = i / segments
            t2 = min((i + 1) / segments, 1.0)
            x1 = int(a[0] + dx * t1); y1 = int(a[1] + dy * t1)
            x2 = int(a[0] + dx * t2); y2 = int(a[1] + dy * t2)
            pygame.draw.line(surface, cfg.PREDICTED_COLOUR, (x1, y1), (x2, y2), 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  Title
# ═══════════════════════════════════════════════════════════════════════════════

def draw_title(surface, font):
    title = font.render(cfg.TITLE, True, cfg.TITLE_COLOUR)
    surface.blit(title, (16, 10))


# ═══════════════════════════════════════════════════════════════════════════════
#  Telemetry panel
# ═══════════════════════════════════════════════════════════════════════════════

def draw_panel(surface, label_font, value_font,
               missile: Missile | None, ac: Aircraft,
               launches: int, sim_time: float, cam: Camera):
    px, py, pw, ph = cfg.PANEL_X, cfg.PANEL_Y, cfg.PANEL_W, cfg.PANEL_H

    pygame.draw.rect(surface, cfg.PANEL_BG, (px, py, pw, ph))
    pygame.draw.rect(surface, cfg.PANEL_BORDER, (px, py, pw, ph), 1)

    row_y = py + 10
    lh = 19

    def _sec(title):
        nonlocal row_y
        row_y += 4
        r = label_font.render(f"── {title} ──", True, cfg.TEXT_ACCENT)
        surface.blit(r, (px + 8, row_y))
        row_y += lh

    def _row(label, value, colour=cfg.TEXT_VALUE):
        nonlocal row_y
        l = label_font.render(label, True, cfg.TEXT_LABEL)
        v = value_font.render(value, True, colour)
        surface.blit(l, (px + 8, row_y))
        surface.blit(v, (px + pw - v.get_width() - 8, row_y))
        row_y += lh

    _sec("SIMULATION")
    _row("Launches:", str(launches))
    _row("Time:", f"{sim_time:.1f} s")

    _sec("AIRCRAFT")
    _row("Position:", f"({ac.x:.0f}, {ac.y:.0f}, {ac.z:.0f})")
    _row("Speed:", f"{ac.speed:.0f} m/s")
    _row("Altitude:", f"{ac.z:.0f} m")
    _row("Heading:", f"{math.degrees(ac.heading):.0f}\u00b0")

    _sec("INTERCEPTOR")
    if missile and missile.alive:
        spd = missile.speed
        dist = math.sqrt((missile.x - ac.x)**2 + (missile.y - ac.y)**2 + (missile.z - ac.z)**2)
        _row("Position:", f"({missile.x:.0f}, {missile.y:.0f}, {missile.z:.0f})")
        _row("Speed:", f"{spd:.0f} m/s")
        _row("Altitude:", f"{missile.z:.0f} m")
        _row("Heading:", f"{missile.heading_deg:.0f}\u00b0")
        _row("Climb:", f"{missile.climb_angle_deg:.1f}\u00b0")
        _row("Flight:", f"{missile.time_alive:.1f} s")
        _row("Dist to Tgt:", f"{dist:.0f} m")
        _sec("STATUS")
        _row("Phase:", "TRACKING", cfg.TEXT_ACCENT)
    elif missile and not missile.alive:
        _row("Position:", f"({missile.x:.0f}, {missile.y:.0f}, {missile.z:.0f})")
        _row("Flight:", f"{missile.time_alive:.1f} s")
        _sec("STATUS")
        if missile.reached_target:
            _row("Result:", "INTERCEPT", cfg.TEXT_OK)
        else:
            _row("Result:", "MISS", cfg.TEXT_WARN)
            dist = math.sqrt((missile.x - ac.x)**2 + (missile.y - ac.y)**2 + (missile.z - ac.z)**2)
            _row("Miss Dist:", f"{dist:.0f} m")
    else:
        _row("Status:", "AWAITING LAUNCH", cfg.TEXT_LABEL)

    _sec("CAMERA")
    _row("Azimuth:", f"{math.degrees(cam.azimuth):.0f}\u00b0")
    _row("Elevation:", f"{math.degrees(cam.elevation):.0f}\u00b0")
    _row("Zoom:", f"{cam.distance:.0f}")

    row_y = py + ph - 80
    _sec("CONTROLS")
    ifont = pygame.font.SysFont("consolas", 10)
    for text in [
        "SPACE    Launch interceptor",
        "R        Reset",
        "DRAG     Orbit camera",
        "SCROLL   Zoom",
        "ESC      Quit",
    ]:
        r = ifont.render(text, True, cfg.TEXT_LABEL)
        surface.blit(r, (px + 10, row_y))
        row_y += 13
