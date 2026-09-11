from app.models.warehouse import Position, Robot
from app.simulation.battery import BatteryManager


def test_energy_required():

    robot = Robot(
        id=1,
        start=Position(row=0, col=0),
        battery_capacity=100,
        battery_level=100,
        energy_per_step=2
    )

    manager = BatteryManager(robot)

    path = [
        Position(row=0, col=0),
        Position(row=0, col=1),
        Position(row=0, col=2),
        Position(row=0, col=3)
    ]

    assert manager.energy_required(path) == 6


def test_battery_consumption():

    robot = Robot(
        id=1,
        start=Position(row=0, col=0),
        battery_capacity=100,
        battery_level=100,
        energy_per_step=2
    )

    manager = BatteryManager(robot)

    manager.consume(3)

    assert robot.battery_level == 94


def test_low_battery():

    robot = Robot(
        id=1,
        start=Position(row=0, col=0),
        battery_capacity=100,
        battery_level=15
    )

    manager = BatteryManager(robot)

    assert manager.is_low() is True


def test_charging():

    robot = Robot(
        id=1,
        start=Position(row=0, col=0),
        battery_capacity=100,
        battery_level=15
    )

    manager = BatteryManager(robot)

    manager.charge()

    assert robot.battery_level == 100
    assert robot.status == "charged"