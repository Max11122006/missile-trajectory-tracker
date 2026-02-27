"""Rendering helpers – draws all visual elements onto the Pygame surface."""

from __future__ import annotations

import math
import pygame
import config as cfg
from missile import Missile
from target import Target
from particles import ParticleSystem


def draw_background(surface: pygame.Surface):
    """Gradient sky + ground."""
    # Sky gradient (top → horizon)
    for y in range(cfg.GROUND_Y):
        t = y / cfg.GROUND_Y
        r = int(cfg.DARK_BLUE[0] * (1 - t) + 30 * t)
        g = int(cfg.DARK_BLUE[1] * (1 - t) + 30 * t)
        b = int(cfg.DARK_BLUE[2] * (1 - t) + 60 * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (cfg.SCREEN_WIDTH, y))

    # Ground
    pygame.draw.rect(surface, (30, 70, 30),
                     (0, cfg.GROUND_Y, cfg.SCREEN_WIDTH,
                      cfg.SCREEN_HEIGHT - cfg.GROUND_Y))
    pygame.draw.line(surface, (50, 110, 50),
                     (0, cfg.GROUND_Y), (cfg.SCREEN_WIDTH, cfg.GROUND_Y), 2)


def draw_stars(surface: pygame.Surface, stars: list[tuple[int, int, int]]):
    """Draw pre-generated starfield."""
    for sx, sy, brightness in stars:
        if sy < cfg.GROUND_Y:
            colour = (brightness, brightness, brightness)
            surface.set_at((sx, sy), colour)


def draw_launcher(surface: pygame.Surface):
    """Draw the missile launcher at the bottom-left."""
    lx, ly = cfg.LAUNCHER_POS
    # base
    pygame.draw.rect(surface, cfg.GREY, (lx - 15, ly - 5, 30, 20))
    # barrel
    end_x = lx + math.cos(cfg.LAUNCH_ANGLE) * 35
    end_y = ly + math.sin(cfg.LAUNCH_ANGLE) * 35
    pygame.draw.line(surface, cfg.WHITE, (lx, ly), (end_x, end_y), 4)
    # platform
    pygame.draw.rect(surface, cfg.DARK_GREY, (lx - 20, ly + 10, 40, 8))


def draw_missile(surface: pygame.Surface, m: Missile):
    """Draw the missile body as a rotated shape."""
    if not m.alive:
        return

    cos_a = math.cos(m.angle)
    sin_a = math.sin(m.angle)
    L = cfg.MISSILE_LENGTH
    W = cfg.MISSILE_WIDTH

    # nose
    nose = (m.x + cos_a * L, m.y + sin_a * L)
    # left / right tail
    perp_x, perp_y = -sin_a, cos_a
    tail_l = (m.x - cos_a * L * 0.3 + perp_x * W,
              m.y - sin_a * L * 0.3 + perp_y * W)
    tail_r = (m.x - cos_a * L * 0.3 - perp_x * W,
              m.y - sin_a * L * 0.3 - perp_y * W)

    # body
    pygame.draw.polygon(surface, cfg.WHITE, [nose, tail_l, tail_r])

    # flame when thrusting
    if m.fuel > 0:
        flame_len = 10 + 6 * math.sin(m.time_alive * 30)
        flame_tip = (m.x - cos_a * (L * 0.3 + flame_len),
                     m.y - sin_a * (L * 0.3 + flame_len))
        pygame.draw.polygon(surface, cfg.ORANGE,
                            [tail_l, tail_r, flame_tip])


def draw_trajectory(surface: pygame.Surface, history: list[tuple[float, float]]):
    """Draw the trajectory path as a fading line."""
    n = len(history)
    if n < 2:
        return
    for i in range(1, n):
        t = i / n
        alpha = int(180 * t)
        colour = (alpha, alpha // 2, alpha // 4)
        pygame.draw.line(surface, colour, history[i - 1], history[i], 1)


def draw_target(surface: pygame.Surface, target: Target):
    """Draw the target crosshair."""
    if not target.active:
        return
    x, y = int(target.x), int(target.y)
    pulse = 1.0 + 0.2 * math.sin(target.pulse)
    r1 = int(cfg.TARGET_RADIUS * pulse)
    r2 = int(cfg.TARGET_RING_RADIUS * pulse)

    pygame.draw.circle(surface, cfg.RED, (x, y), r2, 2)
    pygame.draw.circle(surface, cfg.RED, (x, y), r1, 2)
    # crosshair lines
    gap = r1 - 3
    line_len = r2 + 6
    pygame.draw.line(surface, cfg.RED, (x - line_len, y), (x - gap, y), 1)
    pygame.draw.line(surface, cfg.RED, (x + gap, y), (x + line_len, y), 1)
    pygame.draw.line(surface, cfg.RED, (x, y - line_len), (x, y - gap), 1)
    pygame.draw.line(surface, cfg.RED, (x, y + gap), (x, y + line_len), 1)


def draw_particles(surface: pygame.Surface, psys: ParticleSystem):
    """Draw all particles with alpha fade."""
    for p in psys.particles:
        alpha = p.alpha
        r = int(p.colour[0] * alpha)
        g = int(p.colour[1] * alpha)
        b = int(p.colour[2] * alpha)
        size = max(1, int(p.size * alpha))
        pygame.draw.circle(surface, (r, g, b), (int(p.x), int(p.y)), size)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font,
             missile: Missile | None, target: Target, missiles_fired: int):
    """Draw the heads-up display with telemetry."""
    pad = cfg.HUD_PADDING
    y = pad
    lines: list[str] = []

    lines.append(f"Missiles Fired: {missiles_fired}")

    if missile and missile.alive:
        spd = missile.velocity
        alt = missile.altitude
        dist = math.hypot(missile.x - target.x, missile.y - target.y)
        fuel_pct = max(0, missile.fuel / cfg.MISSILE_FUEL_TIME * 100)
        lines.append(f"Speed: {spd:.0f} px/s")
        lines.append(f"Altitude: {alt:.0f} px")
        lines.append(f"Distance to Target: {dist:.0f} px")
        lines.append(f"Fuel: {fuel_pct:.0f}%")
        lines.append(f"Time: {missile.time_alive:.1f}s")
    elif missile and not missile.alive:
        if missile.reached_target:
            lines.append("STATUS: TARGET HIT!")
        else:
            lines.append("STATUS: MISSILE LOST")

    for i, text in enumerate(lines):
        rendered = font.render(text, True, cfg.CYAN)
        surface.blit(rendered, (pad, y + i * (cfg.HUD_FONT_SIZE + 4)))

    # Instructions at bottom
    instructions = [
        "LEFT CLICK: Set target  |  SPACE: Launch missile  |  R: Reset  |  ESC: Quit"
    ]
    for i, text in enumerate(instructions):
        rendered = font.render(text, True, cfg.LIGHT_BLUE)
        rect = rendered.get_rect(centerx=cfg.SCREEN_WIDTH // 2,
                                 y=cfg.SCREEN_HEIGHT - 28 + i * 18)
        surface.blit(rendered, rect)
