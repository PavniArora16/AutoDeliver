class BatteryManager:

    LOW_BATTERY_THRESHOLD = 20.0

    def __init__(self, robot):
        self.robot = robot

    # ---------------------------------------------
    # Calculate energy required for a path
    # ---------------------------------------------

    def energy_required(self, path):

        if not path:
            return 0.0

        movements = len(path) - 1

        return movements * self.robot.energy_per_step

    # ---------------------------------------------
    # Check if robot has enough battery
    # ---------------------------------------------

    def can_complete(self, path):

        required = self.energy_required(path)

        return self.robot.battery_level >= required

    # ---------------------------------------------
    # Consume battery after movement
    # ---------------------------------------------

    def consume(self, steps=1):

        energy_used = (
            steps * self.robot.energy_per_step
        )

        self.robot.battery_level = max(
            0.0,
            self.robot.battery_level - energy_used
        )

        return energy_used

    # ---------------------------------------------
    # Low battery check
    # ---------------------------------------------

    def is_low(self):

        return (
            self.robot.battery_level
            <= self.LOW_BATTERY_THRESHOLD
        )

    # ---------------------------------------------
    # Charge robot
    # ---------------------------------------------

    def charge(self):

        self.robot.battery_level = (
            self.robot.battery_capacity
        )

        self.robot.status = "charged"

        return self.robot.battery_level