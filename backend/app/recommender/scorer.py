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
                "reason": "No successful benchmark results available."
            }

        # -----------------------------------------------------
        # Find reference values
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # Calculate final scores
        # -----------------------------------------------------

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

            # -------------------------------------------------
            # Dynamic weighting
            # -------------------------------------------------

            cost_variance = self.features.get(
                "edge_cost_variance",
                0
            )

            heuristic_quality = self.features.get(
                "heuristic_quality",
                0
            )

            # Path cost becomes more important when
            # warehouse movement costs vary significantly.
            cost_weight = 0.40

            if cost_variance > 1:
                cost_weight = 0.50

            # Speed/efficiency receives the remaining weight.
            node_weight = 0.35

            runtime_weight = (
                1
                - cost_weight
                - node_weight
            )

            # A high-quality heuristic makes A*/GBFS
            # more useful, so slightly reward them.
            heuristic_bonus = 0

            if algorithm in ["A*", "GBFS"]:
                heuristic_bonus = (
                    heuristic_quality * 5
                )

            score = (
                cost_score * cost_weight
                +
                node_score * node_weight
                +
                runtime_score * runtime_weight
            ) * 100

            score += heuristic_bonus

            # Keep score between 0 and 100
            score = min(
                max(score, 0),
                100
            )

            final_scores[algorithm] = round(
                score,
                2
            )

        # -----------------------------------------------------
        # Select winner
        # -----------------------------------------------------

        recommended_algorithm = max(
            final_scores,
            key=final_scores.get
        )

        # -----------------------------------------------------
        # Generate explanation
        # -----------------------------------------------------

        reason = self._generate_reason(
            recommended_algorithm,
            metrics,
            final_scores
        )

        return {
            "scores": final_scores,
            "recommended_algorithm":
                recommended_algorithm,
            "reason": reason
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