# object.py
from engine.animation import Segment, Point, Animation
from matplotlib.axes import Axes
import math


class EngineObject:
    def __init__(
        self,
        animation: Animation,
        engine,
        *,
        start_point: Point,
        size: float = 1,
        rotation: float = 0.0,
        pivot: Point = Point(0, 0),
        fps: int = 24
    ) -> None:
        self.engine = engine
        self.start_point = start_point
        self.size = size
        self.animation = animation
        self.rotation = rotation
        self.pivot = pivot
        self.fps = fps

    def _transform(self, segment: Segment) -> Segment:
        """
        Local -> (rotate about pivot) -> scale -> translate to world.
        """
        # 1) rotate local endpoints about local pivot
        p1r = self._rotate(segment.start, self.rotation, self.pivot)
        p2r = self._rotate(segment.end, self.rotation, self.pivot)

        # 2) scale (uniform)
        p1s = Point(p1r.x * self.size, p1r.y * self.size)
        p2s = Point(p2r.x * self.size, p2r.y * self.size)

        # 3) translate to world
        x1 = self.start_point.x + p1s.x
        y1 = self.start_point.y + p1s.y
        x2 = self.start_point.x + p2s.x
        y2 = self.start_point.y + p2s.y

        return Segment(Point(x1, y1), Point(x2, y2), segment.line)

    @staticmethod
    def _rotate(p: Point, angle: float, origin: Point) -> Point:
        """Rotate point p by angle (radians) around origin (both in local space)."""
        dx, dy = p.x - origin.x, p.y - origin.y
        c, s = math.cos(angle), math.sin(angle)
        return Point(
            origin.x + dx * c - dy * s,
            origin.y + dx * s + dy * c,
        )

    def draw(self, ax: Axes, frame_clock: int, engine_fps: int = 24) -> None:
        """
        The default draw function for EngineObject. Can be overwritten for more advanced shapes with rotation ect.
        """
        for segment in self.animation.get_current_frame(
            frame_clock, self.fps, engine_fps
        ):
            transformed_segment = self._transform(segment)
            ax.plot(
                [transformed_segment.start.x, transformed_segment.end.x],
                [transformed_segment.start.y, transformed_segment.end.y],
                color=segment.line.color,
                linestyle=segment.line.style,
                marker=segment.line.marker,
                linewidth=segment.line.weight,
                alpha=segment.line.alpha,
            )

    def update(self, frame_clock: int):
        """
        Will update every frame. move location, update size ect.
        """
        ...
