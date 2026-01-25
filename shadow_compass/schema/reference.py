from dataclasses import dataclass


@dataclass(frozen=True)
class Reference:
    pass


@dataclass(frozen=True)
class CardReference(Reference):
    id: int


@dataclass(frozen=True)
class EndingReference(Reference):
    id: int


@dataclass(frozen=True)
class EventReference(Reference):
    id: int


@dataclass(frozen=True)
class LootReference(Reference):
    id: int


@dataclass(frozen=True)
class RiteReference(Reference):
    id: int


@dataclass(frozen=True)
class TagReference(Reference):
    id: str


@dataclass(frozen=True)
class UpgradeReference(Reference):
    id: int
