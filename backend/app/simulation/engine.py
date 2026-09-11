from ..models.simulation import SimulationStep


class SimulationEngine:

    def simulate_path(self, path):

        steps = []

        for time_step, position in enumerate(path):

            steps.append(
                SimulationStep(
                    time_step=time_step,
                    position=position
                )
            )

        return steps