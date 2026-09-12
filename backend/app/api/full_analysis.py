from fastapi import APIRouter

from ..models.warehouse import Warehouse
from ..recommender.features import WarehouseFeatures
from ..recommender.benchmark import AlgorithmBenchmark
from ..recommender.scorer import AlgorithmScorer
from ..multi_agent.planner import MultiAgentPlanner
from ..simulation.engine import SimulationEngine


router = APIRouter(
    prefix="/analysis",
    tags=["Complete Analysis"]
)


from fastapi import APIRouter

from ..models.warehouse import Warehouse
from ..recommender.features import WarehouseFeatures
from ..recommender.benchmark import AlgorithmBenchmark
from ..recommender.scorer import AlgorithmScorer
from ..multi_agent.planner import MultiAgentPlanner
from ..simulation.engine import SimulationEngine


router = APIRouter(
    prefix="/analysis",
    tags=["Complete Analysis"]
)


@router.post("/run")
def run_complete_analysis(warehouse: Warehouse):

    # =====================================================
    # 1. Extract warehouse features
    # =====================================================

    feature_extractor = WarehouseFeatures(warehouse)

    features = feature_extractor.extract_all()

    # =====================================================
    # 2. Benchmark A*, UCS and GBFS
    # =====================================================

    benchmark = AlgorithmBenchmark(warehouse)

    benchmark_results = benchmark.run()

    benchmark_summary = benchmark.summary(
        benchmark_results
    )

    # =====================================================
    # 3. Generate recommendation
    # =====================================================

    scorer = AlgorithmScorer(
        features,
        benchmark_results
    )

    recommendation = scorer.calculate_scores()

    # =====================================================
    # 4. Multi-agent planning
    # =====================================================

    planner = MultiAgentPlanner(warehouse)

    planning_result = planner.plan()

    # =====================================================
    # 5. Simulation
    # =====================================================

    simulation_result = None

    if planning_result["success"]:

        engine = SimulationEngine()

        robot_simulations = []

        for robot_id, path in planning_result["paths"].items():

            if path is None:
                continue

            steps = engine.simulate_path(path)

            robot_simulations.append({
                "robot_id": robot_id,
                "steps": steps
            })

        simulation_result = {
            "success": True,
            "makespan": planning_result["makespan"],
            "robots": robot_simulations
        }

    # =====================================================
    # 6. Return complete result
    # =====================================================

    return {
        "success": True,

        "warehouse": {
            "name": warehouse.name,
            "rows": warehouse.rows,
            "cols": warehouse.cols
        },

        "features": features,

        "benchmark": {
            "results": benchmark_results,
            "summary": benchmark_summary
        },

        "recommendation": recommendation,

        "multi_agent": {
            "success": planning_result["success"],
            "assignments": planning_result["assignments"],
            "makespan": planning_result["makespan"]
        },

        "simulation": simulation_result
    }

    # =====================================================
    # 1. Extract warehouse features
    # =====================================================

    feature_extractor = WarehouseFeatures(warehouse)

    features = feature_extractor.extract_all()

    # =====================================================
    # 2. Benchmark A*, UCS and GBFS
    # =====================================================

    benchmark = AlgorithmBenchmark(warehouse)

    benchmark_results = benchmark.run()

    benchmark_summary = benchmark.summary(
        benchmark_results
    )

    # =====================================================
    # 3. Generate recommendation
    # =====================================================

    scorer = AlgorithmScorer(
        features,
        benchmark_results
    )

    recommendation = scorer.calculate_scores()

    # =====================================================
    # 4. Multi-agent planning
    # =====================================================

    planner = MultiAgentPlanner(warehouse)

    planning_result = planner.plan()

    # =====================================================
    # 5. Simulation
    # =====================================================

    simulation_result = None

    if planning_result["success"]:

        engine = SimulationEngine()

        robot_simulations = []

        for robot_id, path in planning_result["paths"].items():

            if path is None:
                continue

            steps = engine.simulate_path(path)

            robot_simulations.append({
                "robot_id": robot_id,
                "steps": steps
            })

        simulation_result = {
            "success": True,
            "makespan": planning_result["makespan"],
            "robots": robot_simulations
        }

    # =====================================================
    # 6. Return complete result
    # =====================================================

    return {
        "success": True,

        "warehouse": {
            "name": warehouse.name,
            "rows": warehouse.rows,
            "cols": warehouse.cols
        },

        "features": features,

        "benchmark": {
            "results": benchmark_results,
            "summary": benchmark_summary
        },

        "recommendation": recommendation,

        "multi_agent": {
            "success": planning_result["success"],
            "assignments": planning_result["assignments"],
            "makespan": planning_result["makespan"]
        },

        "simulation": simulation_result
    }