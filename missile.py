"""Missile physics and guidance system."""

from __future__ import annotations

import math
import config as cfg


class Missile:
    """A guided missile with thrust, gravity, drag, and proportional-navigation guidance."""

    def __init__(self, x: float, y: float, angle: float, speed: float):
        self.x = x
        self.y = y
        self.angle = angle  # radians, 0 = right, negative = up
        self.speed = speed
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.fuel = cfg.MISSILE_FUEL_TIME
        self.alive = True
        self.reached_target = False
        self.time_alive = 0.0

        # trajectory history for trail drawing
        self.history: list[tuple[float, float]] = []

    # ── helpers ───────────────────────────────────────────────────────────
    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def velocity(self) -> float:
        return math.hypot(self.vx, self.vy)

    @property
    def altitude(self) -> float:
        """Altitude above ground in pixels."""
        return max(0.0, cfg.GROUND_Y - self.y)

    # ── guidance ──────────────────────────────────────────────────────────
    def _desired_angle(self, tx: float, ty: float) -> float:
        """Angle from missile towards the target."""
        return math.atan2(ty - self.y, tx - self.x)

    def _steer_towards(self, target_angle: float, dt: float) -> float:
        """Return a new angle after steering towards *target_angle*."""
        diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        max_turn = cfg.MISSILE_TURN_RATE * dt
        turn = max(-max_turn, min(max_turn, diff))
        return self.angle + turn

    # ── main update ───────────────────────────────────────────────────────
    def update(self, dt: float, target_x: float, target_y: float):
        if not self.alive:
            return

        self.time_alive += dt

        # Guidance: steer towards target while fuel remains
        if self.fuel > 0:
            desired = self._desired_angle(target_x, target_y)
            self.angle = self._steer_towards(desired, dt)

        # Thrust
        if self.fuel > 0:
            self.fuel -= dt
            ax = math.cos(self.angle) * cfg.MISSILE_THRUST
            ay = math.sin(self.angle) * cfg.MISSILE_THRUST
        else:
            ax = 0.0
            ay = 0.0

        # Gravity (downward = positive y in screen coords)
        ay += cfg.GRAVITY

        # Drag  (opposes velocity)
        speed = self.velocity
        if speed > 0:
            drag = cfg.AIR_DRAG * speed * speed
            drag_ax = -self.vx / speed * drag
            drag_ay = -self.vy / speed * drag
            ax += drag_ax
            ay += drag_ay

        # Integrate
        self.vx += ax * dt
        self.vy += ay * dt

        # Clamp speed
        speed = self.velocity
        if speed > cfg.MISSILE_MAX_SPEED:
            scale = cfg.MISSILE_MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Update angle to match velocity when out of fuel (ballistic)
        if self.fuel <= 0 and speed > 1:
            self.angle = math.atan2(self.vy, self.vx)

        # Store history
        self.history.append((self.x, self.y))
        if len(self.history) > 3000:
            self.history.pop(0)

        # Ground collision
        if self.y >= cfg.GROUND_Y:
            self.y = cfg.GROUND_Y
            self.alive = False

        # Off-screen
        if (self.x < -100 or self.x > cfg.SCREEN_WIDTH + 100
                or self.y < -500):
            self.alive = False

        # Target proximity
        dist = math.hypot(self.x - target_x, self.y - target_y)
        if dist < cfg.TARGET_RADIUS + 4:
            self.reached_target = True
            self.alive = False
