class CollisionDetector:

    def __init__(self, reservation_table):

        self.reservations = reservation_table

    # ---------------------------------------------------------
    # Check whether a move is safe
    # ---------------------------------------------------------

    def is_move_safe(
        self,
        current,
        next_position,
        next_time,
        robot_id
    ):

        # ---------------------------------------------
        # 1. Vertex collision
        # ---------------------------------------------

        if self.reservations.is_reserved(
            next_position,
            next_time,
            robot_id
        ):

            return False

        # ---------------------------------------------
        # 2. Edge collision
        #
        # Robot A:
        # (1,1) → (1,2)
        #
        # Robot B:
        # (1,2) → (1,1)
        #
        # They swap positions and collide.
        # ---------------------------------------------

        other_robot = (
            self.reservations.get_owner(
                current,
                next_time
            )
        )

        if other_robot is not None:

            previous_owner = (
                self.reservations.get_owner(
                    next_position,
                    next_time - 1
                )
            )

            if (
                previous_owner == other_robot
            ):

                return False

        return True