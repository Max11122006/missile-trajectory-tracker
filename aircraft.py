"""Aircraft target – flies aggressively through full 3-D space."""

from __future__ import annotations

import math
import random
import config as cfg


class Aircraft:
    """A manoeuvring aircraft that uses the full 3-D volume."""

    def __init__(self):
        sx, sy, sz = cfg.AIRCRAFT_START
        self.x = sx
        self.y = sy
        self.z = sz
        self.speed = cfg.AIRCRAFT_SPEED
        self.heading = cfg.AIRCRAFT_HEADING      # horizontal heading (rad)
        self.climb = 0.0                          # climb angle (rad)
        self.alive = True

        # manoeuvre state
        self._turn_target = self.heading
        self._climb_target = 0.0
        self._manoeuvre_timer = random.uniform(0, 2)  # stagger first manoeuvre
        self._speed_target = self.speed

        self.history: list[tuple[float, float, float]] = [(self.x, self.y, self.z)]

    @property
    def pos(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def vx(self) -> float:
        return self.speed * math.cos(self.climb) * math.cos(self.heading)

    @property
    def vy(self) -> float:
        return self.speed * math.cos(self.climb) * math.sin(self.heading)

    @property
    def vz(self) -> float:
        return self.speed * math.sin(self.climb)

    @property
    def velocity(self) -> tuple[float, float, float]:
        return (self.vx, self.vy, self.vz)

    def _pick_manoeuvre(self):
        """Choose a new random heading, climb, and speed target."""
        # big heading changes – up to ±120°
        self._turn_target = self.heading + random.uniform(-2.1, 2.1)

        # dramatic climb / dive – up to ±30°
        self._climb_target = random.uniform(math.radians(-30), math.radians(30))

        # vary speed ±30 %
        self._speed_target = cfg.AIRCRAFT_SPEED * random.uniform(0.7, 1.3)

        # randomise next manoeuvre interval (2–6 s)
        self._manoeuvre_timer = -random.uniform(0, cfg.AIRCRAFT_MANOEUVRE_PERIOD * 0.5)

    def update(self, dt: float):
        if not self.alive:
            return

        # periodic manoeuvre changes
        self._manoeuvre_timer += dt
        if self._manoeuvre_timer >= cfg.AIRCRAFT_MANOEUVRE_PERIOD:
            self._manoeuvre_timer = 0.0
            self._pick_manoeuvre()

        # ── steer heading ────────────────────────────────────────────
        turn_rate = cfg.AIRCRAFT_TURN_RATE * dt
        h_diff = (self._turn_target - self.heading + math.pi) % (2 * math.pi) - math.pi
        self.heading += max(-turn_rate, min(turn_rate, h_diff))

        # ── steer climb/dive ─────────────────────────────────────────
        climb_rate = cfg.AIRCRAFT_CLIMB_RATE * dt
        c_diff = self._climb_target - self.climb
        self.climb += max(-climb_rate, min(climb_rate, c_diff))
        self.climb = max(math.radians(-45), min(math.radians(45), self.climb))

        # ── speed adjustment ─────────────────────────────────────────
        spd_diff = self._speed_target - self.speed
        self.speed += max(-40 * dt, min(40 * dt, spd_diff))

        # ── altitude boundary reactions ──────────────────────────────
        if self.z < cfg.AIRCRAFT_MIN_ALT and self.climb < math.radians(10):
            self._climb_target = random.uniform(math.radians(15), math.radians(30))
        if self.z > cfg.AIRCRAFT_MAX_ALT and self.climb > math.radians(-10):
            self._climb_target = random.uniform(math.radians(-30), math.radians(-15))

        # ── move ─────────────────────────────────────────────────────
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        # ── keep within world bounds (hard turn-back) ────────────────
        margin = 300
        if self.x < -margin:
            self._turn_target = random.uniform(0, math.pi * 0.5)
        elif self.x > cfg.WORLD_X_MAX + margin:
            self._turn_target = random.uniform(math.pi * 0.5, math.pi * 1.5)
        if self.y < -(cfg.WORLD_Y_MAX + margin):
            self._turn_target = random.uniform(0, math.pi)
        elif self.y > cfg.WORLD_Y_MAX + margin:
            self._turn_target = random.uniform(-math.pi, 0)

        self.z = max(cfg.AIRCRAFT_MIN_ALT * 0.5, self.z)

        self.history.append((self.x, self.y, self.z))
        if len(self.history) > 8000:
            self.history.pop(0)
