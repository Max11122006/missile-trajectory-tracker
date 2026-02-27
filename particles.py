"""Particle system for smoke trails and explosions."""

from __future__ import annotations

import math
import random
import config as cfg


class Particle:
    """A single particle with position, velocity, colour, and lifetime."""

    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "colour")

    def __init__(self, x, y, vx, vy, life, size, colour):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.colour = colour

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        """0..1 fade factor."""
        return max(0, self.life / self.max_life)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += cfg.GRAVITY * 0.3 * dt  # light gravity on particles
        self.life -= dt


class ParticleSystem:
    """Manages collections of particles."""

    def __init__(self):
        self.particles: list[Particle] = []
        self._trail_accum = 0.0  # accumulator for trail spawn rate

    # ── emitters ──────────────────────────────────────────────────────────
    def emit_trail(self, x: float, y: float, angle: float, dt: float):
        """Spawn smoke-trail particles behind the missile."""
        self._trail_accum += dt
        interval = 1.0 / cfg.TRAIL_RATE
        while self._trail_accum >= interval:
            self._trail_accum -= interval
            spread = 0.4
            back_angle = angle + math.pi + random.uniform(-spread, spread)
            speed = random.uniform(20, 60)
            vx = math.cos(back_angle) * speed
            vy = math.sin(back_angle) * speed
            life = cfg.TRAIL_LIFETIME * random.uniform(0.6, 1.0)
            size = cfg.TRAIL_SIZE * random.uniform(0.6, 1.3)

            # colour: bright orange → grey fade (pick initial colour)
            t = random.random()
            if t < 0.3:
                colour = cfg.YELLOW
            elif t < 0.7:
                colour = cfg.ORANGE
            else:
                colour = cfg.GREY

            self.particles.append(Particle(x, y, vx, vy, life, size, colour))

    def emit_explosion(self, x: float, y: float, hit: bool = True):
        """Spawn a burst of particles for an explosion."""
        count = cfg.EXPLOSION_PARTICLES
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, cfg.EXPLOSION_SPEED)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = cfg.EXPLOSION_LIFETIME * random.uniform(0.3, 1.0)
            size = random.uniform(2, 6)

            if hit:
                colour = random.choice([cfg.RED, cfg.ORANGE, cfg.YELLOW, cfg.WHITE])
            else:
                colour = random.choice([cfg.ORANGE, cfg.GREY, cfg.DARK_GREY])

            self.particles.append(Particle(x, y, vx, vy, life, size, colour))

    # ── update / cull ─────────────────────────────────────────────────────
    def update(self, dt: float):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def clear(self):
        self.particles.clear()
        self._trail_accum = 0.0
