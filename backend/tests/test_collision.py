from app.multi_agent.reservation import ReservationTable
from app.multi_agent.collision import CollisionDetector
from app.models.warehouse import Position


def test_vertex_collision():

    table = ReservationTable()

    table.reserve(
        Position(row=1, col=1),
        time_step=1,
        robot_id=1
    )

    detector = CollisionDetector(table)

    safe = detector.is_move_safe(
        current=Position(row=1, col=0),
        next_position=Position(row=1, col=1),
        next_time=1,
        robot_id=2
    )

    assert safe is False


def test_edge_swap_collision():

    table = ReservationTable()

    path_robot_1 = [
        Position(row=1, col=0),
        Position(row=1, col=1)
    ]

    table.reserve_path(
        path_robot_1,
        robot_id=1
    )

    detector = CollisionDetector(table)

    safe = detector.is_move_safe(
        current=Position(row=1, col=1),
        next_position=Position(row=1, col=0),
        next_time=1,
        robot_id=2
    )

    assert safe is False


def test_safe_move():

    table = ReservationTable()

    detector = CollisionDetector(table)

    safe = detector.is_move_safe(
        current=Position(row=0, col=0),
        next_position=Position(row=0, col=1),
        next_time=1,
        robot_id=1
    )

    assert safe is True