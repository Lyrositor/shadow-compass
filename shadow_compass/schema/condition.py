from abc import ABC
from dataclasses import dataclass
from typing import Any, Self, TypeVar, Callable, Iterable

from shadow_compass.prop import prop
from shadow_compass.schema.common import CustomSchema, ParseFunc, COMPARATOR, COUNTER_ID, CARD_ID, TAG, SLOT
from shadow_compass.schema.enums import CardType, CardRarity, Comparator
from shadow_compass.schema.formula import FormulaElement
from shadow_compass.schema.reference import Reference, CardReference, RiteReference, LootReference, TagReference, \
    UpgradeReference
from shadow_compass.sudanjson import MultiDict


@dataclass(frozen=True)
class Condition(ABC):
    @property
    def cls(self) -> str:
        return self.__class__.__name__

    def references(self) -> Iterable[Reference]:
        yield from []


T = TypeVar('T', bound=Condition)

conditions: list[tuple[str, type[Condition]]] = []


def condition(pattern: str) -> Callable[[type[T]], type[T]]:
    def decorator(cls: type[T]) -> type[T]:
        conditions.append((pattern, cls))
        return cls
    return decorator


def _parse_comparator(data: Any) -> Comparator:
    return Comparator(data) if data else Comparator.EQ


@condition(r'!(?P<condition>.+)')
@dataclass(frozen=True)
class NotCondition(Condition, CustomSchema):
    condition: Condition

    def references(self) -> Iterable[Reference]:
        yield from self.condition.references()

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        conds = parse_func({data['condition']: data['value']}, tuple[Condition, ...], False)
        return cls(condition=conds[0]) if conds else None


@condition(r'all')
@dataclass(frozen=True)
class AllCondition(Condition):
    value: tuple[Condition, ...]

    def references(self) -> Iterable[Reference]:
        for cond in self.value:
            yield from cond.references()


@condition(r'any')
@dataclass(frozen=True)
class AnyCondition(Condition):
    value: tuple[Condition, ...]

    def references(self) -> Iterable[Reference]:
        for cond in self.value:
            yield from cond.references()


@condition(r'difficulty')
@dataclass(frozen=True)
class DifficultyCondition(Condition):
    value: int


@condition(r'is')
@dataclass(frozen=True)
class IsCondition(Condition):
    value: int

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.value)


@condition(r'(?:is_rite|rite)')
@dataclass(frozen=True)
class IsRiteCondition(Condition):
    value: int

    def references(self) -> Iterable[Reference]:
        yield RiteReference(self.value)


@condition(r'loot')
@dataclass(frozen=True)
class LootCondition(Condition):
    value: int

    def references(self) -> Iterable[Reference]:
        yield LootReference(self.value)


@condition(fr'rare{COMPARATOR}')
@dataclass(frozen=True)
class RarityCondition(Condition):
    value: CardRarity
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(r'type')
@dataclass(frozen=True)
class TypeCondition(Condition):
    value: CardType


@condition(fr'round{COMPARATOR}')
@dataclass(frozen=True)
class RoundCondition(Condition):
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'f:(?P<elements>[\w()./*+-]+) *({COMPARATOR})')
@dataclass(frozen=True)
class FormulaCondition(Condition):
    elements: tuple[FormulaElement, ...]
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        for element in self.elements:
            yield from element.references()


@condition(fr'r(?P<roll>\d+):(?P<elements>[\w()./*+-]+) *({COMPARATOR})')
@dataclass(frozen=True)
class RollCondition(Condition):
    roll: int
    elements: tuple[FormulaElement, ...]
    value: tuple[int, ...] | int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        for element in self.elements:
            yield from element.references()


@condition(fr'cost\.{CARD_ID}{COMPARATOR}')
@dataclass(frozen=True)
class CardCostCondition(Condition):
    card_id: int
    value: tuple[int, ...]|int
    comparator: Comparator = prop(parser=_parse_comparator)

    @property
    def is_multi_value(self) -> bool:
        return isinstance(self.value, tuple) and len(self.value) > 1

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)


@condition(fr'counter\.{COUNTER_ID}{COMPARATOR}')
@dataclass(frozen=True)
class CounterCondition(Condition):
    counter_id: int
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'global_counter\.{COUNTER_ID}{COMPARATOR}')
@dataclass(frozen=True)
class GlobalCounterCondition(Condition):
    counter_id: int
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'have\.{CARD_ID}{COMPARATOR}')
@dataclass(frozen=True)
class HaveCardCondition(Condition):
    card_id: int
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)


@condition(fr'have\.{CARD_ID}\.lifetime{COMPARATOR}(?P<count>\d+)\.count')
@dataclass(frozen=True)
class HaveCardLifetimeCondition(Condition):
    card_id: int
    count: int
    value: int = prop(assert_equals=1)
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)


@condition(fr'have\.{CARD_ID}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class HaveCardTagCondition(Condition):
    card_id: int
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)
        yield TagReference(self.tag)


@condition(fr'have\.char\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class HaveCharTagCondition(Condition):
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'have\.sudan{COMPARATOR}')
@dataclass(frozen=True)
class HaveSudanCondition(Condition):
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'have\.sudan\.lifetime{COMPARATOR}(?P<count>\d+)\.count')
@dataclass(frozen=True)
class HaveSudanLifetimeCondition(Condition):
    count: int
    value: int = prop(assert_equals=1)
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'have\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class HaveTagCondition(Condition):
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'have\.{TAG.replace('tag', 'tagged')}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class HaveTaggedTagCondition(Condition):
    tagged: str
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tagged)
        yield TagReference(self.tag)


@condition(fr'hand_have\.{CARD_ID}{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveCardCondition(Condition):
    card_id: int
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)


@condition(fr'hand_have\.{CARD_ID}\.rare{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveCardRarityCondition(Condition):
    card_id: int
    value: CardRarity
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)


@condition(fr'hand_have\.{CARD_ID}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveCardWithTagCondition(Condition):
    card_id: int
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)
        yield TagReference(self.tag)


@condition(fr'hand_have\.sudan{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveSudanCondition(Condition):
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'hand_have\.{TAG}(?:\|{TAG.replace('tag', 'additional_tag')})?{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveTagCondition(Condition):
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)
    additional_tag: str | None = None

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'hand_have\.{TAG}\.rare{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveTagRarityCondition(Condition):
    tag: str
    value: CardRarity
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'hand_have\.{TAG.replace('tag', 'tagged')}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class HandHaveTaggedTagCondition(Condition):
    tagged: str
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tagged)
        yield TagReference(self.tag)


@condition(fr'sudan_pool_have\.sudan{COMPARATOR}')
@dataclass(frozen=True)
class SudanPoolHaveCondition(Condition):
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'table_have\.{CARD_ID}{COMPARATOR}\s*')
@dataclass(frozen=True)
class TableHaveCardCondition(Condition):
    card_id: int
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)


@condition(fr'table_have\.{CARD_ID}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class TableHaveCardTagCondition(Condition):
    card_id: int
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)
        yield TagReference(self.tag)


@condition(fr'table_have\.char\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class TableHaveCharTagCondition(Condition):
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'table_have\.sudan{COMPARATOR}')
@dataclass(frozen=True)
class TableHaveSudanCondition(Condition):
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'table_have\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class TableHaveTagCondition(Condition):
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'table_have\.{TAG.replace('tag', 'tagged')}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class TableHaveTaggedTagCondition(Condition):
    tagged: str
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tagged)
        yield TagReference(self.tag)


@condition(fr'tag_tips\.{TAG}')
@dataclass(frozen=True)
class TagTipsCondition(Condition):
    tag: str
    value: int = prop(assert_equals=1)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'cost\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class TagCostCondition(Condition):
    tag: str
    value: tuple[int, ...]|int
    comparator: Comparator = prop(parser=_parse_comparator)

    @property
    def is_multi_value(self) -> bool:
        return isinstance(self.value, tuple) and len(self.value) > 1

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(SLOT)
@dataclass(frozen=True)
class SlotCondition(Condition):
    slot: int
    value: int


@condition(fr'{SLOT}\.equip_slot:驯兽')
@dataclass(frozen=True)
class SlotHasAnimalHandlingCondition(Condition):
    slot: int
    value: int

    def references(self) -> Iterable[Reference]:
        yield TagReference('驯兽')


@condition(fr'{SLOT}\.is')
@dataclass(frozen=True)
class SlotIsCondition(Condition):
    slot: int
    value: int

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.value)


@condition(fr'{SLOT}\.rare{COMPARATOR}')
@dataclass(frozen=True)
class SlotRarityCondition(Condition):
    slot: int
    value: CardRarity
    comparator: Comparator = prop(parser=_parse_comparator)


@condition(fr'{SLOT}\.type')
@dataclass(frozen=True)
class SlotTypeCondition(Condition):
    slot: int
    value: CardType


@condition(fr'{SLOT}\.{TAG}{COMPARATOR}')
@dataclass(frozen=True)
class SlotTagCondition(Condition):
    slot: int
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'parent\.{TAG}')
@dataclass(frozen=True)
class ParentTagCondition(Condition):
    tag: str
    value: int

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'self\.{TAG}')
@dataclass(frozen=True)
class SelfTagCondition(Condition):
    tag: str
    value: int

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(fr'(?!!){TAG}{COMPARATOR}')
@dataclass(frozen=True)
class TagCondition(Condition):
    tag: str
    value: int
    comparator: Comparator = prop(parser=_parse_comparator)

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@condition(r'unlock_upgrade')
@dataclass(frozen=True)
class UpgradeUnlockedCondition(Condition):
    value: int

    def references(self) -> Iterable[Reference]:
        yield UpgradeReference(self.value)


def list_conditions() -> list[tuple[str, type[Condition]]]:
    return conditions
