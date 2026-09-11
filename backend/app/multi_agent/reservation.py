class ReservationTable:

    def __init__(self):
        # (row, col, time) -> robot_id
        self.reservations = {}

    def reserve(
        self,
        position,
        time_step,
        robot_id
    ):
        key = (
            position.row,
            position.col,
            time_step
        )

        self.reservations[key] = robot_id

    def is_reserved(
        self,
        position,
        time_step,
        robot_id=None
    ):
        key = (
            position.row,
            position.col,
            time_step
        )

        if key not in self.reservations:
            return False

        # If the position belongs to the same robot,
        # it is not considered a collision.
        if robot_id is not None:
            return self.reservations[key] != robot_id

        return True

    def get_owner(
        self,
        position,
        time_step
    ):
        key = (
            position.row,
            position.col,
            time_step
        )

        return self.reservations.get(key)

    def reserve_path(
        self,
        path,
        robot_id
    ):
        for time_step, position in enumerate(path):
            self.reserve(
                position,
                time_step,
                robot_id
            )

    def clear(self):
        self.reservations.clear()