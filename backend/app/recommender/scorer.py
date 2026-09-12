class AlgorithmScorer:

    ALGORITHMS = ["A*", "UCS", "GBFS"]

    def __init__(self, features, benchmark_results):

        self.features = features
        self.results = benchmark_results

    # ---------------------------------------------------------
    # Main scoring function
    # ---------------------------------------------------------

    def calculate_scores(self):
        metrics = self._aggregate_metrics()

        if not metrics:
            return {
                "scores": {},
                "recommended_algorithm": None,
                "reason": "No successful benchmark results available.",
                "features": self.features,
                "benchmark_metrics": {}
            }

        costs = [
            data["avg_path_cost"]
            for data in metrics.values()
        ]

        nodes = [
            data["avg_nodes_expanded"]
            for data in metrics.values()
        ]

        runtimes = [
            data["avg_runtime_ms"]
            for data in metrics.values()
        ]

        min_cost = min(costs)
        min_nodes = min(nodes)
        min_runtime = min(runtimes)

        # ------------------------------------------------------
        # WAREHOUSE STRUCTURE
        # ------------------------------------------------------

        obstacle_density = self.features.get(
            "obstacle_density", 0
        )

        branching = self.features.get(
            "avg_branching_factor", 2
        )

        dead_end_ratio = self.features.get(
            "dead_end_ratio", 0
        )

        cost_variance = self.features.get(
            "edge_cost_variance", 0
        )

        heuristic_quality = self.features.get(
            "heuristic_quality", 0
        )

        # ------------------------------------------------------
        # NORMALIZED ENVIRONMENT DIFFICULTY
        # ------------------------------------------------------

        complexity = (
            obstacle_density * 0.40
            + dead_end_ratio * 0.30
            + max(0, 3 - branching) / 3 * 0.30
        )

        cost_pressure = min(
            cost_variance / 5,
            1
        )

        final_scores = {}

        for algorithm, data in metrics.items():

            cost_score = self._relative_score(
                min_cost,
                data["avg_path_cost"]
            )

            node_score = self._relative_score(
                min_nodes,
                data["avg_nodes_expanded"]
            )

            runtime_score = self._relative_score(
                min_runtime,
                data["avg_runtime_ms"]
            )

            # --------------------------------------------------
            # DYNAMIC WEIGHTS
            # --------------------------------------------------

            cost_weight = (
                0.40
                + cost_pressure * 0.15
            )

            node_weight = (
                0.30
                + complexity * 0.10
            )

            runtime_weight = (
                1
                - cost_weight
                - node_weight
            )

            score = (
                cost_score * cost_weight
                + node_score * node_weight
                + runtime_score * runtime_weight
            ) * 100

            # --------------------------------------------------
            # STRUCTURE-AWARE ALGORITHM BONUS
            # --------------------------------------------------

           # --------------------------------------------------
# STRUCTURE-AWARE ALGORITHM BONUS
# --------------------------------------------------

            # --------------------------------------------------
            # STRUCTURE-AWARE ALGORITHM BONUS
            # --------------------------------------------------

            if algorithm == "A*":
                # A* is preferred for complex warehouse layouts.
                score += complexity * 15

                # Strong heuristic quality benefits A*.
                score += heuristic_quality * 5

            elif algorithm == "UCS":
                # UCS is preferred when traversal costs vary.
                score += cost_pressure * 10

            elif algorithm == "GBFS":
                # GBFS is preferred mainly for simple/open layouts.
                simplicity = 1 - complexity
                score += simplicity * 3

            # Keep every algorithm's score between 0 and 100.
            score = min(
                max(score, 0),
                100
            )

            final_scores[algorithm] = round(
                score,
                2
            )

        recommended_algorithm = max(
            final_scores,
            key=final_scores.get
        )

        reason = self._generate_reason(
            recommended_algorithm,
            metrics,
            final_scores
        )

        return {
            "scores": final_scores,
            "recommended_algorithm": recommended_algorithm,
            "reason": reason,
            "features": self.features,
            "benchmark_metrics": metrics
        }

    # ---------------------------------------------------------
    # Aggregate results across robots
    # ---------------------------------------------------------

    def _aggregate_metrics(self):

        grouped = {}

        for result in self.results:

            if not result["found"]:
                continue

            algorithm = result["algorithm"]

            if algorithm not in grouped:
                grouped[algorithm] = {
                    "costs": [],
                    "nodes": [],
                    "runtimes": []
                }

            grouped[algorithm]["costs"].append(
                result["path_cost"]
            )

            grouped[algorithm]["nodes"].append(
                result["nodes_expanded"]
            )

            grouped[algorithm]["runtimes"].append(
                result["runtime_ms"]
            )

        aggregated = {}

        for algorithm, data in grouped.items():

            aggregated[algorithm] = {

                "avg_path_cost":
                    self._average(data["costs"]),

                "avg_nodes_expanded":
                    self._average(data["nodes"]),

                "avg_runtime_ms":
                    self._average(data["runtimes"])
            }

        return aggregated

    # ---------------------------------------------------------
    # Convert a metric into a 0-1 relative score
    # ---------------------------------------------------------

    def _relative_score(self, best, actual):

        if actual <= 0:
            return 1

        if best <= 0:
            return 0

        score = best / actual

        return min(
            max(score, 0),
            1
        )

    # ---------------------------------------------------------
    # Average helper
    # ---------------------------------------------------------

    def _average(self, values):

        if not values:
            return 0

        return sum(values) / len(values)

    # ---------------------------------------------------------
    # Human-readable explanation
    # ---------------------------------------------------------

    def _generate_reason(
        self,
        algorithm,
        metrics,
        scores
    ):

        data = metrics[algorithm]

        avg_cost = data["avg_path_cost"]

        avg_nodes = data["avg_nodes_expanded"]

        avg_runtime = data["avg_runtime_ms"]

        reason = (
            f"{algorithm} achieved the highest overall "
            f"score of {scores[algorithm]}/100. "
        )

        reason += (
            f"Its average path cost was "
            f"{avg_cost:.2f}, with "
            f"{avg_nodes:.1f} nodes expanded "
            f"and an average runtime of "
            f"{avg_runtime:.4f} ms."
        )

        return reason