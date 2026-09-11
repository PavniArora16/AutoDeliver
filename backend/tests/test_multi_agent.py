from app.models.warehouse import (
    Position,
    Robot,
    Warehouse
)

from app.multi_agent.planner import MultiAgentPlanner


def test_multi_agent_planner():

    warehouse = Warehouse(
        name="Test Warehouse",
        rows=5,
        cols=5,

        grid=[
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ],

        robots=[
            Robot(
                id=1,
                start=Position(row=0, col=0)
            ),

            Robot(
                id=2,
                start=Position(row=4, col=0)
            )
        ],

        goals=[
            Position(row=4, col=4),
            Position(row=0, col=4)
        ]
    )

    planner = MultiAgentPlanner(warehouse)

    result = planner.plan()

    print("\n================================")
    print("MULTI-AGENT RESULT")
    print("================================")
    print(result)
    print("================================\n")

    assert result["success"] is True
    assert result["paths"][1] is not None
    assert result["paths"][2] is not None

    assert result["assignments"][1] is not None
    assert result["assignments"][2] is not None


def test_multi_agent_paths_are_collision_free():

    warehouse = Warehouse(
        name="Collision Test",
        rows=5,
        cols=5,

        grid=[
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ],

        robots=[
            Robot(
                id=1,
                start=Position(row=2, col=0)
            ),
            Robot(
                id=2,
                start=Position(row=2, col=4)
            )
        ],

        goals=[
            Position(row=2, col=4),
            Position(row=2, col=0)
        ]
    )

    planner = MultiAgentPlanner(warehouse)

    result = planner.plan()

    assert result["success"] is True

    path1 = result["paths"][1]
    path2 = result["paths"][2]

    assert path1 is not None
    assert path2 is not None

    max_time = max(len(path1), len(path2))

    for t in range(max_time):
        pos1 = path1[t] if t < len(path1) else path1[-1]
        pos2 = path2[t] if t < len(path2) else path2[-1]

        assert pos1 != pos2