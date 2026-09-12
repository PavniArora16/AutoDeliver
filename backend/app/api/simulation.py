from fastapi import APIRouter

from ..models.simulation import (
    SimulationRequest,
    SimulationStepRequest,
    SimulationStateRequest,
    SimulationResult,
    RobotSimulation,
    RobotState,
    SimulationTimelineStep,
    SimulationTimelineResult
)

from ..multi_agent.planner import MultiAgentPlanner
from ..simulation.engine import SimulationEngine


router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"]
)


@router.post(
    "/run",
    response_model=SimulationResult
)
def run_simulation(
    request: SimulationRequest
):

    # ---------------------------------------------------------
    # STEP 1: Plan all robots
    # ---------------------------------------------------------

    planner = MultiAgentPlanner(
        request.warehouse
    )

    planning_result = planner.plan()

    engine = SimulationEngine()

    robot_simulations = []

    # ---------------------------------------------------------
    # STEP 2: Simulate each robot
    # ---------------------------------------------------------

    for robot in request.warehouse.robots:

        robot_id = robot.id

        path = planning_result["paths"].get(
            robot_id
        )

        if path is None:
            continue

        goal = planning_result["assignments"].get(
            robot_id
        )

        # -----------------------------------------------------
        # Run battery-aware simulation
        # -----------------------------------------------------

        steps = engine.simulate_path(
            path=path,
            initial_battery=robot.battery_level,
            battery_capacity=robot.battery_capacity,
            energy_per_step=robot.energy_per_step,
            charging_stations=request.warehouse.charging_stations,
            goal=goal
        )

        # -----------------------------------------------------
        # Calculate path metrics
        # -----------------------------------------------------

        path_length = max(
            0,
            len(path) - 1
        )

        wait_steps = 0
        path_cost = 0.0

        for i in range(
            1,
            len(path)
        ):

            current = path[i]
            previous = path[i - 1]

            # Robot waited
            if current == previous:

                wait_steps += 1

            else:

                row = current.row
                col = current.col

                path_cost += (
                    request.warehouse.grid[row][col]
                )

        # -----------------------------------------------------
        # Final robot state
        # -----------------------------------------------------

        if steps:

            final_battery = steps[-1].battery_level
            final_status = steps[-1].status

        else:

            final_battery = robot.battery_level
            final_status = robot.status

        # -----------------------------------------------------
        # Store simulation
        # -----------------------------------------------------

        robot_simulations.append(
            RobotSimulation(
                robot_id=robot_id,
                steps=steps,
                path_length=path_length,
                wait_steps=wait_steps,
                path_cost=path_cost,
                final_battery=final_battery,
                final_status=final_status
            )
        )

    # ---------------------------------------------------------
    # STEP 3: Return result
    # ---------------------------------------------------------

    return SimulationResult(
        success=planning_result["success"],
        assignments=planning_result["assignments"],
        robots=robot_simulations,
        makespan=planning_result["makespan"]
    )
@router.post("/step")
def simulation_step(
    request: SimulationStepRequest
):
    # ---------------------------------------------------------
    # Find requested robot
    # ---------------------------------------------------------

    robot = next(
        (
            r
            for r in request.warehouse.robots
            if r.id == request.robot_id
        ),
        None
    )

    if robot is None:
        return {
            "success": False,
            "message": f"Robot {request.robot_id} not found"
        }

    # ---------------------------------------------------------
    # Create planner
    # ---------------------------------------------------------

    planner = MultiAgentPlanner(
        request.warehouse
    )

    planning_result = planner.plan()

    path = planning_result["paths"].get(
        request.robot_id
    )

    if path is None:
        return {
            "success": False,
            "message": f"No path found for robot {request.robot_id}"
        }

    # ---------------------------------------------------------
    # Validate timestep
    # ---------------------------------------------------------

    if request.time_step < 0:
        return {
            "success": False,
            "message": "Time step cannot be negative"
        }

    if request.time_step >= len(path):
        return {
            "success": False,
            "message": "Time step exceeds simulation length",
            "max_time_step": len(path) - 1
        }

    # ---------------------------------------------------------
    # Calculate battery up to requested timestep
    # ---------------------------------------------------------

    battery = robot.battery_level

    for i in range(1, request.time_step + 1):

        current = path[i]
        previous = path[i - 1]

        # Charging station
        is_charging = any(
            current == station
            for station in request.warehouse.charging_stations
        )

        if is_charging:
            # Charge only while staying on the charging station
            if current == previous:
                battery = min(
                    robot.battery_capacity,
                    battery + robot.battery_capacity * 0.20
                )
        elif current != previous:
            battery = max(
                0.0,
                battery - robot.energy_per_step
            )

    # ---------------------------------------------------------
    # Previous position
    # ---------------------------------------------------------

    previous_position = None

    if request.time_step > 0:
        previous_position = path[
            request.time_step - 1
        ]

    # ---------------------------------------------------------
    # Generate current step
    # ---------------------------------------------------------

    engine = SimulationEngine()

    goal = planning_result["assignments"].get(
        request.robot_id
    )

    step = engine.simulate_step(
        position=path[request.time_step],
        time_step=request.time_step,
        battery=battery,
        battery_capacity=robot.battery_capacity,
        energy_per_step=robot.energy_per_step,
        charging_stations=request.warehouse.charging_stations,
        goal=goal,
        previous_position=previous_position
    )

    return {
        "success": True,
        "robot_id": request.robot_id,
        "time_step": request.time_step,
        "step": step
    }
@router.post("/state")
def simulation_state(
    request: SimulationStateRequest
):
    # ---------------------------------------------------------
    # Validate timestep
    # ---------------------------------------------------------

    if request.time_step < 0:
        return {
            "success": False,
            "message": "Time step cannot be negative"
        }

    # ---------------------------------------------------------
    # Plan all robots
    # ---------------------------------------------------------

    planner = MultiAgentPlanner(
        request.warehouse
    )

    planning_result = planner.plan()

    engine = SimulationEngine()

    robot_states = []

    # ---------------------------------------------------------
    # Generate state for every robot
    # ---------------------------------------------------------

    for robot in request.warehouse.robots:

        robot_id = robot.id

        path = planning_result["paths"].get(
            robot_id
        )

        if path is None:
            continue

        # -----------------------------------------------------
        # Check whether timestep exists
        # -----------------------------------------------------

        if request.time_step >= len(path):
            continue

        # -----------------------------------------------------
        # Calculate battery until this timestep
        # -----------------------------------------------------

        battery = robot.battery_level

        for i in range(
            1,
            request.time_step + 1
        ):

            current = path[i]
            previous = path[i - 1]

            is_charging = any(
                current == station
                for station in request.warehouse.charging_stations
            )

            if is_charging:
                # Charge only while staying on the charging station
                if current == previous:
                    battery = min(
                        robot.battery_capacity,
                        battery + robot.battery_capacity * 0.20
                    )
            elif current != previous:
                battery = max(
                    0.0,
                    battery - robot.energy_per_step
                )

        # -----------------------------------------------------
        # Previous position
        # -----------------------------------------------------

        previous_position = None

        if request.time_step > 0:

            previous_position = path[
                request.time_step - 1
            ]

        # -----------------------------------------------------
        # Goal
        # -----------------------------------------------------

        goal = planning_result["assignments"].get(
            robot_id
        )

        # -----------------------------------------------------
        # Generate current step
        # -----------------------------------------------------

        step = engine.simulate_step(
            position=path[request.time_step],
            time_step=request.time_step,
            battery=battery,
            battery_capacity=robot.battery_capacity,
            energy_per_step=robot.energy_per_step,
            charging_stations=request.warehouse.charging_stations,
            goal=goal,
            previous_position=previous_position
        )

        robot_states.append(
            RobotState(
                robot_id=robot_id,
                step=step
            )
        )

    # ---------------------------------------------------------
    # Return complete warehouse state
    # ---------------------------------------------------------

    return {
        "success": True,
        "time_step": request.time_step,
        "makespan": planning_result["makespan"],
        "robots": robot_states
    }
@router.post(
    "/timeline",
    response_model=SimulationTimelineResult
)
def simulation_timeline(
    request: SimulationRequest
):

    # ---------------------------------------------------------
    # STEP 1: Plan all robots
    # ---------------------------------------------------------

    planner = MultiAgentPlanner(
        request.warehouse
    )

    planning_result = planner.plan()

    if not planning_result["success"]:
        return SimulationTimelineResult(
            success=False,
            makespan=0,
            timeline=[]
        )

    # ---------------------------------------------------------
    # STEP 2: Create simulation engine
    # ---------------------------------------------------------

    engine = SimulationEngine()

    # ---------------------------------------------------------
    # STEP 3: Generate complete simulation for each robot
    # ---------------------------------------------------------

    robot_steps = {}

    for robot in request.warehouse.robots:

        path = planning_result["paths"].get(
            robot.id
        )

        if path is None:
            continue

        goal = planning_result["assignments"].get(
            robot.id
        )

        steps = engine.simulate_path(
            path=path,
            initial_battery=robot.battery_level,
            battery_capacity=robot.battery_capacity,
            energy_per_step=robot.energy_per_step,
            charging_stations=request.warehouse.charging_stations,
            goal=goal
        )

        robot_steps[robot.id] = steps

    # ---------------------------------------------------------
    # STEP 4: Build timeline
    # ---------------------------------------------------------

    makespan = planning_result["makespan"]

    timeline = []

    for time_step in range(
        makespan + 1
    ):

        current_robot_states = []

        for robot_id, steps in robot_steps.items():

            # -------------------------------------------------
            # Robot still has an active step
            # -------------------------------------------------

            if time_step < len(steps):

                step = steps[time_step]

            # -------------------------------------------------
            # Robot has already completed its path
            # Keep it at final position
            # -------------------------------------------------

            else:

                step = steps[-1]

            current_robot_states.append(
                RobotState(
                    robot_id=robot_id,
                    step=step
                )
            )

        timeline.append(
            SimulationTimelineStep(
                time_step=time_step,
                robots=current_robot_states
            )
        )

    # ---------------------------------------------------------
    # STEP 5: Return timeline
    # ---------------------------------------------------------

    return SimulationTimelineResult(
        success=True,
        makespan=makespan,
        timeline=timeline
    )