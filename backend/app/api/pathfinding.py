from fastapi import APIRouter, HTTPException

from ..models.pathfinding import PathfindingRequest

from ..algorithms.astar import AStar
from ..algorithms.ucs import UCS
from ..algorithms.gbfs import GBFS


router = APIRouter(
    prefix="/pathfinding",
    tags=["Pathfinding"]
)


@router.post("/run")
def run_pathfinding(request: PathfindingRequest):

    # Convert request positions into tuples
    start = (
        request.start.row,
        request.start.col
    )

    goal = (
        request.goal.row,
        request.goal.col
    )

    # Select algorithm
    if request.algorithm == "astar":

        algorithm = AStar()

    elif request.algorithm == "ucs":

        algorithm = UCS()

    elif request.algorithm == "gbfs":

        algorithm = GBFS()

    else:

        raise HTTPException(
            status_code=400,
            detail="Invalid algorithm"
        )

    # Run algorithm
    result = algorithm.find_path(
        request.grid,
        start,
        goal
    )

    # Convert PathResult to JSON-friendly format
    return {
        "algorithm": result.algorithm,
        "found": result.found,
        "path": result.path,
        "path_cost": result.path_cost,
        "nodes_expanded": result.nodes_expanded,
        "max_frontier_size": result.max_frontier_size,
        "runtime_ms": round(
            result.runtime_ms,
            4
        ),
        "explored": result.explored
    }