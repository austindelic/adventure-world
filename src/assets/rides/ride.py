from src.entity import EngineEntity
from src.animation import Animation, Point


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
