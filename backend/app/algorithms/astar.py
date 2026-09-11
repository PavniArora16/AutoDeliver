import heapq
import time

from .base import PathResult, PathfindingAlgorithm
from ..utils.grid_utils import (
    get_neighbors,
    manhattan_distance
)


class AStar(PathfindingAlgorithm):

    name = "A*"

    def find_path(self, grid, start, goal):

        start_time = time.perf_counter()

        # Priority queue:
        # (f_score, counter, position)
        frontier = []

        counter = 0

        heapq.heappush(
            frontier,
            (0, counter, start)
        )

        came_from = {
            start: None
        }

        cost_so_far = {
            start: 0
        }

        explored = []

        max_frontier_size = 1

        while frontier:

            _, _, current = heapq.heappop(frontier)

            explored.append(current)

            # Goal reached
            if current == goal:

                path = self.reconstruct_path(
                    came_from,
                    goal
                )

                runtime = (
                    time.perf_counter() - start_time
                ) * 1000

                return PathResult(
                    algorithm=self.name,
                    found=True,
                    path=path,
                    path_cost=cost_so_far[goal],
                    nodes_expanded=len(explored),
                    max_frontier_size=max_frontier_size,
                    runtime_ms=runtime,
                    explored=explored
                )

            for neighbor, movement_cost in get_neighbors(
                grid,
                current
            ):

                new_cost = (
                    cost_so_far[current]
                    + movement_cost
                )

                if (
                    neighbor not in cost_so_far
                    or new_cost < cost_so_far[neighbor]
                ):

                    cost_so_far[neighbor] = new_cost

                    # Manhattan heuristic
                    h = manhattan_distance(
                        neighbor,
                        goal
                    )

                    f = new_cost + h

                    counter += 1

                    heapq.heappush(
                        frontier,
                        (f, counter, neighbor)
                    )

                    came_from[neighbor] = current

            max_frontier_size = max(
                max_frontier_size,
                len(frontier)
            )

        runtime = (
            time.perf_counter() - start_time
        ) * 1000

        return PathResult(
            algorithm=self.name,
            found=False,
            runtime_ms=runtime,
            nodes_expanded=len(explored),
            max_frontier_size=max_frontier_size,
            explored=explored
        )

    def reconstruct_path(self, came_from, goal):

        path = []

        current = goal

        while current is not None:

            path.append(current)

            current = came_from[current]

        path.reverse()

        return path