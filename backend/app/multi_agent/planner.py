import heapq

from ..models.warehouse import Position, Warehouse
from ..utils.grid_utils import get_neighbors, manhattan_distance
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

    def plan(self):

        # -----------------------------------
        # STEP 1: Assign goals to robots
        # -----------------------------------

        assigner = GoalAssigner()

        assignments = assigner.assign(
            self.warehouse.robots,
            self.warehouse.goals
        )

        planned_paths = {}

        # -----------------------------------
        # STEP 2: Plan robots one by one
        # -----------------------------------

        for robot in self.warehouse.robots:

            goal = assignments.get(robot.id)

            if goal is None:
                planned_paths[robot.id] = None
                continue

            path = self.time_aware_astar(
                start=robot.start,
                goal=goal,
                robot_id=robot.id
            )

            if path is None:
                planned_paths[robot.id] = None
                continue

            planned_paths[robot.id] = path

            # -----------------------------------
            # STEP 3: Reserve the path
            # -----------------------------------

            self.reservations.reserve_path(
                path,
                robot.id
            )

            # Keep the robot's final position reserved.
            # This represents the robot staying at its goal.
            for time_step in range(
                len(path),
                self.max_time + 1
            ):
                self.reservations.reserve(
                    path[-1],
                    time_step,
                    robot.id
                )

        successful = all(
            path is not None
            for path in planned_paths.values()
        )

        makespan = 0

        for path in planned_paths.values():

            if path is not None:
                makespan = max(
                    makespan,
                    len(path) - 1
                )

        return {
            "success": successful,
            "assignments": assignments,
            "paths": planned_paths,
            "makespan": makespan
        }

    def time_aware_astar(
        self,
        start: Position,
        goal: Position,
        robot_id: int
    ):

        # -----------------------------------
        # Check starting position
        # -----------------------------------

        if self.reservations.is_reserved(
            start,
            0,
            robot_id
        ):
            return None

        # -----------------------------------
        # Find minimum traversal cost
        # -----------------------------------

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

        # -----------------------------------
        # A* priority queue
        # -----------------------------------

        counter = 0

        start_state = (
            start.row,
            start.col,
            0
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
                0
            )
        )

        # Best cost for each (row, col, time)
        best_cost = {
            start_state: 0
        }

        # Used to reconstruct the path
        came_from = {}

        # -----------------------------------
        # Search time-expanded graph
        # -----------------------------------

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

            # -----------------------------------
            # Goal reached
            # -----------------------------------

            if current == goal:

                return self.reconstruct_path(
                    came_from,
                    state,
                    start_state
                )

            # -----------------------------------
            # Stop after maximum time
            # -----------------------------------

            if time >= self.max_time:
                continue

            # -----------------------------------
            # Get possible movements
            # -----------------------------------

            next_positions = get_neighbors(
                self.warehouse.grid,
                (current.row, current.col)
            )

            # Waiting is also allowed
            next_positions.append(
                ((current.row, current.col), 1)
            )

            # -----------------------------------
            # Explore movements
            # -----------------------------------

            for next_position, movement_cost in next_positions:
                next_position = Position(
                    row=next_position[0],
                    col=next_position[1]
                )

                next_time = time + 1

                # -----------------------------------
                # Collision check
                # -----------------------------------

                if not self.collision_detector.is_move_safe(
                    current,
                    next_position,
                    next_time,
                    robot_id
                ):
                    continue

                # -----------------------------------
                # Calculate new cost
                # -----------------------------------

                new_cost = (
                    current_cost + movement_cost
                )

                next_state = (
                    next_position.row,
                    next_position.col,
                    next_time
                )

                # -----------------------------------
                # Better path found
                # -----------------------------------

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
                        new_cost + heuristic
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