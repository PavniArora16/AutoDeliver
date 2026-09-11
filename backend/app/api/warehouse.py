from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

from ..models.warehouse import Warehouse


router = APIRouter(
    prefix="/warehouse",
    tags=["Warehouse"]
)


@router.get("/sample")
def get_sample_warehouse():

    file_path = (
        Path(__file__).resolve()
        .parents[2]
        / "data"
        / "generated"
        / "sample_warehouse.json"
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Sample warehouse not found"
        )

    with open(file_path, "r") as file:

        data = json.load(file)

    warehouse = Warehouse(**data)

    return warehouse


@router.post("/validate")
def validate_warehouse(
    warehouse: Warehouse
):

    if warehouse.rows <= 0 or warehouse.cols <= 0:
        raise HTTPException(
            status_code=400,
            detail="Warehouse must have at least 1 row and 1 column"
        )

    # Check grid dimensions
    if len(warehouse.grid) != warehouse.rows:

        raise HTTPException(
            status_code=400,
            detail="Number of grid rows does not match 'rows'"
        )

    for row in warehouse.grid:

        if len(row) != warehouse.cols:

            raise HTTPException(
                status_code=400,
                detail="Grid column count does not match 'cols'"
            )

    # Check robot positions
    for robot in warehouse.robots:

        if warehouse.grid[
            robot.start.row
        ][
            robot.start.col
        ] == -1:

            raise HTTPException(
                status_code=400,
                detail=f"Robot {robot.id} starts on an obstacle"
            )

    return {
        "valid": True,
        "message": "Warehouse is valid",
        "rows": warehouse.rows,
        "cols": warehouse.cols,
        "robots": len(warehouse.robots),
        "goals": len(warehouse.goals),
        "charging_stations": len(
            warehouse.charging_stations
        )
    }