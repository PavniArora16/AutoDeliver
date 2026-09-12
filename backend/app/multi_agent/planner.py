import heapq

from ..models.warehouse import Position, Warehouse
from ..utils.grid_utils import get_neighbors, manhattan_distance
from ..simulation.battery import BatteryManager

from .assignment import GoalAssigner
from .reservation import ReservationTable
from .collision import CollisionDetector


class MultiAgentPlanner:

    def __init__(self, warehouse: Warehouse):

        self.warehouse = warehouse

        self.reservations = ReservationTable()

        self.collision_detector = CollisionDetector(
            self.reservations
        )

        self.max_time = max(
            warehouse.rows * warehouse.cols * 4,
            50
        )

    # ==========================================================
    # MAIN PLANNER
    # ==========================================================

    def plan(self):

        # ------------------------------------------------------
        # STEP 1: Assign goals to robots
        # ------------------------------------------------------

        assigner = GoalAssigner()

        assignments = assigner.assign(
            self.warehouse.robots,
            self.warehouse.goals
        )

        planned_paths = {}

        battery_info = {}

        deadline_info = {}

        # ------------------------------------------------------
        # STEP 2: Plan robots one by one
        # ------------------------------------------------------

        for robot in self.warehouse.robots:

            battery_manager = BatteryManager(robot)

            goal = assignments.get(robot.id)

            # Initial deadline information
            deadline_info[robot.id] = {
                "deadline": robot.deadline,
                "completion_time": None,
                "status": (
                    "no_deadline"
                    if robot.deadline is None
                    else "pending"
                )
            }

            # --------------------------------------------------
            # No goal assigned
            # --------------------------------------------------

            if goal is None:

                planned_paths[robot.id] = None

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": 0,
                    "used_charging_station": False,
                    "status": "no_goal"
                }

                deadline_info[robot.id]["status"] = (
                    "no_goal"
                )

                continue

            # --------------------------------------------------
            # First try direct route
            # --------------------------------------------------

            direct_path = self.time_aware_astar(
                start=robot.start,
                goal=goal,
                robot_id=robot.id,
                start_time=0
            )

            # --------------------------------------------------
            # No direct path exists
            # --------------------------------------------------

            if direct_path is None:

                planned_paths[robot.id] = None

                robot.status = "no_path"

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": 0,
                    "used_charging_station": False,
                    "status": "no_path"
                }

                deadline_info[robot.id]["status"] = (
                    "no_path"
                )

                continue

            # --------------------------------------------------
            # Check direct route battery
            # --------------------------------------------------

            direct_energy = battery_manager.energy_required(
                direct_path
            )

            if robot.battery_level > BatteryManager.LOW_BATTERY_THRESHOLD and battery_manager.can_complete(direct_path):

                # --------------------------------------------------
                # Battery is sufficient
                # --------------------------------------------------

                planned_paths[robot.id] = direct_path

                # --------------------------------------------------
                # Evaluate deadline using actual A* path
                # --------------------------------------------------

                completion_time = len(direct_path) - 1

                if robot.deadline is None:

                    deadline_status = "no_deadline"

                elif completion_time > robot.deadline:

                    deadline_status = "deadline_missed"

                elif completion_time >= robot.deadline * 0.8:

                    deadline_status = "deadline_at_risk"

                else:

                    deadline_status = "on_time"

                deadline_info[robot.id] = {
                    "deadline": robot.deadline,
                    "completion_time": completion_time,
                    "status": deadline_status
                }

                # --------------------------------------------------
                # Battery information
                # --------------------------------------------------

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": direct_energy,
                    "remaining_battery": max(
                        0,
                        robot.battery_level - direct_energy
                    ),
                    "used_charging_station": False,
                    "status": "direct_route"
                }

                robot.status = "planned"

                # --------------------------------------------------
                # Reserve direct path
                # --------------------------------------------------

                self.reserve_complete_path(
                    direct_path,
                    robot.id
                )

                continue

            # ==================================================
            # BATTERY INSUFFICIENT
            # TRY CHARGING STATION
            # ==================================================

            charging_station = self.find_nearest_charging_station(
                robot.start
            )

            # --------------------------------------------------
            # No charging station
            # --------------------------------------------------

            if charging_station is None:

                planned_paths[robot.id] = None

                robot.status = "low_battery"

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": direct_energy,
                    "used_charging_station": False,
                    "status": "no_charging_station"
                }

                deadline_info[robot.id]["status"] = (
                    "low_battery"
                )

                continue

            # --------------------------------------------------
            # Plan robot -> charging station
            # --------------------------------------------------

            path_to_station = self.time_aware_astar(
                start=robot.start,
                goal=charging_station,
                robot_id=robot.id,
                start_time=0
            )

            # --------------------------------------------------
            # Charging station unreachable
            # --------------------------------------------------

            if path_to_station is None:

                planned_paths[robot.id] = None

                robot.status = "charging_station_unreachable"

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": direct_energy,
                    "used_charging_station": False,
                    "status": "charging_station_unreachable"
                }

                deadline_info[robot.id]["status"] = (
                    "charging_station_unreachable"
                )

                continue

            # --------------------------------------------------
            # Check whether robot can reach charger
            # --------------------------------------------------

            station_energy = battery_manager.energy_required(
                path_to_station
            )

            if not battery_manager.can_complete(
                path_to_station
            ):

                planned_paths[robot.id] = None

                robot.status = "battery_too_low"

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": station_energy,
                    "used_charging_station": True,
                    "charging_station": charging_station,
                    "status": "cannot_reach_charging_station"
                }

                deadline_info[robot.id]["status"] = (
                    "battery_too_low"
                )

                continue

            # --------------------------------------------------
            # Reserve robot -> charging station
            # --------------------------------------------------

            self.reserve_complete_path(
                path_to_station,
                robot.id
            )

            station_arrival_time = len(path_to_station) - 1

            # --------------------------------------------------
            # Robot reaches charging station
            # --------------------------------------------------

            battery_after_station = max(
                0,
                robot.battery_level - station_energy
            )

            # Battery becomes full
            charged_battery = robot.battery_capacity

            # --------------------------------------------------
            # Plan charging station -> goal
            # --------------------------------------------------

            path_from_station = self.time_aware_astar(
                start=charging_station,
                goal=goal,
                robot_id=robot.id,
                start_time=station_arrival_time
            )

            # --------------------------------------------------
            # Goal unreachable after charging
            # --------------------------------------------------

            if path_from_station is None:

                planned_paths[robot.id] = None

                robot.status = "goal_unreachable_after_charge"

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": station_energy,
                    "used_charging_station": True,
                    "charging_station": charging_station,
                    "status": "goal_unreachable_after_charge"
                }

                deadline_info[robot.id]["status"] = (
                    "goal_unreachable_after_charge"
                )

                continue

            # --------------------------------------------------
            # Calculate energy after charging
            # --------------------------------------------------

            # First position is already the charging station,
            # so don't duplicate it.
            path_after_charge = path_from_station[1:]

            goal_energy = battery_manager.energy_required(
                path_from_station
            )

            # --------------------------------------------------
            # Check battery capacity after charging
            # --------------------------------------------------

            if goal_energy > robot.battery_capacity:

                planned_paths[robot.id] = None

                robot.status = "battery_capacity_insufficient"

                battery_info[robot.id] = {
                    "battery_level": robot.battery_level,
                    "battery_capacity": robot.battery_capacity,
                    "energy_required": goal_energy,
                    "used_charging_station": True,
                    "charging_station": charging_station,
                    "status": "even_full_battery_insufficient"
                }

                deadline_info[robot.id]["status"] = (
                    "battery_capacity_insufficient"
                )

                continue

            # ==================================================
            # COMBINE ROBOT -> CHARGER -> GOAL
            # ==================================================

            # --------------------------------------------------
            # Add charging dwell time
            # --------------------------------------------------
            CHARGING_STEPS = 5

            charging_wait = [charging_station] * CHARGING_STEPS

            # Robot reaches charger first,
            # stays there while charging,
            # then continues to the goal.
            complete_path = (
                path_to_station
                + charging_wait
                + path_after_charge
            )

            planned_paths[robot.id] = complete_path

            # --------------------------------------------------
            # Evaluate deadline using complete actual path
            # --------------------------------------------------

            completion_time = len(complete_path) - 1

            if robot.deadline is None:

                deadline_status = "no_deadline"

            elif completion_time > robot.deadline:

                deadline_status = "deadline_missed"

            elif completion_time >= robot.deadline * 0.8:

                deadline_status = "deadline_at_risk"

            else:

                deadline_status = "on_time"

            deadline_info[robot.id] = {
                "deadline": robot.deadline,
                "completion_time": completion_time,
                "status": deadline_status
            }

            # --------------------------------------------------
            # Reserve complete path
            # --------------------------------------------------

            self.reserve_complete_path(
                complete_path,
                robot.id
            )

            robot.status = "planned_via_charger"

            # --------------------------------------------------
            # Battery information
            # --------------------------------------------------

            battery_info[robot.id] = {
                "battery_level": robot.battery_level,
                "battery_capacity": robot.battery_capacity,
                "battery_after_reaching_station": (
                    battery_after_station
                ),
                "battery_after_charging": (
                    charged_battery
                ),
                "energy_to_station": (
                    station_energy
                ),
                "energy_after_charging": (
                    goal_energy
                ),
                "total_energy_used": (
                    station_energy +
                    goal_energy
                ),
                "used_charging_station": True,
                "charging_station": charging_station,
                "status": "route_via_charging_station"
            }

        # ======================================================
        # STEP 3: Overall success
        # ======================================================

        successful = all(
            path is not None
            for path in planned_paths.values()
        )

        # ======================================================
        # STEP 4: Calculate makespan
        # ======================================================

        makespan = 0

        for path in planned_paths.values():

            if path is not None:

                makespan = max(
                    makespan,
                    len(path) - 1
                )

        # ======================================================
        # FINAL RESULT
        # ======================================================

        return {
            "success": successful,
            "assignments": assignments,
            "paths": planned_paths,
            "makespan": makespan,
            "battery": battery_info,
            "deadlines": deadline_info
        }

    # ==========================================================
    # FIND NEAREST CHARGING STATION
    # ==========================================================

    def find_nearest_charging_station(
        self,
        position: Position
    ):

        if not self.warehouse.charging_stations:
            return None

        nearest_station = None
        best_distance = float("inf")

        for station in self.warehouse.charging_stations:

            distance = manhattan_distance(
                (
                    position.row,
                    position.col
                ),
                (
                    station.row,
                    station.col
                )
            )

            if distance < best_distance:

                best_distance = distance
                nearest_station = station

        return nearest_station

    # ==========================================================
    # RESERVE COMPLETE PATH
    # ==========================================================

    def reserve_complete_path(
        self,
        path,
        robot_id
    ):

        self.reservations.reserve_path(
            path,
            robot_id
        )

        # Keep final position reserved.
        # This represents the robot remaining at its goal.
        for time_step in range(
            len(path),
            self.max_time + 1
        ):

            self.reservations.reserve(
                path[-1],
                time_step,
                robot_id
            )

    # ==========================================================
    # TIME-AWARE A*
    # ==========================================================

    def time_aware_astar(
        self,
        start: Position,
        goal: Position,
        robot_id: int,
        start_time: int = 0
    ):

        # ------------------------------------------------------
        # Check starting position
        # ------------------------------------------------------

        if self.reservations.is_reserved(
            start,
            start_time,
            robot_id
        ):
            return None

        # ------------------------------------------------------
        # Find minimum traversal cost
        # ------------------------------------------------------

        min_cost = float("inf")

        for row in self.warehouse.grid:

            for cell in row:

                if cell != -1:

                    min_cost = min(
                        min_cost,
                        cell
                    )

        if min_cost == float("inf"):
            return None

        # ------------------------------------------------------
        # A* priority queue
        # ------------------------------------------------------

        counter = 0

        start_state = (
            start.row,
            start.col,
            start_time
        )

        open_set = []

        heapq.heappush(
            open_set,
            (
                0,
                counter,
                0,
                start.row,
                start.col,
                start_time
            )
        )

        # Best cost for each (row, col, time)
        best_cost = {
            start_state: 0
        }

        # Used to reconstruct path
        came_from = {}

        # ------------------------------------------------------
        # Search time-expanded graph
        # ------------------------------------------------------

        while open_set:

            (
                _,
                _,
                current_cost,
                row,
                col,
                time
            ) = heapq.heappop(open_set)

            state = (
                row,
                col,
                time
            )

            # Ignore outdated queue entries
            if current_cost > best_cost.get(
                state,
                float("inf")
            ):
                continue

            current = Position(
                row=row,
                col=col
            )

            # --------------------------------------------------
            # Goal reached
            # --------------------------------------------------

            if current == goal:

                return self.reconstruct_path(
                    came_from,
                    state,
                    start_state
                )

            # --------------------------------------------------
            # Maximum planning time
            # --------------------------------------------------

            if time >= self.max_time:
                continue

            # --------------------------------------------------
            # Get possible movements
            # --------------------------------------------------

            next_positions = get_neighbors(
                self.warehouse.grid,
                (
                    current.row,
                    current.col
                )
            )

            # Waiting is allowed
            next_positions.append(
                (
                    (
                        current.row,
                        current.col
                    ),
                    1
                )
            )

            # --------------------------------------------------
            # Explore movements
            # --------------------------------------------------

            for next_position, movement_cost in next_positions:

                next_position = Position(
                    row=next_position[0],
                    col=next_position[1]
                )

                next_time = time + 1

                # --------------------------------------------------
                # Collision check
                # --------------------------------------------------

                if not self.collision_detector.is_move_safe(
                    current,
                    next_position,
                    next_time,
                    robot_id
                ):
                    continue

                # --------------------------------------------------
                # Calculate cost
                # --------------------------------------------------

                new_cost = (
                    current_cost +
                    movement_cost
                )

                next_state = (
                    next_position.row,
                    next_position.col,
                    next_time
                )

                # --------------------------------------------------
                # Better path found
                # --------------------------------------------------

                if new_cost < best_cost.get(
                    next_state,
                    float("inf")
                ):

                    best_cost[next_state] = new_cost

                    came_from[next_state] = state

                    # Manhattan heuristic
                    heuristic = (
                        manhattan_distance(
                            (
                                next_position.row,
                                next_position.col
                            ),
                            (
                                goal.row,
                                goal.col
                            )
                        )
                        * min_cost
                    )

                    priority = (
                        new_cost +
                        heuristic
                    )

                    counter += 1

                    heapq.heappush(
                        open_set,
                        (
                            priority,
                            counter,
                            new_cost,
                            next_position.row,
                            next_position.col,
                            next_time
                        )
                    )

        return None

    # ==========================================================
    # RECONSTRUCT PATH
    # ==========================================================

    def reconstruct_path(
        self,
        came_from,
        current_state,
        start_state
    ):

        path = []

        current = current_state

        while current != start_state:

            row, col, time = current

            path.append(
                Position(
                    row=row,
                    col=col
                )
            )

            current = came_from[current]

        # Add starting position
        path.append(
            Position(
                row=start_state[0],
                col=start_state[1]
            )
        )

        path.reverse()

        return path