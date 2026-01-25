from dataclasses import dataclass
from typing import Iterable

from shadow_compass.loc import Loc
from shadow_compass.schema.condition import Condition
from shadow_compass.schema.enums import LootType, LootItemType
from shadow_compass.schema.reference import Reference, CardReference, EventReference, LootReference, RiteReference


@dataclass(frozen=True)
class LootItem:
    num: int
    id: int
    type: LootItemType
    weight: int
    condition: tuple[Condition, ...] = ()

    def item_references(self) -> Iterable[Reference]:
        match self.type:
            case LootItemType.CARD:
                yield CardReference(self.id)
            case LootItemType.EVENT:
                yield EventReference(self.id)
            case LootItemType.LOOT:
                yield LootReference(self.id)
            case LootItemType.RITE:
                yield RiteReference(self.id)

    def condition_references(self) -> Iterable[Reference]:
        for condition in self.condition:
            yield from condition.references()


@dataclass(frozen=True)
class Loot:
    id: int
    name: str
    repeat: int
    type: LootType
    item: tuple[LootItem, ...]

    @property
    def name_(self) -> Loc:
        return Loc(self.name, f'loot_{self.id}_name')

    def item_references(self) -> Iterable[Reference]:
        for item in self.item:
            yield from item.item_references()

    def condition_references(self) -> Iterable[Reference]:
        for item in self.item:
            yield from item.condition_references()

    def __repr__(self) -> str:
        return f'<Loot id={self.id} name={self.name}>'