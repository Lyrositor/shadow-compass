import re
from abc import ABC
from dataclasses import dataclass
from typing import Any, Self, Callable, TypeVar, Iterable

from shadow_compass.loc import Loc
from shadow_compass.prop import prop
from shadow_compass.schema.common import CustomSchema, ParseFunc, OPERATOR, TAG, CARD_ID, SLOT, RITE_ID, COUNTER_ID, \
    TEXT_ID
from shadow_compass.schema.enums import Operator, CardRarity, Slot
from shadow_compass.schema.reference import Reference, CardReference, TagReference, EventReference, EndingReference
from shadow_compass.sudanjson import MultiDict


@dataclass(frozen=True)
class Effect(ABC):
    @property
    def cls(self) -> str:
        return self.__class__.__name__

    def references(self) -> Iterable[Reference]:
        yield from []


T = TypeVar('T', bound=Effect)

effects: list[tuple[str, type[Effect]]] = []


def effect(pattern: str) -> Callable[[type[T]], type[T]]:
    def decorator(cls: type[T]) -> type[T]:
        effects.append((pattern, cls))
        return cls
    return decorator


@dataclass(frozen=True)
class CardChange(ABC):
    @property
    def cls(self) -> str:
        return self.__class__.__name__

    def references(self) -> Iterable[Reference]:
        yield from []


@dataclass(frozen=True)
class CardQuantityChange(CardChange):
    quantity: int


@dataclass(frozen=True)
class CardCountChange(CardChange):
    count: int


@dataclass(frozen=True)
class CardTagChange(CardChange):
    tag: str
    operator: Operator
    value: int

    def references(self) -> Iterable[Reference]:
        yield TagReference(self.tag)


@dataclass(frozen=True)
class OptionItem:
    text: str
    tag: str


@effect(fr'table\.{CARD_ID}{OPERATOR}equip')
@dataclass(frozen=True)
class AdjustEquipCardTableEffect(Effect):
    card_id: int
    operator: Operator
    value: int


@effect(fr'parent{OPERATOR}equip')
@dataclass(frozen=True)
class AdjustEquipParentEffect(Effect):
    operator: Operator
    value: int


@effect(fr'{SLOT}{OPERATOR}equip')
@dataclass(frozen=True)
class AdjustEquipSlotEffect(Effect, CustomSchema):
    slot: int
    operator: Operator
    card_id: int | None = None
    tag: str | None = None

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        d = {'slot': data['slot'], 'operator': data['operator']}
        if isinstance(data['value'], list) and isinstance(data['value'][0], str):
            d['tag'] = data['value'][0]
        elif isinstance(data['value'], int):
            d['card_id'] = data['value']
        else:
            raise ValueError(f'Unsupported value: {data["value"]}')
        return parse_func(d, cls, True)


@effect(fr'{SLOT}{OPERATOR}{SLOT.replace('slot', 'slotted')}')
@dataclass(frozen=True)
class AdjustEquipSlotSlottedEffect(Effect):
    slot: int
    operator: Operator
    slotted: int
    value: int = prop(assert_equals=1)


@effect(fr'table\.{TAG.replace('tag', 'tagged')}{OPERATOR}equip')
@dataclass(frozen=True)
class AdjustEquipTaggedTableEffect(Effect, CustomSchema):
    tagged: str
    operator: Operator
    card_id: int | None = None
    tag: str | None = None

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        d = {'tagged': data['tagged'], 'operator': data['operator']}
        if isinstance(data['value'], list) and isinstance(data['value'][0], str):
            d['tag'] = data['value'][0]
        elif isinstance(data['value'], int):
            d['card_id'] = data['value']
        else:
            raise ValueError(f'Unsupported value: {data["value"]}')
        return parse_func(d, cls, True)


@effect(fr'{CARD_ID}\.uprare')
@dataclass(frozen=True)
class AdjustRarityCardEffect(Effect):
    card_id: int
    value: int


@effect(fr'table\.{CARD_ID}\.uprare')
@dataclass(frozen=True)
class AdjustRarityCardTableEffect(Effect):
    card_id: int
    value: int


@effect(fr'{SLOT}\.uprare')
@dataclass(frozen=True)
class AdjustRaritySlotEffect(Effect):
    slot: int
    value: int


@effect(fr'{TAG}\.uprare')
@dataclass(frozen=True)
class AdjustRarityTaggedEffect(Effect):
    tag: str
    value: int


@effect(fr'table\.{TAG}\.uprare')
@dataclass(frozen=True)
class AdjustRarityTaggedTableEffect(Effect):
    tag: str
    value: int


@effect(fr'{CARD_ID}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagCardEffect(Effect):
    card_id: int
    operator: Operator
    tag: str
    value: int


@effect(fr'table\.{CARD_ID}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagCardTableEffect(Effect):
    card_id: int
    tag: str
    operator: Operator
    value: int


@effect(fr'total\.{CARD_ID}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagCardTotalEffect(Effect):
    card_id: int
    tag: str
    operator: Operator
    value: int


@effect(fr'parent{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagParentEffect(Effect):
    tag: str
    operator: Operator
    value: int


@effect(fr'self{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagSelfEffect(Effect):
    tag: str
    operator: Operator
    value: int


@effect(fr'{SLOT}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagSlotEffect(Effect):
    slot: int
    operator: Operator
    tag: str
    value: int


@effect(fr'total\.sudan{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagSudanTotalEffect(Effect):
    operator: Operator
    tag: str
    value: int


@effect(fr'{TAG.replace('tag', 'tagged')}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagTaggedEffect(Effect):
    tagged: str
    operator: Operator
    tag: str
    value: int


@effect(fr'table\.{TAG.replace('tag', 'tagged')}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagTaggedTableEffect(Effect):
    tagged: str
    operator: Operator
    tag: str
    value: int


@effect(fr'total\.{TAG.replace('tag', 'tagged')}{OPERATOR}{TAG}')
@dataclass(frozen=True)
class AdjustTagTaggedTotalEffect(Effect):
    tagged: str
    operator: Operator
    tag: str
    value: int


@effect(r'all')
@dataclass(frozen=True)
class AllEffect(Effect):
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(r'begin_guide')
@dataclass(frozen=True)
class BeginGuideEffect(Effect, CustomSchema):
    type: str

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        # Don't bother parsing any more details
        return parse_func({'type': data['value']['type']}, cls, True)


@effect(r'card')
@dataclass(frozen=True)
class CardEffect(Effect, CustomSchema):
    card_id: int
    changes: tuple[CardChange, ...]

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        value = data['value']
        if isinstance(value, int):
            card_id = value
            changes = []
        else:
            card_id = value[0]
            changes = []
            for change_string in value[1:]:
                if match := re.match(r'^数量\+(\d+)$', change_string):
                    changes.append(CardQuantityChange(quantity=int(match.group(1))))
                elif match := re.match(r'^count\+(\d+)$', change_string):
                    changes.append(CardCountChange(count=int(match.group(1))))
                elif match := re.match(r'^(\w+)([=+-])?(\d+)?$', change_string):
                    change_value = match.group(3)
                    changes.append(
                        CardTagChange(
                            tag=match.group(1),
                            operator=Operator(match.group(2) or '+'),
                            value=int(change_value) if change_value else 1,
                        ),
                    )
                else:
                    raise ValueError(f'Unsupported change: {change_string}')
        return cls(card_id=card_id, changes=tuple(changes))

    def references(self) -> Iterable[Reference]:
        yield CardReference(self.card_id)
        for change in self.changes:
            yield from change.references()


@effect(r'case:(op)?(?P<option>\d+)')
@dataclass(frozen=True)
class CaseEffect(Effect):
    option: int
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(fr'table\.change_card_name\.{TEXT_ID}\.{CARD_ID}')
@dataclass(frozen=True)
class ChangeCardNameCardTableEffect(Effect):
    text_id: str
    card_id: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'change_card_name_{self.text_id}')


@effect(fr'total\.change_card_name\.{TEXT_ID}\.{CARD_ID}')
@dataclass(frozen=True)
class ChangeCardNameCardTotalEffect(Effect):
    text_id: str
    card_id: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'change_card_name_{self.text_id}')


@effect(fr'change_card_name\.{TEXT_ID}\.{SLOT}')
@dataclass(frozen=True)
class ChangeCardNameSlotEffect(Effect):
    text_id: str
    slot: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'change_card_name_{self.text_id}')


@effect(fr'total\.change_card_text\.{TEXT_ID}\.{CARD_ID}')
@dataclass(frozen=True)
class ChangeCardTextCardTotalEffect(Effect):
    text_id: str
    card_id: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'change_card_text_{self.text_id}')


@effect(fr'change_card_text\.{TEXT_ID}\.{SLOT}')
@dataclass(frozen=True)
class ChangeCardTextSlotEffect(Effect):
    text_id: str
    slot: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'change_card_text_{self.text_id}')


@effect(r'change_name')
@dataclass(frozen=True)
class ChangeNameEffect(Effect):
    value: int


@effect(r'choose')
@dataclass(frozen=True)
class ChooseEffect(Effect):
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(fr'clean\.{CARD_ID}')
@dataclass(frozen=True)
class CleanCardEffect(Effect):
    card_id: int
    value: int = prop(assert_equals=1)


@effect(fr'table\.clean\.{CARD_ID}(?:\|{TAG})?')
@dataclass(frozen=True)
class CleanCardTableEffect(Effect):
    card_id: int
    value: int
    tag: str | None = None


@effect(fr'table\.clean\.char\|{TAG}=0')
@dataclass(frozen=True)
class CleanCharTableEffect(Effect):
    value: int
    tag: str


@effect(r'table\.clean\.item(?P<card_ids>[|!\d]+)')
@dataclass(frozen=True)
class CleanItemTableEffect(Effect):
    value: int
    card_ids: tuple[int, ...] = prop(parser=lambda c: c[2:].replace('!', '').split('|'))


@effect(r'clean.rite')
@dataclass(frozen=True)
class CleanRiteEffect(Effect):
    value: tuple[int, ...] | int

    @property
    def rite_ids(self) -> tuple[int, ...]:
        return (self.value, ) if isinstance(self.value, int) else self.value


@effect(r'clean\.self')
@dataclass(frozen=True)
class CleanSelfEffect(Effect):
    value: int = prop(assert_equals=1)


@effect(fr'clean\.{SLOT}')
@dataclass(frozen=True)
class CleanSlotEffect(Effect):
    slot: int
    value: int


@effect(fr'clean\.{TAG}')
@dataclass(frozen=True)
class CleanTagEffect(Effect):
    tag: str
    value: int = prop(assert_equals=1)


@effect(fr'table\.clean\.{TAG}(?:\|{TAG.replace('tag', 'additional_tag')})?(?:\.rare=(?P<rarity>\d))?')
@dataclass(frozen=True)
class CleanTagTableEffect(Effect):
    tag: str
    value: int
    additional_tag: str | None = None
    rarity: CardRarity|None = None


@effect(r'close_box')
@dataclass(frozen=True)
class CloseBoxEffect(Effect):
    value: bool


@effect(r'(?:coin|金币)')
@dataclass(frozen=True)
class CoinEffect(Effect):
    value: int


@effect(r'confirm')
@dataclass(frozen=True)
class ConfirmEffect(Effect, CustomSchema):
    id: str
    text: str
    icon: tuple[str, ...]
    confirm_text: str
    cancel_text: str

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'CONFIRM_{self.id}_TEXT')

    @property
    def confirm_text_(self) -> Loc:
        return Loc(self.confirm_text, f'CONFIRM_{self.id}_CONFIRM_TEXT')

    @property
    def cancel_text_(self) -> Loc:
        return Loc(self.cancel_text, f'CONFIRM_{self.id}_CANCEL_TEXT')

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        return parse_func(data['value'], cls, True)


@effect(fr'counter(?P<operator>[=+.-]){COUNTER_ID}')
@dataclass(frozen=True)
class CounterEffect(Effect):
    counter_id: int
    value: int
    operator: Operator = prop(parser=lambda d: Operator(d) if d != '.' else Operator.ADD)  # TODO Confirm this is the behaviour


@effect(fr'global_counter(?P<operator>[.=+-]){COUNTER_ID}')
@dataclass(frozen=True)
class CounterGlobalEffect(Effect):
    counter_id: int
    value: int
    operator: Operator = prop(parser=lambda d: Operator(d) if d != '.' else Operator.ADD)  # TODO Confirm this is the behaviour


@effect(fr'copy\.{SLOT}')
@dataclass(frozen=True)
class CopySlotEffect(Effect):
    slot: int
    value: int


@effect(r'debug')
@dataclass(frozen=True)
class DebugEffect(Effect):
    value: str


@effect(r'delay')
@dataclass(frozen=True)
class DelayEffect(Effect, CustomSchema):
    id: int
    round: int
    effects: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.effects:
            yield from eff.references()

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        return parse_func(
            {
                'id': data['value']['id'],
                'round': data['value']['round'],
                'effects': {k: v for k,v in data['value'].items() if k not in ('id', 'round')}
            },
            cls,
            True,
        )


@effect(r'delay_off')
@dataclass(frozen=True)
class DelayOffEffect(Effect):
    value: int = prop(assert_equals=1)


@effect(r'difficulty')
@dataclass(frozen=True)
class DifficultyEffect(Effect):
    value: int


@effect(r'enable_auto_gen_sudan_card')
@dataclass(frozen=True)
class EnableAutoGenSudanCardEffect(Effect):
    value: bool


@effect(fr'{SLOT}\+equip_slot')
@dataclass(frozen=True)
class EquipSlotAddSlotEffect(Effect):
    slot: int
    value: Slot


@effect(fr'{SLOT}=equip_slot:(?P<equip_slot>{'|'.join(str(s.value) for s in Slot)})')
@dataclass(frozen=True)
class EquipSlotSetSlotEffect(Effect):
    slot: int
    equip_slot: Slot
    value: int = prop(assert_equals=0)


@effect(r'event_on')
@dataclass(frozen=True)
class EventOnEffect(Effect):
    value: tuple[int, ...] | int

    @property
    def event_ids(self) -> Iterable[int]:
        return (self.value, ) if isinstance(self.value, int) else self.value

    def references(self) -> Iterable[Reference]:
        yield from (EventReference(event_id) for event_id in self.event_ids)


@effect(r'event_off')
@dataclass(frozen=True)
class EventOffEffect(Effect):
    value: tuple[int, ...] | int

    @property
    def event_ids(self) -> tuple[int, ...]:
        return (self.value, ) if isinstance(self.value, int) else self.value

    def references(self) -> Iterable[Reference]:
        yield from (EventReference(event_id) for event_id in self.event_ids)


@effect(r'failed')
@dataclass(frozen=True)
class FailedEffect(Effect):
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(fr'focus\.{RITE_ID}')
@dataclass(frozen=True)
class FocusRiteEffect(Effect):
    rite_id: int
    value: tuple[int, ...]


@effect(r'hand_card_refresh')
@dataclass(frozen=True)
class HandCardRefreshEffect(Effect):
    value: int = prop(assert_equals=1)


@effect(r'loot')
@dataclass(frozen=True)
class LootEffect(Effect):
    value: tuple[int, ...] | int

    @property
    def loot_ids(self) -> tuple[int, ...]:
        return (self.value, ) if isinstance(self.value, int) else self.value


@effect(fr'loot\.{TAG}\+1(?:\|{TAG.replace('tag', 'exclude_tag')}-1)?')
@dataclass(frozen=True)
class LootTagEffect(Effect):
    tag: str
    value: tuple[int, ...] | int
    exclude_tag: str | None = None

    @property
    def loot_ids(self) -> tuple[int, ...]:
        return (self.value, ) if isinstance(self.value, int) else self.value


@effect(r'magic_sudan')
@dataclass(frozen=True)
class MagicSudanEffect(Effect):
    value: int


@effect(fr'table\.{CARD_ID}\.追随者=0\+追随者')
@dataclass(frozen=True)
class MakeFollowerCardTableEffect(Effect):
    card_id: int
    value: int = prop(assert_equals=1)


@effect(fr'total\.{CARD_ID}\.追随者=0\+追随者')
@dataclass(frozen=True)
class MakeFollowerCardTotalEffect(Effect):
    card_id: int
    value: int = prop(assert_equals=1)


@effect(r'no_prompt')
@dataclass(frozen=True)
class NoPromptEffect(Effect):
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(r'no_show')
@dataclass(frozen=True)
class NoShowEffect(Effect):
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(r'option')
@dataclass(frozen=True)
class OptionEffect(Effect, CustomSchema):
    id: str
    text: str
    items: tuple[OptionItem, ...]
    icon: tuple[str | None, ...] | str | None = None

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'OPTION_{self.id}_TEXT')

    def get_item_text(self, idx: int) -> Loc:
        return Loc(self.items[idx].text, f'OPTION_{self.id}_ITEM_{idx+1}_TEXT')

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        return parse_func(data['value'], cls, True)


@effect(r'over')
@dataclass(frozen=True)
class OverEffect(Effect):
    value: int

    def references(self) -> Iterable[Reference]:
        yield EndingReference(self.value)


@effect(fr'pop\.{TEXT_ID}\.{CARD_ID}')
@dataclass(frozen=True)
class PopCardEffect(Effect):
    text_id: str
    card_id: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'hand_pop\.{TEXT_ID}\.{CARD_ID}')
@dataclass(frozen=True)
class PopCardHandEffect(Effect):
    text_id: str
    card_id: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'rite_pop\.{TEXT_ID}\.{CARD_ID}')
@dataclass(frozen=True)
class PopCardRiteEffect(Effect):
    text_id: str
    card_id: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'pop\.{TEXT_ID}\.self')
@dataclass(frozen=True)
class PopSelfEffect(Effect):
    text_id: str
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'pop\.{TEXT_ID}\.{SLOT}')
@dataclass(frozen=True)
class PopSlotEffect(Effect):
    text_id: str
    slot: int
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'hand_pop\.{TEXT_ID}\.sudan')
@dataclass(frozen=True)
class PopSudanHandEffect(Effect):
    text_id: str
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'pop\.{TEXT_ID}\.{TAG}')
@dataclass(frozen=True)
class PopTaggedEffect(Effect):
    text_id: str
    tag: str
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'hand_pop\.{TEXT_ID}\.{TAG}')
@dataclass(frozen=True)
class PopTaggedHandEffect(Effect):
    text_id: str
    tag: str
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(fr'think_pop\.{TEXT_ID}')
@dataclass(frozen=True)
class PopThinkEffect(Effect):
    text_id: str
    value: str

    @property
    def text(self) -> Loc:
        return Loc(self.value, f'POP_{self.text_id}_TEXT_1')


@effect(r'prompt')
@dataclass(frozen=True)
class PromptEffect(Effect, CustomSchema):
    id: str
    text: str
    icon: tuple[tuple[int, ...]|str|None, ...] | str | None = None

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'PROMPT_{self.id}_TEXT')

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        return parse_func(data['value'], cls, True)


@effect(fr'rebirth\.{SLOT}')
@dataclass(frozen=True)
class RebirthSlotEffect(Effect):
    slot: int
    value: int = prop(assert_equals=0)


@effect(r'rite')
@dataclass(frozen=True)
class RiteEffect(Effect):
    value: int


@effect(r'sleep')
@dataclass(frozen=True)
class SleepEffect(Effect):
    value: float


@effect(r'slide')
@dataclass(frozen=True)
class SlideEffect(Effect):
    value: str


@effect(r'steam_achievement')
@dataclass(frozen=True)
class SteamAchievementEffect(Effect):
    value: str


@effect(r'success')
@dataclass(frozen=True)
class SuccessEffect(Effect):
    value: tuple[Effect, ...]

    def references(self) -> Iterable[Reference]:
        for eff in self.value:
            yield from eff.references()


@effect(r'sudan_card')
@dataclass(frozen=True)
class SudanCardEffect(Effect):
    value: tuple[int, ...]


@effect(r'sudan_pool\.sudan\+冻结')
@dataclass(frozen=True)
class SudanPoolFreezeEffect(Effect):
    value: int = prop(assert_equals=1)


@effect(r'sudan_pool\.sudan-冻结')
@dataclass(frozen=True)
class SudanPoolUnfreezeEffect(Effect):
    value: int = prop(assert_equals=1)


@effect(r'g\.card')
@dataclass(frozen=True)
class UpgradeCardEffect(Effect, CustomSchema):
    card_id: int
    tags: dict[str, int]

    @classmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        value = data['value']
        tags = {}
        if isinstance(value, int):
            card_id = value
        elif isinstance(value, list):
            card_id = value[0]
            for val in value[1:]:
                if not (match := re.match(fr'{TAG}\+(?P<count>\d+)', val)):
                    raise ValueError(f'Invalid upgrade card: {data}')
                tags[match.group('tag')] = int(match.group('count'))
        else:
            raise ValueError(f'Invalid upgrade card: {data}')
        return parse_func({'card_id': card_id, 'tags': tags}, cls, True)


@effect(fr'g\.{CARD_ID}\+{TAG}')
@dataclass(frozen=True)
class UpgradeCardAddTagEffect(Effect):
    card_id: int
    tag: str
    value: int


@effect(r'g\.change')
@dataclass(frozen=True)
class UpgradeCardChangeEffect(Effect, CustomSchema):
    card_id: int
    new_card_id: int

    @classmethod
    def parse(cls, data: dict[str, Any] | MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        return cls(*data['value'])


@effect(r'g\.coin')
@dataclass(frozen=True)
class UpgradeCoinEffect(Effect):
    value: int


@effect(fr'g\.{TAG.replace('tag', 'tagged')}\+{TAG}')
@dataclass(frozen=True)
class UpgradeTagAddTagEffect(Effect):
    tagged: str
    tag: str
    value: int


def list_effects() -> list[tuple[str, type[Effect]]]:
    return effects
