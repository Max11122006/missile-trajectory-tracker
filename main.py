#!/usr/bin/env python3
"""Missile Trajectory Tracker – main entry point.

A physics-based missile tracking and trajectory animation system.
Click to place a target, press SPACE to launch, and watch the guided
missile navigate with realistic physics.

Controls:
    LEFT CLICK   – Set / move target
    SPACE        – Launch missile
    R            – Reset simulation
    ESC / Q      – Quit
"""

from __future__ import annotations

import math
import random
import sys

import pygame

import config as cfg
from missile import Missile
from target import Target
from particles import ParticleSystem
from renderer import (
    draw_background,
    draw_stars,
    draw_launcher,
    draw_missile,
    draw_trajectory,
    draw_target,
    draw_particles,
    draw_hud,
)


def generate_stars(count: int = 200) -> list[tuple[int, int, int]]:
    """Pre-generate random starfield positions."""
    return [
        (random.randint(0, cfg.SCREEN_WIDTH),
         random.randint(0, cfg.GROUND_Y - 1),
         random.randint(120, 255))
        for _ in range(count)
    ]


class Game:
    """Top-level game state and loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption(cfg.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", cfg.HUD_FONT_SIZE)

        self.stars = generate_stars()
        self.reset()

    def reset(self):
        """Reset the simulation state."""
        self.target = Target(cfg.SCREEN_WIDTH * 0.75, cfg.GROUND_Y - 60)
        self.missile: Missile | None = None
        self.particles = ParticleSystem()
        self.missiles_fired = 0
        self.bg_cache: pygame.Surface | None = None

    def _cache_background(self):
        """Pre-render the static background to avoid per-frame gradient loops."""
        if self.bg_cache is None:
            self.bg_cache = pygame.Surface(
                (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
            draw_background(self.bg_cache)
            draw_stars(self.bg_cache, self.stars)

    def launch(self):
        """Launch a new missile from the launcher."""
        lx, ly = cfg.LAUNCHER_POS
        self.missile = Missile(lx, ly, cfg.LAUNCH_ANGLE, cfg.LAUNCH_SPEED)
        self.particles.clear()
        self.missiles_fired += 1

    # ── event handling ────────────────────────────────────────────────────
    def handle_events(self) -> bool:
        """Process input. Return False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if event.key == pygame.K_SPACE:
                    self.launch()
                if event.key == pygame.K_r:
                    self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.target.set(mx, my)
        return True

    # ── update ────────────────────────────────────────────────────────────
    def update(self, dt: float):
        self.target.update(dt)

        if self.missile and self.missile.alive:
            self.missile.update(dt, self.target.x, self.target.y)

            # emit trail particles while thrusting
            if self.missile.fuel > 0:
                self.particles.emit_trail(
                    self.missile.x, self.missile.y,
                    self.missile.angle, dt)

            # check if just died this frame
            if not self.missile.alive:
                self.particles.emit_explosion(
                    self.missile.x, self.missile.y,
                    hit=self.missile.reached_target)

        self.particles.update(dt)

    # ── draw ──────────────────────────────────────────────────────────────
    def draw(self):
        self._cache_background()
        self.screen.blit(self.bg_cache, (0, 0))

        draw_launcher(self.screen)
        draw_target(self.screen, self.target)

        if self.missile:
            draw_trajectory(self.screen, self.missile.history)
            draw_missile(self.screen, self.missile)

        draw_particles(self.screen, self.particles)
        draw_hud(self.screen, self.font, self.missile,
                 self.target, self.missiles_fired)

        pygame.display.flip()

    # ── main loop ─────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 0.05)  # cap delta to avoid spiral of death

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
