# scenario_models.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from .assets.backgrounds import Day
from .entity import EngineEntity
from .assets.rides import FerrisWheel, PirateShip


class MapPositionModel(BaseModel):
    x: float
    y: float
    z: Optional[float] = None


class RideModel(BaseModel):
    type: Literal["FerrisWheel", "PirateShip"]
    position: MapPositionModel
    max_capacity: int = Field(..., ge=0)
    ride_time: float = Field(..., ge=0)


class RulesModel(BaseModel):
    max_guests: int = Field(..., ge=0)
    spawn_rate: float = Field(..., ge=0)
    target_fps: int = Field(..., ge=0)


class Scenario:
    """Runtime scenario that holds all live objects."""

    def __init__(
        self,
        name: str,
        background: EngineEntity,
        rules: RulesModel,
        rides: list[EngineEntity],
    ):
        self.name = name
        self.background = background
        self.rules = rules
        self.rides: list[EngineEntity] = rides

    def add_ride(self, ride: EngineEntity) -> None:
        self.rides.append(ride)

    def __repr__(self) -> str:
        return f"<Scenario {self.name!r}, rides={len(self.rides)}>"


class ScenarioModel(BaseModel):
    """Pure configuration (JSON schema level)."""

    name: str
    background: Literal["Day", "Night"]
    rules: RulesModel
    rides: List[RideModel] = Field(default_factory=list)

    def build(self) -> Scenario:
        engine_entity_rides: list[EngineEntity] = []
        engine_entity_background: EngineEntity
        for ride_data in self.rides:
            # TODO
            if ride_data.type == "FerrisWheel":
                engine_entity_rides.append(FerrisWheel())
            elif ride_data.type == "PirateShip":
                engine_entity_rides.append(PirateShip())
            else:
                raise ValueError("Invalid ride")

        if self.background == "Day":
            engine_entity_background = Day()
        elif self.background == "Night":
            # TODO
            engine_entity_background = Day()
        else:
            raise ValueError("Invalid background")

        scenario = Scenario(
            name=self.name,
            background=engine_entity_background,
            rules=self.rules,
            rides=engine_entity_rides,
        )

        return scenario
