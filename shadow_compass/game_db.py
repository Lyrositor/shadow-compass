from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self, Iterable, TypeVar, Any

from shadow_compass.game_config import GameConfig
from shadow_compass.loc import Loc
from shadow_compass.resources import list_image_resources
from shadow_compass.schema.card import Card
from shadow_compass.schema.enums import CardDisplayType, CardRarity
from shadow_compass.schema.event import Event
from shadow_compass.schema.gallery_card import GalleryCard
from shadow_compass.schema.loot import Loot
from shadow_compass.schema.over import Over
from shadow_compass.schema.quest import Quest
from shadow_compass.schema.reference import CardReference, RiteReference, TagReference, UpgradeReference, LootReference, \
    Reference, EventReference, EndingReference
from shadow_compass.schema.rite import Rite
from shadow_compass.schema.tag import Tag
from shadow_compass.schema.upgrade import Upgrade

logger = logging.getLogger(__name__)

SOURCE_LANGUAGE = 'zhCN'


def stub_default() -> Any:
    raise RuntimeError('Stubbed default value')


@dataclass(frozen=True)
class Entry(ABC):
    card_vanish_effects: list[CardEntry] = field(default_factory=list)
    card_post_rite_conditions: list[CardEntry] = field(default_factory=list)
    card_post_rite_effects: list[CardEntry] = field(default_factory=list)
    event_triggers: list[EventEntry] = field(default_factory=list)
    event_conditions: list[EventEntry] = field(default_factory=list)
    event_effects: list[EventEntry] = field(default_factory=list)
    loot_items: list[LootEntry] = field(default_factory=list)
    loot_conditions: list[LootEntry] = field(default_factory=list)
    rite_conditions: list[RiteEntry] = field(default_factory=list)
    rite_effects: list[RiteEntry] = field(default_factory=list)

    @property
    @abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def label(self) -> Loc:
        raise NotImplementedError

    @property
    def sort_key(self) -> Loc:
        return self.label

    def __repr__(self):
        return f'<{self.__class__.__name__} key={self.key}>'


E = TypeVar('E', bound=Entry)


@dataclass(frozen=True, repr=False)
class CardEntry(Entry):
    card: Card = field(default_factory=stub_default)
    gallery_card: GalleryCard | None = None
    tags: list[tuple[TagEntry, int]] = field(default_factory=list)
    equips: list[TagEntry] = field(default_factory=list)

    @property
    def key(self) -> str: return f'cards/{self.card.id}'

    @property
    def label(self) -> Loc: return self.card.name_

    @property
    def display_type(self) -> CardDisplayType | None: return self.gallery_card.show_type if self.gallery_card else None

    def get_resources(self, available_image_resources: set[str]) -> tuple[tuple[CardRarity, str], ...]:
        if isinstance(self.card.resource, str):
            resources = ((self._get_rarity_for_resource(self.card.resource), self.card.resource),)
        else:
            resources = tuple((self._get_rarity_for_resource(r), r) for r in self.card.resource)
        return tuple(r for r in resources if r[1] in available_image_resources)

    def _get_rarity_for_resource(self, resource: str) -> CardRarity:
        if self.gallery_card is not None:
            for gallery_resource in self.gallery_card.resources:
                if gallery_resource.pic_res == resource:
                    return gallery_resource.rare
        return self.card.rare


@dataclass(frozen=True, repr=False)
class EndingEntry(Entry):
    id: int = field(default_factory=stub_default)
    over: Over = field(default_factory=stub_default)
    on_cards_vanish: list[CardEntry] = field(default_factory=list)
    on_cards_post_rite: list[CardEntry] = field(default_factory=list)

    @property
    def key(self) -> str: return f'endings/{self.id}'

    @property
    def label(self) -> Loc: return self.name

    @property
    def name(self) -> Loc: return Loc(self.over.name or '', f'over_{self.id}_name')

    @property
    def sub_name(self) -> Loc: return Loc(self.over.sub_name or '', f'over_{self.id}_subname')

    @property
    def text(self) -> Loc: return Loc(self.over.text, f'over_{self.id}')

    def get_extra_text(self, idx: int) -> Loc:
        return Loc(self.over.text_extra[idx].result_text, f'over_{self.id}_extra_{idx}_text')


@dataclass(frozen=True, repr=False)
class EventEntry(Entry):
    event: Event = field(default_factory=stub_default)
    on_cards_vanish: list[CardEntry] = field(default_factory=list)

    @property
    def key(self) -> str: return f'events/{self.event.id}'

    @property
    def label(self) -> Loc: return self.event.text_


@dataclass(frozen=True, repr=False)
class LootEntry(Entry):
    loot: Loot = field(default_factory=stub_default)

    @property
    def key(self) -> str: return f'loots/{self.loot.id}'

    @property
    def label(self) -> Loc: return self.loot.name_


@dataclass(frozen=True, repr=False)
class ObjectiveEntry(Entry):
    quest: Quest = field(default_factory=stub_default)

    @property
    def key(self) -> str: return f'objectives/{self.quest.id}'

    @property
    def label(self) -> Loc: return self.quest.name_


@dataclass(frozen=True, repr=False)
class RiteEntry(Entry):
    rite: Rite = field(default_factory=stub_default)

    @property
    def key(self) -> str: return f'rites/{self.rite.id}'

    @property
    def label(self) -> Loc: return self.rite.name_


@dataclass(frozen=True, repr=False)
class TagEntry(Entry):
    tag: Tag = field(default_factory=stub_default)
    cards: list[CardEntry] = field(default_factory=list)
    card_equips: list[CardEntry] = field(default_factory=list)
    rite_tips: list[RiteEntry] = field(default_factory=list)

    @property
    def key(self) -> str: return f'tags/{self.tag.code}'

    @property
    def label(self) -> Loc: return self.tag.name_


@dataclass(frozen=True, repr=False)
class UpgradeEntry(Entry):
    upgrade: Upgrade = field(default_factory=stub_default)

    @property
    def key(self) -> str: return f'upgrades/{self.upgrade.id}'

    @property
    def label(self) -> Loc: return self.upgrade.name_


@dataclass(frozen=True)
class GameDb:
    image_resources: set[str]
    cards: dict[int, CardEntry]
    endings: dict[int, EndingEntry]
    events: dict[int, EventEntry]
    loots: dict[int, LootEntry]
    objectives: dict[int, ObjectiveEntry]
    rites: dict[int, RiteEntry]
    tags: dict[str, TagEntry]
    upgrades: dict[int, UpgradeEntry]
    localisations: dict[str, dict[str, str]]

    @property
    def cards_by_display_type(self) -> Iterable[tuple[CardDisplayType | None, list[CardEntry]]]:
        display_types = (*sorted(CardDisplayType, key=lambda cdt: cdt.label), None)
        cards_by_display_type = {cdt: [] for cdt in display_types}
        for card_entry in self.cards.values():
            cards_by_display_type[card_entry.display_type].append(card_entry)
        for display_type in display_types:
            yield display_type, cards_by_display_type[display_type]

    def trans(self, loc: Loc, lang: str) -> str:
        text = self.localisations.get(lang, {}).get(loc.loc_id)
        if text is None:
            text = loc.text if lang == SOURCE_LANGUAGE or not loc.fallback else loc.fallback
        return text

    def sort(self, entries: Iterable[E], lang: str) -> list[E]:
        return sorted(entries, key=lambda entry: self.trans(entry.sort_key, lang))

    @classmethod
    def from_config(cls, config: GameConfig, additional_localisations_path: Path) -> Self:
        logger.info('Building game database')

        cards = {
            card_id: CardEntry(card=card, gallery_card=config.gallery_cards.get(card_id))
            for card_id, card in config.cards.items()
        }
        endings = {over_id: EndingEntry(id=over_id, over=over) for over_id, over in config.overs.items()}
        events = {event_id: EventEntry(event=event) for event_id, event in config.events.items()}
        loots = {loot_id: LootEntry(loot=loot) for loot_id, loot in config.loots.items()}
        objectives = {quest_id: ObjectiveEntry(quest=quest) for quest_id, quest in config.quests.items()}
        rites = {rite_id: RiteEntry(rite=rite) for rite_id, rite in config.rites.items()}
        tags = {tag.name: TagEntry(tag=tag) for tag in config.tags.values()}
        upgrades = {upgrade_id: UpgradeEntry(upgrade=upgrade) for upgrade_id, upgrade in config.upgrades.items()}

        for card in cards.values():
            for tag_name, value in card.card.tag.items():
                if tag_name in tags:
                    tags[tag_name].cards.append(card)
                    card.tags.append((tags[tag_name], value))
                else:
                    logger.warning(f'Failed to locate tag: {tag_name}')
            card.tags.sort(key=lambda t: t[0].tag.code)
            for tag_name in card.card.equips:
                if tag_name in tags:
                    tags[tag_name].card_equips.append(card)
                    card.equips.append(tags[tag_name])
                else:
                    logger.warning(f'Failed to locate tag: {tag_name}')
            card.equips.sort(key=lambda t: t.tag.code)

            for references, attr_name in (
                (card.card.vanish_effect_references(), 'card_vanish_effects'),
                (card.card.post_rite_condition_references(), 'card_post_rite_conditions'),
                (card.card.post_rite_effect_references(), 'card_post_rite_effects'),
            ):
                _apply_references(card, references, attr_name, cards, endings, events, loots, rites, tags, upgrades)

        for rite in rites.values():
            for tag_tip_reference in rite.rite.tag_tips_references():
                if tag_tip_reference.id in tags:
                    tags[tag_tip_reference.id].rite_tips.append(rite)
                else:
                    logger.warning(f'Failed to locate tag: {tag_tip_reference.id}')

            for references, attr_name in (
                (rite.rite.condition_references(), 'rite_conditions'),
                (rite.rite.effect_references(), 'rite_effects'),
            ):
                _apply_references(rite, references, attr_name, cards, endings, events, loots, rites, tags, upgrades)

        for event in events.values():
            for references, attr_name in (
                (event.event.event_on_references(), 'event_triggers'),
                (event.event.condition_references(), 'event_conditions'),
                (event.event.effect_references(), 'event_effects'),
            ):
                _apply_references(event, references, attr_name, cards, endings, events, loots, rites, tags, upgrades)

        for loot in loots.values():
            _apply_references(loot, loot.loot.item_references(), 'loot_items', cards, endings, events, loots, rites, tags, upgrades)
            _apply_references(loot, loot.loot.condition_references(), 'loot_conditions', cards, endings, events, loots, rites, tags, upgrades)

        localisations = json.load(additional_localisations_path.open(encoding='utf-8'))
        for lang, lang_localisations in config.localisations.items():
            localisations[lang].update(lang_localisations)

        return cls(
            image_resources=list_image_resources(),
            cards=cards,
            endings=endings,
            events=events,
            loots=loots,
            objectives=objectives,
            rites=rites,
            tags=tags,
            upgrades=upgrades,
            localisations=localisations,
        )

    def __repr__(self):
        return f'<GameDb {id(self)}>'


def _apply_references(
    entry: Entry,
    references: Iterable[Reference],
    attr_name: str,
    cards: dict[int, CardEntry],
    endings: dict[int, EndingEntry],
    events: dict[int, EventEntry],
    loots: dict[int, LootEntry],
    rites: dict[int, RiteEntry],
    tags: dict[str, TagEntry],
    upgrades: dict[int, UpgradeEntry],
) -> None:
    for ref in references:
        target = None
        match ref:
            case CardReference():
                if ref.id in cards:
                    target = cards[ref.id]
                else:
                    logger.warning(f'Failed to locate card: {ref.id}')
            case EndingReference():
                if ref.id in endings:
                    target = endings[ref.id]
                else:
                    logger.warning(f'Failed to locate ending: {ref.id}')
            case EventReference():
                if ref.id in events:
                    target = events[ref.id]
                else:
                    logger.warning(f'Failed to locate event: {ref.id}')
            case LootReference():
                if ref.id in loots:
                    target = loots[ref.id]
                else:
                    logger.warning(f'Failed to locate loot: {ref.id}')
            case RiteReference():
                if ref.id in rites:
                    target = rites[ref.id]
                else:
                    logger.warning(f'Failed to locate rite: {ref.id}')
            case TagReference():
                if ref.id in tags:
                    target = tags[ref.id]
                else:
                    logger.warning(f'Failed to locate tag: {ref.id}')
            case UpgradeReference():
                if ref.id in upgrades:
                    target = upgrades[ref.id]
                else:
                    logger.warning(f'Failed to locate upgrade: {ref.id}')
            case _:
                raise ValueError(f'Unknown reference type: {ref}')
        if target is not None:
            attr = getattr(target, attr_name)
            if not any(e for e in attr if e.key == entry.key):
                attr.append(entry)
