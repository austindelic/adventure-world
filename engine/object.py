"""
File: object.py
Author: Austin Delic (austin@austindelic.com)
"""

from matplotlib.axes import Axes
from .animation import Segment, Point, Animation
from math import cos, sin
from .time import ClockProtocol
from .camera import Camera
from math import isfinite


class EngineObject:
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
        # Per-frame pose adjustments (set by update()):
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

    def draw(
        self,
        ax: Axes,
        frame_clock: int,
        engine_fps: int = 24,
        camera: Camera | None = None,
    ) -> None:
        # base axes limits (view space)
        x_lo, x_hi = ax.get_xlim()
        y_lo, y_hi = ax.get_ylim()

        # padding (as a fraction of current view size)
        pad_x = self.cull_pad_frac * (x_hi - x_lo)
        pad_y = self.cull_pad_frac * (y_hi - y_lo)

        # expanded bounds
        ex_lo, ex_hi = x_lo - pad_x, x_hi + pad_x
        ey_lo, ey_hi = y_lo - pad_y, y_hi + pad_y

        def in_view(p: Point) -> bool:
            return (
                isfinite(p.x)
                and isfinite(p.y)
                and (ex_lo <= p.x <= ex_hi)
                and (ey_lo <= p.y <= ey_hi)
            )

        for segment in self.animation.get_current_frame(
            frame_clock, self.fps, engine_fps
        ):
            t = self._transform(segment)  # world space
            s = camera.to_view(t.start) if camera else t.start
            e = camera.to_view(t.end) if camera else t.end

            # Cull if BOTH endpoints are outside the padded view
            if not (in_view(s) or in_view(e)):
                continue

            ax.plot(
                [s.x, e.x],
                [s.y, e.y],
                color=segment.line.color,
                linestyle=segment.line.style,
                marker=segment.line.marker,
                linewidth=segment.line.weight,
                alpha=segment.line.alpha,
            )

    def update(self, clock: ClockProtocol) -> None:
        """Override in subclasses (read time/dt/frame)."""
        ...
