from ..models.warehouse import Position, Robot
from ..utils.grid_utils import manhattan_distance


class GoalAssigner:

    def assign(
        self,
        robots: list[Robot],
        goals: list[Position]
    ):
        """
        Assign unique goals to robots using:
        1. Task priority
        2. Deadline feasibility
        3. Distance

        Higher-priority robots get assignment preference.
        If a deadline is specified, goals that can be reached
        within the deadline are preferred.
        """

        assignments = {}

        remaining_robots = robots.copy()
        remaining_goals = goals.copy()

        # ------------------------------------------------------
        # STEP 1: Sort robots by priority
        # ------------------------------------------------------

        # Higher priority is handled first.
        # If priority is equal, earlier deadline is preferred.
        remaining_robots.sort(
            key=lambda robot: (
                -robot.priority,
                robot.deadline
                if robot.deadline is not None
                else float("inf")
            )
        )

        # ------------------------------------------------------
        # STEP 2: Assign goals
        # ------------------------------------------------------

        for robot in remaining_robots:

            if not remaining_goals:
                assignments[robot.id] = None
                continue

            best_goal = None
            best_distance = float("inf")

            # --------------------------------------------------
            # Find goals that satisfy the deadline
            # --------------------------------------------------

            deadline_goals = []

            if robot.deadline is not None:

                for goal in remaining_goals:

                    distance = manhattan_distance(
                        (robot.start.row, robot.start.col),
                        (goal.row, goal.col)
                    )

                    if distance <= robot.deadline:
                        deadline_goals.append(
                            (goal, distance)
                        )

            # --------------------------------------------------
            # If deadline-feasible goals exist,
            # choose the nearest one.
            # --------------------------------------------------

            if deadline_goals:

                for goal, distance in deadline_goals:

                    if distance < best_distance:

                        best_distance = distance
                        best_goal = goal

            # --------------------------------------------------
            # Otherwise choose nearest available goal.
            # --------------------------------------------------

            else:

                for goal in remaining_goals:

                    distance = manhattan_distance(
                        (robot.start.row, robot.start.col),
                        (goal.row, goal.col)
                    )

                    if distance < best_distance:

                        best_distance = distance
                        best_goal = goal

            # --------------------------------------------------
            # Store assignment
            # --------------------------------------------------

            assignments[robot.id] = best_goal

            remaining_goals.remove(best_goal)

        return assignments