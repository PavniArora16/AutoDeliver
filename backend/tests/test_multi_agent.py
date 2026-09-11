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