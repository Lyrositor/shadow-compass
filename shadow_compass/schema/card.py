from dataclasses import dataclass
from typing import Iterable

from shadow_compass.loc import Loc
from shadow_compass.prop import prop
from shadow_compass.schema.effect import Effect
from shadow_compass.schema.enums import CardType, CardRarity
from shadow_compass.schema.outcome import Outcome
from shadow_compass.schema.reference import Reference


@dataclass(frozen=True)
class Card:
    id: int
    name: str
    title: str
    text: str
    card_favour: str
    type: CardType
    tips: str
    rare: CardRarity
    resource: str | tuple[str, ...]
    tag: dict[str, int]
    card_vanishing: int
    vanish: tuple[Effect, ...]
    equips: tuple[str, ...]
    is_only: bool
    sfx: str | None = None
    post_rite: tuple[Outcome, ...] | None = None
    destroy_resources: tuple[str, ...] = ()
    pops: tuple[str, ...] = prop(assert_equals=(), default=())

    @property
    def name_(self) -> Loc:
        return Loc(self.name, f'card_{self.id}_name')

    @property
    def title_(self) -> Loc:
        return Loc(self.title, f'card_{self.id}_title')

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'card_{self.id}_text')

    def get_post_rite_result_text(self, idx: int) -> Loc:
        assert self.post_rite is not None
        return Loc(self.post_rite[idx].result_text or '', f'card_{self.id}_settlement_extre_{idx}_text')

    def post_rite_condition_references(self) -> Iterable[Reference]:
        if self.post_rite:
            for post_rite in self.post_rite:
                yield from post_rite.condition_references()

    def post_rite_effect_references(self) -> Iterable[Reference]:
        if self.post_rite:
            for post_rite in self.post_rite:
                yield from post_rite.effect_references()

    def vanish_effect_references(self) -> Iterable[Reference]:
        for effect in self.vanish:
            yield from effect.references()

    def __repr__(self) -> str:
        return f'<Card id={self.id} name={self.name}>'
