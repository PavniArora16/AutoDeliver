from fastapi import FastAPI

from .api.pathfinding import router as pathfinding_router
from .api.warehouse import router as warehouse_router
from .api.recommendation import router as recommendation_router


app = FastAPI(
    title="AutoDeliver",
    description="Intelligent Multi-Agent Warehouse Robot Simulator",
    version="1.0.0"
)


app.include_router(
    pathfinding_router
)

app.include_router(
    warehouse_router
)

app.include_router(
    recommendation_router
)


@app.get("/")
def home():

    return {
        "message": "AutoDeliver backend is running!",
        "version": "1.0.0"
    }