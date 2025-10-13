from __future__ import annotations
from typing import TYPE_CHECKING
from .assets.person import Person
from src.animation import Frame, Line, Point, Segment
from src.entity import EngineEntity
import random
from src.entity import EngineEntity
from src.animation import Animation, Point


if TYPE_CHECKING:
    from src.engine import Engine  # avoid circular import


class SpawnerEntity(EngineEntity):
    """
    Acts as a normal EngineEntity but can spawn and despawn
    other entities within the Engine.
    """

    def __init__(
        self,
        engine: Engine,
        spawn_rate: float = 10.0,
        max_entities: int = 100,
    ):
        animation = Animation(
            [[Segment(Point(0, 0), Point(1, 1), Line("black", weight=0.1))]]
        )
        super().__init__(animation=animation)
        self.engine = engine
        self.spawn_rate = spawn_rate  # seconds between spawns
        self.max_entities = max_entities
        self._time_since_last_spawn = 0.0
        self.spawned_entities: list[EngineEntity] = []

    def update(self, clock) -> None:
        """Called every frame by the engine."""
        super().update(clock)
        self._time_since_last_spawn += clock.dt

        # Try spawning if cooldown passed
        if (
            self._time_since_last_spawn >= self.spawn_rate
            and len(self.spawned_entities) < self.max_entities
        ):
            self.spawn_person()
            self._time_since_last_spawn = 0.0

        # Despawn logic: e.g., remove off-screen or too old
        for e in list(self.spawned_entities):
            if e.position.y > 20 or getattr(e, "dead", False):
                self.despawn(e)

    def spawn_person(self):
        """Example: spawns a random entity near the spawner."""
        new_entity = Person(Point(0, 0))

        self.engine.entities.append(new_entity)
        self.spawned_entities.append(new_entity)
        print(f"[Spawner] Spawned entity at {new_entity.position}")

    def despawn(self, entity: EngineEntity):
        """Remove an entity from the engine and this spawner’s list."""
        if entity in self.engine.entities:
            self.engine.entities.remove(entity)
        if entity in self.spawned_entities:
            self.spawned_entities.remove(entity)
        print(f"[Spawner] Despawned entity {entity}")
