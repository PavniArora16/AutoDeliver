from fastapi import FastAPI

from .api.pathfinding import router as pathfinding_router
from .api.warehouse import router as warehouse_router
from .api.recommendation import router as recommendation_router
from .api.simulation import router as simulation_router
from fastapi.middleware.cors import CORSMiddleware
from .api.full_analysis import router as full_analysis_router

app = FastAPI(
    title="AutoDeliver",
    description="Intelligent Multi-Agent Warehouse Robot Simulator",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(simulation_router)

app.include_router(
    pathfinding_router
)
app.include_router(full_analysis_router)

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
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AutoDeliver Backend"
    }