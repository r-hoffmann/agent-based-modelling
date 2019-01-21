from enum import IntEnum


# 2: to top, 6: to bottom, 0: to right, 4: to left
class Direction(IntEnum):
    EAST = 0
    NORTH_EAST = 1
    NORTH = 2
    NORTH_WEST = 3
    WEST = 4
    SOUTH_WEST = 5
    SOUTH = 6
    SOUTH_EAST = 7

    def opposite(self):
        if self == self.EAST:
            return self.WEST
        elif self == self.WEST:
            return self.EAST
        elif self == self.NORTH:
            return self.SOUTH
        elif self == self.SOUTH:
            return self.NORTH

    def is_opposite(self, c):
        if self.opposite() == c:
            return True
        return False

    def is_equal(self, c):
        if self == c:
            return True
        return False

