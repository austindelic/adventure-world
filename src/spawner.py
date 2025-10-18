"""Guest spawner entity for the simulation."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .animation import Animation, Frame, Line, Point, Segment
from .assets.person import Person
from .clock import ClockProtocol
from .entity import EngineEntity, Size

if TYPE_CHECKING:  # pragma: no cover
    from .engine import Engine


_SPAWNER_ICON: Frame = [
    Segment(Point(0.0, 0.0), Point(0.0, 0.6), Line("darkgray", 2.0)),
    Segment(Point(0.0, 0.6), Point(0.2, 0.8), Line("darkgray", 2.0)),
    Segment(Point(0.0, 0.6), Point(-0.2, 0.8), Line("darkgray", 2.0)),
    Segment(Point(-0.15, 0.0), Point(0.15, 0.0), Line("darkgray", 2.0)),
]


class SpawnerEntity(EngineEntity):
    """Spawns :class:`Person` entities until the configured capacity is reached."""

    def __init__(
        self,
        engine: Engine,
        *,
        position: Point,
        spawn_rate: float,
        max_guests: int,
        spawn_radius: float = 0.05,
    ) -> None:
        super().__init__(
            animation=Animation([_SPAWNER_ICON]),
            position=position,
            target_size=Size(1.0, 1.0, 1.0),
        )
        self.engine = engine
        self.max_guests = max(0, int(max_guests))
        self.spawn_rate = max(0.0, spawn_rate)  # guests per second
        self.spawn_radius = spawn_radius
        self._rng = random.Random()
        self._time_accumulator = 0.0
        self.spawned_entities: list[Person] = []
        self._spawn_interval = (
            1.0 / self.spawn_rate if self.spawn_rate > 0.0 else float("inf")
        )

    def _current_guest_count(self) -> int:
        self.spawned_entities = [
            guest for guest in self.spawned_entities if guest in self.engine.entities
        ]
        return len(self.spawned_entities)

    def _spawn_guest(self) -> None:
        if self._current_guest_count() >= self.max_guests:
            return

        offset_x = self._rng.uniform(-self.spawn_radius, self.spawn_radius)
        offset_y = self._rng.uniform(-self.spawn_radius, self.spawn_radius)
        spawn_point = Point(self.position.x + offset_x, self.position.y + offset_y)

        guest = Person(position=spawn_point)
        self.engine.add_engine_objects([guest])
        self.spawned_entities.append(guest)
        print(f"[Spawner] Guest spawned at ({spawn_point.x:.2f}, {spawn_point.y:.2f})")

    def _despawn_guest(self, guest: Person) -> None:
        if guest in self.engine.entities:
            self.engine.entities.remove(guest)
        if guest in self.spawned_entities:
            self.spawned_entities.remove(guest)
        print("[Spawner] Guest despawned")

    def update(self, clock: ClockProtocol) -> None:
        if self.max_guests <= 0 or self._spawn_interval == float("inf"):
            return

        self._time_accumulator += clock.dt

        while (
            self._time_accumulator >= self._spawn_interval
            and self._current_guest_count() < self.max_guests
        ):
            self._spawn_guest()
            self._time_accumulator -= self._spawn_interval

        for guest in list(self.spawned_entities):
            if guest.position.y > 20 or getattr(guest, "dead", False):
                self._despawn_guest(guest)
