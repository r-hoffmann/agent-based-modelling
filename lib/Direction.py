from enum import IntEnum


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
        """
        Get the opposite direction
        :return: Direction
        """
        if self == self.EAST:
            return self.WEST
        elif self == self.WEST:
            return self.EAST
        elif self == self.NORTH:
            return self.SOUTH
        elif self == self.SOUTH:
            return self.NORTH

    def is_opposite(self, c):
        """
        Check if two directions are the opposite
        :param c: Other direction
        :return: Boolean
        """
        if self.opposite() == c:
            return True
        return False

    def is_equal(self, c):
        """
        Check if two direction are the same
        :param c: Other direction
        :return: Boolean
        """
        if self == c:
            return True
        return False
