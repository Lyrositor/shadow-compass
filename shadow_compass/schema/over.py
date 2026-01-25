from dataclasses import dataclass

from shadow_compass.schema.condition import Condition


@dataclass(frozen=True)
class OverTextExtra:
    condition: tuple[Condition, ...]
    result_text: str


@dataclass(frozen=True)
class Over:
    text: str
    bg: str
    icon: str
    title: str|None = None
    name: str|None = None
    sub_name: str|None = None
    success: int|None = None
    open_after_story: int|None = None
    manual_prompt: bool|None = None
    text_extra: tuple[OverTextExtra, ...] = ()

    def __repr__(self) -> str:
        return f'<Over {id(self)}>'
