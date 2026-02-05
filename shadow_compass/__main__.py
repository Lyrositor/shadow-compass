import argparse
import logging
import pickle
import sys
from pathlib import Path

from shadow_compass.exporter.html import HtmlExporter
from shadow_compass.game_config import GameConfig
from shadow_compass.game_db import GameDb

logger = logging.getLogger(__name__)

RESOURCES_PATH = Path('resources')
ADDITIONAL_LOCALISATIONS_PATH = RESOURCES_PATH / 'additional_i18n.json'
GAME_PATH = RESOURCES_PATH / 'game'

OUTPUT_PATH = Path('output')
CACHE_PATH = OUTPUT_PATH / 'cache.pickle'
EXPORT_PATH = OUTPUT_PATH / 'export_html'


def main() -> int:
    """Main entry point for Shadow Compass."""
    parser = argparse.ArgumentParser(description='Shadow Compass - Game data exploration tool for Sultan\'s Game')
    parser.add_argument('--no-cache', action='store_true', help='Disable cache and force reparse')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before running')
    args = parser.parse_args()

    logger.info('Building Shadow Compass')

    if not OUTPUT_PATH.exists():
        OUTPUT_PATH.mkdir(parents=True)

    if args.clear_cache and CACHE_PATH.exists():
        logger.info('Clearing cache')
        CACHE_PATH.unlink()

    game_config = load_game_config(use_cache=not args.no_cache)
    game_db = GameDb.from_config(game_config, ADDITIONAL_LOCALISATIONS_PATH)
    render(game_db, OUTPUT_PATH / 'html')

    logger.info('Build completed successfully')
    return 0


def load_game_config(use_cache: bool = True) -> GameConfig:
    if use_cache and CACHE_PATH.exists():
        logger.info('Loading game config from cache')
        try:
            with CACHE_PATH.open('rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError, AttributeError) as e:
            logger.warning(f'Failed to load cache: {e}. Reparsing game files.')

    logger.info('Parsing game files for game config')
    config = GameConfig.from_directory(GAME_PATH)

    with CACHE_PATH.open('wb') as f:
        pickle.dump(config, f, pickle.HIGHEST_PROTOCOL)
    logger.info('Cache saved successfully')

    return config


def render(game_db: GameDb, output_path: Path) -> None:
    logger.info(f'Exporting HTML to {output_path}')
    exporter = HtmlExporter(game_db)
    exporter.export(output_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s'
    )
    sys.exit(main())
