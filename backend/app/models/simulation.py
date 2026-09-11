from pydantic import BaseModel
from typing import Dict, List

from .warehouse import Position, Warehouse


class SimulationRequest(BaseModel):
    warehouse: Warehouse


class SimulationStepRequest(BaseModel):
    warehouse: Warehouse
    robot_id: int
    time_step: int


class SimulationStateRequest(BaseModel):
    warehouse: Warehouse
    time_step: int


class SimulationStep(BaseModel):
    time_step: int
    position: Position

    battery_level: float
    battery_percentage: float

    status: str
    is_charging: bool
    is_goal_reached: bool


class RobotState(BaseModel):
    robot_id: int
    step: SimulationStep

class SimulationTimelineStep(BaseModel):
    time_step: int
    robots: List[RobotState]


class SimulationTimelineResult(BaseModel):
    success: bool
    makespan: int
    timeline: List[SimulationTimelineStep]


class RobotSimulation(BaseModel):
    robot_id: int
    steps: List[SimulationStep]

    path_length: int
    wait_steps: int
    path_cost: float

    final_battery: float
    final_status: str


class SimulationResult(BaseModel):
    success: bool
    assignments: Dict[int, Position | None]
    robots: List[RobotSimulation]
    makespan: int