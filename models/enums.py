# models/enums.py
from enum import Enum


class Hand(Enum):
    LEFT = "left"
    RIGHT = "right"


class Finger(Enum):
    PINKY = "pinky"
    RING = "ring"
    MIDDLE = "middle"
    INDEX = "index"
    THUMB = "thumb"


class Row(Enum):
    TOP = "top"
    HOME = "home"
    BOTTOM = "bottom"
    THUMB = "thumb"


class Layer(Enum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3


class RollDirection(Enum):
    NONE = "none"
    INWARD = "inward"
    OUTWARD = "outward"