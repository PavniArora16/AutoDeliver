from fastapi import APIRouter

from ..models.warehouse import Warehouse

from ..recommender.features import WarehouseFeatures
from ..recommender.benchmark import AlgorithmBenchmark
from ..recommender.scorer import AlgorithmScorer


router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"]
)


@router.post("/analyze")
def analyze_warehouse(
    warehouse: Warehouse
):

    # =============================================
    # 1. Extract warehouse features
    # =============================================

    feature_extractor = WarehouseFeatures(
        warehouse
    )

    features = (
        feature_extractor.extract_all()
    )

    # =============================================
    # 2. Benchmark algorithms
    # =============================================

    benchmark = AlgorithmBenchmark(
        warehouse
    )

    benchmark_results = benchmark.run()

    # =============================================
    # 3. Create benchmark summary
    # =============================================

    benchmark_summary = (
        benchmark.summary(
            benchmark_results
        )
    )

    # =============================================
    # 4. Score algorithms
    # =============================================

    scorer = AlgorithmScorer(
        features,
        benchmark_results
    )

    recommendation = (
        scorer.calculate_scores()
    )

    # =============================================
    # 5. Return everything
    # =============================================

    return {

        "warehouse": warehouse.name,

        "features": features,

        "benchmark": benchmark_results,

        "benchmark_summary":
            benchmark_summary,

        "recommendation":
            recommendation
    }