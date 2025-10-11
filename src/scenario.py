# scenario_models.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from .entity import EngineEntity
from .assets import FerrisWheel, PirateShip
from .animation import Point

RIDE_CLASSES = {
    "FerrisWheel": FerrisWheel,
    "PirateShip": PirateShip,
}


class MapPosition(BaseModel):
    x: float
    y: float
    z: Optional[float] = None


class RideModel(BaseModel):
    type: Literal["FerrisWheel", "PirateShip"]
    position: MapPosition
    max_capacity: int = Field(..., ge=0)
    ride_time: float = Field(..., ge=0)


class RulesModel(BaseModel):
    max_guests: int = Field(..., ge=0)
    spawn_rate: float = Field(..., ge=0)


class ScenarioModel(BaseModel):
    """Pure configuration (JSON schema level)."""

    name: str
    background: Literal["day", "night"] = "day"
    rules: RulesModel = Field(
        default_factory=lambda: RulesModel(max_guests=100, spawn_rate=1.0)
    )
    rides: List[RideModel] = Field(default_factory=list)


class Scenario:
    """Runtime scenario that holds all live objects."""

    def __init__(self, name: str, background: str, rules):
        self.name = name
        self.background = background
        self.rules = rules
        self.rides: list[EngineEntity] = []

    def add_ride(self, ride: EngineEntity) -> None:
        self.rides.append(ride)

    def __repr__(self) -> str:
        return f"<Scenario {self.name!r}, rides={len(self.rides)}>"


class ScenarioBuilder:
    """Converts a validated ScenarioModel into a live Scenario with runtime objects."""

    def __init__(self, model: ScenarioModel):
        self.model = model

    def build(self) -> Scenario:
        scenario = Scenario(
            name=self.model.name,
            background=self.model.background,
            rules=self.model.rules,
        )

        for ride_data in self.model.rides:
            cls = RIDE_CLASSES[ride_data.type]
            ride_obj = cls()
            ride_obj.pose_position = Point(
                ride_data.position.x,
                ride_data.position.y,
            )
            scenario.add_ride(ride_obj)

        return scenario
