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

    # ── threat levels (distance thresholds in metres) ────────────────
    THREAT_FAR   = 3000   # cruise – normal random manoeuvres
    THREAT_MED   = 1800   # defensive – frequent jinking
    THREAT_CLOSE = 900    # panic – max-g break turns

    def _pick_manoeuvre(self, threat: float):
        """Choose heading / climb / speed targets scaled by *threat*.

        *threat* is 0.0 when missile is far / absent, up to 1.0 at knife-edge.
        """
        # heading change: bigger when threatened
        max_turn = 1.2 + 1.8 * threat          # 1.2 … 3.0 rad
        self._turn_target = self.heading + random.uniform(-max_turn, max_turn)

        # climb/dive: steeper when threatened
        max_pitch = math.radians(15 + 35 * threat)    # 15° … 50°
        self._climb_target = random.uniform(-max_pitch, max_pitch)

        # speed: afterburner boost when threatened
        base = cfg.AIRCRAFT_SPEED
        self._speed_target = base * (random.uniform(0.7, 1.0) + 0.5 * threat)

        # next manoeuvre sooner when threat is high
        period = cfg.AIRCRAFT_MANOEUVRE_PERIOD * (1.0 - 0.7 * threat)
        self._manoeuvre_timer = -random.uniform(0, period * 0.3)

    def _evasive_break(self, mx: float, my: float, mz: float):
        """Hard break-turn perpendicular to threat bearing."""
        bearing = math.atan2(my - self.y, mx - self.x)
        # choose a direction 90° ± 30° off the threat
        side = random.choice([-1, 1])
        self._turn_target = bearing + side * random.uniform(math.radians(70), math.radians(110))
        # dive or climb hard away
        if self.z > (cfg.AIRCRAFT_MIN_ALT + cfg.AIRCRAFT_MAX_ALT) / 2:
            self._climb_target = random.uniform(math.radians(-50), math.radians(-30))
        else:
            self._climb_target = random.uniform(math.radians(30), math.radians(50))
        self._speed_target = cfg.AIRCRAFT_SPEED * 1.4  # afterburner

    def _threat_level(self, missile_pos: tuple[float, float, float] | None) -> float:
        """Return 0.0 (safe) … 1.0 (imminent intercept)."""
        if missile_pos is None:
            return 0.0
        dx = missile_pos[0] - self.x
        dy = missile_pos[1] - self.y
        dz = missile_pos[2] - self.z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist >= self.THREAT_FAR:
            return 0.0
        if dist <= self.THREAT_CLOSE:
            return 1.0
        return 1.0 - (dist - self.THREAT_CLOSE) / (self.THREAT_FAR - self.THREAT_CLOSE)

    def update(self, dt: float,
               missile_pos: tuple[float, float, float] | None = None):
        if not self.alive:
            return

        threat = self._threat_level(missile_pos)

        # ── manoeuvre selection ───────────────────────────────────────
        self._manoeuvre_timer += dt
        # base period shortens with threat
        period = cfg.AIRCRAFT_MANOEUVRE_PERIOD * max(0.3, 1.0 - 0.8 * threat)
        if self._manoeuvre_timer >= period:
            self._manoeuvre_timer = 0.0
            if threat > 0.8 and missile_pos is not None:
                # panic – hard break turn
                self._evasive_break(*missile_pos)
            elif threat > 0.4 and missile_pos is not None:
                # defensive jink + biased away from missile
                self._pick_manoeuvre(threat)
                # bias heading away from threat
                bearing = math.atan2(missile_pos[1] - self.y,
                                     missile_pos[0] - self.x)
                away = bearing + math.pi + random.uniform(-0.6, 0.6)
                self._turn_target = (self._turn_target + away) / 2
            else:
                self._pick_manoeuvre(threat)

        # ── steer heading (rate scales with threat) ──────────────────
        eff_turn = cfg.AIRCRAFT_TURN_RATE * (1.0 + 1.5 * threat)  # up to 2.5× turn rate
        turn_rate = eff_turn * dt
        h_diff = (self._turn_target - self.heading + math.pi) % (2 * math.pi) - math.pi
        self.heading += max(-turn_rate, min(turn_rate, h_diff))

        # ── steer climb/dive (rate scales with threat) ───────────────
        eff_climb = cfg.AIRCRAFT_CLIMB_RATE * (1.0 + 1.5 * threat)
        climb_rate = eff_climb * dt
        c_diff = self._climb_target - self.climb
        self.climb += max(-climb_rate, min(climb_rate, c_diff))
        self.climb = max(math.radians(-55), min(math.radians(55), self.climb))

        # ── speed adjustment (faster accel when evading) ─────────────
        accel = (40 + 60 * threat) * dt
        spd_diff = self._speed_target - self.speed
        self.speed += max(-accel, min(accel, spd_diff))

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
