from pydantic import BaseModel, Field
from typing import List


class Position(BaseModel):
    row: int
    col: int


class Robot(BaseModel):
    id: int
    start: Position
    goal: Position | None = None

    # Battery system
    battery_capacity: float = 100.0
    battery_level: float = 100.0
    energy_per_step: float = 1.0

    # Robot state
    status: str = "idle"

    # Task management
    priority: int = 1
    deadline: int | None = None


class Warehouse(BaseModel):
    name: str = "Warehouse"

    rows: int
    cols: int

    # Grid cell values:
    #
    # -1 = obstacle / shelf
    #  1 = normal floor
    #  2 = narrow aisle
    #  3 = congested area
    #  5 = high-cost area
    grid: List[List[int]]

    robots: List[Robot] = Field(
        default_factory=list
    )

    goals: List[Position] = Field(
        default_factory=list
    )

    charging_stations: List[Position] = Field(
        default_factory=list
    )