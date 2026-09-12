from ..algorithms.astar import AStar
from ..algorithms.ucs import UCS
from ..algorithms.gbfs import GBFS
from ..multi_agent.assignment import GoalAssigner

class AlgorithmBenchmark:

    def __init__(self, warehouse):

        self.warehouse = warehouse

        self.algorithms = [
            AStar(),
            UCS(),
            GBFS()
        ]

    def run(self):

        results = []

        # Assign warehouse goals to robots
        # using the same assignment logic as the multi-agent planner.
        assigner = GoalAssigner()

        assignments = assigner.assign(
            self.warehouse.robots,
            self.warehouse.goals
        )

        for robot in self.warehouse.robots:

            goal_position = assignments.get(robot.id)

            # No goal assigned to this robot
            if goal_position is None:
                continue

            start = (
                robot.start.row,
                robot.start.col
            )

            goal = (
                goal_position.row,
                goal_position.col
            )

            for algorithm in self.algorithms:

                result = algorithm.find_path(
                    self.warehouse.grid,
                    start,
                    goal
                )

                results.append({
                    "robot_id": robot.id,

                    "algorithm": result.algorithm,

                    "found": result.found,

                    "path_cost": result.path_cost,

                    "path_length": len(result.path),

                    "nodes_expanded":
                        result.nodes_expanded,

                    "max_frontier_size":
                        result.max_frontier_size,

                    "runtime_ms":
                        round(
                            result.runtime_ms,
                            4
                        )
                })

        return results

    # ---------------------------------------------------------
    # Summary of benchmark
    # ---------------------------------------------------------

    def summary(self, results):

        algorithms = [
            "A*",
            "UCS",
            "GBFS"
        ]

        summary = {}

        for algorithm in algorithms:

            algorithm_results = [
                r for r in results
                if r["algorithm"] == algorithm
            ]

            if not algorithm_results:
                continue

            successful = [
                r for r in algorithm_results
                if r["found"]
            ]

            summary[algorithm] = {

                "success_rate":
                    round(
                        len(successful)
                        /
                        len(algorithm_results)
                        * 100,
                        2
                    ),

                "average_path_cost":
                    round(
                        self._average(
                            successful,
                            "path_cost"
                        ),
                        2
                    ),

                "average_path_length":
                    round(
                        self._average(
                            successful,
                            "path_length"
                        ),
                        2
                    ),

                "average_nodes_expanded":
                    round(
                        self._average(
                            successful,
                            "nodes_expanded"
                        ),
                        2
                    ),

                "average_frontier_size":
                    round(
                        self._average(
                            successful,
                            "max_frontier_size"
                        ),
                        2
                    ),

                "average_runtime_ms":
                    round(
                        self._average(
                            successful,
                            "runtime_ms"
                        ),
                        4
                    )
            }

        return summary

    def _average(self, results, key):

        if not results:
            return 0

        values = [
            result[key]
            for result in results
        ]

        return sum(values) / len(values)