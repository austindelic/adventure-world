from dataclasses import dataclass
from .animation import Segment, Point, Animation, Frame, Fill
from math import cos, sin
from .clock import ClockProtocol


@dataclass
class Size:
    height: float
    width: float
    depth: float


class EngineEntity:
    """Model + view glue: holds pose and renders transformed geometry."""

    def __init__(
        self,
        animation: Animation,
        position: Point = Point(0.0, 0.0),
        size: Size = Size(1, 1, 1),  # 1m^3
        fps: int = 24,
    ) -> None:
        self.position = position
        self.size = size
        self.animation = animation
        self.fps = fps

    def get_frame(self, frame_clock: int, engine_fps: int = 24) -> Frame:
        """Return the current transformed Frame for this object."""
        frame = self.animation.get_current_frame(frame_clock, self.fps, engine_fps)
        return frame

    # ---------- Behaviour ----------
    def update(self, clock: ClockProtocol) -> None:
        """Override in subclasses to animate."""
        ...
