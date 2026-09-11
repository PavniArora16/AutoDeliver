from app.algorithms.astar import AStar
from app.algorithms.ucs import UCS
from app.algorithms.gbfs import GBFS


grid = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, -1, -1, -1, -1, -1, 1, 1],
    [1, 1, 1, 1, 1, -1, 1, 1],
    [1, -1, -1, -1, 1, -1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, -1, -1, -1, -1, -1, -1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]


start = (0, 0)
goal = (7, 7)


algorithms = [
    AStar(),
    UCS(),
    GBFS()
]


print("\n==========================================")
print("        AutoDeliver Algorithm Test")
print("==========================================")

print(f"Start : {start}")
print(f"Goal  : {goal}")

for algorithm in algorithms:

    result = algorithm.find_path(
        grid,
        start,
        goal
    )

    print("\n------------------------------------------")

    print(f"Algorithm       : {result.algorithm}")
    print(f"Path Found      : {result.found}")
    print(f"Path Cost       : {result.path_cost}")
    print(f"Nodes Expanded  : {result.nodes_expanded}")
    print(f"Max Frontier    : {result.max_frontier_size}")
    print(f"Runtime         : {result.runtime_ms:.4f} ms")

    print(f"Path Length     : {len(result.path)}")

print("\n==========================================")