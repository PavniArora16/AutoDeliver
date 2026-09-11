# Four-direction movement:
# Up, Down, Left, Right

DIRECTIONS = [
    (-1, 0),  # Up
    (1, 0),   # Down
    (0, -1),  # Left
    (0, 1)    # Right
]


def is_inside(grid, row, col):
    """Check whether a position is inside the grid."""

    return (
        0 <= row < len(grid)
        and 0 <= col < len(grid[0])
    )


def is_walkable(grid, row, col):
    """Return True if the cell is not an obstacle."""

    return (
        is_inside(grid, row, col)
        and grid[row][col] != -1
    )


def get_neighbors(grid, position):
    """
    Return all walkable neighboring cells.

    Each result is:
        (neighbor_position, movement_cost)
    """

    row, col = position

    neighbors = []

    for dr, dc in DIRECTIONS:

        new_row = row + dr
        new_col = col + dc

        if is_walkable(grid, new_row, new_col):

            cost = grid[new_row][new_col]

            neighbors.append(
                ((new_row, new_col), cost)
            )

    return neighbors


def manhattan_distance(a, b):
    """Manhattan distance for 4-direction movement."""

    return abs(a[0] - b[0]) + abs(a[1] - b[1])