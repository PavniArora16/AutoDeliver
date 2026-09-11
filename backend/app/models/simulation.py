from pydantic import BaseModel
from typing import Dict, List
from .warehouse import Position, Warehouse


class SimulationRequest(BaseModel):
    warehouse: Warehouse


class SimulationStep(BaseModel):
    time_step: int
    position: Position


class RobotSimulation(BaseModel):
    robot_id: int
    steps: List[SimulationStep]


class SimulationResult(BaseModel):
    success: bool
    assignments: Dict[int, Position | None]
    robots: List[RobotSimulation]
    makespan: int