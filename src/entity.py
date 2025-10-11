"""
File: object.py
Author: Austin Delic (austin@austindelic.com)
"""

from matplotlib.axes import Axes
from shapely.lib import bounds
from .animation import Segment, Point, Animation, Frame
from math import cos, sin
from .clock import ClockProtocol
from .camera import Camera
from math import isfinite


class EngineEntity:
    """Model + view glue: holds pose and renders transformed geometry."""

    def __init__(
        self,
        animation: Animation,
        *,
        start_point: Point = Point(0.0, 0.0),
        size: float = 1.0,
        rotation: float = 0.0,  # radians (base/orientation)
        pivot: Point = Point(0.0, 0.0),
        fps: int = 24,
    ) -> None:
        self.start_point = start_point
        self.size = size
        self.animation = animation
        self.rotation = rotation
        self.pivot = pivot
        self.fps = fps
        self.pose_rotation = 0.0
        self.cull_pad_frac = 0.05

    def _transform(self, segment: Segment) -> Segment:
        total_rot = self.rotation + self.pose_rotation
        p1r = self._rotate(segment.start, total_rot, self.pivot)
        p2r = self._rotate(segment.end, total_rot, self.pivot)
        p1s = Point(p1r.x * self.size, p1r.y * self.size)
        p2s = Point(p2r.x * self.size, p2r.y * self.size)
        return Segment(
            Point(self.start_point.x + p1s.x, self.start_point.y + p1s.y),
            Point(self.start_point.x + p2s.x, self.start_point.y + p2s.y),
            segment.line,
        )

    @staticmethod
    def _rotate(p: Point, angle: float, origin: Point) -> Point:
        dx, dy = p.x - origin.x, p.y - origin.y
        c, s = cos(angle), sin(angle)
        return Point(origin.x + dx * c - dy * s, origin.y + dx * s + dy * c)

    def get_frame(self, frame_clock: int, engine_fps: int = 24) -> Frame:
        """Return the current transformed Frame for this object."""
        segments: Frame = [
            self._transform(segment)
            for segment in self.animation.get_current_frame(
                frame_clock, self.fps, engine_fps
            )
        ]
        return segments

    def update(self, clock: ClockProtocol) -> None:
        """Override in subclasses (read time/dt/frame)."""
        ...


class Ride(EngineEntity):
    def __init__(
        self,
        animation: Animation,
        start_point: Point = Point(0, 0),
        size: float = 1,
        rotation: float = 0,
        pivot: Point = Point(0, 0),
        fps: int = 24,
        max_capacity: int = 10,
    ) -> None:
        self.max_capacity = max_capacity
        super().__init__(
            animation,
            start_point=start_point,
            size=size,
            rotation=rotation,
            pivot=pivot,
            fps=fps,
        )


# class Zone(EngineEntity):
#     def __init__(self, animation: Animation, start_point: Point = Point(0, 0), size: float = 1, rotation: float = 0, pivot: Point = Point(0, 0), fps: int = 24, bounds: pass) -> None:
#         self.bounds = bounds
#         super().__init__(animation, start_point=start_point, size=size, rotation=rotation, pivot=pivot, fps=fps)
