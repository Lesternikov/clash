from enum import Enum

class Tile(Enum):
    EMPTY = "."
    WALL = "X"
    TRAP = "T"
    TREASURE = "$"
    LOCK = "C"
