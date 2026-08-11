from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class Spacing:
    column_pitch: float
    row_pitch: float


@dataclass(slots=True, frozen=True)
class PositiveDirection:
    x: str
    y: str
    z: str


@dataclass(slots=True, frozen=True)
class Origin:
    type: str
    positive: PositiveDirection


@dataclass(slots=True, frozen=True)
class Stagger:
    column: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Angles:
    splay: float = 0.0
    tenting: float = 0.0
    rotation: float = 0.0


@dataclass(slots=True, frozen=True)
class Transform:
    angles: Angles


@dataclass(slots=True, frozen=True)
class Geometry:
    spacing: Spacing
    origin: Origin
    stagger: Stagger
    transform: Transform