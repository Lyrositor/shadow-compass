import os.path
from pathlib import Path

RESOURCES_PATH = Path('resources')
IMAGES_PATH = RESOURCES_PATH / 'images'


def list_image_resources() -> set[str]:
    return set(
        os.path.splitext(p.relative_to(IMAGES_PATH).as_posix())[0]
        for p in IMAGES_PATH.rglob('*.png')
    )
