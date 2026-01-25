from dataclasses import dataclass
from typing import Iterable

from shadow_compass.schema.condition import Condition
from shadow_compass.schema.effect import Effect
from shadow_compass.schema.reference import Reference


@dataclass(frozen=True)
class Outcome:
    action: tuple[Effect, ...]
    condition: tuple[Condition, ...]
    result: tuple[Effect, ...]
    result_text: str | None = None
    result_title: str | None = None
    guid: str | None = None

    def condition_references(self) -> Iterable[Reference]:
        for cond in self.condition:
            yield from cond.references()

    def effect_references(self) -> Iterable[Reference]:
        for effect in self.action:
            yield from effect.references()
        for effect in self.result:
            yield from effect.references()

    def __repr__(self) -> str:
        return f'<Outcome {id(self)}>'