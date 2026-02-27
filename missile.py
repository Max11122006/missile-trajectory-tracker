"""Guided interceptor missile – proportional navigation in 3-D.

Launched from the ground, the missile accelerates towards the target
aircraft using proportional navigation guidance.  Gravity and drag
act throughout flight.
"""

from __future__ import annotations

import math
import config as cfg


def _norm(x: float, y: float, z: float) -> float:
    return math.sqrt(x*x + y*y + z*z)


class Missile:
    """A guided ground-to-air interceptor."""

    def __init__(self, target_pos: tuple[float, float, float]):
        """Launch from LAUNCH_POS, initially aimed toward *target_pos*."""
        ox, oy, oz = cfg.LAUNCH_POS
        self.x, self.y, self.z = ox, oy, oz

        # initial direction: toward the target
        dx = target_pos[0] - ox
        dy = target_pos[1] - oy
        dz = target_pos[2] - oz
        d = _norm(dx, dy, dz)
        if d < 1:
            d = 1
        # start with a modest speed along that direction
        init_speed = 100.0
        self.vx = dx / d * init_speed
        self.vy = dy / d * init_speed
        self.vz = dz / d * init_speed

        self.alive = True
        self.reached_target = False
        self.time_alive = 0.0

        # previous line-of-sight for PN
        self._prev_los: tuple[float, float, float] | None = None

        self.history: list[tuple[float, float, float]] = [(ox, oy, oz)]

    # ── properties ────────────────────────────────────────────────────────
    @property
    def pos(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def speed(self) -> float:
        return _norm(self.vx, self.vy, self.vz)

    @property
    def heading_deg(self) -> float:
        return math.degrees(math.atan2(self.vy, self.vx))

    @property
    def climb_angle_deg(self) -> float:
        hs = math.hypot(self.vx, self.vy)
        if hs < 0.01:
            return 90.0 if self.vz > 0 else -90.0
        return math.degrees(math.atan2(self.vz, hs))

    # ── update ────────────────────────────────────────────────────────────
    def update(self, dt: float,
               tgt_pos: tuple[float, float, float],
               tgt_vel: tuple[float, float, float]):
        if not self.alive:
            return

        self.time_alive += dt

        # ── proportional navigation guidance ──────────────────────────
        rx = tgt_pos[0] - self.x
        ry = tgt_pos[1] - self.y
        rz = tgt_pos[2] - self.z
        r = _norm(rx, ry, rz)
        if r < 1:
            r = 1

        # line-of-sight unit vector
        los_x, los_y, los_z = rx / r, ry / r, rz / r

        if self._prev_los is not None:
            # LOS rate  = (los - prev_los) / dt
            dlos_x = (los_x - self._prev_los[0]) / dt
            dlos_y = (los_y - self._prev_los[1]) / dt
            dlos_z = (los_z - self._prev_los[2]) / dt

            # closing velocity
            vrx = tgt_vel[0] - self.vx
            vry = tgt_vel[1] - self.vy
            vrz = tgt_vel[2] - self.vz
            vc = -(vrx * los_x + vry * los_y + vrz * los_z)  # positive when closing
            vc = max(vc, 50.0)  # avoid zero/negative closing velocity

            # PN acceleration command:  a = N * Vc * LOS_rate
            N = cfg.MISSILE_NAV_GAIN
            cmd_ax = N * vc * dlos_x
            cmd_ay = N * vc * dlos_y
            cmd_az = N * vc * dlos_z
        else:
            cmd_ax = cmd_ay = cmd_az = 0.0

        self._prev_los = (los_x, los_y, los_z)

        # ── thrust along velocity direction ───────────────────────────
        spd = self.speed
        if spd > 0.1:
            thrust_dir_x = self.vx / spd
            thrust_dir_y = self.vy / spd
            thrust_dir_z = self.vz / spd
        else:
            thrust_dir_x, thrust_dir_y, thrust_dir_z = los_x, los_y, los_z

        ax = thrust_dir_x * cfg.MISSILE_ACCEL + cmd_ax
        ay = thrust_dir_y * cfg.MISSILE_ACCEL + cmd_ay
        az = thrust_dir_z * cfg.MISSILE_ACCEL + cmd_az

        # ── gravity ───────────────────────────────────────────────────
        az -= cfg.GRAVITY

        # ── drag ──────────────────────────────────────────────────────
        if spd > 0:
            drag = cfg.DRAG_MISSILE * spd * spd
            ax -= (self.vx / spd) * drag
            ay -= (self.vy / spd) * drag
            az -= (self.vz / spd) * drag

        # ── integrate ─────────────────────────────────────────────────
        self.vx += ax * dt
        self.vy += ay * dt
        self.vz += az * dt

        # clamp speed
        spd = self.speed
        if spd > cfg.MISSILE_MAX_SPEED:
            s = cfg.MISSILE_MAX_SPEED / spd
            self.vx *= s; self.vy *= s; self.vz *= s

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        # ── record history ────────────────────────────────────────────
        self.history.append((self.x, self.y, self.z))
        if len(self.history) > 8000:
            self.history.pop(0)

        # ── ground collision ──────────────────────────────────────────
        if self.z <= 0 and self.time_alive > 0.5:
            self.z = 0.0
            self.alive = False

        # ── out of bounds ─────────────────────────────────────────────
        if (self.x < -500 or self.x > cfg.WORLD_X_MAX + 1000
                or abs(self.y) > cfg.WORLD_Y_MAX + 1000
                or self.z > cfg.WORLD_Z_MAX + 1000):
            self.alive = False

        # ── timeout ───────────────────────────────────────────────────
        if self.time_alive > 60:
            self.alive = False

        # ── hit check ─────────────────────────────────────────────────
        dist = _norm(self.x - tgt_pos[0], self.y - tgt_pos[1], self.z - tgt_pos[2])
        if dist < cfg.HIT_RADIUS:
            self.reached_target = True
            self.alive = False
