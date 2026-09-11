class ReservationTable:

    def __init__(self):

        # Key:
        # (row, col, time)

        # Value:
        # robot_id

        self.reservations = {}

    # ---------------------------------------------------------
    # Reserve a cell at a specific time
    # ---------------------------------------------------------

    def reserve(
        self,
        position,
        time_step,
        robot_id
    ):

        key = (
            position[0],
            position[1],
            time_step
        )

        self.reservations[key] = robot_id

    # ---------------------------------------------------------
    # Check whether a cell is already reserved
    # ---------------------------------------------------------

    def is_reserved(
        self,
        position,
        time_step,
        robot_id=None
    ):

        key = (
            position[0],
            position[1],
            time_step
        )

        if key not in self.reservations:
            return False

        # Allow the same robot to access
        # its own reservation.
        if (
            robot_id is not None
            and self.reservations[key] == robot_id
        ):
            return False

        return True

    # ---------------------------------------------------------
    # Reserve an entire path
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Clear all reservations
    # ---------------------------------------------------------

    def clear(self):

        self.reservations.clear()

    # ---------------------------------------------------------
    # Get reservation owner
    # ---------------------------------------------------------

    def get_owner(
        self,
        position,
        time_step
    ):

        key = (
            position[0],
            position[1],
            time_step
        )

        return self.reservations.get(
            key
        )