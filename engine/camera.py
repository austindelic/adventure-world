"""
File: camera.py
Author: Austin Delic (austin@austindelic.com)
"""

from typing import Protocol
from .animation import Point
from dataclasses import dataclass
from math import cos, sin


class CameraProtocol(Protocol):
    def to_view(self, p: Point) -> Point: ...


@dataclass(slots=True)
class Camera(CameraProtocol):
    x: float = 0.5  # camera position in world coords
    y: float = 0.0
    zoom: float = 1.0  # 1.0 = no zoom
    rot: float = 0.0  # optional rotation (radians), 0 = none

    def to_view(self, p: Point) -> Point:
        # world -> camera space (translate so camera is origin)
        dx = p.x - self.x
        dy = p.y - self.y
        # rotate (camera yaw) – optional; keep if you want “look rotation”
        if self.rot != 0.0:
            c, s = cos(-self.rot), sin(-self.rot)
            dx, dy = dx * c - dy * s, dx * s + dy * c
        # zoom (scale)
        return Point(dx * self.zoom, dy * self.zoom)

    # Convenience ops
    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def set_pos(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def set_zoom(self, zoom: float) -> None:
        self.zoom = max(1e-6, zoom)  # avoid zero/neg

    def add_zoom(self, dzoom: float) -> None:
        self.set_zoom(self.zoom + dzoom)

    def set_rot(self, angle_rad: float) -> None:
        self.rot = angle_rad
