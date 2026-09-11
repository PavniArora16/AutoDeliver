from collections import deque
import statistics

from ..utils.grid_utils import get_neighbors


class WarehouseFeatures:

    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.grid = warehouse.grid
        self.rows = warehouse.rows
        self.cols = warehouse.cols

    # ---------------------------------------------------------
    # 1. Obstacle Density
    # ---------------------------------------------------------

    def obstacle_density(self):

        total_cells = self.rows * self.cols

        if total_cells == 0:
            return 0

        obstacle_cells = 0

        for row in self.grid:
            for cell in row:

                if cell == -1:
                    obstacle_cells += 1

        return obstacle_cells / total_cells

    # ---------------------------------------------------------
    # 2. Average Branching Factor
    # ---------------------------------------------------------

    def average_branching_factor(self):

        branching_values = []

        for r in range(self.rows):
            for c in range(self.cols):

                if self.grid[r][c] == -1:
                    continue

                neighbors = get_neighbors(
                    self.grid,
                    (r, c)
                )

                branching_values.append(
                    len(neighbors)
                )

        if not branching_values:
            return 0

        return statistics.mean(
            branching_values
        )

    # ---------------------------------------------------------
    # 3. Dead-End Ratio
    # ---------------------------------------------------------

    def dead_end_ratio(self):

        free_cells = 0
        dead_ends = 0

        for r in range(self.rows):
            for c in range(self.cols):

                if self.grid[r][c] == -1:
                    continue

                free_cells += 1

                neighbors = get_neighbors(
                    self.grid,
                    (r, c)
                )

                # A free cell with only one
                # possible exit is a dead end.
                if len(neighbors) == 1:
                    dead_ends += 1

        if free_cells == 0:
            return 0

        return dead_ends / free_cells

    # ---------------------------------------------------------
    # 4. Edge-Cost Variance
    # ---------------------------------------------------------

    def edge_cost_variance(self):

        costs = []

        for r in range(self.rows):
            for c in range(self.cols):

                if self.grid[r][c] == -1:
                    continue

                costs.append(
                    self.grid[r][c]
                )

        if len(costs) < 2:
            return 0

        return statistics.pvariance(costs)

    # ---------------------------------------------------------
    # 5. Heuristic Quality
    # ---------------------------------------------------------

    def heuristic_quality(self):

        """
        Measures how close Manhattan distance is
        to actual shortest-path distance.

        Score:
            1.0 = very good heuristic
            0.0 = poor heuristic
        """

        pairs = []

        # Use warehouse robot start/goal pairs
        for robot in self.warehouse.robots:

            if robot.goal is not None:

                start = (
                    robot.start.row,
                    robot.start.col
                )

                goal = (
                    robot.goal.row,
                    robot.goal.col
                )

                pairs.append(
                    (start, goal)
                )

        if not pairs:
            return 0

        scores = []

        for start, goal in pairs:

            true_distance = self._shortest_distance(
                start,
                goal
            )

            if true_distance is None:
                continue

            manhattan = (
                abs(start[0] - goal[0])
                +
                abs(start[1] - goal[1])
            )

            if true_distance == 0:
                scores.append(1.0)

            else:

                score = manhattan / true_distance

                # Safety clamp
                score = min(
                    max(score, 0),
                    1
                )

                scores.append(score)

        if not scores:
            return 0

        return statistics.mean(scores)

    # ---------------------------------------------------------
    # Shortest Distance Helper
    # ---------------------------------------------------------

    def _shortest_distance(self, start, goal):

        queue = deque()

        queue.append(
            (start, 0)
        )

        visited = {start}

        while queue:

            current, distance = queue.popleft()

            if current == goal:
                return distance

            for neighbor, _ in get_neighbors(
                self.grid,
                current
            ):

                if neighbor in visited:
                    continue

                visited.add(neighbor)

                queue.append(
                    (
                        neighbor,
                        distance + 1
                    )
                )

        return None

    # ---------------------------------------------------------
    # 6. Overall Feature Extraction
    # ---------------------------------------------------------

    def extract_all(self):

        return {

            "grid_rows": self.rows,

            "grid_cols": self.cols,

            "total_cells":
                self.rows * self.cols,

            "obstacle_density":
                round(
                    self.obstacle_density(),
                    4
                ),

            "average_branching_factor":
                round(
                    self.average_branching_factor(),
                    4
                ),

            "dead_end_ratio":
                round(
                    self.dead_end_ratio(),
                    4
                ),

            "edge_cost_variance":
                round(
                    self.edge_cost_variance(),
                    4
                ),

            "heuristic_quality":
                round(
                    self.heuristic_quality(),
                    4
                )
        }