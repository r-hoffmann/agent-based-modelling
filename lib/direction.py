from enum import Enum


# 2: to top, 6: to bottom, 0: to right, 4: to left
class Direction(Enum):
    EAST = 0
    NORTH = 2
    WEST = 4
    SOUTH = 6
