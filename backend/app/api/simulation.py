from fastapi import APIRouter

from ..models.simulation import (
    SimulationRequest,
    SimulationResult,
    RobotSimulation
)

from ..multi_agent.planner import MultiAgentPlanner
from ..simulation.engine import SimulationEngine


router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"]
)


@router.post("/run", response_model=SimulationResult)
def run_simulation(request: SimulationRequest):

    planner = MultiAgentPlanner(request.warehouse)

    planning_result = planner.plan()

    engine = SimulationEngine()

    robot_simulations = []

    for robot_id, path in planning_result["paths"].items():

        if path is None:
            continue

        steps = engine.simulate_path(path)

        robot_simulations.append(
            RobotSimulation(
                robot_id=robot_id,
                steps=steps
            )
        )

    return SimulationResult(
        success=planning_result["success"],
        assignments=planning_result["assignments"],
        robots=robot_simulations,
        makespan=planning_result["makespan"]
    )