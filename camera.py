"""3-D camera and perspective projection."""

from __future__ import annotations

import math
import config as cfg


class Camera:
    """Orbiting camera with perspective projection."""

    def __init__(self):
        self.azimuth = cfg.CAM_AZIMUTH
        self.elevation = cfg.CAM_ELEVATION
        self.distance = cfg.CAM_DISTANCE
        self.target = list(cfg.CAM_TARGET)

    @property
    def position(self) -> tuple[float, float, float]:
        cx = self.target[0] + self.distance * math.cos(self.elevation) * math.cos(self.azimuth)
        cy = self.target[1] + self.distance * math.cos(self.elevation) * math.sin(self.azimuth)
        cz = self.target[2] + self.distance * math.sin(self.elevation)
        return (cx, cy, cz)

    def project(self, wx: float, wy: float, wz: float) -> tuple[int, int, float] | None:
        """Project world → screen.  Returns (sx, sy, depth) or None."""
        ex, ey, ez = self.position
        dx, dy, dz = wx - ex, wy - ey, wz - ez

        # forward
        fx = self.target[0] - ex
        fy = self.target[1] - ey
        fz = self.target[2] - ez
        fl = math.sqrt(fx*fx + fy*fy + fz*fz)
        if fl < 1e-9:
            return None
        fx /= fl; fy /= fl; fz /= fl

        # right = forward × up(0,0,1)
        rx = fy; ry = -fx; rz = 0.0
        rl = math.sqrt(rx*rx + ry*ry + rz*rz)
        if rl < 1e-9:
            rx, ry, rz = 1.0, 0.0, 0.0
        else:
            rx /= rl; ry /= rl; rz /= rl

        # up = right × forward
        ux = ry*fz - rz*fy
        uy = rz*fx - rx*fz
        uz = rx*fy - ry*fx

        cam_z = dx*fx + dy*fy + dz*fz
        if cam_z < 1.0:
            return None
        cam_x = dx*rx + dy*ry + dz*rz
        cam_y = dx*ux + dy*uy + dz*uz

        factor = cfg.FOV_FACTOR / cam_z
        sx = int(cfg.SCREEN_WIDTH / 2 + cam_x * factor)
        sy = int(cfg.SCREEN_HEIGHT / 2 - cam_y * factor)
        return (sx, sy, cam_z)

    def orbit(self, da: float, de: float):
        self.azimuth += da
        self.elevation = max(math.radians(5), min(math.radians(85), self.elevation + de))

    def zoom(self, amount: float):
        self.distance = max(cfg.CAM_MIN_DIST, min(cfg.CAM_MAX_DIST, self.distance + amount))
