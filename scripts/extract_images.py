import json
import shutil
import sys
from pathlib import Path

from PIL import Image

BASE_GAME_RESOURCES_PATH = Path('resources') / 'game' / 'resources'
IMAGES_PATH = BASE_GAME_RESOURCES_PATH / 'Resources' / 'image'
TEXTURES_PATH = BASE_GAME_RESOURCES_PATH / 'Texture2D'
TAGS_MANIFEST_PATH = IMAGES_PATH / 'tags.bytes'
TAGS_DATA_PATH = IMAGES_PATH / 'tags.png'
OUTPUT_PATH = Path('resources') / 'images'

EQUIP_SLOTS = {
    'slot_accessory.png': 'decorate_equip.png',
    'slot_animal_handling.png': 'mount_equip.png',
    'slot_cloth.png': 'cloth_equip.png',
    'slot_weapon.png': 'weapon_equip.png',
}


def main() -> int:
    for directory in ('cards', 'common', 'pic'):
        copy_images_directory(directory)
    extract_equipment_slots()
    extract_image_map(IMAGES_PATH / 'tags.bytes', IMAGES_PATH / 'tags.png', OUTPUT_PATH)
    extract_image_map(IMAGES_PATH / 'rites.bytes', IMAGES_PATH / 'rites.png', OUTPUT_PATH)
    return 0


def copy_images_directory(directory: str) -> None:
    directory_path = IMAGES_PATH / directory
    for path in directory_path.rglob('*.png'):
        dest_path = OUTPUT_PATH / directory / path.relative_to(directory_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, dest_path)


def extract_equipment_slots() -> None:
    for dest_filename, source_filename in EQUIP_SLOTS.items():
        base = Image.open(TEXTURES_PATH / 'equip_slot.png')
        slot = Image.open(TEXTURES_PATH / source_filename)
        base.alpha_composite(slot, ((base.width - slot.width) // 2, (base.height - slot.height) // 2))
        base.save(OUTPUT_PATH / dest_filename)


def extract_image_map(map_json_path: Path, map_png_path: Path, output_path: Path) -> None:
    image_map = json.loads(map_json_path.read_text(encoding='utf-8'))
    image_map_data = Image.open(map_png_path)
    for frame in image_map['frames']:
        pivot_x = frame.get('pivot', {}).get('x', 1.0)
        pivot_y = frame.get('pivot', {}).get('y', 1.0)
        left = frame['frame']['x'] * pivot_x
        upper = frame['frame']['y'] * pivot_y
        right = left + frame['frame']['w'] * pivot_x
        lower = upper + frame['frame']['h'] * pivot_y
        image_map_data.crop((left, upper, right, lower)).save(output_path / frame['filename'])


if __name__ == '__main__':
    sys.exit(main())
