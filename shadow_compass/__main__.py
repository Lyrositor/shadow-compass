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
CACHE_PATH = OUTPUT_PATH/'cache.pickle'
EXPORT_PATH = OUTPUT_PATH/'export_html'


def main() -> int:
    logger.info('Building Shadow Compass')

    if not OUTPUT_PATH.exists():
        OUTPUT_PATH.mkdir(parents=True)

    game_config = load_game_config()
    game_db = GameDb.from_config(game_config, ADDITIONAL_LOCALISATIONS_PATH)
    render(game_db, OUTPUT_PATH / 'html')

    return 0


def load_game_config() -> GameConfig:
    if not CACHE_PATH.exists():
        logger.info('Parsing game files for game config')
        config = GameConfig.from_directory(GAME_PATH)
        with open(CACHE_PATH, 'wb') as f:
            pickle.dump(config, f, pickle.HIGHEST_PROTOCOL)
        return config
    else:
        logger.info('Loading game config from cache')
        with open(CACHE_PATH, 'rb') as f:
            return pickle.load(f)


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
