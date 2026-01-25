from dataclasses import dataclass

from shadow_compass.loc import Loc
from shadow_compass.schema.condition import Condition
from shadow_compass.schema.effect import Effect


@dataclass(frozen=True)
class Upgrade:
    id: int
    name: str
    text: str
    cost: int
    condition: tuple[Condition, ...]
    icon: str
    link_card: int
    effect: tuple[Effect, ...]
    incompatible: int

    @property
    def name_(self) -> Loc:
        return Loc(self.name, f'upgrade_{self.id}_name')

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'upgrade_{self.id}_text')

    def __repr__(self) -> str:
        return f'<Upgrade id={self.id} name={self.name}>'
