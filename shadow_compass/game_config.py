import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self, TypeVar, Any

from shadow_compass import sudanjson
from shadow_compass.parser import parse_value
from shadow_compass.schema.after_story import AfterStory
from shadow_compass.schema.card import Card
from shadow_compass.schema.event import Event
from shadow_compass.schema.gallery_card import GalleryCard
from shadow_compass.schema.loot import Loot
from shadow_compass.schema.over import Over
from shadow_compass.schema.quest import Quest
from shadow_compass.schema.rite import Rite
from shadow_compass.schema.rite_template import RiteTemplate, RiteTemplateMapping
from shadow_compass.schema.tag import Tag
from shadow_compass.schema.upgrade import Upgrade

T = TypeVar('T')


@dataclass(frozen=True)
class GameConfig:
    after_stories: dict[int, AfterStory]
    cards: dict[int, Card]
    events: dict[int, Event]
    gallery_cards: dict[int, GalleryCard]
    loots: dict[int, Loot]
    overs: dict[int, Over]
    quests: dict[int, Quest]
    rites: dict[int, Rite]
    rite_templates: dict[int, RiteTemplate]
    rite_template_mappings: dict[int, RiteTemplateMapping]
    tags: dict[str, Tag]
    upgrades: dict[int, Upgrade]
    localisations: dict[str, dict[str, str]]

    @classmethod
    def from_directory(cls, path: Path) -> Self:
        config_path = path / 'config'
        return cls(
            after_stories=_load_entities_from_directory_files(config_path / 'after_story', AfterStory),
            cards=_load_entities_from_file(config_path / 'cards.json', Card),
            events=_load_entities_from_directory_files(config_path / 'event', Event),
            gallery_cards=_load_entities_from_file(config_path / 'gallery_cards.json', GalleryCard),
            loots=_load_entities_from_directory_files(config_path / 'loot', Loot),
            overs=_load_entities_from_file(config_path / 'over.json', Over),
            quests=_load_entities_from_file(config_path / 'quest.json', Quest),
            rites=_load_entities_from_directory_files(config_path / 'rite', Rite),
            rite_templates=_load_entities_from_directory_files(config_path / 'rite_template', RiteTemplate),
            rite_template_mappings=_load_entities_from_file(config_path / 'rite_template_mappings.json', RiteTemplateMapping),
            tags=_load_entities_from_file(config_path / 'tag.json', Tag, str),
            upgrades=_load_entities_from_file(config_path / 'upgrade.json', Upgrade),
            localisations=_load_localisations(path / 'i18n'),
        )


def _load_entities_from_directory_files(path: Path, entity_cls: type[T], id_field: str = 'id') -> dict[Any, T]:
    entities = {}
    for file_name in os.listdir(path):
        with open(path / file_name, encoding='utf-8') as f:
            data = sudanjson.load(f)
            entity = parse_value(data, entity_cls)
            entities[getattr(entity, id_field)] = entity
    return entities


def _load_entities_from_file(path: Path, entity_cls: type[T], id_type: type = int) -> dict[Any, T]:
    entities = {}
    with open(path, encoding='utf-8') as f:
        data = sudanjson.load(f)
        for key, value in data.items():
            entity = parse_value(value, entity_cls)
            entities[id_type(key)] = entity
    return entities


def _load_localisations(path: Path) -> dict[str, dict[str, str]]:
    localisations = {}
    for sub_path in path.iterdir():
        if not sub_path.is_dir():
            continue
        lang = sub_path.name
        with open(sub_path / 'config.json', encoding='utf-8') as f:
            localisations[lang] = sudanjson.load(f, False)
    return localisations
