from dataclasses import dataclass
from typing import Iterable

from shadow_compass.schema.condition import Condition
from shadow_compass.schema.enums import EndingOutcome
from shadow_compass.schema.reference import Reference


@dataclass(frozen=True)
class OverTextExtra:
    condition: tuple[Condition, ...]
    result_text: str

    def condition_references(self) -> Iterable[Reference]:
        for condition in self.condition:
            yield from condition.references()


@dataclass(frozen=True)
class Over:
    text: str
    bg: str
    icon: str
    title: str|None = None
    name: str|None = None
    sub_name: str|None = None
    success: EndingOutcome = EndingOutcome.DEFEAT
    open_after_story: bool = False
    manual_prompt: bool = False
    text_extra: tuple[OverTextExtra, ...] = ()

    @property
    def extra_text(self) -> tuple[tuple[int, OverTextExtra], ...]:
        return tuple(
            (i, over_text_extra)
            for i, over_text_extra in enumerate(self.text_extra)
            if over_text_extra.condition or over_text_extra.result_text
        )

    def condition_references(self) -> Iterable[Reference]:
        for text_extra in self.text_extra:
            yield from text_extra.condition_references()


    def __repr__(self) -> str:
        return f'<Over {id(self)}>'
