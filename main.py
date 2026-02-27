"""Ground-to-air intercept trajectory tracker – main loop."""

from __future__ import annotations

import sys
import pygame
import config as cfg
from camera import Camera
from aircraft import Aircraft
from missile import Missile
import renderer


class Simulation:
    """Manages state and runs the Pygame event loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(cfg.TITLE)
        self.clock = pygame.time.Clock()

        # fonts
        self.font_title = pygame.font.SysFont("consolas", cfg.FONT_TITLE, bold=True)
        self.font_label = pygame.font.SysFont("consolas", cfg.FONT_LABEL)
        self.font_value = pygame.font.SysFont("consolas", cfg.FONT_VALUE, bold=True)
        self.font_axis  = pygame.font.SysFont("consolas", cfg.FONT_AXIS)

        # camera
        self.cam = Camera()

        # sim objects
        self.aircraft = Aircraft()
        self.missile: Missile | None = None
        self.launches = 0
        self.sim_time = 0.0

        # mouse orbit
        self._dragging = False
        self._last_mouse = (0, 0)

    # ── reset ──────────────────────────────────────────────────────────
    def reset(self):
        self.aircraft = Aircraft()
        self.missile = None
        self.sim_time = 0.0

    # ── launch ─────────────────────────────────────────────────────────
    def launch(self):
        if self.missile is not None and self.missile.alive:
            return  # only one in flight at a time
        self.missile = Missile(self.aircraft.pos)
        self.launches += 1

    # ── event handling ─────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.launch()
                elif event.key == pygame.K_r:
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._dragging = True
                    self._last_mouse = event.pos
                elif event.button == 4:
                    self.cam.zoom(-cfg.CAM_ZOOM_SPEED)
                elif event.button == 5:
                    self.cam.zoom(cfg.CAM_ZOOM_SPEED)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self._dragging:
                    dx = event.pos[0] - self._last_mouse[0]
                    dy = event.pos[1] - self._last_mouse[1]
                    self.cam.orbit(
                        -dx * cfg.CAM_ROTATE_SPEED,
                         dy * cfg.CAM_ROTATE_SPEED,
                    )
                    self._last_mouse = event.pos
            elif event.type == pygame.MOUSEWHEEL:
                self.cam.zoom(-event.y * cfg.CAM_ZOOM_SPEED)
        return True

    # ── physics update ─────────────────────────────────────────────────
    def update(self, dt: float):
        self.sim_time += dt
        self.aircraft.update(dt)
        if self.missile and self.missile.alive:
            self.missile.update(dt, self.aircraft.pos, self.aircraft.velocity)

    # ── draw ───────────────────────────────────────────────────────────
    def draw(self):
        renderer.draw_background(self.screen)
        renderer.draw_grid(self.screen, self.cam)
        renderer.draw_axes(self.screen, self.cam, self.font_axis)
        renderer.draw_origin(self.screen, self.cam)

        # aircraft
        renderer.draw_aircraft_trail(self.screen, self.cam, self.aircraft.history)
        renderer.draw_aircraft(self.screen, self.cam, self.aircraft, self.font_label)

        # missile
        if self.missile:
            renderer.draw_missile_trail(self.screen, self.cam, self.missile.history)
            renderer.draw_missile(self.screen, self.cam, self.missile)
            renderer.draw_closing_line(self.screen, self.cam, self.missile, self.aircraft)
            renderer.draw_intercept(self.screen, self.cam, self.missile, self.font_label)

        renderer.draw_title(self.screen, self.font_title)
        renderer.draw_panel(
            self.screen, self.font_label, self.font_value,
            self.missile, self.aircraft,
            self.launches, self.sim_time, self.cam,
        )
        pygame.display.flip()

    # ── main loop ──────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 0.05)  # clamp to avoid spiral of death
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Simulation().run()
