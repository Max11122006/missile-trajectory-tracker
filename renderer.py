"""Rendering helpers – scientific graph-style visualisation."""

from __future__ import annotations

import math
import pygame
import config as cfg
from missile import Missile
from target import Target


# ── coordinate transforms ────────────────────────────────────────────────────

def world_to_screen(wx: float, wy: float) -> tuple[int, int]:
    """Convert world coordinates (metres) to screen pixel coordinates.
    World: x = horizontal distance, y = altitude (up is positive).
    Screen: standard pygame (0,0 top-left, y increases downward).
    """
    sx = cfg.GRAPH_LEFT + (wx - cfg.WORLD_X_MIN) / (cfg.WORLD_X_MAX - cfg.WORLD_X_MIN) * cfg.GRAPH_W
    sy = cfg.GRAPH_BOTTOM - (wy - cfg.WORLD_Y_MIN) / (cfg.WORLD_Y_MAX - cfg.WORLD_Y_MIN) * cfg.GRAPH_H
    return (int(sx), int(sy))


def screen_to_world(sx: int, sy: int) -> tuple[float, float]:
    """Convert screen pixels back to world coordinates."""
    wx = cfg.WORLD_X_MIN + (sx - cfg.GRAPH_LEFT) / cfg.GRAPH_W * (cfg.WORLD_X_MAX - cfg.WORLD_X_MIN)
    wy = cfg.WORLD_Y_MIN + (cfg.GRAPH_BOTTOM - sy) / cfg.GRAPH_H * (cfg.WORLD_Y_MAX - cfg.WORLD_Y_MIN)
    return (wx, wy)


# ── background & grid ────────────────────────────────────────────────────────

def draw_background(surface: pygame.Surface):
    """Dark background with graph plotting area."""
    surface.fill(cfg.BG)
    pygame.draw.rect(surface, cfg.GRAPH_BG,
                     (cfg.GRAPH_LEFT, cfg.GRAPH_TOP, cfg.GRAPH_W, cfg.GRAPH_H))


def draw_grid(surface: pygame.Surface, axis_font: pygame.font.Font):
    """Draw coordinate grid lines with axis labels."""
    # ── vertical grid lines (X axis) ──
    x = cfg.WORLD_X_MIN
    while x <= cfg.WORLD_X_MAX:
        sx, _ = world_to_screen(x, 0)
        is_major = (x % (cfg.GRID_X_STEP * 2) == 0) or x == 0
        colour = cfg.GRID_COLOUR_MAJOR if is_major else cfg.GRID_COLOUR
        pygame.draw.line(surface, colour, (sx, cfg.GRAPH_TOP), (sx, cfg.GRAPH_BOTTOM), 1)
        label = axis_font.render(f"{int(x)}", True, cfg.LABEL_COLOUR)
        surface.blit(label, (sx - label.get_width() // 2, cfg.GRAPH_BOTTOM + 6))
        x += cfg.GRID_X_STEP

    # ── horizontal grid lines (Y axis / altitude) ──
    y = cfg.WORLD_Y_MIN
    while y <= cfg.WORLD_Y_MAX:
        _, sy = world_to_screen(0, y)
        is_major = (y % (cfg.GRID_Y_STEP * 2) == 0) or y == 0
        colour = cfg.GRID_COLOUR_MAJOR if is_major else cfg.GRID_COLOUR
        pygame.draw.line(surface, colour, (cfg.GRAPH_LEFT, sy), (cfg.GRAPH_RIGHT, sy), 1)
        label = axis_font.render(f"{int(y)}", True, cfg.LABEL_COLOUR)
        surface.blit(label, (cfg.GRAPH_LEFT - label.get_width() - 8, sy - label.get_height() // 2))
        y += cfg.GRID_Y_STEP

    # ── axes border ──
    pygame.draw.rect(surface, cfg.AXIS_COLOUR,
                     (cfg.GRAPH_LEFT, cfg.GRAPH_TOP, cfg.GRAPH_W, cfg.GRAPH_H), 1)

    # ── axis titles ──
    x_title = axis_font.render("Distance (m)", True, cfg.LABEL_COLOUR)
    surface.blit(x_title, (cfg.GRAPH_LEFT + cfg.GRAPH_W // 2 - x_title.get_width() // 2,
                            cfg.GRAPH_BOTTOM + 24))

    y_title = axis_font.render("Altitude (m)", True, cfg.LABEL_COLOUR)
    y_title_rot = pygame.transform.rotate(y_title, 90)
    surface.blit(y_title_rot, (cfg.GRAPH_LEFT - 60,
                                cfg.GRAPH_TOP + cfg.GRAPH_H // 2 - y_title_rot.get_height() // 2))


# ── ground line ──────────────────────────────────────────────────────────────

def draw_ground(surface: pygame.Surface):
    """Draw the ground level line at y=0."""
    _, gy = world_to_screen(0, 0)
    if cfg.GRAPH_TOP <= gy <= cfg.GRAPH_BOTTOM:
        pygame.draw.line(surface, (50, 70, 50),
                         (cfg.GRAPH_LEFT, gy), (cfg.GRAPH_RIGHT, gy), 2)


# ── origin / launch marker ──────────────────────────────────────────────────

def draw_origin(surface: pygame.Surface):
    """Small marker at the launch position."""
    sx, sy = world_to_screen(cfg.LAUNCH_X, cfg.LAUNCH_Y)
    pygame.draw.circle(surface, cfg.ORIGIN_COLOUR, (sx, sy), 5, 2)
    ang = cfg.LAUNCH_ANGLE
    length = 30
    ex = sx + math.cos(ang) * length
    ey = sy - math.sin(ang) * length
    pygame.draw.line(surface, cfg.ORIGIN_COLOUR, (sx, sy), (int(ex), int(ey)), 1)


# ── target ───────────────────────────────────────────────────────────────────

def draw_target(surface: pygame.Surface, target: Target, time: float):
    """Draw the target as a small blue dot with a subtle ring."""
    if not target.active:
        return
    sx, sy = world_to_screen(target.x, target.y)
    pygame.draw.circle(surface, cfg.TARGET_COLOUR, (sx, sy), cfg.TARGET_RADIUS)
    ring_r = cfg.TARGET_RADIUS + 5 + int(2 * math.sin(time * 2.5))
    pygame.draw.circle(surface, cfg.TARGET_RING, (sx, sy), ring_r, 1)

    label_font = pygame.font.SysFont("consolas", 11)
    coord_text = f"({target.x:.0f}, {target.y:.0f})"
    label = label_font.render(coord_text, True, cfg.TARGET_COLOUR)
    surface.blit(label, (sx + cfg.TARGET_RADIUS + 6, sy - 6))


# ── missile ──────────────────────────────────────────────────────────────────

def draw_missile(surface: pygame.Surface, m: Missile):
    """Draw the missile as a small red dot with a velocity vector."""
    if not m.alive:
        return
    sx, sy = world_to_screen(m.x, m.y)
    pygame.draw.circle(surface, cfg.MISSILE_COLOUR, (sx, sy), 5)
    # velocity vector
    scale = 0.15
    vx_s = m.vx * scale
    vy_s = -m.vy * scale  # invert for screen
    end_x = sx + vx_s
    end_y = sy + vy_s
    pygame.draw.line(surface, cfg.VELOCITY_VEC, (sx, sy), (int(end_x), int(end_y)), 1)


# ── trajectory ───────────────────────────────────────────────────────────────

def draw_trajectory(surface: pygame.Surface, history: list[tuple[float, float]]):
    """Draw the flight path as a gradient line on the graph."""
    n = len(history)
    if n < 2:
        return
    for i in range(1, n):
        t = i / n
        r = int(cfg.MISSILE_TRAIL_FADE[0] + (cfg.MISSILE_TRAIL[0] - cfg.MISSILE_TRAIL_FADE[0]) * t)
        g = int(cfg.MISSILE_TRAIL_FADE[1] + (cfg.MISSILE_TRAIL[1] - cfg.MISSILE_TRAIL_FADE[1]) * t)
        b = int(cfg.MISSILE_TRAIL_FADE[2] + (cfg.MISSILE_TRAIL[2] - cfg.MISSILE_TRAIL_FADE[2]) * t)
        p1 = world_to_screen(*history[i - 1])
        p2 = world_to_screen(*history[i])
        pygame.draw.line(surface, (r, g, b), p1, p2, 2 if t > 0.8 else 1)


# ── impact marker ────────────────────────────────────────────────────────────

def draw_impact(surface: pygame.Surface, m: Missile):
    """Draw an X at the impact point after the missile dies."""
    if m.alive:
        return
    sx, sy = world_to_screen(m.x, m.y)
    size = 8
    colour = cfg.TEXT_OK if m.reached_target else cfg.IMPACT_COLOUR
    pygame.draw.line(surface, colour, (sx - size, sy - size), (sx + size, sy + size), 2)
    pygame.draw.line(surface, colour, (sx - size, sy + size), (sx + size, sy - size), 2)

    font = pygame.font.SysFont("consolas", 11)
    status = "HIT" if m.reached_target else "IMPACT"
    label = font.render(f"{status} ({m.x:.0f}, {m.y:.0f})", True, colour)
    surface.blit(label, (sx + 12, sy - 6))


# ── title ────────────────────────────────────────────────────────────────────

def draw_title(surface: pygame.Surface, title_font: pygame.font.Font):
    """Draw the title above the graph."""
    title = title_font.render(cfg.TITLE, True, cfg.TITLE_COLOUR)
    surface.blit(title, (cfg.GRAPH_LEFT, cfg.GRAPH_TOP - 34))


# ── telemetry panel ──────────────────────────────────────────────────────────

def draw_panel(surface: pygame.Surface,
               label_font: pygame.font.Font,
               value_font: pygame.font.Font,
               missile: Missile | None,
               target: Target,
               missiles_fired: int,
               sim_time: float):
    """Draw the right-side telemetry data panel."""
    px = cfg.PANEL_X
    py = cfg.PANEL_Y
    pw = cfg.PANEL_W
    ph = cfg.PANEL_H

    pygame.draw.rect(surface, cfg.PANEL_BG, (px, py, pw, ph))
    pygame.draw.rect(surface, cfg.PANEL_BORDER, (px, py, pw, ph), 1)

    row_y = py + 14
    line_h = 22

    def _section(title: str):
        nonlocal row_y
        row_y += 6
        rendered = label_font.render(f"── {title} ──", True, cfg.TEXT_ACCENT)
        surface.blit(rendered, (px + 10, row_y))
        row_y += line_h

    def _row(label: str, value: str, colour=cfg.TEXT_VALUE):
        nonlocal row_y
        lbl = label_font.render(label, True, cfg.TEXT_LABEL)
        val = value_font.render(value, True, colour)
        surface.blit(lbl, (px + 12, row_y))
        surface.blit(val, (px + pw - val.get_width() - 12, row_y))
        row_y += line_h

    _section("SIMULATION")
    _row("Launches:", str(missiles_fired))
    _row("Sim Time:", f"{sim_time:.1f} s")

    _section("TARGET")
    _row("X:", f"{target.x:.0f} m")
    _row("Y:", f"{target.y:.0f} m")

    _section("MISSILE")
    if missile and missile.alive:
        spd = missile.velocity
        dist = math.hypot(missile.x - target.x, missile.y - target.y)
        fuel_pct = max(0, missile.fuel / cfg.MISSILE_FUEL_TIME * 100)
        angle_deg = math.degrees(missile.angle)

        _row("Position:", f"({missile.x:.0f}, {missile.y:.0f})")
        _row("Speed:", f"{spd:.1f} m/s")
        _row("Altitude:", f"{missile.y:.0f} m")
        _row("Heading:", f"{angle_deg:.1f}\u00b0")
        _row("Dist to Tgt:", f"{dist:.0f} m")
        _row("Fuel:", f"{fuel_pct:.0f}%",
             cfg.TEXT_WARN if fuel_pct < 20 else cfg.TEXT_VALUE)
        _row("Flight Time:", f"{missile.time_alive:.1f} s")

        _section("STATUS")
        if fuel_pct > 0:
            _row("Phase:", "GUIDED", cfg.TEXT_OK)
        else:
            _row("Phase:", "BALLISTIC", cfg.TEXT_WARN)

    elif missile and not missile.alive:
        _row("Position:", f"({missile.x:.0f}, {missile.y:.0f})")
        _row("Flight Time:", f"{missile.time_alive:.1f} s")
        _section("STATUS")
        if missile.reached_target:
            _row("Result:", "TARGET HIT", cfg.TEXT_OK)
        else:
            _row("Result:", "MISS", cfg.TEXT_WARN)
        dist = math.hypot(missile.x - target.x, missile.y - target.y)
        _row("Miss Dist:", f"{dist:.0f} m")
    else:
        _row("Status:", "AWAITING LAUNCH", cfg.TEXT_LABEL)

    # ── instructions at bottom of panel ──
    row_y = py + ph - 90
    _section("CONTROLS")
    inst_font = pygame.font.SysFont("consolas", 10)
    instructions = [
        "CLICK   Set target",
        "SPACE   Launch missile",
        "R       Reset",
        "ESC     Quit",
    ]
    for text in instructions:
        rendered = inst_font.render(text, True, cfg.TEXT_LABEL)
        surface.blit(rendered, (px + 14, row_y))
        row_y += 15
