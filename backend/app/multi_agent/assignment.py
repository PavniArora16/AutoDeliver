from ..models.warehouse import Position, Robot
from ..utils.grid_utils import manhattan_distance


class GoalAssigner:

    def assign(self, robots: list[Robot], goals: list[Position]):
        """
        Assign unique goals to robots using greedy nearest-distance matching.
        """

        assignments = {}

        remaining_robots = robots.copy()
        remaining_goals = goals.copy()

        while remaining_robots and remaining_goals:

            best_robot = None
            best_goal = None
            best_distance = float("inf")

            for robot in remaining_robots:

                for goal in remaining_goals:

                    distance = manhattan_distance(
                        (robot.start.row, robot.start.col),
                        (goal.row, goal.col)
                    )

                    if distance < best_distance:
                        best_distance = distance
                        best_robot = robot
                        best_goal = goal

            assignments[best_robot.id] = best_goal

            remaining_robots.remove(best_robot)
            remaining_goals.remove(best_goal)

        # If there are more robots than goals,
        # the remaining robots receive no goal.
        for robot in remaining_robots:
            assignments[robot.id] = None

        return assignments