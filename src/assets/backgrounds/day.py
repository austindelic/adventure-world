from src.animation import Animation, Fill, Frame, Point
from src.entity import EngineEntity, Size


class Day(EngineEntity):
    """Simple static background with blue sky and green grass."""

    def __init__(self) -> None:
        # Blue sky (top half)
        sky = Fill(
            points=[
                Point(0.0, 0.5),
                Point(1.0, 0.5),
                Point(1.0, 1.0),
                Point(0.0, 1.0),
            ],
            color="b",
            alpha=1.0,
        )

        # Green grass (bottom half)
        grass = Fill(
            points=[
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                Point(1.0, 0.5),
                Point(0.0, 0.5),
            ],
            color="g",
            alpha=1.0,
        )

        base_frame: Frame = [sky, grass]
        super().__init__(
            animation=Animation([base_frame]), position=Point(0, 0), size=Size(1, 1, 1)
        )
