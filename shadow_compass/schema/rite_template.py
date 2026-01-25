from dataclasses import dataclass


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float


@dataclass(frozen=True)
class RiteTemplateSlot:
    is_hide_bg: bool
    is_set_card_hide_bg: bool
    pos: Vec2
    scale: Vec2
    rotation_z: float
    slot_bg: str|None = None


@dataclass(frozen=True)
class RiteTemplate:
    id: int
    name: str
    tips: str
    bg: str
    bg_pos: Vec2
    title_pos: Vec2
    slots: dict[str, RiteTemplateSlot]
    fg: str|None = None
    nomal_slot_bg: str|None = None
    fg_in_slot_index: int|None = None


@dataclass(frozen=True)
class RiteTemplateMapping:
    id: int
    tips: str
    template_id: int
    slot_open: tuple[str, ...]
