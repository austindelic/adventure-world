from .animation import Segment, Point, Animation, Frame, Fill
from math import cos, sin
from .clock import ClockProtocol


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

    # ---------- Geometry Transforms ----------
    def _transform_point(self, p: Point) -> Point:
        """Apply rotation, scale, and translation to a single point."""
        total_rot = self.rotation + self.pose_rotation
        dx, dy = p.x - self.pivot.x, p.y - self.pivot.y
        c, s = cos(total_rot), sin(total_rot)
        # Rotate and scale
        xr = dx * c - dy * s
        yr = dx * s + dy * c
        xs, ys = xr * self.size, yr * self.size
        # Translate
        return Point(self.start_point.x + xs, self.start_point.y + ys)

    def _transform_segment(self, seg: Segment) -> Segment:
        """Apply transformation to a Segment."""
        return Segment(
            start=self._transform_point(seg.start),
            end=self._transform_point(seg.end),
            line=seg.line,
        )

    def _transform_fill(self, fill: Fill) -> Fill:
        """Apply transformation to a Fill (polygon)."""
        transformed_points = [self._transform_point(p) for p in fill.points]
        return Fill(
            points=transformed_points,
            color=fill.color,
            alpha=fill.alpha,
            edgecolor=fill.edgecolor,
        )

    # ---------- Frame Handling ----------
    def get_frame(self, frame_clock: int, engine_fps: int = 24) -> Frame:
        """Return the current transformed Frame for this object."""
        raw_frame = self.animation.get_current_frame(frame_clock, self.fps, engine_fps)
        transformed: Frame = []
        for draw in raw_frame:
            if isinstance(draw, Segment):
                transformed.append(self._transform_segment(draw))
            elif isinstance(draw, Fill):
                transformed.append(self._transform_fill(draw))
            else:
                raise TypeError(f"Unsupported draw type: {type(draw)}")
        return transformed

    # ---------- Behaviour ----------
    def update(self, clock: ClockProtocol) -> None:
        """Override in subclasses to animate."""
        ...
