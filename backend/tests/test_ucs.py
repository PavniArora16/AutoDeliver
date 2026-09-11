from app.algorithms.ucs import UCS


def test_ucs_finds_path():

    grid = [
        [1, 1, 1, 1, 1],
        [1, -1, -1, -1, 1],
        [1, 1, 1, 1, 1],
        [1, -1, 1, -1, 1],
        [1, 1, 1, 1, 1]
    ]

    start = (0, 0)
    goal = (4, 4)

    algorithm = UCS()

    result = algorithm.find_path(
        grid,
        start,
        goal
    )

    assert result.found is True

    assert result.path[0] == start

    assert result.path[-1] == goal

    assert result.path_cost > 0