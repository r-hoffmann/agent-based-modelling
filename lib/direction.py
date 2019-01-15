from enum import Enum


# 2: to top, 6: to bottom, 0: to right, 4: to left
class Direction(Enum):
    EAST = 0
    NORTH_EAST = 1
    NORTH = 2
    NORTH_WEST = 3
    WEST = 4
    SOUTH_WEST = 5
    SOUTH = 6
    SOUTH_EAST = 7
