from ..models.simulation import SimulationStep


class SimulationEngine:

    def simulate_path(
        self,
        path,
        initial_battery=100.0,
        battery_capacity=100.0,
        energy_per_step=1.0,
        charging_stations=None,
        goal=None
    ):

        if charging_stations is None:
            charging_stations = []

        steps = []
        battery = initial_battery

        for time_step, position in enumerate(path):

            is_charging = any(
                position == station
                for station in charging_stations
            )

            is_goal_reached = (
                goal is not None
                and position == goal
            )

            if is_charging:

                battery = battery_capacity
                status = "charging"

            else:

                if time_step > 0:
                    battery = max(
                        0.0,
                        battery - energy_per_step
                    )

                if is_goal_reached:
                    status = "completed"

                elif (
                    time_step > 0
                    and position == path[time_step - 1]
                ):
                    status = "waiting"

                else:
                    status = "moving"

            if battery_capacity > 0:
                battery_percentage = (
                    battery / battery_capacity
                ) * 100
            else:
                battery_percentage = 0.0

            steps.append(
                SimulationStep(
                    time_step=time_step,
                    position=position,
                    battery_level=round(battery, 2),
                    battery_percentage=round(
                        battery_percentage,
                        2
                    ),
                    status=status,
                    is_charging=is_charging,
                    is_goal_reached=is_goal_reached
                )
            )

        return steps

    # =========================================================
    # STEP-BY-STEP SIMULATION
    # =========================================================

    def simulate_step(
        self,
        position,
        time_step,
        battery,
        battery_capacity=100.0,
        energy_per_step=1.0,
        charging_stations=None,
        goal=None,
        previous_position=None
    ):

        if charging_stations is None:
            charging_stations = []

        # -----------------------------------------------------
        # Check charging station
        # -----------------------------------------------------

        is_charging = any(
            position == station
            for station in charging_stations
        )

        # -----------------------------------------------------
        # Check goal
        # -----------------------------------------------------

        is_goal_reached = (
            goal is not None
            and position == goal
        )

        # -----------------------------------------------------
        # Battery + status
        # -----------------------------------------------------

        if is_charging:

            battery = battery_capacity
            status = "charging"

        else:

            # Consume energy when robot moves
            if (
                time_step > 0
                and previous_position is not None
                and position != previous_position
            ):
                battery = max(
                    0.0,
                    battery - energy_per_step
                )

            if is_goal_reached:

                status = "completed"

            elif (
                previous_position is not None
                and position == previous_position
            ):

                status = "waiting"

            else:

                status = "moving"

        # -----------------------------------------------------
        # Battery percentage
        # -----------------------------------------------------

        if battery_capacity > 0:

            battery_percentage = (
                battery / battery_capacity
            ) * 100

        else:

            battery_percentage = 0.0

        # -----------------------------------------------------
        # Return one simulation step
        # -----------------------------------------------------

        return SimulationStep(
            time_step=time_step,
            position=position,
            battery_level=round(
                battery,
                2
            ),
            battery_percentage=round(
                battery_percentage,
                2
            ),
            status=status,
            is_charging=is_charging,
            is_goal_reached=is_goal_reached
        )