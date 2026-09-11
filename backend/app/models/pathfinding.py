from pydantic import BaseModel
from typing import Literal


class PositionRequest(BaseModel):
    row: int
    col: int


class PathfindingRequest(BaseModel):
    grid: list[list[int]]

    start: PositionRequest

    goal: PositionRequest

    algorithm: Literal["astar", "ucs", "gbfs"]