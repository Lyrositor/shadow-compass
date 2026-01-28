from dataclasses import dataclass
from typing import Iterable

from shadow_compass.loc import Loc
from shadow_compass.schema.condition import Condition
from shadow_compass.schema.reference import Reference


@dataclass(frozen=True)
class QuestTarget:
    text: str
    show_counter: str  # TODO Support counter reference
    condition: tuple[Condition, ...]

    def condition_references(self) -> Iterable[Reference]:
        for condition in self.condition:
            yield from condition.references()


@dataclass(frozen=True)
class Quest:
    id: int
    name: str
    text: str
    favour_text: str
    upgrade_point: int
    pre: int
    target: tuple[QuestTarget, ...]
    icon: str

    @property
    def name_(self) -> Loc:
        return Loc(self.name, f'quest_{self.id}_name')

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'quest_{self.id}_text')

    @property
    def favour_text_(self) -> Loc:
        return Loc(self.favour_text, f'quest_{self.id}_favour_text')

    def condition_references(self) -> Iterable[Reference]:
        for target in self.target:
            yield from target.condition_references()

    def get_target_text(self, idx: int) -> Loc:
        return Loc(self.target[idx].text, f'quest_{self.id}_target_{idx+1}')

    def __repr__(self) -> str:
        return f'<Quest id={self.id} name={self.name}>'
