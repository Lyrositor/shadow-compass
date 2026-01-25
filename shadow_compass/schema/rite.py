from dataclasses import dataclass
from typing import Iterable

from shadow_compass.loc import Loc
from shadow_compass.prop import prop
from shadow_compass.schema.condition import Condition
from shadow_compass.schema.effect import Effect
from shadow_compass.schema.enums import RiteResult, RiteType
from shadow_compass.schema.outcome import Outcome
from shadow_compass.schema.reference import Reference, TagReference


@dataclass(frozen=True)
class RandomTextUp:
    text: str
    type: RiteResult
    type_tips: str
    low_target: int
    low_target_tips: str


@dataclass(frozen=True)
class TagTipsUp:
    tips: tuple[str, ...] | None = None
    type: RiteResult | None = None


@dataclass(frozen=True)
class RiteCardSlotPop:
    condition: tuple[Condition, ...]
    action: tuple[Effect, ...]


@dataclass(frozen=True)
class RiteCardSlot:
    guid: str
    condition: tuple[Condition, ...]
    open_adsorb: bool
    is_key: bool
    is_empty: bool
    is_enemy: bool
    text: str
    pops: tuple[RiteCardSlotPop, ...] = ()


@dataclass(frozen=True)
class RitePin:
    rite_id: int
    controls: tuple[tuple[int, ...], ...]
    resolution: int
    width: int
    arrow_length: int
    arrow_angle: int
    start_reserve: float
    color: tuple[int, ...]
    dashed: bool


@dataclass(frozen=True)
class RiteOpenCondition:
    condition: tuple[Condition, ...]
    tips: str

    def condition_references(self) -> Iterable[Reference]:
        for cond in self.condition:
            yield from cond.references()


@dataclass(frozen=True)
class Rite:
    id: int
    name: str
    text: str
    tips: str
    once_new: int
    round_number: int
    waiting_round: int
    waiting_round_end_action: tuple[Outcome, ...]
    auto_begin: bool
    auto_result: bool
    location: str
    icon: str
    tag_tips: tuple[str, ...]
    tips_text: tuple[str, ...]
    open_conditions: tuple[RiteOpenCondition, ...]
    random_text: dict[str, str]
    settlement_prior: tuple[Outcome, ...]
    settlement: tuple[Outcome, ...]
    settlement_extre: tuple[Outcome, ...]
    type: RiteType | None = None
    mapping_id: int | None = None
    mapping: int | None = None
    tag_tips_up: TagTipsUp | None = None
    final_pin: bool | None = None
    from_pins: tuple[RitePin, ...] = ()
    random_text_up: dict[str, RandomTextUp] = prop(default_factory=dict)
    cards_slot: dict[str, RiteCardSlot] = prop(default_factory=dict)
    method_settlement: str = '' # Unused
    random_effect: tuple[Effect, ...] = ()  # Unused

    @property
    def name_(self) -> Loc:
        return Loc(self.name, f'rite_{self.id}_name')

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'rite_{self.id}_text')

    def tag_tips_references(self) -> Iterable[TagReference]:
        for tag_tip in self.tag_tips:
            yield TagReference(tag_tip)
        if self.tag_tips_up and self.tag_tips_up.tips:
            for tag_tip in self.tag_tips_up.tips:
                yield TagReference(tag_tip)

    def condition_references(self) -> Iterable[Reference]:
        for open_condition in self.open_conditions:
            yield from open_condition.condition_references()
        for settlement_group in (self.settlement, self.settlement_prior, self.settlement_extre):
            for settlement in settlement_group:
                yield from settlement.condition_references()
        for card_slot in self.cards_slot.values():
            for cond in card_slot.condition:
                yield from cond.references()
            for pop in card_slot.pops:
                for cond in pop.condition:
                    yield from cond.references()

    def effect_references(self) -> Iterable[Reference]:
        for settlement_group in (self.settlement, self.settlement_prior, self.settlement_extre):
            for settlement in settlement_group:
                yield from settlement.effect_references()

    def get_tips_text(self, idx: int) -> Loc:
        return Loc(self.tips_text[idx], f'rite_{self.id}_tips_text_{idx}')

    def get_open_conditions_tips(self, idx: int) -> Loc:
        return Loc(self.open_conditions[idx].tips, f'rite_{self.id}_open_conditions_tips_{idx}')

    def get_random_text_text(self, key: str) -> Loc:
        return Loc(self.random_text[key], f'rite_{self.id}_random_text_{key}_text')

    def get_random_text_up_text(self, key: str) -> Loc:
        return Loc(self.random_text_up[key].text, f'rite_{self.id}_random_text_{key}_text')

    def get_random_text_up_type_tips(self, key: str) -> Loc:
        return Loc(self.random_text_up[key].type_tips, f'rite_{self.id}_random_text_{key}_type_tips')

    def get_random_text_up_low_target_tips(self, key: str) -> Loc:
        return Loc(self.random_text_up[key].low_target_tips, f'rite_{self.id}_random_text_{key}_low_target_tips')

    def get_settlement_prior_title(self, idx: int) -> Loc:
        return Loc(self.settlement_prior[idx].result_title or '', f'rite_{self.id}_prior_settlement_{idx}_title')

    def get_settlement_prior_text(self, idx: int) -> Loc:
        return Loc(self.settlement_prior[idx].result_text or '', f'rite_{self.id}_prior_settlement_{idx}_text')

    def get_settlement_title(self, idx: int) -> Loc:
        return Loc(self.settlement[idx].result_title or '', f'rite_{self.id}_settlement_{idx}_title')

    def get_settlement_text(self, idx: int) -> Loc:
        return Loc(self.settlement[idx].result_text or '', f'rite_{self.id}_settlement_{idx}_text')

    def get_settlement_extre_title(self, idx: int) -> Loc:
        return Loc(self.settlement_extre[idx].result_title or '', f'rite_{self.id}_settlement_extre_{idx}_title')

    def get_settlement_extre_text(self, idx: int) -> Loc:
        return Loc(self.settlement_extre[idx].result_text or '', f'rite_{self.id}_settlement_extre_{idx}_text')

    def get_card_slot_text(self, key: str) -> Loc:
        return Loc(self.cards_slot[key].text, f'rite_{self.id}_cards_slot_{key}_text')

    def __repr__(self) -> str:
        return f'<Rite id={self.id} name={self.name}>'
