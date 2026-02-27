"""Missile physics and guidance system.

Coordinate system (world):
    x  – horizontal distance in metres (right is positive)
    y  – altitude in metres (up is positive)
    Gravity acts in the -y direction.
"""

from __future__ import annotations

import math
import config as cfg


class Missile:
    """A guided missile with thrust, gravity, drag, and proportional-navigation guidance."""

    def __init__(self, x: float, y: float, angle: float, speed: float):
        """
        Parameters
        ----------
        x, y : float
            Launch position in metres.
        angle : float
            Launch angle in radians above the horizontal (positive = upward).
        speed : float
            Initial speed in m/s.
        """
        self.x = x
        self.y = y
        self.angle = angle  # radians above horizontal
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.fuel = cfg.MISSILE_FUEL_TIME
        self.alive = True
        self.reached_target = False
        self.time_alive = 0.0

        # trajectory history: list of (x, y) in world coords
        self.history: list[tuple[float, float]] = [(x, y)]

    # ── helpers ───────────────────────────────────────────────────────────
    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def velocity(self) -> float:
        return math.hypot(self.vx, self.vy)

    # ── guidance ──────────────────────────────────────────────────────────
    def _desired_angle(self, tx: float, ty: float) -> float:
        """Angle from missile towards the target (radians, positive = up)."""
        return math.atan2(ty - self.y, tx - self.x)

    def _steer_towards(self, target_angle: float, dt: float) -> float:
        """Return a new angle after rate-limited steering."""
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

        # Thrust (along heading)
        if self.fuel > 0:
            self.fuel -= dt
            ax = math.cos(self.angle) * cfg.MISSILE_THRUST
            ay = math.sin(self.angle) * cfg.MISSILE_THRUST
        else:
            ax = 0.0
            ay = 0.0

        # Gravity (pulls downward = negative y)
        ay -= cfg.GRAVITY

        # Drag (opposes velocity)
        speed = self.velocity
        if speed > 0:
            drag = cfg.AIR_DRAG * speed * speed
            ax -= (self.vx / speed) * drag
            ay -= (self.vy / speed) * drag

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

        # Update heading to match velocity when ballistic
        if self.fuel <= 0 and speed > 1:
            self.angle = math.atan2(self.vy, self.vx)

        # Store history
        self.history.append((self.x, self.y))
        if len(self.history) > 5000:
            self.history.pop(0)

        # Ground collision (y <= 0)
        if self.y <= cfg.GROUND_Y:
            self.y = cfg.GROUND_Y
            self.alive = False

        # Out of world bounds
        if (self.x < cfg.WORLD_X_MIN - 200
                or self.x > cfg.WORLD_X_MAX + 200
                or self.y > cfg.WORLD_Y_MAX + 500):
            self.alive = False

        # Target proximity (hit detection – within 50 m)
        dist = math.hypot(self.x - target_x, self.y - target_y)
        if dist < 50:
            self.reached_target = True
            self.alive = False
