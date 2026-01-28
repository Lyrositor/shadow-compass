from dataclasses import dataclass
from typing import Any, Iterable

from shadow_compass.loc import Loc
from shadow_compass.prop import prop
from shadow_compass.schema.condition import Condition
from shadow_compass.schema.effect import Effect
from shadow_compass.schema.reference import Reference, CardReference, EndingReference, RiteReference


@dataclass(frozen=True)
class EventOn:
    back_to_prev_round_end: bool | None = None
    card_born: int | None = None
    card_clean: tuple[int, ...] | int | None = None
    close_begin_guide: str | None = None
    close_prompt: bool | None = None
    close_wizard: bool | None = None
    counter: int | None = None
    game_end: tuple[int, ...] | int | None = None
    open_card_info: bool | None = None
    open_card_info_end: bool | None = None
    open_rite: bool | None = None
    open_rite_end: int | None = None
    rite_can_fill: bool | None = None
    rite_can_start: bool | None = None
    rite_can_stop: bool | None = None
    rite_cancel: int | None = None
    rite_start: tuple[int, ...] | int | None = None
    rite_end: tuple[int, ...] | int | None = None
    round_begin_ba: tuple[int, ...] | int | None = None
    show_wizard_option: bool | None = None
    sudan_redraw_start: bool | None = None

    @property
    def card_cleans(self) -> tuple[int, ...]:
        return (self.card_clean,) if isinstance(self.card_clean, int) else self.card_clean or ()

    @property
    def game_ends(self) -> tuple[int, ...]:
        return (self.game_end,) if isinstance(self.game_end, int) else self.game_end or ()

    @property
    def rite_starts(self) -> tuple[int, ...]:
        return (self.rite_start,) if isinstance(self.rite_start, int) else self.rite_start or ()

    @property
    def rite_ends(self) -> tuple[int, ...]:
        return (self.rite_end,) if isinstance(self.rite_end, int) else self.rite_end or ()

    @property
    def round_begin_bas(self) -> tuple[int, ...]:
        return (self.round_begin_ba,) if isinstance(self.round_begin_ba, int) else self.round_begin_ba or ()

    def references(self) -> Iterable[Reference]:
        if self.card_born is not None:
            yield CardReference(self.card_born)

        for card_clean in self.card_cleans:
            if card_clean != 1:
                yield CardReference(card_clean)

        for game_end in self.game_ends:
            yield EndingReference(game_end)

        for rite_start in self.rite_starts:
            yield RiteReference(rite_start)

        for rite_end in self.rite_ends:
            yield RiteReference(rite_end)

        if self.open_rite_end:
            yield RiteReference(self.open_rite_end)

        if self.rite_cancel:
            yield RiteReference(self.rite_cancel)


@dataclass(frozen=True)
class EventSettlement:
    action: tuple[Effect, ...] = ()
    tips_resource: str | None = None # Unused
    tips_text: str | None = None # Unused

    def effect_references(self) -> Iterable[Reference]:
        for action  in self.action:
            yield from action.references()


def _parse_auto_start_init(value: Any) -> bool | None:
    if value == [1]:
        return True
    elif value == [0]:
        return False
    elif value is None:
        return None
    else:
        raise ValueError(f'Unexpected value for auto_start_init: {value}')


@dataclass(frozen=True)
class Event:
    id: int
    text: str
    is_replay: bool
    start_trigger: bool
    on: EventOn
    settlement: tuple[EventSettlement, ...]
    condition: tuple[Condition, ...]
    auto_start: bool = prop(default=True)
    auto_start_init: bool | None = prop(parser=_parse_auto_start_init, default=None)

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'event_{self.id}_text')

    def get_settlement_tips_text(self, idx: int) -> Loc:
        return Loc(self.settlement[idx].tips_text or '', f'event_{self.id}_settlement_{idx}_tips_text')

    def event_on_references(self) -> Iterable[Reference]:
        yield from self.on.references()

    def condition_references(self) -> Iterable[Reference]:
        for condition in self.condition:
            yield from condition.references()

    def effect_references(self) -> Iterable[Reference]:
        for settlement in self.settlement:
            yield from settlement.effect_references()

    def __repr__(self) -> str:
        return f'<Event id={self.id}>'
