import re
from abc import ABC
from dataclasses import dataclass
from typing import Iterable

from shadow_compass.schema.common import SLOT, TAG, COUNTER_ID
from shadow_compass.schema.reference import Reference, TagReference


@dataclass(frozen=True)
class FormulaElement(ABC):
    @property
    def cls(self) -> str:
        return self.__class__.__name__

    def references(self) -> Iterable[Reference]:
        yield from []


@dataclass(frozen=True)
class OperatorFormulaElement(FormulaElement):
    operator: str


@dataclass(frozen=True)
class CounterFormulaElement(FormulaElement):
    counter_id: int


@dataclass(frozen=True)
class GlobalCounterFormulaElement(FormulaElement):
    counter_id: int


@dataclass(frozen=True)
class LiteralFormulaElement(FormulaElement):
    value: float


@dataclass(frozen=True)
class RarityFormulaElement(FormulaElement):
    pass


@dataclass(frozen=True)
class SlotRarityFormulaElement(FormulaElement):
    slot: int


@dataclass(frozen=True)
class SlotTagFormulaElement(FormulaElement):
    slot: int
    tag: str

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@dataclass(frozen=True)
class TagFormulaElement(FormulaElement):
    tag: str

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@dataclass(frozen=True)
class EnemyFormulaElement(FormulaElement):
    elements: tuple[FormulaElement, ...]

    def references(self) -> Iterable[Reference]:
        for element in self.elements:
            yield from element.references()


def parse_formula(formula: str) -> tuple[tuple[FormulaElement, ...], int]:
    i = 0
    n = len(formula)
    elements = []
    while i < n:
        if formula[i] == ')':
            # Assume we are closing out an EnemyElement
            i += 1
            break
        if formula[i] in ('+', '-', '*', '/'):
            elements.append(OperatorFormulaElement(formula[i]))
            i += 1
        elif formula[i:i + 2] == 'e(':
            i += 2
            enemy_elements, enemy_i = parse_formula(formula[i:])
            elements.append(EnemyFormulaElement(enemy_elements))
            i += enemy_i
        elif match := re.match(r'(?P<value>[\d.]+)', formula[i:]):
            elements.append(LiteralFormulaElement(float(match.group('value'))))
            i += match.end()
        elif match := re.match(fr'(?:{SLOT}\.)?rare', formula[i:]):
            slot = match.group('slot')
            elements.append(SlotRarityFormulaElement(int(slot)) if slot else RarityFormulaElement())
            i += match.end()
        elif match := re.match(fr'^counter\.{COUNTER_ID}', formula[i:]):
            elements.append(CounterFormulaElement(int(match.group('counter_id'))))
            i += match.end()
        elif match := re.match(fr'^global_counter\.{COUNTER_ID}', formula[i:]):
            elements.append(GlobalCounterFormulaElement(int(match.group('counter_id'))))
            i += match.end()
        elif match := re.match(fr'^{SLOT}\.{TAG}', formula[i:]):
            elements.append(SlotTagFormulaElement(int(match.group('slot')), match.group('tag')))
            i += match.end()
        elif match := re.match(TAG, formula[i:]):
            elements.append(TagFormulaElement(match.group('tag')))
            i += match.end()
        else:
            raise ValueError(f'Failed to parse formula: {formula}')
    return tuple(elements), i
