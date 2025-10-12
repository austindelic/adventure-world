from dataclasses import dataclass
from src.entity import EngineEntity
from src.animation import Animation, Point
from src.entity import Size


class Ride(EngineEntity):
    def __init__(
        self,
        animation: Animation,
        position: Point = Point(0, 0),
        size: Size = Size(10, 10, 10),
        fps: int = 24,
        max_capacity: int = 10,
    ) -> None:
        self.max_capacity = max_capacity
        super().__init__(
            animation,
            position=position,
            target_size=size,
            fps=fps,
        )
