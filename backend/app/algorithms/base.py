from dataclasses import dataclass, field
from typing import List, Tuple


Position = Tuple[int, int]


@dataclass
class PathResult:

    algorithm: str

    found: bool

    path: List[Position] = field(default_factory=list)

    path_cost: float = 0

    nodes_expanded: int = 0

    max_frontier_size: int = 0

    runtime_ms: float = 0

    # Order in which cells were explored
    explored: List[Position] = field(default_factory=list)


class PathfindingAlgorithm:

    name = "Base"

    def find_path(
        self,
        grid,
        start: Position,
        goal: Position
    ) -> PathResult:

        raise NotImplementedError