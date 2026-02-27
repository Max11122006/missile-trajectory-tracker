#!/usr/bin/env python3
"""Missile Trajectory Tracker – main entry point.

A physics-based missile tracking and trajectory visualisation system
rendered as a professional scientific graph.

Controls:
    LEFT CLICK   – Set / move target (click inside the graph area)
    SPACE        – Launch missile
    R            – Reset simulation
    ESC / Q      – Quit
"""

from __future__ import annotations

import sys

import pygame

import config as cfg
from missile import Missile
from target import Target
from renderer import (
    screen_to_world,
    draw_background,
    draw_grid,
    draw_ground,
    draw_origin,
    draw_target,
    draw_missile,
    draw_trajectory,
    draw_impact,
    draw_title,
    draw_panel,
)


class Simulation:
    """Top-level simulation state and loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption(cfg.TITLE)
        self.clock = pygame.time.Clock()

        # fonts
        self.title_font = pygame.font.SysFont("consolas", cfg.FONT_TITLE, bold=True)
        self.axis_font = pygame.font.SysFont("consolas", cfg.FONT_AXIS)
        self.label_font = pygame.font.SysFont("consolas", cfg.FONT_LABEL)
        self.value_font = pygame.font.SysFont("consolas", cfg.FONT_VALUE)

        self.sim_time = 0.0
        self.reset()

    def reset(self):
        """Reset the simulation state."""
        self.target = Target(cfg.DEFAULT_TARGET_X, cfg.DEFAULT_TARGET_Y)
        self.missile: Missile | None = None
        self.missiles_fired = 0
        self.sim_time = 0.0

    def launch(self):
        """Launch a new missile from the configured origin."""
        self.missile = Missile(
            cfg.LAUNCH_X, cfg.LAUNCH_Y,
            cfg.LAUNCH_ANGLE, cfg.LAUNCH_SPEED)
        self.missiles_fired += 1

    # ── events ────────────────────────────────────────────────────────────
    def handle_events(self) -> bool:
        """Process input. Returns False to quit."""
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
                # only accept clicks inside the graph area
                if (cfg.GRAPH_LEFT <= mx <= cfg.GRAPH_RIGHT
                        and cfg.GRAPH_TOP <= my <= cfg.GRAPH_BOTTOM):
                    wx, wy = screen_to_world(mx, my)
                    self.target.set(wx, wy)

        return True

    # ── update ────────────────────────────────────────────────────────────
    def update(self, dt: float):
        self.sim_time += dt
        self.target.update(dt)

        if self.missile and self.missile.alive:
            self.missile.update(dt, self.target.x, self.target.y)

    # ── draw ──────────────────────────────────────────────────────────────
    def draw(self):
        draw_background(self.screen)
        draw_grid(self.screen, self.axis_font)
        draw_ground(self.screen)
        draw_title(self.screen, self.title_font)
        draw_origin(self.screen)
        draw_target(self.screen, self.target, self.sim_time)

        if self.missile:
            draw_trajectory(self.screen, self.missile.history)
            draw_missile(self.screen, self.missile)
            draw_impact(self.screen, self.missile)

        draw_panel(self.screen, self.label_font, self.value_font,
                   self.missile, self.target,
                   self.missiles_fired, self.sim_time)

        pygame.display.flip()

    # ── main loop ─────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 0.05)  # cap delta time

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Simulation().run()
