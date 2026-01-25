from dataclasses import dataclass


@dataclass(frozen=True)
class UIItem:
    zhCN: str|None = None
    zhTW: str|None = None
    en: str|None = None
    ja: str|None = None
    comment: str|None = None


@dataclass(frozen=True)
class TextStyle:
    size: int|None = None
    color: str|None = None
    font: str|None = None


@dataclass(frozen=True)
class ImageStyle:
    width: int|None = None
    height: int|None = None
    sprite: str|None = None


@dataclass(frozen=True)
class MobileHelpSlide:
    res: str
    text: str


@dataclass(frozen=True)
class MobileHelp:
    type: str
    slides: tuple[MobileHelpSlide, ...]
