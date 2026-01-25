import logging
import shutil
from pathlib import Path
from typing import Iterable, Any

import minify_html
from jinja2 import Environment, PackageLoader, select_autoescape, pass_context
from jinja2.runtime import Context, make_logging_undefined
from markupsafe import Markup, escape

from shadow_compass.game_db import GameDb, Loc, Entry
from shadow_compass.resources import IMAGES_PATH, RESOURCES_PATH

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = 'en'
LANGUAGES = ('zhCN', 'zhTW', 'en', 'ja')
RESOURCES = (
    'logo.png',
    'script.js',
    'style.css',
)

Undefined = make_logging_undefined(logger)


class HtmlExporter:
    game_db: GameDb

    def __init__(self, game_db: GameDb):
        self.game_db = game_db

    def export(self, output_path: Path):
        logger.info('Clearing output directory')
        if output_path.exists():
            for sub_path in output_path.iterdir():
                if sub_path.is_dir():
                    shutil.rmtree(sub_path)
                else:
                    sub_path.unlink()
        else:
            output_path.mkdir(parents=True)

        logger.info('Copying resources')
        for path, contents in self._get_resources():
            file_path = output_path / path
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(contents)

        shutil.copytree(IMAGES_PATH, output_path / 'images')

        for language in LANGUAGES:
            logger.info(f'Processing pages for {language}')
            for path, contents in self.get_pages(language):
                self._write_page(output_path / language / path, contents)

        self._write_page(
            output_path / 'index.html',
            self._build_env(DEFAULT_LANGUAGE, root='./').get_template('index.html').render(key=''),
        )

    def get_pages(self, lang: str) -> Iterable[tuple[str, str]]:
        lang_index_env = self._build_env(lang, root='../')
        lang_entries_index_env = self._build_env(lang, root='../../')
        lang_entries_view_env = self._build_env(lang, root='../../../')

        yield 'index.html', lang_index_env.get_template('index.html').render(key='')

        for entries, key, entry_name  in (
            (self.game_db.cards.values(), 'cards', 'card'),
            (self.game_db.endings.values(), 'endings', 'ending'),
            (self.game_db.events.values(), 'events', 'event'),
            (self.game_db.loots.values(), 'loots', 'loot'),
            (self.game_db.objectives.values(), 'objectives', 'objective'),
            (self.game_db.rites.values(), 'rites', 'rite'),
            (self.game_db.tags.values(), 'tags', 'tag'),
            (self.game_db.upgrades.values(), 'upgrades', 'upgrade'),
        ):
            logger.info(f'Rendering {key} pages')
            yield f'{key}/index.html', lang_entries_index_env.get_template(f'{entry_name}_index.html').render(key=key)
            for entry in entries:
                yield f'{entry.key}/index.html', lang_entries_view_env.get_template(f'{entry_name}_view.html').render(
                    key=entry.key,
                    **{entry_name: entry},
                )

    def _build_env(self, lang: str, root: str) -> Environment:
        env = Environment(
            loader=PackageLoader('shadow_compass'),
            autoescape=select_autoescape(),
            auto_reload=False,
            undefined=Undefined,
        )
        env.globals['game'] = self.game_db
        env.globals['lang'] = lang
        env.globals['root'] = root
        env.globals['log'] = logger.warning
        env.filters['a'] = _a
        env.filters['c'] = _c
        env.filters['e'] = _e
        env.filters['l'] = _l
        env.filters['o'] = _o
        env.filters['r'] = _r
        env.filters['t'] = _t
        env.filters['_'] = _translate
        env.filters['_sort'] = _translatesort
        env.filters['gametext'] = _gametext
        env.filters['slotnum'] = _slotnum
        return env

    @staticmethod
    def _write_page(file_path: Path, contents):
        contents = minify_html.minify(
            contents,
            minify_css=True,
            minify_js=True,
        )
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(contents, encoding='utf-8')

    @staticmethod
    def _get_resources() -> Iterable[tuple[str, bytes]]:
        for resource in RESOURCES:
            yield resource, (RESOURCES_PATH / resource).read_bytes()


@pass_context
def _a(ctx: Context, entry: Any) -> Markup:
    if isinstance(entry, Undefined):
        return Markup('???')
    elif isinstance(entry, Entry):
        return Markup(f'<a href="/{escape(_lang(ctx))}/{escape(entry.key)}">{escape(_translate(ctx, entry.label))}</a>')
    raise ValueError(f'Unexpected entry type: {type(entry)}')


@pass_context
def _c(ctx: Context, card_id: int) -> Markup:
    game: GameDb = ctx['game']
    return _a(ctx, game.cards.get(card_id) or Undefined(f'Card {card_id}'))


@pass_context
def _e(ctx: Context, event_id: int) -> Markup:
    game: GameDb = ctx['game']
    return _a(ctx, game.events.get(event_id) or Undefined(f'Event {event_id}'))


@pass_context
def _l(ctx: Context, loot_id: int) -> Markup:
    game: GameDb = ctx['game']
    return _a(ctx, game.loots.get(loot_id) or Undefined(f'Loot {loot_id}'))


@pass_context
def _o(ctx: Context, ending_id: int) -> Markup:
    game: GameDb = ctx['game']
    return _a(ctx, game.endings.get(ending_id) or Undefined(f'Ending {ending_id}'))


@pass_context
def _r(ctx: Context, rite_id: int) -> Markup:
    game: GameDb = ctx['game']
    return _a(ctx, game.rites.get(rite_id) or Undefined(f'Rite {rite_id}'))


@pass_context
def _t(ctx: Context, tag: str) -> Markup:
    game: GameDb = ctx['game']
    return _a(ctx, game.tags.get(tag) or Undefined(f'Tag {tag}'))


@pass_context
def _translate(ctx: Context, loc: Loc) -> str:
    game: GameDb = ctx['game']
    return game.trans(loc, _lang(ctx))


@pass_context
def _translatesort(ctx: Context, entries: Iterable[Entry]) -> list[Entry]:
    game: GameDb = ctx['game']
    return game.sort(entries, _lang(ctx))


def _gametext(text: str) -> Markup:
    formatted_text = '<br /><br />'.join(escape(line) for line in text.split('\n'))
    return Markup(f'<blockquote>{formatted_text}</blockquote>' )


def _slotnum(slot: str) -> str:
    # Hacky fix for a typo
    return slot.strip('.is')


def _lang(ctx: Context) -> str:
    return ctx['lang']
