from dataclasses import dataclass

from shadow_compass.schema.condition import Condition


@dataclass(frozen=True)
class AfterStoryItem:
    key: str
    result_text: str
    condition: tuple[Condition, ...]
    sort: int|None = None
    pic: str|None = None
    result_title: str|None = None


@dataclass(frozen=True)
class AfterStory:
    id: int
    name: str
    prior: tuple[AfterStoryItem, ...]
    extra: tuple[AfterStoryItem, ...]

    def __repr__(self) -> str:
        return f'<AfterStory id={self.id} name={self.name}>'
