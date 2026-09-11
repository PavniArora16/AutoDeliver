from app.multi_agent.reservation import ReservationTable
from app.multi_agent.collision import CollisionDetector
from app.models.warehouse import Position


def test_vertex_collision():
    reservation = ReservationTable()

    position = Position(row=2, col=2)

    reservation.reserve(
        position,
        time_step=3,
        robot_id=1
    )

    detector = CollisionDetector(reservation)

    # Robot 2 tries to move into a cell
    # already reserved by Robot 1
    assert not detector.is_move_safe(
        current=Position(row=2, col=1),
        next_position=position,
        next_time=3,
        robot_id=2
    )


def test_no_vertex_collision():
    reservation = ReservationTable()

    position = Position(row=2, col=2)

    reservation.reserve(
        position,
        time_step=3,
        robot_id=1
    )

    detector = CollisionDetector(reservation)

    other_position = Position(row=2, col=3)

    # Robot 2 moves to a different cell
    assert detector.is_move_safe(
        current=Position(row=2, col=2),
        next_position=other_position,
        next_time=3,
        robot_id=2
    )