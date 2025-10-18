"""Entity base classes and geometry helpers.

EngineEntity holds pose and an Animation, and exposes get_frame/update hooks.
"""

from dataclasses import dataclass
from typing import Iterable

from .animation import Animation, Fill, Frame, Point, Segment
from .clock import ClockProtocol

EPS = 1e-9


@dataclass
class Size:
    height: float
    width: float
    depth: float


@dataclass
class Bounds:
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y


def _iter_points(frame: Frame) -> Iterable[Point]:
    for d in frame:
        if isinstance(d, Segment):
            yield d.start
            yield d.end
        elif isinstance(d, Fill):
            for p in d.points:
                yield p


class EngineEntity:
    """Model + view glue: holds pose and renders transformed geometry."""

    def __init__(
        self,
        animation: Animation,
        position: Point = Point(0.0, 0.0),
        target_size: Size = Size(1, 1, 1),
        fps: int = 24,
    ) -> None:
        self.position = position
        self.target_size = target_size
        self.animation = animation
        self.fps = fps

        # Derived at construction:
        self.bounds = self._compute_animation_bounds()
        self.size = self._calc_size_from_target()  # metres per normalised unit
        # Optional: offset that recentres the animation bbox min corner at (0,0)
        self.norm_offset = Point(-self.bounds.min_x, -self.bounds.min_y)

    def _compute_animation_bounds(self) -> Bounds:
        pts_x, pts_y = [], []

        # Try the most informative source first
        frames = getattr(self.animation, "frames", None)

        if frames is not None:
            for fr in frames:
                for p in _iter_points(fr):
                    pts_x.append(p.x)
                    pts_y.append(p.y)
        else:
            # Fallback: sample a reasonable number of frames
            # Try to use a known frame count if exposed; else sample 60 steps
            n = getattr(self.animation, "num_frames", None) or 60
            for i in range(n):
                fr = self.animation.get_current_frame(i, self.fps, self.fps)
                for p in _iter_points(fr):
                    pts_x.append(p.x)
                    pts_y.append(p.y)

        if not pts_x:
            # Degenerate bbox; treat as unit box
            return Bounds(0.0, 1.0, 0.0, 1.0)

        return Bounds(min(pts_x), max(pts_x), min(pts_y), max(pts_y))

    def _calc_size_from_target(self) -> Size:
        w = self.bounds.width if self.bounds.width > EPS else 1.0
        h = self.bounds.height if self.bounds.height > EPS else 1.0
        return Size(
            height=self.target_size.height / h,  # e.g. 10 / 0.7 -> 14.2857 m/unit
            width=self.target_size.width / w,
            depth=self.target_size.depth,  # passthrough for now
        )

    def get_frame(self, frame_clock: int, engine_fps: int = 24) -> Frame:
        return self.animation.get_current_frame(frame_clock, self.fps, engine_fps)

    # ---------- Behaviour ----------
    def update(self, clock: ClockProtocol) -> None:
        """Optional per-frame behavior; default does nothing."""
        pass
