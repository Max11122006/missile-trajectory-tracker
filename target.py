"""Target that the missile aims for."""

from __future__ import annotations

import config as cfg


class Target:
    """A target marker placed by the user."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.active = True
        self.pulse = 0.0   # used for pulsing animation

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def update(self, dt: float):
        self.pulse += dt * 3.0

    def set(self, x: float, y: float):
        """Set target in world coordinates (metres)."""
        self.x = x
        self.y = max(y, cfg.GROUND_Y)  # can't be below ground
        self.active = True
